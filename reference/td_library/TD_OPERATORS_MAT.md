---
title: MATs — Material Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every MAT in TD 2025.32460. Materials assigned to SOP/POP geometry in the render pipeline.
dependencies: TD_LIBRARY_INDEX.md, TD_PATTERNS_3D_SCENES.md, TD_OPERATORS_TOP.md
---

# MATs — MATERIAL OPERATORS CATALOG

MATs are **shading models applied to geometry during render**. A MAT is assigned to a SOP (via Material SOP or on the Geometry COMP's Render tab) or referenced by a Geometry COMP.

**Core facts:**
- MATs run in the Render TOP pass — they are fragment + vertex shaders packaged as parameters.
- On Mac: MATs with custom geometry-shader stages won't work (Metal limitation). Stick to stock MATs or custom GLSL MAT without geometry stage.

---

## Standard Material MATs

### Constant MAT
Flat color / unlit — no lighting response.
- Params: Color, Alpha, Emit map, Texture map.
- Use: UI elements, emissive objects, unlit stylized looks, particles with glow.

### Phong MAT
Classic Phong lighting — diffuse + specular.
- Params: Diffuse Color, Specular Color + Roughness / Shininess, Ambient, Emit, Alpha, plus Texture Maps (Color / Normal / Specular / Alpha / Env / Height).
- Use: default lit material for non-PBR looks.

### PBR MAT
Physically-based rendering — metallic + roughness workflow.
- Params: Base Color, Metallic, Roughness, Normal, Emission, Ambient Occlusion, Height, Env Map, IOR.
- Use: realistic materials, PBR texture sets.
- **Built-in rim light:** `rimlight0color` + `rimlight0strength` add edge highlights at the material level — no separate rim-light COMP needed. POPX `dla.toe` canonical setup: `metallic=0.058, roughness=0.322, ambientocclusion=0.907, rimlight0color=(0.4, 0.4, 0.4), rimlight0strength=0.9`. Cleanly separates instanced sphere silhouettes against dark backgrounds in particle-cloud scenes where adding an actual 4th light would mess with primary illumination.
- **`wireframe='topology'`**: renders the geometry as wireframe lines via the PBR material — no separate Line MAT needed. Critical for rendering linestrip geometry (e.g. from `lineresamplePOP` output, or `gridPOP` with `surftype='linestrips'`). POPX `curve advection.toe` uses this for the advected curve render: `pbrMAT` with `basecolor=(1.8, 1.8, 1.8)` overbright + `roughness=0.488` + `wireframe='topology'`.
- **Overbright `basecolor` (values > 1)** for HDR-readable rendering: pushes color output past clamp into HDR range. Useful when paired with downstream bloom (creates soft glow halos) OR when light dimmers are very high and the material would otherwise wash to grey. POPX `curve advection.toe` uses `basecolor=(1.8, 1.8, 1.8)` alongside `light1.dimmer=5.0` — overbright comp with no downstream bloom in that file, so the choice is for HDR readability + light-dimmer compensation, not glow.
- **Emissive source-color matching pattern**: when a sphere/sprite "injects" something downstream (e.g. into a fluid sim or particle field), set the sphere's emit color to match the downstream injection color. POPX `curve advection.toe`: `pbr2.emit=(1.0, 0.77, 0.50)` matches `flow1.par.Injectcolor=(1.0, 0.77, 0.50)`. Visual continuity — the source IS the fluid color, making the connection between particle origin and fluid trail feel physical.
- **`rimlight0center` (in addition to `rimlight0color/strength`)**: per TD help, "The center of the rim lights location, situated somewhere on a 360 degree circle." Range 0–360, default 90. This is an angular POSITION (where the rim sits on a 360° circle around the object), NOT a coverage/spread parameter — values 0 and 360 are the same position. Rim coverage/spread is controlled separately (likely other rimlight params — verify with TD's customize-component UI if precise tuning matters).
- **`blending=True` enables custom blend modes (NOT just translucency)**: pairs with `srcblend` and `destblend` params for HDR-friendly additive accumulation, screen-blending, etc. POPX `sweep_example.toe` uses `blending=True, srcblend='one', destblend='omsa', postmultalpha=True, polygonoffset=True` — additive-like accumulation that lets stacked sweep layers visually combine without alpha-occluding each other. The `polygonoffset=True` is the load-bearing partner — prevents z-fighting when coplanar/overlapping geometry uses this blend mode.

### Point Sprite MAT
Billboarded sprites — faces camera, textured.
- Params: Sprite Texture, Size, Color, Alpha.
- Use: particle rendering, stars, dust — POP instancing often pairs with Point Sprite MAT.

### Line MAT
Renders lines / wires with consistent screen-space width.
- Params: Color, Width, Pattern (solid, dashed), Anti-Alias.

### Wireframe MAT
Wireframe shading — shows edges.
- Params: Wireframe color, Fill color, Wire width.

### Depth MAT
Outputs depth as color — for shadow buffers or depth visualization.
- Use: custom SSAO, depth compositing.

### GLSL MAT
**Escape hatch** — write your own vertex + fragment shader.
- Params: Vertex + Fragment source, Uniforms (vectors, arrays, CHOPs, TOPs), Compile button.
- Use: custom lighting models, procedural shaders, raymarching in a material slot.
- On Mac: vertex + fragment stages only; no geometry stage.

### GLSL Multi MAT
Multiple output buffers from one MAT — analogous to GLSL Multi TOP.

### Environment Light MAT
Environment-based lighting (HDRI) — image-based lighting for PBR.
- Requires environment map input.

---

## Material Network Nodes

### Select MAT
Pulls a MAT from elsewhere by name.

### Switch MAT
Switches between MATs by index.

### Null MAT
Named passthrough.

### In MAT / Out MAT
COMP I/O.

---

## Assigning MATs — Workflow

### On a Geometry COMP
- Geometry COMP → Render tab → Material path: point to a MAT.
- Affects the whole SOP in that Geometry COMP.

### Per-primitive via Material SOP
- Material SOP before the Null feeding the Geometry COMP.
- Assigns different MATs to different primitives/groups.

### Per-instance — POPs with Attribute POP
- Set per-instance `Cd`, `alpha`, custom attribute.
- MAT reads via `vertex_attribute` / uniform.

---

## Texture Maps on MATs

Most MATs have texture map slots. Common:

- **Color Map** — base color.
- **Normal Map** — bump/normal from a TOP.
- **Specular Map** (Phong) / **Metallic + Roughness Map** (PBR).
- **Alpha Map** — transparency mask.
- **Emit Map** — emissive contribution.
- **Height Map / Displacement** — for PBR or Phong parallax.
- **Environment Map** — reflection source (HDRI).

Any TOP can be the source. Use Null TOP as reference point.

---

## Canonical MAT Usage Patterns

### Standard 3D object
```
Geometry COMP ──► Material: Phong MAT
                  ├─ Color Map: Null TOP of albedo
                  ├─ Normal Map: Null TOP of normal
                  └─ Specular Roughness: 0.3
```

### PBR product shot
```
Geometry COMP ──► Material: PBR MAT
                  ├─ Base Color: albedo TOP
                  ├─ Metallic Map: metal mask
                  ├─ Roughness Map: roughness
                  ├─ Normal Map: normal
                  └─ Env Map: HDRI
```

### POP-instanced particles
```
POP with Attribute POP setting Cd, pscale ──► Geometry COMP (template = Sphere SOP or quad)
                                              Material: Constant MAT with color driven by Cd attribute
                                              OR: Point Sprite MAT
```

### Custom GLSL look (e.g., cel shading)
```
Geometry COMP ──► GLSL MAT with vertex + fragment source
                  Uniforms: light direction from Light COMP
                  Output: two-tone cel shading
```

### Wireframe overlay on solid
```
Render Pass 1: Geometry COMP with Phong MAT
Render Pass 2 (Render Pass TOP): same Geometry COMP with Wireframe MAT
Composite Over
```

---

## MAT Performance Notes

- Constant MAT is the cheapest — use when lighting isn't needed.
- Phong MAT is cheap; fine at high poly counts.
- PBR MAT is more expensive (more texture samples); use where realism matters.
- GLSL MAT cost depends entirely on the shader — keep shader math proportional to scene budget.
- Environment Light MAT + HDRI is expensive for large scenes — bake if possible.
- Point Sprite MAT is cheap and GPU-ideal for particle rendering.

---

## MAT on Mac Apple Silicon — Caveats

- GLSL MAT: no geometry shader stage (see `TD_APPLE_SILICON.md`).
- GLSL MAT compile errors can be delayed by one compile cycle on Metal — compile, check, compile again if in doubt.
- Environment Map TOPs: use PNG / HDR / EXR — confirm colorspace is Linear on import.

---

## Reading This File

MATs are a small family — read top to bottom once to internalize. For specific materials in specific pipelines, see "Canonical MAT Usage Patterns." Brand-specific MAT choices (especially for Wobar acts) live in `WOBAR_TD_REFERENCE.md`.
