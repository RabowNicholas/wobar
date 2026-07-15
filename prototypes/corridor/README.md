---
title: Corridor Prototypes — WebGL look-dev
version: 1.0
last_updated: 2026-07-14
status: live
scope: WebGL/Shadertoy look-dev sketches for the corridor spine. Prototype here, port to glslTOP. Governed by [[working/WOBAR_VISUAL_RESET]] §3.
dependencies: [[working/WOBAR_VISUAL_RESET]], [[reference/WOBAR_WORLD]], [[reference/WOBAR_TD_REFERENCE]]
---

# CORRIDOR PROTOTYPES

Look-dev happens **here**, not in TouchDesigner. A WebGL sketch iterates in seconds
and puts judgment minutes into a session instead of hours. Only port to `glslTOP`
once the geometry reads. Established 2026-07-14 after five prior WOBAR pieces each
got built ground-up in TD and each landed at v0.

Open the `.html` directly in a browser. No build, no deps, no server.

---

## `corridor_v5_superposition.html` — the approved collapse mechanic

**Nick, 2026-07-14: "this is closer. this concept is approaching what i see"** and
**"i actually like this more than my original idea."** First approved collapse in six
attempts. Live artifact: https://claude.ai/code/artifact/b9994a61-e477-40fc-afa6-65e1f12606fb

### What it does

Four copies of the **same** corridor, 4-fold rotationally symmetric, laterally
offset, **superposed** — each raymarched independently and composited by weight.
The stable corridor (weight 1) is the reading perception committed to; the other
three are always present at weight 0. **The collapse is the weights equalizing**
until all four sit at ¼ and none of them is the corridor. Nothing is created —
perception stops being able to prefer one. This is WORLD §4's *uncollapsed*, built.

### The four rules it proved

1. **NO SDF BOOLEANS. Ever.** Every combine operator — `min`, `max`, `smin` — takes
   N fields and returns **one surface**. Resolving is its entire job, and resolving
   is precisely what must not happen. **The corridors never meet in the field. They
   meet only in the composite.** This is the whole find; five versions failed on it.
2. **Superposition, not union.** Union carves a shared volume → one connected space
   → a cave → arrival (banned). Superposition overlays: the same space *is* corridor
   A and B and C at once, none occluding, none more real.
3. **Symmetry, not asymmetry** (Nick's call). Arbitrary angles produce soup.
   Symmetric offsets **interfere**, and interference is legible — it reads as
   architecture. Escher's impossible geometry is highly symmetric; the symmetry is
   what makes it readable as impossible rather than as mush. The *arrangement* is
   clean symmetry while the *mirror* stays imperfect at 0.88 (K3) — different axes,
   no conflict with the anti-kaleidoscope rule.
4. **The offset is the geometry.** It is the primary artistic knob, not the collapse.

### The emergent find — the convergence point

The four stay **parallel**, so they share **one vanishing point**. They coincide
exactly at the convergence and diverge everywhere else: **sharp at the center,
multiplied at the edges.**

**The four only agree at the point you can't reach.** Everything visible is
uncertain; the only certain thing is the one you never get to. Four contradictory
readings of the path, one unanimous destination — the understanding fractures into
four and all four still point at the same real thing.

This also **answers the hint** (VISUAL_RESET §3, previously open): the convergence
point *is* the hint. Not a light or a door bolted onto the end — just where the
readings agree. Nothing added.

⚠️ **Do not give the four different recession axes.** Different axes → different
vanishing points → the convergence is destroyed. Claude proposed exactly this and
was about to ship it; Nick caught it. The parallelism is load-bearing.

### Not in this build (deliberately)

- **Scale nesting / self-similarity.** Nick's original note was *"fractal off into
  multiple dimensions"*; v5 is four copies at **one** scale — multiple, not fractal.
  He then preferred v5 to his own idea, so this is **parked, not owed.**
- **Multi-axis recession.** Actively ruled out — see the warning above.
- **Audio.** Geometry only, per the workflow.

### Knobs

`offset` (0.60 — the geometry) · `collapse` (auto-loops; toggle off to scrub by
hand) · `scroll` · `mirror` (0.88, K3) · `grain` · `fog`. The loop runs
stable → floor falls out (~0.5s) → cannot be held → snaps back, and never returns
fully to zero: each pass leaves a higher floor. fps readout bottom-right — four
marches is 4× cost, so fbm runs 3 octaves; at collapse 0 only one march runs.

---

## Dead ends — recorded so they are not re-derived

Five failed collapse mechanics, all Claude-proposed, all rejected by Nick. Every
geometric one failed for the **same** reason: it used a boolean, and booleans resolve.

| # | Mechanic | Nick's verdict | Why it failed |
|---|---|---|---|
| v0 | twist + fold + fbm ramp | *"never falls out, just becomes a more organic corridor"* | All three are **continuous deformations**. A twisted, folded, rough corridor is still a corridor. Deformation can only ever produce *organic*. Also faded over ~2.7s — a slow fade **is** a morph, so the organic read was baked into the timing too. And ramping fbm made "collapsed" literally mean "more texture." |
| v1 | 2nd corridor at 34° + fog/AO killed | *"collapses into pure chaos that looks like nothing"* | Killing the depth cues flattened it. Also a real bug: `min()` of two fbm-eaten fields is not a valid SDF, so the marcher over-stepped and returned genuine noise. |
| v2 | 90° 2nd corridor + perspective→orthographic | (superseded) | The ortho idea was **Claude's own, unasked-for**, layered on top of Nick's direction. Dropped. |
| v3 | KIFS-style fractal branching, `min()` | *"collapse immediately implodes on itself"* | **Sign error, three versions deep.** The field is **inside-positive** (`d = -box2`, so `d>0` means in the air). For an inside-positive field **union is `max`, not `min`**. `min` is *intersection* — it carved the space down to the region inside every corridor at once, which shrinks to nothing the moment a second corridor exists. |
| v4 | same, `max()` | *"now collapse does nothing"* | Correct union — and it changes nothing, because unioning distant air doesn't move corridor A's walls. **`min` imploded, `max` did nothing: the same lesson twice.** Booleans resolve. No parameter tweak was ever going to fix it. |

**Method note.** Claude went 0-for-5 on the collapse mechanic and 0-for-4 on the
aesthetic calls before it (skin / time-made-spatial / the mark / the act mapping).
Every load-bearing idea in this file came from Nick in one or two sentences —
*"the corridor is my limited understanding of higher dimensions trying to resolve
it,"* *"stable at the beginning… allows the floor to fall out,"* *"a number of
corridors all existing in the same space,"* *"symmetry will provide clean
geometrical patterns."* Claude also twice theorized elaborately over what turned
out to be a one-character sign error. See memory `feedback_creative_direction`.
The working loop that produced this: **Nick reacts to pixels, Claude builds, Claude
does not theorize in between.**
