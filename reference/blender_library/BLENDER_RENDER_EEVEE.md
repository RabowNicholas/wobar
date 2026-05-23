---
title: EEVEE Next — Real-Time-ish Render Engine Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: EEVEE Next render-engine reference — the 4.2+ rewrite, shadow systems (virtual shadow maps), raytracing options (screen-space, horizon scan, raytrace), light probes (Irradiance Volume, Reflection Plane, Sphere), depth of field, motion blur, bloom replacement, the bpy `scene.eevee` surface, M1/Metal specifics, EEVEE vs Cycles decision criteria.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_APPLE_SILICON.md, BLENDER_RENDER_CYCLES.md
---

# EEVEE NEXT — REAL-TIME-ISH RENDER ENGINE REFERENCE

EEVEE Next is Blender's **GPU-rasterized** render engine, rewritten from the ground up and shipped in Blender 4.2 LTS. It targets the fast / stylized / preview niche. The path-traced engine for offline cinematic work is Cycles — see `[[BLENDER_RENDER_CYCLES]]`.

Terminology note: in **4.2+**, "EEVEE" *means* EEVEE Next. The legacy EEVEE engine was retired. Old tutorials, addons, and forum posts that say "EEVEE" usually mean the legacy engine and will not match what you see in 4.2+. The visible UI label is just "EEVEE"; the Python identifier `BLENDER_EEVEE_NEXT` is the only place "Next" survives — and it gets renamed back to `BLENDER_EEVEE` in Blender 5.0+.

**Core facts:**
- EEVEE Next is **GPU rasterized** — it draws polygons through the same Vulkan/Metal pipeline as the viewport, not path-traced. Fast, viewport-friendly, less physically accurate than Cycles.
- Runs on **Metal** on Apple Silicon. Same backend the viewport uses; no separate compile target. See `[[BLENDER_APPLE_SILICON]]`.
- Uses **Virtual Shadow Maps** (4.2+) — replaces legacy shadow cube/cascade maps. One unified tiled shadow atlas, per-light, allocated on demand.
- Supports **screen-space and ray-traced reflections / refractions / GI** — three modes per effect: Raytrace, Screen Trace, None.
- Indirect light comes from **light probes**: Irradiance Volume (baked diffuse GI), Reflection Plane (planar mirror), Reflection Sphere (cube map). Probes are baked offline via `bpy.ops.scene.light_cache_bake()`.
- **Sample-per-pixel** model — like Cycles, but counts are far lower (16–64 for finals, 8–16 for previews) and samples drive **Temporal Anti-Aliasing (TAA)**, not path noise.
- Supports **volumetrics** — tiled volume textures, Volume Max Ray Depth, volume bounding boxes.
- **Displacement** is limited vs Cycles — adaptive subdivision-style true displacement is Cycles-only; EEVEE can do shader-level displacement on subdivided meshes with caveats.
- **Bloom is gone** as a built-in panel — moved to the Compositor's **Glare** node (or post). Same for legacy SSAO/SSR panels.
- The renderer string in `bpy` is **`'BLENDER_EEVEE_NEXT'`** in Blender 4.2 – 4.5. Legacy `'BLENDER_EEVEE'` no longer resolves in 4.2+ (and is reclaimed by EEVEE Next itself in 5.0+).
- HDR / linear pipeline is intact — color management is the same as Cycles (AgX, Filmic, Khronos PBR Neutral, Standard, Raw); see `[[BLENDER_MATERIALS]]`.
- Shader graph compatibility: every Principled BSDF feature now works under EEVEE Next, including subsurface and transmission. Shader-to-RGB remains EEVEE-only.

---

## Setting the Engine

```python
import bpy
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'   # 4.2 – 4.5
# In 5.0+ the string is reclaimed back to:
# bpy.context.scene.render.engine = 'BLENDER_EEVEE'
```

**Verify at install time** which string the installed build accepts:

```python
items = bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys()
# items will include 'BLENDER_EEVEE_NEXT' (4.2–4.5) or 'BLENDER_EEVEE' (5.0+)
```

Older docs, addons, and snippets will reference `'BLENDER_EEVEE'` — in a 4.2 – 4.5 build this throws `TypeError: enum "BLENDER_EEVEE" not found in ('BLENDER_EEVEE_NEXT', 'BLENDER_WORKBENCH', 'CYCLES')`. Match the string to the installed version, or use the introspection above.

