---
title: Procedural Patterns — Recipes for Generative Geometry
version: 1.0
last_updated: 2026-05-22
status: live
scope: Paste-ready recipes for procedural geometry generation — scatter, instancing, recursive growth, organic form, voronoi/fracture, displacement, generative environments. Built on Geometry Nodes, shader procedurals, and modifier stacks. The "what to assemble" layer; the "how each node works" layer lives in BLENDER_GEOMETRY_NODES.md.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_GEOMETRY_NODES.md, BLENDER_SHADER_NODES.md, BLENDER_MODELING.md
---

# PROCEDURAL PATTERNS — RECIPES FOR GENERATIVE GEOMETRY

This is a **recipe library**. Each entry is a paste-ready combination of nodes and modifiers that builds a specific procedural result — a scatter, an instance array, a fractal, a landscape, a procedural material. The agent's workflow is **find the closest recipe → diff against it** (add one node, change one param, swap one input) rather than building from scratch.

This file is the *what to assemble* layer. The *how each node works* layer lives in [[BLENDER_GEOMETRY_NODES]] for Geometry Nodes and [[BLENDER_SHADER_NODES]] for shader nodes. Modifier-level operations live in [[BLENDER_MODELING]]. When a recipe says "Distribute Points on Faces," the contract of that node is documented elsewhere — this file says *which combination of nodes builds a forest*.

The structure mirrors TouchDesigner's reference-network approach in `TD_PATTERNS_*.md`: a curated set of canonical patterns, each parameterized, each diff-able. A new request rarely needs a new pattern — it almost always wants Recipe N with one altered slider.

**Core facts:**

- A typical Geometry Nodes recipe uses **5–20 nodes**. Anything past ~30 nodes is a candidate for splitting into NodeGroups.
- Most scatter recipes share the same **Distribute Points on Faces → Instance on Points** backbone. The variants differ only in what feeds density, scale, and rotation.
- **Modifier stacks layer on top of GN.** A common stack is `Subdivision Surface → Geometry Nodes (scatter/displace) → Bevel → Solidify → Wireframe`. Order matters — GN evaluates on the geometry that arrives at its slot, not the raw mesh.
- **Shader procedurals are independent of geometry procedurals.** A flat plane with a 5-node shader graph can read as carved wood. A 30-node GN recipe with no material reads as gray clay. The two layers compose freely.
- **Instances vs Realize is the central performance tradeoff.** A million instances of the same mesh cost roughly one mesh's worth of memory. `Realize Instances` collapses them into one big mesh — proportional cost, but required before some operations (Boolean, Bake, Wireframe).
- **Recipes become reusable via the NodeGroup interface.** Wrap a recipe in a group, expose 5–10 sliders via `tree.interface`, and the same recipe drops onto any object via a Geometry Nodes modifier.
- **Repeat zones** (4.0+) are how recursion enters Geometry Nodes — at compile time, not per frame. They unroll N iterations of a sub-graph deterministically.
- **Simulation zones** (4.0+) carry state across frames. Most "growth," "flock," and "drift" recipes live in simulation zones.
- **Bake nodes** (4.1+) cache a point in the graph so downstream changes do not re-cook the heavy upstream. Use this on any recipe whose first half is expensive.
- **Voronoi is fast in Geometry Nodes, slower in Shader nodes.** If a recipe needs voronoi-driven displacement, capture it on geometry rather than reading it in the shader.
- **W (4th coord) of noise textures = time.** Wire `Scene Time → Seconds → W` and a static noise becomes animated without re-sampling at higher dimension.
- **The same backbone serves many recipes.** Scatter-on-surface is one backbone. Sample-on-curve is another. Sphere + Set Position is another. Most of this file is variations on those three.

---

## Recipe Format — Read This First

Every recipe in this file follows the same five-field convention. Use this format when adding new recipes.

- **Use:** one sentence — when to reach for this recipe.
- **Build:** the node chain or modifier stack as a numbered list. Node names match the Blender 4.5 menu names exactly.
- **Params:** the key sliders to expose on the NodeGroup interface (the modifier panel) or material — the user-facing surface.
- **Variations:** 1–3 alternative configurations of the same backbone — "swap node X for Y, change input Z."
- **Performance notes:** cost considerations on M1 — what's cheap, what's expensive, what to bake.

Recipes are written as if pasted into a fresh Geometry Nodes modifier on a host object (unless noted otherwise — e.g. shader recipes go into a Material).

---

## Scatter Recipes

The scatter backbone is **Distribute Points on Faces → Instance on Points**. Almost every "forest of X" recipe in production work is a variant of this with different inputs for density, scale, rotation, and the asset to instance.

### Scatter on Surface (the backbone)

**Use:** scatter any asset (foliage, rocks, props, debris) across a host mesh's surface with random transform variation.

**Build:**

1. `Group Input` → exposes `Asset` (Object/Collection), `Density`, `Seed`, `Scale Min`, `Scale Max`.
2. `Group Input.Geometry` → `Distribute Points on Faces` (Random mode).
3. `Distribute Points on Faces.Points` → `Instance on Points.Points`.
4. `Object Info` (or `Collection Info`) → `Instance on Points.Instance`. Set `Collection Info → Separate Children` if scattering from a collection of varied assets.
5. `Random Value` (Float, Min/Max from group inputs, ID = Index) → `Scale Instances.Scale`.
6. `Random Value` (Vector, range `(0,0,0) → (0,0,2π)`) → `Rotate Instances.Rotation`.
7. `Set Material` → output → `Group Output.Geometry`.

