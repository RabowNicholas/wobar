---
title: Wobar Context Index
version: 1.3 (+ mastering docs registered 2026-08-01)
last_updated: 2026-08-01
status: live
scope: Master index for all Wobar reference files. Read this first in every conversation.
dependencies: none
---

# WOBAR CONTEXT INDEX

This is the index file for the Wobar project reference system. Read this file first. Pull additional files only as needed for the task at hand.

---

## ⚖ THE DRIFT RULE — read before editing any file

*Added 2026-07-27 after two drift failures in one week. The vault is large enough that duplicated facts now age independently and produce wrong decisions.*

### 1. Form vs state

| | Holds | Files |
|---|---|---|
| **`reference/` — locked** | **Form and identity.** What doesn't change: positioning, registers, laws, archetypes, conventions, formats. | BRAND · SONIC · COPY · GRAMMAR · FRAMEWORK · WORLD · CONTENT · ARCHIVE |
| **`working/` — live** | **Strategy and state.** Decisions, constraints, current position, door statuses, open questions. | GROWTH_PLAN · ACTIVE · PLACEMENT_PLAN · RESEARCH_* |

**A locked doc must never contain a number that will be wrong in three months.** No cadences, no catalogues, no follower counts, no current-target lists. If it changes, it lives in `working/` and the reference doc points at it.