The render properties surface for the engine lives at `scene.eevee` (a `SceneEEVEE` struct). Render-format properties (resolution, output path, file format) live at `scene.render` and are shared with Cycles.

---

## Sampling

EEVEE samples are not path-trace samples — they are **Temporal Anti-Aliasing (TAA)** samples. Each sample reprojects the previous frame and jitters subpixel offsets / shadow rays / probe rays. More samples → smoother edges, smoother shadows, less raytrace noise.

**Typical sample counts:**
- Final render: **64** (still 4–8× faster than a comparable Cycles render)
- Stylized / flat final: **16–32**
- Preview animation: **8–16**
- Viewport rotate: **1–8** (TAA accumulates while idle)

**Sampling panel** (Properties → Render Properties → Sampling):
- **Render Samples** — `scene.eevee.taa_render_samples` (default 64)
- **Viewport Samples** — `scene.eevee.taa_samples` (default 16)
- **Use Temporal Reprojection** — `scene.eevee.use_taa_reprojection` (default True; turn off for fully deterministic frames)

TAA reprojection causes **ghosting** on fast-moving objects with low sample counts. The fix is either more samples or motion vectors via the motion blur pass.

---

## Shadows — Virtual Shadow Maps

Virtual Shadow Maps (VSM) replace the old cube map / cascade shadow system in 4.2+. One pool of GPU memory, partitioned into tiles, allocated on demand by visible lights and shadow casters. Biases are computed automatically.

**Per-scene properties** (`scene.eevee`):
- `shadow_pool_size` — total shadow atlas size, MB. Default 512. Bump to 1024 / 2048 for large scenes with many lights. Out-of-memory = missing shadows, not a crash.
- `shadow_ray_count` — rays per shadow sample for soft shadows. Default 1.
- `shadow_step_count` — steps along each shadow ray. Default 6.

**Per-light properties** (`light.data` for any Light object):
- `light.data.use_shadow` — boolean, default True.
- `light.data.shadow_soft_size` — radius of the light source for soft shadow penumbra. Larger = softer shadow.
- `light.data.shadow_filter_radius` — extra screen-space softening on top of the ray-traced penumbra.

Contact shadows are **gone** in 4.2+ — VSM ray tracing handles short-range occlusion natively. The old `use_contact_shadows` property no longer exists.

The old "Cube Size" / "Cascade Size" / shadow buffer settings are also gone. VSM is fully automatic.

---

## Raytracing

The 4.2 Raytracing panel is the single biggest feature in EEVEE Next. Three indirect-light effects (Reflections, Refractions, Diffuse GI) each get one of three modes:

**Modes:**
1. **Raytrace** — true rays in BVH against the scene. Accurate, slowest. Falls back to light probes when a ray misses or exits the BVH budget.
2. **Screen Trace** — screen-space ray march against the depth buffer. Fast. Fails at screen edges, behind occluders, on off-camera geometry. Falls back to light probes.
3. **None** — disabled; reads exclusively from light probes.

**Panel properties** (`scene.eevee`):
- `use_raytracing` — master toggle, default True.
- `ray_tracing_method` — `'SCREEN'` (Screen Trace) or `'PROBE'` (probe-only). Per-method override available on each BSDF effect via the inner `ray_tracing_options` struct.
- `ray_tracing_options.resolution_scale` — `'1'` (full), `'2'` (half), `'4'` (quarter). Halving roughly doubles speed at cost of denoising quality.
- `ray_tracing_options.sample_clamp` — clamps fireflies. Default 10.0.
- `ray_tracing_options.screen_trace_max_roughness` — above this roughness, fall back to probes. Default 0.5.
- `ray_tracing_options.screen_trace_quality` — march quality 0–1.
- `ray_tracing_options.screen_trace_thickness` — assumed thickness of screen-space surfaces.
- `ray_tracing_options.use_denoise` — temporal + spatial denoiser, default True.

**Surfel-based diffuse GI** — when `ray_tracing_method` is `'PROBE'` and an Irradiance Volume is present, EEVEE bakes surfels (surface samples) inside the volume to approximate light bouncing across surfaces. This is the closest EEVEE gets to Cycles diffuse GI.

**Decision rule for the agent:**
- Need plausible reflections on curved geometry in motion → Screen Trace + Reflection Sphere fallback.
- Need correct reflections off-screen (mirror facing camera, reflected geometry behind camera) → Raytrace.
- Need cheap, static scene reflections → probe-only.