**Params:** `Density` (0–1000 / m²), `Seed` (int), `Scale Min/Max`, `Tilt Range` (0–π/4), `Asset` (Object or Collection).

**Variations:**

- **Density-mask scatter** (see next recipe).
- **Slope-aware scatter** (see further below).
- **Multi-asset:** replace `Object Info` with `Collection Info → Separate Children = True`, then use `Random Value (Int)` into `Instance on Points.Pick Instance` index to choose per-point.

**Performance notes:** lazy as long as instances stay un-realized. A million instances on M1 is fine to view; previewing in Cycles requires Persistent Data on or expect long re-builds. Avoid `Realize Instances` before render.

### Density-Mask Scatter

**Use:** restrict scatter to a painted region — keep density high in painted areas, zero elsewhere.

**Build:**

1. On the host mesh, create a vertex group `density_mask` and paint it in Weight Paint mode (0–1).
2. In GN: `Named Attribute` (Float, name = `density_mask`, domain = Point).
3. `Group Input.Density` → `Math (Multiply) → Named Attribute` → `Distribute Points on Faces.Density Factor`.
4. Continue with backbone (steps 3–7 of Scatter on Surface).

**Params:** `Density` (scalar multiplier), `Mask Attribute Name` (string, default `density_mask`).

**Variations:**

- **Texture-mask scatter:** replace `Named Attribute` with `Image Texture` sampled via UV — useful when the mask is authored as a 2D texture rather than painted weights.
- **Inverted mask:** wire through `Math (Subtract, 1.0 - value)` for "anything but the painted area."
- **Multi-layer mask:** combine two vertex groups via `Math (Maximum)` or `Math (Multiply)` for AND-style intersection.

**Performance notes:** the multiplier runs per face during scatter; cost is in the scatter, not the mask read. Free.

### Slope-Aware Scatter

**Use:** scatter only on level ground — trees do not grow on cliff faces, snow accumulates on shallow slopes.

**Build:**

1. Backbone steps 1–2.
2. `Normal` (face domain) → `Separate XYZ.Z` → `Compare (Greater Than)` with threshold (e.g. 0.7 = ~45° from up).
3. `Compare` output → `Math (Multiply)` with `Group Input.Density` → `Distribute Points on Faces.Density Factor`.
4. Continue with backbone.

**Params:** `Slope Threshold` (0–1, dot product with up vector), `Density`, asset inputs.

**Variations:**

- **Inverted (cliff-only):** swap `Greater Than` for `Less Than`.
- **Smooth falloff:** replace binary `Compare` with `Map Range (Linear)` mapped over [low, high] of `Normal.Z` — gives a soft band instead of a hard cutoff.
- **Slope-driven scale:** also wire `Normal.Z` into `Scale Instances` — smaller things on steeper ground.

**Performance notes:** same cost as backbone — the dot product per face is free.

### Even-Spacing Scatter (Poisson Disk)

**Use:** natural-looking distribution where no two points are closer than a minimum distance. Avoids the visible clusters of pure-random scatter.

**Build:**

1. `Distribute Points on Faces` → set mode to **Poisson Disk**.
2. Expose `Distance Min` (the minimum spacing), `Density Max` (upper-bound cap).
3. Backbone steps 3–7 as before.

**Params:** `Distance Min` (m), `Density Max` (per m²), `Seed`, scale/rotation ranges.

**Variations:**

- **Hexagonal-feeling lattice:** push `Density Max` high and `Distance Min` close to the resulting average spacing — Poisson hits its packing limit.
- **Stratified jitter:** combine Poisson scatter with a tiny `Set Position` jitter via `Random Value (Vector)` → `Translate Instances` for organic variance.

**Performance notes:** Poisson is more expensive than Random — roughly 2–5× slower on dense scatters. Still cheap at <100k points.

---

## Instancing Recipes

Instancing patterns where the *placement geometry* is something other than a surface — a curve, a recursive subdivision, or a procedural rule.

### Array Along Curve

**Use:** evenly-spaced or curve-parameter-spaced instances following a curve — fence posts, vertebrae, beads on a string, lights along a path.

**Build:**

1. `Group Input.Curve` → `Resample Curve` (Count = N or Length = L).
2. `Resample Curve` → `Instance on Points.Points`.
3. `Object Info` (the asset) → `Instance on Points.Instance`.
4. `Curve Tangent` → `Align Rotation to Vector (Axis = X, Pivot = Z)` → `Rotate Instances.Rotation` (instances align to curve direction).
5. Optional: `Spline Parameter.Factor` (0–1 along curve) → `Map Range` → `Scale Instances` (taper from one end to the other).

**Params:** `Count` (int) or `Spacing` (m), `Asset`, `Tangent Align` (bool), `Scale Start`, `Scale End`.

**Variations:**

- **Twist along curve:** add `Spline Parameter.Factor` → `Map Range (0 → 2π)` → `Combine XYZ (0,0,θ)` → `Rotate Instances` for a screw/helix.
- **Density along curve via attribute:** paint a weight along the curve handles and wire into `Resample Curve.Count` via `Sample Curve` for variable spacing.
- **End-cap pattern:** use `Index` + `Compare` to pick which point gets the asset, others get nothing — beads with special end pieces.

**Performance notes:** curves cap out fast — even a million-point curve cooks in milliseconds. Cost lives in the instances downstream.

### Recursive Subdivision Instances

**Use:** organic recursive structures — trees, lightning bolts, neuron-style branching where each pass subdivides and re-instances.

**Build:**

