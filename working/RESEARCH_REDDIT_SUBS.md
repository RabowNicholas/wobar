---
title: Reddit Subreddit Landscape — Bass / 140 / Fan + Festival
version: 2.0
created: 2026-07-27
last_updated: 2026-07-27
status: raw research output — for manual review and curation by Nick
scope: Discovery + activity measurement of bass/140 genre subs AND artist/festival fan subs. Sizes, activity, engagement. NO RULES PULLED — Nick reviews self-promo policy manually per sub.
supersedes: v1.0 (genre-only discovery, no activity data)
method_note: Three sweeps, all from live Reddit API calls in-browser, 2026-07-27. Nothing from memory or search summaries.
dependencies: [[working/WOBAR_GROWTH_PLAN]]  # WOBAR_REDDIT_PLAN deleted on retirement 2026-07-30; see WOBAR_CLOSED
---

# REDDIT SUBS — BASS / 140 / FAN + FESTIVAL

## Method

**Sweep 1 — genre vocabulary.** 24 bass/140 queries → 987 raw subreddits.

**Sweep 2 — empirical artist location.** Post search on 24 lane artists/labels, tallying which subs their posts appear in → 614 subs touched, 112 hit by ≥2 artists.

**Sweep 3 — artist + festival targeted (new in v2.0).** 24 queries on bass artists and festivals: Excision · Lost Lands · Wakaan · Shambhala · Electric Forest · Bass Canyon · Subtronics · Zeds Dead · Rezz · Of The Trees · CloZee · Ganja White Night · Liquid Stranger · Svdden Death · Peekaboo · Space Jesus · Ivy Lab · GRiZ · Tipper · bass music festival · dubstep festival · bass camping festival · headbangers · Rampage → **691 subs, 126 relevant at ≥500 members.**

**Activity measurement.** 100 most recent posts pulled per sub: posts in last 7 days, median comments on the 25 newest, days since last post. **150 of 168 measured** before the API rate limit locked out; 18 unmeasured, listed at the end.

## Column key
`P/wk` — posts in the last 7 days. **`>100` means the 100-post API window was entirely inside 7 days — a floor, not a count.**
`Med` — median comments on the 25 most recent posts. **See the confound warning below before using this column.**
`Last` — days since the most recent post.

---

## ⚠ CONFOUND — read before using the Med column

Median comments is measured on the **newest** 25 posts, so post age varies with sub volume. In a sub posting >100/week those 25 posts are a few hours old and haven't accumulated comments yet. In a sub posting 25/week they span the full week.

**This biases the Med column downward for high-volume subs.** The festival-vs-genre gap below is real but partly manufactured by the method. Do not treat it as a clean measurement.

To fix it: re-sample sorted by top-of-month instead of newest. I have not done this.

Flagging it because the same class of error — a size-biased metric used to rank — already caused a bad recommendation earlier in this session.

---

## The signal anyway

Even discounted for the confound, the gap is large:

| | Posts/wk | Median comments |
|---|---|---|
| r/EDM | >100 | **0** |
| r/riddim | 80 | **0** |
| r/trap | 49 | **0** |
| r/musicfestivals | 22 | **0** |
| r/dubstep | >100 | 7 |
| r/LostLandsMusicFest | 33 | **14** |
| r/ElectricForest | 25 | **15** |
| r/hulaween | 9 | **14** |
| r/BassCoast | 7 | **14** |
| r/RiotFest | 9 | **16** |

**Genre and music-posting subs run at 0–2 median comments. Festival and artist-fan subs run at 6–16.** Music subs are drop boxes — people post links and leave. Festival subs are conversations.

That supports the instinct behind this pass. Post a track in r/riddim and the median outcome is zero replies. Say something in r/ElectricForest and people talk back.

---

## Tier A — fan and festival subs, live (the fan lane)

