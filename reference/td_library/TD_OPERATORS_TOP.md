---
title: TOPs — Texture Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every TOP in TD 2025.32460. GPU textures — the visual backbone.
dependencies: TD_LIBRARY_INDEX.md, TD_APPLE_SILICON.md, TD_NETWORK_VS_GLSL.md
---

# TOPs — TEXTURE OPERATORS CATALOG

TOPs are **2D GPU textures**. Every visual ends up through TOPs. They are the most-used operator family in TD.

**Core facts:**
- Each TOP holds a GPU texture with a resolution, pixel format, and colorspace.
- TOPs render via Vulkan → Metal (MoltenVK) on Mac; see `TD_APPLE_SILICON.md`.
- Resolution capped at 1280 on either axis on Non-Commercial license.
- Default pixel format is 16-bit float RGBA (good dynamic range; slightly slower than 8-bit). Set 8-bit for post stages where HDR isn't needed.

---

## Resolution, Format, and Colorspace — Read This First

Every TOP exposes on its Common page:

- **Resolution** — fixed or Use Input. Set explicitly where possible.
- **Pixel Format** — 8-bit RGBA (fast), 16-bit float RGBA (HDR default), 32-bit float (precision-heavy). Use 16-bit for HDR feedback, 8-bit for final display.
- **Colorspace** — sRGB vs Linear. TOPs operate in linear internally; import/export do gamma conversion. Mismatched colorspace is the #1 cause of "why is this so dark / so washed out."
- **Cook Type** — Selective by default. Only set Always for source TOPs that read time-varying external state (cameras, NDI, etc.).

---

## Generators

### Constant TOP
Solid color fill.
- Params: Color RGBA, Resolution.
- Use: background, mask base, alpha fill.

### Ramp TOP
Linear / radial / circular gradients.
- Params: Keys (color stops), Type (linear/radial/circular/spiral), Phase, Angle.
- Use: backgrounds, ramps for Lookup TOP, soft masks.

### Noise TOP
GPU noise texture — Perlin, Simplex, Sparse, Alligator, Random, Hermite.
- Params: Type, Translate, Resolution, Amplitude, Period, Seed, Harmonics (octaves), Clamp.
- Use: organic motion, displacement source, breakup texture.
- **On M1:** fine at 1280², starts to stress with 4+ harmonics at 16-bit.

### Circle TOP
Single circle / ring primitive.
- Params: Center, Radius, Softness, Color, Border.
- Use: spotlights, masks, vignettes.

### Rectangle TOP
Rectangle with adjustable corner radius.
- Params: Size, Corner Radius, Border.
- Use: UI elements, banners, masks.

### Tri TOP
Triangle / regular polygon primitive.
- Params: Sides, Radius, Rotation.

### Checker TOP
Checkerboard pattern.
- Use: test textures, UV debugging.

### Null TOP (as source)
Passthrough — no visual of its own unless given input.

### Text TOP
Renders text as a texture.
- Params: Text, Font, Size, Alignment, Border, Fill, Outline.
- On Mac: color fonts/emoji fall back to outline-only — use Text SOP with a font atlas for color emoji.

---

## Input / Source TOPs

### Video Device In TOP
Captures from webcam / capture card via AVFoundation on Mac.
- Params: Device, Resolution, Format.
- Use: live camera input.

### NDI In TOP
Receives NDI stream.
- Caveat: NDI on M1 Apple Silicon can be unstable — verify per session.

### Syphon In TOP
Receives Syphon stream (Mac-native inter-app texture sharing).
- Caveat: Syphon path in TD 2025.x on Mac has intermittent issues; see `TD_FOOTGUNS.md`.

### Touch In TOP
Receives texture from another TD instance via TD's own protocol.

### Screen Grab TOP
Captures a region of the desktop.

### Kinect TOP / Kinect Azure TOP
Depth/RGB stream from Kinect/Orbbec devices.
- On M1: use Orbbec sensors with Orbbec SDK; Azure Kinect not supported on Mac.

