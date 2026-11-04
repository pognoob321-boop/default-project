"""Simple multi-asset rotation: SPY vs TLT.

Clean implementation, no clever state machine:
- Signal on close, fill at next open
- Hold one asset at a time (switch) or both (blend)
- Track positions and cash explicitly
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class RotConfig:
    lookback: int = 100
    mode: str = "switch"   # "switch" | "blend"
    fee_pct: float = 0.001
    slippage_pct: float = 0.0005


def run_rotation(spy_df: pd.DataFrame, tlt_df: pd.DataFrame, cfg: RotConfig):
    idx = spy_df.index.intersection(tlt_df.index)
    s = spy_df.loc[idx]
    t = tlt_df.loc[idx]
    n = len(idx)
    if n < cfg.lookback + 20:
        raise ValueError("not enough aligned bars")

    cs = s["close"].to_numpy()
    ct = t["close"].to_numpy()
    os_ = s["open"].to_numpy()
    ot = t["open"].to_numpy()

    # Momentum over lookback, known at close of day i
    mom_s = (pd.Series(cs).shift(1) / pd.Series(cs).shift(1 + cfg.lookback) - 1).to_numpy()
    mom_t = (pd.Series(ct).shift(1) / pd.Series(ct).shift(1 + cfg.lookback) - 1).to_numpy()

    cash = 1.0
    u_s = 0.0   # units SPY
    u_t = 0.0   # units TLT
    pos = None  # "spy" | "tlt" | "both" | None
    eq = np.empty(n)
    trades = 0

    for i in range(n):
        if i + 1 >= n:
            eq[i] = cash + u_s * cs[i] + u_t * ct[i]
            break

        # decide for next bar
        ms = mom_s[i]
        mt = mom_t[i]
        next_spy = False
        next_tlt = False
        if not np.isnan(ms) and not np.isnan(mt):
            if cfg.mode == "switch":
                if ms > mt:
                    next_spy = True
                else:
                    next_tlt = True
            else:  # blend
                if ms > 0:
                    next_spy = True
                if mt > 0:
                    next_tlt = True

        ni = i + 1
        # exit current positions at next open
        if pos == "spy" and u_s > 0 and not next_spy:
            cash += u_s * os_[ni] * (1 - cfg.slippage_pct)
            trades += 1
            u_s = 0.0
        if pos == "tlt" and u_t > 0 and not next_tlt:
            cash += u_t * ot[ni] * (1 - cfg.slippage_pct)
            trades += 1
            u_t = 0.0
        if pos == "both":
            if not next_spy and u_s > 0:
                cash += u_s * os_[ni] * (1 - cfg.slippage_pct)
                trades += 1
                u_s = 0.0
            if not next_tlt and u_t > 0:
                cash += u_t * ot[ni] * (1 - cfg.slippage_pct)
                trades += 1
                u_t = 0.0
        pos = None

        # enter new positions at next open
        if next_spy and u_s == 0:
            fee = cash * cfg.fee_pct
            fill = os_[ni] * (1 + cfg.slippage_pct)
            u_s = (cash - fee) / fill
            cash -= u_s * fill + fee
            trades += 1
        if next_tlt and u_t == 0 and cfg.mode == "blend":
            # split remaining cash
            fee = cash * cfg.fee_pct
            fill = ot[ni] * (1 + cfg.slippage_pct)
            u_t = (cash - fee) / fill
            cash -= u_t * fill + fee
            trades += 1
        elif next_tlt and u_t == 0 and cfg.mode == "switch":
            fee = cash * cfg.fee_pct
            fill = ot[ni] * (1 + cfg.slippage_pct)
            u_t = (cash - fee) / fill
            cash -= u_t * fill + fee
            trades += 1

        pos = "spy" if u_s > 0 and u_t == 0 else ("tlt" if u_t > 0 and u_s == 0 else ("both" if u_s > 0 and u_t > 0 else None))
        eq[i] = cash + u_s * cs[i] + u_t * ct[i]

    eq[-1] = cash + u_s * cs[-1] + u_t * ct[-1]
    return pd.Series(eq, index=idx, name="eq"), trades
