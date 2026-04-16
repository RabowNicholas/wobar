---
title: TD Expression Cookbook
version: 1.0
last_updated: 2026-04-15
status: live
scope: Paste-ready expressions, CHOP access patterns, and audio-reactive mappings for WOBAR TD builds. No tutorials — jump to the snippet.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]], [[working/TD_CLAUDE_DEBUG_LOG]]
---

# TD EXPRESSION COOKBOOK

Snippets only. One-line purpose → code → one-line "why this over alternatives."

---

## 1. Parameter References

### Basic op() lookup — sibling operator
**Access a sibling operator by name (relative path)**
```python
op('ctrl_fractal')['power']
```
Preferred over absolute path — survives container moves and copies.

---

### Absolute path lookup
**When referencing across containers (e.g. base_audio from base_act2)**
```python
op('/project1/base_audio/null_audio')['sub_pressure']
```
Use when the source is in a different container. Breaks if containers are renamed — prefer Select CHOPs (see Section 5) for cross-container audio.

---

### Parent COMP reference
**Access a parameter on the parent COMP**
```python
parent().par.Intensity.eval()
```
Use for COMP custom parameters (e.g. `ctrl_master.Intensity`). `.eval()` forces expression evaluation — never use `.val` to read back a custom par.

---

### `me` — current operator
**Self-reference inside an operator's own parameter expression**
```python
me.digits   # integer suffix from operator name (e.g. noise3 → 3)
me.name     # 'noise3'
me.path     # '/project1/base_act2/noise3'
```
Use `me.digits` to index into a Shuffle CHOP for per-instance channel access.

---

### `iop` — input operator
**Reference the first input connected to this operator** [VERIFY: only available in some DAT/CHOP contexts]
```python
iop.numChans
```
Rarely needed in expressions. Prefer explicit `op('name')` for clarity.

---

### Relative vs absolute — when each fails

| Pattern | Fails when |
|---------|-----------|
| `op('name')` | Name changed, or target is not a sibling |
| `op('./child')` | Used in a non-COMP context |
| `op('../sibling')` | Wrong nesting level |
| `op('/absolute/path')` | Container renamed or moved |
| `parent().par.X` | Called from outside the container |

**Rule:** Relative paths in expressions, absolute paths only as a last resort or for cross-container reads. Better than absolute: wire a Select CHOP to bring the signal local.

---

## 2. CHOP Value Access

### Access by channel name
**Read a named channel from a CHOP**
```python
op('ctrl_fractal')['power']
op('audio_ref')['sub_pressure']
```
Preferred — survives channel reordering. Fails if channel doesn't exist (returns 0, no error).

---

### Access by index
**Read by channel position (0-based)**
```python
op('ctrl_fractal')[0]   # first channel
```
Fragile — breaks on channel reorder. Use only when channel names are unknown or for compact iteration.

---

### Guard against empty CHOP
**Prevent expression errors when CHOP has no channels (e.g. audio not connected)**
```python
op('audio_ref')['sub_pressure'] if op('audio_ref').numChans > 0 else 0
```
Use on any audio-reactive expression. Prevents cook errors when audio is disconnected.

---

### `eval()` vs `.val` for parameter verification
**Verify what an expression actually evaluates to**
```python
op('fractal_glsl').par.color0rgbr.eval()   # correct
op('fractal_glsl').par.color0rgbr.val      # WRONG — returns cached value, may be stale
```
Always use `.eval()`. `.val` returns the last cooked value and does not reflect the current expression.

---

### `numSamples` — multi-sample CHOPs
**Check how many samples a CHOP has (relevant for animation curves, recordings)**
```python
op('rec_audio').numSamples   # e.g. 132300 for 3s at 44100 Hz
op('null_audio').numSamples  # 1 for a single-sample analysis CHOP
```
Analysis CHOPs (lagCHOP, analyzeCHOP outputs) are always 1 sample. RecordCHOP output grows over time.

---

## 3. Time & Timeline

### Absolute time — seconds
**Continuous seconds since project started. Drives animations in expressions.**
```python
absTime.seconds
```
Use in GLSL uniforms (`uTime`) and for continuous oscillators. Does not reset on timeline loop.

---

### Absolute time — frame
**Current global frame number**
```python
absTime.frame
```
Use for frame-accurate sync. Note: does not respect COMP-local playback rate.

---

### Local COMP time
**Frame number relative to the current COMP's timeline (respects Time COMP)**
```python
me.time.frame
me.time.seconds
```
Use inside a COMP with a local Time COMP for looping animations. [VERIFY: `me.time.seconds` available in all contexts]

---

