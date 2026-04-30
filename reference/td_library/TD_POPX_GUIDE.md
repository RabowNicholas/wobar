---
title: POPX Library Guide (TD 2025)
version: 1.1
last_updated: 2026-04-30
status: reconciled with official docs (popsextension.com, v1.3.0). Major correction in v1.1: universal `Initialize → Start → Play` pattern documented; Flow's `Advect` toggle distinguished from `Solvermode`; v1.3.0 breaking changes added (Path Tracer/DLA/Constraints/Material/Particle/Soft Body); 9 missing modules added (Spread/Object/Curve Falloff, Apply/Extract Attributes, Geometry/Merge/Delete tools, Preview Falloff). All 55 examples surveyed (v1.0); guide is feature-complete for 1.3.0.
scope: Reference for the third-party POPX library (v1.3.0). Per-module documentation, install state, conventions, gotchas, integration patterns, WOBAR application notes. Capability table maps "without POPX" → "with POPX" for the major recipes.
td_version_target: 2025.32460 (Non-Commercial)
dependencies: [[td_library/TD_OPERATORS_POP]], [[td_library/TD_PATTERNS_INSTANCING]]
---

# POPX LIBRARY GUIDE

POPX is a third-party POP toolkit (v1.3.0, save build 2025.32460) that wraps higher-level POP operations on top of TD 2025's native POP family. Where native POPs give primitives (sphere, line, copy, attribute, normal, etc.), POPX provides composed modules — Instancer, Convert, Aim, MoveAlongCurve, MoveAlongMesh, OrientMesh, Randomize, Spring, Texture Falloff, Transform Modifier, etc. — with parameter UIs, in-viewport guides, and a shared `popxFalloff` attribute convention for layered control.

**Source:** `touchdesigner/POPX_Examples_1_3_0/` in this repo (examples + assets). Installer container is `/POPX_1_3_0` at the project root.

---

## Why It Matters For WOBAR

POPX solves classes of problem that previously required Script-CHOP-bridge math (per the Act 2 vortex pattern) or per-instance custom GLSL POPs:

