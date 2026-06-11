---
title: TouchDesigner Agent Build Rules
version: 3.1
last_updated: 2026-06-10
status: live
scope: Conventions any AI agent must follow when creating or modifying TouchDesigner networks in the WOBAR project. Read before any TD build action.
dependencies: [[WOBAR_CONTEXT]], [[reference/WOBAR_TD_REFERENCE]], [[reference/WOBAR_FRAMEWORK]]
---

# TOUCHDESIGNER AGENT BUILD RULES

Rules for any AI agent (Claude Code + TWOZERO MCP, or any future TD automation) building or modifying networks in the WOBAR project. These are non-negotiable conventions. If a rule here conflicts with a default behavior, the rule wins.

---

## Rule 0: Check the Debug Log First

**Before giving any TD technical advice or executing any build action, read `working/TD_CLAUDE_DEBUG_LOG.md` and check for matching past failures.**

If your planned action, parameter choice, or operator selection matches a logged failure — stop, cite the entry (date + wrong advice), and use the corrected pattern instead. This is the highest-priority rule. It runs before all others.

---

## Rule 0b: Check Reference Networks Before Building

**Before building any new visual network, read `touchdesigner/reference_networks/README.md` and identify the closest structural match.**

If a structurally similar example exists — same feedback pattern, same TOP family, same act-type constraints — propose the new build as a diff against it: "This is the Act 3 tunnel entry but with X changed." Do not rebuild from scratch when a reference exists. This prevents structural drift across acts and surfaces taste decisions that are already resolved.

If no close match exists, build from scratch and add an entry to the README after the session.

---

## Network Folder Structure

```
wobar/touchdesigner/networks/
  [network_name]/
    [network_name]_v001.tox
    [network_name]_v002.tox
    CHANGE_LOG.md
    moves/
      move_001.json
      move_002.json
```

- One folder per visual/network. Agent picks a descriptive name on creation.
- `.tox` checkpoints at the network root. Sequential, zero-padded to 3 digits.
- `CHANGE_LOG.md` at the network root — records why changes were made. Feeds the learning loop.
- `moves/` subfolder holds the move history stack.

---

## Move History System

**Full spec: `reference/WOBAR_MOVE_SYSTEM.md`**

Every TD modification goes through the move system. No exceptions.

- **Move** = everything the agent does in response to one user request. One request, one move.
- Before executing any TWOZERO call, capture the before-state of what's about to change.
- After all calls succeed, write `move_NNN.json` to the network's `moves/` folder.
- If any call fails mid-move, auto-rollback: replay before-states in reverse. No move file written. If rollback fails, write `move_NNN_failed.json`.
- Undo = pop last N moves off the stack, replay before-states, delete move files.
- Save = `.tox` checkpoint via TWOZERO, analyze moves first, then flush, restart numbering.

---

## Skills

Three skills govern the TD workflow:

| Skill | Trigger | What it does |
|-------|---------|-------------|
| `td-build` | Any TD modification request | Capture before-state → execute TWOZERO calls → write move file. |
| `td-undo` | "Undo that" / "undo last N" | Read last N move files → replay before-states in reverse → delete move files. |
| `td-save` | "Save it" / "I'm happy with this" | Save `.tox` via TWOZERO → flush moves → log to CHANGE_LOG.md → analyze session → propose rule updates. |

---

## Naming Conventions

- **Operators**: lowercase_with_underscores. Descriptive. `null_audio`, `ctrl_force`, `feedback_spiral`, not `null1`, `constant2`, `feedback1`.
- **Control CHOPs**: always prefixed `ctrl_`. Example: `ctrl_light`, `ctrl_scene`, `ctrl_force`, `ctrl_noise`.
- **Null TOPs**: always prefixed `null_`. Cap every chain with a Null TOP. No exceptions.
- **Base COMPs**: prefixed `base_`. Example: `base_act1`, `base_switcher`, `base_globals`.
- **File naming**: versioned `.toe` files per visual module. Format: `[module]_v[NNN].toe`. Example: `vortex_v002.toe`, `sphere_v003.toe`.