### Oscillator with controllable speed
**Slow sine wave from a ctrl_ CHOP speed channel**
```python
math.sin(absTime.seconds * op('ctrl_fractal')['orbit_speed'])
```
Driving rotation, breathing, or LFO. Import `math` is implicit in TD expression context.

---

### Normalized random per-instance (stable)
**Reproducible random value from an integer seed**
```python
tdu.rand(me.digits + 100)     # different value per operator index, stable across frames
tdu.rand(me.digits + absTime.frame * 0.01)  # slow drift per instance [VERIFY: exact signature]
```
Use for staggered timing across instanced operators (particles, multi-arm spirals).

---

### Locked-to-timeline audio sync
**Index an Audio File In CHOP to the timeline for deterministic render**
```python
# Set on audiofileinCHOP par.index:
me.time.frame / root.time.rate
# Set par.playmode = 'locked'
```
Required for all renders. `sequential` mode drifts; `locked` ties audio frame to cook frame.

---

## 4. Audio-Reactive Mappings

All examples assume audio channels are available at `op('audio_ref')` (a Select CHOP pointing to `/project1/base_audio/null_audio`). Guard all with `if op('audio_ref').numChans > 0 else default`.

---

### Bass → scale (zoom)
**Sub-bass drives inward zoom — more pressure = tighter pull**
```python
1.0 - (1.0 - op('ctrl_fractal')['zoom']) * op('audio_ref')['sub_bass']
```
Maps sub_bass 0→1 to zoom range `[zoom_base, 1.0]`. Keeps zoom controllable via ctrl_.

---

### Bass → opacity (feedback trail length)
**Sub-bass increases feedback opacity — more bass = longer trails**
```python
op('ctrl_scene')['opacity_base'] + op('audio_ref')['sub_bass'] * 0.08
```
Keep multiplier small (0.05–0.10). Above 0.99 = white-out. Below 0.85 = trails die instantly.

---

### Energy → rotation speed
**Energy envelope drives rotation — breakdown near-still, drop spins**
```python
op('ctrl_scene')['rotate_base'] * op('audio_ref')['energy']
```
`energy` channel is the weighted band sum with slow release lag (5s down) — tracks song energy, not transients.

---

### Transient → size flash
**Fast onsets cause momentary size burst — returns to base instantly**
```python
op('ctrl_scene')['size_base'] + op('audio_ref')['transient'] * op('ctrl_scene')['transient_amt']
```
`transient` is a filterCHOP edge on energy_lag — fires on note attacks, silent otherwise.

---

### Sub-pressure → chaos (with power curve)
**Sub-bass cumulative pressure drives chaos — smooth at breakdown, wild at drop**
```python
min(op('audio_ref')['sub_pressure'] * op('ctrl_fractal')['chaos_sens'], 1.0)
```
Then in GLSL: `float chaos = pow(uChaos, 3.0);` — steep exponent keeps breakdown calm.

---

### Growl → turbulence amplitude
**Mid-bass content drives organic wobble**
```python
op('ctrl_scene')['noise_amp_base'] + op('audio_ref')['growl'] * 0.25
```
`growl` is 180Hz BP — tracks bass wobble and mid-bass texture, not sub pressure.

---

### Full-expression guard template
```python
# Paste this pattern for any audio expression
(op('audio_ref')['sub_pressure'] * 0.4 + op('ctrl_fractal')['base_val']) if op('audio_ref').numChans > 0 else op('ctrl_fractal')['base_val']
```
Always have a ctrl_ fallback so the visual is controllable without audio connected.

---

## 5. CHOP Export vs Expression vs Reference — Which to Use When

### The tradeoff table

| Method | Cook cost | Readable | Breakable by | Use when |
|--------|-----------|----------|--------------|----------|
| **Expression in par** | Low per-par | Moderate | Name changes, missing channels | 1–2 CHOP reads per parameter, simple math |
| **CHOP Export** | One cook, fans to many pars | Low | Export table conflicts | Driving many parameters from same channel (e.g. all position XYZ) |
| **Pre-compute CHOP** (`ctrl_audio_live`) | One CHOP cook | High | Nothing | Complex audio math reused across many expressions |

---

### Expression (most common)
```python
# In a parameter expression field:
op('ctrl_fractal')['power']
absTime.seconds * op('ctrl_fractal')['orbit_speed']
```
Use for 1–4 CHOP reads per expression. More than ~4 expressions × 8+ reads = FPS crash risk at 60fps.

---

### Pre-compute CHOP (WOBAR standard for audio)
**Do the math once in a Math CHOP, then read the result cheaply**
```python
# ctrl_audio_live pattern:
# audio_ref → mathCHOP (band × energy) → rename → mergeCHOP → null (ctrl_audio_live)
# Then in TOP expressions:
op('ctrl_audio_live')['sub_e']       # sub × energy, pre-multiplied
op('ctrl_audio_live')['energy']      # raw energy
```
Required when same audio math feeds 5+ parameters. Avoids re-evaluating the same CHOP expression N times per cook.

