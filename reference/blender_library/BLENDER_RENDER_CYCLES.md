---
title: Cycles — Path-Traced Render Engine Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Cycles render-engine reference — devices (CPU/CUDA/Metal/HIP/OneAPI), sample counts, denoisers (OpenImageDenoise, OptiX-unavailable on M1), light paths, motion blur, DOF, volume rendering, persistent data, performance tuning, the bpy `scene.cycles` surface.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_APPLE_SILICON.md
---

# CYCLES — PATH-TRACED RENDER ENGINE

Cycles is Blender's **physically-based path-tracing** render engine. It traces individual light rays through the scene from the camera, bouncing them off surfaces, accumulating energy at each interaction. Slower per frame than EEVEE Next, but physically correct: true caustics, accurate subsurface, real volumetric scattering, displacement geometry, and unbiased global illumination.

**Use Cycles when** — cinematic stills, glass and refraction, accurate skin/wax/marble subsurface, volumetric godrays through dust or fog, micro-displacement, photoreal product shots, anything where light behavior matters.

**Use EEVEE Next when** — viewport speed, real-time iteration, stylized work, motion graphics, NPR. See `[[BLENDER_RENDER_EEVEE]]`.

"Path-traced" means: each pixel fires *N* sample rays; each ray bounces up to a depth cap; noise decreases as samples increase; a denoiser cleans the residual grain. Doubling samples cuts noise by ~√2.

**Core facts:**
- Cycles is **path-traced** — sample-count driven. More samples = less noise = longer render.
- Supports compute backends: **CPU**, **NVIDIA CUDA**, **NVIDIA OptiX**, **AMD HIP**, **Intel oneAPI**, **Apple Metal**.
- Cycles X (Blender 3.0+) **removed tile-based rendering** — the whole frame is sampled progressively. "Tile Size" in 4.x is a memory-management hint, not a sampling region.
- **OpenImageDenoise (OIDN)** is the default denoiser. GPU-accelerated on Metal/CUDA/HIP since 4.1+; on Apple Silicon it runs on Metal in 4.2+.
- **OptiX denoiser** is NVIDIA-only. Not available on Apple Silicon — selecting it on M-series silently falls back or fails. See `[[BLENDER_APPLE_SILICON]]`.
- **Persistent Data** caches the BVH (bounding volume hierarchy) between frames — major animation speedup, but stale when topology changes.
- The **depsgraph** evaluates all scene dependencies before each render — modifiers, drivers, simulations resolve here.
- **Light paths** cap bounce depth per ray type (diffuse, glossy, transmission, volume, transparent). Hitting the cap turns the ray black.
- `scene.cycles` is the bpy entry point for engine settings; `scene.render` holds engine-agnostic settings (resolution, fps, output path).
- Cycles supports **OSL** (Open Shading Language) but only on CPU on Apple Silicon — Metal does not run OSL.
- **Temporal denoising** (cross-frame OIDN) is a 4.5+ feature via the OIDN command-line tool / Python script — no GUI button yet.

---

## Setting the Engine — Read This First

```python
import bpy
scene = bpy.context.scene
scene.render.engine = 'CYCLES'   # 'CYCLES' | 'BLENDER_EEVEE_NEXT' | 'BLENDER_WORKBENCH'
```

Engine must be set **before** touching `scene.cycles` — otherwise the `cycles` property group may not be registered.

**Device selection** (per-scene):
```python
scene.cycles.device = 'GPU'   # 'CPU' | 'GPU'
```

**GPU compute backend** is configured globally in Preferences, NOT per scene:
```python
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'METAL'  # 'NONE' | 'CUDA' | 'OPTIX' | 'HIP' | 'ONEAPI' | 'METAL'
prefs.refresh_devices()              # forces re-enumeration
for d in prefs.devices:
    d.use = (d.type == 'METAL')      # enable only Metal GPU(s); leave CPU off for pure GPU render
```

The `prefs.devices` list contains every device Blender enumerated — Metal GPU, CPU, sometimes an integrated GPU. **Enable the discrete GPU; leave CPU disabled** unless deliberately doing CPU+GPU hybrid (which adds VRAM transfer overhead and is usually a wash).

**Verify a device is active:**
```python
active = [d for d in prefs.devices if d.use]
assert any(d.type == 'METAL' for d in active), "No Metal GPU enabled — will render on CPU"
```

This check is the #1 install-time verification. A silently-CPU render takes 10–50x longer.

---

## Compute Device Backends

Each backend is a different GPU compute API. Choose **one** via `prefs.compute_device_type`.

### CUDA — NVIDIA
- Mature, fastest baseline on NVIDIA hardware.
- Works on all NVIDIA cards from GTX 6xx upward (with some caveats).
- Lacks raytracing hardware acceleration; use OptiX for that.