**And the vault holds no operations at all.** The **release schedule** — calendars, release dates, T-minus counters, per-release packet checklists — **does not live here** (removed 2026-07-30, Nick's call). Nick runs it. The vault holds the *rate* as a strategic commitment ([[working/WOBAR_GROWTH_PLAN]] §1) and nothing else about scheduling.

### 2. One owner per fact

Every mutable fact has **exactly one owning file**. Every other mention is a `[[link]]` to the owner, never a copy.

| Fact | Owner |
|---|---|
| Output rate / release cadence | [[working/WOBAR_GROWTH_PLAN]] §1 |
| Label targets, door status, tiering | [[working/RESEARCH_LABEL_LANDSCAPE]] §2 |
| **Collab targets — artists and labels, by tier** | [[working/WOBAR_COLLAB_TARGETS]] (**desire only** — door status stays with LANDSCAPE §2) |
| Position metrics (listeners, followers, submissions sent) | [[working/WOBAR_GROWTH_PLAN]] |
| Current state of live threads | [[working/WOBAR_ACTIVE]] |
| The goal, and what a fan is | [[working/WOBAR_ROADMAP]] §1 |
| Mirror door copy + SMS acquisition model | [[working/MIRROR_THRESHOLD_SPEC]] §0 |
| Surface **roles** (what each organ is) | [[reference/WOBAR_WORLD]] §7.5 |
| Surface **exposure status + decisions** | [[working/WOBAR_SURFACES]] |
| **Instagram / TikTok role, content buckets, peer funnel** | [[working/WOBAR_SOCIAL_PLAN]] |
| Reference artists / comps, by register | [[reference/WOBAR_SONIC]] — the six-register table |
| **Mastering posture** (form — why it's done this way) | [[reference/WOBAR_SONIC]] — Mastering — the posture |
| **Mastering chain values + reasoning** | [[working/WOBAR_MASTER_CHAIN_V1]] |
| **Mastering procedure** (what to actually do) | [[working/WOBAR_MASTER_CHECKLIST]] |
| Bio copy (EPK + world-facing) | [[reference/WOBAR_COPY]] — BIO TEMPLATES |
| Reddit strategy | **Loop RETIRED 2026-07-28.** The plan was deleted 2026-07-30 (action items for a dead channel); the *findings* survive in [[working/WOBAR_CLOSED]] and [[working/RESEARCH_REDDIT_SUBS]] |
| Released catalogue | **No owner yet — deliberately not in a locked doc.** Needs a working file if it's wanted |

### 3. Shape matters as much as content

A **flat list standing in for a structured thing** is a drift generator, not just an error. The 2026-07 comp failure wasn't five wrong names — it was one list where six registers belonged, and every doc downstream inherited whichever register sat on top. **Before writing a list into a reference doc, ask whether the thing actually has structure.**

### 4. What went wrong, so it isn't repeated

- **Comps** — `Of The Trees / Shlump / INZO` sat flat in BRAND, propagated into SONIC and the **EPK bio**, and put psy-bass references in front of wonky-140 labels. Cost: four wrong label targets and a pitch that misdescribed the artist. Shlump had never appeared in the benchmark set at all.
- **Cadence** — "one per month" lived in SONIC, CONTENT **and** the Growth Plan at once. The copies drifted; only the Growth Plan's was current (it includes flips).
- **SubCarbon** — recorded as sub.mission's Denver label on a naming collision; it is Belgian. Voided a whole strategic chain in the Placement Plan and helped keep a loop open for a month.

---

## File Registry

### Project / Brand
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[skills/README]] | /skills | Source of truth for WOBAR Claude skills — `~/.claude/skills/` on each machine is a synced copy | live |
| [[working/WOBAR_ACTIVE]] | /working | **Current context — read at session start.** Position, live threads, standing traps. **Context, not a task tracker:** what is live, decided, blocked or genuinely open. No next-action lists, no session recaps — Nick tracks his own work. Rebuilt v2.0 on 2026-07-30 | live (v2.0) |
| [[working/WOBAR_SESSION_LOG]] | /working | **Frozen archive** of session narratives, split out of WOBAR_ACTIVE 2026-07-30 (it was 79% of the file that gets loaded every session). Read only when reconstructing *why* something was done. **Do not append** — git is the change log | archive |
| [[working/WOBAR_CLOSED]] | /working | Completed project loops, archived from WOBAR_ACTIVE | live |
| [[working/WOBAR_GROWTH_PLAN]] | /working | **GOVERNING — read before any growth/content/platform decision.** 12-month goal (people listening, online): SoundCloud-first, flips as a numbered main-account series, originals to a 2-track reserve on day-60 calendar release, DJ promo, IG demoted to a 5-second credibility surface. Every claim confidence-tagged. **Owner of: output rate (§1) and position metrics.** §4 label doors rebuilt 2026-07-27 from browser-verified data — the old 7-door list was psy-lane. Supersedes the social strategy in WOBAR_CONTENT | live (v1.1) |
| [[working/WOBAR_SURFACES]] | /working | **The two-axis surface map.** §1 the **depth ladder** (0 sound → 4 the centre) with every surface placed, and §1.5 the **duration axis** — how long each surface holds someone, which is what actually produces a return. Together they show: depth 1 is the emptiest and cheapest band · **live is strongest on both axes and is still marked *undesigned*** · depth 2 has no home, so *"someone who loves the music has nowhere to meet the person"* · an unfilmed set converts only the bodies present. Carries the **pre/post-experience test** and the note that **structural exposure never violates §8**. Owns exposure status; roles live in WORLD §7.5 | live (v2.1) |
| [[working/WOBAR_ROADMAP]] | /working | **GOVERNING — the strategy layer.** §1 owns **the goal — *"12 months: people who come back"*** — plus what a fan is (returns → seeks it out → passes it on; **fan ≠ follower**; ladder listener → fan → Wanderer) and the **duration principle** (fans are made by duration, not reach). §2 the funnels — self-release is the only one that exits; labels/flips/DJ feed it — with the **peer layer** beside them and the **owned layer** beneath. §3 standing rules (private links only, day-60 is a date, cap the reserve at two). §4 sequence constraints + **the catalogue gap: register 2 empty, register 3 has one track.** §5 how you'd know it's working. §6 what it doesn't know. **Trackers removed 2026-07-30** — the cadence table, six phase gates and leading scorecard were work-tracking, not strategy | live (v1.1) |
| [[working/WOBAR_SOCIAL_PLAN]] | /working | **GOVERNING for Instagram and TikTok.** Socials are a **peer-facing surface — the audience is producers and DJs, not fans**; output is credibility and conversations, never followers/reach/streams. Target tier = **one rung up (2K–20K)**, because Flow State only has value to people at or just above this stage. Three buckets — **CUTDWN's list adopted verbatim 2026-08-03**: **performance** (Discovery; ⚠ capture-gated and capture is parked, so the top of the funnel is currently empty), **music** (Ability — prevent dismissal; legibility not brand), **give-back** (Credibility — *where you differentiate*; broadcast deferred, **1:1 starts now, and it is worth more at 55 followers than it ever will be again**). **§3.5 = memes, demoted from a bucket to a format** — nothing was disproved, it lost a taxonomy argument — and carries the **CUTDWN failure-mode rail**, promoted plan-wide because it governs any non-music content that outperforms the music. Funnel: performance → engagement → **triage** → proof → **outbound warm DM** → **SoundCloud, not a smart link** — ⚠ **and its mouth is currently blocked**, which surfaces the 2026-07-30 finding (*top of funnel searched for and not found*) in the taxonomy instead of hiding it. **§1 carries the correction that the vault's 316-send "distribution is not the constraint" finding was a Flow State collab and is void.** §7 records four unresolved holes. Supersedes the Platforms table in WOBAR_CONTENT | live (v1.1) |
| [[working/WOBAR_GIVEBACK_NICHE]] | /working | **GOVERNING for bucket 3 content — the niche, decided 2026-08-04.** Audience = **DJ-producers who do both** (structural, not demographic: they are the only ones who have felt the mechanic at both ends, so the thesis is checkable against their own memory rather than taken on faith). Vocabulary = **tension and release**. Thesis = **the mechanic never changes, only the scale does**. §2 the diagnosis the niche rests on — **jargon is compression**; beginners already understand tension/release at 8 bars, and *"tell a story"* is a veteran describing the same physics at a scale they've never operated at. The job is **decompression, not doctrine** — which is also the only version safe without credentials. §3 the **six-rung scale ladder** (rungs 2–5 are the territory, the **3↔4 crossing is the lane**, rungs 1 and 6 are weak) plus the **collective protagonist** at rung 4. §4 why the hero's journey doesn't map — plot is causation, music has none; what persists is a shape, **the cycle is fixed and the proportions are free**, so the numbers must never be fixed. §5 inherited format constraints: **show don't explain · say `tell a story` never `storytelling` · think in public, never claim results** | live (v1.0) |
| [[working/GIVEBACK_CONTENT_PLAN]] | /working | **The content bank for bucket 3 — five lists, fifteen pieces, zero scripts.** OWNS the idea set and its cuts; thesis and territory stay in [[working/WOBAR_GIVEBACK_NICHE]] and are not restated. **§1 the rule that shapes everything: duration is not length, it is what kind of claim you are allowed to make** — 15s can only provoke, 45s buys one turn, 90s carries a full case, and a 15s piece is a *different genre* from the 90s one, never a cut-down. Every piece carries its claim, its **on-screen object** and its native duration. §2 the standing constraints — **negative examples must be big enough to take it** (using a small artist is punching down at the peer audience this bucket serves), check every number, and **concede the enemy's case first**. §3–§7 the lists: frequency vs character · contrast axes · the freedom argument · the myths · **interactive, which is the spine and outranks the rest because it is the only list where Nick is not the authority**. §8 the cuts, recorded so they aren't re-proposed. §9 the four open items — **including two of the best lines having no object solved** | live — ideas locked, no scripts |
| ~~`working/RESEARCH_PLAN_BRAND`~~ | — | 🔴 **RETIRED and DELETED 2026-08-04.** The plan for a series teaching brand theory to small artists — *archetypes · brand voice · visual identity*, on a **curator-not-judge / no-teardowns-yet** posture. **Killed by the research it commissioned:** the format had already been run properly by someone else and died at 150–700 views, the space is occupied by better-credentialed operators, and the audience actively punishes uncredentialed strategy teaching. Deleted rather than kept, per the Reddit-plan precedent — a retired plan still gets read. **The evidence survives in [[working/RESEARCH_BRAND_PSYCHOLOGY]], the subject survives as belief 2 of [[working/WOBAR_GIVEBACK_NICHE]], and the full narrative — including what died, what survived, and the two method lessons the round paid for — is in [[working/WOBAR_CLOSED]].** Do not rebuild the educational frame from the research file | retired |
| [[working/RESEARCH_BRAND_PSYCHOLOGY]] | /working | **What the evidence actually says about brand theory.** ⚠ **Read as evidence, not as a plan** — it was commissioned for an educational series that it then killed; that frame is RETIRED (see [[working/WOBAR_CLOSED]]) and must not be rebuilt from this file. Four briefs, every claim evidence-graded, load-bearing citations verified independently against source. **§1 the headline: the evidence base does not reach a brand this small — and its own authors say so.** Barker-Trowse/Sharp et al. (2026, *JBR*) states brands under 1% share were "overlooked… we know little"; Sharp's own 2002 paper names stationarity and non-partitioning as necessary conditions, so a brand growing from zero sits outside the law's stated scope. The authority available is **methodological, not findings**. **§2 the space is occupied** — a 71.7K-sub channel runs the exact concept in the exact genre — **and the null result is the finding: `effi summers creative` ran the proposed product properly and got 150–700 views.** **§3 archetypes — both the agency claim and the dismissal are wrong**; the twelve come from a 1991 self-help book, not Jung. **§4 the exemplar map**, ranked on transfer to a no-budget artist, with the failures section as the richest untouched material. **§5 four briefs converge on criticism of the lane, not education for it.** **§6 flags a live collision with [[working/WOBAR_ROADMAP]] §1** — deficit loyalty at the small end vs a return-first goal — stated as open, not resolved. §7 the biggest gap: short-form was never measured | raw research — unreviewed |
| [[working/RESEARCH_STORYTELLING]] | /working | **What the internet actually says about storytelling in music, DJing and artist branding.** Reddit-primary, source material for the give-back content niche. Every claim carries an evidence grade (✅ verified / 🟡 reported / ❌ void). **§0 records a method failure and its resolution: WebSearch cannot reach Reddit at all, and every "found nothing" claim in the run was a rate-limit artifact. A controlled re-sweep (85 queries, 8 controls, all passed) found ZERO absences — killing the confident-but-false "endings are under-discussed" finding. §9 is now a standing rule: a scraped zero is not evidence until a control passes in the same pass.** **§6.5 = the attention map, and it carries Nick's framing correction: saturation is the TARGET, thin means nobody cares — an unoccupied niche is usually uninteresting. Its usable output is that `tell a story` is saturated while `storytelling` is thin in every craft sub: the noun is a marketer's word, the verb is native. §6.6 is the strategic finding — the topic is over-asserted and under-demonstrated; "mix to tell a story" is a cliché the community complains about because nobody shows examples, abstract narrative posts score 0 and a real five-hour-set writeup scores 648. Show it, don't explain it.** Live findings: the demand is real and beginners describe structure in emotional language (*boring, empty, goes nowhere*) while getting technical answers · DJs say **journey**, not narrative — the narrative vocabulary is educator-side, top-down · **cohesive ≠ narrative** is a live unresolved argument among engaged listeners · one verified stranger states the whole thesis — *"fans connect to consistency of world, not access to your kitchen"* · **§5 the credential reaction: thinking in public is safe, claiming results is not** | raw research — unreviewed |
| [[working/RESEARCH_VERIFICATION_MEMO]] | /working | **Read before trusting any 2026-07-26 research file.** 13-agent adversarial verification — 9 of 10 claims UNSUPPORTED, two sub-reports contained fabricated data. What survived, what didn't, and what nobody has measured | live |
| [[working/RESEARCH_LABEL_LANDSCAPE]] | /working | **GOVERNING for label targeting.** Tiered door list for the dark/wonky 140 lane, verified 2026-07-27 by direct browser load. Two screens do the work: **founder share of Top 10** (kills release vehicles) and **set overlap** (Nick's own set vs each label's top sellers). Deadbeats' free 4-field Google Form is the headline. **§2.5 = the Beatport visibility sweep** (sales vs editorial are two different systems; best-fit doors have near-zero visibility). **§2.6 = the artist-discography sweep — 22 new labels and the VA compilation economy: ten recurring multi-artist series, most 20+ artists per volume, all live. A 29-slot compilation vs a one-slot signing is the biggest strategic find in the file.** Supersedes the door/tier tables in RESEARCH_LABEL_MAP and the label section of WOBAR_GROWTH_PLAN | live (v4.0 — unreviewed) |
| [[working/WOBAR_COLLAB_TARGETS]] | /working | **The collab ladder — dream artists and labels, top-down from untouchable to local.** OWNS the target set and **what the ask actually is at each rung**; door status stays with RESEARCH_LABEL_LANDSCAPE §2 and reference artists with WOBAR_SONIC. **Structured by register inside each tier, never flat** — a flat collab list is the 2026-07 comp failure repeated. §0 the five things that shape it: **collabs are never won by submission** (T1 is submission-shaped, T3/T4 collaboration-shaped, and the rung between is introduced not climbed) · **Flow State is calibrated to exactly one rung (T3, 2K–20K)**, which makes T3 the only tier where Nick has something to trade today · the **free visualizer** is the T2 currency · and **the realistic first "collab" is a VA tracklist, not a joint track**. §1 artists T0–T5, **STVSH the anchor** (most-played in Nick's own set and on three of four verified-open doors) and **Wormhole's whole top 10 sitting in T3**. §2 labels, with the **tier ≠ difficulty** warning — Deadbeats and Subsidia are ceiling by size and floor by access. §3 the ask-per-rung table and the sequencing that falls out: **the list is worked from the bottom.** **🔴 T4 (peer) and T5 (local/SLC) are empty and only Nick can fill them** — every discovery method run so far is structurally incapable of surfacing them. No follower numbers by design; **tier placement is unverified judgment** | live (v1.0 — bottom two rungs owed) |
| [[working/RESEARCH_REDDIT_SUBS]] | /working | 🔴 **RETIRED 2026-07-28 — reference only.** Discovery + activity data, 179 bass/140/fan/festival subs, 150 activity-measured. Three sweeps: genre vocabulary · **empirical artist-location** (where the lane's posts actually live — a method reusable on any platform) · artist+festival. **Finds r/SpaceBass (36,414, 16/24 lane artists, "Genre Defying Bass")** and kills 57 dead subs incl. r/bassmusicproduction at 1,073 days. **Genre subs run 0–2 median comments; festival/artist subs run 6–16** — carries its own confound warning on that column | retired (v2.0) |
| [[working/RESEARCH_LABEL_MAP]] | /working | Where the artists in Wobar's set actually release. Three lanes (US wonky-140/flip · psy-bass · deep dubstep), label→artist map, Beatport chart read, adjacent-artist list. **Door status superseded by RESEARCH_LABEL_LANDSCAPE** | live (partly superseded) |
| [[working/RESEARCH_SOUNDCLOUD_COMPS]] | /working | Cross-platform comp table (SoundCloud vs IG vs Spotify listeners) for 14 lane artists. Carries corrections — see header | live |
| [[working/RESEARCH_IG_COMPS]] | /working | Instagram comp sweep v2, neutral-frame sampled from label rosters. v1's cohort was convenience-sampled; two findings retracted | live (v2.0) |
| [[working/RESEARCH_IG_CONVERSION]] | /working | Does IG convert? Study A (IG vs Spotify listeners) + Study B (do labels gate on audience). Study B survives; Study A downgraded — see header | live |
| [[working/RESEARCH_IG_MECHANICS]] | /working | IG platform mechanics 2026 — ranking signals, Trial Reels, Meta Series, source-tiered claims table | live |
| [[working/IG_COMP_SAMPLE_FRAME]] | /working | The sampling frame + handle-resolution method behind the comp sweeps. Documents the convenience-sampling failure and the fix | live |
| [[working/WOBAR_PLACEMENT_PLAN]] | /working | Get-heard strategy — the **lever map** (curators · promoters/scene · labels · DJ promo), promo-service verdicts, DIY ads playbook. **Its Target Label Roadmap is superseded** (psy-lane; Deadbeats' DROPPED verdict reversed) → use RESEARCH_LABEL_LANDSCAPE. The Denver convergence thesis is void — SubCarbon is Belgian, Memory Palace is closed; that loop is parked | live (v1.3 — partly superseded) |
| [[working/MIRROR_THRESHOLD_SPEC]] | /working | Mirror Threshold build spec — the SMS door into the Ether; Twilio + Next.js/Neon/Vercel integration, state machine, compliance. **§0 = the acquisition model (2026-07-27)** — the funnel inverted from volume to relationship, **door copy LOCKED** (plain, never reaching), ~40 right people not volume, passive placement is texture / personal invitation is mechanism, and the fifth glimpse format: **unreleased music sent for reaction**. **Owns door copy.** Blocked on 10DLC | live (v0.2) |
| [[working/RESEARCH_REDDIT_SUBS]] | /working | Subreddit landscape for bass/140 — sizes + descriptions from live Reddit API calls, two independent sweeps (vocabulary + empirical artist-location). **No rules pulled — self-promo policy is a manual per-sub review.** Companion data for WOBAR_REDDIT_PLAN | raw research — awaiting review |
| [[working/WOBAR_MASTER_CHECKLIST]] | /working | **The per-track mastering procedure — open this to work.** Nine steps from production render to logged master, with the fail-condition table and the standing rules. Only two things are decided per track: EQ (0–2 moves) and Maximizer Gain | live (v1.0) |
| [[working/WOBAR_MASTER_CHAIN_V1]] | /working | **GOVERNING for mastering — the reasoning behind every value.** Built for real 2026-08-01 in Ableton and saved as a template; v1 was research, v1.1 is what survived contact. Governing design principle: **bounded error, not optimality** — under this monitoring every setting is chosen so being wrong is survivable. Carries the Ableton rig (warp, pre-fader master, the A/B compensation rig), the **render standard** that makes Stage 1 trim ≈ 0 on every track, and a change log that is the actual feedback loop. **Open items are load-bearing** — Soft Clip untested, GP still largely unmeasured | live (v1.1) |
| [[working/RESEARCH_MASTER_CHAIN_TOOLS]] | /working | Tool capability research behind the chain — includes the unrun GP measurement protocol (Part 6) | live |
| [[working/RESEARCH_MASTERING_EDM_DUBSTEP]] | /working | Mastering practice research for the genre. Source of the Shepherd short-term rule and the Jason Goz loop | live |
| [[working/WEB_HOME_SPEC]] | /working | The web home = a terminal you wander (early-RPG), guided by *the daemon*; full rebuild of wobar-landing-page; paths, offerings, AI rails | live |
| [[working/WOBAR_VISUAL_RESET]] | /working | **The visualizer design system — READ BEFORE ANY VISUALIZER BUILD.** Audits the old visual system vs world v0.6, then supplies the spine: the corridor is the *artifact* of perception failing to render a higher dimension (not the territory) — from which non-arrival, the drop-as-failure, and the stable-then-collapse arc all follow. §3 = the spec. Governs all visualizer work; supersedes the per-act material affinities in TD_REFERENCE §3/§4 | live (v0.2 — spine locked) |
| [[prototypes/corridor/README]] | /prototypes/corridor | **Look-dev sketches — prototype HERE, port to `glslTOP` after.** Holds the Nick-approved collapse mechanic (4× same corridor, superposed, no SDF booleans, weights equalizing) + the convergence-point find + 5 recorded dead ends so they aren't re-derived. Companion build-side to VISUAL_RESET §3 | live |
| [[reference/WOBAR_BRAND]] | /reference | Foundation, mission, archetypes, beliefs, positioning | locked |
| [[reference/WOBAR_WORLD]] | /reference | World mechanics — ground truth, geography, 3-version cycle, two-axis entity/the source, sacred, lexicon (Mirror/seeing/Wanderer/the Ether/glimpses/the Passage/the mark/the daemon), the Ether content model + void poems, Surfaces of the World §7.5 | live (v0.6 draft) |
| [[reference/WOBAR_FRAMEWORK]] | /reference | 5-Act Portal Framework, act definitions, percentages | locked |
| [[reference/WOBAR_GRAMMAR]] | /reference | **The cross-modal grammar — the shared root beneath visual, copy, sound.** Law 0 (ground it, let depth emerge, never reach) + the six-law × three-surface table + the mirror principle + the utility-floor + the §8 register-gate. VISUAL_RESET/COPY/SONIC all derive from it. Read to keep the three surfaces one world | live (v1.0 — governing) |
| [[reference/WOBAR_COPY]] | /reference | **v2.0** — the mirror spine, the 4-register voice stack (light/daemon/journal/source), the act axis, the utility floor, reconciled lexicon, register-scoped anti-vocab, the 4 tests, the daemon deflection bank, EPK+world-facing bios. Derives from GRAMMAR | live (v2.0 — governing) |
| [[reference/WOBAR_SONIC]] | /reference | Sonic identity, reference artists, genre positioning; re-parented to GRAMMAR (v1.2). **§Mastering — the posture (v1.6, 2026-08-01)** holds the form-level mastering strategy: in-house from a fixed template, master follows mix, loudness is not a goal, sub is mono, bounded error over optimality | locked |
| [[reference/WOBAR_CONTENT]] | /reference | Content system, release architecture, posting | locked |
| [[reference/WOBAR_ARCHIVE]] | /reference | Archive sourcing by act, portal depth, pipeline | locked |
| [[reference/WOBAR_CLAUDE]] | /reference | How to work with Nick | locked |
| [[reference/WOBAR_PATCH_SYSTEM]] | /reference | Serum 2 patch naming, 8-macro standard, versioning | locked |
| [[reference/WOBAR_OBSCURA]] | /reference | Obscura visual identity and reference system | locked |
| [[reference/WOBAR_YOUTUBE]] | /reference | YouTube description system — fold rules, chapter/tracklist requirements, links/CTA order, hashtags, the Wobar template; utility floor + light register. Derives from COPY | live (v1.0 — governing) |

### TouchDesigner — Entry Point
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_INDEX]] | /reference | **TD entry point** — decision tree for which TD docs to load per task | live |

### TouchDesigner — Core Rules & Conventions
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_AGENT_RULES]] | /reference | Build conventions: naming, architecture, act constraints, Python rules | live |
| [[reference/WOBAR_TD_REFERENCE]] | /reference | Full specs: audio pipeline, visual primitives, color system, export — load by section | locked |
| [[reference/WOBAR_MOVE_SYSTEM]] | /reference | Move history system spec — JSON schema, lifecycle, network→comp mapping | locked |