---

### CHOP Export
**Export a CHOP channel directly to a parameter — bypasses expression system**
```python
# Via Export CHOP or the export table on a nullCHOP
# Path: op('/project1/base/target_op').par.tx → export from chop['tx']
```
**Warning:** Export steals the parameter — you cannot set it via expression or `td_set_operator_pars` while the export is active. Use for static routing (position, color) not dynamic expressions.

---

## 6. Python in Execute DATs

### onFrameStart — run every frame
```python
def onFrameStart(frame):
    ctrl = op('../ctrl_scene')
    val = ctrl['speed'] * 0.5
    op('../noise1').par.period = val
    return
```
**Why:** onFrameStart fires once per cook — efficient. Always define `op()` inside the function body, not at script scope (confirmed failure — see TD_CLAUDE_DEBUG_LOG.md).

---

### onValueChange — react to a CHOP channel crossing a threshold
```python
def onValueChange(channel, sampleIndex, val, prev):
    if channel.name == 'kick' and val > 0.5:
        op('../flash_lv').par.brightness1 = 2.0
    return
```
**Why:** More targeted than onFrameStart — only fires on change. Use for trigger-based events (kick flash, beat snap).

---

### tdu.digits — extract number suffix from operator name
**Get the index of a named operator (e.g. `ramp3` → `3`)**
```python
index = tdu.digits('ramp3')   # returns 3
index = me.digits              # same, from inside an expression on the operator itself
```
Use for per-instance channel access via `op('shuffle1')['chan' + str(me.digits)]`. [VERIFY: `tdu.digits` accepts string; `me.digits` is always int]

---

### Batch par-setting in a DAT script
```python
def setup():
    lvc = op('../lvc')
    lvc.par.brightness1 = 2.0
    lvc.par.gamma1 = 0.70
    lvc.par.contrast = 1.0
    lvc.par.blacklevel = 0.0
```
**Why:** Cleaner than multiple `td_set_operator_pars` calls when setting 4+ pars at once from a script.

---

## 7. Common Footguns

### Cook dependency cycle
**Symptom:** 🔴 STOP in TWOZERO footer, FPS drops to 0
**Cause:** Operator A reads from operator B which reads from A (circular dependency)
**Fix:** Disconnect the offending input immediately. Common with feedback loops where `feedbackTOP.par.targetop` points to itself instead of a downstream null.
```python
# feedbackTOP should point to null_out (downstream), not null_in (upstream)
op('feedback1').par.targetop = 'null_out'
```

---

### `.val` returns stale cache
**Symptom:** Script reads a parameter and gets the wrong value
**Cause:** `par.val` is a cached value from last cook, not the live expression result
```python
# Wrong:
x = op('lvc').par.brightness1.val     # may be 0 even if expression = 2.0

# Correct:
x = op('lvc').par.brightness1.eval()  # forces evaluation
```

---

### Export stealing a parameter
**Symptom:** `td_set_operator_pars` call succeeds but parameter value doesn't change in TD
**Cause:** A CHOP Export is overriding the parameter — export wins over all other methods
**Fix:** Find the export source (check the parameter's Export flag — blue dot in UI) and remove the export, or disable the exporting CHOP.

---

### Script-level `op()` globals in Execute DATs
**Symptom:** `NameError: name 'chop' is not defined` inside a helper function
**Cause:** Variables defined at script scope are not visible inside function bodies in TD's execute environment
```python
# Wrong:
chop = op('../audio_ref')
def analyze():
    return chop['sub_pressure']    # NameError

# Correct:
def analyze():
    chop = op('../audio_ref')      # op() inside the function
    return chop['sub_pressure']
```
Confirmed failure — logged in TD_CLAUDE_DEBUG_LOG.md (see: expressions tag).

---

### Audio expression returning 0 at breakdown
**Symptom:** Visual freezes or returns to base state during breakdown even when the track has content
**Cause 1:** Channel mapped to `energy` — energy is highest during melodic breakdowns (wide-band content), lowest during drops (sub-only). Map to `sub_pressure` for drop reactivity.
**Cause 2:** `analyzeCHOP` on HP filter output using `function='average'` — bipolar signal averages to ~0
**Cause 3:** Power curve exponent too low — `pow(x, 1.8)` still passes small breakdown values. Use `pow(x, 2.5–3.0)`.
```python
# Chaos stays flat at breakdown:
float chaos = pow(uChaos, 3.0);   # steep curve — only real drops push through
```
All three are confirmed failures — logged in TD_CLAUDE_DEBUG_LOG.md (audio tag).
