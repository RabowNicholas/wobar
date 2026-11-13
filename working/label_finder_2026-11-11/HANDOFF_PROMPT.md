# Label research: handoff prompt

Paste everything below the line into a new conversation.

---

I'm Nick, a bass music producer (project: WOBAR). Over 2026-11-11 to 2026-11-13 I ran a "label target finder" with Claude. I want to abstract the process into something reusable (a skill, a repeatable workflow, or a cleaner tool). Below is the full context: what we did, how, the rules, what broke, and where everything lives. Read the files listed before proposing anything.

## Goal of the original run

Find record labels worth sending demos to, ranked and backed by evidence, in two lists:
- **List A (small/medium):** labels I can realistically get signed to now.
- **List B (Dream):** bigger labels I want to reach within 12 months.

Plus side lists: scouting queue (good label, no public demo door), manual review, rejected (with reasons), and a known ledger of past sends (empty).

My genres: 140 / Deep Dubstep / Grime (primary) and Dubstep. No Trap, Future Bass or DnB.
Goal: releases on 3 to 5 Dream labels within 12 months, plus at least one entry in the Beatport 140 or Dubstep Top 100.

## Hard rules (keep these in any abstraction)

- Research only. Never send a message, submit a form, create an account, log in, or pay.
- Write only new files, in one dated folder. Never edit my existing files.
- No outreach drafts until I approve the lists and ask.
- Record a demo contact only if the label publishes it for demos on its own pages or bios. Never guess addresses, never collect personal emails.
- Never put my name, contacts or unreleased music into any outside site.
- If a site blocks you (captcha, bot check, 403/429), stop and tell me. Never work around a block.
- Plain language, terse. No em dashes in anything written to me.

## The process, step by step

1. **Setup questions.** Genres, goal, goal labels, peer artists/labels, tracks, past sends, exclusions, run size, browser permission.
2. **Build the universe.** Every release in both genres on Beatport for 24 months, crawled month by month (genre listings cap at 10,000 results). Result: 18,709 releases, 2,597 labels, 17,394 artists. Page counts checked against Beatport's totals.
3. **Chart evidence.** Beatport Top 100 for both genres (one snapshot; no Hype chart exists for either genre). 158 chart tracks across 68 labels. Owner-credited chart tracks counted separately from independent ones.
4. **Label catalogues.** Latest 100 tracks per Beatport label id (226 ids, including alternate ids for the same label).
5. **Gates** (all must pass for List A):
   - Genre: 8 of last 12 releases in 140 + Dubstep (release genre = majority of its tracks). Manual override for labels I judge in-genre (Odyzey, Trippy Bee).
   - Activity: 2 releases in 6 months and 1 in the last 60 days.
   - Roster: 5+ distinct artists in 2 years, 3+ not the owner.
   - Identity: label's SoundCloud confirmed by 3+ track titles matching Beatport.
   - Door: a published demo email, form or portal.
6. **Scoring.** Chart proof 40, roster strength 30, newcomer share 15, genre fit 8, reach (SoundCloud followers) 7.
   - Roster strength index (RSI): how many of the label's artists also release on my goal labels and peer labels. Self-overlap from the same label group excluded.
   - Labels without chart tracks need RSI 40+.
7. **SoundCloud pass.** Find each label's account, confirm by title matching, read bio for demo doors and owners. Followers only count from confirmed accounts.
8. **Door pass.** Label sites, linktrees, forms, LabelRadar. Copy wording exactly, note rules (exclusive-only, VA-only, fees).
9. **List B.** Goal labels plus any label meeting 2 of 3 criteria: 3+ independent chart tracks, follower count at the goal-label median (47,843), 5+ artists shared with goal labels. Ranked by reach 60 + fit 40. Access tagged OPEN / NARROW (few newcomers) / CLOSED.
10. **Route plans for closed Dream labels.** Which List A labels share roster artists with them (stepping stones).
11. **Calibration with me.** Show near-misses, let me adjust rules, record what changed and why.
12. **Listening pass.** Build one private Spotify playlist per label (last 12 months of releases) so I can hear each label's sound, then kill or keep by ear.

## Calibration and decisions I made

- Activity lowered from 3 to 2 releases in 6 months; no-chart RSI bar lowered from 60 to 40 (both so Locus Sound qualifies).
- Odyzey and Trippy Bee counted as in-genre ("not really trap").
- Owner statement dropped from the identity gate; unstated owners are fine.
- Relationship cap (no-chart labels capped at half of List A) lifted.
- Odyzey kept despite missing the 60-day rule by one day.
- Monstercat and Gravitas stay on List B but out of the first 10 to send to (only 4/12 in genre); Bassrush took the slot.
- Bad Medic rejected as too small.
- I'm not sending anything yet. I need more finished songs first.

## My listening feedback (the most important output)

- **Trippy Bee:** possibly the best fit. Psychedelic, heavy hip hop influence, "weird music". My sound design is already there.
- **Aspire Higher:** dark experimental 140, fits Act 3/4.
- **Odyzey:** world bass, fits wobar.lite and Acts 1, 2, 5.
- **1985 Music:** dark minimal 140 and DnB, great for certain songs, not fully my sound.
- **DUPLOC:** strictly 140, less of an immediate fit, still possible.
- **Killed:** Neoluminum, Sounds Of Mayhem, Port Zero.

