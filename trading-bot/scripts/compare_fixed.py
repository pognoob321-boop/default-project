"""Compare fixed configurations over the full history, on both venues.

No search here: every config below was fixed in advance (the enhanced one uses
the parameters the walk-forward picked MOST OFTEN, not the ones that scored
best - choosing by score would be selecting on the test data).

    python scripts/compare_fixed.py --source yahoo --symbol SPY --interval 1d --range 30y
    python scripts/compare_fixed.py --source archive --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive, metrics as M, trend


def load(args) -> pd.DataFrame:
    if args.source == "archive":
        df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
        rule = args.resample.replace("d", "D")
        return df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
    from bot import data
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
    p.add_argument("--split", default=None, help="optional IS/OOS split date")
    args = p.parse_args()

    df = load(args)
    bpy = M.bars_per_year_from_data(df)
    print(f"{args.symbol}: {len(df)} bars {df.index[0].date()} -> {df.index[-1].date()} "
          f"({bpy:.0f} bars/year)")
    print(f"costs: fee {args.fee:.4%} + slippage {args.slippage:.4%} per side\n")

    base = dict(fee_pct=args.fee, slippage_pct=args.slippage, side="long", max_leverage=1.0)

    configs = {
        "A plain Donchian 20/10": dict(base, entry_len=20, exit_len=10),
        "B modal enhanced 20/50": dict(base, entry_len=20, exit_len=50, atr_stop_mult=2.0),
        "C enhanced + regime200": dict(base, entry_len=20, exit_len=50, atr_stop_mult=2.0, regime_len=200, regime_slope=True),
        "D enhanced + vol target": dict(base, entry_len=20, exit_len=50, atr_stop_mult=2.0, regime_len=200, regime_slope=True, vol_target=0.01, max_leverage=1.0),
        "E enhanced + trailing": dict(base, entry_len=20, exit_len=50, atr_stop_mult=2.0, regime_len=200, regime_slope=True, trailing_atr=3.0, time_stop_bars=250, cost_filter_mult=2.0, dd_cut=0.15),
    }

    curves = {"buy & hold": trend.buy_and_hold(df, args.fee, args.slippage)}
    for name, kwargs in configs.items():
        res = trend.run_trend(df, trend.TrendConfig(**kwargs))
        curves[name] = res.equity
        print(f"  {name:<24} trades={len(res.trades):>4}  exposure={res.exposure*100:>5.1f}%  "
              f"avg leverage {res.avg_leverage:.2f}x  fees {res.fees_paid:.3f}")

    def show(label: str, sub: pd.DataFrame) -> None:
        rows = []
        lo, hi = sub.index[0], sub.index[-1]
        for name, eq in curves.items():
            s = eq[(eq.index >= lo) & (eq.index <= hi)]
            if len(s) < 5:
                continue
            m = M.metrics(s, bpy)
            rows.append({"curve": name, **m})
        t = pd.DataFrame(rows).set_index("curve")
        print(f"\n=== {label} ===")
        print(t.to_string(float_format=lambda v: f"{v:,.3f}"))

    show("FULL HISTORY", df)
    if args.split:
        cut = pd.Timestamp(args.split, tz=df.index.tz)
        show(f"IN-SAMPLE (before {args.split})", df[df.index < cut])
        show(f"OUT-OF-SAMPLE (from {args.split})", df[df.index >= cut])

    out = Path(__file__).resolve().parent.parent / "data" / f"fixed_{args.symbol}_{args.source}.csv"
    pd.DataFrame(curves).to_csv(out)
    print(f"\ncurves written to {out}")


if __name__ == "__main__":
    main()
