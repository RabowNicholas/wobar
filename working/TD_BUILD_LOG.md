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
| Python helper functions in `td_execute_python` don't inherit script-level globals — all `op()` refs must be inside the function body | **2** | **✅ PROMOTED** |
| `annotateCOMP` nodeY = bottom edge (not top) — top = nodeY + nodeHeight | 1 | No |
| `analyzeCHOP function='average'` returns ~0 on HP filter output — use `rmspower` for highpass chains | 1 | No |
| `null_audio` is analysis CHOP at rate 30 — use `audio_in` (audiofileinCHOP) for recording audiochop | 1 | No |
| HSV desat kills warm low-luminance colors — muted orange/warm goes black. Warm palettes need higher RGB values to survive the desat chain | 1 | No |
| `triggerCHOP` par expressions unreliable — use `ParMode.CONSTANT` with hardcoded values | 1 | No |
| List comprehensions in `td_execute_python` cannot reference outer-scope variables — use explicit for loops | 1 | No |

---

## Build Sessions

---

### 2026-04-16 — base_act2_underwater Audio Tuning + Kick Response (moves 037–043)

**What was built:**
Audio reactivity tuning and kick response system for `/project1/base_act2_underwater` — Act 1/5 portal web visual.

**Audio analysis findings (rec_audio, 16400 samples from null_audio):**
- sub_bass: typical 0.05–0.15, peaks 0.81 — clear discrete kicks, mostly quiet
- energy: typical 0.005–0.02, peaks 0.87 — very dynamic, near-zero between hits
- growl: typical 0.13–0.20, peaks 1.0187 — CLIPPING (growl_max was 0.16, raised to 0.22)
- transient: typical 0.03, peaks 0.76

**Changes made:**
- `ctrl_norm.growl_max` 0.16 → 0.22 (fix clipping)
- `glsl_shimmer uBreathAmt` expression: pow(sub_bass,1.8)*0.9 → linear sub_bass*0.75 (gentle audio was crushed by power curve)
- `lvc brightness1`: energy*0.484 → energy*0.45 linear
- `blur_shimmer size`: growl-driven → sub_bass-driven (0px base, spikes to ~13px on kick)
- Portal triangle anchor: added base positions (0,0.28), (0.22,-0.22), (-0.22,-0.22) — portals were phase-locking bottom-left at low chaos. Lissajous amplitude cut 0.44/0.58 → 0.18/0.22
- Kick glow burst: blur_kick (70px gaussian from ramp_lookup) → lvc_kick (brightness1=sub_bass*1.5) → comp_kick (Add) → null_underwater_out
- movie_out wired (null_underwater_out, audio_in) → /Users/nicholasrabow/Desktop/wobar/renders/output.mov

**What agent got right first pass:**
- rec_audio analysis approach (read min/max/val from recordCHOP channels)
- Identifying power curve as the root cause of dead audio response at gentle values
- Linear modulation mapping design for Act 1/5 character
- Glow burst architecture (blur source image, scale by audio, Add composite)
- moviefileoutTOP audiochop → audio_in (not null_audio)

**What needed correction / iteration:**
- blur_shimmer base of 4px was double-blurring on top of GLSL's inherent softness — dropped to 0
- Portal bottom-left issue: Lissajous amplitudes up to ±0.58 caused phase-locking at low chaos. Solution: explicit triangle base positions + tight drift offsets
- Kick warp+spin shader change (move_038) was reverted — user wanted different type of movement (settled on blur smear instead)

**New patterns discovered:**
- At low chaos (driftMult=0.136), Lissajous drift barely moves but portals still visit their full amplitude range slowly — if phase offset lands them off-screen, they stay there for a long time. Anchor base positions + small drift offsets is more reliable for composition control.
- For gentle audio (Act 1/5), power curves above 1.2 effectively kill modulation. Record first with rec_audio, check typical values (not just peaks), then design curves to those typical values.
- Glow burst using the palette-mapped output as blur source keeps colors consistent — no color bleed from pre-grade signals.

---

