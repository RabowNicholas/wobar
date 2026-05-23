---
title: Add-ons — Extension System, Essential Add-ons, MCP as Add-on
version: 1.0
last_updated: 2026-05-22
status: live
scope: Blender add-on system reference — the 4.2+ Extensions repository, enabling/disabling via bpy, the essential add-ons every Blender setup needs (Node Wrangler, Loop Tools, Hard Ops/BoxCutter optional, Quad Remesher, Auto-Rig Pro, the official MCP connector), the structure of an add-on, common gotchas with version mismatches.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md
---

# ADD-ONS — EXTENSION SYSTEM, ESSENTIAL ADD-ONS, MCP AS ADD-ON

An add-on is a **Python module** that extends Blender by registering operators, panels, menus, properties, and handlers into `bpy`. Historically (pre-4.2) add-ons shipped two ways: bundled with the Blender install (`scripts/addons/`) or user-installed via the legacy `Install from File…` button. **Blender 4.2 LTS replaced this with the Extensions system** — a signed, manifest-based distribution model backed by `extensions.blender.org`. Most formerly-bundled add-ons (Node Wrangler, LoopTools, Bool Tool, F2, etc.) now live in the Extensions repo, but a small core set still ships in the Blender binary. The Blender Foundation's official MCP connector is itself an add-on installed through the same machinery — see Section 8.

**Core facts:**
- Add-ons are Python modules with a `register()` and `unregister()` function. Enabling an add-on imports the module and calls `register()`.
- Legacy add-ons use a `bl_info` dict at the top of the file. Extensions-system add-ons use a `blender_manifest.toml` next to the script.
- Bundled add-ons ship in the Blender install directory and only need to be **enabled** (checkbox), not installed. They appear in Preferences → Add-ons.
- User-installed add-ons go to the per-user config: macOS `~/Library/Application Support/Blender/4.x/extensions/`, Windows `%APPDATA%/Blender Foundation/Blender/4.x/extensions/`, Linux `~/.config/blender/4.x/extensions/`.
- The Extensions Browser (Preferences → Get Extensions) is the new install UI; it pulls from `extensions.blender.org` over HTTPS.
- The `enabled` add-on set lives in **user preferences**, not in the `.blend` file. Sending a `.blend` to someone else does not transfer add-on state.
- Add-ons that fail their `bl_info['blender']` minimum-version check are shown but greyed out with a warning.
- Add-on operators are not available until the add-on is enabled — calling `bpy.ops.node.nw_*` with Node Wrangler disabled returns `'CANCELLED'`.
- The official MCP connector is distributed as a `.zip` add-on with a drag-and-drop install URL from `blender.org/lab/mcp-server/`.
- Add-on preferences (per-addon settings) live at `bpy.context.preferences.addons['module_name'].preferences` and must be **saved** with `bpy.ops.wm.save_userpref()` to persist.
- Add-on enablement does **not** require restart — `register()` runs immediately. Some add-ons (those that patch keymaps at load time) behave better after a restart.

---

## The Extensions System (4.2+)

Blender 4.2 LTS introduced a fundamental change to add-on distribution. Before 4.2, every Blender release shipped with ~60 bundled add-ons in `scripts/addons/`. From 4.2 onward, the bundled set was trimmed to a core handful (importers/exporters, Cycles, Rigify, and a few essentials); everything else moved to **`extensions.blender.org`** — an official, signed, web-based repository.

- **`extensions.blender.org`** — the official repo. As of 4.5 LTS it hosts ~600 free add-ons and themes, all open-source-licensed.
- **Preferences → Get Extensions** — the in-Blender browser. Search, install, update, and remove extensions without leaving the app.
- **"Allow Online Access"** — a single global preference (Preferences → System) that gates all network features in Blender, including the Extensions Browser. Off by default on first launch; the user is prompted on first Get Extensions visit.
- **Trust model** — Extensions are distributed as signed packages with a `blender_manifest.toml`. The manifest declares the add-on's Blender version compatibility, permissions, and dependencies. Blender displays the requested permissions before install.
- **Install paths** — three routes:
  1. **Browse and install in-app** — Preferences → Get Extensions → search → Install.
  2. **Drag-and-drop a .zip** — drop a `.zip` extension package directly onto the Blender window. This is the offline path.
  3. **Drag-and-drop an install URL** — drag a `blender.org`-hosted install link onto Blender, which triggers `bpy.ops.preferences.extension_url_install`. **This is how the MCP connector installs.**
