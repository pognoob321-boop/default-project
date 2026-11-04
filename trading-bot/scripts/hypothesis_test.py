"""Hypothesis test: does the ORB edge appear only with a session anchor and a
range-width filter?

The repo's ORB research claims a range-width filter is critical (1.41 PF on
NAS100, 1,166 trades) and that crypto needs a defined session anchor. The
first 9-year BTC run used a 00:00 UTC anchor with no width filter and found
zero gross edge. This script varies both.

    python scripts/hypothesis_test.py --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import backtest, binance_archive, instruments, strategy


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default="15min")
    p.add_argument("--target-r", type=float, default=3.0)
    p.add_argument("--stop-mode", default="range")
    args = p.parse_args()

    df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
    if "open_time" in df.columns:
        df = df.drop(columns="open_time")
    rule = args.resample if args.resample.endswith("min") else args.resample + "min"
    df = df.resample(rule).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()
    print(f"data: {len(df)} bars {rule} | {df.index[0]} -> {df.index[-1]}")
    print(f"symbols: {df['close'].iloc[0]:.0f} -> {df['close'].iloc[-1]:.0f}\n")

    costs = instruments.costs_for(args.symbol)
    zero = dict(costs)
    zero.update(fee_pct=0.0, slippage_pct=0.0, commission_per_rt=0.0, slippage_points=0.0)

    anchors = ["00:00", "08:00", "13:30"]
    or_mins = [15, 30, 60]
    widths = [None, 0.005, 0.010]

    rows = []
    for anchor, or_min, width in itertools.product(anchors, or_mins, widths):
        res = {}
        for label, c in (("net", costs), ("gross", zero)):
            cfg = strategy.ORBConfig(
                **c,
                session_start=anchor,
                flat_by="23:50",
                or_minutes=or_min,
                stop_mode=args.stop_mode,
                target_r=args.target_r,
                min_or_width_pct=width,
            )
            trades = strategy.generate_trades(df, cfg)
            tdf = backtest.apply_costs(trades, cfg)
            res[label] = float(tdf["r_net"].mean()) if len(tdf) else float("nan")
            res["n"] = len(tdf)
        rows.append(
            {
                "anchor": anchor,
                "or_min": or_min,
                "width_pct": width if width else 0,
                "trades": res["n"],
                "gross_r": res["gross"],
                "net_r": res["net"],
            }
        )
        r = rows[-1]
        print(
            f"anchor={anchor}  OR={or_min:>2}m  width_filter={'none' if not width else f'{width*100:.1f}%':>6}  "
            f"n={r['trades']:>5}  gross={r['gross_r']:+.3f}R  net={r['net_r']:+.3f}R",
            flush=True,
        )

    import pandas as pd
    out = pd.DataFrame(rows)
    out.to_csv("data/hypothesis_test.csv", index=False)
    print("\n--- top 8 by GROSS expectancy (no fees: the only fair test of an edge) ---")
    print(out.sort_values("gross_r", ascending=False).head(8).to_string(index=False))
    print("\n--- top 8 by NET expectancy (after 0.3% round-trip cost) ---")
    print(out.sort_values("net_r", ascending=False).head(8).to_string(index=False))
    print(
        f"\nconfigs with a positive GROSS edge: {(out['gross_r'] > 0).sum()}/{len(out)}\n"
        f"configs with a positive NET edge  : {(out['net_r'] > 0).sum()}/{len(out)}"
    )


if __name__ == "__main__":
    main()
