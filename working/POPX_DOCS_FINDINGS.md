---
title: POPX Docs vs Internal Guide — Findings Report
date: 2026-04-30
docs_version: 1.3.0
internal_guide: reference/td_library/TD_POPX_GUIDE.md (v1.0)
sources: working/popx_raw/*.md (raw doc extracts saved alongside)
status: ready for guide update
---

# POPX Docs vs Internal Guide — Findings Report

This report compares the official POPX 1.3.0 docs (popsextension.com) against our internal guide. The internal guide was built from observation of example .toe files; this report identifies where it's wrong, what it missed, and what should be added.

---

## Section 1: Critical Corrections

### 1.1 SA (Strange Attractor) — Init→Start→Play sequence (not just Init)

**Internal guide says:** Pulse `Initialize` to start simulation. Use `Solvermode='advect'` and points will animate.

**Docs say:** REQUIRED 4-step sequence in Advect mode:
1. **Initialize** (pulse) — reset & spawn particles
2. **Start** (pulse) — begin from initialized state
3. **Play** (toggle) — enable continuous playback
4. **Step** (pulse) — frame-by-frame when paused

**Why this matters:** Tonight's entire SA build session failed because we never pulsed `Start` after Initialize. Integration would freeze post-init. The "freeze after initialize" gotcha I documented in v001 was actually USER ERROR — we missed step 2.

**Also:** Advect mode REQUIRES `Pointsupdatepop` (Target Points Update POP) reference. Without it, the feedback loop doesn't close.

**Guide section to fix:** SA module section (~line 1820+). Add the 4-step sequence prominently. Remove the "Solvermode='advect' collapses points" claim from canonical patterns — that was misdiagnosis.

### 1.2 Flow — Advect TOGGLE is separate from Solvermode

**Internal guide says:** Flow's `Solvermode='advect'` enables particle advection.

**Docs say:** `Solvermode` (simple/advect) and `Advect` (toggle) are TWO INDEPENDENT controls. Both must be configured. `Solvermode` selects the algorithm; `Advect` toggle activates the particle advection feature.

**Why this matters:** This is the headline confusion that blocked our Flow setup tonight. Setting `Solvermode='advect'` alone does nothing visible if `Advect=False`.

### 1.3 Universal pattern — ALL stateful simulators use Init→Start→Play

**Internal guide:** Documents Initialize for some modules, doesn't surface this as a universal pattern.

**Docs:** Init→Start→Play is the canonical sequence for EVERY stateful POPX module:
- SA, Flow (variant), Particle, DLA, DLG, Physarum, Mesh Fill, Infection Falloff, Spring Modifier (Advect mode), Noise Modifier (Advect mode), Move Along Curve (Solver mode), Relax (Advect mode)

Soft Body is the exception: `Initialize + Play` (no Start step).

**Guide section to fix:** Add a "Stateful Simulation Setup Sequence" reference at the top of the modules section, before any individual module docs. Cross-reference from each stateful module.

### 1.4 v1.3.0 Breaking changes the guide hasn't tracked

**Path Tracer:**
- Voxel Tracer REMOVED
- Built-in Material/Lights pages REMOVED
- Now REQUIRES separate POPX Light component connection

**DLA:**
- Built-in mesh and volume outputs REMOVED
- Use Voxelize/Polygonize downstream for those representations

**Constraints:**
- Standalone "Constraints Config" operator REMOVED
- Constraints are now configured within POPX Constraints itself

**Material:**
- "Subsurface" parameter REMOVED
- Renamed parameters follow updated PBR conventions
- New Maps page with texture inputs
- New Clearcoat and Emission parameters

**Particle (formerly SPH):**
- Renamed from SPH to Particle
- Added multiple solver modes (SPH / PBF / Grains)
- Added material options

**Soft Body:**
- Restructured with new Collisions architecture

**Guide section to fix:** All affected module sections need version-update notes; capability table may have entries that reference removed features (Path Tracer's built-in lighting, DLA's volume output).

### 1.5 SA preset list — guide has 6, docs have 11

**Guide says:** Presets include lorenz, thomas, aizawa, halvorsen, rossler, chen.

**Docs say:** Full list is 11 presets:
**Lorenz, Aizawa, Thomas, Halvorsen, Dadras, Chen, Rossler, Sprott, Four-Wing, Nose-Hoover, Custom.**

Plus `Custom SA` parameter accepts a DAT reference; "Generate Script DAT" pulse creates a template you can edit.

### 1.6 Solvermode='simple' meaning is universal

**Docs clarify across modules:**
- `Simple` = single-step velocity field evaluation (no integration history). Static-looking output unless input changes per-frame.
- `Advect` = updates state with full simulation controls (Init/Start/Play required).

This applies consistently across SA, Flow, Particle, Spring, Noise, Magnetize, Move Along Curve, Relax. Document once at the top, reference per-module.

---

## Section 2: Missing Modules

### 2.1 Spread Falloff
**Not in guide.** Non-simulation falloff that propagates outward from seeds through neighbor connections. Looks like Infection Falloff but is DIRECT (no Init/Start/Play). Use when you want infection-shaped patterns without simulation overhead.

Key params: Spread By (radius/connectivity), Search Radius, Falloff Width, Spread Amount (organic randomization), Threshold for seed activation.

### 2.2 Object Falloff
**Not in guide.** Generates falloff based on distance to arbitrary 3D mesh (vs Shape Falloff which is geometric primitives). Area of Influence modes: inside/outside, surface distance, surface intersection.

### 2.3 Curve Falloff
**Not in guide.** Distance-from-curve falloff. 3 modes: distance to curve, distance × curve position, normalized curve position alone. Different from MoveAlongCurve (which is a modifier).

### 2.4 POPX Material
**Underdocumented in guide.** v1.3.0 changes are significant: Disney BRDF, Maps page with texture inputs (normal, metallic/roughness, emission), Clearcoat and Emission parameters (new in 1.3.0), Subsurface removed. Substance Integration support.

### 2.5 Apply Attributes
**Not in guide.** Core transformation engine — takes packed primitives and applies template point attributes for transforms. Slerp for rotation interpolation, linear for translations/scales. The "engine" of how POPX modifiers actually drive transforms.

### 2.6 Extract Attributes
**Not in guide.** Bridges POPX → native TD: converts POPX transforms back to standard point attributes (N, Up, Orient, Scale, Pivot, Euler) for use with native Copy to Points or Geometry COMP instancing.

### 2.7 Geometry (POPX tool)
**Not in guide.** POPX's per-instance material renderer. Functions like a TD Geometry COMP but allows different materials per instance based on index. Key for varied-material crowds / scenes.

### 2.8 Merge (POPX tool)
**Not in guide.** Combines multiple POPX geometry streams into one. Preserves attributes/groups/instance data from each source. Add/remove inputs dynamically.

### 2.9 Delete (POPX tool)
**Not in guide.** 5 filtering methods (Attribute / Thin / Pattern / Group / Bounding) combinable with logical operators (AND, OR, XOR, NAND, NOR).

### 2.10 Preview Falloff (tool)
**Not in guide.** Standalone debugging tool that visualizes falloff via color ramps (Heatmap/Blackbody/Infrared/custom). Different from the inline `Previewfalloff` toggle on each falloff module.

---

## Section 3: Missing Critical Gotchas

### 3.1 Init→Start→Play — universal sequence
*(Already covered in 1.3 — this is the biggest missing gotcha)*

### 3.2 Flow's Advect ≠ Solvermode
*(Already covered in 1.2)*

### 3.3 SA: Pointsupdatepop required in Advect mode
Docs make this explicit. Our guide treated `Pointsupdatepop` as optional/advanced. It's required.

### 3.4 Magnetize per-magnet attribute names
Docs list the EXACT attribute names that override magnet parameters per-magnet:
**`P, radius, strength, exponent, mode, spindir, contain`**

Our guide mentions per-magnet customization but doesn't list the attribute name conventions.

### 3.5 Infection Falloff seed attribute names
Docs say: "Seed attributes must match parameter token names" — i.e., a seed POP must use `P` for Position, `radius` for Radius, etc. Mismatched attribute names silently break seeding.

### 3.6 Sweep cross-section types
Internal guide: lists tube, square, rectangle, input. Docs: only THREE types — Round Tube / Square Tube / **Second Input Cross Sections** (for custom curves via input[1]). The "rectangle" we documented may be a v1.2 alias or wrong.

### 3.7 Voxelize has 4 outputs (we documented 4 but with wrong slots)
Docs:
- Output 0: Volume (TOP)
- Output 1: Surface (TOP)
- Output 2: SDF (TOP)
- Output 3: Hit Attributes (POP — mesh mode only)

Our guide had output[3] as "voxel-center POP with Inside attribute." That POP output (Output 3) IS the hit attributes — `Inside` is one of the hit attrs. Need to reconcile / clarify.

### 3.8 Move Along Curve — three modes (not two)
Docs: `Mode` has Simple, Solver, AND Goal options. Solver mode requires Init/Start/Play. Simple uses procedural Goal parameter (0=start, 1=end). We documented 2 modes; missed the procedural-vs-stateful split clarification.

### 3.9 Spring Modifier "Other" mode + Pointsupdatepop = feedback loop
Docs say Target Points Update reference "WILL CAUSE A FEEDBACK LOOP" when Solver Mode uses Advect. This is intentional and required for true Spring physics — but it's the source of the per-point lag we saw with `Spring 1.toe`.

### 3.10 Reorient outputs `popxOrient` quaternion attribute
Docs name it explicitly: `popxOrient`. Our guide describes the function but doesn't name the attribute.

### 3.11 Attribute To Index outputs `popxIndex` (default)
Confirmed. Our guide is correct here.

---

## Section 4: Missing Parameter Details

### 4.1 SA — full Bounds page
Docs: per-axis Limit Type Min/Max with options **Off, Clamp, Loop, Zig Zag**. Internal guide had `'off'`, `'clamp'`, `'wrap'`. Actual options are **Off / Clamp / Loop / Zig Zag** — and "wrap" doesn't exist.

### 4.2 Flow — full parameter inventory
Docs list ~60+ params across categories: General, Velocity, Substance, Pop Injection (Inject toggle, Injectionpop, Injectpos, Injectscale, Injectgain, Injectstrength, Injecttemp, Injectcolor), Source (Addsource, Substancegain, Forcestrength, Temperaturegain), Buoyancy (Applybuoyancy, Buoyancystrength, Gasweight, Coolingrate, Expansion), Gravity (Applygravity, Gravityvector, Gravitystrength, Surfacelevel), External Force (Externalforcetop, Extforcestrength), Optical Flow (Opticalflowtop, Optiflowforcestrength), Bounds (Boundstop, Showbounds), Obstacle (Obstacletop, Renderobstacle, Obstacleopacity), Particles (Advect, Solvermode, Particlesupdatepop, Advectionstep, Spawn, Numparticles, Densityscale, Threshold, Seed, Maxattempts, Enableparticlelife, Lifespan, Lifevariance, Lifeseed), Lookup Color, Channel masks. The internal guide lists Flow but doesn't enumerate these — needed for accurate audio binding plans.

### 4.3 Particle — collision types
Internal guide doesn't enumerate. Docs list: **None, POP, Box, Plane, Sphere, Torus, 3D-SDF, 2D-SDF, T3D, T2D**. T3D/T2D are texture-based collision (e.g. for animated 2D collision shapes — a key audio-reactive vector).

### 4.4 Particle — material modes
**Fluids-SPH, Fluids-PBF, Grains.** Each has mode-specific params:
- PBF: Cohesion, Surface Tension, Adhesion
- Grains: Repulsion Weight, Attraction Weight

The internal guide treats Particle generally without distinguishing these.

### 4.5 Soft Body — Collisions architecture (v1.3.0 restructure)
Multiple geometry types: ground plane, bounding box, sphere, box, plane, SDF, T3D, T2D. Self-collision with configurable neighbor search. Maximum acceleration limiting. Integration order (first/second). Collision-triggered fallback integration. Need to update the Soft Body section to reflect 1.3.0 architecture.

### 4.6 Mesh Fill — 8 outputs
Docs:
0. Trails (TOP)
1. Filled Volume (TOP)
2. Inverted Filled Volume (TOP)
3. Velocity (TOP)
4. Volume (TOP)
5. Seed (POP)
6. Trails (POP)
7. Mesh (POP)

Internal guide doesn't enumerate these; they're each independently useful.

### 4.7 Physarum — outputs include 2 TOPs
Docs: Output 0 = Particles (POP), Output 1 = Trail (TOP), Output 2 = Deposit (TOP). The Trail TOP is the iconic Physarum visual — accumulated pheromone texture.

### 4.8 Pivot — 5 modes (we have 3)
Internal guide: bbox, shift, setworld.
Docs: **Center Pivot / Align to BBox / Shift Pivot / Set Pivot (Local) / Set Pivot (World)**.

The "Center Pivot" and "Set Pivot (Local)" modes aren't in our guide.

### 4.9 Aim — three Aim Methods
Internal guide focuses on simple aim. Docs distinguish:
- **Vector-based** (aim toward fixed direction)
- **Object-based** (aim toward a single object's position)
- **Points-based** (each instance aims toward corresponding point in target POP)

Plus mirrored Up Method (Vector / Object / Points) and `Constrain Around Up` to restrict rotation to up axis only.

### 4.10 Color Modifier — Ramp can be internal editor OR external Ramp TOP
Docs: "Color Ramp accepts internal editor or external Ramp TOP reference." Internal guide should mention the external Ramp TOP path explicitly.

### 4.11 Subdivider — Iterations & Inset semantics
Internal guide describes them roughly. Docs clarify: `Iterations` = post-subdivision passes, `Inset` = inset amount per pass, falloff value of 1.0 = full max-subdivisions per primitive.

---

## Section 5: Capability Table Additions

Recommended new rows for the capability table at top of guide:

| Need | Without POPX | With POPX |
|------|-------------|-----------|
| Falloff from arbitrary 3D mesh shape | Custom SDF GLSL | `Object Falloff` |
| Falloff from distance to a curve | Custom GLSL | `Curve Falloff` |
| Non-simulating wave-spread falloff (no Init/Play overhead) | Hand-author flood-fill | `Spread Falloff` (NOT Infection Falloff) |
| Convert any point attribute → integer index for indexed instancing | Math CHOP per-instance | `Attribute To Index` (writes `popxIndex`) |
| Bridge POPX transforms back to native TD operators | Manual matrix extraction | `Extract Attributes` |
| Per-instance materials in a packed POPX render | Multiple Geometry COMPs | `Geometry` (POPX tool) — auto-detects instance count |
| Combine multiple POPX streams | Multiple merges of native POPs | `Merge` (POPX tool) |
| Delete points by attribute / index range / pattern / group / bounding | Hand-author Delete SOP chain | `Delete` (POPX tool — 5 methods, AND/OR/XOR combinable) |
| Reset rotation axes after Explode/Voronoi shatter | Manual quaternion math | `Reorient` (writes `popxOrient`) |
| Smooth orientation frames along curve for sweep | Custom parallel-transport math | `Orient Curve` |
| Mesh-surface flow / swirling motion frames | Custom GLSL geodesic | `Orient Mesh` (with Cross Up Vector for swirl) |
| Visualize falloff distribution for debugging | Manual color ramp + lookup | `Preview Falloff` standalone tool |
| 11 chaos attractor presets (was: 6) | Hand-author equation | `SA` with full preset library + Custom DAT |

---

## Section 6: Setup Sequences Reference Card

Stateful simulation modules — the EXACT sequence:

### SA (Strange Attractor) — Advect Mode
1. Set `Solvermode = 'Advect'`
2. Set `Pointsupdatepop` to downstream POP (required)
3. Pulse **Initialize** — reset & spawn
4. Pulse **Start** — begin from initialized state
5. Toggle **Play** = True — continuous playback
6. (Optional) Pulse **Step** for frame-by-frame when paused

### Flow — Particle Simulation
1. Connect inputs (POP injection → Input 0; TOP source → Input 1; POP particles → Input 2)
2. **Enable `Advect` toggle** (separate from Solvermode!)
3. Set `Solvermode` ('simple' or 'advect')
4. Enable `Spawn` (or provide Particles via Input 2)
5. Set `Particlesupdatepop` to downstream POP reference
6. Pulse **Reset** to initialize
7. Adjust `Timescale` to control evolution

### Particle (SPH/PBF/Grains)
1. Set Material Mode (Fluids-SPH / Fluids-PBF / Grains)
2. Set Solvermode ('simple' or 'advect')
3. Pulse **Initialize**
4. Pulse **Start**
5. Toggle **Play** = True

### DLA
1. Connect POP seed input
2. Pulse **Initialize**
3. Pulse **Start**
4. Toggle **Play** = True
5. Optionally set Updatepop for feedback

### DLG
1. Connect line geometry input
2. Set `Target Line Update POP` (required for feedback)
3. Pulse **Initialize**
4. Pulse **Start**
5. Toggle **Play** = True

### Physarum
1. Connect particles to Input 0; optional constraint TOP to Input 1
2. Set both `Target Particles Update` and `Target Trail Update` (both required for feedback)
3. Pulse **Initialize**
4. Pulse **Start**
5. Toggle **Play** = True

### Soft Body — exception: no Start step
1. Connect POP geometry to Input 0
2. Connect constraints to Input 1
3. Connect collision geometry to Input 2 + enable collision types
4. Pulse **Initialize**
5. Toggle **Play** = True

### Mesh Fill
1. Pulse **Initialize**
2. Pulse **Start**
3. Toggle **Play** = True

### Infection Falloff
1. Configure seed (Position+Radius OR seed POP with matching `P/radius` attrs)
2. Pulse **Initialize**
3. Pulse **Start**
4. Toggle **Play** = True

### Spring Modifier — Advect mode
1. Set `Solvermode = 'Advect'` and select effect mode (Position/Rotation/Scale/Other)
2. If "Other" mode: set `Attr` to target attribute name
3. Set `Pointsupdatepop` (creates feedback loop)
4. Pulse **Initialize**
5. Pulse **Start**
6. Toggle **Play** = True

### Noise Modifier — Advect mode
1. Set `Mode = 'Advect'`
2. Pulse **Initialize**
3. Pulse **Start**
4. Toggle **Play** = True

### Move Along Curve — Solver mode
1. Set `Mode = 'Solver'`
2. Pulse **Initialize**
3. Pulse **Start**
4. Toggle **Play** = True
5. Use **Step** for frame-by-frame if paused

### Relax — Advect mode
1. Set `Solvermode = 'Advect'`
2. Set `Pointsupdatepop` (required for feedback)
3. Pulse **Initialize**
4. Pulse **Start**
5. Toggle **Play** = True

### Magnetize — Advect mode
1. Connect input POP to Input 0
2. Connect magnet POP to Input 1 (or set Magnets POP parameter)
3. Set `Solvermode = 'Advect'` (otherwise no integration)
4. Toggle **Play** = True

---

## Section 7: Documentation Gaps (where internal guide is BETTER)

The internal guide covers things the official docs don't:

1. **WOBAR-specific applications** — "use this for Act 1 cosmic descent" framing that ties modules to creative use cases.

2. **Audio-reactivity wiring** — concrete `op('audio_ref')['sub_bass']` expressions and binding patterns to module parameters. Official docs treat each module in isolation.

3. **Integration patterns (cumulative section)** — multi-module recipes like:
   - Disintegration recipe (Explode → Infection Falloff → Noise Modifier → Transform Modifier)
   - Trail-driven age-based instancing (animated points → trailPOP → popxto → Attribute Falloff → Instancer)
   - Mesh-as-flow-field via differential geometry
   - Hierarchical attribute propagation through Instancer→Unpack→Solver
   - Per-letter typography rig (Convert→Pivot→Spring→Transform Modifier→Unpack)
   - Living Voronoi (pointgen→Relax→noise→null→Explode-voronoi)
   - Voxel-art instancing
   - Hair/strings on rigged characters

4. **The `popxFalloff` attribute as universal control mechanism** — docs treat this as a per-module convention; our guide elevates it to a key architectural concept.

5. **Native POP / POPX bridging via `popxto`** — official docs describe popxto but don't surface it as a critical bridge between native + POPX worlds.

6. **Cost / performance notes** — "5k–20k points typical at 60fps" guidance is in our guide but not in docs.

7. **Failure-mode debugging** — "what goes wrong and why" content like "without an upstream randomize, all points share trajectory and visually overlap" is in our guide.

**These should be PRESERVED in the update.** The corrections in Sections 1-5 should be ADDITIVE; don't lose this WOBAR context.

---

## Recommended Update Strategy

1. **Add a top-level "POPX Conventions" section** at start of guide (after capability table, before modules):
   - Init→Start→Play universal pattern (with the simple state diagram)
   - Solvermode (simple vs advect) meaning across modules
   - `popxFalloff` attribute convention
   - `Pointsupdatepop` feedback pattern
   - POPX Geometry vs standard POP (packed-data vs point-stream)

2. **Per-module corrections** (Sections 1–4) — apply targeted edits, don't rewrite.

3. **Add missing modules** (Section 2): Spread Falloff, Object Falloff, Curve Falloff, Apply Attributes, Extract Attributes, Geometry, Merge, Delete, Preview Falloff. Each gets a brief module section.

4. **Append Setup Sequences Reference Card** (Section 6) as a clean appendix near the end of the guide. Cross-link from each stateful module section.

5. **Add v1.3.0 breaking changes notes** to the Path Tracer, DLA, Constraints, Material, Particle, Soft Body sections.

6. **Capability table additions** (Section 5) — append rows.

7. **Bump guide version to 1.1**, add changelog note: "Reconciled against official docs 2026-04-30; major correction: Init→Start→Play universal pattern was missing."

8. **DON'T touch** — WOBAR application notes, integration patterns section, audio reactivity examples, cost notes, failure-mode debugging. These are guide-unique value.
