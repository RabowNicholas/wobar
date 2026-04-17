---
title: COMPs — Component Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every COMP in TD 2025.32460. Containers, 3D objects (geometry, cameras, lights), UI panels.
dependencies: TD_LIBRARY_INDEX.md, TD_PATTERNS_3D_SCENES.md, TD_PATTERNS_INSTANCING.md
---

# COMPs — COMPONENT OPERATORS CATALOG

COMPs are **containers** — they hold other operators, expose parameters, and serve as the units of scene graph, 3D objects, UI panels, and modular network packaging. They are the primary reuse mechanism in TD.

**Types of COMPs:**
- **Object COMPs** — 3D entities in the render graph (Geometry, Camera, Light, Null Object, Bone).
- **Panel COMPs** — UI (Container, Button, Slider, Field, etc.).
- **Container COMPs** — logical packaging (Base COMP).
- **Execution COMPs** — Engine, Replicator, BulletSolver.

---

## 3D Object COMPs

### Geometry COMP
Holds a SOP or POP stream; rendered by a Render TOP.
- Tabs: Common, Xform, Instance, Render, Sub-Object, Texture.
- **Instance tab**: enables instancing — Translate / Rotate / Scale / Color / Texture / Quaternion / Custom attribute OPs point to CHOPs (multi-sample) or POPs (direct).
- **Render tab**: assigns Material (MAT path), shadow casting, light interaction flags.
- Use: every 3D renderable object is a Geometry COMP.

### Camera COMP
Scene camera for a Render TOP.
- Tabs: View (near/far, angle, ortho vs persp), Projection, Stereo.
- Params: Translate, Rotate, Look At, FOV, Near/Far, Orthographic option.
- Use: camera for Render TOP. Multiple Camera COMPs for multi-angle rendering.

### Light COMP
Scene light source.
- Types: Point, Directional (sun), Cone (spot), Area, Ambient.
- Params: Color, Intensity, Attenuation, Shadow on/off, Shadow Map Size.
- Use: lighting in Render TOP. Multiple lights = multiple Light COMPs.

### Null COMP
Empty object — transforms only, no geometry.
- Use: parent target, pivot, control proxy.

### Bone COMP
Skeletal bone for rigging.

### Environment Light COMP (in some builds)
Image-based lighting for PBR.

### Force COMP
Force source for Bullet / particle sim.

### Handle COMP
Visual manipulator in the viewport.

### Replicator COMP
Creates N clones of a template COMP driven by a DAT.
- Params: Template COMP, Template DAT (rows drive clone count and per-clone params), Callbacks.
- Use: small N instancing with per-instance logic. For large N, use POP instancing instead (see `TD_EFFICIENT_NETWORKS.md` §9).

---

## Container COMPs

### Base COMP
General-purpose container — holds any operators, exposes parameters.
- **The workhorse container.** Use for logical grouping, reuse, modularity.
- Parameters: custom params on the COMP's own parameter page (Component Editor → Custom Parameters).
- Inputs / Outputs via In / Out operators inside.

### Container COMP (Panel)
UI container — holds UI COMPs, displays as a panel.
- Use: build UI.

### Animation COMP
Holds animation channels with a timeline editor.
- Use: author curves in a dedicated COMP.

### Time COMP
Local timebase — a sub-network with its own time, independent of root.
- Use: scenes that run at different speeds, paused sub-networks.

### Window COMP
Displays a TOP on a monitor as a separate window / Perform mode output.
- Params: Monitor, Size, Position, Borders, Vsync.
- Use: Perform Mode output; secondary display.

---

## Execution COMPs

### Engine COMP
Runs a .tox sub-network in a separate process (no cook contention with parent).
- Params: External .tox path, Clones / Auto Start, IO wiring.
- Use: scene isolation, hot-swappable modules, parallel cooking.
- Non-Commercial: Engine clone limit.

### Engine Manager COMP
Manages multiple Engine COMPs.

### Bullet Solver COMP
Rigid-body dynamics physics engine.
- Use: geometry physics simulation.

### NVIDIA Flow COMP (Windows only; not relevant on Mac M1)

### Actor COMP
Dynamics actor for Bullet Solver.

---

## Panel COMPs — UI

### Button COMP
Pressable button — momentary or toggle.

### Slider COMP
1D / 2D / radial slider.

### Field COMP
Text input field.

### List COMP
Scrollable list.

### Radio COMP
Radio button group.

### Select COMP
Dropdown.

### Checkbox COMP
Checkbox.

### Text COMP (panel variant)
Text display / label.

