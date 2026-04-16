---
title: Wobar Closed Loops
version: 1.0
last_updated: 2026-04-10
status: live
scope: Completed project loops archived from WOBAR_ACTIVE. Reference only — no action required.
dependencies: [[WOBAR_CONTEXT]]
---

# WOBAR CLOSED LOOPS

Loops moved here from [[working/WOBAR_ACTIVE]] at session close-out. Most recent first.

---

## Act 1/5 Visual — base_act2_underwater Portal Web

**Closed:** 2026-04-16

**Context:**
Multi-session build on `/project1/base_act2_underwater`. Started as an underwater-looking-up refraction scene (sky + caustics + surface normal map). Evolved through: Snell's window sky (rejected), shimmer-only portal web (kept), sky and caustics removed, portals pushed as primary element. Final visual: 3-portal vortex web with ice-fire palette, dual-rate breath (7s/13s), global spin, kick-driven blur smear + glow burst composite layer. Audio tuned for Act 1/5 gentle sub content via rec_audio waveform analysis.

**Resolution:**
Visual complete. `movie_out` wired and ready to record. Output: `/Users/nicholasrabow/Desktop/wobar/renders/output.mov`. Tuning levers documented in WOBAR_ACTIVE (lvc_kick brightness1, blur_kick size). 43 moves logged in `touchdesigner/networks/act2_underwater_surface/moves/`.

---

## Act 2 Visual — act2_fractal Kaleidoscope Tunnel

**Closed:** 2026-04-15

**Context:**
Two-session build on `/project1/base_act2_fractal`. Started as a Mandelbulb raymarcher, pivoted to a 2D polar kaleidoscope tunnel. Explored domain warp, global rotation, color cycling, breathing scale, audio-reactive chaos, psychedelic color experiments.

**Resolution:**
Network deleted. Experiments and learnings fully preserved in TD_BUILD_LOG.md (2026-04-15 entry). Key takeaways promoted: power curves on audio inputs suppress breakdown noise better than Lag CHOP alone; HSV desat kills warm low-luminance palettes; three independent color oscillators at different rates create non-repeating variation within a constrained palette.

---

## Research — Posting Quality (Compression + TD Export)

**Closed:** 2026-04-15

**Context:**
Four-phase research into mitigating quality loss on visualizer posts to IG Reels and TikTok. Identified two load-bearing constraints: platform-enforced 4:2:0 chroma subsampling and Free-license TD export ceiling. Phase 1 mapped 2026 platform re-encode behavior for both platforms. Phase 2 compared three export pipelines (Free+HandBrake, Commercial h264nvgpu, image sequence+FFmpeg). Phase 3 locked the recipe into WOBAR_TD_REFERENCE.md Section 8. Phase 4 benchmark protocol designed but not yet executed — battle-testing deferred to live posting.

**Resolution:**
Section 8 of WOBAR_TD_REFERENCE.md replaced with per-platform tables (IG 15–25 Mbps / TikTok 10–12 Mbps), cross-platform safe zone (center 980×1230), three-pipeline decision matrix (Pipeline A retired, Pipeline C image-sequence→FFmpeg as new default on Free license), ready-to-run FFmpeg command with Rec.709 tagging and `-tune grain`, upload protocol (desktop web on both platforms), and five-item quality mitigations list. Research artifacts saved in working/: RESEARCH_POSTING_QUALITY, RESEARCH_PHASE1_PLATFORM_SPECS, RESEARCH_PHASE2_TD_EXPORT, RESEARCH_PHASE4_BENCHMARK. Grain-as-banding-protection hypothesis flagged for empirical validation during real posting cycles.

---

## Act 2 Visual — Tunnel (/project1/tunnel)

**Closed:** 2026-04-14

**Context:**
Concentric square tunnel built in `/project1/tunnel`. L-infinity distance GLSL shader (20 rings, exponential perspective spacing, brightness/linewidth gradient). Full feedback loop with fb_displace, noise_warp counter-rotation. Color pipeline: lvc → displace → lkp/ramp_purple → color_mult (thresh_mask) → glow_comp → chrom_ab → null_final. Muted psychedelic palette: blue/purple/teal dominant, orange accents, ramp cycles via absTime.