1. `Group Input.Geometry` (start mesh — typically a single edge or small mesh) → `Repeat Input.Geometry`.
2. Inside Repeat: `Subdivide Mesh (Cuts=1)` → `Extrude Mesh` along normal with `Random Value` offset → `Scale Elements (Factor < 1)` per branch.
3. Optionally: `Distribute Points on Faces` on the new geometry → `Instance on Points` of a smaller copy.
4. Repeat output → next iteration. Set iteration count on the Repeat zone (e.g. 4–6).
5. After Repeat: `Realize Instances` (only if downstream needs real geometry).

**Params:** `Iterations` (int, 2–8), `Scale per Iteration` (0.4–0.8), `Branch Offset Random`, `Seed`.

**Variations:**

- **L-system feel:** at each iteration, instance multiple copies rotated around the parent's tangent (e.g. 3 rotated by 120°).
- **Per-iteration material:** use the Repeat Index as a Named Attribute, sample it in the shader for younger/older branches.

**Performance notes:** exponential growth in geometry — 6 iterations of 3 branches each = 729 leaves. Always work in instance space inside the loop; `Realize` only at the end if you must.

### Camera-Distance LOD Instancing

**Use:** swap high-detail instances for low-detail ones based on camera distance. Lets a scene hold 100k visible instances by keeping most at proxy detail.

**Build:**

1. `Object Info` of the active camera (or any reference object) → `Position` output.
2. Per-point `Position` minus camera position → `Vector Length` = distance.
3. `Compare (Less Than)` with threshold (e.g. 20 m) → boolean per point.
4. `Switch (Instance)` with True/False inputs from `Object Info (high)` and `Object Info (low)` → `Instance on Points.Instance`.

**Params:** `LOD Distance` (m), `High Detail Asset`, `Low Detail Asset`, `Camera` (object input).

**Variations:**

- **3-tier LOD:** chain two `Switch` nodes for near / mid / far.
- **Cull at distance:** wire `Compare (Greater Than)` to `Delete Geometry` on the points before instancing — cheaper than rendering far instances at all.
- **Fade-in via scale:** use `Map Range (clamped)` from distance to scale, so far instances shrink to zero rather than popping.

**Performance notes:** the swap is per-point, evaluated once per cook. Negligible cost — the savings come from drawing fewer high-detail meshes.

### Procedural Drift (Boid-Feel) Instances

**Use:** instances that drift, flock, or swarm without using Blender's particle-system boids — purely Geometry-Nodes simulation.

**Build:**

1. `Simulation Input.Geometry` carries a point cloud with a `velocity` attribute.
2. Inside zone: read each point's position, sample a 4D noise (W = `Scene Time`) at that position → get a vector offset.
3. Add a small attractor pull: `Position - Target Object Position` → normalize → multiply small → subtract from velocity.
4. Add a separation term: `Index of Nearest` + `Position` delta → push away if within radius.
5. New velocity → `Set Position` (offset) and store back into the `velocity` attribute via `Store Named Attribute`.
6. `Simulation Output.Geometry` → `Instance on Points` of a small asset, aligned to `velocity` direction.

**Params:** `Cohesion`, `Separation Radius`, `Noise Amplitude`, `Noise Scale`, `Target Object`.

**Variations:**

- **Pure-noise drift (no flocking):** drop the separation and cohesion terms — just velocity = noise(position + time). Cheapest version, works for fish, sparks, dust.
- **Wind field:** add a constant vector to velocity, optionally modulated by a texture for spatial variation.
- **Bounded volume:** add a position-clamp term that pushes points back inside a bounding box.

**Performance notes:** simulation zones cook every frame and are **CPU-only on Apple Silicon**. Keep point counts under ~50k for real-time playback. Bake the sim once happy.

---

## Recursive / Fractal Recipes

Self-similar structures built via Repeat zones. Each pass scales down and re-applies the same operation.

### L-System-Like Growth

**Use:** branching plant-like structures where each iteration scatters smaller copies on the previous result.

**Build:**

1. Start with a small seed mesh (a stem cube or an upright edge).
2. `Repeat Input.Geometry`.
3. `Distribute Points on Faces (Density Max ~ a few)` → `Instance on Points` of a scaled-down copy of the input geometry.
4. `Scale Instances` by `(Iteration Index → Map Range → 0.7^index)`.
5. `Rotate Instances` by random per-point angles.
6. `Join Geometry` (original input + new instances) → `Repeat Output`.
7. Run 3–5 iterations.

**Params:** `Iterations`, `Branches per Iteration`, `Scale Falloff` (per-iter multiplier 0.5–0.8), `Tilt Range`, `Seed`.

**Variations:**

- **Phyllotaxis spiral:** instead of random rotation, rotate each branch by the golden angle (137.5°) — gives sunflower-style packing.
- **Asymmetric growth:** weight more branches toward one normal direction (gravity bias) by biasing the random with a constant offset.

**Performance notes:** geometry explodes exponentially. Use instances all the way through and only Realize at the end. Use the Bake node after the Repeat for downstream iteration without re-cooking.

### Recursive Subdivision with Bevel

**Use:** sci-fi panel-greeble surfaces, weathered architectural detail, mechanical fractal feel.

**Build (modifier stack, not GN graph):**

1. Subdivision Surface modifier (Catmull-Clark, level 2).
2. Geometry Nodes modifier: `Distribute Points on Faces` → `Instance on Points` of small extruded cubes → `Realize Instances`.
3. Bevel modifier (Width = 0.01, Segments = 2).
4. Subdivision Surface modifier (level 1, smooth).
5. Repeat steps 2–4 if you want a second pass.

**Params:** subsurf levels, scatter density, bevel width.

**Variations:**

