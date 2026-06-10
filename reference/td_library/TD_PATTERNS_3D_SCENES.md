---
title: 3D Scene Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Building 3D scenes in TD — camera + lights + geometry + render + post. Multi-pass, depth, shadows, stereo, AR/VR.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_COMP.md, TD_OPERATORS_MAT.md
---

# 3D SCENE PATTERNS

A TD 3D scene is composed of **Camera COMPs + Light COMPs + Geometry COMPs + Render TOP**. This file covers building, lighting, rendering, and post-processing 3D scenes.

---

## Minimal 3D Scene

```
Box SOP ──► Null ──► Geometry COMP
                       - Render tab: Material = Phong MAT

Light COMP (Directional, white, 1.0 intensity)
Camera COMP (default position, looking at origin)

Render TOP:
  - Geometry: /project1/geo_box
  - Camera: /project1/cam_main
  - Lights: /project1/light_main
  - Resolution: 1280×720
  - Output: Null TOP
```

Result: a lit cube on the default background.

---

## Scene Graph — Hierarchy

### Parenting
- Set Geometry COMP → Xform tab → Parent (operator path) → points to a Null COMP.
- Moving the parent moves all children.
- Use: vehicles, characters, any rigid group.

### Null COMP as a pivot
```
Null COMP "pivot" (at origin)
  ├── Geometry COMP "wheel_front_left" (parent = pivot)
  ├── Geometry COMP "wheel_front_right" (parent = pivot)
  └── Geometry COMP "body" (parent = pivot)
```
Rotate the Null → everything rotates together.

### Object Merge for scene composition
Build sub-scenes in Base COMPs; Object Merge SOP pulls them into the main render graph with transforms.

---

## Camera Control

### Basic camera
Camera COMP → set Translate XYZ, Rotate XYZ, or use "Look At" + target op.

### Orbit camera
```
Null COMP "orbit_center" (at subject)
Camera COMP (parent = orbit_center)
  - Translate Z = -5 (distance)
  - orbit_center's Rotate Y driven by Time or mouse
```

### Dolly / fly-through
LFO CHOP or animation channel driving Camera Translate Z.

### First-person navigation
Keyboard In CHOP + Mouse In CHOP → compute forward/strafe → Camera COMP translate/rotate.

### Multiple cameras (multi-angle render)
Build multiple Camera COMPs. Each Render TOP uses one. Switch TOP between them for scene cuts.

### Orthographic
Camera COMP → View tab → Projection = Orthographic. Size controls zoom. Use for: UI, 2D-feel 3D, architectural views.
- **`projection='ortho', orthowidth=N`** with a flat textured quad and a single angled bright light = the "TOP-rendered-through-3D-pipeline" trick (see Compositing/Rendering Notes below). No perspective distortion + 3D lighting gradient = looks like a flat poster with directional shading.

---

## Lighting

### Light types (Light COMP → Light Type)
- **Directional** — sun. Parallel rays, no position.
- **Point** — omnidirectional from a position. Falloff by distance.
- **Cone / Spot** — directional from a position with angle falloff.
- **Area** — rectangular area light for soft shadows.
- **Ambient** — flat global fill.

### Classic three-point lighting
```
Key Light:  Directional, bright, from front-right-above.
Fill Light: Directional, half intensity, from front-left.
Back Light: Directional, white or warm, from behind-above.
```

### Two-cone + environment lighting (POPX `dla.toe` canonical for particle scenes)
For particle / instanced-geometry scenes where you want clean separation without overcomplicating the lighting (scene scale: ±5 unit cube, camera at z=6.5):
```
environmentlightCOMP  ← ambient IBL (low contribution)
coneLight #1 at (-4.3, 1.0, 13.7)   ← far-back rim (≈2.7× scene-radius behind, slightly above)
coneLight #2 at (2.0, 6.0, -0.7)    ← above-front fill (≈1.2× scene-radius above, slightly forward)
```
Three lights total (env + 2 cones), but the cones do the directional work — env just provides ambient floor. Positions are absolute world units for the canonical example's ±5 scene; scale them proportionally to your geometry size. No explicit "key" — the rim defines form, the fill softens shadows. Combined with PBR `rimlight0` on the material itself, you get edge-defined silhouettes without a 4th light.

