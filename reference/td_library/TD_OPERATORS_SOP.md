---
title: SOPs — Surface Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every SOP in TD 2025.32460. CPU-based 3D geometry. See POPs for GPU geometry.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_POP.md, TD_PATTERNS_3D_SCENES.md
---

# SOPs — SURFACE OPERATORS CATALOG

SOPs are **CPU-based 3D geometry**. Points, polygons, curves, NURBS. They predate POPs and are still the right tool for procedural modeling, NURBS, authored meshes, and any geometry below ~5k points.

**Core mental model:** a SOP is a bag of points + primitives (polygons / curves / NURBS patches), with optional attributes on points / primitives / vertices / details.

**SOP vs POP:**
- SOP: CPU. Good for traditional modeling, imported meshes, curves, NURBS. Limited to ~10k points before perf drops.
- POP: GPU. Good for particle clouds, heavy instancing, per-point math at large counts.

**Default:** SOP for traditional 3D work; POP for large N / per-frame point animation. See `TD_OPERATORS_POP.md` last-section decision table.

---

## Generators — Primitives

### Box SOP
Cube / rectangular box.
- Params: Size, Center, Divisions.

### Sphere SOP
Sphere (polygon, NURBS, or mesh).
- Params: Radius, Rows, Columns, Type (polygon, NURBS, mesh, primitive).

### Grid SOP
Flat grid / plane.
- Params: Size, Divisions, Orientation.

### Torus SOP
Donut / torus.

### Circle SOP
Circle / ellipse / disc.
- Params: Radius, Divisions, Orientation, Arc Type (full, open arc, closed arc).

### Tube SOP
Cylindrical tube with optional caps.

### Line SOP
Straight line segment.

### Rectangle SOP
2D rectangle — useful for ribbons, UI, texture planes.

### Text SOP
Extruded 3D text from a font.
- Params: Text, Font, Size, Depth (extrusion), Bevel.

### Metaball SOP
Isosurface from blended metaballs.
- Params: Weight, Radius.

### Fractal SOP
Fractal geometry — terrain, organic forms.

### Polygon SOP
Polygon shapes (triangle, N-gon).

### L-System SOP
Lindenmayer system — procedural plant / tree generation from rules.

### Arc SOP / Curve SOP / NURBS Curve SOP
Curve generators.

### Twist SOP — see Deformers.

---

## Generators — File Import

### File In SOP
Imports 3D files (OBJ, FBX, STL, etc.).
- Params: File, Reload, Scale, Rotation.

### Alembic In SOP
Imports Alembic (.abc) — animated geometry from Cinema 4D / Houdini / Blender.

### FBX In SOP (via File In)
FBX skeletal geometry.

### glTF In SOP
glTF format (modern web/interchange).

### Point File In SOP
Point cloud files.

---

## Deformers

### Transform SOP
Translate / Rotate / Scale the whole geometry.

### Twist SOP
Twists geometry along an axis.
- Params: Strength, Axis, Center.

### Bend SOP
Bends along an axis.

### Taper SOP
Tapers along an axis.

### Noise SOP
Displaces points with noise.
- Params: Noise Type, Amplitude, Frequency, Roughness, Attribute to Affect (P, N, Cd, etc.).

### Lattice SOP
Free-form deformation via a lattice cage.

### Morph SOP
Blend between two topologically identical SOPs.

### Ray SOP
Project / raycast points onto target geometry.

### Wire SOP
Deform a SOP along a curve.

### Sweep SOP
Extrude a cross-section along a spine curve.

### Skin SOP
Surface spanning multiple curves.

### Extrude SOP
Extrude faces.

### Revolve SOP
Lathe — revolve a curve around an axis.

---

## Modifiers — Topology

### Boolean SOP
CSG operations (union, intersection, difference).

### Subdivide SOP
Catmull-Clark subdivision surface.

### Facet SOP
Computes face normals; controls faceting.

### Triangulate SOP / Triangulate 2D SOP
Converts polygons to triangles.

### Delete SOP
Removes points / polygons by criteria.

### Refine SOP
Refines curves / surfaces by inserting points.

### Cap SOP
Caps open curves / tubes.

### Reverse SOP
Reverses point / polygon order.

### Fuse SOP
Merges coincident points.

### Divide SOP
Divides polygons into smaller ones.

### Clip SOP
Clips geometry against a plane.

### Blend SOP
Blends multiple SOPs by weight.

### Fit SOP
Fits curve or surface to a set of points.

### Convert SOP
Converts between geometry types (polygon ↔ NURBS ↔ mesh ↔ polyline).

---

## Attributes

### Attribute Create SOP
Adds an attribute (point / prim / vertex / detail, float/vec/string).
- Params: Class, Name, Type, Default.

### Attribute SOP
Per-attribute arithmetic / expression.

### Point SOP
Per-point operations — position, normal, color, etc.

### Primitive SOP
Per-primitive operations.

### Vertex SOP
Per-vertex operations.

### Detail SOP
Per-detail-level single values.

### Sort SOP
Sorts points / primitives by criteria.

### Group SOP
Assigns points / primitives to named groups.

### Normal SOP
Computes or modifies normals.

### UV Map SOP
Assigns UV coordinates — Box, Spherical, Cylindrical, Polar, Auto.

