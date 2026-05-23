---
title: Blender UI Vocabulary
version: 1.0
last_updated: 2026-05-22
status: live
scope: Canonical names for Blender editors, panels, modes, regions, and layout concepts. The bridge between human-speak ("the N-panel," "the Outliner") and bpy ("region_type='UI'", "SpaceOutliner").
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_DATA_MODEL.md
---

# BLENDER UI VOCABULARY

This file is the **translation layer** between how a human talks about Blender and how the API names the same things. When the user says "press N to open the BlenderMCP tab," the agent needs to know that "N" toggles the `UI` region of the active `SpaceView3D`, and the "BlenderMCP tab" is a `bpy.types.Panel` whose `bl_category` is `"BlenderMCP"`. Likewise when reading Blender docs or tutorial transcripts: "the Outliner shows…" → `SpaceOutliner`; "in the Properties editor's Object tab…" → `SpaceProperties` with `context = 'OBJECT'`.

Lock this vocabulary first. Everything else in the library assumes it.

**Core facts:**

- Blender's UI is built from **Editors** — non-overlapping rectangular **Areas** that tile the window. Each Area hosts one Editor type.
- Each Editor has a fixed region structure: **header** (top or bottom strip with menus/dropdowns), **main region** (the content), optional **sidebar** ("N-panel," right side), optional **toolbar** ("T-panel," left side), optional **footer**, optional **HUD** (transient operator redo).
- The entire UI layout is itself part of the Blender file. Open a `.blend` and you get its saved layout. This is why `bpy.data.workspaces`, `bpy.data.screens`, and `bpy.data.window_managers` exist as datablocks.
- Areas can be **split** (drag corner inward) or **joined** (drag corner over neighbor). They can also be **swapped**, **maximized** (Ctrl+Space), or **fullscreened** (Ctrl+Alt+Space).
- Saved layouts are called **Workspaces**. The default file ships with: **Layout, Modeling, Sculpting, UV Editing, Texture Paint, Shading, Animation, Rendering, Compositing, Geometry Nodes, Scripting**.
- Workspaces are tabs across the **Topbar** (top of the window). Switching workspaces does not change the scene — only which Editors are visible.
- Inside an Editor, the body usually contains **Panels** (collapsible boxes) grouped into **Tabs** (vertical icon strip on the side, e.g., in Properties editor and N-panel).
- Most editors operate on the **active scene** (`bpy.context.scene`) and **active object** (`bpy.context.active_object`). The Properties editor in particular is context-driven — its tabs change depending on what is active.
- Blender does not have modal dialogs in the OS sense. Almost everything is an inline panel, a **popover**, or a **pie menu**.
- Almost every UI element has a Python equivalent reachable through `bpy.context.<area>` or via the underlying datablock. Right-clicking a control and choosing **Copy Full Data Path** is the canonical way to discover the API path for a UI value.

---

## Editors — The Main Ones

Each editor has a Python `Space` subclass under `bpy.types`. The list below covers the editors an agent will encounter in practice. (Blender ships a few more — `SpaceSequenceEditor`, `SpaceClipEditor`, `SpaceSpreadsheet` — included at the end.)

### 3D Viewport
- **Human name:** "the viewport," "the 3D view," "the scene"
- **Shows:** the 3D scene — meshes, lights, cameras, gizmos
- **bpy class:** `SpaceView3D`
- **Regions:** header (top) / main 3D canvas / sidebar (N) / toolbar (T) / HUD / overlays popover
- See the dedicated section below — this is the most-used editor.

### Outliner
- **Human name:** "the Outliner," "the scene tree"
- **Shows:** hierarchical list of datablocks — collections, objects, modifiers, materials, etc.
- **bpy class:** `SpaceOutliner`
- **Regions:** header / main tree / filter popover
- Display mode is set in the header (see Outliner section below).