### High-quality single soft-shadow light (POPX `curve advection.toe` canonical)
When one well-tuned light suffices and you want clean soft shadows on instanced geometry (scene scale: ±1 unit, camera at z=1.2 — light positions are tight to scene):
```
lightCOMP at (0.08, -1.31, 0.95), rotated to point at scene center
  shadowtype = 'soft2d'
  filtersamples = 32      ← more = smoother penumbra
  searchsteps = 32        ← more = better shadow edges
  shadowresolution1/2 = 2024   ← high-res shadow map
  lightsize1/2 = 0.1      ← smaller = sharper, larger = softer
  dimmer = 5.0            ← HDR overbright (pairs with PBR overbright basecolor)
  aperture = 44.1         ← lens aperture
  polygonoffsetunits = 4.55  ← reduces shadow acne
```
One light + soft-shadow params + HDR overbright = clean depth cues without an environment light or fill. Used when the scene is intentionally moody/single-source rather than evenly lit. **Scale `dimmer` and shadow softness to your scene's basecolor brightness and overall post grade — 5.0 is paired here with PBR basecolor=(1.8, 1.8, 1.8) overbright; a darker-basecolor scene needs even more dimmer headroom.**

### 3-cone-light complementary-color rim setup (POPX `sweep_example.toe` canonical)
For colored chromatic lighting on a black-basecolor PBR material — the lights ARE the visible color (scene scale: ±2 unit area, camera distance ~5):
```
light1 (side-fill GREEN):    cone, color (0.68, 1.0, 0.50), wide 87°, dimmer=2.0, at (-2.6, -0.4, 0.5)
light2 (side-fill MAGENTA):  cone, color (0.36, 0.0, 1.0), wide 87°, dimmer=2.0, at (1.3, 0.3, 2.0)
light3 (overhead KEY):       cone, color (0.36, 0.0, 1.0), narrow 46°, dimmer=3.0, elevated at (1.5, -8.1, 7.6)
```
All three: `shadowtype='soft2d', filtersamples=64, searchsteps=64, shadowresolution=3024, lightsize=0.1, maxshadowsoftness=0.048`
- **light1 + light2 act as opposing colored side-fills** (green and magenta — complementary colors maximize chromatic contrast on form)
- **light3 is the de-facto key** — narrower cone (46° vs 87°), higher dimmer (3.0 vs 2.0), elevated overhead, painting the dominant directional light
- **PBR material `basecolor=(0,0,0)`** means the lights themselves ARE the visible color — no basecolor mixing in
- Higher specs than the single-light setup (64 samples vs 32, 3024 shadow resolution vs 2024) for production-quality renders
- Use when the scene benefits from "what color is this surface?" being ambiguous because it depends entirely on which light is hitting it

### Pre-processing HDRI for IBL (desat + blur — POPX `sweep_example.toe` canonical)
When you want the HDRI's directional lighting STRUCTURE but not its hue (e.g. scene has its own deliberate color palette and you don't want env color contamination):
```
moviefileinTOP (HDRI, e.g. CloudyOcean.tif)
   ↓
hsvadjustTOP                   ← tune saturation/value if needed
   ↓
monochromeTOP                  ← strip all color → pure luminance
   ↓
blurTOP                        ← soften directional cues (blur SIZE controls the tradeoff —
                                  see below)
   ↓
nullTOP                        ← publish point
   ↓ (assigned via par.val)
environmentLightCOMP.par.envlightmap
```
Result: ambient lighting that follows the HDRI's spatial brightness pattern (sky vs ground, sunlit vs shadow side) but doesn't fight your scene's color palette with HDRI hue bleed.

