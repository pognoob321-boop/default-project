# YouTube Music Playlists: API Access, Export, and Import (as of Oct 2026)

> Research page. Every claim carries a URL. Freshness date noted per source.

## The headline finding

**REFUTED (in part), CONFIRMED (in part).** The common claim "the YouTube Data API v3 does not
expose YouTube Music" is wrong as stated and right about the part that matters.

There are three distinct objects people all call "a YouTube Music playlist":

1. **A playlist you created** in YT Music. This is an ordinary YouTube playlist with a `PL…` ID,
   owned by your channel. Google's own help page says playlists "will show up on the Library tab of
   **both the YouTube Music and YouTube apps**" and that "If you make a playlist in the YouTube main
   app, only music videos from your playlist will surface on YouTube Music"
   (https://support.google.com/youtubemusic/answer/7205933). `ytmusicapi.create_playlist()` returns
   such an ID (https://ytmusicapi.readthedocs.io/en/1.9.1/reference/playlists.html).
   **=> Fully visible to the official Data API v3.**

2. **The YT Music Library** (Liked Music, saved albums, saved playlists from other users,
   Listen Again, subscriptions, stations). This is NOT channel-owned and NOT in the Data API.
   Google's official portability page enumerates what cannot be moved: "YouTube Music curated
   playlists. Liked Music Playlists in YouTube Music. Collaborative playlists if you aren't the
   owner", plus the tip "playlists from other users that you've saved to your library can't be
   transferred" (https://support.google.com/accounts/answer/14792019).
   **=> Only reachable via the private InnerTube API.**

3. **The audio stream.** A YT Music catalog track is not a YouTube video. Redirecting a `PL…` URL
   to youtube.com yields the music *video*, not the audio (yt-dlp issue #14591, open since
   2025-10-10, https://github.com/yt-dlp/yt-dlp/issues/14591).

## What the Data API can and cannot do

`playlists.list` returns **only user-created / channel-owned playlists**. Google's own sample-requests
page says the `mine=true` call "does not retrieve the system-generated playlists included in the
channel information (uploads, watchHistory, and so on). It retrieves only user-created playlists"
(https://developers.google.com/youtube/v3/sample_requests).

Correction to a common misconception: `playlists.list` does **not** return Uploads, Watch Later, or
Liked Videos. Uploads and Likes are reachable only as playlist IDs from the channel resource
(`contentDetails.relatedPlayplays`), and Watch Later is not supported at all — the documented error
is `playlistOperationUnsupported`: "The API does not support the ability to list the specified
playlist. For example, you can't list your watch later playlist"
(https://developers.google.com/youtube/v3/docs/playlists/list, last updated 2026-10-15 UTC).

### Quota and scopes (all pages last updated 2026-10-15 UTC)

| Method | Quota | Scopes |
|---|---|---|
| `playlists.list` | 1 unit | OAuth for `mine=true`; read is enough |
| `playlistItems.list` | 1 unit | `youtube.readonly`, `youtube`, `youtube.force-ssl` |
| `playlists.insert` | 50 units | `youtubepartner`, `youtube`, `youtube.force-ssl` |
| `playlistItems.insert` | 50 units | `youtubepartner`, `youtube`, `youtube.force-ssl` |
| `search.list` | 1 unit, **capped at 100 calls/day** | API key only |

Quota model: default allocation is "100 `search.list` calls, 100 `videos.insert` calls, and 10,000
units per day combined for all other endpoints"
(https://developers.google.com/youtube/v3/getting-started). `search.list` is the notable one: it is
1 unit but hard-capped at 100 calls/day, so it is useless for bulk playlist discovery.

**`playlistItems.insert` cannot create playlists.** Playlist creation is `playlists.insert`, which
writes to the authenticated user's *channel* — a normal YouTube playlist, which happens to also
appear in YT Music. It cannot create a YT Music *library* entry.

Scope strings (https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps):
`https://www.googleapis.com/auth/youtube`, `.../youtube.readonly`, `.../youtube.force-ssl`,
`.../youtube.upload`, `.../youtubepartner`, `.../youtubepartner-channel-audit`,
`.../youtube.channel-memberships.creator`. Note `youtube.upload` is **not** accepted for
`playlistItems.insert` — only for `videos.insert`.

## InnerTube

- Transport: `POST https://music.youtube.com/youtubei/v1/browse` (client `WEB_REMIX`), uniform
  `{"context": {...}, ...}` body (https://github.com/IarChep/MeeTube/blob/master/docs/INNERTUBE_API.md).
- Library playlists browse ID: `FEmusic_liked_playlists`. Liked songs: `FEmusic_liked_songs`
  (https://github.com/z-huang/InnerTune/blob/dev/innertube/src/main/java/com/zionhuang/innertube/YouTube.kt).
- Auth is cookie-derived, not OAuth: `ytmusicapi` states it "emulates YouTube Music web client
  requests using the user's cookie data for authentication"
  (https://pypi.org/project/ytmusicapi) and its docs say "This project is not supported nor
  endorsed by Google" (https://ytmusicapi.readthedocs.io/en/stable/).
- Independent corroboration that it is a private API: the MeeTube engineering reference opens with
  "There is no public documentation; everything below is reverse-engineered"; `nezbut/innertube-go`
  README titles it "Google's Private InnerTube API" and tabulates what the Data API cannot do
  (https://pkg.go.dev/github.com/nezbut/innertube-go).

## Export tooling (ranked)

| Tool | Works? | Limits | Maintained |
|---|---|---|---|
| Google Takeout | Yes | Includes `playlists` and `songs-library-music` under the "YouTube and YouTube Music" product. Watch Later excluded (system playlist). Known-incomplete history reports | Google |
| `ytmusicapi` | Yes, best programmatic route | Needs session cookies; unofficial | v1.12.3, 2026-09-16; OpenSSF "Maintained 10/10" as of 2026-08-24 |
| `yt-dlp` | Partially | `music.youtube.com/playlist?list=…` redirects to youtube.com and **loses the audio**; cannot read library playlists; open issue since 2025-10-10 | Yes, active |
| `ytm-playlist-exporter` (Chrome ext) | Yes | Per-playlist CSV/JSON only, not a whole-account backup | Created 2026-05-04 |
| TuneMyMusic / Soundiiz | Yes | Commercial; these are the two services Google itself names | Commercial |

Takeout sub-option names confirmed at
https://github.com/dtinit/portability-articles/blob/main/articles/watch-history2.md
(`songs-library-music`, `playlists`).

## Import tooling

- **Official, YT Music → Apple Music only:** https://support.google.com/accounts/answer/14792019.
  One-shot, all playlists, no subset selection, no reverse. Blocked on work/school accounts and
  accounts with Advanced Protection on.
- **Official, other service → YT Music:** YT Music app → profile → Settings → Privacy & data →
  Transfer playlists from other apps (https://support.google.com/youtubemusic/answer/14729358).
  Google's own page explicitly points at TuneMyMusic and Soundiiz for services without built-in
  transfer, and says "this list is not comprehensive and does not indicate that Google has any
  formal relationship with these providers."
- **Spotify → YT Music specifically:** no first-party Google route. Use Soundiiz
  (https://soundiiz.com/tutorial/spotify-to-youtube-music) or TuneMyMusic
  (https://www.tunemymusic.com/transfer/spotify-to-youtube-music), or roll your own with
  `spotify2ytmusicv2` (https://pypi.org/project/spotify2ytmusicv2) / `ytmusicapi`.
- **YT → YT Music:** manual via "Save playlist" / "Add to library", or via `playlists.insert` +
  `playlistItems.insert` on the Data API, since it is the same object.

## The "Save playlist to local" claim

**Refuted as stated.** No such menu item exists in the current YT Music web UI. What exists:

- YT Music: "Save to library" / "Add to library" (adds to *your library*, does not export).
  https://support.google.com/youtubemusic/answer/6313542
- YouTube web: "Save playlist" to the You tab. https://support.google.com/youtube/answer/4541577
- Real export to a file: Premium-only offline Downloads (https://support.google.com/youtubemusic/answer/6313542),
  or Takeout.

Privacy requirement for sharing: a playlist must be Public or Unlisted to be shared. A Product
Expert on Google Help states "It cannot be private if you want to share. It has to be set for
Unlisted or Public" (https://support.google.com/youtubemusic/thread/367813436/can-i-share-a-playlist).

## Freshness ledger

- All `developers.google.com/youtube/v3` pages fetched: **last updated 2026-10-15 UTC**;
  `docs/playlists` resource page: 2026-09-16 UTC.
- `ytmusicapi` 1.12.3 released **2026-09-16** (commit `206d470b`), PyPI.
- OpenSSF scorecard snapshot **2026-08-24**.
- `yt-dlp` issue #14591 filed 2025-10-10, still open as of this research.
- `ytm-playlist-exporter` repo created 2026-05-04.
- Google Help pages carry "©2026" but no explicit revision date; the YT Music transfer page has a
  `pubDate=20251022` variant, suggesting a 2025-10-22 publication date.
