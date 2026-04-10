# WOBAR Patch System

## Purpose

Studio convention for building, organizing, and naming Serum 2 patches across WOBAR projects. Two halves: the 8-macro standard (how every patch is built) and the naming convention (how every patch is filed). This is the engineering layer of WOBAR sound design — separate from the aesthetic identity in WOBAR_SONIC.md and the structural framework in WOBAR_FRAMEWORK.md.

---

## Part 1 — The Five Axes of Variation

The conceptual framework. Every patch can be varied along five axes:

1. **Tonal** — what color the sound is (harmonic content, waveform shape, saturation harmonics)
2. **Motion** — how it moves through time (LFO rate, depth, modulation character)
3. **Body** — how heavy it sits (level, sub balance, fundamental presence)
4. **Width** — how it occupies stereo space (unison, dimension, utility width)
5. **Air / Density** — what texture lives on top (noise dust, high-frequency erosion, shimmer)

**Rule:** variations move ONE or TWO axes at a time. Moving more = a different sound, not a variation. The discipline of riding axes one at a time is what gives a song coherence — the same instrument in different moods, not many different instruments.

---

## Part 2 — The 8-Macro Standard

Fixed slot meanings across every WOBAR patch. Slots that aren't musically meaningful for a given patch stay empty — never repurpose a slot.

```
M1 — TONE A     primary harmonic balance
M2 — TONE B     waveform shape / secondary tonal lever
M3 — DRIVE      saturation intensity (often multi-destination)
M4 — MOTION     rhythmic movement
M5 — BODY       weight / level
M6 — WIDTH      stereo space
M7 — AIR        top-end texture
M8 — SCENE      patch-specific wildcard (renamed per patch)
```

Tone gets three slots (M1, M2, M3) because tonal expressivity is where WOBAR patches develop personality across a song. Everything else gets one slot. M8 is the only macro whose name varies per patch — it's the wildcard for whatever unique knob a specific patch needs (FLUTTER, GRAIN, FB, SCAN, etc.).

---

## Part 3 — Standardization Rules

- **Same macro = same axis on every patch, always.** Macro 4 is always MOTION whether it's modulating an LFO depth, a filter cutoff sweep, a granular scan rate, or a wavetable position automation. The meaning of the knob is fixed; what's underneath it changes per patch.
- **0% = minimum of the axis, never "off".** MOTION at 0% might mean "very slow LFO at 5% depth," not "LFO bypassed." The macro should never disable the axis, only minimize it. This is critical for smooth automation.
- **Home position usually 35–50%** so the macro has headroom in both directions. If your home position is at 80% on every macro, you have nowhere to go up.
- **Empty slots stay empty — do not repurpose.** If a patch has no air axis, M7 stays empty rather than being remapped to something else. Repurposing breaks the muscle memory of the standard.
- **Multi-destination macros are encouraged when a single parameter is too weak.** If DRIVE doesn't feel impactful enough, route M3 to multiple destinations at once (Drive + Hyper Detune + Compressor Gain). One knob, coordinated push across the chain.
- **Macros named at the AXIS level, not the parameter level.** TONE A, DRIVE, BODY — not WT POS, DISTORTION DRIVE, OSC LEVEL. The name describes what the knob does to the *sound*, not what's routed underneath.
- **M8 is the only macro renamed per patch.** Document the M8 meaning in the patch comments or as part of the patch name so future-you knows what the wildcard does.

---

## Part 4 — Naming Convention

Format:

```
[Project]_[Category]_[Function]_[Key]_[Version]
```

- **Project** — codename (Alpha, Bravo…), swappable to real track name later
- **Category** — high-level type (Bass, Lead, Pad, Sub, FX, Drum)
- **Function** — fixed vocabulary (Sub, Mid, Reese, Vocal, Pluck, Warm, Riser…)
- **Key** — musical key (Fmaj, Cmin, Em…)
- **Version** — revision counter (v1, v2, v3)

Example: `Alpha_Bass_Mid_Fmaj_v1`

When sorted alphabetically in Serum's browser, all `Alpha_*` patches group together, then within Alpha all the Basses are adjacent, then sub-sorted by function. You can scan an entire project's sound design in one column.

---

## Part 5 — Function Vocabulary (the fixed list)

The function slot only works if you use a fixed vocabulary. If you call one patch "Mid" and another "MidLayer" and another "MidBass," sorting breaks. Pick one word per role and stick to it.

**Bass:** Sub, Mid, Reese, Growl, Wub, Layer
**Lead:** Vocal, Pluck, Stab, Sustain, Arp
**Pad:** Warm, Drone, Texture, Choir
**FX:** Riser, Impact, Drone, Sweep, Drop, Reverse
**Drum:** Kick, Snare, Clap, Hat, Perc

This list is starter — add to it as needed, but commit to one word per function and never invent ad-hoc variants. If you find yourself wanting "MidBass" *and* "Mid," that's a sign one of them needs a different function name like "Layer" or "Body."

---

## Part 6 — Versioning Rules

- **Same architecture, different settings → same name, increment version.** A knob tweak is not a new version. A redesign of the FX chain is.
- **Different architecture or different role → new function descriptor.** Don't make `v2` for a patch that's actually a different sound — give it a new function name or a new patch entirely.
- **Never delete old versions, duplicate first.** You'll want to roll back at some point.

Rule of thumb: if you'd struggle to explain how v2 differs from v1 in one sentence, it's not a new version — it's a different patch.

---

## Part 7 — Wavetable Naming (parallel system)

Custom wavetables follow a parallel convention:

```
[Project]_WT_[Description]_[Frames]f
```

Example: `Alpha_WT_HollowMid_4f`

This way you can see exactly which custom wavetable is loaded just by reading its name in the OSC slot. When the project gets a real track name, the wavetable rename comes along with everything else via find-replace.

---

## Part 8 — Project Codename Roster

Phonetic alphabet, used in order. When a project gets a real track name, find-replace `[Codename]_` → `[TrackName]_` across all patches and wavetables for that project.

```
Alpha    Bravo    Charlie  Delta    Echo
Foxtrot  Golf     Hotel    India    Juliet
Kilo     Lima     Mike     November Oscar
Papa     Quebec   Romeo    Sierra   Tango
Uniform  Victor   Whiskey  Xray     Yankee   Zulu
```

26 codenames built in. If more than 26 active WOBAR project codenames are floating around without real track names, that's a signal to ship something.

---

## Part 9 — Maintenance

This is a living system. Update the function vocabulary as new categories emerge. Update the macro standard if a sixth axis becomes essential. Always preserve backward compatibility — never rename existing macro slots, only add new ones if absolutely required.

The whole point of the system is consistency over time. A patch saved today should be legible six months from now without a manual.
