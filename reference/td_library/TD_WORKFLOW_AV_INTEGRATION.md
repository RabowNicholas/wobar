---
title: AV System Integration Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: TD as part of a larger AV rig — Syphon/Spout/NDI video routing, Resolume handoff, multi-machine, front-of-house replacement planning.
dependencies: TD_LIBRARY_INDEX.md, TD_APPLE_SILICON.md, TD_WORKFLOW_LIVE_VJ.md, TD_OPERATORS_TOP.md
---

# AV SYSTEM INTEGRATION WORKFLOW

TD in the context of a full AV rig — video routing between apps, multi-machine setups, and the eventual goal of replacing front-of-house with Nick's own system.

---

## The End Goal

Nick's stated direction:
- Solo visualizers → **live-synced visualizers** → **full AV system replacing front-of-house**.

This file is the bridge from "TD as solo artist tool" to "TD as the backbone of the AV rig."

---

## Video Routing — Between Apps

### Syphon (Mac)
- Mac's GPU-to-GPU video-sharing protocol.
- Apps can publish frames; other apps subscribe.
- Zero-copy, low latency, GPU-side.

**Publishing from TD**:
```
Syphon Spout Out TOP (or Syphon Out TOP on older versions)
  - Name: "TD_Output"
  → Becomes visible to any Syphon receiver
```

**Receiving in TD**:
```
Syphon Spout In TOP
  - Source: "Resolume_Output"
```

**On Mac M1 in 2025**: Syphon has had intermittent issues on Metal. Verify before relying. See `TD_APPLE_SILICON.md` §5.

### Spout (Windows)
- Equivalent to Syphon, for Windows only.
- Not available on Mac.

### NDI (Network Device Interface)
- Cross-platform, cross-machine.
- CPU-side, network-based.
- Higher latency than Syphon (30–80ms typical).
- Useful for cross-machine: M1 sends to Windows, etc.

**Publishing from TD**:
```
NDI Out TOP
  - Name: "TD_Output"
```

**Receiving**:
```
NDI In TOP
  - Source: dropdown selects available streams on network.
```

**Mac M1 NDI caveat**: has had instabilities. Test explicitly on gig hardware.

### Physical — Capture card + HDMI
- Fallback when software routing fails.
- Send TD out via HDMI to a capture card on another machine, then into OBS / another TD instance.
- Reliable, introduces 30–80ms latency.

---

## TD + Resolume

### Pattern 1 — Resolume as final mixer, TD as clip generator
```
TD renders loops offline → ProRes files → Resolume plays them as clips
```
- Reliable, predictable.
- No live TD→Resolume link during show.
- Nick controls in Resolume; TD doesn't need to be open at the gig.

### Pattern 2 — TD live, Resolume does color + mapping
```
TD Syphon Out → Resolume Syphon In as a source → Resolume effects + mapping → Output
```
- Resolume handles projection mapping, color, post.
- TD handles generative content.

### Pattern 3 — Resolume for specific elements, TD for others
- Resolume plays VJ loops (stock footage, pre-rendered WOBAR loops).
- TD renders generative stuff.
- Both feed a Layer Mix TOP or compositor inside one app (usually Resolume).

**Nick's future**: TD likely owns more and more as his skill grows. Start with Pattern 1, migrate to Pattern 2/3.

---

## TD + OBS

For streaming / recording the set:
```
TD Syphon Out → OBS Syphon In (needs obs-ndi or Syphon plugin) → OBS records / streams
```

Alternative: TD NDI Out → OBS NDI Source.

On Mac: Syphon direct is better if it works; NDI is more reliable across versions.

---

## TD + Ableton Set

```
Ableton plays music → BlackHole → TD
Ableton Link tempo → TD sync
TD renders visuals → Syphon/HDMI → venue screens
```

See `TD_WORKFLOW_LIVE_AUDIOREACTIVE.md` for full audio detail.

---

## Multi-Machine AV Rigs

### Why multi-machine
- One Mac can't push 4× 4K projection outputs.
- Redundancy: if one machine crashes, another takes over.
- Separation of concerns: one machine for audio, one for visuals, one for lighting.

### M1 Studio + M1 MBP (Nick's available rigs)
- **M1 Studio** as the heavy lifter: TD runs here. External monitor to venue.
- **M1 MBP** as the DJ/music machine: Ableton runs here.
- Link both over ethernet (switch or direct cable).
- BlackHole isn't cross-machine — use audio-over-network (Dante Virtual Soundcard, or route a single output cable machine-to-machine via an interface).
- Link works over network (same subnet).

### Control machine + render machine
- MBP runs control UI + MIDI controller handling.
- Studio runs render-only TD, receives commands via OSC.
- Crash on render = restart; control continues.

### Render slave array
- Multi-machine rendering in TD exists via MultiTouchOut / similar. Complex to set up.
- For single-output gigs, overkill.

---

## Front-of-House Replacement — Planning

The long-term goal: Nick's AV rig replaces traditional house systems.

