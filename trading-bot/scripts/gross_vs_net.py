"""Gross vs net expectancy - is the strategy losing, or are the fees losing?

    python scripts/gross_vs_net.py --source archive --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import backtest, binance_archive, data, instruments, strategy


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--source", default="archive", choices=["yahoo", "archive"])
    p.add_argument("--interval", default="1m")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default="15min")
    p.add_argument("--or-minutes", type=int, default=60)
    p.add_argument("--stop-mode", default="range")
    p.add_argument("--target-r", type=float, default=3.0)
    p.add_argument("--session-start", default="00:00")
    p.add_argument("--flat-by", default="23:50")
    args = p.parse_args()

    if args.source == "archive":
        df = binance_archive.load_dataset(args.symbol, args.interval, args.start, args.end, verbose=False)
    else:
        df = data.fetch_yahoo(args.symbol, args.interval, "60d")
    if args.resample:
        rule = args.resample if args.resample.endswith("min") else args.resample + "min"
        df = df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
    if "open_time" in df.columns:
        df = df.drop(columns="open_time")

    real_costs = instruments.costs_for(args.symbol)
    zero_costs = dict(real_costs)
    zero_costs.update(fee_pct=0.0, slippage_pct=0.0, commission_per_rt=0.0, slippage_points=0.0)

    print(f"{'config':<28} {'trades':>7} {'gross R':>10} {'net R':>10} {'cost R':>8}")
    print("-" * 70)
    for label, costs in (("net (real fees+slippage)", real_costs), ("gross (zero cost)", zero_costs)):
        cfg = strategy.ORBConfig(
            **costs,
            session_start=args.session_start,
            flat_by=args.flat_by,
            or_minutes=args.or_minutes,
            stop_mode=args.stop_mode,
            target_r=args.target_r,
        )
        trades = strategy.generate_trades(df, cfg)
        tdf = backtest.apply_costs(trades, cfg)
        gross = tdf["r_gross"].mean()
        net = tdf["r_net"].mean()
        cost = gross - net
        print(f"{label:<28} {len(tdf):>7} {gross:>+10.3f} {net:>+10.3f} {cost:>8.3f}")
        if label.startswith("gross"):
            tdf.to_csv("data/gross_vs_net_trades.csv", index=False)
            print(f"  -> trade detail written to data/gross_vs_net_trades.csv")

    # how wide are the stops relative to price? (fees are a % of price)
    tdf = pd.read_csv("data/gross_vs_net_trades.csv")
    tdf["stop_pct"] = tdf["risk_points"] / tdf["entry"] * 100
    print("-" * 70)
    print(f"median stop distance : {tdf['stop_pct'].median():.3f}% of price")
    print(f"round-trip cost      : {2*(real_costs['fee_pct']+real_costs['slippage_pct'])*100:.3f}% of price")
    print(f"=> cost as a share of the stop: "
          f"{2*(real_costs['fee_pct']+real_costs['slippage_pct'])*100/tdf['stop_pct'].median():.2f}R")
    print(f"break-even move needed before fees: "
          f"{2*(real_costs['fee_pct']+real_costs['slippage_pct'])*100:.3f}% per trade")


if __name__ == "__main__":
    import pandas as pd  # noqa: E402  (used in the summary block)
    main()