Listening beat the numbers: two of the three killed labels had scored near the top. Any abstraction should put a listening step before ranking is trusted.

## Current lists

- **List A (11):** 1985 Music, Trippy Bee, DUPLOC, Odyzey, Aspire Higher, ANTAGONIST, LDH Records, Sound in Picture (exclusive-only door), Locus Sound, Arctic Empire, Cimmerian. Not yet heard: ANTAGONIST, LDH, Sound in Picture, Locus Sound, Arctic Empire, Cimmerian.
- **List B send set (10):** Wubaholics, Deep Dark & Dangerous, SubCarbon, UKF, Jadū Dala, Deadbeats, Circus, Disciple, DirtySnatcha, Bassrush. 15 more are CLOSED (Cyclops, Subsidia, Wakaan, Wormhole, Drama Club, Good Society, Memory Palace, Local Void, Never Say Die, Kannibalen, Crucast, cd91x, Buku, Deep Medi, Mersiv).
- **Strongest route:** Wakaan shares 5 roster artists with Odyzey. Cyclops shares 5 with ANTAGONIST.
- **Send plan (when ready):** waves of about 8; held-back tracks to Dream labels first with a 3-week wait; never the same track to an exclusive-only label and others at once; I send everything myself.

## Technical lessons (what broke and how it was handled)

- **Beatport:** curl gets 403. Read it from a real browser tab (Claude in Chrome). Pages are Next.js; data is in `__NEXT_DATA__` at `props.pageProps.dehydratedState.queries[*].state.data`. Useful paths: genre listings `per_page=100&page=N&order_by=-publish_date&publish_date=A:B` (140 is genre id 95, Dubstep 18); label catalogue `/label/x/{id}/tracks?per_page=100&order_by=-publish_date`; label search `/search/labels?q=`. Label bios were empty.
- **Getting data out of the browser:** the browser tool returns only about 1k characters and blocks some output. Workaround: build JSON in-page, save it as a blob download to ~/Downloads, then move it into the project with a script. Chrome allows one automatic download per site until I allow more. Background tabs throttle timers, so keep the crawling tab in front.
- **SoundCloud:** read via its public api-v2 endpoints (search/users, users/{id}/tracks, web-profiles) with the client_id from the site's own assets, inside the browser.
- **Spotify:** my Spotify MCP server runs through my own developer app in Development mode, which has a small rate limit.
  - The first run fired about 650 searches in a few minutes and got search blocked. Retrying during the block extended it, ending in 4-hour and then 23-hour waits.
  - Playlist creation was never blocked, only search.
  - The fix was a script that reuses the MCP server's own auth helper (token never printed), searches once per track at about 1 every 3 seconds, honours Spotify's Retry-After exactly, and stops if the wait is over 2 minutes.
  - Odesli (song.link) public API is deprecated, and Deezer can't give Spotify IDs, so Spotify search is the only way to get Spotify IDs.
  - Spotify's `label:` search filter matches loosely (LDH Records returned a different artist entirely), so match Beatport titles + artists instead.
- **Sites left alone:** Manuka (bot check), Wakaan (certificate error).

## Where everything is

Folder: `working/label_finder_2026-11-11/` in the WOBAR vault.
- `REPORT.md`: full report, rules as used, decisions, limits.
- `LISTENING_NOTES.md`: my listening feedback.
- `LIST_A.csv`, `LIST_B.csv`, `SIDE_LISTS.csv`: lists with every metric, door wording, links.
- `RELEASES_LAST_YEAR.md` / `.csv`: every release in the last 12 months for List A and the send set.
- `CALIBRATION.md`: calibration notes.
- `scripts/`: `collect.py` (move downloads into raw/), `common.py`, `config.py` (all rule constants and my overrides), `universe.py`, `rsi.py`, `gates.py`, `sc_crawl.js`, `sc_match.py`, `assemble.py`, `report.py`. Run order: universe, rsi, gates, sc_match, assemble, report.
- `data/`: derived data (owners.json, doors.json, sc_manual.json, lists.json, etc). `raw/`: everything read.
- `spotify/`: `sp_match.mjs` (match: `node sp_match.mjs`; build playlists: `node sp_match.mjs create`), `label_tracks.json`, `label_matches.json`, `label_playlists.json` (20 playlists made).

## Open item

Circus, Disciple, DirtySnatcha and Bassrush playlists still need 245 tracks matched. Spotify asked for a 23-hour wait starting 2026-11-12 5pm, so it's clear after about 4pm on 2026-11-13. Then run `node sp_match.mjs` then `node sp_match.mjs create` from the `spotify/` folder (about 15 minutes).

## What I want from this new conversation

Help me abstract this into something reusable. Things worth separating out:
- The genre-agnostic method (universe, gates, scoring, calibration, listening) vs. my specific settings in `config.py`.
- The data-collection layer (Beatport, SoundCloud, Spotify) and its fragile parts.
- A lighter re-run mode (refresh charts, re-check doors, add new labels) for every couple of weeks.
- Where my ear should come earlier in the process.

Ask me what shape I want it in before building.