### OptiX — NVIDIA RTX
- Hardware-accelerated raytracing on RTX cards.
- 1.5–3x faster than CUDA on the same hardware.
- Exposes the **OptiX denoiser** (faster than OIDN on NVIDIA).
- **Not on Apple Silicon.** Not on AMD. Not on Intel.

### HIP — AMD
- Native AMD GPU path (RX 6000 series and newer recommended).
- Feature parity behind CUDA — some shaders/features lag.

### oneAPI — Intel
- Intel Arc GPUs (A3xx/A5xx/A7xx).
- Hardware raytracing on Arc.

### Metal — Apple Silicon
- **The Apple Silicon path.** M1 / M2 / M3 / M4 (Pro/Max/Ultra all included).
- Requires macOS 13.0+ for full feature support.
- 4.3+ **drops** Metal support for AMD and Intel GPUs on Mac — Apple Silicon only going forward.
- GPU-accelerated raytracing supported on M-series.
- **OIDN runs on Metal** as of 4.1+; full quality at interactive rates in viewport.
- Feature parity status (as of 4.5):
  - Surface shading: full parity
  - Volume rendering: full parity
  - Subsurface scattering: full parity
  - **OSL: not supported on Metal** — script nodes force CPU fallback
  - AMD/Intel Metal: removed in 4.3+
- Cross-ref `[[BLENDER_APPLE_SILICON]]` for memory ceilings, thermal behavior, and benchmark numbers.

---

## Sampling — How Many Rays Per Pixel

The **sample count** is the dominant render-time lever. Cycles fires N rays per pixel; each ray accumulates lighting then returns a color. More rays = less noise.

### Sampling panel (Properties → Render → Sampling)

**Render samples** — final render quality. `scene.cycles.samples` (default `4096`).
**Viewport samples** — preview quality. `scene.cycles.preview_samples` (default `1024`).

In practice, with a good denoiser, **128–512 render samples** is enough for most photoreal work. **32–64 viewport samples** is enough for shading lookdev.

### Adaptive Sampling

Cycles can stop sampling a pixel early once its variance drops below a threshold. Massive speedup on flat areas.

```python
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01    # 0.01 = strict, 0.1 = loose; 0 = auto
scene.cycles.adaptive_min_samples = 0     # 0 = auto-derived from threshold
```

- **0.01** — high quality, slower
- **0.05** — balanced default
- **0.1** — fast preview, may show noise in dark corners
- **0** (auto) — Cycles picks based on render samples

### Time Limit

Hard ceiling per frame:
```python
scene.cycles.time_limit = 0    # seconds; 0 = no limit
```

Use for animation safety — caps worst-case frame time. Cycles renders as many samples as it can within the budget.

### Sample Subset (4.5+)

Distributed rendering — split sample count across machines and merge.
```python
scene.cycles.sample_offset = 0      # start of this machine's range
scene.cycles.samples = 256          # local sample count
```
Renders to OpenEXR with sample metadata; combine with the `cycles_merge` operator.

### Light Sampling Threshold

```python
scene.cycles.light_sampling_threshold = 0.01
```
Lights contributing less than this fraction of a pixel's intensity get probabilistically skipped. Speeds up scenes with many faint lights. Set to `0` to disable.

### Pixel Filter

Anti-aliasing kernel:
```python
scene.cycles.pixel_filter_type = 'BLACKMAN_HARRIS'  # 'BOX' | 'GAUSSIAN' | 'BLACKMAN_HARRIS'
scene.cycles.filter_width = 1.5
```
Blackman-Harris is the default and usually correct. Reduce filter_width for sharper output.

---

## Denoisers

A denoiser converts a noisy low-sample render into a clean image. Without it you'd need 4–10x more samples for the same visual quality.

### OpenImageDenoise (OIDN) — Default

- Intel's open-source AI denoiser.
- CPU baseline; **GPU-accelerated on Metal/CUDA/HIP/oneAPI** in 4.1+.
- Available on every platform Blender runs on.
- Best quality on photoreal work.
- Slightly softer than OptiX on fine detail but no "AI smear" artifacts.

```python
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'  # 'OPENIMAGEDENOISE' | 'OPTIX'
scene.cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'  # 'RGB' | 'RGB_ALBEDO' | 'RGB_ALBEDO_NORMAL'
scene.cycles.denoising_prefilter = 'ACCURATE'  # 'NONE' | 'FAST' | 'ACCURATE'
scene.cycles.denoising_quality = 'HIGH'  # 4.2+: 'FAST' | 'BALANCED' | 'HIGH'
```

