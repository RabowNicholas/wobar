---
title: Projection Mapping Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Projection mapping in TD — kantan Mapper, CamSchnappr, keystone, edge blending, multi-projector setups.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_TOP.md, TD_OPERATORS_COMP.md
---

# PROJECTION MAPPING WORKFLOW

Mapping TD output onto physical surfaces — walls, sculptures, sets. TD has two built-in tools (kantan Mapper, CamSchnappr) plus manual approaches.

---

## When You Need Projection Mapping

- Projector misaligned with screen → keystone correction.
- Projecting on a non-flat surface → warping / mesh deformation.
- Projecting a single image across multiple projectors → edge blending.
- Projecting onto 3D objects (stage elements, sculpture) → 3D-accurate content via CamSchnappr.

---

## kantan Mapper

### What it is
Built-in TD component: drag-and-drop 2D projection mapping. Quads, triangles, and shapes on the projector canvas, each with their own content source.

### Basic workflow
1. Open Palette → Tools → kantan Mapper.
2. Drag Kantan Mapper COMP into project.
3. Connect TD's final output (TOP) to Kantan Mapper input.
4. Open Kantan's UI — drag-out shapes, place them in the projector canvas.
5. Each shape can source from the TD output and warp.
6. Assign each output shape a UV region of the input content.

### Use cases
- Windows of a building each get different content.
- Ceiling-mounted projector aimed at floor — correct for distortion.
- Multiple walls / surfaces in a venue each mapped separately.

### Performance
- Kantan Mapper is moderate cost — each mapped quad is a draw call.
- Fine up to ~50 shapes on M1.

---

## CamSchnappr

### What it is
3D-aware projection mapping: TD knows the 3D geometry of a physical object, you align a virtual camera to match a real projector's position, and TD renders the content correctly mapped onto the 3D surface.

### Basic workflow
1. Model the physical object in Blender / TD SOPs.
2. Import model into TD as a Geometry COMP.
3. Add CamSchnappr COMP (Palette → Tools → CamSchnappr).
4. Project physical calibration pattern (dots grid) from TD to physical projector.
5. Mark the corresponding 3D positions of the dots on the virtual model in TD's Camera Schnapper UI.
6. TD solves for the virtual camera pose that matches the real projector.
7. Now any rendered view from that virtual camera maps correctly onto the 3D object.

### When to use
- Projecting on a complex 3D sculpture.
- Projecting on a car, drum kit, furniture.
- Multi-projector coverage of a curved surface — each projector runs CamSchnappr independently.

### Cost
- Setup takes 30–60 minutes per projector per position.
- Content creation in TD is standard 3D rendering; CamSchnappr only handles the projection.

---

## Keystone Correction (Simple)

### The problem
Projector pointing at a wall from an angle → trapezoidal projection.

### Simple fix — OpenGL matrix
Use Transform TOP's Corner Pin (4-corner warp):
```
TD output → Transform TOP (Corner Pin enabled, drag corners to match the wall)
  → Out TOP → projector
```

### Non-CPU manual approach
Some projectors have on-device keystone correction. Use first if available (quality can be better than software).

### Kantan Mapper for this
For a 4-corner warp, Kantan Mapper with one quad = same thing but UI-driven.

---

## Edge Blending (Multi-Projector)

### The problem
Two projectors cover one seamless wall. Where they overlap, the image is 2× bright. Where they don't, there's a seam.

### Solution — gradient feather + black-level adjustment
```
TD output ──► split into N outputs
  For each output:
    ──► Transform TOP (crop to this projector's region with an overlap)
    ──► Ramp TOP (gradient feather in overlap region, dark at edges)
    ──► multiplied against content
  → Out to each projector
```

### Edge blend via Kantan Mapper
- Assign each projector as an output surface.
- Set overlap feather per edge.

