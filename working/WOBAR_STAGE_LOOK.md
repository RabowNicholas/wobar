---
title: Wobar Stage Look — the costume test and the chest piece
version: 0.1 (opened 2026-10-05)
last_updated: 2026-10-05
status: live
scope: How Nick reads on stage, in footage and in press — the personal signature the brand audit never built. Owns the stage-look decisions and the chest-piece design rules. Not the visualizer (WOBAR_VISUAL_RESET) and not the mark itself (locked in WOBAR_BRAND / WOBAR_WORLD §9).
dependencies: [[reference/WOBAR_BRAND]] · [[reference/WOBAR_WORLD]] §4 · [[working/WOBAR_SOCIAL_PLAN]] §3.6
---

# WOBAR STAGE LOOK

## 1. Why this file exists

The test is Chris Alba's: **could a stranger costume as you and be recognised.** The 2026-09-01 brand audit (Phase 6) skipped it on the grounds that *"the entity is deliberately faceless, so there's no personal styling to costume."* That reasoning rested on a rule WORLD §4 had already lifted on 2026-08-04 — **the entity is faceless; Nick is not.** The test applies to Nick and was never run.

**The rail that governs everything below (WORLD §4):** a face in frame is permitted, a personality being sold is not. The signature carries **the world (the mark)**, never a character or a persona prop.

## 2. The base — what Nick already wears

Long curly hair · very baggy cargos · combat boots · oversized tee, long-sleeve, or a tight tank.

**Verdict: authentic, not iconic.** It is the default uniform of a large share of any bass crowd — a fan dressed this way reads as *a guy at a bass show*. It is the base, not the signature. Its value is that it is true (nothing manufactured — belief 8, the enemy).

**Decided:**
- **Hair down on stage, always.** The ponytail is for studio and daytime. Rooms are dark with the screen behind, so the crowd reads silhouette, not face — a backlit curly mane is a silhouette; a ponytail is not.
- **The uniform stops varying.** Same cut, same boots, same top type. Recognition is built by repetition.
- **A light top, not black.** Black on a near-black/purple visualizer disappears — the same failure as SOCIAL_PLAN §3.6's dark-on-black legibility constraint. Bone, ash or lichen sage (the sage mesh top in the 2026-10-05 test photo already proves it).
- Fabric follows BRAND's Texture & Finish: matte, washed, earthy, never neon.

## 3. The signature — the chest piece

**One object, and it is the mark.** The hair and clothes say *Nick*; the mark says *Wobar*. The combination is unownable by anyone else and survives a press photo.

**Private shorthand: "Tarzan meets Iron Man."** It is the HOHLWEG cover on a body — a built object inside the wild — and it maps onto the archetype pair (Magician lives in the dark; Creator built the thing on his chest). **Never in public copy, bio or press** — it turns the look into a reference to other people's characters.

### Design rules

| Rule | Why |
|---|---|
| **Metal plate with the mark cut *through* it as slots; light behind.** The glowing shape *is* the mark | A fully lit disc is the arc reactor. The light forms the broken rings |
| **LED, not polished metal** | Reflection depends on venue front-light (often none) and returns random glints, not a shape. Self-lit is the only consistent version — and the fan version needs it |
| Matte aged metal overall, **only cut edges and high points brushed bright** | Edges outline the mark under camera flash; LEDs carry the stage. TEXTURE: matte, reflective only at mirror moments |
| **Warm light — amber/bone. Never cyan or ice-blue** | At crowd distance colour is the *only* thing separating this from Iron Man. Hard line |
| Slow attack/release, swells with the low end, never strobes | Bioluminescence, not LED (TEXTURE); the enemy at the scale of a light |
| **~10cm diameter** | See §4 |
| Short thick leather cord + back strap, worn high at the sternum. **No chain, no beads** | A chain swings and flips over the decks. Beads read kandi |
| **Mark geometry exactly as locked** — gaps not widened | See §5 |

