---
type: research
source: multiple (Stanford IR book, RFC 9309, Common Crawl, CourtListener opinions, arXiv, GitHub/PyPI APIs)
verdict: useful
updated: 2026-10-22
---

# Web Crawler: Deep Research

> Research date: 2026-10-22. Legal claims verified against primary court documents.
> Star counts, versions, and prices checked 2026-10-22 via GitHub REST API, PyPI JSON API, and official pricing pages.

## Summary

A web crawler is a loop — **fetch → parse → extract links → dedupe → schedule** — and almost every design decision is a decision about the *frontier* (the queue of discovered-but-unfetched URLs). At web scale the frontier becomes a distributed data structure, and the only unrelaxable global constraint is per-host politeness; the standard trick (partition by hostname) turns that global constraint into local bookkeeping. Two facts dominate the rest: **robots.txt is a request, not a lock** (RFC 9309 says so explicitly), and **the legal line in the US runs at technical access barriers, not at terms of service** — but 2025-2026 shifted the real risk to the DMCA §1201 anti-circumvention claim, which is where the live litigation is.

## Takeaways

1. **The whole "is scraping legal" question was answered in 2021-2022 and then reopened in 2025-2026.** CFAA risk is low for public pages. DMCA §1201 risk is now the live one. See "Legal" below.
2. **For a solo dev, the OSS stack wins.** Scrapy + Crawl4AI + trafilatura, all free, unlimited. Firecrawl's free tier is a 1,000-page demo, not a pipeline.
3. **Sitemap-first, BFS-fallback.** Mapping URLs before fetching them separates the cheap step from the expensive step and tells you the size of the job before you commit.
4. **llms.txt does not work.** 97% of published llms.txt files were never fetched by anything. Don't build on it.
5. **Rendering is ~5x the cost of fetching** and buys you only what JS actually gates.

---

## 1. Architecture: the frontier is the whole design

Canonical source: Manning, Raghavan & Schuetze, *Introduction to Information Retrieval* ch. 20 ("Web Crawling and Indexing") — https://nlp.stanford.edu/IR-book/html/htmledition/crawler-architecture-1.html

### The five modules

1. **URL frontier** — URLs yet to be fetched
2. **DNS resolution** — URL → server
3. **Fetch** — HTTP GET
4. **Parse** — extract text + links
5. **Duplicate elimination** — has this content/URL been seen?

### The two-tier frontier (Mercator design)

Front queues (F) implement **prioritization**; back queues (B) implement **politeness**. The back queues have two invariants: (i) non-empty while the crawl runs, (ii) contain URLs from a **single host** only. A heap tracks the earliest time each host may be contacted.

- **Priority** = f(change rate, page quality). A spam page that changes completely on every fetch must *not* get high priority — this is why quality and change rate are combined, not either alone.
- **Politeness heuristic**: wait an interval ~10x the last fetch duration to the same host. One connection at a time per host.
- **robots.txt is checked immediately before the fetch**, not at enqueue time — a URL can sit in the frontier for weeks and the rules can change. The robots.txt *cache* still works well because of locality of reference (most links on a page point to the same host).

### Distributed crawling: partition by host

Source: Najork, "Web Crawler Architecture" (EDS 2009) — https://marc.najork.org/papers/eds2009a.pdf

- The Google crawler / PolyBot design keeps the discovered-URL and pending-URL sets on a **single machine**. Conceptually simple, does not scale.
- Mercator and C-proc **partition URLs by hostname** across machines. Consequence: politeness decisions are made locally with zero cross-node communication, and since most hyperlinks point to the same host, most extracted links are checked against local data structures rather than shipped to peers.
- Scaling number: a 10-billion-page corpus refreshed every 4 weeks requires **>4,000 pages/sec**.

### Dedup data structures

- URL set → hash table. Hash must be collision-resistant; n URLs need log2(n) bits each.
- A 10-billion-URL frontier at ~100 chars/URL cannot live in RAM → disk-based FIFO, or a disk heap (too expensive: multiple seeks per op).
- Duplicate *content* (not URL) → checksums, or shingles for near-duplicates.
- Cache DNS lookups per host.

### Fetch history → priority

Attach per-URL metadata: discovery time, last fetch time, checksum/sketch of the document. This lets the crawler detect meaningful change and adjust priority. Freshness signals come from the *change rate* between crawls.

### Modern open-source frontier

- **url-frontier** (crawler-commons) — service-based frontier with `GetURLs`/`PutURLs`. URLs returned are "in transit" until updated or `delay_requestable` elapses, which prevents orphaned URLs if a client crashes. https://github.com/crawler-commons/url-frontier
- **meguri** (Go) — partition-per-host, 128-bit key with host in the high half, CRC-checked columnar `.meguri` checkpoint files, no external queue or DB. https://github.com/tamnd/meguri

---

## 2. Politeness, rate limiting, and robots.txt

### RFC 9309 (the actual standard)

https://www.rfc-editor.org/rfc/rfc9309.pdf — Sept 2022, Koster/Illyes/Zeller/Sassman (all Google).

