---
title: Artist Growth Audit — Generalized Playbook
version: 1.0
created: 2026-07-26
status: live — genre-agnostic method, extracted from the 2026-07-26 WOBAR session
scope: A reusable prompt sequence for auditing an independent artist's growth position and building an evidence-graded plan. The METHOD transfers; the FINDINGS do not.
---

# ARTIST GROWTH AUDIT — PLAYBOOK

Extracted from a full-day audit of one artist. **Nothing about the conclusions transfers** — that artist's answer was "SoundCloud, not Instagram," but a pop artist, a folk songwriter, or an ambient producer will land somewhere completely different. What transfers is the sequence, and specifically the two places it went wrong.

## The two mistakes to avoid (read first)

**1. Tactics before goals.** The session spent hours optimising Instagram before anyone asked what the artist actually wanted in 12 months. When that question finally got asked, the answer made most of the prior work irrelevant. **Run Phase 2 before Phase 3.** Always.

**2. Convenience-sampled comparisons.** The first peer cohort was built from artists whose social handles were findable by web search — which correlates with having press and management. Every single one over-performed, no struggling artist appeared, and it nearly produced a confident false conclusion. **The fix is Phase 4, and it's the most valuable single technique here.**

---

# PHASE 1 — MEASURE THE POSITION

Do this before any opinion is formed. Real numbers only.

> **PROMPT 1**
>
> I'm auditing my growth position as an independent [GENRE] artist. Before any strategy, I want the actual numbers.
>
> Pull and tabulate my current position across every platform I use — followers, post/track counts, and per-post or per-track performance on the most recent 6–10 items. Include my streaming numbers (monthly listeners, followers) and, where the platform exposes it, my analytics: reach, profile visits, link clicks, follows-per-post.
>
> My accounts: [LIST EVERY URL — social, streaming, Bandcamp, SoundCloud, YouTube, mailing list size]
>
> Then compute the funnel: how many people are reached, how many visit the profile, how many convert to a follow or a click. Present it as a table with no interpretation yet. If a number can't be retrieved, say so rather than estimating.

**Why:** the funnel almost always localises the problem to a place nobody expected. In the source session it showed 9,148 people reached in 90 days producing ~0 follows — reach was fine, conversion was the failure, and every prior assumption had been about reach.

---

# PHASE 2 — THE GOAL (do not skip, do not do later)

> **PROMPT 2**
>
> Before we plan anything, I want to pressure-test what I actually want.
>
> Ask me: **if it's 12 months from now and this went well, what specifically happened?** Push me for a concrete image, not a category. Then challenge my answer — tell me what it implies, what it demotes, and where it conflicts with how I'm currently spending my time.
>
> Also tell me honestly if the different parts of my project are pointed at different goals. [PASTE OR DESCRIBE: your current projects, docs, releases, side ventures]
>
> Don't move to tactics until we've settled this.

**Why:** most artists are running two or three incompatible projects under one name — a streaming career, a body of work, and a live practice — with effort going to whichever is most enjoyable. Naming that is often the whole audit.

**Expect to change your answer mid-conversation.** In the source session the artist first said "a room full of people at my headlined night," then revised to "realistically, people listening to my music, and I'd rather build online than local." Those two answers imply almost entirely opposite plans. The revision was the real answer.

---

# PHASE 3 — FIND THE ACTUAL LANE

Do not use the artist's stated influences. Use their behaviour.

> **PROMPT 3**
>
> Here is the tracklist from my most recent DJ set / my current live setlist / my most-played playlist: [PASTE]
>
> Map it by runtime, not by track count. Break it into sections and tell me what percentage of the set each occupies. Then tell me: who is my most-played artist, where is the center of mass, and does that match how I describe my own sound? [PASTE your bio or stated influences]
>
> If they don't match, say so bluntly and tell me which one is real.

**Why:** artists reliably describe themselves by their most aspirational or most emotionally significant material, not their center of mass. In the source session, the artist's stated comps turned out to occupy the final 24% of his set; the middle 45% was a scene he'd never named — and that scene had an entire label ecosystem nobody had looked at.

**If you're not a DJ:** substitute your last 10 finished tracks, your most-played Spotify artists of the year, or the lineup of the last show you played.

---

# PHASE 4 — BUILD A NEUTRAL COMP FRAME

**This is the most important technique in the playbook.** It exists to stop you from accidentally studying only successful people.