**Blur size tuning tradeoff:**
- **Small blur (size 1-5):** preserves directional cues — you can still tell where the "sun" is, scene gets subtle direction from the HDRI's bright spots
- **Medium blur (size 10-30):** smooths into broad zones — useful for getting "sky on top, ground on bottom" feel without hard sun position
- **Heavy blur (size 50+):** converges toward uniform color — basically the HDRI's AVERAGE luminance, no directional information, almost equivalent to a constant ambient

Pick based on whether you want the env to suggest a sun direction (small blur) vs purely add ambient lift (heavy blur). Underrated technique — most uses pipe the raw HDRI through and accept whatever color contamination comes with it.

### Shadows
Light COMP → Shadow tab → On. Shadow Map Size 1024 or 2048. Higher = cleaner edges, higher VRAM.
Only works with shadow-compatible MATs (Phong, PBR).

### Image-Based Lighting (IBL)
For PBR: use Environment Light COMP + HDRI.
- Loads an HDR equirectangular texture.
- Lights the scene based on the environment.
- Needed for photoreal PBR materials.

---

## Materials — See `TD_OPERATORS_MAT.md`

Pick per scene:
- **Constant MAT** — unlit stylized / glowing.
- **Phong MAT** — classic lit look, cheap.
- **PBR MAT** — photoreal with HDRI lighting.
- **GLSL MAT** — custom shading (cel, toon, custom BRDF).

---

## Rendering Options

### Render TOP parameters
- **Antialias** — 1× / 2× / 4× / 8× MSAA. Higher = smoother edges, more cost.
- **Background** — solid color or alpha (0 alpha for transparent background).
- **Order** — depth test mode.
- **Lights / Geometry / Camera** — scene inputs.

### Multi-pass rendering
- **Render Pass TOP** — additional passes layered on top.
- Use: outlines, wireframe overlay, depth-of-field, custom composites per-pass.

### Render Select TOP
Pick specific buffers from a multi-output render.

### G-buffer (deferred shading)
GLSL Multi TOP inside a MAT outputs multiple buffers (color, normal, depth). Composite the buffers into final image with custom shaders.

### Routing a 2D animated TOP through the 3D PBR pipeline (POPX `physarum_dumps.toe` pattern)

You can route a purely-2D animated source (POPX trail, audio FFT viz, GLSL output, video footage) through a 3D-render-and-PBR pipeline instead of compositing the TOP directly. The reason isn't realism — it's getting access to:
- A **directional shading gradient** from a 3D light hitting a flat textured surface
- The full **3D-render post chain** downstream (feedback over rendered output, lumablur with control inputs, render-targeted level grades) for effects that don't compose cleanly in pure TOP-land

```
animated_TOP ──▶ [optional limit/normalize] ──▶ nullTOP (stable publish point)
                                                     │
                                                     │ (referenced as pbr.basecolormap)
                                                     ▼
gridPOP (high subdivision, but FLAT — no displacement) ──▶ normalPOP ──▶ geometryCOMP
                                                                            │  (material = PBR)
                                                                            ▼
                                                                        renderTOP
                                                                            ↑
                                                                cameraCOMP (projection='ortho',
                                                                            orthowidth ≈ 1.0)
                                                                lightCOMP (single, angled,
                                                                           dimmer = high (5-15+);
                                                                           tune to PBR basecolor + post grade)
                                                                            │
                                                                            ▼
                                                                        [render post chain: feedback/cross/lumablur/level]
```

**What makes this different from "just composite the TOP":**
- The angled light creates a directional brightness fade across the quad — gives the 2D source a subtle "lit from this side" feel without manually compositing a gradient
- The render output now feeds the same post chain you'd use for 3D scenes (feedback for trails, lumablur with a depth or ramp control, etc.)
- The PBR material's `metallic`/`roughness` parameters add a tactile reflective character that pure TOP compositing lacks

