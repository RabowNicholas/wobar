---
title: Geometry Nodes — Procedural Geometry Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Geometry Nodes graph reference — fields, attributes, the node taxonomy (mesh/curve/instance/volume/point/utility/simulation/repeat), common procedural patterns, the bpy node-tree API surface, performance notes.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_DATA_MODEL.md
---

# GEOMETRY NODES — PROCEDURAL GEOMETRY REFERENCE

Geometry Nodes is Blender's procedural modeling system. It is the Blender analog of TouchDesigner's POPX family — a graph that transforms geometry data through a chain of nodes, with everything driven by **fields** (per-element functions) rather than scalar parameters. A Geometry Nodes graph lives inside a **Geometry Nodes modifier** on an Object, takes the object's geometry as input, and outputs new geometry that replaces it in the modifier stack.

Geometry Nodes is the workhorse for:

- Scattering instances (grass, rocks, crowds, particles).
- Procedural meshing (parametric props, architecture, generative form).
- Curve work (sweeps, profile lofts, hair/cable systems).
- Simulation (cloth-like, flock, n-body, generative growth — via simulation zones).
- Data import / sampling / baking (read OBJ, VDB, CSV directly in 4.5+).

This document is the catalog. For the broader Python surface that drives these graphs, see [[BLENDER_PYTHON_API]]. For the underlying data model (`bpy.data.node_groups`, `Object.modifiers`), see [[BLENDER_DATA_MODEL]]. For materials referenced by the Set Material node, see [[BLENDER_MATERIALS]] and [[BLENDER_SHADER_NODES]]. For ready-to-paste recipes, see [[BLENDER_PATTERNS_PROCEDURAL]].

**Core facts:**

- Geometry Nodes is a **modifier** (`type='NODES'`) on an Object. The modifier holds a pointer to a NodeGroup (`mod.node_group`) and a per-modifier values dict for the exposed inputs.
- NodeGroups live in `bpy.data.node_groups`. A Geometry Nodes group is the type `'GEOMETRY'` (i.e. `node_group.bl_idname == 'GeometryNodeTree'`).
- **Fields vs values** is the central mental model. A field is a function evaluated per-element on a domain; a value is a single number/vector. Sockets accept one or the other (or both).
- **Attributes** are named per-domain data stored on geometry. Domains: `POINT`, `EDGE`, `FACE`, `CORNER` (face-corner), `CURVE` (spline), `INSTANCE`, `LAYER` (Grease Pencil).
- The five geometry types Geometry Nodes operates on: **Mesh**, **Curve**, **Point Cloud**, **Volume**, **Instances**. (A sixth, **Edit**, is internal — exposed only inside certain edit nodes.)
- **Instances are lazy.** A million instances of the same mesh cost one mesh worth of memory. `Realize Instances` collapses the hierarchy and is expensive.
- **Simulation zones** (4.0+) carry state from one frame to the next — input/output node pair, automatic cache during playback.
- **Repeat zones** (4.0+) run a sub-graph N times at compile time. Not per-frame — a deterministic loop inside one evaluation.
- **For Each Element zones** (4.3+) iterate over every element of a geometry. Slower than vectorized fields; use only when per-element branching is required.
- **Bake nodes** (4.1+) explicitly cache geometry at a point in the graph. Bake-still and bake-animation modes. Bakes can be packed into the `.blend` (4.3+).
- **`tree.interface`** (4.0+) is the API for declaring group inputs/outputs. The pre-4.0 `inputs`/`outputs` API is removed.
- The modifier-stack order matters: Geometry Nodes can sit before or after Subdivision Surface, Mirror, etc. — the modifier evaluates on its input geometry, not the raw mesh datablock.

---

## Fields and the Field-vs-Value Model — Read This First

This is the foundational concept. Get this wrong and nothing else makes sense.

A **value** is a single number, vector, color, or boolean. The node socket pin for a value is a **filled circle**.

A **field** is a function — a recipe for computing a value per element on whatever domain is being evaluated. `Position` is a field: it returns a different vector for each vertex / face / point. `Index` is a field. `Normal` is a field. A constant `3.0` plugged into a node is a value.

The node socket pin for a field input is a **hollow / diamond shape**. The socket accepts either a literal value (which becomes a constant field) or another field.

**The implicit "input on domain" concept:** When a field reaches a node that operates on geometry, it is evaluated *on the domain the node operates on*. `Set Position` takes a Position field and evaluates it once per point. `Set Material Index` takes an Index field and evaluates it once per face. The same field connected to different nodes can resolve to entirely different shapes of data — this is the system's power and its #1 footgun.

**Fields are lazy.** Nothing computes until a field hits a node that consumes it on a domain. Plugging a field into a viewer node forces evaluation; plugging it into a value socket on another field-builder node just composes a longer field.

**Capture Attribute freezes a field.** When you want a field's value at a *specific point in the graph* (before later operations change the geometry), use Capture Attribute. The node evaluates the field on the chosen domain at that point and stores the result as an anonymous attribute that flows downstream with the geometry. This decouples "where the data was computed" from "where it's consumed."

**Example 1 — Why Capture Attribute matters:**

```
[Cube] → [Subdivide Mesh (Level=3)] → [Set Position offset=Noise(Position)] → Output
```

Here `Position` is sampled *after* subdivision, so noise is evaluated per subdivided vertex. If you wanted noise computed per *original* vertex and then carried through subdivision, you'd Capture Position on the points domain before subdivision, then read it back as the captured attribute after.

**Example 2 — Domain mismatch silently averages:**

```
[Mesh] → [Capture Attribute (Float, domain=FACE) input=Index] → ...
       → [Set Position offset=Combine XYZ(captured, 0, 0)]
```

Set Position evaluates on the POINT domain. The captured face-index attribute gets interpolated from FACE to POINT by averaging neighboring face indices. You wanted distinct per-face values; you got averaged ones. Either change the consumer or capture on POINT.

**Socket-shape quick reference:**

| Pin | Meaning |
|-----|---------|
| Filled circle | Value socket — accepts a single value. |
| Hollow circle | Field input — accepts a field (or a value, which becomes constant). |
| Diamond | Field output — produces a field. |
| Filled square | Geometry socket — passes a geometry datablock. |

---

## Domains

Every attribute lives on a domain. Choosing the wrong domain is the second most common Geometry Nodes bug (after misreading field-vs-value).

