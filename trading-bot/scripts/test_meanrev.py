"""Quick mean reversion test on both venues, fixed configs only (no search)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive, data, metrics as M, meanrev


def load(args) -> pd.DataFrame:
    if args.source == "archive":
        df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
        rule = args.resample.replace("d", "D")
        return df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
    return data.fetch_yahoo(args.symbol, args.interval, args.range_).drop(columns=["open_time"], errors="ignore")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="SPY")
    p.add_argument("--source", default="yahoo", choices=["yahoo", "archive"])
    p.add_argument("--interval", default="1d")
    p.add_argument("--range", dest="range_", default="30y")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default="1D")
    p.add_argument("--fee", type=float, default=0.0)
    p.add_argument("--slippage", type=float, default=0.0001)
    p.add_argument("--split", default=None)
    args = p.parse_args()

    df = load(args)
    bpy = M.bars_per_year_from_data(df)
    print(f"{args.symbol}: {len(df)} bars {df.index[0].date()} -> {df.index[-1].date()} ({bpy:.0f} bars/yr)")

    from bot import trend
    curves = {"buy & hold": trend.buy_and_hold(df, args.fee, args.slippage)}

    configs = {
        "MR z=2.0 exit=mean": dict(window=20, z_entry=2.0, z_exit=0.0),
        "MR z=2.5 exit=mean": dict(window=20, z_entry=2.5, z_exit=0.0),
        "MR z=1.5 exit=mean": dict(window=20, z_entry=1.5, z_exit=0.0),
        "MR z=2.0 exit=mean+0.5std": dict(window=20, z_entry=2.0, z_exit=0.5),
        "MR RSI<30 / >70": dict(window=20, z_entry=0, rsi_low=30, rsi_high=70),
        "MR RSI<25 / >75": dict(window=20, z_entry=0, rsi_low=25, rsi_high=75),
        "MR z=3.0 exit=mean": dict(window=30, z_entry=3.0, z_exit=0.0),
    }

    for name, kwargs in configs.items():
        cfg = meanrev.MeanRevConfig(fee_pct=args.fee, slippage_pct=args.slippage, **kwargs)
        eq, tdf = meanrev.run_mean_reversion(df, cfg)
        curves[name] = eq
        m = M.metrics(eq, bpy)
        print(f"  {name:<28} trades={len(tdf):>4}  CAGR={m['cagr']*100:>6.1f}%  Sharpe={m['sharpe']:>5.2f}  DD={m['max_dd']*100:>6.1f}%")

    cut = pd.Timestamp(args.split, tz=df.index.tz) if args.split else None
    if cut:
        print(f"\n=== OUT-OF-SAMPLE (from {cut.date()}) ===")
        for name, eq in curves.items():
            s = eq[eq.index >= cut]
            if len(s) < 5:
                continue
            m = M.metrics(s, bpy)
            print(f"  {name:<28} CAGR={m['cagr']*100:>6.1f}%  Sharpe={m['sharpe']:>5.2f}  DD={m['max_dd']*100:>6.1f}%")
    print("\nNone of these are tuned - all fixed configs.")


if __name__ == "__main__":
    main()
