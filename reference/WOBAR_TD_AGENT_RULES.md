---
title: TouchDesigner Agent Build Rules
version: 3.0
last_updated: 2026-04-30
status: locked
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

## Control Architecture — The 13-Parameter Contract

Every visual module is fully controlled via named **Constant CHOPs**. This is the established pattern:

- Group related parameters into named Constant CHOPs: `ctrl_force`, `ctrl_noise`, `ctrl_speed`, `ctrl_geometry`, `ctrl_visual`, `ctrl_light`, `ctrl_scene`.
- Access parameters via expression syntax: `op('ctrl_name')['channel_name']`
- Time-evolving noise: `absTime.seconds * op('ctrl_noise')['noise_speed']`
- Per-instance channel access via Shuffle CHOPs: `op('shuffle3')['chan' + str(me.digits)]`
- All control values normalized 0-1 where possible. Mapping to actual ranges happens in the expression.

**Never hardcode parameter values in operator fields when they should be controllable.** If a value might change during performance or between scenes, it goes in a `ctrl_` Constant CHOP.

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

Critical parameters:
- Level TOP `opacity` (Post tab): 0.89-0.97. Above 0.99 = white-out. Below 0.85 = trails die instantly.
- Transform `sx`/`sy`: <1.0 for inward pull (Act 2), >1.0 for outward expansion (Act 4). Never exactly 1.0.
- Always include an HSV Adjust TOP in the chain if color drift is desired.

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

- **Permitted:** matte, rough, gritty, organic grain, oil-on-water, oxidized metal, tarnished mirror, polished metal, anodized titanium, glass, wet ceramic, lacquer
- **Lean away from traditional rave:** glowstick brightness, plastic-bright surfaces, candy-pop sheen, holographic-foil rainbow shifts
- **Bioluminescence-style glow still preferred for dim scenes** (deep-sea creature, not LED rave-stick), but LED glow is not banned — it has to stay desaturated
- Reference fields: Tipper visuals, Of The Trees album art, oxidized copper, bioluminescent deep-sea, 70s psychedelic art aged 50 years, oil-on-water darkened, Alex Grey's darker bodies of work

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

- **Realtime OFF** during render. Non-negotiable.
- Audio File In: `Play Mode` = Locked to Timeline.
- Match Movie File Out `fps` to project cook rate.
- YouTube: 1920x1080, h264nvgpu, yuv420, 8000 Kb/s avg.
- TikTok/IG: 1080x1920, h264nvgpu, yuv420, 10000-12000 Kb/s.
- Master/archival: ProRes 422 HQ.

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

**Rule: No list comprehensions that reference outer-scope variables — use explicit for loops.**

List comprehensions in `td_execute_python` cannot reliably reference variables defined in the same script block outside the comprehension. Use explicit for loops instead, or define everything inside a function.

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

## Feedback Loop — Agent Self-Improvement

The `td-save` skill handles this automatically. Findings are appended to `working/TD_BUILD_LOG.md`:
- What was built (module name, act, brief description)
- What the agent got right on first pass
- What needed manual correction (parameter values, node choices, naming)
- Any new patterns discovered

This log is the training data for improving these rules. If a correction appears 2+ times in the log, it becomes a rule in this file.