---

## Light Probes

Light probes are placeable objects that store baked indirect lighting. EEVEE Next exposes three types — all are added via `bpy.ops.object.lightprobe_add(type=...)`:

**Types:**
- **Irradiance Volume** (`type='VOLUME'`) — 3D grid of probe points storing diffuse GI. Bake once; objects inside the volume receive the baked indirect light. Use for room interiors, enclosed spaces, anywhere diffuse light needs to bounce.
- **Reflection Plane** (`type='PLANE'`) — single planar reflection. Use for mirrors, floors, water. Far better than screen-space tracing for a known flat reflector.
- **Reflection Sphere** (`type='SPHERE'`) — cube map captured from the probe's origin. Provides fallback reflections when ray tracing misses. **Now dynamic in 4.2+** — sphere probes update if moved (no rebake required for translation).

**Baking** (the Light Cache):
```python
bpy.ops.scene.light_cache_bake()        # bakes all probes in scene
bpy.ops.scene.light_cache_bake_all()    # rebake including world
bpy.ops.scene.light_cache_free()        # discard bake
```

**Quality settings** (`scene.eevee`):
- `gi_diffuse_bounces` — number of diffuse bounces inside the Surfel bake. Default 3.
- `gi_cubemap_resolution` — resolution per cubemap face. Default 1024.
- `gi_visibility_resolution` — resolution of the visibility shell. Default 32.
- `gi_irradiance_pool_size` — atlas size for irradiance volumes, MB.

**When probes are needed vs not:**
- Raytrace mode on for all three effects + a Sphere probe at world origin → covers most scenes with no other probes.
- Indoor scenes / multi-room interiors → need Irradiance Volume for diffuse, otherwise interiors go flat.
- Mirror floor / water plane → Reflection Plane is mandatory for high quality; Screen Trace alone has edge artifacts.

Probe bakes go **stale** when geometry, materials, or lights change. Rebake or the scene drifts.

---

## Volumetrics

EEVEE Next renders volumes (Principled Volume, Volume Scatter, Volume Absorption shaders) using a **froxel grid** — a 3D voxel volume aligned to the camera frustum.

**Properties** (`scene.eevee`):
- `volumetric_tile_size` — `'2'`, `'4'`, `'8'`, `'16'`. Smaller = sharper volume but slower. Default 8.
- `volumetric_samples` — depth slices through the frustum. Default 64. Bump to 128 for thick fog or high-contrast god rays.
- `volumetric_sample_distribution` — slice distribution exponent (logarithmic toward camera). Default 0.8.
- `volumetric_ray_depth` — max bounces for volume scattering. Default 16. Low values flatten dense volumes.
- `use_volumetric_shadows` — volume self-shadowing. Default True. **Expensive** — turn off for cheap atmospheres.
- `volumetric_shadow_samples` — shadow march samples. Default 16.
- `volumetric_start` / `volumetric_end` — frustum range for volume sampling. Tighten this aggressively when fog is bounded.

**Fog / atmosphere recipe:** World shader → Volume Scatter (density 0.01–0.05) + Volume Absorption (low density), Volumetric Samples 128, Volumetric Ray Depth 8, sun light with high energy → god rays appear in the sun beam.

Volume bounding objects (Mesh / Empty with a Principled Volume material) act as bounded fog regions and are far cheaper than world-volume fog.

---

## Motion Blur

EEVEE Next does post-process motion blur driven by motion vectors.

**Properties** (`scene.eevee`):
- `use_motion_blur` — master toggle.
- `motion_blur_shutter` — shutter open duration, in frames. Default 0.5 (180° shutter at 24fps).
- `motion_blur_position` — `'START'`, `'CENTER'`, `'END'`. Default `'CENTER'`.
- `motion_blur_steps` — number of intermediate samples for accurate curve blur. Default 1 (linear).
- `motion_blur_depth_scale` — z-aware blur, controls foreground/background discrimination.

**Alternative: vector pass output** for compositor motion blur. Enable `view_layer.use_pass_vector` and the Vector EXR pass becomes available; use Compositor's Vector Blur node for higher-quality, post-rendered motion blur (essential for animation when you want shutter-tweakable output).

---

## Depth of Field

Camera-level DOF is shared with Cycles — set on the camera, not the engine:

