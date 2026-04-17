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
