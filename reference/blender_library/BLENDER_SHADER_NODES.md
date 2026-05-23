---
title: Shader Nodes — Material Shader Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Shader graph node reference — the BSDF / Texture / Vector / Color / Converter / Output node families, Principled BSDF, subsurface scattering, anisotropic, emission, volume, displacement, world shader trees, the bpy ShaderNodeTree API.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_MATERIALS.md
---

# SHADER NODES — MATERIAL SHADER REFERENCE

A **shader node tree** is the graph that defines how a surface, volume, or world responds to light. Nodes produce closures (BSDF, Emission, Volume) which feed a single **Material Output** node; the renderer (Cycles or EEVEE Next) evaluates that closure per shading sample. Three contexts use shader trees:

- **Object / material trees** — live on `Material.node_tree`. Define a mesh's surface, volume, and displacement. The most common case.
- **World trees** — live on `World.node_tree`. Define the environment lighting / background. See section 18.
- **Linestyle trees** — used by Freestyle line rendering (`LineStyle.node_tree`). Niche; same node toolkit, different output.

All three share the `ShaderNodeTree` Python type. Outside the renderer, the same node language reappears in Geometry Nodes and Compositor — see `[[BLENDER_GEOMETRY_NODES]]` and `[[BLENDER_COMPOSITOR]]` — but those are different tree types with overlapping but not identical node sets.

**Core facts:**
- Shader trees live on Materials (`material.node_tree`) or Worlds (`world.node_tree`), accessed only when `use_nodes = True`.
- The graph terminates at a `Material Output` node. Anything not reachable from that output is dead code (still compiled, still costs RAM, but does nothing visual).
- Cycles and EEVEE Next share most nodes; ~95% of trees render identically across engines.
- Some nodes are engine-specific: **Shader to RGB** is EEVEE-only, **Bevel** and **Light Path (most outputs)** and **OSL Script** are Cycles-only.
- Sockets are typed: Float, Vector, Color (RGBA, 4-tuple), Shader (closure), Geometry, String, Image, Material — the typing is enforced and mismatched links auto-insert a converter or fail.
- **Shader sockets are not values, they are closure definitions.** You cannot read an RGB out of a BSDF socket directly — use `Shader to RGB` (EEVEE only) or sample via baking.
- `node.update()` is mostly automatic; manual calls are rare and only relevant after rewriting `bl_idname`-level data via Python.
- Color sockets are 4-component (RGBA). Setting `default_value` requires a 4-tuple, not a 3-tuple. Alpha is the 4th channel and defaults to 1.0.
- Image Texture color space matters: **sRGB** for albedo / base color, **Non-Color** for normals, roughness, metallic, displacement, anything that isn't a "viewable" color.
- The Material Output node can be scoped per-engine via `target = 'CYCLES' | 'EEVEE' | 'ALL'` — a material can carry separate trees for each engine.

---

## The Material Output Node

`bl_idname = 'ShaderNodeOutputMaterial'`. The required terminal of every material tree. If absent or unconnected, the surface renders as default gray.

**Inputs (3):**
- **Surface** — Shader socket. The BSDF / shader closure that defines reflectance.
- **Volume** — Shader socket. Volume Scatter / Volume Absorption / Principled Volume. Evaluated for rays inside the mesh.
- **Displacement** — Vector socket. Moves surface points along normal (or as a 3D vector if connected via Vector Displacement). Only true-displaces in Cycles when material's `cycles.displacement_method` is `'DISPLACEMENT'` or `'BOTH'`; in EEVEE it falls back to bump.

**Property: `target`** — `'CYCLES'`, `'EEVEE'`, `'ALL'`. Lets a material carry two parallel output nodes, one per engine, so you can author engine-specific trees in the same material. In Python:
```python
mat = bpy.data.materials.new("M")
mat.use_nodes = True
out = mat.node_tree.nodes['Material Output']
out.target = 'CYCLES'
```

Most materials have one output with `target='ALL'`. Add a second output and set targets when you genuinely need divergent behavior.

---

## Principled BSDF — Deep Dive

`bl_idname = 'ShaderNodeBsdfPrincipled'`. The universal artist-facing shader. A multi-lobe stack: base diffuse + specular + transmission + coat + sheen + emission + subsurface + thin-film. Default node in every new material.

The 4.0 release rewrote this node substantially. Names changed. Old "Specular" became **Specular IOR Level**. Old "Subsurface" (a 0–1 mix) became **Subsurface Weight** with a separate **Subsurface Scale**. Old "Clearcoat" became **Coat**. If you have references that predate Blender 4.0, the parameter names will not match.

**Properties:**
- `distribution` — `'GGX'` (default) or `'MULTI_GGX'` (energy-preserving, more accurate for rough metals, slightly slower).
- `subsurface_method` — `'BURLEY'` (fast diffusion approx) or `'RANDOM_WALK'` (Cycles only — physically accurate, slower, supports anisotropy and IOR).

### Inputs

**Base layer:**
- **Base Color** — Color (default `(0.8, 0.8, 0.8, 1.0)`). The diffuse / albedo color. For metals, this is the F0 reflection tint.
- **Metallic** — Float 0–1 (default 0.0). 0 = dielectric, 1 = conductor. Avoid mid-values except for thin films of metal over dielectric (rust, oxidation).
- **Roughness** — Float 0–1 (default 0.5). 0 = mirror, 1 = fully diffuse. Below ~0.05 you start to see aliased highlights in EEVEE.
- **IOR** — Float (default 1.5). Index of refraction for the dielectric specular lobe and transmission. Common: 1.33 (water), 1.45 (skin), 1.5 (glass / plastic), 1.55 (gemstones), 2.4 (diamond).
- **Alpha** — Float 0–1 (default 1.0). Per-pixel opacity. In EEVEE, requires `blend_method` set appropriately on the material. In Cycles, drives a transparent-BSDF mix internally.
- **Normal** — Vector (default = geometry normal). Feed from a Normal Map node or Bump node.

**Subsurface scattering (4.0+ model):**
- **Subsurface Weight** — Float 0–1 (default 0.0). 0 disables subsurface entirely. Mix factor between surface diffuse and subsurface lobes.
- **Subsurface Radius** — Vector (default `(1.0, 0.2, 0.1)`). Per-channel RGB scattering distance, in meters before the Scale multiplier. Red travels farthest in flesh, which is why skin shaders push the R component.
- **Subsurface Scale** — Float (default 0.05). Multiplier on Radius. Tune this for scene scale — a 0.05 default assumes a roughly meter-scale object.
- **Subsurface IOR** — Float (default 1.4). Only used with the `RANDOM_WALK` method.
- **Subsurface Anisotropy** — Float -1 to 1 (default 0.0). -1 = back-scatter, 0 = isotropic, 1 = forward-scatter. Random walk only.

