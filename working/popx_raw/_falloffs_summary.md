# Falloffs — Summary

## Falloff sources (write popxFalloff or custom Output Falloff Attribute)
| Module | Source type | Key params |
|--------|-------------|-----------|
| Texture Falloff | TOP sample | UVW lookup attr (default P), extend modes, normalization |
| Shape Falloff | Geometric primitive distance field | Sphere/Box/Torus/Tube(infinite/capped/rounded)/Capsule/Plane(X/Y/Z)/Parabola/LineProjection |
| Object Falloff | Arbitrary 3D mesh proximity | Object geometry, Area of Influence (inside/outside/surface dist), transforms |
| Curve Falloff | Distance from curve | Curve geometry, modes (distance/distance×position/normalized position), min/max dist |
| Noise Falloff | Procedural noise | Perlin/Simplex 2D-4D, period, harmonics, amplitude, transform |
| Paint Falloff | Interactive viewport painting | Paint Mode toggle, brush size, transition range |
| Infection Falloff | Simulation — radius/connectivity spread from seeds | **Init→Start→Play**, infection rate, dissipation, reinfection |
| Spread Falloff | Non-sim wave propagation through neighbors | Spread By (radius/connectivity), search radius, seed config — direct (no Init/Play) |

## Falloff transformers (modify existing falloff)
| Module | What it does |
|--------|-------------|
| Attribute Falloff | Convert ANY point attribute → falloff (incl point index) |
| Remap Falloff | Fit/Clamp/Absolute/Invert/Ramp transform of existing falloff |
| Combine Falloff | Stack & blend multiple falloffs with gain controls |

## Cross-module conventions
- **Output Falloff Attribute** — name of attr where final values stored (default `popxFalloff`)
- **Combine Operation** — how to merge with existing falloff: add, subtract, multiply, divide, screen, overlay, max, min, set
- **Combine Strength** — gain on the merge
- **Preview Falloff** — toggle viewport visualization
- **Falloff Ramp presets** — heatmap, blackbody, infrared, custom
- Most falloffs have **Remap page** — fit/clamp/invert/curve

## Critical insight
- **Infection Falloff is the ONLY simulating falloff** — needs Init→Start→Play
- Spread Falloff looks similar but is direct (no simulation)
