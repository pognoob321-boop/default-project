"""Parameter sweep for the trend strategy, with the same in-sample / out-of-sample
discipline as the ORB sweep - and a buy-and-hold benchmark in each half.

    python scripts/run_trend_sweep.py --resample 1D
    python scripts/run_trend_sweep.py --resample 4h
"""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive, metrics as M, trend


def load(args) -> pd.DataFrame:
    if args.source == "archive":
        df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
        rule = args.resample
        if rule.endswith("d"):
            rule = rule.replace("d", "D")
        df = df.resample(rule).agg(
            {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
        ).dropna()
        return df

    from bot import data
    df = data.fetch_yahoo(args.symbol, args.interval, args.range_)
    return df.drop(columns=[c for c in ("open_time",) if c in df.columns])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--source", default="archive", choices=["yahoo", "archive"])
    p.add_argument("--interval", default="1m")
    p.add_argument("--range", dest="range_", default="max")
    p.add_argument("--start", default="2017-08")
    p.add_argument("--end", default="2026-09")
    p.add_argument("--resample", default="1D")
    p.add_argument("--split", default="2023-01-01")
    p.add_argument("--fee", type=float, default=0.001)
    p.add_argument("--slippage", type=float, default=0.0005)
    p.add_argument("--atr-stop-mult", type=float, default=0.0)
    args = p.parse_args()

    df = load(args)
    bpy = M.bars_per_year_for(args.resample)
    split = pd.Timestamp(args.split, tz=df.index.tz)
    print(f"data: {len(df)} bars of {args.resample} | {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"split: {args.split}\n")

    bh_full = trend.buy_and_hold(df, args.fee, args.slippage)
    bh_is = bh_full[bh_full.index < split]
    bh_oos = bh_full[bh_full.index >= split]
    m_bh_is = M.metrics(bh_is, bpy)
    m_bh_oos = M.metrics(bh_oos, bpy)
    print("BUY & HOLD benchmark")
    print(f"  in-sample : CAGR {m_bh_is['cagr']*100:>6.1f}%  Sharpe {m_bh_is['sharpe']:>5.2f}  maxDD {m_bh_is['max_dd']*100:>6.1f}%")
    print(f"  out-sample: CAGR {m_bh_oos['cagr']*100:>6.1f}%  Sharpe {m_bh_oos['sharpe']:>5.2f}  maxDD {m_bh_oos['max_dd']*100:>6.1f}%\n")

    rows = []
    grid = list(itertools.product([10, 20, 50, 100], [5, 10, 20, 50], ["long", "both"]))
    for entry_len, exit_len, side in grid:
        cfg = trend.TrendConfig(
            entry_len=entry_len,
            exit_len=exit_len,
            side=side,
            fee_pct=args.fee,
            slippage_pct=args.slippage,
            atr_stop_mult=args.atr_stop_mult,
        )
        res = trend.run_trend(df, cfg)
        eq = res.equity
        m_is = M.metrics(eq[eq.index < split], bpy)
        m_oos = M.metrics(eq[eq.index >= split], bpy)
        rows.append(
            {
                "entry": entry_len,
                "exit": exit_len,
                "side": side,
                "trades": len(res.trades),
                "fees": res.fees_paid,
                "is_cagr": m_is["cagr"],
                "is_sharpe": m_is["sharpe"],
                "is_dd": m_is["max_dd"],
                "oos_cagr": m_oos["cagr"],
                "oos_sharpe": m_oos["sharpe"],
                "oos_dd": m_oos["max_dd"],
            }
        )
        r = rows[-1]
        flag = "  <-- beats B&H (sharpe)" if r["oos_sharpe"] > m_bh_oos["sharpe"] else ""
        print(
            f"entry={entry_len:>3} exit={exit_len:>2} {side:<4} trades={r['trades']:>3} "
            f"IS: sharpe {r['is_sharpe']:>5.2f} dd {r['is_dd']*100:>6.1f}%  |  "
            f"OOS: sharpe {r['oos_sharpe']:>5.2f} cagr {r['oos_cagr']*100:>6.1f}% dd {r['oos_dd']*100:>6.1f}%{flag}",
            flush=True,
        )

    out = pd.DataFrame(rows)
    out.to_csv("data/trend_sweep.csv", index=False)

    beat_sharpe = (out["oos_sharpe"] > m_bh_oos["sharpe"]).sum()
    beat_cagr = (out["oos_cagr"] > m_bh_oos["cagr"]).sum()
    beat_dd = (out["oos_dd"] > m_bh_oos["max_dd"]).sum()
    n = len(out)
    print(f"\n=== VERDICT ({args.resample}) ===")
    print(f"configs beating buy&hold OUT-OF-SAMPLE on Sharpe : {beat_sharpe}/{n}")
    print(f"configs beating buy&hold OUT-OF-SAMPLE on CAGR   : {beat_cagr}/{n}")
    print(f"configs beating buy&hold OUT-OF-SAMPLE on maxDD  : {beat_dd}/{n}  (less drawdown is better)")
    print("\nTOP 8 BY OUT-OF-SAMPLE SHARPE")
    print(out.sort_values("oos_sharpe", ascending=False).head(8).to_string(index=False))
    print("\nTOP 8 BY IN-SAMPLE SHARPE  (if this table disagrees with the one above, it is noise)")
    print(out.sort_values("is_sharpe", ascending=False).head(8).to_string(index=False))


if __name__ == "__main__":
    main()