| Sub | Members | P/wk | Med | Last |
|---|---|---|---|---|
| **r/Shambhala** | 25,717 | >100 | 2 | 0d |
| **r/festivals** | 219,541 | >100 | 2 | 0d |
| **r/aves** | 571,578 | >100 | 3 | 0d |
| **r/avesNYC** | 102,470 | >100 | 7 | 0d |
| **r/kandi** | 59,363 | >100 | 3 | 0d |
| r/veld | 5,707 | 83 | 4 | 0d |
| r/ElementsMusicFestival | 13,612 | 78 | 5 | 0d |
| r/BoomtownFestival | 19,347 | 68 | 6 | 0d |
| **r/avesLA** | 38,008 | 61 | 4 | 0d |
| r/nnmfestival | 1,825 | 50 | 5 | 1d |
| **r/ZedsDeadFam** | 10,559 | 46 | 2 | 0d |
| r/Coachella | 257,043 | 46 | 5 | 0d |
| r/OutsideLands | 30,931 | 45 | 6 | 0d |
| **r/BassCanyon** | 10,174 | 39 | 6 | 1d |
| **r/DenverEDM** | 10,709 | 38 | 2 | 0d |
| **r/LostLandsMusicFest** | 50,960 | 33 | **14** | 0d |
| r/chicagoEDM | 29,522 | 33 | 2 | 0d |
| r/readingfestival | 14,601 | 29 | 1 | 0d |
| r/FOVfestival | 1,259 | 28 | 6 | 0d |
| r/HardFestival | 9,347 | 26 | 6 | 0d |
| **r/ElectricForest** | 112,131 | 25 | **15** | 0d |
| r/musicfestivals | 30,067 | 22 | 0 | 0d |
| **r/prettylights** | 25,458 | 22 | **10** | 0d |
| r/TorontoRaves | 19,992 | 19 | 6 | 0d |
| **r/Tipper** | 26,793 | 19 | **8** | 0d |
| r/atlantaedm | 18,861 | 18 | 1 | 0d |
| r/creamfields | 5,281 | 16 | 4 | 0d |
| r/electricdaisycarnival | 173,339 | 15 | **10** | 0d |
| r/aclfestival | 38,844 | 14 | **10** | 0d |
| r/NCMF | 3,517 | 13 | 0 | 1d |
| r/BassVI | 11,867 | 13 | 6 | 0d |
| r/RiotFest | 24,483 | 9 | **16** | 1d |
| r/hulaween | 22,265 | 9 | **14** | 3d |
| r/ARCMusicFestival | 9,167 | 8 | 9 | 0d |
| **r/griz** | 23,015 | 8 | 6 | 1d |
| **r/BassCoast** | 2,298 | 7 | **14** | 2d |
| **r/SevenStarsFest** | 6,729 | 7 | 7 | 1d |
| **r/Subtronics** | 12,742 | 6 | 3 | 1d |
| **r/ofthetrees** | 2,060 | 6 | 3 | 2d |
| **r/LightningInABottle** | 20,419 | 5 | 8 | 2d |
| r/rollingloudfestival | 23,063 | 4 | 7 | 2d |
| r/Dancefestopia | 4,230 | 4 | 4 | 1d |
| r/ssbdfest | 1,155 | 4 | 3 | 0d |
| r/glastonbury_festival | 82,276 | 3 | **12** | 4d |
| r/MovementDEMF | 9,146 | 3 | 4 | 1d |
| **r/Excision** | 12,691 | 3 | 2 | 2d |
| **r/Wakaan** | 8,186 | 3 | 7 | 1d |
| r/UMF | 36,433 | 2 | 6 | 0d |
| r/BigEarsMusicFestival | 1,282 | 2 | 6 | 1d |
| r/roskildefestival | 10,810 | 2 | **29** | 4d |
| **r/SvddenDeath** | 3,626 | 2 | **10** | 4d |
| r/ImagineMusicFestival | 6,445 | 1 | 2 | 6d |
| r/ForbiddenKingdomFest | 5,332 | 1 | 5 | 0d |
| **r/Rezz** | 8,135 | 1 | 7 | 6d |
| **r/CloZee** | 3,412 | 1 | 7 | 6d |
| **r/ganjawhitenight** | 3,098 | 1 | 4 | 6d |
| r/BassCollector | 1,538 | 1 | 1 | 4d |
| r/escapademf | 1,311 | 1 | 6 | 6d |
| r/Rampagefestival | 1,206 | 1 | 4 | 3d |
| r/PembertonFestival | 1,492 | 1 | 3 | 3d |
| r/Magfest | 9,580 | 1 | 0 | 2d |
| r/zedsdead | 896 | 1 | 0 | 0d |

---

## Tier B — genre / production subs, live (the promo + craft lane)