| Domain | Lives on | Common attributes |
|--------|----------|-------------------|
| `POINT` | Mesh vertices, Point Cloud points, Curve control points | `position`, `radius`, `id`, `velocity` |
| `EDGE` | Mesh edges | `edge_crease`, `bevel_weight`, edge sharp/seam flags |
| `FACE` | Mesh faces | `material_index`, `sharp_face`, face area |
| `CORNER` (face-corner) | Mesh face corners (per-loop) | `UVMap`, vertex colors (per-corner color), corner normals |
| `CURVE` | Spline | `cyclic`, `resolution`, `nurbs_weight`, handle types |
| `INSTANCE` | Instance entries | per-instance transform, instance index, custom attrs |
| `LAYER` | Grease Pencil layer | layer-level attrs (Grease Pencil v3, 4.3+) |

**Why it matters:**

- **Store Named Attribute** has a Domain dropdown. The same name on POINT vs FACE produces two distinct attributes.
- **Capture Attribute** has a Domain dropdown. It evaluates the input field on that domain and stores the result there.
- **Set Position** writes to the POINT domain implicitly — there is no domain dropdown. If your Offset field is captured on FACE, it interpolates down to POINT.
- **Auto-interpolation:** Blender interpolates attributes between domains as needed (FACE → POINT averages; POINT → FACE averages; CORNER → POINT interpolates). This is convenient but lossy — explicit Capture on the target domain is more predictable.

`Domain Size` returns the count of elements in a domain — useful for guarding against empty geometry and for index math.

---

## Geometry Types

Geometry Nodes treats geometry as a "geometry set" — a container that can hold any combination of these types simultaneously. Most nodes take and return a single geometry set; some operate on only one type and pass others through unchanged.

| Type | What it is | Built from | Typical conversion |
|------|------------|------------|--------------------|
| **Mesh** | Vertices + edges + faces. The polygon mesh. | Primitives, edit ops, Curve to Mesh, Volume to Mesh | the default. |
| **Curve** | Control points + spline data (Bezier / NURBS / Poly / Catmull-Rom). | Curve primitives, Mesh to Curve | Curve to Mesh, Curve to Points. |
| **Point Cloud** | Points with position, radius, optional attributes. No connectivity. | Distribute Points, Mesh to Points, Points node | Points to Vertices (→ Mesh), Points to Volume. |
| **Volume** | OpenVDB sparse grids — density, velocity, etc. | Volume Cube, Mesh to Volume, VDB import (4.5+) | Volume to Mesh, Distribute Points in Volume. |
| **Instances** | Lightweight references to other geometry with per-instance transforms. | Instance on Points, Collection Info (with Separate Children), Object Info (instance mode) | Realize Instances → flat geometry; Instances to Points → centers. |
| **Edit** | Internal-only edit-mode representation. | n/a | Exposed inside specific edit-mode nodes only. |

**Common conversions:**

- `Mesh to Points` — turns mesh vertices into a Point Cloud. Carries selected attributes.
- `Mesh to Curve` — turns mesh edge loops into curves. 4.5 adds a "Face" mode (each face becomes a cyclic curve).
- `Curve to Mesh` — sweeps a profile curve along a curve. The workhorse for ribbons, cables, pipes. 4.5 adds a `Scale` input replacing the implicit `radius` use.
- `Curve to Points` — samples the curve at N points or by length.
- `Points to Vertices` — Point Cloud → Mesh with no edges/faces.
- `Mesh to Volume` — voxelizes a mesh into a density VDB. Expensive.
- `Volume to Mesh` — surface-extracts (Adaptive / Fixed). Expensive.
- `Points to Volume` — splatters points into a density grid.

---

## Node Taxonomy — Mesh Nodes

### Primitives

- **Cube** (`GeometryNodeMeshCube`) — Size XYZ, Vertices XYZ. Produces a UV-unwrapped cube.
- **UV Sphere** (`GeometryNodeMeshUVSphere`) — Segments, Rings, Radius.
- **Ico Sphere** (`GeometryNodeMeshIcoSphere`) — Subdivisions, Radius. Tri-only.
- **Cylinder** (`GeometryNodeMeshCylinder`) — Vertices, Side Segments, Fill Segments, Radius, Depth, Fill Type.
- **Cone** (`GeometryNodeMeshCone`) — same family as Cylinder with top/bottom radius.
- **Grid** (`GeometryNodeMeshGrid`) — Size X, Size Y, Verts X, Verts Y. The base for displacement work.
- **Mesh Line** (`GeometryNodeMeshLine`) — N points along an axis; Offset / Start+End modes.
- **Mesh Circle** (`GeometryNodeMeshCircle`) — Vertices, Radius, Fill Type (None/N-gon/Triangle Fan).

### Operations

- **Subdivide Mesh** (`GeometryNodeSubdivideMesh`) — Linear subdivision. Doubles edge count per level. Cheap.
- **Subdivision Surface** (`GeometryNodeSubdivisionSurface`) — Catmull-Clark smoothing subdivision. UV smoothing, boundary smoothing options.
- **Triangulate** (`GeometryNodeTriangulate`) — Quad and N-gon methods (Beauty / Fixed / Clip).
- **Dual Mesh** (`GeometryNodeDualMesh`) — Faces ↔ vertices swap. Tris become hex-ish patterns.
- **Mesh Boolean** (`GeometryNodeMeshBoolean`) — Intersect / Union / Difference. Solver: Exact (robust, slow) vs Fast.
- **Mesh to Curve** (`GeometryNodeMeshToCurve`) — Edge loops → curves. 4.5: Face mode.
- **Mesh to Points** (`GeometryNodeMeshToPoints`) — Vertices/Edges/Faces/Corners → Point Cloud. Mode dropdown selects source domain.
- **Mesh to Volume** (`GeometryNodeMeshToVolume`) — Voxelize. Density mode + voxel size. Expensive.
- **Extrude Mesh** (`GeometryNodeExtrudeMesh`) — Vertices/Edges/Faces modes. Offset field per element. Returns Top/Side selection fields.
- **Scale Elements** (`GeometryNodeScaleElements`) — Per-face/edge scale with pivot. Field-driven.
- **Split Edges** (`GeometryNodeSplitEdges`) — Disconnect edges by selection. Used to harden seams.
- **Flip Faces** (`GeometryNodeFlipFaces`) — Reverse face normals on selection.
- **Set Mesh Normal** (`GeometryNodeSetMeshNormal`) — 4.5+. Custom corner normals. Modes: Tangent Space, Free (3D vector).

### Topology query nodes

These return adjacency info as fields. All cheap.

- **Edge Vertices** — for current edge, returns vert indices/positions of endpoints.
- **Edge Neighbors** — face count adjacent to edge.
- **Edges of Vertex** — per vertex: connected edge indices.
- **Edges of Corner** — per face-corner: the two edges around it.
- **Face of Corner** / **Vertex of Corner** / **Corners of Face** / **Corners of Vertex** — corner ↔ face/vertex lookups.
- **Offset Corner in Face** — walk N corners around a face.

