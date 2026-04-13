---
title: TouchDesigner Build Log
version: 1.0
last_updated: 2026-04-12
status: live
scope: Session-by-session log of AI-assisted TD builds. Used to identify recurring corrections and promote them to rules in WOBAR_TD_AGENT_RULES.md.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]]
---

# TD BUILD LOG

One entry per build session. Newest at top. This is the feedback loop — patterns that repeat here become rules.

---

## Correction Tracker

Corrections that appear 2+ times get promoted to WOBAR_TD_AGENT_RULES.md.

| Correction | Count | Promoted? |
|-----------|-------|-----------|
| (none yet) | — | — |

---

## Build Sessions

---

### 2026-04-12 — Act 2 Underwater Visual (Sessions 1–2 combined)

**What was built:**
`/project1/base_act2` — full underwater-looking-up visual stack.

Signal chain: `ring_src` (GLSL 3-arm Archimedean spiral) → feedback loop (`comp` ← `lv` ← `tr`) → `null_out` → `warp` → `hsv` → `lvc` → `lkp`/`ramp` → `null_final` → `zoom_out` → `lv_crush` → `null_black` → caustic layer (`caustic_glsl` → `caustic_lv` → `comp_caustic` → `null_caustic_out`) → surface glow (`ramp_surface` → `lv_surface` → `comp_surface` → `null_surface_out`).

**Key parameters:**
- Spiral: 3 arms, spacing=0.072, hue 0.50–0.67, shader sat mix 0.15, brightness 0.036
- Feedback: opacity 0.982, rotation 38°/frame (constant), zoom sx=sy=0.966+0.005*sin(t*0.18)
- Zoom out: 3.5x (inside the spiral, fills frame)
- lvc: brightness 1.20, gamma 0.80, contrast 1.65
- HSV: hueoffset 0.0, satmult 0.75
- lv_crush: blacklevel 0.03, contrast 1.30
- Caustic: 3-layer Voronoi Worley edges, animated at 0.30/0.22/0.18 speed, screen-blended opacity 0.50
- Surface glow: radial ramp (pale cyan-white center → black), screen-blended at brightness 0.55

**What agent got right first pass:**
- Feedback loop architecture correct
- GLSL caustic shader built clean, no shader errors
- Screen blend composite wiring for additive layers
- Time uniform setup matched ring_src pattern exactly

**What needed correction:**
- `lvc.par.contrast1` does not exist — correct par name is `lvc.par.contrast`
- rampTOP keys: initial values too dark at mids, had to iterate brightness up
- Color shift from purple to water: required 3 iterations (purple → blue → too neon → dialed back saturation + ramp)
- Early in session: `contrast1` typo on levelTOP — par is `contrast` not `contrast1`

**New patterns discovered:**
- levelTOP contrast par: `par.contrast` (not `par.contrast1`)
- For "transparent water" color: shader internal desaturation mix 0.15 (very low) + HSV satmult 0.75 + desaturated ramp = correct read
- Wide wave crest spacing: increase GLSL `spacing` from 0.042 to 0.072+
- Caustic chain should be fully isolated (new nodes only) so it can be bypassed/removed independently