### The read at two distances (the Rezz-goggles model)
- **In the room:** *the light on his chest.* Position and glow are the signature; the logo does not need to resolve. Brightness and diffusion matter more than size.
- **Up close — phone video, press, thumbnails, a costume:** the mark resolves. This is where the costume test is actually judged.

At distance a glowing chest will always rhyme with an arc reactor. **Accepted** — context (hair, booth, bass show) disambiguates, the costume is judged up close where it is unmistakable, and warm colour holds the distance read.

### Material direction (round 1 renders, 2026-10-05)
- **B — The Forge: out.** Rivets, bail and centre disc are the most arc-reactor of the three.
- **A — The Relic:** best material — verdigris copper reads *excavated artifact*, unlike anything in the scene. Textured centre too busy.
- **C — The Void:** best legibility — clean face, the mark is the only thing. Violet reads LED/tech.
- **Leading: A's material + C's clean face + warm amber.** Not locked.

### Signature show moment
Everything goes dark except the mark, breathing with the sub. Placement in the arc is Nick's call, unmade.

## 4. Scale — 10cm, not 13

Initially specced at 13cm for crowd legibility of the logo. **Revised:** the crowd only needs one warm light at the chest; the mark has to resolve in front-row video, press and thumbnails. ~10cm does that, stays a wearable fashion piece rather than armour, and is lighter on the cord. Confirm with the cardboard test (§6).

## 5. The mark at 10cm — from `assets/brand/SVG/logo-black1080.svg`

- Outer ring ~82mm across, **4mm slot** (stroke 40/1000)
- Inner ring ~66mm across, **2mm slot** (stroke 20/1000) — glows dimmer, by design of the mark
- Both breaks ~6° of arc → **~4mm of solid metal bridge.** The breaks are what make it stencil-cuttable: a closed ring would drop its centre
- **The SVG is strokes.** Cutting services need closed outlines → Illustrator, Outline Stroke, export DXF

*Correction on record:* widening the gaps for distance legibility was proposed and withdrawn the same session — the mark is locked and never varies.

## 6. Prototype path

0. **Cardboard at 10cm**, phone light behind, filmed in the dark from 15–20m.
1. **v0 — commission.** Light-up logo pendants already exist as fan merch (a 3D-printed A State of Trance piece was the reference, 2026-10-05: square box, logo cutout, LED behind, bead cord). Architecture is identical. Brief a maker: round, ~10cm, warm amber only, outlined SVG, leather cord, as thin as the battery allows.
2. **v1 — build.** Copper/brass faceplate 1–1.5mm via SendCutSend or Ponoko · 3D-printed back housing 15–20mm · opal acrylic diffuser · WS2812 mini/COB strip at ~66 and ~82mm · Seeed XIAO ESP32-C3 · INMP441 mic, low-end follower · 500–1000mAh LiPo · patina by liver of sulfur (dark) / ammonia-salt fume (verdigris). Order spare plates.
3. **Final — metalsmith or armour maker**, briefed from a working prototype, not a render.

## 7. The fan pendant — later, not now

**Mic-reactive, not stage-synced.** Each pendant listens to the room and reacts to the same bass Nick is playing. No transmitters, no venue dependency, works at home with the record — and it keeps Nick as one more light answering the music rather than the one switching the crowd on (the guru line, WORLD §8). Same principle as the audio-reactive visualizers.

**Why it fits:** the crowd wearing the performer's mark is the mirror — *"I build the mirror. What you see in it is yours."* Evidence that it is real behaviour: fans already make and wear glowing logos of artists unprompted (the ASOT piece).

**Two tiers:** fans get a printed version; Nick's is the aged-metal original.

**Gated on audience.** Merch sells to people who already recognise the mark on him. Before that it is a gadget.

## 8. Open
- Material: A+C combination unconfirmed; copper vs brass ageing.
- Light colour: amber vs bone.
- Where the blackout moment sits in the arc.
- The outfit round (light top variants) has not been run.
- Whether the locked parts of this file get promoted into WOBAR_BRAND.
