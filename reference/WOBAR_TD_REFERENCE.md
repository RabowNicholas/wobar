# WOBAR TouchDesigner Reference
*Technical reference for building WOBAR visualizers. Read by the coaching skill as needed — not meant to be read top to bottom.*

---

## Table of Contents
1. [Operator Family Quick Reference](#operators)
2. [Audio Pipeline](#audio)
3. [Visual Primitives by Act](#primitives)
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

### Import
**Audio File In CHOP** — set `File` to WAV path. `Play Mode` = **Locked to Timeline** (mandatory for deterministic render). Always use WAV, not MP3.

### Frequency Band Extraction
Four parallel **Audio Filter CHOPs** from same Audio File In:

| Band | Type | Center/Cutoff | Q | Channel Name |
|------|------|---------------|---|--------------|
| Sub-bass | Band Pass | 50Hz | 0.7 | `sub_bass` |
| Bass | Band Pass | 150Hz | 0.8 | `bass` |
| Mid | Band Pass | 1000Hz | 0.5 | `mid` |
| High | High Pass | 4000Hz | — | `high` |

After each filter: **Analyze CHOP** → Function = **RMS Power**. Then **Merge CHOP** combines all four.

For sub-bass pressure (continuous rumble): add Filter CHOP after Analyze, Low Pass cutoff 5Hz.

### Smoothing
**Lag CHOP** — separate `Lag Up` and `Lag Down`:
- Sub-bass breath: Up 0.05s, Down 0.3s
- Kick hits: Up 0.005s, Down 0.15s
- Hi-hats: Up 0.001s, Down 0.05s

**Math CHOP** — remap range: `From Range` (e.g., 0–0.3 typical RMS) → `To Range` (e.g., 0.5–3.0 for scale). Enable Clamp. Power ~0.5 compresses range.

### Beat Detection
**Beat CHOP** — Low/High Freq = 40–150Hz for kicks. Threshold ~0.5. Min Period ~0.3s for 140 BPM. Outputs 0 or 1 triggers.

Use **Speed CHOP** (Differentiate) for transient-only triggering.
Use **Threshold CHOP** → **Trigger CHOP** (attack 0.01s, sustain 0.1s, release 0.5s) for audio-peak-only effects.

### Mapping Expressions
```python
# Scale breathing (sub-bass)
0.5 + op('null_audio')['sub_bass'] * 2.5

# Feedback opacity (bass)
0.88 + op('null_audio')['bass'] * 0.11

# Displacement intensity (mid)
op('null_audio')['mid'] * 0.5

# Flash on kick
op('null_audio')['kick_trigger']
```

### Full Audio Chain
```
Audio File In (WAV, Locked to Timeline)
  ├→ Audio Filter (BP 50Hz) → Analyze (RMS) → Lag → "sub_bass"
  ├→ Audio Filter (BP 150Hz) → Analyze (RMS) → Lag → "bass"
  ├→ Audio Filter (BP 1kHz) → Analyze (RMS) → Lag → "mid"
  ├→ Audio Filter (HP 4kHz) → Analyze (RMS) → Lag → "high"
  └→ Beat CHOP → Threshold → Trigger → "kick"
→ Merge CHOP → Math CHOP → Null CHOP (export point)
```

---

## 3. Visual Primitives by Act {#primitives}

### CIRCLE / VIGNETTE — Act 1 + Act 5

**Portal-open / portal-close. Breath rhythm 60–80 BPM equivalent.**

Build (Multiply mask method):
1. **Circle TOP** — `radius` 0.45 (Fraction), `softness` 0.25–0.4, fill white, bg black
2. **Composite TOP** (Multiply) — circle × content. White center passes through, black edges darken.

Build (circular crop method):
1. **Circle TOP** — `bgalpha` = 0 (transparent bg), `softness` 0.02–0.3
2. **Composite TOP** (Inside) — Input 1 = content, Input 2 = Circle. Crops to circle's alpha.

Audio-reactive breath:
- **LFO CHOP** (Sine, 1.0–1.33Hz for 60–80 BPM) → Math CHOP (0–1 → 0.35–0.55) → Export to `circle1/radiusx` + `circle1/radiusy`
- Sub-bass Analyze → Lag (0.3s) → Export to `radius` and `softness`

Act 5 note: same build as Act 1. The visual callback is intentional — same footage category, different emotional weight.

---

### INWARD SPIRAL — Act 2

**Pulling inward. Something descending. Audio tightens the spiral.**

Core feedback loop:
```
Feedback TOP → Transform TOP → Level TOP → Composite TOP → Null TOP
                                                ↑
                                        [New content source]
Feedback TOP: targetop = null_out (downstream)
```

Parameters:
- **Transform TOP**: `rotate` = 0.5–3.0° (constant per frame), `sx`/`sy` = **0.98–0.995** (must be <1.0 for inward pull), `bgcolor` = black
- **Level TOP**: `opacity` (Post tab) = 0.89–0.98. Controls trail length. Lower = shorter trails. **Critical — too high = white-out.**
- **Composite TOP**: Operation = Over or Add

Audio reactivity:
- Bass → rotation speed: `absTime.seconds * (5 + op('null_audio')['bass'] * 20)`
- Bass → scale: `1.0 - (op('null_audio')['bass'] * 0.05)` → 1.0 silent, 0.95 loud

Depth illusion: **Displace TOP** with radial **Ramp TOP** (center white, edge black) as displacement map. `displaceweight` controls pull intensity.

**Use 16-bit float pixel format** in feedback chain. Prevents banding in dark purples.

---

### TUNNEL + MIRROR DISTORTION — Act 3

**Infinite depth. Confrontation. 85–90% symmetry with meaningful asymmetry. No warm colors.**

Tunnel build: same as spiral but `scale` ~0.98, `rotate` 0–0.5°. Add new content at **edges** (use inverted Circle TOP as mask — `bgalpha` = 1, `fillalpha` = 0).

Partial mirror (85–90% symmetry):
- Source → **Flip TOP** (`flipx` = on) → **Level TOP** (opacity 0.85–0.90) → **Composite TOP** (Over or Average) with original
- OR: **Cross TOP** with `cross` value 0.85–0.90

Glitch/stutter:
- **Cache TOP + Cache Select TOP** — drive `index` with random CHOP for frame stuttering
- **Displace TOP + Noise TOP** — `displaceweight` 0.01–0.05 subtle, 0.1–0.5 aggressive. Animate Noise `period` and `amplitude`
- Trigger glitch on audio peaks via Threshold CHOP — not constantly

Impossible geometry: Feedback → Transform (scale 0.95, rotate 3°) → Tile TOP (2×2 mirror) → Composite → back to Feedback. Creates fractal recursion.

Act 3 rule: **no emotional relief, no warm colors, no vocals**. This act does not comfort.

---

### RADIAL EXPLOSION — Act 4

**Cathartic release. Outward expansion. Full color palette activates. Heavy but held.**

Core feedback loop (reverse of spiral):
```
Feedback TOP → Transform TOP (sx, sy = 1.02–1.05) → Level TOP (opacity 0.90–0.97) → Composite TOP → Null TOP
                                                                                           ↑
                                                                                   [Center content]
```

Parameters:
- Transform `sx`/`sy` = **1.02–1.05** (>1.0 = outward expansion)
- Level opacity 0.90–0.97 (fast-fading trails for explosive feel)
- HSV Adjust TOP in feedback chain with slight `hueoffset` per frame = rainbow expanding rings

Audio peak triggering:
```
Analyze CHOP → Threshold (0.7–0.8) → Trigger (attack 0.01s, sustain 0.1s, release 0.5s)
→ Math (0–1 → 1.0–1.15 for scale, or 0–1 → 0.5–2.0 for brightness)
→ Lag → Export to Transform sx/sy and Level brightness
```

Act 4 is cathartic release — heavy but held. Rhythm exists. This is not chaos.

---

## 4. Color System + Palette Values {#color}

### The Core Pipeline
```
[Source] → HSV Adjust TOP → Level TOP → Lookup TOP ← Ramp TOP (1024×1, 16-bit)
```

### HSV Adjust TOP
- `saturationmult` = 0.15 (nearly grayscale base)
- `valuemult` = 0.8–0.85
- `hueoffset` — minimal effect on near-grayscale content; use Lookup instead for tinting

### Level TOP (use 16-bit float pixel format)
- `blacklevel` = 0.08 (kills noise)
- `gamma1` = 0.75 (darkens midtones)
- `contrast` = 1.3–1.35
- `inhigh` = 0.85, `outhigh` = 0.8 (no pure whites)

### Ramp TOP (palette map — 1024×1, Hermite interpolation, 16-bit float)
Base purple palette keyframes:

| Position | RGB (0–1) | Hex | Role |
|----------|-----------|-----|------|
| 0.00 | 0.0, 0.0, 0.0 | #000000 | Black base |
| 0.15 | 0.098, 0.0, 0.157 | #190028 | Deep purple dark |
| 0.50 | 0.176, 0.02, 0.275 | #2D0546 | Deep purple mid |
| 0.85 | 0.353, 0.059, 0.471 | #5A0F78 | Purple highlight |
| 1.00 | 0.4, 0.1, 0.5 | #661A80 | Top |

### Act-Specific Accent Colors

| Act | Accent | RGB (0–1) | Hex | How to add |
|-----|--------|-----------|-----|-----------|
| Act 1 | Warm purple glow | 0.392, 0.118, 0.353 | #641E5A | Blur TOP (15–25) → Level (brightness 0.1) → Composite Add |
| Act 2 | Muted cyan | 0.118, 0.314, 0.353 | #1E505A | Constant TOP → Composite Screen, alpha 0.08–0.15, drive with sub-bass |
| Act 3 | Muted magenta | 0.353, 0.059, 0.255 | #5A0F41 | HSV Adjust hueoffset 320°. Kill warm: second HSV Adjust targeting orange, satmult 0.0 |
| Act 4 | Warm orange | 0.706, 0.314, 0.078 | #B45014 | Constant TOP, alpha driven by kick analysis. All accents active simultaneously. |
| Act 5 | Return to purple | — | — | Timer/LFO fades warm/cyan opacity → 0. Returns to Act 1 palette. |

### Act Transitions
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

### Full Portal Processing Chain
```
Movie File In → speed 0.25 (or Specify Index for variable)
→ HSV Adjust (satmult 0.15)
→ Level TOP (purple palette tint)
→ Composite Add (grain)
→ Composite Inside (Circle matte)
→ Null TOP
```

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

### TikTok / Instagram (1080×1920)
| Parameter | Value |
|-----------|-------|
| Resolution | 1080 × 1920 |
| videocodec | h264nvgpu |
| moviepixelformat | yuv420 |
| fps | 30 |
| avgbitrate | 10000–12000 Kb/s |
| Audio codec | AAC 256–320 kb/s |

TikTok: upload via web browser (10 GB limit), not mobile (287 MB limit). Keep key content in center 60% of frame — platforms overlay UI at top ~250px and bottom ~340px.

### Frame Rate
- **30fps** recommended for psychedelic bass music (fast audio-reactive movement, social-native)
- **24fps** for slower atmospheric sections, cinematic feel

**Match Movie File Out `fps` to project cook rate.** Default project = 60fps, default Movie File Out = 30fps — mismatch loses half the frames.

### Free License Limitation
H.264/H.265 requires Commercial or Pro license + NVIDIA GPU. Free license: render to MPEG 4, then transcode via HandBrake.

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
