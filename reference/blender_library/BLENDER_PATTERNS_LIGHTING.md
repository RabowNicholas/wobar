---
title: Lighting Patterns — Paste-Ready Lighting Setups
version: 1.0
last_updated: 2026-05-22
status: live
scope: Lighting recipes — 3-point, studio softbox, HDRI-only, cinematic dramatic, single-source key, volumetric god rays, night/moonlight, sunset/golden hour, product shot, character portrait. Engine-agnostic where possible with Cycles vs EEVEE Next notes. Light types, color temperatures, intensity ranges, supporting world / probe / compositor settings.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_RENDER_CYCLES.md, BLENDER_RENDER_EEVEE.md, BLENDER_PATTERNS_CINEMATIC.md
---

# LIGHTING PATTERNS — PASTE-READY LIGHTING SETUPS

Lighting is the dominant factor in render mood and quality. Geometry and materials matter, but a great model in bad light reads worse than a rough model in great light. This file is a recipe library: pick the closest match, diff for your case. Each recipe gives light types, positions, energies, color temperatures, world settings, and engine-specific notes for Cycles vs EEVEE Next.

**Core facts:**
- Blender has 5 light sources: **Point**, **Sun**, **Spot**, **Area**, and **mesh emission** (any mesh with an Emission shader).
- Color temperature is measured in **Kelvin**: 1500K candle / 2700K incandescent / 3200K halogen / 4500K cool fluorescent / 5500K daylight / 6500K overcast / 8000K shade / 10000K deep blue twilight.
- Intensity is in **Watts** for Cycles (physically meaningful), arbitrary units for EEVEE (relative). Same number ≠ same look across engines.
- Sun light is the exception — measured in **W/m²** because it's a parallel-ray emitter at infinity.
- **Light Falloff** in Cycles supports Quadratic (physical default) / Linear / Constant / Custom via the Light Falloff shader node.
- **HDRIs** light the entire scene in one move — environment + ambient + direction in a single texture.
- **Light probes** in EEVEE Next bake indirect diffuse (Irradiance Volume) and reflections (Reflection Plane / Sphere). Without probes, EEVEE has no indirect light.
- **Mesh emission** is a light at the mesh level — use for shaped sources (screens, signs, neon, fire, hot metal). Cycles samples mesh lights via Multiple Importance Sampling; EEVEE Next requires probes for indirect contribution.
- Light data lives on `bpy.data.lights`; the light *object* with transform lives on `bpy.data.objects` with `object.data` pointing at the light.
- Cycles soft shadows come for free from sampling; EEVEE Next uses Virtual Shadow Maps with per-light Soft Shadow size.
- **Filmic** is Blender's default view transform — it tone-maps highlights gracefully but masks over-bright lights in viewport. Always test final renders, not viewport.
- Light **groups** (View Layer → Light Groups) let you render each light to its own AOV for compositor relighting.
- See [[BLENDER_RENDER_CYCLES]] for sampling/bounces, [[BLENDER_RENDER_EEVEE]] for probes/Virtual Shadow Maps, [[BLENDER_PATTERNS_CINEMATIC]] for full-mood pipelines.

---

## The 5 Light Types — Read This First

### Point Light
Radiates from a single point in all directions. Inverse-square falloff by default.
- **Params:** `energy` (W), `color`, `shadow_soft_size` (radius of the virtual sphere → softer shadows).
- **Use:** bare bulbs, small fires, candles, lanterns, anything that emits omnidirectionally from a small source.
- **Note:** `shadow_soft_size` > 0 is required for soft shadows. Default 0.25 m is fine for room-scale scenes; 0.01 m for pinpoint sources.