**Specular control:**
- **Specular IOR Level** — Float (default 0.5). Multiplier on the dielectric reflection. 0.5 corresponds to the physically-correct F0 derived from IOR; values >0.5 brighten specular non-physically. (Replaces the 3.x "Specular" param at the same scale.)
- **Specular Tint** — Color (default white). Tints the dielectric specular at facing angles. White = physical.

**Anisotropic (rough metal directional highlights):**
- **Anisotropic** — Float 0–1 (default 0.0). 0 = isotropic GGX. Positive values stretch the highlight along the tangent.
- **Anisotropic Rotation** — Float 0–1 (default 0.0). Rotates the anisotropy direction; 1.0 = full revolution.
- **Tangent** — Vector. Optional explicit tangent direction; if unconnected, uses the mesh's UV-derived tangent.

**Sheen (cloth / dust / velvet):**
- **Sheen Weight** — Float 0–1 (default 0.0). Adds a soft retro-reflective lobe at grazing angles.
- **Sheen Roughness** — Float 0–1 (default 0.5).
- **Sheen Tint** — Color (default white).

**Coat (clearcoat layer over the base):**
- **Coat Weight** — Float 0–1 (default 0.0). Enables a glossy dielectric layer above everything else.
- **Coat Roughness** — Float 0–1 (default 0.03). Usually low — clearcoat is glossy.
- **Coat IOR** — Float (default 1.5).
- **Coat Tint** — Color (default white). Absorption tint of the coat — tints transmitted light, not the surface color directly.
- **Coat Normal** — Vector. Independent normal for the coat. Useful for surface-flake / orange-peel paint where the coat has different micro-geometry than the base.

**Transmission (glass / liquid):**
- **Transmission Weight** — Float 0–1 (default 0.0). Mix between opaque and transmissive. 1.0 = fully transmissive glass.

**Emission (self-illumination):**
- **Emission Color** — Color (default black).
- **Emission Strength** — Float (default 0.0). Multiplied with Emission Color. Set above 1.0 for HDR-bright surfaces that bloom and light other geometry.

**Thin Film (iridescence, 4.2+):**
- **Thin Film Thickness** — Float in nanometers (default 0.0). 0 disables. Visible interference 100–1000 nm. Drives angle-dependent color shift like soap bubbles, oil slicks, beetle shells.
- **Thin Film IOR** — Float (default 1.33). IOR of the thin film itself, between air and the substrate.

**Output:**
- **BSDF** — Shader socket. Connect to Material Output → Surface.

---

## Other BSDFs

Use these when Principled is overkill, when you need a behavior Principled does not expose, or when you want to combine them via Mix Shader. Most production work stays in Principled.

- **Diffuse BSDF** (`ShaderNodeBsdfDiffuse`) — Lambertian (or Oren-Nayar at high Roughness). Lightweight, useful in NPR or as a base for custom mixes.
- **Emission** (`ShaderNodeEmission`) — Pure light-emitter, no reflection. Cheaper than Principled-with-emission-only.
- **Glass BSDF** (`ShaderNodeBsdfGlass`) — Combined refraction + Fresnel reflection. Single distribution (GGX/Multi-GGX/Beckmann). Use for solid glass; Principled with Transmission=1 produces equivalent results.
- **Glossy BSDF** (`ShaderNodeBsdfGlossy`, formerly Anisotropic BSDF) — Pure specular reflection. Used in custom-stacked materials and as a building block for mix-with-fresnel.
- **Refraction BSDF** (`ShaderNodeBsdfRefraction`) — Refraction only, no reflection lobe. Pair with Glossy via Fresnel for hand-built glass.
- **Translucent BSDF** (`ShaderNodeBsdfTranslucent`) — Light passes through and diffuses on the back side. For thin objects like leaves, paper, lampshades. Much cheaper than full SSS.
- **Transparent BSDF** (`ShaderNodeBsdfTransparent`) — No refraction, no shading — light passes straight through. Used for masking, decals, and the standard "punch a hole" pattern.
- **Hair BSDF** (`ShaderNodeBsdfHair`) — Legacy hair shader. Two components: Reflection and Transmission. Largely superseded by Principled Hair.
- **Principled Hair BSDF** (`ShaderNodeBsdfHairPrincipled`) — Realistic hair with Melanin, Roughness, IOR. The default for character hair.
- **Subsurface Scattering** (`ShaderNodeSubsurfaceScattering`) — Standalone SSS, four falloff types. Mostly replaced by Principled's SSS but still useful when stacking custom mixes.
- **Velvet BSDF** — Removed in 4.0. Use Principled Sheen instead.
- **Anisotropic BSDF** — Renamed to Glossy BSDF in 4.0; the `bl_idname` is `ShaderNodeBsdfAnisotropic` for older files, `ShaderNodeBsdfGlossy` for new.
- **Toon BSDF** (`ShaderNodeBsdfToon`) — Cycles cel-shading primitive with stepped diffuse / glossy. In EEVEE, prefer Shader to RGB + Color Ramp.
- **Specular BSDF** (`ShaderNodeEeveeSpecular`) — EEVEE-Legacy holdover, non-PBR. Avoid in new work; EEVEE Next prefers Principled.

---

## Mix Shader / Add Shader

Two ways to combine BSDFs.

- **Mix Shader** (`ShaderNodeMixShader`) — Two shader inputs (Shader, Shader), one Fac (Float 0–1). Linear blend. Energy-conserving when Fac is in [0,1]. The bread-and-butter combiner.
- **Add Shader** (`ShaderNodeAddShader`) — Sums two shaders. **Not energy-conserving** — a Glossy + Diffuse can reflect more light than it received. Use sparingly: when you genuinely want additive layering (e.g., a base + a tiny extra spec lobe).

**The classic glass-or-gloss pattern** uses a Fresnel or Layer Weight node into Mix Shader Fac:
```
Layer Weight (Facing) → Mix Shader Fac
Glossy BSDF → Mix Shader Shader 1
Refraction BSDF → Mix Shader Shader 2
Mix Shader → Material Output Surface
```
Result: looks like glass at grazing angles, refracts head-on. Principled with Transmission handles this internally now, but the pattern still shows up in custom builds.

---

## Volume Nodes

Volume shaders connect to the **Volume** input on Material Output. They define how light scatters and absorbs *inside* the mesh's bounding region.

