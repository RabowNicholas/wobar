---
title: Wobar Active Loops
version: 1.0
last_updated: 2026-05-06
last_session: 2026-05-06
status: live
scope: All open project loops. Read this alongside WOBAR_CONTEXT at the start of any working session. Updated by Claude at the end of each session.
dependencies: [[WOBAR_CONTEXT]]
---

# WOBAR ACTIVE LOOPS

Living document. Not locked. Updated at the end of every working session.
When a loop closes, it moves to [[working/WOBAR_CLOSED]].


LOOP: Release Schedule
STATUS: in progress
LAST: v2 release packet built at /working/RELEASE_PACKET.xlsx. Mirror-only structure. 7 required assets per release: 4 short clips 30–60s + 1 hook clip 15s + 1 single artwork + 1 track upload. Each visualizer used 2× (TK + IG) = 10 visualizer posts across the 14-day release window. BTS lives as trigger-based companion (Mirror clip clears 1.5× baseline → 1 BTS clip from TD network with song playing, posted 24–48h after, cap 3 trigger posts per release). T-counter dates auto-calculate from B6 Release Date — duplicate the tab, change one date, schedule shifts. 16 releases scheduled biweekly Fridays 5/29 → 12/25 (SCHEDULE tab). MUR locked as #01. TD output target: 3/week floor = 96 visualizers produced over 32 weeks vs 80 needed = 16 surplus for slips, BTS triggers, orbit content. v1 packet (uploads/wobar_release_packet.xlsx) deprecated — 200-piece scope was the bottleneck that stalled MUR.
NEXT: MUR T-21 is Friday 2026-05-08. Distributor upload + Spotify for Artists pitch + pre-save page (Hypeddit) by 5/8 or MUR slides to 6/12 and year-end count drops to 15. Daily job becomes building the per-release packet. Release windows overlap by 7 days (current at T+7 while next at T-7) — system designed for that overlap.


LOOP: Walls Are Thin Review
STATUS: in progress
LAST: Walls Are Thin decoupled from release packet during 5/6 release-schedule session. The bucket was a 4-asset-per-release tax that wasn't earning its place — Phase 1 capture was inconsistent and the locked formats (talking to camera, voice memo, journal, quote carousel) didn't ring true. v2 release packet is Mirror-only. BTS becomes the Mirror trigger response (handles "process visible" without forcing performance). Walls bucket removed from WOBAR_CONTENT.md entirely in v2.0 rewrite (5/6) — bucket is now homeless: not in brand docs, not in release production. Option (a)/(b)/(c) decision still pending. The existing Format Testing — The Transmission loop is testing a Walls-bucket format and its output feeds this review.
NEXT: Define what Walls Are Thin is when it's not tied to releases. Three options on the table: (a) standalone series with its own cadence, (b) folded entirely into the BTS-trigger pattern (which would retire the bucket), (c) quiet retirement. Decision waits for: Transmission test data accumulating + first few BTS triggers actually firing on Mirror clips that clear baseline. Until then, packet ships Mirror-only.


LOOP: Act 2 Visual — tunnel export
STATUS: in progress
LAST: Visual signed off. Loop closed. Pending full-song export.
NEXT: Convert mur v1.mp3 to WAV → set audio_in file + playmode=locked → set timeline end frame to match WAV duration → Movie File Out → render with Realtime OFF.


---

LOOP: Format Testing — The Cut (Found Footage Hook)
STATUS: in progress
LAST: Format defined and written to working/FORMAT_TESTING.md. Three hook categories confirmed: skateboarding (street), nature "what is going on" (disasters, extreme weather, bizarre phenomena), extreme commitment sports (cliff jumping, skydiving, snowboarding). Satisfying process content and flow arts killed — process pulls away from the music, flow arts too on the nose. Optical illusions killed — not enough contrast with visualizer.
NEXT: Source reuse-safe footage across the three categories. Test first version against an upcoming release.

LOOP: Format Testing — Stacked Horizontal ("You Are Here")
STATUS: in progress
LAST: Format defined. Three horizontal strips stacked vertically for TikTok/Reels. Three perspectives of the same moment. Especially strong for outdoor sets — drone/wide angle + close angles. Pure proof-of-experience format.
NEXT: Test with existing set footage. Build template.

LOOP: Format Testing — The Transmission (Journaling)
STATUS: in progress
LAST: Continuing to test as defined (journal timelapse visual + talking to camera VO). No changes. Needs reps.
NEXT: Keep posting. Evaluate after 5+ posts against baseline.

