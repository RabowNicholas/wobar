---
title: Instancing Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Rendering many copies of geometry efficiently — POP instancing, Replicator COMP, Geometry COMP instance tab.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_POP.md, TD_OPERATORS_COMP.md, TD_EFFICIENT_NETWORKS.md
---

# INSTANCING PATTERNS

Instancing is how you render **many copies** of geometry without paying per-copy cost. The GPU draws N instances of a template mesh in one draw call, each with different transforms/colors/attributes.

**Default choice at scale: POPs → Geometry COMP instance.**
**Fallback for <50 copies with per-instance logic: Replicator COMP.**

---

## The Mental Model

1. **Template** — one piece of geometry (a cube, sphere, quad, custom mesh).
2. **Per-instance data** — arrays of positions, rotations, scales, colors, one value per instance.
3. **Renderer** — Geometry COMP with Instance tab configured, receiving per-instance data from a CHOP or POP.

---

## Pattern 1 — POP to Geometry COMP Instance

Canonical modern pattern. Works for large N (thousands to hundreds of thousands on M1).

```
Sphere POP (point count = 10000) 
  ──► Attribute POP (set per-point position, color, scale)
  ──► Null POP
      │
      ▼
Geometry COMP:
  - SOP Input: Box SOP (small template)
  - Instance tab:
      Instance OP = null POP
      Translate = P (auto from POP position)
      Rotate = (custom rotation attribute if needed)
      Scale = pscale attribute
      Color = Cd attribute
  - Material: Constant MAT (color driven by Cd)
```

### Why this works
- POP is GPU-native. 10k points live on the GPU.
- Geometry COMP's instancer reads the POP buffer directly — no CPU round-trip.
- Material reads per-instance Cd (color) via attribute.

---

## Pattern 2 — CHOP-driven Instancing

Classic pre-POP pattern, still useful for smaller counts or simple data:

```
Pattern CHOP (N samples, generates tx/ty/tz) ──► Null CHOP
Geometry COMP:
  - SOP Input: template
  - Instance tab:
      Instance OP = null CHOP
      Translate = null CHOP channels tx, ty, tz
      (same for rotate, scale)
```

- Simple and visible; CHOP chains are easy to reason about.
- Breaks down above ~5k instances due to CPU cook cost of large CHOPs.

---

## Pattern 3 — Replicator COMP (Per-Instance Logic)

When each instance needs **different internal logic** (e.g., one plays audio, another fires a pulse), not just different transforms:

```
Template COMP "card" (custom params: Title, Color, AudioFile)
Replicator COMP:
  - Template COMP = card
  - Template DAT = Table DAT with rows of per-card data
```
- Replicator creates N clones, each reading its DAT row for params.

### Where Replicator fails
- Large N (>100): each clone is a full COMP. Cook cost explodes.
- Per-frame animation of N instances: every clone re-cooks.

### Use when
- N is small (< 50).
- Instances have complex internal behavior.
- Cards / UI widgets / named entities.

---

## Pattern 4 — Data-Driven Instancing from a Table DAT

```
Table DAT (N rows: x, y, z, r, g, b, scale)
  ──► DAT to CHOP
  ──► Null CHOP ──► Geometry COMP Instance
```
- External data (CSV, API response, user input) driving positions.
- Good for data viz, location markers, music track visualizations.

---

## Pattern 5 — Audio-Reactive Instancing

Per-instance animation driven by audio:

```
Sphere POP (5000 points)
  ──► Attribute From CHOP POP (reads null_audio_sub across samples → per-point pscale)
  ──► Noise POP (on P, amplitude driven by null_audio_mid)
  ──► Geometry COMP instance
```
- Every point's scale/position responds to audio.
- Bass pushes out; mid jitters; high adds sparkle.

---

## Pattern 6 — Image-Driven Particles

Particles whose positions / colors come from an image:

```
Trace POP (input image, threshold) ──► 10k points in image silhouette
  ──► Attribute From Texture POP (sample image color → Cd)
  ──► Noise POP (light jitter)
  ──► Geometry COMP instance (Point Sprite MAT)
```
- A logo explodes into a point cloud of colored dust.

---

## Pattern 7 — Force-Simulated Particle Instancing

```
Point Generator POP (emit N per second with velocities)
  ──► Simulate POP 
        ├── Gravity POP
        ├── Wind POP
        └── Drag POP
  ──► Lifespan POP
  ──► Geometry COMP instance (small glowing quad)
```
- Actual particle system. See `TD_PATTERNS_PARTICLES.md` for more.

---

## Pattern 8 — Mesh Instancing on Surface Points

Instance small geometry on the surface of a larger mesh:

```
Host SOP (Sphere at large scale) ──► Sprinkle POP (scatter 5000 points over surface)
  ──► Attribute POP (align normals to surface)
  ──► Geometry COMP with Instance template = small grass blade SOP
```
- Grass on a terrain, scales on a creature, fur, stars on a sphere.

---

## Pattern 9 — Text Instancing

Text POP (2025) creates points per-character or per-path sample:

```
Text POP ("WOBAR", sample path) ──► 500 points along letter outlines
  ──► Attribute POP (add offset, jitter)
  ──► Geometry COMP instance (small sphere)
```
- Text made of particles. See `TD_PATTERNS_TEXT.md`.

---

