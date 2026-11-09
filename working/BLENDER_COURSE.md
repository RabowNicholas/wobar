---
title: Blender Course — HOHLWEG continuous-push visualizer
status: live
scope: A YouTube-built course covering every technique needed for the HOHLWEG visualizer — an 11-minute continuous camera push through a moonlit sunken lane, elements lit by MIDI/audio, rendered in EEVEE on an M1 Max (32 GB). Techniques only; creative design lives elsewhere. Keybindings go in [[BLENDER_CHEATSHEET]].
---

# BLENDER COURSE — HOHLWEG

**Locked constraints:** EEVEE · 11:00 runtime (15,840 frames @ 24fps) · no modeling, assets only · photoreal through darkness lit by in-scene elements · moon as light source only · fog/mist · lights driven by MIDI clips and EQ bands · YouTube 16:9 primary.

**Version:** Blender 5.2 is installed. Most videos below are 4.2+ (EEVEE Next) or 5.x. Older ones are flagged where the UI moved.

**How to use this:** each module ends with an **exercise** that builds part of the actual piece. Do the exercise before moving on. The modules stack: by Module 10 you have a working proof-of-concept segment.

---

## MODULE 1 — Foundations
- [ ] [Beginner Blender Tutorial (2026)](https://www.youtube.com/watch?v=z-Xl9tGqH14) — Blender Guru, 4:19:10. **Watch Parts 1, 2, 4, 7, 8** (basics, basic modelling, materials, scattering, lighting/rendering). Parts 3, 5, 6 (organic modelling, texturing, UVs) are skippable since you aren't modeling.
- [ ] *Alt/backup:* [Blender 5 Complete Beginners Guide — Part 1, The Interface](https://www.youtube.com/watch?v=kVcY7K-JA1Y) — Grant Abbitt, 12:42

**Exercise:** finish the donut through Part 8. Add every new shortcut to the cheat sheet.

## MODULE 2 — Assets without modeling
- [ ] [How to Use Online Asset Libraries in Blender 5.2](https://www.youtube.com/watch?v=o8sWu8dJHHU) — Ryan King Art, 5:54
- [ ] [Asset Browser in Blender 5.2 — Bringing Assets Into Other Files](https://www.youtube.com/watch?v=v94cRbQMkwQ) — Artisans of Vaul, 11:09
- [ ] [Install and use BlenderKit in Blender 5.1](https://www.youtube.com/watch?v=AuvjIn45hZU) — S_broz3D, 10:22
- [ ] *Optional (older):* [Poly Haven's own Blender add-on](https://www.youtube.com/watch?v=ku_xv6WV6UE) — Poly Haven, 7:58

**Exercise:** build a personal asset library: 3 soil/mud materials, 3 root or fallen-branch models, 3 ferns/undergrowth, 2 rocks, 1 tree. Mark them as assets.

## MODULE 3 — Shaping the lane
- [ ] [How to Use the Displace Modifier](https://www.youtube.com/watch?v=XBdNZIs1U8w) — The CG Essentials, 9:46
- [ ] [Array an Object Along a Curve](https://www.youtube.com/watch?v=lRK8UMudejg) — Ryan King Art, 3:16. *The "one curve is the spine" idea starts here.*
- [ ] [How to Place Roads on ANY Terrain](https://www.youtube.com/watch?v=3q-3XBTVcGs) — I Am Machino11, 36:14. *Carving a path along a curve into terrain = carving the lane.*
- [ ] *Optional:* [Sculpting Terrain](https://www.youtube.com/watch?v=-wqMvq5F2Uo) — PzThree, 26:49. Grab/Smooth brushes only, for touching up walls.

**Exercise:** a 100 m lane following one Bezier curve, with walls rising 3–5 m above the path. Real-world scale.

## MODULE 4 — Scattering the world
- [ ] [Blender 5.0 — The Scatter on Surface Modifier](https://www.youtube.com/watch?v=zaFlqVTZMB8) — Blender Made Easy, 8:21. *Built-in, new in 5.0.*
- [ ] [Distribute Objects using Weight Paint (Geometry Nodes)](https://www.youtube.com/watch?v=6LMuT2hN2yw) — Ryan King Art, 10:35. *Paint where things grow: banks dense, path clear.*
- [ ] [How To Create Beautiful Environments](https://www.youtube.com/watch?v=Y1bOokHzEAk) — Max Hay, 13:58. *Composition and density, not tool clicks.*
- [ ] *Optional (paid add-on):* [Introduction to Geo-Scatter](https://www.youtube.com/watch?v=djmgTnZm2uQ) — Martin Klekner, 16:35. Worth it if the built-in scatter gets slow over the full length.

**Exercise:** dress the 100 m lane: roots spilling from the walls, undergrowth on the banks, a clear path down the middle.

## MODULE 5 — The camera push
- [ ] [Follow Path Constraint — Variable Speed](https://www.youtube.com/watch?v=1byaQygtcpc) — 5 Minutes Blender, 4:38. *Evaluation-time control = the GRUND slowdown.*
- [ ] [Camera Follow Path: Step-by-Step](https://www.youtube.com/watch?v=5EQdQdtg-ao) — What Make Art, 8:25
- [ ] [How to Use the Graph Editor for Beginners](https://www.youtube.com/watch?v=sc64wS-gukU) — Ryan King Art, 18:12. *Required for everything in Modules 9–10 too.*
- [ ] [How to Use Depth of Field](https://www.youtube.com/watch?v=ahT3P274EMw) — Ryan King Art, 2:40
- [ ] [Realistic Camera Shake, No Add-ons](https://www.youtube.com/watch?v=9EDOxaV950s) — JustAboutEverything, 4:05. *Noise modifier on F-curves. Keep it subtle: weight, not handheld.*

**Exercise:** camera on the same curve as the lane, constant push for 60 s, then ease to a near-stop over the last 10 s. Track To an empty for aim.

## MODULE 6 — EEVEE, properly
- [ ] [How to use Eevee — Full Blender Course](https://www.youtube.com/watch?v=-gW6vk_OuNQ) — Blender Guru, 1:16:54. **The core of this course.** Noise/samples, raytracing, light bounces, sphere probes, volume probes (baked lighting), volumetrics, flickering alpha maps (foliage), light bleed.
- [ ] [10 Tips for Better Renders in the New EEVEE (4.3)](https://www.youtube.com/watch?v=yMfouQTkmFA) — SouthernShotty, 11:52
- [ ] [How to make EEVEE Next look like Cycles](https://www.youtube.com/watch?v=wGS0xp-XBqw) — Edin Spiegel, 4:01

**Note for this build:** baked volume probes don't respond to animated lights. Bake them for the moonlight base layer only.

## MODULE 7 — Moonlight and darkness
- [ ] [Creating Realistic Moonlight is Complicated](https://www.youtube.com/watch?v=9gb9bNrb8P4) — William H Baker, 9:11. *Quality, distance, angle, color, vision. Directly on target.*
- [ ] [10 Secrets to Beautiful Night Lighting](https://www.youtube.com/watch?v=5W9MFK6Ioa4) — SouthernShotty, 11:28
- [ ] [How to get good lighting in Blender](https://www.youtube.com/watch?v=c3FnWQTMo9s) — Max Hay, 27:53
- [ ] [Light Falloff (with Gleb Alexandrov)](https://www.youtube.com/watch?v=IK3l8WC6Ssg) — Blender Secrets, 1:02. *Light pools in darkness.*
- [ ] [Rendering with AgX — the Raw Workflow](https://www.youtube.com/watch?v=hS7uaTquwWc) — CG Cookie, 14:27. *Color management, where darkness either holds or turns to mud.*

**Exercise:** light the lane with moonlight only. The image should be dark but readable, with blacks that stay deep rather than grey.

## MODULE 8 — Fog and mist
- [ ] [Everything About Volumetrics](https://www.youtube.com/watch?v=A8KkY9zLbDI) — Thridigi, 5:24. *Settings, absorption vs scattering, cheap volumetrics.*
- [ ] Blender Guru EEVEE course, chapter **1:02:44 Volumetrics** (Module 6 video). Re-watch now with your scene open.
- [ ] [Fog and Mist Using the Mist Pass](https://www.youtube.com/watch?v=EHrTQZQ9uQ4) — Ryan King Art, 6:52. *The cheap fake-fog route; also good as a depth layer on top of real fog.*
- [ ] [Epic God Rays in EEVEE](https://www.youtube.com/watch?v=x4c1qbA1ryc) — Architecture Topics, 2:06

**Exercise:** low mist in the lane. Moonlight shafts through the canopy. Check the Volumes panel's start/end distance so fog exists around the camera along the whole path.

## MODULE 9 — The lit elements
- [ ] [How to Animate Flickering Lights](https://www.youtube.com/watch?v=2rXl5pSuGio) — Ryan King Art, 4:57. *Animating emission + light strength.*
- [ ] [Custom Properties and Drivers Made Easy](https://www.youtube.com/watch?v=_197jQFh22E) — Pierrick Picaut, 14:12. **Key technique:** one control value drives the glow material and the real light together.
- [ ] [Quick Tip: Working With Drivers](https://www.youtube.com/watch?v=CPEEjlRLKEU) — Polyfjord, 4:26
- [ ] [Light & Shadow Linking (4.0)](https://www.youtube.com/watch?v=hR2G95R4C3Y) — Ryan King Art, 4:57. *Check it works in EEVEE in your version before designing around it.*
- [ ] [Start Compositing in Blender 5.0](https://www.youtube.com/watch?v=kAWfjBKcgFc) — Pau the Hueman, 19:12. *Glare node = bloom on the elements.*

**The pattern to build:** every glowing element = emissive material + real point/area light at the same spot, both driven by one custom property. Set the light's Volume influence separately so it lights the fog.

**Exercise:** one element in the lane, pulsing by hand-placed keyframes, lighting the fog and the walls around it.

## MODULE 10 — Driving it from the music
- [ ] [Making an Audio Visualizer in Blender 5.2](https://www.youtube.com/watch?v=kO_vPohvF-k) — Ducky 3D, 21:05. *Current-version Bake Sound to F-Curves.*
- [ ] [Bake Sound to F-Curves not showing (4.2+)](https://www.youtube.com/watch?v=HzEH02X60lY) — AnimFX, 1:02. *The menu moved. Watch this if older tutorials don't match your UI.*
- [ ] [Bake Sound to F-Curves like a pro](https://www.youtube.com/watch?v=ZFfQStzF2eA) — Aisjam 3D, 17:43. *Frequency cutoffs = your EQ-band modulation.*
- [ ] [How to Add Sound in Blender 5.0 (Video Sequencer)](https://www.youtube.com/watch?v=h9wOj820jDI) — MOTION BEAST, 0:45. *Track in the timeline for scrubbing.*
- [ ] [MIDI to Keyframes add-on](https://www.youtube.com/watch?v=E4wfblQWhtY) — Ryosuke, 13:48

**EQ bands:** cleaner than Blender's frequency cutoffs is bouncing band-filtered stems from Ableton (one per element), then baking each to its element's custom property.

**MIDI, with one gap no tutorial covers:** ERNSTFALL's 174→140 deceleration. Every MIDI→keyframe tool converts ticks to seconds with a tempo, and if the tempo map isn't in the exported file, the lights drift after the slowdown. **Test this first:** export one ERNSTFALL clip that spans the deceleration, import it, and check the last notes against the audio. If it drifts, Claude can write a Python importer that reads the tempo map (or takes it from Ableton) and writes keyframes with attack/release shaping.

**Exercise (proof of concept):** the 100 m segment with the camera pushing, moonlight, fog, and one element pulsing from a real MIDI clip in sync with the track.

## MODULE 11 — Scaling to 11 minutes
- [ ] [This Is How You ACTUALLY Optimize Blender](https://www.youtube.com/watch?v=fS9BU_L6LCE) — Smeaf, 3:03
- [ ] [How to Render Insane Scenes](https://www.youtube.com/watch?v=tXdnAVKEU8E) — Christopher Fraser, 2:16. *Instancing.*
- [ ] [Blender Eevee Render Speed Settings](https://www.youtube.com/watch?v=OF7WV9JZAJc) — Yisen Cinema, 3:53

**Benchmark here, before building the full length:** render 5 frames of the proof-of-concept segment at final quality. Average seconds/frame × 15,840 = the full render. 10 s/frame ≈ 1.8 days; 30 s/frame ≈ 5.5 days.

**No tutorial for these, learn by doing:** split the world into sections (collections or linked files) along the one curve; hide what's behind the camera; camera clip start/end tuned for a long scene; 32 GB unified memory is the ceiling for scatter density.

## MODULE 12 — Rendering and output
- [ ] [Export Animation Renders the RIGHT Way](https://www.youtube.com/watch?v=UH-zqJ2Jx64) — Brandon 3D, 12:11. *Image sequences, not video files: crash-safe and resumable.*
- [ ] [How to Render Your Animation to a Video File](https://www.youtube.com/watch?v=OENbinegV2c) — Ryan King Art, 6:31. *Turning the sequence into the final file.*

**Settings to know:** frame range per chunk, "Overwrite" off, render as EXR or PNG sequence, motion blur on (a forward push without it reads as a game), final grade/LUT in Resolve.

---

## Gaps with no good tutorial (ask Claude when you get there)
- MIDI import that respects ERNSTFALL's tempo map (Module 10)
- Splitting an 11-minute world into sections along one camera move (Module 11)
- Rebuilding the Green (Patina) / Purple Gradient Map grades from [[WOBAR_VISUAL_RESET]] §8 as a LUT for Resolve