### OptiX Denoiser

- NVIDIA-only — uses Tensor cores on RTX.
- Faster than OIDN-on-Metal.
- Available for both viewport and final render.
- **Not available on Apple Silicon** — see `[[BLENDER_APPLE_SILICON]]`.

```python
scene.cycles.denoiser = 'OPTIX'   # ERRORS or silently CPU-falls-back on M-series
```

### None

```python
scene.cycles.use_denoising = False
```
For unbiased reference renders, multi-sample comparisons, or compositor workflows where denoising happens in post.

### Input Passes — quality matters

Denoisers work better when they know surface properties:
- **RGB** — just color. Fastest, lowest quality.
- **RGB+Albedo** — color + base color. Better edges.
- **RGB+Albedo+Normal** — color + base color + surface normal. **Best quality, recommended default.**

Albedo/Normal passes add render cost (~5–10%) but the denoise quality jump is significant.

### Prefilter

Denoiser pre-pass on the albedo/normal inputs before main denoise:
- **None** — skip; only use if albedo/normal are already clean
- **Fast** — quick prefilter; good for animation
- **Accurate** — best for stills

### Quality (4.2+)

OIDN exposes three quality tiers:
- **Fast** — ~1/3 the time, slightly softer
- **Balanced** — ~1/2 the time of High, retains most quality
- **High** — full quality, slowest

Default to **Balanced** for animation, **High** for stills.

### Viewport Denoise (separate setting)

```python
scene.cycles.use_preview_denoising = True
scene.cycles.preview_denoiser = 'OPENIMAGEDENOISE'
scene.cycles.preview_denoising_start_sample = 1
scene.cycles.preview_denoising_input_passes = 'RGB_ALBEDO_NORMAL'
```

### Temporal Denoising (4.5+, animation)

For animation flicker reduction across frames. Not available as a render-time toggle — render the animation with denoising **off** to EXR, then run the OIDN CLI tool with temporal flag, or invoke the Python denoise operator with a sequence. Standalone OIDN `oidnDenoise --ldr` reads previous+current+next frames.

---

## Light Paths — Bounce Depth Control

Each ray bounces until it hits the depth cap, then terminates as black. Higher caps = more accurate light = slower.

```python
lp = scene.cycles
lp.max_bounces = 12            # total bounces, hard cap
lp.diffuse_bounces = 4         # matte / lambertian
lp.glossy_bounces = 4          # mirrors, metal, glossy
lp.transmission_bounces = 12   # glass, refraction — needs HIGH count
lp.volume_bounces = 0          # volumetric scattering — expensive
lp.transparent_max_bounces = 8 # transparent shader (alpha, leaves, hair)
```

**Defaults are conservative for speed.** Adjust per scene:
- **Interior with windows / glass** — transmission ≥ 12
- **Studio product** — diffuse 2, glossy 4, transmission 8 is fine
- **Volumetric godrays** — volume_bounces = 2 minimum
- **Forest / leaves / hair** — transparent_max_bounces ≥ 12 (each leaf alpha-cutout costs a bounce)

### Clamping

Caps maximum brightness per ray — kills fireflies:
```python
scene.cycles.sample_clamp_direct = 0     # 0 = off
scene.cycles.sample_clamp_indirect = 10  # 10 is a common safe value
```
Direct clamp ≠ Indirect clamp. Indirect clamp at 10 is safe; lower values darken bright reflections. Set direct clamp only if direct lights are blowing out.

### Caustics

```python
scene.cycles.caustics_reflective = True
scene.cycles.caustics_refractive = True
scene.cycles.blur_glossy = 1.0   # 4.x: blurs caustic noise; 0 = sharp, 1 = balanced
```

Caustics are notoriously noisy. Disable both for product shots and interiors — except glass pours, swimming pools, or lensed light where caustics are the point.

### Fast GI

Approximates diffuse indirect light with tinted AO. ~20% faster, slight darkening in shadows. Good for viewport, sometimes final.
```python
scene.cycles.use_fast_gi = True
scene.cycles.fast_gi_method = 'REPLACE'  # 'REPLACE' | 'ADD'
scene.cycles.ao_bounces = 1
scene.cycles.ao_bounces_render = 1
```

---

## Volumetrics

For fog, smoke, godrays, atmosphere. Expensive — every volume ray steps through the volume at fixed intervals.

```python
scene.cycles.volume_step_rate = 1.0    # step rate multiplier; smaller = finer = slower
scene.cycles.volume_preview_step_rate = 1.0
scene.cycles.volume_max_steps = 1024   # safety cap; protects against runaway steps
```

(In Blender 4.x these properties live on `scene.cycles`. The legacy `volume_step_size` from 2.8x is gone.)