### Container COMP (panel)
UI container.

### Table COMP
Table widget for UI.

### Parameter COMP
Exposes a referenced operator's parameters as UI.

### Window COMP — see Container COMPs.

---

## Specialty COMPs

### FBX COMP
Imports an FBX hierarchy as a COMP tree.

### glTF COMP
glTF import with hierarchy.

### Alembic COMP
Alembic file as COMP hierarchy.

### USD COMP (if present)
USD scene import.

### Blend COMP
Weighted blending of parameters across multiple COMPs.

### Widget COMP (palette)
Pre-built UI bundles.

### TDAbleton COMP (palette)
Ableton Link + Max For Live integration.

---

## COMP Parameters

### Custom Parameters
Every COMP can have custom parameters on a user-defined page. Add via Component Editor (right-click COMP → Customize Component).
- Use: expose tunable values at COMP level instead of burying them in internal ops.
- Types: Float, Int, Toggle, String, Menu, Pulse, RGB, RGBA, XY, XYZ, UV, WH, UVW, File, Folder, OP path.

### External .tox
Save COMP's contents to an external .tox file. Load as Engine or Clone on other projects.
- Use: reusable components library.

### Clone COMP (pattern)
- Internal COMP's "Clone Master" parameter points at a master COMP.
- Changes to master propagate to clones.
- Use: template-based scene architecture.

---

## COMP Architecture Patterns

### Reusable visual primitive
```
Base COMP "feedback_core"
  ├─ In TOP (source input)
  ├─ Composite ← Feedback ← Transform ← Level
  ├─ Custom Parameters: Decay, Zoom, Rotation (exposed as pars)
  └─ Out TOP
```
Drop the .tox into any project. Wire In, set Decay/Zoom/Rotation, use Out.

### Scene with internal control
```
Base COMP "scene_act_3"
  ├─ Custom Parameters: Intensity, ColorShift, TrailLength
  ├─ Audio input pulled via Select from global "null_audio_*"
  ├─ 3D pipeline (SOPs/POPs → Geometry → Camera → Light → Render)
  ├─ Post stack (Level, Bloom, etc.)
  └─ Out TOP
```

### Global controls COMP
```
Base COMP "controls"
  ├─ UI Sliders / Buttons (Panel COMP)
  ├─ OSC In CHOP (from phone)
  ├─ MIDI In Map CHOP (from controller)
  ├─ Null CHOPs ("null_intensity", "null_scene_index", ...)
  └─ Out (but usually referenced by Select from consumers)
```

### Engine-isolated scene
```
Save scene_act_3 to external scene_act_3.tox
In project: Engine COMP → External .tox = scene_act_3.tox
              ├─ Parent Inputs: audio CHOP, control CHOP
              └─ Output: TOP
```
Scene cooks in a separate process; Perform Mode survives if it crashes.

---

## Instance Tab on Geometry COMP — the Cheat Sheet

Geometry COMP → Instance tab is where GPU instancing lives.

| Parameter | What to wire |
|-----------|--------------|
| Instance On | On |
| Instance OP | CHOP with N samples, or a POP |
| Translate OP | CHOP channels tx, ty, tz (length N) |
| Rotate OP | CHOP channels rx, ry, rz (length N), or quaternion channels |
| Scale OP | CHOP channels sx, sy, sz (length N) |
| Color OP | CHOP channels r, g, b, a (length N) |
| Custom Attributes | Named channels; available in MAT as uniforms/attributes |
| Texture OP | Texture to sample per-instance via UV lookup |

**From POPs:** use POP to CHOP with one channel group per attribute, or connect POP directly to Instance OP slot if the build supports it. POP-direct is newer and preferred.

---

## COMP Performance Notes

- Base COMP itself has no runtime cost; it's purely organizational.
- Engine COMP has startup cost (process spawn) but saves cook time by moving work to another process. Pre-warm at project load (see `TD_FOOTGUNS.md` §H4).
- Replicator COMP at large N is slow (clones N full COMPs). Use POP instancing instead.
- Geometry COMP with instancing is cheap — the GPU does the heavy lifting.
- Panel COMPs (UI) have some cook cost on every panel event — don't put heavy logic in panel event callbacks.
- Clone hierarchy (COMPs cloned from a master) recooks when the master changes — large clone trees are expensive to edit.

---

## Reading This File

COMPs are fewer than other operator families — read top-to-bottom for 3D Object and Container types, Grep for specific UI COMPs when building interfaces. For architecture patterns, see the "COMP Architecture Patterns" section.