### TouchDesigner — TWOZERO MCP
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TWOZERO_GUIDE]] | /reference | Confirmed type strings, parameter names, limitations, known behaviors | live |
| [[reference/WOBAR_TWOZERO_MCP_CATALOG]] | /reference | Full parameter tables for all 35 TWOZERO tools — load by group, not full file | live |

### TouchDesigner — Snippet Libraries
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_EXPRESSION_COOKBOOK]] | /reference | Paste-ready expressions: CHOP access, audio-reactive mappings, time, footguns | live |
| [[reference/WOBAR_GLSL_PATTERNS]] | /reference | Act-specific GLSL shaders (10 total), utility functions, act color reference | live |
| [[touchdesigner/reference_networks/README]] | /touchdesigner | Structural examples — node chains + taste decisions per network type | live |

### TouchDesigner — Session Logs
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[working/TD_CLAUDE_DEBUG_LOG]] | /working | Confirmed wrong advice + corrected patterns — read before any TD action | live |
| [[working/TD_BUILD_LOG]] | /working | Session-by-session build log — correction tracker, patterns | live |
| touchdesigner/networks/[network]/CHANGE_LOG.md | /touchdesigner | Per-network change log — why changes were made | live |
| touchdesigner/networks/[network]/moves/ | /touchdesigner | Per-network move history — JSON files for granular undo | live |