- **Step Rate 1.0** — default, balanced
- **Step Rate 0.1** — high quality for hero shots, very slow
- **Step Rate 5.0** — fast preview, may band

Banding = step rate too large. Wispy fog detail = step rate too small.

**Volume bounces** (light_paths section above) defaults to 0 — must be raised to 2+ for godrays passing through dust to lit volumes.

See `[[BLENDER_PATTERNS_LIGHTING]]` for godray and atmosphere recipes.

---

## Motion Blur

Camera and object motion blur — engine-level, captured at render time.

```python
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5       # fraction of frame; 0.5 = 180° shutter
scene.render.motion_blur_position = 'CENTER' # 'START' | 'CENTER' | 'END'
scene.cycles.motion_blur_position = 'CENTER' # mirrors the render setting
scene.cycles.rolling_shutter_type = 'NONE'   # 'NONE' | 'TOP'
scene.cycles.rolling_shutter_duration = 0.1
```

- **Shutter 0.5** = 180° shutter angle = cinematic default.
- **Position CENTER** = blur extends ±0.25 frame around frame integer. Matches most physical cameras.
- **Position START** = blur trails the current frame (motion vectors point backward).
- **Geometry motion blur** requires the object to have motion (animated transform or deforming modifier).
- **Camera-only motion blur** still works without object motion.
- **Rolling shutter TOP** simulates CMOS scan-line distortion.

Motion blur multiplies render cost (typically ~1.5–2x). For animation, consider rendering motion vectors and applying blur in the compositor — see render passes below.

---

## Depth of Field

DOF is **camera-level**, not engine-level. Same for both Cycles and EEVEE.

```python
cam = bpy.context.scene.camera
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = 2.0       # meters
cam.data.dof.focus_object = some_empty  # overrides focus_distance if set
cam.data.dof.aperture_fstop = 2.8       # photographic f-stop; lower = shallower
cam.data.dof.aperture_blades = 6        # bokeh shape; 0 = circular
cam.data.dof.aperture_rotation = 0.0
cam.data.dof.aperture_ratio = 1.0       # anamorphic squeeze; 2.0 = oval bokeh
```

- **f/1.4–f/2.8** — shallow, cinematic
- **f/5.6–f/11** — moderate, product
- **f/16+** — deep, architectural
- **focus_object** — point an empty at the subject; animate the empty to rack focus

In Cycles, DOF is **path-traced** (real, accurate, no fakery), so high-quality DOF is a free byproduct of sampling. EEVEE Next uses a screen-space approximation — see `[[BLENDER_RENDER_EEVEE]]`.

See `[[BLENDER_PATTERNS_CINEMATIC]]` for f-stop / focal length combos.

---

## Output Settings

```python
r = scene.render
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = 100      # scales both; useful for half-res previews
r.fps = 24
r.fps_base = 1.0
r.filepath = "//renders/shot_##.exr"  # // = relative to .blend, # = frame pad
r.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
r.image_settings.color_mode = 'RGBA'   # 'BW' | 'RGB' | 'RGBA'
r.image_settings.color_depth = '32'    # '8' | '16' | '32' (32 = float; EXR only)
r.image_settings.exr_codec = 'ZIP'     # 'NONE' | 'RLE' | 'ZIPS' | 'ZIP' | 'PIZ' | 'PXR24' | 'B44' | 'B44A' | 'DWAA' | 'DWAB'
r.image_settings.compression = 15      # PNG only; 0-100
r.image_settings.quality = 90          # JPEG only; 0-100
```

### File formats

- **PNG** — 8/16-bit, lossless, alpha — final delivery, web
- **OpenEXR** — 16/32-bit float, lossless, deep — VFX, compositing
- **OpenEXR Multilayer** — all render passes in one file — compositor workflow
- **TIFF** — 8/16-bit lossless — print
- **JPEG** — 8-bit lossy — proxies, web
- **FFmpeg** — H.264 / ProRes / etc. — direct video output

### EXR sub-options

```python
r.image_settings.exr_codec = 'ZIP'             # ZIP = best lossless ratio
r.image_settings.use_zbuffer = False           # legacy, leave off
# Half-float (16-bit) — half the size of 32-bit, near-lossless for color:
r.image_settings.color_depth = '16'
```

For animation final: **OpenEXR Multilayer, ZIP, Half-Float (16)**, with all useful passes enabled. Compositor reads from the multilayer EXR; reruns are cheap.

### Color management