Key normative rules:
- Robots file at `/robots.txt`, UTF-8, `text/plain`.
- Follow **at least 5 consecutive redirects**; if more → assume unavailable.
- **4xx (client error) → "unavailable" → MAY access any resource.**
- **5xx / network error → "unreachable" → assume complete disallow.** (The strictest rule and the most often forgotten.)
- If undefined for ~30 days → MAY treat as unavailable or keep using cache.
- Cache per standard HTTP cache control, typically **>24 hours**.
- Parsing limit **at least 500 KiB** (a DoS guard).
- **"These rules are not a form of access authorization."** (stated in the RFC itself)
- Crawlers MUST treat robots.txt as untrusted content.

### Politeness in practice

- `crawley` (Python): `crawl_delay`, `max_concurrency_per_host`, exponential backoff with jitter (~`0.5 * 2**attempt`, capped 30s), `Retry-After` header takes precedence.
- `Scrapling`: `concurrent_requests_per_domain`, `download_delay`, `autothrottle_enabled` (delay ← observed latency / target concurrency), `autothrottle_block_backoff` (doubles delay on 429/403/captcha — because blocks usually return *faster* than real content, so latency alone would speed you up into the block).
- `Scrapy`: `AUTOTHROTTLE_ENABLED` + `DOWNLOAD_DELAY`, `RETRY_HTTP_CODES`, `max_request_retries`.
- **Adaptive token bucket**: read `Retry-After` verbatim (delta-seconds or HTTP-date); read draft `RateLimit-Remaining`/`RateLimit-Reset` to recompute refill rate; clamp to your own ceiling — *a server advertising 10,000 req/min does not obligate you to use them*. Missing headers → hold current rate, never accelerate.
- **Google's own advice to site owners**: return 500/503/429 to reduce crawl rate, and include `Retry-After`. https://developers.google.com/crawling/docs/crawlers-fetchers/reduce-crawl-rate

### Error taxonomy (don't retry what can't succeed)

| Error | Type | Action |
|---|---|---|
| 429, 500, 502, 503, 504 | transient | back off + retry (honor `Retry-After`) |
| ConnectionError, ReadTimeout, ECONNRESET | transient | back off + retry |
| 400, 401, 403, 404, 410, 422 | permanent | log + skip |

Backoff = exponential + 0-500ms jitter (avoid thundering herd), cap 3-5 attempts.

---

## 3. JavaScript-rendered pages and the anti-bot arms race

### What breaks, and where

Stock headless Chromium leaks automation at **three layers simultaneously**:

1. **JavaScript layer** — `navigator.webdriver === true`, CDP artifacts, empty plugin arrays.
2. **Network/TLS layer** — bundled Chromium's JA3/JA4 fingerprint differs measurably from consumer Chrome; **HTTP/2 fingerprints and ClientHello extensions** are scored server-side *before any HTML is served*. A block happens at the edge, not in the DOM.
3. **IP layer** — datacenter/VPS ASNs are pre-scored as high-risk.

