---
title: Wobar Instagram — Content Strategy Review + Research Plan
version: 0.2
created: 2026-07-26
last_updated: 2026-07-26
status: baseline captured — research not yet executed
scope: Diagnosis of wobar.exe from live Insights, plus the research plan to answer (a) what IG is FOR in the Wobar system, (b) what actually grows an account in this lane, (c) whether the documented content system survives contact with data. Produces a CONTENT.md v3.0 rewrite.
dependencies: [[reference/WOBAR_CONTENT]], [[working/WOBAR_PLACEMENT_PLAN]], [[working/FORMAT_TESTING]], [[reference/WOBAR_GRAMMAR]], [[reference/WOBAR_BRAND]]
---

# IG RESEARCH PLAN

## Why this exists
`reference/WOBAR_CONTENT.md` v2.0 (locked) says IG is Mirror content — track + visualizer per drop, "community depth, retention." The live account does not do that, and where it does, that content is the worst-performing content on the page. No baseline numbers existed anywhere in the vault, so nothing had been judged. Baseline is now captured; this plan gets credible external data before rewriting the strategy.

---

# PART 1 — BASELINE (live Insights, pulled 2026-07-26)

**Profile:** 101 posts · **400 followers** · 146 following
**Bio:** "deep dubstep / monthly sets at @flow.state.slc events / booking/collabs contact.wobar@gmail.com / enter the void 👇 / wobar.music"

## Account funnel

| Metric | Last 30d | Last 90d |
|---|---|---|
| Views | 24,527 | **116,070** |
| Accounts reached | 6,136 | **9,148** |
| Non-follower share of views | 86.2% | **92.6%** |
| Interactions | 1,664 | 12,036 |
| Accounts engaged | 737 | 5,508 |
| Profile visits | 285 | **706** |
| External link taps | 14 | **20** |
| Content mix (views) | Reels 95.2% / Stories 3.8% / Posts 1.1% | Reels 97.9% / Stories 1.7% / Posts 0.4% |

**Conversion rates (90d):** reached → profile visit = **7.7%** · profile visit → link tap = **2.8%** · reached → link tap = **0.22%** · 9,148 unique accounts reached against a **400-follower** base (23× the follower count).

## Content performance by type (public Reel view counts, ~30 recent Reels)

| Content type | Observed views | Median |
|---|---|---|
| Event promo (hangar rave, cave rave, DEPARTURES flyer) | 11.4K · 10.8K · 8.1K · 5.0K · 3.6K · 2.8K · 2.8K · 1.6K | ~3.2K |
| Talking-head / community ("building community around music") | 7.6K | 7.6K |
| Live-set POV footage | 2.1K · 1.5K | 1.8K |
| "day N standing in same spot" street series | 1.8K · 1.5K · 458 · 262 | ~1.0K |
| Meme edits (spongebob / teletubbies / aux / POV) | 491 · 443 · 337 · 258 · 181 | ~340 |
| **Visualizers — the documented WOBAR content system** | 314 · 266 · 258 · 207 · 203 · 190 · 187 · 184 · 176 · 133 | **~205** |

Confirmed independently by IG's own Content Insights: sorted by views descending, the top of the list is entirely event promo; sorted ascending, the bottom is entirely visualizer/artwork posts. Sorted by **shares**, the top four are again all event promo — zero visualizers appear anywhere near the top on any metric.

## The decisive data point

Top-performing post (hangar-rave promo, Jun 22):

| | |
|---|---|
| Views | 11,463 |
| Accounts reached | 7,243 |
| Non-follower views | **97.2%** |
| Interactions | 821 (402 likes · 19 comments · 60 saves · **316 shares**) |
| Accounts engaged | 542 |
| **Profile activity** | **--** |
| **Follows** | **0** |

A 316-share, 11.5K-view, 97%-non-follower hit produced **no profile activity and no follows.** Sampled visualizer posts return 0 likes / 0 comments / 0 saves / 0 shares / 0 follows.

## Diagnosis — five findings

