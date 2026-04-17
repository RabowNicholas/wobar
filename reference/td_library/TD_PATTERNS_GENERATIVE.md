---
title: Generative Visual Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Abstract / non-referential visuals — noise fields, flow fields, L-systems, reaction-diffusion, fractals, SDF raymarching.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_TOP.md, TD_OPERATORS_POP.md, TD_NETWORK_VS_GLSL.md
---

# GENERATIVE VISUAL PATTERNS

Non-referential visuals built from math — no camera, no physical model, just procedural rules producing form. The most "TD-native" category.

Organized from simplest to most complex. Start with Noise; raymarching is the deep end.

---

## 1. Noise Fields

### Basic Noise TOP
```
Noise TOP (Type = Perlin, Harmonics = 3, Period = 0.5) ──► Null
```
- Perlin / Simplex / Sparse / Alligator — different looks.
- Animate via Translate XY — noise scrolls over time.
- Harmonics (octaves): 1 = smooth, 3+ = detailed.

### Time-animated noise
```
Noise TOP — Translate X expression: absTime.seconds * 0.1
```
Or use LFO CHOP → Export to Translate.

### Multi-octave noise
Layer multiple Noise TOPs at different frequencies with Composite Add / Multiply for natural fractal detail.

### Noise as displacement
```
Geometry ──► Displace TOP (displacement = Noise TOP) ──► Out
```

### Noise POP for points
```
Grid POP ──► Noise POP (affect P, amplitude 0.5) ──► Geometry COMP instance
```

---

## 2. Flow Fields

Vector field where each pixel stores a direction. Particles / points follow the field.

### GPU flow field
```
GLSL TOP outputting (vx, vy) per pixel from simplex noise + sin(time)
      ──► Null "null_flow"

Particle positions (POP Simulate) read velocity from null_flow via Attribute From Texture POP
```
- Each particle's position samples the flow field; its velocity is the field value.
- Classic organic swarm behavior.

### Curl noise flow field
- Curl(noise) produces divergence-free velocity — particles don't bunch up.
- GLSL TOP computing `curl(simplexNoise(p, t))` is ~20 lines — see `WOBAR_GLSL_PATTERNS.md`.

---

## 3. L-Systems

### L-System SOP
```
L-System SOP ──► rules: F → F+F-F-F+F (Koch curve)
              ──► Skin SOP or Sweep SOP for thickness
              ──► Render
```
- Ruleset determines fractal plant / tree geometry.
- Generate offline (cook once) and cache — high rule counts are expensive per-frame.

### Stochastic L-Systems
Random rules → organic plants. TD's L-System SOP supports stochastic rules.

---

## 4. Reaction-Diffusion

Gray-Scott model. Two chemicals react and diffuse, producing spots, stripes, organic patterns.

### GLSL TOP implementation
```
State TOP (RG = concentrations) ──► GLSL TOP (compute new state via Laplacian + reaction)
                                ──► Null ──► Feedback ──► State TOP
```
- Pure feedback + compute shader pattern.
- Parameters: Feed rate (f), Kill rate (k) — tune for spots, stripes, maze patterns.
- Run at 512² for cost; upscale for display.

### Parameters classic set
| Pattern | f | k |
|---------|---|---|
| Spots | 0.038 | 0.061 |
| Stripes | 0.029 | 0.057 |
| Maze | 0.029 | 0.062 |
| Chaos | 0.055 | 0.062 |

---

## 5. Cellular Automata

Game of Life, cyclic CAs, generalized 2D rules.

### Game of Life
```
State TOP (8-bit) ──► GLSL TOP (check 8 neighbors, apply birth/death rules)
                  ──► Feedback loop
```
- Emergent patterns from simple rules.

### Generalized CA
Vary the rules — Wireworld, Brian's Brain, cyclic CA (each pixel cycles through N colors when enough neighbors match the next color).

---

## 6. Fractals

### Mandelbrot / Julia (GLSL TOP)
```
GLSL TOP sampling complex plane ──► iterate z = z² + c, count escape iterations ──► color via Lookup TOP
```
- Classic. Tunable via zoom and center parameters.

### Fractal SOP
Built-in procedural fractal geometry.

### Iterated Function Systems (IFS)
- Implement via GLSL: each pixel does N iterations of random transforms.
- Produces Sierpinski-like fractals.

### Mandelbulb / distance fields
See SDF Raymarching below.

---

## 7. SDF Raymarching

Signed distance field raymarching — rendering implicit geometry via distance function.