### 2026-04-15 — act2_fractal Kaleidoscope Tunnel Refinement (no checkpoint)

**What was built:**
Continued refinement of `/project1/base_act2_fractal` — 2D polar kaleidoscope tunnel GLSL shader. Full session of iteration on visual quality, audio reactivity, and recording setup.

**Final shader state:**
- 6-fold kaleidoscope fold (float N, so morphable)
- Double-layer fbm domain warp (warp of a warp): `warpAmp = 0.06 + chaos * 0.22`
- Breathing scale: `sin(uTime * 0.22) * 0.04` applied to UV before warp
- Global clockwise rotation: `-uTime * (0.20 + chaos * 0.25)` before fold
- Chaos power curve: `pow(uChaos, 3.0)` — steep, keeps breakdown calm
- Sub_pressure power curve: `pow(uSubPressure, 2.5)` in scroll — suppresses breakdown rumble
- Color cycling: 3 independent oscillators (c1=0.018, c2=0.031, c3=0.052 rad/s), each layer gets own hue angle, constrained to ±0.4 rad max — stays purple/indigo/violet family
- Three ring layers + fold edge + center void + depth fog + vignette + film grain

**Signal chain:** `fractal_glsl → bloom_blur + bloom_comp → lvc → hsv_desat → null_out → rec_out`

**Recording setup added:**
- `rec_out` (moviefileoutTOP): h264nvgpu, yuv420, 10000 Kb/s, 30fps, unique suffix on
- Connected to `null_out` for video, `audio_in` for audio (44100 Hz)
- Output: `~/Desktop/wobar/renders/act2_fractal.mov`