| Need | Without POPX | With POPX |
|------|-------------|-----------|
| Instances on a 3D grid / curve / mesh | Script CHOP generating tx/ty/tz × N | `Instancer` module, single node |
| Instances aimed at a point | Per-instance look-at matrix in GLSL/Script CHOP | `Aim` modifier, parameter-driven |
| Flow instances along a curve with thickness | Per-instance phase + perpendicular offset math | `MoveAlongCurve(solver) + MaintainOffset` |
| Multi-shape image → individually-controllable instances | Manual per-shape mask + offset compositing | `tracePOP → Convert → modifiers` pipeline |
| Per-instance falloff field driven by an image / audio | Custom GLSL POP per-point sampling + smoothing | `Texture Falloff` writes `popxFalloff` automatically |
| Smooth audio-jittery attribute drives | Lag CHOPs + filter chains | `Spring` modifier with damping |
| Partial / falloff response per instance | Per-instance weight CHOP + interpolation | `popxFalloff` attribute, automatic |
| Geometry advected by simulated turbulence / smoke / fire | Custom GLSL Stam-style fluid solver | `Flow` module — full Navier-Stokes with TOP/optical-flow drivers |
| Coral / lightning / mycelium fractal growth from a seed | Custom GLSL DLA shader, hand-modeled SOP, L-system | `DLA` module — diffusion-limited aggregation, audio-drivable |
| Brain-coral / labyrinth / fingerprint pattern from a seed line | Custom GLSL differential growth shader, Houdini import | `DLG` module — differential line growth with self-avoidance |
| Mesh shattered into Voronoi shards | Houdini fracturing + import | `Explode` module — Voronoi/perprim partitioning |
| Wavefront-style propagation across instances over time | Custom GLSL flood-fill / per-frame attribute writes | `Infection Falloff` module — viral spread from seed POP |
| Wind-blown / dissolving fragment motion | Custom GLSL curl-noise displacement | `Noise Modifier` module — `Curlnoise=True, Mode=advect` |
| Full disintegration / "Thanos snap" effect | Custom multi-shader pipeline | `Explode → Infection Falloff → Noise Modifier (curl,advect) → Transform Modifier (scale 0.2)` chain |
| Geometry → 3D voxel grid for Flow injection / volume rendering | Custom GLSL voxelizer | `Voxelize` module — pointcloud / surface / SDF modes |
| Particle emitter with proper birthrate/lifetime + Flow integration | Hand-rolled particle CHOP/SCRIPT setup | Native `particlePOP` + Flow `Solvermode='simple'` |
| Visible motion trails per particle | Custom feedback TOP shader | Native `trailPOP` with attribute-matching |
| Per-instance falloff from a 3D shape (sphere/box/etc) | Custom GLSL distance-field POP | `Shape Falloff` module — geometric falloff source |
| Discretize a continuous attribute into N integer index buckets | Custom CHOP/Python expression on point attribute | `Attribute To Index` module — bridge to multi-geometry instancing |
| Different geometries assigned to different point subsets via index | Multiple Replicators or hand-stitched Switch chains | `Instancer` with `Indexingmode='pointattr'` + multiple `InstancesNpop` slots |
| Multi-source attract/repulse/spin force field | Custom GLSL attractor math, hand-rolled magnet logic | `Magnetize` module with per-magnet attribute control |
| Per-instance color from a behavior attribute via ramp lookup | Custom GLSL color shader, manual MAT setup | `Color Modifier` module — `Falloffattr` + `Ramptop` |
| Per-point geometric analysis (curvedness, gradient) | Custom GLSL analysis pass, Houdini-style measure SOP | `Measure` module |
| Mesh-following particle flow along topology features | Custom GLSL geodesic integrator | `Measure (curvedness) → Measure (gradient) → mathmixPOP (cross w/ N) → Advect Modifier (refgeo)` chain |
| Particles advected along a per-point vector attribute on geometry | Custom GLSL vector-field integrator | `Advect Modifier` with `Advectsource='refgeo', Advectattr='Dir'` |
| Volume-fill the interior of a mesh with organic trails | Custom space-colonization algorithm, Houdini import | `Mesh Fill` module — boundary IS the input mesh |
| Particles flow along the SURFACE of a mesh (constrained, never escape) | Custom GLSL geodesic integrator | `MoveAlongMesh` (with `OrientMesh` for direction field) |
| "Living skin" / creature-with-veins effect | Custom GLSL surface-flow shader | `mesh → OrientMesh (curl noise) → MoveAlongMesh (scatter, lifetime, scaleByAge) → trailPOP` chain |
| Spatial falloff variation from procedural noise | Custom GLSL noise + attribute writeback | `Noise Falloff` module — fifth member of the falloff family |
| Manual hand-authored falloff regions painted via viewport | Vertex paint workflow + custom export | `Paint Falloff` module — sixth member of the falloff family, takes user input |
| Particle-based fluid simulation (water, droplets, splashes) | Custom GLSL SPH solver | `POPX Particle (Fluid SPH mode)` — Lagrangian fluid (vs Flow's Eulerian voxel grid) |
| Render fluid particles as continuous liquid surface (refraction, absorption) | Custom screen-space fluid GLSL shader | `SSFR` module — Screen Space Fluid Renderer |
| Real-time painted/animated collision shapes for SPH fluid | Custom GLSL collision sampler | `Particle.Collisiontype='t2d'` + `Collisontop=<animated TOP>` — TOP defines collision field |
| Physically-based path-traced rendering with global illumination | Octane / Redshift / external PBR renderer + handoff | `Path Tracer + POPX Material + POPX Light` — full PBR pipeline inside TD |
| Per-instance PBR material variation driven by attribute | Hand-author N materials + manual switching | `POPX Material` with `Roughness/Metallic/Emission` driven by per-instance `popxFalloff` |
| Image-based environment lighting (HDRI) | Manual env light setup | `POPX Light Type='env'` with `Texturemap=<HDRI TOP>` |
| Slime-mold / mycelium / vascular network simulation | Custom GLSL Physarum compute shader | `Physarum` module — 2D or 3D, with TOP-bounded constraint volume |
| Per-instance pivot offset for foot/top/edge rotations | Manual matrix transform per instance | `Pivot` module — `Mode='bbox', Alignmentside='ym'` for foot rotation |
| Distribute points evenly across an arbitrary mesh interior | Lloyd's / Poisson-disk sampling implementation | `Relax` module + Voxelize SDF as `Collisontop` |
| Reset local axes after randomized/aimed rotation (visual randomness + functional predictability) | Manual quaternion math per instance | `Reorient` module — `Attrtype='quat'` with identity quaternion attribute |
| Vascular tree / branching network / leaf-vein pattern | Custom GLSL shortest-path solver, hand-modeled tree | `Shortest Path` (single start, many ends) + `Sweep` (Scaletop trunk-to-branch ramp) |
| 2D triangulated mesh patch in arbitrary shape | gridPOP (regular grid) or hand-modeled SOP | `Planar Patch` module — irregular triangulation, edge-length controlled |
| Tube/ribbon surface from line strips with along-curve scale + color | Custom skinSOP + per-vertex attribute | `Sweep` module with `Applyscale` + `Scaletop` + `Applycolor` + `Colortop` |
| Position-based dynamics soft body / cloth / inflatable simulation | Houdini Vellum / external sim + import | `Soft Body` + `Constraints` + `Constraint Property` + `SBPP` chain |
| Per-region constraint property variation in soft body sim | Hand-author constraint groups | `Constraint Property` with `Map.Restscaleattr='popxFalloff'` (or any per-point attribute) |
| Multiple constraint flavors on same body (surface springs + internal volume preservation) | Single Constraints module — only one `Constrainttype` at a time | **Chain Constraints modules in series** — e.g. `Constraints(cloth) → Constraints(struts)`. Each writes its own constraint set; Soft Body solver uses all. Order is solver-irrelevant. |
| Soft body hitting a single flat ground without authoring a collider mesh | Build plane + Constraints + Constraint Property + merge into solver | **Soft Body `Enablegroundcollision=True`** — built-in infinite ground at `Groundposition*=(0,0,0)`. Independent friction via `Groundstaticscale` / `Grounddynamicscale`. |
| Hair / fur / fringe / ribbons attached to a moving (rigged or skin-deformed) character | Houdini Vellum hair sim + import per frame | `Sprinkle (on deformed skin) → Copy(line template, dotemplaterotateto=True) → group(pt 0,1 = 'pin') → Constraints(Constrainttype='string', Pintype='stopped', Matchanimation=True) → Soft Body → Sweep(Skinops='group', Inc=points-per-line)` |
| Pinned soft body that follows a moving source (hair on running character, cloth on actor's shoulder) | Permanent pins detach from animating source | `Pintype='stopped'` + `Matchanimation=True` — pinned points re-read source position every frame; free points simulate dynamically |
| Wave / scroll / reveal travels through a mesh with elastic per-point lag | Hand-keyframed offset arrays + custom GLSL trail shader | `Spring Modifier(Other=True, Attr='popxFalloff') → Transform POP(weightattr='popxFalloff')` — Spring on the driving attribute (not the transform) gives each point its own lag based on when the falloff source touches it |
| Chaos-attractor point cloud (Lorenz butterfly / Thomas spiral / Aizawa torus) | Hand-write GLSL feedback loop per-attractor; Houdini VEX solver + import | `Strange Attractor` module with `Solvermode='advect'` — every input point advected along chosen preset's velocity field. Built-in presets: lorenz, thomas, aizawa, halvorsen, rossler, chen. Output `PartVel` drives downstream scale/color. |
| Strange-attractor coefficient morph driven by audio | Compile-time GLSL constants — no audio binding | SA module's `Ua…Uf` are scalar par slots; bind to CHOPs. Coefficient changes warp the attractor's shape live (e.g. ρ in Lorenz changes lobe separation → audible "breath"). |
| Crystalline / coral / dragonfruit / spike geometry from any base mesh | Houdini PolyExtrude→Subdivide chains; GLSL displacement shader | `Subdivider` module — `Subdivisions=N` (face density), `Extrudestrength` (spike length), `Inset` (taper), `Iterations=2+` for fractal stacking. Pair with falloff for region-localized growth. |
| Audio-reactive crystallization (bass crystallizes one region, kick another) | Multi-pass GLSL with custom mask logic | `Texture Falloff(audio FFT TOP)` upstream of `Subdivider(Dofalloff=True)` — spikes erupt only where falloff>0; coefficient bound to audio = bass-reactive growth |
| 2D image / video / spectrogram rendered as 3D stacked sweeps (each pixel-row becomes one curve) | Hand-author N sweep modules, route N TOP slices, custom GLSL displacement | `Sweep` with `Scalepercurve=True, Colorpercurve=True, Twistpercurve=True` — feed N stacked curves as backbone + a 2D TOP; each curve reads its row of the TOP. Same TOP can drive scale + twist + color simultaneously. |
| Custom cross-section profile for sweep (heart, star, hand-drawn outline) | Hand-build cross-section in GLSL or import from SOP; tube/square primitives only | `Sweep(Surfaceshape='input')` + provide cross-section curve as input[1]. Any POP curve works (circlePOP, patternPOP, custom line). |
| Per-letter typographic animation (wordmark bounces / squashes / tips per letter on beat) | Hand-keyframe each letter in After Effects; per-letter SOPs in TD; GLSL distortion shader | `textSOP → soptoPOP → cleanup → Convert(Partitionmethod='connectivity') → Pivot(Mode='bbox', Alignmentside='ym') → Shape Falloff → Spring → Transform Modifier → Unpack`. Convert auto-detects letters as connected components; Pivot anchors each letter to its baseline; Spring gives elastic per-letter lag |
| Living / breathing Voronoi tessellation (cells continuously rearrange) | Static voronoi from frozen seed cloud, or hand-author via GLSL with custom seed update | `pointgen → Relax(Solvermode='advect', Pointsupdatepop=feedback) → noisePOP(small amp) → null → Explode(Partitionmethod='voronoi', in1=relaxed-seeds)`. Self-feedback through null gives smooth seed diffusion; cells animate rather than freezing. |
| Voxel-art / Minecraft-style rendering of any mesh | Hand-build voxel grid in SOPs; brute-force point sampling | `mesh → Voxelize(Voxelizemode='mesh', Outputvolume=True, output[3]=voxel-centers) → geometryCOMP(instancing=True, instanceactive='Inside', template=boxPOP)`. The `instanceactive='Inside'` flag is the trick — only renders cubes inside the source mesh. |
| Debug visualization of per-instance orientation frames | Custom debug shader | `Visualize Frame` module — colored XYZ axes at each instance |
| Decoupled noise generation + advection (noise as data, not displacement) | Custom GLSL velocity field shader | `Noise Modifier (Outputnoiseattr=True) → feedbackPOP → Advect (Advectsource='ptattr', Advectattr='Noise')` chain |
| Convert any per-instance attribute into a standard falloff | Custom CHOP/expression attribute remapping | `Attribute Falloff` module |
| Bridge native POPs (Trail/Particle/Sprinkle) into POPX modifier chains | Manual attribute remapping, format conversion | `popxto` module — passthrough format conversion |
| Comet-tail / age-fading trail with per-sample geometry | Custom GLSL trail shader + per-fragment fade | `trailPOP (ageattr=seconds) → popxto → Attribute Falloff (Age) → Instancer (Copytemplateattributes='*') → Transform/Color Modifier` chain |
| Convert instanced output into raw POP geometry for downstream chains | Manual transform-baking + attribute copying | `Unpack` module — `Applytransform=True, Transferattrs='popxFalloff'` |
| Transform an existing falloff non-linearly (invert, fit, ramp) | Custom Math CHOP / GLSL POP | `Remap Falloff` module — distinct from Attribute Falloff (which converts any attr → falloff) |
| Falloff from arbitrary 3D mesh (not a primitive shape) | Custom SDF GLSL or distance-field SOP chain | `Object Falloff` — distance to any input mesh; modes for inside/outside, surface distance, surface intersection |
| Falloff from distance to a curve | Custom GLSL or distance-CHOP per point | `Curve Falloff` — three modes: distance to curve, distance × curve position, normalized curve position |
| Non-simulating wave-spread falloff (no Init/Play overhead) | Hand-author flood-fill | `Spread Falloff` — propagates from seeds through neighbor connections, direct (no simulation, vs Infection Falloff which IS simulation) |
| Bridge POPX-packed transforms back to native TD operators | Manual matrix extraction + attribute conversion | `Extract Attributes` — exports `N`/`Up`/`Orient`/`Scale`/`Pivot`/`Euler` for use with native Copy to Points or Geometry COMP |
| Per-instance materials within a single packed POPX render | Multiple Geometry COMPs in TD | `Geometry` (POPX tool) — auto-detects instance count, assigns material per index |
| Combine multiple POPX geometry streams into one | Multiple `mergePOP` chains | `Merge` (POPX tool) — preserves all attributes/groups/instance data per source |
| Filter / delete points by attribute / index range / pattern / group / bounding | Hand-author Delete SOP chain | `Delete` (POPX tool) — 5 methods combinable with AND/OR/XOR/NAND/NOR logical operators |
| Reset rotation axes after Explode/Voronoi shatter | Manual quaternion math | `Reorient` writes `popxOrient` quaternion attribute |
| Smooth orientation frames along curve for sweep | Custom parallel-transport math | `Orient Curve` — Parallel Transport algorithm, smooth predictable orientations |
| Mesh-surface flow / swirling motion frames | Custom GLSL geodesic | `Orient Mesh` with Cross Up Vector for swirling motion effects |
| Standalone falloff debugging viz | Manual color ramp + lookup | `Preview Falloff` tool (separate from per-module `Previewfalloff` toggles) |
| 11 chaos attractor presets (was: 6 documented in v1.0) | Hand-author equation per attractor | `SA` with full preset library: Lorenz, Aizawa, Thomas, Halvorsen, Dadras, Chen, Rossler, Sprott, Four-Wing, Nose-Hoover, Custom (DAT-defined) |
| Stateful POPX simulation that actually animates (vs frozen state) | Pulse Initialize and assume it runs | **Universal pattern: Initialize → Start → Play (4 steps, not 1).** See "POPX Universal Patterns" section. |
| Flow particles that actually move with the velocity field | Set Solvermode='advect' alone | **`Advect` toggle is independent of `Solvermode`** — both must be configured. See "POPX Universal Patterns". |

The native POP family + Script CHOP bridge still works and is dependency-free; POPX trades a vendor dependency for assembly speed and built-in visualization. **Default to native POPs unless a POPX module materially shortens the build.**

---

## Install State

- POPX 1.3.0 installer at `/POPX_1_3_0` (containerCOMP). Already installed in Nick's TD environment.
- `Index = 5`, `Expose = True` — POPX modules appear in the operator menu.
- `Createstubs` / `Replacestubs` pulse params on the installer regenerate stub references if the install path changes.

**Dependency caveat:** `.tox` files using POPX modules require POPX installed in the receiving TD environment. Do not commit POPX-dependent visuals to WOBAR final exports unless we either bake POPX out (convert to native POPs at save time) or commit to POPX as a project dependency.

---

## Convention Notes

POPX modules share a structural pattern that is useful to recognize while inspecting:

- Internal nodes prefixed `POPX_in*` / `POPX_out*` — input/output passthrough connectors
- `POPXExt` baseCOMP — extension class that backs `par.ext0object`, providing the module's logic
- `License` annotateCOMP — POPX licensing marker (do not delete)
- `FamManifest` baseCOMP — POPX module metadata (do not delete)
- `replicate_instance` replicatorCOMP — internally clones per-instance children when needed
- Custom parameter pages: each module exposes its own pages (e.g. `[Aim]`, `[Up]`, `[Orientation]`, `[General]`) plus standard `[Pre-Xform]`, `[Instance]` from the underlying geometryCOMP

When inspecting a POPX module via TWOZERO, the meaningful pars are usually on the **module-named pages** (e.g. `[Aim]`), not the inherited geometryCOMP pages.

---

## POPX Universal Patterns

These conventions apply across every POPX module. Knowing them up front prevents the "module silently does nothing" failure mode that's the #1 trap with POPX.

### 1. Stateful simulation modules: `Initialize → Start → Play`

For every POPX module that integrates state across frames (any "Advect" or "Solver" mode), the activation sequence is **four steps, not one**:

| Step | Action | Required? |
|------|--------|-----------|
| 1 | Pulse `Initialize` | Yes — resets state and spawns initial particles |
| 2 | Pulse `Start` | Yes — begins simulation from the initialized state |
| 3 | Toggle `Play = True` | Yes — enables continuous per-frame integration |
| 4 | Pulse `Step` | Optional — frame-by-frame advance when `Play=False` |

**Modules that follow this pattern:**
- `Strange Attractor (SA)` — Advect mode
- `Particle` — all modes (SPH / PBF / Grains)
- `DLA`, `DLG`, `Physarum`, `Mesh Fill`
- `Infection Falloff`
- `Spring Modifier` — Advect mode
- `Noise Modifier` — Advect mode
- `Move Along Curve` — Solver mode
- `Relax` — Advect mode
- `Magnetize` — Advect mode

**Exceptions:**
- **Soft Body** uses `Initialize + Play` only (no Start step)
- **Flow** has its own pattern (see below)

**Why this matters:** if you pulse Initialize but skip Start, the simulation is "loaded but paused" — every cook produces the same frozen state. This was THE source of every "SA freezes after init" failure.

### 2. Solvermode: `simple` vs `advect`

A near-universal parameter on stateful modules. Means the same thing across modules:

- **`simple`** — single-step velocity field evaluation per cook. Output = f(input) deterministically. **No state, no time integration.** Looks static unless input changes per frame.
- **`advect`** — full simulation with internal state. Integrates forward each frame using the Init→Start→Play sequence above. Holds state via internal `feedbackPOP`.

If a module looks frozen with `Solvermode='simple'`, that's **expected** — switch to `'advect'` and run the activation sequence.

### 3. The `*Updatepop` feedback pattern

Stateful POPX solvers expose a `*Updatepop` parameter (named per-module: `Pointsupdatepop`, `Targetpointsupdatepop`, `Walkersupdatepop`, `Lineupdatepop`, `Targetparticlesupdate`, `Targettrailupdate`, `Particlesupdatepop`).

This is a self-feedback handle: the solver reads from the named POP each frame, applies its update, writes new state back. Some modules **require** it for animation; others use it as an extension point for inserting per-frame modifiers into the loop.

**Required (won't animate without it):**
- `SA` — Advect mode requires `Pointsupdatepop`
- `Spring Modifier` — Advect mode (creates intentional feedback loop)
- `Relax` — Advect mode
- `DLG` — `Target Line Update POP`
- `Physarum` — both `Target Particles Update` AND `Target Trail Update`

**Optional (extension point):**
- `Flow`, `DLA`, `MoveAlongCurve`, `Particle`, `Mesh Fill`

Pattern:
```
solver → [optional modifiers] → null → solver.par.*Updatepop
```

### 4. The `popxFalloff` attribute convention

The shared per-instance falloff attribute. Most POPX falloff sources write to it (default name `popxFalloff`); most modifiers respect it via `Falloffattr` parameter. This is the architectural backbone for layered, audio-reactive, and spatially-varying control.

- Default attribute name: `popxFalloff`
- Override per-module via `Outputfalloffattr` (write side) or `Falloffattr` (read side)
- Use multiple distinct names (`popxFalloff_audio`, `popxFalloff_proximity`, etc.) to layer independent control fields

### 5. Flow's `Advect` toggle is independent of `Solvermode`

Flow has TWO controls that are easy to confuse:

| Control | What it does | Required? |
|---------|--------------|-----------|
| `Advect` (toggle) | Activates particle-system advection by the velocity field | YES — without this, particles do nothing |
| `Solvermode` (enum: simple/advect) | Selects the integration algorithm | Yes |

**Both must be configured.** Setting `Solvermode='advect'` alone with `Advect=False` produces no particle motion. This was THE source of every "Flow looks dead" confusion.

### 6. POPX Geometry vs standard POP

POPX Geometry is a **packed structure** where each instance is represented as a single point carrying transform attributes (P, Orient, Scale, Pivot, popxId, etc.). Standard POP is the per-vertex/per-prim native form.

- Generators (Convert, Explode, Instancer) PACK standard POPs into POPX format
- `Unpack` and `popxto` UNPACK back to standard POPs
- `Apply Attributes` is the engine that materializes packed transforms onto downstream geometry
- `Extract Attributes` exports POPX transforms as standard `N`/`Up`/`Orient`/`Scale`/`Pivot`/`Euler` attrs for native TD ops (Copy to Points, Geometry COMP)

Modifiers operate on either form transparently. Use `popxto` whenever a native POP output (`trailPOP`, `particlePOP`, `sprinklePOP`) feeds into POPX modifiers — it normalizes the format.

---

## Modules

### Aim — orient instances toward a target point

**Example:** `touchdesigner/POPX_Examples_1_3_0/examples/aim.toe`

**Concept:** Aim/look-at modifier. For every instance in the input POP stream, compute an orthonormal frame from (target_dir, up_vector, axis convention) and apply it as instance rotation. Acts as a downstream rotation modifier — does not move instances, only rotates them.

**Pipeline position:** placed after an `Instancer` (or any POP with multiple points). Reads instance positions from input, writes rotation attributes to output.

**Inputs:**
- Input 0: POP — geometry to orient
- Input 1: POP — Aim target source (when `Aimmethod='points'`)
- Input 2: POP — Up target source (when `Upmethod='points'`)

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Aim | `Aimmethod` | **Three modes:** `'vector'` (aim toward a fixed direction vector), `'object'` (aim toward a single object's position), **`'points'` (each instance aims toward the corresponding point in the target POP at Input 1)** |
| Aim | `Aimaxis` | Local axis (X/Y/Z) that points toward target |
| Aim | `Invertaim` | Reverses aim direction 180° |
| Aim | `Aimposition1/2/3` | World-space target xyz (when `Aimmethod='vector'`/`'object'`). Common to drive via CHOP export. |
| Aim | `Aimvector1/2/3` | Forward direction vector (when `Aimmethod='vector'`) |
| Aim | `Displayaimguide`, `Aimguidescale`, `Aimcolorr/g/b` | Viewport guide — keep on while authoring |
| Up | `Upmethod` | **Three modes:** `'vector'` / `'object'` / `'points'` — same trio as Aim |
| Up | `Upaxis` | Local axis (X/Y/Z) for up orientation |
| Up | `Invertup` | Flip up direction |
| Up | `Upvector1/2/3` | World up direction (e.g. `(0,1,0)` for Y-up) when `Upmethod='vector'` |
| Up | `Displayupguide`, `Upguidescale`, `Upcolorr/g/b` | Viewport guide |
| Orientation | `Constrainaroundup` | If True: rotation restricted to up axis only (yaw-only — instances stay upright). If False: full 3D pointing. |
| General | `Dofalloff` | Enable per-instance partial-aim weighting |
| General | `Falloffattr` | Attribute name on the input POP that scales the aim effect (default `popxFalloff`). 0 = no rotation, 1 = full aim. |

**WOBAR application scenarios:**

- **Audio-driven gaze field** (Act 3 confrontation, Act 1 awareness) — populate a 3D grid of instanced geometry; drive `Aimposition1/2/3` from an audio CHOP export so the field tracks energy/transient peaks. Reads as "things looking at the listener" — aligns with Act 3 mirror principle and shadow work metaphor.
- **Camera-tracking decoration** — instanced ambient objects that subtly turn toward the camera as it drifts through a scene. Adds 3D presence without per-frame Python.
- **Returning-portal callback** (Act 5) — instanced ritual elements all rotate to face the closing portal as it shrinks. `Aimposition` = portal center, `Falloffattr` ramps from 0 → 1 as the act progresses.

**Replaces in our toolkit:** writing per-instance look-at rotation matrices via Script CHOP. Previously we'd have computed `cross(forward, up)`, normalized, decomposed to Euler — POPX does this on GPU with parameter-driven targets and visualization built in.

**Cost:** GPU, scales with instance count. No notes on perf cap yet (will measure if it shows up).

---

### Attribute To Index — discretize a continuous attribute into N integer index buckets

**Example:** `index from attribute.toe`

**Concept:** Bridge module. Takes a continuous attribute (default `popxFalloff`, range 0–1), divides the range into `Indexsteps` equal bands, writes a discrete integer index attribute (default `popxIndex`). Powers the multi-geometry instancing workflow where Instancer can swap between N different geometries based on per-instance index value.

**Pipeline position:** anywhere downstream of an attribute writer (Shape Falloff, Texture Falloff, Infection Falloff, etc.). Output feeds Instancer's `Indexattr` parameter.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Index | `Inputattr` | Continuous attribute to read. Default `'popxFalloff'`. **Any per-point attribute works** — `'Color'` (luminance/R), `'P(0)'` (x-position), `'N(1)'` (y-normal), custom user attrs. |
| Index | `Inputattrrange1/2` | Input range for normalization (e.g. 0–1, or audio-driven dynamic range) |
| Index | `Indexsteps` | Number of discrete index buckets |
| Index | `Indexstart` | First index value (default 0) |
| Index | `Outputattr` | Attribute to write (default `'popxIndex'`) |
| Index | `Debugcolor` | Color-code points by index for inspection (debug aid — disable for final render) |

**WOBAR application:** the bridge that enables falloff-driven multi-geometry instancing. See "Multi-Geometry Index-Based Instancing" in WOBAR Integration Patterns.

---

### Advect Modifier — advect points along a per-point vector attribute field

**Example:** `measure.toe`

**Concept:** Per-point advection through a vector attribute field. Distinct from `Noise Modifier` (noise displacement) and from `Flow.Solvermode='advect'` (fluid sim advection). Advect Modifier reads a per-point vector attribute (e.g. `'Dir'`) and integrates points along that field. Crucially, it can sample the field from **reference geometry** (`Advectsource='refgeo'`), so particles moving through space find their direction by looking up the field on a separate underlying mesh — enabling "particles flow across this surface" patterns.

**Pipeline position:** any modifier slot. Operates per particle. Typically downstream of a particlePOP and a field-providing geometry chain.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Advect | `Advectsource` | `'refgeo'` (sample field from reference geometry — `measure.toe`), `'ptattr'` (read directly from particle's own attribute — `noise advection.toe`), or `'self'` |
| Advect | `Advectattr` | Per-point vector attribute name (e.g. `'Dir'`, `'N'`, `'Gradient'`, `'Noise'`) |
| Advect | `Maxdistance` | Per-frame motion clamp |
| Advect | `Lookupmode` | `'avg'` (smooth — average over nearest neighbors) or `'nearest'` (sharp) |
| Advect | `Distribution`, `Maxptsavg` | Neighbor sampling strategy and count for averaging mode |
| Advect | `Timestep` | Integration timestep |
| Advect | `Rotateto` | Orient particles to face the flow direction (for visible alignment with flow) |
| Advect | `Feedbackpop` | Optional self-feedback POP for state accumulation |
| Advect | `Enablelife`, `Lifeseed`, `Lifespan`, `Lifevariance` | Particle lifetime (rebirth when expired) |
| Advect | `Passthroughattrs` | Comma-separated attributes to carry through advection |
| Advect | `Dofalloff`, `Falloffattr` | Standard falloff blending |

**WOBAR application:** see "Mesh-as-flow-field" pattern below. Any time you have a per-point vector field on a mesh and want particles to flow along it across the surface.

---

### Attribute Falloff — generate `popxFalloff` from any per-instance attribute via remap

**Example:** `motion instancer.toe`

**Concept:** The general-purpose "attribute → falloff" module. Reads any per-instance attribute, remaps via standard ramp/range chain, writes `popxFalloff`. Distinct from Texture/Shape/Infection Falloff (which generate the source attribute) — Attribute Falloff converts an EXISTING attribute into a standard falloff format that downstream modifiers can read.

**Pipeline position:** between any attribute writer (Trail's Age, audio-driven custom attributes, position-derived values) and downstream modifiers expecting `popxFalloff`.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Attribute | `Inputattr` | Attribute name to read (e.g. `'Age'`, `'Weight'`, custom names) |
| Falloff | (standard) | `Outputfalloffattr`, `Combineop`, `Combstrength`, `Previewfalloff`, `Fallofframp` |
| Noise | (standard) | Optional noise overlay |
| Remap | (standard) | Optional fit/clamp/ramp/invert |

**WOBAR application:** the bridge between any custom attribute and the standard POPX falloff system. Trail age, audio-driven attributes, custom user attributes, position components — anything you've written or inherited can become a falloff that drives downstream Transform/Color/Noise/etc modifiers.

---

### Color Modifier — per-instance color via attribute → ramp lookup

**Example:** `magentize.toe`

**Concept:** POPX color-application module. Reads any per-instance scalar attribute and maps it through a Ramp TOP (used as a 1D LUT) to assign per-instance Color. Standard "color by behavior" / heatmap-style visualization tool.

**Pipeline position:** any modifier slot, typically near end of chain. Writes per-instance Color attribute that downstream rendering uses.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Color | `Group` | Optional point group filter |
| Color | `Falloffattr` | Attribute to read for ramp lookup. Default `'popxFalloff'`. Common values: `'Weight'` (from Magnetize), `'popxFalloff'` (from any falloff module), `'popxIndex'` (from Attribute To Index — gives stepped colors). |
| Color | `Ramptop` | TOP used as 1D color lookup (0–1 input → RGBA output). Wire any animated/audio-reactive Ramp TOP for dynamic color schemes. **Per docs: ramp can be the internal editor OR an external Ramp TOP reference** — both paths are first-class. The internal editor is fine for static palettes; external Ramp TOP wins when you want to animate the gradient itself. |

**WOBAR application:**
- **WOBAR brand-palette ramp** — author a 1024×1 Ramp TOP with brand purple/black/etc keyframes; wire to any Color Modifier; all per-instance attribute → brand-palette mapping.
- **Visualize behavior, not state** — read `Weight` from Magnetize → only magnetized instances are colored, idle ones stay neutral. The visual shows where the action is.
- **Audio-reactive ramp scrolling** — the `Ramptop` itself can be audio-reactive (animated phase, scrolling LUT). Color mapping shifts with the music.

---

### Convert — turn regular geometry into POPX-packed instances by detecting pieces

**Example:** `convert.toe`

**Concept:** Architecturally critical module. Takes a single POP mesh and partitions it into N addressable POPX instances, either by **spatial connectivity** (flood-fill across topology) or by **attribute value**. Without Convert, downstream POPX modifiers can't address visually-distinct parts of a mesh independently — a mesh with 4 disconnected silhouettes is just one continuous POP stream.

**Pipeline position:** between native-POP source (e.g. `tracePOP`, `fileinPOP`, hand-built mesh) and any POPX modifier chain. `Convert → TextureFalloff → Spring → Transform` is the canonical "image-as-instances" pipeline.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Convert | `Partitionmethod` | `'connectivity'` (auto flood-fill on topology) or `'attribute'` (use existing attr value) |
| Convert | `Inputpointcount` | Read-only — input point count, useful for sanity checking |
| Convert | `Piecesdetected` | Read-only — number of pieces found |
| Convert | `Minpointsperpiece` | Discard pieces smaller than this — noise floor (default 5) |
| Convert | `Searchpasses` | Connectivity flood-fill iteration depth (higher = more reliable on complex meshes; this example used 140) |
| Convert | `Attribute`, `Attrclass`, `Pieceattr` | When `Partitionmethod='attribute'`: which attribute defines piece membership |
| Convert | `Transferattrs` | Glob — which input attributes propagate to pieces (`*` = all) |
| Convert | `Generatenormals`, `Maxprimsperpoint`, `Angle` | Normal generation options |
| Convert | `Visualizepieces`, `Visualizationseed` | Debug — color-code each piece for inspection |

**WOBAR application:**
- **Multi-shape image → individually-animated instances** — threshold a brand mark / set of glyphs → `tracePOP` polygonizes → Convert(connectivity) → each glyph is a separate instance with its own falloff, spring, transform behavior. Powers "brand mark deconstruction" or "letterform scatter" Act visuals.
- **Imported multi-part OBJ → per-part control** — load OBJ with multiple mesh objects (face + body, hand + arm), Convert(attribute) using a material/group ID = each named subobject becomes an instance.

**Mac/Win shader caveat:** Convert ships with platform-specific GLSL POP variants (`avg_win`/`sum_win` for Windows, `avg_mac`/`sum_mac` for Mac). On Mac you'll see "Compile failed" errors on the `_win` variants — these are inactive on Mac and harmless. POPX selects the correct variant at runtime. Don't try to fix the `_win` shaders.

---

### popxto — convert native POP output into POPX-packed format

**Example:** `motion instancer.toe`

**Concept:** Bridge module that takes data from native TD POPs (`trailPOP`, `particlePOP`, `sprinklePOP`, etc.) and packs it into POPX-compatible format with the right attribute structure. Required when inserting POPX modifiers downstream of native POP operators.

**Pipeline position:** between native POP outputs and POPX modifier chains.

**Key parameters:** minimal — typically just attribute remapping settings. Acts as a passthrough format converter.

**WOBAR application:** any time you want POPX modifiers (Attribute Falloff, Transform Modifier, Color Modifier, etc.) downstream of native POP operators (Trail, Particle, Sprinkle). Insert `popxto` to bridge the formats. Most common use: trailPOP outputs → popxto → POPX falloff/instancer chain.

---

### Unpack — convert instanced output into raw POP geometry

**Example:** `move along curve 4.toe`

**Concept:** Bridge module. Instancer outputs are abstract "instances of geometry" (instance positions/transforms referring to source POPs). Unpack evaluates those instances and produces actual evaluated geometry as a single POP cloud — raw points/topology that downstream operations can consume.

**Pipeline position:** between an Instancer (or any module producing instances) and downstream operations that need raw geometry. Common after an Instancer when feeding the result as curves/seeds/templates to another solver.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `Applytransform` | Bake per-instance transforms (xforms from upstream modifiers) into output point positions. Default True. |
| `Transferattrs` | Comma-separated attributes to propagate from instance metadata into unpacked geometry (e.g. `'popxFalloff'`, `'*'` for all) |
| `Transfergroups` | Propagate group memberships |

**WOBAR application:** any time you need raw geometry from an Instancer's output. Most common: instanced circles/lines from Stage 1 become CURVES for Stage 2's MoveAlongCurve. Without Unpack, the curve-input expects raw geometry but receives instance abstractions.

---

### Path Tracer + POPX Material + POPX Light — physically-based raytraced rendering pipeline

**Example:** `path tracer (spheres).toe`

**v1.3.0 BREAKING CHANGES:**
- Path Tracer's **Voxel Tracer is REMOVED**
- Path Tracer's **built-in Material/Lights pages are REMOVED** — now requires a separate **POPX Light** component connection
- POPX Light adds an **Environment Light type** for HDR image-based lighting
- POPX Material **`Subsurface` parameter is REMOVED**; renamed parameters follow updated PBR conventions
- POPX Material adds a **Maps page** with texture inputs (normal, metallic/roughness, emission), **Clearcoat**, and **Emission** parameters
- POPX Material has **Substance integration** (auto-texture assignment from Substance TOPs)
- Realtime/offline modes; NVIDIA DLSS denoiser support added
- Disney BRDF compliance for Material

**Concept:** POPX provides a **complete physically-based path-traced rendering pipeline** parallel to TD's standard rasterized rendering. Three cooperating modules:
- **POPX Material** — assigns Disney BRDF (PBR) attributes per-instance via point/primitive/vertex attributes
- **POPX Light** — extended light type system: area, point, directional, spot, **environment (HDR IBL)**
- **Path Tracer** — Monte-Carlo path tracer with denoiser, depth-of-field, motion blur

Quality jumps significantly from the rasterized look — true reflections, true soft shadows, true global illumination, true environment lighting. **For music video renders / hero stills, not live performance** (too slow for sustained 60fps).

---

#### Path Tracer (renderer)

| Page | Parameter | Purpose |
|------|-----------|---------|
| Path Tracer | `Rendermode` | `'realtime'` (incremental refinement) or alt |
| Path Tracer | `Refinesamples`, `Maxrefinesamples` | Progressive refinement (more samples = cleaner but slower) |
| Path Tracer | `Rendertop` | Source renderTOP — the rasterized scene the path tracer uses as guide |
| Path Tracer | `Raysperpixel` | Rays per pixel per frame (5 typical for realtime) |
| Path Tracer | `Maxbounces` | Max ray bounce depth (5 typical; 10+ for caustics) |
| Path Tracer | `Renderemissives` | Emissive materials emit light |
| Path Tracer | `Enablefireflyclamp`, `Fireflyclamp` | Suppress bright stray Monte-Carlo noise pixels |
| Path Tracer | `Dof`, `Focallength`, `Aperture`, `Showfocalplane`, `Focalplanesize` | Depth of field |
| Path Tracer | `Motionblur`, `Enablemotionblur`, `Blurstrength`, `Blursamples` | Motion blur |
| Path Tracer | `Enabletonemap`, `Exposure`, `Gamma` | Tonemapping |
| Denoiser | `Denoiser` | `'svgf'` (Spatiotemporal Variance-Guided Filter — cross-platform, **use this on Apple Silicon**) or `'optix'` (NVIDIA OptiX via DLL plugin — **NVIDIA RTX only, does not work on Mac**) |
| Denoiser | `Temporalreprojection`, `Usemotionvectors`, `Normalreject`, `Depthreject`, `Albedoreject` | Temporal reuse + bad-sample rejection |
| Denoiser | `Diffusehistoryblend`, `Specularhistoryblend`, etc. | Per-channel temporal filter |
| Denoiser | `Diffpasses`, `Specpasses`, `Smoothreflections` | Spatial filter passes |

#### POPX Material (Disney/Principled BSDF per-instance)

| Parameter | Purpose |
|-----------|---------|
| `Attrclass` | `'point'` etc. |
| `Basecolorr/g/b` | Albedo |
| `Metallic` | 0=dielectric, 1=metal |
| `Roughness` | 0=mirror, 1=fully diffuse |
| `Specularlevel`, `Speculartintr/g/b` | Specular F0 + tint |
| `Anisotropiclevel`, `Anisotropicangle` | Anisotropic specular (brushed metal, hair) |
| `Sheenlevel`, `Sheentintr/g/b` | Sheen (fabric, velvet) |
| `Clearcoatlevel`, `Clearcoatroughness`, `Clearcoattintr/g/b` | Clearcoat (car paint) |
| `Ior`, `Thickness`, `Transmission`, `Dispersion` | Glass/refraction |
| `Absorptioncolorr/g/b` | Beer-Lambert absorption (colored glass) |
| `Emissionlevel`, `Emssioncolorr/g/b` | Self-emission |
| `Maps.*` | Texture maps for every PBR channel (Substance, Basecolor, Metallic, Roughness, Specular, Anisotropic, Sheen, Clearcoat, Transmission, Emission, Normal) |

**The killer feature:** any per-instance attribute (e.g. `popxFalloff`) can drive material parameters. Per-instance PBR variation without authoring N materials. Example: row of spheres where `Roughness` is driven by `popxFalloff` (0→1 across the row) → first sphere mirror-smooth, last sphere rough.

#### POPX Light (extended light types)

POPX wrapper around lightCOMP adding path-tracer-specific light types.

| Parameter | Purpose |
|-----------|---------|
| `Type` | `'area'` (rectangular soft area light), `'env'` (environment map IBL), `'point'`, etc. |
| `Colorr/g/b`, `Dimmer` | Color + intensity |
| `Bidirectional` | Light works both directions |
| `Volsteps`, `Voldensityscale` | Volumetric scattering through participating media |
| `Texturemap` | Texture for env light (IBL HDRI) or projected light pattern |
| `Envlightmaprotatex/y/z` | Rotate environment map |
| `Attenuated`, `Attenuationstart/end/exp` | Distance attenuation |

Standard PBR studio setup: one `Type='area'` light (key + shadows) + one `Type='env'` with HDRI texturemap (image-based ambient).

**WOBAR application:**
- **Final music video renders** — replace procedural refraction shader on glass orb with POPX Material (Transmission=1.0, IOR=1.5) + Path Tracer. True caustics, soft shadows, real environment reflection.
- **Hero stills / album art** — slow renders are fine; quality jumps to "real product photo" level.
- **Per-instance material variation** — drive Roughness/Metallic/Emission from audio energy across an instance field; path-traced output looks photographic.

**PBR Material recipe library** (from `path tracer materials.toe`):

| Recipe | Pars | Look |
|--------|------|------|
| **Anisotropic metal** (brushed metal / hair) | `Metallic=1.0, Roughness=1.0, Anisotropiclevel=1.0, Anisotropicangle=1.0` | Streaked highlights along anisotropic angle |
| **Clean reflective metal** | `Metallic=1.0, Roughness=0.066, Normalmap=<noise normal>` | Mirror-like with subtle surface texture |
| **Colored glass with absorption** | `Transmission=1.0, Thickness=0.35, Absorptioncolor=<tint>` | Tinted glass — color depth depends on thickness traversed |
| **Clearcoat over rough base** (car paint, lacquer) | `Roughness=1.0, Specularlevel=0.657, Clearcoatlevel=1.0, Clearcoattint=<colored coat>` | Layered: rough base + glossy colored coating on top |
| **Texture-mapped chrome** | `Metallic=1.0, Roughness=0.012, Basecolormap=<image>, Normalmap=<normal>` | Mirror with image albedo + surface detail |
| **Emissive with color** | `Roughness=1.0, Emissionlevel=10.0, Emssioncolor=<tint>` | Self-illuminated; emits light into the scene |
| **Substance integration** (single-source-of-truth) | `Maps.Substance=<substanceTOP>` | All channels (basecolor/metallic/roughness/normal/etc.) from one Substance file |

**Cost:** Path tracing is GPU-heavy. Realtime mode at 5 rays × 5 bounces × 720×1280 with SVGF denoiser is ~30fps on Apple Silicon NC. Increase samples for export quality, accept lower fps. **Not for live performance** — for renders only.

---

### Voxelize — convert geometry into a 3D voxel grid (density / surface / SDF) + voxel-center point cloud

**Examples:** `flow (interactive).toe` (Flow injection bridge); **`voxelize.toe`** (voxel-art instancing — Minecraft-style box rendering of any mesh)

**Concept:** Bridge module that turns a POP geometry stream into a volumetric grid. Used primarily to feed Flow injection (Flow consumes voxel grids as substance/density sources), or to convert dynamic geometry into 3D textures for raymarching, custom shaders, or caching.

**Pipeline position:** between any POP source and Flow's `in1` (substance source) input, or as a standalone "geometry to volume" converter.

**Inputs:**
- `in0` — POP geometry to voxelize

**Outputs (4 ports per official docs):**
- Output 0: **Volume** (TOP) — main voxelized volume representation
- Output 1: **Surface** (TOP) — surface shell extraction
- Output 2: **SDF** (TOP) — signed distance field (when `Outputsdf=True`)
- Output 3: **Hit Attributes** (POP) — ray-casting hit data (mesh mode only); contains `Inside` attribute usable with `geometryCOMP.par.instanceactive='Inside'` for "draw cubes only where they're inside the source mesh" voxel-art rendering

**Two voxelization modes per docs:**

| `Voxelizemode` | Behavior | Use case |
|----------------|----------|----------|
| `'mesh'` | Geometry voxelized via ray casting to determine interior/exterior. Generates the Hit Attributes POP output. | Voxel-art rendering, mesh-to-SDF, Flow obstacle field |
| `'pointcloud'` | Individual points converted directly into voxel density values | Substance injection from POP into Flow |

(The "surface" / "sdf" modes referenced in v1.0 of this guide were toggle params on top of the mesh mode — `Outputsurface`, `Outputsdf` — not separate Voxelizemode values. Reconciled with docs v1.3.0.)

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Voxelize | `Voxelizemode` | One of pointcloud / surface / sdf |
| Voxelize | `Maxaxisresolution` | Voxel grid resolution (auto-scales other axes) |
| Voxelize | `Lowerboundsx/y/z`, `Upperboundsx/y/z` | Sim domain — match Flow's sim bounds for clean injection |
| Voxelize | `Margin` | Padding around bounds |
| Voxelize | `Outputvolume`, `Outputsurface`, `Outputsdf` | Which output to generate (can combine). **`Outputsdf=True` with `Voxelizemode='mesh'`** produces a 3D signed-distance-field TOP — the canonical input for `Relax.Collisontop` (Collisiontype='t3d') and other 3D-collision-bounded solvers. |
| Voxelize | `Surfacethreshold`, `Smoothness` | Surface/SDF tuning |
| Voxelize | `Pointscale` | Radius around each point that contributes to voxels |
| Voxelize | `Densityscale` | Multiplier on output density |
| Voxelize | `Enablemaxpointcount`, `Maxpointcount` | Budget cap |
| Voxelize | `Raydirmode`, `Raydirx/y/z` | (For SDF mode?) ray direction for distance computation |
| Voxelize | `Colorr/g/b`, `Bgcolor*`, `Bgalpha` | Color tint applied to voxelized output |
| Voxelize | `Displaybounds` | Visualize the voxel domain |

**WOBAR application:**
- **Voxelize a brand mark for Flow injection** — load WOBAR wordmark via fileinPOP → tracePOP → Voxelize(pointcloud) → Flow.in1 with `Inject=True`. Wordmark dissolves into smoke through the simulated fluid.
- **Voxelize an audio-reactive POP** — generate POP positions from audio analysis, voxelize, inject into Flow → audio "draws into" the fluid.
- **Voxelize a DLA structure** — coral grown by DLA becomes a volumetric density that can be rendered with raymarching shaders or used as Flow obstacle.
- **Voxel-art rendering** — any mesh → Voxelize(`Voxelizemode='mesh'`, `Maxaxisresolution=32`, `Outputvolume=True`) → output[3] (voxel-center POP) → instance boxes at those points with `geometryCOMP.par.instanceactive='Inside'`. Minecraft-style chunky rendering of any geometry. WOBAR variants: voxelized brand mark on the drop, voxelized character / dancer silhouette, voxel-shatter (Voxelize → randomize Color → animate per-voxel scale via Transform Modifier + audio falloff = chunky audio-reactive cube cloud).

**Canonical voxel-art pipeline (`voxelize.toe`):**

```
mesh (sphere / sweep / brand mark / anything)
    → Voxelize(Voxelizemode='mesh', Maxaxisresolution=32,
              Outputvolume=True, Margin=0.1,
              Getbounds.expr=ResetPulse — auto-recompute bounds on reset)
    → output[3] (voxel-center POP with Inside attribute)
    → randomPOP (per-voxel jitter, color seed)
    → lookuptexturePOP (sample ramp TOP at per-voxel attr → write Color)
    → mathmix / null
    → geometryCOMP(instanceop=null, instancing=True,
                  instanceactive='Inside',          ← only render Inside voxels
                  instancetx/ty/tz='P(0..2)',
                  instancer/g/b='Color(0..2)')
       template: boxPOP
    → render
```

**The `instanceactive='Inside'` trick** is what separates voxel-art from a full bounding-box grid of boxes. Voxelize writes per-voxel `Inside` (1 = inside source mesh, 0 = outside); the geometryCOMP only draws boxes where Inside=1.

**Cost:** scales cubically with `Maxaxisresolution`. 32³ ≈ 33k voxels (real-time). 64³ ≈ 260k. 128³ ~2M voxels (heavy). Match Flow's voxel resolution to avoid resampling.

---

### Explode — break a continuous mesh into clustered POPX instances (Voronoi / perprim partitioning)

**Example:** `explode curl.toe`

**Concept:** Like Convert (detects pre-existing pieces via connectivity), but for a single continuous mesh. Imposes new pieces via spatial partitioning — Voronoi tessellation is the default and produces natural-looking shards. Each output piece is an addressable POPX instance with position, orientation, and a cluster of source primitives.

**Pipeline position:** between fileinPOP/source mesh and any POPX modifier chain. The "destruction" counterpart to Convert's "discover pieces" — used when you want to artificially shatter, not detect existing parts.

**Inputs:**
- `in0` — source mesh POP

**Output:**
- POP with N piece-instances, each with computed center position, orientation (from source normals), and grouped source primitives

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Explode | `Partitionmethod` | `'voronoi'` (3D Voronoi shards), alt: `'connectivity'`, `'attribute'`, etc. |
| Explode | `Scattermethod` | `'perprim'` (cluster centers per primitive) or alt |
| Explode | `Numberofclusters` | Target number of pieces |
| Explode | `Maxpoints`, `Maxtriangles` | Capacity caps for the partitioning |
| Explode | `Maxdistance` | Spatial hash query radius |
| Explode | `Numhashbuckets` | Spatial hash performance tuning |
| Explode | `Clustering`, `Clustersseed` | Optional clustering attribute + RNG seed |
| Explode | `Visualizepieces`, `Visualizationseed` | Debug — color-code each piece |
| Orient | `Computesourceorient` | Compute per-piece orientation from original mesh normals (default True — important for downstream rotation modifiers to make sense) |
| Orient | `Generatenormals`, `Maxprimsperpoint`, `Angle` | Normal generation if missing |
| Orient | `Usecustomupvector`, `Customupvectorx/y/z`, `Invertn`, `Invertup` | Override the up vector convention |

**WOBAR application:**
- **Mesh shattering** — explode any imported mesh (brand mark, performer silhouette, sculpted form) into addressable shards. Pair with Infection Falloff + Noise Modifier + Transform Modifier for the full disintegration chain.
- **Voronoi-textured surfaces** — even without animating the pieces, a Voronoi-exploded mesh is a valid aesthetic — pieces with subtle gaps reads as cracked pottery, faceted gemstone, lattice structure.

**Cost:** Voronoi partitioning of 1M-point mesh into 2000 clusters runs at ~5 fps in this example. Heavy. For live-rate use, either reduce mesh density (decimate before Explode) or reduce cluster count, or pre-bake the explosion (run once, freeze with `Play=False`).

---

### Infection Falloff — propagate a falloff value from seed points across instances over time

**Example:** `explode curl.toe`

**Concept:** Viral-propagation solver. Writes per-instance `popxFalloff` that spreads from a configurable seed point/POP across nearby neighbors, with controllable rate, threshold, resistance, dissipation. State accumulates frame-by-frame — creates a wavefront that moves through the geometry over time.

**Distinct from Texture Falloff:** Texture Falloff samples a (static or animated) TOP at point positions. Infection Falloff is a temporal solver where values spread between instances based on proximity/connectivity.

**Distinct from DLA:** DLA aggregates new points by walker collision. Infection Falloff infects existing points by neighbor proximity. DLA grows structure; Infection Falloff stains existing structure.

**Pipeline position:** downstream of any module producing a stream of instances. Writes to `popxFalloff` (or custom attribute) that downstream modifiers respect.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Infection | `Infectby` | `'radius'` (proximity-based) or alt |
| Infection | `Distribution` | `'closest'` — propagate to closest neighbors first; alt: random, etc. |
| Infection | `Searchradius` | Proximity threshold for neighbor detection |
| Infection | `Maxconnections` | Max neighbors each infected instance can spread to per frame |
| Infection | `Infectionrate` | Spread strength (0–1) |
| Infection | `Distweight`, `Weightamount` | Weight infection by distance to seed |
| Infection | `Dissipationrate` | Per-frame falloff decay (0 = stays infected, >0 = recovers) |
| Infection | `Enablereinfection` | Allow re-infection after dissipation |
| Infection | `Threshold`, `Resistance` | Propagation thresholds |
| Infection | `Play` | Pause/resume |
| Seed | `Positionx/y/z`, `Radius` | Initial infection seed position + radius |
| Seed | `Useseedattr`, `Seedattr` | Read seed flag from attribute |
| Seed | `Seedpop` | Use a POP as seed positions (multiple simultaneous seed points). Wire POP into `infection_falloff1.in1`. Each point becomes a seed. Optional per-point `radius` attribute on the seed POP controls each seed's influence area independently — heterogeneous seed sizes in one module. |
| Seed | `Transitionrange`, `Transitionalign`, `Transitiontype` | Soft seed boundary characteristics |
| Falloff | (same as Texture Falloff) | `Outputfalloffattr`, `Combineop`, `Combstrength`, viz |
| Noise | (same as Texture Falloff) | Optional noise overlay |
| Remap | (same as Texture Falloff) | Optional fit/clamp/ramp |

**Two distinct operating modes:**

1. **One-shot wavefront** (`convert.toe`-style) — `Dissipationrate=0`, `Enablereinfection=False`. Infection spreads once and stays. Use for "permanent transformation passing through" effects (e.g. dissolution that doesn't reverse).

2. **Continuous evolution** (`infection falloff (interactive).toe`-style) — `Dissipationrate>0` (e.g. 1.0 = 1 unit of decay per second), `Enablereinfection=True`. Cells fade back to uninfected after seed leaves; can be re-infected when seed returns. Use for "live painting" effects where the seed continuously moves and the field continuously evolves.

**WOBAR application:**
- **Audio-driven infection seed** — drive `Seed.Positionx/y/z` from an audio CHOP (kick triggers a new seed location); infection spreads from kick locations.
- **Cursor-driven live painting** — `cursor.insideu/insidev → Seed.Positionx/y` via expression, with continuous-evolution config. Performative.
- **Time-progression mask** — over an Act's duration, slow seed motion creates a wavefront sweeping through the instance grid; downstream modifiers (Transform, Noise, Color) animate as it passes.
- **Beat-synced re-infection rhythm** — `Dissipationrate` and `Maxconnections` scale with audio (high decay quiet, slow decay drop, etc.) — infection behavior breathes with the music.

**Replaces in our toolkit:** custom GLSL POP propagation solvers, attribute-flooding compute shaders.

---

### Mesh Fill — volume-filling trail solver constrained by a mesh

**Example:** `mesh fill.toe`

**Concept:** Volumetric trail solver constrained to the interior of a mesh. Sends trail-like paths growing from seed points; trails respect the mesh boundary by construction (the bounding volume IS the input mesh). Over time, trails fill the interior with dense organic threading. Imagine pumping a thread into the mesh until the whole interior is packed.

**Distinct from:**
- **DLA** — grows outward in unconstrained space; aggregation pattern
- **DLG** — lines pack in 2D space with self-avoidance; brain-coral pattern
- **Flow** — fluid simulation in a box bound; smoke/ink behavior
- **Mesh Fill** — fills the inside of a specific mesh shape; volumetric trail packing

**Pipeline position:** standalone solver. Builds a voxel grid sized to the input mesh. Outputs trail line POP + optionally a sampled volume field.

**Inputs:**
- `in0` — the mesh whose interior gets filled
- `in2` — seed POP (typically `sprinklePOP + randomPOP` on the mesh surface)

**Output:**
- POP with trail line topology (visible threads)
- Sampled volume field (if `Lookupfilledvol=True`) for downstream use

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Mesh Fill | `Maxaxisres` | Voxel grid resolution (default 64; cubic cost) |
| Mesh Fill | `Lowerboundsx/y/z`, `Upperboundsx/y/z` | Sim domain (auto-fit to mesh extent) |
| Mesh Fill | `Margin`, `Normalizeinputmesh` | Domain padding + auto-normalize |
| Mesh Fill | `Raydirmode`, `Raydirx/y/z` | Ray direction for inside/outside testing |
| Mesh Fill | `Precision` | `'16-bit float'` (default) or 32-bit |
| Mesh Fill | `Fillsurface` | Fill mesh surface (True) or interior only (False, default) |
| Mesh Fill | `Radius` | Trail thickness |
| Mesh Fill | `Size`, `Filterscale` | Trail filter scale |
| Mesh Fill | `Retention` | How much of each frame's growth is retained (small = thinner trails, larger = thicker accumulation) |
| Mesh Fill | `Stopthreshold` | Termination threshold (when growth slows below this, stop) |
| Mesh Fill | `Continuoussim` | Continuous simulation (vs single fill run) |
| Mesh Fill | `Timestep`, `Play` | Time control |
| Mesh Fill | `Switchtovol`, `Displaybounds` | Visualization toggles |
| Seed | `Spawn` | Auto-spawn seeds (vs use input seed POP) |
| Seed | `Seedcount`, `Seed`, `Maxattempts` | Seed control |
| Trails | `Enabletrails` | Trails are visible output (vs just volume) |
| Trails | `Length` | Temporal trail length (frames) |
| Trails | `Filtertype` (`'gaussian'` etc.), `Filterdist`, `Effect` | Trail topology smoothing |
| Trails | `Endpointsfixed` | Pin trail endpoints |
| Lookup | `Lookuptrails`, `Sizetrials`, `Preshrinktrials`, `Applyblurtrails` | Trail-output sampling controls |
| Lookup | `Lookupfilledvol`, `Sizevol`, `Preshrinkvol`, `Applyblurvol`, `Outputinverted` | Volume-output sampling controls |
| Lookup | `Lookupoffsetx/y/z`, `Lookupscalex/y/z` | Sampling transform |
| Lookup | `Debug` | Debug output toggle |

**WOBAR application:**
- **Brand mark interior dissection** — extrude WOBAR wordmark into 3D mesh, Mesh Fill threads through letterform interiors. Brand looks veined.
- **Body interior reveal** — performer pose mesh threaded with internal trails. Strong shadow-work metaphor.
- **Mycelium aesthetic** — any organic mesh (mushroom, root, anatomy) interior-filled = direct Act 2 mycelium look.
- **Glass orb interior structure** — pre-bake a Mesh Fill of a smaller shape inside the orb; threads provide visual depth for the motes to ride along.

**Cost:** voxel grid scales cubically with `Maxaxisres`. 64³ ≈ 262k voxels — runs OK on Apple Silicon NC. Bumping to 128³ multiplies cost 8×.

**Replaces:** custom volumetric path-finding shaders, Houdini-style space colonization algorithms.

---

### Physarum — slime mold network simulation (2D or 3D)

**Example:** `physarum 2d.toe`

**Concept:** Implements the **Physarum slime mold algorithm** — particles deposit pheromone trails as they move, sense their environment ahead via 3-sensor steering (left/center/right), and turn toward stronger pheromone concentrations. Result: emergent network patterns identical to real biology — vascular networks, mycelium, neuron networks, transit maps, cellular foam. Rules are 4 lines of math; output is profound.

**Pipeline position:** standalone solver. Inputs particle stream (`in0`) + optional bounds TOP (`in1`). Outputs current particle positions (POP) and accumulated pheromone trail (TOP).

**Two operating spaces:**
- `Simspace='2d'` — flat slime mold pattern. Higher per-axis resolution (1080² typical), 250k particles, lower per-step movement and rotation. 60fps live on Apple Silicon NC.
- `Simspace='3d'` — volumetric slime mold. Lower per-axis resolution (128³ typical), more particles (550k+), larger rotations (45° base vs 18°) and smaller move steps to navigate 3D space. ~30fps on Apple Silicon NC. **Different aesthetic from 2D extrusion** — true volumetric mycelium / neuron-cloud / vascular-tree look. Best viewed with camera motion and depth cues (lighting/fog) — static frontal camera angles look like noise.

**2D vs 3D parameter recipes:**

| Parameter | 2D recipe | 3D recipe |
|-----------|-----------|-----------|
| `Simspace` | `'2d'` | `'3d'` |
| `Maxaxisres` | 1080 (high detail) | 128 (volumetric tradeoff) |
| `Numberofparticles` | 250k | 550k+ |
| `Movedistancebase` | 0.28 | 0.1 (smaller 3D steps) |
| `Rotationanglebase` | 18° | 45° (sharper 3D turns) |
| Use case | Flat detail networks | Volumetric clouds / immersive 3D fields |

**Key parameters by page:**

**`[Physarum]` — sim setup**

| Parameter | Purpose |
|-----------|---------|
| `Particlesupdatepop`, `Trailupdatetop` | Optional feedback POP/TOP for state |
| `Simspace` | `'2d'` or `'3d'` |
| `Maxaxisres`, `Simresx/y/z` | Grid resolution (higher = finer network) |
| `Boundssizex/y/z` | Sim domain extent |
| `Boundstype1/2/3` | Per-axis boundary: `'loop'`, `'clamp'`, etc. |
| `Numberofparticles` | Particle count (250k typical for dense networks) |
| `Seed`, `Pointsize` | Initialization + render size |

**`[Sense]` — sensor controls** (WHERE particles look ahead)

| Parameter | Purpose |
|-----------|---------|
| `Sensordistancebase/power/scale` | How far ahead particles sense — KEY parameter for network scale (small = fine detail; large = broad network) |
| `Sensoranglebase/power/scale` | Angular spread of 3 sensors (typically ~22.5° each side of center) |

**`[Move]` — turning + stepping**

| Parameter | Purpose |
|-----------|---------|
| `Rotationanglebase/power/scale` | Turn rate per frame toward strongest pheromone |
| `Movedistancebase/power/scale` | Step size per frame |

**`[Diffuse]` — pheromone trail evolution**

| Parameter | Purpose |
|-----------|---------|
| `Decay` | Trail fade rate per frame (0.25 typical) |
| `Diffusepasses` | Blur passes per frame on the trail |
| `Type`, `Extend`, `Size`, `Filterscale*`, `Offsetx/y/z` | Diffusion filter params |

**`[Constraint Volume]` — TOP-defined bounds (CRITICAL)**

| Parameter | Purpose |
|-----------|---------|
| `Constrainttovolume` | Master enable |
| `Constraintvolume` | TOP defining bounds — bright pixels allow growth, dark blocks |
| `Forcestrength`, `Preshrink`, `Filtersize` | Constraint enforcement |

The `Constraintvolume` TOP can be ANY animated source: audio FFT visualization, painted user input, brand mark, performer silhouette extraction. Animatable in real time.

**WOBAR application — extremely on-brand:**
- **Act 2 DESCENSION mycelium** (2D) — track naming already includes MYCELIUM. Physarum IS the literal-form of mycelium. Subtle desaturated palette + slow decay = network grows over the act.
- **Volumetric mycelium for Act 2** (3D) — true 3D mycelium network growing through space, camera orbits through it. More immersive than 2D variant.
- **Inside-the-orb Physarum** (3D) — small 3D sim sized to glass orb interior. Through the orb's refraction, the volumetric network reads as a captured living organism.
- **Brand mark constraint** (2D) — `Constraintvolume = WOBAR_wordmark_TOP` → physarum grows only inside wordmark letters. Brand mark self-organizes from biological growth.
- **Audio-reactive constraint** — animate the constraint TOP from audio energy bins → physarum responds to music by changing where it can grow.
- **Performer silhouette as container** — webcam → silhouette → constraint → physarum grows in/on performer's body.

**Cost:** scales with particle count × sim resolution. 250k particles at 1080² 2D runs at 60fps on Apple Silicon NC. Bumping to 3D space significantly increases cost.

**Replaces:** custom GLSL Physarum shaders, GPU compute Physarum implementations.

---

### Relax — point distribution solver (push points apart for even spacing)

**Example:** `point relax (Mac).toe`

**Concept:** Iterative solver that pushes points away from each other to achieve a minimum-spacing / even-density distribution. Like Lloyd's algorithm or particle relaxation. Points start clumped (from sprinkle/random scatter); Relax spreads them until they reach `Maxrelaxradius` from every neighbor. Combined with TOP-defined collision boundary (typically Voxelize SDF output), produces uniform point distribution INSIDE any mesh.

**Distinction from Mesh Fill:** Mesh Fill grows TRAIL paths through interior. Relax distributes individual POINTS evenly. Both fill mesh interiors with different visual signatures:
- Mesh Fill → threading / vein-like / mycelium
- Relax → uniform point distribution / cellular packing

**Pipeline position:** standalone solver. `in0` = particle stream; outputs relaxed positions.

**Two solver modes:**
- `Solvermode='advect'` — state-accumulating per-frame relaxation
- `Solvermode='simple'` — one-shot non-stateful

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Relax | `Solvermode` | `'advect'` or `'simple'` |
| Relax | `Relaxmethod` | `'nebr'` (neighbor-based via spatial hash) or alt (field-based) |
| Relax | `Pointsupdatepop` | Feedback POP for state |
| Relax | `Affectposition` | Apply relaxation to positions |
| Relax | `Relaxiters` | Iterations per frame (more = faster convergence, slower) |
| Relax | `Overrideradius`, `Radiusaxis`, `Radiusscale` | Per-point radius override |
| Relax | `Maxrelaxradius` | Effective per-point repulsion radius |
| Relax | `Distribution` (`'closest'`), `Numhashbuckets`, `Maxneighbors` | Neighbor-lookup strategy |
| Relax | `Maxaxisres`, `Kernelsize`, `Fieldlowerboundsx/y/z`, `Fieldupperboundsx/y/z` | Field-method grid params + domain |
| Relax | `Relaxstrength` | Per-frame push strength (0.05 typical) |
| Relax | `Attractpositionx/y/z`, `Attractstrength` | Optional attractor toward a point — combine attract + relax for "spread evenly while gathered toward a region" |
| Relax | `Outputforceattribute` | Optional force attribute writeback |
| Relax | `Displayradius` | Visualize repulsion radius per point |
| Relax | `Play` | Pause/resume |
| Collisions | `Collisiontype` | `'t3d'` (3D TOP texture / SDF) — new variant. Also `'pop'` (mesh) and shape primitives. |
| Collisions | `Collisontop` | 3D TOP (typically Voxelize SDF) defining boundary |
| Collisions | (full collision params, same as POPX Particle) | Standard collision system |

**WOBAR application:**
- **Brand-mark uniform fill** — WOBAR wordmark mesh → sprinkle → voxelize SDF → relax. Render relaxed points as small spheres = "wordmark filled with constellation."
- **Body-shape character fill** — performer pose mesh → relaxed point cloud inside silhouette. `Maxrelaxradius` audio-driven for packed/sparse pulsing.
- **Glass-orb interior** — small shape inside orb relaxed-filled with motes; through refraction looks like cellular life.
- **Attract + relax combo** — `Attractstrength > 0, Attractposition` audio-driven → points spread evenly but with localized attractor that gathers them on demand.

**Mesh-bounded point relaxation recipe:**
```
mesh source
   ├─→ sprinklePOP (initial scatter on surface)
   │      → Relax (Relaxmethod='nebr', Solvermode='advect',
   │              Collisiontype='t3d', Collisontop=<SDF>)
   │      → render
   └─→ Voxelize (Voxelizemode='mesh', Outputsdf=True)
          → Relax.Collisontop
```

**Cost:** scales with point count × Relaxiters. Manages 5–10k points at 60fps; bumps to 5–10fps at 50k+ points.

---

### Pivot — offset each instance's pivot point (where rotation/scale operates from)

**Example:** `pivot 1.toe`

**Concept:** Modifies each instance's pivot point — the point around which downstream transforms (rotation, scale) operate. Without Pivot, transforms operate around each instance's local origin (typically center of geometry); with Pivot, the pivot can be aligned to bounding-box edges, custom positions, or attribute-driven points. Critical distinction for "things rotating around their feet vs around their center."

**Pipeline position:** between Instancer (or any module producing instances) and downstream Transform Modifier. `Instancer → Pivot → Transform Modifier → ...`

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Pivot | `Mode` | **Five modes** (per official docs): `'centerpivot'` (auto-center on geometry), `'aligntobbox'` / `'bbox'` (per-instance bbox-face alignment via `Alignmentside`), `'shift'` (per-instance origin + numeric `Shiftamount*`), `'setlocal'` (explicit local-space pivot via `Pivotx/y/z`), `'setworld'` (group: ALL instances share single world-space pivot — rigid-group rotation). |
| Pivot | `Alignmentside` | Bbox-mode only. **Six options** (per docs): `'-X'`, `'+X'`, `'-Y'`, `'+Y'`, `'-Z'`, `'+Z'`. Use `'-Y'` for bottom (footing), `'+Y'` for top (suspension), etc. |
| Pivot | `Pivotonly` | Only modify pivot, don't move geometry |
| Pivot | `Localspace` | Pivot in instance local space (default) vs world |
| Pivot | `Shiftamountx/y/z` | Custom offset on top of bbox alignment |
| Pivot | `Pivotx/y/z` | Direct pivot position (`setlocal`/`setworld` modes) |
| Pivot | `Dofalloff`, `Falloffattr` | Standard falloff blending — different pivots per region |

**WOBAR application — patterns by Mode:**
- **Per-instance foot-rotation** (characters/dancers turning, Mode='bbox', Alignmentside='ym') — Transform Modifier rotates around feet. Crowd of instanced character meshes responding to audio looks like dancers turning, not tumbleweeds.
- **Per-instance pendular motion** (Mode='shift' with elevated Y) — pivot floats above each instance; Transform Modifier rotation produces pendulum-from-above swing per instance.
- **Group constellation rotation** (Mode='setworld') — ALL instances share one world-space pivot; entire set rotates as one rigid group. Beat-synced camera-tracked constellation rotation, brand-glyph-array spinning around orb center, "tilting whole scene" Act 3 disorientation effect.
- **Per-region pivot variation** — `Dofalloff=True` lets some instances rotate around center, others around feet, controlled by spatial falloff.

**Pivot Mode decision tree:**
- **Each instance has its own pivot variation per-instance** → `'bbox'` or `'shift'`
- **All instances share a single pivot in world space (group rotation)** → `'setworld'`

---

### Visualize Frame — debug viz of per-instance orientation frame

**Example:** `pivot 1.toe`

**Concept:** Renders the local coordinate frame (red/green/blue X/Y/Z axes) at each instance's position. Pure authoring aid — disable for final renders. Critical for understanding how Pivot, Aim, Orient, and other rotation-modifying modules affect each instance's orientation.

**Key parameter:** `Lengthscale` (default ~0.15) — controls axis arrow length.

**WOBAR application:** keep enabled during any complex POPX rotation work; disable before render. Same authoring-time role as `Visualizeoffset` on MoveAlongCurve.

---

### POPX Particle — multi-mode particle simulation (Fluids-SPH / Fluids-PBF / Grains)

**Example:** `particle (fluid-sph) + ssfr.toe`

**v1.3.0 RENAME + EXPANSION:** This module was previously called "SPH" in v1.2 and earlier. In v1.3.0 it was renamed to **Particle** with **three material modes** and multiple solver modes added.

**Material Modes:**
- **Fluids-SPH** — Smoothed Particle Hydrodynamics (water, slime, viscous fluids)
- **Fluids-PBF** — Position-Based Fluids (alternate fluid solver with Cohesion, Surface Tension, Adhesion params)
- **Grains** — Granular materials (sand, debris, gravel) with Repulsion Weight, Attraction Weight params

**Solver Modes:** Simple / Advect — same convention as other stateful modules. Advect mode requires **Init→Start→Play** activation sequence.

**Setup sequence (Advect mode):**
```
Choose Material Mode (Fluids-SPH / Fluids-PBF / Grains)
Set Solvermode = 'advect'
↓
Pulse Initialize    # spawn particles
Pulse Start         # begin from initialized state
Toggle Play = True  # continuous simulation
(Step pulse for frame-by-frame when paused)
```

**Distinction from Flow:** Flow is **grid-based** (Eulerian voxel fluid — better for smoke/fire/diffuse). POPX Particle is **particle-based** (Lagrangian — better for liquid surfaces, droplets, splashes, grains). Pick by aesthetic: smoke = Flow, water/grains = Particle.

**Pipeline position:** standalone solver. Inputs particle stream (`in0` from native `particlePOP`); outputs simulated particle positions for downstream rendering (typically via SSFR).

**Decoupled architecture (recommended):** `Solvermode='simple'` — SPH solver computes physics; native `particlePOP` handles emission/lifecycle/integration/feedback. Same pattern as Flow's decoupled mode.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Particle | `Solvermode` | `'simple'` (decoupled) or `'advect'` |
| Particle | `Particlesupdatepop` | Feedback POP (when not decoupled) |
| Particle | `Iterations` | Solver passes per frame (4 typical; higher = more stable, slower) |
| Particle | `Timestep` | Sim time step |
| Particle | `Maxneighbors` | Cap on per-particle neighbor count for SPH calcs (perf vs accuracy) |
| Properties | `Targetdensity` | Equilibrium density (controls compressibility) |
| Properties | `Pressuremulti` | Pressure response strength |
| Properties | `Nearpressuremult` | Short-range pressure (prevents collapse) |
| Properties | `Viscosity` | Water=low, slime=high |
| Collisions | `Enablebboxcollision`, `Bbox`, `Bboxupperbounds2` | Bounding box collision |
| Collisions | `Collisiontype` | `'pop'` (3D POP geometry) / `'t2d'` (TOP texture as 2D collision field) / shape primitives |
| Collisions | `Collisionpop` | 3D mesh collision geometry (when type='pop') |
| Collisions | `Collisontop` | TOP texture as 2D collision field (when type='t2d') — bright pixels = solid, dark = empty. Animatable in real time. |
| Collisions | `Collisionoffset` | Spacing margin |
| Collisions | `Solid`, `Project`, `Sizex/y/z`, `Radiusx/y/z`, `Cornerradius`, `Usecustombounds`, `Lowerboundsx/y/z`, `Upperboundsx/y/z`, `Tx/Ty/Tz`, etc. | Shape-primitive collision when not using POP/TOP |
| Collisions | `Displaygeo` | Viewport collision viz |
| Forces | `Gravitymultiplier`, `Velocitydamping`, `Dynamicscale` | Global force controls |

**WOBAR application:**
- Water/liquid moments — Act 1 portal threshold reading as water surface, Act 5 emergence from water.
- Audio-reactive viscosity — drive `Viscosity` from audio energy → fluid changes from water to slime as music intensifies.
- Brand mark splash — emit particles in WOBAR wordmark shape, let them fall and pool. The mark dissolves into liquid.

**Cost:** SPH is GPU-heavy. Particle count × neighbor count × iterations. 16k particles × 20 neighbors × 4 iters runs at ~30fps on Apple Silicon NC. Reduce particle count or `Maxneighbors` for live performance budgets.

---

### SSFR — Screen Space Fluid Renderer (renders particles as continuous fluid surface)

**Example:** `particle (fluid-sph) + ssfr.toe`

**Concept:** POPX rendering module specifically for fluid particles. Takes a particle-based render output and reconstructs a continuous fluid surface using screen-space techniques — depth filtering, thickness estimation, surface normals from depth gradients, refraction sampling. Without SSFR you'd see thousands of discrete spheres; with SSFR you see connected liquid with realistic refraction.

**Pipeline position:** consumes a renderTOP (rendering the particle scene); produces final fluid surface output.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `Rendertop` | Points at the renderTOP rendering the particle scene |
| `Filterradius` | Smoothing kernel for depth-based surface reconstruction (5.3 typical) |
| `Thicknessscale` | Perceived fluid depth/density |
| `Absorptionscale` | Beer-Lambert absorption (color fades through depth) |
| `Refractionscale` | Background refraction strength (Snell's law sampling) |
| `Envmap` | Environment map TOP for reflection |
| `Renderenvmap` | Show env map behind fluid |
| `Enabletonemap`, `Gamma`, `Exposure` | Final output tonemapping |

**WOBAR application:** the renderer for any SPH fluid sim. Pair with POPX Particle (SPH mode). For brand-aligned looks: feed a tinted/cool environment map for moody underwater aesthetics, lower `Refractionscale` for less photorealistic / more painterly water.

**Cost:** screen-space rendering scales with output resolution × particle density. 720×1280 with 16k particles is OK on Apple Silicon NC.

---

### MoveAlongMesh — animate particles along a mesh surface (constrained to surface)

**Example:** `move along mesh.toe`

**Concept:** The mesh-surface analog of MoveAlongCurve. Particles are constrained to a mesh surface and travel along an orientation field provided by `OrientMesh`. Particles can never leave the mesh — the mesh IS the "ground." Combined with `OrientMesh` (which generates the direction field), this is the canonical "creature covered in glowing veins" / "living skin" visual.

**Pipeline position:** standalone solver. `in0` = particle stream (Instancer or any POP); `in1` = mesh with orientation attributes (typically OrientMesh's output).

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Move Along Mesh | `Mesh` | Path to mesh POP (alt: wire to `in1`) |
| Move Along Mesh | `Displaymesh`, `Displaycolor*` | Viewport mesh visualization |
| Move Along Mesh | `Play` | Pause/resume |
| Attach | `Attachmode` | `'scatter'` (random surface distribution), `'nearest'`, etc. |
| Attach | `Locktomesh` | Lock particles to mesh (prevent escape) |
| Attach | `Seed`, `Searchradius` | Scatter parameters |
| Attach | `Offset`, `Maintainoffset`, `Maintainorientoffset` | Perpendicular offset from mesh surface |
| Attach | `Visualizeoffset` | Debug viz |
| Animate | `Speed`, `Randomspeed`, `Speedseed` | Speed control (base + per-particle random) |
| Animate | `Dofalloff`, `Falloffattr` | Speed modulated by falloff |
| Animate | `Enablelifetime`, `Life`, `Lifevariance`, `Lifeseed`, `Lifeh` | Particle lifecycle |
| Animate | `Outputlifeattrs` | Writes per-particle Age and lifecycle attributes for downstream |
| Animate | `Scalebyage`, `Remapscalex`, `Remapscaley`, `Scaletop` | Particles grow/shrink with age (scale=0 at birth → scale=1 at full life is canonical) |
| Animate | `Enablepointrelax`, `Relaxiters`, `Maxrelaxradius`, `Maxneighbors`, `Numhashbuckets`, `Distribution`, `Relaxstrength` | Optional point-relaxation — particles avoid each other on the surface |

**WOBAR application:**
- **Living skin** — any mesh becomes "alive" with veins of moving particles. The pighead example is on-brand for shadow-work / mycelium / neural-network metaphor visuals.
- **Form-revealing flow** — particles trace the topology of the mesh, making form visible through motion.
- **Audio-reactive vein flow** — drive `MoveAlongMesh.Speed` or `OrientMesh.Curl Noise.T4d` rate from audio energy → flow speeds up on drops, slows in quiet sections.
- **Glass orb internal mesh** — a small mesh inside the glass orb covered in moving veins, viewed through the refraction. Adds living detail to the orb's interior.

---

### OrientMesh — generate orientation field on a mesh (forward / up / orient quaternion)

**Example:** `move along mesh.toe`

**Concept:** Computes per-vertex orientation attributes on a mesh. Outputs `forward`, `up`, and `orient` (quaternion) attributes that downstream modules (especially MoveAlongMesh) consume as a direction field. Optional curl noise modulation perturbs the field for organic motion.

**Pipeline position:** between source mesh and MoveAlongMesh's `in1` input. Read mesh in, write orientation attributes out.

**Key parameters (3 pages):**

**`[Orient Mesh]` — base orientation computation**

| Parameter | Purpose |
|-----------|---------|
| `Computemethod` | `'nup'` (normal + up) — most common; computes orientation from mesh normals + a reference up |
| `Computenormals` | Generate normals if missing on input |
| `Autoup`, `Upvectorx/y/z` | Up direction: auto-computed or specified |
| `Style` | `'first'` etc. — orientation style |
| `Attributename` | Optional alt attribute name |
| `Makeortho`, `Invertn`, `Invertup`, `Crossupvector` | Orthogonalization + flip toggles |
| `Outputtangent` | Optional tangent output |
| `Visualizeupvector`, `Lengthscale`, `Colorr/g/b` | Debug — draws arrows at each vertex showing up direction |

**`[Curl Noise]` — optional curl-noise modulation of the orientation field**

| Parameter | Purpose |
|-----------|---------|
| `Enablecurlnoise` | Add curl noise to the orientation field (perturbs directions for organic motion) |
| `Blend` | 0–1 mix between pure orientation and noise-perturbed |
| `Type`, `Period`, `Harmon`, `Spread`, `Gain`, `Amp`, `Exp` | Standard noise field params |
| `T4d` | 4D noise time — animate for evolving direction field |
| `Tx/Ty/Tz`, `Sx/Sy/Sz`, etc. | Transform applied to noise sampling space |

**`[Blur]` — optional smoothing of the orientation field**

| Parameter | Purpose |
|-----------|---------|
| `Enableblur`, `Iterations`, `Kernalradius` | Smoothing kernel |
| `Influencetype` | `'conn'` (topology-aware) or alt |

**WOBAR application:** the upstream orientation provider for any MoveAlongMesh visual. The curl noise + time animation is what makes the particles wander organically across the mesh surface instead of moving in lockstep. **Animate `T4d` rate from audio energy** for music-reactive direction-field evolution.

---

### Noise Falloff — generate `popxFalloff` from procedural noise sampled at point positions

**Example:** `noise advection.toe`

**Concept:** The fifth falloff source. Writes `popxFalloff` based on simplex/perlin noise field sampled at each point's position (animated via `T4d`). Spatial variation that's noise-derived rather than texture/shape/infection/attribute-derived.

**Pipeline position:** anywhere downstream of an instance stream. Writes the falloff attribute that downstream modifiers respect.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Noise | `Type` (`'simplex4d'`), `Period`, `Harmon`, `Spread`, `Gain`, `Amp`, `Exp`, `Offset` | Standard noise field params |
| Noise | `Userestattr` | Sample noise at point's rest position vs current position (rest-bound vs world-bound noise) |
| Noise | `Normalizednoise` | Output normalized 0–1 (vs ±1) |
| Noise | `Seed` | Deterministic seed |
| Transform | `Tx/Ty/Tz`, `Sx/Sy/Sz`, `T4d` | Noise sampling space transform + 4D noise time animation |
| Falloff | `Outputfalloffattr`, `Combineop`, `Combstrength`, `Previewfalloff`, `Fallofframp` | Standard falloff output controls |

**WOBAR application:** spatial variation driven by procedural noise. Audio-modulated `T4d` rate or `Amp` for music-reactive falloff fields. Layered with other falloff sources (Shape Falloff for "inside the orb" + Noise Falloff for "with organic variation") via different `Outputfalloffattr` names.

**The complete falloff family (5 sources):**
- **Shape Falloff** — geometric (distance to sphere/box/etc)
- **Texture Falloff** — image-based (samples a TOP)
- **Infection Falloff** — temporal viral spread
- **Attribute Falloff** — converts any existing attribute
- **Noise Falloff** — procedural noise sampled at point positions

All five write `popxFalloff` (or custom name); downstream modifiers are agnostic to the source.

---

### Noise Modifier — curl noise / simplex noise displacement (advect or displace instances)

**Example:** `explode curl.toe`

**Concept:** Per-instance noise field. Has TWO operating modes:

1. **Direct displacement mode** (`explode curl.toe`) — `Affectposition=True, Mode='advect'` or `'displace'`. Noise displaces points directly. Standard "wind-blown / dissolving" motion.

2. **Attribute writer mode** (`noise advection.toe`) — `Affectposition=False, Outputnoiseattr=True, Noiseattr='Noise'`. Noise field is written to a per-point attribute; downstream modules (Advect, Transform Modifier with custom Falloffattr) consume the attribute. Decouples generation from application — useful for layering, routing, inspecting the noise field.

Distinct from Texture Falloff's noise overlay (which generates a falloff value) — Noise Modifier generates a vector field. Two crucial flags differentiate behavior:
- **`Curlnoise = True`** — divergence-free curl noise. No inflow/outflow, all rotation/swirl. Gold standard for natural-looking smoke, mist, dissolution motion.
- **`Mode = 'advect'`** vs **`'displace'`** vs **`'simple'`** — advect accumulates motion over time; displace per-frame offset; simple = direct application.

The combo `Curlnoise=True, Mode='advect', Affectposition=True, Affectrotation=True, Dofalloff=True` is the canonical "wind-blown / dissolving" motion (mode 1).
The combo `Outputnoiseattr=True, Noiseattr='Noise', Affectposition=False` is the canonical "noise as data" pattern (mode 2) → consumed by Advect with `Advectsource='ptattr', Advectattr='Noise'`.

**Pipeline position:** any modifier slot. Operates per instance.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Noise | `Curlnoise` | Divergence-free curl noise (rotational, no inflow/outflow). Critical flag for natural motion |
| Noise | `Type`, `Period`, `Harmon`, `Spread`, `Gain`, `Amp1/2/3`, `Exp1/2/3`, `Offset1/2/3` | Standard noise field params (per-axis amplitudes/offsets so xyz are decorrelated) |
| Noise | `Noisesignature` | `'vector'` (3D vector output) or scalar |
| Noise | `Userestattr`, `Enabledirattr`, `Defaultdir1/2/3`, `Directionattr` | Direction-attribute overrides |
| Noise | `Outputnoiseattr`, `Noiseattr` | Optional: write the noise field to an attribute for downstream reuse |
| Noise | `Seed` | Determinism |
| Noise | `Dofalloff`, `Falloffattr` | Standard falloff blending |
| Transform | `Tx/Ty/Tz/Rx/Ry/Rz/Sx/Sy/Sz`, `T4d` | Optional: superimpose a base transform on the noise displacement |
| Affect | `Mode` | `'advect'` (accumulating drift) or `'displace'` (per-frame offset) |
| Affect | `Affectposition` + `Positionamount` | Enable + scale position effect |
| Affect | `Affectrotation` + `Rotationmode` (`'additive'`) + `Rotationamount` + `Aimweight` | Enable + scale rotation effect |
| Affect | `Affectscale` + `Scalemode` (`'add'`/`'mult'`) + `Uniformscale` + `Scaleamount` | Enable + scale scale effect |
| Affect | `Fromlow1/2/3`, `Fromhigh1/2/3`, `Tolow1/2/3`, `Tohigh1/2/3` | Per-axis remap of noise output |
| Affect | `Play` | Pause/resume (advect accumulation freezes when Play=False) |

**WOBAR application:**
- **Wind-blown dissolution** — combine with Explode + Infection Falloff for the canonical disintegration chain (see Patterns below).
- **Ambient drift in Act 1** — every Act 1 instance gets gentle curl-noise advection so they float subtly. Adds organic life to static layouts.
- **Heavy chaotic motion in Act 3** — `Curlnoise=True` with high `Amp` and `Period` mismatched between axes = chaotic shaking that respects the falloff field.
- **Audio-driven shaking** — `Affect.Play` toggled on transient detection, `Amp` ramped with energy. Instances "wake up and shake" on beat.

**Replaces:** custom GLSL curl-noise displacement, manual noise CHOP → instance offset wiring.

---

### DLG — Differential Line Growth (brain-coral / labyrinth / fingerprint pattern solver)

**Example:** `dlg.toe`

**Concept:** Generative line-growth simulator. Takes a seed POP of line strips, grows them frame-by-frame by:
1. Subdividing segments longer than `Maxdistance` (vertex count grows)
2. Repelling each vertex from nearby other vertices (self-avoidance — lines push apart)
3. Attracting each vertex to its line-neighbors (line stays continuous)
4. Optional noise modulation, optional collision constraints

The result: lines that lengthen organically, pack convolutedly, and fill space with maze-like curves. Mathematically related to reaction-diffusion patterns, brain coral, fingerprints, intestinal villi, voronoi tessellation, Turing patterns.

**Pipeline position:** standalone solver. Like Flow and DLA, uses a `*Updatepop` feedback pattern: `dlg1 → [optional modifiers] → null1`, with `dlg1.par.Lineupdatepop = null1`. Modifiers inserted in the chain become part of the per-frame update.

**Inputs:**
- `in0` — seed line POP. Any line topology — circle, arc, hand-drawn line, traced silhouette via tracePOP

**Output:**
- POP with current vertices + line topology, growing per frame until `Maxverts`

**Key parameters by category:**

**`[DLG]` — solver controls**
| Parameter | Purpose |
|-----------|---------|
| `Lineupdatepop` | Feedback POP for state propagation (downstream-facing, same pattern as `Flow.Particlesupdatepop`) |
| `Maxverts` | Cap on total vertex count |
| `Growthstrength`, `Mass` | How aggressively segments grow; vertex inertia |
| `Maxdistance` | Segment length threshold for subdivision. Smaller = more splits = denser pattern |
| `Distribution` | Vertex spacing strategy (`'default'` or alt) |
| `Numhashbuckets`, `Maxneighbors` | Spatial hash for self-avoidance queries |
| `Linestrips` | `'closelinestrips'` (closed loops) or alt (open) |
| `Filtertype`, `Filterdist`, `Effect` | Topology smoothing (gaussian/etc) |
| `Play` | Pause/resume |

**`[Noise]` — built-in per-frame noise modulation**
| Parameter | Purpose |
|-----------|---------|
| `Applynoise`, `Type` (`'simplex4d'` etc), `Period`, `Harmon`, `Spread`, `Gain`, `Amp`, `Exp`, `Offset` | Standard noise params |
| `Animate` | Time-rate for 4D noise (alternative to inserting an animated noisePOP downstream) |

**`[Collisions]` — boundary constraints**
| Parameter | Purpose |
|-----------|---------|
| `Collisiontype` | `'sphere'`, box, capsule, custom |
| `Sizex/y/z`, `Radiusx/y/z`, `Scale` | Boundary shape |
| `Solid`, `Project` | If solid: lines project to surface; otherwise bounce off |
| `Collisiondamping`, `Collisionoffset` | Energy loss + clearance margin |
| `Collisionpop`, `Collisontop`, `Geometrycollision` | Alternate boundaries: from POP, TOP, or arbitrary mesh |
| `Mintype1/2/3`, `Maxtype1/2/3` + `Min/Max1/2/3` | Per-axis hard bounds (independent of shape boundary) |
| `Lower/Upperbounds*`, `Usecustombounds` | Custom AABB |
| `Collisioncolorr/g/b`, `Displaygeo` | Visualization |

**WOBAR application scenarios:**
- **Act 1 RIFT — gentle weaving lines** — single seed circle, slow growth, soft purple. The portal threshold drawing itself.
- **Act 2 DESCENSION — descending weave** — multiple seeds, downward-biased noise, darkening as it densifies.
- **Act 3 CONFRONTATION — fragmented labyrinth** — high growth speed, tight `Maxdistance`, partial mirror. Confusion architecture.
- **Act 5 INTEGRATION — settling pattern** — slow, soft, freeze (`Play=False`) for final still.
- **Brand-glyph-as-seed** — trace WOBAR wordmark via tracePOP → DLG seed → labyrinth grows around the brand mark.
- **DLG + Flow combo** — insert Flow advection between DLG output and `Lineupdatepop` target. Lines grow according to fluid forces (audio-driven turbulence biasing growth direction).
- **DLA + DLG layering** — use DLA-grown points as the DLG seed. Frost grown on mycelium. Two-fractal composition.

**Brand alignment:** The labyrinth / brain-coral / fingerprint aesthetic is deeply on-brand. Reads as "intricate organic system" — the visual analog of the WOBAR therapeutic framework. Single-color renders work natively in 80% black + purple palette.

**Cost:** scales with vertex count × Maxneighbors. 40k verts at 60fps in this example. Slows when growth approaches `Maxverts`. Use `Numhashbuckets` to tune spatial hash performance.

**Replaces in our toolkit:** custom GLSL DLG shaders, Houdini imported DLG simulations, hand-drawn labyrinth assets.

---

### DLA — Diffusion-Limited Aggregation (coral / lightning / mycelium fractal solver)

**Example:** `dla.toe`

**v1.3.0 BREAKING CHANGE:** Built-in mesh and volume outputs are **REMOVED**. Use **`Voxelize`** (then optional Polygonize/marching cubes) downstream to get mesh/volume representations from DLA points.

**Concept:** Generative aggregation simulator. Random walkers diffuse through a sim volume; when one gets within `Attachdist` of any existing aggregated point, it sticks and joins the aggregated set. Iterating produces fractal branching structures — the algorithm behind coral, frost crystals, lightning, lichen, mycelium, dendrites, electrodeposition. State accumulates frame-over-frame.

**Setup sequence (Init→Start→Play):**
```
Connect seed POP to Input 0
↓
Pulse Initialize    # reset & seed
Pulse Start         # begin from initialized state
Toggle Play = True  # continuous simulation
(Step pulse for frame-by-frame when paused)
Optionally: set Walkersupdatepop for feedback / extension
```

**Pipeline position:** standalone solver. Takes a seed POP at `in0` (the initial aggregated points), outputs a POP with the growing aggregated structure + line connectivity attribute (which point attached to which parent — useful for ribbon/line rendering).

**Inputs:**
- `in0` — seed POP (any geometry: a circle, a line, a point cloud, a traced silhouette)

**Outputs (3 ports):**
- Output 0: DLA Structure (Points)
- Output 1: DLA Structure (Lines)
- Output 2: Random Walkers (live diffusing positions, useful for trail visualization)

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| DLA | `Walkersupdatepop` | Optional override POP for walker motion. Default = pure internal noise. Wire to Flow's advected positions for "DLA grown along fluid flow" |
| DLA | `Simboundsx/y/z` | Walker domain extent. Set Z very small (e.g. 0.01) for 2D coral; thick Z for volumetric aggregation |
| DLA | `Maxpoints` | Cap on aggregated structure size (default 100k) |
| DLA | `Seed` | Deterministic random seed for repeatability |
| DLA | `Maxsearchdist` | Walker perception radius — how far a walker looks for nearby aggregation. Larger = tighter/compact growth, smaller = more spread |
| DLA | `Attachdist` | Distance threshold for sticking. Smaller = finer detail, denser fractal |
| DLA | `Attachstrength` | Probability (0–1) of sticking on contact. < 1.0 = bouncing walkers → denser tips |
| DLA | `Maxneighbors` | 1 = dendritic branching (classic DLA). 2+ = walls / sheets / cellular structures |
| DLA | `Internalnoise` + `Noiseamp` | Brownian motion magnitude on walkers (when no external velocity) |
| DLA | `Play` | Pause/resume growth |
| DLA | `Displaybounds`, `Displayrandomwalkers`, `Displaydlapoints`, `Displaydlalines` | Visualization toggles for inspecting growth in real time |

**Five output rendering patterns:**
- Sphere instanced at each aggregated point (this example): `dla → copy(sphere, dla_pts) → render`
- Line ribbons using the connectivity attribute: read line topology, render as glow strands
- Point cloud splatter: directly render as POPs through a phong/PBR
- Volumetric: convert aggregated points to a voxel field for raymarching
- Static export: freeze growth (`Play=False`), export as SOP for use elsewhere

**WOBAR application scenarios:**
- **Act 2 (DESCENSION) mycelium** — track naming language already includes MYCELIUM. Circular seed at orb bottom, growth fills upward; audio energy drives growth speed. The underground network spreading.
- **Act 3 (CONFRONTATION) neural / shadow roots** — radial growth dark-on-dark; pair with feedback tunnel for the "shadow taking shape" visual.
- **Act 4 (RELEASE) lightning** — tight `Maxsearchdist`, high growth speed, transient-triggered Play toggle = kick-synced lightning strikes.
- **Act 5 (RETURN) frost crystal closing** — seed = frame-edge ring; aggregation collapses inward. Portal frosting over.
- **DLA from brand glyph** — feed WOBAR wordmark via tracePOP as seed → coral grows out of the mark. Brand dissolution.
- **DLA + Flow combo** — set `Walkersupdatepop` to read Flow's advected positions. Walkers ride the fluid. Audio injection into Flow biases coral growth direction.

**Brand alignment notes:**
- The DLA aesthetic IS deeply on-brand. Coral / lichen / mycelium / neural / lightning all align with WOBAR's shadow-work and "everything you need is already there" philosophy.
- Output is naturally monochromatic-readable — works in 80% black + purple palette without recoloring.
- Growth is slow and meditative by default — fits Act 1/Act 2 "felt, not aggressive."

**Cost:** scales with aggregated set size × walker count. 100k points runs 60fps in the example because growth is gradual (~thousands of new points/second). Watch for slowdown as aggregation reaches Maxpoints.

**Replaces in our toolkit:** custom GLSL DLA shaders, manual L-system fractal builds, hand-modeled coral SOPs.

---

### Flow — GPU fluid simulation (Navier-Stokes) for advecting geometry or rendering smoke

**Example:** `curve advection.toe`

**Concept:** A complete grid-based GPU fluid simulator packaged as a POPX module. Solves velocity, pressure, viscous diffusion, vorticity confinement, substance/temperature/color advection, particle advection, and POP injection on a 3D voxel grid.

**CRITICAL — Flow has TWO independent advection controls** (this is THE source of "Flow looks dead" confusion):

| Control | Purpose | Required? |
|---------|---------|-----------|
| **`Advect` (toggle)** | Activates the particle advection feature itself | YES — without this, particles do nothing regardless of Solvermode |
| **`Solvermode` (enum)** | Selects the integration algorithm: `'simple'` or `'advect'` | Yes |

**Both must be configured.** Setting `Solvermode='advect'` alone with `Advect=False` produces no particle motion. Setting `Advect=True` with `Solvermode='simple'` does basic motion without advanced velocity-field tracking.

**Inputs:**
- Input 0: POP — injection source (substance/density)
- Input 1: TOP — source field
- Input 2: POP — particles in (for "external particles advected by fluid" mode)

**Outputs (4 ports):**
- Output 0: Substance/density (TOP)
- Output 1: Velocity (TOP)
- Output 2: Temperature (TOP)
- Output 3: Particles Out (POP) ← what to render

**Pipeline position:** standalone — has its own internal solver state across many subnetworks (Velocity_Field, Pressure_Solver, Advection, Inject_Substance, Inject_Temperature, Particle_Advection, etc.). Inputs feed source/injection geometry; outputs are TOPs (sim state) and POPs (advected geometry positions).

**Resolution sizing:** 3D voxel grid `Resolutionx/y/z`. Cost scales cubically with axis resolution. Defaults are modest (128×128×32 = ~524k voxels) for live use; bumping to 256³ is ~16M voxels and will tank fps on Apple Silicon NC.

**Key parameter pages:**

**`[General settings]`** — sim domain & precision
| Parameter | Purpose |
|-----------|---------|
| `Resolutionx/y/z` | Voxel grid resolution per axis |
| `Maxaxisres` | Cap on largest axis (auto-scales others) |
| `Precision` | `'16-bit float'` (default) or `'32-bit float'` (more precision, more cost) |
| `Simboundsx/y/z` | Physical extent of sim domain in world units |
| `Timescale`, `Timestep` | Sim time control (Timestep often `1/me.time.rate`) |

**`[Velocity]`** — Navier-Stokes solver controls
| Parameter | Purpose |
|-----------|---------|
| `Veldissipation` | Per-frame velocity decay (0 = energy preserved) |
| `Pressureiters` | Pressure projection iterations enforcing incompressibility (default 25; higher = more accurate, slower) |
| `Viscosity` + `Diffusioniters` | Viscous smoothing |
| `Vorticity` | Vorticity confinement strength — preserves swirl detail against numerical dissipation. Higher = curlier, more visible turbulence |

**`[Substance]`** — transported scalar fields (smoke density, color)
| Parameter | Purpose |
|-----------|---------|
| `Dissipation` | Substance decay over time |
| `Colordissipationr/g/b` | Per-channel color decay (independent — useful for non-uniform fadeout) |

**`[POP Injection]`** — inject a POP as a continuous substance/force/color source
| Parameter | Purpose |
|-----------|---------|
| `Inject` | Master enable |
| `Injectionpop` | Path to a POP whose points become injection sites |
| `Injectposx/y/z`, `Injectscale` | Position offset and scale of injection volume |
| `Injectgain`, `Injectstrength` | Substance amount and force amount injected per frame |
| `Injecttemp`, `Injectcolorr/g/b` | Temperature and color deposited |

**`[Buoyancy]`** — temperature creates upward force (smoke/fire effect)
| Parameter | Purpose |
|-----------|---------|
| `Applybuoyancy` | Master enable |
| `Buoyancystrength`, `Gasweight` | Temperature-to-force conversion |
| `Coolingrate` | How fast hot regions cool (lose temperature) |
| `Expansion` | Volume expansion with temperature |

**`[Gravity]`** — directional bulk force
| Parameter | Purpose |
|-----------|---------|
| `Applygravity` | Master enable |
| `Gravityvectorx/y/z` | Force direction |
| `Gravitystrength`, `Surfacelevel` | Magnitude and below-surface threshold |

**`[External Force]`** — paint forces with a TOP
| Parameter | Purpose |
|-----------|---------|
| `Addexternalforce` | Enable |
| `Externalforcetop` | TOP encoding per-voxel force vectors (RGB = xyz) |
| `Extforcestrength` | Multiplier |

**`[Optical Flow]`** — drive forces from video motion
| Parameter | Purpose |
|-----------|---------|
| `Addopticalflowforce` | Enable |
| `Opticalflowtop` | Source video TOP — Flow analyzes motion and injects as forces |
| `Optiflowforcestrength` | Multiplier — turn live camera input into fluid forces |

**`[Bounds]`** + **`[Obstacle]`** — TOP-defined domain shape and obstacles
| Parameter | Purpose |
|-----------|---------|
| `Boundstop` | TOP defining custom sim boundary (beyond box) |
| `Obstacletop` | TOP marking solid obstacles fluid flows around |
| `Renderobstacle`, `Obstacleopacity` | Visualization |

**`[Advect]`** — geometry advection mode (the killer feature)
| Parameter | Purpose |
|-----------|---------|
| `Advect` | Enable advection of external geometry |
| `Solvermode` | `'advect'` (drag external POP through fluid) or `'simulate'` (full fluid render) |
| `Particlesupdatepop` | POP to read positions from each frame, advect, write back |
| `Numparticles` | Scaling for particle systems |
| `Spawn`, `Densityscale`, `Threshold`, `Seed`, `Maxattempts` | Particle birth controls |
| `Enableparticlelife`, `Lifespan`, `Lifevariance`, `Lifeseed` | Particle lifetime |
| `Lookupcolor`, `Hcolor`, `Channelmask*`, `From/To low/high*` | Color sampling and remap from sim state |

**The curve advection pattern (this example):** wire `Particlesupdatepop` to a downstream POP that itself reads from Flow's output. This creates a GPU-side feedback loop where geometry is continuously dragged through the velocity field. Insert `lineresamplePOP` in the loop to keep curves smooth as they deform under shear.

**Particle simulation setup sequence (canonical murmuration):**

```
1. Connect injection POP → Input 0  (the swarm seed cloud)
2. Toggle Advect = True             ← BOTH this AND step 3 required
3. Set Solvermode = 'advect'        ← BOTH this AND step 2 required
4. Toggle Inject = True
5. Set Injectionpop = <POP source>  (or use Injectpos fallback)
6. Toggle Spawn = True              (spawn particles where density > Threshold)
7. Set Particlesupdatepop = <downstream POP>  (feedback handle)
8. Pulse Reset to initialize
9. Adjust Vorticity ≥ 0.5 for swirling motion (default 0.25)
10. Tune Veldissipation 0.02–0.05 for momentum preservation
11. Render Output 3 (particles POP)
```

**Murmuration parameter recipe (from docs):**

| Parameter | Recommended | Why |
|-----------|-------------|-----|
| `Vorticity` | 0.5–2.0 | Swirling detail (vorticity confinement) |
| `Pressureiters` | 20–40 | Tighter incompressibility = denser swarms |
| `Veldissipation` | 0.02–0.05 | Low decay preserves momentum patterns |
| `Spawn` | True | Particles emerge where density clusters form |
| `Advectionstep` | 1.0–1.5 | Particle response sensitivity |
| `Externalforcetop` | curl noise | Drives coherent group motion (optional) |

**WOBAR application scenarios:**
- **Act 2 Descension — fluid-pulled inward flow** — radial gravity (via External Force TOP) sucks bodies toward orb center; turbulent flow makes the descent organic, not analytic.
- **Act 3 Confrontation — turbulent mirror** — Optical Flow TOP fed by live camera; performer's silhouette generates fluid forces; decorative geometry advects through; the visual literally responds to the body.
- **Act 4 Release — substance/smoke** — full simulate mode with substance injection, buoyancy, color mixing. Real smoke/ink-in-water without GLSL.
- **Glass Orb integration** — replace N-body gravity in motes with a tiny Flow sim inside the orb. Sub-bass injects as substance at center → bass kicks become turbulence ripples that push motes hydrodynamically.

**Cost warnings:**
- Voxel resolution³ × pressure iters × diffusion iters × per-frame passes. 128×128×32 is ~bare-minimum live; bumping any axis or iter counts dramatically multiplies cost.
- 16-bit float precision usually sufficient. Only switch to 32-bit if visible numerical artifacts (ringing, banding) appear.
- Lots of internal feedback TOPs/POPs hold state — `Reset` pulse re-initializes; without proper Reset wiring (parent shortcut chains) the solver can lock into a stuck state.

**Replaces in our toolkit:** custom GLSL fluid solvers, Stam's stable fluids implementations, ad-hoc smoke/fire shaders. Flow is a complete drop-in fluid that exposes the right knobs.

---

### Instancer — distribute instances along a curve / mesh / grid / radial / honeycomb

**Examples:** `aim.toe` (linear grid mode, implicit), `coil torus.toe` (curve mode)

**Concept:** The primary distribution module. Generates many instances of an input POP (e.g. a sphere primitive, a mesh) and lays them out according to a chosen pattern. All downstream POPX modifiers (Aim, MoveAlongCurve, Randomize) operate on the Instancer's output.

**Pipeline position:** takes a POP source as input[0] (the thing being instanced), outputs a POP stream with N instances + per-instance attributes (position, popxIndex, popxFalloff, etc.).

**Distribution modes (`Distributiontype`):**

| Mode | Behavior | When to use |
|------|----------|-------------|
| `linear` | Straight 3D grid | Stacks, lattices, regular tilings |
| `radial` | Radial pattern from center axis | Sun rays, circular emanation |
| `curve` | Along a curve POP — points spaced by curve length | Flow paths, ribbons, torus coils, tunnel walls |
| `mesh` | Scatter directly onto a mesh template's surface | Carpet a mesh with instances per face |
| `honeycomb` | Hexagonal honeycomb tiling | Faceted fields, structured surface patterns |
| `pointcloud` | Use the input POP's existing points as instance positions | Pre-computed seeds, hand-authored layouts, indexed multi-geometry |

**Key shared parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Distribution | `Distributiontype` | One of the modes above |
| Distribution | `Templateobject` | Path to the curve/mesh/SOP that defines the distribution shape (mode-dependent) |
| Distribution | `Templategroup` | Optional group filter on the template |
| Distribution | `Attrstocopy` | Comma-separated attributes to pass through from template (default `popxFalloff`) |
| Distribution | `Copytemplateattributes` | Whether to copy all template attributes onto instances |

Mode-specific subpages exist (e.g. `[Curve]`, `[Mesh]`, `[Honeycomb]`) with mode-only parameters not yet enumerated.

**WOBAR application:** This is THE replacement for the Script-CHOP-bridge instancing pattern from the Act 2 vortex build. Instead of writing a Python script CHOP that emits 720 tx/ty/tz samples, instantiate `Instancer(curve)` pointing at a curve POP and you get the same effect with audio-reactive curve geometry built in.

**Cost:** GPU; depends on instance count + distribution complexity. Should benchmark before betting a heavy visual on it.

---

### Magnetize — multi-source attract / repulse / spin force field

**Example:** `magentize.toe`

**Concept:** Multi-magnet physics solver. Each "magnet" is a point in a POP wired to `Magnetspop` (`in1`). Per-magnet attributes (`radius`, `strength`, `mode`, `spindir`) configure each magnet independently. Instances within range get pushed/pulled/spun based on the nearby magnets.

**Pipeline position:** standalone modifier. Operates per instance.

**Inputs:**
- `in0` — instance stream to affect
- `in1` — magnet POP (positions + per-magnet attributes)

**Three magnet modes** (encoded as per-magnet `mode` integer attribute):
- **Attract** — pull instances toward the magnet
- **Repulse** — push instances away
- **Spin** — rotate instances around the magnet's spin axis (`spindir` attribute)

**Per-magnet attributes** (set via `attributePOP` upstream of the magnet POP input — these names are the **exact attribute names per the official docs that override module parameters per-magnet**):

| Attribute | Type | Purpose |
|-----------|------|---------|
| `P` | vec3 | Magnet position (the point's P attribute) |
| `radius` | float | Influence area for this magnet |
| `strength` | float | Field strength |
| `exponent` | float | Falloff curve exponent |
| `mode` | int | 0/1/2 — attract/repulse/spin (per docs: enum integer values, 0 = first option) |
| `spindir` | vec3 | Spin axis (when mode=spin) |
| `contain` | int | Containment behavior (per docs) |

**Module-level parameters (defaults overridden by per-magnet attrs):**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Magnetize | `Magnetspop` | Path to magnet POP (alt: wire to `in1`) |
| Magnetize | `Solvermode` | `'advect'` (state-accumulating) — likely also `'simple'` |
| Magnetize | `Searchradius` | Broad scan radius for finding instances near magnets |
| Magnetize | `Relaxfactor` | Solver relaxation |
| Magnetize | `Mode`, `Strength`, `Radius`, `Exponent` | Default magnet params (overridden by per-magnet attrs) |
| Magnetize | `Spindirx/y/z` | Default spin axis |
| Magnetize | `Contain` | Containment / boundary |
| Magnetize | `Affectpos` + `Moveweight` | Position effect on/off + 0–1 blend strength |
| Magnetize | `Affectrot` + `Aimweight` | Rotation effect on/off + 0–1 blend strength |
| Magnetize | `Outputforceattr` → `Force` | Write per-instance force vector for downstream use |
| Magnetize | `Outputweightattr` → `Weight` | Write per-instance cumulative effect strength — drives downstream Color Modifier / Transform reads |
| Magnetize | `Initialpop` | Optional reset state for instances |
| Magnetize | `Displaymagents` | Viewport magnet gizmos (shows where magnets are + their radius) |
| Magnetize | `Dofalloff`, `Falloffattr` | Standard falloff blending |
| Magnetize | `Play` | Pause/resume |

**WOBAR application:**
- **Audio-driven magnets** — magnet POP positions track audio peaks (one magnet per frequency band); each band magnetizes differently (bass attract, treble repulse, mid spin).
- **Cursor as moving magnet** — single-point POP at cursor with `mode=spin` → cursor "stirs" the field as it moves.
- **Performer-as-magnet** — body-tracking → audience behaves around the performer.
- **Beat-pulsed strength** — `magnet.strength` attribute driven by audio energy; magnets pulse stronger on kicks.
- **`Weight` output → Color Modifier** — visualize WHERE the action is happening. Only magnetized instances get colored; idle ones stay neutral.

**Replaces:** custom GLSL force-field shaders, hand-rolled per-instance attractor math.

---

### Measure — per-point geometric measurement (curvedness, gradient, etc.)

**Example:** `measure.toe`

**Concept:** Geometric analysis module that reads mesh topology and writes per-point analytic attributes — curvedness, gradient of any scalar field, normal estimates, etc. Acts like a SOP analysis op but in POP space, fully GPU-friendly.

**Pipeline position:** between any mesh source and downstream attribute-reading modules. Often used in **chains** where the output of one Measure feeds the input of another (e.g. `Measure(curvedness) → Measure(gradient of Curvedness)`).

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Measure | `Measure` | What to measure: `'curvedness'`, `'gradient'`, (likely also `'normal'`, `'area'`, `'distance'`, etc. — explore module menu) |
| Measure | `Scalarattr` | When `Measure='gradient'`: which scalar attribute's gradient to compute (e.g. `'Curvedness'`) |
| Measure | `Maxdistance` | Neighborhood radius |
| Measure | `Smoothingradius` | Smoothing kernel for the analysis |
| Measure | `Maxneighbors` | Cap on neighbors per point (perf tuning) |
| Measure | `Distribution` | `'closest'` neighbor strategy |
| Measure | `Numhashbuckets` | Spatial hash size |
| Measure | `Usenebrsattr`, `Nebrtype` | Use precomputed neighbor attribute or compute fresh |
| Measure | `Outputmeasureattr` | Attribute name to write (default `'Measure'`; e.g. `'Curvedness'`, `'Gradient'`) |
| Measure | `Outputneighborsattrs` | Optional: write neighbor info attributes |
| Preview | `Previewmeasure`, `Measureramp` | Heatmap visualization for debugging |

**WOBAR application:** see "Mesh-as-flow-field via differential geometry" pattern.

---

### MoveAlongCurve — animate instances along a curve, optionally with per-instance offset

**Example:** `coil torus.toe`

**Concept:** Animation modifier that flows instances along a curve POP over time. **Three modes per official docs:**
- **`'simple'`** — parametric position lookup. Each instance gets a 0–1 phase, MoveAlongCurve places it at that fraction of the curve length. Stateless.
- **`'goal'`** — procedural Goal parameter direct control: `Goal=0` snaps instances to curve start; `Goal=1` snaps to curve end; intermediate values position along curve. No pulse activation needed — just animate Goal directly.
- **`'solver'`** — frame-to-frame state accumulation. Velocity, acceleration, drift all respected. Per-instance state persists across frames (this is why feedback1/feedback2 internal POPs exist — they hold the state). **Solver mode requires Init→Start→Play activation sequence.**

**The Maintain Offset feature:** when bodies are scattered around (not exactly on) a curve and then flowed along it, MoveAlongCurve can **preserve each instance's perpendicular distance from the curve**. So a thick torus made of jittered spheres stays thick as it flows — you don't collapse to a single filament. This is what makes the coil-torus example look voluminous.

**Pipeline position:** typically downstream of Instancer + Randomize. Uses input[0] for the instance stream, takes the curve POP via `Curve` parameter or input[1].

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Move Along Curve | `Curve` | Path to the curve POP (alt: wire to input[1]) |
| Move Along Curve | `Mode` | `'simple'` (parametric) / `'goal'` (Goal-driven 0→1) / `'solver'` (state-accumulating, needs Init→Start→Play) |
| Move Along Curve | `Goal` | (goal mode only) 0=start, 1=end, animate this for direct procedural movement |
| Move Along Curve | `Lock to Curve` | Freezes attachment points after setup — significant performance win for large instance counts |
| Attach | `Curveselectmode` | `dist` = nearest curve segment by distance, `prim` = curve primitive index |
| Attach | `Attachmethod` | `dist` (distance) / `nearest` (closest point) |
| Attach | `Maintainoffset` | 0–1 weight: 0 = clamp to curve, 1 = full perpendicular offset preserved |
| Attach | `Resampledivs` | Curve subdivision for smooth tracking (default 4, this example used 100) |
| Animate | `Reverse` | Flow direction |
| Animate | `Scalebygoal` | Scale instances based on remaining distance to end of curve |
| Animate | `Acctop` / `Twisttop` / `Scaletop` / `Orienttop` / `Offsettop` | TOP textures used as 1D LUTs to vary acceleration / twist / scale / orientation / offset along curve length |
| Animate | `Twistcurvetop` | Twist axis curve |
| Animate | `Remapscale2` | Multiplier on the `Scalebygoal` scale variation. Higher = more dramatic size-by-distance variation along the curve (default 1.0; example `move along curve 1.toe` used 2.5 for big peaks-to-tail size range) |
| Attach | `Visualizeoffset` | When True: draws per-instance attachment lines (the perpendicular distance from each instance to its anchor on the curve). Critical authoring aid for tuning `Maintainoffset` — you can SEE how each instance is anchored. Disable for final render. |
| Attach | `Snaptocentroid` | If True: ENTIRE instance set snaps to the curve as one unit (centroid attaches; instances retain relative positions). If False (default): each instance attaches independently at its nearest curve point. Group-motion vs distributed-flow modes. |
| Attach | `Doorientsnap` | When `Snaptocentroid=True`: rotate the whole group to face the curve's direction at the centroid attachment. Pairs with Snaptocentroid for "object moves along curve" effect. |
| Attach | `Attachmethod` | `'dist'` (nearest-distance, default), `'attr'` (use a per-instance attribute), `'nearest'` (closest-point) |
| Animate | `Outputgoalattrs` | When True: MoveAlongCurve writes per-instance attributes that downstream modifiers can read. **`GoalU`** = normalized 0–1 position along curve length (each instance's curve-progress). Likely also `GoalV` (perpendicular position) and `Goalindex` (curve segment). The bridge between curve solver and attribute-aware Color/Transform modifiers. |
| Animate | `Twistamount` | Twist amount in degrees applied along the curve length |
| Animate | `Speed` | Base speed multiplier for instance flow along the curve |
| Animate | `Dofalloff` | When True: per-instance `popxFalloff` modulates the speed (and other animate behaviors). `popxFalloff=1.0` → full speed; `popxFalloff=0.0` → zero speed. Lets you create per-instance speed variation from any falloff source. |
| Animate | `Wrap` | When True: instances loop from end of curve back to start (cyclic). When False: instances stop at the curve's terminus (one-shot traversal). |
| Animate | `Randomspeed` | Random per-instance speed variation (e.g. 0.01). Adds non-uniformity decoupled from spatial falloff. Combines with `Speed` (base) and `Dofalloff` (spatial) for full speed control. |

**Why TOP-as-LUT pattern matters:** parameters like `Acctop`, `Scaletop` etc. let you paint per-curve-position behavior using a 1D ramp/gradient TOP. Audio-reactive TOPs (e.g. a Lookup TOP whose phase is driven by energy) become per-position behavior modulators on the flow. Powerful for rhythm-driven choreography along a path.

**WOBAR application:**
- **Act 2 vortex** — replace 720-sphere Script CHOP build. Curve = spiral POP, MoveAlongCurve(solver) flows bodies inward, Acctop ramps acceleration toward center for "falling in" feel.
- **Act 3 tunnel** — particles flowing along a tunnel curve toward the viewer; `Reverse=True` so they come at you. Scaletop ramps size from distant→close.
- **Act 4 release** — radial outward curves; flow speed ramps with audio energy.
- **Act 5 portal close** — convergent curves toward portal center; `Maintainoffset` decays as portal closes for collapse motion.

**Internal solver gotcha:** the `feedback1`/`feedback2` POPs inside the module hold per-frame state. They have `Startpulse` / `Initializepulse` parameters that reference `parent.POPX.par.Startpulse|Initializepulse`. If you wrap the module inside a container that breaks the POPX parentShortcut chain (e.g. a base COMP without the POPX shortcut promoted), these expressions error. Fix: don't wrap MoveAlongCurve inside arbitrary baseCOMPs without preserving the POPX shortcut, OR clear the broken expressions.

---

### Shape Falloff — generate `popxFalloff` from a 3D shape (sphere / box / cylinder / capsule / plane)

**Example:** `index from attribute.toe`

**Concept:** The "geometric falloff source." Computes per-instance distance to a 3D shape and writes it as `popxFalloff`. Distinct from Texture Falloff (samples a TOP) and Infection Falloff (temporal viral spread) — Shape Falloff is purely geometric/static.

**Pipeline position:** anywhere downstream of an instance stream. Writes the falloff attribute that downstream modifiers respect via `Falloffattr='popxFalloff'`.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Shape | `Shape` | `'sphere'` (and box/cylinder/capsule/plane variants likely) |
| Shape | `Specpop` | Alt: use a POP to define the shape geometry (custom shape from any mesh) |
| Shape | `Sizex/y/z`, `Radx/y/z`, `Height` | Shape dimensions (mode-dependent) |
| Shape | `Roundness` | Edge softness for box/capsule shapes |
| Shape | `Pointax/y/z`, `Pointbx/y/z`, `Strengthx/y` | Cylinder/capsule axis endpoints + per-axis strength |
| Shape | `Exponent` | Falloff curve exponent |
| Shape | `Transitionrange` | Soft transition zone width (smaller = harder boundary) |
| Shape | `Transitionalign` | Center the transition inside (-) or outside (+) the shape |
| Shape | `Transitiontype` | `'linear'` etc. |
| Shape | `Displayshape`, `Displaycolor*` | Viewport debug visualization |
| Transform | Standard `Tx/Ty/Tz/Rx/Ry/Rz/Sx/Sy/Sz/Px/Py/Pz` | Position the shape in space |
| Falloff | (same as other falloff modules) | `Outputfalloffattr`, `Combineop`, `Combstrength`, `Previewfalloff`, `Fallofframp` |
| Noise | (standard noise overlay) | Optional per-point noise on the falloff |
| Remap | (standard remap chain) | Optional fit/clamp/ramp/invert |

**WOBAR application:**
- **Spatial mask** — modify only instances inside a sphere/box. Gate any Transform/Noise/Color modifier with shape_falloff.
- **Smooth boundary feather** — soft transition between affected/unaffected regions.
- **Combined with delete** — use `popxFalloff` as a delete-key to cull points outside a region.
- **Brand-glyph-as-shape** — use `Specpop` with traced WOBAR wordmark to make instances inside the brand mark behave differently from those outside.
- **Animated shape transform** — drive the shape's Tx/Ty/Tz from audio CHOPs to make the spatial mask move with the music.

**Replaces:** custom GLSL distance-field POP, hand-written attribute computation per shape.

---

### Paint Falloff — manual viewport painting of `popxFalloff` (interactive)

**Example:** `paint falloff.toe`

**Concept:** The sixth falloff source — and the only one that takes USER INPUT directly via the viewport. Click+drag to paint falloff values onto geometry; W = paint, E = erase, Q = clear all (defaults). Painted falloff goes to standard `popxFalloff` attribute that downstream modifiers consume.

**Pipeline position:** between geometry source and downstream POPX modifier chains. Wraps in a containerCOMP for viewport interaction. Often used during AUTHORING phase of a project — paint masks/regions, then save the geometry with the painted attribute baked in.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Paint | `Paintmode` | Master enable |
| Paint | `Paint`, `Paintkey` (default `'w'`) | Paint trigger + keyboard shortcut |
| Paint | `Erase`, `Erasekey` (default `'e'`) | Erase trigger + shortcut |
| Paint | `Eraseallkey` (default `'q'`) | Clear all painted values |
| Paint | `Brushsize1/2/3` | Brush radius |
| Paint | `Transitionrange`, `Transitionalign`, `Transitiontype` | Soft-edge brush profile |
| Paint | `Displaybrush` | Show brush cursor in viewport |
| Paint | `Autorotate` | Auto-rotate view as paint |
| Paint | `Group`, `Showgroup` | Operate on a point group |
| Falloff | (standard) | `Outputfalloffattr`, `Combineop`, `Combstrength`, `Previewfalloff`, `Fallofframp` |
| Remap | (standard) | Optional fit/clamp/ramp |

**WOBAR application:**
- **Hand-authored brand accents** — paint custom falloff regions onto extruded WOBAR wordmark for selective per-letter behavior.
- **Custom asset prep** — paint per-mesh masks once during authoring, save the geometry with `popxFalloff` baked, downstream consumes it.
- **Live performance via tablet/touchpad** — wire paint input to performer's gesture device for real-time falloff authoring.

**The complete falloff family is now 6 sources:**
- **Shape Falloff** — geometric (distance to 3D shape)
- **Texture Falloff** — image-based (samples a TOP)
- **Infection Falloff** — temporal viral spread
- **Attribute Falloff** — converts any pre-existing attribute
- **Noise Falloff** — procedural noise sampled at point positions
- **Paint Falloff** — manual viewport painting

All 6 write `popxFalloff` (or custom `Outputfalloffattr` for layering). Downstream modules are agnostic to the source.

---

### Remap Falloff — fit/clamp/invert/ramp transform of an existing falloff attribute

**Example:** `move along curve 4.toe`

**Concept:** Lightweight transform module for an existing per-instance attribute (typically `popxFalloff`). Applies fit/clamp/invert/ramp/abs operations and writes the result. Distinct from Attribute Falloff (which CONVERTS any attribute INTO popxFalloff) — Remap Falloff is for transforming an existing falloff non-linearly.

**Pipeline position:** anywhere downstream of a falloff-writing module. Often used between two stages where the second stage needs a transformed version of the first stage's falloff.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Remap | `Inputattr` | Attribute to read (default `'popxFalloff'`) |
| Remap | `Outputattr` | Attribute to write (default `'popxFalloff'`; can write to a new name to layer) |
| Remap | `Clamp`, `Fit`, `Auto` | Standard normalization options |
| Remap | `Inputmin/max`, `Outputmin/max` | Range remap |
| Remap | `Invert` | 1−x flip |
| Remap | `Absvalue` | Absolute value |
| Remap | `Enableremapramp`, `Remaptop` | Use a TOP as 1D LUT for nonlinear remap (gamma curves, custom shapes) |

**WOBAR application:**
- Invert a falloff to drive an effect on the OPPOSITE side (instances with low source falloff → high downstream effect)
- Fit a tight dynamic range falloff to a wider one for stronger downstream response
- Pass through a Ramp TOP for non-linear curves (audio-reactive ramps work here too — animate the Remap TOP for evolving response curves)

**Distinction recap:**
- **Attribute Falloff** — converts any per-instance attribute INTO popxFalloff (general source bridge)
- **Remap Falloff** — transforms an existing popxFalloff (non-linear transformation in-place)

---

### Reorient — redefine instance local axes without visibly transforming geometry

**Example:** `reorient 1.toe`

**Concept:** Subtle but architecturally important module. Writes a new `popxOrient` quaternion attribute that **redefines each instance's local coordinate frame** — without visibly changing the geometry. Used to "reset" local frames after Aim/OrientMesh/Randomize rotation operations so downstream Transform Modifiers operate in predictable axes (typically world axes).

**The problem it solves:** randomized/aimed instance rotations make each instance have its own local frame. Downstream `Transform Modifier.Tz=1` then translates each instance along ITS rotated Z → they scatter in random directions. Reorient writes a NEW orient quaternion (typically identity) → downstream transforms operate in world axes → instances move uniformly while still appearing visually rotated.

**Pipeline position:** between rotation-modifying modules (Aim, OrientMesh, Randomize Rotation) and downstream Transform Modifier.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `Orientsource` | Two modes: **`'ptattr'`** (read orientation from an attribute already on the instance — for "I have computed per-instance orientations and want to apply them"); **`'refgeo'`** (find each instance's closest point on a separate reference geometry and copy that point's orientation — for "use this mesh's surface orientation as a guide for instances near it"). Symmetric with Advect's source modes. |
| `Referencegeo` | Optional reference geometry for the new frame |
| `Maxdistance`, `Distribution` | Reference geo lookup strategy |
| `Attrtype` | `'quat'` (quaternion) / `'normal'` / `'up'` / `'matrix'` — what kind of attribute defines the new frame |
| `Quatattr` | When type='quat': attribute name (e.g. `'NewOrient'`); identity quaternion = `(0,0,0,1)` |
| `Normalattr`, `Upattr`, `Matrixattr` | Corresponding attribute names for non-quaternion types |

**The "randomize visually, reset functionally" pattern:**
```
Instancer → Randomize (Rotation, Rotrand=True)         # rotates instances visually
         → attributePOP (NewOrient = (0,0,0,1))        # identity quaternion attribute
         → Reorient (Attrtype='quat', Quatattr='NewOrient')  # reset local frames
         → Transform Modifier (Tz=1)                   # NOW operates in WORLD Z axes
         → render
```

Without Reorient: instances translate in their OWN rotated axes → scatter. With Reorient: they translate in world axes → uniform motion despite visual randomness.

**WOBAR application:**
- **Random-looking but coordinated motion** (`'ptattr'` mode) — chaotic visual variety + uniform audio response.
- **Reset after Aim** (`'ptattr'` mode) — Aim points instances at target; Reorient resets axes; Transform Modifier operates in world space again.
- **Reference-geometry-driven orientation field** (`'refgeo'` mode) — instances near a mesh get the mesh's surface orientation; downstream transforms operate in that local frame. WOBAR uses:
  - **Radial-outward from orb center** — sphere as reference geometry; instances around it inherit outward-pointing local Z; Transform Modifier Tz produces radial pulsing on audio drive.
  - **Surface-tangent on brand mark** — wordmark mesh as reference; instances become tangent-aligned; Tz translates them perpendicular to the surface (think "letterforms growing fur perpendicular to their faces").
  - **Aligned to flow field** — pair OrientMesh's curl-noise mode + Reorient(refgeo) → instances' local frames bend with the flow.
- **Authoring/debug** — bypass to compare; reveals exactly how Reorient changes downstream behavior.

---

### Subdivider — recursive subdivide + extrude generator (crystalline spikes, coral, dragonfruit shells)

**Example:** `subdivider.toe`

**Concept:** Per-face mesh transformer that **subdivides each face N times, then extrudes (with optional inset) outward along normals**. The result depends on params: `Inset≈0` produces cube/spike protrusions; `Inset≈1` collapses to pyramid points; large `Extrudestrength` makes long spikes; falloff masking spikes only certain regions. Iterating the whole subdivide+extrude loop multiple times produces **fractal coral / dragonfruit / crystalline aggregates**.

**Pipeline position:** between any source mesh (sphere, cube, custom geo) and downstream rendering. Works on triangle/quad meshes; output is a much-higher-poly displaced mesh.

**Key parameters:**

| Parameter | Default | This example | Purpose |
|-----------|---------|--------------|---------|
| `Subdivisions` | 0 | 4 | Subdivide each face this many times **before** extrude (higher = finer spike density) |
| `Extrudestrength` | 0.0 | 5.0 | How far to push extruded faces outward along normals. **Large values = long spikes**. |
| `Extrusionfalloffexp` | 1.0 | 8.0 | Falloff exponent along extrusion length — higher = sharper, narrower spike tips |
| `Inset` | 0.0 | 0.52 | Inset extruded face inward before push. `0`=full-face cubes; `1`=collapse to pyramid points; mid=tapered crystals |
| `Iterations` | 1 | 1 | Recurse subdivide+extrude this many times. **`Iterations=2+` produces fractal coral** (spikes growing on spikes) |
| `Postsubdivide` | False | True | Apply Catmull-Clark style smoothing after extrusion (rounded crystal vs. faceted polygonal) |
| `Maxtriangles` | 100000 | 100000 | Output cap — safety limit (subdivision is multiplicative in triangle count) |
| `Dofalloff` / `Falloffattr` | False / `'popxFalloff'` | True / `'popxFalloff'` | **Spike only where falloff is non-zero** — per-region crystallization. Combine with audio-driven falloff TOP for bass-reactive spikes. |
| `Minarea` | 0.001 | — | Skip faces below this area (avoids degenerate spike spam) |
| `Creaseweight` | 0.0 | — | Catmull-Clark crease control for sharper edges when `Postsubdivide=True` |
| `Nml` | `'alwayscompute'` | — | Normal recomputation mode (preserve | always recompute) |
| `Compnmltech` | `'atomiccompswap'` | — | GPU technique for averaging per-vertex normals from contributing faces |

**Canonical pattern — bass-reactive crystal sphere:**

```
spherePOP → Texture Falloff(audio FFT TOP, P→UV lookup) → Subdivider(Subdivisions=4, Extrudestrength=5.0, Inset=0.52, Extrusionfalloffexp=8.0, Dofalloff=True, Iterations=1, Postsubdivide=True) → render
```

The audio-driven falloff masks which faces extrude; bass hits crystallize one region, kicks crystallize another. With `Iterations≥2`, spikes grow on spikes between hits.

**WOBAR application:**
- **Act 1 cosmic descent — fractal crystalline orb** that erupts spikes on first kick. `Extrudestrength` bound to envelope-followed kick channel ramps from 0→8 on impact.
- **Brand-mark crystallization** — WOBAR wordmark mesh + Texture Falloff sampling an audio TOP → spikes erupt only on regions hit by the dominant frequency.
- **Coral organism** — `Iterations=3, Subdivisions=2, Inset=0.55` over a sphere produces bumpy fractal coral; pair with TrailPOP for "grown" reveal.
- **Act 4 clarity diamond** — `Iterations=1, Postsubdivide=False, Inset=0.85` (sharp tips, faceted) on a low-poly icosahedron → angular reflective gem. Pair with PBR mirror MAT for liquid-light readings.
- **Drop crystallization** — `Subdivisions` and `Iterations` ramp up exactly on the drop; mesh visibly "freezes" from smooth sphere into crystal.

**Cost:** subdivision is multiplicative — `Subdivisions=4` on a 32-poly sphere → ~32 × 4^Subdivisions × Iterations = 8000 base subdivided faces; with `Iterations=2` → 64000+. Always set `Maxtriangles` to cap. 60fps comfortably with `Subdivisions=3, Iterations=1` on input meshes <500 polys.

**Replaces:** Houdini PolyExtrude → Subdivide → repeat networks; Cinema 4D MoExtrude effector chains; custom GLSL displacement-along-normal shaders.

**Gotcha:** without `Dofalloff=True`, every face extrudes at full `Extrudestrength` → uniform spike ball. Pair with **Texture Falloff or Shape Falloff upstream** for spatially varied / audio-reactive spikes.

---

### Strange Attractor (SA) — chaos-equation point advection (Lorenz / Thomas / Aizawa / etc.)

**Example:** `strange attractors.toe`

**Concept:** Per-point integrator for **3D nonlinear chaotic systems**. Treats each input point as an initial condition and advances it along the chosen attractor's velocity field every frame. Produces the canonical "strange attractor" cloud — Lorenz butterfly, Thomas spiral, Aizawa torus, Halvorsen swirl. Output points carry both updated `P` (position) and `PartVel` (velocity) attributes; downstream modules can read either.

**Pipeline position:** runs over an instance stream after some randomization (initial scatter is essential — homogeneous starts collapse to a single trajectory). Output feeds geometry instancing or trail generators.

**Setup sequence (Advect mode — REQUIRED 4-step activation):**

```
Solvermode = 'Advect'
Pointsupdatepop = <downstream POP — REQUIRED, not optional>
↓
Pulse Initialize    # reset & spawn particles
Pulse Start         # begin from initialized state
Toggle Play = True  # enable continuous playback
(Step pulse for frame-by-frame when paused)
```

**Skipping any of Init/Start/Play freezes the simulation post-init.** This is the universal POPX simulation pattern (see "POPX Universal Patterns" at top of guide).

**Key parameter pages:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| SA | `Strangeattractor` | Preset chaos system. **11 presets:** `'lorenz'` (default), `'aizawa'`, `'thomas'`, `'halvorsen'`, `'dadras'`, `'chen'`, `'rossler'`, `'sprott'`, `'fourwing'`, `'nosehoover'`, `'custom'`. Each has its own visual signature and stable basin shape. |
| SA | `Customsa` | DAT reference for custom equations (when `Strangeattractor='custom'`) |
| SA | `Generatedat` (pulse) | Generate an editable Script DAT containing the current preset's equations — the canonical way to tweak coefficients at the math level |
| SA | `Ua` / `Ub` / `Uc` / `Ud` / `Ue` / `Uf` | Six scalar coefficient slots fed to the attractor equations (availability varies by preset — Lorenz uses Ua/Ub/Uc as σ, ρ, β; Aizawa uses all six). |
| SA | `Solvermode` | `'simple'` evaluates the velocity field at input positions per frame (no integration history — looks static unless input changes); **`'advect'` integrates with internal state** (requires Init/Start/Play activation, see above). |
| SA | `Timescale` | Solver dt multiplier. `1.0` = baseline; `6.5` = fast trajectory motion; lower = lazy drift. Higher Timescale also requires more sub-iteration for stability. |
| SA | `Pointsupdatepop` | **Required in Advect mode.** Reference to a downstream POP — the solver writes its updated state through this feedback handle each frame. |
| SA | `Initializepulse` / `Startpulse` / `Play` / `Steppulse` | Activation sequence pulses (see "Setup sequence" above). |
| Bounds | `Mintype1/2/3`, `Maxtype1/2/3` | Per-axis boundary behavior. **Four options: `'off'` / `'clamp'` / `'loop'` / `'zigzag'`** (NOT `'wrap'` — that name doesn't exist in the docs). |
| Bounds | `Min1/2/3`, `Max1/2/3` | Per-axis bounds values |

**Output attributes:**
- `P` — updated position
- `PartVel` — current velocity vector (3D). Pair with downstream `mathmixPOP(comb0oper='length', comb0scopea='PartVel', comb0result='LenVel')` to compute speed; drive instance scale or color by `LenVel`.

**Canonical pattern — chaos-attractor instance cloud:**

```
pointGenerator(N points) → noisePOP(random rotate) → SA(Strangeattractor='thomas', Solvermode='advect', Timescale=6.5) → noisePOP(small random pos jitter) → mathmixPOP(length of PartVel → LenVel) → null → geometryCOMP(instancing=True, instanceop=null, instancetx/ty/tz='P(0..2)', instancesx/sy/sz='LenVel')
```

`pxform` rotation on the geo COMP (`pry.expr='absTime.seconds*15'`) adds slow whole-system Y-spin for added depth.

**WOBAR application:**
- **Act 1 cosmic descent — Thomas/Aizawa cloud** as the wordmark dissolves; thousands of small instances trace chaos trajectories. Strange attractors are the single most "psychedelic-yet-mathematical" visual primitive available; perfect for the trance/awakening transition.
- **Act 4 clarity butterfly** — Lorenz butterfly with high-saturation gold trail (TrailPOP downstream of SA), reading as "consciousness untangling" at the resolution beat.
- **Background plate behind any act** — sparse SA cloud (200–500 points) at low opacity behind primary visuals; constant motion that never repeats.
- **Audio-driven coefficient morph** — bind `Ua`/`Ub`/`Uc` to slow audio bands → the attractor's *shape* warps with the music (e.g. ρ in Lorenz controls how separated the lobes are; modulating it makes the butterfly breathe).
- **Per-band attractor stack** — three SA modules with different presets; sub-bass → Lorenz, mids → Thomas, highs → Aizawa, all blended at render. Distinct chaos signatures for each frequency band.

**Cost:** SA solver is GPU-fast — 5k–20k points typical at 60fps. Cost scales linearly with point count and `Timescale` (higher Timescale = more numerical iteration per frame to maintain stability).

**Replaces:** Custom GLSL feedback loops implementing Lorenz / Aizawa equations, Houdini Solver SOP with hand-written VEX, particle-system kludges that try to imitate strange-attractor flow without the actual math.

**Gotchas:**

1. **`Solvermode='simple'` does not animate** — it just evaluates the velocity field at input positions every frame. With static input, output is static. **Use `'advect'` + the Init→Start→Play sequence for the cloud-of-particles look.**
2. **Skipping `Pulse Start`** after Initialize freezes the integration. Most common SA failure mode — observed across multiple build sessions before the docs review.
3. **`Pointsupdatepop` is REQUIRED in Advect mode** — it's the feedback handle the solver writes through. Without it, no continuous integration.
4. **Initial scatter is mandatory** — without an upstream noise/randomize on positions, all points share trajectory and visually overlap. Use `pointgenPOP(shape='sphere')` + downstream `noisePOP(combineop='none', noiseoutputattrscope='Rotate')` to scatter without disturbing P.
5. **Boundary `Mintype/Maxtype='wrap'` doesn't exist** — the option is `'loop'` (per docs).

---

### Shortest Path — graph shortest-path solver on POP geometry (vascular trees, transit networks)

**Example:** `shortest path.toe`

**Concept:** Given a mesh + start-point group + end-point group(s), finds shortest paths through the mesh's connectivity graph from start to each end. **The aesthetic is profound:** single-source-to-many-destinations naturally produces branching tree structures because paths share common segments — exactly how vasculature, leaf veins, lightning, transit networks, and capillary trees develop in nature.

**Pipeline position:** between mesh source and any line-consuming module (Sweep, MoveAlongCurve, render). `in0` = mesh; `in1` = start/end points (typically merged POP with point groups identifying which).

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `Startgroup` | Group name identifying start points (e.g. `'start'`) |
| `Endgroup` | Group name identifying end points (e.g. `'end'`) |
| `Costattrib` | Attribute name to use as edge cost (default: edge length); custom cost = paths prefer low-cost regions |
| `Iterations` | Solver passes (200 typical) |
| `Nebrtype` | `'connected'` (use mesh edges) or alt (distance-based) |
| `Maxdistance`, `Numhashbuckets`, `Maxneighbors` | For non-connected mode |
| `Maxpaths`, `Maxverts` | Capacity caps |
| `Lockalternate` | Lock to alternating path solutions |
| `Visualizepaths`, `Visualizecost`, `Visualizestartend`, `Displaylinestrips`, `Displaygeo` | Debug visualizations |

**WOBAR application:**
- **Vascular tree generation** — single start point (e.g. orb center) + many end points (around perimeter, brand mark vertices) → naturally tree-shaped paths.
- **Brand-mark vascular** — WOBAR wordmark mesh with start at center, ends at mark perimeter; veins grow out of brand.
- **Audio-driven branching** — fix start, drive end-point positions from audio CHOPs (FFT bin coords) → each beat re-routes the branches.
- **Multi-start competing trees** — start group with multiple seeds; trees compete for territory of end points.

**Cost:** scales with mesh complexity × path count × iterations. 200 paths on a circular planar patch runs at 60fps; high-density meshes may slow significantly.

---

### Planar Patch — generate 2D triangulated mesh in a defined shape

**Example:** `shortest path.toe`

**Concept:** 2D mesh generator. Creates a triangulated patch in various shapes (circle, rectangle, custom) with controllable edge length, relaxation, and orientation. Used as input for modules that need triangulated 2D geometry (Shortest Path, Mesh Fill, etc.).

**Pipeline position:** standalone source. Outputs a triangulated POP mesh.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `Shape` | `'circle'` (this example), `'rectangle'`, custom |
| `Edgelength` | Target triangle edge length (smaller = denser mesh) |
| `Relaxiters` | Smoothing passes on triangulation (higher = more uniform) |
| `Seed` | RNG for triangulation variation |
| `Orient` | `'xy'`, `'yz'`, `'xz'` — which plane |
| `Centerx/y/z`, `Scalex/y/z`, `Uniformscale` | Position + size |
| `Roundcorners`, `Cornerradius` | Corner softening |
| `Side`, `Taper`, `Skew`, `Innersizex/y` | Shape variations |
| `Openarc1`, `Openarc2` | For circle: angular range open (`Openarc2=270` = ¾ circle) |

**WOBAR application:** alternative to gridPOP when you need irregular triangulation (better for shortest-path, mesh-fill, organic patterns). Creates clean triangulated patches in arbitrary 2D shapes.

---

### Sweep — generate tube/ribbon surface from line strips with along-curve scale and color

**Examples:** `shortest path.toe` (tapered vascular trunks); `soft body (strings).toe` (`Skinops='group'`, `Inc=line.divs+1` for many short polylines as separate tubes); `soft body (interactive cloth).toe` & `spring 2.toe` (`Twistamount=360`, `Applyscale=True` for folded ribbon look); **`sweep 1.toe` (donut/torus topology — `circlePOP` backbone + `Surfaceshape='square'` + `Roundcorners=True` + `Closedsurface=True` + `Twistamount=360`)**

**Concept:** Takes line-strip geometry and generates a swept-surface mesh — tubes, ribbons, custom cross-sections following the input curves. Critically supports along-curve **scale modulation** (thick trunk → thin branches) and **color modulation** (gradient along path) via 1D TOP LUTs. Standard for converting any line-output (Shortest Path, MoveAlongCurve, gridPOP linestrips) into rendered geometry.

**Pipeline position:** between line-output and render.

**Key parameters by page:**

**`[Orient Curve]` — cross-section orientation along curve**

| Parameter | Purpose |
|-----------|---------|
| `Reorientcurve`, `Closedcurve`, `Invertn` | Curve preprocessing |
| `Customfirsttangent`, `Firsttangentx/y/z` | Initial direction override (avoids flipping) |
| `Twistamount`, `Twisttop` (1D LUT), `Twistpercurve`, `Twistbyattribute`, `Twistattr` | Twist along curve |

**`[Surface]` — cross-section + along-curve modulation**

| Parameter | Purpose |
|-----------|---------|
| `Surfaceshape` | **Three cross-section types per official docs:** `'roundtube'` (circular profile, default), `'squaretube'` (rectangular — pair with `Roundcorners=True` + `Cornerradius` for tapered ribbon), **`'input'` (use input[1] geometry as a custom cross-section curve — `circlePOP`, `patternPOP`, hand-drawn line strip, anything)**. Earlier guide versions documented additional names (`'tube'`, `'square'`, `'rectangle'`) — those are likely legacy aliases or our local POPX install's internal labels; the official 1.3.0 docs name them as above. |
| `Width` | Base cross-section width |
| `Columns` | Cross-section subdivision (8 = octagonal tube) |
| `Roundcorners`, `Cornerradius`, `Cornersides` | Corner softening |
| `Scalecrosssections` | Master scale |
| `Skinops`, `Closedsurface`, `Outputquads`, `Generatevertexnormals` | Topology |
| **`Applyscale`** + `Scaletop` + `Scalepercurve` + `Scalebyattr` + `Scaleattr` | **Scale-along-curve** — `Scaletop=<ramp 1→0>` produces thickening trunk → thin branches WITHOUT any per-branch logic |
| **`Applycolor`** + `Colortop` + `Colorpercurve` | **Color-along-curve** via TOP LUT (red→blue gradient in this example) |

**`[Attributes]`** — which attributes propagate from input

**WOBAR application:** the renderer for any line-based generative pattern. Pair with Shortest Path for vascular trees, with MoveAlongCurve for tube ribbons, with DLG for filled labyrinth tubes. The `Applyscale` + `Scaletop` combo is the canonical "trunk-to-branch tapering" pattern.

**Per-curve modulation by 2D TOP (sweep stack as video player / spectrogram waterfall) — `sweep 2.toe`:**

When the input contains **N curves** and you set `Scalepercurve=True`, `Colorpercurve=True`, and/or `Twistpercurve=True`, each curve **reads its own row of the modulation TOP**:
- TOP V-axis = curve index (each row = one curve in the stack)
- TOP U-axis = position along that curve (0 → 1 from start to end)
- TOP RGB = scale × color (or twist amount, depending on which TOP par)

Pipeline:
```
linePOP(divs=200) + linePOP(divs=20) → copyPOP(line1 onto line2's 21 points → 21 horizontal lines stacked vertically)
  → transformPOP(aspect correct, ty per-row offset)
  → Sweep(in0=stacked lines, in1=cross-section circlePOP, Surfaceshape='input',
          Scaletop=videoTOP, Scalepercurve=True,
          Colortop=videoTOP, Colorpercurve=True,
          Twisttop=videoTOP, Twistpercurve=True, Twistamount=1440,
          Width=0.05, Scalecrosssections=0.01, Inc=op('info_curve_pts')['num_points'])
```

**A single TOP can drive multiple modulators simultaneously** — the example uses one video-feed TOP for both Color and Twist, with a separate TOP for Scale. This is the **3D-sweep-print** of any 2D image: video, audio spectrogram, brand mark, FFT history. Each pixel column becomes a bump or color tint on its corresponding curve segment. WOBAR variants:
- **Camera feed → 3D sweep stage backdrop**: audience image rendered as scale-and-color stacked sweeps on screen.
- **Audio spectrogram waterfall**: scrolling FFT history TOP (rows = time, cols = frequency bins) → stacked sweeps form a 3D temporal frequency landscape.
- **Brand wordmark embossed sweep**: textTOP of WOBAR → into Scaletop → wordmark sits as 3D bumps in a horizontal sweep array.
- **Per-band sweep row**: 5 horizontal lines (one per audio band: sub / bass / mid / hi / air); per-band envelope channel writes to that row of a 5×N TOP via constantTOP / chopToTOP. Each band drives its own sweep's scale/color independently.

**Closed-loop topology (donut / torus / wormhole ring):**

```
circlePOP(divs=200, orient='zx') → (optional patternPOP for procedural attribute writes) → Sweep(Surfaceshape='square', Width=0.4, Roundcorners=True, Cornerradius=0.106, Cornersides=20, Twistamount=360, Closedsurface=True)
```

`Closedsurface=True` joins the first and last cross-section so the sweep loops back on itself — required for ring/wormhole topology. Without it the donut ends would be open. WOBAR variants: tunnel ring around the wordmark, twisted Möbius brand element, audio-driven `Width.expr` makes the donut breathe with the kick.

---

### Soft Body + Constraints + Constraint Property + SBPP — position-based dynamics (PBD) soft-body / cloth / inflatable simulation

**Example:** `soft body (inflate).toe`

**v1.3.0 BREAKING CHANGES:**
- The standalone **`Constraints Config` operator is REMOVED** — constraints are now configured WITHIN the POPX **Constraints** module itself.
- **Soft Body has a restructured Collisions architecture** — multiple geometry types (ground plane, bounding box, sphere, box, plane, SDF, T3D, T2D), self-collision with configurable neighbor search, maximum acceleration limiting, integration order selection (first/second), collision-triggered fallback integration mode.

**Setup sequence (exception — Soft Body uses Init+Play, NO Start step):**
```
Connect POP geometry to Input 0
Connect constraints data to Input 1
Connect collision geometry to Input 2 + enable desired collision types
↓
Pulse Initialize
Toggle Play = True       # NO Start step — Soft Body is the exception
```

**Concept:** Four cooperating POPX modules implement a complete **position-based dynamics soft-body simulation system** — comparable to Houdini Vellum. Soft Body is the PBD solver; Constraints generates the constraint topology (springs holding the body together); Constraint Property modifies properties per-region; SBPP smooths and visualizes the result.

**The four modules and their roles:**

#### **Soft Body** — PBD physics solver

Standalone solver. Inputs constraint geometry (`in0`); outputs simulated mesh.

**Key parameter pages:**

- **`[Soft Body]`** — `Solvermode`, `Timescale`, `Timestep`, `Substeps`, `Iterations` (4 typical), `Targetupdatepop`, `Play`
- **`[Collisions]`** — five simultaneous collision modes:
  - **Ground**: `Enablegroundcollision`, `Groundposition*` (default 0,0,0 = y=0 plane), `Groundmargin`, `Displayground`, `Groundstaticscale` / `Grounddynamicscale` (ground-specific static/dynamic friction multipliers — independent of body-on-body friction in `Dynamicscale`)
  - **BBox**: `Enablebboxcollision`, `Bbox`, `Bboxmargin`
  - **Geometry**: `Collisiontype` (`'pop'` / `'t3d'` SDF / sphere / box / etc.), `Collisionpop`, `Collisontop` (3D SDF), `Collisionoffset`, shape primitive params
  - **Custom bounds**: `Usecustombounds`, `Lower/Upperbounds*`
  - **Self-collision**: `Enableselfcollision`, `Maxdistance`, `Numhashbuckets`, `Maxneighbors`
- **`[Forces]`** — `Gravityx/y/z` (default 0,-9.8,0), `Gravitymultiplier`, `Velocitydamping`, `Staticthreshold`, `Dynamicscale`, `Enableexternal`, `Enableself`, **Grabber** for interactive cursor manipulation (`Enablegrabber`, `Grab`, `Grabposition*`, `Grabradius*`, `Grabstrength`)
- **`[Advanced]`** — `Integrationorder`, `Enablemaxacc`, `Maxacceleration`, `Limitaccel`, `Fallbackcollision`

#### **Constraints** — generate constraint topology

Generates the springs / connections holding the soft body together.

**Constraint types** (`Constrainttype`):
- **`'cloth'`** — preserves surface (stretch + bend springs along mesh edges)
- **`'struts'`** — preserves volume (additional internal springs between non-adjacent points)
- **`'pressure'`** — internal volumetric pressure (gas-filled balloon behavior; bodies resist squashing, push outward from inside a closed mesh)
- **`'string'`** — 1D rope/hair topology — stretch + bend along a polyline; use for hair, ribbons, tassels, ropes
- **`'pin'`** — pins points to animation/positions
- **`'attach'`** — attaches to other geometry
- **`'glue'`** — bonds points

**Volume preservation choice:** `'struts'` resists deformation via internal springs (stiffer, more solid feel). `'pressure'` resists deformation via gas pressure (softer, more balloon feel — gives squash-and-bounce look in self-collision scenarios). Often combined: cloth surface + pressure for balloons; cloth + struts for inflatables.

**Key parameter pages:**
- **`[Geometry]`** — `Mass`, `Setmass`, `Density`, `Setthickness`, `Edgelengthscale`, `Normaldrag`, `Tangentdrag`, `Enablepartition`, `Partitionmethod`, `Numpieces`, `Targetgeometry`, `Targetpath`. **`Thickness` has three modes:** `'unchanged'` (default), `'set'` (apply Setthickness uniformly), `'calcvarying'` (**auto-compute per-point thickness from local density** — recommended for self-collision on irregular meshes).
- **`[Constraints]`** — `Constrainttype` + per-type params:
  - **Stretch**: `Stretchstiffscale`, `Stretchstiff`, `Stretchdampratio`, `Stretchrestscale`, `Stretchplasticity`, `Stretchthreshold`, `Stretchrate`, `Stretchhardening`, `Stretchgroup`
  - **Bend**: same set
  - **Pin**: `Pinpoints` (group/attribute name marking pinned points), `Pintype` (`'permanent'` = freeze at start position; `'stopped'` = follow source position but contribute zero velocity, use when source is animating to prevent whip-crack), `Matchanimation` (when True + `'stopped'`, pinned points read updated positions every frame from input geometry — the mechanism for hair/strings staying attached to a moving rigged character)
- **`[Search]`** — `Struts`, `Constperpoint`, `Strutsjitter`, `Anyhit`, `Detach`, `Strutsseed`; `Attach search` and `Glue` params

#### **Constraint Property** — modify constraint properties per-region

Modifies stiffness/damping/rest-length/plasticity of EXISTING constraints, optionally per-instance via attribute lookup.

**Key parameters:**
- `Constraintgroup` — which constraint group to modify (e.g. `'cloth'`)
- **Constraints page:** `Stiffness`+`Stiffop`, `Dampingratio`+`Dampratioop`, `Restscale`+`Restscaleop`, `Plasticthreshold`/`Plasticrate`/`Plastichardening`
- **Map page:** drive any constraint property from a per-point attribute. Critical: **`Enablerestscalemap=True, Restscaleattr='popxFalloff'`** = rest length driven by falloff. **Constraints with higher rest length = more inflated locally.** This is how spatial inflation variation works.

#### **SBPP** (Soft Body Post Process) — smooth + visualize

Post-processing for soft body output.

**Operations page:** `Bluriterations`, `Maxneighbors`, `Blurstrength` (smoothing); `Subdidve`, `Depth`, `Creaseweight`, `Simplecoeffs` (subdivision for finer rendering).

**Visualize page:** togglable color overlays — `Simulatedgeometry`, `Collisions`, `Selfcollision`, `Thickness`, `Distancealongedges`, `Bendacrosstriangles`, `Struts`, `Attachtogeometry`, `Pintotarget`. Plus `Property`, `Displayproperty`, `Maxvalue` for visualizing custom constraint properties (e.g. stretch stress) as color on the surface.

**Complete pipeline:**

```
mesh source
    → Constraints (Constrainttype='cloth', Stretchgroup='cloth')
    → Constraints (Constrainttype='struts')   # for volume preservation / inflation
    → Constraint Property (Constraintgroup='cloth', Map page: Restscaleattr='popxFalloff')
    → Soft Body (PBD solver, Iterations=4, collisions enabled)
    → SBPP (Bluriterations, optional stress viz)
    → render
```

**WOBAR application:**
- **Audio-driven inflation** — `Constraint Property.Restscale` driven by audio energy + falloff → body inflates with the music. "Soft body breathing" — direct on-brand for shadow-work / felt-not-aggressive.
- **Brand mark deformable** — WOBAR wordmark mesh as soft body; collision sphere from cursor. Brand becomes a squishy interactive object.
- **Performer-shaped soft body** — body-tracked silhouette mesh → soft body → audio drives inflation. Performer's body pulses with music.
- **Glass-orb interior soft body** — small soft body sized to orb interior; through orb refraction, looks like organism inside.

**Two canonical patterns:**

1. **Inflatable** (`soft body (inflate).toe`) — Constraints(cloth) + Constraints(struts) + Constraint Property(Restscaleattr=audio-driven falloff) + Soft Body. Body inflates spatially per falloff.

2. **Pinned cloth with interactive Grabber** (`soft body (interactive cloth).toe`) — Planar Patch → groupPOP marking pin points (corners/edges) → Constraints(pin) + Constraints(cloth) → Soft Body with `Iterations=25` (high for cloth stability) and `Enablegrabber=True`, `Grab.expr=cursor.lselect`, `Grabposition*.expr=cursor.insideu/v`. Cloth hangs from pinned points; user click-drags to pull and stretch in real time. WOBAR variants: audio-grabbed cloth (cursor → audio peak position), wordmark-shaped fabric, multi-pin choreography (animated pin positions).

3. **Multi-body self-colliding pressurized softbodies** (`soft body (self collision).toe`) — multiple instanced spheres → Constraints(cloth, `Thickness='calcvarying'`, `Edgelengthscale=0.35`) + Constraints(pressure) → Soft Body with `Iterations=15`, `Enableselfcollision=True`, `Maxdistance=0.15`, `Maxneighbors=5`, **`Gravitymultiplier=0.505`** (reduced — full gravity overpowers pressure), **`Velocitydamping=0.01`** (prevents oscillation), **`Dynamicscale=0.1`** (high friction stabilizes contact). Multiple balloon-like bodies squish, deform, settle against each other and bounding walls. WOBAR variants: audio-driven balloon cluster (each sphere's pressure driven by different audio band), brand-mark balloons, physical mosh pit (Grabber as shaker).
   - **Self-collision tuning recipe:** reduce gravity (~0.5×), add velocity damping (0.01), increase dynamic friction (0.1), use `Thickness='calcvarying'` for auto-thickness, use `'pressure'` constraint over `'struts'` for balloon feel.

4. **Single soft body bouncing on built-in ground** (`soft body (simple collision).toe`) — sphere POP → Constraints(`Constrainttype='cloth'`, surface) + Constraints(`Constrainttype='struts'`, `Constperpoint=10`, internal) → Soft Body with **`Enablegroundcollision=True`** (no external collider needed — built-in infinite ground plane at `Groundposition*=0`), `Iterations=20` (single body — can afford more than self-collision's 15), `Ty=2.0` (drop from above), `Scale=2.0`, default gravity. Sphere falls, deforms briefly on impact, settles. **Simplest possible soft body baseline** — start here when prototyping, then add complexity. WOBAR uses: drop test for any new mesh as soft body, brand-mark thud onto stage, percussion-triggered drop (kick fires `Initializepulse`).
   - **Built-in ground vs. collider body:** `Enablegroundcollision=True` is cheaper than a separate plane body (no extra Constraints chain) and gives infinite extent. Use it when one flat ground is enough; switch to a collider body (Constraints + Constraint Property + merge into solver) when you need contoured terrain or moving floors. `Groundstaticscale` / `Grounddynamicscale` tune ground friction independently from body-on-body friction.
   - **Stacked Constraints pattern:** `cloth` (surface springs) → `struts` (internal volume preservation) chained in series gives a sphere that holds shape better than cloth alone but is still squishy. Each Constraints module writes its own constraint set; the Soft Body solver uses all of them. Order doesn't matter for solver correctness, but later modules can reference earlier groups via `Pinpoints`/`Geogroup`.

5. **Strings/hair attached to a moving rigged character** (`soft body (strings).toe`) — animated FBX rig (Mixamo character, `speed=0.65`, `scale=0.01`) → `importselectPOP` (geometry from rig) → `skindeformPOP` (skeletal deform) → `sprinklePOP(numpoints=5000)` (5000 random points on deformed surface) → `linePOP(divs=8, pt1posz=1.0)` template (single 8-segment string) + `groupPOP(grname='pin', pattern='0 1')` (mark first 2 points of line as `pin`) → `copyPOP(dotemplatescale=True, dotemplaterotateto=True)` (copy line to each sprinkle point — each line orients to local surface frame, root pinned to surface) → Constraints(`Constrainttype='string'`, `Pinpoints='pin'`, `Pintype='stopped'`, `Matchanimation=True`, `Edgelengthscale=0.25`) → Soft Body (string roots track skin per-frame; tips dangle and swing dynamically) → `forceradial1` (optional radial blowback as character moves) → Sweep (`Width=0.005`, `Skinops='group'`, `Inc=line.divs+1=9` so each polyline becomes one tube) → render. **This is the recipe for hair, fur, fringe, tassels, ribbons, dreadlocks attached to anything that animates.** WOBAR variants: brand-mark with hair (POPX wordmark mesh as source, fringe attached), performer-tracked silhouette mesh with audio-driven blow-back, ribbon dance (sparse strings, length=4 sec lag, color-modulated by act).
   - **Why `Pintype='stopped'` + `Matchanimation=True` matters:** with `'permanent'`, pinned points freeze at their start positions and the source moves out from under them — strings detach. `'stopped'` + `Matchanimation=True` re-reads pinned-point positions from the source every frame, so strings stay rooted while their free ends simulate dynamically.
   - **Sweep convention for many polylines:** when many short curves of equal length feed Sweep, set `Skinops='group'` and `Inc=<points per polyline>` (here `line.divs+1=9`) so the module knows where each curve ends. Without this it tries to interpret all input as one giant polyline.

**Cost:** PBD with `Iterations=4` and ~1k-vertex mesh runs at 60fps. High-vertex meshes (10k+) drop to 30fps. Self-collision adds significant cost.

**Replaces:** Houdini Vellum import, custom GLSL PBD solver, Cinema 4D soft body sim. Comparable quality to Vellum for cloth and inflatables.

---

### Spring — temporal smoothing / spring-and-damper physics on POPX attributes

**Examples:** `convert.toe`, `spring 1.toe` (2D grid + curl rotation), `spring 2.toe` (1D line + vertical lift + twisted tube — same Spring pattern reduced to a ribbon dancer)

**Concept:** Per-instance spring-damper physics applied to chosen attributes. The module animates an attribute toward its incoming value with mass + spring constant + damping. Used for two main purposes: smoothing audio-jittery attribute drives (so transient kicks don't visually pop), and adding bounce/inertia to instance position/rotation/scale.

**Pipeline position:** anywhere downstream of an attribute writer (Texture Falloff, Convert, etc.). Operates per-instance.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Spring | `Position` / `Rotation` / `Scale` | Toggle which built-in transform attributes get spring physics |
| Spring | `Other` + `Attr` | Apply spring to an arbitrary custom attribute (e.g. `popxFalloff` itself for smoothed falloff transitions) |
| Spring | `Mass`, `Springconst`, `Dampingcoef` | Spring physics constants. `Springconst` higher = snappier; `Dampingcoef` 0–1 (closer to 1 = critically damped) |
| Spring | `Usemassattr`, `Massattr` | Per-instance mass via attribute (variable instance behavior) |
| Spring | `Play` | Solver running toggle |
| Spring | `Pointsupdatepop` | Optional alternate input for "target" values |
| Spring | `Dofalloff`, `Falloffattr` | Standard falloff blending — only spring instances where falloff is non-zero |

**WOBAR application:**
- **Smooth audio attribute drives** — Texture Falloff sampling an audio-driven TOP can be jittery on fast transients. Insert Spring downstream with `Other=True, Attr='popxFalloff'` and tuned damping → transitions feel organic, not glitchy.
- **Inertia on instance positions** — when audio drives Transform.Tx via expression, the response is instant. Spring on Position adds momentum/overshoot — bodies feel like they have weight responding to the beat.
- **Per-instance mass variability** — write a `Mass` attribute upstream (random, position-dependent, or from an image), enable `Usemassattr`. Some instances respond fast, others lag — adds asymmetry to the field response.

**Canonical pattern — elastic attribute-driven deformation** (`spring 1.toe`):

```
gridPOP → Shape Falloff(lineprojection, Ty animated by lfo) → Spring Modifier(Other=True, Attr='popxFalloff', Springconst=0.7, Dampingcoef=0.95) → Transform POP(weightattr='popxFalloff', ry=180)
```

The line projection moves vertically; each grid point sees its falloff value step from 0→1 as the line passes. Spring on the attribute itself converts that step into a damped overshoot. Transform POP then rotates each point by `ry=180°` weighted by the springed falloff → the curl wave travels through the grid with springy lag, producing layered fan/scroll shapes. **This is the recipe for "elastic ribbons", "wave passing through fabric", "scrolling reveal with bounce".** WOBAR variants: title-card reveal scroll synced to drop, audio-rhythm stretch on brand mark, Act 4 clarity reveal as light-front sweeps across geometry.

**Why spring on the attribute (not the transform):** if you Spring `Position`, only the bulk position lags — every point moves identically. By Springing the **driving attribute** (popxFalloff) and letting a downstream Transform module read it via `weightattr`, every point gets its own per-instance lag based on when the attribute's shape source touches it. Result: traveling wave with elastic afterglow, not a uniformly delayed mesh.

**1D variant — bouncing ribbon** (`spring 2.toe`):

```
linePOP(divs=50, pt0x=-0.5, pt1x=0.5) → Shape Falloff(animated source) → Spring Modifier(Other=True, Attr='popxFalloff', Springconst=0.7, Dampingcoef=0.95) → Transform POP(weightattr='popxFalloff', ty=0.5) → Sweep(Width=0.05, Twistamount=360, Applyscale=True) → render
```

Same Spring pattern on a **1D source** with vertical lift (`ty=0.5`) instead of rotation. The 50-division line becomes a ribbon arch as the wave passes; under-damped spring gives bounce. Sweep with `Twistamount=360` rotates the cross-section once along the length, producing a folded-ribbon look (reads as banner/streamer rather than tube). WOBAR variants: percussion-driven banner pulse across the screen, audio-band ribbon stack (one ribbon per band, vertically offset, color-graded per band), mantle-ribbon underneath the wordmark that bounces on every kick.

---

### Texture Falloff — sample a TOP at point positions to write the popxFalloff attribute

**Example:** `convert.toe`

**Concept:** Per-instance falloff value generator. Samples a TOP texture at each point's position (configurable: P.x/y/z, normalized or pixel coords) and stores the sampled luminance/RGBA into an attribute (default `popxFalloff`). Optional layered noise modulation and remap chains baked in. The most flexible way to drive POPX modifier strength from any 2D/3D image source.

**Pipeline position:** runs over an instance stream and writes the falloff attribute. Place upstream of any modifier with `Dofalloff=True` to control its per-instance strength.

**Key parameters (organized by page):**

**`[Texture]` — what TOP to sample and how:**

| Parameter | Purpose |
|-----------|---------|
| `Top` | The TOP to sample (e.g. a Ramp TOP, audio-driven Lookup TOP, GLSL TOP) |
| `Lookupindexattr0/1/2` | Which attribute components to use as UVW lookup (default `P(0)`/`P(1)` = use point position xy) |
| `Lookupindexoffset1/2/3` | Offset added to the lookup |
| `Indexunit1/2/3` | `'normalized'` (0–1 across TOP) or `'pixel'` |
| `Lookupchannel` | `'luminance'` / `'r'` / `'g'` / `'b'` / `'a'` — which TOP channel becomes the falloff |
| `Pixelcentered1/2/3` | Sample at pixel centers (default True) |
| `Cyclic1/2/3`, `Inputextend1/2/3` | Wrap behavior at TOP edges (`'repeat'`, `'mirror'`, etc.) |
| `Interpolate` | Bilinear vs nearest-neighbor sampling |
| `Tx/Ty/Tz/Rx/Ry/Rz/Sx/Sy/Sz` + `Scale` | Transform applied to the lookup before sampling — animate this for "the focal field moves through the instances" |
| `Normalizesamplepos` | Auto-fit sample positions to TOP |

**`[Falloff]` — how to combine + visualize:**

| Parameter | Purpose |
|-----------|---------|
| `Combineop` | `'set'` (overwrite) / `'add'` / `'multiply'` / etc. — how to combine with existing falloff attribute |
| `Combattrscope` | Attribute(s) to combine into |
| `Combstrength` | Blend weight |
| `Outputfalloffattr` | Default `'popxFalloff'`, can write to a different attribute name to layer multiple falloff fields |
| `Previewfalloff`, `Fallofframp` | Debug viz — `'heatmap'` ramp shows falloff as colors |

**`[Noise]` — optional per-point noise modulation:**

| Parameter | Purpose |
|-----------|---------|
| `Applynoise` | Enable noise overlay |
| `Combineopnoise` | How noise combines with the texture falloff |
| `Type` (`'simplex4d'` etc.), `Period`, `Harmon`, `Spread`, `Gain`, `Amp`, `Exp`, `Offset` | Standard noise params |
| `T4dnoise` | 4D noise time component — animate for evolving noise |

**`[Remap]` — output post-processing:**

| Parameter | Purpose |
|-----------|---------|
| `Remap`, `Clamp`, `Fit`, `Auto`, `Inputmin/max`, `Outputmin/max`, `Invert` | Standard remap chain |
| `Enableremapramp`, `Remaptop` | Use a TOP as a 1D LUT to nonlinearly remap the falloff |

**WOBAR application:**
- **Audio-driven focal field** — a Ramp TOP whose phase/center is energy-driven becomes a moving heat zone in the instance field; bodies in the heat zone get full transform strength, bodies outside stay calm. Cleanest way to make audio energy "ripple through" a POPX instance scene.
- **Cursor / hover field for VJ performance** — TOP position fed by mouse → falloff peaks at cursor → Transform pushes bodies away. Performative.
- **Mask-based reveals** — animate a wipe TOP (e.g. growing circle), Texture Falloff inherits it, downstream Transform sets `Sx/Sy/Sz=1` only inside the mask = pieces reveal/hide along a wipe.
- **Layered falloff** — multiple Texture Falloff modules in a row, each writing to a different `Outputfalloffattr` (e.g. `popxFalloff_audio`, `popxFalloff_proximity`) and downstream modifiers picking which attribute they respect. Lets you compose multiple drivers (audio + spatial proximity + timer) without conflicts.

---

### Transform Modifier — apply transform to instances with falloff blending

**Example:** `convert.toe`

**Concept:** Per-instance transform with built-in falloff blending. Tx/Ty/Tz/Rx/Ry/Rz/Sx/Sy/Sz applied to each instance, scaled by the per-instance `popxFalloff` attribute value. Falloff=0 → no transform; falloff=1 → full transform; smooth gradient between.

This is the **default response shape** for any POPX visual: Texture Falloff (or other source) writes per-instance falloff → Transform Modifier scales its action by that falloff = visible response field.

**Pipeline position:** typically at the end of the modifier stack, just before render. Can be chained (multiple Transform Modifiers stacked, each with its own falloff source attribute).

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Transform | `Tx/Ty/Tz/Rx/Ry/Rz/Sx/Sy/Sz` + `Scale` | Standard transform parameters. Apply at full strength when falloff=1. |
| Transform | `Px/Py/Pz` | Pivot point |
| Transform | `Localspace` | If True: transform applied in each instance's local frame (rotation about its own center). If False: world space. |
| Transform | `Rord` | Rotation order |
| Transform | `Rotmode`, `Scalemode`, `Pivmode` | `'add'` (offset existing transform) or `'mult'` (replace) |
| Transform | `Dofalloff` | Required — enables falloff blending |
| Transform | `Falloffattr` | Which attribute drives the blend (default `'popxFalloff'`, but can target named attributes for layered falloff) |

**WOBAR application:**
- **Audio-driven response field** — Texture Falloff samples audio TOP → Transform Modifier scales/rotates instances proportionally → "the field reacts to sound."
- **Multi-stage layered response** — chain two Transform Modifiers: first reads `popxFalloff_audio`, second reads `popxFalloff_proximity`. Each composes independently. The final motion is the sum of both fields.
- **Scattered-then-reformed reveals** — start with `Sx/Sy/Sz=0.02` (pieces tiny / invisible), animate falloff from 0→1 across pieces over time → pieces grow into place.

---

### Randomize — per-instance jitter (position, color, rotation)

**Example:** `coil torus.toe`

**Concept:** Per-instance random offset modifier. Adds jitter to position / color / rotation channels of an instance stream. The randomization is deterministic from a seed — same seed → same jitter pattern.

**Pipeline position:** typically between Instancer and any animation modifier (MoveAlongCurve etc.) so the jitter "rides" with the bodies as they animate.

**Key parameters by page:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Position | `Posrand` | Enable positional jitter |
| Rotation | `Rotrand` | Enable random rotation per instance — useful with `Reorient` downstream for "visually random + functionally predictable" pattern |
| Color | `Colortop` | TOP used as color LUT for randomized color assignment |

(Likely also Scale page, full sub-controls per channel.)

**WOBAR application:**
- Add organic variation to any structured POPX layout (instancer grids feel less rigid)
- Use the `Color` page with a brand-palette ramp TOP for per-instance color variation in Act 1 motes / Act 4 release fields without writing the per-body color logic by hand
- Tie `Posrand` strength to audio energy via expression for "rougher motion on drops"

---

*Add new module sections below in alphabetical order as examples are reviewed.*

---

## Modules added from official docs reconciliation (v1.1)

The following modules are documented in the official 1.3.0 docs but were missing from the v1.0 guide. Added here without WOBAR application notes — those should be filled in as we use each module in production builds.

### Spread Falloff — non-simulation wave-spread falloff

**Concept:** Propagates outward from seed points through neighbor connections, creating organic wave-like patterns. Critically: **this is direct (no simulation)** — unlike Infection Falloff (which IS a simulation requiring Init→Start→Play). Use Spread Falloff when you want the infection-shaped look without the simulation overhead.

**Key parameters:**
- `Spread By` — radius or connectivity methods
- `Search Radius` — max distance for neighbor detection
- `Falloff Width` — diminishment rate
- `Spread Amount` — randomization for organic variation
- Seed config: Position & Radius (numeric) OR Seed Attribute (use existing attr)
- Threshold for seed activation
- Standard Combine + Remap + Noise pages

**When to pick over Infection Falloff:** if you want the look but DON'T want to wire Init/Start/Play activation. Direct, deterministic.

---

### Object Falloff — falloff from arbitrary 3D mesh proximity

**Concept:** Generates falloff based on distance to ARBITRARY 3D mesh. Distinguished from Shape Falloff (which uses geometric primitives — sphere/box/cylinder/etc.). Object Falloff lets you art-direct falloff regions with modeled meshes.

**Key parameters:**
- `Object Geometry` — POP reference to the falloff object
- `Area of Influence` — calculation method:
  - **Inside/Outside detection** (binary or smooth)
  - **Surface distance** (continuous distance from mesh surface)
  - **Surface intersection proximity** (close to mesh surface but not inside/outside)
- Standard transform controls (translate, rotate, scale, pivot)
- Combine Operation, Output Falloff Attribute, optional noise + remap

**Use case:** "Falloff is hot near this hand-modeled mesh." Modeled influence zones for art direction.

---

### Curve Falloff — falloff from distance to a curve

**Concept:** Distance-from-curve falloff. Different from MoveAlongCurve (modifier that animates instances along curves) — Curve Falloff just samples distance.

**Three modes:**
- **Distance to curve** — pure spatial proximity
- **Distance × curve position** — distance modulated by where on the curve the closest point sits (start vs end)
- **Normalized curve position alone** — ignore distance, use only the projection onto the curve's parametric range

**Key parameters:**
- `Curve geometry` reference + viewport visualization controls
- Min/max distance thresholds
- Curve resampling for performance
- Standard transform controls
- Standard Combine, Output, optional noise + remap

---

### Apply Attributes — the POPX transform engine

**Concept:** Core transformation engine of POPX. Takes packed primitives + template point attributes and applies them to drive transforms (position, rotation, scale, pivot). Uses **slerp** for rotation interpolation (smooth quaternion blending), linear for translations and scales. Supports both absolute and relative transformations.

**Key parameters:**
- `Do Falloff` + `Falloff Attribute` (default `popxFalloff`) — blend transformations using falloff
- `Do Translate` / `Do Rotate` / `Do Scale` / `Do Pivot` — independent enables for each transform type
- `Local Space` — apply transformations relative to instance's current transform
- `Rotate Mode` — Add or Set
- `Rotate Order` — six axis orderings (XYZ, XZY, YXZ, YZX, ZXY, ZYX)
- `Scale Mode` — Multiply or Replace
- `Copy Attributes` — transfer point attributes from template to instances
- `Create popxId Attribute` — auto-generates unique identifiers when missing
- `Output Orient/Scale Attributes` — preserves data for downstream operators

**When to use:** rarely directly — most modifiers wrap this. But useful when authoring custom POPX-style behavior or chaining multiple per-instance transforms with falloff blending.

---

### Extract Attributes — bridge POPX → native TD

**Concept:** The reverse of `Convert`. Converts POPX packed transforms back into standard TD point attributes (`N`, `Up`, `Orient`, `Scale`, `Pivot`, `Euler`) for use with native TouchDesigner instancing (Copy to Points, Geometry COMP).

**Key parameters:**
- `Extract Full Transform` — exports complete position, rotation, scale data
- `Extract Pivot` — writes pivot info as attribute
- `Extract POPX Orient` — converts `popxOrient` to standard `Orient` attribute
- `Group` — target specific group if multiple
- `Bypass` — passes input unchanged

**Use case:** when downstream of POPX you need to feed native TD operators that don't speak POPX-packed format. The TD-side bridge complement to `popxto`.

---

### Geometry (POPX tool) — per-instance materials in packed POPX render

**Concept:** Functions like a TD Geometry COMP, but with per-instance material assignment. **Auto-detects instance count from input geometry** and lets each instance use the material slot matching its index.

**Key parameters:**
- Material slots (one per instance, count auto-detected)
- Standard render flags (Render Primitives, Convert to Point Primitives)
- Common params (Free Extra GPU Memory, SRT/RST, Bypass)

**Use case:** crowds with varied materials (different races/colors/uniforms), architectural elements with different surface treatments, brand-mark instances where each letter has a different material — without splitting into multiple Geometry COMPs.

---

### Merge (POPX tool) — combine multiple POPX streams

**Concept:** Combines multiple POPX geometry streams into one unified output. Preserves attributes, groups, and instance data from each source. Dynamically add/remove inputs.

**Use case:** parallel processing chains that need to come back together before render.

---

### Delete (POPX tool) — filter / cull points by 5 methods

**Concept:** Removes (or retains via inversion) packed point instances using five filtering methods, combinable with logical operators.

**Five filtering methods:**
1. **Attribute** — comparison functions on point attribute values
2. **Thin** — by index range, step intervals, or randomly
3. **Pattern** — index-matching patterns
4. **Group** — membership in point groups
5. **Bounding** — bounding volume range

**Combinable** with **AND, OR, XOR, NAND, NOR** logical operators across multiple parameter blocks. Each method supports inversion.

**Common params:** Bypass, GPU memory management, primitive rendering options, transform order.

**Use case:** trim instances to a region, remove every Nth instance for sparse renders, conditionally cull by attribute (e.g. "only show instances where energy > threshold").

---

### Preview Falloff — standalone falloff debugger

**Concept:** Standalone debugging tool that visualizes falloff via color ramps. Distinct from the inline `Previewfalloff` toggle on each falloff module — this is a dedicated viewport visualization operator you place after any falloff source to inspect the field.

**Key parameters:**
- `Falloff Attribute` — which attribute to visualize
- `Preview Falloff` — enable/disable visualization
- `Falloff Ramp` — preset (Heatmap / Blackbody / Infrared) or custom gradient
- `Custom Ramp Editor` for defining custom gradients
- Common params: Bypass, Free GPU Memory, Render Primitives

**Use case:** debugging multi-stage falloff chains — drop in a Preview Falloff after each stage to see which one is producing wrong values.

---

## Native POPs that pair with POPX

Some non-POPX TD 2025 native POPs are conventionally used alongside POPX modules and worth listing here for completeness.

### `particlePOP` — proper particle emitter / integrator

**Example:** `flow (interactive).toe`

**Concept:** Native POP for typical particle simulations. Continuous emission from input geometry, per-particle lifetime, integration through a velocity field. Decouples particle emission/lifetime from POPX Flow's internal particle handling — when used with Flow in `Solvermode='simple'`, particlePOP takes responsibility for birth/integration while Flow only computes the velocity field.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Particles | `targetpop` | Downstream target POP (typically a nullPOP — the integration sink) |
| Particles | `maxparticles` | Hard cap on simultaneous particles |
| Particles | `birthrate` | Particles spawned per second |
| Particles | `life` | Average particle lifetime in seconds |
| Particles | `lifevariance` | 0–1 random variation in lifetime |
| Map | `map0op` | Velocity field TOP that drives integration (typically Flow's velocity output) |

**WOBAR application:** when you want full control over particle birth/death/count separate from a Flow simulation. Replace the Flow built-in particle system with `particlePOP → flow1.in2` for proper emitter shapes, audio-driven birthrate, etc.

### `trailPOP` — line trails from particle position history

**Example:** `flow (interactive).toe`

**Concept:** Records position history per particle over a temporal window and emits line geometry from it. Matches particles across frames using a stable per-particle attribute (typically `PartId`) so trails track the right particle even as IDs reorder.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Trail | `length` | Temporal trail length in seconds |
| Trail | `attrmatch`, `attrname` | Match particles across frames by named attribute (`'PartId'` is standard) |
| Trail | `maxls` | Max line strips (one per particle) |

**WOBAR application:** any time you want to show a particle's path. Combine with particlePOP or any other particle system → visible flow lines through any velocity field. Long trails + few long-lived particles = elegant minimal visual (Act 4 release).

### `tracePOP` — silhouette → triangle mesh polygonization

**Example:** `convert.toe`

**Concept:** Converts a binary 2D silhouette (typically from `thresholdTOP`) into a triangle-mesh POP. The first step in the "image-as-POP-geometry" pipeline.

### `lookuptexturePOP` — sample TOP at point UVs to assign per-point colors

**Example:** `convert.toe`

**Concept:** Takes a POP and a TOP, samples the TOP at each point's UV, writes per-point Color attribute. Pairs with tracePOP to assign original-image colors back to traced silhouette points.

### `fieldPOP` — generate a soft volumetric field as a POP

**Example:** `path tracer materials.toe`

**Concept:** Native POP that produces a soft volumetric field shaped like a sphere/ellipsoid (with separate per-axis radii). Similar to POPX Shape Falloff but native, simpler, and outputs as POP geometry rather than as an attribute writer.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `specpop` | Optional reference POP for shape |
| `radx`, `rady`, `radz` | Per-axis radii of the field |
| `transitionrange` | Soft falloff zone width |
| `combineop` | `'add'`/`'multiply'`/etc. — how to combine with existing attribute on input |

**WOBAR application:** lightweight volumetric mask for any "modify only inside this region" effect. Cheaper than Shape Falloff when you don't need the full falloff-attribute pipeline.

---

### `normalmapTOP` — convert heightfield TOP to tangent-space normal map

**Example:** `path tracer materials.toe`

**Concept:** Standard texture-preparation node. Takes a heightfield/grayscale TOP (e.g. from a noise TOP, image, procedural pattern) and outputs a tangent-space normal map TOP suitable for feeding into `POPX Material.Maps.Normalmap`.

**WOBAR application:** procedural surface detail for path-traced materials. Generate a noiseTOP → wire to normalmapTOP → wire to `POPX Material.Normalmap` for "metal with subtle surface texture" without authoring a normal map asset.

---

### `feedbackCHOP` — accumulate channel state across frames

**Example:** `soft body (interactive cloth).toe`

**Concept:** Native CHOP that accumulates channel state across frames. Used commonly in input pipelines to hold latched state (e.g. mouse-released-but-still-grabbed) or smooth/integrate signals over time. The CHOP-side analog of `feedbackTOP`.

**WOBAR application:** any input chain that needs state-holding behavior between frames — cursor latching, audio-state accumulation, gesture-history tracking.

---

### `linesmoothPOP` — line strip smoothing

**Example:** `move along curve 6.toe`

**Concept:** Smooths line strips via filtering. Reduces sharp angles; preserves overall shape. Standard cleanup after noise-deforming line strips.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `endpointsfixed` | Pin start/end points of each line strip during smoothing (otherwise smoothing pulls them inward) |

---

### `facetPOP` — topology cleanup (deduplicate vertices, normals, edges)

**Example:** `move along curve 6.toe`

**Concept:** SOP-style topology operations in POP form. Most commonly used for `operation='unique'` to merge coincident vertices and remove duplicates after geometry construction. Critical for clean output after deformation chains.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `operation` | `'unique'` (deduplicate vertices), and likely smooth normals / edge ops |
| `bbox` | Bounding-box reference (for some operations) |

---

### `lineresamplePOP` — evenly redistribute points along line strips

**Examples:** `move along curve 6.toe`, `curve advection.toe`, MoveAlongCurve internal solver

**Concept:** Re-spaces points along line strips to a uniform density. Critical after any deformation that distributes points unevenly (noise distortion clusters points in some regions, sparses them elsewhere).

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `resamplemethod` | `'linestrip'` to preserve linestrip topology (vs alternatives) |
| `resampledivs` | How many divisions to resample each strip into (uniform spacing) |

---

### `patternPOP` — procedural pattern / curve generator

**Example:** `move along curve 1.toe`

**Concept:** Native TD POP that generates patterns/curves from procedural parameters. Used most often as a cheap source of parametric curves (sine, ramp, custom function) that feed POPX modules expecting a curve POP (`MoveAlongCurve.Curve`, `Instancer(curve)`, `DLG` seed, etc).

**Key parameters (partial — explore module for full):**

| Parameter | Purpose |
|-----------|---------|
| `tohigh1` | Output range maximum (per channel) |
| `attrnumcomps` | Output components per point (`'3'` = vec3 = position xyz) |
| (likely also `from*`, frequency, phase, pattern type) | Standard pattern controls |

**WOBAR application:** quick procedural curves for MoveAlongCurve flows. Sine wave for "wave" motion, ramp for linear flow, custom for any analytical curve. Cheaper and easier than authoring with copyPOP+circle+line for parametric curves.

---

### `sprinklePOP` — random point scattering on geometry surface

**Example:** `index from attribute.toe`

**Concept:** Native TD POP for scattering N random points across the surface of input geometry (planes, meshes, etc.). Standard upstream point generator before any POPX modifier chain.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `numpoints` | Count to scatter |
| `method` | `'perprim'` (one per primitive) or alt |
| `attemptsperpoint` | Rejection-sampling retries for poisson-disk-like distribution |
| `seed` | RNG seed |
| `pointattrscope`, `primattrscope`, `vertattribscope` | Which input attributes to inherit/transfer |
| `raydirmode`, `raydirx/y/z` | For non-flat surfaces, the projection direction for sampling |
| `hwraytracing` | Use GPU raytracing for the scatter on complex meshes |

**WOBAR application:** generate randomized point seeds for any POPX scatter pipeline. More flexible than `pointgeneratorPOP` (which is shape-constrained) when you need to scatter onto an arbitrary mesh surface.

---

### `mathmixPOP` — pointwise math operations on attributes (cross product, dot, mix, etc.)

**Example:** `measure.toe`

**Concept:** Native TD POP that performs per-point math operations on existing attributes. The "math CHOP for POPs" — reads two (or more) input attributes, applies an operation (cross, dot, add, multiply, mix/lerp, etc.), writes the result to a new attribute.

**Key parameters:**

| Page | Parameter | Purpose |
|------|-----------|---------|
| Inputs | `attrclass` | `'point'`, `'primitive'`, etc. — which attribute level to operate on |
| Inputs | `lengthmismatchnotif`, `lengthmismatchaction` | How to handle length mismatches (warning/repeat) |
| Inputs | `input`, `input0pop` | Multi-input mixing |
| Combine | `comb0oper` | Operation: `'cross'`, `'dot'`, `'add'`, `'sub'`, `'mul'`, `'div'`, `'mix'`, etc. |
| Combine | `comb0scopea/b/c` | Input attribute names |
| Combine | `comb0result` | Output attribute name |
| Uniforms | `vec0name`, `vec0type`, `vec0value0/1/2/3` | Constants you can use as additional inputs |
| Uniforms | `color0name`, `color0rgbr/g/b`, `color0alpha` | Color constants |
| Output | `delattrs`, `delnewattrs` | Optional cleanup |

**WOBAR application:** chain attribute computations to derive new fields. Cross product of gradient and normal → tangent flow direction. Dot product of velocity and normal → impact strength. Mix between two attribute fields → blend two effects spatially.

---

### `attributeconvertPOP` — bridge primitive ↔ point ↔ vertex attributes

**Example:** `instancing indexes.toe`

**Concept:** Native TD POP that converts attributes between geometry levels (primitive ↔ point ↔ vertex). Critical when you author attributes at one level but downstream POPs need them at another. The `convertop='primtopoint'` mode distributes a per-primitive attribute to all points belonging to that primitive — the most common direction.

**Key parameters:**

| Parameter | Purpose |
|-----------|---------|
| `convertop` | `'primtopoint'`, `'pointtoprim'`, `'vertextopoint'`, etc. |
| `inputattrs` | Comma-separated list of attribute names to convert (e.g. `'Color'`, `'Color, N'`) |

**WOBAR application:** the bridge between authored-per-face attributes and per-point pipelines. Random per-face color → per-point color → Attribute To Index → multi-geometry instancing. Without attributeconvertPOP, the per-primitive randomization can't reach downstream point-based modules.

---

### `pointgeneratorPOP` — generate N points in a configurable shape

**Examples:** `dlg.toe`, `flow (interactive).toe`

**Concept:** Generates N points in a circle / sphere / box / line / random distribution. Used for seed positions (DLG seed strips), emitter origins, distribution templates.

---

## Interactive Control Patterns

Documented as we encounter them. POPX visuals can be driven by external input via standard CHOP wiring — useful for performance and live VJ.

### Cursor-position → emitter (canonical interactive pattern)

**Example:** `flow (interactive).toe`

```
panelCHOP (insideu/insidev) → mathCHOP (remap to world) → nullCHOP (cursor) → drives transformPOP via expression
```

`panelCHOP.par.panel = some_panel_comp` returns 0–1 normalized cursor position. Math CHOPs remap to world coords. The output null CHOP is referenced by expressions on emitter positions, Flow injection coords, DLA seed positions, etc.

**Generalizes to:**
- MIDI knob/fader → continuous parameter (use midiinmapCHOP)
- OSC from phone → networked input (oscinCHOP)
- Audio CHOP → emitter follows audio energy peak position
- Webcam centroid → audience-driven visual (computer vision tracker → CHOP)

---

## WOBAR Integration Patterns (cumulative)

- **Falloff via `popxFalloff` attribute** — most POPX modifiers respect a per-instance falloff attribute. Pattern: write a `popxFalloff` channel via attributePOP upstream of the modifier, drive it from audio energy / distance from a focal point / timer, and the modifier blends between unmodified and fully modified per instance. The cleanest way to layer POPX effects with audio reactivity.
- **TOP-as-LUT for per-instance/per-position behavior** — POPX modifiers like MoveAlongCurve expose `*top` parameters (`Scaletop`, `Acctop`, `Twisttop`, etc.) that take a TOP texture as a 1D lookup along the curve length. Drive these TOPs with audio-reactive ramps for sophisticated behavior modulation along a path.
- **Distribution + Modifier chain** — the canonical POPX pipeline shape is: `[POP source] → Instancer(<mode>) → [optional Randomize / Aim / other modifiers] → [optional MoveAlongCurve / MoveAlongMesh] → [render]`. Instancer is always first; modifiers stack downstream.
- **Curve POP from native primitives** — POPX's `Instancer(curve)` takes any curve POP as `Templateobject`. Build the curve from native ops (e.g. small `circle1` copied around `circle2` via `copyPOP` = a torus coil) — POPX handles only the distribution + animation, not the curve generation. Native curve generation stays cheap and dependency-free.
- **Image-as-instances pipeline** — `[image] → thresholdTOP → tracePOP → lookuptexturePOP → Convert → TextureFalloff → Spring → TransformModifier → render`. This is the canonical "many separable shapes from a single image" recipe. tracePOP polygonizes the silhouettes; lookuptexturePOP grabs colors back from the original image; Convert detects the pieces; downstream POPX modifiers act per-piece.
- **Layered falloff fields** — write multiple falloff attributes (`popxFalloff_audio`, `popxFalloff_proximity`, `popxFalloff_timer`) via separate Texture Falloff modules with different `Outputfalloffattr`. Downstream modifiers pick which attribute they respect via `Falloffattr`. Allows composing multiple drivers (audio + spatial + timed reveal) without conflict.
- **Spring as audio-jitter smoother** — when audio-driven attributes (sub_bass, transient) drive a Texture Falloff, Spring on `Other='popxFalloff'` adds physical inertia that smooths transient pops into organic pulses. Critical for Act 1 "felt, not aggressive."
- **Curve / particle / instance advection through Flow** — set `Flow.Solvermode='advect'`, wire `Flow.Particlesupdatepop` to a POP that reads Flow's own output (creating a GPU-side feedback loop). Geometry is continuously dragged through the simulated velocity field. Insert `lineresamplePOP` in the loop to keep curves smooth under shear. Pattern works for curves, particle clouds, instancer outputs, mesh point sets — anything addressable as a POP.
- **Optical flow → fluid forces** — Flow's `Opticalflowtop` parameter takes a video TOP and analyzes its motion to inject as fluid forces. Performer silhouette / camera input becomes a real-time deformer of the entire visual field. Powerful for live performance.
- **POP injection as moving emitter** — wire a POP (line, single point, animated curve) to `Flow.Injectionpop` with an `Injectstrength`/`Injecttemp`/`Injectcolor*` setup. The POP becomes a moving smoke/ink emitter — animate the POP's positions to "draw with smoke" through the fluid.
- **DLA + Flow combination** — set `DLA.Walkersupdatepop` to read Flow's advected positions. Walkers ride the fluid velocity field instead of pure Brownian motion. Aggregation patterns then bias toward fluid flow direction; audio injecting into Flow biases coral growth direction. The two solvers compose: Flow gives the velocity field, DLA gives the structure.
- **Seed POP determines DLA silhouette** — DLA's overall shape is constrained by its seed POP and bounds. Seed = a circle → radial coral. Seed = a line → perpendicular sheet. Seed = a sparse point cloud → multiple competing colonies. Seed = a traced silhouette (via tracePOP) → growth out of any image. Lets you "draw with DLA" by authoring the seed.
- **Generative solver feedback loop pattern** — POPX's stateful solvers (Flow, DLA, DLG, MoveAlongCurve-solver) all expose a `*Updatepop` parameter for self-feedback: `solver → [optional modifiers] → null → solver.par.*Updatepop`. The solver reads positions from the named POP each frame, applies its update, writes new positions back. Modifiers inserted in the chain become per-frame extension points. This is the canonical pattern for stateful POPX behavior. Examples: `Flow.Particlesupdatepop`, `DLA.Walkersupdatepop`, `DLG.Lineupdatepop`, `MoveAlongCurve.Particlesupdatepop`.
- **Multiple seed strips with per-instance color** — `pointgen1 → random1 (→Color.rgb) → copy(geometry, points)` is the canonical pattern for spawning N independent generative solver seeds with distinct colors. Output color attribute is preserved through the solver via `Transferattrs='*'`-like mechanisms, so each strip retains its identity through growth.
- **DLG + DLA combo** — use DLA-aggregated points as the DLG seed (or vice versa). Two layered fractal aesthetics composed.
- **Modifier-in-the-loop trick** — POPX solvers' `*Updatepop` is downstream-facing, so you can insert any POP modifier (noise, transform, attribute manipulation, even Flow advection) between the solver's output and its update target. The modifier becomes part of every frame's update. This is the primary extension point for customizing solver behavior beyond the built-in parameters.
- **Disintegration recipe** — the canonical chain for "Thanos snap" / dissolution effects: `mesh → Explode → Infection Falloff → Noise Modifier (Curlnoise=True, Mode=advect) → Transform Modifier (Scale=0.2) → render`. All three downstream modules respect the same `popxFalloff` written by Infection Falloff, so they share one wavefront. Single source of truth, layered effects.
- **Growth/destruction inverse pattern** — DLA and DLG grow structures from seeds; Explode + Infection Falloff destroys structures from seeds. Together they're the full life cycle. Compose: DLA grows a coral until Maxpoints; once full, Explode-Infection chain begins disintegrating it; reset and loop. Generative birth + decay cycle.
- **Single-falloff, multiple-modifiers pattern** — write `popxFalloff` once (via Texture Falloff, Infection Falloff, or any source), then have multiple downstream modifiers (Transform, Noise, Color, Spring) all respect the same attribute via `Falloffattr='popxFalloff'`. Effects stay coordinated automatically; one wavefront drives everything. To layer independent effects, use `Outputfalloffattr` to write to differently-named attributes (e.g. `popxFalloff_audio`, `popxFalloff_proximity`) and downstream modifiers pick which attribute they respect.
- **Curlnoise=True is the right default for organic motion** — divergence-free noise gives all-rotation, no-inflow/outflow motion. Standard noise displaces points toward sinks/sources; curl noise just swirls. For any "wind", "smoke", "fluid drift", "dissolution", "ambient float" — start with `Curlnoise=True`. Only fall back to standard noise if you specifically need an inflow/outflow effect.
- **Decoupled Flow architecture** — set `Flow.Solvermode='simple'` and pair with native `particlePOP` for full emitter control. Flow generates the velocity field; particlePOP handles birth/death/integration. Wire particlePOP's `map0op` to Flow's velocity TOP output. This trades Flow's built-in particle simplicity for proper emitter controls (birthrate, life, lifevariance, custom emitter shapes via input POP).
- **Voxelize as Flow injection bridge** — POP geometry can't directly inject as Flow substance. Voxelize converts POP → 3D voxel grid → Flow.in1. Match Voxelize's bounds to Flow's `Simboundsx/y/z` for clean injection.
- **Trails from any velocity field** — pair `particlePOP + trailPOP` to visualize ANY velocity field (Flow, custom GLSL TOP, hand-painted force field). Long trails + few particles = minimal elegant visual; short trails + many particles = volumetric flow visualization.
- **Multi-Geometry Index-Based Instancing** — assignment of distinct geometries per point. Pipeline: `[any per-point attribute source: Shape Falloff / Texture Falloff / Infection Falloff / Random / Color / Position component / Normal] → Attribute To Index (Inputattr → popxIndex with N buckets) → Instancer(Indexingmode='pointattr', Indexattr='popxIndex', Instances0pop, Instances1pop, ..., InstancesNpop)`. Each template point picks its geometry from the indexed slot. Multiple index sources work: spatial (Shape Falloff), image-based (Texture Falloff), temporal (Infection Falloff), random (random per-prim/per-point Color), positional (`Inputattr='P(0)'`), normal direction, custom attribute. Lets you swap between distinct geometric vocabularies based on any criterion.
- **Per-primitive randomization for indexed instancing** — pattern: `mesh → randomPOP(outputattrscope='Color.rgb', attrclass='primitive') → attributeconvertPOP(convertop='primtopoint', inputattrs='Color') → attribute_to_index1(Inputattr='Color') → instancer1(mesh distribution + multi-geometry)`. Each face of the source mesh gets a random color, that color discretizes into an index, the index picks a geometry. Generates organic per-face variety from any mesh source.
- **Mesh-distribution instancing** — `Instancer.Distributiontype='mesh'` distributes instances directly onto a mesh template's surface (vs `'pointcloud'` which uses pre-computed point positions, vs `'curve'` which uses curve length). Use for "carpet a mesh with instances" effects without manually scattering points first.
- **Per-magnet attribute pattern** — when wiring a POP to a multi-element module (`Magnetize.Magnetspop`, `Infection Falloff.Seedpop`, etc.), the upstream `attributePOP` lets you set per-element attributes that override the module's defaults. Patterns:
  - `pointgenerator → attributePOP (sets radius, mode, strength per point) → noisePOP (animates positions) → module.in1`
  - Each point in the POP becomes one independent element of the module's behavior. Heterogeneous behavior in a single module call.
- **`Output*attr` chain pattern** — POPX modules consistently write per-instance attributes that downstream modules read:
  - `Texture/Infection/Shape Falloff` write `popxFalloff` (or custom `Outputfalloffattr`)
  - `Attribute To Index` writes `popxIndex` (or custom `Outputattr`)
  - `Magnetize` writes `Weight` and/or `Force` (optional via `Outputweightattr`/`Outputforceattr`)
  - `Noise Modifier` writes `Noise` (optional via `Outputnoiseattr`)
  - Downstream modules read via their `Falloffattr` / `Inputattr` / `Indexattr` parameter naming the source attribute
  - Multiple independent fields can co-exist by using different `Outputfalloffattr` names (`popxFalloff_audio`, `popxFalloff_proximity`, etc.). Modules pick which field they respect. Three independent control fields drive three independent effects without naming conflicts.
  - **Implication:** complex visuals scale via the attribute namespace, not operator topology. Add a new field by writing a new attribute upstream; existing modules are agnostic.
- **Mesh-as-flow-field via differential geometry** — a complete production technique for "particles flow along topology of any mesh":
  ```
  mesh → Measure(curvedness) → Measure(gradient of Curvedness) → mathmixPOP(cross Gradient × N → Dir) → Advect Modifier (Advectsource='refgeo', Advectattr='Dir') → trailPOP → render
  ```
  - Particles flow along **iso-curvedness contours** on the mesh surface — they don't escape, they trace the geometric feature lines (creases, folds, edges).
  - The same pattern can be derived from any source scalar field, not just curvedness:
    - Distance-from-feature → gradient → cross with N → flow toward features
    - Painted attribute → gradient → cross with N → audio-driven flow on a surface
    - Texture-sampled value → gradient → cross with N → image-driven flow on a surface
  - Brand-on-aesthetic for WOBAR — visualizes hidden topology, "everything is already there" reveal.
- **Two-pass Measure chain** — first pass computes a scalar field (curvedness / area / distance / custom), second pass computes the gradient of that field. This is the canonical way to derive a vector field from any per-point scalar in POPX. Then cross with the surface normal to get a tangent-plane flow direction.
- **`Advectsource='refgeo'`** — the powerful flag on Advect Modifier. Particles look up their direction from a reference geometry's per-point attribute, NOT from their own attribute. Means you can move particles freely while they continuously sample a static-or-animated mesh-bound field. The bridge between "field on the mesh" and "particles in space."
- **Sprinkle-as-seed-source pattern** — `mesh → sprinklePOP (random scatter on surface) → randomPOP (per-point colors / per-point attrs) → solver.Seedpop or in2`. Three examples confirmed using this pattern (`dla.toe`, `dlg.toe`, `mesh fill.toe`). Generalizes: any solver accepting seeds via POP can be fed by sprinklePOP+randomPOP+attributePOP for "N random colored seeds anywhere on a surface, with per-seed customization." The standard upstream setup for any volumetric/aggregating POPX solver.
- **Trail-driven age-based instancing (canonical comet-tail)** — complete pattern for "moving thing leaves a trail of decreasing/transforming instances":
  ```
  animated_points → trailPOP (ageattr='seconds', surftype='points')
                      ↓
              popxto (POPX format conversion)
                      ↓
          Attribute Falloff (Inputattr='Age' → popxFalloff)
                      ↓
      Instancer (Distributiontype='pointcloud', Copytemplateattributes='*', Attrstocopy='*')
                      ↓
      Transform Modifier (Scale=0, Rz=720, falloff-driven)
                      ↓
      Color Modifier (Ramptop, falloff-driven color)
                      ↓
                    render
  ```
  - The `Copytemplateattributes='*'` on the Instancer is critical — propagates the age-based `popxFalloff` to instances. Without it, downstream falloff is lost.
  - Generalizes to any motion source (audio-driven points, performer-tracked points, swarm motion). Produces the iconic "comet tail of geometry" effect with full per-instance control over fade behavior.
  - Most "music-video-ready" pattern in POPX. Single network produces a delivery-ready audio-reactive motif.
- **Native-to-POPX bridging via `popxto`** — any time you want POPX modifiers downstream of native POP outputs (`trailPOP`, `particlePOP`, `sprinklePOP`, etc.), insert `popxto` to convert formats. Without it, POPX modifiers downstream may not see the expected attribute structure.
- **Extracting internal POPX sub-data via Select POP** — POPX modules are baseCOMPs containing numbered sub-networks. Some internal POPs hold useful data the module's outer outputs don't expose (intermediate computations, debug visualizations, internal state). Pattern: `selectPOP.par.pop = '/path/to/popx_module/internal_subop'` reaches inside and grabs the named internal POP as downstream geometry. Confirmed on `MoveAlongCurve.offset/offsets` (the offset-line visualization). Generalizes to other modules — Flow's velocity field, DLA's connectivity graph, etc. **Only READ; do not modify internals** (same principle as `/ui` `/sys` `/local`). Useful for: debug visualization, custom render passes, novel composite effects.
- **Group-motion along a curve** — for "object travels coherently along a path" (rather than "field flows along curve"), use MoveAlongCurve with `Snaptocentroid=True, Doorientsnap=True`. Entire instance set retains shape; centroid attaches to curve; whole group orients to direction. Add `Twistamount` for spin during travel.
- **Goal-attribute-driven coloring along curve travel** — set `MoveAlongCurve.Outputgoalattrs=True` → solver writes `GoalU` (0–1 curve progress) per instance → downstream `Color Modifier.Falloffattr='GoalU'` colors instances by their curve position. Combined with trailPOP, the trail captures both the moving shape AND its color-progression history. Music-video-ready pattern: "shape moves with color gradient, trails fade behind in colored arc."
- **Hierarchical attribute propagation through Instancer→Unpack→Solver→Modifier chain** — a single `popxFalloff` field generated at the top can propagate through complex topological transformations (instancing → unpacking → curve-following → modifying) and be reused at multiple stages with different remappings for different visual effects. The `move along curve 4.toe` cake-builder demonstrates: Shape Falloff writes falloff (Stage 1) → Transform Modifier scales rings (Stage 2) → Unpack carries attribute (`Transferattrs='popxFalloff'`) (Stage 3) → MoveAlongCurve picks it up (Stage 4) → Remap Falloff inverts it (Stage 5) → Transform Modifier scales boxes (Stage 6). One source of truth, two coordinated visual effects (ring sizes AND box sizes both taper with the same falloff). This is the deepest "single source of truth" use of POPX falloff — geometric structure and decoration are both controlled by one upstream field.

- **Living Voronoi shatter (`voronoi.toe`)** — animated 2D/3D Voronoi tessellation where cells continuously rearrange as seeds drift:
  ```
  pointgeneratorPOP (N seed points)
      → Relax (Solvermode='advect', Relaxmethod='nebr', Pointsupdatepop=null1,
              Maxrelaxradius=0.247, Relaxstrength=0.319,
              Collisiontype='box', Sizez=0.0 = flat 2D box,
              Solid=False = bounce-on-walls)
      → noisePOP (amp=0.0025, t4d=absTime.seconds*0.1 — tiny slow drift)
      → null1 (feedback target — Relax reads back from here)
                    │
                    ↓
                                ┌── feeds explode1.in1 (Voronoi seeds, Numberofclusters.expr=op('pointgen1').par.numpoints)
  Planar Patch (substrate mesh) ─┘
      → Explode (Partitionmethod='voronoi', Scattermethod='perprim', in0=substrate, in1=relaxed-seeds)
      → Transform Modifier (per-cell explode/scatter via popxFalloff)
      → render
  ```
  - **Why Relax is essential before Voronoi:** without it, random points clump → ugly cells of wildly varying size. Relax pushes seeds apart so cells are roughly equal-sized.
  - **Why the noise + feedback loop:** seeds diffuse smoothly over time → the Voronoi tessellation **animates instead of being static**. Living, breathing shatter pattern.
  - **`Collisiontype='box', Sizez=0.0`** — confines Relax to a 2D plane (z is flat). For 3D Voronoi, set Sizez=1.0.
  - **`Numberofclusters.expr=op('pointgen1').par.numpoints`** — auto-binds Voronoi cell count to seed count; change one parameter, both update.
  - **WOBAR variants:** brand-mark Voronoi shatter on the drop, audio-driven seed motion (kick injects radial impulse to relax's `Attractstrength`), per-cell color from sampled background TOP, sub-bass scales `Relaxstrength` so cells "breathe" with the bassline.

- **Per-letter typographic animation pipeline (`typography.toe`)** — canonical recipe for animating a wordmark letter-by-letter with audio-reactive deformation:
  ```
  textSOP (3D extruded text)
      → soptoPOP (SOP→POP bridge)
      → deletePOP / normalPOP / facetPOP / limitPOP (cleanup: remove degenerate faces, recompute normals, deduplicate verts)
      → transformPOP (initial pose)
      → Convert (Partitionmethod='connectivity', Numberofpieces=N detects letters as connected components)
      → Pivot (Mode='bbox', Alignmentside='ym', Localspace=True, Pivotonly=True
              — each letter pivots from its baseline center, not world origin)
      → Shape Falloff (animated falloff sweeps across the wordmark, e.g. lfo-driven Tx)
      → Spring Modifier (Other=True, Attr='popxFalloff', Springconst=0.7, Dampingcoef=0.95
              — each letter's falloff value lags with elastic ringing)
      → Transform Modifier (Sy=0.02 — squash to ~2% Y, Scale=0.8, Dofalloff=True, Localspace=True
              — letter is squashed where falloff is hot, with springy aftermath)
      → Unpack (Applytransform=True, Transferattrs='popxFalloff'
              — bake POPX-instanced letter transforms back into geometry for rendering)
      → render
  ```
  - **Why each module is essential:** Convert detects letters as separate pieces (no manual per-letter splitting); Pivot anchors rotation/scale to each letter's baseline (not world origin) — critical for "letters tilting back like dominoes" or "letters bouncing off the stage"; Spring on `popxFalloff` adds elastic per-letter timing (the wave passes letter-by-letter with bounce); Transform Modifier reads the springed falloff for actual squash/rotate/scale.
  - **WOBAR variants:**
    - **Drop reveal:** Tx of Shape Falloff sweeps left→right on the drop bar; letters pop up in sequence with bounce.
    - **Per-letter audio bands:** five letters, five band envelopes; write them into a 5-row CHOP, sample as a per-piece attribute, drive `Transform Modifier` from that attribute. Each letter scales to its assigned band.
    - **Domino fall:** rotation Rz on Transform Modifier instead of Sy scale; falloff sweep tips letters over sequentially.
    - **Brand explosion/reassembly:** invert the falloff polarity to scatter, re-invert to reassemble. Same network, two different reveal modes.
  - **Replaces:** hand-keyframed per-letter animation in After Effects, manual per-letter geometryCOMPs in TD, custom GLSL per-instance squash shaders.

- **Decoupled noise field → advection pattern** — separate noise field GENERATION from APPLICATION. Pipeline:
  ```
  instances
      → Noise Falloff (writes popxFalloff — spatial mask)
      → feedbackPOP (state accumulation)
      → Noise Modifier (
            Affectposition=False,            # don't move points directly
            Outputnoiseattr=True,             # write noise vector as 'Noise' attribute
            Curlnoise=True
        )
      → Advect (
            Advectsource='ptattr',            # read noise from point's own attribute
            Advectattr='Noise',
            Dofalloff=True,                  # popxFalloff masks intensity
            Falloffattr='popxFalloff',
            Feedbackpop=feedback1,
            Enablelife=True, Lifespan=1.0,    # particle regeneration
            Passthroughattrs='Color popxFalloff'
        )
      → trailPOP → render
  ```
  Why this matters: noise field is now DATA — inspectable, layerable (multiple Noise Modifiers writing to different `Noiseattr` names), routable to multiple consumers. The POPX equivalent of "write a velocity field shader, then apply it however you want." Different from the direct `explode curl.toe` pattern where Noise Modifier moves things directly.

- **Living-skin / creature-with-veins pattern** — canonical mesh-surface flow effect. Pipeline:
  ```
  mesh source
      → OrientMesh (Computemethod='nup', Curl Noise enabled with animated T4d, optional blur)
      → [provides forward/up/orient field with organic perturbation]
      → MoveAlongMesh (
            Attachmode='scatter',                                      # spawn random on surface
            Enablelifetime=True, Life=1.0, Lifevariance=0.5,           # finite particle life
            Scalebyage=True, Remapscalex=0, Remapscaley=1,             # grow with age
            Enablepointrelax=True,                                     # particles avoid each other
            Outputlifeattrs=True                                       # per-particle Age for downstream
        )
      → trailPOP (records paths)
      → render
  ```
  Result: self-sustaining "living-mesh" visual — particles continuously appear, grow, travel, die, respawn. Mesh appears alive with circulating veins. Audio hooks: `MoveAlongMesh.Speed`, `OrientMesh.Curl Noise.T4d` rate, `Curl Noise.Amp`, `Life` — any of these driven by audio = music-reactive living mesh.

- **Instancer-output as curves for next solver** — instanced circles/lines from one Instancer can become CURVES for a downstream MoveAlongCurve. Pattern: `Instancer (linear stack of circles) → Transform Modifier (scaled by Shape Falloff) → Unpack (Applytransform=True, Transferattrs='*') → MoveAlongCurve.in1`. The instanced output, once unpacked, IS the curve set. Lets you procedurally generate complex curve fields from POPX modules rather than hand-authoring them.

- **`Remap Falloff` vs `Attribute Falloff` distinction** — easy to confuse. Use `Attribute Falloff` to CONVERT any custom attribute (Age, Weight, custom user attr) INTO `popxFalloff`. Use `Remap Falloff` to TRANSFORM an existing `popxFalloff` (invert, fit, non-linear remap via ramp). The two stack: `[any source] → Attribute Falloff → popxFalloff → Remap Falloff → modified popxFalloff → downstream modifiers`.

- **Per-instance speed via falloff (non-uniform group flow)** — `MoveAlongCurve` with `Dofalloff=True` makes per-instance `popxFalloff` modulate each instance's speed along the curve. Faster instances (high falloff) lead, slower (low falloff) trail. Combined with `Snaptocentroid=True, Maintainoffset=1.0, Offsettop` (ramp from 1 to 0) you get the "swarm-with-leader-and-convergence" pattern: group splays apart by speed differences, then all converge at the curve end as offsets ramp to zero. WOBAR-aligned uses: audio-driven leading edge (falloff = audio energy → speed pulses with music), performer-leads-the-swarm, Act 5 convergence finale.
- **`Offsettop` as squeeze-onto-curve** — the `Offsettop` parameter is a TOP serving as a 1D LUT along the curve length, multiplying the `Maintainoffset` per curve-position. Set up a ramp going `1 → 0` along curve length: instances start with full perpendicular offset and squeeze ONTO the curve as they reach the end. Audio-reactive variants: animate the ramp's keys to audio energy → squeeze pulses with the music.

- **Deformed-grid-as-curve-web recipe** — production-ready 5-stage pipeline for "web of intersecting curves with organic distortion":
  ```
  gridPOP(surftype='linestrips')          # N×M parallel line strips
      → noisePOP                          # distort positions with 3D noise
      → lineresamplePOP(method='linestrip', resampledivs=N)  # re-space evenly along distorted lines
      → linesmoothPOP(endpointsfixed=True)  # smooth strips, pin endpoints
      → facetPOP(operation='unique')      # deduplicate coincident vertices
      → [curve consumer: MoveAlongCurve / Instancer(curve) / DLG seed]
  ```
  - The `lineresamplePOP` step is critical — without it, noise distortion bunches points unevenly and the curves break. Resampling forces uniform point distribution.
  - `facetPOP unique` is essential cleanup — gridPOP outputs share vertices at intersections; without facet, downstream solvers may treat them as separate disconnected lines.
  - Output: clean, deformed, smooth, multi-curve POP suitable for any downstream curve-consuming module.
  - WOBAR uses: spider web (Act 3), woven membrane (Act 1 portal threshold), mycelium connection map (Act 2), audio-distorted webs (replace `noisePOP` with audio-driven noise for live reactivity).

- **Group-motion + goal-attr + trail = canonical "traveling motif"** — full pipeline:
  ```
  instancer (3D pattern shape, no curve distribution) →
  MoveAlongCurve(Snaptocentroid=True, Doorientsnap=True, Maintainoffset=1.0,
                  Twistamount=360, Outputgoalattrs=True) →
  Color Modifier(Falloffattr='GoalU', Ramptop=brand_palette) →
  trailPOP(records colored history) →
  render
  ```
  Produces: a rigid colored shape traveling a curve, twisting, leaving a colored trail. Add audio-driven curve generation for full audio reactivity.
- **Attribute Falloff completes the falloff family** — POPX now provides FOUR falloff sources, each from a different domain:
  - **Texture Falloff** — from a TOP (image / audio TOP / animated)
  - **Shape Falloff** — from 3D shape distance (sphere/box/etc)
  - **Infection Falloff** — from temporal viral spread
  - **Attribute Falloff** — from any pre-existing per-instance attribute (Age, custom, position, etc.)
  All four write `popxFalloff` (or custom attribute name). **You can chain or layer them** by writing to differently-named attributes via `Outputfalloffattr` and having downstream modifiers read specific named attributes.

- **Cornell-Box pattern for PBR test scenes** — canonical 3-element scene for verifying POPX path-traced rendering:
  - **Room**: `boxPOP → deletePOP (remove front face) → glslPOP/per-prim color → POPX Material (Attrclass='primitive')` — multi-walled room with different colors per face via per-primitive material
  - **Subject mesh**: `fileinPOP → normalPOP (compute normals) → transformPOP → POPX Material` — imported geometry
  - **Glass sphere**: `spherePOP → transformPOP → noisePOP (surface texture) → POPX Material (Transmission=1.0, Thickness=2.0)` — refraction demo
  - All three merged → Path Tracer + POPX Light (area + env) → render
  - Reveals: (1) `POPX Material.Attrclass='primitive'` for per-face material assignment, (2) `Transmission=1.0, Thickness=2.0` is the canonical glass setup. Use this pattern when prototyping any path-traced WOBAR visual.

- **POPX has TWO rendering pipelines** — recognize which to use when:
  - **Standard rasterized** (renderTOP + lightCOMP + standard MAT) — fast, real-time, the default for live performance and most music video frames. What we've been using throughout.
  - **POPX path-traced** (Path Tracer + POPX Material + POPX Light Type='area'/'env') — physically-based, slower per-frame, dramatically more cinematic (true reflections, soft shadows, GI). For export-quality renders / hero stills only.
  - **They overlay** — `Path Tracer.Rendertop` points at a renderTOP, so you can have raster as guide + path tracer as final, OR use just raster for performance.
  - **Decision rule:** live performance + any visual that needs sustained 60fps → rasterized. Final music video renders / album art / hero stills → path traced.

- **Generative aesthetic taxonomy** — POPX provides multiple distinct generative-aesthetic solvers, each with a different visual signature:
  - **Flow** — Eulerian (grid) fluid / smoke / advected geometry through a velocity field
  - **POPX Particle (Fluid SPH)** — Lagrangian (particle) fluid / liquid surfaces / droplets — paired with **SSFR** for continuous surface rendering
  - **DLA** — outward fractal aggregation (coral, lightning, mycelium)
  - **DLG** — 2D self-avoiding line growth (brain coral, labyrinth, fingerprint)
  - **Mesh Fill** — interior volume packing constrained by a mesh
  - **MoveAlongCurve / MoveAlongMesh** — instances flowing along curves or mesh surfaces
  - **Physarum** — slime mold network simulation (2D or 3D) with TOP-bounded constraint volume
  Pick by aesthetic + topology:
  - "smoke/fire/diffuse fluid in a box" → **Flow** (grid-based)
  - "water droplets/splashes/liquid surfaces" → **POPX Particle SPH + SSFR** (particle-based)
  - "filling space organically outward" → **DLA**
  - "filling 2D plane with maze patterns" → **DLG**
  - "filling INSIDE a specific mesh shape" → **Mesh Fill**
  - "particles flowing along a curve" → **MoveAlongCurve**
  - "particles flowing along a surface" → **MoveAlongMesh + OrientMesh**
  - "vascular / mycelium / slime mold / neural network growth" → **Physarum**
  All follow the `*Updatepop`-style feedback loop pattern internally.
- **Shape Falloff as cull mask** — wire Shape Falloff output through a `deletePOP` thresholded on `popxFalloff` to cull points outside a region. Cleaner than Group filters when the boundary is geometric (sphere/box/etc).
- **Two-falloff layered design** — example pattern: one Shape Falloff (e.g. larger sphere with soft edge) used as a delete mask via deletePOP; a SECOND Shape Falloff (different size/transition) feeds Attribute To Index for downstream geometry assignment. Same geometric concept (sphere) reused twice with different parameters for two distinct purposes.
- **Live infection painting** — `panelCHOP cursor → math/lag → null → infection_falloff1.Seed.Positionx/y.expr`, paired with `Dissipationrate > 0, Enablereinfection = True`. Cursor leaves a temporary trail of infection that fades behind it; re-infects on revisit. The inverse of `trailPOP`: instead of the cursor's path being drawn as trail geometry, the cursor's path activates temporary state across an existing instance grid. Grid is the canvas; cursor is the brush; infection is the paint that fades.
- **TOP-painted real-time collision for SPH fluid** — `Particle.Collisiontype='t2d', Collisontop=<TOP>` reads a TOP as 2D collision field. Bright pixels = solid; dark = empty. Combined with a painted-collider feedback chain, you get fluid that responds to user-painted obstacles in real time:
  ```
  cursor coords → circleTOP (brush at cursor)
              → feedbackTOP (accumulate strokes) → limitTOP (clamp)
              → levelTOP (opacity 0.99 = 1%-per-frame fade)
              → overTOP (new paint on top of fading old)
              → thresholdTOP (binarize for clean collision)
              → particle1.par.Collisontop
  ```
  The painted obstacles fade naturally over time; new strokes accumulate. Generalizes: replace cursor with any TOP source (audio FFT visualization, video silhouette via camera+threshold, image-driven obstacles).
  - **WOBAR applications:** live painting performance, audio-shaped obstacles (FFT → bars → fluid), performer silhouette as collider, brand-mark-shaped fluid containers.
- **Cursor-input smoothing chain** — `panelCHOP → mathCHOP (remap) → mathCHOP (rescale) → lagCHOP → null`. The `lagCHOP` adds inertia so cursor jitter doesn't make the infection seed twitch. Standard for any continuous-input-driving-infection-or-flow pipeline.

- **Animated-pivot pendulum pattern** — `speedCHOP (time accumulator) → functionCHOP (sin/cos) → null → Pivot.Shiftamount*.expr`. Pivot location animates over time → instances rotate around a moving pivot → pendular sway effect. WOBAR variants: replace `speedCHOP` with audio CHOP (energy/sub_bass) for music-driven swinging; drive Shiftamountx/y/z together via `(cos(t), sin(t), 0)` for orbiting pivot → wobble.

- **Spatial-region-controlled pivot variation** — `Pivot.Dofalloff=True, Falloffattr='popxFalloff'` — pivot shift strength per instance controlled by spatial falloff. Pattern: `[falloff source: Shape Falloff / Texture Falloff / Audio-driven] → Pivot (Dofalloff=True, Shiftamount=MAX) → Transform Modifier (Rz)`. Instances at falloff=1 get full pivot shift (rotate around offset point); instances at falloff=0 get no shift (rotate around center). One Pivot module produces spatially-varied rotation behavior. WOBAR uses: audio-pulsed pivot region (only instances near audio energy peak swing), brand-mark pivot (instances inside wordmark behave differently from outside), performer-position pivot (instances near performer rotate dramatically).

- **Animated-falloff-source = traveling effect (THE canonical POPX workflow)** — the smallest viable POPX pipeline: `[instancer] → [falloff source with Tx/Ty/Tz animated by audio/LFO/cursor] → [modifier with Dofalloff=True, Falloffattr='popxFalloff'] → render`. As the falloff source's transform moves, the affected region travels across the instance field. The falloff source defines WHERE the effect is; the modifier defines WHAT the effect is; they're decoupled. **This is how all audio-reactive POPX visuals work.** WOBAR variants:
  - Audio-driven sweep: `Shape Falloff.Tx.expr = audio_energy * 2 - 1` → effect region tracks audio
  - Beat-locked snap: `Shape Falloff.Tx` snaps to discrete positions on transient → effect teleports beat-by-beat
  - Cursor-following region: `Shape Falloff.Tx/Ty.expr = cursor_position` → live painting

- **Vascular tree / branching network recipe** — production-ready pipeline for "leaf veins / capillary tree / lightning / transit network" visuals:
  ```
  pointPOP (single start) + pointgeneratorPOP (many ends arranged on perimeter)
      → groupPOP for each (Startgroup='start', Endgroup='end')
      → mergePOP
      ↓ wired to Shortest Path.in1
  Planar Patch (circular mesh)
      ↓ wired to Shortest Path.in0
  Shortest Path (Iterations=200, Nebrtype='connected', Maxpaths=10000)
      → linesmoothPOP (smooth out triangulation aliasing)
      → Sweep (Surfaceshape='tube', Width=0.005,
              Applyscale=True, Scaletop=<thick→thin ramp>,
              Applycolor=True, Colortop=<gradient ramp>)
      → render
  ```
  - The aesthetic emerges automatically — single-source-multi-destination shortest paths share common segments → branching tree by mathematical inevitability.
  - WOBAR variants: brand-mark vascular (start at mark center, ends at perimeter); audio-driven branching (end-point positions follow FFT); 3D Shortest Path (replace Planar Patch with 3D mesh) for volumetric vasculature.
- **POP-based multi-seed infection with per-seed radius** — instead of a single-position seed, wire a POP into `infection_falloff1.in1` (the Seedpop input). Each point on that POP becomes a simultaneous infection seed. Add a per-point `radius` attribute via `attributePOP` upstream → each seed gets independent influence area. Lets you author heterogeneous infection patterns: 4 corner seeds with small radius, 1 center seed with large radius, audio-driven moving seeds, spectral-band seed positions, etc. — all in one Infection Falloff module.
- **`rectanglePOP surftype='point'`** — gives you the 4 corner vertices of a rectangle as a POP, useful as a corner-seed source. Native POP for "geometry primitive used purely as a small fixed point set" — alternative to manually placing 4 pointPOPs.

---

## Gotchas

- **POPX dependency on receiving TDs** — anything saved as `.tox` that uses POPX requires POPX installed downstream. Either commit POPX as a project dependency or bake out (convert POPX module output to native POPs) before saving WOBAR-final tox files.
- **Vendor library errors are out of scope** — POPX example projects ship with ~100 internal errors when opened standalone (broken `'./text'` / `'./rectangle'` / `'icon'` panel references inside `License/annotation/...`, missing POPXExt sync files, `parent.POPX.par.X` references in module internals). These are POPX library packaging bugs. **Do not modify POPX internals** — same principle as not modifying `/ui`, `/sys`, `/local`. Render output is unaffected.
- **`parent.Loader.par.Reset` / `parent.Example.par.Reset` cascade** — POPX example files assume they're loaded inside a wrapper "Loader" container at runtime. When opened standalone, `parent.Loader` doesn't exist and Reset cascades into MoveAlongCurve solver Startpulse/Initializepulse. Fix: clear the broken expression on the example's root container `par.Reset`. (Confirmed on `coil torus.toe`, 2026-04-29.)
- **`Width clamped due to GPU limitations` warnings** — POPX builds wide internal lookup textures (ramps, fits) for its solver paths. Apple Silicon's GPU texture-width limit clamps these. Performance hint, not a failure — but watch for visible quality degradation in modules using these LUTs.
- **MoveAlongCurve solver state requires intact POPX parent shortcut** — wrapping a MoveAlongCurve module inside a baseCOMP that doesn't promote the `POPX` parent shortcut will break the `Startpulse`/`Initializepulse` references inside the solver. Either preserve the shortcut or let the module live at the parent COMP level.
- **`parent.Loader.par.Resolutiony` cascade** — POPX example files often have expressions like `800 if parent.Loader.par.Showdescription else 1080` on the example container's resolution. When opened standalone, this cascades: `/example.par.Resolutiony` errors → `render1.par.resolutionh` (which references `parent.Example.par.Resolutiony`) errors. Fix: clear the broken expression on the example's `Resolutiony` (and `Reset`) parameters and set them to constants. (Confirmed on `convert.toe`, 2026-04-29.)
- **Mac/Windows POPX shader variants** — POPX modules with GLSL POPs (Convert, others) ship parallel `_mac` and `_win` variants of advanced shaders. The platform-mismatched variants show "Compile failed" errors but are inactive at runtime. Don't try to fix the `_win` shaders on Mac. Confirmed on `convert.toe` for `connectivity/avg_win`, `connectivity/sum_win`.
- **`tracePOP` has no `width`/`height`** — unlike most TOPs, `tracePOP` is a POP operator (not a TOP) so it has no `.width`/`.height` attributes. When inspecting via Python, use `numPoints` instead.
- **Flow voxel cost scales cubically** — `Resolutionx × Resolutiony × Resolutionz × Pressureiters × Diffusioniters × per-frame passes`. 128×128×32 (~524k voxels) is the example default and runs OK on Apple Silicon NC at 60fps; doubling any axis multiplies cost ~8×. Profile before betting a heavy WOBAR visual on Flow at higher resolutions.
- **Flow internal solver state requires intact POPX parent shortcut** — Flow ships with many internal feedback TOPs/POPs (Velocity_Field, Pressure_Solver, Inject_Substance, Inject_Temperature, Particle_Advection) that reference `parent.POPX.par.Reset` for re-initialization. Wrapping Flow in a containing baseCOMP that breaks the POPX shortcut chain breaks all these feedback resets. Same fix as MoveAlongCurve: keep Flow at the parent COMP level or preserve the POPX shortcut.
- **Flow `Reset` cascade** — Flow's Reset par cascades into many internal feedback ResetPulse/Startpulse references. When the parent example container's Reset is broken (`parent.Loader` not found), Flow's `lfo*.resetpulse`, `cache*.activepulse`, `feedback*.resetpulse`, and `Particle_Advection/feedback*.startpulse` all error in cascade. Fix the root container's Reset par; cascade clears.
- **Flow ships with `glsl2_pixel` broken references** — Flow's internal GLSL TOP/POPs reference `glsl2_pixel` / `glsl1_pixel2` text DATs that aren't always present in the example tox. These are POPX library packaging bugs; don't fix them, they don't affect runtime fluid behavior.
- **OptiX denoiser is NVIDIA-only** — `Path Tracer.Denoiser='optix'` requires NVIDIA RTX hardware + OptiX runtime (loaded via DLL). **Does not work on Apple Silicon Mac** — render output silently goes blank. Always use `Denoiser='svgf'` on Mac. Confirmed on `path tracer glass (optix denoiser).toe`, 2026-04-29.
- **`fileinPOP.par.file` parent.Loader expression** — POPX example files load assets via expressions like `parent.Loader.par.Popxreleasefolderpath + '/assets/foo.obj'`. When opened standalone, this errors and the mesh fails to load → render is empty. Fix: clear the expression and set the absolute file path to `<repo>/touchdesigner/POPX_Examples_1_3_0/assets/<asset>.obj`. (Confirmed on `explode curl.toe`, 2026-04-29.)
- **Explode at high cluster counts is expensive** — `napoleon.obj` (~1M points) Voronoi-partitioned into 2000 clusters runs at ~5 fps on Apple Silicon NC. Mitigations: (1) decimate the mesh before Explode, (2) reduce `Numberofclusters`, (3) pre-bake — run Explode once and freeze with `Play=False` (if exposed) or cache the result via a polyreduce/cache POP downstream.

---

## Appendix: Setup Sequences Reference Card

Quick reference for stateful POPX modules. The activation pattern that's universal across the POPX simulation family.

### Universal pattern
Most stateful modules follow `Initialize → Start → Play`:
```
1. Pulse Initialize    # reset & spawn
2. Pulse Start         # begin from initialized state
3. Toggle Play = True  # enable continuous playback
4. (Optional) Step pulse for frame-by-frame when paused
```

### Per-module specifics

| Module | Pattern | Required Setup Beyond Init/Start/Play |
|--------|---------|----------------------------------------|
| **SA (Strange Attractor)** | Init→Start→Play | `Solvermode='advect'`, `Pointsupdatepop` REQUIRED |
| **Flow** | Reset pulse + Advect toggle + Solvermode | `Advect=True` AND `Solvermode='advect'` (BOTH required); `Particlesupdatepop` for feedback; `Inject=True` + `Injectionpop` for substance source |
| **Particle** (Fluids-SPH/PBF/Grains) | Init→Start→Play | Choose Material Mode; set `Solvermode='advect'` |
| **DLA** | Init→Start→Play | Connect seed POP to Input 0; `Walkersupdatepop` optional |
| **DLG** | Init→Start→Play | `Target Line Update POP` REQUIRED for feedback |
| **Physarum** | Init→Start→Play | BOTH `Target Particles Update` AND `Target Trail Update` REQUIRED |
| **Soft Body** | **Init + Play** (NO Start) | Connect POP geo + constraints + collisions to inputs 0/1/2 |
| **Mesh Fill** | Init→Start→Play | Get bounds from input geometry |
| **Infection Falloff** | Init→Start→Play | Configure seeds (Position+Radius OR seed POP with `P`/`radius` attrs) |
| **Spring Modifier** (Advect mode) | Init→Start→Play | `Solvermode='advect'`, select effect mode (Position/Rotation/Scale/Other), `Pointsupdatepop` creates feedback loop |
| **Noise Modifier** (Advect mode) | Init→Start→Play | `Mode='advect'` |
| **Move Along Curve** (Solver mode) | Init→Start→Play | `Mode='solver'` (vs `'simple'`/`'goal'`) |
| **Relax** (Advect mode) | Init→Start→Play | `Solvermode='advect'`, `Pointsupdatepop` REQUIRED |
| **Magnetize** (Advect mode) | Toggle Play (no separate Init/Start documented) | `Solvermode='advect'`; magnets via Input 1 or `Magnetspop` |

### Common failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Module pulses Initialize but freezes immediately | Skipped `Start` pulse | Pulse Start after Initialize |
| Solvermode='advect' but no animation | Skipped Play toggle | `Play=True` |
| Flow particles don't move | `Advect` toggle still False | Set `Advect=True` + `Solvermode='advect'` (both) |
| SA collapses all points to one trajectory | Long runtime + no per-frame input variation | Switch noise to write `Rotate` not `P` (use `combineop='none'`); add upstream randomize on positions before SA |
| DLA / DLG / Physarum stop progressing | Missing `*Updatepop` feedback handle | Wire downstream null POP back to the solver's Updatepop param |
| NaN values in chaos module | Timescale changed mid-run + integration overflowed | Pulse Initialize to reset; lower Timescale to safe value (1.0–2.5) |
| `Solvermode='simple'` looks frozen | That's expected — simple is single-step velocity evaluation, no integration | Switch to `'advect'` if you want time evolution |

### When pulses don't fire (TWOZERO Python from outside TD)

**Reminder from debug log:** Pulse parameter callbacks (`OnXxxPulse` extension methods) do NOT fire automatically when `par.pulse()` is called from outside TD. They require a `parameterexecuteDAT` inside the module with `par.op` pointing at the COMP and `par.pars` listing the pulse pars.

Most POPX modules have this DAT pre-wired internally — look for `parexec1` in their children. If pulses don't seem to advance state, verify:
1. `parent.<ParentShortcut>` is set correctly on the host COMP (`/example.par.parentshortcut='Example'`)
2. The internal `parexec1.par.op` resolves
3. No `td.OPShortcut` AttributeErrors in the textport (those silently break the auto-step machinery)

This is THE source of the externaltox-loaded-example failures we saw on 2026-04-30 — when SA/Flow examples are loaded as `externaltox` rather than as native components, the parent shortcut wiring breaks and pulses become silent.

---

## Related Files

- `td_library/TD_OPERATORS_POP.md` — native POP family (sphere, line, copy, attribute, normal, etc.)
- `td_library/TD_PATTERNS_INSTANCING.md` — pre-POPX instancing patterns (Script CHOP bridge)
- `working/TD_BUILD_LOG.md` — session notes when POPX modules are tried in WOBAR builds
- `working/TD_CLAUDE_DEBUG_LOG.md` — POPX-specific failures, if/when they're confirmed
- `working/POPX_DOCS_FINDINGS.md` — full findings report from official docs reconciliation (2026-04-30)
- `working/popx_raw/*.md` — raw extracts from individual official doc pages (60+ files)