### Properties Editor
- **Human name:** "the Properties panel," "the Properties tab"
- **Shows:** all properties of the active object and active scene, grouped into context tabs.
- **bpy class:** `SpaceProperties`
- **Regions:** header / navigation bar (vertical tab strip) / main panel area
- No sidebar. The vertical icon strip on the left **is** the tab selector — not a toolbar.

### Shader / Geometry Nodes / Compositor (Node Editor)
- **Human name:** "the Shader Editor," "the Geometry Nodes editor," "the Compositor"
- **Shows:** node graph
- **bpy class:** `SpaceNodeEditor` (shared — distinguished by `tree_type`)
- **Regions:** header / main graph / sidebar (N) / toolbar (T)
- See Node Editors section.

### Image Editor / UV Editor
- **Human name:** "the Image Editor," "the UV Editor"
- **Shows:** a 2D image or the UV map of the active mesh
- **bpy class:** `SpaceImageEditor`
- **Regions:** header / main 2D canvas / sidebar (N) / toolbar (T)
- Mode switches between Image View / UV / Paint / Mask in the header.

### Text Editor
- **Human name:** "the Text Editor," "the script editor"
- **Shows:** a text datablock (used for in-Blender Python scripts and OSL)
- **bpy class:** `SpaceTextEditor`
- **Regions:** header / main text / sidebar (N) / footer (info line)

### File Browser
- **Human name:** "the file browser," "the asset browser"
- **Shows:** files for open/save/append/link, or the Asset Browser when in asset mode
- **bpy class:** `SpaceFileBrowser`
- Asset Browser is the same Space class with `browse_mode = 'ASSETS'`.

### Graph Editor / Drivers
- **Human name:** "the Graph Editor," "the F-Curve editor," "the Drivers editor"
- **Shows:** animation F-curves
- **bpy class:** `SpaceGraphEditor`
- Mode toggles between F-Curves and Drivers in the header.

### Dope Sheet / Action Editor / Shape Key Editor / Grease Pencil / Mask
- **Human name:** "the Dope Sheet"
- **Shows:** keyframes on a timeline, grouped by data path
- **bpy class:** `SpaceDopeSheetEditor`
- Mode dropdown in the header selects the variant.

### Nonlinear Animation (NLA)
- **Human name:** "the NLA editor"
- **Shows:** animation strips per object/armature
- **bpy class:** `SpaceNLA`

### Timeline
- **Human name:** "the Timeline"
- **Shows:** playhead, frame range, keyframes for selected
- **bpy class:** `SpaceTimeline` (note: in some versions this is a sub-mode of the Dope Sheet — verify at install time)

### Preferences
- **Human name:** "Preferences," "Edit > Preferences"
- **Shows:** user preferences, addons, keymaps, themes
- **bpy class:** `SpacePreferences`
- Opens in a separate window by default.

### Python Console
- **Human name:** "the Python Console"
- **Shows:** interactive Python REPL with `bpy` pre-imported and `C`, `D` shortcuts for `bpy.context`, `bpy.data`
- **bpy class:** `SpaceConsole`

### Info Editor
- **Human name:** "the Info editor," "the log"
- **Shows:** log of operators run and their Python equivalents — the easiest way to discover the `bpy.ops.*` call behind a UI action
- **bpy class:** `SpaceInfo`

### Other editors (less common in MCP-driven workflows)
- **Video Sequencer** — `SpaceSequenceEditor` — VSE timeline for video editing.
- **Movie Clip Editor** — `SpaceClipEditor` — motion tracking, masking.
- **Spreadsheet** — `SpaceSpreadsheet` — tabular view of geometry node attributes; pairs with the Geometry Nodes editor.

See [[BLENDER_PYTHON_API]] for how to reach a Space instance from `bpy.context.space_data` or by iterating `bpy.context.screen.areas`.

---

## The 3D Viewport In Depth

The single most-referenced editor. Anything the user says about "the viewport" or "the scene" lands here.