- **Updates** — manual: Preferences → Get Extensions → "Check for Updates" button. Blender does not auto-update extensions.
- **Repositories** — multiple repos can be configured. The default is `extensions.blender.org`. Studios can host private repos for in-house extensions.

---

## Add-on Lifecycle via bpy

```python
# Install from a local .zip
bpy.ops.preferences.addon_install(filepath='/path/to/addon.zip', overwrite=True)

# Enable by module name (the directory or .py filename, without extension)
bpy.ops.preferences.addon_enable(module='node_wrangler')

# Disable
bpy.ops.preferences.addon_disable(module='node_wrangler')

# Remove entirely
bpy.ops.preferences.addon_remove(module='node_wrangler')

# Persist enabled state across Blender launches
bpy.ops.wm.save_userpref()

# Extensions-system installs (4.2+)
bpy.ops.preferences.extension_url_install(
    url='https://extensions.blender.org/api/v1/extensions/.../archive.zip'
)
bpy.ops.extensions.repo_sync(repo_index=0)  # refresh repo metadata
```

Module names for bundled add-ons follow the file/folder name in `scripts/addons/`. Extensions-system add-ons are namespaced — `bl_ext.<repo>.<module>`, e.g. `bl_ext.blender_org.node_wrangler`.

---

## Bundled Add-ons Worth Enabling on a Fresh Install

These ship with Blender (or are core extensions auto-installed on first launch) and are off by default. Almost every workflow needs at least the first three.

- **Node Wrangler** — *Must enable.* Power tools for Shader / Geometry Nodes / Compositor editors. Highlights:
  - **Ctrl+Shift+T** on a Principled BSDF — pick a folder of PBR textures (BaseColor, Roughness, Normal, Metallic, Displacement, etc.) and Node Wrangler auto-builds the full graph with correct color spaces and Normal Map / Displacement nodes wired in.
  - **Ctrl+Drag** between nodes — insert a new node mid-link.
  - **Shift+W** — quick access menu for all NW tools.
  - **Alt+S** — swap two selected nodes' positions.
  - **Shift+Ctrl+LMB** on a node — preview that node's output through an Emission/Viewer to the active output.
  - **A** while nodes selected — align horizontally/vertically.
  - **F** with nodes selected — wrap in a labeled Frame node.
  - See `[[BLENDER_SHADER_NODES]]` for shader-graph workflow notes.

- **LoopTools** — Edit-mode mesh extras: **Bridge** (connect two edge loops), **Circle** (round a selection into a perfect circle — invaluable for screw holes, lens openings), **Curve** (re-shape an edge loop along a smooth curve), **Flatten** (project a selection to a best-fit plane), **GStretch** (stretch geometry along a grease-pencil stroke), **Relax** (smooth edge flow without sculpting), **Space** (evenly distribute vertices along a loop).

