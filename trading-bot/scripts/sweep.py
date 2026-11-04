"""Parameter sweep with an in-sample / out-of-sample split.

The point of this file: a bot is NOT proven by one good backtest run.
Two traps this script exists to expose:

  1. Curve fitting. Search 100 parameter sets and the best one is noise.
     Fix: split the data in half by time. Tune on the first half only,
     then report the untouched second half as the honest number.
  2. Lookahead. Strategy code that peeks at future bars looks brilliant and
     loses money live. (This repo already shipped one such bug - it entered
     trades before the opening-range window closed.)

Usage:
    python scripts/sweep.py --symbol "ES=F" --interval 5m --range 60d
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import backtest, data, instruments, strategy


def run(df: pd.DataFrame, cfg: strategy.ORBConfig, index_by_session=None) -> pd.DataFrame:
    trades = strategy.generate_trades(df, cfg, index_by_session=index_by_session)
    return backtest.apply_costs(trades, cfg)


def score(trades: pd.DataFrame) -> tuple[float, int, float]:
    """(expectancy per trade, trade count, profit factor)

    A config with zero trades scores -inf expectancy, NOT 0.0 - otherwise a
    config that never traded would outrank every config that lost money.
    """
    if trades.empty:
        return float("-inf"), 0, 0.0
    r = trades["r_net"]
    wins = r[r > 0].sum()
    loss = abs(r[r <= 0].sum())
    pf = float(wins / loss) if loss else float("inf")
    return float(r.mean()), int(len(trades)), pf


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="ES=F")
    p.add_argument("--source", default="yahoo", choices=["yahoo", "archive"])
    p.add_argument("--interval", default="5m")
    p.add_argument("--range", dest="range_", default="60d")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default=None, help="resample to e.g. 15min")
    p.add_argument("--session-start", default="09:30")
    p.add_argument("--flat-by", default="11:30")
    p.add_argument("--split", type=float, default=0.5, help="in-sample fraction")
    args = p.parse_args()

    if args.source == "archive":
        from bot import binance_archive
        df = binance_archive.load_dataset(args.symbol, args.interval, args.start, args.end, verbose=False)
    else:
        df = data.fetch_yahoo(args.symbol, args.interval, args.range_)

    if args.resample:
        rule = args.resample.strip().lower()
        if rule.endswith("min"):
            pass
        elif rule.endswith("m"):
            rule = rule + "in"
        elif rule.endswith("h"):
            rule = rule + "our"
        else:
            rule = rule + "min"
        df = df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
        print(f"resampled to {rule}")
    days = sorted({d for d in df.index.date})
    cut = days[int(len(days) * args.split)]
    is_df = df[df.index.date < cut]
    oos_df = df[df.index.date >= cut]
    print(f"data: {df.index[0]} -> {df.index[-1]}  ({len(days)} sessions)")
    print(f"in-sample : {len(is_df)} bars, {len({d for d in is_df.index.date})} sessions")
    print(f"out-sample: {len(oos_df)} bars, {len({d for d in oos_df.index.date})} sessions")
    print("-" * 78)

    grid = {
        "or_minutes": [15, 30, 60],
        "stop_mode": ["opposite", "range"],
        "target_r": [1.5, 2.0, 3.0],
        "vwap_filter": [True, False],
    }
    keys = list(grid)
    costs = instruments.costs_for(args.symbol)
    rows = []
    for combo in itertools.product(*(grid[k] for k in keys)):
        kwargs = dict(zip(keys, combo))
        cfg = strategy.ORBConfig(
            **costs,
            session_start=args.session_start,
            flat_by=args.flat_by,
            **kwargs,
        )
        is_tr = run(is_df, cfg)
        oos_tr = run(oos_df, cfg)
        is_exp, is_n, is_pf = score(is_tr)
        oos_exp, oos_n, oos_pf = score(oos_tr)
        rows.append(
            {
                **kwargs,
                "is_trades": is_n,
                "is_exp": is_exp,
                "is_pf": is_pf,
                "oos_trades": oos_n,
                "oos_exp": oos_exp,
                "oos_pf": oos_pf,
                "decay": is_exp - oos_exp,
            }
        )

    res = pd.DataFrame(rows)
    res_sorted = res.sort_values("is_exp", ascending=False)
    print("TOP 8 BY IN-SAMPLE EXPECTANCY (the trap: best IS rarely survives)")
    print(
        res_sorted[
            ["or_minutes", "stop_mode", "target_r", "vwap_filter",
             "is_trades", "is_exp", "oos_trades", "oos_exp", "decay"]
        ].head(8).to_string(index=False)
    )
    print("-" * 78)
    print("TOP 8 BY OUT-OF-SAMPLE EXPECTANCY (what would have been picked without lookahead)")
    print(
        res.sort_values("oos_exp", ascending=False)[
            ["or_minutes", "stop_mode", "target_r", "vwap_filter",
             "is_trades", "is_exp", "oos_trades", "oos_exp", "decay"]
        ].head(8).to_string(index=False)
    )
    print("-" * 78)
    decay = res["decay"].mean()
    print(f"mean IS->OOS expectancy decay across {len(res)} configs: {decay:+.3f}R per trade")
    print(f"configs where OOS was positive: {(res['oos_exp'] > 0).sum()}/{len(res)}")
    print(
        "READ THIS: if the top-IS table and the top-OOS table disagree, the strategy\n"
        "has no real edge in this sample - you were reading noise. That is the result,\n"
        "not a failure of the script."
    )

    out = Path(__file__).resolve().parent.parent / "data" / "sweep_latest.csv"
    res.to_csv(out, index=False)
    print(f"\nsweep written to {out}")


if __name__ == "__main__":
    main()
