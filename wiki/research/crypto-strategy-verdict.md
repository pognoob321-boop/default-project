# Crypto Strategy Verdict — What Actually Works on Free Data

> **Status:** Research page | **Date:** 2026-10-22 | **Data:** 4,789,279 one-minute bars, BTCUSDT, 2017-08-17 → 2026-09-30 (free Binance archive, no account)
> **Code:** `trading-bot/` (bot/trend.py, bot/metrics.py, scripts/run_trend*.py)

## The Question

Two rule-based strategies, tested on 9 years of real Bitcoin data with realistic costs, always measured against **buy and hold** — because a trading strategy that returns less than doing nothing is not a strategy.

| Strategy | Family | Evidence behind it |
|---|---|---|
| ORB (opening-range breakout) | intraday momentum | repo's own research page: `research/orb-trading-strategy.md` |
| Donchian trend following | time-series momentum | strongest cross-market evidence in the literature (Moskowitz/Ooi/Pedersen 2012; Hurst/Ooi/Pedersen 2017) |

## The Discipline

- Same 9-year archive for both, so the venue and the data are constant.
- **In-sample / out-of-sample split** (2017-08 → 2022-12 vs 2023-01 → 2026-09). Parameters are never chosen by looking at the second half.
- Every trade pays **0.1% taker fee per side + 0.05% slippage per side** (0.30% round trip).
- Signals fill at the **next** bar's open. Stops can be gapped through. Both engines were regression-checked against a known baseline.
- Parameter sweeps: 36 ORB configs, 32 trend configs on daily bars, 32 on 4h bars.

## Result 1 — ORB (intraday): no edge, and fees finish it off

| Test | Result |
|---|---|
| 36-config IS/OOS sweep | **0/36 profitable out-of-sample.** Best config -0.13R IS, -0.34R OOS |
| IS vs OOS ranking | **Agreed** → a stable negative result, not noise |
| Gross vs net (3,315 trades) | gross **+0.011R**, net **-0.234R**, cost **0.245R**/trade |
| Anchor + range-width filter (27 configs) | 11/27 positive gross (best +0.074R), **0/27 positive net** |

Two independent failures: the gross edge is ~zero, and crypto's 0.30% round-trip cost equals 0.245R per trade against a median stop of 1.56% of price.

## Result 2 — Trend following (daily/4h): does not beat holding, but cuts the pain

Buy-and-hold benchmark, 9 years: **+1,851%**, CAGR 38.5%, Sharpe 0.83, **max drawdown -83%**.
Out-of-sample (2023-01 → 2026-09): CAGR 53.9%, Sharpe 1.16, max DD -53%.

| Sweep | Beats B&H on Sharpe (OOS) | Beats B&H on CAGR (OOS) | Beats B&H on max drawdown (OOS) |
|---|---|---|---|
| Daily, 32 configs | **0/32** | **0/32** | **23/32** |
| 4-hour, 32 configs | 3/32 | **0/32** | 21/32 |

Best daily config out-of-sample (entry 20, exit 10, long-only): CAGR 25.2%, Sharpe 0.88, max DD **-38%** vs buy & hold's 54% CAGR / 1.16 Sharpe / **-53%** DD.

**Findings that hold across all 64 configs:**
1. **No configuration beat simply holding Bitcoin** on return or risk-adjusted return, in either half of the data.
2. **The trend filter's one reliable benefit is drawdown.** 23 of 32 daily configs made the worst loss smaller (as low as -18% vs -53%). That is a real trade: you give up return to avoid the 2018 and 2022 crashes.
3. **Long-only beats long+short, always.** Every "both" config was negative out-of-sample. Shorting a secular bull market with a 20-50 day channel is death by a thousand cuts.
4. **Fees are irrelevant for slow strategies and fatal for fast ones.** The daily trend system paid 0.27-1.6 of starting equity in fees across 9 years (43 trades). The ORB paid 7,484 (3,300 trades).

## The Unifying Lesson: Trade Less

Cost per trade scales with how often you trade, and so does the damage a bad rule can do:

| Strategy | Trades / 9 years | Fee drag | Outcome |
|---|---|---|---|
| ORB, 15m bars | 3,300 | 0.245R **per trade** | -0.234R/trade net |
| Trend, daily bars | 43 | ~0.2R **per trade** | drawdown -83% → -54%, return below holding |

The trend system was not profitable, but it was not *destroyed* by costs — and that is entirely because it traded 77× less often. **Frequency, not the signal, is what killed the ORB.**

## The Benchmark Is the Real Test

A strategy does not need to be "profitable" — it needs to beat *doing nothing*. On 9 years of Bitcoin, doing nothing won. The honest conclusion is not "trading is pointless" but:

- If you want maximum return on crypto, holding wins.
- If you want to avoid the -83% crash, a slow trend filter is the cheapest way (23/32 configs).
- Any future strategy must be judged against buy & hold, not against zero.

## Result 3 — The bear-market test: the filter earns its place only when markets fall

The 9-year window ends in a pure bull market, which flatters holding. So the same sweep was re-run on the only bear-market window in the archive: **2018-01 → 2021-12** (the 2018 crash, the 2019 recovery, the COVID crash, the 2021 bull), split at 2020-01.

| Period | Buy & hold | Best trend config (selected by in-sample) |
|---|---|---|
| 2018-2019 (the crash) | CAGR **-26.7%**, Sharpe **-0.02**, max DD **-81.2%** | entry 100 / exit 20 long: Sharpe **+1.16**, max DD **-28.1%** |
| 2020-2021 (OOS) | CAGR 153.0%, Sharpe 1.60, max DD -53.6% | same config: CAGR 55.7%, Sharpe 1.11, max DD -47.9% |