**Modes** (set on the active object; header dropdown on the left):
- **Object Mode** — manipulate whole objects (translate, rotate, scale, parent).
- **Edit Mode** — manipulate the geometry inside the active object (verts/edges/faces for meshes, control points for curves, bones for armatures). Toggled with **Tab**.
- **Sculpt Mode** — brush-based mesh sculpting (meshes only).
- **Vertex Paint** — paint vertex colors (meshes only).
- **Weight Paint** — paint vertex group weights (meshes only, typically rigged).
- **Texture Paint** — paint directly onto image textures via the mesh (meshes only).
- **Pose Mode** — pose bones of an armature.
- **Particle Edit** — edit hair particles (meshes with particle systems).
- **Grease Pencil Draw / Edit / Sculpt / Weight / Vertex** — for Grease Pencil objects.

`bpy.context.mode` is the enum reporting current mode. See Modes section below for canonical values.

**Header** (top strip of the viewport):
- **Editor type selector** (leftmost icon) — switches this Area to a different editor.
- **Mode dropdown** — see above.
- **View / Select / Add / Object** (Object Mode) menus — change per mode (Edit Mode shows **Mesh / Vertex / Edge / Face**).
- **Transform pivot point** dropdown (Median / 3D Cursor / Individual / Active / Bounding Box).
- **Snapping toggle** + popover.
- **Proportional editing toggle** + popover.
- **Shading dropdown** (right side, four sphere icons) — Wireframe / Solid / Material Preview / Rendered.
- **Overlays popover** — toggle grid, axes, statistics, wireframes, etc.
- **Gizmos popover** — toggle navigation gizmo, transform gizmos.
- **Viewport shading options gear** — engine-specific viewport settings.

**Sidebar — the N-panel** (toggle with **N**, `region_type='UI'`):
- **Item** — transform of active object (location, rotation, scale, dimensions).
- **Tool** — settings for the currently active tool from the T-panel.
- **View** — viewport view properties (focal length, clip start/end, view lock).
- **(Add-on tabs)** — any addon that draws a Panel with `bl_space_type='VIEW_3D'`, `bl_region_type='UI'` adds a tab here, identified by `bl_category`. **This is where the BlenderMCP tab appears.**

**Toolbar — the T-panel** (toggle with **T**, `region_type='TOOLS'`):
- Active-tool selector (Select Box, Move, Rotate, Scale, Annotate, Measure in Object Mode; many more in Edit/Sculpt).
- In Edit Mode adds Knife, Bevel, Inset, Extrude variants.
- In Sculpt Mode contains the brush list.

**Gizmos and overlays:**
- The viewport navigation gizmo (top right) — orbit, zoom, pan, axis-snap.
- The transform gizmos — appear when a transform tool is active.
- Overlays are toggled per-feature in the Overlays popover (grid floor, axes, wireframes, statistics, face orientation, etc.).

---

## The Properties Editor — Context Tabs

The Properties editor (`SpaceProperties`) is a tabbed control panel. Tabs appear in a vertical icon strip on the left ("navigation bar"). The active tab is `space.context` — an enum.

Tabs that are always present:
- **Render** (`'RENDER'`) — render engine choice (Cycles / EEVEE / Workbench), engine-specific settings (samples, denoising, motion blur).
- **Output** (`'OUTPUT'`) — resolution, frame range, frame rate, file format, output path.
- **View Layer** (`'VIEW_LAYER'`) — passes, cryptomatte, view layer overrides.
- **Scene** (`'SCENE'`) — active camera, units, gravity, audio, rigid body world, keying sets.
- **World** (`'WORLD'`) — world background (sky, HDRI, color), volume, mist.

Tabs that depend on having an active object:
- **Object** (`'OBJECT'`) — transform, relations (parent, collections), visibility, viewport display.
- **Modifiers** (`'MODIFIER'`) — modifier stack (Subdivision Surface, Array, Mirror, Solidify, Boolean, Geometry Nodes, etc.). See [[BLENDER_MODELING]].
- **Particles** (`'PARTICLES'`) — only for mesh objects.
- **Physics** (`'PHYSICS'`) — rigid body, soft body, cloth, fluid, smoke, collision.
- **Object Constraints** (`'CONSTRAINT'`) — copy location, track to, IK, etc.
- **Object Data** (`'DATA'`) — geometry data of the active object. Icon and contents depend on object type:
  - Mesh → vertex groups, shape keys, UV maps, vertex colors, normals
  - Curve → curve properties, geometry, bevel
  - Light → type, color, energy, shape
  - Camera → lens, depth of field, sensor
  - Armature → bone display, layers, viewport
  - Empty → display type, size

