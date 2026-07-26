# CHANGE LOG — low_poly_sphere

TD comp: `/project1/vv_test` (inside `kekkai_low_poly.toe`)
Vector-void wireframe rig — low-poly icosphere, wireframeMAT lines, feedback trail, CA/glow/grain post.

---

## 2026-07-25 — move_001: revive trail + organize network

**Trail revived.** `level_trail` was dead: `opacity` was a hard `0.0` constant and `Ctrl.Trailnow` (plus Trailgate/Trailfloor/Trailcurve) was orphaned — the feedback branch cooked every frame and contributed nothing.
- `level_trail.opacity` and `level_trail.outhigh` both bound to `parent.Ctrl.par.Trailnow` — the ghost-trail recipe from AGENT_RULES (same expression scaling RGB and alpha on the decay levelTOP, composited `over`).
- Trail dials moved into the sane band (AGENT_RULES: opacity 0.89–0.97, >0.99 whites out): `Trailfloor 0 → 0.90`, `Traillength 1.1 → 0.96`, `Trailcurve 1.0 → 1.5`, `Trailgate 0 → 0.15`. Trail now breathes 0.90 → 0.96 with `energy`.
- `feedback_trail.resetpulse` fired to drop the cached resolution (already 1280², rgba16float).
- Feedback wiring was already canonical (fresh content on `input[0]`, `par.top` = loop target) — left alone.

**Naming** to convention: `out→null_out`, `post_out→null_post`, `comp1→comp_trail`, `feedback1→feedback_trail`, `render1→render_wire`, `cam1→cam_main`, `light1→light_key`, `grade→level_grade`. All name-carrying refs re-asserted (`feedback_trail.top`, `render_wire.camera/geometry/lights`).

**Layout** — explicit nodeX/nodeY on all 33 remaining ops, left→right, one row per subsystem:
- spine y=0: geo → render_wire → color_mult → comp_trail → comp_final → null_out → bloom → glsl_tone → level_grade → glsl_ca → comp_glow → comp_grain → null_post → render_out
- y=+400 color branch, y=+600 grain branch, y=+200/+350 shader + info DATs docked under their glslTOPs
- y=−200 trail branch (left) and glow branch (right), y=−400 motion CHOPs, x=−250 left column (mat/cam/light)

**Cleanup**
- Deleted 4 unused TD boilerplate DATs (`glsl_ca_pixel`, `glsl_ca_compute`, `glsl_tone_pixel`, `glsl_tone_compute`) — three pairs were stacked at identical coords. Cleared the dormant `computedat` refs first.
- `vv_test.par.opviewer` pointed at `./out1`, which does not exist → now `./null_post`.
- Audio refs in the `Ctrl` expressions were absolute (`op('/project1/base_audio/null_audio')`) → now `op('base_audio/null_audio')`, portable across a `/project1` rename.

Result: 35 ops, 0 errors, 60 fps.

**Left alone (flagged, not changed):** orphan Ctrl pars `Facets`, `Linehot`, `Thickness`, `Huedrift`, `Huegrowl`, `Energytrail` bind to nothing. `render_out.file` ends `.mov` but `moviecontainer=mp4`. All reactivity dials still zeroed (`Tumblespeed`, `Subgain`, `Energyspin`, `Energyswirl`, `Satmult`, `Bloomamt`, `Grainamt`) — the rig renders a static white wireframe until those are dialed up.
