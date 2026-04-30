---
title: TouchDesigner Build Log
version: 1.0
last_updated: 2026-04-30
status: live
scope: Session-by-session log of AI-assisted TD builds. Used to identify recurring corrections and promote them to rules in WOBAR_TD_AGENT_RULES.md.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]]
---

# TD BUILD LOG

One entry per build session. Newest at top. This is the feedback loop — patterns that repeat here become rules.

---

## Correction Tracker

Corrections that appear 2+ times get promoted to WOBAR_TD_AGENT_RULES.md.

| Correction | Count | Promoted? |
|-----------|-------|-----------|
| `filterCHOP` is smoothing not frequency — use `audiofilterCHOP` | 1 | No |
| `lagCHOP` par names are `lag1`/`lag2` not `lagup`/`lagdown` | 1 | No |
| Multiple op() in TOP expressions (5+ × 8 pars) crashes TD — pre-compute in CHOP | 1 | No |
| `par.val` returns cached value — use `par.eval()` to verify expression result | 1 | No |
| COMP custom par referencing CHOP has cook order issues when TOPs read it — reference CHOP directly in TOP expressions | 1 | No |
| `playmode='locked'` ties audio to timeline length — use `sequential` for full track | 1 | No |
| `audiodeviceoutCHOP` with `cookalways=True` freezes TD | 1 | No |
| Python helper functions in `td_execute_python` don't inherit script-level globals — all `op()` refs must be inside the function body | **2** | **✅ PROMOTED** |
| `annotateCOMP` nodeY = bottom edge (not top) — top = nodeY + nodeHeight | 1 | No |
| `analyzeCHOP function='average'` returns ~0 on HP filter output — use `rmspower` for highpass chains | 1 | No |
| `null_audio` is analysis CHOP at rate 30 — use `audio_in` (audiofileinCHOP) for recording audiochop | **2** | **✅ PROMOTED** |
| Geometry COMP has no external SOP input connectors — SOPs must be created as children INSIDE the COMP | 1 | No |
| `op.display = True` / `op.render = True` (not `setDisplayFlag()`/`setRenderFlag()` — those methods don't exist) | 1 | No |
| `tdu.noise()` doesn't exist in TD Python — use noisePOP or Noise SOP for noise generation | 1 | No |
| blurTOP at full resolution with large size (>20px) is CPU-locked — use box type, smaller size, or reduce resolution | 1 | No |
| AAC audio codec blocked on Non-Commercial license — use MP3 codec instead (mp3 is supported, aac is not) | 1 | No |
| `instancepop` and `instanceop` on Geometry COMP don't do position-based instancing — use Script CHOP bridge (SOP points → tx/ty/tz channels) | 1 | No |
| Script CHOP `op()` resolves at parent COMP scope — siblings accessed as `op('name')` not `op('../name')` | 1 | No |
| feedbackTOP direct wire to target creates cook dependency loop — wire a black seed instead; set par.top = target path only | 1 | No |
| MAT expressions inside child COMPs: relative `op()` paths return None — use absolute paths | 1 | No |
| hsvadjustTOP saturation par is `saturationmult` not `satmult` | 1 | No |
| HSV desat kills warm low-luminance colors — muted orange/warm goes black. Warm palettes need higher RGB values to survive the desat chain | 1 | No |
| `triggerCHOP` par expressions unreliable — use `ParMode.CONSTANT` with hardcoded values | 1 | No |
| List comprehensions in `td_execute_python` cannot reference outer-scope variables — use explicit for loops | 1 | No |
| `instancetop` on Geometry COMP is for TOP-based color instancing only — use `instanceop` for CHOP-based position instancing | **2** | No |
| Script CHOP callbacks: NEVER overwrite the whole DAT — TD silently re-generates the template over custom code. Always read existing DAT first, edit `onCook` in place with `text.replace()` | 1 | No |
| poptoCHOP download (immediate or nextframe) on 1800+ points at 60fps kills FPS (3–6ms/cook → <10fps). Use static Script CHOP positions + bypass POP chain instead | 1 | No |
| Script CHOP with no CHOP inputs + `CookLevel.WHEN_USED`: cooks ~1/s not 60fps. Wire an audio CHOP input or use `CookLevel.ALWAYS` for per-frame updates | 1 | No |
| noiseCHOP `par.channelname` always returns 0 channels regardless of value or timeslice setting — cause unresolved, workaround TBD | 1 | No |
| Camera expression `absTime.seconds * speed` drifts to large values across session — use `me.time.seconds` which resets with the component | **2** | **✅ PROMOTED** |
| GLSL TOP: `iTime` and `uTD.time.seconds` are not available — pass time as a uniform via `color0rgbb.expr = absTime.seconds * rate` | 1 | No |
| RampTOP does not have `par.ramppoints` — use a companion textDAT with pos/r/g/b/a rows and set `par.dat = keys_dat` | 1 | No |
| Circle TOP: `radiusunit` defaults to pixels — 0.48 pixels ≈ invisible on 720×1280. Set `par.radiusunit = 'fractionaspect'` for proper portrait coverage | 1 | No |
| Cross-COMP CHOP wiring fails silently — use `selectCHOP` with absolute path `chops='/project1/comp/inner_chop'` | 1 | No |
| `geometryCOMP` auto-creates a default `torus1` (torusPOP, render=True) child — kills new builds with a giant white blob unless explicitly destroyed | **2** | No |
| `compositeTOP` has only 2 input slots — `inputConnectors[2]` raises IndexError. Chain multiple 2-input composites for N-input add | 1 | No |
| `me.storage` inside scriptCHOP onCook callback = the DAT's storage, NOT the operator the callback is attached to | 1 | No |
| scriptCHOP needs a time-dependent input (e.g. constantCHOP with `value0.expr=absTime.seconds`) wired in to recook per frame — `absTime` inside the callback alone doesn't track | 1 | No |
| `pow(negative_float, 2.5)` in expressions returns COMPLEX → TypeError. Audio channels can have tiny negative noise (~1e-22). Always wrap in `max(0.0, ...)` before `pow()` | 1 | No |
| Velocity-based "anti-collapse" thermostats fail when bodies cluster while still spinning fast inside the cluster — use SPREAD-based (cluster bounding radius) instead | 1 | No |
| Fibonacci-sphere seed positions place bodies at ±Y poles where `cross(pos, Y_axis) = 0` → those bodies start with zero tangential velocity and drag the system into collapse. Use a body-varying reference axis | 1 | No |

---

## Build Sessions

---

### 2026-04-30 — Visual Identity Refresh — TD docs rewritten to new palette + materials + no act-rules

**What was done:**
No TD network was built or modified this session. The session was a docs / identity rewrite that changes how *future* TD builds get framed and validated. Logging it here because the docs governing every future TD build session were materially changed.

**Three changes locked in (with Nick's approval):**
1. **Visual identity lens shifts to mirrors and encounter** over portals and journey. Brand docs (`WOBAR_BRAND.md`, `WOBAR_FRAMEWORK.md`, `WOBAR_COPY.md`) left intentionally locked — the lens governs visual decisions only, not brand language.
2. **Metallic / glossy / reflective surfaces are permitted.** Gloss is no longer banned. LED-style glow is acceptable so long as the underlying hue stays in the desaturated psychedelic palette. Lean from traditional rave brightness — Tipper / Of The Trees / oxidized copper / bioluminescent deep-sea, not glowstick / candy-pop.
3. **Color palette expanded to the full desaturated psychedelic range.** Black + deep purple stay as the foundation. Mauves, magentas, slates, oxidized organics (sage / moss / patina), warm desaturateds (amber / rust / tobacco / brass / coral), mirror metallics (tarnished silver / oxidized copper / bronze patina / pewter), bone/ash highlights are all **first-class** alongside black + purple — no more rare/accent tier. ~30 named hex values catalogued in `WOBAR_TD_REFERENCE.md §4` and as vec3 block in `WOBAR_GLSL_PATTERNS.md`.

**Killed:** the per-act required/forbidden constraint table in `WOBAR_TD_AGENT_RULES.md`. Acts now have **emotional registers** (from `WOBAR_FRAMEWORK.md`) + **shared visual vocabulary** (`WOBAR_TD_REFERENCE.md §3`), but no enforceable rules. Identity emerges from music + brief, not a checklist.

**Pipeline change:** the old `HSV Adjust (saturationmult=0.15) → Level → Lookup → Ramp(purple)` pipeline that forced every visual to grayscale-then-tint-purple is **no longer the default.** Two options now:
- **Render in palette directly** (PBR materials in palette, GLSL using palette vec3s, instance colors in palette) → just grade with Level. Skip the satmult-to-grayscale step.
- **Lookup-route** (saturated source, archive footage) → keep `HSV satmult=0.15 → Lookup → Ramp` but the Ramp is drawn from the new swatch (Purple monochrome, Oxidized-rust, Slate-mauve, Patina, etc. — built per-scene).

**Files updated:**
- `reference/WOBAR_TD_AGENT_RULES.md` v2.0 → v3.0 (act constraint table deleted; new Visual Identity Lens, Color System, Materials and Surface, Act Identity sections)
- `reference/WOBAR_TD_REFERENCE.md` §3 (renamed "Visual Primitives — Vocabulary"; affinities not act-locks), §4 (full palette swatch + render-in-palette vs Lookup-route pipeline + per-act affinity suggestions), §6 (Mirror-Frame Processing Chain)
- `reference/WOBAR_GLSL_PATTERNS.md` v1.0 → v2.0 (Constraints preambles softened to Sensibility; vec3 palette block of 32 named colors; per-act affinities table replaces forbidden-column table)
- `reference/WOBAR_TD_INDEX.md` (pointer descriptions updated)
- `.claude/commands/td-build.md` (Step 5 changed from "Validate Against Act Constraints" → "Sense-Check Against Act Identity (Optional)" — note tension, don't auto-correct)

**What this changes for future builds:**
- New build sessions should reference `WOBAR_TD_REFERENCE.md §4` for the full swatch — not assume purple monochrome.
- Material decisions: gloss/metallic are on the table; consider whether the visual benefits from tarnished mirror, oxidized copper, polished glass, etc. — not just matte.
- Don't validate against required/forbidden tables (they're gone). Sense-check against the act's emotional register only — and only if the user asked for an act-specific build.
- Act 3 in particular: "no warm colors" is no longer a hard rule. Warmth not banned, but if used, it should disturb (oxidized copper, dried tobacco) — not relieve.
- Existing networks built under the old regime (Glass Orb + Motes, Ferrofluid Sphere, base_pop_sphere, base_act1_underwater, tunnel) are signed off and don't require retroactive review.

**No correction tracker entries** — this was a docs change, not a build correction.

---

### 2026-04-30 — POPX Library Survey — alphabetical walkthrough of all 55 official examples

**What was done:**
End-to-end alphabetical survey of every example in `touchdesigner/POPX_Examples_1_3_0/examples/` — `aim.toe` → `voxelize.toe` (55 files). For each: load, fix `parent.Loader` cascade errors (Reset / Resolutiony / fileinPOP.par.file all reference a parent COMP that doesn't exist when example is loaded standalone), screenshot the output, inspect the POPX module's non-default parameters, document new findings into `reference/td_library/TD_POPX_GUIDE.md`. Promoted from version 0.1 → 1.0 (status: complete).

**Final state of `TD_POPX_GUIDE.md` (2651 lines):**
- **Capability table — 65 mappings** of "without POPX → with POPX" recipes (Section: Why It Matters For WOBAR)
- **Module sections — ~30 modules** documented with full parameter pages, canonical patterns, WOBAR variants, cost notes, gotchas. New modules added in this run: Strange Attractor, Subdivider, Soft Body suite (cloth/struts/pressure/string variants), Spring Modifier (attribute mode), expanded Sweep (per-curve TOP modulation, custom cross-section input), Pivot, Convert, expanded Voxelize (4 numbered outputs).
- **Integration patterns (cumulative section)** — typography per-letter rig, living Voronoi, voxel-art, hair/strings on rigged characters, sweep-as-spectrogram, audio-reactive crystallization, etc.

**New POPX patterns confirmed (highlights):**
- **`Constrainttype='string'`** + **`Pintype='stopped'` + `Matchanimation=True`** — the recipe for hair/fur/fringe attached to moving rigged characters. Pinned points re-read source positions every frame; free ends simulate dynamically.
- **`Spring Modifier(Other=True, Attr='popxFalloff')`** chained into **`Transform POP(weightattr='popxFalloff')`** — gives PER-POINT lag with elastic ringing as a falloff source sweeps across geometry. Critical pattern: spring on the *attribute*, not the *transform*.
- **`Strange Attractor.Solvermode='advect'`** — every input point advected along a chaos-equation velocity field (Lorenz / Thomas / Aizawa / Halvorsen / Rossler / Chen). `Ua…Uf` coefficient slots are bindable to audio CHOPs for live shape-morph.
- **`Sweep` per-curve TOP modulation** — when input has N curves and `Scalepercurve=True` (also `Colorpercurve`, `Twistpercurve`), each curve reads its own row of the modulation TOP. Same TOP can drive scale + color + twist simultaneously. Recipe: 2D image / video / spectrogram → 3D stack of sweeps.
- **`Sweep(Surfaceshape='input')`** — custom cross-section profile via input[1] (any POP curve, not just primitives).
- **`Subdivider(Dofalloff=True)`** — recursive subdivide-and-extrude with falloff-masked region growth. Bass-reactive crystallization recipe: audio FFT TOP → Texture Falloff → Subdivider.
- **`Voxelize` has multiple numbered outputs** — `output[0]`=mesh, `output[1]`=density 3D-TOP, `output[2]`=SDF, **`output[3]`=voxel-center POP with `Inside` attribute**. Combined with `geometryCOMP.par.instanceactive='Inside'`, this is the canonical voxel-art / Minecraft-style rendering pipeline.
- **Typography per-letter rig** — `textSOP → soptoPOP → cleanup → Convert(Partitionmethod='connectivity') → Pivot(Mode='bbox', Alignmentside='ym') → Shape Falloff → Spring → Transform Modifier → Unpack`. Convert auto-detects letters; Pivot anchors to baseline; Spring gives elastic per-letter lag. Single source of truth for any wordmark animation.
- **Living Voronoi** — `pointgen → Relax(Solvermode='advect', Pointsupdatepop=feedback) → noisePOP(small drift) → null → Explode(Partitionmethod='voronoi', in1=relaxed-seeds)`. Self-feedback through null gives smooth seed diffusion; cells animate continuously.
- **Soft Body chained Constraints** — `Constraints(cloth) → Constraints(struts)` in series stacks constraint flavors; surface springs + internal volume preservation on the same body.
- **Soft Body `Enablegroundcollision=True`** — built-in infinite ground at `Groundposition*=(0,0,0)`. Cheaper than authoring a collider mesh + Constraints chain when one flat ground is enough.

**New TD/POPX-flavored patterns logged (not yet in correction tracker):**
- `parent.Loader` cascade errors — every POPX example loaded standalone has Reset/Resolutiony/fileinPOP.file expressions referencing a parent Loader COMP. Auto-fix: clear expressions, set to constants, substitute absolute asset paths from `assets/` folder.
- `geometryCOMP.par.instanceactive='<attrname>'` — built-in TD instance gating by per-point attribute. Voxelize writes `Inside` (1/0); instanceactive='Inside' renders only inside-the-mesh voxels. Useful beyond voxel-art (any culling-by-attribute).
- FBX import quirk — `running.fbx` in `soft body (strings).toe` did not render after re-pulse; importselectPOP error "Invalid geometry name" persisted across reload pulses. Likely needs full TD relaunch. Documented as a gotcha; architecture inferred from parameter inspection.
- Mac-specific: OptiX denoiser (`Path Tracer.Denoiser='optix'`) requires NVIDIA RTX hardware. Always `'svgf'` on Apple Silicon.
- Strings / hair architecture: pin points must be marked via `groupPOP(grname='pin', pattern='0 1')` BEFORE Constraints reads `Pinpoints='pin'`.
- Sweep `Skinops='group'` + `Inc=points-per-line` — required when many short polylines feed Sweep, otherwise Sweep tries to interpret all input as one giant polyline.

**Process notes for future POPX work:**
- The `TD_POPX_GUIDE.md` should be loaded by SECTION when consulted, not whole-file (2651 lines). The capability table (rows 23–90) is the entry point — find the recipe row, then jump to the named module's section.
- The "WOBAR Integration Patterns (cumulative)" section near the end (~line 2316) collects multi-module recipes; consult this BEFORE building from scratch.

**What agent got right first pass (this run):**
- Auto-fix function for the Loader cascade — applied uniformly across every example, no manual per-file fixing.
- Parameter-inspection-only documentation when visuals couldn't render (FBX import quirk in strings example).
- Maintained running capability-table count (final: 65 mappings) so future searches can grep for known patterns.
- Cross-referenced new modules against existing entries — Convert, Pivot, Voxelize, Explode all already had base docs from earlier examples; this run extended them with new modes/outputs rather than duplicating.

**What needed correction / iteration:**
- A few sweep-example aesthetic mechanisms (e.g. the 45 visible ribs on `sweep 1.toe`) were not fully explained even after parameter inspection — documented what was clear, left visual mechanism note for future inspection.

---

### 2026-04-27 — Glass Orb Motes — gravitational mote system inside refractive orb (Act 1)

**What was built:**
Long iterative build session inside `/project1/base_glass_orb/base_motes` — an N-body gravitational mote system rendered inside the existing glass orb shader. Three (final) emissive points orbit each other in 3D, refracted through the glass with chromatic aberration. Multi-stage Gaussian bloom for "ball of light" feel, depth-based dimming, hard cage confinement, periodic kick energy injection, audio reactivity (sub-bass → core brightness, energy² → gravity).

**Final architecture:**
- `pos_motes_callbacks` (textDAT, 290 lines): N-body Velocity Verlet sim with hard cage, spread thermostat, depth dimming, per-body color & pulse
- `pos_motes` (scriptCHOP) inputs[0]=time_src, [1]=ctrl_motes — outputs N samples × (tx,ty,tz,r,g,b)
- `time_src` (constantCHOP, value0.expr=absTime.seconds) — required to make scriptCHOP recook per frame
- `ctrl_motes` (constantCHOP, 14 channels): G, mass0/1/2, softening, restoring_k, damping, substeps, escape_r, pullback_k, min_dist, repulsion_k (no-op now), kick_strength, kick_interval
- `geo_motes` (geometryCOMP) → instances `sphere_template` via `instancetop=pos_motes`, color via `instancecolorop=pos_motes` r/g/b channels, `instancecolormode='replace'`
- `cam_motes` (perspective, FOV 75°, tz=2.0, ty expr=`(0.5-ctrl_orb.center_y)*5.45` so motes center matches orb center)
- `render_motes` (renderTOP, 720×1280, 16f, transparent bg)
- 3-stage Gaussian bloom chain: blur_inner(14, ps2)→level_inner / blur_motes(35, ps2)→level_bloom / blur_outer(50, ps4)→level_outer; Screen blend chained 2-input compositeTOPs (comp_b, comp_c)
- `null_motes_out` → `glsl_orb` input[2]
- `glsl_orb_pixel` shader patched to sample `sTD2DInputs[2]` at refracted UVs (uvR/uvG/uvB) and add to refractRGB inside the sphere — motes get true glass refraction + CA
- Scene also got: specular highlights removed (move_006), film grain layer added (`noise_grain → blur_grain → level_grain → comp_grain` between glsl_orb and null_out)
- Visual audio reactivity removed from orb (lvc_bg saturationmult, glsl_orb glow_energy) — replaced by motes-side audio reactivity

**Physics features (final state in callback):**
- Pairwise softened gravity (`F = G·m·dr / (|dr|²+ε²)^1.5`)
- Velocity Verlet integration, 4× sub-steps per frame
- HARD CAGE: position clamped to `escape_r`, radial velocity reflected with `bounce_e=0.98` restitution
- SPREAD THERMOSTAT: every 3s, measures cluster bounding radius from centroid; if < 0.10, pushes all bodies outward at 0.4 speed (replaces velocity-based thermostat which failed for "spinning tight ball" failure mode)
- Per-body deterministic kicks every kick_interval seconds with rotating direction (advancing 30°/kick, distributed 360°/N around bodies)
- Initial seed: Fibonacci-sphere positions at R=0.30, body-varying reference axis for tangent velocity at V_SPEED=1.2 (avoids ±Y pole zero-velocity bug)

**Visual features:**
- 3 distinct Act 1/2 cusp colors (warm gold / warm magenta / deep purple)
- Per-body breath pulse at different rates (0.10/0.16/0.22 Hz, ±15% modulation)
- Depth dimming (z-position → brightness, front 1.0 → back 0.55) for volumetric "in glass" feel
- Soft Gaussian volumetric balls (no hard disk edges) via screen-blended bloom chain
- Sphere source radius 0.022 with bloom expanding presence

**Audio reactivity (final):**
- `level_inner.brightness1` = `28 + max(0, sub_bass) * 10` (cores pulse on bass — Phase 1)
- `ctrl_motes.G` = `0.02 + pow(max(0, energy), 2.5) * 0.08` (gravity ramps on drops, power-curved so quiet sections stay calm — Phase 2)
- Phase 3 (transient → kicks) tried + reverted ("kicks too much")

**Move files in glass_orb/moves/:** 005 (motes added) → 013 (star bloom). Many subsequent tunings done without per-move JSON; final state captured in this log.

**What agent got right first pass:**
- Physics architecture (Verlet integration with substeps, softened gravity)
- Per-body color via instance r/g/b channels driven from scriptCHOP
- Refractive UV sampling pattern for motes inside glass shader
- Screen blend chain of 2-input composites for N-stage bloom (after compositeTOP-only-has-2-inputs failure)
- Fibonacci sphere distribution for N-body seeding

**What needed correction / iteration (key new patterns):**
- `geometryCOMP` auto-creates a default `torus1 (torusPOP, render=True)` child that renders as a giant blob — must explicitly destroy. (2nd occurrence in this session — added to tracker)
- `compositeTOP` only has 2 input slots; chain via 2-input composites for N inputs. (Tried 3-input; IndexError. Reverted, redid as chain.)
- `me.storage` inside scriptCHOP onCook = the DAT's storage, NOT the script CHOP. State went to callback DAT.storage; CHOP's own storage stayed empty. Confused debug for ~5 min.
- scriptCHOP needs time-dependent INPUT to recook per frame — `absTime.seconds` inside the callback alone doesn't establish dependency. Wired a `constantCHOP` with `value0.expr=absTime.seconds` into input[0].
- `pow(negative_float, 2.5)` returns complex → TypeError. Audio channels have tiny negative noise (~1e-22). Wrap with `max(0.0, ...)` before pow. (Spammed 20K stderr lines before catching.)
- Anisotropic blur (`filterscalex=8, size=90`) doesn't produce sharp diffraction-spike star flares — produces stretched gaussians that wash out invisibly AND tank fps. Star spikes need a custom GLSL star-filter shader (deferred).
- Velocity-based anti-collapse thermostat fails for clusters: bodies can have HIGH avg speed while clustered tight (spinning fast in a small ball). Replaced with SPREAD-based thermostat measuring cluster bounding radius from centroid.
- Fibonacci sphere seeding places bodies at ±Y poles where `cross(pos, Y_axis) = 0` → zero initial tangent velocity → those bodies fall straight inward and drag the system into collapse. Fixed with body-varying reference axis: `axis = (cos(i*1.3+0.5)*0.7, 0.6, sin(i*1.3+0.5)*0.7)`.

**Many iterations (paraphrased) that didn't make it:**
- Trail/feedback bloom (added move_013, then "blown out" / removed)
- Hard inter-body repulsion (Lennard-Jones 1/r^4) — was wrong fix to wrong problem; user wanted pass-through with system-level non-collapse
- Audio-triggered kicks via transient — too aggressive musically
- Brightness/sphere-size oscillations: blown-white → translucent → solid-but-blown → screen-blend solved it
- 3 motes → 5 motes → back to 3 (user preferred 3-body identity)

**New rules / patterns to consider promoting (added to correction tracker):**
- geometryCOMP auto-torus footgun (now 2nd occurrence — promotion candidate)
- compositeTOP 2-input limit
- me.storage scope inside scriptCHOP callbacks
- scriptCHOP per-frame cook requires time-dependent input
- pow() with negative-noise floats → complex → TypeError
- Velocity thermostat insufficient for cluster collapse — use spread-based
- Fibonacci pole-velocity bug

---

### 2026-04-21 — base_act1_underwater (Shallow Reef Particle Cloud)

**What was built:**
`/project1/base_act1_underwater` — Act 1 underwater particle cloud. Camera drifts forward through a 3D cloud of 1800 fine suspended particles (sediment/plankton scale). Layered on top: GLSL caustic patterns (6-wave sine interference + vertical surface light shafts), color graded through shallow-reef teal ramp, bloom, chromatic aberration, soft circle crop (underwater lens vignette).

**Direction:** shallow water, off the edge of a reef, volumetric suspended particles (POPs), scattered ambient light.

**Network architecture (final):**
- Audio: `sel_audio` (Select CHOP → /project1/base_audio/null_audio), `lfo_breath` (LFO CHOP, 1.1 Hz)
- Particles: `pos_fixed` (Script CHOP, static seeded random — 1800 pts, AUTOMATIC cook level) → `geo_particles` (Geometry COMP, instanceop=pos_fixed, instancetx/ty/tz='tx/ty/tz', instancesx/sy/sz='scale')
- 3-light ambient rig: `light_key` (point, ty=6, attenuated, dimmer=0.4), `light_ambient2`, `light_ambient3`
- Camera: `cam_main` (tx=0, ty=0, tz=0, tz.expr=`me.time.seconds * -0.07`, fov=65)
- Caustics: `glsl_caustics` (GLSL TOP) — 6-wave interference + surface light shafts. Uniforms: energy, lfo via `color0` pack (r=energy, g=lfo chan1, b=absTime.seconds * 0.15)
- Composite: `render_main → comp_particles (Screen: render + caustics) → level_grade → lkp_blue (Lookup → ramp_blue textDAT shallow-reef ramp) → blur_bloom → level_bloom → comp_bloom (Screen) → comp_surface/comp_surface1 → glsl_ca (chrom. aberration) → comp_crop (Inside: content + circle_crop) → null_out`
- Circle crop: `circle_crop` (Circle TOP, radiusx/y=0.90 fractionaspect, softness=0.45)
- Sphere size: radx=rady=radz=0.008 (fine sediment scale)

**Audio reactivity:**
- `level_grade.brightness1 = 1.0 + energy * 0.5`
- `level_bloom.opacity = 0.25 + energy * 0.35`
- `glsl_caustics` caustic brightness: `1.0 + energy * 0.8`
- `circle_crop.radiusx/y = 0.90 + sub_bass*0.06 + lfo*0.02`
- Chrom aberration strength: `0.006 + energy * 0.004`

**What agent got right first pass:**
- GLSL caustic shader architecture (6-wave interference + light shafts, power curve sharpening)
- 3-light ambient rig placement (no directional shadows, diffuse cloud lighting)
- Blue shallow-reef ramp table (7-stop, black → warm near-white)
- Chromatic aberration GLSL (radial UV split by energy)
- feedbackTOP pattern (black seed + par.top)
- Screen composite for bloom (additive without blowout)

**What needed correction / iteration:**
- `instancetop` set instead of `instanceop` → Geometry COMP showed only single point. Fix: `par.instanceop = chop`, clear `par.instancetop`. (2nd occurrence — correction tracker updated)
- Camera at tz=−94 (absTime.seconds=1429s × 0.07 = 100 units drift) → black render. Fix: cleared expr, set `me.time.seconds * -0.07`.
- Script CHOP `onCook` not firing: written to wrong-name DAT (`pos_fixed_cb`), then tried replacing whole DAT text — TD silently re-generated template over it. Fix: read existing auto-generated DAT (`pos_fixed_callbacks`), edit `onCook` in place via `text.replace()`. (New pattern — critical, added to tracker)
- poptoCHOP GPU→CPU download on 1800 pts: 6.7fps. `immediate`=4.2ms/cook stall, `nextframe`=3.3ms still expensive. Fix: bypass pop_plankton (`allowCooking=False`), use static Script CHOP positions.
- noiseCHOP with `par.channelname='chan1'` always returns 0 channels — root cause unknown. Workaround: animated drift handled by camera motion through static cloud (particles appear to drift from viewer's moving perspective).
- GLSL `iTime` undefined → shader compile error. Fix: pass time packed into `color0rgbb.expr = absTime.seconds * 0.15`.
- RampTOP `par.ramppoints` AttributeError. Fix: companion textDAT with pos/r/g/b/a rows, `par.dat = keys_dat`.
- Circle crop radius 0.90 in pixel mode ≈ invisible. Fix: `par.radiusunit = 'fractionaspect'`.
- Cross-COMP CHOP wiring (poptoCHOP inside pop_plankton → merge_instance in base_act1_underwater) fails. Fix: selectCHOP with absolute path.

**New patterns discovered:**
- Script CHOP callbacks are loaded from a companion auto-generated DAT named `{opname}_callbacks`. TD regenerates this template silently if you replace the whole text. Safe edit path: `op('name_callbacks').text.replace(old_func_body, new_func_body)` only.
- `me.time.seconds` vs `absTime.seconds` for camera drift: `absTime` accumulates across full TD session (hours of uptime = enormous drift). `me.time.seconds` resets with the COMP — always use this for camera motion expressions.
- poptoCHOP is not a viable path for 1000+ point instancing at 60fps on NC. GPU→CPU download is the bottleneck. Use Script CHOP static positions + bypass the POP system when instancing is the goal.
- Camera moving through a static particle cloud creates convincing apparent particle drift — no per-frame Python needed.
- GLSL uniform packing: `color0` parameter (r/g/b/a) is the simplest path to pass multiple float uniforms without `par.uniformnames` complexity. Pack energy/lfo/time into one vec4.

---

### 2026-04-21 — Ferrofluid Sphere (GPU POP + 3-Light Iridescent Rig)

**What was built:**
New visual at `/project1` — black oil ferrofluid sphere floating against a HDRI-lit backdrop plane. GPU POP system drives radial spike displacement; 3-light iridescent rig creates shifting multi-hue surface reflections. Bioluminescent glow ring on backdrop behind sphere. Feedback trail + pulsing glow for hypnotic movement. movie_out wired for export.

**Network architecture (final):**
- GPU POP chain: `spherePOP → noisePOP (combineop='translatealongnormal') → mathmixPOP → normalPOP → selectPOP` — radial spike displacement along point normals (no GLSL, no Script SOP needed)
- PBR material: `pbr1` (basecolor 0,0,0 black, metallic=0.95, roughness=0.02) — black oil surface
- 3-light iridescent rig: `light1` key (tx=2,ty=2,tz=2.5, dimmer=150), `light2` fill (tx=-2,ty=0.5,tz=1.5, dimmer=110), `light3` bioluminescent back-glow (tx=0,ty=0,tz=-2, dimmer pulsed ~0.8Hz via sin). All lights: 120° hue-offset sin wave expressions at 0.12 rad/s, attenuation enabled
- Backdrop: `geo_bg` (tz=-5) containing `grid_bg` (30×52, orient='xy') + `pbr_bg` (basecolor=0.45 gray, metallic=0, roughness=1.0). `environment1` dimmer=0.7
- Render: `render1` (720×1280, 60fps) with geo_sphere + geo_bg + cam_main + light1/2/3 + environment1
- Feedback trail: `seed_trail (black) → feedback_trail (par.top=null_trail) → xform_trail (sx=sy=0.997, rz=0.025°/frame) → level_trail (opacity=0.91) → comp_trail (over: render1 + level_trail) → null_trail`
- Bloom: `blur_bloom (box, 28px) → level_bloom (opacity=0.88) → comp_bloom (screen: null_trail + level_bloom) → null_out`
- movie_out: `null_out → movie_out (MJPEG, video-only — AAC blocked on NC license, mux audio post-render via FFmpeg)`

**Audio reactivity:**
No audio wiring in this build — visual is designed for export with manual energy. Light3 pulsing is LFO-driven (sin wave 0.8Hz), not audio-reactive. Audio can be layered in post or wired to noisePOP amplitude in a future session.

**What agent got right first pass:**
- `noisePOP.par.combineop = 'translatealongnormal'` for radial spike displacement (no GLSL required)
- `sphere1.par.normal = 'pointNormals'` as required prerequisite for translatealongnormal
- PBR black oil surface parameters (metallic=0.95, roughness=0.02)
- 3-light iridescent rig concept: 120° hue offsets on black PBR → different sphere regions catch different colors simultaneously
- feedbackTOP pattern: black seed + par.top (no direct wire)
- backdrop plane as grid_bg child inside geo_bg (Geometry COMP SOPs as children, not external)

**What needed correction / iteration:**
- `geo_water.inputConnectors[0].connect()` → IndexError: Geometry COMPs have NO external input connectors. SOPs must be children INSIDE the COMP. (New pattern — added to correction tracker)
- `op.setDisplayFlag(True)` → tdAttributeError: method doesn't exist. Use `op.display = True` / `op.render = True`. (New pattern)
- `glowTOP` → NameError: not a TD operator type. Already using blur+composite approach.
- `blurTOP` size=60 at 720×1280 → 78ms/cook, FPS 60→5. Fix: type='box', size=18. (CPU-lock pattern — added to tracker)
- Backdrop blown out at pbr_bg basecolor=1.0 + environment dimmer=0.85 — reduced to 0.45 gray + dimmer=0.7
- `comp_final` "not enough sources" after removing hdri_bg layer — simplified chain, removed comp_final, wired comp_bloom directly to null_out
- movie_out AAC error: "AAC not supported in this build" — Non-Commercial blocks ALL audio codecs. Fix: clear audiochop, export video-only, mux audio post-render with FFmpeg. (Added to tracker)
- `tdu.noise()` AttributeError (46k log entries from old `ferrofluid_callbacks` DAT) — `tdu` has no noise function. Use noisePOP / Noise SOP instead. (New pattern)

**New patterns discovered:**
- GPU POP `translatealongnormal` combineop + `pointNormals` on the SOP = native radial displacement. No GLSL shader or Script SOP needed for ferrofluid-style spikes.
- Point light positioned BETWEEN sphere and backdrop (tz=-2 with backdrop at tz=-5) creates centered glow on backdrop. Distance from backdrop controls glow diameter — closer to backdrop = tighter circle.
- Bioluminescent vs LED glow: reduce light color saturation range (0.08–0.50, not 0–1), cut base dimmer, increase bloom spread (box blur size=28, opacity=0.88) → soft diffuse halo reads organic, not projected.
- Non-Commercial blocks AAC but NOT MP3. Set `audiocodec = 'mp3'` (the default) — do not switch to 'aac' or it errors silently.

---

### 2026-04-18 — base_pop_sphere Act 3 Status Indicator Visual

**What was built:**
`/project1/base_pop_sphere` — particle sphere with per-sphere color cycling and radial audio waveform ring. Act 3 "system status indicator" aesthetic: green/amber/red per-sphere color driven by energy.

**Network architecture (final):**
- Script CHOP bridge: `pos_chop` reads `sphere_src` SOP points → tx/ty/tz/cr/cg/cb/sx/sy/sz per sphere
- Color: per-sphere phase offset from position hash + `absTime.seconds * CYCLE_SPEED` cycling green→amber→red. `CYCLE_SPEED = 0.006 + (energy^2.2) * 7.0` — near-frozen at breakdown, chaotic at drop
- Waveform ring: `mono_mix → sel_wave → chop_to_top_wave → glsl_wave (rgba8fixed)` → colored ring. `abs(audio)` for outward-only displacement. GLSL maps displacement magnitude to green/amber/red
- Feedback trail: `black_seed_trail → feedback_trail (par.top=null_trail) → xform_trail → level_trail → comp_trail2`
- Ghost aura: `xform_ghost → level_ghost → comp_ghost`
- Final: `null_out_final` → `movie_out` (MJPEG, 60fps, audio_in wired)

**What agent got right first pass:**
- Script CHOP color channel structure (cr/cg/cb already wired to geo_particles instancecolorop)
- HSV→RGB conversion in Python for full-spectrum color chaos
- Per-sphere phase offset via position hash for asynchronous cycling
- Power curve on energy for dramatic speed range
- `abs(audio)` fix for waveform X/Y drift

**What needed correction / iteration:**
- `glsl_wave` pixel format: default `useinput` inherits single-channel from CHOPtoTOP → grayscale output. Fix: `par.format = 'rgba8fixed'`
- `par.outputformat` doesn't exist on glslTOP — correct par name is `par.format`
- WAV duration via `wave` stdlib (ffprobe not available in TD sandbox, subprocess blocked)
- `CookLevel.EVERY_FRAME` doesn't exist — use `CookLevel.ALWAYS` (carried from prior session, confirmed again)

**New patterns:**
- glslTOP pixel format must be set explicitly when shader outputs color but input is single-channel
- `wave.open()` is the clean path for WAV duration inside TD Python (no ffprobe needed)
- Energy power curve 2.2 creates good "stays quiet, then explodes" behavior for speed parameters

---

### 2026-04-16 — base_act2_particles Descension Vortex (POP instancing build)

**What was built:**
New `/project1/base_act2_particles` — Act 2 torus-of-spheres vortex using TD 2025 POPs + Script CHOP bridge for instancing. 720-sphere torus rotating inward with feedback spiral trail.

**Network architecture (final):**
- POP chain: `torus_pts → noise_pts → attr_pts → null_pop` (for future use / POP-native features)
- SOP fallback for instancing: `torus_sop → noise_sop`
- Script CHOP bridge: `pos_chop` (scriptCHOP) reads `torus_sop.points` → outputs tx/ty/tz × 720 samples
- Geometry COMP: `geo_particles` (instancetop=pos_chop, instancetx/ty/tz='tx/ty/tz') + sphere template (radx=0.03) + constantMAT (Act 2 teal)
- Render: `render_main` (renderTOP, 720×1280) → `hsv_desat` → `level_main` → `comp_main`
- Feedback spiral: `feedback_main` (par.top=null_out, seed=black_seed) → `xform_spiral` (sx/sy=0.993, rz expression) → `level_trail` (opacity=0.82) → `comp_main` input[1]
- Color: `comp_main` → `lookup_act2` ← `ramp_act2` (Act 2 palette: dark 0.02/0.00/0.05 → teal 0.18/0.35/0.42 → bright 0.40/0.65/0.80) → `null_out`
- Audio expressions: xform rz = `absTime.seconds * 22 * (1 + sel_audio['bass'] * 2)`, noise amp driven by sub_bass, level brightness driven by energy, mat color driven by bass

**What agent got right first pass:**
- Overall architecture design (POP → SOP → Script CHOP → Geometry COMP instancing)
- Act 2 color palette and camera angle (overhead -78° for vortex portal look)
- feedbackTOP needs par.top only (no direct wire — that creates cook dependency loop)
- constantTOP uses `par.alpha` not `par.colora`
- Null-guard in Script CHOP callback prevents crash when torus_sop cooks before pos_chop

**What needed correction / iteration:**
- `instancepop` mode: set `geo.par.instancepop` + `instancepx='P.x'` → showed single dot at origin. POP attribute naming format for Geometry COMP is broken/undocumented. Pivoted to Script CHOP bridge.
- `instanceop` (SOP mode): also showed single dot even with correct 720-point SOP. Discovered `instanceop` is for DAT-driven instancing, not position-based SOP instancing.
- `popToCHOP` type string doesn't exist — no POP-to-CHOP bridge operator in TD 2025.
- Script CHOP: `op('../torus_sop')` returns None — in Script CHOP callbacks, `op()` resolves at parent scope, siblings accessed as `op('torus_sop')` (no `../` prefix).
- feedbackTOP wired directly to null_out → cook dependency loop on comp_main. Fix: black_seed constantTOP as wire input, par.top = null_out for the capture reference.
- transformTOP is 2D — no `par.sz`. Only sx/sy.
- MAT expressions inside geo_particles COMP: `op('../../sel_audio')` returns None. Must use absolute path `/project1/base_act2_particles/sel_audio`.
- hsvadjustTOP par is `saturationmult` not `satmult`.

**New patterns discovered:**
- **POP instancing via Geometry COMP is broken for both `instancepop` and `instanceop` modes.** The only working path for POP/SOP position-based instancing is: SOP positions → Script CHOP (tx/ty/tz channels) → Geometry COMP `instancetop` + `instancetx/ty/tz`. Log this as a known blocker.
- Script CHOP `op()` resolves in the parent COMP context, not the DAT's location — siblings are accessed without `../`.
- `feedbackTOP` must NOT be directly wired to its target TOP. Wire a seed (black constantTOP) as input[0]; set par.top = target path. Direct wire creates cook dependency loop.
- MAT expressions inside child COMPs require absolute `op()` paths — relative paths lose context.

---

### 2026-04-16 — base_act2_underwater Audio Tuning + Kick Response (moves 037–043)

**What was built:**
Audio reactivity tuning and kick response system for `/project1/base_act2_underwater` — Act 1/5 portal web visual.

**Audio analysis findings (rec_audio, 16400 samples from null_audio):**
- sub_bass: typical 0.05–0.15, peaks 0.81 — clear discrete kicks, mostly quiet
- energy: typical 0.005–0.02, peaks 0.87 — very dynamic, near-zero between hits
- growl: typical 0.13–0.20, peaks 1.0187 — CLIPPING (growl_max was 0.16, raised to 0.22)
- transient: typical 0.03, peaks 0.76

**Changes made:**
- `ctrl_norm.growl_max` 0.16 → 0.22 (fix clipping)
- `glsl_shimmer uBreathAmt` expression: pow(sub_bass,1.8)*0.9 → linear sub_bass*0.75 (gentle audio was crushed by power curve)
- `lvc brightness1`: energy*0.484 → energy*0.45 linear
- `blur_shimmer size`: growl-driven → sub_bass-driven (0px base, spikes to ~13px on kick)
- Portal triangle anchor: added base positions (0,0.28), (0.22,-0.22), (-0.22,-0.22) — portals were phase-locking bottom-left at low chaos. Lissajous amplitude cut 0.44/0.58 → 0.18/0.22
- Kick glow burst: blur_kick (70px gaussian from ramp_lookup) → lvc_kick (brightness1=sub_bass*1.5) → comp_kick (Add) → null_underwater_out
- movie_out wired (null_underwater_out, audio_in) → /Users/nicholasrabow/Desktop/wobar/renders/output.mov

**What agent got right first pass:**
- rec_audio analysis approach (read min/max/val from recordCHOP channels)
- Identifying power curve as the root cause of dead audio response at gentle values
- Linear modulation mapping design for Act 1/5 character
- Glow burst architecture (blur source image, scale by audio, Add composite)
- moviefileoutTOP audiochop → audio_in (not null_audio)

**What needed correction / iteration:**
- blur_shimmer base of 4px was double-blurring on top of GLSL's inherent softness — dropped to 0
- Portal bottom-left issue: Lissajous amplitudes up to ±0.58 caused phase-locking at low chaos. Solution: explicit triangle base positions + tight drift offsets
- Kick warp+spin shader change (move_038) was reverted — user wanted different type of movement (settled on blur smear instead)

**New patterns discovered:**
- At low chaos (driftMult=0.136), Lissajous drift barely moves but portals still visit their full amplitude range slowly — if phase offset lands them off-screen, they stay there for a long time. Anchor base positions + small drift offsets is more reliable for composition control.
- For gentle audio (Act 1/5), power curves above 1.2 effectively kill modulation. Record first with rec_audio, check typical values (not just peaks), then design curves to those typical values.
- Glow burst using the palette-mapped output as blur source keeps colors consistent — no color bleed from pre-grade signals.

---

### 2026-04-15 — act2_fractal Kaleidoscope Tunnel Refinement (no checkpoint)

**What was built:**
Continued refinement of `/project1/base_act2_fractal` — 2D polar kaleidoscope tunnel GLSL shader. Full session of iteration on visual quality, audio reactivity, and recording setup.

**Final shader state:**
- 6-fold kaleidoscope fold (float N, so morphable)
- Double-layer fbm domain warp (warp of a warp): `warpAmp = 0.06 + chaos * 0.22`
- Breathing scale: `sin(uTime * 0.22) * 0.04` applied to UV before warp
- Global clockwise rotation: `-uTime * (0.20 + chaos * 0.25)` before fold
- Chaos power curve: `pow(uChaos, 3.0)` — steep, keeps breakdown calm
- Sub_pressure power curve: `pow(uSubPressure, 2.5)` in scroll — suppresses breakdown rumble
- Color cycling: 3 independent oscillators (c1=0.018, c2=0.031, c3=0.052 rad/s), each layer gets own hue angle, constrained to ±0.4 rad max — stays purple/indigo/violet family
- Three ring layers + fold edge + center void + depth fog + vignette + film grain

**Signal chain:** `fractal_glsl → bloom_blur + bloom_comp → lvc → hsv_desat → null_out → rec_out`

**Recording setup added:**
- `rec_out` (moviefileoutTOP): h264nvgpu, yuv420, 10000 Kb/s, 30fps, unique suffix on
- Connected to `null_out` for video, `audio_in` for audio (44100 Hz)
- Output: `~/Desktop/wobar/renders/act2_fractal.mov`

**Tried and rejected this session:**
- Mirror cascade (second nested fold) — too mandala/geometric, lost tunnel feel
- Orange palette — went black through HSV desat chain (warm low-luminance colors don't survive desaturation)
- Full ±1.8 rad hue cycling — went full spectrum (green/yellow/cyan), not on brand
- uPower LFO — morphing fold count was disorienting, not hypnotic

**What agent got right first pass:**
- Domain warp structure (double fbm, warp of a warp)
- Breathing scale placement (before warp, on UV)
- Color cycling constraining with `sin * 0.4` range
- Chaos power curve logic
- rec_out wiring and codec parameters

**What needed correction:**
- `null_audio` is analysis CHOP at rate 30 (not audio waveform) — audiochop for recording must point to `audio_in` (44100 Hz stereo), not `null_audio`. Pointed there initially, got "sample rate must be 44100" error.
- Orange colors went black: muted orange (R~0.18, B~0.01) has low luminance that HSV desaturation kills entirely. Warm low-saturation colors need much higher RGB values to survive the desat chain.
- Full-spectrum hue rotation (±1.8 rad) reads as rave/LED — too broad. ±0.4 max keeps it brand-appropriate.

**New patterns discovered:**
- Power curve on audio inputs in GLSL suppresses breakdown noise better than Lag CHOP alone. `pow(x, 2.5–3.0)` flattens small values (breakdown rumble) while passing large values (drop) through cleanly.
- HSV desat kills warm low-luminance colors — test any new palette through the full chain before committing. Purple works because the B channel carries enough luminance after hue rotation.
- Three independent color oscillators at slightly different rates (0.018/0.031/0.052 rad/s) create perpetual non-repeating color variation within a constrained palette — better than a single cycle.
- `moviefileoutTOP` audiochop must be the raw audio stream (audiofileinCHOP or equivalent at 44100), not a downstream analysis CHOP.

---

### 2026-04-15 — base_audio Full Build + Tuning (base_audio v001)

**What was built:**
Complete rebuild and tuning of `/project1/base_audio` — 8-channel dubstep/psychedelic bass audio pipeline tuned to mur.wav.

**Final channel set (null_audio output):**
- `sub_bass` — 50Hz BP → RMS → lag (0.05/0.30s) → normalize, sqrt compress
- `bass` — 150Hz BP → RMS → lag (0.005/0.15s) → normalize
- `mid` — 1kHz BP → RMS → lag (0.002/0.08s) → normalize
- `high` — 4kHz HP → RMS → lag (0.001/0.05s) → normalize
- `energy` — weighted band sum (0.55 sub + 0.35 bass + 0.07 mid + 0.03 high) → lag (0.01/5.0s) → normalize
- `sub_pressure` — 50Hz BP → RMS → slow lag (0.1/1.0s), direct (no math_remap)
- `growl` — 180Hz BP → RMS → lag (0.003/0.12s) → normalize (growl_max=0.16)
- `transient` — filterCHOP edge on energy_lag → normalize (fromrange2=0.30, sqrt compress)

**Tuned ctrl_ values (from mur.wav full-song recording):**
- `ctrl_norm`: band_max=0.32, energy_max=0.135, growl_max=0.16
- `ctrl_smooth`: smooth_up=0.04, smooth_down=0.08 (scope: sub_bass bass mid high growl only)
- `smooth_out` inserted between final_merge and null_audio

**Architecture extras:**
- `rec_audio` (recordCHOP) tapped from null_audio for future full-song analysis
- Network organized left-to-right with 16 annotateCOMP labels

**Kick detection — tried and removed:**
- Attempt 1: HP 2kHz click transient — failed (sub bass masks all click content)
- Attempt 2: sub_bass onset detection (filterCHOP edge on sub_rms) — technically worked but removed by design choice
- Final decision: no kick channel. Organic continuous signals (sub_bass, growl, energy, transient) suit the genre better than impulse triggers

**What agent got right first pass:**
- audiofilterCHOP/analyzeCHOP/lagCHOP architecture for all band chains
- Energy calculation (weighted sum → slow lag) correct on first attempt
- smooth_out Lag CHOP with scope parameter for selective smoothing
- annotateCOMP creation and parameter names (Titletext, Backcolorr/g/b/alpha, layerzone)
- rec_audio recordCHOP + Python analysis workflow for data-driven tuning

**What needed correction:**
- `annotateCOMP` nodeY is the BOTTOM edge, not the top — initial positions all shifted one height upward. Corrected by computing bounding boxes from actual node positions.
- `analyzeCHOP function='average'` produces zero on HP filter output (bipolar signal cancels). HP filters need `function='rmspower'`. BP filters with `average` work because they produce a meaningful envelope.
- `triggerCHOP` parameter expressions (`par.threshup.expr`) evaluated to 0.0 despite ctrl_kick channel having correct value. Safer to use `ParMode.CONSTANT` with hardcoded values for triggerCHOP parameters.
- `td_read_chop` on a 6315-sample × 9-channel recording exceeds token limit — analyze inside TD via `td_execute_python` instead.
- Python helper functions defined in `td_execute_python` don't see script-level `op()` variables — confirmed again (already in log). All `op()` calls must be inside the function body.
- List comprehensions in `td_execute_python` can't reference outer-scope variables — use explicit for loops or wrap everything in a function.

**New patterns discovered:**
- `annotateCOMP` is the correct TD type for network annotation boxes (not `annotationCOMP`, `commentCOMP`, `networkBox`). Key pars: `Titletext`, `Backcolorr/g/b/alpha`, `layerzone='belowgrid'`, `nodeWidth`, `nodeHeight`. nodeY = bottom edge.
- Full-song analysis workflow: recordCHOP (tap from null_audio) → record during song → `list(ch.vals)` + `sorted()` for percentile analysis inside `td_execute_python`. Use p95 as normalization target (not max — too sensitive to outliers).
- Kick detection in dubstep: HP click approach never works. Sub_bass onset (filterCHOP edge on sub_rms) technically functions but design choice may favor removing kick entirely for organic feel.
- Single `band_max` in math_remap can't equalize both sub_bass and high — sub_bass (50Hz) is ~8x louder than high (4kHz HP) in this genre. If per-channel normalization needed, build separate math_remap per band.
- `pane.showParameters = False` hides the parameter panel from code. `pane.homeSelected(zoom=True)` zooms to fit selection.

---

### 2026-04-12 — Act 2 Underwater Visual (Sessions 1–2 combined)

**What was built:**
`/project1/base_act2` — full underwater-looking-up visual stack.

Signal chain: `ring_src` (GLSL 3-arm Archimedean spiral) → feedback loop (`comp` ← `lv` ← `tr`) → `null_out` → `warp` → `hsv` → `lvc` → `lkp`/`ramp` → `null_final` → `zoom_out` → `lv_crush` → `null_black` → caustic layer (`caustic_glsl` → `caustic_lv` → `comp_caustic` → `null_caustic_out`) → surface glow (`ramp_surface` → `lv_surface` → `comp_surface` → `null_surface_out`).

**Key parameters:**
- Spiral: 3 arms, spacing=0.072, hue 0.50–0.67, shader sat mix 0.15, brightness 0.036
- Feedback: opacity 0.982, rotation 38°/frame (constant), zoom sx=sy=0.966+0.005*sin(t*0.18)
- Zoom out: 3.5x (inside the spiral, fills frame)
- lvc: brightness 1.20, gamma 0.80, contrast 1.65
- HSV: hueoffset 0.0, satmult 0.75
- lv_crush: blacklevel 0.03, contrast 1.30
- Caustic: 3-layer Voronoi Worley edges, animated at 0.30/0.22/0.18 speed, screen-blended opacity 0.50
- Surface glow: radial ramp (pale cyan-white center → black), screen-blended at brightness 0.55

**What agent got right first pass:**
- Feedback loop architecture correct
- GLSL caustic shader built clean, no shader errors
- Screen blend composite wiring for additive layers
- Time uniform setup matched ring_src pattern exactly

**What needed correction:**
- `lvc.par.contrast1` does not exist — correct par name is `lvc.par.contrast`
- rampTOP keys: initial values too dark at mids, had to iterate brightness up
- Color shift from purple to water: required 3 iterations (purple → blue → too neon → dialed back saturation + ramp)
- Early in session: `contrast1` typo on levelTOP — par is `contrast` not `contrast1`

**New patterns discovered:**
- levelTOP contrast par: `par.contrast` (not `par.contrast1`)
- For "transparent water" color: shader internal desaturation mix 0.15 (very low) + HSV satmult 0.75 + desaturated ramp = correct read
- Wide wave crest spacing: increase GLSL `spacing` from 0.042 to 0.072+
- Caustic chain should be fully isolated (new nodes only) so it can be bypassed/removed independently

---

### 2026-04-14 — Tunnel Audio Reactivity + base_audio Build

**What was built:**

`/project1/base_audio` — Full audio analysis pipeline from scratch.
- `mono_mix` (Math CHOP, stereo→mono) → 4 `audiofilterCHOP` branches → `analyzeCHOP` (RMS) → `lagCHOP` per band → `merge_bands` → `rename_bands` → `math_remap` → `null_audio`
- Bands: sub (50Hz BP, lag 0.05/0.30), bass (150Hz BP, lag 0.005/0.15), mid (1kHz BP, lag 0.002/0.08), high (4kHz HP, lag 0.001/0.05)
- Beat/kick branch: `beat_filt` (90Hz BP) → `beat_rms` → `kick_logic` → `kick_trigger`
- Energy channel: weighted sum (0.55 sub + 0.35 bass + 0.07 mid + 0.03 high) → `energy_lag` (up=0.05, down=2.5s) → `e_norm` (remaps 0→0.18 to 0→1, peak ~0.18 at max) → merged into `null_audio` as 5th channel
- `audio_out` (Audio Device Out CHOP) for monitoring

`/project1/tunnel` — Full audio reactivity layer.
- `sel_audio` Select CHOP reading all 5 channels from `base_audio/null_audio`
- `sel_kick` Select CHOP reading `kick_trigger`
- `ctrl_audio_live` CHOP pipeline: `energy_scale` (energy × Intensity) → per-band multiply by energy → rename to `sub_e, bass_e, mid_e, high_e` → merge with `energy` + `kick_lag` → `ctrl_audio_live` null
- `kick_lag`: lag1=0.001, lag2=0.3 (instant attack, 300ms decay envelope)
- `Intensity` parameter on `ctrl_master` (Motion page) — manual ceiling 0–1
- All visual expressions rewritten to read from `ctrl_audio_live` (max 2 CHOP lookups per expression)

**Expression architecture (final):**
- `fb_tr.sx/sy`: `1.0 - (1.0-Zoom)*energy - bass_e*0.06`
- `fb_tr.rz`: `(Rotate + sub_e*2.5) * energy`
- `fb_lv.opacity`: `0.82 + 0.15*energy + sub_e*0.02`
- `lvc.contrast`: `1.0 + (Contrast-1.0)*energy + mid_e*1.0`
- `glow_blur.size`: `Glowsize*energy + bass_e*25`
- `chrom_ab.vec0valuex`: `Caamount*energy + high_e*0.04`
- `displace.displaceweightx/y`: `(Dispamt + sub_e*0.15) * energy`

**Network layout:** cleaned left-to-right. Source → feedback loop → post-process → output. Control cluster (ctrl_master, sel_audio) top-right.

**What agent got right first pass:**
- audiofilterCHOP parameter names (filter, units, cutofffrequency, resonance)
- Energy envelope concept (slow release lag) correctly tracks breakdown/drop dynamic
- Normalization step catching the 0→0.18 peak range
- `ctrl_audio_live` pre-compute architecture for performance

**What needed correction:**
- `filterCHOP` used first — wrong operator. Should be `audiofilterCHOP` for frequency filtering
- `lagCHOP` par names: `lag1`/`lag2` not `lagup`/`lagdown`
- `mathCHOP` range pars: `fromrange1/2`, `torange1/2` not `from1/2`, `to1/2`
- `constantCHOP` pars: `const0name`/`const0value` not `value0name`/`value0`
- `par.val = 0` before expression mode poisons the read cache — just set expr + mode, don't touch val
- Cook loop caused by inserting `e_norm` in wrong position in energy chain (between lag and rename instead of after lag before final_merge)
- COMP custom par with CHOP expression had cook ordering errors in TOP context — fixed by reading CHOP directly in TOP expressions
- `playmode='locked'` caused only 10s of audio — switched to `sequential`
- `audiodeviceoutCHOP` with `cookalways=True` froze TD — removed that flag
- Python helper functions in execute_python don't inherit script-level globals — all op() refs must be inline

**New patterns discovered:**
- For audio frequency filtering: `audiofilterCHOP` (not `filterCHOP`). Par: `par.filter='bandpass'`, `par.units='frequency'`, `par.cutofffrequency`, `par.resonance`
- Stereo audio must be collapsed to mono before `analyzeCHOP` — use `mathCHOP` with `chanop='add'`, `gain=0.5`
- Energy envelope: weighted band sum + asymmetric lag (fast attack 0.05s, slow release 2.5s) is the correct pattern for energy tracking
- Peak energy from this band weighting hits ~0.18 — normalize with `mathCHOP fromrange2=0.18` + `postop='clamp'`
- Pre-compute `band × energy` in CHOP domain (`ctrl_audio_live`) — keep TOP parameter expressions to max 2 CHOP lookups. More than ~4 lookups across 8+ expressions causes FPS crash at 60fps
- `par.eval()` forces expression evaluation — `par.val` returns cached value, unreliable for verification
- Kick detection: `audiofilterCHOP` (90Hz BP) → `analyzeCHOP` (RMS) → `logicCHOP` (convert='bound', boundmin=0.25) → `triggerCHOP`. Add `lagCHOP` (0.001/0.3s) downstream in the visual network for envelope shaping
- Cook loop indicator: 🔴 STOP in footer. When triggered, disconnect the offending input immediately before any other action
