# Particle — Official Docs Extract

## Solver Modes
- Simple: Direct particle integration
- Advect: Advanced advection with feedback

## Material Modes
- Fluids-SPH: Smoothed Particle Hydrodynamics (liquid)
- Fluids-PBF: Position Based Fluids
- Grains: Granular materials (sand/debris)

## Setup Sequence
1. Initialize (pulse) — Reset & spawn
2. Start (pulse) — Begin
3. Play (toggle) — Continuous simulation
4. Step (pulse) — Frame-by-frame when paused

## Core Parameter Categories
- Solver: Substeps, Iterations, Time Scale, Timestep(RO)
- Interaction: Smoothing Radius, Distribution (Default/Closest), Num Hash Buckets, Max Neighbors
- Physics: Target Density, Pressure Multiplier, Viscosity
- Collisions: None/POP/Box/Plane/Sphere/Torus/3D-SDF/2D-SDF/T3D/T2D
- Forces: Gravity vector, Velocity/Collision Damping, Static Threshold, Dynamic Scale

## Mode-specific
- PBF: Cohesion, Surface Tension, Adhesion
- Grains: Repulsion Weight, Attraction Weight

## Ports
- Input: POP (Particles In)
- Output: POP (Particles Out)

## Gotchas
- Target Particles ref creates intentional feedback loop for re-injection
- Timestep RO; use Time Scale
- Collision Damping = geometry contact only
