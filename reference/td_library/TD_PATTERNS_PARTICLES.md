---
title: Particle System Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Particle systems via POPs (2025 preferred), legacy Particle SOP notes, emission patterns, forces, lifespan.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_POP.md, TD_PATTERNS_INSTANCING.md
---

# PARTICLE SYSTEM PATTERNS

Particles — emitted points with position, velocity, age, and death. The 2025 POP family is the modern path; Particle SOP remains for legacy / small systems.

---

## POP-Based Particle System (Preferred)

### Minimal emit-simulate-render chain
```
Point Generator POP (emit N points per second with random velocities)
  ──► Simulate POP
        │
        ├── Force POPs (Gravity, Wind, Drag)
        └── Collide POP (optional)
  ──► Lifespan POP (age out old particles)
  ──► Geometry COMP instance (small glowing quad with Point Sprite MAT)
```

### Key operators
- **Point Generator POP** — emitter. Set Rate (pts/sec), Initial velocity range, Position range.
- **Simulate POP** — runs the per-frame physics: integrates velocity into position, applies forces.
- **Force POPs** — Gravity, Wind, Vortex, Attract, Turbulence, Drag. Combine for compound behavior.
- **Lifespan POP** — increments @age each step; deletes when @age > @lifetime.
- **Geometry COMP instance** — renders each particle as a template.

---

## Emission Patterns

### Continuous emission
Point Generator POP with Rate > 0 — emits continuously.

### Burst emission
Trigger-based — on audio onset, emit N particles at once.
```
Pulse (from Trigger CHOP) ──► Point Generator POP Rate (burst 1000 for 1 frame)
```

### Spatial emission
- **From a surface**: Sprinkle POP on a host SOP → particles start at scatter points.
- **From a curve**: Line POP / Curve POP → particles emit along the line.
- **From an image**: Trace POP → particles trace the image silhouette.
- **From a volume**: Box POP or Sphere POP distributing inside the volume.

### Position + velocity inheritance
```
Emitter geometry (e.g., moving spaceship) → Sprinkle POP from its surface
  → particles inherit spaceship's velocity via Attribute Copy POP
```

---

## Force Patterns

### Gravity (constant downward)
```
Gravity POP (direction = (0, -9.81, 0), strength = 1.0)
```

### Wind (directional)
```
Wind POP (direction = (1, 0, 0), strength animated by Noise)
```

### Vortex (spiral)
```
Vortex POP (axis, strength, falloff)
```
- Particles orbit the axis.

### Attraction
```
Attract POP (target = Null COMP position, strength, radius)
```
- Particles pulled toward a point. Negative strength = repel.

### Turbulence (noise field)
```
Turbulence POP (frequency, amplitude, octaves)
```
- Organic jitter — essential for natural-looking particle motion.

### Drag
```
Drag POP (strength 0.1–1.0)
```
- Damps velocity over time. Without drag, wind / vortex accumulates into chaos.

### Compound force field
```
Simulate POP
  ├── Gravity POP
  ├── Turbulence POP
  ├── Vortex POP
  └── Drag POP (slight)
```
Layered forces → rich emergent motion.

---

## Lifespan and Aging

### Per-particle age
Lifespan POP automatically manages:
- @age (current age in seconds)
- @lifetime (random per particle, set at emission)
- Removes when @age > @lifetime.

### Color/scale over lifetime
```
Lifespan POP ──► Attribute POP (
  @Cd = mix(startColor, endColor, @age / @lifetime)
  @pscale = mix(startScale, endScale, @age / @lifetime)
)
```
- Fade from bright to dark; grow or shrink with age.

### Alpha fade
```
Attribute POP (@alpha = 1 - (@age / @lifetime))
```
Used with Constant MAT + alpha for transparent fade-out.

---

## Rendering Particles

### Point Sprite MAT (cheapest)
Billboarded quad facing camera. Texture is a glow or particle sprite.
```
Geometry COMP:
  - Template SOP: empty (Point Sprite handles the geometry)
  - Material: Point Sprite MAT (texture = glow.png)
  - Instance tab: POP with @P, @Cd, @pscale, @alpha
```

