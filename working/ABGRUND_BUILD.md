---
title: ABGRUND — the falling system
version: 1.1 (+ Act 3 reclassification, 2026-08-15)
last_updated: 2026-08-15
status: live
scope: How continuous descent is produced and sustained across the whole of ABGRUND (track 2 of the HOHLWEG EP). The mechanism, why it is built at four rates instead of one, the harmonic condition, and the tools. Technique here is reusable; the arrangement decisions are track-specific. **Act mapping is owned by [[working/HOHLWEG_EP]], not this file.**
dependencies: [[working/HOHLWEG_EP]], [[reference/WOBAR_EMOTIONAL_REGISTER]], [[reference/WOBAR_GRAMMAR]], [[reference/WOBAR_FRAMEWORK]]
---

# ABGRUND — THE FALLING SYSTEM

**Act 3 ENCOUNTER, purely — reclassified 2026-08-15 (was Act 2 DESCENSION).** 140.

**The listener's emotional core is *witnessing*.** Uncomfortable, grotesque in the way that
makes your skin crawl but you can't look away. **The body is still and everything inside is
moving.** Nothing external is causing the descent. Implicit ask: **sit with this — sit through
this.** Patience is the discipline.

> **⚠ The reclassification reverses two rules this file was originally written on. Both were
> Act 2 rules and both are now inverted:**
>
> | Was (Act 2) | Now (Act 3) |
> |---|---|
> | Hypnotic. Comfortable. Head bobbing. **Surrender they never noticed giving.** | **Held, still, confrontational.** The body does not move; the interior does. |
> | *One form persisting. Micro-variations only, never novelty.* | **Unpredictable. Breaks pattern expectations.** Tension and small releases, dissonance resolving only briefly before the next dissonance. |
>
> **The Risset system below survives the change and gets more correct, not less** — a rhythm
> that resolves for an instant at each metabar and immediately re-tensions *is* Act 3's quality
> of movement, and a pulse you cannot lock to is "hard to listen to in the way mirrors are hard."
> What dies is the framing: this is not a comfortable sink. It is a grind that will not let the
> listener settle.
>
> **What breaks Act 3: relieving the discomfort before it has done its work.** Premature release
> is failure. No vocals. No melody. Nothing that makes it watchable rather than felt.

**The track must not end. It gets cut off by track 3.** *Continuously falling* cannot resolve;
the moment it lands it is lying. The floor arrives from outside the track.

---

## 1. THE CORE PROBLEM — a loop is the opposite of a fall

A groove is cyclical. It **returns**, which is the one thing falling never does. So the groove
cannot carry the descent.

**The groove stays put; a parameter underneath it descends.** The listener's foot keeps time
while their body sinks. Falling is not an effect added to the track — it is a set of parameters
running under it.

---

## 2. THE ENGINE — descending Shepard–Risset glissando

Tones glide down continuously; as each leaves the bottom, another fades in at the top. Pitch is
always falling and never arrives.

**Build method (cheapest correct one):** record or synthesize one long descending glissando.
Loop it. Layer three copies, each offset by a third of the loop length so they overlap. Then put
a **static wide bandpass / bell EQ across the bus** — loud in the middle, rolled off at both
extremes.

**Because the EQ does not move and the tones do, each layer fades in at the top and out at the
bottom automatically.** That static curve *is* the Shepard amplitude envelope. It removes the
only difficult part of the build.

> **⚠ Bury it.** Nolan has made this sound like film tension. If a listener can identify it as a
> Shepard tone it has become a reference instead of a mechanism. Low, filtered, felt not heard.

---

## 3. FOUR RATES — because the ear adapts to any single one in ~30 seconds

This is the reason a single effect cannot carry a whole track. The same gesture runs at four
timescales so that when perception normalises one, another is still working.

| Rate | Parameter | Behaviour |
|---|---|---|
| **Bar** | the glissando | cycles every 4–8 bars |
| **Phrase** | filter cutoff | descends over 16 bars, resets under something loud enough to hide it |
| **Track** | reverb size + pre-delay | grows across the entire arrangement, **never resets** — the shaft above them deepens |
| **Event** | Doppler passes | 4–6 across the track; objects move *up*, so the listener is moving down |

The track-level move must be slow enough that nobody can point at it.

The event-level move stays sparse. More than a handful and a physical event becomes a gimmick.

> **⚠ Amended for Act 3, 2026-08-15.** The four rates were built to defeat *adaptation* — the ear
> normalising a single effect. Under Act 3 they have a second job: **the pattern must also break.**
> Act 2 wanted one form persisting; Act 3 wants expectation broken. So at least one of the four
> rates should occasionally **fail to arrive** — a phrase-level reset that doesn't land where the
> previous three did. Not a variation for interest's sake. A withheld return.

---

## 4. THE HARMONIC CONDITION — do not state a tonic

*Abgrund* is literally **un-ground**, and the harmonic form of no ground is music with no
gravitational centre.

- **Whole-tone and octatonic have no leading tone and no tonic pull.** Nothing wants to resolve.
  **Act 3 sharpens this into a positive instruction, 2026-08-15:** the act's named intervals are
  **tritones and half-steps.** Whole-tone is built from tritones and octatonic supplies the
  half-steps, so the earlier advice holds — but it is no longer only *avoid the tonic*, it is
  *use the two intervals that refuse to settle.*
