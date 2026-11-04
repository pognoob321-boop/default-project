"""Performance metrics for an equity curve.

The only two questions that matter:
  1. Did it make money after costs?  (total return, CAGR)
  2. Was it worth the risk vs just holding?  (max drawdown, Sharpe, Calmar)
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((peak - equity).div(peak).max() * -1.0)


def metrics(equity: pd.Series, bars_per_year: float) -> dict:
    equity = equity.dropna()
    if len(equity) < 3:
        return {"total_return": 0.0, "cagr": 0.0, "max_dd": 0.0, "sharpe": 0.0, "calmar": 0.0}

    total = float(equity.iloc[-1] / equity.iloc[0] - 1)
    years = len(equity) / bars_per_year
    if years > 0 and equity.iloc[-1] > 0 and equity.iloc[0] > 0:
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1
    else:
        cagr = -1.0 if equity.iloc[-1] <= 0 else 0.0

    rets = equity.pct_change().dropna()
    vol = float(rets.std())
    sharpe = float(rets.mean() / vol * np.sqrt(bars_per_year)) if vol > 0 else 0.0

    dd = max_drawdown(equity)
    calmar = float(cagr / abs(dd)) if dd < 0 else 0.0

    return {
        "total_return": total,
        "cagr": float(cagr),
        "max_dd": dd,
        "sharpe": sharpe,
        "calmar": calmar,
        "vol_ann": float(vol * np.sqrt(bars_per_year)),
        "final_value": float(equity.iloc[-1]),
    }


def bars_per_year_for(rule: str) -> float:
    """Fallback annualisation factor. Prefer bars_per_year_from_data()."""
    r = rule.strip().lower()
    if r.endswith("d"):
        return 252.0          # trading days, not calendar days
    if r.endswith("w"):
        return 52.0
    if r.endswith("mo") or r.endswith("month"):
        return 12.0
    if r.endswith("min"):
        head = r[:-3]
        mins = int(head) if head.isdigit() else 1
    elif r.endswith("h"):
        head = r[:-1]
        mins = (int(head) if head.isdigit() else 1) * 60
    elif r.endswith("m"):
        head = r[:-1]
        mins = int(head) if head.isdigit() else 1
    else:
        mins = 1
    return 252.0 * 24 * 60 / mins


def bars_per_year_from_data(df) -> float:
    """Annualisation factor measured from the data itself.

    365 calendar days is wrong for equities (252 trading days) and right for
    24/7 crypto; measuring the span avoids guessing.
    """
    if len(df) < 3:
        return 252.0
    span_days = (df.index[-1] - df.index[0]).total_seconds() / 86400.0
    if span_days <= 0:
        return 252.0
    return len(df) / (span_days / 365.25)


def compare(
    results: dict,
    bars_per_year: float,
    label_a: str = "strategy",
    label_b: str = "buy & hold",
) -> pd.DataFrame:
    """Side-by-side table of two equity curves."""
    rows = []
    for name, eq in results.items():
        m = metrics(eq, bars_per_year)
        rows.append({"strategy": name, **m})
    return pd.DataFrame(rows).set_index("strategy")