- **GN-only version:** put the whole chain inside a Repeat zone with Subdivide Mesh + Extrude Mesh inside.
- **Selective bevel:** use a vertex group on the Bevel modifier to limit bevel to specific regions.

**Performance notes:** Realize on every iteration is the bottleneck. Two passes is usually plenty.

### Voronoi Fracture Into Instances

**Use:** breaking a mesh into voronoi shards for destruction, dissolution, or shatter effects.

**Build:**

1. Source mesh → `Realize Instances` if needed.
2. `Position` → `Voronoi Texture` (3D mode, output: F1 distance and Cell ID).
3. `Capture Attribute (Float, domain = Point)` of the Cell ID.
4. `Mesh Boolean (Intersect)` against per-cell convex hulls — or use the `Mesh to Volume → Volume to Mesh` trick to remesh per-cell.
5. `Separate Geometry` by Cell ID into a point cloud of cell centers + per-cell meshes.
6. `Instance on Points`: place each shard mesh at its cell center.

**Params:** `Cell Density`, `Randomness` (0–1, voronoi randomness), `Seed`.

**Variations:**

- **Animated shatter:** translate each shard outward from the source center by `(Cell Center - Source Center).normalize() * time`.
- **Partial fracture:** mask the voronoi region by a vertex group — only break in the painted area.
- **Shader-only fake fracture:** if the asset never needs to physically separate, use the same Voronoi in the shader as a Cell ID, color cracks via Color Ramp on F2-F1 distance. Cheaper.

**Performance notes:** real fracture is expensive. The Mesh Boolean per cell is the cost. Voronoi alone is fast; the booleans are not. Bake the fractured result once and animate the bake.

### Sierpinski / Menger-Like Fractal

**Use:** mathematical fractal forms — Menger sponges, Sierpinski tetrahedra, Koch surfaces.

**Build:**

1. Start with a cube (Menger) or tetrahedron (Sierpinski).
2. `Repeat Input.Geometry`.
3. `Subdivide Mesh` (1 cut → divides each face into 4, each cube into 27 sub-cubes for Menger).
4. `Mesh to Points (Faces)` → carries a Face Index.
5. `Compare` Face Index against a removal pattern (for Menger: remove the 7 center cubes of every 27 — index mod 27 in {4, 10, 12, 13, 14, 16, 22}).
6. `Delete Geometry` based on the comparison.
7. Output → `Repeat Output`, 2–4 iterations.

**Params:** `Iterations` (1–4 typical), `Pattern Type` (enum via Switch).

**Variations:**

- **Random removal:** swap the index-based pattern for `Random Value (Boolean)` — gives a noisy fractal that still looks self-similar.
- **Sierpinski tetrahedron:** start with a tetra, subdivide each face into 4, remove the center one. 4–6 iterations.

**Performance notes:** geometry count is 27^n for Menger — 4 iterations = ~500k cubes. Use instances if at all possible, Realize only for render.

---

## Organic Form Recipes

Smooth, biological, growth-like surfaces. The common thread is **base primitive + displacement field**.

### Crystalline Growth

**Use:** angular crystal clusters, frozen formations, geometric mineral growth.

**Build:**

1. `Ico Sphere` (subdivisions = 4) or `UV Sphere` (high res).
2. `Set Position` with offset = `Normal * (noise_value > threshold ? value : 0)`.
3. The noise: `Voronoi Texture (F1)` scaled large — sharp cell edges → blocky crystals.
4. Apply Shade Flat (or use `Set Shade Smooth` with input = False) for crystalline facets.
5. Optionally: `Repeat` the displacement 2–3 times with progressively smaller scale for nested crystal growth.

**Params:** `Crystal Size` (voronoi scale), `Sharpness` (threshold), `Growth Amount` (offset multiplier), `Seed`.

**Variations:**

- **Quartz cluster:** use `Distribute Points on Faces` on a base rock + `Instance on Points` of an actual modeled quartz prism, slope-aware so they only grow upward.
- **Ice fractal:** stack with a second-pass smaller-scale voronoi for nested detail.

**Performance notes:** voronoi 3D is fast in GN. The Realize step (if any) is the cost.

### Branching Coral

**Use:** branching organic structures with thickness — coral, vasculature, neuron dendrites, root systems.

**Build:**

1. Start with a `Curve Line` or hand-drawn Bezier curve.
2. `Resample Curve` to high density.
3. `Repeat Input.Curve`.
4. Inside: at each point, with probability `branch_chance`, spawn a child curve offset in a randomized normal direction. Use `Index` + `Random Value` + `Compare`.
5. Recurse for N iterations.
6. After Repeat: `Curve to Mesh` with a `Curve Circle` profile, profile radius driven by `Spline Parameter.Factor` (taper toward tip).

**Params:** `Iterations`, `Branch Chance` (0–1), `Branch Angle Range`, `Profile Radius`, `Taper`.

**Variations:**

- **Vasculature feel:** thinner branches, more iterations, less curl.
- **Mangrove roots:** start from multiple seed curves, force downward bias.
- **Lightning bolt:** one curve, displaced sideways each segment via noise, no branching.

**Performance notes:** the `Curve to Mesh` is where mesh count explodes. Keep profile circles low-res (8 verts is plenty for distant work).

### Worn Rock

**Use:** weathered boulders, eroded stone, organic rocky props.

**Build:**

1. `Ico Sphere` (subdiv 5).
2. `Set Position` with offset = `Normal * combined_noise`.
3. `combined_noise` = `Noise Texture (Detail=10, Roughness=0.5) * 0.5 + Voronoi (F2-F1) * 0.3 + Noise (Scale 10, Detail=2) * 0.1` — three octaves at three scales.
4. `Set Shade Smooth` (input = True) — smooth shading sells the wear.
5. Geometry Nodes modifier with this, plus a Subdivision Surface modifier above (level 1) for extra resolution.

