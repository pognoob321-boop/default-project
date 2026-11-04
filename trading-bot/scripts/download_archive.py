"""Download the full Binance archive for a symbol/interval into data/archive/.

    python scripts/download_archive.py --symbol BTCUSDT --interval 1m --start 2017-08 --end 2026-09
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive as ba


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interval", default="1m")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    args = p.parse_args()

    t0 = time.time()
    df = ba.build_dataset(args.symbol, args.interval, args.start, args.end)
    out = ba.ARCHIVE_DIR / f"{args.symbol.upper()}_{args.interval}_{args.start}_{args.end}.csv"
    df.to_csv(out)
    print(
        f"DONE bars={len(df)} {df.index[0]} -> {df.index[-1]} "
        f"in {time.time()-t0:.0f}s -> {out}",
        flush=True,
    )


if __name__ == "__main__":
    main()
