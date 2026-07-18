---
title: TouchDesigner Build Log
version: 1.1
last_updated: 2026-07-17 (corridor Phase 0/1 build entry added)
status: live
scope: Session-by-session log of AI-assisted TD builds (recent sessions; older sessions in TD_BUILD_LOG_ARCHIVE.md). Used to identify recurring corrections and promote them to rules in WOBAR_TD_AGENT_RULES.md.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]]
---

# TD BUILD LOG

One entry per build session. Newest at top. This is the feedback loop — patterns that repeat here become rules.

---

## 2026-07-17 — corridor Phase 0 platform-verify + Phase 1 skeleton — all Metal-risk features GREEN; corridor bones up but soft

**Context:** first build of the new **Corridor Build** loop (POP-native lit-3D corridor, forked off the glslTOP-raymarching spine). Two sub-builds in an empty `NewProject` (build **2025.32820**, saved as `NewProject_v1.toe`): a throwaway platform-probe rig, then the corridor skeleton. Goal of Phase 0 = confirm which Metal render features actually work before investing.

**What was built:**
- **Probe rig `/project1/probe_shadow`** (lit test scene): `geometryCOMP` torus caster (kept default `torus1`) + `geo_floor` (default torus destroyed → `gridSOP` 16×16, `rx=-90` flat, render+display=True) + `phongMAT` (diffuse `diffr/diffg/diffb`=0.72) + **cone `lightCOMP`** (`tx4 ty8 tz5`, `lookat='geo_caster'`, `coneangle35`, `shadowtype='soft2d'`, `shadowcasters='geo_caster'`, `lightsize1 0.04`, `shadowresolution1 1024`, `fov50`) + `cameraCOMP` (`tx6 ty5 tz11`, `lookat` caster) + `renderTOP` (`geometry='geo_*'`, `antialias='aa8'`, 1280×1280). Later added `mat_pbr` (`pbrMAT` — dielectric then metallic 0.9/rough 0.2), `depthTOP depth1` (`par.op='render1'`, `depthspace='cameraspace'`/`'reranged'`), `environmentlightCOMP env1` (`envlightmap` = a `rampTOP`, `envlightmaptype2d='equirect'`, `envlightmapprefilter='off'`).
- **Corridor skeleton `/project1/corridor_v1`**: `geo_corridor` (`geometryCOMP`, default torus destroyed) holding **`tubePOP`** (`orient='z'`, `radx/rady 2.5`, `height 50`, `cols 48`, `rows 40`, `normal='pointNormals'`, `closedu=True`, `endcaps=False`, render+display=True; 1920 pts) + `mat_wall` (`pbrMAT` basecolor 0.52 / metallic 0.1 / roughness 0.6) + attenuated point `lightCOMP` (`tz18`, `attenuationend 42`, dimmer 2) dying into the dark far end (= non-arrival) + `cameraCOMP` (`tz22`, fov55, down -Z) + `renderTOP` (`cullface='neither'`, aa8, 720×1280).