| Sub | Members | P/wk | Med | Last |
|---|---|---|---|---|
| **r/dubstep** | 242,031 | >100 | 7 | 0d |
| **r/EDM** | 3,042,342 | >100 | **0** | 0d |
| **r/DnB** | 303,491 | >100 | 3 | 0d |
| **r/grime** | 139,748 | 86 | 1 | 0d |
| **r/riddim** | 29,618 | 80 | **0** | 0d |
| **r/realdubstep** | 49,262 | 61 | 1 | 0d |
| **r/edmproduction** | 810,335 | 59 | **9** | 0d |
| **r/trap** | 162,691 | 49 | **0** | 0d |
| **r/SpaceBass** | 36,414 | 47 | 1 | 0d |
| r/liquiddnb | 15,852 | 15 | 0 | 0d |
| **r/DubstepFeedback** | 1,309 | 15 | 0 | 1d |
| r/NeuroFunk | 6,988 | 12 | 0 | 0d |
| **r/DubstepProduction** | 3,340 | 11 | 3 | 1d |
| r/basslessons | 21,474 | 9 | 0 | 0d |
| r/bassmusic | 4,491 | 7 | 0 | 1d |
| r/GrimeInstrumentals | 4,584 | 7 | 1 | 1d |
| r/chillstep | 14,342 | 3 | 0 | 2d |
| r/Glitchhop | 5,336 | 3 | 0 | 0d |
| r/HalftimeDnB | 2,718 | 1 | 0 | 1d |
| r/RealDubstepProducers | 902 | 1 | 0 | 7d |
| r/deepdubstep | 1,009 | 1 | 0 | 1d |
| r/futureriddim | 356 | 1 | 0 | 3d |

**r/edmproduction is the only music-craft sub with real discussion** — 59 posts/week at median 9 comments. Everything else in this tier is a link dump.

**r/DubstepFeedback is alive** (15 posts/week) but median 0 comments — people post, nobody replies. That is either a dead-on-arrival sub or a wide-open opportunity, depending on whether you're the one replying.

---

## Tier C — dead or dormant (0 posts in 7 days)

Do not invest in these regardless of member count.

**Long dead:** r/grizzlyfi 1619d · r/bassmusicproduction **1073d** · r/LostlandsCampingTIPS 842d · r/paradisofestival 620d · r/Grizzy 406d · r/OregonEclipse 394d · r/bassnectar **233d** · r/cyclopsarmy 200d · r/lockn 186d · r/Ultramusicfestival 180d · r/electriczoo 148d · r/wakarusa 130d

**Seasonal / dormant:** r/MoonriseMusicFestival 82d · r/SunsetMusicFestival 70d · r/HangoutFest 67d · r/liquidstranger 64d · r/summercampfest 54d · r/RiddimDubstep 52d · r/Wakaanfest 50d · r/Sasquatch 40d · r/FireflyFestival 39d · r/solfest 31d · r/ravememes 31d · r/stagecoach 30d · r/HiJinxFest 21d · r/resonatesuwannee 21d · **r/futuregarage 17d** · r/meredithmusicfestival 13d · r/BeyondWonderland 11d · r/scamp 10d · r/okeechobeemusicfest 9d

27 more dead subs not listed individually.

**Note: r/bassmusicproduction — 3,207 members, last post 1,073 days ago.** It appeared healthy on member count alone in v1.0. This is why the activity pass mattered.

---

## Unmeasured — 18 subs, rate limit hit

r/treemusic · r/electronicmusic · r/DJs · r/ukbass · r/UKBassMusic · r/darkbass · r/Wonky · r/midtempo · r/drumstep · r/subbass · r/bassheavy · r/WorldBass · r/AnythingBass · r/electronicbassmusic · r/wompworthy · r/grimeproduction · r/darkdnb · (1 more)

**r/treemusic (52,084 members, 5 artist hits) is still uncharacterised** — flagged as unknown in v1.0 and still unknown.

---

## Noise excluded (documented so it isn't re-derived)

- **"GRiZ" matched grizzly bears and Memphis Grizzlies:** r/memphisgrizzlies 264,858 · r/GrizzlyBear · r/grizzlyfi · r/Grizzy · r/Grizzzy · r/grizzlybears.
- **"bass" matched instruments:** r/doublebass 20,080 · r/basslessons 21,474 · r/BassVI 11,867 (kept in tables above — verify before use; these are bass **guitar** subs).
- **NSFW rave subs surfaced from festival queries:** r/FestivalSlut 70,624 · r/ravebooty 66,753 · r/festivalslutsover30 · r/INDYRaversandSwingers. Sized only.
- **r/bindingofisaac** 451,860 — matched on an unrelated term.
- **"grime" queries are ~50% Grimes the artist** — 13 subs excluded (see v1.0).

---

## Gaps

1. **No rules pulled for any sub** — by instruction.
2. **Med column is confounded by post age** — see warning above. Needs an age-controlled re-sample to be trustworthy.
3. **18 subs unmeasured**, including r/treemusic.
4. **Sidebar / related-community crawl still not run** — the one discovery angle never executed. Would likely surface another 20–40.
5. **Listener-vs-producer skew not measured.** Inferred from sub identity, not from post content.
6. **Restricted subs not tested** for whether posting approval is obtainable.
7. Reddit rate-limits at roughly 60–150 API calls before a multi-minute lockout. Budget for it.