**What's NOT happening here (common confusion):**
- The heightmap is NOT being used for actual relief, even if `heightmapenable=True` — verify `pbr.par.heightmap` is set AND `displacescale > 0` or `parallaxscale > 0` for it to do anything. In the canonical example file the heightmap par is empty (None) despite the enable toggle, so it's a no-op
- Tangent computation (`normalPOP.par.tang='alwayscompute'`) is only load-bearing when normal/height maps are actively wired; the canonical file has tangents present but unused — leaving them on is harmless cargo
- This is NOT a substitute for true 3D — it's a 2D source dressed up to access 3D-pipeline features

---

## Depth Buffer

Render TOP → Output tab → Render Mode options expose depth. Or use Depth MAT to get depth-as-color.

Uses of depth:
- **DOF (depth of field)** — blur based on depth distance from focal plane.
- **Fog** — reduce saturation/brightness by depth.
- **SSAO** — screen-space ambient occlusion requires depth + normal buffers.
- **Depth compositing** — merge multiple render passes by Z order.

---

## Post-Processing Stack

Typical order after Render TOP:
```
Render TOP ──► Null "null_render"
           ──► Bloom (highlight glow)
           ──► Chromatic Aberration (lens fringing)
           ──► Film Grain (texture)
           ──► Level (final gamma / contrast)
           ──► Out
```

### Expensive post to be aware of
- Bloom with high spread + threshold is costly.
- DOF with per-pixel kernel is very expensive — use fake DOF (Gaussian Blur based on depth mask).
- Motion blur (Temporal Blur TOP) is GPU-intensive.

### Depth-aware atmospheric chain (SSAO + trails + depth-blur — POPX `dla.toe` canonical)

A sophisticated render-post chain for particle clouds / instanced geometry where you want shadow contact between elements + accumulated trails + atmospheric depth softening:

```
render1 (1920×1080, antialias='aa16')
  │
  ├──► ssao1  (ssaopassres='full', ssaoradius=1.0, contrast=1.2, edgethresh=0.1)
  │        │
  │        ├──► feedback1  (par.top = cross1, input[0] = ssao1) ←── feedback samples cross1's PREVIOUS frame
  │        │                                                        input wire from ssao1 (not cross1!) provides
  │        │                                                        format/init without creating a cook loop
  │        └──► cross1.in1  ← current frame
  │              cross1.in0 ◄── feedback1  ← previous accumulated
  │              (crossTOP at default = 50% mix → trail accumulation)
  │
  ├──► depth1  (op=render1, pixelformat='r16float', depthspace='reranged',
  │                rangeto1=0, rangeto2=125, gamma=5.0)  ← depth map with foreground emphasis
  │
  cross1 ──► lumablur1.in0
  depth1 ──► lumablur1.in1   (lumablur1.whitewidth=15 — blur kernel scales by depth/luma)
                                                          → poor-man's DOF: foreground sharp, distance soft
            │
            ▼
       level1  (brightness1=2.0, gamma1=0.67) → out1
```

**Why this works:**
- **SSAO** darkens contact points between geometry → dense particle clouds get visual separation between adjacent instances that would otherwise blur into a mass
- **Cross + feedback** layer current and previous frames → accumulating growth (DLA fronts) leave visual trails of the active growth zone
- **Depth-aware lumablur** uses the render's depth buffer to soften far elements while keeping foreground crisp → atmospheric perspective without true DOF cost
- **Final level grade** (brightness 2× + gamma 0.67) crushes blacks + lifts mids after the chain has dimmed the output

**Cook-loop-safe feedback wiring (cross-ref `TD_PATTERNS_FEEDBACK.md`):**
`feedback1.par.top = cross1` (the target whose previous frame to sample) AND `feedback1.input[0] = ssao1` (a DIFFERENT op that provides format/init). Wiring input[0] to cross1 would create the cook loop. Wiring to ssao1 (which has no dependency on feedback1) is safe. The POPX creator uses exactly this pattern — canonical confirmation.

**depthTOP `reranged` mode:** maps the camera's near/far depth to a custom range (here 0–125) and applies gamma (here 5.0) to bias the response toward foreground. The remapped depth is what makes lumablur's depth-driven kernel produce meaningful spatial variation.