```python
scene.view_settings.view_transform = 'AgX'         # 'Standard' | 'Filmic' | 'AgX' | 'Khronos PBR Neutral' | 'False Color' | 'Raw'
scene.view_settings.look = 'None'                  # AgX has 'AgX - Base Contrast' / 'Punchy' / etc.
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
scene.display_settings.display_device = 'sRGB'
scene.sequencer_colorspace_settings.name = 'sRGB'
```

**AgX** is the 4.0+ default and the modern choice — better highlight handling than Filmic. **Khronos PBR Neutral** for product renders that must match glTF/USD viewers. **Filmic** for legacy compatibility. **Standard** only when feeding into another color pipeline.

---

## Render Passes

Cycles can output many sub-images per frame for compositing. Enable per view layer:

```python
vl = scene.view_layers["ViewLayer"]
vl.use_pass_combined = True       # final beauty
vl.use_pass_z = True              # depth
vl.use_pass_mist = True
vl.use_pass_normal = True
vl.use_pass_vector = True         # motion vectors (for post motion blur)
vl.use_pass_uv = True
vl.use_pass_object_index = True
vl.use_pass_material_index = True
vl.use_pass_diffuse_direct = True
vl.use_pass_diffuse_indirect = True
vl.use_pass_diffuse_color = True
vl.use_pass_glossy_direct = True
vl.use_pass_glossy_indirect = True
vl.use_pass_glossy_color = True
vl.use_pass_transmission_direct = True
vl.use_pass_transmission_indirect = True
vl.use_pass_transmission_color = True
vl.use_pass_volume_direct = True
vl.use_pass_volume_indirect = True
vl.use_pass_emit = True
vl.use_pass_environment = True
vl.use_pass_shadow = True
vl.use_pass_ambient_occlusion = True

# Cryptomatte (per-object masking)
vl.use_pass_cryptomatte_object = True
vl.use_pass_cryptomatte_material = True
vl.use_pass_cryptomatte_asset = True
vl.pass_cryptomatte_depth = 6
```

### Minimum useful set for compositing
- Combined, Z, Normal, Vector (if animating)
- Cryptomatte Object (for masking individual objects)
- Diffuse Direct + Indirect + Color (light grouping, color regrading)

### Why these matter
- **Z** — defocus, fog, depth-based grades
- **Mist** — pre-calculated atmospheric falloff, 0–1 normalized
- **Vector** — post motion blur in compositor (much cheaper than rendering with `use_motion_blur=True`)
- **Cryptomatte** — clean per-object alpha masks; no scene re-setup
- **Diffuse/Glossy Direct+Indirect+Color** — split light contributions; relight in compositor

See `[[BLENDER_COMPOSITOR]]` for downstream pass usage.

---

## View Layers

A view layer is a sub-render of the scene with its own object visibility, ray visibility, and pass set. Render multiple in a single frame, composite together.

```python
# Create
vl_chars = scene.view_layers.new(name="Characters")
vl_bg = scene.view_layers.new(name="Background")

# Per-layer enable
vl_chars.use = True

# Per-layer collection visibility
for lc in vl_chars.layer_collection.children:
    lc.exclude = (lc.name != "Characters_Collection")

# Per-layer ray visibility (override individual objects)
obj.cycles_visibility.camera = True
obj.cycles_visibility.diffuse = True
obj.cycles_visibility.glossy = True
obj.cycles_visibility.transmission = True
obj.cycles_visibility.scatter = True
obj.cycles_visibility.shadow = True
```

Common pattern: **Characters** layer renders characters with full quality; **Background** layer renders the matte plate at lower samples; **Atmosphere** layer renders only volumetrics. Composite into final beauty.

Each enabled view layer adds full render time per frame.

---

## Performance

### Persistent Data

Keep scene state (BVH, textures, shaders) loaded between frames:
```python
scene.render.use_persistent_data = True
```
- **Speedup**: 20–60% on animations
- **Cost**: more RAM/VRAM usage
- **Breaks**: when topology changes (subdiv levels, new geometry, modifier changes per frame)

**Don't enable** if scene has per-frame geometry (cloth, fluid, particle birth, growing meshes).

### Tile Size (4.0+)

Tiles in modern Cycles are **memory tiles for GPU rendering**, not sampling regions. Cycles renders the full frame progressively; tile size affects how the result is shuttled back from GPU memory.

```python
scene.cycles.use_auto_tile = True
scene.cycles.tile_size = 2048    # only used if use_auto_tile = False
```
Auto tile is correct for almost every case. Manual override only matters with extreme VRAM constraints — drop to 512 if hitting OOM.

### Render Region (Border)

Render only part of the frame — fast iteration on a hero region.
```python
scene.render.use_border = True
scene.render.border_min_x = 0.25
scene.render.border_max_x = 0.75
scene.render.border_min_y = 0.25
scene.render.border_max_y = 0.75
scene.render.use_crop_to_border = True   # output image is the cropped region only
```

