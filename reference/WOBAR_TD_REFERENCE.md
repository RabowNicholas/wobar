# WOBAR TouchDesigner Reference
*Technical reference for building WOBAR visualizers. Read by the coaching skill as needed — not meant to be read top to bottom.*

---

## Table of Contents
1. [Operator Family Quick Reference](#operators)
2. [Audio Pipeline](#audio)
3. [Visual Primitives — Vocabulary](#primitives)
4. [Color System + Palette Values](#color)
5. [Analog Grain Pipeline](#grain)
6. [Archive Footage Integration](#archive)
7. [Scene Architecture + Timer Sequencing](#architecture)
8. [Export Settings](#export)
9. [Common Failure Patterns](#failures)

---

## 1. Operator Family Quick Reference {#operators}

| Family | Color | Lives on | Use for |
|--------|-------|----------|---------|
| TOPs | Purple | GPU | All 2D image/video — the main visual chain |
| CHOPs | Green | CPU | Audio analysis, animation, control signals |
| SOPs | Blue | CPU | 3D geometry (rare in this workflow) |
| MATs | Yellow | GPU | Shaders for 3D geometry |
| DATs | Pink | CPU | Text, tables, Python scripts |
| COMPs | Gray | — | Containers (Base COMP per act) |

**Cross-family data flow:** CHOP Export (right-click channel → Export), Python expressions in parameter fields (`op('audioAnalysis')['bass']`), or conversion operators.

**Essential shortcuts:**
- `Tab` — OP Create Dialog
- `P` — toggle parameters
- `D` — toggle node viewer
- `U` — navigate up one level
- `Home` — fit all nodes to view
- `B` — bypass node
- Middle-click+drag — pan

**Always:** cap chains with Null TOPs. Name operators descriptively. Build left to right.

---

## 2. Audio Pipeline {#audio}

**Live component:** `/project1/base_audio` — `base_audio_v001.tox`. Do not rebuild from scratch. Load the .tox.

**Output:** `null_audio` (nullCHOP) — 8 channels, normalized 0→1, smoothed.

---

### Channel Reference

| Channel | Source | Lag Up / Down | Norm Max | Tuned for | Notes |
|---------|--------|---------------|----------|-----------|-------|
| `sub_bass` | 50Hz BP → RMS | 0.05s / 0.30s | 0.32 | Low-end weight, breath | Dominant channel in dubstep |
| `bass` | 150Hz BP → RMS | 0.005s / 0.15s | 0.32 | Bass body, harmonics | Shares band_max with sub/mid/high |
| `mid` | 1kHz BP → RMS | 0.002s / 0.08s | 0.32 | Texture, synth pads | Genuinely quiet in this genre |
| `high` | 4kHz HP → RMS | 0.001s / 0.05s | 0.32 | Air, hi-hats | Very low in dubstep — needs visual gain boost |
| `energy` | Weighted band sum | 0.01s / 5.0s | 0.135 | Macro arc, breakdown→drop | Best channel for overall intensity |
| `sub_pressure` | 50Hz BP → slow RMS | 0.1s / 1.0s | (direct, no remap) | Sustained heaviness | Raw output, max ~0.19, not remapped |
| `growl` | 180Hz BP → RMS | 0.003s / 0.12s | 0.16 | Bass wobble, groove | Primary melodic motion in dubstep |
| `transient` | Edge filter on energy | — | fromrange2=0.30 | Drop onset, hit detection | sqrt-compressed; spikes on fast energy rises |

**Energy weights:** sub×0.55 + bass×0.35 + mid×0.07 + high×0.03

**Output smoothing:** `smooth_out` Lag CHOP between final_merge and null_audio. Scope: `sub_bass bass mid high growl` only (energy/sub_pressure/transient bypass). Up=0.04s, Down=0.08s.

---

### Control Nodes

| Node | Channels | Current Values |
|------|----------|----------------|
| `ctrl_norm` | band_max, energy_max, growl_max | 0.32, 0.135, 0.16 |
| `ctrl_smooth` | smooth_up, smooth_down | 0.04, 0.08 |

---

### Kick Detection — Genre Note

**Do not implement kick detection for psychedelic bass / dubstep.**
- HP 2kHz click approach fails — sub bass masks all click transient content
- Sub_bass onset approach works technically but impulse triggers feel mechanical against the organic mix
- Use `energy` + `transient` channels for drop/hit detection. Use `sub_bass` for beat-locked motion.

---

### Full Signal Chain
```
audio_in (WAV, Play Mode = Sequential)
  └→ mono_mix (Math CHOP, chanop=add, gain=0.5)
       ├→ sub_filt (BP 50Hz)  → sub_rms  (avg) → sub_lag  (0.05/0.30)  ─┐
       │    └→ sub_press_lag (0.1/1.0) ────────────────────────────────→ final_merge[2]
       ├→ bass_filt (BP 150Hz) → bass_rms (avg) → bass_lag (0.005/0.15) ─┤
       ├→ mid_filt  (BP 1kHz)  → mid_rms  (avg) → mid_lag  (0.002/0.08) ─┤→ merge_bands
       ├→ high_filt (HP 4kHz)  → high_rms (avg) → high_lag (0.001/0.05) ─┘   → rename_bands
       ├→ growl_filt (BP 180Hz) → growl_rms → growl_lag (0.003/0.12)           → math_remap_growl → rename_growl → final_merge[3]
       └→ [no kick]

rename_bands → math_remap (normalize, sqrt compress) → final_merge[0]
rename_bands → e_mul (×weights) → e_sum → e_rename → energy_lag
  energy_lag → e_norm (normalize) → final_merge[1]
  energy_lag → transient_edge (filterCHOP, edge) → transient_norm → rename_transient → final_merge[4]

final_merge → smooth_out (Lag, scoped) → null_audio (export point)
null_audio → rec_audio (recordCHOP, record=off by default)
```

---

### Reading Channels in Visual Expressions
```python
# Sub bass breath (radius, scale)
0.15 + op('null_audio')['sub_bass'] * 0.4

# Growl → rotation speed (Act 2 spiral)
absTime.seconds * (5 + op('null_audio')['growl'] * 20)

# Energy → macro intensity (opacity, contrast)
0.82 + op('null_audio')['energy'] * 0.15

# Transient → glitch/hit trigger
op('null_audio')['transient'] * 2.0

# Sub pressure → sustained bloom
op('null_audio')['sub_pressure'] * 5.0
```

---

### Tuning Workflow

To re-tune for a new track:
1. Set `rec_audio.par.record = 'on'`
2. Play the full track through `audio_in`
3. Set `rec_audio.par.record = 'off'`
4. Run analysis script inside TD:
```python
def analyze():
    rec = op('/project1/base_audio/rec_audio')
    n = rec.numSamples
    results = {}
    for i in range(rec.numChans):
        ch = rec.chan(i)
        vals = list(ch.vals)
        sv = sorted(vals)
        results[ch.name] = {'max': sv[-1], 'p95': sv[int(n*.95)], 'p50': sv[int(n*.50)], 'mean': sum(vals)/n}
    for name, v in results.items():
        print(f'{name:<16} max:{v["max"]:.3f}  p95:{v["p95"]:.3f}  p50:{v["p50"]:.3f}')
r = analyze()
```
5. Targets: p95 ≈ 0.85–1.0 per channel. Adjust `ctrl_norm` values accordingly.

---

## 3. Visual Primitives — Vocabulary {#primitives}

These are reusable visual primitives, not act-locked requirements. Each one has a primary affinity (the act it was originally built for / where it tends to land), but cross-act use is fine when it serves the moment. The act's emotional register from `WOBAR_FRAMEWORK.md` does the steering — these are the parts you reach for.

### CIRCLE / VIGNETTE

**Affinity:** Act 1 / Act 5 (threshold, return). **Reads as:** breath, holding, mirror frame, the eye, recognition.

Build (Multiply mask method):
1. **Circle TOP** — `radius` 0.45 (Fraction), `softness` 0.25–0.4, fill white, bg black
2. **Composite TOP** (Multiply) — circle × content. White center passes through, black edges darken.

Build (circular crop method):
1. **Circle TOP** — `bgalpha` = 0 (transparent bg), `softness` 0.02–0.3
2. **Composite TOP** (Inside) — Input 1 = content, Input 2 = Circle. Crops to circle's alpha.

Audio-reactive breath (when wanted):
- **LFO CHOP** (Sine, 1.0–1.33Hz for 60–80 BPM) → Math CHOP (0–1 → 0.35–0.55) → Export to `circle1/radiusx` + `circle1/radiusy`
- Sub-bass Analyze → Lag (0.3s) → Export to `radius` and `softness`

When a circle returns later in the journey, the visual callback is intentional — same shape, different emotional weight from the surrounding music.

---

### INWARD SPIRAL

**Affinity:** Act 2 (descension, pull). **Reads as:** something deepening, audio tightening the form, recursive recognition.

Core feedback loop:
```
Feedback TOP → Transform TOP → Level TOP → Composite TOP → Null TOP
                                                ↑
                                        [New content source]
Feedback TOP: targetop = null_out (downstream)
```

Parameters:
- **Transform TOP**: `rotate` = 0.5–3.0° (constant per frame), `sx`/`sy` = **0.98–0.995** for inward pull (use >1.0 for outward variant), `bgcolor` = black
- **Level TOP**: `opacity` (Post tab) = 0.89–0.98. Controls trail length. Lower = shorter trails. **Critical — too high = white-out.**
- **Composite TOP**: Operation = Over or Add

Audio reactivity:
- Bass → rotation speed: `absTime.seconds * (5 + op('null_audio')['bass'] * 20)`
- Bass → scale: `1.0 - (op('null_audio')['bass'] * 0.05)` → 1.0 silent, 0.95 loud

Depth illusion: **Displace TOP** with radial **Ramp TOP** (center white, edge black) as displacement map. `displaceweight` controls pull intensity.

**Use 16-bit float pixel format** in feedback chain. Prevents banding in dark colors.

---

### TUNNEL + IMPERFECT MIRROR

**Affinity:** Act 3 (encounter, confrontation). **Reads as:** infinite depth, the angle you can't normally reach, recognition under pressure. The mirror is **never perfect** — 85–90% symmetry with meaningful asymmetry is what makes it confrontational rather than decorative.

Tunnel build: same as spiral but `scale` ~0.98, `rotate` 0–0.5°. Add new content at **edges** (use inverted Circle TOP as mask — `bgalpha` = 1, `fillalpha` = 0).

Partial mirror (85–90% symmetry):
- Source → **Flip TOP** (`flipx` = on) → **Level TOP** (opacity 0.85–0.90) → **Composite TOP** (Over or Average) with original
- OR: **Cross TOP** with `cross` value 0.85–0.90

Glitch/stutter:
- **Cache TOP + Cache Select TOP** — drive `index` with random CHOP for frame stuttering
- **Displace TOP + Noise TOP** — `displaceweight` 0.01–0.05 subtle, 0.1–0.5 aggressive. Animate Noise `period` and `amplitude`
- Trigger glitch on audio peaks via Threshold CHOP — not constantly

Impossible geometry: Feedback → Transform (scale 0.95, rotate 3°) → Tile TOP (2×2 mirror) → Composite → back to Feedback. Creates fractal recursion.

The encounter doesn't comfort. Whatever warmth shows up should disturb, not relieve.

---

### RADIAL EXPLOSION

**Affinity:** Act 4 (release, discharge). **Reads as:** outward force, cathartic, heavy-but-held — rhythm exists, this is not chaos.

Core feedback loop (reverse of spiral):
```
Feedback TOP → Transform TOP (sx, sy = 1.02–1.05) → Level TOP (opacity 0.90–0.97) → Composite TOP → Null TOP
                                                                                           ↑
                                                                                   [Center content]
```

Parameters:
- Transform `sx`/`sy` = **1.02–1.05** (>1.0 = outward expansion)
- Level opacity 0.90–0.97 (fast-fading trails for explosive feel)
- HSV Adjust TOP in feedback chain with slight `hueoffset` per frame for color cycling — keep within the desaturated psychedelic range, no rainbow

Audio peak triggering:
```
Analyze CHOP → Threshold (0.7–0.8) → Trigger (attack 0.01s, sustain 0.1s, release 0.5s)
→ Math (0–1 → 1.0–1.15 for scale, or 0–1 → 0.5–2.0 for brightness)
→ Lag → Export to Transform sx/sy and Level brightness
```

---

## 4. Color System + Palette Values {#color}

The palette is the **WOBAR desaturated psychedelic range**. Black and deep purple are the foundation; everything else — mauves, magentas, slates, oxidized organics, ambers, mirror metallics — is first-class alongside them, not rare. Muted 30–40% from full neon. Never pure neon, glowstick, candy, or safety colors.

### Foundation (always present)

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Black | `#000000` | 0.000, 0.000, 0.000 | True base |
| Off-black (purple bias) | `#0E0813` | 0.055, 0.031, 0.075 | Where most "blacks" should sit — already psychedelic |
| Charcoal mauve | `#1F1828` | 0.122, 0.094, 0.157 | Lifted-shadow grade for deep regions |

### Purple spine

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Deep purple dark | `#190028` | 0.098, 0.000, 0.157 | Ramp anchor |
| Deep purple mid | `#2D0546` | 0.176, 0.020, 0.275 | Ramp anchor |
| Deep purple highlight | `#5A0F78` | 0.353, 0.059, 0.471 | Ramp anchor |
| Wobar purple | `#6B2E87` | 0.420, 0.180, 0.529 | Primary brand purple |

### Mauves & dusty violets

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Plum | `#4D2540` | 0.302, 0.145, 0.251 | Deep desaturated wine |
| Smoke mauve | `#8A6E94` | 0.541, 0.431, 0.580 | Faded lilac, organic |
| Ash violet | `#6B5C7A` | 0.420, 0.361, 0.478 | Cooler, leans toward stone |
| Dusty lavender | `#A085AE` | 0.627, 0.522, 0.682 | Highlight — never pure white |

### Magentas & dusty roses

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Wine magenta | `#5A0F41` | 0.353, 0.059, 0.255 | Deep, blood-leaning |
| Muted magenta | `#B34E8F` | 0.702, 0.306, 0.561 | Mid-saturation pink-purple |
| Dusty rose | `#A6586D` | 0.651, 0.345, 0.427 | Warm-cool blend, organic |

### Cools — slate / petrol / dusk

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Petrol | `#2C4554` | 0.173, 0.271, 0.329 | Deep oily blue-gray |
| Oxidized teal | `#1E505A` | 0.118, 0.314, 0.353 | Subaquatic green-blue |
| Slate blue | `#4A6479` | 0.290, 0.392, 0.475 | Oceanic, neutral |
| Dusk blue | `#3B4C73` | 0.231, 0.298, 0.451 | Violet-tinted twilight |
| Wobar cyan | `#4A7B9D` | 0.290, 0.482, 0.616 | Bright cool |

### Oxidized organics — sage / moss / patina

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Aged moss | `#4D6149` | 0.302, 0.380, 0.286 | Forest floor, dim |
| Lichen sage | `#7A8A6F` | 0.478, 0.541, 0.435 | Pale, alkaline |
| Patina copper-green | `#5C7470` | 0.361, 0.455, 0.439 | Oxidized metal — gloss-compatible |

### Warm desaturated — amber / rust / tobacco

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Burnt amber | `#A6633D` | 0.651, 0.388, 0.239 | Rust-leaning warm |
| Dried tobacco | `#8A5A3D` | 0.541, 0.353, 0.239 | Brown-warm, anchoring |
| Brass ochre | `#B89958` | 0.722, 0.600, 0.345 | Yellow that reads metallic |
| Muted orange | `#C17A4E` | 0.757, 0.478, 0.306 | Broad warm |
| Dusty coral | `#B47368` | 0.706, 0.451, 0.408 | Pinkish warm — bridges to magenta |

### Mirror metallics (now first-class — gloss/metallic permitted)

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Tarnished silver | `#6E6E73` | 0.431, 0.431, 0.451 | Dim chrome, not jewelry-bright |
| Oxidized copper | `#6F4E3A` | 0.435, 0.306, 0.227 | Patinaed, organic |
| Bronze patina | `#5A5240` | 0.353, 0.322, 0.251 | Dimmer than copper |
| Pewter | `#8E8E94` | 0.557, 0.557, 0.580 | Pale metallic, reads as light |

### Pale / bone (highlights — no pure white ever)

| Swatch | Hex | RGB (0–1) | Note |
|--------|-----|-----------|------|
| Bone | `#C7BBA6` | 0.780, 0.733, 0.651 | Warm pale, tactile |
| Ash | `#948C9E` | 0.580, 0.549, 0.620 | Cool pale with violet bias |

### What's out (negative space)

- Pure neon: `#FF00FF`, `#00FFFF`, `#00FF00`, `#FFFF00` — never
- Glowstick / candy palettes (CMY-pop, electric pink, school-bus yellow)
- Safety orange, lime green, sky-blue cyan, holographic foil rainbow
- LED glow with the *hue* in the bright neon range. Glow may brighten the light, but the underlying hue stays in the palette.

### Color-Grading Pipeline

The old pipeline forced every visual to grayscale via `HSV Adjust (satmult=0.15)` then re-tinted through a purple ramp. **That mandate is dropped.** Two options now:

**A) Render in palette directly** (preferred when you control the source colors — PBR materials, GLSL shaders using palette `vec3`s, instance colors). Skip the Lookup. Just grade with:
```
[Source in palette] → Level TOP (16-bit float, blacklevel 0.05–0.08, gamma1 0.75–0.9, contrast 1.2–1.35, inhigh 0.85, outhigh 0.8 = no pure whites)
```

**B) Lookup-route a saturated/agnostic source through a Ramp** (use when the source is video / archive / any input not already in the palette, and you want to commit the scene to one color route). Build the Ramp from the swatch above:
```
[Source] → optional HSV Adjust (saturationmult 0.15 only here, when force-to-grayscale serves) → Level → Lookup TOP ← Ramp TOP (1024×1, Hermite, 16-bit float)
```

The Ramp is no longer purple-by-default. Common Ramp routes:
- **Purple monochrome** (`#000000` → `#190028` → `#2D0546` → `#5A0F78` → `#6B2E87`) — Act 1 / Act 5 / brand-anchor scenes
- **Oxidized-rust route** (`#0E0813` → `#2D0546` → `#6F4E3A` → `#A6633D` → `#B89958`) — warmth without going neon
- **Slate-mauve route** (`#000000` → `#1F1828` → `#3B4C73` → `#6B5C7A` → `#A085AE`) — twilight, cool-leaning psychedelic
- **Patina route** (`#0E0813` → `#1E505A` → `#4D6149` → `#5C7470` → `#7A8A6F`) — alien organic, deep-sea
- Build new routes per scene as needed — anchored in the swatch.

### Per-Act Color Affinities (suggestions, not rules)

Acts no longer have required/forbidden palettes. These are **starting points** — the act's emotional register pulls toward certain regions of the palette, but cross-borrowing is fine when it serves the moment.

| Act | Emotional register | Pulls toward |
|-----|---------------------|---------------|
| 1 — RIFT | Warm welcome, threshold opening | Foundation + purple spine + dusty rose / brass ochre / dusty lavender |
| 2 — DESCENSION | Inward pull, deepening | Deep purples + petrol / oxidized teal / dusk blue / charcoal mauve |
| 3 — ENCOUNTER | Confrontation, recognition | Off-black + petrol / wine magenta / patina / pewter / tarnished silver. Warmth not banned — but no warm relief; if warm is used, it should disturb (oxidized copper, dried tobacco), not comfort. |
| 4 — RELEASE | Cathartic discharge | Whole palette can activate; warm desaturated range (burnt amber, dusty coral, brass) and bright cools (Wobar cyan, slate blue) get pushed to peak. |
| 5 — INTEGRATION | Grounded return | Foundation + purple spine + bone/ash highlights — visual callback to Act 1 region |

### Transitions
**Switch TOP** (preferred): `blend` ON, floating-point index crossfades between inputs. Only cooks inputs being blended.
**Cross TOP**: set `cross` 0→1. Cooks both inputs always — use only for 2-scene crossfades.

---

## 5. Analog Grain Pipeline {#grain}

```
Noise TOP (512×512) → Blur TOP (1.5–3.0 Gaussian) → Level TOP (brightness −0.5)
→ Composite TOP (Add) with color-graded source
```

### Noise TOP Parameters
- `type` = Sparse (mimics silver halide crystal distribution)
- `mono` = ON (classic B&W grain)
- `offset` = 0.5
- `period` = 3–5 (16mm) or 5–10 (35mm)
- `harmonics` = 2–3
- `roughness` = 0.4–0.6
- `amplitude` = 0.05–0.12 (subtle 35mm) or 0.1–0.2 (heavy 16mm)
- **Transform Translate Z** = `absTime.seconds * 8` — walks noise space per frame. **Required for temporal variation** — without this, grain is static and looks fake.

**Generate at 512×512**, then upscale via Resolution TOP to output resolution. Full-resolution grain is too fine and digital.

Center grain around zero before composite: Level TOP `brightness1` = −0.5. Otherwise Add composite washes out image.

Composite modes: **Add** (standard), **Screen** (prevents highlight clipping), **Soft Light** (most natural film look).

---

## 6. Archive Footage Integration {#archive}

### Import
**Movie File In TOP** — `Play Mode` = Locked to Timeline. `interp` = ON for slow-motion smoothness. `hwdecode` = ON for NVIDIA GPU decoding. Use HAP Q codec for source footage in TD.

### Layering Modes
| Mode | Use for |
|------|---------|
| Over | Standard alpha layering |
| Inside | Circular crop (Input 1 = content, Input 2 = circle matte) |
| Add | Glowing generative elements over footage |
| Multiply | Grain / texture application |
| Screen | Lighter blend, no clipping |
| Soft Light | Subtle texture |

### Circular Crop (Portal Depth)
1. **Circle TOP** — `bgalpha` = 0, `radius` 0.35–0.45, `softness` 0.02–0.05 (sharp edge) or 0.15–0.3 (vignette)
2. **Composite TOP** (Inside) — Input 1 = footage, Input 2 = Circle

### Full Mirror-Frame Processing Chain
```
Movie File In → speed 0.25 (or Specify Index for variable)
→ HSV Adjust (satmult 0.15) — force the source toward grayscale before recoloring
→ Lookup TOP ← Ramp TOP (drawn from WOBAR palette §4 — pick a Ramp route that fits the act)
→ Level TOP (mild grade)
→ Composite Add (grain)
→ Composite Inside (Circle matte)
→ Null TOP
```

The `satmult=0.15 → Lookup → Ramp` route is the canonical recipe for **archive footage** specifically (where you want to override saturated source colors with the WOBAR palette). It is **not** required for native-rendered visuals — see §4 "Render in palette directly" for the alternative.

### Time Stretching
- **Simple**: Movie File In `speed` = 0.25, `interp` = ON
- **Variable**: Play Mode = Specify Index, drive `index` from Speed CHOP with audio input — footage scrubs with music

### Archive Sourcing by Act (from WOBAR_ARCHIVE.md)
- Act 1: Home movies, pastoral nature, golden hour, amateur astronomy (1940s–60s)
- Act 2: Underwater footage, root systems, cave footage, microscopy/cellular film
- Act 3: Medical/X-ray films, industrial machinery, oscilloscope/wave physics (Bell Labs)
- Act 4: Waterfalls, collective human movement, storms, early NASA footage
- Act 5: Same categories as Act 1 — intentional callback

Primary source: Internet Archive (archive.org). Sort ascending views to surface less-exhausted footage.

---

## 7. Scene Architecture + Timer Sequencing {#architecture}

### Project Structure
```
/ (root)
├── base_globals/          ← Audio analysis, color palettes, grain (shared)
├── base_act1/             ← Act 1 scene, outputs null_out
├── base_act2/
├── base_act3/
├── base_act4/
├── base_act5/
├── base_switcher/         ← Select TOPs + Switch TOP + null_final_out
├── base_timeline/         ← Timer CHOP + act boundary Table DAT
└── moviefileout1          ← Connected to null_final_out
```

Use **Base COMPs** (not Container COMPs). Each act outputs through a **Null TOP** named `null_out`. Use **Select TOP** to reference across containers without visible wiring.

### Timer CHOP Sequencing
Set `timecontrol` = **Lock to Timeline** for deterministic pre-rendered work.

Reference a **Table DAT** for segment lengths (seconds):
| delay | length | cycle | cyclelimit | maxcycles |
|-------|--------|-------|------------|-----------|
| 0 | 30 | 0 | 0 | 1 |
| 0 | 45 | 0 | 0 | 1 |
| ... | ... | ... | ... | ... |

Timer outputs `segment_index` (0–4) → export to Switch TOP `index`.

For a 2-hour Double Journey set, use the Double Journey percentage breakdown from WOBAR_FRAMEWORK.md.

### Switching
**Switch TOP** (preferred): `blend` ON. Only cooks inputs being blended. Set index to `op('timer1')['segment_index']`.

Transition types: cross-dissolve (animate index smoothly), fade-to-black (Level brightness 1→0, switch, 0→1), warp (Displace TOP during crossfade).

### Performance
Disable cooking on inactive scenes: `op('base_act3').cooking = False` in Timer CHOP callback. Saves significant GPU memory.

---

## 8. Export Settings {#export}

### Pre-Render Checklist
1. Turn OFF Realtime (top menu bar)
2. Rewind to frame 1
3. Confirm timeline end frame matches audio duration
4. Toggle Movie File Out Record ON
5. Press Play
6. When done: Record OFF → Realtime back ON

### YouTube (1920×1080)
| Parameter | Value |
|-----------|-------|
| videocodec | h264nvgpu |
| moviepixelformat | yuv420 |
| moviecontainer | mp4 |
| fps | `me.time.rate` |
| profile | high |
| avgbitrate | 8000 Kb/s (30fps) |
| peakbitrate | 12000–16000 |
| keyframeinterval | 15 |
| entropymode | cabac |
| Audio codec | AAC 320 kb/s |
| outputcolorspace | rec709 |

Master/archival: **ProRes 422 HQ** (.mov). YouTube accepts ProRes uploads directly.

### Instagram Reels (1080×1920)
| Parameter | Value |
|-----------|-------|
| Resolution | 1080 × 1920 |
| Container | mp4 |
| Video codec | H.264 (High profile) |
| Pixel format | yuv420p |
| fps | 30 |
| avgbitrate | **15000–25000 Kb/s** (feed the re-encoder) |
| keyframeinterval | 15 |
| Color tagging | bt709 primaries / bt709 transfer / bt709 matrix |
| Audio codec | AAC 320 kb/s, 48 kHz |
| Faststart | yes (`-movflags +faststart`) |

### TikTok (1080×1920)
| Parameter | Value |
|-----------|-------|
| Resolution | 1080 × 1920 |
| Container | mp4 |
| Video codec | H.264 (High profile) |
| Pixel format | yuv420p |
| fps | 30 |
| avgbitrate | **10000–12000 Kb/s** (8–13 Mbps acceptable) |
| keyframeinterval | 15 |
| Color tagging | bt709 primaries / bt709 transfer / bt709 matrix |
| Audio codec | AAC 256–320 kb/s, 48 kHz |
| Faststart | yes |

**Chroma 4:2:0 is platform-enforced on both IG and TikTok — cannot be avoided.** Mitigate with higher upload bitrate, Rec.709 end-to-end, 10-bit source, and grain.

### Safe Zones (cross-platform union)
Keep critical content inside these margins so it reads clean on both IG Reels and TikTok:
- **Top:** 250 px (username, audio attribution, status bar)
- **Bottom:** 440 px (caption, action buttons, audio track, TikTok UI is heavier than IG)
- **Right:** 100 px (like / comment / share column)
- **Left:** 0 px

Effective safe area: roughly the center **980 × 1230 px** of the 1080 × 1920 frame.

### Frame Rate
- **30fps** recommended for psychedelic bass music (fast audio-reactive movement, social-native)
- **24fps** for slower atmospheric sections, cinematic feel

**Match Movie File Out `fps` to project cook rate.** Default project = 60fps, default Movie File Out = 30fps — mismatch loses half the frames.

### Export Pipeline Decision

Three options. Choose by use case:

| Pipeline | Use for | Quality | Cost |
|----------|---------|---------|------|
| **A. MPEG 4 → HandBrake** | Iteration / preview only. Never post. | Low (2 encodes) | Free |
| **B. Commercial license → h264nvgpu direct** | Production default once license justified | High (1 encode) | ~$600 |
| **C. Image sequence → FFmpeg** | **Current posted exports on Free license** | Highest (0 encodes until assembly) | Free |

**Default on Free license: Pipeline C.** TD renders uncompressed frames to disk, FFmpeg does a single fully-controlled encode. Zero generational loss until the platform re-encode. MPEG 4 path is retired for anything that goes live.

### Pipeline C — Image Sequence Workflow

**TD side (Movie File Out TOP):**
- Type: Image Sequence
- Image File Type: PNG (16-bit) — start here. Use EXR only if banding survives.
- Filename: `frame_######.png` in a dedicated per-render subfolder
- Match project cook rate to 30 fps before rendering
- Allocate ~1 GB disk per 30s of 1080×1920 PNG 16-bit
- Render to NVMe SSD — HDD will bottleneck frame writes

**FFmpeg assembly (IG target, 18 Mbps CRF 18):**
```
ffmpeg -framerate 30 -i frame_%06d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -tune grain -x264-params "aq-mode=3:aq-strength=0.8" \
  -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart \
  output.mp4
```

Flag notes:
- `-crf 18` — quality-targeted, visually lossless vs source. Drop to 16 for max quality, raise to 20 for smaller files.
- `-preset slow` — slower encode, better compression efficiency
- `-tune grain` — preserves analog grain pipeline instead of smoothing it to mush
- `aq-mode=3, aq-strength=0.8` — adaptive quantization protecting dark areas and gradients
- `-colorspace/primaries/trc bt709` — explicit Rec.709 tagging, platforms don't second-guess
- `-movflags +faststart` — metadata at front of file for clean streaming upload

For TikTok target, change `-crf 18` to `-crf 20` (matches 10–12 Mbps) or leave at 18 (TikTok will re-encode down either way; feeding higher is harmless).

### Upload Protocol

**Both platforms: upload via desktop web uploader on stable WiFi > 20 Mbps.**

- **Instagram Reels:** instagram.com web uploader OR Meta Business Suite. The historical "mobile on WiFi beats desktop" advice has flipped as of 2026 — desktop web is now equal or better. If mobile is unavoidable, toggle "Upload at Highest Quality" (Settings → Account → Data Usage).
- **TikTok:** tiktok.com/upload (10 GB limit) OR TikTok Studio desktop app. Never mobile for anything important — app is 287 MB cap and cellular uploads get aggressive throttling.

**Never re-upload a downloaded or screen-recorded clip.** Compound compression is the fastest way to destroy a visualizer. Always upload the original master.

### Quality Mitigations

In priority order:

1. **Upload bitrate is the single biggest lever.** Platforms re-encode aggressively; starved sources band hard. Target 15+ Mbps for IG, 10+ for TikTok.
2. **Rec.709 SDR end-to-end.** No sRGB conversions, no HDR flags. Tag explicitly at FFmpeg stage.
3. **10-bit source through the TD pipeline** — render to 16-bit PNG, let FFmpeg dither on the 8-bit conversion. Protects gradients through the 4:2:0 bottleneck.
4. **Grain as banding protection (hypothesis, pending empirical test in Phase 4).** The analog grain pipeline may give the H.264 encoder something to latch onto instead of smooth gradient planes. `-tune grain` in FFmpeg preserves it through the master encode. Validate against Act 2 underwater gradient before trusting.
5. **Never compound-compress.** One encode at master stage, one re-encode at the platform. That's it.

---

## 9. Common Failure Patterns {#failures}

### Feedback chain goes white
- Level TOP opacity too high (>0.99) — lower to 0.89–0.97
- Scale too high (>1.1 for expansion) — reduce to 1.02–1.05
- Pixel format in 8-bit — switch to 16-bit float

### Feedback chain dies instantly
- Level TOP opacity too low (<0.85) — trails vanish immediately
- Scale exactly 1.0 — no motion, no feedback

### No feedback occurring
- Feedback TOP `targetop` not set — must point to downstream Null or Composite TOP

### Grain looks fake / static
- Missing temporal variation: Transform Translate Z must be `absTime.seconds * 8`
- Generated at full resolution — use 512×512 and upscale
- Not centering around zero: Level brightness −0.5 required before Add composite

### Audio not syncing to video
- Realtime was ON during render — must be OFF
- Audio File In not set to Locked to Timeline
- Project cook rate ≠ Movie File Out fps

### Resolution inconsistency
- Generator TOPs default to 256×256 — always check Common page
- Different resolutions in Composite TOP cause unexpected stretching

### Color banding in dark purples
- Pixel format is 8-bit — switch Ramp TOP and Level TOP to 16-bit float

### Spiral pulls outward instead of inward
- Transform `sx`/`sy` is >1.0 — must be <1.0 for inward (0.98–0.995)

### Act 3 accidentally feels cathartic
- Warm colors present — remove completely
- Symmetry too perfect (100%) — partial mirror should be 85–90%
- Rotation too smooth — add Noise-driven jitter