> **PROMPT 4A — the frame**
>
> I want to compare myself against peers, but I want the comparison to be honest — not just artists who are already visible.
>
> Build the sample from **label rosters**, not from search. Pick 4–6 labels that release the artists in my lane [FROM PHASE 3], including at least two small ones. For each label, pull the artist credits from their most recent ~40 releases (Beatport, Bandcamp, Discogs — whatever's authoritative for my genre). Take lead artists only.
>
> Do not filter for who looks successful. The roster IS the sample.
>
> Tell me the frame size before we go further, and propose a neutral reduction rule if it's too big — a recency window, not a quality judgment.

> **PROMPT 4B — the handle trick**
>
> Now resolve their social handles. **Do not use web search to find them** — search only surfaces artists who have press coverage or management, which is exactly the bias I'm trying to avoid.
>
> Instead: go to each label's own social account and search *inside its following list*. Labels follow their artists regardless of whether those artists have any press footprint at all.
>
> Log every handle you can't resolve with a count rather than dropping it silently — that number is the visible residual bias.

**Why it works:** search-discoverability correlates with career infrastructure. A label's following list doesn't. In the source session this surfaced handles no search would ever have returned, and it's what finally produced peers with 800 followers and 200-play tracks — the comparison that actually mattered.

---

# PHASE 5 — SWEEP ACROSS PLATFORMS

> **PROMPT 5**
>
> For each artist in the frame, record: followers on each platform, output volume, performance on the 6 most recent items, and **performance divided by follower count** (reach efficiency).
>
> Build one table comparing every artist across ALL platforms side by side — social, streaming, and wherever the music actually lives in my genre. Put me in the table.
>
> Then tell me which platform my deficit is actually on. Compare per-follower, not in raw numbers — raw comparisons against artists with 50× my audience are meaningless.

**Why:** the source session found the artist was mid-band per-follower on the platform he'd been optimising, and **34× below the smallest peer** on the platform he'd been ignoring. Raw numbers had hidden that completely.

**Genre-dependent:** the platform set is not universal. Bandcamp matters enormously in some scenes and not at all in others. Ask what the platform mix is *for your lane* rather than assuming.

---

# PHASE 6 — DOES ANY OF IT CONVERT?

Two questions that decide whether the whole audit matters.

> **PROMPT 6A — the decoupling test**
>
> For every artist in my comp set, put social followers next to streaming listeners. Look for pairs with **similar social followings and wildly different listener counts** — and pairs with the reverse.
>
> If those pairs exist, social size doesn't predict listeners in this lane, and growing social is not the lever for a listener goal. Tell me plainly which it is, and flag if the data can't support a conclusion either way.

> **PROMPT 6B — the gate test**
>
> Whatever door I actually want — a label, a booking agent, a playlist, a collaborator — find artists who recently got through it, and record how big they were when they did. Current follower count is an upper bound on their count at the time, so small current numbers prove they were signed small.
>
> Tell me whether the doors I want are audience-gated or taste-gated.

**Why:** 6B is often the most liberating finding in the whole audit. In the source session it found a label had released an artist with 119 monthly listeners — meaning the door the artist was "too small" for was open the entire time.

---

# PHASE 7 — TRY TO DESTROY YOUR OWN CONCLUSIONS

Skipping this is how audits produce confident nonsense.

> **PROMPT 7**
>
> Take every load-bearing claim we've reached and try to **refute** it. Not confirm — refute.
>
> For each claim: search independently, apply a source standard, and return a verdict of CONFIRMED / PARTIAL / UNSUPPORTED / REFUTED with confidence and counter-evidence.
>
> **Source tiers:** Tier 1 = the platform or company's own documentation. Tier 2 = large-N studies with stated methodology, or credible trade journalism. Tier 3 = agency blogs, SEO content, Reddit, YouTube advice — record as hypothesis only, never load-bearing.
> CONFIRMED requires Tier 1, or two independent Tier 2s. **"Nobody has published this" is a valid and valuable answer — say UNSUPPORTED and say it plainly.**
>
> Then audit your own findings for: verdict inflation, correlation presented as causation, survivorship bias in the examples, sources that don't say what you claimed, and any statistic you can't trace to a named study.
>
> Finally, list what NOBODY knows — the questions where no credible data exists at all.

**Why:** in the source session this returned **9 of 10 claims UNSUPPORTED** and caught fabricated statistics in circulation — including two widely-cited clusters ("87% of labels accept demos," "r=0.82 Billboard validation study") that trace to no real study and dominate search results on exactly those questions.

**Watch for:** if several independent research passes all converge on the same recommendation, treat that as a **warning sign**, not corroboration — they're probably sharing a dataset or a bias.

---

# PHASE 8 — WRITE THE PLAN, GRADED

> **PROMPT 8**
>
> Write the plan. Tag every single claim with its evidence grade:
> **[SOLID]** verified · **[OBSERVED]** real first-party data, uncontrolled · **[JUDGMENT]** reasoned but unproven · **[UNSUPPORTED]** no credible evidence either way.
>
> Include: the goal and how it's measured, my starting numbers, what I make and where each output goes, what I'm deliberately parking, the 3–5 metrics I track, and an explicit section on **what this plan does not know**.
>
> Then check the recommendations against each other for conflicts — plans built from separate findings often deadlock when combined. Tell me if mine does.
>
> Finally: keep a corrections log of anything we retracted during the audit, so it doesn't get re-derived later.

**Why the conflict check:** the source plan deadlocked invisibly — labels required unreleased material, one channel had been moved elsewhere, and composed literally the artist's main channel had nothing left to post. Nobody noticed until the plans were laid side by side.

---

# PHASE 9 — BRING YOUR OWN EVIDENCE

> **PROMPT 9**
>
> Here's something that contradicts what you found: [LINK / SCREENSHOT / EXAMPLE]
>
> Look at it directly rather than arguing from your earlier research. If it beats what you had, say so and update.

**Why this is a real phase:** in the source session the artist supplied two links that overturned a major recommendation and reinstated a format the research had rejected. **His two links were better evidence than a 13-agent, 962K-token research pass** — because they were a within-account, same-period comparison rather than cross-sectional correlation.

You know your scene. The research doesn't. Push back with specifics and make the analysis update.

---

# WHAT DOESN'T TRANSFER

Do not carry these across genres. They were true for one artist in one lane:

- SoundCloud being the priority platform *(genre-specific — irrelevant in most scenes)*
- Flips/bootlegs as a growth format *(only exists in remix-culture genres)*
- Uncleared remixes being blocked from streaming services *(true, but only relevant if you make them)*
- Any specific label, its door, or its requirements *(these change monthly — always re-verify)*
- Instagram being the wrong platform *(that was one artist's funnel, not a universal)*

# WHAT ALWAYS TRANSFERS

- Measure before you theorise
- Goals before tactics
- Sample from rosters, not from search
- Compare per-follower, not raw
- Instruct the research to refute
- Grade every claim
- **The artist's own first-party data beats every external sweep**
