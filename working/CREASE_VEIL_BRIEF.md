---
title: Crease Veil — Visualizer Vision Brief
version: 1.0
created: 2026-06-15
status: vision locked, pre-build
act: 3 (ENCOUNTER)
song: crease
distinct_from: crease_sa / sa_1 (Rorschach attractor — different piece for same song)
dependencies: [[WOBAR_EMOTIONAL_REGISTER]], [[WOBAR_ACTIVE]]
---

# CREASE — Veil Visualizer (Act 3, ENCOUNTER)

Vision locked with Nick 2026-06-15. Vision-first, no tech decided yet. Build scoping is the next step.

## Premise
You are trapped behind a translucent latex membrane that fills the entire viewport. No safe side. Many small seductive lights live behind it — they read as **Other**, but they are **you** (your shadow / trauma). They press and shine through. The veil never tears, never changes. It only escalates and excites until the song ends. **No breach, no catharsis.** You sit in it.

The paradox is the core: the self perceives them as Other, but they are the self. This is never revealed literally — it is *felt*, never shown.

## Membrane
- Latex **skin**. Fixed for the entire song — never tears, never changes.
- Fills entire viewport. Near-black void in front = trapped, intimate, claustrophobic.
- Surface only visible where backlit by an entity — otherwise lost in the dark.
- Never deforms as a whole sheet — only **local dimples** where things press.

## Entities
Many **small** forms (a crowd, not one presence). Two behaviors, **both planned**:
1. **Press** — push into the latex from behind; the sheet dimples toward the viewer; at each stretched peak the latex goes **thin and bright**, light blooming through the tightest point. The stretch-bloom is the signature / money shot.
2. **Shine** — soft glow through the slack sheet, no deformation.

## Color — Flesh Law (direction A + a trace of B)
Subsurface physics: light through skin reddens (flashlight behind a hand → deep red). The veil's own material warms and reddens everything that presses through it.
- Each press = **cool halo → hot core** gradient.
- Entities carry a faint **seductive hue (magenta / violet)** that survives as a **cool rim** in the slack latex, **warming to red / orange bloom** at the tightest stretched peak.
- Cool-rim-to-hot-core gradient on each dimple = gorgeous and bodily at once.
- Seductive, beautiful, can't-look-away — NOT grotesque/repellent. The horror is the seduction.
- Cleanly distinct from Act 2's blue/teal.

## Cadence
Breathing, never constant. **Press → hold → ease → next press**, in waves tied to the music's dissonance-then-brief-resolve. Held, not chaotic. The whole field pulses with this held-release breathing.

## Build / escalation
Membrane stays constant. Entities **escalate + excite** over the song — more of them, brighter, more active, pressing harder. Ends maxed and trapped. **No release.**

## Hard rules (Act 3 register)
- HARD to look at, the way mirrors are hard.
- **Never reveal the paradox literally** — no face, no mirror-flash. The self-ness is felt, never shown.
- Premature relief = failure. Tension must be sustained.
- Held, organized — not random twinkle, not chaotic.

## Mechanic revision — 2026-06-15 (Part A build, hybrid pivot)
Literal *pressing* was tested and dropped. Reason: a luminous entity behind thin latex physically blows the peak to a flat hot patch — emission has no direction, so it washes out any 3D dome. Seductive-glow and sculpted-press are opposite lanes; glow wins → reads as hot dots, not pressure. Confirmed on screen with Nick.

**Locked mechanic = HYBRID.** Entities are **metaball masses** (smooth merging field) behind the veil. ONE field drives TWO reads:
- **Glow** (tight) — luminous cores, cool-violet rim → hot core. The seduction / lava read.
- **Swell** (broad, heavily blurred) — gentle wide dome of lit skin bulging toward viewer where a mass crowds. The tactile / trapped read. NOT crisp pokes — soft membrane bulge.
Register call: veil stays a **skin pushed at you (trapped)**, not a window you watch through. Lava motion must be directed **menacing** (slow gathering, massing, near-faces forming/dissolving — never literal) to stay Act 3, NOT chill lava-lamp.

## Mechanic revision 2 — 2026-06-16 (FELT pole — supersedes hybrid)
Hybrid swell also failed the trapped read in motion ("they just appear to move closer" = light-in-depth, not surface deforming). Root cause, reasoned from first principles: **a luminous entity is SEEN (light at distance → window → watching); a thing pressing a skin is FELT (shape imprinted in a front-lit surface → skin → trapped). Opposite perceptual cues — the glow always wins, the veil becomes a window.** We had been building the SEEN version while wanting trapped.

**LOCKED POLE = FELT.** Surface is the star, light secondary. Required cues: (1) **front raking light → sliding specular** across the swell = the #1 "solid surface close to me" cue (the whole bet — it WORKED); (2) **continuous visible lit skin** filling frame; (3) **tension wrinkles** radiating, amplified on stretched flanks; (4) entity colour = **subsurface bruise** (violet→hot) at the thinnest stretch, NOT emissive glow; (5) things behind **diffuse/smeared** until they press. Skin tone = dim desat mauve-grey latex. Entities = faint smears always (gathering dread). First pass built (move_002) — front-lit deforming skin + hot bruise pushing through reads as genuine trapped pressure; validated far better than SEEN dots.

## Open technical questions (for build scoping)
- Press deformation: real latex/displacement (POP/SOP membrane displaced by point-source pushers behind it) vs faked-in-2D (TOP displacement / normal-from-height). Stretch-thin bloom is the hard part either way.
- Subsurface warming: shader subsurface vs a height→color ramp that reddens with stretch depth.
- Many-small entity system: instanced point sources behind the sheet driving both deformation and light.
- Cadence driver: bar-clock wave envelope + audio, same family as crease_sa's block system.