### Movie File In TOP
Plays back a video/image file.
- Params: File, Play, Speed, Cue, Trim, Color Space.
- Use the Extend Left/Right params to loop.

### Web Render TOP
Renders a webpage as a texture.
- Use: embed web-based widgets, lyrics display.

### Render TOP
The canonical 3D render output — camera + lights + geometry → texture.
- Required inputs: Camera COMP, Light COMP, Geometry COMP.
- Common tabs: Common, Quality, Render, Output.
- See `TD_PATTERNS_3D_SCENES.md`.

### Render Pass TOP
Extra render pass on top of a Render TOP — for multi-pass effects (stencil, different camera, etc.).

### Render Simple TOP (new in 2025)
A simplified, single-operator render path — Geometry + Camera in one node.
- Use: quick renders without plumbing camera/lights/geometry as separate COMPs.

---

## Output / Sink TOPs

### Out TOP
Marks an output point inside a COMP.

### Null TOP
Named passthrough; preferred output endpoint at every layer.

### Composite TOP output role — see Compositing section.

### Movie File Out TOP
Records to disk.
- On Mac Non-Commercial: **ProRes** is the workable codec; H.264/H.265 gated.
- See `TD_APPLE_SILICON.md` §3 and `TD_WORKFLOW_EXPORT.md`.

### NDI Out TOP
Emits NDI stream — unstable on M1.

### Syphon Out TOP
Emits Syphon stream — intermittent on macOS in 2025.

### Touch Out TOP
Emits texture for Touch In in another TD instance.

### Window COMP (not a TOP, but the output sink)
Displays a TOP to a physical window / monitor.

---

## Filters and Color

### Level TOP
Color correction — brightness, contrast, gamma, opacity, range.
- Most used: Opacity on Post tab — controls decay in feedback loops.
- Also: Blacklevel, Whitelevel, Gamma, Saturation, Hue.
- Use: fundamental color shaping; the other 80% of color work happens here.

### Lookup TOP
Reads input values as coordinates into a lookup texture (1D or 3D LUT).
- Inputs: Input 1 = image, Input 2 = lookup texture (often a Ramp TOP).
- Use: color grading via ramps, custom gradient remaps, LUT application.

### Channel Mix TOP
Per-channel source-channel remapping — e.g., R = 0.5R + 0.5B.
- Use: hue shifts by channel math, channel swaps.

### HSV Adjust TOP
Hue / Saturation / Value shift.
- Use: pipeline-level color grading; quick hue animation.

### Color Map TOP / Cross Chart TOP / Ramp TOP (as source for Lookup)
Build LUT source textures.

### Threshold TOP
Binary threshold on value.
- Params: Threshold, Softness, Invert.
- Use: masks from luminance.

### Fit TOP
Remap input range to output range.
- Use: normalize before feeding a downstream operator that expects 0–1.

### Math TOP
Per-pixel math — add/sub/mul/div; or multi-operand math with other TOPs.
- Use: scaling brightness, combining masks, difference maps.

### Function TOP
Applies a math function (sin, pow, abs, etc.) per pixel.
- Use: curves, easing, value shaping.

### Limit TOP
Clamp values to a range.

### Remap TOP
UV remapping using an input remap texture.
- Use: warping via a displacement map; procedural UV distortion.

---

## Transform / Warp

### Transform TOP
Translate / Rotate / Scale / Pivot / Extend on a 2D texture.
- Most critical post-feedback operator.
- Extend modes: Hold, Zero, Repeat, Mirror — affects how edges behave.

### Fit TOP (geometry)
Fit texture to new aspect / resolution with letterbox / crop options.

### Flip TOP
Flip horizontal / vertical / both.

### Crop TOP
Crop to a rect.

### Resolution TOP
Change resolution (up/down sample).
- Use: downsample before feedback for cost; upsample at end.

### Slope TOP
Linearly warp — shear.

### Corner Pin TOP
4-point perspective warp — classic projection mapping building block.

### Displace TOP
Offset pixels using a displacement map (R=x, G=y).
- Use: waves, heat distortion, turbulence.