**Tried and rejected this session:**
- Mirror cascade (second nested fold) — too mandala/geometric, lost tunnel feel
- Orange palette — went black through HSV desat chain (warm low-luminance colors don't survive desaturation)
- Full ±1.8 rad hue cycling — went full spectrum (green/yellow/cyan), not on brand
- uPower LFO — morphing fold count was disorienting, not hypnotic

**What agent got right first pass:**
- Domain warp structure (double fbm, warp of a warp)
- Breathing scale placement (before warp, on UV)
- Color cycling constraining with `sin * 0.4` range
- Chaos power curve logic
- rec_out wiring and codec parameters

**What needed correction:**
- `null_audio` is analysis CHOP at rate 30 (not audio waveform) — audiochop for recording must point to `audio_in` (44100 Hz stereo), not `null_audio`. Pointed there initially, got "sample rate must be 44100" error.
- Orange colors went black: muted orange (R~0.18, B~0.01) has low luminance that HSV desaturation kills entirely. Warm low-saturation colors need much higher RGB values to survive the desat chain.
- Full-spectrum hue rotation (±1.8 rad) reads as rave/LED — too broad. ±0.4 max keeps it brand-appropriate.

**New patterns discovered:**
- Power curve on audio inputs in GLSL suppresses breakdown noise better than Lag CHOP alone. `pow(x, 2.5–3.0)` flattens small values (breakdown rumble) while passing large values (drop) through cleanly.
- HSV desat kills warm low-luminance colors — test any new palette through the full chain before committing. Purple works because the B channel carries enough luminance after hue rotation.
- Three independent color oscillators at slightly different rates (0.018/0.031/0.052 rad/s) create perpetual non-repeating color variation within a constrained palette — better than a single cycle.
- `moviefileoutTOP` audiochop must be the raw audio stream (audiofileinCHOP or equivalent at 44100), not a downstream analysis CHOP.

---

### 2026-04-15 — base_audio Full Build + Tuning (base_audio v001)

**What was built:**
Complete rebuild and tuning of `/project1/base_audio` — 8-channel dubstep/psychedelic bass audio pipeline tuned to mur.wav.

**Final channel set (null_audio output):**
- `sub_bass` — 50Hz BP → RMS → lag (0.05/0.30s) → normalize, sqrt compress
- `bass` — 150Hz BP → RMS → lag (0.005/0.15s) → normalize
- `mid` — 1kHz BP → RMS → lag (0.002/0.08s) → normalize
- `high` — 4kHz HP → RMS → lag (0.001/0.05s) → normalize
- `energy` — weighted band sum (0.55 sub + 0.35 bass + 0.07 mid + 0.03 high) → lag (0.01/5.0s) → normalize
- `sub_pressure` — 50Hz BP → RMS → slow lag (0.1/1.0s), direct (no math_remap)
- `growl` — 180Hz BP → RMS → lag (0.003/0.12s) → normalize (growl_max=0.16)
- `transient` — filterCHOP edge on energy_lag → normalize (fromrange2=0.30, sqrt compress)

**Tuned ctrl_ values (from mur.wav full-song recording):**
- `ctrl_norm`: band_max=0.32, energy_max=0.135, growl_max=0.16
- `ctrl_smooth`: smooth_up=0.04, smooth_down=0.08 (scope: sub_bass bass mid high growl only)
- `smooth_out` inserted between final_merge and null_audio

**Architecture extras:**
- `rec_audio` (recordCHOP) tapped from null_audio for future full-song analysis
- Network organized left-to-right with 16 annotateCOMP labels

**Kick detection — tried and removed:**
- Attempt 1: HP 2kHz click transient — failed (sub bass masks all click content)
- Attempt 2: sub_bass onset detection (filterCHOP edge on sub_rms) — technically worked but removed by design choice
- Final decision: no kick channel. Organic continuous signals (sub_bass, growl, energy, transient) suit the genre better than impulse triggers

**What agent got right first pass:**
- audiofilterCHOP/analyzeCHOP/lagCHOP architecture for all band chains
- Energy calculation (weighted sum → slow lag) correct on first attempt
- smooth_out Lag CHOP with scope parameter for selective smoothing
- annotateCOMP creation and parameter names (Titletext, Backcolorr/g/b/alpha, layerzone)
- rec_audio recordCHOP + Python analysis workflow for data-driven tuning

**What needed correction:**
- `annotateCOMP` nodeY is the BOTTOM edge, not the top — initial positions all shifted one height upward. Corrected by computing bounding boxes from actual node positions.
- `analyzeCHOP function='average'` produces zero on HP filter output (bipolar signal cancels). HP filters need `function='rmspower'`. BP filters with `average` work because they produce a meaningful envelope.
- `triggerCHOP` parameter expressions (`par.threshup.expr`) evaluated to 0.0 despite ctrl_kick channel having correct value. Safer to use `ParMode.CONSTANT` with hardcoded values for triggerCHOP parameters.
- `td_read_chop` on a 6315-sample × 9-channel recording exceeds token limit — analyze inside TD via `td_execute_python` instead.
- Python helper functions defined in `td_execute_python` don't see script-level `op()` variables — confirmed again (already in log). All `op()` calls must be inside the function body.
- List comprehensions in `td_execute_python` can't reference outer-scope variables — use explicit for loops or wrap everything in a function.

**New patterns discovered:**
- `annotateCOMP` is the correct TD type for network annotation boxes (not `annotationCOMP`, `commentCOMP`, `networkBox`). Key pars: `Titletext`, `Backcolorr/g/b/alpha`, `layerzone='belowgrid'`, `nodeWidth`, `nodeHeight`. nodeY = bottom edge.
- Full-song analysis workflow: recordCHOP (tap from null_audio) → record during song → `list(ch.vals)` + `sorted()` for percentile analysis inside `td_execute_python`. Use p95 as normalization target (not max — too sensitive to outliers).
- Kick detection in dubstep: HP click approach never works. Sub_bass onset (filterCHOP edge on sub_rms) technically functions but design choice may favor removing kick entirely for organic feel.
- Single `band_max` in math_remap can't equalize both sub_bass and high — sub_bass (50Hz) is ~8x louder than high (4kHz HP) in this genre. If per-channel normalization needed, build separate math_remap per band.
- `pane.showParameters = False` hides the parameter panel from code. `pane.homeSelected(zoom=True)` zooms to fit selection.

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
