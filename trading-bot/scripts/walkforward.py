"""Walk-forward: baseline vs enhanced strategy, on real data, honest OOS.

    python scripts/walkforward.py --source yahoo --symbol SPY --interval 1d --range 30y
    python scripts/walkforward.py --source archive --symbol BTCUSDT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import binance_archive, metrics as M, trend, walkforward as WF


def load(args) -> pd.DataFrame:
    if args.source == "archive":
        df = binance_archive.load_dataset(args.symbol, "1m", args.start, args.end, verbose=False)
        rule = args.resample
        if rule.endswith("d"):
            rule = rule.replace("d", "D")
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
    p.add_argument("--train-years", type=int, default=5)
    p.add_argument("--test-years", type=int, default=1)
    p.add_argument("--objective", default="sharpe", choices=["sharpe", "calmar", "cagr"])
    p.add_argument("--max-leverage", type=float, default=1.0)
    args = p.parse_args()

    df = load(args)
    bpy = M.bars_per_year_from_data(df)
    train_bars = int(args.train_years * bpy)
    test_bars = int(args.test_years * bpy)
    print(f"data: {len(df)} bars of {args.resample} | {df.index[0].date()} -> {df.index[-1].date()}")
    print(f"folds: train {args.train_years}y -> test {args.test_years}y, rolling forward")
    print(f"objective: {args.objective} | costs: fee {args.fee:.4%} + slip {args.slippage:.4%} per side\n")

    base = dict(fee_pct=args.fee, slippage_pct=args.slippage, side="long")

    # ---- A. baseline: plain Donchian, parameters fixed (no per-fold search) ----
    baseline_cfg = trend.TrendConfig(**base, entry_len=20, exit_len=10)

    # ---- B. enhanced: same rules + the new ingredients, parameters re-picked per fold ----
    enhanced_grid = {
        "entry_len": [10, 20, 50],
        "exit_len": [10, 20, 50],
        "atr_stop_mult": [0.0, 2.0, 3.0],
        "regime_len": [0, 100, 200],
        "trailing_atr": [0.0, 3.0],
        "vol_target": [0.0, 0.01],
    }
    enhanced_base = dict(base)
    enhanced_base.update(
        regime_slope=True,
        time_stop_bars=250,
        cost_filter_mult=2.0,
        dd_cut=0.15,
        max_leverage=args.max_leverage,
    )

    spec = WF.WalkForwardSpec(
        train_bars=train_bars,
        test_bars=test_bars,
        step_bars=test_bars,
        objective=args.objective,
    )

    print("running WALK-FORWARD enhanced strategy ...")
    res = WF.walk_forward(
        df, enhanced_grid, enhanced_base, spec, bpy,
        baseline_cfg=baseline_cfg, warmup_bars=250,
    )
    print(f"  {len(res.folds)} folds, {res.n_configs} configs searched per fold")

    # ---- C. baseline walk-forward with the SAME protocol (search over a small grid) ----
    base_grid = {"entry_len": [10, 20, 50], "exit_len": [10, 20, 50]}
    print("running WALK-FORWARD baseline (same protocol, fewer knobs) ...")
    res_base = WF.walk_forward(
        df, base_grid, base, spec, bpy,
        baseline_cfg=baseline_cfg, warmup_bars=250,
    )

    table = WF.report(res, bpy, f"{args.symbol} {args.resample} ENHANCED (walk-forward)")
    table2 = WF.report(res_base, bpy, f"{args.symbol} {args.resample} BASELINE (walk-forward)")

    print("\n=== per-fold choices (enhanced) — is the optimizer stable or thrashing? ===")
    for f in res.folds:
        print(f"  test {f['test_start'].date()} -> {f['test_end'].date()}  "
              f"params={f['params']}  test return {f['test_return']*100:+.1f}%")

    bh = M.metrics(res.benchmark, bpy)
    wf_m = M.metrics(res.oos_equity, bpy)
    print("\n=== VERDICT ===")
    print(f"buy & hold      OOS: CAGR {bh['cagr']*100:>6.1f}%  Sharpe {bh['sharpe']:>5.2f}  maxDD {bh['max_dd']*100:>6.1f}%")
    print(f"walk-forward    OOS: CAGR {wf_m['cagr']*100:>6.1f}%  Sharpe {wf_m['sharpe']:>5.2f}  maxDD {wf_m['max_dd']*100:>6.1f}%")
    beat = (wf_m["sharpe"] > bh["sharpe"]) and (wf_m["cagr"] > bh["cagr"])
    print(f"walk-forward beats buy & hold on BOTH Sharpe and CAGR: {beat}")

    out = Path(__file__).resolve().parent.parent / "data" / f"wf_{args.symbol}_{args.source}.csv"
    pd.DataFrame(
        {"walk_forward": res.oos_equity, "baseline": res.baseline, "buy_hold": res.benchmark}
    ).to_csv(out)
    print(f"\nequity curves written to {out}")


if __name__ == "__main__":
    main()