**Params:** `Large Scale Amount`, `Medium Scale Amount`, `Detail Amount`, `Seed`.

**Variations:**

- **Sharp rock:** replace the smooth noises with voronoi F1 (cell distance) — gives crystalline angular form.
- **Smooth river stone:** drop the high-frequency octave, keep only the large-scale noise.
- **Cracked rock:** layer in a separate voronoi pass and use it as a mask for a *negative* displacement (cracks rather than bumps).

**Performance notes:** triple-noise eval is fine. The Subsurf above is the cost — keep it at level 1 unless rendering close-up.

### Cellular Surface (Leaf, Fish Scale, Honeycomb)

**Use:** any surface that should read as packed cells — leaf veins, fish scales, honeycomb, alligator skin.

**Build:**

1. Host surface → `Distribute Points on Faces` (Poisson Disk, controlled `Distance Min`).
2. Per point: `Voronoi Texture (3D)` evaluated at point position gives the cell metric — but for surface cells, use the points themselves as cell centers.
3. `Instance on Points`: a flat scale-shape mesh (small hexagon or curved scale).
4. `Align Euler to Vector (Normal)` → `Rotate Instances` (scales align flat to surface).
5. Random rotation around the surface normal via `Combine XYZ (0,0,random θ)`.
6. Optional: scale variation by position-noise sample.

**Params:** `Scale Density` (via `Distance Min`), `Scale Size`, `Scale Overlap`, `Tilt`.

**Variations:**

- **Cracked leaf vein:** instead of instancing scales, use the voronoi F2-F1 distance on the surface as a *shader* darkening factor — veins read in the material, not the geometry.
- **Reptile scale:** use a higher-poly instance with slight upward curl, raise base scale slightly so they overlap.
- **Honeycomb:** hexagonal instance, low overlap, regular Poisson — reads as bee cells.

**Performance notes:** thousands of small instances. Stay un-realized. The Poisson scatter is the cost; instance count is free.

---

## Environment Recipes

Whole-scene backbones. Each combines several smaller recipes.

### Procedural Landscape from Heightfield

**Use:** terrain, dunes, rolling hills, undulating ground plane.

**Build:**

1. `Mesh Primitive (Grid)` with high subdivision (e.g. 200×200) — or a Plane + Subdivide modifier.
2. `Set Position` with offset = `(0, 0, height_field)`.
3. `height_field` = `Noise Texture (Scale 0.5, Detail 8, Roughness 0.5) * amplitude`.
4. For more character, sum two noises: a large-scale low-frequency one and a small-scale high-frequency one.
5. `Set Shade Smooth` true.
6. Optional: pipe the height into a `Capture Attribute` for downstream use (e.g. snow shader threshold).

**Params:** `Scale` (m), `Amplitude` (m), `Detail`, `Roughness`, `Seed`, `Resolution` (grid count).

**Variations:**

- **Erosion feel:** subtract a `Voronoi (F1)` term — gives ridge-and-valley structure.
- **Plateau / mesa:** wrap the height through `Color Ramp (Constant interpolation)` — flat shelves.
- **Snowline:** capture height; in the material, mix snow shader above threshold.

**Performance notes:** grid resolution is the cost. 200×200 = 40k verts is fine on M1. Push to 1000×1000 only if rendering and bake the result.

### City Block from a Footprint Plane

**Use:** stylized city, modular building tops, urban environment as a backdrop.

**Build:**

1. Footprint plane → `Subdivide Mesh` to roughly building-sized faces.
2. `Mesh to Points (Faces)` → per-face center.
3. `Extrude Mesh` each face individually by a height = `Random Value (range 5–50 m)`.
4. After extrude: `Bevel` (small width) for chamfered edges.
5. Optional: `Boolean (Difference)` against a window-grid pattern mesh for facade detail.

**Params:** `Building Height Min/Max`, `Footprint Subdivisions`, `Bevel Width`, `Seed`.

**Variations:**

- **Setbacks / step-backs:** apply a second `Extrude Mesh` at half the original height with smaller scale for a stepped silhouette.
- **Roof variation:** boolean a `Cylinder` (water tower) or `Cube` (HVAC) onto random buildings.
- **Procedural windows in shader:** instead of geometric windows, use a `Brick Texture` shader with emission for lit windows at night.

**Performance notes:** booleans are expensive — limit to <100 cuts per building. Use shader window pattern for cityscapes seen from afar.

### Underwater Seabed

**Use:** ocean floor, kelp forest base, submerged terrain.

**Build:**

1. Landscape recipe (above) with low amplitude, high detail — sandy ripples.
2. Slope-aware scatter recipe → instance kelp/coral assets only on flatter areas.
3. Density-mask scatter for rocks in cluster regions.
4. World shader: gradient blue-green-black sky → fake underwater volume; OR add a Volume Cube with low-density `Principled Volume` (Density 0.05, Color teal, Absorption 1.0) covering the scene.
5. Optional: caustics — `Voronoi (F2-F1)` warped by noise, animated via Scene Time on the W axis, fed as emission color on the seabed material.

**Params:** terrain params + scatter params + volume density + caustic speed.

**Variations:**

- **Coral reef variant:** dense coral asset scatter with high-variance rotation + bright shader colors.
- **Deep abyss:** raise volume density to 0.3+, near-black, point-light only.

