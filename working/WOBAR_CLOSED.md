---
title: Wobar Closed Loops
version: 1.0
last_updated: 2026-05-05
status: live
scope: Completed project loops archived from WOBAR_ACTIVE. Reference only — no action required.
dependencies: [[WOBAR_CONTEXT]]
---

# WOBAR CLOSED LOOPS

Loops moved here from [[working/WOBAR_ACTIVE]] at session close-out. Most recent first.

---

## Eyes Cut Deeper — 4-cell grid music video + album cover

**Closed:** 2026-05-05 — shipped. Full-song video rendered, album snapshot saved.

**Context:**
4-cell macro-eye grid composite for the Subtronics "Eyes Cut Deeper" remix (Act 4/5 cusp register). Built after the iris-portal approach for the same song was abandoned (couldn't solve blink masking). The grid sidesteps that problem entirely — each of 4 macro-eye source videos gets a distinct effect treatment + WOBAR palette grade, composited into a 2×2 layout. Network: `touchdesigner/networks/eyes_cut_deeper/eyes_cut_deeper.8.toe`.

**Per-cell architecture:**
- **TL — Kaleidoscope mandala** (4-fold radial: bilateral × rotations 0/90/180/270, max-blended). Driven by broadband `energy`. Fold-in scales with energy via `outhigh` on each mirror layer (RGB-fade for max-blend chains, not alpha). Wobble displacement INVERSE to energy — moves at breaks, locks into perfect mirror at drops.
- **TR — Chromatic aberration + animated TV static**. Static CA (R-shift left, B-shift right, fixed amplitude). TV static via `randomgpu` noise (recentered ±range via offset for ADD blend). Driven by `transient` — punches on drops only.
- **BL — Zoom-tunnel feedback** (recursive eye-into-eye). Bronze/amber palette via `bl_keys` lookup. Driven by `sub_pressure`.
- **BR — Calm/oily ripple** displacement. Sage/moss/patina palette via `br_keys` lookup. Driven by `growl`.

**Audio pipeline:** Mid-session swap from custom rebuilt base_audio to canonical `base_audio_v001.tox` (8 channels with band_max normalization). Per-band gains exposed on `ctrl_master.Audio` for cell-specific tuning.

**Final polish:** simplex2d film grain (24 fps scintillation) + radial vignette unifying disparate cell palettes.

**Resolution:**
Music video full-song render shipped to `touchdesigner/renders/eyes_cut_deeper_grid.mov`. Album snapshot TIFF saved to `touchdesigner/album_snapshots/album_snapshot_20260504_231620.tif`. Album cover at NC-license-capped 720×720 will need external upscale (Topaz Gigapixel / Photoshop Preserve Details) for industry-standard 3000×3000 final.

**Metaphor framing (Three Versions + Meeting Point):**
- TL mandala = The Future Version (already knows the structure)
- TR CA/static = The Wounded Version (signal through interference)
- BL zoom-tunnel = The Present Version / The Portal itself (going inward)
- BR sage ripple = The Shadow / Dissolution (bass-as-mirror, somatic dissolution)

**Durable learnings (logged to TD_BUILD_LOG correction tracker):**
6 new TD gotchas — randomgpu output centered at 0.5 (not 0); mathCHOP chanop vs chopop semantics; levelTOP outhigh vs opacity for max-blend fades; feedbackTOP cook-loop warning is real (wire upstream content to input[0]); transformTOP needs two-stage pre-crop for aspect-fill into square output; selectCHOP par.channames takes name patterns not index syntax. The per-band reactivity pattern (TL=energy, TR=transient, BL=sub_pressure, BR=growl) became the canonical "polyrhythmic grid" approach — different cells breathing on different beats rather than single broadband Energy driving everything.

---

## Iris portal — Subtronics "Eyes Cut Deeper" remix (Act 4/5 cusp)

**Closed:** 2026-05-05 — closed unfinished. Approach didn't land.

**Context:**
Built from a "TD Drop #05 Eyes" YouTube tutorial base. Twisted-torus geometry where the inner cylinder doubles as the tunnel-through-pupil — clever single-geo "iris becomes tunnel" mechanic. 13 moves on the stack. Network at `touchdesigner/networks/iris/`.

Composition arc landed: monochrome-purple stylized iris with limbal/stroma/ruff/amber-fleck/slate/bone-ash palette, dominant scale, cool-violet light tint, dilated black pupil mask (`Puprad` exposed), halo pulse breath, feedback boundary mask containing trails inside iris circle, `ctrl_master` baseCOMP with `Puprad` / `Irisx` / `Irisy` / `Irisscale` exposed.

Built a parallel iris-over-video branch attempting to replace the natural iris in a macro-eye blinking video with the WOBAR iris (`xform_iris_replace` + `mask_iris_video` + `comp_video_replace` → `null_video_replace_out`).

**Failed experiments (reverted in-place):** warm halo color tint (added defined ring artifact competing with iris), catchlight in pupil (premultrgbbyalpha gotcha hid it; once visible, position kept overlapping inner-cylinder glint), wet PBR (light dimmer at 5.5 blew any glossy surface to plastic-mirror — would need full lighting rebalance), limbal ring overlay (merged with natural alpha falloff, barely visible).

**Critical blocker — chromakey blink masking failed.** Tried to use the natural iris's blue/teal hue as a key to drive iris-vs-lid detection. HSV analysis showed the iris's hue overlaps with sclera AND lid skin in this footage (sclera at hue 0.53 sat 0.48 val 0.36; iris at hue 0.52 sat 0.42-0.74; lid skin at hue 0.40). Color alone can't separate iris from "lid covering iris." Tried wider hue range, value-based fallback, and `invert` toggle — none cleanly handled the blink case. Reverted.

**Resolution:**
Closed unfinished. The original goal — natural-eye video with WOBAR iris properly masking-out during blinks — was not achieved. Recommended-but-not-attempted next paths were manual keyframing of a blink-alpha param across the 121 frames OR external rotoscope import. Nick chose neither — pivoted to a different visual approach for the same song (the 4-cell macro-eye grid composition at `touchdesigner/networks/eyes_cut_deeper/`).

**What this loop produced (still useful):**
- Standalone iris network is visually strong as a stylized purple iris with dramatic dilated pupil and breathing halo. Could be reused in a different context.
- 7 substantial TD gotchas surfaced (compositeTOP swaporder convention, circleTOP centerunit-as-offset, circleTOP radiusunit anisotropy, circleTOP premultrgbbyalpha invisibility, math.sin in expressions, backface culling on twisted geo, wet-PBR-needs-light-rebalance) — all logged to `TD_BUILD_LOG.md` correction tracker. The session's biggest deliverable was the gotcha catalog.
- Established that for video iris replacement, color-based keying is fragile for human eyes. Future iris-replacement attempts should reach for rotoscope tools (external) or per-frame manual keyframing rather than chromatic detection.

**Why it didn't work how Nick wanted:**
The "alien iris in a real eye" register required clean blink masking that color keying couldn't deliver on this footage. Without it, the WOBAR iris always appeared painted over the closed eyelid — which broke the realism the concept depended on. The 4-cell grid approach (Eyes Cut Deeper loop) sidestepped this entirely by using the original eye videos as-is and treating each cell with a distinct effect, achieving the multiplicity-of-mirror reading without needing iris replacement.

---

## First POPX-on-WOBAR Build

**Closed:** 2026-05-01

**Built under the new (post-2026-04-30) visual identity** — full desaturated psychedelic palette, mirrors-over-portals lens, metallic surfaces permitted, no per-act constraint table.

**Context:**
First polished POPX-on-WOBAR proof. POPX SA-Aizawa point cloud → black pearl PBR sphere instances → mirror-symmetric composite → atmospheric post → recorder. Network at `/project1` (not wrapped in a baseCOMP — Nick rebuilt directly into project1 after v001 abandoned). 22-parameter `ctrl_master` baseCOMP exposes high-leverage knobs across 6 pages (Audio, Material, Lighting, Camera, Composition, Form). Audio reactivity intentionally limited to a single binding: `sa1.Timescale = floor + ceil*max(0,energy)^exp` — every other potential binding (sub-flash, mid-morph, energy-bloom) deferred per Nick's directive.

**Resolution:**
Two register tunings landed during session — hard chaotic mushroom trip (toxic palette / fast breath / sharp curves) and dark hypnotic crimson (red-only palette / slow breath / contemplative camera). Final state: dark hypnotic crimson with pink killed. The control panel makes track-by-track retuning fast — change `ctrl_master` knobs, the look follows. **Validated the POPX guide produces real value** — strange-attractors-from-the-guide pattern landed clean once correct gotchas were navigated (Pointsupdatepop feedback loop, custom attribute stripping through advect, geometryCOMP instance-scale-bare-attribute-only, etc.). Move file `touchdesigner/networks/attractor_chamber/moves/move_002.json` is the full operational record. `CHANGE_LOG.md` summarizes the architecture. Six new TD gotchas logged to `TD_BUILD_LOG.md` correction tracker. Network ready for live use across multiple tracks via the dashboard.

---

## Act 1 Visual — Glass Orb + Motes

**Closed:** 2026-04-30
**Built under the old visual identity (pre-2026-04-30 palette/rules).** Closed at session-end to clear the slate post-identity-refresh. Resume only if re-prioritized against the new palette/lens.

**Context:**
Major build session inside `/project1/base_glass_orb/base_motes`. 3-body N-body gravitational mote system rendered through the existing glass orb refraction shader. Physics: Velocity Verlet integration with hard cage at escape_r=0.25, spread thermostat (cluster bounding radius ≥ 0.10), periodic kicks every 6s, Fibonacci-sphere seeding with body-varying reference axis. Visuals: 3 distinct warm-Act-1 colors (gold/magenta/purple), per-body breath pulse, screen-blended 3-stage Gaussian bloom for "ball of light" feel, depth dimming for volumetric front/back distinction, perspective camera with parallax + ty offset to align with orb center. Audio reactivity: sub_bass → core brightness, energy² → gravity. Specular removed from orb shader, film grain layer added.

**Resolution:**
Visual was working but still being dialed for calm-vs-collapse balance when POPX exploration pulled focus. Spread thermostat was the latest anti-collapse fix; not verified across multiple-minute runs. **Many new TD patterns logged to `working/TD_BUILD_LOG.md` (2026-04-27 entry) and the correction tracker** — including the geometryCOMP auto-torus footgun, compositeTOP 2-input limit, `me.storage` scope inside scriptCHOP onCook callbacks, scriptCHOP per-frame cook requires time-dependent input, `pow()` with negative-noise floats → complex TypeError, Fibonacci pole zero-velocity bug, and velocity-vs-spread thermostat distinction. Move files 005-013 in `touchdesigner/networks/glass_orb/moves/`. Network preserved — re-openable if revisited.

---

## Act 1 Visual — base_act1_underwater

**Closed:** 2026-04-30
**Built under the old visual identity.** Closed at session-end without final sign-off + render. Re-evaluate against new palette before render commit.

**Context:**
Built from scratch at `/project1/base_act1_underwater`. 1800-particle cloud (Script CHOP static positions, AUTOMATIC cook), 3-light ambient rig, GLSL caustic shader (6-wave interference + surface light shafts), shallow-reef teal color ramp, bloom, chromatic aberration, soft circle crop. Camera drifts forward via `me.time.seconds * -0.07`. Settled on radius 0.008 for fine-sediment scale.

**Resolution:**
Visual built and pending Nick sign-off. Render workflow defined (12,660 frames at 60fps = 211s, audio_in + movie_out wired) but not executed. Key technical learnings preserved in TD_BUILD_LOG.md (2026-04-21 entry): Script CHOP callback edit path (text.replace, never overwrite full DAT), `me.time.seconds` for camera drift instead of `absTime.seconds`, poptoCHOP not viable at 1800pts/60fps, camera-through-cloud creates the apparent drift effect.

---

## Ferrofluid Sphere Visual

**Closed:** 2026-04-30
**Built under the old visual identity.** Visual was signed off — closed without final render commit.

**Context:**
GPU POP ferrofluid sphere (translatealongnormal radial spikes), black PBR oil surface (metallic=0.95, roughness=0.02), 3-light iridescent rig (120° hue offset sin waves), HDRI-lit gray backdrop plane (geo_bg at tz=-5), centered bioluminescent glow ring (light3 at tz=-2, pulsing ~0.8Hz). Feedback trail + bloom.

**Resolution:**
Visual signed off. movie_out wired at `/Users/nicholasrabow/Desktop/td_exports/mur_ferrofluid.mov` (MJPEG video-only — AAC blocked on NC license). Render workflow defined (12,660 frames at 60fps, Realtime OFF, hit Record on movie_out, MP3 mux post-render) but not executed. Closed at session-end as a clean-slate decision; can be re-rendered any time using the existing wiring.

---

## Act 2 Visual — Tunnel Export

**Closed:** 2026-04-30
**Built under the old visual identity.** Visual was signed off — closed without final full-song export.

**Context:**
Concentric square tunnel from `/project1/tunnel` (the original main tunnel build, signed off back in April). Loop was kept open specifically to convert mur v1.mp3 to WAV, set audio_in playmode=locked, and render the full-song movie out. Never executed.

**Resolution:**
Closed at session-end. Render workflow remains valid if Nick chooses to re-open: WAV conversion → audio_in → timeline end frame matching WAV duration → Movie File Out with Realtime OFF.

---

## Act 3 Visual — base_pop_sphere

**Closed:** 2026-04-30
**Built under the old visual identity.** Visual was signed off — closed without final render commit.

**Context:**
Particle sphere with per-sphere green/amber/red color cycling (energy-driven speed — imperceptible at breakdown, chaotic at drop), radial audio waveform ring (abs displacement, amplitude-colored), ghost aura ring, feedback spiral trail, camera presets + auto-cycling. movie_out wired and ready. Multiple versions saved during session.

**Resolution:**
Visual signed off. Render workflow defined (12,670 frames for mur.wav at 60fps, audio_in playmode=locked, Realtime OFF, watch for MJPEG codec block on free license — fallback to OBS if needed) but not executed. Closed at session-end. Re-evaluate against new palette before render commit.

---

## Format Testing — The Cut (Found Footage Hook)

**Closed:** 2026-04-30
**Closed at session-end as part of clean-slate cleanup. Re-open later if format testing becomes priority again.**

**Context:**
Format defined and written to `working/FORMAT_TESTING.md`. Three hook categories confirmed: skateboarding (street), nature "what is going on" (disasters, extreme weather, bizarre phenomena), extreme commitment sports (cliff jumping, skydiving, snowboarding). Satisfying process content and flow arts killed (process pulls away from the music; flow arts too on the nose). Optical illusions killed (insufficient contrast with visualizer).

**Resolution:**
Format spec preserved in `working/FORMAT_TESTING.md`. No footage sourced or tested. Re-open if/when format-testing returns to the active queue.

---

## Format Testing — Stacked Horizontal ("You Are Here")

**Closed:** 2026-04-30
**Closed at session-end as part of clean-slate cleanup.**

**Context:**
Format defined. Three horizontal strips stacked vertically for TikTok/Reels — three perspectives of the same moment. Especially strong for outdoor sets (drone/wide angle + close angles). Pure proof-of-experience format.

**Resolution:**
Format spec preserved in `working/FORMAT_TESTING.md`. No template built or footage tested. Re-open if needed.

---

## Format Testing — The Transmission (Journaling)

**Closed:** 2026-04-30
**Closed at session-end as part of clean-slate cleanup. Posting cadence becomes the validator.**

**Context:**
Journal timelapse visual + talking-to-camera VO. Defined in `working/FORMAT_TESTING.md`. Validation strategy was "keep posting, evaluate after 5+ posts against baseline."

**Resolution:**
Format spec preserved. Treat as live posting practice rather than an active loop — re-open only if a deliberate evaluation pass is scheduled.

---

## Carousel Format Definition

**Closed:** 2026-04-30
**Closed at session-end as part of clean-slate cleanup. Was a research loop with no advancement.**

**Context:**
Opened as research loop. Pipeline noted: SVG from Claude → Canva for post-processing. Goal was to research carousel formats currently driving saves and define a brand-aligned format spec. Framework-as-trojan-horse principle (felt not taught) was the brand fit criterion.

**Resolution:**
No research executed, no format spec defined. Closed without progress. Re-open if carousels become a deliberate content priority.

---

## base_act2_particles — POP Tunnel Build (Learning Session)

**Closed:** 2026-04-17
**Network deleted.** Learning session only — not a keeper.

**What was built:** Act 2 torus-of-spheres tunnel. 720-point torus, dual concentric ring sets scrolling opposite directions, camera inside tunnel, feedback spiral, purple brand palette restored after drift. Multiple creative directions tried and reverted (chrome abrasion, rainbow, psychedelic batch).

**Why closed:** Execution quality was high but undirected creative output was generic. Nick's call: not worth keeping, learnings captured in TD_BUILD_LOG.md and memory.

**Key technical learnings promoted to build log:**
- Script CHOP bridge is the only working instancing path — `instancepop`/`instanceop` broken for position-based instancing in TD 2025
- feedbackTOP: seed input + par.top only, no direct wire to target
- MAT expressions inside child COMPs need absolute `op()` paths
- `math.sin()` not `sin()` in TD parameter expressions
- Phase-distributed ring scrolling (0..1 per ring) eliminates modulo jerk

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
