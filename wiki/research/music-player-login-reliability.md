---
title: Music Player Login Reliability & Playlist Portability
type: research
date: 2026-10-17
tags: [music, youtube-music, spotify, api, inner-tube, windows]
---

# Music Player Login Reliability & Playlist Portability

Research triggered by: repeated login failures with YouTube Music client apps (Liner API 503, SimpMusic empty library).

## The root cause of every YT Music client breaking

**YouTube Music has no official public API.** Its library — Liked Music, saved albums, saved-from-other-creators playlists, Listen Again — is reachable only through the private InnerTube API at `music.youtube.com/youtubei/v1/*` (client `WEB_REMIX`), authenticated with stolen browser session cookies.

Verified by replaying the actual session cookie against Google's own endpoint:
`browseId=FEmusic_library_landing` returned HTTP 200 with the body
*"Explore your favorites / Sign in to access tracks that you liked or saved"* —
the logged-out page. Same result for gl=KH, US, CA, TH, VN.

**Consequence:** any app reading a YT Music library is cookie-scraping. Google rotates sessions, the cookie dies, the app shows a stale cached account and returns empty. This is structural, not a bug in any one app.

## What the official APIs actually cover

| Platform | Official API | Can read your library | Can write playlists |
|---|---|---|---|
| YouTube Music (library) | none | no | no |
| YouTube (created `PL…` playlists) | Data API v3 | yes | yes (`playlists.insert`, `playlistItems.insert`) |
| Spotify | Web API | yes | yes (`POST /me/playlists`, `POST /playlists/{id}/items`) |

- Data API v3 `playlists.list` returns only playlists **you created** — not Watch Later (`playlistOperationUnsupported`), not Liked Music, not saved-from-others.
- `search.list` is capped at 100 calls/day. `playlists.insert` / `playlistItems.insert` cost 50 units each.
- Spotify `GET /playlists/{id}/tracks` is deprecated → `GET /playlists/{id}/items`. Writes cap at 100 URIs/request.
- Spotify **does** expose `isrc` as an official search filter (removed Feb 2026, reverted Mar 2026). Exact-match by ISRC works.
- Spotify never releases audio. `preview_url` (30s) is deprecated. Web Playback SDK requires listener-side Premium.

## ytmusicapi now supports real Google OAuth

Not cookie scraping. Uses the **"TVs and Limited Input devices"** Google OAuth flow with a YouTube Data API client ID/secret, producing `oauth.json` with a refresh token.

- Docs: https://ytmusicapi.readthedocs.io/en/latest/setup/oauth.html
- `sigma67/ytmusicapi`, ~3,070 stars, pushed 2026-10-12
- This is the only durable programmatic route into a YT Music library.

## Windows client landscape (verified 2026-10-17)

| App | Windows | Auth | Verdict |
|---|---|---|---|
| **Spotify desktop** | yes (Store, installed) | real OAuth | durable |
| **Apple Music** | yes (Store, Win11) | real OAuth | durable; official inbound transfer from YT Music via Takeout |
| **YT Music PWA** | yes (Edge install) | real OAuth | durable; no official YT Music desktop app exists |
| `ytmdesktop` / `ytmdesktop2` / `th-ch` | yes | Electron webview OAuth | mediocre; reuses real session, but webview-bound |
| **SimpMusic** | yes | **cookie paste** | breaks; issue #2688 "sign in not working" filed 2026-10-16 |
| **YTubic** | yes | login optional, yt-dlp for playback | playback survives, library does not |
| Metrolist / InnerTune / OuterTune / ViMusic | Android only | cookie scrape | N/A on Windows |

**Nobody ships a reliable third-party Windows YT Music client.** The category is structurally broken.

## Transfer services (all cookie-scrape the destination)

