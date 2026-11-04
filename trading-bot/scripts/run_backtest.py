"""Free-stack CLI: fetch data -> run ORB backtest -> print R-based report.

Examples
--------
    python scripts/run_backtest.py
    python scripts/run_backtest.py --symbol NQ=F --or-minutes 15 --target-r 3
    python scripts/run_backtest.py --symbol SPY --range 1y --or-minutes 30
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import backtest, data, instruments, strategy


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="ES=F")
    p.add_argument("--source", default="yahoo", choices=["yahoo", "archive"])
    p.add_argument("--interval", default="5m")
    p.add_argument("--range", dest="range_", default="60d")
    p.add_argument("--start", default=None, help="archive start YYYY-MM")
    p.add_argument("--end", default=None, help="archive end YYYY-MM")
    p.add_argument("--or-minutes", type=int, default=30)
    p.add_argument("--confirm-minutes", type=int, default=5)
    p.add_argument("--stop-mode", default="midpoint", choices=["midpoint", "opposite"])
    p.add_argument("--target-r", type=float, default=2.0)
    p.add_argument("--target-mode", default="r", choices=["r", "measured"])
    p.add_argument("--session-start", default="09:30")
    p.add_argument("--flat-by", default="11:30")
    p.add_argument("--no-vwap-filter", action="store_true")
    p.add_argument("--index", default="SPY")
    p.add_argument("--index-confirm", action="store_true")
    p.add_argument("--min-or-width", type=float, default=None)
    p.add_argument("--max-or-width", type=float, default=None)
    p.add_argument("--commission", type=float, default=None, help="round-turn commission, $")
    p.add_argument("--slippage", type=float, default=None, help="slippage in price points")
    p.add_argument("--point-value", type=float, default=None, help="$ per point")
    p.add_argument("--refresh", action="store_true")
    args = p.parse_args()

    defaults = instruments.costs_for(args.symbol)
    commission = args.commission if args.commission is not None else defaults["commission_per_rt"]
    slippage = args.slippage if args.slippage is not None else defaults["slippage_points"]
    point_value = args.point_value if args.point_value is not None else defaults["point_value"]

    if args.source == "archive":
        from bot import binance_archive
        print(f"fetching archive {args.symbol} {args.interval} {args.start}..{args.end} ...")
        df = binance_archive.load_dataset(args.symbol, args.interval, args.start, args.end, verbose=False)
    else:
        print(f"fetching {args.symbol} {args.interval} range={args.range_} ...")
        df = data.fetch_yahoo(args.symbol, args.interval, args.range_, refresh=args.refresh)
    print(f"  bars={len(df)}  {df.index[0]} -> {df.index[-1]}")

    index_by_session = None
    if args.index_confirm:
        if args.source == "archive":
            from bot import binance_archive
            idx = binance_archive.load_dataset(args.index, args.interval, args.start, args.end, verbose=False)
        else:
            idx = data.fetch_yahoo(args.index, args.interval, args.range_, refresh=args.refresh)
        index_by_session = strategy.split_sessions(idx)
        print(f"  index {args.index} bars={len(idx)}")

    cfg = strategy.ORBConfig(
        session_start=args.session_start,
        or_minutes=args.or_minutes,
        confirm_minutes=args.confirm_minutes,
        stop_mode=args.stop_mode,
        target_r=args.target_r,
        target_mode=args.target_mode,
        vwap_filter=not args.no_vwap_filter,
        index_confirm=args.index_confirm,
        flat_by=args.flat_by,
        min_or_width=args.min_or_width,
        max_or_width=args.max_or_width,
        commission_per_rt=commission,
        slippage_points=slippage,
        point_value=point_value,
    )

    trades = strategy.generate_trades(df, cfg, index_by_session=index_by_session)
    trades_df = backtest.apply_costs(trades, cfg)
    stats = backtest.summarize(trades_df, cfg)
    backtest.print_report(stats, cfg)

    out = Path(__file__).resolve().parent.parent / "data"
    out.mkdir(exist_ok=True)
    trades_df.to_csv(out / "trades_latest.csv")
    print(f"trades written to {out / 'trades_latest.csv'}")


if __name__ == "__main__":
    main()
