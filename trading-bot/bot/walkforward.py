"""Walk-forward validation.

The only honest way to answer "did I improve the strategy?".

Protocol (the standard one):
  for each fold:
      pick parameters that maximise the objective on the TRAIN window
      apply those parameters to the NEXT, untouched TEST window
      chain the test windows into one continuous out-of-sample equity curve
  report the stitched out-of-sample curve against buy-and-hold

Why this and not "search 1000 configs on the whole dataset": the winner of
that search is the maximum of 1000 noisy estimates, and it will look brilliant
and lose money live. Walk-forward measures the *procedure*, not the luck.

Warmup: each test slice is simulated together with the preceding bars so the
rolling channels/ATR are populated, but only the test window is counted.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import metrics as M
from . import trend


@dataclass
class WalkForwardSpec:
    train_bars: int = 1260     # 5 years of daily bars
    test_bars: int = 252       # 1 year
    step_bars: int = 252       # roll forward one year at a time
    objective: str = "sharpe"  # "sharpe" | "calmar" | "cagr"
    min_trades: int = 5        # a config needs this many trades to be considered


@dataclass
class WFResult:
    oos_equity: pd.Series
    benchmark: pd.Series
    baseline: pd.Series
    folds: list = field(default_factory=list)
    n_configs: int = 0


def _score(equity: pd.Series, trades: int, bpy: float, objective: str) -> float:
    if trades < 1 or len(equity) < 10:
        return -np.inf
    m = M.metrics(equity, bpy)
    if objective == "calmar":
        return m["calmar"] if np.isfinite(m["calmar"]) else -np.inf
    if objective == "cagr":
        return m["cagr"]
    return m["sharpe"]


def _run_slice(df: pd.DataFrame, cfg: trend.TrendConfig) -> trend.TrendResult:
    return trend.run_trend(df, cfg)


def walk_forward(
    df: pd.DataFrame,
    grid: dict,
    base: dict,
    spec: WalkForwardSpec,
    bpy: float,
    baseline_cfg: trend.TrendConfig | None = None,
    warmup_bars: int = 120,
) -> WFResult:
    """Run the walk-forward procedure and return the stitched OOS curves."""
    n = len(df)
    keys = list(grid)
    combos = list(itertools.product(*(grid[k] for k in keys)))

    oos_returns: list[pd.Series] = []
    folds: list[dict] = []
    oos_start = None
    oos_end = None

    start = 0
    while start + spec.train_bars + spec.test_bars <= n:
        train = df.iloc[start : start + spec.train_bars]
        test_start = start + spec.train_bars
        test_end = test_start + spec.test_bars
        test = df.iloc[test_start:test_end]

        best_score, best_kwargs, best_trades = -np.inf, None, 0
        for combo in combos:
            kwargs = dict(zip(keys, combo))
            cfg = trend.TrendConfig(**base, **kwargs)
            res = _run_slice(train, cfg)
            s = _score(res.equity, len(res.trades), bpy, spec.objective)
            if s > best_score:
                best_score, best_kwargs, best_trades = s, kwargs, len(res.trades)

        if best_kwargs is None:
            start += spec.step_bars
            continue

        # apply the chosen config to the test window (with warmup history)
        cfg = trend.TrendConfig(**base, **best_kwargs)
        sim_from = max(0, test_start - warmup_bars)
        sim = df.iloc[sim_from:test_end]
        res = _run_slice(sim, cfg)
        eq = res.equity.loc[test.index]
        if len(eq) < 5:
            start += spec.step_bars
            continue
        eq = eq / eq.iloc[0]          # normalise the fold to 1.0
        oos_returns.append(eq.pct_change().dropna())

        if oos_start is None:
            oos_start = test.index[0]
        oos_end = test.index[-1]

        folds.append(
            {
                "train_start": train.index[0],
                "train_end": train.index[-1],
                "test_start": test.index[0],
                "test_end": test.index[-1],
                "params": best_kwargs,
                "train_score": best_score,
                "test_return": float(eq.iloc[-1] - 1),
            }
        )
        start += spec.step_bars

    if not oos_returns:
        return WFResult(pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float), [], 0)

    oos = pd.concat(oos_returns)
    oos = oos[(oos.index >= oos_start) & (oos.index <= oos_end)]
    oos_equity = (1 + oos).cumprod()
    oos_equity.index.name = "timestamp"

    span = df.loc[oos_start:oos_end]
    bench = trend.buy_and_hold(span, base.get("fee_pct", 0.0), base.get("slippage_pct", 0.0))

    base_line = pd.Series(dtype=float)
    if baseline_cfg is not None:
        res = _run_slice(span, baseline_cfg)
        base_line = res.equity

    return WFResult(
        oos_equity=oos_equity,
        benchmark=bench,
        baseline=base_line,
        folds=folds,
        n_configs=len(combos),
    )


def report(result: WFResult, bpy: float, label: str = "walk-forward") -> pd.DataFrame:
    rows = []
    for name, eq in (("walk-forward", result.oos_equity), ("fixed baseline", result.baseline), ("buy & hold", result.benchmark)):
        if eq is None or len(eq) < 5:
            continue
        m = M.metrics(eq, bpy)
        rows.append({"curve": name, **m})
    df = pd.DataFrame(rows).set_index("curve")
    print(f"\n=== {label} | OUT-OF-SAMPLE (stitched) ===")
    print(df.to_string(float_format=lambda v: f"{v:,.3f}"))
    return df