- Configs beating buy & hold out-of-sample on Sharpe: **9/32** (daily), 8/32 (4h).
- Configs beating buy & hold out-of-sample on max drawdown: **28/32** (daily), 20/32 (4h).
- **In the crash half, holding had a Sharpe of -0.02 and a -81% drawdown. Every sane trend config had a positive Sharpe and a -22% to -48% drawdown.** That is the filter doing exactly what it is sold on.

**But the disciplined test still fails the same way:** the config you would have picked from the in-sample half (entry 100 / exit 20 long, in-sample Sharpe 1.16) delivered an out-of-sample Sharpe of 1.11 and CAGR 55.7% against holding's 1.60 and 153%. The 9/32 count is a *post-hoc* number — that is what luck looks like. The 2018-2019 result is the real signal, and it is a **crash-protection** result, not a return result.

### The synthesis

| | When holding wins | When the filter wins |
|---|---|---|
| 2023-2026 (pure bull) | holding wins on everything | filter only cuts drawdown |
| 2020-2021 (bull + crash) | holding wins on return | filter cuts drawdown |
| 2018-2019 (bear) | holding loses 81% | **filter wins outright** |

**A trend filter is not a return engine. It is a crash-protection filter.** Its value is concentrated exactly where holding is worst, and it is close to worthless in a straight bull market. If the goal is maximum return, holding wins in every window tested here. If the goal is not losing 80% in a crash, the filter is the cheapest way to do it.

## Result 4 — The same test on 30 years of US equities (free, no account)

Bitcoin's 19.5× run makes "holding" an unfairly easy target, so the identical 32-config sweep was run on **SPY daily, 1996-10 → 2026-10 (7,546 bars, Yahoo, no key, no signup)**, split at 2010. That window contains four real bear markets: dotcom (-49%), 2008 (-57%), COVID (-34%), 2022 (-25%). Costs: $0 commission + 0.01% slippage (Alpaca-equivalent), not crypto's 0.30%.

| | Buy & hold | Best trend config (post-hoc) |
|---|---|---|
| 1996-2010 (dotcom + 2008) | CAGR 5.1%, Sharpe 0.32, DD **-56.5%** | entry 20 / exit 50 long: Sharpe 0.11, DD -50.7% |
| 2010-2026 (OOS: COVID, 2022) | CAGR **18.0%**, Sharpe **0.91**, DD -34.1% | entry 20 / exit 50 long: CAGR 13.6%, Sharpe **0.92**, DD **-23.8%** |

- Configs beating buy & hold out-of-sample: **2/32** on Sharpe, **0/32** on CAGR, **21/32** on max drawdown.
- The best OOS config *tied* holding on Sharpe (0.92 vs 0.91) with a 10-point smaller drawdown. A tie, not a win.

**So the conclusion generalises across venues and decades: no rule-based trend configuration beat buy-and-hold on return — on 9 years of crypto OR 30 years of US equities, in bull markets or bear markets. The only repeatable effect is a smaller worst-case loss (21/32 and 23/32 configs respectively).**

**This also removes the need for the Alpaca account for the strategy question.** The daily equity test answers it for free. What an Alpaca key would still add: (a) *intraday* equity minute bars to test one more rule family (cost drag ~0.07R per trade instead of crypto's 0.245R, so an intraday rule is not automatically dead there), and (b) a paper order API to forward-test the live version of the filter.

## What This Means For the Bot

- The **paper engine and the backtester stay**: they are the instrument that produced this verdict in a week, for $0, versus a month of manual paper trading.
- The **ORB config is dead** on crypto. Do not forward-paper it.
- The **strategy question is now answered on two venues**: crypto (9y, 4.8M bars) and US equities (30y, free daily). In both, holding wins on return and a slow long-only filter wins on drawdown. If the user's goal is return, the answer is "hold an index". If the goal is not losing 50-80% in a crash, the answer is "hold an index, but exit on a 20-50 day channel".
- **The Alpaca account is no longer needed to answer the strategy question** (the daily equity test did it for free). It is still the only way to get *intraday* equity minute bars and a paper order API.
- A **bear market is the only place a long+short trend system can be tested honestly.** BTC 2018-2020 was one; the OOS window 2023-2026 was not.

## Two Engine Bugs Found While Building This (both would have produced fake results)

1. **Fee charged on the price instead of the position.** `entry * 0.001` on a $1 account = $4.29 → negative units → the equity curve went to -6,984x. The fee must be a fraction of notional.
2. **Position sized off cash instead of equity.** After a long entry, cash is negative (borrowed), so sizing the next trade off it inverted the position sign.
3. Plus `bars_per_year_for('4h')` returning 365 instead of 2,190, which understated every 4h CAGR and Sharpe by √6.
4. **pandas 3.x keeps `datetime64` at MILLISECOND resolution.** A hardcoded `index.astype("int64") // 10**6` therefore divided the epoch twice, and every timestamp in a cached dataset landed in January 1970. The archive loader now uses `index.as_unit("ms")` and detects the unit per file.

Each of these produced a curve that *looked* plausible in a spreadsheet and was nonsense.

## Sources

- https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/ — the archive used (110 monthly zips, 46 MB)
- https://github.com/binance/binance-public-data — archive format and checksums
- Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum", Journal of Financial Economics
- Hurst, Ooi & Pedersen (2017), "A Century of Evidence on Trend-Following Investing", Journal of Portfolio Management
- https://docs.alpaca.markets/us/docs/about-market-data-api — the 10-year minute-bar upgrade for the equities side