---

## Control Architecture — ctrl_master Custom-Parameter Panel

**(Rewritten 2026-06-10 to match established practice — supersedes the old "13-Parameter Contract" of named Constant CHOPs.)** Every visual module is controlled from a single **`ctrl_master` baseCOMP carrying custom parameters**, organized into pages. This is the pattern every shipped network since May 2026 uses (down_bad_3stack, iris_2, magnetize/glass-orb).

- One `ctrl_master` baseCOMP per network. Custom float params via `appendFloat`, grouped into custom pages by subsystem (e.g. Top/Mid/Bot/Video/Post, or Camera/Form/Color/Audio).
- **Par naming (TD-enforced):** first letter uppercase, rest lowercase + digits only. `Echoreact` works; `EchoopacityReact` raises tdError.
- Target ops bind via expressions: `op('ctrl_master').par.Paramname` (or `op('../ctrl_master').par.X` inside a treatment COMP for portability).
- **Audio binding template:** `Base + React * pow(clamp(audio_n, 0, 2), Curve)` with paired ctrl_master dials per binding. `React=0` default leaves baseline behavior untouched — Nick dials reactivity in without rewiring. `Curve`: 1 = linear, 1.5 = gentle punch, 2.5 = very punchy. **Curve above ~1.2 crushes gentle-register material (Act 1/5)** — see Audio Pipeline Standard.
- **Page reorganization / rebuild pattern (atomic):** snapshot all customPars (name → val + default) → collect names list → destroy each by getattr lookup (NOT by iterating customPars — the iterator invalidates after the first destroy) → destroy customPages → recreate pages + pars in order → restore vals. Expression references survive because par names stay identical. **Re-assert all defaults explicitly after recreating** — recreated params can init to wrong values.
- Watch for **silently disconnected params**: a value set directly on a target op during exploration won't show in a reference search — check the target par's actual mode, not just the ctrl value.
- All control values normalized 0–1 where possible; mapping to actual ranges happens in the expression.

**Never hardcode parameter values in operator fields when they should be controllable.** If a value might change during performance or between scenes, it gets a `ctrl_master` custom par.

Legacy note: older networks (pre-May 2026) use named Constant CHOPs (`ctrl_force`, `ctrl_noise`, …) accessed as `op('ctrl_name')['channel_name']`. Don't convert them unprompted, but build new networks on the ctrl_master pattern.

---

## Network Layout

- Build left to right. Inputs on the left, outputs on the right.
- Use **Base COMPs**, not Container COMPs.
- Each act lives in its own Base COMP: `base_act1` through `base_act5`.
- Each act outputs through a **Null TOP** named `null_out`.
- Use **Select TOP** to reference across containers — no visible cross-container wiring.
- Shared resources (audio analysis, color palettes, grain) live in `base_globals`.

**`base_globals` target architecture:** The audio pipeline and color palettes should eventually live in `base_globals` and be referenced by all act COMPs via Select TOPs. Current state: `base_audio` and `base_act2_map` exist as standalone networks. Do not create duplicate audio pipelines per act — when building Act 3+, reference `base_audio` via Select CHOP instead.

---

## Pixel Format and Resolution

- **16-bit float** in all feedback chains. Non-negotiable. 8-bit causes banding in dark purples.
- **Generator TOPs**: always check Common page resolution. Default 256x256 is almost never correct.
- **Grain Noise TOP**: generate at 512x512, upscale via Resolution TOP. Full-res grain looks digital.
- **Ramp TOPs** (palette maps): 1024x1, 16-bit float, Hermite interpolation.

---

## Feedback Chain Rules

Every feedback loop must follow this structure:
```
Feedback TOP -> Transform TOP -> Level TOP -> Composite TOP -> Null TOP
                                                    ^
                                            [New content source]
Feedback TOP: targetop = null_out (downstream Null)
```

