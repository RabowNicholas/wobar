---
title: TouchDesigner Build Log
version: 1.0
last_updated: 2026-05-01
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
| Audio analysis CHOP `energy` channel returns tiny negative values (~e-22) at silence — `energy ** non_integer_exp` raises 'float() argument must be a string or a real number' (returns complex). ALWAYS wrap as `max(0.0, energy) ** exp` in audio-driven expressions | **2** | **✅ PROMOTED** |
| `geometryCOMP.par.instancesx/y/z` accept BARE attribute names ONLY (`'ScaleRand'`) — NOT expressions (`'LenVel*0.6'`). For composite math, write the result to a new attribute via `mathmixPOP` (comb0oper='mult', comb0scopea/b, comb0result='OutAttr') and read OutAttr as the bare instance scale | 1 | No |
| POPX SA `Pointsupdatepop` feedback loop: custom attributes written upstream of SA (e.g. `randomPOP outputattrscope='ColorU'` before sa1) are STRIPPED at SA's output. Only solver-managed attrs (P, PartVel, N, Color, LenVel) pass through. Write per-particle attrs DOWNSTREAM of SA, before geometryCOMP.instanceop chain | 1 | No |
| `nullPOP.points('Color')` returns a list of TUPLES per point (4-comp Color = list of 4-tuples). `nullPOP.points('LenVel')` returns list of FLOATS. Don't index as `arr[i*4+k]` for color — that yields a tuple. Iterate as `pt = arr[i]; pt[component]` | 1 | No |
| `renderTOP.par.geometry` is a glob PATTERN, not a SOP/COMP path. `'geo_attractor'` matches that COMP only. `'geo*'` matches all geo-prefixed. `'* ^geo_aura'` includes all except geo_aura. Setting full path (`/project1/geo_attractor`) silently fails to default-include-everything | 1 | No |
| Aizawa (and other chaotic) attractor's instantaneous mass-center is NOT temporally stationary — particle distribution cycles around the manifold over 30-60s. Hardcoded `cam.lookat = static_null` drifts off-center over time. Solution: `executeDAT.onFrameStart` reads `null_pop_out.points('P')`, computes mean × geo.scale, EMA-lerps lookat target tx/ty/tz at alpha=0.04 (~0.4s lag time-constant — feels cinematic, not jitter) | 1 | No |
| `compositeTOP operand='over'` with input0 + input1: input1 is the TOP layer (composited OVER input0). For form-on-bg with form's render bgcolor=(0,0,0,0), simpler mental model: use `operand='add'` instead — non-form pixels (RGB=0) add nothing to bg, form pixels (RGB>0) light up bg | 1 | No |
| TD `non-realtime mode` (export mode) renders every frame without skipping — good for video export but causes audio playback clicks because `audiodevout` can't keep pace with cooked-frame rate. Switch back to realtime for live audio reactivity tuning | 1 | No |
| **TD `geometryCOMP` instancing rejects POPX-derived POPs that carry rich attribute sets** (PartVel, PartId, PartForce, PrevP, Density, etc.). Error: "Manual number of instances not supported when using a POP with point co[lor]" — even after stripping Color via `attributePOP.par.deletepoint='Color'`. Workaround: instance from native particlePOP (clean attrs) OR from POPX modules with simple POP outputs (SA works because P/PartVel/N/LenVel only) | **3** | **✅ PROMOTED** |
| **`oplength` instance count mode reads `1` from POPX module nullPOP outputs** even when `numPoints()` returns thousands. TD geo COMP can't introspect POPX-derived POPs for instance count. Workaround: `instancecountmode='manual'` + `numinstances.expr = "op('/path/to/null').numPoints()"`. Native particlePOPs hit this same bug — manual mode required for both | **2** | **✅ PROMOTED** |
| **`scriptTOP` with `CookLevel.ALWAYS` doing per-frame numpy operations on stream inputs crashes TD repeatedly** (locked up MCP server twice in one session). Even `CookLevel.ON_CHANGE` is dangerous if the input changes every frame (like a particle stream). Avoid scriptTOP for high-frequency numpy ops on streaming POP/CHOP data | **2** | **✅ PROMOTED** |
| POPX `Particle` (Fluids-PBF) with `Enablebboxcollision=True` + `Usecustombounds=True` does NOT actually contain particles at default `Substeps=1`. Particles tunnel through bbox at gravity scale, falling to y=-167 within seconds. May need higher Substeps + Iterations OR alternate constraint mechanism (collisontop SDF) | 1 | No |
| POPX `physarum.Constraintvolume` is a **TOP**, not a SOP/POP. Bright pixels = allowed growth, dark = blocked. Wiring a sphereSOP causes GLSL compile errors in physarum's internal `3d/distance` shader. For 3D simulation true sphere-shell constraint requires a 3D texture (3D SDF); for 2D simulation a circle TOP works directly | 1 | No |
| POPX `DLA` requires a **seed POP wired to input[0]** for aggregation to start. Without seed, walkers wander but never aggregate (output[0] still emits 5000+ random walkers). With seed, output[0] = aggregated tree, output[1] = lines (parent-child), output[2] = random walkers | 1 | No |
| `circleSOP` parameter is `divs`, NOT `divisions`. Tripped at every assumed name | 1 | No |
| `sweepSOP` output through `geometryCOMP` → `renderTOP` produces nothing visible despite render flags set on the inSOP — even when sweep has 12-24k points and constantMAT is assigned. Mechanism unclear; likely related to the same POP-attribute incompatibility that blocks instancing | 1 | No |
| **POPX attribute screening — the de-risk method for any new POPX module.** Place a copy from `/POPX_1_3_0/custom_operators/<name>`, wire minimum inputs, Init→Start→Play, then `print([a.name for a in op('<mod>/POPX_out1').pointAttributes])`. **Safe (clean attrs):** SA, magnetize. **Unsafe (rich attrs):** DLA (`iNumChildren, Parent, Seed, Rand`), Particle (`PartId, PartForce, PrevP, Density, ...`17 attrs), DLG (line topology, `Parent, Seed`). Unsafe modules will trip `geometryCOMP` instancing wall ("Manual number of instances not supported with point co[lor]") — pivot to TOP-output modules (Flow, physarum, Voxelize) or decoupled architecture (POPX provides force field, native particlePOP holds clean attrs) | **2** | **✅ PROMOTED** |
| **wireframeSOP output cannot be instanced via geometryCOMP directly** — only 1 instance renders even when numinstances reads correctly (e.g. 80). The wireframe topology (line-derived extruded thin tubes) breaks instancing. **Fix:** insert a `convertSOP` with `totype='poly'` AFTER the wireframeSOP, render the convertSOP output instead. The polygonization normalizes topology so geo COMP can multiply instances. Pattern: `boxSOP (render=False) → wireframeSOP (radius=X) → convertSOP totype='poly' (render=True) → instanced` | 1 | No |
| **TD has no native chromatic-aberration TOP.** `lensdistortTOP` is geometric distortion only (k1/k2/k3 coefficients, no RGB split). Manual CA chain: 3 `levelTOP`s to isolate channels (red: `highg=highb=0`, green: `highr=highb=0`, blue: `highr=highg=0`), 2 `transformTOP`s to offset R and B opposite directions (G stays center), 2 `compositeTOP add` blends to recompose. ~7 ops total | 1 | No |
| **feedbackTOP requires BOTH `par.top` set AND target wired to `input[0]`** per TD's SHOT note. The "cook dependency loop detected" warning that appears is visible in the network but does NOT actually block cooking — feedback works at 60fps. Black-seed-only on input[0] without target wire produces "Not enough sources" error. Both required | 1 | No |
| **hsvadjustTOP hue rotation has no effect on pure white (or pure black).** `hueoffset` only shifts saturated colors. Pure white (R=G=B=1, saturation=0) stays white regardless of hueoffset value. To use hue rotation on a "white" wireframe visual: tint the constant material slightly first (e.g. electric cyan 0.2/0.7/1.0), then hue rotation cycles through spectrum | 1 | No |
| **Sawtooth scale pulses have visible snap-back.** Expression `baseline + (t*rate) % range` gives continuous outward growth but the boundary snap (max → min) is jarringly visible to viewers. Use smooth sin instead: `baseline + amp * sin(t * 2π / period)` for hypnotic breathing. Trade-off: alternates "coming toward / going away" instead of continuous outward, but no discontinuity | 1 | No |
| **Inside-POV camera setup for immersive POV:** `Camradius=0.1, Camfov=80, Camelev=0` puts camera at center of particle cloud (≤0.5 unit cluster) with wide-angle perspective; particles surround camera, geometry passes through frame as scale-pulse animation breathes. Default ctrl_master `Camradius.min` clamp at 0.5 blocks this — must lower to 0 to allow inside-POV configs | 1 | No |
| **compositeTOP `over` input order is empirically opaque.** Entry 69 says input1 = top layer with swaporder=False, but this session observed input 0 effectively on top with swaporder=False (black mask circle on input 1 was BENEATH the iris on input 0 — bright crescents leaking through for hours of debugging until swaporder=True flipped it). Verdict: verify empirically each use; if mask isn't covering, toggle swaporder | 1 | No |
| **circleTOP `centerx/y` with `centerunit=fraction` is an OFFSET from the justify-anchor, NOT an absolute position.** With default `justifyh/v=center`, `centerx=0, centery=0` puts the circle at frame center. Setting `0.5, 0.5` shifts the circle by half-resolution in each axis (lands in upper-right corner). Same applies to `pixels` mode — center coords are offsets from the justify anchor. Default is 0,0 — leave alone unless deliberately offsetting | 1 | No |
| **circleTOP `radiusunit=fraction` is ANISOTROPIC on non-square frames.** `radiusx` is fraction of width, `radiusy` is fraction of height. On 720×1280, the same numeric value yields a tall oval (e.g. 0.3 → 216px×384px). Use `fractionaspect` (default) or `pixels` for a true circle. `fraction` is for when you want axis-independent scaling | 1 | No |
| **circleTOP `premultrgbbyalpha=True` (default) can make small or partially transparent circles invisible in `over` composites.** Tested: 200px white circle dead-center + premult=True + composite over iris = visible. 22px-50px white circles or alpha < 1 + premult=True = invisible despite standalone render showing the circle correctly. Setting `premultrgbbyalpha=False` makes them composite as expected. Worth defaulting to False for circles used as composite layers | 1 | No |
| **TD param expressions use the `math` module — bare `sin()`/`cos()`/`pi` are NOT in the expression namespace.** Common pattern for time-driven oscillation: `<base> + <amp> * math.sin(absTime.seconds * 2 * math.pi * <freq_hz>)`. Bare `sin()` raises `NameError: name 'sin' is not defined` | 1 | No |
| **`noiseTOP.par.type='randomgpu'` outputs centered at 0.5 (mid-gray), not 0.** Causes the noise to be the IDENTITY for `overlay` blend (overlay against mid-gray = no change). To use randomgpu as TV-static-style ADD overlay: set `par.amp = 2*range`, `par.offset = -range` to recenter to ±range, then composite with `add` blend. Or switch to `simplex2d` (centered at 0 by default) for overlay-blend use cases. | 1 | No |
| **`mathCHOP.par.chanop` (combine channels within an input) vs `par.chopop` (combine multiple inputs).** Confusingly named. `chopop=average` averages multiple inputs together but keeps original channel count. `chanop=average` averages channels within a single input, collapsing N→1. For stereo→mono on a single input, use `chanop=average` and `chopop=off`. | 1 | No |
| **`levelTOP.par.opacity` only modulates ALPHA — does NOT modulate RGB.** When fading out under `max` blend (which only looks at RGB), opacity has no visible effect. To fade RGB in/out for max-blend chains, use `par.outhigh` (output range max) — set to a value 0-1 to scale RGB output by that amount. Pattern for energy-scaled fade: `outhigh.expr = 'op("ctrl").par.SomeAmp * op("ctrl").par.Energy'`. | 1 | No |
| **`feedbackTOP` cook-dependency-loop warning is NOT cosmetic — it CAN block cooking.** Symptoms: feedback chain ops report 128×128 resolution despite explicit custom resolution; warnings persist. Fix: wire `input[0]` to FRESH CONTENT upstream of the loop (e.g. the lookup feeding the comp), use `par.top = comp` for the loop reference. Then pulse `feedbackTOP.par.resetpulse` once to apply the configured resolution. The earlier rule (entry 82) saying "wire target to input[0]" creates the circular reference that triggers this — the corrected pattern is upstream-content as input[0], target as par.top. | 1 | No |
| **For `transformTOP` to fit a portrait source (720×1280) into a square output (720×720) WITHOUT squishing, use a TWO-STAGE pre-crop:** stage 1 — transformTOP with output 720×720, `sx=1, sy=source_aspect (1.778 for 9:16)` to render full source height extending beyond canvas (auto-cropped at top/bottom by `extend=zero`). Stage 2 — second transformTOP scales/positions the now-square content into final layout. Single-stage with custom sx/sy in the position transform doesn't preserve aspect because content extending beyond cell bounds bleeds into adjacent cells. | 1 | No |
| **`selectCHOP` with `par.channames` selects channels by NAME PATTERN (not index).** For first channel of unknown stereo audio, use `par.channames='chan1'` (the conventional channel name from audiofileinCHOP). Patterns like `'*[0]'` (index syntax) don't work. | 1 | No |
| **mathCHOP `chopop` (inter-CHOP per-channel math) vs `chanop` (intra-CHOP collapse) — easy to confuse, breaks SILENTLY.** When you wire two same-shape CHOPs into a mathCHOP and want per-channel multiply (e.g. `iris × scale_per_band`), set `chopop='mul'`. Setting `chanop='mul'` instead does intra-CHOP combine and produces wrong/empty output with no visible error — the chain just outputs scale constants directly. Already in tracker as entry 92, but bumping count. | **2** | **✅ PROMOTED** |
| **Cross-COMP CHOP wiring fails silently — the `outputConnectors[0].connect()` call from inside a COMP to outside it APPEARS to succeed but the connection list reads empty afterward.** Workaround: use `selectCHOP` with absolute path (`par.chop='/project1/comp/inner_chop'`). Already entry 55; bumping count. | **2** | **✅ PROMOTED** |
| **`null_audio` (analysis-chain output, 60Hz timeslice rate) is NOT 44100Hz, blocks moviefileoutTOP audio export with "Audio CHOP sample rate must be 44100" error.** Workaround: wire `record_out.par.audiochop` to `audio_master/audio_in` (raw 44100Hz stereo) instead of any analysis-chain CHOP. Already entry 32; bumping count. | **3** | **✅ PROMOTED** |
| **TD `td_execute_python` exec environment scoping is fragile — list comprehensions, generator expressions, AND nested function definitions all fail to capture outer-scope names with `NameError: name 'X' is not defined`.** Already entry 45 for list comprehensions; same failure mode for nested defs (`def fn(): use_outer_var`). Workaround: explicit for-loops, capture references locally inside the function body. | **2** | **✅ PROMOTED** |
| **`bloomTOP` is the canonical HDR-feel post — `output='inputplusbloom'` adds the bloom result back onto the source.** Settings for "luminous painterly" register: `bloomthreshold=0.4-0.55` (lower = more pixels glow), `bloomintensity=0.7-1.1`, `maxbloomradius=0.15-0.25`, `bloomscurve=0.7-0.85` (punchier shape), `pregamma=1.0-1.1` (boost mids before bloom). Combine with crushed-blacks levelTOP (`inlow=0.05`, `inhigh=0.92`, `gamma1=0.92`, `contrast=1.18`) for the "burning embers" cusp 4→5 look. | 1 | No |
| **Phase-animated palette lookup pattern for cyclic color shifts:** `palette_keys` (tableDAT, horizontal stops) → `palette_ramp` (rampTOP type='horizontal', 256×1) → `xform_palette_phase` (transformTOP, `tx.expr=phase % 1.0`, `extend='repeat'`) → `lookup_color` (lookupTOP). Phase comes from `chop_color_speed` (constantCHOP, value = audio-driven cycle rate) → `chop_color_phase` (speedCHOP, integrates over time). The phase shift "scrolls" the palette so iris luminance maps to a moving point in the cycle. | 1 | No |
| **`speedCHOP` integrates a dynamic input value over time** — essential for audio-reactive rotation/phase that ACCUMULATES smoothly. Without it, multiplying `absTime.seconds × current_speed` re-multiplies past time by the new speed (jumping). Pattern: `constantCHOP` (with `const0value.expr` = audio-driven speed) → `speedCHOP` → output is cumulative angle/phase. Bind `xform.par.rotate.expr = "op('integrator')['speed']"` for smooth accumulating rotation; negate the binding (`-...`) to flip direction without changing the integrator. | 1 | No |
| **`feedbackTOP` ghost-trails via OVER blend (vs max blend "light writing"):** for proper translucent past-frame overlap, use `compositeTOP operand='over' swaporder=True` AND scale BOTH `outhigh` (RGB) AND `opacity` (alpha) on the feedback decay levelTOP via the same expression. With `over` blend the past frame fades as a translucent layer over current. With max blend (entry 93's pattern) it accumulates as light-writing trails. Different effect, different feel — pick by intent. | 1 | No |
| **TableDAT cell backtick syntax does NOT auto-evaluate** — writing `\`op('ctrl').par.X\`` into a cell stores the string literally, breaks downstream consumers (e.g. rampTOP keys read invalid position). For dynamic cell values driven by params, create a `parameterexecuteDAT` (`par.op` = ctrl COMP, `par.pars` = space-separated param names, `par.valuechange=True`) with an `onValueChange` callback that writes literal float values into the cells when params change. | 1 | No |
| **`circleTOP` background transparency param is `bgalpha`, NOT `bgcolora`** (despite the per-channel `bgcolorr/g/b` naming pattern that suggests it). Setting `bgcolora` raises `tdAttributeError`. Use `bgalpha=0` for transparent surround on overlay-style circles. | 1 | No |
| **Per-channel CHOP normalization architecture — when audio analysis bands have wildly different dynamic ranges (sub_bass overshoots 1.0, mid/high are squished to 0-0.3), normalize before mapping to visuals.** Chain: `chop_audio_in` (selectCHOP from analysis output) → `chop_norm_sub` (mathCHOP `chopop='sub'`, second input = `chop_norm_floors` constantCHOP with per-channel DC offsets) → `chop_norm_mul` (mathCHOP `chopop='mul'`, second input = `chop_norm_scales` constantCHOP with per-channel scale factors = 1/p99 from recordCHOP statistical analysis) → `limitCHOP` (clamp 0-1) → `chop_norm_out`. Now every channel uses the full 0-1 range. | 1 | No |
| **Designer-friendly TD keyframe system without animationCOMP — table-driven approach:** `tableDAT keys` with rows `time(s) | value | curve` (curve string: `linear`/`smooth`/`ease-in`/`ease-out`). `textDAT module` with `get(t)` function that reads the table, sorts by time, finds bracketing keyframes, applies the named curve to interpolation alpha. Param expression: `mod('module_name').get(song_time) + breath_modulation`. Curve fns: `linear` = a, `smooth` = a*a*(3-2*a) (smoothstep), `ease-in` = a*a, `ease-out` = 1-(1-a)*(1-a). | 1 | No |
| **Containers don't have a `.find()` method** — `containerCOMP.find(name=pattern)` raises `tdAttributeError`. Use explicit iteration: `for c in container.children: if predicate(c): ...`. | 1 | No |
| **`audiofileinCHOP.par.indexunit` defaults to `'seconds'`** — `par.index.eval()` directly returns current playback time in seconds. Don't divide by `par.rate.eval()` — that gives nonsensical values. Use `op('audio_in').par.index.eval()` directly as song-time reference for time-driven keyframe interpolation. | 1 | No |
| **TD's `non-realtime mode` engages automatically when recording starts** — TD renders every frame without skipping for clean output. Audio playback during this mode produces clicks/glitches because audio devices can't keep pace with cooked-frame rate. Already entry 70; bumping count. The mode auto-flips back when recording ends. | **2** | **✅ PROMOTED** |
| **rampTOP `fitaspect='fitvert'` makes radial/circular ramps truly circular on portrait canvases** — by default (`fitaspect='fithorz'`), the ramp's radius=1 maps to half-width on a portrait canvas, making the "circle" elliptical-shaped vs the canvas. Use `fitvert` to anchor the radius reference to the longer dimension for true circular vignettes. | 1 | No |

---

## Build Sessions

---

### 2026-05-06 — iris_2 single-eye visualizer for Eyes Cut Deeper, audio-reactive composition done, keyframe choreo + render pending

**What was built:**
Full single-eye visualizer at `/project1` of `touchdesigner/networks/iris_2/iris.toe` for Subtronics "Eyes Cut Deeper" remix (cusp 4→5 register). Started from a Midjourney-generated photoreal iris source (1024×1024 square) and built a complete audio-reactive psychedelic eye that outputs at 720×1280 portrait. Composition migrated through 4 distinct iterations during the session: vertical mirror with hardcut (rejected), asymmetric shift mirror (rejected — "too many fragmentation signals competing"), independent counter-rotating halves with tilted cut (rejected), single rotating eye with circular vignette + black pupil overlay anchor (kept as final).

**Final architecture (left-to-right network spine):**
```
[1024×1024 iris source]
  → xform_iris_center (Sourcex/Sourcey/Sourcezoom — re-centers natural pupil to canvas center for clean rotation pivot)
  → disp_breath (audio-reactive noise displacement) ← noise_breath (simplex3d, slow time evolution)
  → xform_top_rot (rotation around center, scale 1.42x for full-canvas coverage at any angle)
  → lookup_color (palette mapping) ← xform_palette_phase ← chop_color_phase (speedCHOP integrator)
  → xform_aspect (1024² → 720×1280 portrait via outputaspect='resolution' + sx=1.78 for circular pupil preservation)
  → hsv_mute (saturationmult=0.78 — WOBAR muted register)
  → comp_feedback (operand='over', swaporder=True for translucent ghost trails) ← feedback_decay (RGB+alpha decay) ← feedback_iris (par.top references null)
  → comp_vignette (multiply) ← vignette_level ← vignette_ramp (circular, fitaspect='fitvert' for true circle on portrait) ← vignette_keys (Vigsize/Vigfalloff updated via parameterexecuteDAT)
  → comp_pupil_overlay (over, swaporder=True) ← disp_pupil_edge ← circle_pupil + noise_pupil_edge
  → level_post (crush blacks inlow=0.06, roll highlights inhigh=0.95, contrast=1.18, gamma=0.92 cinematic S-curve)
  → bloom_post (HDR — output='inputplusbloom', threshold=0.4, intensity=1.1, maxbloomradius=0.22)
  → null_mirror_out
  → record_out (moviefileoutTOP, h264 yuv420 mp4, audio source = audio_master/audio_in @ 44100Hz)
```

**Audio reactivity remap (after analyzing the recorded 275s × 8-channel signal):**
After recording the song through `audio_master` and computing min/p10/p25/p50/p75/p90/p95/p99/max/mean per channel, classified each channel by dynamics quality. Strong: bass (0-0.81 well-distributed), transient (0-0.79 clean attack), growl (0-1.50 always active). Weak: mid/high (squished, noisy when normalized), sub_pressure (mostly silent). Then built per-channel normalization chain (`chop_norm_floors` + `chop_norm_scales` + `chop_norm_sub` + `chop_norm_mul` + `chop_norm_limit` + `chop_norm_out`) so every channel uses 0-1 fully based on observed p99.

Final mappings:
- **Rotation** ← `Rotspeed + Rotgain × bass^Rotcurve + Rotburst × transient^Rotcurve` (sustained body spin + per-kick snap; clockwise via `xform_top_rot.par.rotate.expr = "-op('chop_rot_integrator')['speed']"`)
- **Color cycle** ← `Colorbase + Colorgain × energy^Colorcurve` (pivoted to energy after growl-driven failed — growl never goes quiet enough for the "slow on break, fast on drop" dynamic; energy's 5-second slow-release lag matches cusp 4→5's emotional decay)
- **Pupil radius** ← `keyframed_radius(song_time) + Pupbreath × sin(t × Breathspeed × 2π)` (audio-reactive removed, pupil is now KEYFRAMED via `anim_pupil_keys` tableDAT + `pupil_kfm` module DAT with linear/smooth/ease-in/ease-out curves)
- **Pupil edge displacement** ← `Pupedgegain × energy^Pupedgecurve` (organic edge wobble during drops only; clean circle in breaks via `Pupedgecurve=3.0` cubic gating)
- **Breath amplitude** ← `Breathamp + Breathgain × bass^Breathcurve` (iris fibers wave harder during drops)

**Key creative decisions:**
- **Pin-point pupil at drops, not dilation.** Reveals MORE iris during peak chaos; pre-drop dilation amplifies the snap. Counter-intuitive vs typical EDM "dilate on drop" but lets the drop's psychedelic chaos read fully.
- **Single eye, not mirror split.** Mirror experiments stacked too many fragmentation signals (cut + asymmetric shift + counter-rotation = "broken" not "intentionally fractured"). Single rotating eye + black pupil overlay = unambiguous gaze + gravity center.
- **Drawn black pupil overlay AT canvas center** is the gravity anchor that makes the eye read as eye regardless of palette phase. Without it, lookup-mapped colors at certain phases turn pupil bright cream and the "eye" reading collapses.
- **Source rectangle edges are visible during rotation** intentionally — adds architectural motion sense ("a card being spun," not just texture shifting). Vignette pulled back (`Vigsize=0.65`, `Vigfalloff=0.95`) to expose this.
- **Sine-wave pupil breath stays through audio-reactive transitions.** Even when pupil is keyframed, the `Pupbreath × sin(t)` term adds always-alive heartbeat.

**Brand check (cusp 4→5 "heavy and beautiful, hard-won softness"):** 8/10. Strong — black pupil = HEAVY, HDR bloom = BEAUTIFUL, pin-point at drops = "open to receive impact," 5-second energy release = residual motion winding down. Drifting — color cycle weights all WOBAR colors equally (could re-weight palette stops to dwell longer in heavy register: deep purple, copper, oxidized teal, wine magenta), peak rotation borderline Act 4 manic, pupil keyframes still placeholder timestamps.

**What got built first-pass right (no correction needed):**
- `xform_iris_center` Sourcex/Sourcey calibration — matched offsets via on-screen pupil drift visualization, locked first try
- HDR bloom — `output='inputplusbloom'` with reasonable defaults nailed the luminous quality immediately
- WOBAR palette ramp — sourced directly from `WOBAR_TD_REFERENCE.md §4`, no iteration needed
- Per-channel CHOP normalization architecture — built once, every channel responded correctly first try (after fixing the `chopop` vs `chanop` bug)
- Pupil keyframe table-driven approach — `tableDAT` + `textDAT` module with curve interpolation worked first try

**What needed correction (NEW gotchas to log — listed in correction tracker above):**
1. `mathCHOP.chopop` vs `chanop` — silent failure when normalizing audio (entry 92 bumped to 2 → promoted)
2. Cross-COMP CHOP wiring fails silently — used selectCHOP bridge as workaround (entry 55 bumped to 2 → promoted)
3. `null_audio` (60Hz analysis) blocked moviefileoutTOP "audio sample rate must be 44100" — switched to `audio_master/audio_in` raw 44100 (entry 32 bumped to 3 → already promoted, count++)
4. Nested function defs in `td_execute_python` fail same as list comps — outer-scope names raise `NameError` (entry 45 bumped to 2 → promoted, broader scope now: list comps + gen exprs + nested defs)
5. `bloomTOP` HDR parameters — first time documented as a canonical pattern
6. Phase-animated palette lookup — first time documented as a canonical pattern
7. `speedCHOP` integrator for dynamic rotation/phase — first time documented
8. `feedbackTOP` OVER-blend ghosting (vs max-blend trails) — first time documented as alternative to entry 93
9. TableDAT cell backticks DON'T auto-evaluate — needed parameterexecuteDAT to update cells dynamically (NEW)
10. `circleTOP.par.bgalpha` (not `bgcolora`) for surround transparency — NEW
11. Per-channel CHOP normalization architecture — first time documented as a reusable pattern
12. Table-driven keyframe system without animationCOMP — first time documented as a reusable pattern
13. `containerCOMP.find()` doesn't exist — minor
14. `audiofileinCHOP.par.indexunit='seconds'` default — `par.index.eval()` returns seconds directly, don't divide by rate
15. TD non-realtime export mode + audio playback clicks — entry 70 bumped to 2 → promoted
16. `rampTOP.par.fitaspect='fitvert'` for true-circular vignette on portrait — NEW

**New patterns discovered (worth documenting in `WOBAR_TD_REFERENCE.md` Visual Primitives Vocabulary):**
- **HDR cinematic eye chain:** crushed-blacks levelTOP → bloomTOP `inputplusbloom`. The signature "burning embers" / luminous-iris-in-black-void look for cusp 4→5.
- **Phase-animated palette cycle:** palette_ramp → xform_palette_phase (tx = integrator % 1.0, extend='repeat') → lookupTOP. Audio-reactive cyclic color shifts through any fixed palette table.
- **Per-channel CHOP normalization layer:** the chain that turns raw analysis CHOPs into 0-1-clamped, p99-scaled, well-distributed visual drivers. Reusable for any audio-reactive build.
- **Table-driven keyframe choreography:** `tableDAT(time, value, curve)` + `textDAT(get_value)` + module call from param expressions. Designer-friendly for music sync without animationCOMP overhead.
- **Single-eye-with-pupil-overlay composition:** the "drawn pupil at canvas center as gravity anchor" pattern for any eye/iris-based visual. Locks the eye reading regardless of color cycling, rotation, or palette transitions.
- **Pupil edge displacement gated by curve:** `displaceTOP` with energy^N curve makes organic perturbation only during drops, clean shape during breaks. Reusable for any "alive at peaks, calm at quiet" effect.

**State at session close:**
- Network ready to record. `record_out` configured (h264 yuv420 mp4, audio = audio_master/audio_in @ 44100Hz).
- Pupil keyframes are PLACEHOLDER — Nick needs to provide actual song drop timestamps and edit the `anim_pupil_keys` table.
- Color cycle pivot from growl→energy means breaks-vs-drops dynamic range is now ~20× (1 cycle/14s break, 1 cycle/0.5s peak).
- `ctrl_master` final state (8 pages, 30 params): Source / Rotation / Color / Pupil / Breath / Vignette / Feedback / (audio bound directly).
- 38 ops total in `/project1`, organized left-to-right in functional bands.
- Brand alignment: 8/10 for cusp 4→5. To get to 10/10: re-weight palette, cap rotation peak lower, real song-time keyframes.

---

**What was built:**
4-cell macro-eye grid composite for the Subtronics "Eyes Cut Deeper" remix (Act 4/5 cusp register). Network: `touchdesigner/networks/eyes_cut_deeper/eyes_cut_deeper.8.toe`. Two parallel outputs from one effects pipeline: `null_grid_out` (720×1280 portrait music video) and `null_album_out` (720×720 album cover).

**Per-cell architecture:**
- TL — 4-fold radial mandala kaleidoscope (bilateral × rotations 0/90/180/270 max-blended). Driven by broadband `energy`. Mandala folds explode at drops (level `outhigh` scaled by Trkaleidoamp × Energy on each mirror layer — RGB fade for max-blend, not just alpha). Wobble displacement INVERSE to energy (perfect mirror at drops, moves at breaks).
- TR — Static-amplitude chromatic aberration (R-shift left, B-shift right, fixed offset) + animated TV static (`randomgpu` type, recentered ±range via offset, ADD blend). Driven by `transient` — punches on drops only.
- BL — Zoom-tunnel feedback (recursive eye-into-eye). Bronze/amber palette via dedicated `bl_keys` lookup table. Driven by `sub_pressure`.
- BR — Calm/oily ripple displacement. Sage/moss/patina palette via `br_keys` lookup. Driven by `growl`.

**Audio pipeline:** Switched mid-session from a custom rebuilt 5-channel base_audio to canonical `base_audio_v001.tox`. Now have 8 channels (sub_bass, bass, mid, high, energy, sub_pressure, growl, transient) with proper band_max normalization. Per-band gains exposed on `ctrl_master.Audio` for cell-specific tuning.

**Final polish:** simplex2d film grain (24 fps scintillation, amp 0.05, mono) overlaid via `overlay` blend + radial vignette (multiply blend, soft 0.45 fractionaspect). Applied to both outputs.

**Composition adjustments:**
- Black inter-cell gaps (sx=0.485, sy=0.4925 — sy slightly larger to balance vertical gap on 9:16 frame against horizontal gap)
- Album branch needed two-stage transforms (square aspect-fill pre-crop, then position) to avoid squishing portrait source into square cells

**What worked first pass:**
- Per-band reactivity transformed the grid feel from "single dial pulsing 4 cells in unison" to "4 facets breathing on different beats" — biggest perceptual win of the session
- Canonical base_audio swap was painless once expressions remapped (`lag_sub` → `sub_bass`, etc.)
- Final grain + vignette polish unifies the disparate cell palettes into one cinematic plane
- 4-fold radial (rotations) reads more ceremonial than 4-fold rectangular (h+v flips) — eye-as-sigil
- Mandala explosion at drops via `outhigh` (RGB scale) instead of `opacity` (alpha-only)
- Album branch built parallel without disturbing music video pipeline

**What needed correction:**
- TV static initially tried with `simplex2d` (smooth blobs, not pixel grain). Switched to `randomgpu` for true per-pixel independence. Then `randomgpu`'s 0.5-centered output killed `overlay` blend — fixed by recentering with `par.offset = -amp/2`.
- `mathCHOP.chanop=average` failed to collapse stereo→mono until set with `chopop=off`. Switched to `selectCHOP.par.channames='chan1'` for cleaner mono extraction.
- Mandala fold-out used `levelTOP.par.opacity` first — invisible at low energy because max-blend ignores alpha. Switched to `par.outhigh` (RGB scale) to actually fade out.
- Feedback chain stuck at 128×128 due to cook-loop warning that I previously documented as "cosmetic." Was actually blocking cook. Fixed by wiring `feedbackTOP.input[0]` to upstream fresh content (not the loop closure), keeping `par.top` for the loop reference, and pulsing `resetpulse` to apply the proper resolution.
- Album branch initial build squished portrait source into square cells. Fixed via two-stage transform: pre-crop to square via `sx=1, sy=1.778, output=720×720, extend=zero`, then position with second transform.
- Sub_pressure on this song is anemic — eyes_cut_deeper is growl-driven (wobble bass), not sustained-sub. Required Blgain=50 to brute-force a response. May need to swap BL's source channel to `bass` for cleaner reactivity.

**Brand alignment:**
- Cells use distinct palettes: TL deep purple (canonical WOBAR), BL warm bronze/amber (oxidized organic), BR sage/moss (oxidized organic). Each cell is monochrome within its palette family.
- TR's CA + static — Nick called this out as "not act-specific, nostalgic register" rather than the rave-bright rainbow register the brand docs lean away from. Opened brand-doc loop to update WOBAR_TD_AGENT_RULES.md Materials section to permit CA as nostalgic/analog primitive.
- Overall composition reads as "4 portals of the eye / 4 facets of the mirror" — direct enactment of WOBAR's "bass as mirror" + multiplicity-of-self thematic.

**Open work for next session:**
1. Render full song to `rec_out` (h264 + mp3, 720×1280). Set Realtime OFF before recording.
2. Album cover at 720×720 needs external upscale (Topaz Gigapixel / Photoshop Preserve Details) for industry-standard 3000×3000 final.
3. Decide on BL audio source — stick with `sub_pressure` and tune gain, or swap to `bass` for stronger response on growl-heavy material.
4. Brand-doc loops opened in WOBAR_ACTIVE.md (palette tier framework + CA register update).

**Reflection:**
Big working session. Substantial creative iteration with on-the-fly tuning. Audio pipeline now matches WOBAR canonical (no more bespoke 5-channel rebuild). Per-band reactivity is the biggest architectural win — gives the grid a layered polyrhythmic feel that single-Energy mapping couldn't achieve. The album branch is a good demonstration that the same effects pipeline can serve multiple deliverables (music video + cover) without duplication.

---

### 2026-05-04 — iris network — 13 moves, NOT shipped

**What was built:**
Iris network for the Subtronics "Eyes Cut Deeper" remix (Act 4/5 cusp, 95 BPM halftime). Started from the YouTube "TD Drop #05 Eyes" tutorial base (twisted-torus geometry creates radial-fiber stroma + the inner cylinder of the torus doubles as the tunnel when camera dives through the pupil — clever single-geo "iris becomes tunnel" mechanic). 13 moves on the stack at session close, manual `.toe` save by Nick at move 011. Network folder: `touchdesigner/networks/iris/`.

**Composition arc (what landed):**
- Recolor to monochrome purple via `ramp2_keys` rewrite (limbal → eggplant → mauve ruff → amber fleck → slate → bone-ash). Killed magenta cast. `noise2.mono=True`, `hsvadj1.saturationmult` 1.34→1.05.
- Dominant scale (`transform2.scale` 1.3→2.2).
- Light recenter (tx 0.77→0, tz 9.97→4.5, ry -4.44→0, dimmer 3.5→5.5) + cool-violet tint (cr 1→0.85, cg 1→0.78, cb 1).
- Pupil baseline (`torus1.rady` 0.65→0.5 — opens hole, hints at inner-cylinder tunnel even at rest, kept by Nick as on-theme feature).
- Halo pulse (10s cycle via expression on `ramp3.period`).
- Black pupil mask (`circle_pupil` 175px) inserted as compositeTOP over `hsvadj1`.
- Feedback boundary mask (`circle_iris_bound` × `comp_iris_bound` between comp4 and downstream) — kills the trail-overflow tail by clipping feedback to the iris circle for both forward path AND `feedback1.par.top` source.
- `ctrl_master` baseCOMP created with `Puprad`, `Irisx`, `Irisy`, `Irisscale` exposed. First WOBAR network with custom-param dashboard built incrementally as needs arose.

**Iris-over-video branch (NOT finished):**
Parallel composite for replacing the natural iris in a 464×832 macro-eye blinking video with the WOBAR iris. `xform_iris_replace` + `mask_iris_video` + `comp_iris_masked` + `comp_video_replace` + `null_video_replace_out`. Position+scale tunable live via `ctrl_master.Replace` page.

**What worked first pass:**
- Twisted-torus + texture+UV chain for the iris stroma — tutorial's geometry is genuinely clever
- Color recalibration via single DAT rewrite (`ramp2_keys`) — biggest leverage move of the session
- Light tinting cool-violet to keep highlights in palette without losing modeling
- Feedback boundary mask via multiplicative circle — clean fix for trail overflow
- ctrl_master incremental param exposure pattern — built only what was needed at each step
- The iris-over-video composite v1 (without blink masking) — alien-eye look landed strongly even without lid masking

**What failed (reverted in-place, no move files written):**
- **Warm halo color tint** — added a defined ring shape that competed with iris instead of complementing it. Lesson: post-render composite layers fight a busy geometric texture rather than enhance it.
- **Catchlight in pupil** — premultrgbbyalpha gotcha hid it for a long time at small sizes; even after fix, position kept overlapping inner-cylinder glint.
- **Wet PBR (low roughness)** — light dimmer at 5.5 (boosted earlier for larger geo) blew out any glossy surface to plastic-mirror look, not "wet eye." Real wet PBR needs light dimmer dropped to ~3 first. Multi-step rebalance, not a quick win.
- **Limbal ring overlay** — barely visible because it merged with the natural alpha falloff at the iris edge.
- **Backface culling on PBR (`cullface=backfaces`)** to remove inner-cylinder glints — didn't work because the twisted geometry has surfaces still front-facing despite curving around. Reverted to `userender`.
- **Chromakey-based blink masking** — natural iris HSV (hue ~0.52, sat 0.42-0.74, val 0.19-0.39) overlaps with sclera (val 0.23-0.36, hue varies including 0.53) AND lid skin (hue 0.40, sat 0.52, val 0.09) in this footage. Color alone can't separate iris from "lid covering iris area." Tried widening hue, adjusting sat/val thresholds, toggling `invert`, switching to value-based threshold — none cleanly handled the blink case. Reverted. Recommended next path: manual keyframing of `Blinkalpha` ctrl_master param across 121 video frames, OR external rotoscope import.

**What needed correction (gotchas — see tracker):**
- compositeTOP `over` input order is empirically opaque — toggling swaporder needed when mask wasn't covering as expected (multiple hours of debugging until this was identified)
- circleTOP center coords are OFFSETS from justify-anchor, not absolute positions
- circleTOP `radiusunit=fraction` is anisotropic on non-square frames
- circleTOP `premultrgbbyalpha=True` hides small/dim shapes in composites
- TD expression namespace requires `math.sin()` not bare `sin()`

**Open work for next session:**
1. Decide on iris-over-video direction (manual keyframe blinks vs. abandon vs. external rotoscope)
2. Build `base_audio` and wire single Energy → Drive binding to (camera tz, twist3 strength, Puprad, light dimmer) for the song-reactive layer
3. Drop choreography (pupil dilation explosion) wiring after audio
4. Recorder for export

**Reflection (Nick's framing — soft mark):**
Lots of color/composition iteration that landed strongly as a standalone iris. The video composite branch is the unfinished piece. Multiple "biological territory" experiments (catchlight, limbal ring, wet PBR, warm halo) all reverted — the iris's geometric character is busy enough that overlay-style additions tend to fight rather than complement. The naturally stylized monochrome-purple iris with dilated black pupil and contained feedback trails is the strong artifact from this session.

---

### 2026-05-01 (evening) — magnet_chamber v001 — second POPX-on-WOBAR primitive shipped

**What was built:**
After the morning's attractor_chamber close-out and afternoon's failed POPX exploration (DLA, physarum-on-sphere, Particle SSFR, DLG — all hit the geo COMP plumbing wall), evening session pivoted to applying the **attribute-screening method** to find a NEW clean POPX module. `magnetize` passed the screen (output: `P, Scale, N, Orient, Transform, Up, FullTransform, PointScale, Pivot` — all transform-related, no `PartId/PartForce/Density/Parent` baggage). Built it out following the attractor_chamber template: POPX magnetize core → manual numinstances → sphere instancing → HDR env + palette-cycling lights → bloom → 4-fold mirror compositing → recorder. Single audio binding: `mag.Strength = floor + ceil*max(0, energy)^exp`. Move file: `touchdesigner/networks/magnet_chamber/moves/move_001.json`. CHANGE_LOG.md created. WOBAR_MOVE_SYSTEM.md updated.

**What worked first pass:**
- Magnetize attribute screening (the methodological win — confirmed it before committing time to render pipeline)
- Native pointgeneratorPOP for both particle source and magnets POP — clean attrs throughout
- Manual `numinstances.expr = numPoints()` pattern (same as attractor_chamber)
- HDR env (qwantani moon noon) lit the pearl spheres immediately
- 4-fold mirror compositing (h + v flips with max blend) — single comp pattern, instantly transformed bilateral form into mandala
- transformPOP between magnets pointgenerator and magnetize input — gave the magnets orbital animation, providing intrinsic motion when audio is silent

**What needed correction:**
- Initial PBR pearl mat with `dimmer=4` lights still rendered too dark — env HDR was needed for proper specular reflection (pattern matches attractor_chamber)
- Camera too close (orbit R=2.0) put camera INSIDE particle cloud — pulled to R=3.5
- No issues with the geo COMP / instancing path itself once attrs were validated

**The two-POPX-primitive milestone:**
With magnet_chamber shipping, WOBAR now has **two confirmed clean POPX primitives**: `SA` (chaotic continuous flow) and `magnetize` (orbital around invisible poles). Different visual registers, both shippable via the same instancing pattern. Future POPX-driven networks can pick one of these or screen new modules via the documented method.

**No new gotchas surfaced in this build** (all the gotchas were from the afternoon's failed exploration, already in the tracker). This was a clean execution of the validated SA-pattern.

---

### 2026-05-01 — POPX exploration day — DLA, physarum-on-sphere, Particle SSFR, DLG — none shipped, all hit TD plumbing walls

**What was attempted (in order):**
1. **Mycelium on a sphere via physarum** — 2D physarum constraint=circle TOP, trail TOP wrapped onto sphere via UV mapping. Got the network rendering with cream tint + bloom + slow camera orbit. Pivoted away when user said it didn't capture the "radial bristles from a center" look of real mycelium photos.
2. **2D physarum direct (no sphere)** — trail TOP straight to output, animated constraint expansion from center. Worked but visually was lattice/foam (closed polygonal cells), not the radial-tree pattern the user wanted.
3. **DLA radial tree** — switched algorithms. DLA is correct shape (tree-like aggregation from seed). Got it growing (5000 aggregated points around a center seed). **Wall:** `geometryCOMP` with manual instance count rejects POPX DLA outputs ("Manual number of instances not supported when using a POP with point co[lor]") even after stripping Color. Tried `oplength` mode — reads 1. Tried `popToSOP` conversion + SOP-instancing path — same wall. Switched to `scriptTOP` numpy rasterizer — **crashed TD twice** at 1024×1024 at `CookLevel.ALWAYS`.
4. **Liquid mirror via POPX Particle (Fluids-PBF) + SSFR** — built native particlePOP emitter (worked at 60fps with manual numinstances), wired POPX Particle for SPH physics. **Walls:** (a) bbox collision didn't contain particles even with `Usecustombounds=True` — particles tunneled to y=-167; (b) Particle's POP output has 17 attributes (PartVel, PartId, PartForce, PrevP, Density, etc.) — same `geometryCOMP` rejection.
5. **DLG hypnotic line growth** — switched to maze/labyrinth/brain-coral pattern. DLG outputs lines (not points) which should render via SOP path. **Walls:** popToSOP'd line → renderTOP shows it as a filled white disc (closed polyline = closed polygon). Sweep tubes through line → render shows nothing despite 12k swept points. Same TD-plumbing fog.

**What WORKED today:**
- POPX `physarum` 2D simulation with constraint TOP + trail TOP rendering — proved the **TOP-output POPX modules bypass the geo COMP wall entirely**. Renders cleanly because output is already a TOP.
- Native `particlePOP` emitter at 60fps with 5000 particles and manual `numinstances.expr = numPoints()` — works for native POPs (no Color attr).
- POPX `DLA` simulation itself — grows the right algorithmic shape; only its rendering is blocked.
- POPX `DLG` simulation itself — grows the labyrinth pattern; rendering blocked at the line-vs-fill distinction.

**Pattern discovered:**
TD's POP→geo→render path has a hard wall that complex POPX module outputs can't cross. The shipped `attractor_chamber` worked because POPX SA outputs **only simple attrs** (P, PartVel, N, Color, LenVel) and we stripped Color before instancing. POPX modules with rich attribute sets (DLA's iNumChildren/Parent/Seed/Rand, Particle's 17 attrs, physarum's POP output) trip the same `geometryCOMP` rejection regardless of workaround attempts.

**Three paths forward when this comes up again:**
1. **Stay in SA-pattern** — only use POPX modules with clean POP outputs. SA has been validated.
2. **Use TOP-output POPX modules directly** — `physarum` (trail TOP), `Flow` (substance/velocity TOPs), `Voxelize` (volume/SDF TOPs). Skip the geo COMP entirely.
3. **GLSL TOP shaders** — write the visual primarily as a `glslTOP`. No POP plumbing involved at all. WOBAR-on-brand candidates: reaction-diffusion (Gray-Scott), domain-warped fractals, audio-reactive caustics, kaleidoscopic mirror cascades.

**No move file written** — no network shipped. **Lessons captured in correction tracker (3 promoted: geometryCOMP-rejects-rich-POPs, oplength-reads-1, scriptTOP-ALWAYS-crashes).**

---

### 2026-05-01 — attractor_chamber v002 — POPX-on-WOBAR proof shipped

**What was built:**
First polished POPX-on-WOBAR network. Lives at `/project1`. POPX SA Aizawa cloud (3000 points, advect mode, audio-bound Timescale) → math_velocity → random_scale (deterministic per-particle ScaleRand 0.6-1.4) → null_pop_out → instanced black-pearl PBR spheres → mirror-symmetric composite → atmospheric post → recorder. 4 lights orbit/cycle through palette channels with non-syncing primes. Centroid tracker keeps lookat target on live mass-center via EMA-lerp. `ctrl_master` baseCOMP exposes 22 custom params across 6 pages (Audio / Material / Lighting / Camera / Composition / Form) — every visual op reads from this dashboard. Audio reactivity intentionally limited to ONE binding per Nick: `sa1.Timescale = floor + ceil*max(0,energy)^exp`. Move file: `touchdesigner/networks/attractor_chamber/moves/move_002.json`. CHANGE_LOG.md updated. Loop closed → WOBAR_CLOSED.md.

**What worked first pass:**
- POPX SA Aizawa setup — Initialize → Start → Play sequence followed cleanly per the v1.1 guide
- pbrMAT black-pearl tuning — basecolor near-black, metallic 0.92, roughness 0.10 hit the "solid pearl glistening" register quickly
- Mirror-flip + max-blend composite for bilateral symmetry — single comp TOP, transformative
- ctrl_master custom param creation via `appendCustomPage` / `appendFloat` / `appendToggle` Python — clean and reliable

**What needed correction:**
- Audio energy `max(0.0, ...)` clamp before pow — see correction tracker; broke `sa1.Timescale` until fixed
- Initial attempts at `instancesx = 'LenVel*0.6'` silently failed — geometryCOMP only accepts bare attribute names
- ColorU custom attribute didn't survive SA's update — moved attribute write downstream of SA
- Several aborted experiments (stretched-ellipsoid orient-along-velocity, curl-noise on P in feedback loop, depth-DOF, luma-blur, aura layer, nebula bg, glints) — each tested and rejected
- 27 orphan ops left over from experiments — cleaned up at session close

**New patterns surfaced (all logged in correction tracker above):**
- Audio negative-noise `pow()` clamp
- geometryCOMP bare-attribute instance scale
- POPX SA strips upstream custom attrs
- `nullPOP.points('attr')` returns typed-per-point lists
- renderTOP geometry glob pattern
- Live centroid tracking via executeDAT + EMA
- compositeTOP operand=over input order vs operand=add for transparent forms
- Non-realtime mode audio click warning

**Open for future iteration:**
- Audio reactivity: only `Timescale` bound. Future tracks could add sub→light flash, mid→Ua morph, energy→bloom. Per-track basis.
- Mirror modes: only bilateral. Quadrant (4-fold radial) would push sigil register harder.
- `base_audio` energy normalization sits at ~0.48 idle — worth surveying internals to confirm calibration.
- Numpoints hardcoded 3000 — expose as ctrl_master.Numpoints if track-specific density tuning needed.

---

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