### Warp TOP
Grid warp (N×M control points) for more complex non-linear warping.
- Use: freeform projection mapping, organic distortion.

### Project TOP
Projects a texture onto geometry using UVs from a render pass.

### Cache TOP / Cache Select TOP
Buffer frames and recall by index.
- Use: time-based trails, delay effects, beat-synced replay.

---

## Compositing

### Composite TOP
Combines two TOPs via a blend mode.
- Modes: Over, Add, Multiply, Screen, Difference, Subtract, Max, Min, Inside, Outside, plus alpha variants.
- Inputs: Background (operand A), Foreground (operand B).
- Common: alpha-compositing layered scene elements.

### Layer Mix TOP (new in 2025)
Multiple inputs, blend modes per layer, opacity per layer — like a Photoshop layer stack.
- **Replaces cascades of Composite TOPs** in most cases.
- Params: per-input Opacity, Mode, Pre-Mult toggle.
- Use: final compositing stacks, UI overlay layers.

### Matte TOP
Alpha matte combining.

### Chroma Key TOP
Green-screen / color-based keying.
- Params: Key Color, Tolerance, Softness, Spill Suppress.

### Luma Blur TOP
Blur based on a luma mask — blur more where bright, less where dark (or inverse).

### Blur TOP
Gaussian blur.
- Params: Size, Extend.
- Cost: O(radius²) non-separable. Use Luma Blur or stacked small blurs for cost.

### Edge TOP
Edge detection.
- Params: Strength, Mode (Sobel, etc.).

### Bloom TOP
Bright-region glow.
- Params: Threshold, Spread, Intensity.
- Use: final-pass glow; hide in post stacks.

### Chromatic Aberration TOP
RGB channel offset by distance from center.
- Params: Aberration Amount, Center.
- Use: psychedelic edge fringing, lens emulation.

### Film Grain TOP
Noise grain overlay.

### Lens Distort TOP
Barrel / pincushion distortion.

### Vignette (via Ramp TOP + Composite Multiply)
Not a dedicated op — build with a radial Ramp TOP + Composite Multiply.

---

## GPU Shader / Render

### GLSL TOP
Single-output fragment shader.
- Params: GLSL code, Input TOPs, Uniforms (Vectors/Arrays/CHOPs), Resolution.
- Use: custom per-pixel math not covered by stock TOPs.
- On Mac: avoid geometry shader stages. See `TD_APPLE_SILICON.md` §1 and `TD_NETWORK_VS_GLSL.md`.

### GLSL Multi TOP
Up to 32 output buffers from one shader.
- Use: G-buffer-style multi-target shaders; multi-pass compositing in one pass.

### GLSL Compute TOP
Compute shader writing to a texture.
- Use: work that doesn't fit a fragment shader (scatter, per-tile aggregation).

### Render TOP — see Input/Source section.
### Render Pass TOP — see Input/Source section.

### Render Select TOP
Picks a specific pass/buffer from a multi-output render.

---

## Feedback / Temporal

