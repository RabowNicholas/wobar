---
title: Wobar Context Index
version: 1.1 (+ the Drift Rule — form-vs-state, one-owner-per-fact 2026-07-27)
last_updated: 2026-07-27
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
| **`working/` — live** | **State and plans.** Anything with a number that moves: rates, calendars, counts, door statuses, what's in flight, current targets. | GROWTH_PLAN · ACTIVE · PLACEMENT_PLAN · RESEARCH_* |

**A locked doc must never contain a number that will be wrong in three months.** No cadences, no catalogues, no follower counts, no current-target lists. If it changes, it lives in `working/` and the reference doc points at it.

### 2. One owner per fact

Every mutable fact has **exactly one owning file**. Every other mention is a `[[link]]` to the owner, never a copy.

| Fact | Owner |
|---|---|
| Output rate / release cadence | [[working/WOBAR_GROWTH_PLAN]] §1 |
| Label targets, door status, tiering | [[working/RESEARCH_LABEL_LANDSCAPE]] §2 |
| Position metrics (listeners, followers, submissions sent) | [[working/WOBAR_GROWTH_PLAN]] |
| Open loops, current work, session history | [[working/WOBAR_ACTIVE]] |
| Reference artists / comps, by register | [[reference/WOBAR_SONIC]] — the six-register table |
| Bio copy (EPK + world-facing) | [[reference/WOBAR_COPY]] — BIO TEMPLATES |
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
| [[working/WOBAR_ACTIVE]] | /working | Open project loops, current context, session history | live |
| [[working/WOBAR_CLOSED]] | /working | Completed project loops, archived from WOBAR_ACTIVE | live |
| [[working/WOBAR_GROWTH_PLAN]] | /working | **GOVERNING — read before any growth/content/platform decision.** 12-month goal (people listening, online): SoundCloud-first, flips as a numbered main-account series, originals to a 2-track reserve on day-60 calendar release, DJ promo, IG demoted to a 5-second credibility surface. Every claim confidence-tagged. **Owner of: output rate (§1) and position metrics.** §4 label doors rebuilt 2026-07-27 from browser-verified data — the old 7-door list was psy-lane. Supersedes the social strategy in WOBAR_CONTENT | live (v1.1) |
| [[working/RESEARCH_VERIFICATION_MEMO]] | /working | **Read before trusting any 2026-07-26 research file.** 13-agent adversarial verification — 9 of 10 claims UNSUPPORTED, two sub-reports contained fabricated data. What survived, what didn't, and what nobody has measured | live |
| [[working/RESEARCH_LABEL_LANDSCAPE]] | /working | **GOVERNING for label targeting.** Tiered door list for the dark/wonky 140 lane, verified 2026-07-27 by direct browser load. Two screens do the work: **founder share of Top 10** (kills release vehicles) and **set overlap** (Nick's own set vs each label's top sellers). Deadbeats' free 4-field Google Form is the headline. **§2.5 = the Beatport visibility sweep** (sales vs editorial are two different systems; best-fit doors have near-zero visibility). **§2.6 = the artist-discography sweep — 22 new labels and the VA compilation economy: ten recurring multi-artist series, most 20+ artists per volume, all live. A 29-slot compilation vs a one-slot signing is the biggest strategic find in the file.** Supersedes the door/tier tables in RESEARCH_LABEL_MAP and the label section of WOBAR_GROWTH_PLAN | live (v4.0 — unreviewed) |
| [[working/RESEARCH_LABEL_MAP]] | /working | Where the artists in Wobar's set actually release. Three lanes (US wonky-140/flip · psy-bass · deep dubstep), label→artist map, Beatport chart read, adjacent-artist list. **Door status superseded by RESEARCH_LABEL_LANDSCAPE** | live (partly superseded) |
| [[working/RESEARCH_SOUNDCLOUD_COMPS]] | /working | Cross-platform comp table (SoundCloud vs IG vs Spotify listeners) for 14 lane artists. Carries corrections — see header | live |
| [[working/RESEARCH_IG_COMPS]] | /working | Instagram comp sweep v2, neutral-frame sampled from label rosters. v1's cohort was convenience-sampled; two findings retracted | live (v2.0) |
| [[working/RESEARCH_IG_CONVERSION]] | /working | Does IG convert? Study A (IG vs Spotify listeners) + Study B (do labels gate on audience). Study B survives; Study A downgraded — see header | live |
| [[working/RESEARCH_IG_MECHANICS]] | /working | IG platform mechanics 2026 — ranking signals, Trial Reels, Meta Series, source-tiered claims table | live |
| [[working/IG_COMP_SAMPLE_FRAME]] | /working | The sampling frame + handle-resolution method behind the comp sweeps. Documents the convenience-sampling failure and the fix | live |
| [[working/WOBAR_PLACEMENT_PLAN]] | /working | Get-heard strategy — the **lever map** (curators · promoters/scene · labels · DJ promo), promo-service verdicts, DIY ads playbook. **Its Target Label Roadmap is superseded** (psy-lane; Deadbeats' DROPPED verdict reversed) → use RESEARCH_LABEL_LANDSCAPE. The Denver convergence thesis is void — SubCarbon is Belgian, Memory Palace is closed; that loop is parked | live (v1.3 — partly superseded) |
| [[working/MIRROR_THRESHOLD_SPEC]] | /working | Mirror Threshold build spec — the SMS door into the Ether; Twilio + Next.js/Neon/Vercel integration, state machine, compliance | live |
| [[working/WEB_HOME_SPEC]] | /working | The web home = a terminal you wander (early-RPG), guided by *the daemon*; full rebuild of wobar-landing-page; paths, offerings, AI rails | live |
| [[working/WOBAR_VISUAL_RESET]] | /working | **The visualizer design system — READ BEFORE ANY VISUALIZER BUILD.** Audits the old visual system vs world v0.6, then supplies the spine: the corridor is the *artifact* of perception failing to render a higher dimension (not the territory) — from which non-arrival, the drop-as-failure, and the stable-then-collapse arc all follow. §3 = the spec. Governs all visualizer work; supersedes the per-act material affinities in TD_REFERENCE §3/§4 | live (v0.2 — spine locked) |
| [[prototypes/corridor/README]] | /prototypes/corridor | **Look-dev sketches — prototype HERE, port to `glslTOP` after.** Holds the Nick-approved collapse mechanic (4× same corridor, superposed, no SDF booleans, weights equalizing) + the convergence-point find + 5 recorded dead ends so they aren't re-derived. Companion build-side to VISUAL_RESET §3 | live |
| [[reference/WOBAR_BRAND]] | /reference | Foundation, mission, archetypes, beliefs, positioning | locked |
| [[reference/WOBAR_WORLD]] | /reference | World mechanics — ground truth, geography, 3-version cycle, two-axis entity/the source, sacred, lexicon (Mirror/seeing/Wanderer/the Ether/glimpses/the Passage/the mark/the daemon), the Ether content model + void poems, Surfaces of the World §7.5 | live (v0.6 draft) |
| [[reference/WOBAR_FRAMEWORK]] | /reference | 5-Act Portal Framework, act definitions, percentages | locked |
| [[reference/WOBAR_GRAMMAR]] | /reference | **The cross-modal grammar — the shared root beneath visual, copy, sound.** Law 0 (ground it, let depth emerge, never reach) + the six-law × three-surface table + the mirror principle + the utility-floor + the §8 register-gate. VISUAL_RESET/COPY/SONIC all derive from it. Read to keep the three surfaces one world | live (v1.0 — governing) |
| [[reference/WOBAR_COPY]] | /reference | **v2.0** — the mirror spine, the 4-register voice stack (light/daemon/journal/source), the act axis, the utility floor, reconciled lexicon, register-scoped anti-vocab, the 4 tests, the daemon deflection bank, EPK+world-facing bios. Derives from GRAMMAR | live (v2.0 — governing) |
| [[reference/WOBAR_SONIC]] | /reference | Sonic identity, reference artists, genre positioning; re-parented to GRAMMAR (v1.2) | locked |
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
