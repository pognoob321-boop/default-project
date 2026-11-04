# Trading Bot — The Completely Free Plan

> **Status:** Feature/plan | **Date:** 2026-10-21 | **Goal:** Build and test a trading bot with $0 total spend — free data, free platform, free testing
> **Code:** `trading-bot/` in this repo (Python 3.12, pandas, zero new pip packages)

## The One-Line Answer

Free data (Yahoo chart API + Binance public klines) → own backtester in pandas → Binance paper engine → *never* real money until the numbers survive an out-of-sample split **and** 100+ forward paper trades.

## What Is Actually Free (verified 2026-10-21 from this machine)

| Need | Free option | Verified limit |
|---|---|---|
| US stock/futures bars | Yahoo Finance chart API, no key | 1m = 7-8d, any intraday = 60d, 1d = decades (2,517 bars over 10y for ES=F) |
| Crypto bars | Binance public klines, no key | 1,000 bars/call, paginates back to 2017 |
| **Crypto history (bulk)** | **data.binance.vision monthly zips, no key** | **110 months downloaded: 4,789,279 1m bars, 2017-08-17 → 2026-09-30, 46 MB, 5 min** |
| Backtest engine | own pandas code in `trading-bot/bot/` | no dependency risk on pandas 3.0.5 |
| Forward test (crypto) | Binance public REST → own paper engine | $0, no account |
| Forward test (equities) | Alpaca Paper Only | email signup only, no KYC/SSN, $100k virtual |
| Order-placement sandbox | Binance Spot Testnet | GitHub login only, no ID/phone/KYC, virtual funds, **own fake order book** |
| Charting + idea validation | TradingView Basic | $0 forever, **no order API** (webhooks = $12.95/mo → fails the $0 rule) |
| Local compute | this machine (Xeon E3-1505M, 32 GB RAM) | already has pandas/numpy/matplotlib |

**Dead ends confirmed:** Kraken futures demo decommissioned 2026-07-14. Bybit demo key requires a KYC'd 18+ mainnet account. OKX demo requires phone + 6-digit code. IBKR paper is only unlocked *after* a funded 18+ live account. Stooq CSV is behind a JS challenge wall (fails from this IP). Forex demo accounts (Pepperstone/IC Markets) need a mobile number and their MT4/MT5 demos expire in 60 days.

## The Plan (5 phases, each with a pass/fail gate)

### Phase 0 — Setup (1 day) ✅ DONE
Python 3.12.10, pandas 3.0.5, numpy 2.4.4, matplotlib, requests, git all present. Project scaffolded at `trading-bot/`. **Zero pip installs** — the data layer calls the JSON APIs directly.

### Phase 1 — Backtest harness (2 days) ✅ DONE
`bot/data.py` (fetchers + CSV cache), `bot/strategy.py` (ORB rules), `bot/backtest.py` (R-based metrics, cost-aware), `bot/instruments.py` (per-symbol costs), `scripts/run_backtest.py`.

**Honest result after an independent review pass** — ES=F, 60d of 5m bars, 30-min OR, midpoint stop, 2R target, VWAP filter:
**48 trades, 37.5% win rate, -0.92R total, -0.019R/trade, PF 0.96, max DD 4.23R, cost 0.027R/trade.**
Break-even to slightly negative. That is the correct answer for a 48-session sample of a raw ORB with no OR-width filter.

The same run **before** the review fixes printed **+2.41R, 43.8% win rate**. The difference was a bug, not a strategy: the backtest entered at the *close* of the breakout candle — a price you only learn after that candle has closed. Fixed to fill at the **next** candle's open.

### Phase 2 — Anti-curve-fit split (1 day) ✅ DONE
`scripts/sweep.py` sweeps 24 configs, tunes on the first half of the data, reports the untouched second half.

Result that teaches the whole lesson: the **best in-sample** config (OR 30m, midpoint, 3R) scored **-0.063R out-of-sample**. The **best out-of-sample** configs were all 15-minute OR, which had been *negative* in-sample. Mean IS→OOS decay: **-0.252R/trade**. Only 25 OOS trades exist, so none of this is significant.

> The top-IS table and the top-OOS table disagreeing IS the result. It means you were reading noise.

**Two filters turned out to be inert** (same numbers with them on and off):
- *VWAP alignment* — on ES with a 30-min OR, the session VWAP at 10:00 still sits inside the opening range, so a breakout above ORH is essentially always above VWAP. The filter rejects ~0% of signals. The research page calls it "the most important single filter" — on this instrument and this setup, it is not.
- *Index confirmation (SPY)* — SPY's direction vs its own VWAP agrees with the ES breakout direction on 1,393 of 1,393 evaluated bars. Same story.

