"""Run the free paper-trading bot (no broker, no account, no cost).

Normal use (forward test, keep it running):
    python scripts/run_paper.py --symbol BTCUSDT --session-start 00:00

Smoke test (replays the last ~300 minutes of 1m candles, separate files so it
never pollutes the real journal):
    python scripts/run_paper.py --smoke
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import paper


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interval", default="1m")
    p.add_argument("--session-start", default="00:00")
    p.add_argument("--or-minutes", type=int, default=15)
    p.add_argument("--stop-mode", default="midpoint", choices=["midpoint", "opposite"])
    p.add_argument("--target-r", type=float, default=2.0)
    p.add_argument("--no-vwap-filter", action="store_true")
    p.add_argument("--flat-by", default="23:50")
    p.add_argument("--fee", type=float, default=0.001)
    p.add_argument("--slippage", type=float, default=0.0005)
    p.add_argument("--poll-seconds", type=int, default=15)
    p.add_argument("--smoke", action="store_true", help="replay last bars into temp files")
    args = p.parse_args()

    if args.smoke:
        paper.STATE_PATH = paper.DATA_DIR / "paper_state_smoke.json"
        paper.JOURNAL_PATH = paper.DATA_DIR / "paper_journal_smoke.csv"

    cfg = paper.PaperConfig(
        symbol=args.symbol,
        interval=args.interval,
        session_start=args.session_start,
        or_minutes=args.or_minutes,
        stop_mode=args.stop_mode,
        target_r=args.target_r,
        vwap_filter=not args.no_vwap_filter,
        flat_by=args.flat_by,
        taker_fee=args.fee,
        slippage_pct=args.slippage,
        poll_seconds=args.poll_seconds,
    )

    paper.run_forever(cfg, max_bars=300 if args.smoke else None)


if __name__ == "__main__":
    main()