1. **This is not a reach problem.** 9,148 unique non-follower accounts reached in 90 days against 400 followers. Distribution is working. **The failure is conversion** — view → profile → follow → link. 706 profile visits and 20 link taps out of 116K views is the whole story.
2. **The reach that exists belongs to Flow State, not Wobar.** Every top performer is event promo for `@flow.state.slc` (4,755 followers), and its CTA is "text hangar to 435-351-8663" — a ticket funnel, not a Wobar funnel. The account is succeeding as a second Flow State channel. Whether that traffic can be converted into anything Wobar-shaped is unresolved and is the central strategic question.
3. **The documented strategy is the account's worst content.** Visualizers median ~205 views vs ~3.2K for event content — a ~16× gap — and post-level insights show them at zero on every interaction metric. The entire WOBAR_CONTENT.md release-content system is, on current evidence, not reaching anyone.
4. **What travels is face-forward, literal, and local** — talking to camera, POV street bits, event flyers. That runs directly against the locked brand position (faceless, abstract, restraint; figurative-cheese rule; see [[reference/WOBAR_WORLD]] and the restraint principle). This conflict is the actual crux and must be resolved on evidence, not split by feel.
5. **Nothing downstream is instrumented.** 20 link taps in 90 days is the only conversion signal in existence, and where those taps landed is unknown. No connection has ever been measured between IG activity and Spotify listeners, Ether crossings, or bookings. The Release Schedule loop's "1.5× baseline" BTS trigger has never had a written baseline — **it is now: median ~205 views for visualizer posts, ~1.0K for street-series, ~3.2K for event promo. Formats must be judged against their own class, not one global number.**

## Still missing
- **Retention / watch-time and per-post follows** — web Insights doesn't expose them; mobile app only.
- Per-post dates and cross-post status for the full 101-post history.
- Where the 20 link taps went; whether `wobar.music` is tracked at all.
- TikTok `wobar1` — is it live and posted to? The vault's "TikTok = discovery / IG = depth" split remains an untested assertion.

---

# PART 2 — RESEARCH PLAN

## Phase 0 — Finish the baseline
*Own data. ~1 hr. Mobile app required.*

- Pull first-3s retention, average watch time, and **follows-per-post** on mobile for a stratified sample: 5 event promos, 5 street-series, 5 memes, 5 visualizers.
- **The question it settles:** do visualizers lose on *reach* (never distributed) or on *retention* (distributed and swiped past)? Those need opposite fixes — distribution vs. hook craft. Everything in Phase 3 reads differently depending on the answer.
- Log per-post dates + cross-post status into `working/IG_BASELINE.csv`.
- Confirm TikTok `wobar1` status and pull equivalent numbers if live.

## Phase 1 — Platform mechanics, 2026
*Desk research. ~half day.*

**Questions, ordered by what the baseline actually implicates:**
- **Conversion-first:** what makes a viewer visit a profile and follow, vs. just watch? What is a normal reached→follow rate for a sub-1k account, so we know whether 7.7% profile-visit rate is bad or typical?
- Does a share-heavy, follow-light post (316 shares → 0 follows) indicate a known failure mode — content that travels as a *utility* (an invite) rather than as *identity*?
- Reels ranking in 2026: actual weighted signals; where sends/shares sit vs watch time and completion.
- What determines whether a Reel leaves the follower graph — and whether abstract/visual-only content is structurally disadvantaged there.
- Trial Reels (non-follower-only test posts): available? A way to test brand-risky formats without polluting the grid.
- Carousels vs Reels for reach and saves in 2026 (bears on the carousel format parked in FORMAT_TESTING).
- Cross-posting: is the TikTok-watermark / re-upload penalty real in 2026 or folklore?
- Cadence effects on per-post reach at sub-1k scale; hashtag/keyword surfaces post-2024.

**Source tiers — load-bearing only if tier 1, or two independent tier 2s:**
- **Tier 1:** Instagram `@creators`, Adam Mosseri's own posts, IG Help Center, Meta Newsroom / engineering blog.
- **Tier 2:** large-N first-party studies with stated sample size and date — Metricool, Buffer, Socialinsider, Later, Hootsuite benchmarks.
- **Tier 3:** practitioner/agency/YouTube claims — hypotheses only, flagged, never load-bearing.

**Method:** carry over Placement Plan discipline — every claim logged verified/refuted with vote count, plus a myth-busted section. Unsourceable claims get written down as unknown, not smoothed over.

**Deliverable:** `working/RESEARCH_IG_MECHANICS.md`.

## Phase 2 — What is IG actually FOR?
*Desk research + own data. ~half day. Explicitly not decided by preference.*

Four candidate jobs, each with a claim that can be checked:

| Candidate job | Claim to verify | Instrument |
|---|---|---|
| Feed Spotify listeners | Social→DSP conversion is meaningful at this scale | Published conversion data for sub-5k artists; S4A Source of Streams (profile/external) |
| Grow the Ether (owned SMS + web home) | Social CTA → owned list beats social → DSP | Owned-audience benchmarks; link taps vs crossings. **Note: the Flow State event posts already prove a text-to-number CTA converts hard in this audience — that is the single strongest local evidence in hand** |
| Bookings + scene credibility | Promoters/talent buyers actually check IG; follower count gates slots | Booking-agent and promoter guidance; Denver-corridor practice |
| Raw follower growth | Scale first, convert later — only defensible if 1–3 test weak | — |

**Plus the question the baseline forces:** what is the Wobar↔Flow State relationship? Wobar's reach *is* Flow State's audience. The honest options are (a) formalize it — wobar.exe as the artist face of the Flow State scene, with a deliberate handoff from event traffic to Wobar's own funnel, or (b) separate them. Pick on evidence. This is finding #2 and appears nowhere in the vault.

**Deliverable:** decision memo scoring the four jobs on (a) evidence of conversion, (b) fit with operating constraints (solo, few hrs/week, <$50/mo — same as the Placement Plan), (c) measurability. **Output = one north-star metric for IG**, written into CONTENT.md v3.0. Until this lands, "growth" has no definition and no format can be judged.

## Phase 3 — Comp teardown (n ≈ 12)
*Hands-on. ~half day.*

**Sample:**
- Core sonic comps at scale (Of The Trees, INZO, Shlump, LSDREAM) — for format vocabulary, not benchmarks.
- 6–8 **mid-tier / emerging** psy-bass and experimental-bass producers, 1k–50k — the real peer set.
- 3 **faceless AV / visualizer-first** accounts that have actually grown on abstract visual content.

**Per account:** ~20 recent posts — public view counts, format tag (visualizer / live footage / face-to-camera / meme / event promo / BTS), cadence, hook style, face vs faceless.

**The fork this settles:** does *anyone* in this lane grow on abstract visualizer content? If yes → Wobar's problem is execution (hook, first 3s, distribution) and the brand survives intact. If no → visualizers are a catalog and retention asset, not a growth asset, and the growth engine must come from somewhere the brand can tolerate. Everything in Phase 4 hangs on this and it should not be guessed.

**Deliverable:** `working/RESEARCH_IG_COMPS.md` — median-views-by-format across accounts + the actual mechanic behind each faceless account that works.

## Phase 4 — Synthesis + strategy rewrite
*~2 hrs, after 0–3.*

- Reconcile `WOBAR_CONTENT.md` against the real account; state what the content system now is, including what role event/face/meme content earns or loses on evidence.
- Resolve the brand-vs-growth conflict as a **written rule** — where the line sits between the faceless/abstract position and what demonstrably travels. Check the result against [[reference/WOBAR_GRAMMAR]] Law 0 before shipping.
- Design the **event-traffic handoff** if Phase 2 supports option (a): how a Flow State event viewer becomes a Wobar listener or a Wanderer. Currently that handoff does not exist — 11.5K views produced 0 follows.
- Close out `FORMAT_TESTING.md` — The Cut / The Stack / The Transmission have been open since April with no verdict. Kill or keep against the per-class baselines above.
- Define the testing protocol: posts-per-format minimum before judgment, the judging metric (from Phase 2), the kill threshold.
- Rewrite the Release Schedule loop's BTS trigger to use per-class baselines.

**Deliverables:** `reference/WOBAR_CONTENT.md` v3.0 · updated `working/FORMAT_TESTING.md` · a metrics block mirroring the Placement Plan's north-star discipline.

---

## Sequencing
Phase 0 is short and unblocks the reach-vs-retention read. Phases 1 and 3 run in parallel — different sources, no dependency. Phase 2 needs Phase 0. Phase 4 needs all.

## Risks
- **Confounded sample.** Top performers are also the newest, event-timed, and Flow-State-amplified. Formats have not been tested against each other under equal conditions.
- **Small-n per format.** 101 posts across many formats; few formats have enough posts to judge alone. Phase 3 compensates.
- **The tempting wrong answer:** "post more event content, it performs." The baseline already refutes it — the best-performing post in 90 days converted zero followers. Volume of the wrong content is not the fix.
- **The other tempting wrong answer:** "abandon the visualizers." They may be a retention/catalog asset that IG simply does not distribute. Phase 0 retention data and Phase 3 comps decide this, not view counts.

## Open items
- Phase 0 mobile pull (retention + follows-per-post).
- Where the 20 link taps land; is `wobar.music` instrumented.
- TikTok `wobar1` status.
- Per-post dates for the full history.