Tabs that depend on data being present:
- **Material** (`'MATERIAL'`) — material slots and active material. Routes to the Shader Editor for node editing.
- **Texture** (`'TEXTURE'`) — legacy texture slots (mostly for brushes and modifiers in modern Blender).

Bone-related tabs only appear with an active armature:
- **Armature** (Object Data tab when armature is active).
- **Bone** (`'BONE'`) — active bone properties in Pose/Edit mode.
- **Bone Constraints** (`'BONE_CONSTRAINT'`).

When the user says "go to the Object tab of the Properties editor" — set `space.context = 'OBJECT'` or use `bpy.ops.buttons.context_menu` in practice the agent reads/writes directly on the underlying datablock and never needs to switch tabs visually.

---

## The Outliner — Display Modes

The Outliner header has a **display mode** dropdown. The mode determines what tree is shown.

- **View Layer** (default) — collections, objects, and their child datablocks for the active view layer. The mode used 95% of the time.
- **Scenes** — all scenes in the file.
- **Blender File** — every datablock in the file, grouped by type (Meshes, Materials, Textures, Images, etc.). Useful for orphan hunting.
- **Data API** — raw `bpy.data` tree. Lets you right-click any property and copy its data path.
- **Library Overrides** — overrides on linked data. Two sub-modes: Hierarchies and Properties.
- **Orphan Data** — datablocks with zero users. Use **Purge** to clean.

Selection in the Outliner syncs with the viewport. Active vs. selected works the same here.

---

## Node Editors — The Three Kinds

All three node editors share the `SpaceNodeEditor` class. They are distinguished by `space.tree_type`:

- **Shader Editor** — `tree_type = 'ShaderNodeTree'`. Header has a **shader type** selector: **Object** (material on active object), **World** (world shading), or **Line Style** (Freestyle). See [[BLENDER_SHADER_NODES]].
- **Geometry Nodes Editor** — `tree_type = 'GeometryNodeTree'`. Edits the node tree of a Geometry Nodes modifier on the active object. See [[BLENDER_GEOMETRY_NODES]].
- **Compositor** — `tree_type = 'CompositorNodeTree'`. Edits the active scene's post-processing graph.

All three have:
- **Header** — tree-type selector, pin toggle, the shader/material/group selector, options (Use Nodes, Backdrop for compositor).
- **N-panel** — Item / Tool / Group tabs. Group tab shows the inputs/outputs of the active node group.
- **T-panel** — minimal; mostly an "Add" search.

The N-panel's **Group** tab is where you edit the inputs and outputs of a node group — the interface that becomes modifier inputs in Geometry Nodes.

---

## The N-panel and T-panel

Two keyboard shortcuts and two regions — common to most editors.

- **N** — toggles the **sidebar**, `region_type='UI'`. Right side of the editor.
- **T** — toggles the **toolbar**, `region_type='TOOLS'`. Left side of the editor.

Both regions are tabbed. Tabs are populated by `bpy.types.Panel` subclasses with matching `bl_space_type`, `bl_region_type`, and a `bl_category` string. Each unique `bl_category` becomes one tab.

When a user says "I don't see the BlenderMCP tab" — the addon is either not enabled, registers panels for a different space, or the sidebar is closed. Fix order: enable addon → press N → check tab list.

---

## Workspaces

A **Workspace** is a named layout. Switching workspaces swaps the entire Area arrangement but keeps the scene and data unchanged.