**Canonical wiring (reconciled 2026-06-10 — supersedes earlier conflicting advice):**
- `feedbackTOP.par.top` = the downstream loop target (the composite/null). Wire `input[0]` to **fresh content upstream of the loop** (e.g. the new-content source) — NOT to the loop target. Target-on-input[0] creates the circular reference that triggers the cook-dependency-loop warning, and that warning is **not cosmetic** — it can block cooking.
- `feedbackTOP` **defaults to 128×128** and caches old resolution. Set the loop ops' resolution explicitly, then pulse `par.resetpulse` once to apply it.
- First-frame "Not enough sources" error clears on cook.

Critical parameters:
- Level TOP `opacity` (Post tab): 0.89-0.97. Above 0.99 = white-out. Below 0.85 = trails die instantly.
- Transform `sx`/`sy`: <1.0 for inward pull (Act 2), >1.0 for outward expansion (Act 4). Never exactly 1.0.
- Always include an HSV Adjust TOP in the chain if color drift is desired.
- Trail feel: `compositeTOP max` = light-writing accumulation; `over` (swaporder=True) with the SAME expression scaling both `outhigh` (RGB) and `opacity` (alpha) on the decay levelTOP = translucent ghost trails. Pick by intent.

---

## Audio Pipeline Standard

Four-band extraction from Audio File In CHOP:
- Sub-bass: Band Pass 50Hz, Q 0.7
- Bass: Band Pass 150Hz, Q 0.8
- Mid: Band Pass 1kHz, Q 0.5
- High: High Pass 4kHz

Each band: Audio Filter -> Analyze (RMS) -> Lag CHOP -> Null CHOP.

Lag values:
- Sub-bass breath: Up 0.05s, Down 0.3s
- Kick hits: Up 0.005s, Down 0.15s
- Hi-hats: Up 0.001s, Down 0.05s

Beat detection: Beat CHOP (40-150Hz for kicks, threshold 0.5, min period 0.3s for 140 BPM).

All audio merged to single Null CHOP as export point.

### Normalization and reactivity rules (promoted 2026-06-10)

- **Record first, then map.** Before binding audio to visuals, record the full song through the analysis output (recordCHOP tap), compute per-band percentiles, and normalize: `preoff = -p10`, `gain = 1/(p_hi - p10)` where `p_hi = p90` for steady bands, `p95` for sparse spike bands (transient). **Normalize to p95/p90, never max** — max is outlier-driven. Publish normalized channels with an `_n` suffix from a `base_audio_react` baseCOMP (selectCHOP per band → mathCHOP preoff/gain → renameCHOP `_n` → mergeCHOP → null_out).
- **Binding template:** `Base + React * pow(clamp(audio_n, 0, 2), Curve)` — see Control Architecture. Clamp at 2 lets peaks above p90 land ~2× without unbounded blowups.
- **Power curves above ~1.2 crush gentle-register modulation.** `pow(x, 2.5-3.0)` is right for punchy drops (flattens breakdown rumble, passes peaks through) but kills audio response on gentle material (Act 1/5) where typical values sit low. Choose the curve from the recorded percentiles, not by feel. (Recurred 04-16 + 05-23 → promoted.)
- **Always wrap audio channels before fractional `pow()`:** analysis channels return tiny negative values (~1e-22) at silence, and `pow(negative, 2.5)` returns complex → TypeError. Use `max(0.0, audio) ** exp`. (Recurred 2× → promoted.)
- **Audio-reactive rotation/phase must be INTEGRATED, not multiplied.** `absTime.seconds * current_speed` re-multiplies past time on every speed change → jumps. Pattern: constantCHOP (`value0.expr` = audio-driven speed) → `speedCHOP` → cumulative angle/phase.

---

## Visual Identity Lens

Visuals lean **mirrors and encounter** over portals and journey. Build for stillness-with-depth, recursive recognition, the gap between observer and image — not forward motion or arrival narratives. Brand docs (`WOBAR_BRAND.md`, `WOBAR_FRAMEWORK.md`, `WOBAR_COPY.md`) keep their existing language; this lens governs visual decisions only.