### Simplify

Subdivide / particle / AO downsamples for viewport AND/OR render.
```python
scene.render.use_simplify = True
scene.render.simplify_subdivision = 2          # viewport
scene.render.simplify_subdivision_render = 6   # render
scene.render.simplify_child_particles = 0.5
scene.render.simplify_child_particles_render = 1.0
scene.cycles.ao_bounces = 0                    # 0 = off; >0 replaces deep diffuse with AO
scene.cycles.ao_bounces_render = 0
```

### GPU Subdivision

OpenSubdiv on GPU — modifier evaluation on GPU rather than CPU:
```python
bpy.context.preferences.system.use_gpu_subdivision = True
```
Major speedup for heavy subdivision modifiers. Always on by default in 4.x.

---

## Animation Rendering

```python
# Frame range
scene.frame_start = 1
scene.frame_end = 240
scene.frame_step = 1

# Filepath — # placeholders pad with frame number
scene.render.filepath = "//renders/shot01_####.exr"   # → shot01_0001.exr, shot01_0002.exr, …

# Render the whole range
bpy.ops.render.render(animation=True, write_still=False)

# Render a single frame
bpy.ops.render.render(write_still=True)
```

**Per-frame side effects:**
- Depsgraph re-evaluates
- BVH rebuilds (unless persistent data is on)
- Image writes to disk at the resolved filepath
- Denoiser applies (per-frame, NOT cross-frame unless using temporal workflow)
- View layers each render in sequence

**Important**: if `filepath` doesn't contain `#` placeholders for an animation, **every frame overwrites the same file**. Always use `####` (or longer) for animation output.

For headless / background renders:
```bash
blender --background scene.blend --render-output //renders/shot_#### --render-format OPEN_EXR_MULTILAYER --render-anim
```

---

## Baking with Cycles

Cycles is the engine that supports the most bake types. Used for game-asset workflows, lightmaps, and pre-computed textures.

Bake panel: Properties → Render → Bake.

```python
scene.cycles.bake_type = 'COMBINED'  # 'COMBINED' | 'AO' | 'SHADOW' | 'POSITION' | 'NORMAL' | 'UV' | 'ROUGHNESS' | 'EMIT' | 'ENVIRONMENT' | 'DIFFUSE' | 'GLOSSY' | 'TRANSMISSION'
scene.render.bake.use_selected_to_active = False
scene.render.bake.margin = 16
scene.render.bake.margin_type = 'EXTEND'
scene.render.bake.use_clear = True
scene.render.bake.target = 'IMAGE_TEXTURES'  # 'IMAGE_TEXTURES' | 'VERTEX_COLORS'
bpy.ops.object.bake(type=scene.cycles.bake_type)
```

The active **Image Texture** node in the material is the bake target. Must exist and be selected before bake.

**Vertex Color baking** (4.x+) lets you bake AO/lighting/curvature directly to mesh vertex colors — no UVs needed.

---

## OSL — Open Shading Language

Script-based shader programming, more flexible than the node tree.
```python
scene.cycles.shading_system = True   # enable OSL
```
- **CPU only** on Apple Silicon — Metal does not run OSL. Enabling OSL forces CPU device on M-series.
- Useful for procedural patterns that the node graph can't express compactly.
- Don't reach for OSL unless the node solution is genuinely impossible — performance hit is significant on Mac.

---

## Common Cycles Recipes

### Photoreal product render
- View transform **AgX** or **Khronos PBR Neutral**
- **256–512 samples**, adaptive threshold 0.01
- **OIDN, High quality, RGB+Albedo+Normal, Accurate prefilter**
- HDRI environment (Studio/Photo type)
- DOF on, f/4–f/5.6, focus on hero
- Motion blur **off**
- Caustics off (unless glass is the hero)
- Persistent data off (single frame)

### Cinematic environment
- **1024+ samples**, adaptive threshold 0.005
- OIDN High, all input passes
- Total bounces 16; transmission 16–24 (clear glass)
- Volumetrics on, step rate 1.0, volume bounces 2
- Motion blur on, shutter 0.5
- AgX view transform, Punchy look
- Multilayer EXR output

### Fast preview / lookdev
- **32–64 samples**
- Adaptive threshold **0.05**, OIDN **Fast** prefilter, **Balanced** quality
- Render region around hero area
- Simplify on with reduced subdivision

### Animation final
- Persistent Data **on** (assuming static topology)
- OIDN Balanced, per-frame
- 128–256 samples + adaptive 0.01
- **OpenEXR Multilayer, Half-Float, ZIP** output
- Cryptomatte + Vector + Z passes enabled
- Filepath with `####` padding