### The basic setup
```
GLSL TOP with fragment shader:
  for (each pixel):
    ray = from camera through pixel
    for (i = 0; i < 128; i++):
      d = sceneDistance(ray_pos)
      if (d < 0.001) break; // hit
      ray_pos += ray_dir * d;
```

### Scene as SDF
```glsl
float scene(vec3 p) {
  float sphere = length(p) - 1.0;
  float box = max(abs(p.x), max(abs(p.y), abs(p.z))) - 0.5;
  return smin(sphere, box, 0.1);  // smooth union
}
```

### Classic SDF tricks
- `smin()` — smooth union between shapes.
- `opRep(p, c)` — infinite repetition: `mod(p, c) - 0.5*c`.
- `opTwist(p, k)` — twist space around axis.
- `opDomainWarp(p, noise)` — warp the input space with noise = organic blobs.

### Performance note
SDF raymarching is expensive. At 1280² with 128 steps per pixel, M1 will struggle. Develop at 512². Limit step count. Use temporal accumulation (feedback-based TAA) for cheaper quality.

---

## 8. Strange Attractors

Lorenz, Rössler, Thomas, Pickover — 3D chaotic attractors. Plot trajectories as point clouds.

### POP-based attractor
```
Point Generator POP (N = 10k, starting positions ~random) 
  ──► GLSL POP stage: iterate attractor equation per point
  ──► Geometry COMP instance (small dot)
```
- Each point is an independent trajectory. Paint them in.

### Feedback-TOP attractor
```
State TOP (N points encoded as RGB) ──► GLSL compute (iterate) ──► Feedback ──► display
```

---

## 9. Boids / Swarms

Three rules: alignment, cohesion, separation.

### POP Simulate-based boids
```
Point Generator POP ──► Simulate POP with:
  - Attract POP (cohesion: pull to neighbor centroid)
  - Align POP (match neighbor velocities — custom GLSL POP)
  - Repel POP (separation: push from too-close neighbors)
```
- Emergent flocking behavior.

---

## 10. Wave / Ripple Simulations

2D wave equation via feedback:
```
State TOP (RG = current, previous) ──► GLSL TOP (wave equation: next = 2*current - prev + dt²*(neighbors - 4*current))
                                    ──► Feedback ──► State TOP
```
- Drop disturbances by painting into the state TOP (audio-driven input, mouse clicks).
- Water surface, drum membrane simulation.

---

## 11. Voronoi / Delaunay

### Voronoi TOP (if present) or GLSL
```
GLSL TOP: for each pixel, find nearest seed point; color = seed's color.
```
- Seed points can be static, animated, or audio-driven.

### Voronoi POP (Triangulate POP, 2025 new)
Takes points → produces Voronoi cells or Delaunay triangulation.

---

## 12. Metaballs

### Metaball SOP
Built-in CPU isosurface.

### GPU metaballs via GLSL TOP
`field(p) = sum over metaballs of 1 / distance²`. Threshold the field for isosurface feel, or use field value as alpha.

---

## 13. Hybrid — Shader Nucleus with Node Shell

Most mature generative work:
```
[Audio + control CHOPs] ──► drive uniforms
[Noise / time TOPs] ──► drive displacement
    ↓
GLSL TOP (20–50 lines of focused math — SDF, reaction-diffusion, etc.)
    ↓
[Post stack: Level → Bloom → Chromatic → Film Grain → Out]
```
- Shader does the irreducible math.
- Everything around it is node graph for controllability.

---

## Performance Notes for Generative Work

- **Feedback-based generative (reaction-diffusion, cellular automata, wave)** is cheap per pass, expensive at full resolution. Develop at 512² before upscaling.
- **SDF raymarching** is the most expensive category. On M1 expect 20–40fps at 1024² with 100 steps.
- **POP-based generative** scales linearly with point count; 10k is comfortable, 100k stresses M1.
- **L-System SOP** re-cooks the whole geometry on param change — cache with Fix / File Out when final.

---

## Taste Notes

Generative work succeeds when:
1. **Constraints are visible.** Pure chaos looks like static. Give the viewer an anchor (a repeating shape, a color palette, a pulse).
2. **Motion has rhythm.** Tie generative motion to audio or a breath-rate LFO.
3. **Simplicity + feedback = depth.** A simple rule iterated over many frames often looks more complex than a complex single-frame computation.
4. **One technique per visual.** Don't stack raymarching + reaction-diffusion + boids in the same frame. Pick the hero technique.

---

## Reading This File

Patterns are independent — skim headers and jump to the one you're using. Pattern 13 (hybrid) is the recommended practical default.