### Phase 3 — Forward paper test (2-4 weeks) ✅ BUILT, needs runtime
`bot/paper.py` + `scripts/run_paper.py`: polls live free candles, signals on a closed candle, fills at the **next** bar's open with slippage + taker fee on both sides, applies stop/target/time-stop, journals every trade to `data/paper_journal.csv`.
Smoke test verified (BTCUSDT 1m, 15-min OR): signal 00:40 → fill 00:41 open → stop-out → **-3.33R**, and the reason is arithmetic, not a bug:

> -1.00R stop, -0.47R exit slippage, -1.86R fees (0.1% taker × 2 sides on a 0.11%-wide stop)
> **A midpoint stop is unviable on crypto at retail fees.** On ES the same stop is 30+ points wide against $4.20 of commission, so the same trade costs 0.03R instead of 1.86R.

**Gate to pass:** ≥100 forward paper trades, positive expectancy, max DD inside the risk budget. Log *skipped* setups too.

### Phase 4 — More data, then re-test (1 day) ✅ DONE — AND IT KILLED THE STRATEGY
Downloaded the full Binance archive: **4,789,279 one-minute bars, 2017-08-17 → 2026-09-30**, 110 monthly zips, 46 MB, no key, no signup, 5 minutes with 8 parallel threads. (Two data traps found on the way: Binance switched the timestamp unit from ms to µs in the 2026-04 files — assuming the wrong unit shifts data 1000×; and pandas 3.x refuses mixed fractional-second CSV timestamps without `format="ISO8601"`.)

**The 9-year result (BTCUSDT, 15m bars, 3,332 sessions, ~3,300 trades per config):**

| Test | Result |
|---|---|
| 36-config IS/OOS sweep | **0/36 configs positive out-of-sample.** Best config -0.13R/trade in-sample, -0.34R out-of-sample |
| IS vs OOS ranking | **Consistent**, unlike ES — so this is a stable negative result, not noise |
| Gross vs net (best config, 3,315 trades) | gross **+0.011R**/trade, net **-0.234R**/trade, cost **0.245R**/trade |
| Anchor + range-width filter test (27 configs) | **0/27 positive net.** 11/27 slightly positive gross; best gross **+0.074R** (13:30 UTC NY-open anchor, 15m OR, 0.5% width filter, 1,472 trades) — still negative after costs at -0.114R |

**Verdict: the ORB has no exploitable edge on BTCUSDT at retail spot fees.** Two separate reasons, and both are load-bearing:
1. The gross edge is ~0 (+0.011R over 3,315 trades; best case +0.074R, ~1-2 sigma). There is nothing to rescue.
2. Crypto's 0.30% round-trip cost (0.1% taker × 2 sides + 0.05% slippage × 2 sides) is **0.245R per trade** against a median stop of 1.56% of price. It would eat 2-3× the best gross edge even if that edge were real.

This is the most valuable thing the data upgrade bought: **instead of "I don't know", you now know it does not work** — and you know it with 3,300 trades instead of 48, so you do not need to spend weeks paper-trading it.

### Phase 4b — The cost structure is the real variable
Same strategy, different venue:

| Market | Round-trip cost | Cost per trade (1% stop) |
|---|---|---|
| ES futures | $4.20 + 1 tick = $16.70 on a 30-point stop | **0.027R** |
| BTCUSDT spot | 0.30% of price on a 1.56% stop | **0.245R** (9× worse) |

An edge of +0.05R survives on ES and dies on crypto. **That is why the next place to test is US equities, not crypto** — and why the Alpaca path (10 years of SPY/QQQ minute bars, $0 commission, ~0.002% slippage) is the right next step even though it needs an account.

### Phase 4c — A second strategy family on the same free data ✅ DONE
Tested **Donchian trend following** (time-series momentum — the only rule-based family with strong cross-market academic evidence) on the same 4.79M bars, 32 configs on daily bars and 32 on 4h bars, same IS/OOS split, same fees, always measured against **buy and hold**.

Full write-up: [Crypto Strategy Verdict](../research/crypto-strategy-verdict.md).

| | Beats B&H OOS on Sharpe | on CAGR | on max drawdown |
|---|---|---|---|
| Daily, 32 configs | **0/32** | **0/32** | **23/32** |
| 4-hour, 32 configs | 3/32 | **0/32** | 21/32 |

**Findings:** no configuration beat simply holding Bitcoin on return or risk-adjusted return, in either half of 9 years. The trend filter's one reliable benefit is **drawdown**: -83% (holding) → as low as -18%. Long-only always beat long+short. And the unifying lesson: the daily system paid 0.27-1.6 of equity in fees across 9 years (43 trades) while the ORB paid 7,484 (3,300 trades) — **frequency, not the signal, is what killed the intraday strategy.**

### Phase 3 — Forward paper test → **DEFERRED, and that is a result**
The paper engine (`bot/paper.py`) works and is free, but there is no point spending 2-4 weeks forward-testing a strategy that just failed 3,315 trades. It stays built for the *equities* version, where the cost structure is 10× kinder. **Gate unchanged:** never real money until 100+ forward paper trades pass on the version that survived the long backtest.