---

## Color System

The palette is the **WOBAR desaturated psychedelic range** — see `WOBAR_TD_REFERENCE.md §4` for the full swatch with hex values. Black and deep purple remain the foundation; mauves, magentas, slates, oxidized organics, ambers, and mirror metallics are all **first-class** alongside them, not rare accents.

**Core discipline:** desaturated psychedelic. Muted 30–40% from full neon. Never pure neon, glowstick, candy, or safety colors. When LED-style glow is in play, the *light* brightens but the underlying hue stays in the palette — no "muted base + neon glow on top."

**Color-grading pipeline (now optional, no longer mandatory force-to-grayscale):**

```
[Source] → Level TOP (mild grade) → optional Lookup TOP ← Ramp TOP (1024×1, drawn from WOBAR palette)
```

- Use a **Lookup TOP + Ramp** when you want a scene to commit to a color route (purple monochrome, oxidized-rust, slate-and-mauve, etc.). Build the Ramp from the swatch in `WOBAR_TD_REFERENCE.md §4`.
- **Skip the Lookup** when you're already rendering inside the palette (PBR materials with palette colors, GLSL shaders using the palette vec3s, native instance colors). Just grade with Level for contrast/black point.
- The old `HSV Adjust (saturationmult 0.15)` pre-step is **no longer required** — that pipeline forced everything to purple-monochrome, which is the wrong default now. Use it only when you specifically want to recolor a saturated source through a single-hue ramp.

---

## Materials and Surface

Texture vocabulary is **wider than before**. Matte, rough, organic grain still works. So do metallic, glossy, and reflective surfaces — gloss is no longer banned.

- **Permitted:** matte, rough, gritty, organic grain, oil-on-water, oxidized metal, tarnished mirror, polished metal, anodized titanium, glass, wet ceramic, lacquer, **chromatic aberration (CA / RGB channel split) as nostalgic / VHS / analog signal distortion** — not as rainbow effect
- **Lean away from traditional rave:** glowstick brightness, plastic-bright surfaces, candy-pop sheen, holographic-foil rainbow shifts (different from CA — see below)
- **Bioluminescence-style glow still preferred for dim scenes** (deep-sea creature, not LED rave-stick), but LED glow is not banned — it has to stay desaturated
- Reference fields: Tipper visuals, Of The Trees album art, oxidized copper, bioluminescent deep-sea, 70s psychedelic art aged 50 years, oil-on-water darkened, Alex Grey's darker bodies of work

### Chromatic aberration — nostalgic register, not act-locked

CA reads two ways. **Off-brand:** rave-bright RGB rainbow (festival lights, holographic foil glamour). **On-brand:** subtle VHS-tape signal-bleed, aged-film magnetic distortion, 70s psychedelic art faded 50 years, analog signal degradation. Tone is the difference: muted + small offset = analog/nostalgic; saturated + large offset = rainbow/rave.

- **Use CA freely as a nostalgic / analog primitive.** Not act-specific. Lives in the shared visual vocabulary (`WOBAR_TD_REFERENCE.md §3`).
- **Recipe (TD has no native CA op):** 3 levelTOPs to isolate channels (red: `highg=highb=0`; green: `highr=highb=0`; blue: `highr=highg=0`) → 2 transformTOPs to offset R and B in opposite directions (G stays center) → 2 add-blend compositeTOPs to recompose. ~7 ops total.
- **Tune to stay nostalgic:** small offsets (1-3px or 0.005-0.015 fraction), partial-channel reduction so the bleed is dim not vivid, optional grain/desaturation pass after to age the result.
- **Canonical example:** TR cell of the eyes_cut_deeper grid (`touchdesigner/networks/eyes_cut_deeper/`). Static-amplitude CA + animated TV static, driven by transient.

---

## Act Identity