Topology queries are the foundation for hand-rolled algorithms — adjacency, dual graphs, mesh walks.

---

## Node Taxonomy — Curve Nodes

### Primitives

- **Bezier Segment** (`GeometryNodeCurvePrimitiveBezierSegment`) — 2-pt with handles.
- **Curve Circle** (`GeometryNodeCurvePrimitiveCircle`) — Radius + Resolution; also 3-Points mode.
- **Curve Line** (`GeometryNodeCurvePrimitiveLine`) — Start + End or Direction + Length.
- **Quadratic Bezier** (`GeometryNodeCurveQuadraticBezier`) — 3-pt control-poly Bezier.
- **Star** (`GeometryNodeCurveStar`) — Inner/Outer radius, Points, Twist.
- **Quadrilateral** (`GeometryNodeCurvePrimitiveQuadrilateral`) — Rect / Parallelogram / Trapezoid / Kite / Points.
- **Spiral** (`GeometryNodeCurveSpiral`) — Resolution, Rotations, Start/End Radius, Height, Reverse.
- **Arc** (`GeometryNodeCurveArc`) — Radius, Start/End angle, or 3-Points mode.

### Operations

- **Resample Curve** (`GeometryNodeResampleCurve`) — Count / Length / Evaluated mode. Re-spaces control points uniformly. Foundation for any curve sweep.
- **Fillet Curve** (`GeometryNodeFilletCurve`) — Bezier/Poly fillet at corners with radius.
- **Curve to Mesh** (`GeometryNodeCurveToMesh`) — Sweep profile along curve. Fill caps option.
- **Curve to Points** (`GeometryNodeCurveToPoints`) — Sample to Point Cloud. Count / Length / Evaluated modes.
- **Trim Curve** (`GeometryNodeTrimCurve`) — Cut by Factor (0..1) or Length.
- **Set Curve Handle Type** — Free/Auto/Vector/Align.
- **Set Curve Tilt** — Per-point twist along curve normal.
- **Set Spline Cyclic** — Open ↔ closed loop.
- **Set Spline Resolution** — Bezier eval resolution per spline.
- **Reverse Curve** — Flip direction.
- **Set Spline Type** — Convert between Poly / Bezier / NURBS / Catmull-Rom.

### Curve fields (read-only, per-domain)

- **Curve Tangent** — Unit tangent vector along curve.
- **Curve Normal** — Normal vector (depends on tilt).
- **Curve Tilt** — Twist around tangent.
- **Curve Length** — Total length of each spline (CURVE domain) or distance along (POINT).
- **Curve Parameter** — `0..1` along each spline.
- **Endpoint Selection** — boolean field marking spline ends.
- **Handle Type Selection** — boolean for matching Bezier handle types.
- **Spline Cyclic** — boolean per CURVE domain.
- **Spline Resolution** — int per CURVE domain.
- **Is Spline Cyclic** / **Spline Length** — readback fields.

---

## Node Taxonomy — Point Nodes

- **Distribute Points on Faces** (`GeometryNodeDistributePointsOnFaces`) — Random / Poisson Disk modes. Density field, density factor, seed. Returns Normal and Rotation fields on the output points (key for orienting instances).
- **Distribute Points in Volume** (`GeometryNodeDistributePointsInVolume`) — Random / Grid modes. Requires a Volume input.
- **Points** (`GeometryNodePoints`) — Build a Point Cloud directly: Count + Position + Radius fields.
- **Points to Vertices** (`GeometryNodePointsToVertices`) — Point Cloud → Mesh verts. No edges.
- **Points to Volume** (`GeometryNodePointsToVolume`) — Splatter to density grid. Resolution / Amount modes for radius.
- **Set Point Radius** (`GeometryNodeSetPointRadius`) — Per-point radius (PointCloud uses radius for rendering as well as some sims).
- **Points of Curve** (`GeometryNodePointsOfCurve`) — Topology query: per curve, which point indices belong to it.

---

## Node Taxonomy — Volume Nodes

- **Volume Cube** (`GeometryNodeVolumeCube`) — Build a density grid from a field on a 3D bounding cube. Density field evaluated per voxel.
- **Distribute Points in Volume** — see above.
- **Mesh to Volume** — see Mesh Operations.
- **Volume to Mesh** (`GeometryNodeVolumeToMesh`) — Surface extract. Threshold + Adaptivity (Adaptive mode) or fixed voxel size.
- **Volume Bounds** — Bounding box and per-axis min/max.
- **Get Named Grid** / **Store Named Grid** (4.4+) — Multi-grid VDB IO inside the graph.

VDB IO directly to/from disk arrived in 4.5 via the **Import VDB** node.

---

## Node Taxonomy — Instance Nodes

The Instance type is **lazy**. One mesh + a million transforms = one mesh in memory plus a transform table.

- **Instance on Points** (`GeometryNodeInstanceOnPoints`) — Place an instance per point. Inputs: Points, Instance (geometry), Pick Instance (bool), Instance Index (int field), Rotation (vec field), Scale (vec field). Workhorse node.
- **Instances to Points** (`GeometryNodeInstancesToPoints`) — Collapse instances back to their pivot points.
- **Realize Instances** (`GeometryNodeRealizeInstances`) — Bake the lazy instances into real geometry. Expensive. Required before any node that needs per-vertex access across instances.
- **Translate Instances** (`GeometryNodeTranslateInstances`) — Per-instance offset.
- **Rotate Instances** (`GeometryNodeRotateInstances`) — Per-instance rotation with pivot + local-space toggle.
- **Scale Instances** (`GeometryNodeScaleInstances`) — Per-instance scale with pivot + local-space.
- **Set Instance Index** — Override which child of an instance collection a point picks (used with Pick Instance on Instance on Points).
- **Instance Bounds** (4.5+) — Per-instance bounding box.

---

## Node Taxonomy — Attribute Nodes

- **Store Named Attribute** (`GeometryNodeStoreNamedAttribute`) — Write a field as a named attribute on a chosen domain. Data type: Float/Int/Vector/Color/Bool/Quaternion (4.2+).
- **Named Attribute** (`GeometryNodeInputNamedAttribute`) — Read a named attribute as a field. Returns Exists boolean alongside the value.
- **Capture Attribute** (`GeometryNodeCaptureAttribute`) — Evaluate a field at this point in the graph on a chosen domain and emit it as an anonymous attribute on the output geometry.
- **Remove Named Attribute** (`GeometryNodeRemoveAttribute`) — Delete a named attribute. Useful pre-export.
- **Attribute Statistic** (`GeometryNodeAttributeStatistic`) — Min/Max/Range/Mean/Median/Sum/Variance/Std-Dev over a domain.
- **Domain Size** (`GeometryNodeAttributeDomainSize`) — Element counts per domain (Mesh: verts/edges/faces/corners; Curve: points/splines; etc.).
- **Blur Attribute** (`GeometryNodeBlurAttribute`) — Diffuse an attribute across neighbors over N iterations. POINT domain on meshes uses edge adjacency.