### Sun Light
Parallel rays from infinity. Position is irrelevant — only **rotation** matters. Scene-scale-independent (doesn't fall off with distance).
- **Params:** `energy` (W/m²), `angle` (apparent disc size in radians/degrees — controls penumbra softness), `color`.
- **Use:** sun, moon, any single-direction light from far away.
- **Note:** `angle` = 0 gives razor-sharp shadows that look CG. Real sun is ~0.526°. For overcast or moon use 1–5°.

### Spot Light
Cone-shaped emission from a point.
- **Params:** `energy`, `spot_size` (cone angle, radians), `spot_blend` (0–1, edge softness), `show_cone` (viewport helper).
- **Use:** stage lights, theatrical spots, lamp shades pointing somewhere specific, headlights, flashlights.
- **Note:** `spot_blend = 0` gives a hard-edged cone. `spot_blend = 1` is fully feathered. Most realistic theatrical spots use 0.15–0.3.

### Area Light
Rectangular, square, disc, or elliptical emitter. The workhorse light type for cinematic work.
- **Params:** `energy`, `size` (X dimension), `size_y` (Y, when shape is Rectangle/Ellipse), `shape` (Rectangle / Square / Disk / Ellipse), `spread` (cone of emission — 180° = hemispherical, smaller = more focused).
- **Use:** softboxes, windows, screens, panels, light boxes, key/fill/rim in 3-point.
- **Note:** Larger `size` = softer shadows but lower apparent intensity per area. Compensate with higher `energy`. `spread` < 180° simulates a snoot or honeycomb grid.

### Mesh Emission
Any mesh with an Emission shader or a Principled BSDF with Emission Strength > 0.
- **Params:** `Emission Strength` (multiplier), `Emission Color` (RGB).
- **Use:** signs, screens, fire, hot metal, light strips, neon, anything where the light source needs visible geometry.
- **Note:** Cycles samples mesh lights via MIS — enable on the material (Object Properties → Sampling, or material's "Multiple Importance" flag in some versions). EEVEE Next contributes mesh emission to probes only after baking.

---

## Color Temperature Reference

| Kelvin | Hex (approx) | Scene context |
|---|---|---|
| 1500K | #ff5e00 | Candle, ember, dim hearth |
| 2000K | #ff7a1a | High-pressure sodium street lamp |
| 2400K | #ff9136 | Match flame, low-wattage tungsten |
| 2700K | #ffa554 | Standard "warm white" bulb, incandescent |
| 3000K | #ffb46b | Halogen indoor |
| 3200K | #ffbd7b | Tungsten studio key (film standard) |
| 4000K | #ffd6a8 | Cool white fluorescent, office overhead |
| 4500K | #ffe1bf | Late afternoon sun, mixed daylight |
| 5500K | #fff4dd | Midday sun, photography daylight standard |
| 6500K | #ffffff | Overcast sky, D65 monitor white |
| 7500K | #e6efff | Open shade, blue hour leading edge |
| 8000K | #d6e4ff | Deep shade, north light |
| 10000K | #b8d0ff | Twilight, cold deep blue |
| 15000K | #a8c4ff | Clear sky zenith |
| 20000K | #9ebbff | Polar twilight, sci-fi cold |

**Warm / cool descriptions → temperature:**
- "Very warm / candlelit" = 1500–2400K
- "Warm / domestic" = 2700–3200K
- "Neutral / sunny" = 5000–5800K
- "Cool / daylight" = 6000–7000K
- "Cold / moonlight / sci-fi" = 7500–10000K
- "Ice / supernatural" = 12000K+

Blender exposes Kelvin via the **Blackbody** shader node. For Python writes to `light.color`, convert Kelvin → RGB manually (see API section).

---

## Recipe Format Convention

Each recipe follows the same structure:
- **Use:** when to reach for it.
- **Lights:** each light's type, position, rotation, energy, color, size.
- **World:** background / HDRI / strength.
- **Render-engine notes:** Cycles-specific and EEVEE-Next-specific tweaks.

Positions assume a subject at world origin, camera roughly on +Y looking at origin, subject ~1.7 m tall (human scale). Scale all distances to your scene.

---

## 3-Point Lighting

The classic portrait / product setup. Safe default for character close-ups, product hero shots, talking-head video stills.

**Use:** character portraits, product shots, default safe lighting, dialog scenes, anything where the subject must read clearly with mild dimensionality.

**Lights:**
- **Key** — Area, Rectangle, size 1.0 × 1.5 m, position (−1.5, −1.5, 2.0), rotated 45° to face subject from front-left and slightly above. Color 6500K (or 3200K for tungsten warm look). Energy 500–1000 W (Cycles).
- **Fill** — Area, Rectangle, size 1.5 × 2.0 m (larger = softer), position (+1.8, −1.2, 1.6), eye-level, facing subject from front-right. Color 5500K. Energy ≈ 25% of key (125–250 W). Larger size and lower energy = soft shadow-filler.
- **Rim** (a.k.a. backlight / hair light) — Area or Spot, size 0.6 m, position (+0.5, +2.0, 2.5), behind subject, slightly above, aimed at back of head/shoulders. Color 7000K (cool to separate from warm key) or 3200K (matching warm). Energy ≈ 50% of key (250–500 W).

**World:** dark gray background (HSV value 0.05) or contextual HDRI at strength 0.2–0.4 to avoid drowning the rim.

**Cycles notes:** Light Paths → Max Bounces → Diffuse 4, Glossy 4. Sampling 256+ for clean soft shadows.

**EEVEE Next notes:** Add an Irradiance Volume covering the subject; bake before final render. Per-light Soft Shadow size 0.5–1.0 for visible softness.

---

## Studio Softbox

Bright, even, near-shadowless. The look of e-commerce product pages and beauty photography.

**Use:** e-commerce product, isolated subject on white/gray, beauty / cosmetic shots, anywhere you want zero drama and total readability.

**Lights:**
- **Top softbox** — Area, Rectangle, size 2.0 × 2.0 m, position (0, 0, 3.0), pointing straight down. 5500K, 800 W.
- **Front-left softbox** — Area, Rectangle, size 1.5 × 1.5 m, position (−2.0, −2.0, 1.5), facing subject. 5500K, 600 W.
- **Front-right softbox** — Area, Rectangle, size 1.5 × 1.5 m, position (+2.0, −2.0, 1.5), facing subject. 5500K, 600 W.
- Optional **bottom fill bounce** — large Area underneath at 10–20% of top, or a white reflective plane.

**World:** pure black (strength 0) for product-on-black, or pure white background plane with its own emission for high-key product.

**Cycles notes:** crank Diffuse bounces to 8 if using a white bounce floor. MIS on world should stay on even for black world (cheap).

**EEVEE Next notes:** Reflection Plane below subject for cleaner specular floor bounces. Probe-bake required.

---

## HDRI-Only Environmental

One texture, whole scene lit. Fastest path to realistic outdoor lighting and the standard starting point for product viz.

**Use:** realistic outdoor / contextual lighting, fast turnaround, lookdev passes, asset previews, anything where the environment plausibly *is* the light source.

**Lights:**
- None, OR one supporting **Sun** matched to the HDRI's sun direction. See [[BLENDER_ASSET_IO]] for HDRI sourcing.

**World tree (Shader Editor → World):**
- **Texture Coordinate** (Generated) → **Mapping** (rotation Z = sun azimuth) → **Environment Texture** (HDRI file, **Linear / Non-Color** data) → **Background** (Strength 1.0–2.0) → **World Output**.

**Adding a Sun for sharper shadows:**
- Match Sun rotation to the HDRI's visible sun direction.
- Sun energy ~3–5 W/m² for noon, 0.5–1.5 for golden hour.
- Sun `angle` = 0.526° for realistic sun disc.
- Drop HDRI Background strength to 0.5–0.8 to compensate (otherwise scene gets double-bright on highlights).

**Cycles notes:**
- Enable World → Sampling → Multiple Importance Sample. Critical for HDRIs with concentrated bright spots (sun, windows).
- Map Resolution 1024 for sampling acceleration on large HDRIs.

**EEVEE Next notes:**
- World renders directly without baking, but indirect bounce off geometry requires Irradiance Volume probes.
- World → Surface uses real-time path tracing in 4.2+ if Raytracing is enabled, otherwise probe-based.

---

## Cinematic Dramatic

Single hard key, deep shadows, strong contrast. Noir, thriller, "something is about to happen."

**Use:** noir, thriller, horror, "heavy" mood, single-subject drama, interrogation scenes, ominous reveals.

**Lights:**
- **Key** — Spot or small Area (size 0.3 m), position (−2.5, −1.0, 2.2), aimed at subject's face from camera-back-side. Color 3200K (warm tungsten) or 5500K (clinical). Energy 1500–3000 W (Cycles) — hot, deliberate.
- **Fill** — either none, or extremely weak (5–10% of key) from below, color complementary (cool blue 8000K if key is warm).
- **Rim** — optional Spot from behind at 50% of key, very tight cone (spot_size 30°, spot_blend 0.1), color 7000K cool — separates subject from black background.

**World:** background strength 0. Pure black. No HDRI.

**Cycles notes:** Max Bounces → Diffuse 2 (you don't want bounced fill brightening the shadows). Volumetric scatter optional for atmosphere.

**EEVEE Next notes:** Virtual Shadow Maps with low Soft Shadow size (0.05–0.1) for hard edges. Disable Irradiance Volume contribution or it'll fill the shadows.

See [[BLENDER_PATTERNS_CINEMATIC]] for the full noir mood pipeline including compositor grade.

---

## Single-Source Key (Chiaroscuro)

One light. No fill. The Caravaggio look. Maximum tonal range, painterly.

**Use:** ceremonial, contemplative, painterly, religious / mythic, single-figure portraiture in the Rembrandt tradition.

**Lights:**
- **Key only** — Area, Square, size 0.8 m, position (−1.5, −1.8, 2.5), 45° down + 45° in from subject. Color 3200K. Energy 800 W.
- **No fill. No rim. No bounce cards.**

**World:** strength 0, pure black. No HDRI.

**Cycles notes:** Diffuse bounces 1–2 — you *want* shadow side to fall to near-black. Sampling high (512+) because the lit-to-shadow ratio is extreme and noise shows up in midtones.

**EEVEE Next notes:** This recipe is harder in EEVEE because probes will fill shadows. Set Irradiance Volume influence to 0 in regions you want crushed, or disable probes entirely.

---

## Volumetric God Rays

Light beams visible through atmosphere. Cathedral light, forest sun shafts, smoke-and-mirrors theatrical.

**Use:** cathedral light beams, smoke / dust ambience, forest sun shafts, club lasers, anywhere atmospheric scattering should be visible.

**Lights:**
- **Source** — Spot light or Sun, positioned so its cone passes through the volumetric region. Spot: spot_size 25°, spot_blend 0.2, energy 2000 W, color 4500K. Sun: energy 5 W/m², angle 1°.

**Volumetric region (Cycles):**
- Add a cube around the lit area (or the whole scene).
- Material: **Principled Volume** shader. Density 0.01–0.1 (start at 0.05). Anisotropy 0.3 (forward-scattering = sun-through-dust look).
- Higher density = thicker fog. Beyond 0.3 you'll lose subject visibility.

**Volumetric region (EEVEE Next):**
- Render Properties → **Volumetrics** section, enable.
- World shader: add **Volume Scatter** with Density 0.02, Anisotropy 0.3 → World Output Volume socket.
- Render Properties → Volumetrics → **Volumetric Shadows** enabled (this is what creates the visible beams).
- Tile Size 4 px for quality, Samples 128.

**World:** dark background (strength 0.1) so the beams pop. HDRI optional but reduce strength to 0.3.

**Cycles notes:** Sampling Volume → bounces 1–2 minimum. Light Paths → Max Bounces → Volume 2+. Render time will rise substantially — use adaptive sampling.

**EEVEE Next notes:** Volumetric Shadows are mandatory or you'll get fog without beams. Resolution slider trades quality for speed.

---

## Night / Moonlight

Cool, low, with warm practicals. The default nocturnal exterior recipe.

**Use:** nocturnal scenes, exteriors at night, after-dark interiors with windows, moonlit landscapes.

**Lights:**
- **Moon** — Sun, rotation pointing down-right at 30° from vertical, energy 0.05–0.2 W/m², color 7500K, angle 1.5° (moon has larger apparent disc softness due to atmospheric scattering).
- **Practicals (candles, lanterns)** — Point Lights at each visible source, color 2700K, energy 20–80 W, shadow_soft_size 0.05 m.
- **Window spill** (if interior) — Area outside windows facing in, size matching window, color 7500K, energy 30–100 W, simulating moonlight.

**World:** HDRI of night sky / starfield at strength 0.05–0.15, OR procedural deep blue background. Color #0a1428 at strength 0.2 works as a placeholder.

**Cycles notes:** Sampling 1024+ — low-light scenes are noisy. Enable denoising (Open Image Denoise) aggressively.

**EEVEE Next notes:** Bloom helps practicals glow correctly. Exposure can be raised in the camera (Render → Color Management → Exposure +1 to +2) and lights dropped proportionally for cleaner viewport feedback.

---

## Sunset / Golden Hour

Warm, low, long shadows. Romantic, contemplative, "magic hour."

**Use:** warm romantic, contemplative outdoor, hero product shots with mood, anything where the light should feel earned and finite.

**Lights:**
- **Sun** — rotation at 5–15° above horizon (very low), color 2700–3200K warm, energy 1.5–3 W/m², angle 2° (large penumbra for soft sunset edges).
- Optional **fill from sky** — large Area above scene, size 5×5 m, color 7500K cool blue (sky is the cool counterpart), energy 50–100 W.

**World:** HDRI of evening sky with strong orange/pink gradient at strength 1.0. Procedural fallback: Sky Texture node (Nishita model, Sun Elevation 8°, Air Density 1, Dust Density 5, Ozone 1).

**Cycles notes:** Sky Texture (Nishita) is physically based and shifts color correctly with Sun Elevation — match your Sun light rotation to the Nishita Sun Elevation for consistency.

**EEVEE Next notes:** Glare/Bloom in compositor (or Render Properties → Bloom in older 4.2) sells the warm halo. Volumetric scatter at very low density (0.005) adds golden-hour haze.

---

## Product Shot

Clean, isolated, hero-object render. Catalog and packshot lighting.

**Use:** clean isolated render of a single object, hero packshots, marketing images, transparent-background renders.

**Lights:**
- **Top key** — Area, Rectangle, size 2.0 × 1.5 m, position (0, −0.5, 2.5), pointing down at 70°. 5500K, 800 W.
- **Rim from behind** — Area, size 1.2 × 1.2 m, position (0, 1.5, 1.5), aimed at subject back. 6500K, 400 W.
- **Fill from below** — Area, size 1.5 × 1.5 m, position (0, −0.5, 0.3), pointing up. 5500K, 100–150 W (just enough to lift shadow side).
- Alternatively, **reflective floor plane** with white diffuse material below subject — cheaper, more controlled bounce.

**World:** subtle gradient sky (light gray top, slightly warmer bottom) at strength 0.3, OR pure white at strength 1.0 for high-key, OR pure black for low-key.

**Cycles notes:** Caustics may be relevant for glass / metallic products — enable per-shader **Cast Shadows / Caustics** if rendering refractions. Light Paths → Caustics → Reflective + Refractive on.

**EEVEE Next notes:** Reflection Plane below subject. Screen Space Reflections on. Bloom for highlight tails on metallic.

See [[BLENDER_MATERIALS]] for product-material setups that pair with this lighting.

---

## Character Portrait

3-point + practical catchlight. Realistic human / character close-up.

**Use:** human or character close-up, portrait headshots, hero shots of a digital double, anything where the eyes must read alive.

**Lights:**
- **Key, Fill, Rim** — as in 3-Point above, scaled to character. Key 800 W, Fill 200 W, Rim 400 W.
- **Catchlight** — small Area, size 0.1 m, position just outside frame in front of character at eye height (~0.5 m from face), energy 5–15 W, color 6500K. The point is the reflection in the eyes, not scene illumination.
- **Optional kicker** — additional Spot from low-side, very tight, 20% of key, for jawline definition.

**World:** HDRI of contextual environment (interior, studio, outdoor) at strength 0.3–0.5 for soft ambience and reflections in the eyes.

**Cycles notes:** Subsurface scattering on skin needs Diffuse bounces 4+. Hair shader needs Glossy bounces 8+ if rendering with backlit hair. Sample 512+ for clean skin.

**EEVEE Next notes:** Subsurface translucency in EEVEE Next is improved over old EEVEE but still approximate — preview with SSS Samples 16+. Bake Irradiance Volume around the character.

---

## Architectural Interior

Sun through windows + practicals. The standard interior recipe.

**Use:** room rendering, real-estate viz, interior design previews, architectural walkthroughs.

**Lights:**
- **Sun** — pointing through windows at the desired angle (afternoon = 35° above horizon). Energy 3–5 W/m², color 5000K, angle 0.526°.
- **Sky fill via HDRI** — clear/overcast sky HDRI, strength 0.5–1.0, rotated to put sun outside windows in the texture (matching the Sun light direction).
- **Practicals** — Point or Area at each lamp, table light, ceiling fixture. 2700K warm, 30–80 W each.
- **Ceiling spill** — Area inside ceiling cavities for indirect ambience if practicals are weak. 3000K, 50 W.

**Light Portal technique (Cycles):**
- Place an **Area light** at each window opening, sized to fit the window aperture.
- In Light → Cycles Settings, enable **Portal**. This tells Cycles "the bright stuff is on the *other* side of this plane — please sample through here." Massively improves sample efficiency for interiors lit by exterior sun/sky.
- Portal lights themselves don't add energy — they're sampling guides only.

**World:** HDRI matching the sky / sun direction at strength 1.0.

**Cycles notes:** Max Bounces → Diffuse 6, Glossy 6, Transmission 8. Caustics off (slow + noisy in interiors). Use **Light Tree** (4.2+) — it dramatically improves many-light sampling.

**EEVEE Next notes:** Irradiance Volume covering all interior space, with a tighter cell distribution near surfaces. Multiple Reflection Probes per room. Light Portal does not apply (EEVEE concept doesn't exist).

---

## Sci-Fi Rim with Colored Lights

Three colored rims + emissive in-scene panels. Cyber, neon, futuristic.

**Use:** futuristic, cyber, neon, sci-fi, music-video style, anywhere realism takes a back seat to graphic color.

**Lights:**
- **Rim 1 (teal)** — Area, size 1.0 × 1.5 m, position (+2.5, +1.0, 1.5), color teal (hex #00d4d4 or 12000K + manual desaturation), energy 600 W.
- **Rim 2 (magenta)** — Area, size 1.0 × 1.5 m, position (−2.5, +1.0, 1.5), color magenta (hex #ff00aa), energy 600 W.
- **Rim 3 (white fill)** — Area, size 0.8 × 0.8 m, position (0, −2.0, 1.2), color 6500K, energy 200 W (low — just enough to reveal form).
- **Mesh emission strips** — geometry strips, panels, neon signs with Emission Strength 5–20, color matching the rim palette.

**World:** strength 0 black, OR very dark blue HDRI of a city night at strength 0.1.

**Cycles notes:** Bloom-equivalent via Compositor → Glare (Fog Glow type) is essential — the look depends on highlight bleed. Sampling 256+, emissives are noisy.

**EEVEE Next notes:** Bloom (Render Properties → Bloom in 4.2; Compositor Glare node in 4.3+). Reflection Probes near reflective surfaces are required or you'll lose the color bleed.

---

## Light Probes for EEVEE Next

EEVEE Next without probes has no indirect light. Direct contribution only — looks flat, plasticky, "video game from 2008." Probes fix this.

**Probe types:**
- **Irradiance Volume** — bakes diffuse indirect lighting in a 3D grid. Place around any area where indirect bounce matters (interiors, character zones, anything not lit purely by HDRI).
- **Reflection Plane** — bakes a planar reflection. Use on floors, mirrors, flat reflective surfaces.
- **Reflection Sphere** — captures a spherical environment map at its location. Use for scattered reflective points (chrome objects, eyes).

**Adding an Irradiance Volume:**
- Add → Light Probe → Irradiance Volume.
- Scale to enclose the region you want lit indirectly.
- Object Data → Resolution X/Y/Z controls grid density. 8×8×4 is fine for a room; raise for higher-frequency lighting.
- Object Data → Capture → **Bake** (or use the Render Properties → Indirect Lighting bake button for all probes at once).

**Baking from Python:**
```python
bpy.ops.scene.light_cache_bake()  # bakes all light probes in scene
```

**When EEVEE results look flat → it's almost certainly missing probes.** First fix: drop an Irradiance Volume around your subject and bake.

**Validity:** probes go stale when geometry, materials, or lights change. Re-bake. The Indirect Lighting panel shows the cache state.

See [[BLENDER_RENDER_EEVEE]] for full EEVEE pipeline.

---

## The bpy API for Lighting

Paste-ready snippets. All assume Blender 4.2+.

### Create a Sun light

```python
import bpy
from math import radians

light_data = bpy.data.lights.new(name="Sun_Key", type='SUN')
light_data.energy = 3.0          # W/m²
light_data.color = (1.0, 0.95, 0.85)
light_data.angle = radians(0.526)  # realistic sun disc

light_obj = bpy.data.objects.new(name="Sun_Key", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (radians(50), 0, radians(30))
```

### Create an Area light (Rectangle, with Kelvin → RGB)

```python
import bpy
from math import radians

def kelvin_to_rgb(k):
    # Tanner Helland approximation, clamped 1000–40000 K
    k = max(1000.0, min(40000.0, k)) / 100.0
    if k <= 66:
        r = 255.0
        g = 99.4708025861 * (k ** 0.0 if k == 0 else __import__('math').log(k)) - 161.1195681661
    else:
        r = 329.698727446 * ((k - 60) ** -0.1332047592)
        g = 288.1221695283 * ((k - 60) ** -0.0755148492)
    if k >= 66:
        b = 255.0
    elif k <= 19:
        b = 0.0
    else:
        import math
        b = 138.5177312231 * math.log(k - 10) - 305.0447927307
    return (max(0, min(255, r)) / 255.0,
            max(0, min(255, g)) / 255.0,
            max(0, min(255, b)) / 255.0)

light_data = bpy.data.lights.new(name="Area_Key", type='AREA')
light_data.shape = 'RECTANGLE'
light_data.size = 1.0      # X
light_data.size_y = 1.5    # Y
light_data.energy = 800.0
light_data.color = kelvin_to_rgb(6500)
light_data.spread = radians(180)

light_obj = bpy.data.objects.new(name="Area_Key", object_data=light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-1.5, -1.5, 2.0)
light_obj.rotation_euler = (radians(60), 0, radians(-45))
```

### Add an Emission material to a mesh

```python
import bpy

mat = bpy.data.materials.new(name="Emission_Sign")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (1.0, 0.3, 0.8, 1.0)
emission.inputs['Strength'].default_value = 10.0

output = nodes.new('ShaderNodeOutputMaterial')
links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Apply to active object
obj = bpy.context.active_object
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

### Set the World to an HDRI

```python
import bpy

world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
env_tex = nodes.new('ShaderNodeTexEnvironment')
env_tex.image = bpy.data.images.load("/path/to/hdri.hdr")
background = nodes.new('ShaderNodeBackground')
background.inputs['Strength'].default_value = 1.0
output = nodes.new('ShaderNodeOutputWorld')

links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
links.new(env_tex.outputs['Color'], background.inputs['Color'])
links.new(background.outputs['Background'], output.inputs['Surface'])

# Rotate HDRI to put sun where you want
from math import radians
mapping.inputs['Rotation'].default_value[2] = radians(45)
```

### Add a Light Probe (Irradiance Volume) and bake

```python
import bpy

bpy.ops.object.lightprobe_add(type='VOLUME', location=(0, 0, 1.0))
probe = bpy.context.active_object
probe.scale = (5, 5, 3)
probe.data.grid_resolution_x = 8
probe.data.grid_resolution_y = 8
probe.data.grid_resolution_z = 4

# Bake all probes (EEVEE Next)
bpy.ops.scene.light_cache_bake()
```

### Set Cycles light bounces

```python
import bpy

cycles = bpy.context.scene.cycles
cycles.max_bounces = 12
cycles.diffuse_bounces = 4
cycles.glossy_bounces = 4
cycles.transmission_bounces = 8
cycles.volume_bounces = 2
cycles.transparent_max_bounces = 8
```

---

## Render-Engine Differences for Lighting

| Aspect | Cycles | EEVEE Next |
|---|---|---|
| **Indirect / Bounces** | Path-traced, respects Light Paths settings | Probes (Irradiance Volume) OR Raytrace mode (4.2+) for screen-space approximation |
| **Soft Shadows** | Sample-based, free, accurate | Virtual Shadow Maps + per-light Soft Shadow size |
| **Caustics** | Yes (with per-shader Caustics flag, MNEE) | No — fake in compositor or with bright emissive patches |
| **Volumetrics** | Principled Volume material on a mesh, scene-accurate | World Volume scatter + Render Properties Volumetrics settings |
| **Sun disc / angular shadows** | `angle` param creates physical penumbra | Soft Shadow size approximates |
| **Light Portals** | Yes (Area light with Portal flag) — interior sampling boost | No equivalent |
| **HDRI accuracy** | World MIS samples bright spots correctly | Probe-based unless Raytrace mode |
| **Mesh emission** | MIS samples accurately | Contributes via probes after baking |
| **Speed** | Slow but physically correct | Fast but approximation-heavy |

**Rule of thumb:** if the lighting *concept* depends on physical accuracy (caustics, volumetrics, sun angle, fine soft shadows), use Cycles. If you need real-time iteration and can pre-bake probes, EEVEE Next.

---

## Common Footguns

- **Energy too high → Filmic clamps the look** but viewport hides it. The image looks fine but loses highlight detail. Solution: render a test frame, check the histogram, not the viewport.
- **HDRI loaded as sRGB → washed out, wrong exposure.** HDRIs must be **Linear** / **Non-Color**. Set Image Texture node's Color Space → Non-Color.
- **World strength 0 + no lights → black render.** Obvious, but easy to do when iterating on world setup.
- **Light inside a closed mesh → no light leaks out** (Cycles will trace into the mesh and bounce internally; you'll see nothing outside). Either move the light outside, or put the mesh on a different ray visibility (Object Properties → Visibility → Ray Visibility → Camera off, Diffuse off, etc.).
- **Cycles with bounces = 0 → only direct lighting.** Shadows are pitch black, no ambient. Set Diffuse bounces ≥ 2.
- **EEVEE Next probe out of date → flat result.** Re-bake after any geometry/material/light change. Cache state is shown in Render Properties → Indirect Lighting.
- **Area light `spread = 180°` → effectively a Point light** in directional behavior. Use 90° for a real softbox cone, smaller for snoots.
- **Sun light `angle = 0` → razor-sharp CG shadows.** Real sun is 0.526°. Use that, or larger for overcast.
- **Mesh emission with no MIS → fireflies (noise specks)** in Cycles. Enable Multiple Importance Sample on the material's emission contribution.
- **Mixing Cycles W and EEVEE arbitrary units → look mismatch.** Lights numbers don't translate 1:1. Eyeball EEVEE intensities separately or use a relative scale.
- **HDRI strength too high + Sun → double exposure.** When adding a supporting Sun to an HDRI, drop the HDRI strength to 0.5–0.8.
- **Filmic + very saturated colored lights → desaturated muddy result.** Filmic's tone-map desaturates extremes. For neon / sci-fi looks, consider Standard view transform or AgX (default in 4.2+) for richer color retention.
- **Light Portal placed wrong way → makes interior darker, not brighter.** The Portal flag's normal must face *into* the room (toward the camera). Check normal direction.
- **Volumetric density too high → opaque fog, lose the subject.** Stay under 0.1 for visible god rays; for thick atmosphere drop the world strength and raise volume scatter together.
- **No catchlight in eyes on character close-up → eyes look dead.** Always add a small Area light just outside frame at eye height — the catchlight reflection sells the shot more than total scene illumination.
- **Render Engine switched (Cycles ↔ EEVEE) but light values not adjusted** → either washed out or pitch black. Maintain two preset stacks if you render in both.

---

## Cross-References

- Render-engine specifics → [[BLENDER_RENDER_CYCLES]], [[BLENDER_RENDER_EEVEE]]
- Materials that pair with lighting (skin SSS, metal, glass) → [[BLENDER_MATERIALS]]
- Full mood pipelines including grade and compositor → [[BLENDER_PATTERNS_CINEMATIC]]
- HDRI sourcing and import → [[BLENDER_ASSET_IO]]
- Library map → [[BLENDER_LIBRARY_INDEX]]
