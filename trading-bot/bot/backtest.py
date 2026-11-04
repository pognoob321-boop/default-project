"""Backtest metrics: R-based, cost-aware, no hand-waving."""

from __future__ import annotations

import pandas as pd

from .strategy import ORBConfig, Trade


def trade_cost_in_r(t, cfg: ORBConfig) -> float:
    """Cost of one round trip expressed in R.

    Two models:
      points  - futures/equities: dollars / (risk_points * point_value)
      percent - crypto: 2 * (fee + slippage) * price, divided by the risk
                 in price units. Both sides pay, so it is a factor of two.
    """
    risk_points = abs(t.entry - t.stop)
    if risk_points <= 0:
        return 0.0
    if cfg.fee_pct or cfg.slippage_pct:
        cost_price = 2.0 * (cfg.fee_pct + cfg.slippage_pct) * t.entry
        return float(cost_price / risk_points)
    dollars = cfg.commission_per_rt + cfg.slippage_points * cfg.point_value
    return float(dollars / (risk_points * cfg.point_value))


def apply_costs(trades: list[Trade], cfg: ORBConfig) -> pd.DataFrame:
    """Convert each trade into a cost-adjusted R value."""
    rows = []
    for t in trades:
        risk_points = abs(t.entry - t.stop)
        cost_r = trade_cost_in_r(t, cfg)
        rows.append(
            {
                "session": t.session,
                "side": t.side,
                "signal_time": t.signal_time,
                "entry_time": t.entry_time,
                "entry": t.entry,
                "stop": t.stop,
                "target": t.target,
                "exit_time": t.exit_time,
                "exit": t.exit,
                "r_gross": t.r,
                "r_net": t.r - cost_r,
                "risk_points": risk_points,
                "reason": t.reason,
            }
        )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame, cfg: ORBConfig) -> dict:
    if df.empty:
        return {"trades": 0, "note": "no trades generated"}

    r = df["r_net"]
    wins = df[df["r_net"] > 0]
    losses = df[df["r_net"] <= 0]
    gross_win = float(wins["r_net"].sum())
    gross_loss = float(abs(losses["r_net"].sum()))
    equity = r.cumsum()

    stats = {
        "trades": int(len(df)),
        "win_rate": float((r > 0).mean()),
        "total_r": float(r.sum()),
        "avg_r": float(r.mean()),
        "avg_win_r": float(wins["r_net"].mean()) if len(wins) else 0.0,
        "avg_loss_r": float(losses["r_net"].mean()) if len(losses) else 0.0,
        "profit_factor": float(gross_win / gross_loss) if gross_loss else float("inf"),
        "max_dd_r": float((equity.cummax() - equity).max()),
        "expectancy_r": float(r.mean()),
        "cost_per_trade_r": float((df["r_gross"] - df["r_net"]).mean()),
        "long_r": float(df[df["side"] == "long"]["r_net"].sum()),
        "short_r": float(df[df["side"] == "short"]["r_net"].sum()),
    }

    by_reason = df.groupby("reason").agg(
        n=("r_net", "size"), total_r=("r_net", "sum"), avg_r=("r_net", "mean")
    )
    stats["by_reason"] = by_reason.to_dict("index")

    by_side = df.groupby("side").agg(
        n=("r_net", "size"), total_r=("r_net", "sum"), avg_r=("r_net", "mean"),
        win_rate=("r_net", lambda s: float((s > 0).mean())),
    )
    stats["by_side"] = by_side.to_dict("index")

    # how many days had a trade at all (coverage)
    stats["sessions_traded"] = int(df["session"].nunique())
    return stats


def print_report(stats: dict, cfg: ORBConfig) -> None:
    print("=" * 62)
    print("ORB BACKTEST REPORT")
    print("=" * 62)
    print(
        f"config: OR={cfg.or_minutes}m confirm={cfg.confirm_minutes}m "
        f"stop={cfg.stop_mode} target={cfg.target_mode}"
        + (f" ({cfg.target_r}R)" if cfg.target_mode == "r" else "")
        + f" vwap_filter={cfg.vwap_filter} index_confirm={cfg.index_confirm}"
    )
    if not stats.get("trades"):
        print("no trades generated")
        return
    print(f"trades            : {stats['trades']}  over {stats['sessions_traded']} sessions")
    print(f"win rate          : {stats['win_rate']*100:.1f}%")
    print(f"total R           : {stats['total_r']:+.2f}R")
    print(f"avg R / trade     : {stats['avg_r']:+.3f}R")
    print(f"avg win / avg loss: {stats['avg_win_r']:+.2f}R / {stats['avg_loss_r']:+.2f}R")
    print(f"profit factor     : {stats['profit_factor']:.2f}")
    print(f"max drawdown      : {stats['max_dd_r']:.2f}R")
    print(f"cost per trade    : {stats['cost_per_trade_r']:.3f}R")
    print(f"long R / short R  : {stats['long_r']:+.2f}R / {stats['short_r']:+.2f}R")
    print("-" * 62)
    for reason, s in stats["by_reason"].items():
        print(f"  exit={reason:<7} n={int(s['n']):<4} total={s['total_r']:+.2f}R  avg={s['avg_r']:+.3f}R")
    for side, s in stats["by_side"].items():
        print(f"  {side:<6} n={int(s['n']):<4} total={s['total_r']:+.2f}R  avg={s['avg_r']:+.3f}R  win={s['win_rate']*100:.0f}%")
    print("=" * 62)