- Workspace tabs run across the top of the window (the **Topbar**).
- Add a workspace with the **+** at the end of the tab strip (choose a template or duplicate current).
- Right-click a workspace tab to rename, reorder, or delete.
- Workspaces are datablocks: `bpy.data.workspaces['Layout']`. Active is `bpy.context.window.workspace`.
- The set that ships with the default file: **Layout / Modeling / Sculpting / UV Editing / Texture Paint / Shading / Animation / Rendering / Compositing / Geometry Nodes / Scripting**.

Workspaces optionally have a **pinned scene** and **filter add-ons** — both rarely used.

---

## Modes

A **mode** is per-active-object and determines which operators are valid. Mode lives in `bpy.context.mode` as one of these enum values:

- `'OBJECT'`
- `'EDIT_MESH'`, `'EDIT_CURVE'`, `'EDIT_SURFACE'`, `'EDIT_METABALL'`, `'EDIT_TEXT'`, `'EDIT_ARMATURE'`, `'EDIT_LATTICE'`
- `'POSE'`
- `'SCULPT'`
- `'PAINT_WEIGHT'`, `'PAINT_VERTEX'`, `'PAINT_TEXTURE'`
- `'PARTICLE'`
- `'PAINT_GPENCIL'`, `'EDIT_GPENCIL'`, `'SCULPT_GPENCIL'`, `'WEIGHT_GPENCIL'`, `'VERTEX_GPENCIL'`

Switch mode via `bpy.ops.object.mode_set(mode='EDIT')` — note the `mode` argument uses a different (shorter) enum: `'OBJECT'`, `'EDIT'`, `'SCULPT'`, `'VERTEX_PAINT'`, `'WEIGHT_PAINT'`, `'TEXTURE_PAINT'`, `'POSE'`, `'PARTICLE_EDIT'`, etc. The `bpy.context.mode` value is then resolved based on the active object type.

Many `bpy.ops` calls fail silently or raise `RuntimeError` if called from the wrong mode. The agent should always check mode before acting. See [[BLENDER_PYTHON_API]].

---

## Selection — Active vs Selected

Blender distinguishes two concepts that humans often conflate:

- **Selected** — a *set* of objects (or verts/edges/faces in Edit Mode). Reachable via `bpy.context.selected_objects`. In Edit Mode: `bpy.context.selected_vertices` etc., or via `bmesh`.
- **Active** — exactly *one* object (the most recently clicked). Reachable via `bpy.context.active_object` or `bpy.context.view_layer.objects.active`.

The active object is normally also in the selected set, but it is possible to have an active object that is not selected (after Alt-clicking, for example).

**UI hint** (useful for parsing screenshots and tutorials):
- **Orange outline** = selected (non-active).
- **Lighter / yellow outline** = active.
- **Red outline** = selected and active in pose/edit specific contexts.
- Outliner shows active row with a brighter highlight.

Many operators act on **selected** (`bpy.ops.object.delete()`), some on **active** (most modifier operations), and some on both. The docstring for each `bpy.ops` will say.

---

## Topbar, Header, Status Bar

Three horizontal strips that humans often confuse with each other.

- **Topbar** — the very top strip of the window. Contains the main menu (File / Edit / Render / Window / Help), the active-workspace tabs, and the scene/view-layer dropdowns. Not editor-specific.
- **Header** — the strip at the top (or bottom) of *each Editor*. Contents change per editor. This is what the user means when they say "in the viewport header" or "in the Outliner's header."
- **Status Bar** — the bottom strip of the window. Shows context-sensitive info: collection name, vertex count, memory usage, version. Configurable via right-click.

A separate **Tool Settings** strip sits below the topbar in some workspaces — this is the "Tool Header" and exposes settings for the active tool (e.g., brush radius in Sculpt Mode).

---

## Common Shortcuts the Human Will Reference

Hotkeys the agent will hear in tutorials and user requests. Mapped to what they actually do.