**Verified on M1 Metal (the Phase-0 deliverable — screenshot + numeric sampling):** soft2d soft shadows RENDER (the #1 unknown); phongMAT + pbrMAT (dielectric AND metallic, no black-silhouette); **Depth TOP returns valid varying depth from opaque geo** (sampled torus 0.973 / floor 0.968 / bg 1.0 — the linchpin for fog + DOF; perspective depth non-linear, tighten far ~28); Environment Light/IBL (metal reflects env map); Bloom TOP native; 1280 + aa8. **Promoted to `TD_APPLE_SILICON.md` §11.** DOF + volumetric fog have no native node anywhere → build on the Depth TOP.

**First-pass-right:** full pre-build reading discipline (index → debug log → twozero guide → the 1126-line bootstrap) before the first op. **Rule 0 paid off** — the debug log's depth-pass-on-transparent-geo and IBL-prefilter-cost entries were read proactively and shaped the probes (kept geo opaque for depth; `envlightmapprefilter='off'` — the promoted 142ms rule held again). Light `lookat` + tight FOV for the shadow map (correct first try, per renderTOP card). geometryCOMP default-torus destroy handled. Child SOP/POP render+display flags set explicitly. `safe_save()` used (no blind `project.save`). Didn't trust downsampled JPEG for depth — sampled numerically.

**Corrections against the agent (tracker candidates — none formally logged to TD_CLAUDE_DEBUG_LOG yet; do in a promotion pass):**
- **exec-server closure trap RECURRED (2×)** — the existing debug-log entry (2026-06-09, twozero) covers list-comps/lambdas referencing outer-block vars; this session it bit **nested `def` functions** too (`safe_save`, a `depth-sample` helper both `NameError`'d on outer `os`/`dp`). Same root, broader scope. **Extend the rule to "any nested function/closure in `td_execute_python`"; fix = inline or pass as args.** Highest-value — it's a Rule-0-class recurrence.
- **phongMAT diffuse par is `diffr/diffg/diffb`, NOT `diffuser`** (guessed wrong, 1 op-worth of retry). New gotcha.
- **Environment Light opType is `environmentlightCOMP`** (all-lowercase 'light') — guessed `environmentLightCOMP` + `envlightCOMP` first. New gotcha.
- **This twozero server's `td_get_hints` registry does NOT include `'3d'` or `'pop_basics'`** (the bootstrap manual references them, but live topics are: animation/noise/connections/parameters/scripting/glsl/construction/ui_analysis/panel_layout/screenshots/input_simulation/undo/flags/privacy/networking). For 3D/POP par knowledge use **`td_get_docs('pops')` + `td_get_par_info(opType)`** instead — don't burn calls on the missing hint topics.

**WOBAR craft (Nick-reviewed):** the load-bearing diagnosis — **the professional miss is FLATNESS**; five prior pieces lived in the 2D-shader/TOP-composite lane, TD's lowest ceiling, and **"professional" = light + depth + atmosphere on real procedural 3D.** Hence the medium fork to POP-native lit-3D. **Non-arrival becomes a render setting** — attenuated light + (coming) fog eat the far end so a reveal is un-renderable. **Verdict on the skeleton: bones read (a corridor receding to black) but SOFT** — the payoff is ribs (legibility / forward-motion / per-ring phase), fog (kills the transparent far-hole), and light shaping, not the bare tube.

---

## 2026-06-10 (later) — act4_explosion stress test — full system built, KILLED by Nick for fresh start; heavy learnings harvest

**The stress test:** prove the brain can produce striking+professional Act 4 visuals fast. Verdict: the SYSTEM-BUILDING was fast and strong (full pipeline in one session, survived 3 creative pivots cheaply); the AESTHETIC never landed — Nick killed it ("cheesy", chunk-grid read at rest, exploded-state form problems). Network `.toe` at `networks/act4_explosion/` (Nick's save), move files in `networks/heave/` (folder predates his naming).

**What was built (all survives as patterns even though the piece died):**
- **Source arc:** napoleon obj (POPX explode curl example) → GOAT obj → **procedural mass** (spherePOP geodesic + noisePOP, `Massseed` = infinite rock variants, no model sourcing) → **instanced solid chunks** (voxelize interior points → solid box template instancing, `instanceactive='Inside'`).
- **Discharge engine:** Shape Falloff (static, replaced the GPU-killer infection sim) radius-driven; three interchangeable envelope drivers — 8-bar clock (`ctrl_cycle` phase/env/pressure constantCHOP), audio drop-gate (`sel_energy→math_gate→lag_slam`, record-first normalized), **bar-based choreography table** (`anim_song_keys` + `song_kfm` interp module — iris keyframe pattern generalized to bars/BPM-agnostic; columns bar/env/pressure/curve with hold|linear|easein|easeout|smooth). `Usetable`/`Songmix` dials switch drivers.
- **Exploded-view explosion:** global radial dilation (transform_modifier, Localspace=False, scale around centroid pivot) = pieces separate but HOLD FORMATION — kills the confetti-chaos read. Noise demoted to whisper. Attack shaped by asymmetric lagCHOP (rise only — table release stays exact).
- **Pressure fuse:** `pressure` channel through assembled window → per-piece shrink (crack_dilate) opens hairline seams → shadow-casting amber point light INSIDE leaks through. `Coreburn` keeps the furnace lit inside the opened rock at drop.
- **Reformation:** chopexec on env with hysteresis (fire >0.92, re-arm <0.3) bumps `Massseed` at peak shatter + recenters mass + re-aims dilation pivot (centroid via sampled `points('P')`) — every discharge rebuilds a DIFFERENT rock.
- **Integrated tumble:** constantCHOP speed → speedCHOP → `geo.ry % 360` (glass-orb pattern).
- ctrl_master: 7 pages / ~50 pars, atomic rebuild performed mid-session (rule's snapshot→destroy→recreate worked clean; one orphaned par intentionally dropped).

**First-pass-right:** audio spine + record-first normalization (rules worked verbatim), binding template everywhere, obsidian PBR (1 move), HDRI/IBL with prefilter-off (promoted rule prevented the 142ms trap), choreography table design, hysteresis trigger (second attempt), exploded-view dilation concept.

**Corrections against the agent (12 logged in DEBUG_LOG, headline 5):** `pointAttribs` vs documented `pointAttributes`; metallic 0.9 light-suppression (EXISTING rule violated — Rule-0-class miss, bump it); hidden example turntable cost ~6 blind pose iterations (new rule candidate: inventory example drive-chains first); paused-timeline screenshot verification produced 2 false alarms; `../` isOP sibling path → silent white instances.

**WOBAR craft (Nick-reviewed, the real lessons):**
- **Figurative object + literal destruction = stock-FX cheese.** Napoleon → vaporwave; goat → metal-cover. Nick's shipped catalog is ALL abstract — the mirror/encounter lens lives in form+motion, never in a recognizable object doing a literal thing. Abstraction is the brand-safe lane.
- **Loop-feel diagnosis:** a bar-clock state machine reads mechanical; continuity comes from integrated motion + song-structure drive + per-cycle variation (never-same-rock). The fix stack (tumble + table + reformation) is right even though this piece died.
- **"Heavy but held" explosion = exploded-view (formation kept), not particle chaos.** Form must survive the discharge.
- Restraint principle (release standard born this session): `working/WOBAR_RELEASE_STANDARD.md` now exists — 3 gates, accretes per session.
- Hollow-shell fracture reads as skin the moment it opens — solidity must be architectural (instanced solid chunks) not cosmetic.

---

## 2026-06-10 — TD system audit (maintenance, no TD build)

Full review of the TD knowledge system. **Found the promotion pipeline broken:** 14 tracker entries marked promoted had never landed in WOBAR_TD_AGENT_RULES.md — all landed now under "Promoted Gotchas — by Operator Family." Promoted 2 count-2 stragglers (instancetop/instanceop, geometryCOMP torus1) + added the undercounted audio power-curve >1.2 rule. Fixed AGENT_RULES contradictions: Export section (h264nvgpu → non-commercial mjpa workflow), Control Architecture (rewritten around ctrl_master custom pars), feedbackTOP (3 conflicting entries reconciled to one canonical wiring — see Feedback Chain Rules). Promoted the audio normalization/binding patterns. Split this log: sessions 2026-05-06 and earlier → `TD_BUILD_LOG_ARCHIVE.md`. Tracker conventions added (dated bumps, SUPERSEDED markers, verify-promoted-landed). Commit `9815ce5`.

**Process learning:** "marked promoted" and "rule landed" drifted apart because td-save proposes promotions but nothing verifies the rule text was written. The tracker convention note now requires verifying the rule exists in AGENT_RULES before marking the cell.

---

## 2026-06-09 (session close) — glass-orb: audio-reactive tumble, drop-melt, cool-color, cleanup, recorder

Finished the glass-orb (magnetize) as an on-brand **Act-2 / DESCENSION** piece; recorded a master (mjpa .mov → HandBrake). Builds on the v003–v005 entry below (translucent glass, hue-cycle env + IBL-prefilter perf fix, ctrl rebuild — not repeated here).

**Built:** audio-reactive shell tumble; drop-gated feedback MELT; cool-color rework; `Postbypass` A/B; network cleanup (10 dead ops + `Showmarkers` removed, subsystem-band layout, 24 node comments + `description` DAT); `rec_out` recorder.

**New reusable patterns:**
- **Audio-reactive ROTATION must be *integrated*, not multiplied:** band → `base+band*react` → `speedCHOP` → angle; geo rx/ry/rz = `angle*Lissajous_ratio % 360`. Multiplying into `absTime*speed` makes rotation JUMP on band changes.
- **Smooth envelopes from builtins (no `sin`):** decaying `pow(1-phase,n)`; symmetric swell `1-x²(3-2x)` with `x=2*min(phase,1-phase)`; triangle via `abs`.
- **Drop-gated audio event:** `clamp(0,(band-gate)*sens,max)` — clean verses, blooms only on drops. `base_audio.energy` ~0.07 quiet → ~0.8 drop; set gate mid-range.
- **Feedback melt:** `feedbackTOP` defaults to **128×128** → set loop res + force-cook; needs `par.top` AND target wired to `input[0]`.
- **Cleanup:** unused-param scans MUST recurse into nested ops (`instancer1/Distribution/spherical` missed → false "unused").
- **rampTOP:** `circular`=concentric (vignettes) vs `radial`=angular; colors via `<name>_keys` DAT.

**Failures (see TD_CLAUDE_DEBUG_LOG):**
- **Repeated bare-`sin`** (logged 2026-05-04 — Rule-0 miss). Fix `math.sin()`. NEW: expr error cascaded → upstream 4K HDRI re-decode 390 ms/frame → fps crash. Check `errors(recurse=True)` when fps tanks.
- **DOF on translucent/instanced glass** — no clean depth pass; abandoned.
- **Non-commercial TD** — no h264; mjpa .mov / PNG seq, pcm16 audio, `audiochop`→44100 `audio_in` (locked).

**WOBAR craft (Nick-reviewed):**
- Audio-reactive motion = the load-bearing element that makes Act-2 "breathe WITH the sound."
- **Depth = spectrum** (lows far/large, highs near/small = a "frequency tunnel"). Nick loved it — keep.
- On-brand Act-2 psychedelia ≈ cool-band hue + desaturation (~0.45) — **a starting point, not a hard rule.** Color comes from the hue-cycle/env, not the (neutral) glass.
- Process: don't fight the tool (DOF-on-glass abandoned); when the last addition makes it worse, stop.
- HELD pending proof: drop-melt as the Act-2↔Act-4 dial.

---

## 2026-06-09 (latest) — magnetize / glass-orb v003–v005 — translucent glass, hue-cycle env, ctrl rebuild

**What was built (on top of the v002 mirror-orb):** multi-pole roaming glints; full **ctrl_master rebuild** into a clean 14-knob panel (+ Showmarkers debug toggle); **translucent frosted-glass** material (pbrMAT: metallic ~0.4, roughness 0.3, alphafront=Opacity + alphaside 0.9 fresnel, blending on, render transparency=sortedblending); **hue-cycling environment** (hdri_env → env_down resTOP → hsv_cycle hsvadjustTOP → env light) for color-cycling reflections, with Cyclespeed/Saturation/Opacity knobs.

**Reusable learnings:**
- **★ Animating an environment light's map re-bakes its IBL every frame — and `envlightmapprefilter='automatic'` is the killer (142 ms/frame here).** Fix: set the env light's prefilter to **`off`** and **downsample the source map** (a resTOP to ~512×256) → ~0 ms, 60 fps. Tradeoff: reflections lose roughness-blur (sharper). For any animated/cycling env, do this first. (Alternative if you need the blur: hue-cycle the final render in *post* instead — ~1 ms, but uniform hue across the whole image rather than varied-per-facet.)
- **Translucent in TD:** material needs `alpha<1` AND `blending=True`; the renderTOP needs `transparency` = sortedblending (or orderind). `alphafront`/`alphaside` give a cheap fresnel-glass feel (see-through face, solid rim). pbrMAT **rimlight is a sequence par that resisted enabling** (`mat.par.rimlight`/`seq.rimlight.numBlocks` both no-op'd) — didn't fight it; got edge/contrast via emit + reflection instead.
- **ctrl_master rebuild pattern** (destroy all custom pars → recreate clean set → re-wire every target op via expressions) works great, BUT: (a) rewiring leaves transient "no attribute" errors until the rewire completes — do destroy+create+wire in one pass; (b) a couple recreated params init'd to a wrong value (Camdist came up 4.4 not 9.2) — re-assert all defaults explicitly after creating. Also: params that were silently **disconnected** (set directly on the op during earlier work) won't show in a reference search — check the op's actual par mode, not just the ctrl value.
- **Process win:** after two rabbit holes earlier, the recurring shard-orientation fight (sliver chaos kept re-aligning to surface latitude rings) was **dropped on Nick's call** ("lets not fight this") and reverted to small squares — knowing when to stop fighting the tool is the skill.

---

## 2026-06-09 (later) — magnetize / mirror-orb v002 — strip-back → intentional rebuild → concept pivot to reflective mirror-orb

**What was built:**

Per Nick's call after the v001 rabbit hole, **stripped the network to a legible base** (flat-white constantMAT `mat_flat`, fixed camera, all forces/bloom/HDRI/rainbow off — `color_modifier1` Bypass, `magnetize` neutralized) so every shard was visible, then **added variation one intentional decision at a time** (each via a multiple-choice question to Nick): sphere form (geodesic volume) → fine elongated slivers → motion. Mid-session **concept pivot**: from "murmuration" to **"mirror fragments the poles orient"** — flat reflective plates whose orientation the poles drive. Built a full-bleed **flat** reflective mirror (metallic `mat_obsidian` + `env_obsidian` HDRI), discovered the pole couldn't affect it, and **landed on a reflective mirror-orb** where a wandering pole turns the facets toward it. Saved `magnetize_v002.tox`.

**What worked:**

- **Strip-to-legible-base methodology** (the v001 lesson applied): flat-bright the field, fix the camera, kill effects → every subsequent decision was made with full visual information. Hugely effective; should be the default opening move for any aesthetic exploration.
- Driving each variation as an explicit either/or decision to Nick (form, density, shard shape, motion, surface curvature) kept it intentional and prevented drift.
- Mirror look: metallic pbrMAT (`metallic` 1.0, `roughness` ~0.12) + `environmentlightCOMP` HDRI in `render1.lights` → convincing reflective facets, each catching a different environment slice.

**What needed correction / the BIG finding:**

- **★ magnetize orientation-aim (`Affectrot`) requires VARIED facet normals — it does NOTHING on a flat grid.** Confirmed exhaustively by reading the output `N`/`Orient` attributes: on the flat camera-facing plane (all normals +Z), attract/repulse aim → identity (no change), spin → in-plane rotation only (a flat facet's reflection is unchanged by in-plane spin). On a curved sphere (normals vary), the same aim engages and turns facets toward the poles. **Orientation-driven pole effects are a curved-surface phenomenon.** This cost ~25–30 tool calls of diagnosis before the geometric cause was nailed — should have tested the mechanic's surface-dependency *immediately* after the pivot instead of building the whole flat mirror first.
- **Coplanar thin plates z-fight:** a grid of paper-thin plates at identical depth, overlapping (size ≥ spacing), banded badly. Fix: shard size < grid spacing → distinct facets, no overlap, clean.
- **POPX grid `Size` axis mapping is NOT x/y/z intuitive** for a camera-facing plane: `Size1`=width(X), `Size2`=depth(collapse to 0), `Size3`=height — found empirically (the plane rendered edge-on until corrected). Also: the spherical `Distribution` par toggles volume(filled ball) vs surface(shell); `Numpoints` only applies when `Enablescatter` is on (otherwise count comes from geodesic `Freq`).
- **Disk filled to <0.4 GB twice mid-session** (machine-level, not our ~MBs) → TD couldn't write screenshots. Watch for it; clearing the pisang screenshot temp doesn't help (need GBs).

**Process note:** the flat-plane-pole detour was a second rabbit hole. The recovery pattern that worked both times: stop, read the actual data (attributes/measurements), find the *geometric/structural* cause, then present the real fork to Nick rather than tuning blindly.

**Correction tracker:** the **list-comprehension / genexpr / nested-def in `td_execute_python`** failure recurred AGAIN several times this session (already a rule). The **"flat-light for legibility before tuning"** lesson is now its own confirmed method (v001 flagged it, v002 proved it by *applying* it successfully) — promote to `WOBAR_TD_AGENT_RULES.md` as a working rule. New candidate (1st occurrence): **"orientation/aim pole effects need a curved surface — test surface-dependency of any orientation mechanic before building the surrounding scene."**

---

## 2026-06-09 — magnetize / murmuration v001 — built end-to-end, then hit a legibility wall (13 moves)

**What was built:**

A murmuration visualizer from the POPX `magnetize` example: 3D shard cloud (instancer grid → `magnetize` wandering attract poles, `Solvermode=advect` for a flowing flock) reflecting a dark studio HDRI via an obsidian-ish pbrMAT + `environmentlightCOMP`, bloomTOP, pure-black composite. `ctrl_master` (5 pages). A song-structure **DIVE system**: `dive_keys` tableDAT (`time|value|curve`) + `dive_kfm` module `get(t)` [reuses the iris_2 `pupil_kfm` pattern] driving a single **Dive 0–1**, with camera distance + elevation + glow (bloom/env) all lerping between dialed inside/outside extremes, plus an ease-out-back `overshoot` curve. Camera went orbit → fly-through → straight dive (first two built then removed). Saved as `magnetize_v001.tox`.

**What worked first pass:**

- magnetize repel-pole + beat-pulse for an Act-4 discharge mechanic; later attract-poles + advect for flocking
- Single **Dive 0–1** value driving camera + glow via `lerp(out,in,dive)` expressions — clean two-extreme model with smooth interpolation
- `dive_kfm` keyframe table reusing the established `pupil_kfm` pattern (sort → bracket → apply curve; curves linear/smooth/ease-in/ease-out, plus a new `overshoot` ease-out-back for natural momentum)
- Removing vestigial custom params cleanly with `op.par.Name.destroy()` after cutting the orbit feature

**What needed correction / what went wrong:**

- **THE RABBIT HOLE — tuning a near-invisible field (key lesson).** The shards were near-black obsidian, so most of the cloud was black-on-black — only glints read. We burned ~30 calls trying to get "enveloped inside" and kept seeing a "small blob," because the surrounding shards were *invisible, not absent*. **RULE CANDIDATE:** never tune form / composition / camera framing on a dark or low-contrast field — flat-light it bright first for legibility, apply the real (dark/reflective) material *last*.
- **POPX render-vs-geometry scale mismatch (UNRESOLVED — flag).** `poptoCHOP` on the magnetize output measured the cloud at ±1.8 (P_0/P_1/P_2), camera demonstrably inside at z=0.3, render confirmed using that camera, `geo2`/`instance1` scale all 1.0, near-clip cleared — yet it rendered as a small central blob. Root cause not found (suspect POPX packed-transform instancing renders at different positions than the readable POP P attribute).
- POPX example `.tox` must be opened **natively (File > Open)**, NOT `loadTox`'d — relative external-sync paths break, modules fail to init/compile, and TD can crash (SSFR crashed TD on Metal during this exploration).
- POPX 1.4.0 needs **TD 2025.32820**; on 32460 the core POP-GLSL (`applyatt/apply`, Instancer compute) fails to compile on Metal — upgraded TD to fix. SSFR + Path Tracer are Vulkan-only; Explode/Voronoi GPU-compute are Metal-incompatible.
- **Method correction (Nick-driven):** rapid experimentation without legibility compounds guesses. Nick called the pivot — "strip to a simple legible base, add variation one intentional decision at a time."

**New TD gotchas (this session):**

- Save a COMP with `comp.save(path)` — NOT `saveToFile` (that's a TOP method)
- Remove a custom parameter with `op.par.Name.destroy()`
- `poptoCHOP` references its source POP via `par.pop` (a path), NOT a wired input connector
- `computeBounds()` on a POPX render geo COMP returns the **template** bounds, not the instanced cloud extent — measure the real cloud with `poptoCHOP` + P_0/P_1/P_2 channel min/max
- `nullCOMP` spawns a `primitive1` that can cook expensively — set `render=False` or use a `baseCOMP` for a lightweight camera look-at target
- camera `near` clip defaults to **0.1** (clips near geometry when flying inside a volume — lower it for interior shots)
- `environmentlightCOMP` (lowercase) is the IBL env light: `par.envlightmap` = equirect HDRI TOP, `par.dimmer` = intensity, `par.envlightmaprotatey` = rotation
- magnetize `Solvermode`: **`simple`** (stateless — snaps to current force, good for envelope-synced reassemble) vs **`advect`** (stateful momentum — needed for flowing/flocking)
- magnetize **attract** poles HOLLOW the cloud (shards evacuate toward the off-center poles, sparse middle); low `Attract` keeps the grid filled
- POPX **Instancer `Globuniscale`** behavior on positions-vs-shard-size is ambiguous and bit us — verify empirically with a measurement before assuming

**Correction tracker:** the **list-comprehension / nested-function-in-`td_execute_python`** failure recurred *many* times again this session — already a rule in `WOBAR_TD_AGENT_RULES.md` (Python Scripting Rules). No new promotion; reinforces the existing rule. The "open POPX examples natively, don't loadTox" lesson now has 1 occurrence (this session) — watch for a repeat to promote.

---

## 2026-05-26 (later) — down_bad_3stack v002 — full pipeline (video timing + audio reactivity + post + export)

**What was built:**

End-to-end music video visualizer on top of v001's composition. New ops: `base_audio_react` (per-band normalization layer, ~30 ops), beat-driven global CA chain (3 levelTOPs + 2 transformTOPs + 1 compositeTOP), cinematic post chain (level_grade + hsv_grade + bloom_post + grain_noise/grain_level/grain_apply), moviefileoutTOP `movie_out`. ctrl_master reorganized to 4+1 pages (Top/Mid/Bot/Video/Post) with ~40 dials. Video timing system: composite ternary index expression on movie_in with Videodelay + first jump (Videoskipat/Videoskipdur) + second back-jump (Videojump2at/Videojump2to). Audio reactivity via per-binding `Base + React * pow(clamp(audio_n, 0, 2), Curve)` formula across 3 bindings (sub_pressure→Echoopacity, bass→Posterize, beat-pulse + sub_bass scalar → CA offset). Cook rate retimed 60→30 (with time.end retimed 11650→5825 frames) to preserve duration when heavy pipeline couldn't sustain 60 cook-fps. Network not saved as canonical .toe — risk to flag.

**What the agent got right first pass:**

- Per-band normalization architecture once mathCHOP scoping understood (selectCHOP upstream → mathCHOP with preoff/gain → renameCHOP _n suffix → mergeCHOP → null_out)
- Audio binding formula `Base + React * pow(clamp(audio_n, 0, 2), Curve)` with React=0 default returns unchanged baseline behavior — Nick dials in, no rewiring needed
- ctrl_master 4-page reorganization (snapshot all values → destroy all custom pars → recreate on correct pages in order → restore values) preserved expression references because par names stayed identical
- 3-channel manual CA chain (3 levelTOPs zeroing two channels each + 2 transformTOPs offsetting R and B in opposite directions + 1 compositeTOP add to recombine) is clean and tunable via single Caoffset dial
- Cinematic post chain template (level → hsv → bloom → grain) wired in one move with 8 paired dials on a new Post page

**What needed correction:**

- moviefileinTOP `playmode` menu values: agent guessed `specifyindex`, actual is `specify` (4 options: locked / specify / sequential / timecodeop)
- moviefileinTOP `numFrames` attribute renamed to `numImages` in TD 2025+ (raises tdError when accessed via old name)
- `me.numImages` in TD parameter expression triggered cook-loop warning falsely (TD analyzer flagged self-reference) — fix: hardcode the integer value in the expression rather than reading via me
- `me.time.seconds` in expression versus exec-tool returned different values; me.time on movie_in = root.time (frame 4363 = 145.4s when cursor scrubbed). Use me.time.seconds for timeline-locked refs; absTime.seconds is wall-clock and won't follow scrubbing/pause
- addSOP `par.addpts` is a toggle that must be set True BEFORE par.point=N takes effect — silently outputs 0 points otherwise
- sphereSOP uses `par.radx / rady / radz` NOT `par.rad` (tdAttributeError on par.rad)
- copySOP wiring: input 0 = template (the geometry to copy), input 1 = source (the points to copy template onto) — reversed gives nothing
- mathCHOP `par.scope` does NOT filter channels — it picks which channels the math applies to, but ALL channels pass through to output. Per-channel normalization requires a selectCHOP upstream OR per-band mathCHOP that gets channels-of-one
- mergeCHOP inputs dynamically grow + compact when connections change. `for ic in mb.inputConnectors: ic.disconnect()` left stale wires AND created duplicates because the connector list shifted mid-iteration. Pattern: disconnect by exact slot index, verify connection count between operations
- compositeTOP type constant is `compositeTOP` not `compTOP` — bare guess raises NameError. Compose: `cm.create(compositeTOP, 'name')`
- TD `appendFloat` par naming rules: First letter uppercase, rest lowercase+digits only. `EchoopacityReact` raises tdError (has multiple uppercase). Use `Echoreact` or `Echoopreact` (abbreviated)
- TD par eval cache vs expression eval: `par.val` returns cached value, `par.eval()` returns current expression result. For verification of expression-mode pars, always `.eval()`
- moviefileoutTOP `par.audiochop` rule: when TWO audiofileinCHOPs exist with same file but different playmode, you MUST route to the LOCKED-TO-TIMELINE one. Sequential one plays in real-time from sample 0 regardless of timeline state → export audio starts from song beginning while video tracks timeline = desync. Live preview hears whichever one is connected to the audiodeviceout, hiding the bug
- TD perf gotcha: heavy comp pipeline (here: 3 panels × treatments + feedback + edge + posterize + CA + post chain + bloom + grain) cannot sustain `cookRate=60` on a 1280×720 source. me.time.seconds advances slower than wall time → video plays slow-mo. Fix: drop project.cookRate + root.time.rate to 30 (also retime root.time.end so the duration in seconds is preserved). Video is 23.978 fps native so 30 is plenty of headroom
- moviefileinTOP `par.samplerate` defaults to 30; controls how index→file-time mapping works. If samplerate=30 but the file is 23.978 fps and the index expression advances at the file's native rate, playback is ~20% slow. Set samplerate to match the file's native rate (numImages / duration_sec) for 1:1 index→frame mapping
- Wobar's existing entry "compositeTOP `over` with swaporder=False puts INPUT 0 ON TOP" (Promoted, 2026-05-04) bit again — comp_on_black wiring during VILOS work followed pattern correctly but it cropped up across sessions, reinforcing the promotion
- baseCOMP customPars iteration during destroy: `for p in cm.customPars: p.destroy()` raised "Invalid Par object" because the iterator invalidated after the first destroy. Fix: collect names first, then destroy by getattr lookup

**New patterns established (worth promoting to TD_AGENT_RULES):**

- **Per-band CHOP normalization layer from rec_audio stats** for audio reactivity: record full song through base_audio's published null_audio CHOP, compute per-band stats (min/p10/p25/p50/p75/p90/p95/max), build `base_audio_react` baseCOMP that selectCHOPs each band → mathCHOP normalizes (preoff = -p10, gain = 1/(p_hi - p10), where p_hi = p90 for steady bands, p95 for sparse spike bands like transient) → renameCHOP adds `_n` suffix → mergeCHOP combines into single output null. Publishes 8 normalized channels for use in any downstream expression. Sample-call: `op('/project1/base_audio_react/null_out')['bass_n']`
- **Audio binding template:** `Base + React * pow(clamp(audio_n, 0, 2), Curve)` with paired ctrl_master dials per binding. React=0 default leaves baseline untouched (no audio influence); Nick dials React up to introduce reactivity without rewiring expressions. Curve shapes response: 1=linear, 1.5=gentle punch, 2.5=very punchy (small values ignored, big peaks land hard). Clamp at 2 lets peaks above p90 still register stronger (~2× max linear range) without unbounded blowups
- **Tempo-driven beat pulse expression** for rhythm-locked visual effects on songs with known BPM: `exp(-((me.time.seconds * BPM / 60 / div) % 1) * decay)` gives a clean per-beat exp-decay pulse (1.0 at downbeat, decays to ~0 by next beat). Pair with optional audio scalar layer `((1 - Beataudio) + Beataudio * clamp(audio_n, 0, 2))` so drops can intensify the pulse while breaks stay flat. 4-dial pattern: Beatbpm + Beatdiv (1=every beat, 2=halftime, 4=downbeats) + Beatdecay (higher=sharper) + Beataudio (0=constant, 1=fully audio-modulated)
- **3-channel manual CA chain** (TD has no native CA op): `input → 3 × levelTOP` each zeroing two channels via `par.high{g,b}=0` for keep_red etc → `2 × transformTOP` (R: tx=+offset, B: tx=-offset, G stays center) → `compositeTOP operand=add` to recombine. Drive offset via pulse expression for rhythm-locked color split. Tuned to nostalgic register (1-3px offset = analog VHS) vs rainbow register (8px+ at saturated luminance = rave). Per WOBAR_TD_AGENT_RULES Materials: muted+small=on-brand analog, saturated+large=off-brand rave
- **Cinematic HDR post template** for final-look stage: `comp_input → level_grade (Cineblacks/Cinegamma/Cinecontrast for crushed blacks + S-curve + contrast) → hsv_grade (Cinesat for saturation) → bloom_post (Bloomint/Bloomthresh/Bloomradius output=inputplusbloom for highlight glow) → grain_apply (compositeTOP screen with grain_noise simplex2d animated via absTime seed + grain_level opacity=Grainamount) → null_out`. 8 dials on dedicated Post page. Per IG-export strategy: grain serves double duty — analog texture + banding protection through platform 4:2:0 re-encode
- **moviefileoutTOP audio routing rule:** when project has multiple audiofileinCHOPs of the same file (common when an audiofileinCHOP feeds base_audio analysis chain AND a separate one feeds direct audiodeviceout for live monitoring), the moviefileoutTOP MUST receive the LOCKED-TO-TIMELINE one via par.audiochop. Sequential-playmode audiofileinCHOPs play in real-time independent of timeline cursor → render captures audio from song beginning regardless of timeline state → desync from video which is timeline-locked
- **ctrl_master 4-page reorganization atomically:** snapshot all customPars (name → val + default) → collect par names list → destroy each by getattr lookup (NOT iterator) → destroy all customPages → recreate desired pages via appendCustomPage → for each page in order, appendFloat each par with desired label, restore val + default. Expression references survive because par names stay identical; only page assignment changes

---

## Correction Tracker

Corrections that appear 2+ times get promoted to WOBAR_TD_AGENT_RULES.md.

**Conventions (2026-06-10):** When bumping a count, append the session date to the count cell (e.g. `2 (05-23, 06-09)`) so bumps are traceable. When a later entry supersedes an earlier one (better diagnosis of the same issue), mark the old entry `SUPERSEDED →` with a pointer instead of leaving two conflicting fixes live. "Promoted" means the rule text actually exists in WOBAR_TD_AGENT_RULES.md — verify it landed before marking the cell. (2026-06-10 audit found 14 entries marked promoted whose rules had never landed; all landed now under "Promoted Gotchas".)

| Correction | Count | Promoted? |
|-----------|-------|-----------|
| isOP pars referencing SIBLINGS need bare name — `./name`=child, `../name` FAILS SILENTLY (renderTOP camera 05-21; geometryCOMP material → white instances 06-10) | 2 (05-21, 06-10) | ✅ PROMOTED (AGENT_RULES Promoted Gotchas; verified 2026-06-12) |
| POP python: `pointAttributes` (not pointAttribs), `numPoints()` is a method, point data via `points('AttrName')` | 1 (06-10) | No |
| Infection/Spread Falloff are SIMULATIONS (neighborPOP per-frame cost explodes on dense meshes, 2.6s/cook GPU); Shape/Object/Curve/Noise/Texture falloffs are static ~0ms | 1 (06-10) | No |
| Geometry upstream of voronoi fracture must be STATIC — animating it re-partitions per frame; time-dependent exprs force cooks even multiplied to 0 (remove expr, don't zero it) | 1 (06-10) | No |
| pbrMAT `darknessemit` is a boolean toggle; emission strength rides `darknessemitcolor` RGB. Emit-where-dark needs a lit scene to differentiate | 1 (06-10) | No |
| Inventory example .tox drive chains BEFORE building on them — dump expression-mode pars on top-level ops (hidden turntable `geo1.ry` cost 6 blind iterations) | 1 (06-10) | No |
| Paused-timeline screenshots of sim-driven networks show STALE state — verify live or numerically; freeze the driver par, not the clock | 1 (06-10) | No |
| resolutionTOP needs `outputresolution='custom'` before resolutionw/h; compositeTOP inherits res from FIRST input (square grain leaked downstream) | 1 (06-10) | No |
| Threshold triggers on noisy CHOPs need hysteresis (fire >hi / re-arm <lo via DAT storage armed flag) — naive prev/val edge fires on every wiggle | 1 (06-10) | No |
| POPX module PULSE pars are silent from python `.pulse()` (extension-handled); value pars work — prefer value-par equivalents to drive sims | 1 (06-10) | No |
| POPX explode = surface fracture (open shells; Mac clip_triangles compile-fails = no capping). Solid chunks = instanced-solid architecture: voxelize Outputvolume points (clean attrs, no Color) + `instanceactive='Inside'` + HitNormal as free rotto variation. mesh_fill outputs Color = instancing killer | 1 (06-10) | No |
| shape_falloff radius exactly 0 degenerates (falloff=1 everywhere) — floor at 0.05 | 1 (06-10) | No |
| moviefileoutTOP `par.audiochop` must point at LOCKED-to-timeline audiofileinCHOP, not sequential — sequential plays real-time from sample 0 regardless of timeline → export audio desyncs from video | 1 | No |
| moviefileinTOP `playmode` menu values are `locked` / `specify` / `sequential` / `timecodeop` — NOT `specifyindex` | 1 | No |
| moviefileinTOP `numFrames` attribute renamed to `numImages` in TD 2025+ — old name raises tdError | 1 | No |
| addSOP `par.addpts` is a toggle that MUST be True before `par.point=N` takes effect — silently outputs 0 points otherwise | 1 | No |
| sphereSOP uses `par.radx / rady / radz` — NOT `par.rad` (tdAttributeError) | 1 | No |
| copySOP wiring: input 0 = template, input 1 = source (points to copy template onto) | 1 | No |
| mathCHOP `par.scope` only filters WHICH channels get the math — others pass through unchanged. Per-channel normalization requires selectCHOP upstream OR per-band math CHOP scoped to one channel | 1 | No |
| mergeCHOP inputs dynamically grow + compact — `for ic in mb.inputConnectors: ic.disconnect()` leaves stale wires AND creates dupes. Disconnect by exact slot index, verify count between operations | 1 | No |
| compositeTOP type constant is `compositeTOP` NOT `compTOP` — bare guess raises NameError | 1 | No |
| TD `appendFloat` par naming: First letter uppercase, rest lowercase+digits only. `EchoopacityReact` raises tdError; `Echoreact` or `Echoopreact` works | 1 | No |
| Heavy comp pipeline + cookRate=60 → TD can't sustain wall rate → me.time.seconds advances slow → video uses me.time plays slow-mo. Fix: drop cookRate to 30 + retime time.end to preserve duration | 1 | No |
| moviefileinTOP `par.samplerate` controls index→file-time mapping. Mismatch with index expression's fps multiplier = slow/fast playback. Set samplerate to file's native rate (numImages / duration_sec) for 1:1 mapping | 1 | No |
| `me.numImages` inside same-op parameter expression triggers false cook-loop warning — hardcode the value or read from a different op | 1 | No |
| baseCOMP customPars iteration + destroy: iterator invalidates after first destroy → "Invalid Par object". Fix: collect names first, then destroy by getattr lookup | 1 | No |
| absTime.seconds is wall-clock (continues during pause); me.time.seconds is timeline (follows scrub/pause). Use me.time for timeline-locked refs | 1 | No |
| `filterCHOP` is smoothing not frequency — use `audiofilterCHOP` | 1 | No |
| `lagCHOP` par names are `lag1`/`lag2` not `lagup`/`lagdown` | 1 | No |
| Multiple op() in TOP expressions (5+ × 8 pars) crashes TD — pre-compute in CHOP | 1 | No |
| `par.val` returns cached value — use `par.eval()` to verify expression result | 1 | No |
| COMP custom par referencing CHOP has cook order issues when TOPs read it — reference CHOP directly in TOP expressions | 1 | No |
| `playmode='locked'` ties audio to timeline length — use `sequential` for full track | 1 | No |
| `audiodeviceoutCHOP` with `cookalways=True` freezes TD | 1 | No |
| Python helper functions in `td_execute_python` don't inherit script-level globals — all `op()` refs must be inside the function body | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| `annotateCOMP` nodeY = bottom edge (not top) — top = nodeY + nodeHeight | 1 | No |
| `analyzeCHOP function='average'` returns ~0 on HP filter output — use `rmspower` for highpass chains | 1 | No |
| `null_audio` is analysis CHOP at rate 30 — use `audio_in` (audiofileinCHOP) for recording audiochop | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| Geometry COMP has no external SOP input connectors — SOPs must be created as children INSIDE the COMP | 1 | No |
| `op.display = True` / `op.render = True` (not `setDisplayFlag()`/`setRenderFlag()` — those methods don't exist) | 1 | No |
| `tdu.noise()` doesn't exist in TD Python — use noisePOP or Noise SOP for noise generation | 1 | No |
| blurTOP at full resolution with large size (>20px) is CPU-locked — use box type, smaller size, or reduce resolution | 1 | No |
| AAC audio codec blocked on Non-Commercial license — use MP3 codec instead (mp3 is supported, aac is not) | 1 | No |
| `instancepop` and `instanceop` on Geometry COMP don't do position-based instancing — use Script CHOP bridge (SOP points → tx/ty/tz channels) | 1 | No |
| Script CHOP `op()` resolves at parent COMP scope — siblings accessed as `op('name')` not `op('../name')` | 1 | No |
| ~~feedbackTOP direct wire to target creates cook dependency loop — wire a black seed instead; set par.top = target path only~~ **SUPERSEDED →** see canonical feedbackTOP wiring entry below (fresh upstream content on input[0], target as par.top, resetpulse) | 1 | Superseded |
| MAT expressions inside child COMPs: relative `op()` paths return None — use absolute paths | 1 | No |
| hsvadjustTOP saturation par is `saturationmult` not `satmult` | 1 | No |
| HSV desat kills warm low-luminance colors — muted orange/warm goes black. Warm palettes need higher RGB values to survive the desat chain | 1 | No |
| `triggerCHOP` par expressions unreliable — use `ParMode.CONSTANT` with hardcoded values | 1 | No |
| List comprehensions in `td_execute_python` cannot reference outer-scope variables — use explicit for loops | 1 | No |
| `instancetop` on Geometry COMP is for TOP-based color instancing only — use `instanceop` for CHOP-based position instancing | **2** | **✅ PROMOTED** (06-10; verified 2026-06-12) |
| Script CHOP callbacks: NEVER overwrite the whole DAT — TD silently re-generates the template over custom code. Always read existing DAT first, edit `onCook` in place with `text.replace()` | 1 | No |
| poptoCHOP download (immediate or nextframe) on 1800+ points at 60fps kills FPS (3–6ms/cook → <10fps). Use static Script CHOP positions + bypass POP chain instead | 1 | No |
| Script CHOP with no CHOP inputs + `CookLevel.WHEN_USED`: cooks ~1/s not 60fps. Wire an audio CHOP input or use `CookLevel.ALWAYS` for per-frame updates | 1 | No |
| noiseCHOP `par.channelname` always returns 0 channels regardless of value or timeslice setting — cause unresolved, workaround TBD | 1 | No |
| Camera expression `absTime.seconds * speed` drifts to large values across session — use `me.time.seconds` which resets with the component | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| GLSL TOP: `iTime` and `uTD.time.seconds` are not available — pass time as a uniform via `color0rgbb.expr = absTime.seconds * rate` | 1 | No |
| RampTOP does not have `par.ramppoints` — use a companion textDAT with pos/r/g/b/a rows and set `par.dat = keys_dat` | 1 | No |
| Circle TOP: `radiusunit` defaults to pixels — 0.48 pixels ≈ invisible on 720×1280. Set `par.radiusunit = 'fractionaspect'` for proper portrait coverage | 1 | No |
| Cross-COMP CHOP wiring fails silently — use `selectCHOP` with absolute path `chops='/project1/comp/inner_chop'` | 1 | No |
| `geometryCOMP` auto-creates a default `torus1` (torusPOP, render=True) child — kills new builds with a giant white blob unless explicitly destroyed | **2** | **✅ PROMOTED** (06-10; verified 2026-06-12) |
| `compositeTOP` has only 2 input slots — `inputConnectors[2]` raises IndexError. Chain multiple 2-input composites for N-input add | 1 | No |
| `me.storage` inside scriptCHOP onCook callback = the DAT's storage, NOT the operator the callback is attached to | 1 | No |
| scriptCHOP needs a time-dependent input (e.g. constantCHOP with `value0.expr=absTime.seconds`) wired in to recook per frame — `absTime` inside the callback alone doesn't track | 1 | No |
| `pow(negative_float, 2.5)` in expressions returns COMPLEX → TypeError. Audio channels can have tiny negative noise (~1e-22). Always wrap in `max(0.0, ...)` before `pow()` | 1 | No |
| Velocity-based "anti-collapse" thermostats fail when bodies cluster while still spinning fast inside the cluster — use SPREAD-based (cluster bounding radius) instead | 1 | No |
| Fibonacci-sphere seed positions place bodies at ±Y poles where `cross(pos, Y_axis) = 0` → those bodies start with zero tangential velocity and drag the system into collapse. Use a body-varying reference axis | 1 | No |
| Audio analysis CHOP `energy` channel returns tiny negative values (~e-22) at silence — `energy ** non_integer_exp` raises 'float() argument must be a string or a real number' (returns complex). ALWAYS wrap as `max(0.0, energy) ** exp` in audio-driven expressions | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| `geometryCOMP.par.instancesx/y/z` accept BARE attribute names ONLY (`'ScaleRand'`) — NOT expressions (`'LenVel*0.6'`). For composite math, write the result to a new attribute via `mathmixPOP` (comb0oper='mult', comb0scopea/b, comb0result='OutAttr') and read OutAttr as the bare instance scale | 1 | No |
| POPX SA `Pointsupdatepop` feedback loop: custom attributes written upstream of SA (e.g. `randomPOP outputattrscope='ColorU'` before sa1) are STRIPPED at SA's output. Only solver-managed attrs (P, PartVel, N, Color, LenVel) pass through. Write per-particle attrs DOWNSTREAM of SA, before geometryCOMP.instanceop chain | 1 | No |
| `nullPOP.points('Color')` returns a list of TUPLES per point (4-comp Color = list of 4-tuples). `nullPOP.points('LenVel')` returns list of FLOATS. Don't index as `arr[i*4+k]` for color — that yields a tuple. Iterate as `pt = arr[i]; pt[component]` | 1 | No |
| `renderTOP.par.geometry` is a glob PATTERN, not a SOP/COMP path. `'geo_attractor'` matches that COMP only. `'geo*'` matches all geo-prefixed. `'* ^geo_aura'` includes all except geo_aura. Setting full path (`/project1/geo_attractor`) silently fails to default-include-everything | 1 | No |
| Aizawa (and other chaotic) attractor's instantaneous mass-center is NOT temporally stationary — particle distribution cycles around the manifold over 30-60s. Hardcoded `cam.lookat = static_null` drifts off-center over time. Solution: `executeDAT.onFrameStart` reads `null_pop_out.points('P')`, computes mean × geo.scale, EMA-lerps lookat target tx/ty/tz at alpha=0.04 (~0.4s lag time-constant — feels cinematic, not jitter) | 1 | No |
| `compositeTOP operand='over'` with input0 + input1: input1 is the TOP layer (composited OVER input0). For form-on-bg with form's render bgcolor=(0,0,0,0), simpler mental model: use `operand='add'` instead — non-form pixels (RGB=0) add nothing to bg, form pixels (RGB>0) light up bg | 1 | No |
| TD `non-realtime mode` (export mode) renders every frame without skipping — good for video export but causes audio playback clicks because `audiodevout` can't keep pace with cooked-frame rate. Switch back to realtime for live audio reactivity tuning | 1 | No |
| **TD `geometryCOMP` instancing rejects POPX-derived POPs that carry rich attribute sets** (PartVel, PartId, PartForce, PrevP, Density, etc.). Error: "Manual number of instances not supported when using a POP with point co[lor]" — even after stripping Color via `attributePOP.par.deletepoint='Color'`. Workaround: instance from native particlePOP (clean attrs) OR from POPX modules with simple POP outputs (SA works because P/PartVel/N/LenVel only) | **3** | **✅ PROMOTED** (verified 2026-06-12) |
| **`oplength` instance count mode reads `1` from POPX module nullPOP outputs** even when `numPoints()` returns thousands. TD geo COMP can't introspect POPX-derived POPs for instance count. Workaround: `instancecountmode='manual'` + `numinstances.expr = "op('/path/to/null').numPoints()"`. Native particlePOPs hit this same bug — manual mode required for both | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **`scriptTOP` with `CookLevel.ALWAYS` doing per-frame numpy operations on stream inputs crashes TD repeatedly** (locked up MCP server twice in one session). Even `CookLevel.ON_CHANGE` is dangerous if the input changes every frame (like a particle stream). Avoid scriptTOP for high-frequency numpy ops on streaming POP/CHOP data | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| POPX `Particle` (Fluids-PBF) with `Enablebboxcollision=True` + `Usecustombounds=True` does NOT actually contain particles at default `Substeps=1`. Particles tunnel through bbox at gravity scale, falling to y=-167 within seconds. May need higher Substeps + Iterations OR alternate constraint mechanism (collisontop SDF) | 1 | No |
| POPX `physarum.Constraintvolume` is a **TOP**, not a SOP/POP. Bright pixels = allowed growth, dark = blocked. Wiring a sphereSOP causes GLSL compile errors in physarum's internal `3d/distance` shader. For 3D simulation true sphere-shell constraint requires a 3D texture (3D SDF); for 2D simulation a circle TOP works directly | 1 | No |
| POPX `DLA` requires a **seed POP wired to input[0]** for aggregation to start. Without seed, walkers wander but never aggregate (output[0] still emits 5000+ random walkers). With seed, output[0] = aggregated tree, output[1] = lines (parent-child), output[2] = random walkers | 1 | No |
| `circleSOP` parameter is `divs`, NOT `divisions`. Tripped at every assumed name | 1 | No |
| `sweepSOP` output through `geometryCOMP` → `renderTOP` produces nothing visible despite render flags set on the inSOP — even when sweep has 12-24k points and constantMAT is assigned. Mechanism unclear; likely related to the same POP-attribute incompatibility that blocks instancing | 1 | No |
| **POPX attribute screening — the de-risk method for any new POPX module.** Place a copy from `/POPX_1_3_0/custom_operators/<name>`, wire minimum inputs, Init→Start→Play, then `print([a.name for a in op('<mod>/POPX_out1').pointAttributes])`. **Safe (clean attrs):** SA, magnetize. **Unsafe (rich attrs):** DLA (`iNumChildren, Parent, Seed, Rand`), Particle (`PartId, PartForce, PrevP, Density, ...`17 attrs), DLG (line topology, `Parent, Seed`). Unsafe modules will trip `geometryCOMP` instancing wall ("Manual number of instances not supported with point co[lor]") — pivot to TOP-output modules (Flow, physarum, Voxelize) or decoupled architecture (POPX provides force field, native particlePOP holds clean attrs) | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **wireframeSOP output cannot be instanced via geometryCOMP directly** — only 1 instance renders even when numinstances reads correctly (e.g. 80). The wireframe topology (line-derived extruded thin tubes) breaks instancing. **Fix:** insert a `convertSOP` with `totype='poly'` AFTER the wireframeSOP, render the convertSOP output instead. The polygonization normalizes topology so geo COMP can multiply instances. Pattern: `boxSOP (render=False) → wireframeSOP (radius=X) → convertSOP totype='poly' (render=True) → instanced` | 1 | No |
| **TD has no native chromatic-aberration TOP.** `lensdistortTOP` is geometric distortion only (k1/k2/k3 coefficients, no RGB split). Manual CA chain: 3 `levelTOP`s to isolate channels (red: `highg=highb=0`, green: `highr=highb=0`, blue: `highr=highg=0`), 2 `transformTOP`s to offset R and B opposite directions (G stays center), 2 `compositeTOP add` blends to recompose. ~7 ops total | 1 | No |
| ~~**feedbackTOP requires BOTH `par.top` set AND target wired to `input[0]`** per TD's SHOT note. The "cook dependency loop detected" warning is cosmetic — feedback works at 60fps.~~ **SUPERSEDED →** see canonical feedbackTOP wiring entry below — the loop warning is NOT always cosmetic; target-on-input[0] is the circular reference that triggers it | 1 | Superseded |
| **hsvadjustTOP hue rotation has no effect on pure white (or pure black).** `hueoffset` only shifts saturated colors. Pure white (R=G=B=1, saturation=0) stays white regardless of hueoffset value. To use hue rotation on a "white" wireframe visual: tint the constant material slightly first (e.g. electric cyan 0.2/0.7/1.0), then hue rotation cycles through spectrum | 1 | No |
| **Sawtooth scale pulses have visible snap-back.** Expression `baseline + (t*rate) % range` gives continuous outward growth but the boundary snap (max → min) is jarringly visible to viewers. Use smooth sin instead: `baseline + amp * sin(t * 2π / period)` for hypnotic breathing. Trade-off: alternates "coming toward / going away" instead of continuous outward, but no discontinuity | 1 | No |
| **Inside-POV camera setup for immersive POV:** `Camradius=0.1, Camfov=80, Camelev=0` puts camera at center of particle cloud (≤0.5 unit cluster) with wide-angle perspective; particles surround camera, geometry passes through frame as scale-pulse animation breathes. Default ctrl_master `Camradius.min` clamp at 0.5 blocks this — must lower to 0 to allow inside-POV configs | 1 | No |
| ~~**compositeTOP `over` input order is empirically opaque** — verify empirically each use; if mask isn't covering, toggle swaporder~~ **SUPERSEDED →** by the canonical swaporder entry below: with `swaporder=False` (default), input 0 is on top; always set `swaporder=True` for intuitive wiring | 1 | Superseded |
| **circleTOP `centerx/y` with `centerunit=fraction` is an OFFSET from the justify-anchor, NOT an absolute position.** With default `justifyh/v=center`, `centerx=0, centery=0` puts the circle at frame center. Setting `0.5, 0.5` shifts the circle by half-resolution in each axis (lands in upper-right corner). Same applies to `pixels` mode — center coords are offsets from the justify anchor. Default is 0,0 — leave alone unless deliberately offsetting | 1 | No |
| **circleTOP `radiusunit=fraction` is ANISOTROPIC on non-square frames.** `radiusx` is fraction of width, `radiusy` is fraction of height. On 720×1280, the same numeric value yields a tall oval (e.g. 0.3 → 216px×384px). Use `fractionaspect` (default) or `pixels` for a true circle. `fraction` is for when you want axis-independent scaling | 1 | No |
| **circleTOP `premultrgbbyalpha=True` (default) can make small or partially transparent circles invisible in `over` composites.** Tested: 200px white circle dead-center + premult=True + composite over iris = visible. 22px-50px white circles or alpha < 1 + premult=True = invisible despite standalone render showing the circle correctly. Setting `premultrgbbyalpha=False` makes them composite as expected. Worth defaulting to False for circles used as composite layers | 1 | No |
| **TD param expressions use the `math` module — bare `sin()`/`cos()`/`pi` are NOT in the expression namespace.** Common pattern for time-driven oscillation: `<base> + <amp> * math.sin(absTime.seconds * 2 * math.pi * <freq_hz>)`. Bare `sin()` raises `NameError: name 'sin' is not defined` | 1 | No |
| **`noiseTOP.par.type='randomgpu'` outputs centered at 0.5 (mid-gray), not 0.** Causes the noise to be the IDENTITY for `overlay` blend (overlay against mid-gray = no change). To use randomgpu as TV-static-style ADD overlay: set `par.amp = 2*range`, `par.offset = -range` to recenter to ±range, then composite with `add` blend. Or switch to `simplex2d` (centered at 0 by default) for overlay-blend use cases. | 1 | No |
| **`mathCHOP.par.chanop` (combine channels within an input) vs `par.chopop` (combine multiple inputs).** Confusingly named. `chopop=average` averages multiple inputs together but keeps original channel count. `chanop=average` averages channels within a single input, collapsing N→1. For stereo→mono on a single input, use `chanop=average` and `chopop=off`. | 1 | No |
| **`levelTOP.par.opacity` only modulates ALPHA — does NOT modulate RGB.** When fading out under `max` blend (which only looks at RGB), opacity has no visible effect. To fade RGB in/out for max-blend chains, use `par.outhigh` (output range max) — set to a value 0-1 to scale RGB output by that amount. Pattern for energy-scaled fade: `outhigh.expr = 'op("ctrl").par.SomeAmp * op("ctrl").par.Energy'`. | 1 | No |
| **CANONICAL feedbackTOP wiring** — the cook-dependency-loop warning is NOT cosmetic — it CAN block cooking. Symptoms: feedback chain ops report 128×128 resolution despite explicit custom resolution; warnings persist. Fix: wire `input[0]` to FRESH CONTENT upstream of the loop (e.g. the lookup feeding the comp), use `par.top = comp` for the loop reference. Then pulse `feedbackTOP.par.resetpulse` once to apply the configured resolution (feedbackTOP defaults to 128×128 and caches old res). The earlier rules saying "wire target to input[0]" create the circular reference that triggers this — both marked superseded above. This entry resolves 3 conflicting feedback-wiring entries. | **3** (resolved 06-10) | **✅ PROMOTED** (06-10; verified 2026-06-12) |
| **For `transformTOP` to fit a portrait source (720×1280) into a square output (720×720) WITHOUT squishing, use a TWO-STAGE pre-crop:** stage 1 — transformTOP with output 720×720, `sx=1, sy=source_aspect (1.778 for 9:16)` to render full source height extending beyond canvas (auto-cropped at top/bottom by `extend=zero`). Stage 2 — second transformTOP scales/positions the now-square content into final layout. Single-stage with custom sx/sy in the position transform doesn't preserve aspect because content extending beyond cell bounds bleeds into adjacent cells. | 1 | No |
| **`selectCHOP` with `par.channames` selects channels by NAME PATTERN (not index).** For first channel of unknown stereo audio, use `par.channames='chan1'` (the conventional channel name from audiofileinCHOP). Patterns like `'*[0]'` (index syntax) don't work. | 1 | No |
| **mathCHOP `chopop` (inter-CHOP per-channel math) vs `chanop` (intra-CHOP collapse) — easy to confuse, breaks SILENTLY.** When you wire two same-shape CHOPs into a mathCHOP and want per-channel multiply (e.g. `iris × scale_per_band`), set `chopop='mul'`. Setting `chanop='mul'` instead does intra-CHOP combine and produces wrong/empty output with no visible error — the chain just outputs scale constants directly. Already in tracker as entry 92, but bumping count. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **Cross-COMP CHOP wiring fails silently — the `outputConnectors[0].connect()` call from inside a COMP to outside it APPEARS to succeed but the connection list reads empty afterward.** Workaround: use `selectCHOP` with absolute path (`par.chop='/project1/comp/inner_chop'`). Already entry 55; bumping count. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **`null_audio` (analysis-chain output, 60Hz timeslice rate) is NOT 44100Hz, blocks moviefileoutTOP audio export with "Audio CHOP sample rate must be 44100" error.** Workaround: wire `record_out.par.audiochop` to `audio_master/audio_in` (raw 44100Hz stereo) instead of any analysis-chain CHOP. Already entry 32; bumping count. | **3** | **✅ PROMOTED** (verified 2026-06-12) |
| **TD `td_execute_python` exec environment scoping is fragile — list comprehensions, generator expressions, AND nested function definitions all fail to capture outer-scope names with `NameError: name 'X' is not defined`.** Already entry 45 for list comprehensions; same failure mode for nested defs (`def fn(): use_outer_var`). Workaround: explicit for-loops, capture references locally inside the function body. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **`bloomTOP` is the canonical HDR-feel post — `output='inputplusbloom'` adds the bloom result back onto the source.** Settings for "luminous painterly" register: `bloomthreshold=0.4-0.55` (lower = more pixels glow), `bloomintensity=0.7-1.1`, `maxbloomradius=0.15-0.25`, `bloomscurve=0.7-0.85` (punchier shape), `pregamma=1.0-1.1` (boost mids before bloom). Combine with crushed-blacks levelTOP (`inlow=0.05`, `inhigh=0.92`, `gamma1=0.92`, `contrast=1.18`) for the "burning embers" cusp 4→5 look. | 1 | No |
| **Phase-animated palette lookup pattern for cyclic color shifts:** `palette_keys` (tableDAT, horizontal stops) → `palette_ramp` (rampTOP type='horizontal', 256×1) → `xform_palette_phase` (transformTOP, `tx.expr=phase % 1.0`, `extend='repeat'`) → `lookup_color` (lookupTOP). Phase comes from `chop_color_speed` (constantCHOP, value = audio-driven cycle rate) → `chop_color_phase` (speedCHOP, integrates over time). The phase shift "scrolls" the palette so iris luminance maps to a moving point in the cycle. | 1 | No |
| **`speedCHOP` integrates a dynamic input value over time** — essential for audio-reactive rotation/phase that ACCUMULATES smoothly. Without it, multiplying `absTime.seconds × current_speed` re-multiplies past time by the new speed (jumping). Pattern: `constantCHOP` (with `const0value.expr` = audio-driven speed) → `speedCHOP` → output is cumulative angle/phase. Bind `xform.par.rotate.expr = "op('integrator')['speed']"` for smooth accumulating rotation; negate the binding (`-...`) to flip direction without changing the integrator. | 1 | No |
| **`feedbackTOP` ghost-trails via OVER blend (vs max blend "light writing"):** for proper translucent past-frame overlap, use `compositeTOP operand='over' swaporder=True` AND scale BOTH `outhigh` (RGB) AND `opacity` (alpha) on the feedback decay levelTOP via the same expression. With `over` blend the past frame fades as a translucent layer over current. With max blend (entry 93's pattern) it accumulates as light-writing trails. Different effect, different feel — pick by intent. | 1 | No |
| **TableDAT cell backtick syntax does NOT auto-evaluate** — writing `\`op('ctrl').par.X\`` into a cell stores the string literally, breaks downstream consumers (e.g. rampTOP keys read invalid position). For dynamic cell values driven by params, create a `parameterexecuteDAT` (`par.op` = ctrl COMP, `par.pars` = space-separated param names, `par.valuechange=True`) with an `onValueChange` callback that writes literal float values into the cells when params change. | 1 | No |
| **`circleTOP` background transparency param is `bgalpha`, NOT `bgcolora`** (despite the per-channel `bgcolorr/g/b` naming pattern that suggests it). Setting `bgcolora` raises `tdAttributeError`. Use `bgalpha=0` for transparent surround on overlay-style circles. | 1 | No |
| **Per-channel CHOP normalization architecture — when audio analysis bands have wildly different dynamic ranges (sub_bass overshoots 1.0, mid/high are squished to 0-0.3), normalize before mapping to visuals.** Chain: `chop_audio_in` (selectCHOP from analysis output) → `chop_norm_sub` (mathCHOP `chopop='sub'`, second input = `chop_norm_floors` constantCHOP with per-channel DC offsets) → `chop_norm_mul` (mathCHOP `chopop='mul'`, second input = `chop_norm_scales` constantCHOP with per-channel scale factors = 1/p99 from recordCHOP statistical analysis) → `limitCHOP` (clamp 0-1) → `chop_norm_out`. Now every channel uses the full 0-1 range. | 1 | No |
| **Designer-friendly TD keyframe system without animationCOMP — table-driven approach:** `tableDAT keys` with rows `time(s) | value | curve` (curve string: `linear`/`smooth`/`ease-in`/`ease-out`). `textDAT module` with `get(t)` function that reads the table, sorts by time, finds bracketing keyframes, applies the named curve to interpolation alpha. Param expression: `mod('module_name').get(song_time) + breath_modulation`. Curve fns: `linear` = a, `smooth` = a*a*(3-2*a) (smoothstep), `ease-in` = a*a, `ease-out` = 1-(1-a)*(1-a). | 1 | No |
| **Containers don't have a `.find()` method** — `containerCOMP.find(name=pattern)` raises `tdAttributeError`. Use explicit iteration: `for c in container.children: if predicate(c): ...`. | 1 | No |
| **`audiofileinCHOP.par.indexunit` defaults to `'seconds'`** — `par.index.eval()` directly returns current playback time in seconds. Don't divide by `par.rate.eval()` — that gives nonsensical values. Use `op('audio_in').par.index.eval()` directly as song-time reference for time-driven keyframe interpolation. | 1 | No |
| **TD's `non-realtime mode` engages automatically when recording starts** — TD renders every frame without skipping for clean output. Audio playback during this mode produces clicks/glitches because audio devices can't keep pace with cooked-frame rate. Already entry 70; bumping count. The mode auto-flips back when recording ends. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **rampTOP `fitaspect='fitvert'` makes radial/circular ramps truly circular on portrait canvases** — by default (`fitaspect='fithorz'`), the ramp's radius=1 maps to half-width on a portrait canvas, making the "circle" elliptical-shaped vs the canvas. Use `fitvert` to anchor the radius reference to the longer dimension for true circular vignettes. | 1 | No |
| **`compositeTOP operand='over'` with `swaporder=False` (default) puts INPUT 0 on top of input 1** — opposite of what TD docs imply. Cost 3 iterations of chasing wrong cause (lookup method, ramp config, channel mode) before tracing the actual chain. Half-documented at 2026-05-04, definitively confirmed at 2026-05-23. CANONICAL FIX: always set `comp.par.swaporder = True` when wiring "input 0 = bottom, input 1 = top" — matches intuition, prevents the trap. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **`layoutTOP` (and likely other multi-input TOPs) auto-compact input connectors on `.disconnect()`** — if you disconnect input 0, input 1 silently shifts to input 0, input 2 shifts to input 1, leaving input 2 empty. Bit me 4× in one session — every layout-input rewire dropped sel_mid or sel_bot. CANONICAL FIX: when changing ANY input on a multi-input TOP, disconnect ALL inputs first, then explicitly re-wire all of them in order. Never partial-disconnect. | **2** | **✅ PROMOTED** (verified 2026-06-12) |
| **`baseCOMP` can't be passed directly to `targetop.inputConnectors[N].connect(basecomp)`** — raises "Invalid number or type of arguments." Must pass the specific output connector: `targetop.inputConnectors[N].connect(basecomp.outputConnectors[0])`. The output index corresponds to the `outTOP1`, `outTOP2`, etc inside the baseCOMP. | 1 | No |
| **`lookupTOP par.channel` defaults to `'independent'` (per-channel R/G/B independent lookup)** — produces weak recoloring because each channel of the source samples the ramp at its own value, often landing near original. For strong tonal remap (dark→low ramp, bright→high ramp), set `par.channel = 'luminance'`. Also confirm `par.darkuv1=0` / `par.lightuv1=1` with `darkuvunit/lightuvunit='fraction'` for full-range mapping. | 1 | No |
| **`edgeTOP par.alphaoutputmenu` defaults to `'edge'`** — non-edge areas output alpha=0 (transparent), causing background to show as TD's checkerboard transparency indicator instead of solid color. To force solid black (or whatever bg color) behind the edges, set `par.alphaoutputmenu='one'` (forces alpha=1 everywhere). | 1 | No |
| **`transformTOP` rotation is `par.rotate` (single 2D rotation value), NOT `par.r`** — par.r is the tuplet GROUP namespace (xyz rotation triplet for COMPs) and doesn't exist on transformTOP. Setting `par.r.expr` raises `tdAttributeError`. | 1 | No |
| **TD `Save As` preserves relative-path STRINGS verbatim but the relative origin moves to the NEW .toe location** — silently breaks all file references stored as relative paths (moviefileinTOP, audiofileinCHOP, custom assets). The errors are clear once you check (File not found in error log) but the breakage is invisible at save time. Either: (a) repoint to absolute paths after Save As, (b) keep assets INSIDE the project folder and use simple relative refs, (c) compute new relative paths from `project.folder` after the Save As. | 1 | No |
| **TD parameter expression `..` walks up ONE level to the parent COMP**, not the operator itself. From `xform` inside `base_psy` at `/project1/base_psy/xform`: `op('../ctrl_master')` resolves to `/project1/ctrl_master` (parent of base_psy). NOT `op('../..')` — that overshoots to `/` (root) and `op('../../ctrl_master')` returns None. Rule: count levels from the EXPRESSION'S OWNER's PARENT, not the owner itself. | 1 | No |
| **randomPOP/noisePOP `combineattrscope` defaults to `'P'`** — with `combineop='mult'/'add'` the generated value combines with POSITION (signed!), not your target attr. Symptom: ScaleRand went −1.77..2.07 (expected 0.3..1.96). Always set `combineattrscope` to the target attr explicitly when using mult/add combineop. | 1 (06-12) | No |
| **depthTOP calibration: grid-sample the depth pass, never derive the rerange window from camera dials.** Mass sat at cameraspace 3.5–4.7 while Camradius implied ~1.9 (geo transforms shift it); unclamped void sampled 2924. Set `depthspace='reranged'` + `clamp=True`, then sample a 7×7 grid and fit rangefrom to the observed mass span. | 1 (06-12) | No |
| **`appendFloat()` returns a ParGroup, not a Par** — `pg.par.normMin` raises `AttributeError: 'td.ParGroup' object has no attribute 'par'`. Index it: `pg[0].normMin / .normMax / .default`. | 1 (06-12) | No |
| **td_write_dat module replace causes a ONE-COOK transient TypeError** in dependent par exprs (old bytecode evaluates against the new module once, e.g. "cycle() takes 3 positional arguments but 4 were given" when neither side passes 4). Self-clears next cook — re-check errors fresh before chasing it. | 1 (06-12) | No |
| **levelTOP Pre page (invert/gamma) applies BEFORE the Range remap (inlow/inhigh→outlow/outhigh)** — exploitable: invert depth then set `inhigh = 1−start` to build a windowed far-fog mask with clean near-clamp in one op. | 1 (06-12) | No |
| **Audio power curves above ~1.2 crush gentle-register modulation.** `pow(x, 2.5-3.0)` is right for punchy drops (flattens breakdown rumble, passes peaks) but kills audio response entirely on gentle material (Act 1/5) where typical band values sit low. Pair with the record-first workflow: record the song through rec_audio, check TYPICAL values (percentiles, not just peaks), normalize to p95, THEN choose the curve. Hit in 04-16 (base_act2_underwater: dead audio response at gentle values) and 05-23 (down_bad_3stack: "weakly driven"). | **2** (04-16, 05-23; tracked 06-10) | **✅ PROMOTED** (06-10; verified 2026-06-12) |

---

## Build Sessions

---

### 2026-06-12 — sa_1 (crease_sa) — full system session: post chain + SACRAMENT + bar-clock color + variation + lens + void — v001 SAVED, Nick "really liking this"

**What was built (18 moves, all on existing crease_sa Aizawa-mirror base):**
(1) **Post chain realism:** manual full-frame bloom (blur32/level/screen) → native `bloom_post` (inputplusbloom, threshold 0.5 — only embers/speculars glow); `level_grade` + `hsv_grade` tone stage (Cineblacks/Cinegamma/Cinecontrast/Cinesat dials); soft2d shadows on light1 + light_back, casters=geo_attractor. (2) **SACRAMENT color register** (song theme: psychedelic trip processing religious trauma — communion wine + tarnished gilt + pewter lucidity edge): palette_lights rewritten twice — first free-running 4-stop SACRAMENT, then **bar-clocked 12-stop block lists** (WINE/GILT/LUCID/COMMUNION × 3 stops, 8 bars/block at 140 BPM, `cycle(channel, t, comp)` reads Bpm/Blockbars/Barstart from ctrl, lerps continuously through block boundaries). Orb albedo + mat rim joined the cycle after diagnosing **Metallic=1.0 tint-lock** (full metal = no diffuse; all color = reflections tinted by static albedo). Post-level mega-ramp sliding-window lookup also built (verified by TOP.sample window math) — now DORMANT at Colormix=0 after Nick moved color into the lights. (3) **Instance variation:** product-distribution sizes (`random_scale2` mult, 25% small/9% large); **render branch outside the SA feedback loop** (`null_pop_out → noise_wobble → noise_breath → null_render_out`, instanceop repointed — solver/centroid stay on clean null) for perlin4d positional wobble + per-particle size breathing. (4) **Audio:** light orbits on integrated energy (`ctrl_orbit_speed → speedCHOP → null_orbit`, period ratios preserved); block-arrival bloom pulse (exp decay off bar clock); ember rim strength on sub (curve 1.1). (5) **Lens stack:** depth-driven lumablur DOF (settled at deep-focus 3px/1.0 after 3 dial-down rounds), back-third depth fog (`Fogstart` 0.6 windowed mask), highlight shoulder (outhigh 0.85), camera micro-drift (incommensurate sin sums). (6) **Living void bg** (Nick's spec via direct ask: eyes-closed darkness + enclosed room, "felt but quiet"): macro simplex room-drift + micro grain → SACRAMENT dark-ramp lookup (palette-locked), 3–7% post-grade violet lift. ctrl_master grew ~25 dials across Post/Color/Camera/Material/Form/Lighting/Composition pages.

**First-pass-right:** speedCHOP integration pattern (promoted rule reapplied clean); `Base + React × pow(clamp,curve)` template throughout; MAT child-COMP absolute paths; 16-bit ramps; swaporder=True; feedback-loop danger correctly identified BEFORE building variation (render-branch architecture, no smeared trajectories); window math verified by sampling before wiring; promotion-pipeline + brand-check + close-out skills all ran first-time clean.

**Corrections against the agent:** randomPOP `combineattrscope` default 'P' multiplied random×position (caught by stats check, fixed same move); depthTOP rerange first guess derived from Camradius was wrong by ~2× (grid-sampling found mass at 3.5–4.7); appendFloat ParGroup-not-Par AttributeError; one-cook transient TypeError after td_write_dat module swap (chased briefly); CA default 2px → 1px (every point-source ember doubled — anaglyph read). Taste corrections from Nick (pattern: **start atmospherics subtle — every atmospheric default I picked got dialed DOWN**): Wobbleamp 0.008→0.004 (silhouette scatter), DOF 10px/6 → 3px/1.0 over three rounds ("basically everything in focus"), fog 0.35→0.2→0.1→restructured to back-third-only at 0.2.

**WOBAR craft (Nick-reviewed):** brand-check scored the base 8/10 Act 3 pre-session (Rorschach crease = most literal mirror-encounter realization; clustered-orb texture passes "hard to look at"). Theme drove color: SACRAMENT = wine/gilt/pewter mapped to body/ritual/waking — affinity rule "warmth must disturb" executed via corroded votive gilt. Block structure = song structure (8 bars), color became composition. Nick's repeated correction direction = restraint on lens/atmosphere; "hypnotic but not psychedelic yet" resolved by COLOR MOTION (bar-clock blocks), not more FX. Void spec gathered by asking (eyes-closed + enclosed room) rather than inventing. Still open: Barstart alignment to track, full-song held-tension watch, emergent-figuration watch, Dreamhaze (needs realization timestamp), mirror-flaw idea (pitched 3×, not taken — drop unless Nick raises). Cleanup debt: dormant lookup chain, `bg_black`, `Basecolor` dials, `Paletteperiodscale`.

---

### 2026-05-23 — down_bad_3stack v001 — music-video stacked composite + 3 reusable psychedelic treatments + ctrl_master (audio NOT wired) AND mercury_womb paused

**What was built:**
Two networks touched this session.

**Primary: `down_bad_3stack` v001** — full network at `touchdesigner/networks/down_bad_3stack/down_bad_3_stack.toe` for the Down Bad remix (Dreamville / J Cole, Act 4 Phase 1 register). 720×1280 portrait 3-cell vertical stack of the source music video.

Architecture: `movie_in` (moviefileinTOP 1280×720 source, renamed from auto-generated `YTDown_YouTube_...` name) → 3 selectTOPs (`sel_top`, `sel_mid`, `sel_bot`, all `par.top='movie_in'`, zero-copy texture refs) → each through its own reusable treatment baseCOMP → `layout_stack` (layoutTOP, `align='verttb'`, `maxcols=1`, `maxrows=3`, `scaleres=True`, `fit='fitoutside'`, 720×1280 output) → `null_out`.

Three reusable treatment baseCOMPs built, each with internal `in1` (inTOP) / `out1` (outTOP) connectors and `../ctrl_master` relative-path expression bindings:

- `base_color` (on TOP cell): palette LOOKUP psychedelic. Internal: `in1 → lookup ← ramp_palette (rampTOP horizontal 1024×1 rgba16float, 6-stop WOBAR ramp: dark purple → mauve → bronze patina → magenta → tarnished bone → pale bone) → level_mix (alpha=Colormix) → comp_mix (over, `swaporder=True`) → out1`. ctrl_master Color page: `Colorphase`, `Colorcycle` (Hz auto-shift), `Colormix` (0-1 clean↔treated crossfade). lookup `channel='luminance'` for strong tonal remap.

- `base_psy` (on MIDDLE cell): FEEDBACK ECHO psychedelic. Internal: `seed (constantTOP, black 1280×720 rgba16float) → fb (feedbackTOP, par.top='out1') → xform (transformTOP, sx/sy/rotate/tx/ty bound to ctrl_master) → level (opacity bound to ctrl_master) → comp (over, sel_top into input 1) → out1`. ctrl_master Top Echo page: `Echoexpand`, `Echoopacity`, `Echorotate`, `Echodriftx`, `Echodrifty`.

- `base_edge` (on BOTTOM cell): EDGE DETECTION psychedelic. Internal: `in1 → edge_detect (edgeTOP, select='luminance', combineinput='edgeonly', alphaoutputmenu='one' for solid black bg) → out1`. ctrl_master Edge page: `Edgestrength`, `Edgeblack`, `EdgecolorRGB`. Currently white edges on black; flagged for "never pure white" fix.

Layout went left-to-right per "always organized" rule: movie_in (0,0) → sel_* (200, ±100/0) → base_* (400, ±100/0) → layout_stack (600,0) → null_out (800,0). ctrl_master baseCOMP at /project1 with 3 pages × 11 custom params.

Mid-session swap: top↔middle cells (base_color now on top, base_psy on middle) for stronger visual rhythm (legible → kinetic → graphic instead of kinetic → legible → graphic).

Nick saved as `down_bad_3_stack.1.toe` in workspace folder — relative file paths broke; repointed `movie_in` and `down_bad_remix_v2_2` audiofileinCHOP to absolute paths.

**Brand check against `WOBAR_EMOTIONAL_REGISTER.md` Act 4 Phase 1 — composition strong, register FAILED:**
- ✓ Mirror/encounter structure (3 cells = recursive recognition)
- ✓ Middle palette recolor is brand-pure WOBAR foundation
- ✓ Format and restraint on-brand
- ❌ **NO AUDIO REACTIVITY WIRED** — violates the explicit failure criterion "the body cannot discharge in still water"
- ❌ Pure-white edge color violates `WOBAR_BRAND.md` "Pale/bone highlights — never pure white"
- ❌ Top cell feedback runs on raw saturated source colors instead of pre-desat WOBAR range

NEXT (logged on the active loop): wire bass→Echoopacity + kick→Edgestrength to land Act 4 register; replace pure white with bone/ash; pre-desat top cell source.

**Secondary: `mercury_womb` v001 PAUSED** — the original direction for the Down Bad visualizer (inside-a-mercury-chamber world building). 12 moves built (tube + noise displacement + PBR mercury MAT + HDR env light + breath/flow animation + ctrl_master setup) before TD locked up mid-session on PBR shader recompile + IBL regen. Nick reset TD, pivoted to the stacked-music-video approach. Mercury_womb plan + move JSONs preserved; loop moved to `WOBAR_CLOSED.md` with full architecture/learnings captured for potential resumption.

**What the agent got right first pass:**
- 3-cell stack architecture chose layoutTOP from the start (right primitive, vs manual transformTOP composite)
- Treatment baseCOMPs designed with in1/out1 from the start (reusable pattern, drops in anywhere)
- Brand check raised concerns proactively when asked (didn't just rubber-stamp visible quality)

**What needed correction:**
- compositeTOP swaporder trap bit again — chased 3 wrong causes before tracing the actual chain
- layoutTOP input compaction bit 4× — every rewire needed re-asserting all 3 inputs
- baseCOMP.outputConnectors[0] syntax for downstream wiring (not directly passing baseCOMP)
- transformTOP rotation is par.rotate not par.r
- lookupTOP par.channel='independent' default produces weak recolor
- edgeTOP alphaoutputmenu='edge' default makes non-edges transparent
- Relative path `..` depth: from xform inside base_psy, `../ctrl_master` (one level) is correct — `../..` overshoots
- Save As broke relative file paths (TD preserves the string but origin moves)

**New patterns/conventions:**
- **Reusable treatment baseCOMP pattern** — `in1 (inTOP) → [chain] → out1 (outTOP)`, all internal bindings use `../ctrl_master.par.X` for portable param access. Wire externally as `source.connectTo(comp.input[0])` and `next.input[0].connect(comp.outputConnectors[0])`. Drop new instances anywhere, copy via `parent.copy(source, name='...')`.
- **selectTOP for zero-copy multi-instance reads** — one source video → 3 selectTOPs all pointing at it via `par.top='source_name'` (sibling bare name). No memory cost for N references. Layout-friendly visual fan-out.
- **layoutTOP for grid stacks** — `align='verttb'/'horizlr'`, `maxcols/maxrows` to force grid shape, `scaleres=True` to make cells derive from output/grid (not from input dims), `fit='fitoutside'` to fill cells with crop. Set borders to 0 for seamless stacking.

**Open loops carried forward:**
- down_bad_3stack v001: audio reactivity wire-up + brand fixes (pure white, top cell desat) before this can ship for Act 4 register.

Network at `touchdesigner/networks/down_bad_3stack/`. 14 move JSONs in `moves/`. Source files: video at `touchdesigner/networks/down_bad/music_video_treatment/...mp4`, audio at `~/Desktop/Music/wobar/down_bad_remix_v2 2.mp3`.

---


### Older sessions

Sessions from 2026-05-06 and earlier moved to `working/TD_BUILD_LOG_ARCHIVE.md` (2026-06-10). Their correction counts are already reflected in the Correction Tracker above.