---

## Transparency

### Alpha in MAT
- Phong/PBR/Constant: set Alpha parameter or use Alpha texture map.

### Order-dependent transparency
Transparency is order-dependent in normal rendering:
1. Sort geometry by depth back-to-front.
2. Render opaque first, then transparent.

### TD's solutions
- **Geometry COMP → Render tab → Render order**: set to Sort if using sort-based transparency.
- **Order Independent Transparency (OIT)** — advanced; use additive blending for most practical cases.

### Additive transparency shortcut
Constant MAT with Alpha + Material SOP setting Blend Mode = Add → transparent emissive. Works for particles, light trails, glow.

---

## Stereo / VR

Camera COMP → Stereo tab → On. Sets eye separation.
Render the scene once per eye, composite.

On Mac M1: Apple Vision Pro workflows emerging but early; typical VR headsets (Quest, Vive) require Windows for TD+SteamVR.

---

## Multi-Camera Render Patterns

### Split screen
Render TOP A from camera A.
Render TOP B from camera B.
Composite side-by-side.

### Scene switcher
One Geometry, N cameras. Switch TOP between Render TOPs.

### Reflections via second render
Mirror camera flipped across a plane, render that view, project onto reflection geometry via UVs.

---

## Procedural Environments

### Skybox
Sphere SOP at large scale, UV-mapped with an equirectangular HDR/EXR, Constant MAT (unlit), scale > camera far clip.

Or: Render TOP → Background Image = equirectangular.

### Terrain
Grid SOP → Noise SOP (Displace P.y) → Normal SOP → Material. Or Grid POP + Attribute From Texture POP (sample heightmap).

### Fog
Post stack: Level TOP with depth-masked darkening, or dedicated fog MAT.

---

## Canonical Scene Templates

### Template A — Object showcase
```
Base COMP "scene_product"
  ├─ Product SOP (Model / File In) ──► Phong MAT with textures
  ├─ Camera COMP (orbiting on LFO)
  ├─ Light COMP (key) + Light COMP (fill) + Light COMP (back)
  ├─ Environment Light (HDRI)
  ├─ Render TOP (1280×720, AA 4×)
  └─ Post: Bloom → Level → Out
```

### Template B — Abstract generative 3D
```
Base COMP "scene_abstract"
  ├─ POP pipeline (generator → attribute → instance) with 10k points
  ├─ Geometry COMP with instanced small quad (Point Sprite MAT)
  ├─ Single Light (Ambient + Directional)
  ├─ Camera with audio-driven shake
  ├─ Render TOP
  └─ Post: Feedback → Bloom → Chromatic → Level
```

### Template C — Low-poly environment flythrough
```
Base COMP "scene_world"
  ├─ Terrain (Grid + Noise)
  ├─ Scattered trees (L-System SOP → instanced via Geometry COMP)
  ├─ Skybox (inverted Sphere with HDRI)
  ├─ Camera moving along a path (animated)
  ├─ Directional sun + ambient
  ├─ Render TOP
  └─ Post: Bloom + Fog
```

---

## Performance Notes

- **Light count directly impacts Render TOP cost** — each light adds shading passes. Keep under 4 dynamic lights for real-time.
- **Shadows are expensive** — each shadowed light adds a shadow pass. Selectively enable shadows only on the key light.
- **MSAA 8× doubles render cost vs 4×** — use 4× for real-time, 8× only for offline rendering.
- **Geometry with >100k triangles per frame stresses M1** — use POP instancing for repeated objects.
- **Transparent materials are expensive** — sort-based rendering + blend operations. Limit transparent surfaces where possible.
- **PBR MAT costs more than Phong** — use Phong when photoreal isn't the goal.

---

## Reading This File

Scene templates near the end are the fastest way to get started. Reference sections for lighting, transparency, post are above. For MAT details see `TD_OPERATORS_MAT.md`; for instancing see `TD_PATTERNS_INSTANCING.md`.
