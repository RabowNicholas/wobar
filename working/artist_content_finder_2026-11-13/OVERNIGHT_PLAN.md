# Overnight run, 2026-11-16 into 11-17 (Nick asleep; decisions below are his, given before bed)

## Nick's decisions
1. Short list: start with 30; if time is left, keep going down the ranking.
2. Main band vs stretch: Claude's call. Main band (10k to 100k Spotify) only for the 30; add ~5 stretch as reference at the end if time allows.
3. Depth: more than 3+1 posts. Goal in his words: "find what is consistently getting over 10k views and find trends."
4. Commit the run folder when done: yes. Update WOBAR_ACTIVE.md loop entry: yes.

## Ranking (Claude, from decision 3)
- Per artist, last 12 posts on the best platform (Instagram reels from raw/reels_all.json, TikTok from gate.json tt_views12), pinned excluded.
- Primary: hits = number of those posts with 10k+ views. Tie-break: median views.
- Main band only. Top 30, then continue.

## Per artist breakdown
- Every post with 10k+ views in the last 12, plus the 2 lowest for contrast.
- Per post: views, likes, comments, date, caption first line verbatim, audio label (own track or not), format, on-screen hook text (read from the grid cover image).
- Cadence from dates of the last 12.
- Song section: only where caption/label says (Claude cannot hear audio). Blank otherwise.

## Rules (Nick's, verbatim, still binding)
"Research only. Never send a message, submit a form, create an account, log in, or pay." / "Write only new files, in one dated folder. Never edit my existing files." / "Never put my name, contacts or unreleased music into any outside site." / "If a site blocks you (captcha, bot check, 403/429), stop and tell me. Never work around a block." / "Plain language, terse. No em dashes in anything written to me." Instagram read only: no follows, likes, DMs, comments.
Exception granted tonight: commit + WOBAR_ACTIVE.md loop update.

## Output
REPORT_CONTENT.md (ranked list, per-artist breakdown, cross-artist patterns, tests for Nick's songs), data/content_posts.json, CONTENT_POSTS.csv.

## Progress log
- reach read: running (200/238 at plan time)
- 21:07 heartbeat: reach read 235/238, running
- 21:12 reach read done (236 accounts, raw/reels_all.json). Ranked: data/ranking.json, RANKING.csv (37 artists with 10+/12 posts over 10k). Post reader started: 489 posts, top 41 IG artists (data/post_targets.json, localStorage acf_posts). TT top-45 artists (KLOPOTA, Sparkz, JordanBeats, Brainrot) still to read on TikTok. Note: many top reels are collabs owned by other accounts; flag in report.
- 21:27 heartbeat: post reader 91/489, running
- 21:47 heartbeat: post reader 223/489, running (dies ~every 50 posts on page reload, relaunched each time)
- 22:07 heartbeat: post reader 299/489, running

## Extension (Nick, 22:24): "lets keep going deeper into artists... like 8-10 hours of this same thing. going down that list"
Order: (1) finish first 489 posts; (2) rest of main band ranks 46-249: data/post_targets_ext.json (183 artists, 1177 posts), appended to localStorage acf_posts_list in chunks; (3) TikTok-first artists (25) video pages; (4) hook text from cover images, top 60; (5) interim report after (2) first half, final report at end; (6) if time left: stretch band reach read + posts as reference.
- 22:27 heartbeat: post reader 386 read, queue 1089 (ranks to ~110 appended), running
- 22:49 interim REPORT_CONTENT.md written (top 30, 9 patterns, 7 tests). Covers read for top 27 IG (data/covers_notes.md). Post reader resumed on deeper list (439 read, 637 queued).
