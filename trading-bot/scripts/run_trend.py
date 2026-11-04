"""Trend-following vs buy-and-hold on the 9-year Binance archive.

    python scripts/run_trend.py --resample 1D
    python scripts/run_trend.py --resample 4h --entry-len 40 --exit-len 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive, metrics as M, trend


def load(args) -> pd.DataFrame:
    df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
    if "open_time" in df.columns:
        df = df.drop(columns="open_time")
    if args.resample:
        rule = args.resample
        if rule.endswith("d"):
            rule = rule.replace("d", "D")
        df = df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
    return df


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default="1D")
    p.add_argument("--entry-len", type=int, default=20)
    p.add_argument("--exit-len", type=int, default=10)
    p.add_argument("--atr-len", type=int, default=14)
    p.add_argument("--atr-stop-mult", type=float, default=0.0)
    p.add_argument("--side", default="both", choices=["long", "both"])
    p.add_argument("--notional", type=float, default=1.0)
    p.add_argument("--fee", type=float, default=0.001)
    p.add_argument("--slippage", type=float, default=0.0005)
    p.add_argument("--split", default="2023-01-01", help="out-of-sample start date")
    args = p.parse_args()

    df = load(args)
    rule = args.resample
    bpy = M.bars_per_year_for(rule)
    print(f"data: {len(df)} bars of {rule} | {df.index[0]} -> {df.index[-1]}")
    print(f"price: {df['close'].iloc[0]:,.0f} -> {df['close'].iloc[-1]:,.0f} "
          f"({df['close'].iloc[-1]/df['close'].iloc[0]:.1f}x)")
    print(f"out-of-sample starts: {args.split}\n")

    cfg = trend.TrendConfig(
        entry_len=args.entry_len,
        exit_len=args.exit_len,
        atr_len=args.atr_len,
        atr_stop_mult=args.atr_stop_mult,
        side=args.side,
        fee_pct=args.fee,
        slippage_pct=args.slippage,
        notional=args.notional,
    )

    split = pd.Timestamp(args.split, tz=df.index.tz)
    results: dict[str, pd.Series] = {}
    results["buy & hold"] = trend.buy_and_hold(df, args.fee, args.slippage)

    for side in (["long", "both"] if args.side == "both" else [args.side]):
        c = trend.TrendConfig(**{**cfg.__dict__, "side": side})
        res = trend.run_trend(df, c)
        results[f"trend {side}"] = res.equity
        n_trades = len(res.trades)
        print(f"trend {side:<4}: {n_trades:>4} trades, exposure {res.exposure*100:>5.1f}%, "
              f"fees paid {res.fees_paid:>6.2f} of starting equity")

    # ---- full period ----
    print("\n=== FULL PERIOD " + df.index[0].strftime('%Y-%m') + " -> " + df.index[-1].strftime('%Y-%m') + " ===")
    table = M.compare(results, bpy)
    print(table.to_string(float_format=lambda v: f"{v:,.3f}"))

    # ---- in-sample / out-of-sample ----
    print(f"\n=== IN-SAMPLE (before {args.split}) ===")
    is_eq = {k: v[v.index < split] for k, v in results.items()}
    print(M.compare(is_eq, bpy).to_string(float_format=lambda v: f"{v:,.3f}"))

    print(f"\n=== OUT-OF-SAMPLE (from {args.split}) ===")
    oos_eq = {k: v[v.index >= split] for k, v in results.items()}
    print(M.compare(oos_eq, bpy).to_string(float_format=lambda v: f"{v:,.3f}"))

    # ---- what the price actually did ----
    print("\n=== CONTEXT ===")
    for label, sub in (("in-sample", df[df.index < split]), ("out-of-sample", df[df.index >= split])):
        if sub.empty:
            continue
        hi = sub["close"].max()
        lo = sub["close"].min()
        print(f"{label:<14} buy&hold {sub['close'].iloc[-1]/sub['close'].iloc[0]:>7.1f}x   "
              f"high {hi:,.0f}  low {lo:,.0f}")

    out = Path(__file__).resolve().parent.parent / "data" / "trend_equity.csv"
    pd.DataFrame(results).to_csv(out)
    print(f"\nequity curves written to {out}")


if __name__ == "__main__":
    main()