### TouchDesigner — General Library (brand-agnostic)
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/td_library/TD_LIBRARY_INDEX]] | /reference/td_library | **Entry point for general TD knowledge** — routes to operator catalogs, patterns, workflows | live |
| [[reference/td_library/TD_APPLE_SILICON]] | /reference/td_library | M1 constraints: Metal/MoltenVK, codec/license limits, Syphon/NDI state, sensor compatibility | live |
| [[reference/td_library/TD_NETWORK_VS_GLSL]] | /reference/td_library | Decision framework — when to use networks vs GLSL, hybrid patterns, red flags | live |
| [[reference/td_library/TD_EFFICIENT_NETWORKS]] | /reference/td_library | Cook model, Cook Type, Null discipline, CHOP→TOP bridging, GPU instancing, canonical templates | live |
| [[reference/td_library/TD_FOOTGUNS]] | /reference/td_library | 50+ general TD failure patterns (feedback, audio, network, render, POPs, MIDI/OSC, export, perform, platform) | live |
| [[reference/td_library/TD_OPERATORS_POP]] | /reference/td_library | Full POP catalog — 2025 GPU point ops (Generators, Transform, Attribute, Control, Simulation) | live |
| [[reference/td_library/TD_OPERATORS_TOP]] | /reference/td_library | Full TOP catalog by role — Generators, Filters, Compositing, GPU Shader, Feedback, Analysis | live |
| [[reference/td_library/TD_OPERATORS_CHOP]] | /reference/td_library | Full CHOP catalog by function — Audio, Analysis, Timing, Math, Hardware, Pattern, Export | live |
| [[reference/td_library/TD_OPERATORS_SOP]] | /reference/td_library | Full SOP catalog — Generators, Deformers, Modifiers, Attributes, Combinations, Specialty | live |
| [[reference/td_library/TD_OPERATORS_MAT]] | /reference/td_library | MATs — Constant, Phong, PBR, Point Sprite, Line, Wireframe, GLSL + assignment patterns | live |
| [[reference/td_library/TD_OPERATORS_DAT]] | /reference/td_library | DATs — Text/Script, Table, Format bridges, Web/Network + Python/Extension patterns | live |
| [[reference/td_library/TD_OPERATORS_COMP]] | /reference/td_library | COMPs — 3D Object, Container, Execution, Panel/UI + Geometry Instance cheat sheet | live |
| [[reference/td_library/TD_PATTERNS_AUDIO_REACTIVITY]] | /reference/td_library | 6-stage audio spine, band splits, onset detection, spectral analysis, tempo sync | live |
| [[reference/td_library/TD_PATTERNS_FEEDBACK]] | /reference/td_library | Feedback TOP loop, 3 critical params, 14 patterns (trails/tunnel/streaking/etc) | live |
| [[reference/td_library/TD_PATTERNS_GENERATIVE]] | /reference/td_library | Noise/flow/L-systems/reaction-diffusion/SDF raymarching/boids/Voronoi/metaballs | live |
| [[reference/td_library/TD_PATTERNS_3D_SCENES]] | /reference/td_library | Scene graph, camera control, lighting, PBR/IBL, depth, post stack, procedural environments | live |
| [[reference/td_library/TD_PATTERNS_INSTANCING]] | /reference/td_library | 10 instancing patterns (POP→Geometry, CHOP-driven, Replicator, data-driven, etc) | live |
| [[reference/td_library/TD_PATTERNS_COMPOSITING]] | /reference/td_library | Layer Mix vs Composite chain, blend modes, alpha, mattes, chroma key, post FX order | live |
| [[reference/td_library/TD_PATTERNS_PARTICLES]] | /reference/td_library | POP-based particle spine, emission, forces, lifespan + 7 canonical recipes | live |
| [[reference/td_library/TD_PATTERNS_TEXT]] | /reference/td_library | Text TOP/SOP/POP paths, typography patterns, audio-reactive text, data-driven text | live |
| [[reference/td_library/TD_WORKFLOW_OPTIMIZATION]] | /reference/td_library | Perf tuning protocol — measure, quick wins, feedback/render/DAT audits, debug protocol | live |
| [[reference/td_library/TD_WORKFLOW_EXPORT]] | /reference/td_library | ProRes pipeline, image sequences, upscaling around 1280 cap, vertical export, long renders | live |
| [[reference/td_library/TD_WORKFLOW_LIVE_VJ]] | /reference/td_library | Engine COMP scene architecture, APC40/Launchpad/LCXL wiring, Perform Mode, pre-gig checklist | live |
| [[reference/td_library/TD_WORKFLOW_LIVE_AUDIOREACTIVE]] | /reference/td_library | Link + TDAbleton + BlackHole, latency comp, per-song calibration | live |
| [[reference/td_library/TD_WORKFLOW_MIDI_OSC]] | /reference/td_library | MIDI In Map/OSC In/Out, controller wiring, phone apps, mapping patterns | live |
| [[reference/td_library/TD_WORKFLOW_AV_INTEGRATION]] | /reference/td_library | Syphon/NDI routing, Resolume handoff, multi-machine, FOH replacement roadmap, DMX/Art-Net | live |
| [[reference/td_library/TD_WORKFLOW_PROJECTION_MAPPING]] | /reference/td_library | kantan Mapper, CamSchnappr, keystone, edge blending, interactive mapping | live |
| [[reference/td_library/TD_WORKFLOW_INSTALLATION]] | /reference/td_library | Kiosk Mode, crashAutoSave, watchdog, sensor input, long-run reliability | live |