**Performance notes:** the volume is the cost — Cycles handles it; EEVEE struggles. Keep volume step size reasonable (≥0.1).

### Forest Floor

**Use:** ground layer of a forest — moss, leaves, twigs, undergrowth — at human-scale density.

**Build:**

1. Host plane (or terrain) → multiple parallel Distribute scatters:
   - **Layer A:** moss patches — high density (~100/m²), small flat scale-instances, slope-aware (only on level ground).
   - **Layer B:** leaf litter — medium density, varied rotation, scale 0.05 m, multiple leaf assets via Collection Info.
   - **Layer C:** twigs — low density, long-thin asset, full random rotation.
   - **Layer D:** small mushrooms / saplings — very low density, density-masked to specific painted areas.
2. Each scatter is a separate Distribute Points on Faces → Instance on Points chain.
3. `Join Geometry` of all four → output.
4. Ground material: procedural soil — Noise + Color Ramp (browns) + Bump via Noise.

**Params:** density per layer, scale per layer, seed.

**Variations:**

- **Snow-covered:** mix a white snow shader on top via a height-based mask in the material.
- **Desert floor:** swap moss for sand-noise displacement, leaves for pebbles, twigs for dried sticks.

**Performance notes:** total instance count can hit millions. Stay un-realized. Hide layers in viewport while authoring (use Modifier `Show in Viewport` toggle).

---

## Shader Procedural Recipes

These live in **Material → Shader Nodes**, not Geometry Nodes. They define color, roughness, and bump per pixel rather than geometry per vertex.

### Procedural Wood

**Use:** wood grain on any surface — flooring, furniture, props.

**Build:**

1. `Texture Coordinate.Object` → `Mapping` (scale Y by 10x for stretched grain).
2. → `Wave Texture` (Bands, Distortion 1.0, Detail 4) → main grain.
3. → `Noise Texture` (Scale 50, Detail 8) → fine knots and irregularity.
4. Mix the wave (90%) and noise (10%) via `Mix (Linear Light)`.
5. → `Color Ramp` (deep brown → light tan, 3 stops) → Base Color of Principled BSDF.
6. The same combined value → another Color Ramp for Roughness (darker = rougher), feed into Roughness.
7. Bump: same value → `Bump` node (strength 0.1) → Normal input.

**Params:** wave scale, distortion, knot frequency, color stops, bump strength.

**Variations:**

- **Plywood:** mix two wave textures rotated 90° from each other for cross-grain layers.
- **Aged wood:** add a `Voronoi (F2-F1)` mask blended over the base for cracks.
- **Oak vs pine:** wider color ramp gap = oak; tighter = pine.

**Performance notes:** all GPU. Cheap in EEVEE and Cycles.

### Procedural Marble

**Use:** marble, agate, stone with veining patterns.

**Build:**

1. `Texture Coordinate.Generated` → `Mapping`.
2. → `Noise Texture` (Scale 5, Detail 6) — use this as distortion.
3. → `Wave Texture` (Bands, Distortion = Noise output × 2.0, Detail 4) — distorted wave gives marble veining.
4. → `Color Ramp` (cream base → narrow dark vein stops at ~0.45–0.55) → Base Color.
5. Roughness: low constant ~0.1 for polished marble.

**Params:** noise scale (vein wildness), wave scale (vein frequency), vein color, vein width (Color Ramp stop tightness).

**Variations:**

- **Agate:** tighter color ramp with multiple bands of contrasting colors.
- **Onyx:** add a second noise multiplied in for translucency mask, drive Subsurface.

**Performance notes:** cheap. Detail >8 starts to matter in real-time.

### Procedural Rust

**Use:** rust, oxidation, weathering on metal surfaces. Stacks over a base PBR metal material.

**Build:**

1. Base: a Principled BSDF with metal params (Metallic 1.0, Roughness 0.3, base color steel gray).
2. Rust source: `Noise Texture` (Scale 8, Detail 6) → `Color Ramp` (sharp step around 0.55) — gives splotchy patches.
3. AND with: `Voronoi Texture (F1)` → `Color Ramp` (threshold) — gives finer rust dots within patches.
4. Combine via `Math (Multiply)` → final rust mask (0 = clean metal, 1 = full rust).
5. Rust material: orange-brown Principled BSDF (Metallic 0.0, Roughness 0.9).
6. `Mix Shader` between clean and rusty driven by the mask.
7. Optional: also drive Bump strength higher where rusty for pitted surface.

**Params:** rust amount (Color Ramp position), rust scale, base metal color, rust color.

**Variations:**

- **Painted-over rust:** add a third white paint layer driven by a separate larger-scale noise, sit it between bare metal and rust.
- **Drip pattern:** use a `Gradient Texture (Linear)` with vertical mapping, multiplied with the rust mask, for vertical streaks.

**Performance notes:** cheap. The dual texture sampling is the only cost.

### Procedural Fabric Weave

**Use:** woven fabric, burlap, canvas, denim — anywhere a fine repeating pattern reads at close range.

**Build:**

1. `Texture Coordinate.UV` → `Mapping` (scale 50–200 for tight weave).
2. `Brick Texture` (Squash 1.0, gives basic checkerboard of warp/weft cells).
3. Separate two interleaved patterns: even rows = warp, odd rows = weft, each with offset.
4. Each cell gets a small bump via `Noise Texture` (Scale 100) → `Bump` (strength 0.3).
5. Color: subtle variation via `Noise Texture (large scale)` for natural fiber irregularity.
6. Roughness: high constant ~0.8.

**Params:** weave scale, bump strength, color noise amount.

**Variations:**