```python
cam = bpy.data.objects['Camera'].data
cam.dof.use_dof = True
cam.dof.aperture_fstop = 2.8           # f-number
cam.dof.focus_distance = 5.0           # meters
cam.dof.focus_object = some_target     # optional: track an object
cam.dof.aperture_blades = 6            # bokeh polygon sides
cam.dof.aperture_rotation = 0.0
cam.dof.aperture_ratio = 1.0           # anamorphic stretch
```

**EEVEE-specific DOF settings** (`scene.eevee`):
- `use_bokeh_jittered` — supersampled jittered bokeh for cleaner highlights. Default False.
- `bokeh_max_size` — clamp on the maximum bokeh circle size in pixels. Default 100; raise for cinematic shallow DOF.
- `bokeh_threshold` — brightness threshold above which jittered bokeh kicks in.
- `bokeh_neighbor_max` — reduces bokeh artifacts on bright neighbors.
- `bokeh_denoise_fac` — denoiser strength for jittered bokeh.

DOF is post-process in EEVEE — it cannot match Cycles' ray-traced DOF for extreme bokeh (out-of-focus geometry leaks; bright highlights bloom imperfectly). For cinematic DOF go to Cycles, or accept the trade.

---

## Bloom

**Bloom is no longer a built-in EEVEE panel.** This is the single most common 4.2+ stumble. The legacy `scene.eevee.use_bloom` property does not exist and `scene.eevee.bloom_*` properties are gone.

**The replacement:** Compositor → Glare node, type = **Bloom** (or **Fog Glow**). See `[[BLENDER_COMPOSITOR]]`.

Minimum compositor stack:
```
Render Layers → Glare (type=BLOOM, size=7, threshold=1.0) → Composite
```

For animation, bake the compositor pass: enable `scene.use_nodes = True`, build the node tree, render. The composited result is what gets written to disk.

Old projects opened in 4.2+ that relied on EEVEE Bloom render flat. Their bloom must be manually rebuilt in the compositor. The migration is not automatic.

---

## Color Management

Color management is identical between EEVEE and Cycles — governed by Scene → Color Management:
- **View Transform** — AgX (default 4.0+), Filmic, Khronos PBR Neutral, Standard, Raw, False Color
- **Look** — None / contrast curves
- **Exposure** — stops
- **Gamma** — final gamma adjustment

`scene.view_settings.view_transform = 'AgX'` is the modern default. AgX handles overexposure gracefully without color hue shift, where Filmic desaturates aggressively.

For HDR linear EXR output, set View Transform to **Raw** at output time and let downstream apps handle the tone map. See `[[BLENDER_MATERIALS]]` for the full color pipeline.

---

## Output Settings

The Output panel (`scene.render`) is shared with Cycles:

```python
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.filepath = '//render/'
scene.render.image_settings.file_format = 'PNG'      # or 'OPEN_EXR', 'OPEN_EXR_MULTILAYER', 'FFMPEG', 'JPEG'
scene.render.image_settings.color_depth = '16'        # 8 or 16 for PNG; 16/32 for EXR
scene.render.image_settings.color_mode = 'RGBA'       # transparent renders need 'RGBA'
scene.render.film_transparent = True                  # transparent background for compositor
```

**Render passes** — EEVEE supports a subset of Cycles passes. Available on `view_layer`:
- Combined, Z, Mist, Normal, Position, Vector, Object Index, Material Index — same as Cycles.
- Cryptomatte Object / Material / Asset — full Cryptomatte support.
- Diffuse Direct, Diffuse Color, Glossy Direct, Glossy Color, Environment, Emission, Shadow, Ambient Occlusion, Volume Direct, Volume Scatter Transmittance.
- **Not available:** Diffuse Indirect, Glossy Indirect (these come from probes/screen-trace and are not split), full Transmission Direct/Indirect (transmission is captured in Combined only), Subsurface separation.

Enable a pass:
```python
view_layer = bpy.context.view_layer
view_layer.use_pass_normal = True
view_layer.use_pass_mist = True
view_layer.use_pass_cryptomatte_object = True
view_layer.pass_cryptomatte_depth = 6
```

For multi-pass output use `'OPEN_EXR_MULTILAYER'` — every enabled pass is written as a layer in one EXR.

---

## Performance on Apple Silicon

EEVEE Next runs on the Metal backend that powers the M1 viewport.

