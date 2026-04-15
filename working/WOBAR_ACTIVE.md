---
title: Wobar Active Loops
version: 1.0
last_updated: 2026-04-15
last_session: 2026-04-15
status: live
scope: All open project loops. Read this alongside WOBAR_CONTEXT at the start of any working session. Updated by Claude at the end of each session.
dependencies: [[WOBAR_CONTEXT]]
---

# WOBAR ACTIVE LOOPS

Living document. Not locked. Updated at the end of every working session.
When a loop closes, it moves to [[working/WOBAR_CLOSED]].

LOOP: Act 2 Visual — base_act2 underwater spiral
STATUS: in progress
LAST: Full parameterization built. 6 ctrl_ CHOPs expose all style constants and audio handles. base_audio (4-band analysis pipeline) and base_act2_map (Act 2 scaling layer) built as standalone Base COMPs. Audio wired to /Users/nicholasrabow/Downloads/20_1_14_26.mp3. ctrl_audio_live Select CHOP is the live swap point — all expressions updated to use it. All three networks laid out left-to-right. Canonical output: null_surface_out.
NEXT: BLOCKER — convert 20_1_14_26.mp3 to WAV before next build session. WOBAR_TD_REFERENCE.md mandates WAV for deterministic render sync (Locked to Timeline does not work correctly with MP3). After that: observe audio reactivity, dial in gain values in base_act2_map (math_zoom.par.gain, math_bright.par.gain etc). When satisfied, run /td-save to checkpoint and export .tox files.

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
