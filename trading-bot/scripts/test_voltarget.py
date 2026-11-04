"""Volatility-targeted Donchian trend on SPY.

Simple, robust: run Donchian 20/50, but scale position size by
min(1.0, target_vol / realized_vol). No leverage, no search, fixed params.
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
    bpy = M.bars_per_year_from_data(spy)
    cut = pd.Timestamp("2010-01-01", tz=spy.index.tz)

    # Daily returns for vol calc
    ret = spy["close"].pct_change()

    # Run Donchian 20/50 using the trend engine
    from bot import trend as T
    res = T.run_trend(spy, T.TrendConfig(entry_len=20, exit_len=50, side="long",
                                          fee_pct=0.0, slippage_pct=0.0001,
                                          max_leverage=1.0))

    eq = res.equity.copy()
    trades = res.trades.copy()

    # --- vol-target overlay: scale each trade's position by inverse vol ---
    # realized vol over prior 20 days, annualized
    rv = ret.rolling(20).std() * np.sqrt(bpy)
    target_vol = 0.15
    size_mult = (target_vol / rv).clip(0.0, 1.0)  # cap at 1x

    # Re-simulate with position sizing: on each entry, size = mult * equity
    cash = 1.0
    units = 0.0
    side = 0
    entry_price = np.nan
    entry_i = 0
    eq2 = np.empty(len(spy))
    stop = np.nan
    pending_exit = None
    pending_entry = 0

    o = spy["open"].to_numpy()
    h = spy["high"].to_numpy()
    lo = spy["low"].to_numpy()
    c = spy["close"].to_numpy()
    n = len(spy)
    entry_high = pd.Series(h).rolling(20).max().shift(1).to_numpy()
    entry_low = pd.Series(lo).rolling(20).min().shift(1).to_numpy()
    exit_high = pd.Series(h).rolling(50).max().shift(1).to_numpy()
    exit_low = pd.Series(lo).rolling(50).min().shift(1).to_numpy()

    for i in range(n):
        # pending exit at this open
        if pending_exit is not None and side != 0:
            fill = c[i] * (1 - 0.0001) if side == 1 else c[i] * (1 + 0.0001)
            fee = abs(units) * fill * 0.0
            cash += units * fill - fee
            units = 0.0
            side = 0
            stop = np.nan
            pending_exit = None

        # pending entry at this open
        if pending_entry != 0 and side == 0 and i > 0:
            ns = pending_entry
            pending_entry = 0
            fill = o[i] * (1 + 0.0001) if ns == 1 else o[i] * (1 - 0.0001)
            equity_now = cash + units * c[i]
            # vol-target size
            mult = float(size_mult.iloc[i]) if not np.isnan(size_mult.iloc[i]) else 1.0
            notional = equity_now * mult
            units = notional / fill
            cash -= units * fill
            side = ns
            entry_price = fill
            entry_i = i

        # channel exit check on close
        if side == 1 and not np.isnan(exit_low[i]) and c[i] < exit_low[i]:
            pending_exit = "channel"
        elif side == -1 and not np.isnan(exit_high[i]) and c[i] > exit_high[i]:
            pending_exit = "channel"

        # entry signal on close
        if side == 0 and pending_entry == 0 and i + 1 < n:
            if not np.isnan(entry_high[i]) and c[i] > entry_high[i]:
                pending_entry = 1

        eq2[i] = cash + units * c[i]

    eq2 = pd.Series(eq2, index=spy.index, name="vol_targeted_donchian")

    print("=== SPY Daily, Donchian 20/50, vol-targeted (target 15% vol, max 1x) ===")
    print(f"\n{'Strategy':<35} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>8} {'Trades':>7}")
    for name, es in [("Buy & hold SPY", trend_buy_hold(spy, 0.0, 0.0001)),
                     ("Donchian 20/50 fixed 1x", res.equity),
                     ("Donchian 20/50 vol-targeted", eq2)]:
        es_oos = es[es.index >= cut]
        m = M.metrics(es_oos, bpy)
        print(f"{name:<35} {m['cagr']*100:>7.1f}% {m['sharpe']:>7.2f} {m['max_dd']*100:>7.1f}% {'-':>7}")

    print(f"\nBuy&hold SPY OOS CAGR: {M.metrics(trend_buy_hold(spy,0.0,0.0001)[cut:], bpy)['cagr']*100:.1f}%")


def trend_buy_hold(df, fee_pct, slippage_pct):
    from bot import trend
    return trend.buy_and_hold(df, fee_pct, slippage_pct)


if __name__ == "__main__":
    main()