**What's fast on M1:**
- Moderate scenes with screen-trace reflections, no probes, 16–32 samples — 1080p frames in 1–3 seconds on M1 Max.
- Virtual Shadow Maps are well-tuned for unified memory.

**What's slow / unstable:**
- **Surfel GI bake** (Irradiance Volume bake) runs on **CPU**, not GPU. Big volumes can take minutes and pin the main thread.
- **Volumetric ray depth** at 32+ scales rapidly — keep ≤16 on M1 unless required.
- **Raytrace mode** at full resolution is 2–5× slower than Screen Trace. Use half-res or quarter-res `resolution_scale` for production.
- **Shadow Pool Size** above 1024 MB can pressure unified memory in large scenes — EEVEE quietly drops shadows when the pool fills.
- Known 4.2+ regression on Apple Silicon: certain rendered-view configurations spike CPU to 100% and the UI hangs. Save before entering Rendered viewport on M1 with large scenes. See `[[BLENDER_APPLE_SILICON]]`.

**Cancellation:** EEVEE renders on Apple Silicon often do not honor ESC promptly — Cycles cancels cleanly, EEVEE does not. Plan render-block sizes accordingly.

---

## EEVEE-Only Shader Features

A small set of shader nodes is EEVEE-only — they have no Cycles equivalent or behave very differently:

- **Shader to RGB** — converts a shader (including BSDFs) to an RGBA color. Foundation of toon shaders, cel shaders, any non-PBR stylization. Cycles cannot read this node (renders pink-error).
- **Light Path node** — works in both engines, but only the rasterized branches (Is Camera Ray, Is Shadow Ray) are reliable in EEVEE; Is Diffuse Ray / Is Glossy Ray are approximate.
- **Volume Info** — EEVEE-only; Cycles uses Attribute reads instead.
- **OSL (Open Shading Language)** is **Cycles-only** — EEVEE cannot run OSL scripts at all.

When a shader graph mixes EEVEE-only nodes and is then rendered in Cycles, those nodes silently pass through as gray and the look breaks. Tag stylized materials explicitly as EEVEE-only.

See `[[BLENDER_SHADER_NODES]]` for the full node reference.

---

## EEVEE vs Cycles Decision Matrix

| Criterion | EEVEE Next | Cycles |
|-----------|-----------|--------|
| Frame time (1080p, moderate scene, M1 Max) | 1–10 s | 30 s – 5 min |
| Accuracy of indirect lighting | Probe-baked or screen-traced; approximate | Path-traced; physically correct |
| Photoreal materials (SSS, anisotropic, transmission) | Acceptable; transmission limited | Reference-quality |
| Glass dispersion / caustics | None | Yes (with manifold next-event estimation) |
| True volumetric god rays | Approximated; needs probe + sun | Native, accurate |
| Subsurface scattering | Screen-space approximation | Full random-walk SSS |
| Displacement | Vertex shader displacement on subdivided mesh only | True micro-polygon displacement |
| Stylized / toon / flat / cel | Native (Shader-to-RGB) | Manual via light paths; clunky |
| OSL scripts | No | Yes |
| Animation frame budget | Cheap; thousands of frames feasible | Expensive; budget per shot |
| Probe baking required for quality | Often | Never |
| HDRI environment quality | Good | Excellent |
| Hair / particles | Good | Excellent |

**Pick EEVEE when:** stylized; toon; flat colors; quick turnaround; many-frame animation where Cycles cost is prohibitive; M1 with limited RAM for path tracing; lookdev iterations before committing to a Cycles bake.

**Pick Cycles when:** photoreal; glass dispersion / caustics; true volumetric god rays; subsurface accuracy; displacement maps; mixed lighting where probe baking is intractable; cinematic single-frame work.

See `[[BLENDER_RENDER_CYCLES]]` for the path-traced counterpart.

---

## The bpy API Surface — `scene.eevee`

Core properties on `scene.eevee` (`SceneEEVEE`). Set via `bpy.context.scene.eevee.<prop>`:

**Engine selection** (on `scene.render`, not `scene.eevee`):
- `scene.render.engine = 'BLENDER_EEVEE_NEXT'` (4.2 – 4.5) / `'BLENDER_EEVEE'` (5.0+)

