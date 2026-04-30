# Modifiers — Summary

## Modules requiring Initialize → Start → Play (Advect mode):
- **Spring Modifier** — when "Other" mode + Pointsupdatepop set (creates feedback loop)
- **Noise Modifier** — when "Advect" mode (vs "Simple"); has Init/Start/Play/Step
- **Move Along Curve** — when "Solver" mode (vs "Simple"/"Goal")
- **Relax** — when "Advect" mode; needs Pointsupdatepop

## Stateless modifiers (no setup pulses):
- Aim, Color Modifier, Magnetize (?), Move Along Mesh, Pivot, Randomize, Transform Modifier
- Note: Magnetize has Solvermode (Simple/Advect) — Advect mode probably also requires sequence

## Key parameters table

| Module | Critical Params | Output Attr |
|--------|----------------|-------------|
| Aim | Aim Method (vector/object/points), Aim Axis, Up Method/Axis, Constrain Around Up | (modifies Rotate) |
| Color Modifier | Falloff Attribute, Color Ramp | (modifies Color) |
| Magnetize | Search Radius, Force Mode (Repulse/Attract/Spin), Per-magnet attrs (P/radius/strength/exponent/mode/spindir/contain) | optional outputforceattr/weightattr |
| Move Along Curve | Mode (Simple/Solver/Goal), Goal, Speed, Lock to Curve, Wrap | — |
| Move Along Mesh | Attach Mode, Speed/Lifetime, Relaxation iterations | — |
| Noise Modifier | Mode (Simple/Advect), Curlnoise, Output Noise Attribute | optional Noise attr |
| Pivot | Mode (Center/Align-to-BBox/Shift/Set-Local/Set-World), Alignment Side (-X/+X/-Y/+Y/-Z/+Z), Pivot Only | — |
| Randomize | Position/Rotation/Scale/Color/Custom modes (Add/Set/Multiply/Replace), independent seeds | — |
| Relax | Method (Neighbor/Field), Iterations, Strength, Max Radius, Point Radius Scale | optional force attr |
| Spring Modifier | Position/Rotation/Scale toggles, Other+Attr, Mass/Spring/Damping; Use Mass Attribute | — |
| Transform Modifier | T/R/S/P, Rotate Order, Scale modes (Add/Set), Local Space, Do Falloff | — |

## Cross-module conventions
- **Do Falloff + Falloff Attribute** appears on most modifiers — the universal per-instance gating mechanism
- **Bypass** parameter passes input unchanged
- **Render Primitives** toggle: geometry vs point-only display
