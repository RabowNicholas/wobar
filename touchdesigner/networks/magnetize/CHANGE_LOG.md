# CHANGE LOG — magnetize

Act 4 RELEASE (Phase 1, physical discharge) visualizer. Built by tweaking the POPX `magnetize` example into a discharge skin: a field of instances detonated outward by a single central repel pole on each kick, reassembling between hits. Working name `magnetize`; renames to a song-specific name (`shatter_break` candidate) once the track lands.

**Engine:** POPX Magnetize (`/example/magnetize1`), Solvermode=simple (stateless). Magnet pole sourced from `pointgen1 → attribute1 → noise1` (per-magnet `mode`/`strength`/`radius` attributes). Discharge driven by `ctrl_blast` Constant CHOP via a beat-pulse strength envelope.

**Platform note:** Requires TD 2025.32820 (POPX 1.4.0's target build). On 2025.32460 the POPX core POP-GLSL shaders (`applyatt/apply`, Instancer compute) fail to compile on Metal — TD was upgraded 2026-06-08 to fix this. SSFR and live Voronoi (Explode) remain Vulkan-locked / Metal-incompatible and were ruled out during concept exploration.

---

## move_001 — discharge mechanic (2026-06-08)

Reconfigured the example's 5 spin poles into one centered repel pole with a pulsing blast envelope.

- `pointgen1`: 5 random points → 1 centered point (numpoints=1, random off, size 0).
- `attribute1`: per-magnet `mode` 2 (spin) → 1 (repulse); `strength` → expression blast envelope `Force * exp(-((t·Bpm/60/Div) % 1)·Decay)` off `ctrl_blast`; `radius` → `ctrl_blast['Radius']`.
- `noise1`: bypassed (pole stays centered, no jitter).
- `magnetize1`: `Searchradius` → `ctrl_blast['Radius']`; `Solvermode` advect → **simple** (stateless = envelope-synced reassemble); `Displaymagnets` off.
- New `ctrl_blast` Constant CHOP: Force=3.0, Bpm=140, Div=2 (halftime), Decay=6, Radius=1.5.

Verified: strength oscillates 0.01 → 2.5 → 0.01 over a 0.857s period (sharp attack, exp decay, halftime spacing); field detonates radially outward at the spike and relaxes to even between hits. Rainbow velocity coloring (color_modifier1) and wide landscape framing are placeholders — addressed in later moves (slab reframe, reflective shards, post).

---

## move_002 — portrait full-bleed mirror slab + Z-thrust (2026-06-08)

Reframed the instance field into the mirror slab (the slab IS the field's rest state).

- `instancer1/Distribution/grid`: 100×50 landscape → **66×112 portrait**, extent 2.0×1.0 → **2.4×4.0** (overflows the frame = full-bleed). ~7400 instances.
- `render1`: 1080×1080 → **720×1280** portrait.
- Z-thrust ("shards burst toward viewer"): added `Depth` channel to `ctrl_blast` (0.6); offset the repel pole along the slab's depth axis via `pointgen1.ty` = `ctrl_blast['Depth']` so the pole sits behind the slab and pushes shards off the surface.

Axis calibration (empirical): `Gridx`/`Size1` = screen-horizontal, `Gridz`/`Size3` = screen-vertical, **`ty` = depth** (toward/away camera; keeps blast screen-centered). Z-thrust sign/magnitude + density read deferred to Move 3 — can't be judged on the box-dot velocity viz; needs real shard geometry + live motion. Camera unchanged (z=-2.5, fov45, horizontal fov → visible ~2.1w×3.7h at slab).

---

## move_003 — obsidian shards (2026-06-08)

Skinned the field as **black obsidian glass** (the chosen mirror character).

- `box1`: flattened `sizey` 1.0 → 0.05 (flat shard, thin on the Y/depth axis so faces point at camera).
- `instancer1.Globuniscale`: 0.01 → **0.045** — the key fix. At 0.01 the shards were ~28% coverage (sparse dot field); at ~grid-spacing they tile near-solid at rest and separate visibly on the blast.
- New `mat_obsidian` (pbrMAT): basecolor 0.03/0.03/0.04 (near-black, faint cool), metallic 0.5, roughness 0.16, **applypointcolor OFF** (kills the rainbow `color_modifier1` tint at the material level — `color_modifier1` is a COMP and can't be reliably bypassed), cool fresnel rimlight (0.45/0.6/0.95).
- Lighting: `light1` moved from *behind* the slab (tz +2.6 = backlight, no glints) to **camera-side front** (tz −1.8, upper-right, dimmer 4.5). Added `light_fill` (cool point, lower-left, dimmer 3.0). Added `light_fill` to `render1.lights` (render uses an explicit light list, not auto-all).

Reads as a near-black tessellated obsidian surface with bright **spectral glint streaks** where tumbling shards catch the lights; domes forward at peak via the Z-thrust. Intentionally dark (obsidian = most void). Open for live aesthetic tuning (brightness, glint density, material color, Z-thrust magnitude) — Nick directs. Debug axis overlay still present (gone with the clean render path). Move 4 bloom will flare the glints.

---

## move_004 — HDRI environment reflection + kill debug overlay (2026-06-08)

Resolved the **"readable mirror at rest vs obsidian minimal-reflection"** tension: a mirror reads as a mirror by *reflecting*, so gave the black glass a dim environment.

- Killed the debug crosshair — it was `geo1` (the pole gizmo) sitting in `render1.geometry`; render now lists only the shards.
- Wired `ferndale_studio_07_4k.exr` (dark studio HDRI — black field with warm dish / cool tubes / white disc as the bright pools) as `env_obsidian` (environmentlightCOMP), `dimmer=0.25` (deep dim → obsidian, only the bright pools reflect). Source TOP `hdri_env` (moviefilein). Added to `render1.lights` alongside the two hero-glint point lights.
- Dropped the stopgap `emit` floor (0.13 → ~0.012) — the env reflection now carries readability. Raised `metallic` 0.5 → 0.7 so the env reads as glass.

**Result — the full cycle works:** REST = near-black glass reflecting a single cool glow (a flat mirror reflects one coherent source); PEAK = domes forward via the Z-thrust and the reflection **fragments into a spectral spread** (greens/cyans/purples + hot white center) as each tumbling shard catches a different HDRI source. That's the shatter-into-pieces-of-reflected-light / mirror-encounter payoff, reading desat-psychedelic naturally. Still dark pre-bloom (intended). Open tuning: `env_obsidian.dimmer` / `envlightmaprotatey` for more rest-presence, spectral balance, Z-thrust depth. HDRI files live in `touchdesigner/hdri/`.

---

## move_006 — CONCEPT PIVOT: flat-slab discharge → murmuration (2026-06-08)

Recognized that magnetize is a force-**field** engine (flow), not an object/elasticity engine. The vision had drifted toward "a liquid droplet straining to pull away from a surface" — which is Soft Body (elastic/surface-tension) or SPH (fluid, **Metal-dead** — same Vulkan wall as SSFR). Both rejected. Instead leaned **into** magnetize's strength — *"poles that wander and interact."*

**New visual:** a 3D cloud of obsidian shards that **streams and flocks behind 2–3 wandering attract poles** — a murmuration of black glass catching fragmented HDRI light. Hypnotic, Act 2 register. **Keeps** the obsidian shards + HDRI reflection + portrait.

Key changes: instancer flat grid (66×1×112) → **25³ 3D cube cloud** (15,625), Size 1.7³; `pointgen1` 1 centered point → **3 random-volume points**, drift/depth expressions removed; magnet mode repulse → **attract**; strength breath-expr → constant 2.5; `noise1` **un-bypassed** → poles wander organically; `Globuniscale` 0.045 → 0.02 (distinct flock elements); camera tz −2.5 → −5.5 (frame the swarm); **`Solvermode` simple → ADVECT** (stateful momentum = the streaming/flocking motion — the unlock) + Initialize/Start pulsed.

Result: shards stream into swooping flock-lines following the wandering poles. Dark/sparse pre-bloom — **the motion is the payoff (judge live).** Dormant `ctrl_blast` discharge channels (Force/Bpm/Div/Decay) + breath/depth channels remain unused in the CHOP. Moves 001–005 (discharge, slab, obsidian, HDRI, breath) superseded by this direction; the material/HDRI work carries forward. Watch for advect drift/collapse over time (poles may over-gather → add a repel pole or tune Relaxfactor if so).

---

## move_007 — solid black background (2026-06-08)

Built `bg_gradient` (rampTOP radial) + `bg_gradient_keys` (tableDAT) + `comp_bg` (compositeTOP, render OVER bg, swaporder=False so input0=render on top); `out1 ← comp_bg`. Tried a dim deep-purple radial glow first; Nick chose **pure black** → keys set to (0,0,0,1). Gradient infrastructure stays for re-introducing a colored backdrop later. Solid black = correct opaque canvas for bloom.

## move_008 — bloom + brightness + genuine wander + ctrl_master (2026-06-08)

- **Bloom:** `bloom_flock` (bloomTOP, inputplusbloom) after `comp_bg`. Glints too dim to bloom → raised `env_obsidian.dimmer` 0.25 → **2.0** (brighter reflections). Landed on **moderate density (25³) + bright env + bloom = shimmering glinting swarm**; max density (32³) just self-occluded into dark masses, so reverted to 25³.
- **Wander:** `noise1` was static (tx/ty/tz=0) → poles were *fixed* and the advect cloud just pooled toward them. Wired `noise1.tx/tz = absTime*Wanderspeed` (scroll the field = genuine independent pole wander) + `amp0 = Wanderamp`.
- **ctrl_master:** baseCOMP with **18 params, 5 pages** — Flock (Polecount/Polespread/Attract/Radius/Wanderamp/Wanderspeed/Flowrelax), Cloud (Density/Cloudsize/Shardsize), Look (Envbright/Envrotate/Metallic/Roughness), Camera (Camdist), Bloom (Bloomint/Bloomthresh/Bloomradius). 23 target params + 3 noise pars wired via `op('/example/ctrl_master').par.X.eval()`; defaults = dialed-in state. Pre-existing harmless POPXExt sync errors (baked-in Windows dev path) remain.

*(Moves 009–013 — dive system, song-structure choreography, overshoot, orbit→fly-through→straight-dive camera experiments, ctrl_master cleanup — are recorded in their move files; summarized in the v001 checkpoint below.)*

---

### v001 — 2026-06-09 (CHECKPOINT, 13 moves flushed)

STATE: **Murmuration visualizer.** A 3D cloud of POPX-instanced shards (25³ grid → `magnetize` with wandering attract poles, `Solvermode=advect` for flowing flock) reflecting a dark studio HDRI (`ferndale_studio_07_4k.exr`) through an obsidian-ish pbrMAT, bloomed, on pure black. `ctrl_master` control panel (Flock / Cloud / Look / Camera / Bloom). **Dive system:** `dive_keys` tableDAT (`time|value|curve`) + `dive_kfm` module `get(t)` (matches iris_2 `pupil_kfm`) drives a single **Dive 0–1** (0=outside/break, 1=inside/drop); camera distance + elevation + glow (bloom/env) all lerp between dialed inside/outside extremes; `overshoot` (ease-out-back) curve on the dramatic moves; the song structure is keyframed in `dive_keys`. Camera is a straight-Z dive (orbit + fly-through rigs were built, then removed). **Requires TD 2025.32820** (POPX 1.4.0 build-match) — runs on Metal.

KNOWN ISSUES: "enveloped inside the cloud" NOT achieved — the cloud's POP positions measure ±1.8 (camera demonstrably inside) yet it renders as a small central blob (unresolved POPX render-vs-geometry scale mismatch); compounded by obsidian-dark shards making most of the field invisible. Several flock/material params drifted off the "loved murmuration" values during the late-session rabbit hole.

NEXT: per Nick — **strip to a legible base** (flat bright shards, fixed camera, no forces/bloom/HDRI) and **add variation one intentional decision at a time**.

MOVES: 13 flushed.

---

### v002 — 2026-06-09 (CHECKPOINT, 3 moves flushed)

STATE: **Reflective mirror-orb.** A sphere (spherical distribution, geodesic *surface*, Scale 3.5) of distinct flat **reflective facets** — metallic pbrMAT `mat_obsidian` reflecting the `ferndale_studio` HDRI via `env_obsidian` — on pure black, camera front-on (`cameraViewport` tz 9.2, fov 45). Reads as a slow reflective disco-ball / mirror-orb; each facet catches a different slice of the environment (cool blues, warm/white glints). A single wandering magnetize **pole turns the facets toward it** (`magnetize1` Affectrot=on / Affectpos=off / Aimweight 1.0, Mode=attract, advect solver) within a **small reach** (ctrl `Radius` + `Searchradius` = 1.0), so a small cluster of turned facets — a roaming reflection-bloom — drifts across the orb as the pole wanders (`Wanderspeed` 0.3). Debug pole marker (`geo1`, small red sphere via `copy1`/`sphere1`) still in the render for tuning. Dormant: dive system, `mat_flat`, bg gradient, the entire flat-plane build.

**KEY FINDING:** the pole-turn (orientation aim) ONLY works on a **curved** surface — facets must already face different directions for the aim to engage. On a FLAT grid (uniform +Z normals) the magnetize aim produces **zero** orientation change (confirmed exhaustively via the `N`/`Orient` attributes: attract/repulse aim → identity; spin → in-plane rotation only, no reflection change). This killed the "flat mirror + pole ripple" idea; the orb is the resolution.

JOURNEY: stripped v001's murmuration to a legible flat-white base (move_001) → intentional decisions: sphere form (move_002), fine slivers (move_003) → **CONCEPT PIVOT** to "mirror fragments the poles orient" → built a gorgeous full-bleed **flat** reflective mirror (but pole-inert) → discovered the curvature requirement → landed on the **reflective mirror-orb** where the turn-toward-pole effect works. Nick: "i like the orb."

NEXT: tune pole effect (size/strength — currently small), then shape the look (facet density, reflection brightness/HDRI, motion), camera, post. Remove debug marker before final render.

MOVES: 3 flushed (strip, sphere-form, sliver-character; the mirror→orb pivot was live exploration, captured here).

---

### v003 — 2026-06-09 (CHECKPOINT, multi-pole glints)

STATE: Same reflective mirror-orb as v002, with the pole system tuned to **multiple roaming glints**: `Polecount` 1→4, `Polespread` 0→2.5 (poles spread through the orb), `Wanderamp` →2.5, glint `Radius`/`Searchradius` 1.0→**2.0** (bigger blooms). Reads as a slow disco-orb with several broad reflection-blooms drifting independently as the 4 poles wander. Nick: "that is good." NEXT (Nick's call): circle back to the **shards** themselves (facet look — size/shape/density/material).

MOVES: 0 (incremental tune on v002).

---

### v004 — 2026-06-09 (CHECKPOINT, ctrl_master rebuilt + small-square facets)

STATE: Reflective mirror-orb, now with **small square facets** (Nick abandoned the sliver attempt — sliver chaos kept re-aligning into latitude rings because the magnetize/POPX pipeline re-derives orientation from the surface; not worth fighting). box1 = small square plate (Facetsize 0.25, thin). Facets airy with gaps (floating-tile read). Pole-glints (4, roaming) intact. **`ctrl_master` fully rebuilt** into a clean 14-knob panel, all live-wired:
- **Orb:** Orbsize (spherical Scale), Facetsize (box1), Facetcount (geodesic Freq)
- **Glints:** Glintcount (pointgen numpoints), Glintspread (pointgen size), Glintreach (magnet radius + Searchradius), Glintturn (magnetize Aimweight), Roamrange (noise amp), Roamspeed (noise scroll)
- **Look:** Metallic, Roughness, Reflectbright (env dimmer), Envrotate
- **Camera:** Camdist (cameraViewport tz)
- **Glints/Showmarkers** toggle → geo1.render (show/hide the red debug pole spheres)

Removed all dead params (Flowrelax, Density, Cloudsize, Envoutside, Dive/Diveauto/Overshoot/Radiusout/Radiusin/Elevation/Elevationin, Bloom×4); re-connected Metallic/Roughness/Reflectbright which had been silently disconnected (set directly on the ops during the mirror build). Neutralized the orphaned op refs (attribute1 magnet strength, bloom_flock, magnetize Relaxfactor) to constants. No errors.

KNOWN LEFTOVERS: dormant dive system (`dive_kfm`/`dive_keys`) still present but unreferenced — safe to delete. Debug marker now toggleable. Nick: "i like where it is at."

NEXT: continue tuning via the clean panel; eventually material (circle back from "TBD"), motion (orb rotation?), post, song.

---

### v005 — 2026-06-09 (CHECKPOINT, translucent glass + hue-cycle HDRI)

STATE: The orb is now **translucent frosted glass** with a **color-cycling reflection.** Material (mat_obsidian pbrMAT): metallic 0.4, roughness 0.3, smoky cool basecolor (0.08/0.10/0.16), faint cool emit floor, `alphafront`=Opacity(0.5)/`alphaside`=0.9 (fresnel-style: see-through faces, solid edges), `blending`=True; `render1.transparency`=sortedblending. Reads as a delicate see-through crystal cluster catching multi-colored light. **Hue-cycle on the HDRI:** `hdri_env`(4K EXR) → **`env_down`** (resolutionTOP 512×256) → **`hsv_cycle`** (hsvadjustTOP, hueoffset animated `(absTime*Cyclespeed)%360`, saturationmult=Saturation) → `env_obsidian.envlightmap`. Different facets reflect different parts of the shifting HDRI → varied colors at once, all cycling the spectrum. New panel knobs (Look): **Opacity, Cyclespeed (20°/s), Saturation (1.5)**.

PERF FIX (important): animating an environmentlight's map re-bakes its IBL every frame; `envlightmapprefilter='automatic'` cost **142 ms/frame**. Setting **prefilter='off'** + downsampling the source map (env_down 512×256) → **~0 ms, 60 fps**. Tradeoff: reflections slightly sharper (no roughness-blur), fine at this facet size.

Nick: liked through the whole pass ("i like where we are headed"). Saved despite a recurring machine disk-full issue (3rd time tonight).

NEXT: continue tuning (Cyclespeed/Saturation/Opacity), then motion (orb rotation?), post, song. Cleanups still pending: dormant dive system, the (toggleable) debug markers.

---

### v006 — 2026-06-09 (CHECKPOINT — finished Act-2 piece, cleaned + recorder, SHIPPED)

STATE: The finished glass-orb, re-homed to **Act 2 / DESCENSION**. On top of v005:
- **Audio-reactive shell tumble** — `base_audio.smooth_out` bass→outer / mid→mid / high→inner, each band → `spin_speeds` (constantCHOP `base*(1+band*react)`) → `spin_angles` (speedCHOP integral) → geo `rx/ry/rz = angle*Lissajous_ratio % 360`. (Integrated so rotation accelerates smoothly, never jumps.)
- **Drop-gated feedback MELT** — `fb_node/fb_xform/fb_blur/fb_fade/fb_comp` loop; decay = `clamp(0,(energy-Meltgate)*Melt,0.92)` → clean verses, radial dissolve on drops.
- **Cool-color rework** (on-brand Act-2): `Saturation` 0.45 + cool-band hue triangle (cyan→violet, no `sin`) + cool grade tint (highr/g/b) + bloom eased to 0.9. Full-rainbow was off-brand; glass is neutral, color comes from the env.
- **`Postbypass`** A/B (switch_post: full post vs raw render).
- **Cleanup:** removed 10 dead ops (geo1/sphere1/copy1/debug_red, dive_kfm/dive_keys, mat_flat/line1, orbit_speed/orbit_angle) + `Showmarkers` param; reorganized into subsystem bands; 24 node comments + `description` overview DAT.
- **`rec_out`** moviefileoutTOP (NON-COMMERCIAL: `mjpa` .mov + `pcm16` audio from `base_audio/audio_in`, `fps=me.time.rate`). Master recorded → HandBrake.

MOVES: 1 (network cleanup, flushed). Brand-checked → Act 2. **Loop closed.**
NEXT: shipped. (CA deliberately skipped — off-brand psychedelic for Act 2. Future: more Act-2 songs / variations.)
