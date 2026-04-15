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
| `filterCHOP` is smoothing not frequency — use `audiofilterCHOP` | 1 | No |
| `lagCHOP` par names are `lag1`/`lag2` not `lagup`/`lagdown` | 1 | No |
| Multiple op() in TOP expressions (5+ × 8 pars) crashes TD — pre-compute in CHOP | 1 | No |
| `par.val` returns cached value — use `par.eval()` to verify expression result | 1 | No |
| COMP custom par referencing CHOP has cook order issues when TOPs read it — reference CHOP directly in TOP expressions | 1 | No |
| `playmode='locked'` ties audio to timeline length — use `sequential` for full track | 1 | No |
| `audiodeviceoutCHOP` with `cookalways=True` freezes TD | 1 | No |

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

---

### 2026-04-14 — Tunnel Audio Reactivity + base_audio Build

**What was built:**

`/project1/base_audio` — Full audio analysis pipeline from scratch.
- `mono_mix` (Math CHOP, stereo→mono) → 4 `audiofilterCHOP` branches → `analyzeCHOP` (RMS) → `lagCHOP` per band → `merge_bands` → `rename_bands` → `math_remap` → `null_audio`
- Bands: sub (50Hz BP, lag 0.05/0.30), bass (150Hz BP, lag 0.005/0.15), mid (1kHz BP, lag 0.002/0.08), high (4kHz HP, lag 0.001/0.05)
- Beat/kick branch: `beat_filt` (90Hz BP) → `beat_rms` → `kick_logic` → `kick_trigger`
- Energy channel: weighted sum (0.55 sub + 0.35 bass + 0.07 mid + 0.03 high) → `energy_lag` (up=0.05, down=2.5s) → `e_norm` (remaps 0→0.18 to 0→1, peak ~0.18 at max) → merged into `null_audio` as 5th channel
- `audio_out` (Audio Device Out CHOP) for monitoring

`/project1/tunnel` — Full audio reactivity layer.
- `sel_audio` Select CHOP reading all 5 channels from `base_audio/null_audio`
- `sel_kick` Select CHOP reading `kick_trigger`
- `ctrl_audio_live` CHOP pipeline: `energy_scale` (energy × Intensity) → per-band multiply by energy → rename to `sub_e, bass_e, mid_e, high_e` → merge with `energy` + `kick_lag` → `ctrl_audio_live` null
- `kick_lag`: lag1=0.001, lag2=0.3 (instant attack, 300ms decay envelope)
- `Intensity` parameter on `ctrl_master` (Motion page) — manual ceiling 0–1
- All visual expressions rewritten to read from `ctrl_audio_live` (max 2 CHOP lookups per expression)

**Expression architecture (final):**
- `fb_tr.sx/sy`: `1.0 - (1.0-Zoom)*energy - bass_e*0.06`
- `fb_tr.rz`: `(Rotate + sub_e*2.5) * energy`
- `fb_lv.opacity`: `0.82 + 0.15*energy + sub_e*0.02`
- `lvc.contrast`: `1.0 + (Contrast-1.0)*energy + mid_e*1.0`
- `glow_blur.size`: `Glowsize*energy + bass_e*25`
- `chrom_ab.vec0valuex`: `Caamount*energy + high_e*0.04`
- `displace.displaceweightx/y`: `(Dispamt + sub_e*0.15) * energy`

**Network layout:** cleaned left-to-right. Source → feedback loop → post-process → output. Control cluster (ctrl_master, sel_audio) top-right.

**What agent got right first pass:**
- audiofilterCHOP parameter names (filter, units, cutofffrequency, resonance)
- Energy envelope concept (slow release lag) correctly tracks breakdown/drop dynamic
- Normalization step catching the 0→0.18 peak range
- `ctrl_audio_live` pre-compute architecture for performance

**What needed correction:**
- `filterCHOP` used first — wrong operator. Should be `audiofilterCHOP` for frequency filtering
- `lagCHOP` par names: `lag1`/`lag2` not `lagup`/`lagdown`
- `mathCHOP` range pars: `fromrange1/2`, `torange1/2` not `from1/2`, `to1/2`
- `constantCHOP` pars: `const0name`/`const0value` not `value0name`/`value0`
- `par.val = 0` before expression mode poisons the read cache — just set expr + mode, don't touch val
- Cook loop caused by inserting `e_norm` in wrong position in energy chain (between lag and rename instead of after lag before final_merge)
- COMP custom par with CHOP expression had cook ordering errors in TOP context — fixed by reading CHOP directly in TOP expressions
- `playmode='locked'` caused only 10s of audio — switched to `sequential`
- `audiodeviceoutCHOP` with `cookalways=True` froze TD — removed that flag
- Python helper functions in execute_python don't inherit script-level globals — all op() refs must be inline

**New patterns discovered:**
- For audio frequency filtering: `audiofilterCHOP` (not `filterCHOP`). Par: `par.filter='bandpass'`, `par.units='frequency'`, `par.cutofffrequency`, `par.resonance`
- Stereo audio must be collapsed to mono before `analyzeCHOP` — use `mathCHOP` with `chanop='add'`, `gain=0.5`
- Energy envelope: weighted band sum + asymmetric lag (fast attack 0.05s, slow release 2.5s) is the correct pattern for energy tracking
- Peak energy from this band weighting hits ~0.18 — normalize with `mathCHOP fromrange2=0.18` + `postop='clamp'`
- Pre-compute `band × energy` in CHOP domain (`ctrl_audio_live`) — keep TOP parameter expressions to max 2 CHOP lookups. More than ~4 lookups across 8+ expressions causes FPS crash at 60fps
- `par.eval()` forces expression evaluation — `par.val` returns cached value, unreliable for verification
- Kick detection: `audiofilterCHOP` (90Hz BP) → `analyzeCHOP` (RMS) → `logicCHOP` (convert='bound', boundmin=0.25) → `triggerCHOP`. Add `lagCHOP` (0.001/0.3s) downstream in the visual network for envelope shaping
- Cook loop indicator: 🔴 STOP in footer. When triggered, disconnect the offending input immediately before any other action
