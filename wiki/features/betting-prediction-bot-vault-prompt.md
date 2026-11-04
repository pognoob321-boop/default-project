# OpenCode Prompt — Betting, Prediction Markets & Botting Obsidian Vault (Deep Dive Vault #2)

Paste this whole block into a NEW OpenCode session. Do not merge with other sessions. This vault is ONLY for betting, prediction markets, and betting bots. It is separate from the Roblox vault.

================================================================================
ROLE
================================================================================

You are a quantitative betting analyst, prediction-market researcher, and betting-bot engineer. Build me a second, standalone Obsidian vault dedicated 100% to betting, prediction markets, market prediction, and botting automation. This is a DEEP DIVE — every market type, bot strategy, risk rule, and data source must have its own note, template, and place in the folder hierarchy.

================================================================================
LOCATION
================================================================================

Create the vault here (do NOT put it inside the existing wiki/ repo or inside the Roblox vault):

C:\Users\ZBook\Documents\Obsidian\Betting-Prediction-Bots

If that path is wrong for your machine, ask me once, then use the path I give you. Do not merge this vault into C:\Users\ZBook\Documents\Default Project.

================================================================================
FOLDER STRUCTURE (create every folder)
================================================================================

00 Inbox / Quick Capture
01 Prediction Markets (Polymarket, Kalshi, Manifold, etc.)
02 Sports Betting (odds, lines, steam, arbitrage, value)
03 Crypto Betting & Markets (on-chain betting, perp funding, prediction tokens)
04 Betting Bots & Automation (architecture, scrapers, executors, trackers)
05 Bankroll & Risk Management (Kelly criterion, unit sizing, drawdown rules)
06 Backtesting & Paper Trading (historical odds, simulation, results logs)
07 Data Sources & APIs (odds APIs, exchange APIs, scrapers, news feeds)
08 Legal & Compliance (jurisdiction, age, tax, terms of service)
Templates
Assets (screenshots, odds sheets, API docs)
Daily Notes

================================================================================
STARTER NOTES — create at least one deep note per folder
================================================================================

Each note must be substantive (200–600 words), use Obsidian wikilinks [[ ]] to other notes, and include YAML frontmatter where useful.

01 Prediction Markets — these notes minimum:
- How Prediction Markets Work (binary outcomes, share prices, implied probability)
- Polymarket (USDC, Polygon, conditional tokens, CLOB, liquidity mining)
- Kalshi (event contracts, regulation, CFTC, fee structure)
- Manifold Markets (play money, mana, subsidy, creator markets)
- Converting Odds to Implied Probability (decimal, fractional, American)
- Market Efficiency & Wisdom of Crowds (when markets are right/wrong)
- Event Resolution & Oracles (how outcomes are determined, dispute resolution)

02 Sports Betting — these notes minimum:
- Odds Formats (decimal, fractional, American/moneyline, Hong Kong, Indonesian, Malay)
- Line Movement & Steam Moves (sharp money, reverse line movement, steam chases)
- Arbitrage Betting (surebets, middle betting, Dutching, calculating arb %)
- Value Betting (expected value, true probability vs implied probability)
- Key Numbers (NFL 3 and 7, hooks, buying points)
- Player Props & Same-Game Parlays (correlation, payout math)
- Live/In-Play Betting (momentum, timeout effects, latency)
- Steam & Syndicate Plays (following sharp action, line services)

03 Crypto Betting & Markets — these notes minimum:
- On-Chain Betting Protocols (smart contract sportsbooks, decentralized oracles)
- Prediction Tokens & Outcome Tokens (binary tokens, payout at resolution)
- Perp Funding & Directional Betting (funding rates as sentiment, delta-neutral)
- Crypto Sportsbooks (BTC/ETH/USDC deposits, provably fair, KYC vs no-KYC)
- Wallet Security for Betting (hot vs cold, seed phrases, multisig)

04 Betting Bots & Automation — these notes minimum:
- Bot Architecture (scraper → signal engine → risk filter → executor → tracker)
- Odds Scraping (API vs HTML scraping, rate limits, user agents, proxies)
- Execution Layer (placing bets via API, bet slip automation, session management)
- Bankroll Tracker (ledger of bets, P&L by market, ROI, yield)
- Alerting (Telegram/Discord alerts for line moves, arb opportunities, bet placement)
- Error Handling (failed bets, partial fills, API downtime, bet rejection)
- Logging & Audit Trail (every bet: timestamp, odds, stake, market, outcome, P&L)

05 Bankroll & Risk Management — these notes minimum:
- Kelly Criterion (full Kelly, fractional Kelly, bankroll fraction formula)
- Flat Betting vs Variable Staking (unit size, confidence scaling)
- Max Drawdown Rules (stop-loss for bankroll, daily loss limits)
- Variance & Downswings (expected losing streaks, bankroll of ruin)
- ROI vs Yield vs Profit (definitions, how to calculate each)
- Portfolio of Markets (diversification across sports, books, bet types)

06 Backtesting & Paper Trading — these notes minimum:
- Historical Odds Collection (closing lines, opening lines, line movement archives)
- Paper Trading Ledger (fake bankroll, tracked bets, performance vs live)
- Backtest Template (market, selection, odds, stake, result, P&L, notes)
- Overfitting Checks (curve fitting, lookahead bias, survivorship bias)
- Performance Metrics (win rate, average odds, ROI, yield, Sharpe for betting)

07 Data Sources & APIs — these notes minimum:
- Odds Aggregators (API-football, Odds API, TheRundown, SportsRadar, Pinnacle API)
- Exchange APIs (Betfair API-NG, Betdaq, Matchbook)
- News & Injury Feeds (Twitter scraping, official injury reports, weather)
- Free vs Paid Data Tiers (rate limits, delay, historical depth)
- API Key Rotation & Usage Monitoring

08 Legal & Compliance — these notes minimum:
- Jurisdiction Rules (where betting is legal, age requirements)
- Tax on Gambling Winnings (reporting, deductibility, country-specific)
- Terms of Service (multi-accounting, bonus abuse, prohibited software)
- Responsible Gambling (self-exclusion, deposit limits, problem gambling resources)

================================================================================
TEMPLATES (create these notes under Templates/)
================================================================================

Templates/Bet Record.md — frontmatter:
- date, market, selection, odds, stake, book, bet_type, result, pnl, implied_prob, notes

Templates/Arbitrage Opportunity.md — fields: event, book_a, book_b, odds_a, odds_b, stake_split, arb_percent, guaranteed_profit, expiry

Templates/Bot Run Log.md — fields: timestamp, scraper source, signals found, bets placed, errors, bankroll_before, bankroll_after

Templates/Prediction Market Position.md — fields: market_id, outcome, shares, avg_price, current_price, implied_prob, resolution_date, unrealized_pnl

================================================================================
README.md at vault root
================================================================================

Purpose of vault, folder guide, how to log a bet, how to record an arb, how to backtest, how to use templates, bankroll rules, disclaimer (this is information, not financial advice; gambling involves risk).

================================================================================
WORKFLOW INSTRUCTIONS FOR YOU
================================================================================

1. Create folders and all starter notes.
2. Create all template notes.
3. Create vault README.md.
4. Show me the complete file tree you created.
5. Tell me exactly where to open this vault in Obsidian.

This is Vault #2. I will paste Vault #3 (GitHub + OpenCode teacher/engineer) into a separate session later. Do not combine Vault #1 and Vault #2.

End of prompt.