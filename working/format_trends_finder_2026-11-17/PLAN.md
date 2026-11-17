# Format trends finder (2026-11-17)

**Decision this serves:** which 3 to 5 templates Nick's format accounts launch with.
**Score:** views only (conversion is tested later, on Nick's accounts).
**Platforms:** Instagram and TikTok. Read only, Nick's logged-in Chrome, stop on any block.
Same rules as the artist content finder: no follows, likes, DMs, comments; no contacts recorded; new files only in this folder.

## What counts as a format account
A page that posts one repeatable template, mostly someone else's music (or its own), little or no personality being sold: lyric/text-over-visual, visualizer/loop, POV/"songs that hit different", edits (sped up, slowed, mashup), drop compilations, discovery/repost pages, studio-clip pages. Labels, events and artists are kept only as reference, not scored.

## Steps
1. **Seeds.** (a) 241 non-artist accounts that co-own collab posts with the 249 ranked artists (raw/seed_ig_coowners.json). (b) Instagram and TikTok tag pages and search for lane terms (dubstep, riddim, 140, deep dubstep, bass music, dnb as a reference). (c) Instagram audio pages of moving lane tracks: the reels using a sound show who posts it.
2. **Classify** each account: format page / label / event / artist / other. Keep format pages.
3. **Reach read:** followers plus the last 12 posts' views. Score: count over 10k, median, and views per follower (artist baseline 0.37; a template that beats it is breaking the follower ceiling).
4. **Template read** (by eye, top 30 or so): the template precisely enough to rebuild, hook text, length, edit effort, how it scales, brand fit flags.
5. **Sound layer:** use counts on audio pages for lane tracks, and what the top reels on a moving sound look like.
6. **Output:** TEMPLATES.md, 5 to 10 templates, each with recipe, examples with numbers, effort, scale, fit.
