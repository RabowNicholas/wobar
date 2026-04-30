# SA (Strange Attractor) — Official Docs Extract

## Solver Modes
- **Simple**: Computes velocity vectors, stores in PartVel attribute. NO position update.
- **Advect**: Updates positions over time with full simulation controls.

## Animation Setup Sequence (Advect Mode) — REQUIRED
1. **Initialize** (pulse) — Reset and spawn particles
2. **Start** (pulse) — Begin from initialized state
3. **Play** (toggle) — Enable continuous playback
4. **Step** (pulse) — Advance one frame when paused

## Key Parameters & Defaults
- Solver Mode (dropdown): Simple/Advect
- Strange Attractor (dropdown): Lorenz, Aizawa, Thomas, Halvorsen, Dadras, Chen, Rossler, Sprott, Four-Wing, Nose-Hoover, Custom
- Time Scale (float): Global speed multiplier
- uA–uF (float): Coefficient scale factors (availability varies by attractor)
- Custom SA (DAT ref)
- Target Points Update POP — REQUIRED in Advect mode

## Boundary Controls (Per-Axis)
- Minimum/Maximum Type: Off, Clamp, Loop, Zig Zag
- Min/Max Values: XYZ bounds

## Ports
- Input: POP (Particles In)
- Output: POP (Particles Out)

## Critical Gotchas
- **Advect mode REQUIRES Target Points Update POP** — without it integration won't run continuously
- Custom attractors need DAT reference; "Generate Script DAT" creates templates
- Boundary controls apply independently to X, Y, Z axes
- Simple mode does NOT animate positions — only writes PartVel