**Sampling:**
- `taa_render_samples` — final render samples (int, default 64)
- `taa_samples` — viewport samples (int, default 16)
- `use_taa_reprojection` — temporal reprojection (bool, default True)

**Shadows:**
- `shadow_pool_size` — MB (enum: '16','32','64','128','256','512','1024','2048','4096')
- `shadow_ray_count` — int, default 1
- `shadow_step_count` — int, default 6

**Raytracing:**
- `use_raytracing` — bool, default True
- `ray_tracing_method` — `'SCREEN'` or `'PROBE'`
- `ray_tracing_options.resolution_scale` — `'1'` / `'2'` / `'4'`
- `ray_tracing_options.sample_clamp` — float, default 10.0
- `ray_tracing_options.screen_trace_max_roughness` — float, 0–1, default 0.5
- `ray_tracing_options.screen_trace_quality` — float, 0–1
- `ray_tracing_options.screen_trace_thickness` — float, meters
- `ray_tracing_options.use_denoise` — bool

**Light probes / GI:**
- `gi_diffuse_bounces` — int, default 3
- `gi_cubemap_resolution` — string enum, default '1024'
- `gi_visibility_resolution` — string enum, default '32'
- `gi_irradiance_pool_size` — MB

**Volumetrics:**
- `volumetric_tile_size` — '2'/'4'/'8'/'16', default '8'
- `volumetric_samples` — int, default 64
- `volumetric_sample_distribution` — float, default 0.8
- `volumetric_ray_depth` — int, default 16
- `use_volumetric_shadows` — bool, default True
- `volumetric_shadow_samples` — int, default 16
- `volumetric_start` / `volumetric_end` — float, meters

**Motion blur:**
- `use_motion_blur` — bool
- `motion_blur_shutter` — float, default 0.5
- `motion_blur_position` — `'START'`/`'CENTER'`/`'END'`
- `motion_blur_steps` — int
- `motion_blur_depth_scale` — float

**Depth of field:**
- `use_bokeh_jittered` — bool
- `bokeh_max_size` — float, default 100
- `bokeh_threshold` — float
- `bokeh_neighbor_max` — float
- `bokeh_denoise_fac` — float

**Misc:**
- `clamp_surface_direct` / `clamp_surface_indirect` — firefly clamping on direct/indirect surface light
- `use_overscan` — bool, render beyond frame edges for compositor
- `overscan_size` — pixels

For exhaustive property listing, introspect at runtime:
```python
for prop in bpy.context.scene.eevee.bl_rna.properties:
    if not prop.is_readonly:
        print(prop.identifier, prop.type, prop.default if hasattr(prop, 'default') else '')
```

See `[[BLENDER_PYTHON_API]]` for `bpy` patterns generally.

---

## Light Probe Baking via Script

The light cache is global per scene. Operators:

```python
import bpy

# Bake all visible probes (Irradiance Volume + Reflection Sphere + Reflection Plane)
bpy.ops.scene.light_cache_bake()

# Bake including world / HDRI environment
bpy.ops.scene.light_cache_bake_all()

# Free the bake — invalidates indirect lighting
bpy.ops.scene.light_cache_free()
```

Operator is **blocking** — runs on the calling thread, including CPU surfel computation. For agent-driven workflows on M1, expect 10–120 seconds for a moderate Irradiance Volume bake. There is no built-in "bake on render" auto-flag in 4.2+ — you must explicitly call the bake before rendering, or run it once after every scene-affecting edit.

The bake is stored in the .blend file. Save after baking, or the bake is lost on reload.

---

## Common EEVEE Next Recipes

### Stylized animation preview
```python
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 16
scene.eevee.use_raytracing = True
scene.eevee.ray_tracing_method = 'SCREEN'
scene.eevee.ray_tracing_options.resolution_scale = '2'
scene.view_settings.view_transform = 'AgX'
# No probes baked — screen trace + sphere fallback if World HDRI is present
```

### High-quality stylized final
```python
scene.eevee.taa_render_samples = 64
scene.eevee.use_raytracing = True
scene.eevee.ray_tracing_method = 'SCREEN'           # or 'PROBE' for fully baked
scene.eevee.ray_tracing_options.resolution_scale = '1'
scene.eevee.gi_diffuse_bounces = 3
# Add Irradiance Volume covering scene, then:
bpy.ops.scene.light_cache_bake()
# Bloom in Compositor → Glare node (BLOOM type)
```