- **Denim:** add blue-gray base + small white noise spots for fiber.
- **Burlap:** lower weave scale (chunkier), higher bump.
- **Silk:** drop bump, raise specular, narrow color variance.

**Performance notes:** cheap. Real fabric in close-up benefits from a proper anisotropic shader; this is the at-distance version.

---

## Animated Procedural Recipes

Add time as an input and recipes become motion.

### Animated Noise Displacement

**Use:** ripples, breathing surface, slow undulation. The simplest way to animate a procedural surface.

**Build:**

1. `Set Position` with offset = `Normal * Noise Texture (4D)`.
2. The Noise: feed `Scene Time → Seconds → Math (Multiply by speed) → W` input of the noise.
3. Default 3D coordinate from `Position`.

**Params:** `Speed` (W multiplier), `Amplitude`, `Scale`, `Detail`.

**Variations:**

- **Direction-biased:** add a constant vector to Position before the noise — gives flowing-in-one-direction motion.
- **Pulsing breath:** swap noise for `Math (Sin(time * frequency))` and drive uniform expansion along normal.

**Performance notes:** evaluates per frame. M1 handles a million vertices comfortably. Bake to disk for long animations to avoid re-cooking.

### Flowing Curves

**Use:** energy threads, neon arcs, animated cables, hair flow.

**Build:**

1. `Curve Line` (or imported curve).
2. `Resample Curve` to high count.
3. `Set Position` on the curve points with offset = `Vector(0,0,noise(position.xy + time * speed))` — gives wave-like motion.
4. `Curve to Mesh` with a small `Curve Circle` profile.
5. Material: Emission shader.

**Params:** curve resolution, offset amplitude, scroll speed, profile radius.

**Variations:**

- **Spiral animation:** wire `Spline Parameter.Factor + time` into rotation around tangent.
- **Multiple parallel curves:** Duplicate Elements (Curve) by N, each with a slight position offset, scale and roate over time.

**Performance notes:** lightweight. Cost is the Curve to Mesh resolution.

### Pulsing Scale on Instances

**Use:** instances that breathe — pulsing lights, beating crystals, throbbing pods.

**Build:**

1. Scatter recipe (any).
2. Between scatter and `Instance on Points`, store `Random Value (Float, ID = Index)` as a per-instance phase offset attribute via `Store Named Attribute`.
3. After `Instance on Points`, scale instances by `base + sin((Scene Time + phase) * frequency) * amplitude`.
4. `Scale Instances` accepts a per-instance field — wire it in.

**Params:** `Base Scale`, `Pulse Amplitude`, `Frequency`, `Phase Randomness`.

**Variations:**

- **Synchronized:** drop the per-instance phase — all instances pulse together.
- **Travelling wave:** replace phase with `Position.X * spatial_frequency` — phase rolls across the field.

**Performance notes:** free — per-instance fields cost nothing.

### Drifting Clouds (Volumetric)

**Use:** sky clouds, atmospheric fog, dust, smoke. Volumetric, not surface.

**Build:**

1. Cube primitive (sized to the volume bounds) → material slot with a volume-only shader.
2. Shader: `Texture Coordinate.Object` → `Mapping (translate by Scene Time * vector)` → `Noise Texture (Scale 5, Detail 8)` → `Color Ramp (sharp step around 0.55)` for cloud density mask.
3. Output: `Principled Volume` (Density = mask * 5.0, Color = white, Anisotropy 0.4).

**Params:** drift direction & speed (Mapping translate vector), density, cloud edge sharpness (Color Ramp), color.

**Variations:**

- **Storm:** multiply density by a second large-scale noise for clumped storm cells.
- **Aurora:** swap noise for `Wave Texture (Rings)` and emission instead of scattering.
- **Smoke trail:** drive Mapping translate by an object's position rather than time.

**Performance notes:** volumes are Cycles-strong, EEVEE-weak. In EEVEE, increase `Volumetric Samples` and reduce `Tile Size` for quality. In Cycles, expect long renders — bake to OpenVDB once happy via the File → Export → OpenVDB path (or the bake-to-VDB GN flow).

---

## Combination Patterns — Layered Recipes

Real scenes layer multiple recipes. A "procedural forest" is `landscape + slope-aware scatter + density-mask scatter + ground material + volume`.

### Procedural Rocky Terrain With Scattered Plants

**Layers:**

1. **Terrain** — Landscape recipe (height = large noise + erosion voronoi).
2. **Rock scatter** — Density-mask scatter restricted to high-slope or high-elevation regions (via slope-aware recipe).
3. **Plant scatter** — Slope-aware scatter, slope threshold 0.7+, density biased toward low altitude (via Position.Z → Map Range → density factor).
4. **Material** — height-based shader mix: rock above threshold, grass below, snow above another threshold.

Each layer is a separate Geometry Nodes modifier on the host plane, or all merged in one graph via `Join Geometry`.

**Diff to make a desert:** drop the grass, replace with sand-grain shader, raise rock density, drop slope threshold.

### City Block With Population

**Layers:**

1. **Buildings** — City block recipe with random heights.
2. **Streets** — boolean-cut the footprint plane with a grid pattern before extrusion.
3. **Vehicles** — Array along curve recipe along the street centerlines, asset = car collection (random pick).
4. **Pedestrians** — Density-mask scatter on sidewalks (mask painted via vertex group along edges of streets), low density, random person assets.
5. **Streetlights** — Array along curve recipe with regular spacing, asset = lamppost mesh, scale-by-curve-param off.

Each is its own modifier (or NodeGroup inside one master graph).

**Diff to make a suburb:** lower building heights to 5–8 m, swap building asset for house templates, drop vehicle density.