**Naming conventions:**

- Plain `name` — visible attribute, persists on geometry, shows in mesh data → Attributes panel.
- `.name` (leading dot) — "internal" / hidden attribute. Auto-pruned at export and outside the graph that created it. Use this for graph-internal scratch storage.
- Anonymous attributes (from Capture Attribute) have UUID-style names internally and are pruned aggressively if not referenced downstream.

---

## Node Taxonomy — Geometry Nodes (Generic)

- **Join Geometry** (`GeometryNodeJoinGeometry`) — Concatenate multiple geometries. Preserves type — meshes join to mesh, points join to points, instances join to instances.
- **Bounding Box** (`GeometryNodeBoundBox`) — Min, Max, Bounding Box (mesh) outputs.
- **Convex Hull** (`GeometryNodeConvexHull`) — Mesh hull from points / mesh.
- **Delete Geometry** (`GeometryNodeDeleteGeometry`) — Delete by selection field. Mode: Only Face / Edges & Faces / All. Domain dropdown.
- **Duplicate Elements** (`GeometryNodeDuplicateElements`) — N copies of each selected element. Domain dropdown. Per-element amount field. Returns Duplicate Index field.
- **Geometry Proximity** (`GeometryNodeProximity`) — Nearest distance + position to a target geometry. Per-element. Expensive (BVH per element).
- **Separate Geometry** (`GeometryNodeSeparateGeometry`) — Split by selection field into Selection + Inverted geometries.
- **Transform Geometry** (`GeometryNodeTransform`) — Translate, Rotate, Scale on the whole geometry (not per-element — that's Set Position / Translate Instances).
- **Set Position** (`GeometryNodeSetPosition`) — Move POINT-domain elements. Inputs: Position (replace) and Offset (add). Selection field gates which points move.
- **Set ID** (`GeometryNodeSetID`) — Per-point integer ID. Useful for stable identification through topology changes.
- **Self Object** (`GeometryNodeSelfObject`) — Reference to the object the modifier is on. Use with Object Info to read self's transform.
- **Index of Nearest** (`GeometryNodeIndexOfNearest`) — Per-element nearest-neighbor index within the same geometry.
- **Sample Index** (`GeometryNodeSampleIndex`) — Look up an attribute at a specific element index on another geometry.
- **Sample Nearest** — Index of the nearest element on a target geometry.
- **Sample Nearest Surface** (`GeometryNodeSampleNearestSurface`) — Closest surface point on a target mesh, plus interpolated attribute at that point. Per-element cost.
- **Sample UV Surface** — Sample attributes at a UV coordinate on a target mesh.
- **Sample Curve** (`GeometryNodeSampleCurve`) — Position/Tangent/Normal at a Factor or Length along a target curve.
- **Geometry to Instance** (`GeometryNodeGeometryToInstance`) — Wrap geometry as a single instance.
- **Merge by Distance** — Weld close-by elements. Mode: All / Connected. Distance field.

---

## Node Taxonomy — Material Nodes

- **Set Material** (`GeometryNodeSetMaterial`) — Assign a material to selected faces. Materials slot is a Material datablock.
- **Set Material Index** — Per-face material index (int).
- **Material Index** — Read material index as a field.
- **Material Selection** — Returns boolean field for faces using a given material.
- **Material** — Material datablock socket (input only, used by Set Material).

See [[BLENDER_MATERIALS]] for material assignment semantics on objects with Geometry Nodes.

---

## Node Taxonomy — Utility / Math

- **Math** (`ShaderNodeMath`) — Add/Sub/Mul/Div, Power/Log/Sqrt, Sin/Cos/Tan/Asin/Acos/Atan/Atan2, Floor/Ceil/Round/Truncate/Fract, Modulo/Wrap/Snap/PingPong, Min/Max/Clamp, Compare/Sign/Smooth Min/Smooth Max, Multiply Add, Inverse Sqrt, Exponent. Field-friendly.
- **Vector Math** (`ShaderNodeVectorMath`) — Add/Sub/Mul/Div, Cross/Dot/Project/Reflect/Refract/Faceforward, Distance, Length, Scale, Normalize, Wrap/Snap/Floor/Ceil/Mod/Fraction/Absolute, Min/Max/Sin/Cos/Tan.
- **Boolean Math** (`FunctionNodeBooleanMath`) — AND/OR/NOT/NAND/NOR/XOR/XNOR/IMPLY/NIMPLY.
- **Compare** (`FunctionNodeCompare`) — Less/Greater/Equal with epsilon; Float/Int/Vector/String/Color modes.
- **Float Curve** (`ShaderNodeFloatCurve`) — Hand-drawn 1D curve remap.
- **Color Ramp** (`ShaderNodeValToRGB`) — Float → Color via gradient.
- **Map Range** (`ShaderNodeMapRange`) — Remap range with optional clamp + Linear/Smoothstep/Smootherstep modes.
- **Combine XYZ / Separate XYZ** — Vector ↔ floats.
- **Combine Color / Separate Color** — Color ↔ RGB/HSV/HSL.
- **Switch** (`GeometryNodeSwitch`) — Pick A or B by boolean field. Per-type variants.
- **Mix** (`ShaderNodeMix`) — Uniform mixer for Float/Vector/Color/Rotation (4.0+). Replaces the old type-specific Mix RGB / Mix Vector.
- **Random Value** (`FunctionNodeRandomValue`) — Float/Int/Vector/Bool with Seed + ID. The ID is what makes it stable across re-evaluation.
- **Bit Math** (4.5+) — Bitwise AND/OR/XOR/NOT/shifts on ints.
- **Quaternion / Rotation** — Quaternion (4.3+) is a first-class socket type. Combine/Separate, Rotate Vector, Invert/Multiply.

---

## Node Taxonomy — Input Nodes

- **Position** — POINT-domain vector field. The current element's position.
- **Normal** — Per-FACE (or per-CORNER for smooth shading) normal vector.
- **Radius** — Per-point radius (PointCloud/Curve).
- **ID** — Per-element ID int field.
- **Index** — Element index within its domain.
- **Scene Time** — Two outputs: Seconds and Frame. Drive animated graphs.
- **Frame** — Alias for Scene Time / Frame.
- **Random Value** — see Utility.
- **Active Camera** — Returns the scene's active camera as Object socket.
- **Object Info** (`GeometryNodeObjectInfo`) — Inputs: Object (datablock), As Instance bool. Outputs: Location, Rotation, Scale, Geometry. Transform mode dropdown (Original / Relative).
- **Collection Info** (`GeometryNodeCollectionInfo`) — Inputs: Collection, Separate Children, Reset Children, As Instances. Outputs: Instances.
- **Image Info** (4.0+) — Width, Height, Frame Count for image datablocks.
- **Image Texture** (`GeometryNodeImageTexture`) — Sample an image at a Vector field. Returns Color + Alpha. Works in geometry context (independent of any material).
- **Self Object** — see Generic Geometry.
- **Camera Info** (4.5+) — Camera datablock → projection / focal length / clip range.
- **Viewport Transform** (4.4+) — Read viewport view matrix for camera-relative effects.

---

## Simulation Zones

Simulation zones cache state across **frames**. They're how you build cloth-like, n-body, particle, or any temporally evolving graph.

**Structure:** A Simulation Input node and a Simulation Output node form a paired zone. All nodes between them run once per frame. The output's state is fed back as the input of the next frame. The Input's "Delta Time" output gives `1/fps` per frame.

**State sockets:** Add sockets on the Simulation Input — Geometry, Float, Vector, etc. Each one persists frame-to-frame. The Output sets the new state value.

**Cache:** Auto-cached during playback. Cache lives in the modifier's bake folder (or packed into the `.blend` from 4.3+). Yellow line in the Timeline indicates cached frames.

**Baking:** Object Properties → Geometry Nodes → Bake. Bake-still and bake-animation. Once baked, the simulation reads from disk; the graph itself stops running until invalidated.

**When to use simulation vs animation drivers:**

- Simulation zone — state depends on previous frame's state (springs, momentum, growth, accretion).
- Animation driver / Scene Time — state is a pure function of current time (orbits on rails, parametric animation).
- Driver on modifier input — sparse per-modifier values driven by F-curves.

**Caveats:**

- On scrub backward, the cache plays back; an uncached scrub-forward triggers a re-bake from cache start.
- Simulation zones evaluate CPU-side. Heavy sims can stall playback.
- Cannot nest simulation zones inside simulation zones (single-frame loops only).

---

## Repeat Zones

Repeat zones run a sub-graph **N times in a single evaluation** — not per frame.

**Structure:** A Repeat Input and Repeat Output paired zone with an Iterations int input. State sockets flow from one iteration's output into the next iteration's input.

**Use cases:**

- Recursive subdivision (subdivide → set position → subdivide → ...).
- L-system-style growth — append geometry, then re-iterate on the new tips.
- Iterative refinement — relax positions, smooth normals, redistribute points.
- Multi-pass scattering (place trees, then place rocks around trees).

**Caveats:**

- Compile-time loop. Heavy `Iterations` counts blow up evaluation time linearly (or worse if geometry grows).
- Can't read out per-iteration intermediates — only the final state. Use Bake nodes to inspect, or temporarily set Iterations = N and view.
- Repeat zones cannot reference per-frame state. For per-frame iteration, use Simulation zone.

---

## Bake Nodes and Explicit Baking (4.1+)

A **Bake node** caches the geometry flowing through it at a chosen frame range. Two modes:

- **Bake Still** — One geometry snapshot, reused on every frame.
- **Bake Animation** — Per-frame snapshots, played back by frame.

**Workflow:**

1. Drop a Bake node inline.
2. Set mode + frame range in the node properties.
3. Press Bake on the node or via the Manage Bakes panel on the modifier.
4. Subsequent evaluations skip everything upstream of the Bake node — they read from disk (or from `.blend` if packed, 4.3+).

**Why bake explicitly (vs simulation auto-cache):**

- Heavy distribution + subdivision graphs that don't change frame to frame.
- Imported VDB or OBJ where you want to lock the geometry without re-reading from disk every eval.
- Mid-graph checkpoints for fast tweaking downstream.

**Manage Bakes panel:** Modifier UI lists every bake on the modifier with size, frame range, and explicit Bake / Free buttons.

---

## For Each Element Zone (4.3+)

The **For Each Geometry Element** zone iterates explicitly over each element of an input geometry, runs an inner graph per element, and joins the per-element outputs.

**Structure:** A For Each Element Input + Output zone pair. Inside the zone, every field resolves to the value at the current element's index. Outputs in the Generated panel (Geometry default, plus any custom) are joined across all iterations.

**When to use:**

- Per-element work that produces *new geometry* of varying size (you can't vectorize "make a different-sized cube per face").
- Per-element branching that field math can't express (each element runs entirely different node paths via switches).
- Per-instance custom transforms that require reading multi-step element-local state.

**When NOT to use:**

- Anything a field on a domain can express. The for-each path is far slower than vectorized field evaluation for the same math.
- Per-frame state (use Simulation zone).
- Fixed-count iteration (use Repeat zone).

**Heuristic:** if the work can be written as `result = f(per_element_inputs)` where `f` is a math expression on fields, use fields. If the work requires a "different mesh / different subgraph per element," use For Each.

---

## Group Input / Group Output / Sockets

A Geometry Nodes graph is a NodeGroup with a defined **interface** — the sockets that appear on the modifier UI. These are declared via the `tree.interface` API (4.0+).

**Interface items** can be:

- Sockets (`NodeTreeInterfaceSocket`) — typed inputs/outputs.
- Panels (`NodeTreeInterfacePanel`) — collapsible groups of sockets in the modifier UI.

**Socket types:**

- `NodeSocketGeometry` — Geometry.
- `NodeSocketFloat` — Float (subtypes: NONE, DISTANCE, ANGLE, FACTOR, PERCENTAGE, TIME, WAVELENGTH).
- `NodeSocketInt` — Int (subtypes: NONE, UNSIGNED, PERCENTAGE, FACTOR).
- `NodeSocketVector` — Vector (subtypes: NONE, TRANSLATION, DIRECTION, VELOCITY, ACCELERATION, EULER, XYZ).
- `NodeSocketColor` — RGBA.
- `NodeSocketBool` — Bool.
- `NodeSocketRotation` — Quaternion (4.3+).
- `NodeSocketString` — String.
- `NodeSocketObject`, `NodeSocketCollection`, `NodeSocketMaterial`, `NodeSocketImage`, `NodeSocketTexture` — datablock pickers.
- `NodeSocketMenu` (4.1+) — Dropdown.

**Defaults, min, max, subtype** are set on the interface socket, not on the Group Input node's internal output.

**Example — add a Float input with bounds:**

```python
tree = bpy.data.node_groups.new("MyGraph", 'GeometryNodeTree')
geo_in  = tree.interface.new_socket(name="Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
geo_out = tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
amount  = tree.interface.new_socket(name="Amount",   in_out='INPUT',  socket_type='NodeSocketFloat')
amount.default_value = 0.5
amount.min_value = 0.0
amount.max_value = 1.0
amount.subtype = 'FACTOR'
```

`tree.interface.items_tree` is the flat collection of all interface items.

---

## The Modifier ↔ Node Tree Relationship

The Geometry Nodes modifier (`type='NODES'`) holds:

- `node_group` — pointer to a NodeGroup datablock in `bpy.data.node_groups`.
- A per-modifier dict of values for each exposed input socket.
- Bake settings (frame range, bake target).

**One NodeGroup can power many modifiers.** Edit the NodeGroup once; every modifier referencing it updates.

**Per-modifier values are addressed by socket identifier** (not by name — the identifier is stable across renames). In Python:

```python
mod = obj.modifiers["GeometryNodes"]
# Read the input identifier
input_id = mod.node_group.interface.items_tree["Amount"].identifier
mod[input_id] = 0.75
mod[input_id + "_attribute_name"] = "my_attr"   # for field inputs driven by attributes
mod[input_id + "_use_attribute"] = True
```

For a field input on the modifier, the user can switch between "value" and "attribute" mode — driven by `<id>_use_attribute` bool + `<id>_attribute_name` string sibling properties.

**Renaming / duplicating:**

- Renaming the modifier doesn't touch the NodeGroup.
- Duplicating an object copies the modifier; the NodeGroup is shared by default.
- `node_group.copy()` or modifier-context "Make Single User" forks the NodeGroup.

**Library override** — linked NodeGroups from a library can be overridden per-input value but not per-graph-structure.

---

## Common Procedural Patterns

### 1. Scatter mesh on surface

```
[Object Info: target mesh] →
[Distribute Points on Faces (Density, Seed)] →
[Instance on Points (Instance: cube/asset, Rotation: from Normal field, Scale: Random Value)] →
[Output]
```

Distribute outputs `Normal` and `Rotation` fields; pipe `Rotation` into Instance on Points for surface-aligned scatter.

### 2. Recursive subdivision with falloff

```
[Mesh In] →
[Repeat Input (Iterations=4) →
  [Subdivide Mesh (Selection = Distance(Position, Vec(0,0,0)) < falloff_radius)] →
[Repeat Output]
] → [Output]
```

Each iteration subdivides only the central faces, producing a falloff in tessellation density.

### 3. Animated noise displacement

```
[Mesh In] →
[Set Position
  Offset = Vec(0,0, NoiseTexture(Position + Vec(0,0,SceneTime.Seconds * speed))) * amplitude
] → [Output]
```

`Scene Time → Seconds` plus `Position` → 4D noise via XYZ + time offset. Cheap, real-time.

### 4. Audio / driver-baked attribute drive

Concept: Bake an F-curve (audio amplitude or driver result) into a named float attribute on the object — typically captured at frame time via Scripted Driver → custom property → store as `.audio_level` attribute. Then in the graph:

```
[Mesh In] →
[Named Attribute "audio_level" (Float)] → A
A → [Set Position offset = Normal * A * gain] →
[Output]
```

Brand-agnostic placeholder — the source of the bake is whatever signal your project drives off-graph.

### 5. Voronoi shatter into instances

```
[Source Mesh] →
[Capture Attribute (FACE, Int)
  input = Voronoi Texture(Position).Distance binned to int via Math floor
] →
[For Each Element (FACE) — or Repeat zone over bins] →
  [Separate Geometry (Selection = captured == current_bin)] →
  [Geometry to Instance] →
[Output: Join Geometry]
```

Captured Voronoi index becomes the shard ID. Each shard becomes an independent instance for per-shard animation.

### 6. Curve-driven sweep

```
[Curve In: spine] →
[Resample Curve (Length, 0.05)] →
[Set Curve Tilt (per-point twist field)] →
[Curve to Mesh (Profile = Curve Circle(radius=0.1), Fill Caps=True)] →
[Output]
```

The workhorse for cables, pipes, tubes, ribbons.

### 7. Boolean cutter

```
[Primary Mesh] → A
[Tool Mesh] → B
[Mesh Boolean (Operation = Difference, Solver = Exact)
  Mesh 1 = A
  Mesh 2 = B
] → [Output]
```

`Solver = Exact` for robustness; `Fast` for speed (will misbehave on coplanar / degenerate cases).

### 8. Instance count by camera distance (LOD)

```
[Distribute Points on Faces (Density = 50)] →
[Capture Attribute (POINT, Vec): captured_pos = Position] →
[Set Position
  Selection = Distance(captured_pos, ObjectInfo(ActiveCamera).Location) > cull_dist
  Position = Vec(0,0,-9999)   # banish; or use Delete Geometry instead
] →
[Instance on Points
  Instance Index = Switch(near_test, hi_lod_idx, lo_lod_idx)
  with collection of LODs picked via Pick Instance
] → [Output]
```

In 4.5 you'd use the new **Camera Info** node and proper culling rather than the banish trick.

### 9. L-system-like recursive growth

```
[Initial Point] →
[Repeat (Iterations=N)
  → [Instance on Points (Instance = "branch segment")] →
  → [Realize Instances]   # required to query tips of the new geometry
  → [Mesh to Points (selection = tip vertices)] →
  → loop back into Instance on Points
] → [Output]
```

Each iteration grows segments at the previous iteration's tips. Beware: `Realize` inside a Repeat zone is expensive; cap Iterations.

### 10. Cloth-like simulation

```
[Mesh In] →
[Simulation Input (state: Geometry, Velocity[Vec])] →
[Set Position
  Offset = Velocity * Delta Time
] →
  pin selected verts (e.g. boundary) — Switch(selection, Position, captured_initial)
  Velocity = Velocity + (gravity + spring_force_from_neighbors) * Delta Time
[Simulation Output (Geometry, Velocity)] → [Output]
```

For real cloth use the dedicated Cloth modifier — this pattern is the structural reference for any spring-mass-damper sim done in nodes.

### 11. Volumetric flow trail

```
[Emitter Mesh] →
[Mesh to Volume (voxel size = 0.05)] →
[Distribute Points in Volume (Density)] →
[Set Position
  Offset = NoiseTexture(Position * scale + SceneTime.Seconds * flow) * step
] →
[Instance on Points (Instance = sprite quad)] →
[Output]
```

Use a Simulation zone wrapping the Set Position step if you want trails (state carries position from frame N-1).

---

## The bpy API Surface for Geometry Nodes

### Accessing the tree

```python
import bpy
obj = bpy.data.objects["Cube"]

# Add a Geometry Nodes modifier and create an empty tree
mod = obj.modifiers.new(name="GeometryNodes", type='NODES')
tree = bpy.data.node_groups.new("MyGraph", 'GeometryNodeTree')
mod.node_group = tree

# Or grab existing:
tree = mod.node_group
```

### Declaring the interface (4.0+)

```python
tree.interface.new_socket(name="Geometry", in_out='INPUT',  socket_type='NodeSocketGeometry')
tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
```

### Group I/O nodes

```python
gi = tree.nodes.new("NodeGroupInput")
go = tree.nodes.new("NodeGroupOutput")
gi.location = (-400, 0)
go.location = ( 400, 0)
```

### Creating and linking nodes

```python
set_pos = tree.nodes.new("GeometryNodeSetPosition")
set_pos.location = (0, 0)

tree.links.new(gi.outputs["Geometry"], set_pos.inputs["Geometry"])
tree.links.new(set_pos.outputs["Geometry"], go.inputs["Geometry"])
```

### Reading/writing socket defaults

```python
# A literal-value default on a node's input socket:
noise = tree.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 5.0

# An interface default (the default shown to the user on the modifier):
amt = tree.interface.items_tree["Amount"]
amt.default_value = 0.5
amt.min_value = 0.0
amt.max_value = 1.0
```

### Difference: socket default vs modifier input value

- **Socket default** on an inner node — used only when nothing is connected to that socket.
- **Interface default** on a group input — the value the modifier shows initially when first added.
- **Modifier value** (`mod[input_id]`) — the actual per-modifier override the user has set. Independent of the interface default.

### Common node `type=` strings

| Node | `bl_idname` |
|------|-------------|
| Group Input | `NodeGroupInput` |
| Group Output | `NodeGroupOutput` |
| Set Position | `GeometryNodeSetPosition` |
| Set Material | `GeometryNodeSetMaterial` |
| Set Material Index | `GeometryNodeSetMaterialIndex` |
| Set ID | `GeometryNodeSetID` |
| Set Point Radius | `GeometryNodeSetPointRadius` |
| Position (input) | `GeometryNodeInputPosition` |
| Normal (input) | `GeometryNodeInputNormal` |
| Index (input) | `GeometryNodeInputIndex` |
| ID (input) | `GeometryNodeInputID` |
| Scene Time | `GeometryNodeInputSceneTime` |
| Random Value | `FunctionNodeRandomValue` |
| Math | `ShaderNodeMath` |
| Vector Math | `ShaderNodeVectorMath` |
| Mix | `ShaderNodeMix` |
| Map Range | `ShaderNodeMapRange` |
| Switch | `GeometryNodeSwitch` |
| Compare | `FunctionNodeCompare` |
| Combine XYZ | `ShaderNodeCombineXYZ` |
| Separate XYZ | `ShaderNodeSeparateXYZ` |
| Cube | `GeometryNodeMeshCube` |
| UV Sphere | `GeometryNodeMeshUVSphere` |
| Ico Sphere | `GeometryNodeMeshIcoSphere` |
| Grid | `GeometryNodeMeshGrid` |
| Cylinder | `GeometryNodeMeshCylinder` |
| Curve Line | `GeometryNodeCurvePrimitiveLine` |
| Curve Circle | `GeometryNodeCurvePrimitiveCircle` |
| Curve to Mesh | `GeometryNodeCurveToMesh` |
| Resample Curve | `GeometryNodeResampleCurve` |
| Subdivide Mesh | `GeometryNodeSubdivideMesh` |
| Subdivision Surface | `GeometryNodeSubdivisionSurface` |
| Triangulate | `GeometryNodeTriangulate` |
| Mesh Boolean | `GeometryNodeMeshBoolean` |
| Distribute Points on Faces | `GeometryNodeDistributePointsOnFaces` |
| Distribute Points in Volume | `GeometryNodeDistributePointsInVolume` |
| Points | `GeometryNodePoints` |
| Mesh to Points | `GeometryNodeMeshToPoints` |
| Mesh to Curve | `GeometryNodeMeshToCurve` |
| Mesh to Volume | `GeometryNodeMeshToVolume` |
| Volume to Mesh | `GeometryNodeVolumeToMesh` |
| Instance on Points | `GeometryNodeInstanceOnPoints` |
| Realize Instances | `GeometryNodeRealizeInstances` |
| Translate Instances | `GeometryNodeTranslateInstances` |
| Rotate Instances | `GeometryNodeRotateInstances` |
| Scale Instances | `GeometryNodeScaleInstances` |
| Object Info | `GeometryNodeObjectInfo` |
| Collection Info | `GeometryNodeCollectionInfo` |
| Self Object | `GeometryNodeSelfObject` |
| Join Geometry | `GeometryNodeJoinGeometry` |
| Transform Geometry | `GeometryNodeTransform` |
| Bounding Box | `GeometryNodeBoundBox` |
| Convex Hull | `GeometryNodeConvexHull` |
| Delete Geometry | `GeometryNodeDeleteGeometry` |
| Separate Geometry | `GeometryNodeSeparateGeometry` |
| Duplicate Elements | `GeometryNodeDuplicateElements` |
| Geometry Proximity | `GeometryNodeProximity` |
| Sample Index | `GeometryNodeSampleIndex` |
| Sample Nearest | `GeometryNodeSampleNearest` |
| Sample Nearest Surface | `GeometryNodeSampleNearestSurface` |
| Sample UV Surface | `GeometryNodeSampleUVSurface` |
| Sample Curve | `GeometryNodeSampleCurve` |
| Capture Attribute | `GeometryNodeCaptureAttribute` |
| Store Named Attribute | `GeometryNodeStoreNamedAttribute` |
| Named Attribute (read) | `GeometryNodeInputNamedAttribute` |
| Remove Named Attribute | `GeometryNodeRemoveAttribute` |
| Attribute Statistic | `GeometryNodeAttributeStatistic` |
| Domain Size | `GeometryNodeAttributeDomainSize` |
| Blur Attribute | `GeometryNodeBlurAttribute` |
| Noise Texture | `ShaderNodeTexNoise` |
| Voronoi Texture | `ShaderNodeTexVoronoi` |
| Image Texture | `GeometryNodeImageTexture` |
| Simulation Input | `GeometryNodeSimulationInput` |
| Simulation Output | `GeometryNodeSimulationOutput` |
| Repeat Input | `GeometryNodeRepeatInput` |
| Repeat Output | `GeometryNodeRepeatOutput` |
| For Each Element Input | `GeometryNodeForeachGeometryElementInput` |
| For Each Element Output | `GeometryNodeForeachGeometryElementOutput` |
| Bake | `GeometryNodeBake` |

> Verify any unfamiliar string by creating the node interactively, then `node.bl_idname` in the Python console. Names occasionally rename between major releases.

### Iterating and removing

```python
for n in tree.nodes:
    print(n.bl_idname, n.name, n.location)

tree.nodes.remove(tree.nodes["Set Position"])

# Disconnect a specific link:
for lk in list(tree.links):
    if lk.from_node == some_node:
        tree.links.remove(lk)
```

### Reading the result of a graph

The evaluated geometry sits on `obj.evaluated_get(depsgraph).data`:

```python
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = obj.evaluated_get(depsgraph)
eval_mesh = eval_obj.data   # post-modifier mesh, including geo-nodes output
```

See [[BLENDER_PYTHON_API]] for full depsgraph semantics.

---

## Performance Notes

- **Realize Instances** — collapses N instances into N copies of full mesh data. Memory explodes; runtime explodes. Place as late as possible in the graph; ideally never (instances export to Cycles/EEVEE natively).
- **Mesh Boolean (Exact)** — robust but slow on large meshes. Fast solver is ~10x faster but fails on coplanar / degenerate input. Prefer pre-processing (remesh / weld / decimate the tool mesh) over fighting Boolean cost.
- **Volume conversions** — `Mesh to Volume` and `Volume to Mesh` scale with `1/voxel_size^3`. Voxel size 0.05 on a 1m mesh = ~8000 voxels worth of work; voxel size 0.01 = 1,000,000. Tune voxel size first, everything else second.
- **Sample Nearest / Sample Nearest Surface** — builds a BVH on the target, queries per element. Linear in source × log(target). Cache target geometry with a Bake node when reused.
- **Geometry Proximity** — same family as Sample Nearest. Per-element BVH query.
- **Subdivision Surface** — Catmull-Clark is quadratic per level. Level 3 is fine; Level 6 is regret.
- **For Each Element zone** — slower than vectorized fields for the same math. Always check whether a field can do it before reaching for the zone.
- **Repeat zone** — runtime is `iterations × inner-cost`. Watch for geometry growth inside the loop — N iterations of doubling = `2^N`.
- **Simulation zone** — CPU-only (no GPU sim path as of 4.5). Heavy sims stall playback. Bake explicitly to disk for smooth review.
- **Apple Silicon (M1/M2/M3):** Geometry Nodes evaluation runs CPU-side on all current Blender versions; simulation zones don't see GPU acceleration. Expect linear scaling with cores. Metal acceleration on the M-series targets rendering (Cycles / EEVEE), not graph eval.
- **Anonymous attribute lifetime** — attributes from Capture Attribute are pruned aggressively if no downstream consumer references them. Memory friendly; can be confusing when debugging via Spreadsheet (the attribute "vanishes").

---

## Common Footguns

1. **Field on the wrong domain.** Capturing on FACE then consuming on POINT silently auto-interpolates. Either match domains or accept the interpolation. Always set Capture Attribute's Domain dropdown explicitly.
2. **Selection input defaults to True when unconnected.** Most `Set …` nodes operate on all elements by default. To gate, you must connect a boolean field — passing `False` literally (constant False) results in *no* effect, easy to forget.
3. **`Set Position` writes only POINT.** A face-domain field plugged into Offset will average to vertices. Use `Translate Instances` for instance-domain transforms, never `Set Position`.
4. **Edit type is internal-only.** You cannot create or pass around Edit-geometry sockets; it appears only inside specific edit-mode nodes (Mesh Edit Mode integration). Treat as black-box.
5. **Renaming a NodeGroup vs renaming a modifier.** `mod.name = "X"` does not rename the NodeGroup. The dropdown in the modifier panel uses the NodeGroup name. To rename what users see in the dropdown, rename `mod.node_group.name`.
6. **One NodeGroup → many modifiers.** Editing the graph in one modifier edits *all* modifiers using that NodeGroup. To fork, `node_group.copy()` or use Make Single User.
7. **Circular modifier references.** Object A's Geometry Nodes reads Object B via Object Info; B's Geometry Nodes reads A. Depsgraph will refuse and stall evaluation. Break the cycle.
8. **`.attribute_name` modifier inputs.** A field input on a modifier has three properties: `mod[id]` (value), `mod[id + "_use_attribute"]` (bool), `mod[id + "_attribute_name"]` (str). Setting only `_attribute_name` without `_use_attribute=True` silently uses the value, not the attribute.
9. **Anonymous attribute pruning.** If you Capture an attribute, then don't read it downstream of a node that requires it, it's optimized away. Force materialization via a Store Named Attribute or by connecting it into a viewer / spreadsheet.
10. **Socket type mismatch silently defaults to 0.** Plugging an Int into a Vector socket converts each int to a vec3 of that value. Plugging a Vector into a Float socket takes `.x` only on some node families, average on others. Verify in Spreadsheet.
11. **Mesh attributes vs Geometry-Nodes attributes.** Attributes you write via Store Named Attribute on a Geometry Nodes modifier are *not* part of the mesh datablock — they live only in the evaluated geometry. To persist them on the mesh, apply the modifier or use the "Realize Instances" + bake path.
12. **`Realize Instances` resets transforms.** After Realize, the instance transforms have been baked into vertex positions. Any downstream node that wanted the instance's transform separately is out of luck.
13. **Material Index domain.** Material Index is FACE-domain. Setting it on POINT via Store Named Attribute does nothing visible.
14. **Subdivide Mesh vs Subdivision Surface.** Subdivide Mesh is linear (no smoothing). Subdivision Surface is Catmull-Clark (smooths). Using Subdivide when you wanted smoothing produces flat, faceted output.
15. **Curve Resampling with Length on a closed loop.** `Resample Curve` in Length mode on a cyclic spline may snap the join — explicitly re-set `Set Spline Cyclic` after resampling if you need a clean loop.
16. **Internal attribute prefix.** Attributes named `.foo` are hidden from the Attributes panel and pruned on export. Useful for scratch storage, surprising the first time you can't find one.
17. **Mix node 4.0+ vs old Mix RGB.** Old .blends may load with deprecated Mix RGB nodes; new graphs should use the unified Mix (which auto-types Float/Vector/Color/Rotation).
18. **Bake node path conflicts.** Two Bake nodes with the same identifier inside the same modifier collide on disk. Rename one if you copy-paste.

---

## Cross-references

- [[BLENDER_PYTHON_API]] — bpy entry points, depsgraph, evaluated_get patterns.
- [[BLENDER_DATA_MODEL]] — `bpy.data` collections, datablock lifecycle, modifier stack.
- [[BLENDER_SHADER_NODES]] — shader-node equivalents (Math, Vector Math, texture nodes shared between contexts).
- [[BLENDER_MATERIALS]] — Set Material semantics, slot ordering.
- [[BLENDER_PATTERNS_PROCEDURAL]] — ready-to-paste recipes that build on this catalog.