### Motion vector pass (cheap post-blur)
- `scene.render.use_motion_blur = False`
- `vl.use_pass_vector = True`
- Render to EXR Multilayer
- Apply Vector Blur node in Compositor — 10–20% the cost of true render-time motion blur
- See `[[BLENDER_COMPOSITOR]]`

---

## bpy API Surface — `scene.cycles` and friends

Frequently-set properties for the MCP agent. All paths assume `scene = bpy.context.scene`.

### Engine + device
- `scene.render.engine` → `'CYCLES'`
- `scene.cycles.device` → `'CPU'` | `'GPU'`
- `bpy.context.preferences.addons['cycles'].preferences.compute_device_type` → `'METAL'` (etc.)

### Resolution + framerate
- `scene.render.resolution_x` / `resolution_y` → int
- `scene.render.resolution_percentage` → 1–100
- `scene.render.fps` / `fps_base` → int / float

### Sampling
- `scene.cycles.samples` → int (render)
- `scene.cycles.preview_samples` → int (viewport)
- `scene.cycles.use_adaptive_sampling` → bool
- `scene.cycles.adaptive_threshold` → 0.0–1.0
- `scene.cycles.adaptive_min_samples` → int (0 = auto)
- `scene.cycles.time_limit` → seconds (0 = none)
- `scene.cycles.light_sampling_threshold` → 0.0–1.0

### Denoise
- `scene.cycles.use_denoising` → bool
- `scene.cycles.denoiser` → `'OPENIMAGEDENOISE'` | `'OPTIX'`
- `scene.cycles.denoising_input_passes` → `'RGB'` | `'RGB_ALBEDO'` | `'RGB_ALBEDO_NORMAL'`
- `scene.cycles.denoising_prefilter` → `'NONE'` | `'FAST'` | `'ACCURATE'`
- `scene.cycles.denoising_quality` → `'FAST'` | `'BALANCED'` | `'HIGH'`
- `scene.cycles.use_preview_denoising` → bool

### Light paths
- `scene.cycles.max_bounces` → int
- `scene.cycles.diffuse_bounces` / `glossy_bounces` / `transmission_bounces` / `volume_bounces` → int
- `scene.cycles.transparent_max_bounces` → int
- `scene.cycles.sample_clamp_direct` / `sample_clamp_indirect` → float (0 = off)
- `scene.cycles.caustics_reflective` / `caustics_refractive` → bool
- `scene.cycles.blur_glossy` → 0.0–10.0
- `scene.cycles.use_fast_gi` → bool

### Volume
- `scene.cycles.volume_step_rate` → float
- `scene.cycles.volume_max_steps` → int

### Motion blur
- `scene.render.use_motion_blur` → bool
- `scene.render.motion_blur_shutter` → 0.0–1.0
- `scene.cycles.motion_blur_position` → `'START'` | `'CENTER'` | `'END'`
- `scene.cycles.rolling_shutter_type` → `'NONE'` | `'TOP'`

### Camera DOF
- `camera.data.dof.use_dof` → bool
- `camera.data.dof.focus_distance` → meters
- `camera.data.dof.focus_object` → Object
- `camera.data.dof.aperture_fstop` → float (lower = shallower)
- `camera.data.dof.aperture_blades` → int (0 = circular)

### Output
- `scene.render.filepath` → str (use `//` for relative, `####` for frame padding)
- `scene.render.image_settings.file_format` → `'PNG'` | `'OPEN_EXR_MULTILAYER'` | etc.
- `scene.render.image_settings.color_depth` → `'8'` | `'16'` | `'32'`
- `scene.render.image_settings.exr_codec` → `'ZIP'` | `'PIZ'` | etc.

### Performance
- `scene.render.use_persistent_data` → bool
- `scene.cycles.use_auto_tile` → bool
- `scene.render.use_simplify` → bool

### Color management
- `scene.view_settings.view_transform` → `'AgX'` | `'Filmic'` | `'Khronos PBR Neutral'` | `'Standard'`
- `scene.view_settings.look` → str
- `scene.view_settings.exposure` → float (stops)

Cross-ref `[[BLENDER_PYTHON_API]]` for the broader bpy surface.

---

## Common Footguns

1. **OptiX denoiser selected on Apple Silicon** → silent fall-back to CPU denoise or render fails. Always check `denoiser == 'OPENIMAGEDENOISE'` on M-series. See `[[BLENDER_APPLE_SILICON]]`.

2. **OIDN GPU not enabled in Preferences → System** → OIDN runs on CPU even when scene uses GPU. Massive denoise slowdown. Check Preferences → System → "OpenImageDenoise on GPU" toggle (4.1+).

