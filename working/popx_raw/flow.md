# Flow — Official Docs Extract

## Setup Sequence (Particle Simulation)
1. Connect inputs: POP→Input 0 (injection), TOP→Input 1 (source), POP→Input 2 (particles in)
2. **Enable Advect toggle** (SEPARATE from Solvermode)
3. **Set Solvermode**: 'simple' or 'advect'
4. **Enable Spawn** (or provide Particles In via Input 2)
5. Configure particle behavior (Numparticles, Lifespan, Lookupcolor)
6. **Reference downstream POP in Particlesupdatepop**
7. Pulse Reset to initialize; Timescale controls evolution

## Solvermode
- 'simple': basic particle motion without advanced advection
- 'advect': particles advected by fluid velocity field (smoke trails, ember effects)

## CRITICAL: Advect Toggle ≠ Solvermode='advect'
Both must be configured. Solvermode selects algorithm; Advect TOGGLE enables the particle advection feature.

## Outputs
- Output 0 (TOP): Substance/density
- Output 1 (TOP): Velocity
- Output 2 (TOP): Temperature
- **Output 3 (POP): Particles Out** ← what to render

## Inject + Injectionpop
- Inject toggle: enable substance injection
- Injectionpop: POP source for injection (uses P + optional scale/gain/strength/temp/Cd attrs)
- Fallback if no Injectionpop: uses Injectpos parameter

## Spawn vs Numparticles
- Spawn toggle: spawns particles where substance density > Threshold
- Numparticles: MAX spawnable per frame
- Maxattempts: placement attempts before stopping
- Densityscale: spawn detection resolution (lower = faster)

## Gotchas
- Timestep is READ-ONLY (tied to TD FPS); use Timescale for control
- Solvermode ≠ Advect toggle (both required)
- Particles need EITHER Particles In (Input 2) OR Spawn + Particlesupdatepop ref
- 32-bit precision more accurate but heavier
- No particles spawn if density below Threshold

## All Parameters (key ones)
Reset, Timescale, Timestep(RO), Simbounds, Maxaxisres, Precision, Veldissipation, 
Pressureiters, Viscosity, Diffusioniters, Vorticity, Dissipation, Colordissipation,
Inject, Injectionpop, Injectpos, Injectscale, Injectgain, Injectstrength, Injecttemp, Injectcolor,
Addsource, Substancegain, Forcestrength, Temperaturegain,
Applybuoyancy, Buoyancystrength, Gasweight, Coolingrate, Expansion,
Applygravity, Gravityvector(0,-1,0), Gravitystrength, Surfacelevel,
Addexternalforce, Externalforcetop, Extforcestrength,
Addopticalflowforce, Opticalflowtop, Optiflowforcestrength,
Boundstop, Showbounds, Obstacletop, Renderobstacle, Obstacleopacity,
**Advect**, **Solvermode**, Particlesupdatepop, Advectionstep,
Spawn, Numparticles, Densityscale, Threshold, Seed, Maxattempts,
Enableparticlelife, Lifespan, Lifevariance, Lifeseed, Lookupcolor,
Channelmask, Fromlow/high, Tolow/high, Matchtot3d, Freeextragpumem
