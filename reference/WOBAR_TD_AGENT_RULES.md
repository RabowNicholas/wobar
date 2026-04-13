---
title: TouchDesigner Agent Build Rules
version: 1.0
last_updated: 2026-04-12
status: locked
scope: Conventions any AI agent must follow when creating or modifying TouchDesigner networks in the WOBAR project. Read before any TD build action.
dependencies: [[WOBAR_CONTEXT]], [[reference/WOBAR_TD_REFERENCE]], [[reference/WOBAR_FRAMEWORK]]
---

# TOUCHDESIGNER AGENT BUILD RULES

Rules for any AI agent (Claude Code + TWOZERO MCP, or any future TD automation) building or modifying networks in the WOBAR project. These are non-negotiable conventions. If a rule here conflicts with a default behavior, the rule wins.

---

## Version Control — Save Before You Change

**Non-negotiable. No exceptions.**

Before any structural change to a visual module — new node, rewire, blend mode change, pixel format change, or anything that affects the signal chain — save a .tox snapshot first.

**Save procedure:**
```python
op('/project1/base_act2').saveToFile(
    '/Users/nicholasrabow/Desktop/wobar/wobar/touchdesigner/base_act2/base_act2_v001.tox'
)
```

**Naming:** `[module]_v[NNN].tox` — sequential, zero-padded to 3 digits. Never skip a version number.

**Log the entry immediately** in `touchdesigner/[module]/CHANGE_LOG.md`:
- What the visual looks like at save time (STATE)
- What change is about to be made (WHAT)
- What to reload to undo (UNDO: reload previous .tox)

**Parameter-only changes** (no structural change) do not require a new .tox — log old/new values in CHANGE_LOG.md only.

**File storage:** `wobar/touchdesigner/[module]/` — one subfolder per visual module, .tox files + CHANGE_LOG.md inside.

If you did not save a .tox before a change and the visual breaks, say so explicitly. Do not attempt to fix forward through multiple changes. Stop and acknowledge the missing checkpoint.

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

## Color System

Base palette is purple. Every visual passes through:
```
[Source] -> HSV Adjust TOP (satmult 0.15) -> Level TOP -> Lookup TOP <- Ramp TOP (1024x1)
```

Act-specific accents are additive layers, not replacements of the base palette. See WOBAR_TD_REFERENCE.md Section 4 for exact RGB values per act.

**Act 3 rule**: no warm colors. Zero. Not "mostly cool with a hint of warmth." Zero warm.

---

## Act Constraints (Build Validation)

Before delivering any build, validate against these. If a build violates its act constraint, fix it before presenting.

| Act | Required | Forbidden |
|-----|----------|-----------|
| 1 | Circles, warm purple glow, breath rhythm 60-80 BPM | Sharp geometry, aggressive motion, cool colors |
| 2 | Inward spiral, depth, tightening with audio | Outward expansion, warm colors dominating, flat motion |
| 3 | Tunnel, 85-90% mirror (not 100%), infinite depth, glitch on peaks | Emotional relief, warm/orange tones, perfect symmetry |
| 4 | Outward radial expansion, full color palette, rhythm | Inward motion, cool-only palette, unrhythmic chaos |
| 5 | Circle returns, portal closing, breath rhythm returns | New visual concepts — this is callback to Act 1 |

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

## Feedback Loop — Agent Self-Improvement

After every build session, append findings to `working/TD_BUILD_LOG.md`:
- What was built (module name, act, brief description)
- What the agent got right on first pass
- What needed manual correction (parameter values, node choices, naming)
- Any new patterns discovered

This log is the training data for improving these rules. If a correction appears 2+ times in the log, it becomes a rule in this file.