Observed real failure modes (Adobe's own engineering notes): `net::ERR_HTTP2_PROTOCOL_ERROR` on the *first* navigation, before any JS runs, against Akamai-managed origins. `--disable-http2` converts it to a 30s timeout. Working fallbacks: headed real Chrome (`headless:false, channel:'chrome'`) plus `--disable-blink-features=AutomationControlled` + `navigator.webdriver → undefined` per context; or a "route-fulfiller" pattern where a bare `request` API context (different TLS fingerprint) fulfills the page's network calls.

**The key operational lesson: validate the response, not the navigation.** A Cloudflare managed challenge makes `goto()` *resolve* with a 403/429/503 interstitial. A probe that only catches exceptions sails past it and the block surfaces later as a fatal capture error. Detect `cf-mitigated: challenge`, `cf-ray`, `server: cloudflare/akamai`.

### Defender side (Cloudflare)

- Per-customer anomaly detection: behavioral analysis (session traversal paths, request sequence, interaction with dynamic elements), client fingerprinting (JA4 against the site's own traffic baseline), content-agnostic detection. Flagged **138 million scraping requests on 5 beta zones in 24 hours**. https://blog.cloudflare.com/per-customer-bot-defenses/
- Global bot fingerprinting: 50 heuristics written since June, using HTTP/2 fingerprints and ClientHello extensions; a novel fingerprint appearing across many sites is treated as a botnet signature and blocked campaign-wide.

### Off-the-shelf anti-bot tooling

- **Crawlee**: browser-fingerprint generation on by default for `PlaywrightCrawler`/`PuppeteerCrawler`; `handleCloudflareChallenge` helper; **Camoufox** (stealthy Firefox build) for harder cases. https://crawlee.dev/js/docs/guides/avoid-blocking
- **Scrapling** `StealthyFetcher`: real Chrome option, CDP connection, WebRTC leak blocking, canvas noise, timezone-mismatch defeat, `solve_cloudflare=True` for JS/interactive/invisible Cloudflare challenges. https://scrapling.readthedocs.io/en/latest/fetching/stealthy.html
- **Adobe's documented "known-working fallback"**: headed real Chrome, with the note that stealth patching "becomes a part-time job" because fingerprint vendors update detectors roughly monthly.

### Cost

Rendering is a **separate, expensive unit of work**, not a free upgrade. Firecrawl's published credit model is the cleanest public proxy for the *price*: **1 credit = 1 page** for scrape/crawl/map, but **2 credits per browser-minute** for Interact, and **+4 credits/page** for JSON/Question/Highlight formats. So: fetch-only = 1 credit, rendered+structured ≈ 5 credits.

**Measured locally on 2026-10-22** (books.toscrape.com, Playwright 1.62.0 → `chrome-headless-shell`): the widely repeated "1-2 GB RAM per Chromium tab" figure is **wrong for headless shell** and appears to come from headed/full Chromium. Actual numbers on this machine (31.8 GB RAM, 8 logical cores):

| Config | Peak RAM | Wall clock | CPU |
|---|---|---|---|
| 1 context, sequential | ~190 MB | **0.35 s/page** (2.0 s first page, cold start) | ~1.2 CPU-sec/page |
| 3 contexts, concurrent | **572 MB** (7 processes) | 2.35-2.68 s/page | 4.9 CPU-sec for 4 pages |

For comparison, the user's **own Chrome was running 55 processes / 9,255 MB** at measurement time — 16x the crawler's entire footprint. Headless crawling is a rounding error next to an ordinary browser session. Practical rule: keep concurrency at 2-3 contexts, and only reach for headed real Chrome (the anti-bot fallback, ~400-500 MB/context) as a last resort.

---

## 4. LLM-era crawling

### The pipeline that replaced "crawl the whole web"

Stage 1 **Domain discovery** — sitemap-first (`/sitemap.xml`, `/sitemap_index.xml`, the `Sitemap:` line in robots.txt; recursively expand `<sitemapindex>`), BFS fallback. Capture `<lastmod>` to skip unchanged pages. Strip `utm_*`/tracking params; use a Bloom filter or Redis set for dedup.

Stage 2 **Render + normalize** — headless render for JS sites, then HTML→clean Markdown. **Boilerplate stripping cuts token consumption 40-60% per page** (nav, cookie banners, sidebars, footers inflate context and degrade vector retrieval). Preserve H1/H2/H3 hierarchy, tables, and code blocks.

Stage 3 **Incremental differential sync** ("Corpus-as-Manifest"):
1. Hash **normalized text**, not raw HTML (raw HTML contains hydration markers and CSRF tokens that change every request). Composite SHA-256 over normalized Markdown + page metadata + a config signature (e.g. chunk size).
2. Fingerprint match → skip chunking and embedding entirely (zero API cost for that document).
3. Fingerprint differs → delete old chunks by canonical ID, re-chunk, upsert.
4. URLs absent from a *complete* sitemap run → flag deleted. **Safety guard: deletion purges only run if discovery completed with verified success across the entire URL graph.**

### Agentic RAG acquisition

The retrieval loop: `Question → Plan → Search → Render/fetch → Normalize → Grade → Store or answer → Cite`. Each arrow is a contract — "Search returns candidates, not truth. Rendering returns page state, not a clean record. A vector store returns similar chunks, not necessarily sufficient evidence." Escalate cost: search → plain fetch → browser render only when client-side execution controls the relevant state. Record a retrieval envelope per document: `canonicalUrl, title, retrievedAt, contentHash, retrievalMethod, text`.

### Agentic web crawling is the new frontier (2025-2026 research)

- **Odysseys** (CMU, 2026): 200 long-horizon multi-site tasks on the live Internet. Best frontier models reach **44.5% success**; rubric-based evaluation beats binary pass/fail; **Trajectory Efficiency (rubric score per step) is only 1.15%** for frontier agents. https://arxiv.org/html/2604.24964
- **GTA** (Salesforce AI Research / USC, 2026): crawl → retrieval-based seeding → in-context task generation → quality control → executable trajectories. Decouples crawling from generation so you crawl once and generate tasks cheaply from a site graph. https://arxiv.org/html/2605.29218
- **Sodium** (UIUC, 2026): frames the web as a "latent database" to be instantiated. SodiumBench = 105 tasks from published papers; best of 6 agents = **46.5%**; SodiumAgent = **91.1%**. https://arxiv.org/html/2603.18447
- **Mango** (Purdue, 2026): do a *lightweight* BFS crawl first to build a global site structure, then treat URL selection as a multi-armed bandit (Thompson Sampling) to allocate a navigation budget. +26.8% over baseline on WebWalkerQA. https://arxiv.org/html/2604.18779
- **Parallel WebBench** (2026): 1,679 verified records; GRPO training raised *completion* from 50.7% to 96.0% but *binary accuracy stayed far below completion*. Three persistent failure modes: context-bound search loops, premature termination on partial answers, synthesis collapse after evidence was already retrieved. https://export.arxiv.org/pdf/2606.20724
- **Beyond BeautifulSoup** (2026): benchmarked LLM-powered scraping for novices across 35 sites / 5 security tiers. End-to-end agents succeed where scripted workflows fail (authenticated + CAPTCHA sites); but for static sites, agents cost **15-20x the runtime for no benefit** (10-20s vs under 2s). https://arxiv.org/html/2601.06301

**Takeaway: crawling is becoming a solved sub-problem feeding an unsolved agent problem.** The crawler gets you the corpus; the agent still fails at multi-page synthesis, and it fails by *stopping early*, not by not finding pages.

### AI crawlers and llms.txt

The AI web now has a **split between training crawlers and answer crawlers**:

| Token | Operator | Job |
|---|---|---|
| `GPTBot` | OpenAI | training |
| `OAI-SearchBot` | OpenAI | ChatGPT search / citations |
| `ChatGPT-User` | OpenAI | user-triggered fetch (may ignore robots.txt) |
| `ClaudeBot` | Anthropic | training |
| `Claude-SearchBot` | Anthropic | search / citations |
| `Claude-User` | Anthropic | user-triggered fetch (honors robots.txt) |
| `PerplexityBot` / `Perplexity-User` | Perplexity | citations / user fetch (User generally ignores robots.txt) |
| `Google-Extended` | Google | **token, not a crawler** — Gemini training + grounding opt-out |
| `Applebot-Extended` | Apple | token, not a crawler |
| `CCBot` | Common Crawl | open training corpus |
| `Meta-ExternalAgent` / `Meta-ExternalFetcher` | Meta | training / user fetch (Fetcher may bypass robots.txt) |
| `Amazonbot` | Amazon | training + product use |
| `Bytespider` | ByteDance | training; **compliance not guaranteed** |
| `cohere-ai` | Cohere | training |

Blocking a *training* bot opts you out of training but does **not** remove you from AI answers. Blocking an *answer* bot removes you from citations. Conflating the two is the standard mistake. `Claude-Web` and `anthropic-ai` are **retired** — write rules for the three current Anthropic tokens.

**llms.txt does not work.** Evidence:
- **Ahrefs, 137K domains**: 28% publish llms.txt; **97% of those files received zero traffic**; 96% of the fetches that did happen came from bots; **zero requests came from AI bots for llms.txt files that don't exist — they never go looking.** https://ahrefs.com/blog/llmstxt-study/
- **Readable, ~2M AI-agent requests/month: not a single request for llms.txt.** https://www.tryreadable.ai/blog/are-llms-txt-file-useful
- **Common Crawl, July 2026 crawl** (584,107 real llms.txt files): 99.23% Markdown, 49.90% follow the full spec shape, only **32.94%** carry the required per-link note, **22.56% contain no links at all**, 6.59% contain policy language the spec never defines (rate limits 3.05%, copyright 0.93%), and some contain **prompt injections**. Common Crawl's own conclusion: *"llms.txt is not like robots.txt. It grants nothing and blocks nothing, and no crawler is obliged to read it."* Of 32 files claiming to block CCBot, **none blocked it in robots.txt.** https://commoncrawl.org/blog/a-content-analysis-of-llms-txt-files-from-the-july-2026-crawl-archive
- **SE Ranking, ~300K domains**: no relationship between having llms.txt and AI citation frequency.

**Robots.txt compliance is itself imperfect**: TechnologyChecker.io (July 2026), 10,894 domains — **39.5% of GPTBot bans set in robots.txt were not honored at the network level.** robots.txt is step one, not the plan; enforce at the CDN/WAF layer.

---

## 5. Common Crawl — the corpus shortcut

- Two indexes: **CDXJ** (gzipped plain text, 3000-line blocks for random access) and **URL Index** (Apache Parquet, "Columnar Index" renamed). https://commoncrawl.org/url-index
- Current crawl: **CC-MAIN-2026-43** (Oct 2026). Monthly cadence. https://commoncrawl.org/latest-crawl
- Retrieval = `filename` + `offset` + `length` → HTTP **Range request** → the WARC record.
- Formats: **WARC** (raw HTTP response + request + metadata), **WAT** (computed metadata), **WET** (extracted plaintext).
- Query: Athena (SQL over Parquet), DuckDB, Spark, Polars, Arrow.
- **Browsers can now read it directly** — CORS `Access-Control-Allow-Origin: *` on `data.commoncrawl.org` and `index.commoncrawl.org` with `Range` exposed, so a static HTML page can do the full CDX→Range-fetch→decode pipeline, and DuckDB-WASM can run SQL over the Parquet index from a browser. https://commoncrawl.org/blog/you-can-now-build-directly-on-common-crawl-from-the-browser
- **Caveat:** `index.commoncrawl.org` is rate-limited and strict; for anything heavy use the URL Index on `data.commoncrawl.org`.
- WARC record IDs now use **Type 7 UUIDs** (RFC 9562) = Unix epoch seconds + random, so the timestamp is embedded in the ID.

---

## 6. Legal: verified case-by-case

> Verified against primary court documents on CourtListener / govinfo / supremecourt.gov on 2026-10-22.
> **Correction to a common claim: there was NO 2025 Supreme Court decision in hiQ.** The GVR was 2021.

### hiQ Labs v. LinkedIn — the canonical "public data is safe" case

- 9th Cir. 2019, 938 F.3d 985 — affirmed preliminary injunction.
- **Supreme Court granted cert and GVR'd June 14, 2021** (141 S. Ct. 2752) in light of *Van Buren v. United States*, 593 U.S. 374 (2021). Judgment vacated, remanded. https://www.supremecourt.gov/docket/docketfiles/html/public/19-1116.html
- 9th Cir. on remand, **April 18, 2022**, 31 F.4th 1180 — affirmed again. https://law.justia.com/cases/federal/appellate-courts/ca9/17-16783/17-16783-2022-04-18.html

**Holdings:**
- CFAA "without authorization" is **inapplicable where access is open to the general public**. "A computer hosting publicly available webpages has erected no gates to lift or lower in the first place." The CFAA is an **anti-intrusion** statute, not a misappropriation statute; the conduct it covers is "breaking and entering."
- **Terms of service ≠ authorization.** A cease-and-desist letter alone does not convert public access into unauthorized access.
- **Robots.txt, rate limits, and CAPTCHAs are not "authentication requirements"** and do not make public data non-public.
- **Proxy IP rotation ≠ "without authorization."** No affirmative duty to identify yourself by IP.
- Rule of lenity: the CFAA is both civil and criminal, so read it narrowly rather than "turn a criminal hacking statute into a sweeping Internet-policing mandate."
- **Limits:** this is a *preliminary injunction* ruling, not a final merits judgment; 9th Cir. only, not binding elsewhere; it does not cover logged-in data, and does not protect barrier evasion.

**Aftermath (Nov 3, 2022)** — N.D. Cal. cross-motions for summary judgment: hiQ **did breach** the User Agreement (directing creation of fake accounts + copying URL data), but triable issues remained on waiver (hiQ publicly discussed its scraping model at conferences attended by LinkedIn execs), when LinkedIn learned of the scraping, and whether LinkedIn had to act sooner. https://infobytes.orrick.com/2022-11-10/district-court-unclear-when-networking-site-became-aware-data-scraping/

### X Corp. v. Bright Data — the CFAA/DMCA split

3:23-cv-03698-WHA (N.D. Cal., Judge Alsup).

- **Oct 30, 2024** (733 F. Supp. 3d 832): dismissed X's **CFAA, CDAFA, and DMCA** claims. Terms ≠ authorization; anti-scraping measures (CAPTCHAs, rate limits, robots.txt) do not make public data non-public; proxy IPs ≠ unauthorized; and X's measures were **not "digital walls" controlling access to a public website** — "Bright Data doesn't break a lock, it uses an open path." Rate limiters and robots.txt were not "effective controls" under §1201(a)(3)(B). https://storage.courtlistener.com/recap/gov.uscourts.cand.415869/gov.uscourts.cand.415869.141.0.pdf
- **Nov 8, 2024**: reconsidered in part — the DMCA claim **could survive** at the pleading stage. Bright Data did not dispute circumventing X's robots.txt; allegations of **CAPTCHA cracking, fraudulent/automatically created accounts, and IP-spoofing to reset rate limiters** were sufficient to plead a DMCA claim ("textbook circumvention"). "The DMCA claim fails because X's technological measures are not 'digital walls'... " was narrowed to: a factual question that cannot be resolved on a 12(b)(6) motion. https://storage.courtlistener.com/recap/gov.uscourts.cand.415869/gov.uscourts.cand.415869.149.0.pdf
- **Settled**: settlement in principle June 21, 2025 → stipulation of dismissal with prejudice June 27, 2025 → End of Case Order July 1, 2025. Terms confidential. Not a merits ruling. https://storage.courtlistener.com/recap/gov.uscourts.cand.415869/gov.uscourts.cand.415869.357.0_1.pdf

### Meta Platforms v. Bright Data — logged-out scraping is outside the ToS

3:23-cv-00077-EMC (N.D. Cal., Judge Chen).

- **Jan 23, 2024**: granted Bright Data's motion for summary judgment on breach of contract; denied Meta's. "The Terms do not apply to Bright Data's logged-off scraping of publicly viewable data." The court also said that using automated tools to bypass **CAPTCHAs is not the same as accessing a password-protected website**, and that Meta's evidence (e.g. a 615M-record Instagram dataset sold for $860,000) did not prove logged-in scraping. https://storage.courtlistener.com/recap/gov.uscourts.cand.406956/gov.uscourts.cand.406956.181.0_1.pdf
- **Feb 23, 2024**: Meta dismissed its tortious-interference claim without prejudice and waived appeal. Bright Data stated it was **not a settlement** — "a total concession by Meta." https://techcrunch.com/2024/02/26/meta-drops-lawsuit-against-web-scraping-firm-bright-data-that-sold-millions-of-instagram-records/

### Reddit v. SerpApi / Perplexity — the DMCA §1201 front line (2025-2026)

1:25-cv-08736 (S.D.N.Y., Judge Engelmayer). Filed **Oct 22, 2025**. Defendants: Perplexity AI, SerpApi, Oxylabs UAB, AWMProxy. Claims: DMCA §1201(a)(1)(A) circumvention, §1201(a)(2)/(b) trafficking, NY unjust enrichment, unfair competition, civil conspiracy.

**July 31, 2026 opinion** — motions to dismiss **predominantly denied**:
- **Survives**: §1201(a)(1)(A) against both Perplexity and SerpApi; §1201(a)(2) against SerpApi; NY civil conspiracy against both.
- **Dismissed**: §1201(b) against SerpApi; unjust enrichment and unfair competition against both (preempted by the Copyright Act).
- Reddit has standing; the claims of circumventing **SearchGuard** (Google's Jan 2025 JavaScript challenge) are plausibly pleaded. Reddit's proof: a test post containing an uncommon hex string, served to Google and withheld elsewhere, appeared in Perplexity's answers within hours. Perplexity's citations of Reddit allegedly rose **40-fold** after its May 2024 cease-and-desist.
- https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2025cv08736/651592/104/ | https://www.reuters.com/legal/litigation/perplexity-ai-loses-bid-toss-reddit-lawsuit-over-data-scraping-2026-07-31/

**Related**: Reddit, Inc. v. Anthropic PBC, Case No. **CGC-25-625892** (Super. Ct., S.F. Cty., filed **June 4, 2025**) — breach of contract, unjust enrichment, trespass to chattels, unfair competition.

### Google v. SerpApi — the counterweight (July 20, 2026)

4:25-cv-10826-YGR (N.D. Cal., Judge Yvonne Gonzalez Rogers). Google sued SerpApi Dec 19, 2025 for bypassing **SearchGuard**.

**Motion to dismiss GRANTED (in part)**, discovery stayed, Google has 21 days to amend:
- **Without leave to amend** (permanent): §1201(a)(1)(A) and (a)(2) claims **to the extent they cover Search results containing no copyrighted content** — the DMCA does not protect works that are not copyrighted (*Lexmark*).
- **With leave to amend**: the claims covering results with a copyrighted Knowledge Panel component, because Google **failed to allege that SearchGuard was implemented "with the authority of the copyright owner"** as §1201(a)(3)(B) requires. That authorization cannot be inferred from the facts alleged.
- SerpApi's hiQ-based argument failed: **hiQ is a CFAA case, not a DMCA case** — inapposite for §1201 purposes.
- Court did **not** accept SerpApi's lack-of-standing argument: Google sufficiently alleged that SerpApi circumvented SearchGuard.
- https://storage.courtlistener.com/recap/gov.uscourts.cand.461513/gov.uscourts.cand.461513.42.0.pdf | https://searchengineland.com/google-loses-key-dmca-claims-against-serpapi-in-scraping-lawsuit-483185

**Read the two together:** Reddit's DMCA case survived because Reddit could plausibly tie its own content to the protection; Google's case died because Google could not tie *third-party licensed images inside a SERP* to a copyright owner who authorized SearchGuard. **The "authority of the copyright owner" requirement is the new dividing line.**

### The practical line (as the 2026 case law draws it)

| Behavior | CFAA risk | DMCA §1201 risk | Contract/ToS risk | Privacy (GDPR) risk |
|---|---|---|---|---|
| Public pages, no login, no barrier evasion | **Low** | Low | Low-Medium | Medium (if personal data) |
| Public pages + ToS prohibits scraping | Low | Low | **Medium-High** (contract, not CFAA) | Medium |
| Fake accounts / CAPTCHA solving / rate-limit evasion | **High** (cf. BrandTotal, Power Ventures) | **High** | High | Medium-High |
| Selling/reselling scraped datasets | Low on CFAA *use* | Medium-High | High | High |
| Profiling/inferring sensitive traits | Low | Low | Medium | **Highest** (GDPR Art. 9/14/21; CJEU C-21/23) |

**The single most useful sentence:** *CFAA exposure tracks technical access barriers and barrier evasion; contract exposure tracks ToS; privacy exposure tracks personal data and profiling.* From 2026 onward, add: *DMCA §1201 exposure tracks circumvention of a technological measure that effectively controls access to a copyrighted work, implemented with the copyright owner's authority.*

**Not verified in this pass:** *Reddit v. Scrapfly* (3:23-cv-03601) and *Reddit v. Dataprovider* — the specific holdings and current status were not confirmed against a primary document. Also unverified: the UK Data (Use and Access) Act 2025's "recognised legitimate interests" annex wording, and the current status of any Meta/Irish DPC or UK regulator action against scraping vendors.

### GDPR note (scraping PII)

- Lawful basis: Art. 6(1)(f) legitimate interests, which requires a balancing test (reasonable expectations, necessity, proportionality) — see CJEU **C-102/20** (Stadt Kaufland), **C-808/18** (KNLTB), **C-211/21** (Met_ctl).
- Scraping personal data triggers Arts. 14 (notice) and 15 (access), 17 (erasure), 21 (object), and Art. 9 + CJEU **C-21/23** (Bundeskartellamt v Meta) if you infer sensitive traits from public data.

---

## 7. Tooling (all versions/checked 2026-10-22)

| Tool | Version | Lang | License | Free tier | Best for | Weak at |
|---|---|---|---|---|---|---|
| **Scrapy** | 2.19.0 (2026-09-10) | Python ≥3.10 | BSD-3 | Unlimited | High-throughput structured crawling; item pipelines, autothrottle, feed exports, `SitemapSpider` | No JS rendering out of the box; Twisted reactor learning curve; not LLM-ready output |
| **Playwright** | v1.64.1 (2026-10-14) | TS/JS, Py, Java, .NET | Apache-2.0 | Unlimited | Cross-browser (Chromium/Firefox/WebKit), auto-wait, parallel contexts, network interception, tracing | **Not a crawler** — no frontier, no politeness, no dedup; heavy per-context RAM |
| **Puppeteer** | v25.15.0 (2026-10-20) | Node ≥18 | Apache-2.0 | Unlimited | Chrome/Chromium-first, CDP-level control | Chromium-only; not a crawler |
| **Crawlee** | v3.18.2 (2026-09-29) | TS/JS **+ Python** | Apache-2.0 | Unlimited | **The missing middle layer**: URL queue + scheduler + retries + proxy rotation + session/cookie mgmt + dataset export on top of Playwright/Puppeteer/HTTP | Still not "clean text for RAG" — you add extraction; more machinery than a script |
| **Crawl4AI** | 0.9.5 (2026-10-14) | Python ≥3.10 | Apache-2.0 | Unlimited | **LLM-ready output**: HTML→clean Markdown, structured extraction, `arun_many` concurrency, BM25/semantic chunking, adaptive crawling, sitemap+Common Crawl seeding | Heavier than plain HTTP (Playwright by default); version-tag inconsistency (`v0.9.5` vs `v.3.72` vs `vr0.6.3`) |
| **Firecrawl** | v2.11.0 (2026-06-19); tags at v2.11.586 (2026-10-22) | TS | **AGPL-3.0** | 1,000 credits/mo (≈1,000 pages), 2 concurrent browsers, **2 req/min on `/crawl`** | Zero-ops: `/scrape`, `/crawl`, `/map`, `/search`, `/parse`, `/monitor`; Markdown + JSON; SOC 2 Type II | AGPL for self-host; credit math confusing (JSON/Question/Highlight **+4 credits/page**); self-host needs your own LLM key for LLM modes |
| **Apify** | platform | JS/TS + Py SDK | proprietary (SDKs Apache-2.0) | $5 credit (**unverified** — pricing page not read) | Actor marketplace, managed proxies, scheduling, datasets, webhooks | Surprise bills; tiny free credit; per-page cost worse than Firecrawl for plain Markdown |
| **Scrapling** | v0.5 (2026-10-17) | Python ≥3.10 | BSD-3 | Unlimited | **Stealth/adaptive fetching**: TLS/JA3 impersonation, rotating proxies, auto-retry on blocks, Cloudflare solve, adaptive selectors that survive DOM changes | Python-only; not an LLM-ready extractor (pair with trafilatura); stealth ≠ guaranteed unblocking |
| **trafilatura** | v2.3.1 (2026-10-06) | Python ≥3.10 | Apache-2.0 | Unlimited | **Boilerplate removal**: HTML→clean main text/metadata, optional Markdown, SAX-based, very fast | Not a crawler or fetcher; no JS rendering; loses tables/structure |
| **SearXNG** | rolling tags | Python | AGPL-3.0 | Unlimited, self-host | Meta-search over 250+ engines → free private **search** API, replaces paid Brave/Bing/Serper/Exa | You run it; HTML output not LLM-ready; no crawl frontier |

GitHub stars on 2026-10-22: firecrawl 193,963 · playwright 98,244 · puppeteer 95,730 · scrapling 89,059 · crawl4ai 85,997 · scrapy 64,942 · searxng 38,713 · crawlee 26,217 · trafilatura 7,003.

### Free-tier arithmetic

- All OSS options: **unlimited**, limited only by your hardware.
- **Firecrawl free: 1,000 pages/month**, but only **2 concurrent browsers** and **2 req/min on `/crawl`** → a demo tier, not a pipeline tier. JSON/Highlight output drops you to ~200 pages/month. Paid: Hobby $19/mo (5,000 credits, 5 concurrent) → Standard $83/mo (100,000 credits, 25 concurrent) → Growth $333/mo (500,000) → Scale $599/mo (1,000,000). Pricing effective 2026-09-04; $75M Series B; launched "Alexandria". https://www.firecrawl.dev/pricing
- **Apify**: $5 free credit (**unverified**).

### Recommended stack for a solo dev

**Scrapy or Crawlee** (frontier, politeness, retries) → **Crawl4AI** (LLM-ready Markdown) → **trafilatura** (cheap non-JS pages) → **SearXNG** (seed URL discovery). All $0, all self-hosted, all unlimited. Add **Scrapling** only when you get blocked. Skip Firecrawl/Apify unless you want zero-ops and don't mind the per-page bill.

---

## 8. Build recipe (practical)

### Minimum viable crawler (~50 lines of real behavior)

1. **Map first, fetch second.** Try `/robots.txt` (read the `Sitemap:` line), `/sitemap.xml`, `/sitemap_index.xml`. Recurse `<sitemapindex>`. Only then fall back to BFS.
2. **Normalize URLs before dedup**: lowercase scheme/host, strip fragments, strip `utm_*`/`gclid`/`fbclid`/`ref`, one trailing-slash policy. Without this, "a 10,000-page site" is really 900 pages in costumes.
3. **BFS, not DFS.** Empirically on a 50-page site: BFS visited 48 depth-1 pages; DFS followed one pagination chain to depth 49 and visited zero category pages. **The URL sets did not overlap.** BFS is right for full-site audits; DFS only for a single known chain.
4. **BFS bounds are non-negotiable**: max depth 3-4, max page count hard cap (so a faceted search or calendar widget can't trap you in infinite generated URLs).
5. **Politeness**: 1 req/s per host default; `urllib.robotparser` cached per host; check `can_fetch(UA, url)` right before the fetch; identify with a real UA + contact URL; per-domain token bucket.
6. **Retries**: exponential + jitter, 3-5 cap, honor `Retry-After`; never retry 4xx except 429.
7. **Persisted frontier** (SQLite) for anything over a few minutes — in-memory crawlers lose state on crash.
8. **Extract**: `trafilatura` for text, `Crawl4AI` for LLM-ready Markdown. Validate a *response*, not a navigation, for bot blocks.

### The 40-line sketch that actually works

```python
import time, requests
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode
from bs4 import BeautifulSoup

TRACKING = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content","gclid","fbclid","ref"}

def normalize(url):
    p = urlparse(url)
    q = urlencode([(k,v) for k,v in parse_qsl(p.query) if k not in TRACKING])
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/") or "/", "", q, ""))

def crawl(start, max_depth=3, max_pages=500, delay=1.0):
    domain = urlparse(start).netloc.lower()
    queue = deque([(normalize(start), 0)])
    visited, results = set(), []
    while queue and len(results) < max_pages:
        url, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "MyCrawler/1.0 (+https://mysite.com/bot)"})
        except requests.RequestException:
            continue
        time.sleep(delay)
        if "text/html" not in resp.headers.get("content-type", ""):
            continue
        results.append(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            link = normalize(urljoin(url, a["href"]))
            if urlparse(link).netloc.lower() == domain and link not in visited:
                queue.append((link, depth + 1))
    return results
```

This does **not** render JavaScript, retry failures, run in parallel, or extract content. That gap is the sketch → production boundary.

### Pitfalls that bite

- `link not in queue` is O(queue length) — fine small, but the in-memory frontier starts eating RAM at 100k+ URLs. Use an on-disk frontier + Bloom filter.
- `noindex` is an **indexing** directive, not a crawling one — you must exclude it post-hoc.
- `rel=next` / `?page=N` pagination is not linked → invisible to BFS and usually absent from sitemaps.
- Infinite scroll and lazy images require JS execution; shadow DOM is invisible to `document.querySelector`; iframes are separate documents from separate origins and must be enumerated.
- Raw HTML changes every request (hydration markers, CSRF tokens) — hash the **normalized text**, not the HTML.

---

## 9. Common misconceptions, corrected

| Claim | Reality | Source |
|---|---|---|
| "robots.txt is legally binding" | It is a request. RFC 9309: "These rules are not a form of access authorization." 39.5% of GPTBot bans were not honored at the network level. | RFC 9309; TechnologyChecker.io 2026 |
| "The Supreme Court ruled on hiQ in 2025" | **No 2025 decision.** The GVR was June 14, 2021; the 9th Cir. reaffirmed April 18, 2022. | supremecourt.gov docket 19-1116 |
| "Scraping public data is always legal" | CFAA-safe, yes — but DMCA §1201 (circumvention), contract, and privacy law are live. Reddit v. SerpApi survived dismissal in July 2026. | S.D.N.Y. 1:25-cv-08736 |
| "llms.txt is how you get into AI answers" | 97% of llms.txt files are never fetched by anything. Zero AI-bot requests for files that don't exist. | Ahrefs 137K; Common Crawl 584K files |
| "robots.txt + rate limits make data protected" | Explicitly rejected in X v. Bright Data (Oct 30, 2024): "Bright Data doesn't break a lock, it uses an open path." | 733 F. Supp. 3d 832 |
| "Headless Chrome is enough" | Blocked at the edge, before any HTML, on TLS/H2 fingerprints and JA4. Use headed real Chrome or a managed browser. | Adobe engineering notes; OmniScrape guide; Cloudflare |
| "llms.txt ~10% adoption" | 28% of Ahrefs domains publish it, but 97% of those get zero traffic. Adoption ≠ use. | Ahrefs 2025-10 |
| "DFS is fine for site crawls" | On a 50-page site, BFS and DFS URL sets did not overlap. Use BFS. | hasdata benchmark |

---

## 10. Open questions (not verified in this pass)

1. *Reddit v. Scrapfly* and *Reddit v. Dataprovider* — specific holdings and current status.
2. UK Data (Use and Access) Act 2025 — exact "recognised legitimate interests" annex wording on AI training.
3. Any Meta / Irish DPC / UK ICO action against scraping vendors.
4. ~~First-party benchmark of Chromium RAM-per-tab and latency-vs-HTTP-GET~~ — **RESOLVED 2026-10-22, measured locally.** Headless shell: ~190 MB per context, 572 MB at 3 concurrent, 0.35 s/page sequential. The "1-2 GB per tab" figure applies to headed/full Chromium, not headless shell. See §3.
5. Crawl4AI `AdaptiveCrawler` exact stopping rule (docs not opened; "stops when answers converge" is inferred).
6. Apify pricing page (free tier dollar amount unverified).
7. The full 2025-2026 new-entrant sweep beyond Firecrawl Alexandria and SearXNG.
8. Whether Google's amended complaint in *Google v. SerpApi* (21 days from 2026-07-20) survives the "authority of the copyright owner" challenge.

## Related Pages

- [[research/agentic-ai]] — agent architecture these crawlers feed
- [[research/agentic-ai-building-guide]] — ReAct / tool-use / multi-agent patterns
- [[research/music-player-login-reliability]] — the same "no official API, structural fragility" pattern
- [[concepts/research-methods]] — how this page was produced
- [[features/deep-research-guide]] — the method behind the funnel
