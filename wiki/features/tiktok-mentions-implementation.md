# TikTok Mentions & Links — Implementation Prompt

## One-line ask

Build a "TikTok mention" feature: when a user pastes a `vt.tiktok.com` (or `tiktok.com`) link into a chat/composer, detect it, unfurl the video metadata, and render it as an interactive mention card that opens the video in-app or in TikTok.

## Context (from your screenshot)

Four `vt.tiktok.com` shortlinks were sent at 8:35 PM in a messaging thread:

```
https://vt.tiktok.com/ZSgpA9gSy/
https://vt.tiktok.com/ZSgpA3D6v/
https://vt.tiktok.com/ZSgpAnqs9/
https://vt.tiktok.com/ZSgpAtBpc/
```

Each shortlink expands to one TikTok video. The feature must treat these the same way other apps treat `@username` mentions: a tappable rich preview inside the conversation.

## What the prompt should tell a developer to build

Copy/paste this block into your task tracker or LLM:

```
Feature: TikTok mentions / link unfurling

Scope:
- Detect TikTok URLs (vt.tiktok.com and tiktok.com) in message text and composer input.
- Resolve each shortlink to its canonical video (follow redirects / call oEmbed or your backend unfurl service).
- Extract: video ID, author @username, thumbnail, title/caption, duration, like count.
- Render one "TikTok mention card" per URL in the message bubble:
    * left: thumbnail with play badge
    * right: @username + video title (truncate to 2 lines)
    * bottom: TikTok music note icon + duration
- Tapping the card opens the video: prefer in-app WebView/TikTok embed; fallback to browser.
- Dedupe: if the same TikTok link is sent twice in a thread, render one card (or collapse repeats).
- Rate limit unfurls: max 5 URLs per message, cache metadata per video ID for 24h.
- Graceful degradation: if unfurl fails, render the plain link as a clickable text URL.

Deliverables:
1. URL regex + detection utility for vt.tiktok.com / tiktok.com.
2. Unfurl service (backend) or client fetch using TikTok oEmbed: https://www.tiktok.com/oembed?url=<encoded_url>
3. MentionCard UI component (thumbnail, @username, title, play badge, duration).
4. Composer integration: auto-detect on paste/send, insert mention entity instead of raw text where possible.
5. Message renderer: show MentionCard inside message bubbles.
6. Unit tests: detection, dedupe, truncation, failure fallback.

Acceptance criteria:
- [ ] Pasting https://vt.tiktok.com/ZSgpA9gSy/ into the composer shows a mention card, not just raw text.
- [ ] Card shows correct @username and thumbnail for that video.
- [ ] Tapping card opens the TikTok video.
- [ ] Sending the same link twice shows one card (deduped).
- [ ] Unfurl failure falls back to a clickable plain link without crashing.
```

## Suggested file layout (adapt to your stack)

```
src/
  lib/
    tiktok.ts          # URL regex, video ID extraction, dedupe key
    unfurl.ts          # fetch oEmbed metadata, cache, fallback
  components/
    MentionCard.tsx    # TikTok mention card UI
    MessageBubble.tsx  # renders MentionCard inside bubbles
  composer/
    TikTokDetector.ts  # paste/send detection
```

## TikTok oEmbed reference

Endpoint: `https://www.tiktok.com/oembed?url=<URL-encoded TikTok link>`
Returns JSON with: `title`, `author_name`, `author_url`, `thumbnail_url`, `provider_name`, `type`, `width`, `height`.
Note: TikTok oEmbed may require the full `tiktok.com/@user/video/123...` URL, so resolve `vt.tiktok.com` redirects first.

## Quick next step (< 2 min)

Pick your stack (web / React Native / Flutter / etc.) and paste the "Scope" block above into your task tracker or ask an LLM to generate the `tiktok.ts` detection utility first — that's the smallest verifiable piece.

**Done:** prompt written to `wiki/features/tiktok-mentions-implementation.md` — copy the Scope block into your dev task and start with the URL detection utility.