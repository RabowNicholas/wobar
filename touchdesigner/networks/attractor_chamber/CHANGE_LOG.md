# CHANGE LOG — attractor_chamber

Strange Attractor Chamber — first POPX-on-WOBAR proof. Audio-reactive Aizawa attractor cloud rendered through the new desaturated psychedelic palette.

TD location: `/project1/base_attractor_chamber`

---

## v001 — Abandoned (2026-04-30)

**Status:** rebuilt-from-scratch attempt, abandoned. Network cleared from TD. Move 001 (`moves/move_001.json`) preserved as a record of what was tried + the gotchas surfaced.

**Why abandoned:** rebuilding from the POPX guide turned into a long debug session. Architecture matched the example by the end — but tuning and the FPS-vs-SA-integration loop got bogged down. Nick called it and decided to start from the working `strange_attractors.toe` example file directly and modify from there. Rule 0b (find the closest reference, diff against it) should have been followed from the start.

**Gotchas surfaced (preserved in `moves/move_001.json` and the 2026-04-30 entry of `working/TD_BUILD_LOG.md`):**

1. **`noisePOP.combineop` defaults to combining noise into P** — silently destroys positions. Must set `combineop='none'` when using `noiseoutputattrscope='Rotate'` to leave P alone. This is THE bug that caused the entire SA collapse — `noise_rotate` was supposed to randomize per-instance Rotate attributes but was actually overwriting positions with 360-amplitude noise, sending all 5k points to identical SA-clamped trajectories.
2. **POPX SA `Solvermode='advect'` requires the TD timeline to actually advance** to integrate. `op.cook(force=True)` from Python doesn't progress simulation time. If FPS is 0 (e.g. heavy render chain), SA stays frozen at initial state.
3. **TD 2025 geometryCOMP has 0 input/output connectors** for vanilla geometry — the rendered template comes from CHILD operators inside the COMP. The example's `geo1` had input connectors only because it was built as a POPX-aware geometryCOMP with `inPOP/outPOP` ports.
4. **Camera rotation via `par.ry.expr=absTime*speed` rotates camera in-place** (away from scene), NOT around the scene. To orbit the geometry: set `par.lookat=target` and animate `tx/tz` via sin/cos.
5. **`par.expr` setter doesn't auto-set `par.mode = ParMode.EXPRESSION`** — silent failures if mode stays CONSTANT.
6. **`noiseTOP` CPU types (`'sparse'`, `'random'`, etc.) freeze TD** — only use GPU types: `perlin2d/3d/4d`, `simplex2d/3d/4d`, `randomgpu`. Animate via `par.seed.expr` (no `par.t`).
7. **`levelTOP.par.blacklevel` (no `1` suffix)** — inconsistent with `gamma1`, `brightness1`. The first I/O is unsuffixed; suffixes start at 1 for additional channels.
8. **`renderTOP` background** is controlled via its own `par.bgcolor*` (not the camera's).
9. **`constantMAT` has no `emit*` pars** — it's unlit by definition; `colorr/g/b` IS the output. Use `applypointcolor=True` to read per-point Color attribute, otherwise material color shows.

---

## v002 — Built (2026-05-01)

**Status:** shipped. First polished POPX-on-WOBAR proof. Lives at `/project1` (not `/project1/base_attractor_chamber` as v001 plan stated — Nick rebuilt directly into project1, no wrapping baseCOMP).

**Architecture (left to right at /project1):**

POPX chain → `pointgen1` (3000 sphere points) → `sa1` (POPX SA Aizawa, advect mode, audio-bound Timescale) → `math_velocity` (LenVel from PartVel) → `random_scale` (per-point ScaleRand 0.6..1.4) → `null_pop_out` (terminal cap; feeds back to sa1.Pointsupdatepop and forward to geo instances).

Scene → `geo_attractor` (instances null_pop_out, child sphere_template + pbrMAT "black pearl") → 4 lights (warm/cool/earth/pale palette-cyclers, two orbiting) → `cam` (slow orbit, lookat tracks live centroid via `centroid_tracker` executeDAT + EMA-lerp on `lookat_target`) → `environment1` (HDR moon-noon at low dimmer for deep shadows).

Render → `render` → bloom branch → mirror_flip + mirror_comp (bilateral symmetry) → comp_bg ADD on `bg_black` → grain chain → `null_out` → `rec_out` (HAP, audio routed from audio_in).

**Audio reactivity (single binding only, per Nick):**
`sa1.Timescale = ctrl.Audiofloor + ctrl.Audioceil * (max(0.0, energy)^ctrl.Audioexp)`. Speed of point motion responds to overall audio energy. Every other potential binding (sub→flash, mid→Ua, energy→bloom, etc.) deferred for explicit user request. The `max(0, …)` clamp is required because audio analysis returns tiny negative noise (~e-22) at silence which breaks non-integer exponents.

**Control panel — `/project1/ctrl_master`:**
22 custom parameters across 6 pages (Audio, Material, Lighting, Camera, Composition, Form). Every visual op param reads from `ctrl_master` via expressions. Two register tunings landed during session:
- **Hard chaotic mushroom trip**: toxic palette (blood wine / sulfur / bilious green / bruise purple), audio exp 1.3, breath ±18%/6s, orbit 35s, fov 28
- **Dark hypnotic crimson** (final state): red-only palette (dark crimson → bright red → wine / mulberry / rust / mahogany / bone / taupe — pink killed at user request), audio exp 1.7, breath ±10%/18s, orbit 80s, fov 32

**Cleaned up at session close (27 ops deleted):** noise_swirl, random_coloru, lookup_color, math_scale, ramp_palette + keys, dof_depth, lumablur_glow, atmospheric_bg + keys, bg_with_nebula, nebula_*, glints_* (5), bg_final, geo_aura + children, render_aura, blur_aura, level_aura, mirror_flip_aura, mirror_aura_comp, comp_orbs_over_mist, comp_vignette, vignette + keys.

**New gotchas surfaced (logged in `working/TD_BUILD_LOG.md`):**
1. Audio energy returns tiny negative values at silence — `**` raises complex error. Always `max(0.0, energy)` before pow.
2. `geometryCOMP.par.instancesx/y/z` accept BARE attribute names only — no expressions like `LenVel*0.6`. Bake math into a new attribute via mathmixPOP.
3. POPX SA strips custom upstream attributes through advection — write per-particle attrs DOWNSTREAM of SA.
4. `nullPOP.points('Color')` returns list of TUPLES per point, not flat float buffer.
5. `renderTOP.par.geometry` is glob pattern not path — `geo_attractor` matches that COMP only.
6. Aizawa instantaneous centroid is NOT temporally stationary — fixed lookat drifts. Solution: executeDAT.onFrameStart with EMA-lerp on lookat_target.

**Move file:** `moves/move_002.json` (full operational record).