- **Bool Tool** — Faster boolean operators in Edit/Object mode. Ctrl+Numpad+/-/* for Union/Difference/Intersect on the active pair. Not as powerful as Hard Ops but free.

- **Extra Objects (Mesh)** — `add_mesh_extra_objects`. Additional mesh primitives: rounded cube, geodesic dome, Menger sponge, math functions, gears, pipe joints.

- **Extra Objects (Curves)** — `add_curve_extra_objects`. Spirals, knots, Bezier curve presets.

- **Import Images as Planes** — `io_import_images_as_planes`. File → Import → Images as Planes. Drops an image into the scene as a textured plane with the image's aspect ratio. The reference-board workhorse.

- **Copy Attributes Menu** — `space_view3d_copy_attributes`. Ctrl+C in the 3D Viewport opens a menu to copy any object attribute (location, rotation, scale, constraints, modifiers, drivers) to selected objects.

- **F2** — Edit-mode F-key extended. With one vertex or edge selected, F creates a quad inferred from surrounding topology. The standard retopo accelerator.

- **Stored Views** — `space_view3d_stored_views`. Save and recall named camera/viewport positions per-scene. Useful for showing the same shot from multiple angles during review.

- **Auto Save Render** — `render_auto_save`. Automatically saves the post-render image to a folder with a timestamp. Cheap insurance against forgetting to save the F12 output.

- **VRM addon** — `io_scene_vrm`. VRM avatar I/O. Specialized, but essential for any VTuber, MetaHuman-adjacent, or VRChat pipeline.

- **Animation Nodes** — *Legacy flag.* A pre-Geometry-Nodes procedural framework. Largely superseded by Geometry Nodes since 3.0. Only enable for legacy `.blend` files that depend on it; do not start new projects with it.

---

## Importer / Exporter Bundled Add-ons

Most are off by default. Enable as the pipeline demands. See `[[BLENDER_ASSET_IO]]` for format-specific notes.

- **FBX** — `io_scene_fbx`. Ubiquitous game-engine interchange. Bundled, enabled by default.
- **glTF 2.0** — `io_scene_gltf2`. The modern open standard for real-time. Bundled, enabled by default. Best results for web/Three.js/Babylon pipelines.
- **OBJ** — Blender 4.x ships a **native fast C++ OBJ implementation** (File → Import/Export → Wavefront (.obj)). The legacy Python `io_scene_obj` add-on is **deprecated** — do not enable it in 4.x.
- **STL** — Same story. 4.x has native fast STL. Legacy `io_mesh_stl` is deprecated.
- **USD** — `io_scene_usd`. Pixar Universal Scene Description. Bundled, enabled by default in 4.x. The Hydra render delegate path also depends on this.
- **Alembic** — Built into Blender core, **not an add-on**. File → Import/Export → Alembic is always available.
- **VRM** — `io_scene_vrm` (community). Avatar format. See above.
- **Collada** — `io_scene_collada` / `io_anim_bvh` — legacy interchange; rarely needed unless dealing with old motion-capture or SketchUp exports.

---

## Major Paid Third-Party Add-ons Worth Knowing

Not required, not currently installed in any default workflow, but ubiquitous enough that an agent should recognize references to them. All paid, all from Blender Market or Gumroad unless noted.

- **Hard Ops + BoxCutter** (masterxeon1001) — the canonical hard-surface modeling duo. BoxCutter is a draw-on-mesh boolean cutter; Hard Ops is a modifier/bevel/edge-management toolkit. Together they define modern destructive sci-fi/mech workflows in Blender.
- **Quad Remesher** (Exoside) — best-in-class auto-retopology. One-click conversion of dense triangulated meshes to clean quad topology. Paid plugin with a separate per-seat license.
- **Auto-Rig Pro** (Lucky3D) — production-grade auto-rigging for biped/quadruped character work. Includes Mixamo export, IK/FK switching, and game-engine-ready skeleton presets.
- **Real Snow / Real Grass / Real Cloth / Real Dirt** (Blender Market) — procedural-look add-ons that drop polished material/geometry presets onto selected objects.
- **Decal Machine** (machin3) — non-destructive decal placement. Attach labels, screws, vents, panel lines as decals projected from libraries.
- **MeshMachine** (machin3) — non-destructive mesh editing focused on hard-surface fusion and bevel cleanup.
- **Asset Sketcher / Asset Wizard** — scatter and asset-library management. Asset Sketcher emphasizes painting assets onto surfaces; Asset Wizard focuses on the import side.
- **Animation Layers** — non-destructive animation layering, similar to Maya's Anim Layers.
- **MMD Tools / Cats Plugin** — anime / VTuber pipeline. MMD Tools imports MikuMikuDance PMX/PMD files; Cats normalizes them for VRChat export.

---

## The MCP Connector as an Add-on

**Meta-note for the agent:** the Blender Foundation's official MCP connector at `blender.org/lab/mcp-server/` **is a Blender add-on**. There is no separate "MCP install" mechanism — installation, enabling, and uninstallation use the same `bpy.ops.preferences.addon_*` operators documented above.

- The drag-and-drop install link on the lab page triggers `bpy.ops.preferences.extension_url_install` with the manifest URL.
- Once installed, it registers a panel in the **3D Viewport N-panel** under the **"BlenderMCP"** tab.
- The panel exposes a **"Connect to Claude"** button which starts a local socket server (default port varies by version; see the lab page) that the MCP client speaks to.
- The add-on registers operators under `bpy.ops.blendermcp.*` — these are the same operators Claude calls remotely when driving Blender.
- Disabling the add-on shuts down the socket server. Re-enabling restarts it.
- If the "BlenderMCP" tab does not appear after install, the add-on is installed but **not enabled** — check Preferences → Add-ons → search "MCP". This is the single most common failure mode.

---

## The ahujasid/blender-mcp Community Add-on

Documented for completeness; **not currently used in this workflow**. A separate, community-maintained add-on distributed via GitHub (`github.com/ahujasid/blender-mcp`) that predates the official Blender Foundation connector.

- Installed via the legacy `Install from File…` route (or drag-and-drop the `.zip` onto Blender).
- Requires `uv` (Python package manager from Astral) and a JSON entry in `claude_desktop_config.json` pointing at the MCP server script.
- Provides additional integrations the official connector does not: **Poly Haven** HDRI / texture / model download, **Hyper3D Rodin** text-to-mesh generation, viewport screenshot capture, **Sketchfab** asset import.
- Operators land under `bpy.ops.blendermcp.*` (name collision with the official connector — do not enable both simultaneously).

---

## Add-on Structure

A minimal add-on is a single `.py` file with a `bl_info` dict and `register`/`unregister` functions:

```python
bl_info = {
    "name": "My Add-on",
    "author": "Me",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),     # minimum Blender version
    "location": "View3D > Sidebar > MyTab",
    "category": "3D View",
}

import bpy

class MY_OT_hello(bpy.types.Operator):
    bl_idname = "my.hello"
    bl_label = "Hello"
    def execute(self, context):
        self.report({'INFO'}, "hi")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MY_OT_hello)

def unregister():
    bpy.utils.unregister_class(MY_OT_hello)
```

For larger add-ons, the file becomes a **package** (a folder with `__init__.py`) containing operators, panels, properties, and keymap registration. See `[[BLENDER_PYTHON_API]]` for the `bpy.utils.register_class` / `PropertyGroup` patterns.

**Extensions manifest (4.2+)** — alongside the Python module, an Extensions-system add-on includes `blender_manifest.toml`:

```toml
schema_version = "1.0.0"
id = "my_addon"
version = "1.0.0"
name = "My Add-on"
tagline = "Does a thing"
maintainer = "Me <me@example.com>"
type = "add-on"
blender_version_min = "4.2.0"
license = ["SPDX:GPL-3.0-or-later"]
tags = ["3D View"]
```

The manifest **replaces `bl_info`** for Extensions-system distribution; the legacy `bl_info` is still read for bundled add-ons. Both can coexist for back-compat during the transition.

---

## Inspecting Which Add-ons Are Enabled

```python
import bpy

# List enabled add-on module names
list(bpy.context.preferences.addons.keys())
# → ['cycles', 'io_scene_fbx', 'io_scene_gltf2', 'node_wrangler', ...]

# Check if a specific add-on is enabled
'node_wrangler' in bpy.context.preferences.addons

# Access a specific add-on's preferences
prefs = bpy.context.preferences.addons['node_wrangler'].preferences
# (the .preferences attribute is an AddonPreferences subclass defined by the add-on)

# Iterate all available (installed) add-ons including disabled ones
import addon_utils
for mod in addon_utils.modules():
    print(mod.__name__, addon_utils.check(mod.__name__))
    # check() returns (loaded_default, loaded_state)
```

For Extensions-system add-ons, the module key is the namespaced form: `bl_ext.blender_org.node_wrangler`.

---

## Common Add-on Gotchas

1. **Installed but not enabled.** The most common failure. The add-on appears in the list but the checkbox is unticked → its operators are missing from menus and `bpy.ops.<addon>.*` returns `CANCELLED` or raises `AttributeError`. Fix: Preferences → Add-ons → search → tick checkbox → save user prefs.
2. **Enabled but breaks on a new Blender version.** `bl_info['blender']` minimum-version check passes but an internal API the add-on uses was removed/renamed (e.g. `bpy.types.SpaceView3D.draw_handler_add` signature changes, the `2.8 → 2.93 → 3.0 → 4.0` operator-name shifts). Symptom: red error text in the Add-on Preferences entry, plus a traceback in the System Console. Fix: update the add-on, or pin Blender to the last working LTS.
3. **Preferences not saved.** Enabled the add-on this session, but on next launch it's disabled again. Cause: `bpy.ops.wm.save_userpref()` was never called. Preferences → bottom-left hamburger → "Save Preferences". Or set Preferences → "Auto-Save Preferences" on.
4. **Hotkey collisions.** Two add-ons binding the same shortcut (e.g. Hard Ops and Bool Tool both wanting Ctrl+Numpad+). Symptom: only one fires, or one silently shadows the other. Fix: Preferences → Keymap → search the hotkey → resolve conflict per-keymap.
5. **Extensions install fails silently in offline mode.** With "Allow Online Access" off, the Extensions Browser shows an empty list and `extension_url_install` errors with a network message. Fix: Preferences → System → "Allow Online Access" on; or download the `.zip` separately and drag-drop install.
6. **Import errors on enable.** The add-on enables but immediately disables itself with red traceback text. Common causes: missing Python dependency (the add-on `import`s a package not bundled with Blender), wrong file structure inside the `.zip` (the manifest/`__init__.py` must be at the root, not nested inside an extra folder). Check the System Console (Window → Toggle System Console on Windows; launch Blender from a terminal on macOS/Linux) for the traceback.
7. **macOS vs Windows add-on paths.** The per-user add-on directory differs:
   - macOS: `~/Library/Application Support/Blender/<version>/extensions/` and `.../scripts/addons/`
   - Windows: `%APPDATA%\Blender Foundation\Blender\<version>\extensions\` and `...\scripts\addons\`
   - Linux: `~/.config/blender/<version>/extensions/` and `.../scripts/addons/`
   Scripts that hardcode one OS's path break on the others. Use `bpy.utils.user_resource('EXTENSIONS')` / `'SCRIPTS'`.
8. **`version` field mismatch with changelog.** An add-on's `bl_info['version']` or `blender_manifest.toml` `version` field hasn't been bumped, so two functionally different builds report the same version number. Symptom: agent or user "updates" the add-on and sees no change in the Preferences UI even though behavior shifted. Fix: trust file mtime over the displayed version when debugging.
9. **Module name collisions between bundled and Extensions versions.** During the 4.2 transition some add-ons exist in both the legacy bundled location and the Extensions repo with slightly different module paths (`node_wrangler` vs `bl_ext.blender_org.node_wrangler`). Enabling both at once can register classes twice and raise `Error: register_class(...): already registered`. Fix: pick one path, disable the other.
10. **Per-add-on `preferences` attribute missing.** Accessing `bpy.context.preferences.addons['x'].preferences` raises `AttributeError` if the add-on does not define an `AddonPreferences` subclass. Not all add-ons do. Guard with `getattr(..., 'preferences', None)`.

---

## Cross-references

- `[[BLENDER_PYTHON_API]]` — operator/panel/property registration patterns add-ons depend on.
- `[[BLENDER_SHADER_NODES]]` — Node Wrangler's shader-graph workflows in context.
- `[[BLENDER_ASSET_IO]]` — FBX, glTF, USD, OBJ, STL pipeline notes.
- `[[BLENDER_LIBRARY_INDEX]]` — top-level Blender library map.

---

## Sources

- Blender Manual — Add-ons preferences: `https://docs.blender.org/manual/en/latest/editors/preferences/addons.html`
- Blender Manual — Extensions (4.5 LTS): `https://docs.blender.org/manual/en/4.5/editors/preferences/extensions.html`
- Blender Extensions repository: `https://extensions.blender.org/`
- Blender Extensions manual: `https://docs.blender.org/manual/en/latest/advanced/extensions/index.html`
- Devtalk announcement — Changes to Add-on and Themes Bundling (4.2 onwards): `https://devtalk.blender.org/t/changes-to-add-on-and-themes-bundling-4-2-onwards/34593`
- `blender/blender-addons` repo (frozen at 4.1, historical): `https://projects.blender.org/blender/blender-addons`
- Node Wrangler manual: `https://docs.blender.org/manual/en/4.2/addons/node/node_wrangler.html`
- Blender Foundation MCP Lab page: `https://www.blender.org/lab/mcp-server/`
