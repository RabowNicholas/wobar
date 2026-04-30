# DLA — Official Docs Extract

## Setup Sequence
1. Initialize (pulse) — reset & seed
2. Start (pulse) — begin from initialized state
3. Play (toggle) — continuous simulation
4. Step (pulse) — frame-by-frame

## Parameters
- Target Random Walkers (Updatepop) — POP node ref
- Simulation Bounds (Simbounds x/y/z)
- Display Bounds / Random Walkers / DLA Structure (Points/Lines)
- Max Number of Points (Maxpoints)
- Seed
- Max Search Distance (Maxsearchdist) — branch density
- Attach Distance (Attachdist) — stickiness threshold
- Attach Strength (Attachstrength)
- Max Neighbors
- Internal Noise (toggle), Noise Amplitude

## Outputs
- Output 0: DLA Structure (Points)
- Output 1: DLA Structure (Lines)
- Output 2: Random Walkers

## Gotchas
- Requires POP seed input
- Max Search Distance affects visual density significantly
- Smaller Attach Distance = finer detail but slower growth