## Pattern N — Geometry Self-Replication via Transform-and-Merge Branches (low-N "manual instancing")

For small numbers of differently-transformed copies (3–8), explicit transform-merge branches are often cleaner than full instancing — each branch can have its own static position AND animated rotation independently.

POPX `sweep_example.toe` canonical: ONE sweep output forked into 3 transform-pair branches, each pair = static position + animated rotation, then merged.

```
sweep_or_geo_output
  ├──▶ transform1 (tx=2/3, ty=2/3, ry=120°, rz=-30°)   ── static position
  │      └──▶ transform4 (ry.expr = 'absTime.seconds*15')   ── animated rotation
  │             ↓
  │           mergePOP.in0
  │
  ├──▶ transform2 (ty=1/30 — tiny offset)
  │      └──▶ transform3 (ry.expr = 'absTime.seconds*15')
  │             ↓
  │           mergePOP.in1
  │
  └──▶ transform5 (tx=2/3, ty=-2/3, ry=-90°, rz=10°)
         └──▶ transform6 (ry.expr = 'absTime.seconds*15')
                ↓
              mergePOP.in2
              ↓
         downstream rendering
```

**Why two transforms per branch instead of one:**
- The FIRST transform sets the STATIC position + orientation offset (where this copy lives in the composition)
- The SECOND transform applies the ANIMATED rotation (`absTime.seconds * speed` expression)
- This separation lets you tune layout once and never touch it again while the animation runs cleanly

**When to use this vs. true instancing:**
- ≤ ~8 copies, each needing distinctly different transforms (especially animated independently)
- You want each copy to be addressable individually for later branching
- The geometry isn't expensive enough that you need GPU instancing

**When NOT to use this:**
- N > ~10: switch to geometryCOMP instancing via POP attributes (see Pattern 1)
- All copies should have identical animation: use a single transform + the geo COMP's instancing tab

**Pattern variations:**
- 3-fold (120° between branches) for triangular symmetry
- 4-fold (90° between branches) for cross symmetry
- Plus translation offsets for non-radial compositions

---

## Pattern 10 — Per-Instance Material Variation

Material reads per-instance attributes:

```
GLSL MAT with fragment shader:
  in vec4 inst_color;  // instance color attribute
  out_color = inst_color * base_tex;
```

Or with Phong MAT:
- Constant MAT reads Cd attribute via built-in.
- PBR MAT supports per-instance albedo tint via attribute.

Expose custom attributes via:
- Geometry COMP Instance tab → Custom Attribute rows.
- POP defines the attribute; Geometry COMP exposes it; MAT consumes it.

---

## Scaling Strategy

| N (instance count) | Method |
|---------------------|--------|
| 1–10 | Copy SOP or manual placement |
| 10–50 | Replicator COMP |
| 50–500 | CHOP-driven Instance on Geometry COMP |
| 500–100,000 | POP → Geometry COMP instance |
| 100,000+ | POP with aggressive culling; consider screen-space techniques |

---

## Performance Notes

- **POP instancing is GPU** — 50k instances render at full framerate on M1 with simple template geometry.
- **Template complexity matters** — 50k copies of a 1000-triangle mesh = 50M triangles. Keep templates simple (low-poly cubes, quads, spheres).
- **Point Sprite MAT is the cheapest instance material** — billboarded quad.
- **Per-instance color is cheap**; per-instance texture (different texture per instance) is expensive.
- **Per-instance custom attributes cost bandwidth** — minimize count. Each custom attribute adds a float/vec per instance transferred to the shader.
- **Shadow casting on instances is expensive** — often OK to disable shadows on instanced geometry, keep on hero objects only.

---

## Debugging Instancing

- **See zero instances**: Instance tab is Off; or CHOP/POP has 1 sample instead of N.
- **See one instance at origin**: all N samples have the same position, or Translate OP is wired wrong.
- **See correct count but black**: template geometry's MAT is broken, or lighting is off.
- **See the right shape but wrong color**: Cd attribute not reaching MAT. Check attribute name and Custom Attribute wiring.
- **Performance drops as N grows**: template is too complex, OR shadow casting is on, OR per-instance texture is enabled.

---

## Canonical Example — 10,000 Audio-Reactive Cubes

```
Base COMP "scene_cubes"
  ├─ Grid POP (100×100 = 10,000 points)
  ├─ Attribute From CHOP POP (reads null_audio_spectrum, one bin per point → @pscale)
  ├─ Noise POP (small jitter on P)
  ├─ Attribute POP (@Cd = HSV from @pscale)
  ├─ Null POP "null_grid"
  │
  ├─ Geometry COMP:
  │    - SOP: Box SOP (size 0.05)
  │    - Instance: null_grid; Translate=P, Scale=pscale, Color=Cd
  │    - Material: Constant MAT (color from Cd)
  │
  ├─ Camera COMP (orbit)
  ├─ Light COMP (ambient only — Constant MAT doesn't need lights)
  ├─ Render TOP (1280×720)
  └─ Post stack (Bloom → Level → Out)
```

One spectrum-driven field of 10k cubes. ~6ms cook on M1.

---

## Reading This File

Start with the scaling strategy table to pick your method, then the pattern number for that method. For the POP operator details behind patterns 1, 5, 6, 7, 9 see `TD_OPERATORS_POP.md`.
