# Simulations — Summary of Setup Sequences

## UNIVERSAL PATTERN: stateful simulators all follow Initialize → Start → Play

| Module | Inputs | Outputs | Setup |
|--------|--------|---------|-------|
| SA | POP particles | POP particles | Init→Start→Play (Advect mode); Pointsupdatepop required |
| Flow | POP inj/TOP src/POP particles | TOP×3 + POP particles | Reset pulse + Advect toggle + Solvermode + Spawn or Particles In + Particlesupdatepop |
| Particle | POP particles | POP particles | Init→Start→Play; Material modes (SPH/PBF/Grains) |
| DLA | POP seed | DLA(pts/lines) + Walkers | Init→Start→Play; Updatepop required |
| DLG | (line geometry) | LineStrip POP | Init→Start→Play; Target Line Update POP feedback required |
| Physarum | POP+TOP | POP+TOP×2 | Init→Start→Play; both Particles & Trail Update feedback required |
| Soft Body | POP geo + constraints + collisions | POP+constraints+collision | Init pulse + Play toggle (no Start) |
| Mesh Fill | mesh | TOP×5 + POP×3 | Init→Start→Play |
| Shortest Path | path geometry + start/end | POP line strips + ref | One-shot, no setup sequence |
| Path Tracer | (404 — page missing) | ? | ? |

## Key insights
- The `Initialize → Start → Play` triad is THE universal POPX simulation pattern
- Every stateful sim has a `Pointsupdatepop` / `Targetupdatepop` / `Updatepop` parameter for feedback (some required, some optional)
- Step pulse for frame-by-frame when paused
- Soft Body uses `Init + Play` (no Start step) — exception
- Flow has its own pattern: Reset pulse + Advect TOGGLE + Solvermode (advect/simple)
- Path Tracer doc is 404 (page missing or moved)