### Forest From Terrain to Canopy

**Layers:**

1. **Terrain** — Landscape recipe.
2. **Tall trees** — Slope-aware scatter, asset = tree collection, low density (~0.1/m²).
3. **Bushes** — Density-mask scatter, asset = bush collection, medium density.
4. **Ground cover** — Forest floor recipe (moss / leaves / twigs).
5. **Fog volume** — Drifting clouds volumetric recipe with very low density (0.05), green-tinted color, drifting slowly horizontal.
6. **Sun light** — strong directional, slight warm color, low angle for shafts.

The volume + sun gives god-ray feel without explicit setup.

**Diff to make jungle:** raise tree density 5×, swap fog to higher density, raise ambient humidity (saturate world color toward green).

---

## Parameterization Patterns

When wrapping a recipe in a NodeGroup, expose these inputs via `tree.interface`:

- **Always expose:**
  - `Density` (or `Count`) — scalar control over how much of the thing exists.
  - `Seed` (int) — re-roll randomness without changing anything else.
  - `Scale Min / Scale Max` — size envelope.
  - `Asset` (Object or Collection) — what's being instanced.

- **Expose where useful:**
  - `Tilt Range` — rotation jitter ceiling.
  - `Mask Input` — Vertex Group name or Object to sample from. Use a `String` socket for vertex group name, `Object` socket for a target reference.
  - `Category Enum` — Boolean (for 2 variants) or Menu socket (4.5+) to switch between sub-recipes inside one graph.
  - `Color` — for shader recipes that have a hero color choice.

**Switch-based variant pattern:**

1. Build two sub-graphs inside the NodeGroup — Recipe A and Recipe B.
2. Both feed into a `Switch (Geometry)` node.
3. Expose the `Switch` boolean input as a group input named `Use Variant B`.
4. The user toggles the modifier checkbox to swap variants without two separate modifiers.

For more than 2 variants, use Menu sockets (4.5+) or nested Switches keyed off `Compare (Integer)`.

**Single-modifier multi-recipe pattern:** any time the user might want to swap "rocks scatter" for "plants scatter" on the same surface, wrap both into one NodeGroup with a Switch — keeps the modifier stack short and the parameter surface unified.

---

## Performance Notes

The recipes above range from free to expensive. The cost rules:

- **Lazy instances are nearly free.** A million instances of a 10k-vert mesh cost ~10k verts of memory plus a few KB of transform data. Stay un-realized as long as possible.
- **`Realize Instances` is proportional to total geometry.** A million instances of a 10k-vert mesh becomes a 10-billion-vert mesh — usually not what you want.
- **Simulation zones are CPU-only on Apple Silicon.** They do not benefit from M1's GPU. Keep point counts under ~50k for real-time playback.
- **Voronoi in Geometry Nodes is fast. Voronoi in shader nodes is slower** (per-pixel rather than per-element, and shader nodes don't get the same SIMD path). When voronoi-driven displacement is needed, do it on geometry and capture the result as an attribute; sample the attribute in the shader.
- **Volume operations are expensive.** Mesh to Volume, Volume to Mesh, and Principled Volume rendering all eat time. Bake volumes to OpenVDB once authored.
- **The Bake node (4.1+) is the right answer to "this recipe is slow."** Bake immediately after the expensive step (the scatter, the simulation, the voronoi fracture). Downstream edits cook only the cheap nodes.
- **Bake-to-disk wins over bake-to-blend for large data.** The `.blend` file balloons fast otherwise.
- **Subdivision Surface above Geometry Nodes** evaluates after — heavy. Below — evaluates before — also heavy if the GN graph reads the dense mesh. Place Subsurf where the cheapest evaluation lives.
- **Apply Modifier** is the nuclear option — converts the procedural result to plain mesh data. Useful when authoring is done and the procedural was just a generator.

---

## The "Diff Against This Recipe" Pattern

When the agent gets a new request, the workflow is:

1. **Identify the closest recipe** in this file. (Scatter? Curve array? Fractal? Animated displacement?)
2. **Read the recipe's Build steps.** This gives the backbone.
3. **Diff:** what's different from the request? Usually one of:
   - **One node swap** — e.g. swap `Random` distribution for `Poisson Disk`.
   - **One input change** — e.g. drive Density from a painted attribute instead of a slider.
   - **One additional node** — e.g. add a `Compare` before the density to slope-filter the scatter.
4. **Apply the diff.** Build the recipe, then make the change.
5. **Don't rebuild from scratch** unless the request truly does not match any backbone. 90% of requests match.

This mirrors the TouchDesigner pattern: a curated set of reference networks, each with a documented contract. New work is almost always a diff against an existing network, not a new one.

When proposing a recipe to the user, say which canonical one it's based on and what the diff is — "Density-mask scatter, but with the mask driven by camera distance instead of a vertex group." Surfaces the diff makes the change reviewable.

---

## Related

- [[BLENDER_GEOMETRY_NODES]] — the node-level reference. What every GN node *does*.
- [[BLENDER_SHADER_NODES]] — the shader-node reference. Procedural materials live here.
- [[BLENDER_MODELING]] — modifier stack reference. The non-GN modifier pipeline (Subsurf, Bevel, Solidify, Wireframe, etc).
- [[BLENDER_MATERIALS]] — material datablock model, where shader recipes are wrapped.
- [[BLENDER_PATTERNS_LIGHTING]] — lighting recipes that complete the scenes built here.
- [[BLENDER_APPLE_SILICON]] — M1 performance constraints referenced throughout.
- [[BLENDER_LIBRARY_INDEX]] — the entry point.