Acts have **emotional registers** (from `WOBAR_FRAMEWORK.md`) and a **shared visual vocabulary** (`WOBAR_TD_REFERENCE.md §3`). They no longer have hard required/forbidden constraints. The act's identity emerges from the music + the brief; visuals serve the act's emotional register without a checklist.

What this means for builds:
- Don't validate visuals against required-vocabulary tables (there is no longer a table).
- An Act 1 build doesn't have to be a circle. An Act 3 build doesn't have to be a tunnel. An Act 4 build doesn't have to explode outward.
- The `WOBAR_TD_REFERENCE.md §3` primitives are starting points and reusable vocabulary, not act-locked requirements.
- Cross-act color borrowing is fine when it serves the moment.
- The act's *emotional register* is still load-bearing — Act 3 should still feel confrontational, Act 4 should still feel cathartic. That comes from the music, the motion, and the build's overall shape, not from a banned-color list.

---

## Export and Render

**(Corrected 2026-06-10 — the old platform table specified h264nvgpu, which contradicts the non-commercial license rule below. Platform-ready h264 is produced OUTSIDE TD, e.g. HandBrake/FFmpeg, from the mjpa master.)**

- **This machine runs NON-COMMERCIAL TouchDesigner — no H.264/H.265 export from TD.** `moviefileoutTOP`: `videocodec='mjpa'` (.mov) or PNG image-sequence. Audio codec `pcm16` (mp3/aac can be license-gated).
- `audiochop` → the raw 44100 Hz `audiofileinCHOP` (e.g. `audio_in`) with `playmode='locked'` — NEVER an analysis CHOP (`null_audio` runs at cook rate, errors "Audio CHOP sample rate must be 44100"). If two audiofileinCHOPs share the file, route the LOCKED-to-timeline one — the sequential one plays real-time from sample 0 and desyncs the export.
- Audio File In: `Play Mode` = Locked to Timeline.
- Match Movie File Out `fps` to project cook rate (`fps = me.time.rate`).
- **Non-realtime mode engages automatically when recording starts** (TD cooks every frame) and flips back when it ends. Audio playback clicks/glitches during recording are expected — don't debug them; return to realtime for reactivity tuning.
- Delivery: transcode the mjpa master to platform h264 in HandBrake/FFmpeg. YouTube 1920×1080; TikTok/IG 1080×1920.

---

## Build Order

Always follow this sequence when building a new visual module:
1. Geometry / visual source
2. Lighting and materials (establish PBR settings early — high Metallic suppresses light)
3. Color pipeline (HSV Adjust -> Level -> Lookup)
4. Grain layer
5. Control architecture (Constant CHOPs)
6. Parametrize all values through control CHOPs
7. Audio pipeline (only after visual is fully parametrized)
8. Post-processing (bloom, final comp)

**Parametrize before wiring audio.** Do not skip to audio reactivity before the visual module is fully controllable via CHOPs.

---

## Known Parameter Name Gotchas

These are par names that differ from what you'd expect. Check here before guessing.

| Operator | Wrong | Correct |
|----------|-------|---------|
| levelTOP | `par.contrast1` | `par.contrast` |
| levelTOP | `par.brightness` | `par.brightness1` |
| levelTOP | `par.gamma` | `par.gamma1` |

---

## Python Scripting Rules (td_execute_python)

**Rule: All `op()` calls must be inside the function body — no script-level globals.**

Helper functions defined in `td_execute_python` do not inherit variables defined at the script's outer scope. Any `op()` reference in a helper function must be called inside that function, not passed in from outside or defined at the module level.

**Wrong:**
```python
chop = op('/project1/base_audio/rec_audio')  # script-level

def analyze():
    vals = list(chop.chan(0).vals)  # NameError: chop not defined inside function
```

**Correct:**
```python
def analyze():
    chop = op('/project1/base_audio/rec_audio')  # inside the function
    vals = list(chop.chan(0).vals)
```

**Rule: No list comprehensions, generator expressions, lambdas, OR nested function definitions that reference outer-scope variables — use explicit for loops. (Extended 2026-06-10; recurred across 3+ sessions.)**

