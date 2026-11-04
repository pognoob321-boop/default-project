"""Multi-asset rotation test: SPY vs TLT.

All data from Yahoo Finance, free, no account.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import metrics as M, rotation


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="SPY")
    p.add_argument("--bond", default="TLT")
    p.add_argument("--range", dest="range_", default="30y")
    p.add_argument("--fee", type=float, default=0.0)
    p.add_argument("--slippage", type=float, default=0.0001)
    p.add_argument("--split", default="2010-01-01")
    args = p.parse_args()

    from bot import data

    spy = data.fetch_yahoo(args.symbol, "1d", args.range_).drop(columns=["open_time"], errors="ignore")
    tlt = data.fetch_yahoo(args.bond, "1d", args.range_).drop(columns=["open_time"], errors="ignore")
    bpy = M.bars_per_year_from_data(spy)
    print(f"SPY: {len(spy)} bars {spy.index[0].date()} -> {spy.index[-1].date()}")
    print(f"TLT: {len(tlt)} bars {tlt.index[0].date()} -> {tlt.index[-1].date()} ({bpy:.0f} bars/yr)")

    curves = {"buy & hold SPY": None, "buy & hold TLT": None}
    from bot import trend
    curves = {
        "buy & hold SPY": trend.buy_and_hold(spy, args.fee, args.slippage),
        "buy & hold TLT": trend.buy_and_hold(tlt, args.fee, args.slippage),
        "60/40 SPY/TLT (rebal monthly)": None,
    }

    configs = {
        "Rotation switch, lookback=100": dict(lookback=100, mode="switch"),
        "Rotation switch, lookback=200": dict(lookback=200, mode="switch"),
        "Rotation switch, lookback=60": dict(lookback=60, mode="switch"),
        "Rotation blend, lookback=100": dict(lookback=100, mode="blend"),
        "Rotation filter (SPY>SMA200), lookback=100": dict(lookback=100, mode="filter", regime_len=200),
        "Rotation filter (SPY>SMA100), lookback=100": dict(lookback=100, mode="filter", regime_len=100),
    }

    for name, kwargs in configs.items():
        cfg = rotation.RotationConfig(fee_pct=args.fee, slippage_pct=args.slippage, **kwargs)
        eq, trades, fees = rotation.run_rotation(spy, tlt, cfg)
        curves[name] = eq
        m = M.metrics(eq, bpy)
        print(f"  {name:<42} trades={trades:>4}  CAGR={m['cagr']*100:>6.1f}%  Sharpe={m['sharpe']:>5.2f}  DD={m['max_dd']*100:>6.1f}%")

    # 60/40 monthly rebalance
    spy_aligned = spy.reindex(spy.index)
    tlt_aligned = tlt.reindex(spy.index)
    # Monthly rebalance: last trading day of each month
    month_ends = spy.resample("ME").last().index
    # Build daily equity
    cash = 1.0
    units_spy = 0.0
    units_tlt = 0.0
    equity = np.empty(len(spy))
    for i in range(len(spy)):
        date = spy.index[i]
        if date in month_ends or i == 0:
            # rebalance to 60/40
            port_val = cash + units_spy * spy["close"].iloc[i] + units_tlt * tlt_aligned["close"].reindex([date]).iloc[0] if i > 0 else 1.0
            # sell everything
            cash = port_val
            units_spy = 0
            units_tlt = 0
            # buy 60% SPY, 40% TLT at next open... but for simplicity use close
            fill_spy = spy["close"].iloc[i] * (1 + args.slippage)
            fill_tlt = tlt_aligned["close"].reindex([date]).iloc[0] * (1 + args.slippage)
            notional_spy = port_val * 0.6
            notional_tlt = port_val * 0.4
            units_spy = notional_spy / fill_spy
            units_tlt = notional_tlt / fill_tlt
            cash = 0
        equity[i] = cash + units_spy * spy["close"].iloc[i] + units_tlt * tlt_aligned["close"].reindex([date]).iloc[0] if i > 0 else 1.0
    curves["60/40 SPY/TLT (rebal monthly)"] = pd.Series(equity, index=spy.index, name="eq")

    cut = pd.Timestamp(args.split, tz=spy.index.tz)
    print(f"\n=== OUT-OF-SAMPLE (from {cut.date()}) ===")
    for name, eq in curves.items():
        s = eq[eq.index >= cut]
        if len(s) < 5:
            continue
        m = M.metrics(s, bpy)
        print(f"  {name:<42} CAGR={m['cagr']*100:>6.1f}%  Sharpe={m['sharpe']:>5.2f}  DD={m['max_dd']*100:>6.1f}%")

    print("\nFull history:")
    for name, eq in curves.items():
        m = M.metrics(eq, bpy)
        print(f"  {name:<42} CAGR={m['cagr']*100:>6.1f}%  Sharpe={m['sharpe']:>5.2f}  DD={m['max_dd']*100:>6.1f}%")


if __name__ == "__main__":
    main()