### What FOH usually does
- **Lighting**: color, motion, strobe, intelligent fixtures.
- **Lasers**: safety, content.
- **LED walls / projectors**: video content.
- **Tracking**: DMX, Art-Net, timecode.

### What TD can do
- **Lighting via Art-Net DMX**: TD sends DMX values to fixtures. DMX Out CHOP on M1 works over UDP/Art-Net, needs an Art-Net node at venue.
- **Lasers**: TD can output to laser software via OSC or ILDA-over-network. Professional lasers usually have their own control — TD cues them.
- **LED walls / projectors**: TD renders content, sends over HDMI / NDI / SDI (with capture card).
- **Timecode**: TD can chase or generate MTC.

### Building toward this
1. **Phase 1** (current): TD generates visuals for single-screen video output. Done.
2. **Phase 2**: Add lighting layer. Small DMX universe (1 fixture array). TD drives colors synced to music.
3. **Phase 3**: Multi-screen. Two projectors, or a projector + LED. Edge blending or independent content per output.
4. **Phase 4**: Full rig. Lights + lasers + projections + mapping — all from TD's state, one control surface.

### Reliability progression
- Phase 1 can crash mid-set; audience sees no visuals for 30 seconds; recoverable.
- Phase 4 crashing means no lights, no visuals, no lasers — the show stops. **Much higher reliability bar.**

### Tech stack at Phase 4
- 2× render machines with failover (second one mirrors output, takes over if primary hangs).
- External DMX node (uArtNet or Enttec) that can cache last-known-good.
- Timecode chase so if TD crashes, lights/lasers still follow timecode from an external clock.
- Pre-scripted fallback: when TD loses sync, it plays a generative loop until recovered.

---

## DMX / Art-Net from TD

### DMX Out CHOP
```
CHOP channels (values 0–255 or 0.0–1.0) → DMX Out CHOP
  - Type: Art-Net (network)
  - Net / Subnet / Universe
  - IP: venue's Art-Net node
```

### Addressing a fixture
Each fixture has a DMX start address. A 7-channel RGB fixture at address 1 takes channels 1–7. Route CHOP channels to those DMX slots.

### Multi-universe
- Each universe = 512 channels.
- Split across multiple DMX Out CHOPs, one per universe.
- Most small-venue setups fit in 1 universe.

### Software validation
Use a DMX monitor like QLC+ or a DMX-over-IP sniffer to confirm TD is sending. Most gig failures are mis-addressed fixtures, not TD.

---

## Timecode

### MTC (MIDI Timecode)
- HH:MM:SS:FF sync.
- TD can receive via MIDI In Map; outputs via MIDI Out.

### LTC (Longitudinal Timecode)
- Audio-signal timecode.
- Requires an audio interface input.
- TD has specific LTC operators (LTC In / LTC Out).

### Ableton Link is NOT timecode
- Link syncs tempo/phase; it's not an absolute time reference.
- For chasing a fixed cue list, use timecode, not Link.

---

## Layered Output — Pixel Mapping vs Video

### Pixel mapping (for pixel-addressable LEDs, e.g., FastLED strips via Art-Net)
TD renders a small texture that maps to LED strip positions, DMX Out sends pixel values as DMX channels.

### Video output (for HD LED walls, projectors)
TD renders full-res texture, sends via HDMI/NDI/SDI.

Both can happen from one TD project.

---

## Sync Across Multiple TDs

### Time of Day (ToD) sync
Each TD has absTime (since project open) and a wall clock (datetime). For multi-machine, sync to wall clock: `time.time()` from Python.

### Link for visuals
Between two TDs on LAN with Ableton Link enabled, they sync tempo. Use for cross-machine coordination of beat-reactive visuals.

### OSC for discrete events
```
Machine A (control) OSC Out → Machine B (render)
  /event/scene_change 5 → Machine B switches to scene 5
```

---

## Signal Flow Diagrams

### Simple solo set
```
Laptop Ableton (music) ──┬──► BlackHole ──► same laptop TD (visuals) ──► HDMI ──► projector
                         └──► Speakers
```

### Medium — 2-machine
```
MBP Ableton ──► Speakers
         │
         ├── BlackHole + Link ──► [ethernet] ──► Studio TD
         │                                             │
         └── MIDI controller ────────────────────────► Studio TD
                                                       │
                                       HDMI ──► projector / LED wall
```

### Large — dedicated FOH
```
MBP Ableton ──► Dante network ──► audio rig
         │
         └── Link over ethernet ──► Studio TD ──┬──► HDMI ──► projector
                                                ├──► HDMI ──► LED wall 2
                                                ├──► Art-Net ──► lighting rig
                                                └──► OSC ──► laser
```

---

## Reading This File

Routing (§Video Routing) is the first thing to decide. Next step is Resolume/OBS relationships if relevant. For the long-arc vision: §Front-of-House Replacement Planning and §Multi-Machine Rigs. DMX/Timecode sections are for when Nick adds lighting to the rig — probably Phase 2 of the plan.