- **N** — toggle sidebar (N-panel) of active editor.
- **T** — toggle toolbar (T-panel) of active editor.
- **Tab** — toggle Object Mode ↔ Edit Mode on the active object.
- **G** — Grab/Move. Often chained: `G, X` (move along X), `G, Z, Z` (along local Z).
- **R** — Rotate. Same chaining (`R, X, 45, Enter`).
- **S** — Scale. Same chaining.
- **X** or **Delete** — delete selected. X prompts; Delete is immediate.
- **A** — select all (toggle).
- **Alt+A** — deselect all.
- **Shift+A** — Add menu (see below).
- **Shift+S** — Snap pie menu (Cursor to Selected, Selection to Cursor, etc.).
- **Shift+D** — duplicate.
- **Alt+D** — linked duplicate (shared data).
- **Z** — shading pie menu (Wireframe / Solid / Material Preview / Rendered).
- **`** (backtick) — viewport navigation pie (Top / Front / Side / Camera / etc.). On non-US layouts this key varies — Blender remaps if needed.
- **Ctrl+Tab** — mode pie menu.
- **F12** — render still image.
- **Ctrl+F12** — render animation.
- **Ctrl+S** — save file.
- **Ctrl+Shift+S** — save as.
- **F3** — operator search (the menu the user types into when they say "I searched for Subdivide").
- **Q** — favorites pie (user-defined; users add operators via right-click → Add to Quick Favorites).

---

## The Add Menu (Shift+A) Categories

In the 3D Viewport, Object Mode. Each is a `bpy.ops.object.*` or `bpy.ops.mesh.primitive_*` family.

- **Mesh** — Plane, Cube, Circle, UV Sphere, Ico Sphere, Cylinder, Cone, Torus, Grid, Monkey.
- **Curve** — Bezier, Circle, Path, NURBS variants.
- **Surface** — NURBS surfaces.
- **Metaball** — Ball, Capsule, Plane, Ellipsoid, Cube.
- **Text** — 3D text object.
- **Volume** — Empty, Import OpenVDB.
- **Grease Pencil** — Blank, Stroke, Monkey, Scene templates.
- **Armature** — single bone, ready to extrude.
- **Lattice** — deformation cage.
- **Empty** — Plain Axes, Arrows, Single Arrow, Circle, Cube, Sphere, Cone, Image.
- **Image** — Reference, Background (also under Empty in current versions).
- **Light** — Point, Sun, Spot, Area.
- **Light Probe** — Sphere, Plane, Volume (for EEVEE indirect lighting).
- **Camera** — perspective by default.
- **Speaker** — for spatial audio.
- **Force Field** — Force, Wind, Vortex, Magnetic, Harmonic, Charge, Lennard-Jones, Texture, Curve Guide, Boid, Turbulence, Drag, Fluid Flow.
- **Collection Instance** — instances an existing collection at the cursor.

These are the most common agent targets. See [[BLENDER_PYTHON_API]] for the exact ops calls.

---

## Editor-Specific N-panel Tabs

Tabs vary by editor. The most useful to know:

- **3D Viewport** — **Item / Tool / View**, plus any addon tabs (BlenderMCP, Node Wrangler addons that draw in viewport, etc.).
- **Shader Editor / Geometry Nodes / Compositor** — **Item / Tool / Group**. (Group exposes node-tree interface.)
- **Image / UV Editor** — **Image / Tool / View / Grease Pencil**.
- **Text Editor** — **Properties** (font, line numbers, find/replace).
- **Outliner** — no sidebar (filter is a popover in the header).
- **Properties** — no sidebar; its vertical icon strip is the tab navigation, not an N-panel.
- **Timeline** — no sidebar.

Addon tabs are namespaced by `bl_category` string. Multiple addons with the same category share a tab.

---

## Pies and Popovers

- **Pie menus** — radial 8-direction menus invoked by hotkey. Built-in pies: **Z** (shading), **`** (viewport navigation), **Ctrl+Tab** (mode), **Q** (favorites — user-defined), **Shift+S** (snap).
- **Popovers** — temporary panels that anchor to a UI element (e.g., the Overlays popover, the Gizmos popover, the Snapping popover). Click outside to close.
- **Operator panel (HUD)** — appears in the bottom-left of the viewport after running an operator (e.g., Bevel, Loop Cut). Lets you tweak the parameters of the last operator. Equivalent to editing `bpy.context.window_manager.operator_properties_last` — though the canonical Python pattern is to re-call the operator with explicit kwargs.