- Even where the track reads as minor: the bass moves in a cycle that **never lands on the 1**.
- **No perfect cadence anywhere.**
- Wherever a satisfying downbeat impact would normally sit, place nothing — or place something
  that begins slightly *before* the 1.

**A wind bed underneath all of it.** Falling has a real sound and it is air. Filtered noise
opening very slowly across the track, read as increasing velocity.

---

## 5. RISSET RHYTHM — the tempo version, and the tool

The temporal equivalent of a Shepard tone: multiple streams playing one pattern at different
tempos with amplitude crossfades, producing perceived perpetual acceleration. Run it on hats and
percussion **while the kick stays locked** — the locked kick is what keeps the groove from
falling with everything else.

**Almost unused in bass music.** This is the layer most likely to make the track sound like
nothing else in the lane.

### Tool — installed 2026-08-14

**`risset` — polyrhythmic Risset rhythm MIDI generator.** Nathan Turczan.
`https://github.com/nathanturczan/risset`

- **Max for Live device installed to** `~/Music/Ableton/User Library/MIDI Tools/Max Generators/risset.amxd`
- Reached in Live via the **MIDI Tools panel (wand icon) → Generators → risset**, on a selected
  MIDI clip.
- Parameters: direction (accel / decel) · mode (**arc** = 2 metabars, complete cycle · **ramp** =
  1 metabar, a single crossfade, the composable building block) · tempo ratio · the two layer
  pitches · velocity response curve.
- **Polyrhythmic ratios are the point.** Classic Risset uses tempo octaves (2:1); this does
  arbitrary ratios — 3:2, 5:4, 3:5 — after Volkov (2023). The odd ratios are where it stops
  sounding like a demo.
- A CLI generator (`risset.py`, needs `midiutil`) does the same offline with `--ratio`,
  `--direction`, `--measures`, `--bpm`, `--ramp`. Pre-rendered example MIDI is in the repo's
  `examples/midi/`.

> **⚠ Two dependencies worth knowing.** The device's UI is **hosted externally and needs an
> internet connection** — do not first discover this at a venue. A native-UI version exists in
> the repo but was unfinished as of this clone. And MIDI Tools are **Live 12 only**, Suite only
> (Max for Live) — none of this exists in the Live 11 install.

---

## 6. WHAT KILLS IT

- **Any downlifter that lands.** A downsweep is *one* fall; a fall that terminates is a floor.
  Descending sweeps must not resolve.
- **Any riser** — and equally, any 16-bar tension curve, because a tension curve promises arrival.
- **Silence used as impact.** A full stop reads as landing.
- **Anything that implies a bottom is coming.** The moment the listener can sense a floor, the
  falling stops being continuous and becomes a build.

**To reset adaptation without suggesting a bottom:** *remove* the Shepard layer for two bars and
bring it back. Absence resets perception, and the return re-establishes the motion — a build
would have done the same job and destroyed the premise.

---

## 6.5 THE DROP — accelerating Risset, not a locked pattern

*Decided 2026-08-15, and the Act 3 reclassification confirms it after the fact.*

**A locked hat pattern at the drop is relief, and Act 3 forbids relief.** The original plan —
straight offbeat 8ths with ghosts, dead on the grid — was written while this was Act 2, where a
groove to hold onto is correct. Under Act 3 it is the named failure mode: *relieving the
discomfort before it has done its work.*

**Instead the hats reverse direction: an accelerating Risset over an 8-bar metabar, ratio 3:2
inverted to 2/3.** Nothing locks; the only thing that changes is which way the illusion runs.

- **Same ratio as the falling section on purpose.** The ratio is also the polyrhythm — two layers
  at 3:2 *are* three-against-two — so keeping it means the hats retain their character while
  reversing. Changing ratio *and* direction at once reads as a new idea rather than an inversion.
- **8 bars against the falling section's 16 = double the rate of change**, so the escalation comes
  from the metabar length, not from a bigger ratio. Ratio is the distance; clip length is the time.
- **Real falling accelerates.** Decel reads as sinking; accel is gravity. The two sections together
  say *the body slows while the fall speeds up*, which is both halves of the story at once.
- Run them **sequentially, not stacked.** Two opposed Risset layers at once is as likely to cancel
  into mush as to work, and the drop is the wrong place to debug it.
- ⚠ **UI:** direction follows the ratio — `Num > Denom → decel`. For the accel clip the ratio must
  read **2/3**. Check the status line, not just the button.

---

## 7. OPEN

- ~~The Act 2→3 cusp is deliberately skipped~~ — **superseded 2026-08-15 by the Act 3
  reclassification.** ABGRUND no longer sits after the cusp; it *is* Act 3. The cusp's marking
  moment now lives at the ERNSTFALL→ABGRUND track boundary. Mapping owned by
  [[working/HOHLWEG_EP]].
- **Does this track still want a groove-locked kick?** The locked 140 kick was justified as the
  anchor that buys a more aggressive Risset ratio, and perceptually that still holds. But Act 3
  *pushes the listener into the ground and keeps the body still* — a groove-forward 4/4 that makes
  people move is Act 2 and Act 4 behaviour. Unresolved.
- **The static reference element** (§3) is still needed — falling requires something to be slow
  relative to — but under Act 3 a friendly 16th shaker is comfort. Make it a **texture rather than
  a groove element**: air, noise, a held tone. Same perceptual job, no relief.
- **How the cut into track 3 is executed** is undecided, and it is the most important second on
  the EP.
- Nothing here has been tried on the actual arrangement yet. Every rate above is a hypothesis.