- **Principled Volume** (`ShaderNodeVolumePrincipled`) — Combined scattering + absorption + emission. Inputs: Color, Density, Anisotropy (g for Henyey-Greenstein phase, -1 back / 1 forward), Absorption Color, Emission Strength, Emission Color, Blackbody Intensity (fire), Temperature. Density attribute support for VDB volumes. Default volumetric for fog / smoke / clouds.
- **Volume Scatter** (`ShaderNodeVolumeScatter`) — Scattering only. Lighter weight. Use for clean atmospheres.
- **Volume Absorption** (`ShaderNodeVolumeAbsorption`) — Pure absorption, no scattering. Tints transmitted light through a transparent volume. Pair with Glass or Transmission on the surface for tinted glass / colored liquid.
- **Volume Info** (`ShaderNodeVolumeInfo`) — Reads VDB volume attributes (Color, Density, Flame, Temperature) for use inside volume shader trees.
- **Attribute** (`ShaderNodeAttribute`) — In a volume context, fetches named grids from a VDB. `attribute_type = 'GEOMETRY'` with `attribute_name = 'density'` is the standard pattern for smoke sim shading.

Volumes in EEVEE Next use a froxel grid — quality is set per-material and per-viewport (Volumetric Tile Size, Samples). Cycles volumetrics are path-traced and converge more slowly but look correct under any lighting.

---

## Texture Nodes

