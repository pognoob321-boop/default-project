"""Dual momentum (Antonacci GEM-style) on SPY + TLT + cash.

Rule:
  - If SPY momentum > 0 AND SPY momentum > TLT momentum: hold SPY
  - Else if TLT momentum > 0: hold TLT
  - Else: cash
  - Signal on close, fill at next open, 1x leverage, no shorting
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bot import data, metrics as M, trend


def main() -> None:
    spy = data.fetch_yahoo("SPY", "1d", "max").drop(columns=["open_time"], errors="ignore")
    tlt = data.fetch_yahoo("TLT", "1d", "max").drop(columns=["open_time"], errors="ignore")
    bpy = M.bars_per_year_from_data(spy)
    cut = pd.Timestamp("2010-01-01", tz=spy.index.tz)

    idx = spy.index.intersection(tlt.index)
    s = spy.loc[idx]
    t = tlt.loc[idx]
    n = len(idx)
    lookback = 200  # ~12 months

    cs = s["close"].to_numpy()
    ct = t["close"].to_numpy()
    os_ = s["open"].to_numpy()
    ot = t["open"].to_numpy()

    mom_s = (pd.Series(cs).shift(1) / pd.Series(cs).shift(1 + lookback) - 1).to_numpy()
    mom_t = (pd.Series(ct).shift(1) / pd.Series(ct).shift(1 + lookback) - 1).to_numpy()

    cash = 1.0
    u_s = 0.0
    u_t = 0.0
    pos = None
    eq = np.empty(n)
    trades = 0

    for i in range(n):
        if i + 1 >= n:
            eq[i] = cash + u_s * cs[i] + u_t * ct[i]
            break

        ni = i + 1
        # exits at next open
        if pos == "spy" and u_s > 0:
            cash += u_s * os_[ni] * 0.9999
            trades += 1
            u_s = 0.0
        if pos == "tlt" and u_t > 0:
            cash += u_t * ot[ni] * 0.9999
            trades += 1
            u_t = 0.0
        pos = None

        # entries at next open
        ms = mom_s[i]
        mt = mom_t[i]
        if not np.isnan(ms) and not np.isnan(mt):
            if ms > 0 and ms >= mt:
                fee = cash * 0.001
                fill = os_[ni] * 1.0001
                u_s = (cash - fee) / fill
                cash -= u_s * fill + fee
                trades += 1
                pos = "spy"
            elif mt > 0 and mt > ms:
                fee = cash * 0.001
                fill = ot[ni] * 1.0001
                u_t = (cash - fee) / fill
                cash -= u_t * fill + fee
                trades += 1
                pos = "tlt"
            # else: stay in cash

        eq[i] = cash + u_s * cs[i] + u_t * ct[i]

    eq[-1] = cash + u_s * cs[-1] + u_t * ct[-1]
    eq = pd.Series(eq, index=idx, name="dual_momentum")

    bh_spy = trend.buy_and_hold(spy, 0.001, 0.0001)
    bh_tlt = trend.buy_and_hold(tlt, 0.001, 0.0001)

    print("=== Dual Momentum (SPY vs TLT vs Cash), 12-month lookback ===\n")
    print(f"{'Strategy':<35} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>8} {'Trades':>7}")
    for name, es in [("Buy & hold SPY", bh_spy),
                     ("Buy & hold TLT", bh_tlt),
                     ("Dual momentum", eq)]:
        es_oos = es[es.index >= cut]
        m = M.metrics(es_oos, bpy)
        print(f"{name:<35} {m['cagr']*100:>7.1f}% {m['sharpe']:>7.2f} {m['max_dd']*100:>7.1f}% {'-':>7}")

    # Full history too
    print("\n=== FULL HISTORY ===")
    for name, es in [("Buy & hold SPY", bh_spy),
                     ("Buy & hold TLT", bh_tlt),
                     ("Dual momentum", eq)]:
        m = M.metrics(es, bpy)
        print(f"{name:<35} {m['cagr']*100:>7.1f}% {m['sharpe']:>7.2f} {m['max_dd']*100:>7.1f}% {'-':>7}")


if __name__ == "__main__":
    main()
