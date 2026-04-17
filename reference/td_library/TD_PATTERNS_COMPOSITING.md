---
title: Compositing Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Layer stacks, blend modes, mattes, keying, post FX chains, final look assembly.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_TOP.md
---

# COMPOSITING PATTERNS

Compositing is how independent visual elements (scenes, overlays, text, effects) come together into the final frame. The mechanics live in TOPs — Composite TOP, Layer Mix TOP, Matte TOP, Chroma Key TOP — plus the post stack.

---

## Two Compositing Paradigms

### Paradigm A — Composite TOP chain (legacy)
```
A ──► Composite (Over) ◄── B
         ──► Composite (Over) ◄── C
             ──► Composite (Over) ◄── D
```
- Each pair-wise composite explicitly.
- Clear wiring, but verbose at 5+ layers.

### Paradigm B — Layer Mix TOP (2025, preferred)
```
Layer Mix TOP:
  - Input 0: Background
  - Input 1: Layer A (Mode = Over, Opacity = 1.0)
  - Input 2: Layer B (Mode = Add, Opacity = 0.8)
  - Input 3: Text overlay (Mode = Over, Opacity = 1.0)
```
- Photoshop-style layer stack in one node.
- Per-layer Opacity, Mode, Pre-Mult toggle.
- **Use for anything >2 layers.**

---

## Blend Modes — What They Do

Assuming Layer A = base, Layer B = top:

| Mode | Formula | Use |
|------|---------|-----|
| Over | B + A*(1-Bα) | Standard alpha composite |
| Add | A + B | Glow, additive light |
| Multiply | A * B | Shadow, darkening, tinting |
| Screen | 1 - (1-A)*(1-B) | Brightening without blowout |
| Difference | abs(A - B) | Comparison, psychedelic |
| Subtract | A - B | Darkening |
| Max | max(A, B) | Keep brightest pixel |
| Min | min(A, B) | Keep darkest pixel |
| Inside | A where Bα > 0 | Use B as mask for A |
| Outside | A where Bα == 0 | Inverse mask |
| Divide | A / B | Rare; dehaze |
| Darken / Lighten | channel-wise min / max | Per-channel selection |

### Common uses
- **Over** — UI, text, any alpha overlay.
- **Add** — glow, light trails, emissive.
- **Multiply** — vignette, shadow, color tinting.
- **Screen** — ambient light, stacked glows.
- **Max** — keep bright detail from multiple passes (common in generative).
- **Difference** — psychedelic two-layer patterns.

---

## Alpha Handling — Premultiplied vs Straight

- **Straight alpha**: RGB stores the color, A stores the mask.
- **Premultiplied alpha**: RGB is already multiplied by alpha.

Convention in TD: most TOPs work premultiplied internally. Imports from PNGs (straight alpha) are often converted automatically, but check if edges look wrong.

### Fix
Composite TOP → Common tab → Pre-Multiply RGB by A / Post-Divide.
Toggle on/off until edges look right.

---

## Mattes and Masks

### Mask as alpha
A grayscale TOP → used as alpha source for another TOP via Matte TOP or Composite with alpha override.

### Matte TOP
- Inputs: RGB, Alpha source.
- Combines them into a matted texture.
- Use: take a full-color Render and mask with a custom shape.

### Mask as Composite Inside/Outside
```
Image ──► Composite (Mode = Inside, Mask = B) ──► Out
```
Image only shows where B has alpha > 0.

---

## Chroma Key

### Chroma Key TOP
Inputs: source footage + key color.
- Params: Key Color, Tolerance, Softness, Spill Suppress.
- Use: green screen, blue screen.

### Workflow
1. Video Device In / Movie File In TOP — footage.
2. Chroma Key TOP — pick the green, tune tolerance.
3. Layer Mix TOP — composite over new background.
4. Spill suppress reduces green tint on subject edges.

### Non-green keying
- Color-based keying for any dominant color.
- Luma keying for dark/light backgrounds — use Threshold TOP + Level TOP instead.

---

## Layering Strategy

### Typical scene stack (bottom to top)
1. **Background** — solid color, or slow noise, or gradient.
2. **Hero scene** — main 3D/generative render.
3. **Atmosphere** — fog, dust, light rays (additive).
4. **UI / text** — lyric, title, overlays (Over mode).
5. **Global post** — Bloom, Chromatic Aberration, Film Grain, Level.