The `td_execute_python` exec environment cannot capture outer-scope names inside any nested scope: comprehensions, genexprs, lambdas, and `def`-inside-the-script all fail with `NameError`. Use explicit for loops with `.append()`, and bind every reference locally inside the function body.

**Wrong:**
```python
ba = op('/project1/base_audio/rec_audio')
vals = [ba.chan(i).vals for i in range(ba.numChans)]  # NameError: ba not defined
```

**Correct:**
```python
def collect():
    ba = op('/project1/base_audio/rec_audio')
    vals = []
    for i in range(ba.numChans):
        vals.append(list(ba.chan(i).vals))
    return vals
```

**Rule: Use `rmspower` for analyzeCHOP on HP filter output — not `average`.**

HP filters produce a bipolar audio signal. `analyzeCHOP function='average'` averages positive and negative samples → returns ~0. Use `function='rmspower'` for any chain coming out of a high-pass filter. Bandpass filters work with `average` because they produce an envelope-like output.

**Rule: Do not use `par.val` to verify expression results — use `par.eval()`.**

`par.val` returns a cached value that may not reflect the current expression output. To verify what an expression actually evaluates to, use `par.eval()`.

---

## Promoted Gotchas — by Operator Family (landed 2026-06-10)

These all hit 2+ occurrences in the TD_BUILD_LOG Correction Tracker. They were marked "promoted" in the tracker but the rule text never landed here until the 2026-06-10 audit. Check this section before touching any of these operators.

### compositeTOP
- **`operand='over'` with `swaporder=False` (default) puts INPUT 0 ON TOP** — opposite of intuition and of what the docs imply. Cost hours of debugging twice. **Always set `swaporder=True`** when wiring "input 0 = bottom, input 1 = top."

### Multi-input TOPs (layoutTOP, etc.)
- **Input connectors auto-compact on `.disconnect()`** — disconnect input 0 and input 1 silently shifts into its slot. When changing ANY input on a multi-input TOP: disconnect ALL inputs first, then re-wire all of them in order. Never partial-disconnect.

### mathCHOP
- **`chopop` (inter-CHOP per-channel math) vs `chanop` (intra-CHOP channel collapse) — wrong one breaks SILENTLY.** Two same-shape CHOPs, per-channel multiply → `chopop='mul'`. `chanop='mul'` combines channels within one input and outputs wrong data with no error.

### CHOP wiring across COMPs
- **Cross-COMP CHOP wiring fails silently** — `outputConnectors[0].connect()` from inside a COMP to outside appears to succeed but the connection reads empty. Use `selectCHOP` with an absolute path (`par.chop='/project1/comp/inner_chop'`).

### Time references
- **Camera/transform expressions on `absTime.seconds * speed` drift to huge values across a session** — use `me.time.seconds` (resets with the component, follows scrub/pause). `absTime` is wall-clock; reserve it for things that should never rewind (noise seeds, grain).

### scriptTOP
- **`CookLevel.ALWAYS` doing per-frame numpy on streaming inputs crashes TD** (locked the MCP server twice in one session). `ON_CHANGE` is equally dangerous if the input changes every frame. Don't use scriptTOP for high-frequency numpy on streaming POP/CHOP data.

### geometryCOMP + instancing
- **A fresh `geometryCOMP` auto-creates a rendering `torus1` child** — destroy it (or `render=False`) immediately after creation, or it dominates the frame as a giant white blob. Verify: `for c in geo.children: print(c.name, c.render)`.
- **`instancetop` is for TOP-based color instancing; `instanceop` is the CHOP/POP source.** Don't swap them.
- **POPX-derived POPs with rich attribute sets (PartId, PartForce, PrevP, Density…) are REJECTED by geometryCOMP instancing** ("Manual number of instances not supported when using a POP with point co[lor]") — even after stripping Color. Instance from native particlePOP or from POPX modules with clean outputs (SA, magnetize: P/PartVel/N/LenVel only).
- **`oplength` instance-count mode reads 1 from POPX nullPOP outputs** (and native particlePOPs) even when `numPoints()` is thousands. Use `instancecountmode='manual'` + `numinstances.expr = "op('/path/null').numPoints()"`.
- **POPX attribute screening — de-risk any new POPX module BEFORE building around it:** place a copy, wire minimum inputs, Init→Start→Play, then `print([a.name for a in op('<mod>/POPX_out1').pointAttributes])`. Clean attrs → safe to instance. Rich attrs → pivot to TOP-output modules or a decoupled architecture (POPX provides the force field, native particlePOP holds clean attrs).