**Brand files above override the general library** — WOBAR_TD_AGENT_RULES and WOBAR_TD_REFERENCE are source of truth for brand constraints. Use td_library when the question is about TD itself, not WOBAR-specific conventions. Don't read the whole library — pull the one file the task needs via `TD_LIBRARY_INDEX`.

## Current State
**Growth strategy rebuilt 2026-07-26.** `working/WOBAR_GROWTH_PLAN.md` is the governing execution doc for the next 12 months (goal: people listening, online). SoundCloud is the priority surface; Instagram is demoted to a credibility surface. Seven label doors verified open. **`reference/WOBAR_SONIC.md` comps are wrong and need a pass** — Of The Trees / Shlump / INZO describe only the final 22 minutes of Nick's set; the center of mass is dark/wonky 140 + rap flips. `WOBAR_CONTENT.md`'s social strategy is superseded by the growth plan. Mirror Threshold + Terminal Rebuild PARKED.

Brand 6.0 locked March 2026. All files reflect current version.
TWOZERO MCP integration added April 2026. TD agent rules established.
Move history system added April 2026. Three slash commands: /td-build, /td-undo, /td-save.
TD doc library expanded April 2026: MCP catalog, debug log, expression cookbook, GLSL patterns, reference networks, TD index all added.
TD general library added April 2026: `reference/td_library/` — 27 files covering all operator families, patterns, workflows (brand-agnostic, scoped to 2025.32460 Non-Commercial on M1).
Skills source of truth added April 2026: `skills/` — git-tracked WOBAR Claude skills. `~/.claude/skills/` on each machine is a synced copy.
WOBAR_PROJECT_INSTRUCTIONS.md is deprecated — CLAUDE.md is the authority.

## Notes
When a file status is in-flux, confirm current state with Nick before using as reference.