Full audio reactivity via `ctrl_audio_live` CHOP (pre-computed band×energy channels). `ctrl_master` Base COMP exposes all parameters including `Intensity` (manual energy ceiling). `base_audio` pipeline built as standalone component: mono_mix → 4 audiofilterCHOP branches → RMS → lag → merge, plus energy envelope (0.55 sub + 0.35 bass weighted sum, 2.5s release lag, normalized 0→1), plus kick branch.

**Resolution:** Visual dialed in and signed off. Energy-driven Intensity scales all motion parameters — breakdown goes near-still, drop comes alive. Kick mapped but not used (no target felt right). File saved by user. Needs WAV conversion + full export before final archive.

---

## Common Enemy (Buffalo Farm) Remix

**Closed:** 2026-04-10

**Context:**
Heavy track. Vocals only from original — building everything else around them. Guitar riff motif kernel: G-F#-A-Bb (translated from C major original). Key: G harmonic minor. F#→G chromatic pull is the spine of the motif. Emotional texture: grief that became anger.

**Resolution:** Closed during full loop review. Riff translation mapped, DAW test was next step.

---

## ASAP Rocky "Everyday" Remix

**Closed:** 2026-04-10

**Context:**
140 BPM, C# minor. Act 3/4 cusp. Structural container phase — map the full arc before touching the peak section.

**Resolution:** Closed during full loop review. No session work beyond initial open.

---

## Flow State Monthly Residency

**Closed:** 2026-04-10

**Context:**
Monthly residency at Flow State, SLC. Primary live Wobar set context. Recurring performance footage and community touchpoint.

**Resolution:** Closed during full loop review. Residency holding as of March 2026.

---

## Thursday Event Concept

**Closed:** 2026-04-10

**Context:**
Event concept tied to Thursday. Three clarifying questions were identified but never logged or answered.

**Resolution:** Closed during full loop review. Concept unresolved — never advanced past initial flag.

---

## Origin Story Content Series

**Closed:** 2026-04-10

**Context:**
5-chapter origin story arc for When The Walls Are Thin bucket. Final sequence: Container Problem → The Culture → Awareness Without Tools → The Alignment → The Search. All videos filmed raw. All TikTok and IG captions written. Format: video Reels on both platforms. Deployment window: Mar 11–23.

**Resolution:** Closed during full loop review. All content was written, reviewed, and approved. Deployment window passed.

---

## FREQUENCY — Lake Effect

**Closed:** 2026-04-10

**Context:**
FREQUENCY hosted by Wobar at Lake Effect, SLC. One guest artist (1 hr opener), Wobar closes (2 hrs, full 5-act arc). Community-first, free, no cover. Business card design locked: Moo Luxe, black stock, soft-touch matte, raised spot gloss on act names + hidden WOBAR wordmark. Landing page was the blocker for print.

**Resolution:** Closed during full loop review. Card design locked, landing page and remaining checklist items incomplete.

---

## Platform Bio Rewrite

**Closed:** 2026-04-10

**Context:**
Brand 6.0 bios across TikTok (80 chars), Instagram (150 chars), YouTube (1,000 chars), SoundCloud (1,000 chars). Limits confirmed, no copy written.

**Resolution:** Closed during full loop review. No copy produced.

---

## Organic Distortion Visual System

**Closed:** 2026-04-10

**Context:**
Transparent distortion layer built from organic structures (Voronoi, mycelium, reaction-diffusion) over real footage. Audio reactive, act-mapped. TouchDesigner pipeline.

**Resolution:** Closed during full loop review. Concept locked, no TD build started.

---

## Logo Animation

**Closed:** 2026-03-10

**Context:**
Counter-rotation animation. Pipeline: SVGator → DaVinci Resolve. SVGator handles animation export, DaVinci handles compositing and final output.

**Resolution:** Loop closed by Nick. Pipeline documented for future reference.

---