LOOP: Carousel Format Definition
STATUS: waiting
LAST: Opened as research loop. Current pipeline: SVG from Claude → Canva for post-processing. Need to research what carousel formats are driving saves right now and match one to brand. Framework as trojan horse — felt not taught.
NEXT: Research carousel best practices, define format spec, test.

---

## Session Log

| Date | Summary |
|------|---------|
| 2026-05-06 | WOBAR_CONTENT.md v2.0 rewrite. Cut Walls Are Thin bucket, format system (Mirror/Room/Transmission), posting system, baseline monitoring, 10-asset gate. New shape: release content only. Original Track package = full track + 1 visualizer per in-song drop + reactive BTS (gut call — could be Nick likes it, could be over-baseline performance, his decision). Series content lives in working docs until promoted. Walls Are Thin no longer in brand docs. Drift to reconcile: Release Schedule loop locks BTS trigger at 1.5× baseline; brand doc loosens to gut call. |
| 2026-05-06 | Release schedule loop opened. Reviewed v1 release packet (uploads/wobar_release_packet.xlsx), diagnosed 200-piece-per-release scope as the bottleneck that stalled MUR (track done since 4/3, system blocked execution). Built v2 packet at /working/RELEASE_PACKET.xlsx — 4 tabs (SCHEDULE, TEMPLATE, MUR, ARCHIVE INDEX). Mirror-only, 7 required assets (5 visualizers + artwork + track), T-counter formulas off Release Date so duplicating the tab shifts the schedule. Biweekly cadence locked: 16 releases through 12/31 (5/29 → 12/25 Fridays). MUR pre-filled as #01. BTS decoupled from required content, now lives as trigger-based companion to Mirror via 1.5× baseline rule (TD network screen capture with song playing, no voiceover). Walls Are Thin decoupled from release packet entirely — opened as separate review loop. TD output target locked at 3/week floor = 96 visualizers produced vs 80 needed = 16 surplus by year-end. MUR T-21 deadline is 2026-05-08. |
| 2026-04-16 | TD general knowledge library built. New brand-agnostic `reference/td_library/` subfolder with 27 files: LIBRARY_INDEX, APPLE_SILICON, NETWORK_VS_GLSL, EFFICIENT_NETWORKS, FOOTGUNS, full operator catalogs (POP/TOP/CHOP/SOP/MAT/DAT/COMP — "every single operator"), pattern library (AUDIO_REACTIVITY, FEEDBACK, GENERATIVE, 3D_SCENES, INSTANCING, COMPOSITING, PARTICLES, TEXT), workflow playbooks (OPTIMIZATION, EXPORT, LIVE_VJ, LIVE_AUDIOREACTIVE, MIDI_OSC, AV_INTEGRATION, PROJECTION_MAPPING, INSTALLATION). Scoped to 2025.32460 Non-Commercial on M1. Explicit POP-first, network-over-GLSL bias per Nick's stated gap. WOBAR_TD_INDEX.md updated with cross-reference. Brand files untouched. |
| 2026-04-16 | base_act2_underwater audio tuning + kick response session. Analyzed rec_audio waveform (16400 samples) — sub_bass peaks 0.81, energy 0.87, growl clipping at 1.02. Fixed: growl_max raised 0.16→0.22, power curves dropped (1.8/2.5 → linear) for Act 1/5 gentle content. Added kick-driven blur (blur_shimmer 0→16px), kick glow burst composite (blur_kick+lvc_kick+comp_kick Add layer). Fixed portal drift — anchored triangle formation, was bottom-left. Added movie_out for recording. Moves 037–043.
| 2026-04-15 | act2_fractal refinement session. Kaleidoscope tunnel: added domain warp (double fbm), global clockwise rotation, color cycling (3 independent oscillators, purple family only), breathing scale, chaos power curve 3.0, sub_pressure power 2.5 for smooth breakdowns. Tried + rejected: mirror cascade, orange palette, full-spectrum psychedelic colors. rec_out wired (h264nvgpu, audio_in at 44100). No checkpoint yet.
| 2026-04-15 | Posting quality research — four-phase investigation into IG/TikTok compression + TD export limitations. Phase 1 platform specs mapped (4:2:0 forced, 15–25 Mbps IG / 10–12 TikTok, desktop web beats mobile on both). Phase 2 pipeline comparison (A retired, C image-sequence→FFmpeg as default on Free license, B reserved for future license upgrade). Phase 3 locked recipe into WOBAR_TD_REFERENCE.md Section 8 — per-platform tables, cross-platform safe zone (center 980×1230), FFmpeg command with Rec.709 + `-tune grain`, upload protocol, quality mitigations. Phase 4 benchmark protocol designed (5-section torture clip) but deferred — battle-testing through live posting instead. Research loop closed. |
| 2026-04-14 | Tunnel audio reactivity session. Built base_audio from scratch (4-band audiofilterCHOP pipeline, energy envelope, kick branch). Built ctrl_audio_live pre-compute CHOP layer in tunnel. Wired all visual parameters to energy: zoom, rotation, opacity, contrast, glow, CA, displace. Intensity parameter on ctrl_master is manual energy ceiling. Explored kick mapping (zoom snap, shockwave, contrast flash — all removed, none felt right). Color cycling via ramp phase tried and removed. Energy-driven Intensity is the keeper — breakdown goes near-still, drop comes alive. |
| 2026-04-12 | Act 2 TD build session continued. Evolved 3-arm spiral from purple to underwater aesthetic. Shifted color to desaturated blue/teal (0.50–0.67 hue, sat 0.40 at shader, 0.75 HSV). Widened wave crest spacing (spacing 0.042→0.072). Added caustic layer (Voronoi edge detection GLSL, 3 animated scales, screen-blended — null_caustic_out). Added radial surface glow (ramp_surface screen-blended — null_surface_out). Brand reviewed: Act 2 DESCENSION alignment strong. Blue color approved as contextual departure. |
| 2026-04-10 | Content format review session. Reviewed existing buckets and format system. Defined three new test formats in working/FORMAT_TESTING.md: The Cut (found footage hook → visualizer at drop, three hook categories: skate/nature chaos/extreme sports), The Stack (three horizontal strips stacked vertical, "you are here" multi-angle), continued Transmission testing. Carousel format parked as research loop. Satisfying process, flow arts, optical illusions killed with reasoning. Formats stay in testing doc until performance data earns them a spot in WOBAR_CONTENT.md. |
| 2026-04-10 | Full loop review. All 8 open loops closed: Common Enemy remix, ASAP Rocky remix, Flow State residency, Thursday event concept, Origin Story series, FREQUENCY Lake Effect, platform bio rewrite, Organic Distortion visual system. Clean slate. |
| 2026-03-30 | Content strategy audit against FSC research. Identified gaps: no baseline monitoring, no format system. Built three wobar-specific formats: The Mirror, The Room, The Transmission. Validated against brand. Baseline monitoring to be added to posting system. |
| 2026-03-15 | FREQUENCY card design locked. Moo Luxe, black stock, soft-touch matte. Raised spot gloss on act names + hidden WOBAR wordmark over logo. White logo, brand purple act names, Futura PT Bold/Heavy. QR centered bottom. One side only. No visible wordmark — IYKYK. Color palette and typography added to WOBAR_BRAND.md from Art Direction Playbook. |
| 2026-03-12 | Common Enemy (Buffalo Farm) remix loop opened. Heavy track. Guitar riff written in C major — working on translation to G minor. Scale degree map and harmonic minor options discussed. Decision point: B as chromatic pull vs E as color note determines approach. |
| 2026-03-12 | Origin Story Content Series. 6-chapter arc built, filmed, captions written and approved. Chapter 2 cut. Chapter 6 folded into The Search. Format locked — video Reels on both TikTok and Instagram. Deployment starts Mar 11. |
| 2026-03-11 | Phone session. Platform bio rewrite loop opened. Character limits confirmed. No copy produced. |
| 2026-03-10 | Origin Story Content Series loop opened. 7-chapter story arc built. TikTok hooks locked. Instagram captions written and brand checked. Two-week deployment calendar mapped. Task list complete. Middle/bottom funnel layer deferred. |
| 2026-03-10 | FREQUENCY event planning session. Lake Effect venue confirmed. Full checklist built and checked against FSC brief and Wobar brand docs. Event agnostic business card concept locked (framework + logo + QR). Landing page scope defined. Content map drafted. Artist outreach — Nick has names, will reach out directly. |
| 2026-03-10 | Audit + systems session. Broken links fixed. WOBAR_CLOSED.md created. Folder structure finalized (root/working/reference). Obsidian Git plugin installed — replaces scheduled task. GitHub connector wired to Claude.ai Project. WOBAR_PROJECT_INSTRUCTIONS.md written. Phone workflow established. No project loops worked. |
| 2026-03-10 | Vault infrastructure session. Git initialized, pushed to GitHub (RabowNicholas/wobar). Daily auto-commit at 5am. WOBAR_ACTIVE, WOBAR_CLOSED created. Folder structure reorganized. No project loops worked. |
