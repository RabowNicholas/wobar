# CHANGE LOG — mycelium_chamber

DLA-on-surface POPX experiment — second WOBAR-on-brand POPX primitive after `attractor_chamber`. Form: branching mycelium-style network growing on the surface of an invisible sphere. Tests whether *accumulating growth* (DLA) lands as a complementary register to *continuous flow* (SA Aizawa).

TD location: `/project1`

---

## v001 — In progress (2026-05-01)

**Plan:** `~/.claude/plans/sorted-snacking-moon.md`

**Three design choices set at planning:**
1. Substrate sphere INVISIBLE — pure math constraint, only the network renders. Cosmic feel.
2. Render as thread-tubes (sweepPOP) — true hyphae, not beaded points.
3. Fresh build — no scaffold cloning from `attractor_chamber`. Every op chosen for this form.

**Architecture (target):**
```
seed_pop (1-5 pts on sphere surface)
  → dla_grow (POPX DLA, Walkersupdatepop=proj_sphere)
  → proj_sphere (P_new = normalize(P) * R)
  → null_pop_out
  → sweep_tubes (thin tubes through DLA points)
  → geo_mycelium (geo COMP + pbrMAT cream organic)
  → render → bloom → grain → null_out → rec_out
```

**Single audio binding:** `dla_grow.Stepsperframe = floor + ceil * max(0, energy)^exp` (same `max(0, …)` clamp pattern as `attractor_chamber`).

**Build status:** workspace folder created, CHANGE_LOG drafted. TD build pending — Nick is taking it one step at a time.

---
