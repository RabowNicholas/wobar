---
title: POPs — Point Operators Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every POP in TD 2025.32460. GPU-based point operators, introduced in the 2025 release. Priority knowledge gap.
dependencies: TD_LIBRARY_INDEX.md, TD_EFFICIENT_NETWORKS.md, TD_PATTERNS_INSTANCING.md, TD_PATTERNS_PARTICLES.md
---

# POPs — POINT OPERATORS CATALOG

POPs are the newest operator family, introduced in TD 2025. They are **GPU-based point processors** built on compute shaders. Think of them as SOPs that run on the GPU — or as a unified instancing + particle + geometry data pipeline.

**Why POPs matter on this machine:**
- GPU compute works fine on Mac Metal (geometry shaders don't — see `TD_APPLE_SILICON.md`).
- Replace slow Replicator COMP patterns for N > 50.
- Handle hundreds of thousands of points at real-time rates.
- Feed directly into Geometry COMP instancing without CPU intermediation.

**Core mental model:** a POP stream is an array of points, each with named attributes (position P, normal N, color Cd, UV uv, scale, rotation, plus any custom attribute you add). POPs read, transform, and output this array.

---

## POP Wiring Basics

- **Generator POPs** produce a stream with no input (Box, Sphere, Grid, Point Generator).
- **Transform POPs** take a POP stream in and output a modified stream.
- **Attribute POPs** read, write, or compute per-point attribute values.
- **Control POPs** merge, select, switch, sort, visualize.
- **Output paths:**
  - To **Geometry COMP → Instance** for rendering via instancing.
  - To **SOP** via a POP-to-SOP bridge operator.
  - To **CHOP** via POP to CHOP for channel extraction.

---

## Generator POPs

### Box POP
Creates a box-shaped point cloud or mesh representation.
- Key params: Size XYZ, Divisions XYZ, Geometry Type (points, quads, tris).
- Use: base shape for deformation, instancing source positions.

### Sphere POP
Creates a sphere point cloud.
- Key params: Radius, Rows, Columns, or Point Count for uniform sphere.
- Modes: UV sphere (rows/cols), Fibonacci sphere (evenly distributed).
- Use: emitters, bounded distributions, hero geometry bases.

### Grid POP
Creates a regular grid of points or quads.
- Key params: Size X/Y, Divisions X/Y, Center.
- Use: flat plane of instances (a field of cubes), texture sampling grid.

### Circle POP
Creates a ring or disc of points.
- Key params: Radius, Divisions, Fill (hollow ring vs filled disc).
- Use: radial layouts, orbit bases.

### Line POP
Line of points between two endpoints.
- Key params: Start XYZ, End XYZ, Point Count.
- Use: beam geometry, ribbon source, path sampling.

### Tube POP
Cylindrical tube point cloud.
- Key params: Radius, Height, Rows, Columns, Caps.
- Use: tunnel geometry, column instancing sources.

### Torus POP
Ring/donut point cloud.
- Key params: Orbit Radius, Cross Radius, Orbit Divs, Cross Divs.
- Use: ring visuals, orbital systems.

### Point Generator POP
Generates N points with attributes determined by expressions or CHOP input.
- Key params: Point Count, Attribute expressions.
- **This is the flexible workhorse.** When you need arbitrary N points with custom starting attributes, this is the generator.

### Pattern POP
Generates points following procedural patterns (waves, sines, noise).
- Key params: Pattern Type, Frequency, Amplitude, Phase.
- Use: audio-driven waveform geometry, procedural instancing sources.

### Alembic In POP
Loads point data from an Alembic (.abc) file.
- Use: imported animated point clouds, scanned geometry with per-point attributes.

### Text POP (new in 2025)
Generates point data from text — per-character, per-word, or per-path samples.
- Key params: Text, Font, Size, Sampling Mode (chars, glyphs, path samples).
- Use: typographic animation, text that explodes into particles.

### Trace POP (new in 2025)
Traces/samples a 2D image to produce points.
- Key params: Input TOP, Threshold, Sample Density.
- Use: convert a TOP (logo, silhouette) into a point cloud for instancing.

### Triangulate POP (new in 2025)
Takes points and produces triangles — Delaunay or Voronoi partitioning.
- Use: meshing a point cloud, creating triangulated surfaces for rendering.

### Import POP
Loads point data from external files (PLY, OBJ with point data, common interchange formats).
- Use: 3D-scanned clouds, externally authored point data.

---

## Transform POPs

### Extrude POP
Extrudes point curves/surfaces along a vector or normal.
- Key params: Direction, Distance, Steps.
- Use: from-line to prism; thickening thin geometry.

### Revolve POP
Revolves a curve of points around an axis to create a surface.
- Key params: Axis, Revolutions, Divisions.
- Use: lathe-style geometry, pottery forms, circular symmetry.

### Skin POP
Creates a surface from multiple curves of points (like loft).
- Key params: input curves, bridging mode.
- Use: ribbons, arches, surface from rails.

### Trail POP
Records position history of points and outputs trailing geometry.
- Key params: Trail Length (samples), Step, Attributes to trail.
- Use: motion trails for particles, streak geometry.

### Subdivide POP
Subdivides point geometry — increases point density.
- Key params: Subdivision Level, Scheme (linear, Catmull-Clark-like).
- Use: smooth imported low-res geometry; densify before deformation.

### Sprinkle POP
Scatters points over surface of input geometry.
- Key params: Count, Seed, per-triangle weighting.
- Use: scatter instances (grass, rocks, particles) on a surface.

### Facet POP
Controls shading faceting — computes face normals vs smooth normals.
- Key params: Smooth Threshold, Compute Normals On/Off.
- Use: flat-shaded look vs smooth shading prep before materials.

### Normal POP
Computes or modifies per-point normals.
- Key params: Method (computed from neighbors, aligned to axis, from attribute).
- Use: before lighting — ensure usable normals exist.

### Ray POP
Raycasts points against geometry; outputs hit data as attributes.
- Key params: Ray direction, Max distance, Hit geometry reference.
- Use: drop points onto terrain; intersection-based effects.

### Boundary POP
Extracts boundary points/curves from a point cloud or mesh.
- Use: edge geometry, contour lines.

### Noise POP
Adds noise to point attributes (position, normal, scale, color, etc.).
- Key params: Noise Type (Sparse, Perlin, Simplex), Amplitude, Frequency, Seed, Attribute to Affect.
- Use: organic displacement, jitter, randomization.

### Transform POP
Translates/rotates/scales the whole point stream.
- Key params: T XYZ, R XYZ, S XYZ, Pivot, Order.
- Use: positioning a whole stream in world space before merging with others.

### Twist POP / Bend POP / Taper POP
Deformers analogous to SOP deformers but on POP streams.
- Key params: axis, amount, range.
- Use: warp organized geometry.

### Lattice POP
Deform a stream via a control lattice.
- Use: free-form deformation of a point cloud.

### Copy POP
Copies a template onto each input point — classic "copy stamp" pattern.
- Key params: Template input, Count, Attribute propagation.
- Use: cubes copied onto a sphere of emit points.

---

## Attribute POPs

Attributes are the per-point data fields. Default attributes: P (position), N (normal), Cd (color diffuse), uv (UV0), plus often pscale, alpha, id, v (velocity), rot.

### Attribute Create POP
Adds a new attribute to the stream.
- Key params: Name, Class (float/vec2/vec3/vec4), Default value.
- Use: before referencing a custom attribute, you must create it.

### Attribute POP
General-purpose per-point attribute manipulation via expressions.
- Key params: per-attribute expression field.
- Use: `Cd = @P * 0.5 + 0.5;` etc. — small per-point math.

### Attribute From Texture POP
Samples a TOP and writes the sample to per-point attributes.
- Key params: Input TOP, UV source, Attribute to write.
- Use: color points by sampling an image at their UV; write displacement from a heightmap.

### Attribute From CHOP POP
Pulls CHOP channels into per-point attributes.
- Use: drive positions or colors with a multi-sample CHOP.

### Attribute Copy POP
Copies attributes from a reference stream onto this stream.
- Key params: Source stream, Attributes to copy, Matching (by ID, by index, by proximity).
- Use: transfer colors from a scanned cloud onto a resampled cloud.

### Attribute Promote POP
Promotes an attribute from one class to another (e.g., vertex attribute to per-primitive).
- Use: bridging SOP-style attribute classes in POP pipeline.

### Attribute Delete POP
Removes attributes.
- Use: clean up before export or to reduce memory.

### Attribute Rename POP
Renames an attribute.
- Use: standardize names before merging streams with different conventions.

---

## Control POPs

### Merge POP
Merges multiple POP streams into one. Unions.
- Key params: Attribute Handling (keep all / keep first / merge).
- Use: combine emitters with different source shapes.

### Select POP
Pulls a POP stream from elsewhere in the project by name.
- Use: cross-network reference without wiring.

### Switch POP
Switches between multiple inputs by index.
- Use: scene switching, A/B testing POP variants.

### Null POP
Named passthrough; cache point; reference target.
- Use: always name your endpoints.

### Sort POP
Sorts points by attribute value (by depth, by ID, by scalar).
- Use: depth-sort for transparency; order for iteration.

### Filter POP / Group POP
Selects a subset of points by attribute value criteria.
- Use: keep only points where `@pscale > 0.5`; split into subsets.

### Delete POP
Removes points matching criteria.
- Use: cull points outside bounds; remove dead particles.

### Visualize POP
Viewer helper — shows attributes as overlay (labels, gizmos).
- Use: debug — see exact values per point.

### Info POP / POP Info DAT
Returns metadata about a stream (point count, attribute list, bounds).
- Use: driving logic based on "how many points are in this stream right now."

### Reorder POP
Reorders attributes for efficient GPU packing.
- Use: rare — performance tuning at high point counts.

---

## Simulation / Dynamics POPs

### Simulate POP
Runs point simulation — velocity integration, force accumulation.
- Key params: Timestep, Forces input.
- Use: particle simulation; points with momentum.

### Force POP family
Apply forces to simulated points — Gravity POP, Wind POP, Vortex POP, Attract POP, Turbulence POP, Drag POP.
- Use: compose the force field driving a Simulate POP.

### Collide POP
Collision detection/response against geometry.
- Use: particles bouncing off surfaces.

### Constrain POP
Constrain points to a surface, line, or distance relationship.
- Use: particles stuck on a plane; fabric-like behavior.

### Lifespan POP
Manage per-point age and removal on death.
- Key params: Lifetime, Birth Attribute, Removal mode.
- Use: emitter → lifespan → particles die out naturally.

---

## Scripting POPs

### GLSL POP / GLSL Compute POP
Write a compute shader that operates on the point stream.
- Key params: GLSL code, uniforms, input bindings.
- Use: custom per-point math not covered by stock POPs.

### Script POP
CPU-side Python script over the point stream.
- Key params: Python function.
- Use: **only for small streams or one-shot initialization.** Do not use per-frame on large streams.

---

## Output / Bridge POPs

### POP In / POP Out
COMP I/O — used inside Base COMPs to pass streams in and out.

### Convert POP
Converts between POP representations (point cloud, mesh, line, etc.).

### SOP to POP / POP to SOP
Bridges between legacy SOP pipeline and POP pipeline.
- Use: imported SOP geometry into POP stream; POP result back into a SOP-only workflow.

### POP to CHOP
Extracts a single attribute across all points as a CHOP channel.
- Use: point positions → CHOP for Geometry COMP instance Translate OP.

### POP to DAT
Dump attribute values to a table DAT for inspection or export.

---

## Instancing Pattern (Canonical)

The most common POP use — instance geometry on points:

```
Sphere POP ──► Noise POP (jitter positions) ──► Attribute POP (set Cd from audio)
              ──► POP to CHOP ──► [exports to] ──► Geometry COMP
                                                    │
                                                    └─► Instance On
                                                        Translate OP = POP to CHOP
                                                        Rotate = (POP to CHOP)
                                                        Scale = (POP to CHOP)
                                                        Color = (POP to CHOP)
                                                    Template geometry: Box SOP
```
The Geometry COMP iterates per instance, placing a Box SOP at each Sphere POP point.

---

## Common Pipelines

### Pipeline A — Audio-reactive scatter
```
Grid POP ──► Attribute From CHOP POP (audio amplitude → @pscale)
         ──► Noise POP (animate jitter)
         ──► Attribute POP (color from scale)
         ──► Geometry COMP instance
```

### Pipeline B — Text explosion
```
Text POP ──► Noise POP (explode outward)
         ──► Simulate POP with Drag + Gravity forces
         ──► Lifespan POP
         ──► Geometry COMP instance (small glowing quad)
```

### Pipeline C — Scanned cloud replay
```
Alembic In POP ──► Attribute Copy POP (color from reference)
               ──► Transform POP (scene positioning)
               ──► Geometry COMP instance
```

### Pipeline D — Image-driven particles
```
Trace POP (image silhouette) ──► Sprinkle POP (densify)
                             ──► Noise POP (jitter)
                             ──► Geometry COMP instance with Point Sprite MAT
```

### Pipeline E — Data-driven vis
```
Table DAT ──► DAT to CHOP ──► Pattern POP (or Point Generator POP with per-point attrs)
                          ──► Attribute POP (compute colors)
                          ──► Geometry COMP instance
```

---

## POP Performance Notes

- POPs run on GPU compute — do not fall back to Script POP for per-frame per-point logic.
- Attribute POPs are cheap. Chain them freely.
- Simulate POP with <50k points runs in real-time on M1.
- >500k points starts to stress M1 — benchmark specifically.
- Trail POP cost scales with Trail Length × point count.
- Raycast POP with dense geometry is expensive — minimize Max Distance; use BVH source geometry.
- Use POP to CHOP **once** at the end of the chain, not multiple times — the GPU→CPU readback is the expensive part.

---

## POP vs SOP — Quick Decision

| Need | Use |
|------|-----|
| Large point counts (>10k) for instancing | POP |
| Per-frame per-point animation | POP |
| CPU-only geometry authoring (modeling) | SOP |
| Legacy workflow with established SOP chains | SOP |
| Particle systems | POP (new), Particle SOP (legacy, smaller systems) |
| Procedural meshing, curves, 3D modeling | SOP |
| Sampling a TOP as points | POP (Trace POP) |
| Traditional NURBS / SubD modeling | SOP |

**Default for new work involving per-point data and large counts: POP.**

---

## Reading This File

Use Grep / search by POP name. All POPs are grouped by function — skim the function headers to find the right one. For pipelines, see the canonical examples near the end, then the pattern files (`TD_PATTERNS_INSTANCING.md`, `TD_PATTERNS_PARTICLES.md`).