3. **No GPU device enabled in Preferences → System → Cycles Render Devices** → render falls back to CPU silently. 10–50x slower. Always iterate `prefs.devices` post-set and assert at least one Metal/CUDA/HIP device has `use = True`.

4. **Render comes out black** → check camera pointing direction, scene has at least one light or world background, world output is connected, camera is the scene camera (`scene.camera`).

5. **Denoise enabled but `denoising_input_passes` = `'RGB'`** → quality drop. Albedo+Normal makes a big visible difference; always default to `'RGB_ALBEDO_NORMAL'`.

6. **Persistent Data on while scene topology changes per frame** → stale BVH causes geometry artifacts, wrong shadows, missing objects. Disable for animated cloth/fluid/particle birth.

7. **Filmic / AgX limits emission brightness** → very bright emitters look tonemapped to white. Use exposure compensation rather than emission strength wars; or switch to `Standard` view transform for the comparison.

8. **`transmission_max_bounces` too low** → glass goes black after N internal reflections. Default 12 is the floor for clear glass; 16–24 for thick objects or stacked panes.

9. **Volumetrics with `volume_step_rate` too large** → banding, missed thin smoke detail. Step rate at 1.0 default is OK for most fog; drop to 0.25–0.5 for hero volumetrics.

10. **Output filepath without `#` placeholder for animation** → every frame overwrites the same file; only the last frame survives. Always use `####` or longer for animation.

11. **OSL enabled on Apple Silicon** → forces CPU device, kills GPU acceleration. Confirm `scene.cycles.shading_system == False` for Metal renders unless OSL is genuinely required.

12. **CPU + GPU hybrid enabled but tile size auto** → VRAM transfer dominates; often slower than pure GPU. On M-series, leave CPU off (`d.use = False` for CPU devices in `prefs.devices`).

13. **`use_motion_blur = True` without animation** → still renders, but every object's motion segment is zero so the result is identical to a still — just with motion-blur overhead. Disable for stills.

14. **Adaptive sampling threshold = 0** without specifying `adaptive_min_samples` → Cycles uses internal heuristic; may render longer than expected. Set threshold explicitly (`0.01` baseline).

15. **Render Region (`use_border`) left on between renders** → only the regional crop renders for the next shot too. Always reset `scene.render.use_border = False` after region iteration.

16. **Cryptomatte enabled but `pass_cryptomatte_depth` too low** → overlapping objects collide in the same cryptomatte ID slot. Default 6 covers most cases; raise to 8–10 for crowded scenes.

17. **EXR output with `color_depth = '8'`** → silently invalid; EXR forces float regardless. Use PNG/TIFF/JPEG if 8-bit is the goal.

18. **`frame_step > 1`** in production renders → every Nth frame only. Use 1 unless deliberately rendering keyframes for proxy.

---

## Cross-References

- `[[BLENDER_APPLE_SILICON]]` — Metal backend details, OIDN-on-Metal, OptiX absence, memory ceilings
- `[[BLENDER_RENDER_EEVEE]]` — when to switch engines, EEVEE feature comparison
- `[[BLENDER_COMPOSITOR]]` — using render passes downstream, vector blur, cryptomatte
- `[[BLENDER_PATTERNS_LIGHTING]]` — HDRI / three-point / godray recipes that drive sample-count choices
- `[[BLENDER_PATTERNS_CINEMATIC]]` — focal length / f-stop / shutter combos for cinematic look
- `[[BLENDER_PYTHON_API]]` — broader bpy surface, depsgraph, scene/object access

---

## Sources

- Blender Manual — Cycles: `https://docs.blender.org/manual/en/latest/render/cycles/index.html`
- Blender Manual — Cycles GPU Rendering: `https://docs.blender.org/manual/en/latest/render/cycles/gpu_rendering.html`
- Blender Manual — Light Paths: `https://docs.blender.org/manual/en/latest/render/cycles/render_settings/light_paths.html`
- Blender Manual — Volumes: `https://docs.blender.org/manual/en/4.0/render/cycles/render_settings/volumes.html`
- Blender API — CyclesRenderSettings: `https://docs.blender.org/api/current/bpy.types.CyclesRenderSettings.html`
- Blender 4.1 Release Notes — Cycles: `https://developer.blender.org/docs/release_notes/4.1/cycles/`
- Phoronix — Blender 4.2 LTS with OIDN GPU acceleration: `https://www.phoronix.com/news/Blender-4.2-Released`
- Developer Forum — Metal AMD/Intel removed in 4.3+: `https://devtalk.blender.org/t/cycles-remove-support-of-metal-with-amd-intel-gpus-for-4-3-and-onwards/35098`