### Toon / cel shader
- Shader graph: `Diffuse BSDF → Shader to RGB → Color Ramp (constant interpolation) → Emission` for hard-banded toon.
- Add `Irradiance Volume` to fill ambient lit-side / shadow-side without flat-shading the dark areas.
- `scene.view_settings.view_transform = 'Standard'` (Filmic / AgX flatten the banding).
- `scene.eevee.taa_render_samples = 32`.

### Architectural walkthrough with HDRI
- World HDRI environment.
- One **Reflection Plane** on the main floor (orient z-up, scale to floor).
- One **Irradiance Volume** enclosing the building interior; resolution 8/8/8 minimum.
- `ray_tracing_method = 'SCREEN'`, max roughness 0.5.
- `taa_render_samples = 64`, motion blur off for stills.
- Bake light cache after lights are placed.

### Fast viewport preview
```python
scene.eevee.taa_samples = 8
scene.eevee.use_raytracing = False
scene.eevee.use_volumetric_shadows = False
scene.eevee.volumetric_samples = 32
```

---

## Common Footguns

1. **`scene.render.engine = 'BLENDER_EEVEE'` in 4.2 – 4.5** → `TypeError: enum not found`. Use `'BLENDER_EEVEE_NEXT'`. In 5.0+ it's renamed back; always introspect on install.
2. **Expecting a Bloom panel** → it's gone; build Glare(BLOOM) in the Compositor. Old .blend files render flat in 4.2+.
3. **Expecting OSL** → Cycles-only. EEVEE silently ignores `script` nodes.
4. **Raytrace reflections with `screen_trace_thickness` too low** → reflections cut off at object silhouettes. Bump thickness or fall back to probes.
5. **Light probe bake out of date after edits** — geometry, material, or light changes invalidate the bake. Indirect light freezes at the last bake state. Rebake or lighting goes wrong.
6. **Low `taa_render_samples` + noisy material** → flickering between frames (raytrace + screen trace are temporally accumulated). Either bump samples or disable temporal reprojection.
7. **Shader uses Light Path node** → only Camera Ray / Shadow Ray branches behave; Diffuse/Glossy/Transmission Ray branches are approximate or wrong. Use Cycles for accurate light path branching.
8. **Volume Max Ray Depth too low (e.g. 2)** → dense volumes go flat and unlit; god rays disappear. Default 16 is usually enough; raise to 32 for thick fog.
9. **Soft shadow not soft enough** — `light.shadow_soft_size` is the physical radius of the light, not a blur slider. Increase it. If still hard, raise `scene.eevee.shadow_ray_count` to 4+.
10. **Emission strength clamped by AgX/Filmic** — extreme emission values (>50) get rolled off by the tone map. Lift `scene.eevee.clamp_surface_indirect` and consider a Standard view transform for stylized neon.
11. **Surfel GI bake hung on M1** → it's CPU-bound and single-threaded; very large Irradiance Volumes (e.g. 32³) can take minutes. Reduce volume resolution or split into smaller volumes.
12. **Reflection Plane orientation wrong** → planes only reflect along their +Z. Rotate to match the floor normal exactly; mis-rotation = no reflection.
13. **Transparent background ignored by Glare node** → the Glare node's bloom output additively mixes; ensure alpha is preserved via separate compositor path.
14. **`film_transparent = True` plus screen-trace reflections** → reflections of the empty background show as black smears. Fall back to a Sphere probe baked against a neutral world for clean alpha renders.
15. **EEVEE renders not cancelling on M1** → there is no clean ESC handler for many EEVEE stages on Apple Silicon. Save before rendering. See `[[BLENDER_APPLE_SILICON]]`.

---

## Cross-References

- `[[BLENDER_RENDER_CYCLES]]` — the path-traced counterpart; pick by decision matrix above.
- `[[BLENDER_APPLE_SILICON]]` — M1 / Metal specifics, known regressions, memory pressure.
- `[[BLENDER_COMPOSITOR]]` — where Bloom (Glare node), motion vector blur, and final color grading live.
- `[[BLENDER_SHADER_NODES]]` — shader graph node reference, EEVEE-only nodes.
- `[[BLENDER_MATERIALS]]` — color management, view transforms, PBR pipeline.
- `[[BLENDER_PYTHON_API]]` — `bpy` patterns, context, operators.
- `[[BLENDER_LIBRARY_INDEX]]` — full library map.