### Post at the top, not per-layer
Global post runs on the composited output, not on each layer. Cheaper and more consistent look.

```
Layer Mix (background, scene, atmosphere, UI) ──► Null "null_composite"
                                             ──► Bloom → Chromatic → Grain → Level ──► Out
```

---

## Post FX Stack — Canonical Order

The order matters. Canonical sequence for a music video:

```
null_scene ──► Bloom (highlight glow)
            ──► Chromatic Aberration (lens fringing)
            ──► Lens Distort (barrel, subtle)
            ──► Vignette (Ramp TOP + Composite Multiply)
            ──► Film Grain
            ──► Level (final color/contrast/gamma)
            ──► Out
```

### Why this order
- **Bloom first** while highlights are intact.
- **Chromatic after Bloom** — fringing applies to the bloom glow.
- **Lens Distort / Vignette** — simulate physical lens.
- **Grain last (before final Level)** — grain applies to everything including effects.
- **Level last** — global color grade after all effects.

---

## Color Grading

### Level TOP
- Blacklevel, Whitelevel — contrast.
- Gamma — midtone shift.
- Saturation, Hue — color.
- Brightness — overall exposure.
- Opacity — final fade.

### Lookup TOP with Ramp
For film-look grading, use a custom Ramp TOP as the LUT and Lookup TOP applies it:
```
Scene ──► Lookup TOP (Lookup Input = custom ramp) ──► Out
```
Or load an external LUT via File In TOP.

### HSV Adjust TOP
Hue shift pipeline — rotate the entire color wheel by N degrees.

### Channel Mix TOP
Per-channel source remapping. Hollywood orange-teal grade = R boost, B shift to teal.

---

## Practical Composite Patterns

### Pattern 1 — Hero scene + slow-moving background
```
Noise TOP (slow, warm) ──► Blur ──► Null "bg"
Scene Render TOP ──► Null "scene"

Layer Mix:
  Input 0: bg
  Input 1: scene, Mode = Over
──► Post stack
```

### Pattern 2 — Two layers with audio-reactive blend
```
Layer A: Act 2 scene
Layer B: Act 3 scene

Cross TOP (fade = null_audio_transition) ──► Out
```

### Pattern 3 — Picture-in-picture
```
Full scene ──► Null
Sub scene  ──► Fit TOP (crop/resize) ──► Layer Mix (at corner, Over mode)
```

### Pattern 4 — Title card over live scene
```
Render scene ──► Null "scene"
Text TOP "WOBAR" ──► Null "title"

Layer Mix:
  Input 0: scene
  Input 1: title, Mode = Over, Opacity = 1.0
```

### Pattern 5 — Additive glow stack
```
Scene ──► Null "scene"
Bloom high-threshold ──► Level (boost) ──► Null "hot_glow"
Bloom low-threshold  ──► Level (boost) ──► Null "ambient_glow"

Layer Mix:
  Input 0: scene (base)
  Input 1: ambient_glow, Mode = Add, Opacity = 0.5
  Input 2: hot_glow, Mode = Add, Opacity = 1.0
```

### Pattern 6 — Mask-based split
```
Circle TOP (radial gradient) ──► Null "mask"

Layer Mix:
  Input 0: Layer A (full frame)
  Input 1: Layer B, Mode = Over, uses mask as alpha
```
Layer B only visible inside the circle.

### Pattern 7 — Feedback layer (composite with time)
```
Current scene ──► Feedback via Composite → trails pattern from TD_PATTERNS_FEEDBACK.md
```

---

## Mac-Specific Compositing Notes

- Most TOPs are 16-bit float — wide dynamic range.
- Bloom + Add composites can overflow to HDR — final Level before output clamps / tone-maps.
- ProRes 4444 supports alpha export; 422 does not. See `TD_APPLE_SILICON.md` §3.

---

## Performance

- Composite TOP is cheap — O(pixels).
- Layer Mix TOP is cheap — same cost as a Composite chain.
- Chroma Key TOP is medium — per-pixel color math.
- Bloom is expensive at high spread — use moderate spread + high threshold.
- Chromatic Aberration at high aberration value requires more samples; cheaper when subtle.
- Film Grain is cheap.
- Level is cheap.

---

## Reading This File

Start with Blend Modes table and Layering Strategy. For specific recipes, jump to Practical Composite Patterns. Post stack order is opinionated but proven — start with the canonical order, then tune.