- **Soundiiz** — free tier 200 tracks/transfer, 1 playlist at a time. Premium $39/yr or $5/mo. Only service with open re-importable formats (CSV, M3U, JSON, XML, XSPF, WPL, NML, PLS).
- **TuneMyMusic** — free 500 tracks. $2/mo annual. Claims ISRC matching.
- **FreeYourMusic** — free 600 songs.

**Match quality is metadata-based, not audio-fingerprinting.** Soundiiz's own doc lists failure modes: live vs studio, remix vs original, remastered vs original, same-name-artist collisions. ~95% claimed. Favorite/order timestamps are not preservable on any platform via API.

## Self-hosted escape hatch

**Navidrome** — 24,202 stars, pushed 2026-10-17, Windows MSI, v0.64.2 (2026-09-24). Playlists are plain `.m3u` on disk. Built-in Last.fm + ListenBrainz. v0.63 added synced lyrics. Login = your own username, cannot break.

**But:** it plays files you own. You cannot rip Spotify or YouTube. Relevant only if he already has a local collection — in which case it permanently kills lock-in.

## Cambodareality

- Spotify: **available in Cambodia** (confirmed on Spotify's official territory list). App already installed at v1.304.258.0.
- YouTube Music: launched in Cambodia 2023-12-05.
- Apple Music: available in Cambodia; transfer feature **not** blocked (blocked only in China Mainland, Myanmar, Russia).

## Relevant to this machine

- Windows 11, HP ZBook 15 G3
- Spotify already installed: `SpotifyAB.SpotifyMusic` 1.304.258.0
- Apple Music (Media Player) installed: `Microsoft.ZuneMusic` 11.2607.16.0
- SimpMusic 2.3.0 installed at `C:\Program Files\WindowsApps\Simpmusic_2.3.0.0_x64__ejp2bhxmz1qq6`
- SimpMusic data at `C:\Users\ZBook\.simpmusic\` — **app.log contains live Google session cookies in plaintext** (SID, SAPISID, __Secure-3PSID). Never attach to a public issue.
- Python 3.12.10 available; `ytmusicapi` and `spotipy` not installed
- Chrome + Edge both present

## Sources

1. https://developers.google.com/youtube/v3/docs/playlists/list — quota + `playlistOperationUnsupported`
2. https://developers.google.com/youtube/v3/docs/playlistItems/insert — 50 units, scopes
3. https://developers.google.com/youtube/v3/docs/search/list — 100 calls/day cap
4. https://support.google.com/accounts/answer/14792019 — what does NOT transfer between music services
5. https://support.spotify.com/us/article/full-list-of-territories-where-spotify-is-available/ — Cambodia listed
6. https://developer.spotify.com/documentation/web-api/reference/search — `isrc` filter
7. https://developer.spotify.com/documentation/web-api/references/changes/february-2026 — endpoint removals
8. https://ytmusicapi.readthedocs.io/en/latest/setup/oauth.html — OAuth TV-device flow
9. https://github.com/sigma67/ytmusicapi — maintenance
10. https://www.simpmusic.org/docs/guide/accounts-login — desktop cookie-paste login
11. https://github.com/maxrave-dev/SimpMusic/issues/2688 — sign-in failure, 2026-10-16
12. https://github.com/NUber-dev/YTubic — README admits breakage risk
13. https://support.soundiiz.com/hc/en-us/articles/32567703886098-Wrong-Track-Matches-Causes-How-to-Fix-Them — match failure taxonomy
14. https://www.navidrome.org/docs/getting-started/ — m3u playlists
15. https://support.apple.com/en-us/118249 — YT Music → Apple Music transfer
16. https://github.com/sigma67/ytmusicapi/issues/2101 — Netscape cookie bug (also SimplMusic #2101)

## Open questions

- Does Spotify→YouTube Music transfer preserve order but lose "liked at" timestamps? Documented as lost, but not measured on YouTube Music specifically.
- YouTube Music's UGC-heavy catalog is the predicted worst case for fuzzy matching (covers, rips, 1-hour mixes). No source measures this.