### Instanced mesh (detailed)
Template SOP = small mesh (cube, flake, snowflake).
- More expensive per particle but richer look.

### Line trails (Trail POP)
Render previous positions as lines:
```
Simulate POP ──► Trail POP (length 30 samples)
             ──► Geometry COMP instance with line template
```

---

## Common Particle Patterns

### Pattern 1 — Dust motes
```
Point Generator POP (continuous emit, volume = scene bounds)
  ──► Simulate POP
        ├── Turbulence POP (low amplitude)
        └── Drag POP (high — slow drift)
  ──► Attribute POP (@alpha = random 0.1–0.3)
  ──► Geometry COMP instance (Point Sprite, soft glow tex)
```

### Pattern 2 — Sparks
```
Burst emit (on trigger) at emit position
  ──► Simulate POP
        ├── Gravity POP
        ├── Initial random velocity spread
        └── Drag POP (medium)
  ──► Lifespan POP (0.5s lifetime)
  ──► Attribute POP (@Cd fades from white-hot to red to black)
  ──► Geometry COMP instance (Point Sprite, bright)
```

### Pattern 3 — Explosion
```
Burst emit from point, 1000 particles with radial initial velocity
  ──► Simulate POP
        ├── Drag POP (high — slow from speed quickly)
        └── Turbulence POP
  ──► Trail POP (streak trails)
  ──► Lifespan POP
  ──► Geometry COMP instance (Point Sprite)
```

### Pattern 4 — Snow
```
Continuous emit at high y, over large XZ area
  ──► Simulate POP
        ├── Gravity POP (gentle)
        └── Turbulence POP (XZ drift)
  ──► Attribute POP (@pscale random 0.5–1.5)
  ──► Lifespan POP (long — reach ground)
  ──► Geometry COMP instance (Point Sprite, snowflake tex)
```

### Pattern 5 — Audio-reactive sparks on kick
```
null_kick_trigger ──► fires emit burst
Point Generator POP with burst rate tied to trigger
  ──► Simulate POP with audio-driven force strengths
  ──► Trail POP
  ──► Geometry COMP instance
```

### Pattern 6 — Image-source particles
```
Trace POP (input = logo) → 5000 points in logo silhouette
  ──► Attribute From Texture POP (color from logo pixels)
  ──► Simulate POP with Attract POP (pull back to original position + turbulence)
  ──► Geometry COMP instance (Point Sprite)
```
- Logo "breathes" or "disintegrates" based on attract strength.

### Pattern 7 — Flock / swarm
```
Point Generator POP (initial positions random in volume)
  ──► Simulate POP with:
        ├── Align POP (velocities match neighbors) [may need GLSL POP]
        ├── Attract POP (centroid pull)
        ├── Repel POP (too-close separation)
        └── Drag POP
  ──► Geometry COMP instance (small arrow or streak)
```
Boids behavior.

---

## Performance

- **POP particle systems handle 10–50k particles comfortably on M1.**
- **100k+** stresses M1; test specifically, reduce template complexity.
- **Trail POP** cost scales with trail length × particle count. Keep trails short.
- **Collide POP** against complex meshes is expensive. Use low-poly collision proxies.
- **GPU instance rendering is cheap** — template complexity is the bottleneck more than count.

---

## Particle SOP (Legacy)

Particle SOP still works and is fine for small systems (<1000 particles):
```
Particle SOP ──► Sources (emitters), Forces, Lifespan params in one op
```
- Simpler setup than POP chain for quick prototyping.
- CPU-bound — avoid for 1000+ particles per frame.

**Default modern path: POPs.**

---

## Debugging Particle Systems

- **Zero particles visible**: emit rate is 0, or Geometry COMP instance isn't wired to POP, or template has no mesh.
- **Particles all at origin**: positions aren't being emitted correctly — check Point Generator POP's Position parameters.
- **Particles fly off infinitely**: no Drag or Lifespan — add both.
- **All same color**: @Cd not being set per-particle. Check Attribute POP creating Cd.
- **Performance drops**: template too complex, or trail too long, or collide too expensive.

---

## Reading This File

Start with Minimal chain and key operators. Emission / Force / Lifespan / Rendering sections are independent — read what applies. Common Particle Patterns are recipes to fork.
