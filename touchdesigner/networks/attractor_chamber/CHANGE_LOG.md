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

## v002 — Plan (next session, after Nick imports working example)

Start from `touchdesigner/third_party/POPX/POPX_Examples_1_3_0/examples/strange attractors.tox` as the structural baseline. Diff modifications:
- Re-color via WOBAR desaturated psychedelic palette (Lookup TOP from new ramp)
- Add audio reactivity (`/project1/base_audio/null_audio` → SA `Ua` / `Timescale`, geo scale)
- Wrap into `/project1/base_attractor_chamber` for WOBAR convention
- Add post chain: bloom + grain