### Phase 5 — Real money (month 3+, only if every gate passed)
1 contract only (MNQ for futures), 0.5-1% risk per trade, money you can lose 100%. Same checklist. Nothing changes except it is real.

## The Review Pass (this is the part that matters)

An independent reviewer audited the code and returned **REJECT — 4 critical + 8 major bugs**. All were fixed and the numbers re-run. The headline bugs, because every one of them makes a bot lie:

1. **Entry at an unknowable price.** The backtest entered at the breakout candle's close. You cannot trade a price you only learn at that candle's close. Now: fill at the next open. (Changed the headline result from +2.41R to -0.92R.)
2. **Stops that can never lose more than 1R.** Every stop filled exactly at the stop price, so gap risk was invisible. Now: a gap fills at the open and the loss exceeds 1R (observed average -1.026R).
3. **Time stop fired late.** "Flat by 11:30" exited at the 11:30 bar's close. Now: exits at the 11:30 bar's open.
4. **VWAP anchored at midnight.** The baseline included overnight futures volume, so the "VWAP filter" was filtering on a meaningless number. Now: session-anchored.
5. **Lookahead in the index filter.** It read the index's *final* bar of the day (≈20:00 ET) to decide a 10:00 trade. Now: the last index bar at or before the decision time.
6. **`--confirm-minutes` was a no-op** — the confirmation-candle rule was never implemented.
7. **Paper engine deleted gap-through trades** (the worst trades never reached the journal → optimistic expectancy) and **charged the fee on one side only** (≈0.5R/trade missing).
8. **The still-forming Binance candle was treated as closed** → signals on partial closes.

The reviewer's own conclusion: *"the reported +0.05R/trade, PF 1.12 and the IS/OOS decay numbers all come from the code path carrying these bugs, so they are not decision-grade until those are fixed."* They were. The new numbers are the baseline.

## The Two Rules That Keep a Bot Honest

1. **No lookahead.** A decision on bar N may only use bars up to N. This repo shipped a version that entered trades *before* the opening-range window closed — it produced a beautiful **-45R** backtest (4% win rate). The `or_end` guard fixed it to **+2.41R, 43.8%**. Then the fill bug fixed it to **-0.92R, 37.5%**. Two bugs, two completely different "results" — and both were fake.
2. **Split before you tune.** Choose parameters on one half, judge on the untouched half. If the ranking flips, you have noise, not an edge.

## Two Traps Specific to This User's Situation

- **Crypto in Cambodia is a grey zone.** Binance's ToU requires 18+; *Binance Junior* (6 to under 18) explicitly has **no trading and no API keys**. Cambodian banks are prohibited from facilitating crypto transfers, and 16 exchange websites were blocked by the TRC in Nov 2024 (apps kept working). TradingView paper trading — no order API — is the safer sandbox. Verified from this machine: `api.binance.com`, `data-api.binance.vision` and `testnet.binance.vision` all respond, so the API path works even though the websites are blocked. **Note:** `api.binance.com` started resetting connections under repeated load, so the fetchers now rotate `api.binance.com` → `data-api.binance.vision` → `api-gcp.binance.com`.
- **A bot that trades its own backtest.** The most common failure is tuning the bot until it matches the historical data. The IS/OOS split is the cure; a 100-trade forward journal is the confirmation.

## Related Wiki Pages

- [ORB Trading Strategy](../research/orb-trading-strategy.md) — the strategy rules and backtest statistics this bot implements
- [Order Flow Crash Course](../research/orderflow-crash-course.md) — the concepts behind the VWAP and delta filters
- [Order Flow Beginner Guide](orderflow-beginner-guide.md) — the human-side path (paper trade by hand first)

## Sources

- https://docs.alpaca.markets/us/docs/paper-trading — "Anyone globally can create an Alpaca Paper Only Account! All you need to do is sign up with your email address." $100k default virtual balance.
- https://docs.alpaca.markets/us/docs/about-market-data-api — free Basic: IEX real-time, history since 2016, 200 hist calls/min.
- https://github.com/binance/binance-spot-api-docs/blob/master/testnet/rest-api.md — "API keys can be created on the SPOT Test Network upon logging in with your Github account"; virtual funds, own orderbook.
- https://github.com/binance/binance-public-data · https://data.binance.vision/ — bulk historical zips with checksums.
- https://www.tradingview.com/pricing — Basic is $0 but webhook automation starts at Essential $12.95/mo.
- https://support.kraken.com/articles/360024809011-api-testing-environment-derivatives — demo decommissioned 14 July 2026.
- https://github.com/ranaroussi/yfinance — "Intraday data cannot extend last 60 days".
- https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/bf4879710c904b991848972ec4818ba2cf9e4ce314c09adae84fa2750d3477f7.pdf — Binance ToU cl. 2.1(b): individuals must be at least 18.
- https://www.datawallet.com/crypto/best-crypto-exchanges-cambodia — TRC website blocks Nov 2024, apps unaffected; P2P-only funding.