### Black-level floor (2025)
Blended seams have raised blacks (two projectors can't make "true black" together). Compensate by bumping non-overlap black to match blended black — evens out the image.

### Projector hardware edge blend
High-end projectors (Panasonic PT-RZ series) have built-in edge blend. Simpler than software.

---

## Multi-Projector Setup — Output Configuration

### Canvas sizing
One TD canvas covers all projectors. If 3 projectors are side-by-side at 1280×720 each, total canvas = 3840×720. Each projector gets its 1280-wide slice.

On Non-Commercial: 1280 output cap. Must use multiple Window COMPs, one per projector, each ≤1280.

### Window COMPs per projector
```
Window "proj1" — Monitor 1, 1280×720
Window "proj2" — Monitor 2, 1280×720
Window "proj3" — Monitor 3, 1280×720
```

Each Window shows its own slice of the content via Crop TOP.

### Mac display arrangement
System Settings → Displays → Arrangement → drag displays to physical layout. Primary = main screen; others = projector outputs.

---

## Content Design for Mapped Surfaces

### Rectangular panels
- Design content at the aspect ratio of the panel.
- Edge-safe zone: the outer 10% may be hidden by bezels / surface edges → design content with the important stuff centered.

### Architectural / building mapping
- Study the building's geometry first. Render a test pattern (grid) onto the building to confirm.
- Content is custom per-building. Very time-intensive.

### 3D objects (CamSchnappr)
- Render a 3D scene from the virtual camera's perspective.
- Content placed on 3D surfaces inside that scene → shows up on the physical object.

---

## Calibration Process

### Day-of calibration
1. Power up projectors. Let them warm (1–2 minutes of blacks).
2. Show a calibration image (grid, alignment marks) from TD.
3. Walk the floor. Check:
   - All edges aligned with physical features.
   - No pixelation or aliasing on sharp edges.
   - Overlap regions blend smoothly.
   - Color matches across projectors.
4. If movement / vibration is expected, do calibration with everything in final position.

### Save calibration
kantan Mapper and CamSchnappr COMPs store their state in the project. Save project after calibrating. **Back up the project file** so you don't lose it.

### Re-calibration
If a projector is bumped, re-calibration is needed. Build this into showflow:
- 15-minute buffer before doors for final check.
- Every 60+ minutes if rig is near a stage, audience, etc.

---

## Interactive Projection Mapping

### Tracking people interact with mapped surfaces
- **Orbbec / Structure Sensor**: depth cameras track bodies in front of mapped walls.
- **MediaPipe via GPU plugin**: body/hand tracking from webcam.
- See `TD_APPLE_SILICON.md` §6 for sensor support on Mac.

### Pattern
```
Sensor → tracking → 2D position of person → TD content
  → Content reacts / follows person → projects onto wall
```

### Calibration
- Camera sees camera coordinates.
- Projector projects projector coordinates.
- Need a transform: camera-space → wall-space → projector-space.
- Calibration step: user touches points on the wall; tracker reports camera-space; wall has known projector-space coords (via mapping); solve transform.

---

## Common Mapping Failures

### Image shows but is wrong size
Projector resolution ≠ TD output resolution. Check Window COMP size vs projector spec.

### Edge blend visible
Feather too sharp or positions not exact. Re-align kantan shapes.

### Colors don't match across projectors
Different projector settings. Calibrate each (color temp, gamma) on projector side, or bake a per-projector color matrix into TD post.

### Projector tearing
Vsync off on Window COMP. Set Vsync = On.

### Live movement messes alignment
Projector on a hanging truss vibrates; image wobbles. Need stage-rigged mount or truss damping. Software can't fix.

### Keystone makes image blurry
Keystone uses OpenGL resampling → softens. Prefer physical projector alignment; use keystone only as a final touch.

### CamSchnappr calibration drifts
Projector moved. Need recalibration. This is why CamSchnappr only works for rigs where the projector doesn't move.

---

## Pre-Gig Checklist (Projection)

- [ ] Projector positions confirmed.
- [ ] All projectors same resolution, same refresh rate.
- [ ] HDMI/SDI cables tested end-to-end.
- [ ] TD Window COMPs mapped to correct Monitor indexes (see §Multi-Projector Setup).
- [ ] Kantan Mapper / CamSchnappr calibrated and saved.
- [ ] Test content shown on all outputs. No black outputs.
- [ ] Test with worst-case complexity scene — framerate holds.
- [ ] Backup: a simple single-projector fallback scene ready if a projector dies.

---

## Reading This File

If you need simple trapezoidal correction: §Keystone Correction. Multi-panel wall: §Kantan Mapper. 3D objects: §CamSchnappr. Multi-projector seamless: §Edge Blending. Interactive installations: §Interactive Projection Mapping. Always end with §Pre-Gig Checklist before a real-world deployment.
