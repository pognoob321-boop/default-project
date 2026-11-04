"""Rotation test with clean benchmarks on the SAME aligned period."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import data, metrics as M, rotation


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--split", default="2010-01-01")
    p.add_argument("--fee", type=float, default=0.001)
    p.add_argument("--slippage", type=float, default=0.0001)
    args = p.parse_args()

    spy = data.fetch_yahoo("SPY", "1d", "max").drop(columns=["open_time"], errors="ignore")
    tlt = data.fetch_yahoo("TLT", "1d", "max").drop(columns=["open_time"], errors="ignore")
    bpy = M.bars_per_year_from_data(spy)
    print(f"SPY: {len(spy)} bars {spy.index[0].date()} -> {spy.index[-1].date()}")
    print(f"TLT: {len(tlt)} bars {tlt.index[0].date()} -> {tlt.index[-1].date()}")

    # Benchmarks over FULL history
    bh_spy = data_trend_buy_hold(spy, args.fee, args.slippage)
    bh_tlt = data_trend_buy_hold(tlt, args.fee, args.slippage)
    print(f"\nBuy&hold SPY (full):  CAGR {M.metrics(bh_spy, bpy)['cagr']*100:>6.1f}%  Sharpe {M.metrics(bh_spy, bpy)['sharpe']:>5.2f}  DD {M.metrics(bh_spy, bpy)['max_dd']*100:>6.1f}%")
    print(f"Buy&hold TLT (full):  CAGR {M.metrics(bh_tlt, bpy)['cagr']*100:>6.1f}%  Sharpe {M.metrics(bh_tlt, bpy)['sharpe']:>5.2f}  DD {M.metrics(bh_tlt, bpy)['max_dd']*100:>6.1f}%")

    configs = [
        ("switch 60", 60, "switch"),
        ("switch 100", 100, "switch"),
        ("switch 200", 200, "switch"),
        ("blend 100", 100, "blend"),
    ]

    cut = pd.Timestamp(args.split, tz=spy.index.tz)

    print(f"\n=== OUT-OF-SAMPLE from {cut.date()} ===")
    print(f"{'Strategy':<20} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>8} {'Trades':>7}")
    for name, lb, mode in configs:
        cfg = rotation.RotConfig(lookback=lb, mode=mode, fee_pct=args.fee, slippage_pct=args.slippage)
        eq, trades = rotation.run_rotation(spy, tlt, cfg)
        s = eq[eq.index >= cut]
        if len(s) < 10:
            print(f"{name:<20} {'n/a':>8} {'n/a':>8} {'n/a':>8} {'n/a':>7}")
            continue
        m = M.metrics(s, bpy)
        print(f"{name:<20} {m['cagr']*100:>7.1f}% {m['sharpe']:>7.2f} {m['max_dd']*100:>7.1f}% {trades:>7}")

    # Buy & hold over OOS period
    bh_spy_oos = bh_spy[bh_spy.index >= cut]
    bh_tlt_oos = bh_tlt[bh_tlt.index >= cut]
    print(f"{'Buy&hold SPY':<20} {M.metrics(bh_spy_oos, bpy)['cagr']*100:>7.1f}% {M.metrics(bh_spy_oos, bpy)['sharpe']:>7.2f} {M.metrics(bh_spy_oos, bpy)['max_dd']*100:>7.1f}% {'-':>7}")
    print(f"{'Buy&hold TLT':<20} {M.metrics(bh_tlt_oos, bpy)['cagr']*100:>7.1f}% {M.metrics(bh_tlt_oos, bpy)['sharpe']:>7.2f} {M.metrics(bh_tlt_oos, bpy)['max_dd']*100:>7.1f}% {'-':>7}")


def data_trend_buy_hold(df, fee_pct, slippage_pct):
    from bot import trend
    return trend.buy_and_hold(df, fee_pct, slippage_pct)


if __name__ == "__main__":
    main()