---

## What "Press N to Open the BlenderMCP Tab" Actually Means

A worked example that ties the whole vocabulary together.

The Blender MCP addon registers one or more `bpy.types.Panel` subclasses with:
- `bl_space_type = 'VIEW_3D'`
- `bl_region_type = 'UI'`
- `bl_category = 'BlenderMCP'`

When the user says **"press N to open the BlenderMCP tab"**, the literal sequence is:

1. Focus the 3D Viewport area (`area.type == 'VIEW_3D'`).
2. Press **N** — Blender toggles the `UI` region's visibility on that area. Internally: `area.regions[<UI region>].active = True`. Note: visibility is controlled via the `show_region_ui` property on `SpaceView3D` — set `bpy.context.space_data.show_region_ui = True`.
3. The right sidebar now shows a vertical strip of tabs — one per unique `bl_category` across all enabled Panels.
4. Click **BlenderMCP** in that strip — Blender filters the panel list to those with `bl_category == 'BlenderMCP'`.

For the agent: this means the addon's panel layout is fully introspectable. Iterate `bpy.types.Panel.__subclasses__()` to find every BlenderMCP panel and read their `bl_label`. You never have to actually click the tab — the operator buttons inside those panels each map to a `bpy.ops.<idname>()` call that can be invoked directly. The UI is a convenience; the API is the ground truth.

---

## bpy ↔ UI Cheat-Sheet

When the human says X, reach for Y.

| Human reference | bpy path |
|---|---|
| "the active object" | `bpy.context.active_object` |
| "the selected objects" | `bpy.context.selected_objects` |
| "the current scene" | `bpy.context.scene` |
| "the current frame" | `bpy.context.scene.frame_current` |
| "the start/end frame" | `bpy.context.scene.frame_start` / `frame_end` |
| "the render engine" | `bpy.context.scene.render.engine` |
| "the render resolution" | `bpy.context.scene.render.resolution_x` / `resolution_y` |
| "the output path" | `bpy.context.scene.render.filepath` |
| "the world background" | `bpy.context.scene.world` |
| "the active camera" | `bpy.context.scene.camera` |
| "the active material" | `bpy.context.active_object.active_material` |
| "the material slots" | `bpy.context.active_object.material_slots` |
| "the active modifier" | `bpy.context.active_object.modifiers.active` |
| "the modifier stack" | `bpy.context.active_object.modifiers` |
| "the active object's mesh data" | `bpy.context.active_object.data` |
| "the vertices" (Object Mode) | `bpy.context.active_object.data.vertices` |
| "the vertices" (Edit Mode) | use `bmesh.from_edit_mesh(obj.data).verts` |
| "the active collection" | `bpy.context.collection` |
| "the active workspace" | `bpy.context.window.workspace` |
| "the current mode" | `bpy.context.mode` |
| "the viewport" (active 3D view) | iterate `bpy.context.screen.areas` for `area.type == 'VIEW_3D'`, read `area.spaces.active` |
| "the N-panel" / "the sidebar" | `space.show_region_ui` on the relevant Space |
| "the toolbar" / "T-panel" | `space.show_region_toolbar` |
| "the active node" | `bpy.context.active_node` (in node editor context) |
| "the active bone" | `bpy.context.active_pose_bone` or `bpy.context.active_bone` |
| "the 3D cursor location" | `bpy.context.scene.cursor.location` |
| "the active view layer" | `bpy.context.view_layer` |

See [[BLENDER_DATA_MODEL]] for the broader datablock map and [[BLENDER_PYTHON_API]] for context overrides, operator calling, and the difference between `bpy.context` and `bpy.data`.