### UV Texture SOP
Manipulates UVs.

### UV Transform SOP
Translates / scales / rotates UVs.

### UV Unwrap SOP (if present in build)
Automatic UV unwrapping.

### Color SOP
Sets per-point colors.

### Material SOP
Assigns materials to primitives.

---

## Combinations

### Merge SOP
Merges multiple SOPs.

### Copy SOP
Copies one SOP's geometry onto every point of another SOP — the classic copy-stamp.
- Params: Count, Stamp (per-copy variations).

### Replicator SOP (deprecated — see Replicator COMP / POP instancing for new work)

### Switch SOP
Switches between inputs.

### Cross SOP
Blends between SOPs.

### Magnet SOP
Attractive / repulsive deformation based on another SOP.

### Stitch SOP / Join SOP
Joins SOPs by closest points / shared edges.

### Align SOP
Aligns point sequences.

---

## Particle / Dynamics SOPs (legacy; prefer POPs for new work)

### Particle SOP
Legacy CPU particle system.
- Still functional; for any serious particle work on 2025 and Mac, use POPs instead.

### Spring SOP
Mass-spring system.

### Wire SOP (dynamics)
Rope / wire simulation.

### Cloth SOP
Cloth simulation.

### Bullet Solver COMP (rigid body dynamics) — COMP, not SOP, but often used alongside SOPs.

---

## Specialty

### Font SOP (legacy text; prefer Text SOP)

### Model SOP
Parametric modeling node.

### Trace SOP
Traces an image silhouette into a 2D polygon/curve.

### Script SOP
Python script operating on geometry.
- Expensive; use only for small point counts or one-shot initialization.

### Carve SOP
Extract portions of a curve.

### Facet SOP — see Modifiers.

### In SOP / Out SOP
COMP I/O.

### Null SOP
Named endpoint passthrough.

### Select SOP
Pulls a SOP from elsewhere.

### Object Merge SOP
Merges SOPs from other COMPs, with transforms applied.

---

## Curves & NURBS

### NURBS Curve SOP / NURBS Surface SOP
NURBS geometry creation.

### Profile SOP
Extract profile curves from surfaces.

### Skin SOP — see Deformers.

### Sweep SOP / Extrude SOP / Revolve SOP — see Deformers.

### Sweep SOP with a Circle cross-section along a Curve = tube along a path.

---

## Bridges to Other Families

### SOP to DAT (as part of export)
Dump SOP attributes to tables.

### SOP to POP
Bridges CPU SOP data into POP pipeline.

### POP to SOP
Bridges POP stream back into SOP pipeline (usually to import instance data for SOP-dependent operators).

### Pre / In / Out / Null: COMP I/O and endpoints.

---

## Canonical SOP Chains

### Procedural plant
```
L-System SOP ──► Skin SOP ──► Subdivide ──► Noise (on P) ──► UV Map ──► Null ──► Material SOP
```

### Copy stamp cubes on a sphere
```
Sphere SOP ──► Null ("emit_points")
Box SOP ──► Copy SOP (Template In = emit_points, Count per-point) ──► Null ("copied_cubes")
```
For large N (>500), use POP instancing instead.

### Imported mesh prep
```
File In (.fbx) ──► Transform ──► Normal ──► UV Map ──► Fuse (optional) ──► Null ──► Material
```

### Extruded 3D text
```
Text SOP ──► Extrude ──► Bevel ──► Subdivide ──► Normal ──► Null ──► render
```

### Ribbon along a curve
```
Circle SOP (cross-section) ──► Null
Curve SOP (spine)           ──► Sweep SOP (Cross-Section = circle) ──► Null
```

### Cloth drape
```
Grid SOP ──► Cloth SOP (with collision / constraints) ──► Normal ──► Material
```

---

## SOP vs POP Decision Table

| Scenario | SOP | POP |
|----------|-----|-----|
| <1k static or simple animated points | SOP | POP also fine |
| >5k points, animated per-frame | ✗ | POP |
| Procedural modeling / curves / NURBS | SOP | ✗ |
| Imported animated mesh (Alembic) | Either | POP if Alembic In POP supports it |
| Instancing 10k+ objects | ✗ | POP → Geometry COMP |
| Particle system with forces | Particle SOP (legacy, small) | Simulate POP + Force POPs (preferred) |
| Text to 3D | Text SOP | Text POP if you want per-glyph point cloud |

---

## SOP Performance Notes

- SOPs run on CPU — cost scales with point count, primitive count, and per-point math.
- Script SOP is the slowest SOP — avoid per-frame at scale.
- Subdivide SOP at high levels explodes point counts — use sparingly in per-frame contexts.
- Cloth, Spring, Wire simulations: fine for small meshes; heavy for large.
- Cache SOP (like Cache TOP) — not a thing; use Lock / Fix / Freeze by disconnecting input once geometry is final.
- For large static geometry that doesn't change per frame, save to a file and File In — disk-backed is faster than recomputing.

---

## Reading This File

Grep by SOP name. Groups: Generators (primitives + imports), Deformers, Modifiers (topology), Attributes, Combinations, Specialty, Curves, Bridges. For pipeline shapes, see "Canonical SOP Chains."
