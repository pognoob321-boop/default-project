# trading-bot — completely free stack

A backtest + paper-trading bot for the ORB (Opening Range Breakout) strategy already
researched in `wiki/research/orb-trading-strategy.md`.

**Costs: $0.** No paid data, no paid broker, no paid course, no API keys, no signup.

## What runs right now (verified 2026-10-21 on this machine)

| Piece | Free source | Limit |
|---|---|---|
| US stock / futures bars | Yahoo Finance chart API | 1m = 7d, 5m = 60d, 1d = decades |
| Crypto bars | Binance public klines API | back to 2017, 1m+ |
| Backtest engine | own pandas code | no dependency risk |
| Paper trading | Binance public REST (live candles) | $0, no account |

Python 3.12 + pandas + numpy + requests + matplotlib were already installed.
This project adds **zero new pip packages**.

## Run it

```powershell
cd "C:\Users\ZBook\Documents\Default Project\trading-bot"

# 1. backtest ES futures, 30-min opening range, 2R target
python scripts\run_backtest.py --symbol "ES=F" --interval 5m --range 60d --or-minutes 30 --target-r 2

# 2. sweep parameters, with an in-sample / out-of-sample split
python scripts\sweep.py --symbol "ES=F" --interval 5m --range 60d

# 3. paper-trade crypto live (no account, no money)
python scripts\run_paper.py --symbol BTCUSDT --or-minutes 15

# 4. 9 years of free Binance 1m history, then the 9-year crypto test
python scripts\download_archive.py --symbol BTCUSDT --interval 1m --start 2017-08 --end 2026-09
python scripts\sweep.py --source archive --symbol BTCUSDT --resample 15min --session-start 00:00 --flat-by 23:50
python scripts\gross_vs_net.py --symbol BTCUSDT
python scripts\hypothesis_test.py --symbol BTCUSDT

# 5. trend following (Donchian) vs buy & hold, same data
python scripts\run_trend.py --resample 1D --entry-len 20 --exit-len 10
python scripts\run_trend_sweep.py --resample 1D
```

## The verdict so far (9 years of BTCUSDT, 100 configs, realistic fees)

| Strategy | Beats buy & hold OOS on Sharpe | on CAGR | on max drawdown |
|---|---|---|---|
| ORB (intraday, 36 configs) | 0/36 | 0/36 | — |
| Trend, daily (32 configs) | **0/32** | **0/32** | **23/32** |
| Trend, 4h (32 configs) | 3/32 | **0/32** | 21/32 |

- **Nothing beat simply holding Bitcoin** on return or risk-adjusted return, in either half of 9 years.
- The trend filter's one reliable benefit: worst-case loss cut from **-83% to as low as -18%**.
- Long-only always beat long+short.
- **Frequency, not the signal, is what killed the intraday strategy:** the daily system paid
  0.27-1.6 of equity in fees on 43 trades; the ORB paid 7,484 on 3,300 trades.

Do not forward-paper the ORB on crypto. The same code on ES costs 0.027R per trade instead
of 0.245R — that is the venue to test next (10 years of SPY/QQQ minute bars via a free
Alpaca key).

## Layout

```
bot/
  data.py       free data fetchers (Yahoo + Binance) with CSV cache
  strategy.py   ORB rules, session logic, no-lookahead guards
  backtest.py   R-based metrics, cost-aware, report printer
  paper.py      live paper engine (signal -> next-bar fill -> stop/target/fee)
scripts/
  run_backtest.py
  sweep.py
  run_paper.py
data/           cached bars, trade journals, sweep results
```

## The two rules that keep a bot honest

1. **No lookahead.** A decision on bar N may only use bars up to N. This repo
   shipped a version that entered trades *before* the opening-range window closed
   (using levels from the future). It produced a beautiful -45R backtest.
2. **Fill at a price you can actually get.** A signal on a closed candle is
   filled at the *next* candle's open. The first version entered at the signal
   candle's close — a price you only learn after that candle has closed — and
   printed +2.41R instead of -0.92R.
3. **Split before you tune.** Choose parameters on one half of the data, judge
   on the untouched other half. `scripts/sweep.py` does this automatically.
   In the first run, the best in-sample config was **-0.06R** out-of-sample.

## Current honest result (ES=F, 60 days of 5m bars, 2026-08-12 -> 2026-10-21)

48 trades, 37.5% win rate, -0.92R total, -0.019R/trade, PF 0.96, max DD 4.23R.

That is **not** an edge: 48 trades is under the 100-trade significance bar in the
repo's own research page, and 25 of those trades are out-of-sample. It is a
working pipeline that produces believable numbers, which is what Phase 1
is supposed to deliver.

An independent review pass found and fixed 4 critical + 8 major bugs
(lookahead in the index filter, unfillable entry prices, stops that could never
lose more than 1R, a fee charged on one side only, and more). The numbers above
are post-fix.

## Next free upgrades (no cost)

- **More data:** Alpaca free IEX key -> years of 1-minute US equity bars
  (`pip install alpaca-py`, free key, paper account, no KYC for paper).
- **Longer Yahoo window:** 5m is capped at 60 days; that is why the split
  above has only ~30 sessions per side.
- **Crypto backtest:** `bot/data.py::fetch_binance` paginates to 2017 with no key,
  which gives 5+ years of 1m data for a proper statistical test.