### isOP parameter paths (renderTOP, geometryCOMP.material, env maps, …)
- **Sibling references take the BARE name; `./name` = child; `../name` FAILS SILENTLY (resolves None).** Hit twice: renderTOP camera/lights (2026-05-21, "No Camera COMP found") and geometryCOMP material on instances (2026-06-10 — symptom: everything renders default WHITE). When in doubt use a full `op()` path. Promoted 2026-06-10.

### feedbackTOP
- See **Feedback Chain Rules** above for the canonical wiring (fresh content on `input[0]`, target as `par.top`, explicit resolution + `resetpulse`). The loop warning is not cosmetic.

### Export / recording
- See **Export and Render** above: non-commercial license (no h264/h265 from TD), `audiochop` → raw 44100 Hz locked `audio_in` (never `null_audio`), non-realtime auto-engages during recording.

---

## Feedback Loop — Agent Self-Improvement

The `td-save` skill handles this automatically. Findings are appended to `working/TD_BUILD_LOG.md`:
- What was built (module name, act, brief description)
- What the agent got right on first pass
- What needed manual correction (parameter values, node choices, naming)
- Any new patterns discovered

This log is the training data for improving these rules. If a correction appears 2+ times in the log, it becomes a rule in this file.

---

## Promoted Rules (2026-06-09)

**Rule: Use `math.sin()` / `math.cos()` / `math.pi` in parameter expressions — never bare `sin`/`cos`.**
Bare `sin` is a `NameError` (TD expr namespace exposes `math` and `tdu`, not bare math fns). Logged twice (2026-05-04, 2026-06-09) → promoted. Bonus insight: a par-expression error re-cooks every frame and can stall expensive **upstream** cooks (a 4K HDRI re-decode tanked fps to ~6) — when fps drops unexpectedly, check `op('/x').errors(recurse=True)` first.

**Rule: This machine runs NON-COMMERCIAL TouchDesigner — no H.264/H.265 export.**
For `moviefileoutTOP`: `videocodec='mjpa'` (.mov) or a PNG image-sequence; audio `pcm16` (mp3/aac can be license-gated); `audiochop` → the raw 44100 Hz `audiofilein` with playmode `locked` (never an analysis CHOP); `fps = me.time.rate`.

---

## Working Principles (glass-orb session, 2026-06-09)

Principles, not hard conventions — they encode how the best sessions have gone.

- **Don't fight the tool.** When a technique repeatedly resists (shard-orientation rings, depth-of-field on transparent glass), stop and find another route or drop it. Recognizing the dead-end early is the skill.
- **Strip to a legible base, then add variation one intentional decision at a time.** Get to a state where everything is visible, then introduce each change as a deliberate choice (ideally a question to Nick) — not a pile of simultaneous tweaks.
- **When the last addition makes it worse, you've hit the stopping point.** That's the signal the piece is done — clean up and ship, don't keep gilding.
- **Act-2 "breathe WITH the sound" = audio-reactive motion is load-bearing.** A self-clocked hypnotic loop is not DESCENSION until the form responds to the track — usually the element that separates "pretty" from "on-brand."
- **Depth = spectrum** is a strong WOBAR audio-visual mapping: lows far/large, highs near/small, so layered depth becomes a "frequency tunnel" the listener stands inside. (Reusable beyond the glass-orb.)