### Feedback TOP
Reads back the previous frame's output — the core of trails, tunnels, decay effects.
- Params: Target TOP (where it reads from, usually itself's downstream chain), Resolution, Extend.
- **Critical pairing:** Level TOP opacity < 1.0 to attenuate; otherwise goes white.
- See `TD_PATTERNS_FEEDBACK.md`.

### Trails TOP
Simpler alternative to Feedback + Composite — motion trails with a decay parameter.
- Use: quick trails without wiring a feedback loop.

### Temporal Blur TOP / Motion Blur TOP
Motion-aware blurring — across consecutive frames.

### Frame Blur TOP
Blends over recent N frames.

### Cache TOP / Cache Select TOP (temporal role)
See Transform/Warp — also serves as frame delay.

---

## Analysis

### Analyze TOP
Readback — reduces texture to scalar(s). RMS, Mean, Min, Max, Sum, Median over a region.
- Output: a CHOP-friendly scalar, readable via `Analyze TOP → CHOP` chain.
- **Costly** — GPU→CPU readback. Use sparingly.

### Histogram TOP
Computes histogram of an input.
- Use: exposure/curves analysis; level controls driven by content.

### Optical Flow TOP
Computes motion vectors between consecutive frames.
- Use: motion-driven effects, warping by motion.

### Delta TOP
Difference between consecutive frames.
- Use: motion detection, change masks.

### Feedback Analysis — via Analyze on Feedback output
Feed an Analyze TOP with the feedback frame to detect saturation and drive adaptive opacity.

---

## Text & UI TOPs

### Text TOP — see Generators.
### Text SOP → Render → TOP path — use for complex typography, path data, per-character animation; Text SOP is preferred over Text TOP when you need glyph-level control.

### UI TOPs (in Palette / official extras)
Slider, Button, Switch widgets — for in-project control surfaces.

---

## Capture / Stream TOPs

### Screen Grab TOP — see Input.
### Video Device In TOP — see Input.
### NDI In/Out — see Input/Output.
### Syphon In/Out — see Input/Output.

---

## Anti-Aliasing / Sampling

### FXAA TOP
Fast approximate AA on a rendered image.

### Multisample TOP / Temporal Antialiasing
Attached to Render TOP for AA during rendering.

### MSAA on Render TOP
Render TOP → Common tab → Antialias = 2×, 4×, 8×.

---

## Special / Utility

### Ring TOP
Annulus (hollow ring) primitive.

### SVG TOP
Vector graphics (SVG) source — resolution-independent.

### Substance TOP
Substance Designer file loader. Generate textures procedurally from .sbsar.

### Voodoo TOP / Magnet TOP / Kaleidoscope TOP
Specialty warps/distortions.

### Point File In TOP
Reads point cloud files as 2D TOP layouts.

### PBR / Environment Map TOPs
Various utilities for PBR workflows.

---

## Network Operators

### Select TOP
Pulls a TOP from elsewhere by name.

### Switch TOP
Switches between N inputs by index.

### Cross TOP
Dissolves between two inputs (simple alpha cross-fade).

### In TOP / Out TOP
COMP I/O — used inside Base COMPs.

---

## ST 2110 (new in 2025)
SMPTE ST 2110 professional broadcast video I/O (uncompressed over IP).
- Specialized — relevant only for broadcast-grade installations.

---

## Canonical TOP Chains

### Basic visual → output
```
Source TOP ──► Level ──► Transform ──► Bloom ──► Level ──► Out
```

### Feedback core
```
Source ──► Composite (Over, A = Source, B = feedback) ──► Null ("null_frame")
              ▲                                              │
              └─── Feedback TOP ◄── Transform ◄── Level ◄────┘
```

### 3D render + post
```
Geo + Cam + Light ──► Render TOP ──► Null ──► Bloom ──► Chromatic ──► Level ──► Out
```

### Audio-reactive color grade
```
Render ──► Lookup (grade ramp driven by audio) ──► Bloom ──► Out
           ▲
           └── Ramp TOP (colors drive by Audio RMS)
```

### Live VJ input → post → output
```
Video Device In ──► Level ──► Chroma Key ──► Layer Mix (w/ background) ──► NDI Out
```

---

## TOP Performance Notes

- 16-bit float RGBA is default; 8-bit for final/display halves memory bandwidth.
- Feedback TOP at 1280² at 16-bit is the single biggest budget eater — downsample before it.
- Blur TOP at large radius is non-separable — use Luma Blur or stacked small blurs.
- GLSL TOPs at full resolution with many texture samples can exceed frame budget on M1 — develop at half-res.
- Render TOP with many lights / shadows is expensive — limit light count, bake if possible.
- Analyze TOP triggers GPU→CPU sync; call only where needed.

---

## Reading This File

Grep by TOP name. Or jump to the section for the role: Generator / Filter / Transform / Composite / Render / Feedback / Analysis. For the shape of the pipeline, see "Canonical TOP Chains" near the end.