All texture nodes accept a Vector input (texture coordinates). Default coords are auto-generated from the mesh — see [Texture Coordinates](#vector--texture-coordinates) below.

- **Image Texture** (`ShaderNodeTexImage`) — Samples a 2D image. See in-depth section below.
- **Environment Texture** (`ShaderNodeTexEnvironment`) — Samples an equirectangular / mirror-ball HDRI. Used in the World tree feeding a Background node.
- **Sky Texture** (`ShaderNodeTexSky`) — Procedural sky. Three models: `'NISHITA'` (modern, supports sun disk, altitude, air density), `'HOSEK_WILKIE'`, `'PREETHAM'`.
- **Noise Texture** (`ShaderNodeTexNoise`) — Perlin-style fractal noise. See section 10.
- **Voronoi Texture** (`ShaderNodeTexVoronoi`) — Cellular / Worley noise. See section 10.
- **Wave Texture** (`ShaderNodeTexWave`) — Sinusoidal bands. Types: Bands, Rings. Profile: Sine, Saw, Triangle. Good for wood-grain bases.
- **Magic Texture** (`ShaderNodeTexMagic`) — Psychedelic interference pattern. Depth-controlled. Rarely realistic, useful for abstract.
- **Brick Texture** (`ShaderNodeTexBrick`) — Procedural brick wall with mortar. Squash / offset / row height controls.
- **Checker Texture** (`ShaderNodeTexChecker`) — Two-color checkerboard. UV debugging / abstract.
- **Gradient Texture** (`ShaderNodeTexGradient`) — Linear / quadratic / spherical / radial gradients on the input vector.
- **Musgrave Texture** — **Removed in Blender 4.1.** Functionality folded into Noise Texture's new Fractal modes. Files that contain it will display a "Legacy" version that still cooks.
- **IES Texture** (`ShaderNodeTexIES`) — Reads `.ies` photometric files. Drive light strength by an IES profile. Lights only.
- **Point Density Texture** (`ShaderNodeTexPointDensity`) — Samples a particle system or vertex cloud as a volumetric texture. Cycles-mostly.
- **White Noise Texture** (`ShaderNodeTexWhiteNoise`) — Hash-based per-coord random. Use for ID-driven variation.

---

## Image Texture in Depth

`bl_idname = 'ShaderNodeTexImage'`. Reads a single image (or sequence) and outputs Color + Alpha.

**Properties:**
- `image` — pointer to a `bpy.types.Image` datablock. Set via Python: `node.image = bpy.data.images.load('/path/to/file.png')`.
- `interpolation` — `'Linear'` (default, bilinear), `'Cubic'` (smoother, slower), `'Closest'` (nearest-neighbor — use for pixel art and ID maps), `'Smart'` (Cycles GPU adaptive).
- `projection` — `'FLAT'` (default UV), `'BOX'` (tri-planar, has a Blend factor for seams), `'SPHERE'` (sphere-mapped), `'TUBE'` (cylinder-mapped).
- `projection_blend` — Float, only for BOX projection. Seam softness.
- `extension` — `'REPEAT'`, `'EXTEND'` (clamp edge), `'CLIP'` (transparent outside 0–1), `'MIRROR'`.

**Image datablock properties (`node.image.colorspace_settings.name`):**
- `'sRGB'` — for albedo / base color / any "viewable" texture.
- `'Non-Color'` — for normal maps, roughness, metallic, displacement, height. **Critical** — sRGB-decoded normals look broken.
- `'Linear Rec.709'` — HDR textures already in linear.
- `'Raw'` — bypass colorspace entirely.

**Alpha:**
- `image.alpha_mode` — `'STRAIGHT'`, `'PREMUL'`, `'CHANNEL_PACKED'`, `'NONE'`. PNG with alpha is typically Straight; web textures sometimes Premul; texture atlases that pack metalness/roughness/AO in RGB channels use `'CHANNEL_PACKED'`.

**Sequence vs single-frame:**
- Set `image.source = 'SEQUENCE'`, then on the node set `image_user.frame_duration`, `frame_start`, `frame_offset`, `use_auto_refresh`, `use_cyclic`. Useful for video-as-texture.

**Inputs / outputs:**
- Input **Vector** — if unconnected, uses the active UV map. Feed a Texture Coordinate or UV Map node for explicit control.
- Output **Color** — RGB.
- Output **Alpha** — Float (1.0 if image has no alpha).

---

## Procedural Noise Nodes

### Noise Texture
`ShaderNodeTexNoise`. Multi-octave Perlin/Simplex-style fractal noise. The default procedural.

- `noise_dimensions` — `'1D'`, `'2D'`, `'3D'` (default), `'4D'`. 4D adds a **W** scalar input — drive it from Scene Time or a value node to animate the noise without UV motion.
- `noise_type` (4.1+) — `'MULTIFRACTAL'`, `'RIDGED_MULTIFRACTAL'`, `'HYBRID_MULTIFRACTAL'`, `'FBM'` (default), `'HETERO_TERRAIN'`. The 4.1 release replaced the Musgrave node by adding its modes here.
- Inputs: Vector, W (if 4D), Scale, Detail (octaves; ~16 max useful), Roughness (lacunarity weighting), Lacunarity, Distortion (warps the input vector before sampling).
- Outputs: Fac (single float), Color (RGB noise — different from Fac for color-tinted variation).

### Voronoi Texture
`ShaderNodeTexVoronoi`. Cellular noise — distance to scattered random points.

- `voronoi_dimensions` — `'1D'` / `'2D'` / `'3D'` / `'4D'`.
- `feature` — `'F1'` (nearest-point distance), `'F2'` (second-nearest), `'SMOOTH_F1'` (smoothed minimum, useful for organic blobs), `'DISTANCE_TO_EDGE'` (cell wall outlines), `'N_SPHERE_RADIUS'` (largest inscribed sphere).
- `distance` — `'EUCLIDEAN'`, `'MANHATTAN'`, `'CHEBYCHEV'`, `'MINKOWSKI'`. Distance metric for the cells.
- Inputs: Vector, Scale, Smoothness (Smooth F1 only), Exponent (Minkowski only), Randomness (0–1, default 1.0 — drop toward 0 to align cells to a grid).
- Outputs: Distance, Color, Position, W (in 4D).

### Wave Texture
`ShaderNodeTexWave`. Banded / ringed sinusoid. Parameters: Type (`Bands`/`Rings`), Direction, Profile (`Sine`/`Saw`/`Triangle`), Distortion, Detail. Good for wood grain when combined with Noise distortion.

**Scale-vs-detail tradeoff:** Higher Detail = more octaves = exponentially more cost per sample. Use 2–4 Detail for backgrounds, 6–8 for hero. Above 12 you are paying for noise below pixel resolution.

---

## Vector / Texture Coordinates

- **Texture Coordinate** (`ShaderNodeTexCoord`) — Outputs Generated (object-space bbox normalized), Normal (object-space normal), UV (active UV map), Object (object-space position, can target another Object for projected texturing), Camera (camera-space position), Window (screen-space 0–1), Reflection (reflection vector — useful for matcap-like effects).
- **UV Map** (`ShaderNodeUVMap`) — Outputs a *specific named* UV map, not the active one. Set `uv_map = 'UVMap.001'`. Required when a mesh has multiple UV layers.
- **Mapping** (`ShaderNodeMapping`) — Location / Rotation / Scale on a vector. `vector_type`: `'POINT'`, `'TEXTURE'` (inverse — for moving the texture, not the surface), `'VECTOR'`, `'NORMAL'`. Sits between coordinates and textures.
- **Vector Rotate** (`ShaderNodeVectorRotate`) — Rotates a vector around an axis or via Euler. Cheaper than full Mapping for rotation-only.
- **Vector Curves** (`ShaderNodeVectorCurve`) — Per-axis curve remap. Slow to author, useful for warping coordinates non-linearly.
- **Vector Math** (`ShaderNodeVectorMath`) — Operation enum: Add, Subtract, Multiply, Divide, Cross Product, Project, Reflect, Refract, Dot Product, Distance, Length, Scale, Normalize, Wrap, Snap, Floor, Ceil, Modulo, Fraction, Absolute, Minimum, Maximum, Sine, Cosine, Tangent.
- **Vector Displacement** (`ShaderNodeVectorDisplacement`) — Reads a tangent-or-object-space RGB displacement texture, outputs a vector for the Material Output Displacement input. See section 17.
- **Displacement** (`ShaderNodeDisplacement`) — Converts a scalar height into a vector along the normal. Inputs: Height, Midlevel, Scale, Normal. Feeds Material Output Displacement.
- **Bump** (`ShaderNodeBump`) — Synthetic normal perturbation from a height value. Inputs: Strength, Distance, Height, Normal. Output: Normal. See section 16.
- **Normal Map** (`ShaderNodeNormalMap`) — Reads a tangent-space normal map and outputs a perturbed normal. `space`: `'TANGENT'` (default — requires a UV map), `'OBJECT'`, `'WORLD'`, `'BLENDER_OBJECT'`, `'BLENDER_WORLD'`. Inputs: Strength, Color. Output: Normal.

---

## Color Nodes

- **Mix Color** (`ShaderNodeMix` with `data_type='RGBA'`) — The unified 4.x Mix node. Replaces the old MixRGB. `blend_type`: `'MIX'`, `'DARKEN'`, `'MULTIPLY'`, `'COLOR_BURN'`, `'LIGHTEN'`, `'SCREEN'`, `'COLOR_DODGE'`, `'ADD'`, `'OVERLAY'`, `'SOFT_LIGHT'`, `'LINEAR_LIGHT'`, `'DIFFERENCE'`, `'EXCLUSION'`, `'SUBTRACT'`, `'DIVIDE'`, `'HUE'`, `'SATURATION'`, `'COLOR'`, `'VALUE'`. Properties: `clamp_factor`, `clamp_result`.
- **Color Ramp** (`ShaderNodeValToRGB`) — Maps a 0–1 float into a gradient. Add/remove/move color stops in `node.color_ramp.elements`. Interpolation: `'EASE'`, `'CARDINAL'`, `'LINEAR'`, `'B_SPLINE'`, `'CONSTANT'`. The single most-used "tweak a procedural" tool.
- **RGB Curves** (`ShaderNodeRGBCurve`) — Per-channel curve remap, plus a combined Composite curve. Authored only in the UI; not Python-friendly.
- **Hue/Saturation/Value** (`ShaderNodeHueSaturation`) — Color shift. Inputs: Hue (0.5 = no shift), Saturation, Value, Fac, Color. Cheap for tinting.
- **Brightness/Contrast** (`ShaderNodeBrightContrast`) — Linear remap. Simpler than RGB Curves.
- **Gamma** (`ShaderNodeGamma`) — Power function on color. Quick contrast tweak.
- **Invert** (`ShaderNodeInvert`) — 1 - color. Fac to blend.
- **Light Falloff** (`ShaderNodeLightFalloff`) — Cycles-only. Modifies a light's falloff curve (Quadratic / Linear / Constant). Connect to Emission Strength on a Light's shader tree.

---

## Math / Map Range / Float Curve

### Math
`ShaderNodeMath`. Single-float ops via the `operation` property. Two value inputs (some ops use only one). `use_clamp` clamps output to 0–1.

Full operation list (4.x):
- **Functions:** Add, Subtract, Multiply, Divide, Multiply Add, Power, Logarithm, Square Root, Inverse Square Root, Absolute, Exponent.
- **Comparison:** Minimum, Maximum, Less Than, Greater Than, Sign, Compare (with epsilon), Smooth Minimum, Smooth Maximum.
- **Rounding:** Round, Floor, Ceil, Truncate, Fraction, Modulo, Floored Modulo, Wrap, Snap, Ping-Pong.
- **Trigonometric:** Sine, Cosine, Tangent, Arcsine, Arccosine, Arctangent, Arctan2, Hyperbolic Sine, Hyperbolic Cosine, Hyperbolic Tangent.
- **Conversion:** Radians, Degrees.

### Map Range
`ShaderNodeMapRange`. Remap a value from one range to another. `interpolation_type`:
- `'LINEAR'` — straight remap.
- `'STEPPED'` — quantized output with a Steps input.
- `'SMOOTHSTEP'` — Hermite smooth (S-curve).
- `'SMOOTHERSTEP'` — fifth-order smooth.

Inputs: Value, From Min, From Max, To Min, To Max, (Steps). `data_type`: `'FLOAT'` or `'FLOAT_VECTOR'`. `clamp` property forces output into the target range.

### Float Curve
`ShaderNodeFloatCurve`. Single-curve remap of a float. UI-authored. Useful for arbitrary nonlinear shaping (S-curves, falloffs, custom easing) without stacking math nodes.

---

## Converter Nodes

- **Combine XYZ / Separate XYZ** — Float ↔ Vector. `ShaderNodeCombineXYZ` / `ShaderNodeSeparateXYZ`.
- **Combine RGB / Separate RGB** — Float ↔ Color (legacy in 4.x; the unified Combine Color / Separate Color now covers RGB/HSV/HSL).
- **Combine Color** (`ShaderNodeCombineColor`) / **Separate Color** (`ShaderNodeSeparateColor`) — `mode`: `'RGB'`, `'HSV'`, `'HSL'`. Replaced the old per-mode nodes in 3.3+.
- **RGB to BW** (`ShaderNodeRGBToBW`) — Color → Float via luminosity weights.
- **Blackbody** (`ShaderNodeBlackbody`) — Temperature in Kelvin → Color along the Planckian locus. 1500K = ember, 3200K = tungsten, 5500K = daylight, 6500K = overcast, 10000K = blue sky.
- **Wavelength** (`ShaderNodeWavelength`) — Single wavelength in nm → visible-spectrum Color. 380–780nm.
- **Shader to RGB** (`ShaderNodeShaderToRGB`) — **EEVEE ONLY.** Evaluates a connected BSDF and outputs RGB + Alpha. Silently does nothing in Cycles (passes black). Foundation of EEVEE toon / NPR workflows.
- **Clamp** (`ShaderNodeClamp`) — Clamps a value between Min and Max. `clamp_type`: `'MINMAX'`, `'RANGE'`.

---

## Input Nodes

- **Geometry** (`ShaderNodeNewGeometry`) — Outputs: Position (world-space), Normal, Tangent, True Normal (un-bumped), Incoming (view direction), Parametric (per-face UV), Backfacing (1 if camera sees the back face), Pointiness (curvature — Cycles only, approximate in EEVEE), Random Per Island (per-mesh-island hash).
- **Object Info** (`ShaderNodeObjectInfo`) — Location (object world position), Color (the object's display color), Alpha, Object Index (the integer `pass_index`), Material Index, Random (per-object hash). Useful for randomizing instances without per-object materials.
- **Light Path** (`ShaderNodeLightPath`) — **Mostly Cycles only.** Outputs: Is Camera Ray, Is Shadow Ray, Is Diffuse Ray, Is Glossy Ray, Is Singular Ray, Is Reflection Ray, Is Transmission Ray, Ray Length, Ray Depth, Diffuse Depth, Glossy Depth, Transparent Depth, Transmission Depth. EEVEE Next supports Is Camera and Is Shadow (in the world tree); other outputs return 0. Use to make objects invisible to certain ray types ("light linking via shader").
- **Layer Weight** (`ShaderNodeLayerWeight`) — Outputs Fresnel and Facing. Fresnel uses Blend input as the IOR-ish factor; Facing is a simple dot(N, view) ramp. Mix-Shader-Fac default.
- **Fresnel** (`ShaderNodeFresnel`) — Pure Fresnel by IOR. Single input. For physically correct mix factors.
- **Particle Info** (`ShaderNodeParticleInfo`) — Index, Random, Age, Lifetime, Location, Size, Velocity, Angular Velocity. For legacy particle systems.
- **Curves Info** (`ShaderNodeHairInfo` / `ShaderNodeCurvesInfo`) — Per-strand: Is Strand, Intercept (root-to-tip 0–1), Length, Thickness, Tangent Normal, Random.
- **Point Info** — Per-point cloud info: Position, Radius, Random.
- **Volume Info** — See Volume section.
- **RGB** (`ShaderNodeRGB`) — Constant color value node. Convenient for shared color picks.
- **Value** (`ShaderNodeValue`) — Constant float. Often the target of drivers.
- **Bevel** (`ShaderNodeBevel`) — **Cycles only.** Outputs a normal vector with rounded edges (without actually beveling geometry). Inputs: Radius, Samples, Normal.
- **Ambient Occlusion** (`ShaderNodeAmbientOcclusion`) — Per-shader AO. In Cycles, raytraced and accurate. In EEVEE Next, approximates via screen-space — quality varies.
- **Hair Info** — alias for Curves Info on hair geometry.
- **Wireframe** (`ShaderNodeWireframe`) — Outputs 1 on edges, 0 on faces. `use_pixel_size` toggles screen-space vs object-space thickness.
- **Camera Data** (`ShaderNodeCameraData`) — View Vector, View Z Depth, View Distance.
- **UV Along Stroke** (Linestyle-only).
- **Attribute** (`ShaderNodeAttribute`) — Reads a named mesh / object / instance attribute. `attribute_type`: `'GEOMETRY'`, `'OBJECT'`, `'INSTANCER'`, `'VIEW_LAYER'`. The bridge from Geometry Nodes-authored attributes into shaders.

---

## Bump and Normal Handling

Three different ways to add surface detail without subdividing geometry:

### Bump node
`ShaderNodeBump`. Cheap. Takes a scalar **Height** input, computes the gradient via differentials, and outputs a perturbed Normal. Inputs:
- **Strength** — 0–1, blend with un-bumped normal.
- **Distance** — multiplier on the height effect. Like Strength but on the source scalar.
- **Height** — the scalar (typically Noise or grayscale image).
- **Normal** — base normal to perturb. If unconnected, uses geometry normal.
- `invert` property — flips height direction.

Bump is a **per-pixel illusion**. Silhouettes still show flat geometry. Use for fabric weave, paint texture, small dents.

### Normal Map node
`ShaderNodeNormalMap`. Reads a tangent-space (or object/world-space) normal map and produces a perturbed normal. Inputs: Strength, Color. Tangent space is the default and requires a UV map. Always set the Image Texture colorspace to **Non-Color** before feeding it here.

### Vector Displacement node
`ShaderNodeVectorDisplacement`. Reads an RGB texture where each channel is a 3D offset. Outputs a vector for Material Output → Displacement. Used for high-frequency sculpt detail bakes.

**Bump vs Displacement (Material Output) — which to use:**
- **Bump** = fake. No geometry change. Works in EEVEE.
- **Displacement** input on Material Output = real geometry motion when the material's `cycles.displacement_method` is `'DISPLACEMENT'` or `'BOTH'`. Requires subdivided geometry (Adaptive Subdivision in Cycles is the go-to). EEVEE falls back to bump regardless.

You can connect a Bump node *and* feed Material Output Displacement — they stack.

---

## Vector Displacement vs Bump vs Displacement — Three Costs

| Method | Renders silhouette | Needs subdivided geometry | EEVEE | Cycles | Cost |
|---|---|---|---|---|---|
| Bump node → BSDF Normal | No (fake) | No | Yes | Yes | Cheap |
| Displacement node → Output Displacement (`BUMP` method) | No (same as Bump) | No | Yes (bump only) | Yes | Cheap |
| Displacement node → Output Displacement (`DISPLACEMENT` method) | Yes | **Yes** | No (falls back) | Yes | Heavy |
| Vector Displacement → Output Displacement | Yes (in 3D directions) | **Yes** | No (falls back) | Yes | Heavy |

Cycles displacement requires the material's `Settings → Surface → Displacement` set to `'Displacement Only'` or `'Displacement and Bump'`. Adaptive Subdivision (`object.cycles.use_adaptive_subdivision = True`) lets Cycles refine only what the camera sees.

---

## World Shader Trees

The world tree (`world.node_tree`) defines environment lighting and the visible background. Same node toolkit, different output node: `ShaderNodeOutputWorld` with a Surface input that takes a Background or Emission closure.

**Standard HDRI setup:**
```
Texture Coordinate (Generated)
    → Mapping (Rotation Z = sun angle)
    → Environment Texture (HDRI, colorspace Linear Rec.709)
    → Background (Strength = exposure multiplier)
    → World Output
```

**Sky Texture** alternative — procedural sky, no HDRI:
- `sky_type = 'NISHITA'` — modern atmospheric scattering. Inputs: Sun Disc, Sun Size, Sun Intensity, Sun Elevation, Sun Rotation, Altitude, Air, Dust, Ozone.
- `sky_type = 'HOSEK_WILKIE'` — older analytical sky.
- `sky_type = 'PREETHAM'` — oldest, fastest.

Light path filtering in world: in Cycles, the world is sampled by all ray types; you can wrap the Background in a Mix Shader where the Fac is `Light Path → Is Camera Ray` to give the camera a different background than what lights the scene. EEVEE Next supports Is Camera and Is Shadow only in the world tree.

---

## OSL (Open Shading Language) in Cycles

`ShaderNodeScript`. Embeds an OSL script as a custom shader node. Cycles only. **CPU only** on Apple Silicon — OSL is not yet GPU-compiled for Metal as of 4.5 LTS. Toggle `cycles.shading_system = True` on the scene to enable.

Use when:
- You need a math op or pattern not exposed as a built-in node.
- You're porting a published OSL shader from elsewhere.
- You need a custom BSDF closure.

Avoid when:
- You're rendering on GPU and need speed — OSL forces a slower CPU path.
- The job can be done with a few Math + Vector Math nodes — usually faster end-to-end.

---

## Group Nodes for Shader Trees

`ShaderNodeGroup` wraps a sub-tree as a reusable node.

**Creating a group via Python:**
```python
group = bpy.data.node_groups.new('MyShader', 'ShaderNodeTree')
# Inputs / outputs are interface sockets (4.0+ API):
group.interface.new_socket(name='Color', in_out='INPUT', socket_type='NodeSocketColor')
group.interface.new_socket(name='Shader', in_out='OUTPUT', socket_type='NodeSocketShader')
# Internal Group Input / Group Output nodes:
gi = group.nodes.new('NodeGroupInput')
go = group.nodes.new('NodeGroupOutput')
# ... build the internal graph, link to gi outputs and go inputs.

# Use it in a material:
inst = mat.node_tree.nodes.new('ShaderNodeGroup')
inst.node_tree = group
```

The 4.0 release changed the group I/O API — `group.inputs.new(...)` is gone, replaced by `group.interface.new_socket(...)`. Older code will silently fail.

Groups can nest. A group can contain other groups. They're the primary mechanism for reusable shader systems (e.g., a "PBR Texture Set" group that takes file paths and produces a shader).

---

## The bpy API Surface for Shader Nodes

### Accessing the tree
```python
mat = bpy.data.materials['M']
mat.use_nodes = True            # required, or node_tree is None
tree = mat.node_tree
nodes = tree.nodes              # collection
links = tree.links              # connection collection
```

### Creating nodes
```python
n = tree.nodes.new(type='ShaderNodeBsdfPrincipled')
n.location = (200, 0)
n.label = 'Body'                # user-visible label
n.name = 'BodyBSDF'             # python-unique id
```

### Linking sockets
```python
img = tree.nodes.new('ShaderNodeTexImage')
bsdf = tree.nodes['Principled BSDF']
tree.links.new(img.outputs['Color'], bsdf.inputs['Base Color'])
```

`tree.links.new(from_socket, to_socket)` — order is from → to. Returns the link object. If a socket already has an incoming link, the new one replaces it (single-input rule for input sockets).

### Setting input values
```python
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)   # 4-tuple, RGBA
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Metallic'].default_value = 1.0
```
Setting `default_value` on a connected input has no visual effect — the link wins. Disconnect the link first.

### Output target (engine scoping)
```python
out = tree.nodes['Material Output']
out.target = 'CYCLES'   # 'EEVEE' or 'ALL'
```

### Common node type strings (paste-ready)

| Node | `type=` string |
|---|---|
| Material Output | `ShaderNodeOutputMaterial` |
| World Output | `ShaderNodeOutputWorld` |
| Light Output | `ShaderNodeOutputLight` |
| Principled BSDF | `ShaderNodeBsdfPrincipled` |
| Diffuse BSDF | `ShaderNodeBsdfDiffuse` |
| Emission | `ShaderNodeEmission` |
| Glass BSDF | `ShaderNodeBsdfGlass` |
| Glossy BSDF | `ShaderNodeBsdfGlossy` |
| Refraction BSDF | `ShaderNodeBsdfRefraction` |
| Translucent BSDF | `ShaderNodeBsdfTranslucent` |
| Transparent BSDF | `ShaderNodeBsdfTransparent` |
| Principled Hair BSDF | `ShaderNodeBsdfHairPrincipled` |
| Subsurface Scattering | `ShaderNodeSubsurfaceScattering` |
| Toon BSDF | `ShaderNodeBsdfToon` |
| Mix Shader | `ShaderNodeMixShader` |
| Add Shader | `ShaderNodeAddShader` |
| Background | `ShaderNodeBackground` |
| Principled Volume | `ShaderNodeVolumePrincipled` |
| Volume Scatter | `ShaderNodeVolumeScatter` |
| Volume Absorption | `ShaderNodeVolumeAbsorption` |
| Image Texture | `ShaderNodeTexImage` |
| Environment Texture | `ShaderNodeTexEnvironment` |
| Sky Texture | `ShaderNodeTexSky` |
| Noise Texture | `ShaderNodeTexNoise` |
| Voronoi Texture | `ShaderNodeTexVoronoi` |
| Wave Texture | `ShaderNodeTexWave` |
| Magic Texture | `ShaderNodeTexMagic` |
| Brick Texture | `ShaderNodeTexBrick` |
| Checker Texture | `ShaderNodeTexChecker` |
| Gradient Texture | `ShaderNodeTexGradient` |
| White Noise Texture | `ShaderNodeTexWhiteNoise` |
| IES Texture | `ShaderNodeTexIES` |
| Texture Coordinate | `ShaderNodeTexCoord` |
| UV Map | `ShaderNodeUVMap` |
| Mapping | `ShaderNodeMapping` |
| Vector Math | `ShaderNodeVectorMath` |
| Vector Rotate | `ShaderNodeVectorRotate` |
| Bump | `ShaderNodeBump` |
| Normal Map | `ShaderNodeNormalMap` |
| Displacement | `ShaderNodeDisplacement` |
| Vector Displacement | `ShaderNodeVectorDisplacement` |
| Mix (unified) | `ShaderNodeMix` |
| Color Ramp | `ShaderNodeValToRGB` |
| RGB Curves | `ShaderNodeRGBCurve` |
| Hue/Saturation | `ShaderNodeHueSaturation` |
| Bright/Contrast | `ShaderNodeBrightContrast` |
| Gamma | `ShaderNodeGamma` |
| Invert Color | `ShaderNodeInvert` |
| Math | `ShaderNodeMath` |
| Map Range | `ShaderNodeMapRange` |
| Float Curve | `ShaderNodeFloatCurve` |
| Clamp | `ShaderNodeClamp` |
| Combine XYZ | `ShaderNodeCombineXYZ` |
| Separate XYZ | `ShaderNodeSeparateXYZ` |
| Combine Color | `ShaderNodeCombineColor` |
| Separate Color | `ShaderNodeSeparateColor` |
| RGB to BW | `ShaderNodeRGBToBW` |
| Blackbody | `ShaderNodeBlackbody` |
| Wavelength | `ShaderNodeWavelength` |
| Shader to RGB | `ShaderNodeShaderToRGB` |
| Geometry | `ShaderNodeNewGeometry` |
| Object Info | `ShaderNodeObjectInfo` |
| Light Path | `ShaderNodeLightPath` |
| Layer Weight | `ShaderNodeLayerWeight` |
| Fresnel | `ShaderNodeFresnel` |
| Attribute | `ShaderNodeAttribute` |
| Wireframe | `ShaderNodeWireframe` |
| Bevel | `ShaderNodeBevel` |
| Ambient Occlusion | `ShaderNodeAmbientOcclusion` |
| Volume Info | `ShaderNodeVolumeInfo` |
| Particle Info | `ShaderNodeParticleInfo` |
| Curves Info | `ShaderNodeHairInfo` |
| RGB | `ShaderNodeRGB` |
| Value | `ShaderNodeValue` |
| Group | `ShaderNodeGroup` |
| Group Input | `NodeGroupInput` |
| Group Output | `NodeGroupOutput` |
| Frame | `NodeFrame` |
| Reroute | `NodeReroute` |
| OSL Script | `ShaderNodeScript` |

---

## Cycles vs EEVEE Next — Feature Compatibility

**Identical behavior in both engines:**
- Principled BSDF base/metallic/roughness/IOR/coat/sheen/emission/alpha
- Diffuse, Glossy, Refraction, Glass, Transparent, Translucent, Emission BSDFs
- All texture nodes (Image, Environment, Sky, Noise, Voronoi, Wave, Magic, Brick, Checker, Gradient, White Noise)
- All Color, Math, Vector Math, Map Range, Mix, Color Ramp nodes
- Bump and Normal Map nodes
- Texture Coordinate, UV Map, Mapping, Attribute

**Cycles only:**
- **Bevel node** (`ShaderNodeBevel`)
- **OSL Script node** (`ShaderNodeScript`) and the entire OSL system
- **Light Path node** — most outputs work only in Cycles; EEVEE Next supports Is Camera and Is Shadow in the world tree only
- **True surface Displacement** — EEVEE always falls back to bump
- **Principled BSDF Subsurface with `RANDOM_WALK` method** — fully physically accurate. EEVEE uses an approximation.
- **Caustics through transmission** — Cycles only (and even then requires manual caustics setup or Manifold Next-Event Estimation)
- **Pointiness** output on Geometry node — Cycles only (returns 0 in EEVEE)
- **Volume scattering with many light bounces** — Cycles converges, EEVEE Next froxel-approximates

**EEVEE only:**
- **Shader to RGB** (`ShaderNodeShaderToRGB`) — the foundation of EEVEE NPR. Silently returns black in Cycles.
- **Specular BSDF** (`ShaderNodeEeveeSpecular`) — legacy EEVEE-only, avoid in new work.

**Different behavior between engines:**
- **Volumetrics** — Cycles is path-traced, EEVEE Next uses a froxel grid. Same node tree, different look. EEVEE Next is faster and supports nested volumes; Cycles is more physically accurate.
- **Subsurface Scattering** — Cycles Random Walk is most accurate; EEVEE Next approximates via screen-space blur of the diffuse pass.
- **Anisotropy** — both support it; Cycles is more accurate at high anisotropy.
- **Ambient Occlusion node** — Cycles raytraces; EEVEE Next screen-space approximates.
- **Reflection** — Cycles is ground truth; EEVEE Next uses screen-space + light probes, with raytraced reflections available 4.2+.

---

## Common Shader Recipes

### 1. Photoreal PBR from an Image Set
For a texture set with `albedo.png`, `normal.png`, `roughness.png`, `metallic.png`, `ao.png`:
```
albedo  (sRGB)      → MixColor (Multiply, ao) → Principled Base Color
ao      (Non-Color)
normal  (Non-Color) → Normal Map (Tangent) → Principled Normal
roughness (Non-Color) → Principled Roughness
metallic  (Non-Color) → Principled Metallic
```
AO multiplied into base color is the standard cheat — for true AO use the Ambient Occlusion node.

### 2. Glass with Chromatic Dispersion
```
Principled BSDF (Transmission=1, IOR=1.5, Roughness=0)
→ Material Output
```
For dispersion (rainbow fringes), drive three separate Glass BSDFs with slightly different IOR (1.50 / 1.52 / 1.54) for R/G/B channels, combine via Add Shader. Cycles converges; EEVEE doesn't show dispersion correctly.

### 3. Toon / Cel Shading
**EEVEE:**
```
Diffuse BSDF → Shader to RGB → Color Ramp (Constant interpolation, 3-4 stops) → Emission → Output
```
**Cycles:** use Toon BSDF directly with `component='DIFFUSE'`.

### 4. Procedural Marble
```
TexCoord (Generated) → Mapping
  → Noise (Scale=3, Detail=8) + Voronoi (F1, Scale=1.5) → Mix (Mix mode, Fac=0.5)
  → Color Ramp (white → veined dark)
  → Principled Base Color
```

### 5. HDRI Environment Lighting (World tree)
```
TexCoord (Generated) → Mapping → Environment Texture (HDRI, Linear Rec.709)
  → Background (Strength = exposure)
  → World Output
```

### 6. Volumetric Atmosphere
```
Principled Volume (Density=0.05, Anisotropy=0.3, Color=(0.9,0.95,1.0))
  → Material Output Volume
```
Apply to a large cube containing the scene. EEVEE Next: increase Volumetric Tile Size in render settings if it's grainy.

### 7. Animated Noise (4D)
```
Scene Time (output: Seconds) → Math (Multiply by speed) → Noise W
Noise (4D, Scale=2, Detail=4) → Color Ramp → Principled
```

### 8. Anisotropic Brushed Metal
```
Tangent (UV map) → Principled Tangent
Principled (Metallic=1, Roughness=0.3, Anisotropic=0.8, Anisotropic Rotation=0.0)
```
For the brushed-circle look, use a Tangent node with `direction_type='RADIAL'` and an axis.

### 9. Emissive UI / Signage
```
Principled (Base Color = sign color, Emission Color = sign color, Emission Strength = 5.0)
```
EEVEE: enable Bloom (4.2+ Compositor or post). Cycles: just turn up Strength — the HDR is preserved through to output.

### 10. Iridescent Thin Film
```
Layer Weight (Blend=0.3) → Facing → Map Range (0 → 200, 1 → 600) → Principled Thin Film Thickness
Principled (Thin Film IOR=1.33, Base Color=neutral, Metallic depends on material)
```
The thickness sweep across the angle creates the soap-bubble rainbow.

### 11. Object-ID Random Color
```
Object Info (Random) → Color Ramp (rainbow stops) → Principled Base Color
```
Every instance gets a different color without per-object materials.

### 12. Wood Grain
```
TexCoord (Object) → Mapping (Scale Z = 20)
→ Noise (Distortion=2) → Wave (Bands, Distortion driven by Noise)
→ Color Ramp (light wood → dark wood)
→ Principled (Roughness ~0.6)
```

---

## Common Footguns

1. **Color sockets need 4-tuples for `default_value`.** Writing `(0.8, 0.2, 0.1)` raises a Python error. Always include alpha: `(0.8, 0.2, 0.1, 1.0)`.

2. **Color space matters on Image Texture.** Normals, roughness, metallic, AO, displacement all need `colorspace_settings.name = 'Non-Color'`. sRGB-decoded normals produce subtly wrong lighting that's hard to diagnose.

3. **Shader to RGB silently does nothing in Cycles.** It returns black. If your toon-shader works in EEVEE viewport but turns the object black in Cycles, this is the cause. Use Toon BSDF in Cycles.

4. **`tree.links.new(a, b)` is from → to.** Reversing it produces a link that won't error but won't carry data correctly. The argument order is `from_socket, to_socket`.

5. **Setting `default_value` on a driven or linked input has no visual effect.** The connection / driver overrides it. Disconnect first, or write into the driver target.

6. **Material Output needs Surface connected — but Volume and Displacement are optional.** Leaving Surface empty produces a black surface; leaving Volume empty is fine.

7. **`node.outputs[0]` vs `node.outputs['BSDF']`.** Index works but breaks when nodes are reordered or have multiple outputs. Always prefer the name lookup. Names are stable across Blender versions for built-in nodes.

8. **EEVEE Next ignores Material Output Displacement unless the material's surface displacement is set to bump.** True displacement is Cycles-only. Design Cycles-displaced scenes with this in mind.

9. **The 4.0 Principled rename broke older Python scripts.** Old: `bsdf.inputs['Specular'].default_value`. New: `bsdf.inputs['Specular IOR Level'].default_value`. Old: `bsdf.inputs['Clearcoat']`. New: `bsdf.inputs['Coat Weight']`. Old: `bsdf.inputs['Subsurface']`. New: `bsdf.inputs['Subsurface Weight']`. Check Blender version before assuming names.

10. **Group interface API changed in 4.0.** `group.inputs.new(...)` is gone — use `group.interface.new_socket(name=..., in_out='INPUT', socket_type='NodeSocketColor')`. Scripts that worked in 3.x silently break.

11. **Nodes off the visible area still cook.** Disconnected nodes that don't reach Material Output are dead, but they still get compiled. Delete them or wrap unused chains in a muted Frame.

12. **Musgrave Texture is gone in 4.1+.** Its modes are merged into Noise Texture via `noise_type`. Old files load with a legacy compatibility node; new code should use `ShaderNodeTexNoise` with the appropriate `noise_type`.

13. **`use_nodes = False` makes `node_tree` return None.** Always set `mat.use_nodes = True` before reaching for the tree.

14. **`material.node_tree.nodes['Principled BSDF']` works only if that's the node's `name` (not label).** Renaming via the N-panel changes the *label*, not the name. Name is unique within a tree; label is purely cosmetic.

15. **Cycles `displacement_method` is on the material, not the modifier.** `material.cycles.displacement_method = 'BOTH'`. Without setting this, your Displacement input on Material Output silently behaves like bump even in Cycles.

16. **Sheen is not Velvet.** The 4.0 release removed the Velvet BSDF and folded similar behavior into Principled's Sheen layer. The math is different — sheen sits on top of the base, velvet was a standalone. Don't expect identical results when porting old scenes.

17. **`Anisotropic Rotation` is in turns, not radians.** 0.25 = 90°, 0.5 = 180°, 1.0 = full turn. Most other rotations in shader nodes are radians — this one is the exception.

18. **Specular IOR Level default is 0.5, not 1.0.** 0.5 is the physically-correct dielectric F0 for IOR=1.5. Setting it to 1.0 doubles the specular, which is non-physical but matches some legacy assets.
