---
title: Animation — Keyframes, Drivers, F-Curves, NLA, Armatures
version: 1.0
last_updated: 2026-05-22
status: live
scope: Blender animation reference — the keyframe data model (Actions / F-Curves / Keyframes / Slots), drivers (Python and built-in), the NLA editor and strip stacking, armature posing and rigging basics, the bpy AnimData surface, audio-baked-to-F-curve pattern, agent-friendly vs human-only workflows.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_DATA_MODEL.md
---

# ANIMATION — KEYFRAMES, DRIVERS, F-CURVES, NLA, ARMATURES

Blender animation has **three layers of motion**, stacked from explicit to procedural:

1. **Keyframes** — explicit poses-in-time. You set a value at frame N, another at frame M, Blender interpolates. The simplest and most authored layer.
2. **Drivers** — programmatic relationships. A property is computed every frame from a Python expression that reads other properties. No keyframes, no curves to author — a formula runs at evaluation time.
3. **NLA (Non-Linear Animation)** — composite stacked Actions on tracks. Reuse, layer, sequence, and blend named Actions like clips on a video timeline.

Sitting on top of all three: **armatures** (skeletal rigs) and **shape keys** (blendshapes), which use the same keyframe/driver/NLA machinery but address bone transforms or vertex deltas instead of object properties.

**Anthropic launch positioning — animation is mostly-unsolved-by-agents.** Agents driving the official Blender Foundation MCP connector are reliable for **structural, parametric, and data-driven motion**: inserting keyframes on specified properties, attaching F-curve modifiers, wiring drivers, baking audio to curves, stamping constraints, sequencing NLA strips. Agents are **not** reliable for **performance animation** — timing/spacing, anticipation/overshoot, walk cycles, facial expression, complex rigs. When the user asks for "the bouncing ball" with the right squash-and-stretch feel, expect to need human authorship on the handles and timing. When the user asks for "scale this cube on every kick drum hit," that's agent-deliverable end-to-end.

**Core facts:**
- Animation data lives on an `AnimData` container attached to most ID datablocks — `Object`, `Material`, `NodeTree`, `World`, `Camera`, `Light`, `MeshSequenceCacheFile`, `ShapeKey`, `Action` itself (for layered Actions in 4.4+), and more.
- Each `AnimData` has **one active Action** (`anim_data.action`), an **NLA track list** (`anim_data.nla_tracks`), and a **drivers list** (`anim_data.drivers`).
- An `Action` is a named, reusable container of F-Curves. Lives in `bpy.data.actions`. Can be assigned to many AnimData slots in 4.4+.
- An `FCurve` has a `data_path` (string, e.g. `'location'` or `'modifiers["Subsurf"].levels'`) and an optional `array_index` (int, for vector components). It contains a `keyframe_points` collection and an optional `modifiers` stack.
- A `Keyframe` (a `BezierTriple` inside `keyframe_points`) is `(frame, value)` plus left/right handle coordinates and per-keyframe interpolation type.
- A **driver** replaces an F-curve with a Python expression. Read via `fcurve.driver` after `obj.driver_add(...)`.
- The **NLA** stacks Actions on tracks. Strips have blend modes (Replace/Combine/Add/Subtract/Multiply), influence (0..1), extrapolation, scale, and offset.
- **Armatures** have a separate Pose system. `obj.pose.bones[name]` is a `PoseBone` — the pose-mode transform layered on top of the rest-pose `Bone`.
- **4.4+ Action Slots** — one Action can now hold animation for multiple datablocks via named **slots**. `action.slots`. Legacy single-slot API still works but is deprecated, removal target Blender 5.0.
- The **timeline cursor** is `scene.frame_current`; setting it does NOT auto-evaluate dependent properties — use `scene.frame_set(frame)` to force update.
- **FPS** lives on `scene.render.fps` (int) and `scene.render.fps_base` (float). Actual FPS = `fps / fps_base`.
- The **playback range** is `scene.frame_start` … `scene.frame_end`. `scene.frame_step` controls stride during render and playback.

---

## The AnimData Container — Where Animation Lives

Most ID datablocks expose an `animation_data` attribute. **It is `None` until something is animated on that ID.**

```python
obj = bpy.data.objects['Cube']
print(obj.animation_data)              # None on a fresh object
obj.animation_data_create()            # Creates the container
print(obj.animation_data)              # <bpy_struct, AnimData>
```

The `animation_data_create()` call is **idempotent and safe** — agents should call it before assigning an Action or driver on any ID that might not have AnimData yet.

**Where AnimData attaches:**
- `obj.animation_data` — object-level (location/rotation/scale, custom props, modifier params via path)
- `mat.animation_data` — material-level
- `mat.node_tree.animation_data` — shader node values; this is a **separate AnimData** from the Material's
- `obj.data.animation_data` — mesh / curve / camera / light data block animation
- `obj.data.shape_keys.animation_data` — shape key animation (note: shape_keys is a separate ID)
- `world.animation_data` — world settings
- `scene.animation_data` — scene-level (render settings, frame_current itself, etc.)

**AnimData fields agents touch:**
- `.action` — the active Action (read/write)
- `.action_slot` (4.4+) — which slot of the Action drives this AnimData
- `.nla_tracks` — the NLA stack
- `.drivers` — the per-ID driver list
- `.use_nla` — bool, whether the NLA evaluates
- `.action_blend_type`, `.action_influence`, `.action_extrapolation` — how the active Action layers over the NLA result

**Footgun:** an Action assigned but no slot bound (4.4+) silently produces no animation. Always set `action_slot` after assignment if you need single-slot legacy behavior.

---

## Actions and F-Curves

An `Action` is a named, reusable container of F-Curves (and, in 4.4+, slots and layers).

```python
action = bpy.data.actions.new(name="CubeBounce")
obj.animation_data_create()
obj.animation_data.action = action
```

**Actions live in `bpy.data.actions`** — independent of any Object. You can assign the same Action to many AnimData containers (and with 4.4+ slots, store separate channels for each inside one Action).

**The F-Curve `data_path`** is a string that names the property to animate, relative to the AnimData's owner:
- `'location'` — animate the location vector
- `'rotation_euler'` — animate the Euler rotation vector
- `'scale'` — animate scale
- `'modifiers["Subsurf"].levels'` — animate a modifier parameter
- `'pose.bones["Bone.001"].location'` — animate a bone transform (when AnimData is on the Object)
- `'data.shape_keys.key_blocks["Smile"].value'` — DOES NOT WORK from object AnimData; shape key AnimData is its own container. Animate `'key_blocks["Smile"].value'` from `obj.data.shape_keys.animation_data` instead.
- `'["my_custom_prop"]'` — animate a custom property (RNA-pathed)

**`array_index`** picks one component of a vector property:
- `array_index=0` — X
- `array_index=1` — Y
- `array_index=2` — Z
- `array_index=-1` — all components (treated as a scalar where the API allows)

A vector property like `location` produces **three F-curves** when fully animated — one per component, distinguished by `array_index`.

**Reading F-curves on an Action:**
```python
for fc in action.fcurves:
    print(fc.data_path, fc.array_index, len(fc.keyframe_points))
```

**Finding an F-curve by path + index:**
```python
fc = action.fcurves.find('location', index=0)   # X-location curve, or None
```

**Creating an F-curve directly (rare; prefer keyframe_insert):**
```python
fc = action.fcurves.new(data_path='location', index=2, action_group='LocZ')
```

---

## Keyframes — The (frame, value) Points

Each F-curve holds a `keyframe_points` collection. Each point is a `Keyframe` with:

- `co` — `(frame, value)` Vector2
- `handle_left`, `handle_right` — Vector2 handles for Bezier interpolation
- `handle_left_type`, `handle_right_type` — `'FREE' | 'ALIGNED' | 'VECTOR' | 'AUTO' | 'AUTO_CLAMPED'`
- `interpolation` — `'CONSTANT' | 'LINEAR' | 'BEZIER' | 'SINE' | 'QUAD' | 'CUBIC' | 'QUART' | 'QUINT' | 'EXPO' | 'CIRC' | 'BACK' | 'BOUNCE' | 'ELASTIC'`
- `easing` — `'AUTO' | 'EASE_IN' | 'EASE_OUT' | 'EASE_IN_OUT'` (for non-Bezier curve interpolations)
- `amplitude`, `back`, `period` — extra params for ELASTIC/BACK
- `type` — `'KEYFRAME' | 'BREAKDOWN' | 'MOVING_HOLD' | 'EXTREME' | 'JITTER'` (semantic tag, no math effect)

**Inserting a keyframe** — the high-level path:
```python
obj.keyframe_insert(data_path='location', frame=1)            # all 3 components
obj.keyframe_insert(data_path='location', frame=24, index=2)  # Z only
obj.keyframe_insert(data_path='rotation_euler', frame=1)
obj.keyframe_insert(data_path='["my_prop"]', frame=10)        # custom prop
```

The value used is **whatever the property currently holds**. Set the property first, then keyframe.

**Deleting a keyframe:**
```python
obj.keyframe_delete(data_path='location', frame=24)
```

**Editing handles directly:**
```python
fc = obj.animation_data.action.fcurves.find('location', index=2)
kp = fc.keyframe_points[0]
kp.interpolation = 'BEZIER'
kp.handle_left_type = 'AUTO_CLAMPED'
kp.handle_right_type = 'AUTO_CLAMPED'
fc.update()   # Recompute the curve cache after edits
```

**Footgun:** after batch-editing `keyframe_points`, call `fc.update()` once. Without it, the cached evaluation may show stale values.

---

## The Action Slot System (Blender 4.4+)

**The change:** before 4.4, one Action could only drive one datablock cleanly. Assigning the same Action to two Objects produced ambiguous behavior. 4.4 introduces **slots** — named bindings inside an Action, each tied to an ID type, each holding its own set of F-curves.

**Why it matters for agents:**
- You can author a single "Character.Walk" Action that contains an OBJECT slot (root motion) and an ARMATURE slot (bone animation), and assign it to both the Object and the Armature data without splitting Actions.
- A linked-asset Action carries its animation across multiple linked instances cleanly.
- The legacy single-Action-per-datablock pattern still works through the **backward-compatible legacy API**, which operates on slot 0 implicitly. Removal target is Blender 5.0.

**Working with slots:**
```python
action = bpy.data.actions.new("Walk")
slot_obj = action.slots.new(id_type='OBJECT', name="RootMotion")
slot_arm = action.slots.new(id_type='OBJECT', name="ArmaturePose")  # armature-owning Object

obj.animation_data_create()
obj.animation_data.action = action
obj.animation_data.action_slot = slot_obj
```

**ID types** an action slot can target include `'OBJECT'`, `'MESH'`, `'CURVE'`, `'MATERIAL'`, `'NODETREE'`, `'KEY'` (shape keys), `'CAMERA'`, `'LIGHT'`, `'WORLD'`, `'SCENE'`, `'ARMATURE'`.

**Suitable-slot discovery:**
```python
candidates = obj.animation_data.action_suitable_slots
for s in candidates:
    print(s.name_display, s.identifier)
```

**Agent guidance — slots vs separate Actions:**
- **Separate Actions:** for clip-like clips you want to sequence in the NLA (Walk, Run, Idle, Jump). Each is independently selectable on the NLA editor.
- **One Action with multiple slots:** for asset-like bundles where animation crosses datablocks (object + armature, character + clothing) and you want them packaged together.

**Footgun:** assigning an Action without explicitly setting `action_slot` may auto-bind to a matching slot — or not. For deterministic agent code, always set the slot after assigning the Action.

---

## F-Curve Modifiers — Parametric Motion Without Keyframes

An F-curve modifier is a **stack-of-effects** applied on top of (or in place of) the curve's authored keyframes. This is the **most agent-friendly authoring path** — no keyframe timing to get right, just a formula.

**Modifier types** (`fcurve.modifiers.new(type=...)`):
- `'GENERATOR'` — polynomial generator. `mode = 'POLYNOMIAL'` or `'POLYNOMIAL_FACTORISED'`. Coefficients `coefficients` (list of floats). Use for linear or polynomial drift.
- `'FNGENERATOR'` — Built-in Function. `function_type = 'SIN' | 'COS' | 'TAN' | 'SQRT' | 'LN' | 'SINC'`. Parametric `amplitude`, `phase_multiplier`, `phase_offset`, `value_offset`.
- `'ENVELOPE'` — reshape the curve with low/high reference points.
- `'CYCLES'` — repeat the keyframed range. `mode_before` / `mode_after` ∈ `{'NONE','REPEAT','REPEAT_OFFSET','MIRROR'}`. The cleanest way to loop a baked animation.
- `'NOISE'` — adds pseudo-random noise. Params `scale`, `strength`, `phase`, `offset`, `depth`, `blend_type`. Indispensable for handheld camera shake, organic wiggle.
- `'LIMITS'` — clamp to a min/max box on both axes.
- `'STEPPED'` — sample every N frames; produces stepped/snap motion. Params `frame_step`, `frame_offset`, `use_frame_start`, `frame_start`, `use_frame_end`, `frame_end`.

**Adding a modifier:**
```python
fc = action.fcurves.find('location', index=2)
mod = fc.modifiers.new(type='NOISE')
mod.scale = 12.0          # frames per noise cycle
mod.strength = 0.3        # amplitude in property units
mod.depth = 2             # octaves
```

**The pattern:** an empty F-curve (no keyframes) plus a Generator or FNGenerator gives you **fully procedural** motion driven entirely by frame number. Combine with Cycles modifier for repeating; with Noise for variation; with Stepped for snap.

---

## Drivers — Programmatic Property Computation

A **driver** replaces an F-curve with a Python expression evaluated every frame. The expression reads **driver variables** (RNA-tracked references to other properties) and returns a number that becomes the property value.

**Why drivers matter for agents:** drivers express **relationships** ("this property = 2× that property + a sine wave"). Once wired, the relationship holds for the whole timeline with no keyframe authorship. Pair drivers with an audio-baked source F-curve and you have a fully data-driven animation chain.

**Creating a driver:**
```python
fc = obj.driver_add('scale', 0)   # X-scale; returns an FCurve with .driver set
drv = fc.driver
drv.type = 'SCRIPTED'             # 'AVERAGE' | 'SUM' | 'MIN' | 'MAX' | 'SCRIPTED'
drv.expression = "var * 2.0 + 1.0"

var = drv.variables.new()
var.name = 'var'
var.type = 'SINGLE_PROP'
tgt = var.targets[0]
tgt.id_type = 'OBJECT'
tgt.id = bpy.data.objects['Source']
tgt.data_path = 'location.z'
```

**Driver variable types:**
- `'SINGLE_PROP'` — any RNA property. One target. `tgt.id_type`, `tgt.id`, `tgt.data_path`. The workhorse.
- `'TRANSFORMS'` — a transform channel from one bone or object. One target. `tgt.transform_type ∈ {'LOC_X','LOC_Y','LOC_Z','ROT_X','ROT_Y','ROT_Z','ROT_W','SCALE_X','SCALE_Y','SCALE_Z','SCALE_AVG'}`. `tgt.transform_space ∈ {'WORLD_SPACE','TRANSFORM_SPACE','LOCAL_SPACE'}`. `tgt.rotation_mode` for rotation types.
- `'ROTATION_DIFF'` — angle (radians) between two bones. Two targets, each pointing at an Object + bone.
- `'LOC_DIFF'` — distance between two bones/objects. Two targets.
- `'CONTEXT_PROP'` — read from `bpy.context` (active scene, active object). Advanced; used in node-group drivers.

**Driver expression rules:**
- Standard Python math is allowed: `+ - * / ** % //`, parens, function calls.
- The math module is implicitly available — `sin`, `cos`, `pi`, `radians`, `degrees`, `sqrt`, etc.
- Variable names you create become locals in the expression.
- Drivers run in a **sandbox**; many modules and dunder access are blocked.
- Custom functions: register with `bpy.app.driver_namespace['my_fn'] = my_callable`. Drivers can call `my_fn(x)`.

**Security warning — drivers disabled on file open by default.** Blender treats Python expressions in drivers as untrusted code from foreign files. Opening a file with drivers shows "Auto-run disabled" until the user enables Python execution (top-right of the file open prompt or in Preferences → Save & Load → Auto Run Python Scripts). **Agents writing files for the user to open must flag this** — until the user trusts the file, every driver evaluates to 0 and the scene looks broken.

**Paste-ready driver recipes:**

**1. Property mirror — scale.x follows location.z of another object:**
```python
fc = obj.driver_add('scale', 0)
drv = fc.driver
drv.type = 'SCRIPTED'
drv.expression = "var"
v = drv.variables.new(); v.name = 'var'; v.type = 'SINGLE_PROP'
t = v.targets[0]; t.id_type = 'OBJECT'; t.id = bpy.data.objects['Source']
t.data_path = 'location.z'
```

**2. Sine wave on Z based on frame:**
```python
fc = obj.driver_add('location', 2)
drv = fc.driver
drv.type = 'SCRIPTED'
drv.expression = "sin(frame * 0.1) * 0.5"
v = drv.variables.new(); v.name = 'frame'; v.type = 'SINGLE_PROP'
t = v.targets[0]; t.id_type = 'SCENE'; t.id = bpy.context.scene
t.data_path = 'frame_current'
```

**3. Bone-rotation drives shape-key value (corrective shape on knee bend):**
```python
fc = mesh.shape_keys.driver_add('key_blocks["KneeCorrective"].value')
drv = fc.driver
drv.type = 'SCRIPTED'
drv.expression = "max(0, -ry)"   # only fires when ry is negative
v = drv.variables.new(); v.name = 'ry'; v.type = 'TRANSFORMS'
t = v.targets[0]
t.id = bpy.data.objects['Armature']
t.bone_target = 'Knee.L'
t.transform_type = 'ROT_X'
t.transform_space = 'LOCAL_SPACE'
t.rotation_mode = 'AUTO'
```

**4. Distance-driven IK stretch (LOC_DIFF):**
```python
fc = obj.driver_add('scale', 1)
drv = fc.driver
drv.type = 'SCRIPTED'
drv.expression = "d / 2.0"
v = drv.variables.new(); v.name = 'd'; v.type = 'LOC_DIFF'
v.targets[0].id = bpy.data.objects['Shoulder']
v.targets[1].id = bpy.data.objects['Wrist']
```

**5. Audio bake → driver on material emission:**
```python
# Assumes an Empty named "AudioBake_Sub" has its location.z baked from audio.
fc = mat.node_tree.driver_add('nodes["Emission"].inputs[1].default_value')
drv = fc.driver
drv.type = 'SCRIPTED'
drv.expression = "amp * 8.0"
v = drv.variables.new(); v.name = 'amp'; v.type = 'SINGLE_PROP'
t = v.targets[0]; t.id_type = 'OBJECT'; t.id = bpy.data.objects['AudioBake_Sub']
t.data_path = 'location.z'
```

**Reading a driven property's current frame value** — drivers require dependency-graph evaluation:
```python
depsgraph = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(depsgraph)
print(obj_eval.scale[0])     # post-driver value
```

---

## NLA Editor — Stacked Actions on Tracks

The **NLA (Non-Linear Animation)** editor treats Actions as clips on a track-based timeline. Each AnimData has an `nla_tracks` collection; each track has `strips`; each strip references an `Action` and adds per-strip controls.

**When to use NLA:**
- Sequencing distinct clips (Walk → Idle → Walk).
- Layering passes (a base run cycle plus an additive head-bob).
- Reusing the same Action multiple times at different points.
- Variation via blend modes and influence sweeps.

**When NOT to use NLA:**
- Single-Action scenes — just leave the Action assigned to AnimData; don't push to the NLA stack.
- Driver-driven motion — drivers bypass the NLA entirely.

**Strip blend modes** (`strip.blend_type`):
- `'REPLACE'` — overwrite the result so far.
- `'COMBINE'` — quaternion-aware blend, the safest default for layered character animation.
- `'ADD'` — sum onto the lower stack.
- `'SUBTRACT'` — subtract.
- `'MULTIPLY'` — multiply.

**Strip extrapolation** (`strip.extrapolation`):
- `'NOTHING'` — outside the strip, no contribution.
- `'HOLD'` — hold the first/last value in both directions.
- `'HOLD_FORWARD'` — hold only after the strip's end.

**Strip influence** is 0..1 (`strip.influence`). Animatable — keyframe `strip.influence` to fade strips in and out.

**Strip timing** — `strip.frame_start`, `strip.frame_end`, `strip.scale`, `strip.repeat`. `strip.use_animated_time` lets a separate F-curve drive the strip's internal time pointer (clip-scrub style).

**Pushing the active Action to NLA:**
```python
# Programmatic equivalent of "Push Down Action" in the NLA editor:
ad = obj.animation_data
track = ad.nla_tracks.new()
strip = track.strips.new(name="WalkStrip", start=1, action=ad.action)
ad.action = None   # Clear the active slot so playback uses the NLA
```

**Adding a strip on a new track:**
```python
ad = obj.animation_data
trk = ad.nla_tracks.new()
trk.name = "Layer_HeadBob"
s = trk.strips.new(name="HeadBob", start=1, action=bpy.data.actions['HeadBob'])
s.blend_type = 'ADD'
s.influence = 0.5
s.extrapolation = 'HOLD'
```

**Cyclic strip (loop a 24-frame walk across 240 frames):**
```python
s.repeat = 10            # repeat 10× → 240 frames
s.use_auto_blend = True  # auto-blend with adjacent strips
```

---

## Armatures — Bones, Pose, and Rest

An **Armature** is an Object (`obj.type == 'ARMATURE'`) whose data block (`obj.data`, an `Armature` ID) is a hierarchy of bones. Three different bone-flavored data types you'll touch:

- **EditBone** — only exists in Edit mode. Geometry of the rig: head, tail, roll, parent links. `obj.data.edit_bones`.
- **Bone** — the rest pose. Read-only structural reference. `obj.data.bones`.
- **PoseBone** — the deformable pose-mode transform layered on top of the rest. **This is what you animate.** `obj.pose.bones[name]`.

**Creating an armature:**
```python
bpy.ops.object.armature_add()             # adds Armature + one bone "Bone"
arm = bpy.context.object
```

**Adding bones in Edit mode:**
```python
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones.new("UpperArm")
eb.head = (0, 0, 1.5)
eb.tail = (0, 0, 1.0)
parent = arm.data.edit_bones["Bone"]
eb.parent = parent
bpy.ops.object.mode_set(mode='OBJECT')
```

**Pose mode access — no mode switch required for property writes:**
```python
pb = arm.pose.bones["UpperArm"]
pb.rotation_mode = 'QUATERNION'        # match the data's rotation mode
pb.rotation_quaternion = (1, 0, 0, 0)
pb.location = (0, 0, 0)
```

**Rotation modes** — `'XYZ'` / `'XZY'` / `'YXZ'` / `'YZX'` / `'ZXY'` / `'ZYX'` (Euler orderings), `'QUATERNION'`, `'AXIS_ANGLE'`. Setting `rotation_quaternion` on a bone whose `rotation_mode` is `'XYZ'` writes the data but doesn't drive the pose. **Always match the assignment to the rotation_mode.**

**Keyframing a bone:**
```python
arm.keyframe_insert(data_path='pose.bones["UpperArm"].rotation_quaternion', frame=1)
arm.keyframe_insert(data_path='pose.bones["UpperArm"].location', frame=1)
```

Note: the AnimData is on the **Object** (the armature object), not on the Armature data. F-curve `data_path` is `pose.bones["..."].rotation_quaternion`.

---

## Posing Armatures — Constraints, IK, Weight Painting

**PoseBone constraints** are stamped onto the bone, not the armature data:
```python
pb = arm.pose.bones["Hand.L"]
c = pb.constraints.new(type='IK')
c.target = bpy.data.objects['IK_Target']
c.subtarget = ""           # or a bone name on target
c.chain_count = 3
c.use_tail = True
c.use_stretch = False
```

**Common pose-bone constraint types:**
- `'IK'` — inverse kinematics solver. `target`, `subtarget`, `chain_count`, `use_tail`, `use_stretch`, `iterations`, `weight`, `orient_weight`.
- `'COPY_LOCATION'` / `'COPY_ROTATION'` / `'COPY_SCALE'` — mirror from target.
- `'COPY_TRANSFORMS'` — all three at once.
- `'TRACK_TO'` / `'DAMPED_TRACK'` — point the bone's primary axis at a target.
- `'LIMIT_DISTANCE'` — keep within / on / outside a radius from target.
- `'STRETCH_TO'` — scale along axis to reach a target (good for ribbon rigs).
- `'CHILD_OF'` — parent-like; supports per-channel inheritance toggles.
- `'FOLLOW_PATH'` — ride a curve.
- `'SPLINE_IK'` — IK along a curve.

**Auto-IK** is a viewport-only mode for human-driven posing (Pose Mode → header → Auto IK). Not exposed as a stamp-and-go API; agents should set up proper IK constraints instead.

**Weight painting** (mesh-to-bone influences) — agents should NOT attempt to author weights by direct vertex-group manipulation for character meshes. Use:
```python
bpy.ops.object.parent_set(type='ARMATURE_AUTO')   # automatic weights
```
…and accept that complex characters need a human cleanup pass on the weights.

---

## Rigging Basics — Minimal Viable Setup

This file is **not a rigging guide**. The minimal agent-deliverable rig:

1. Add an armature, add bones in Edit mode where the rig joints belong.
2. Select the mesh, then shift-select the armature.
3. Parent with automatic weights:
   ```python
   bpy.ops.object.parent_set(type='ARMATURE_AUTO')
   ```
4. Confirm an `ARMATURE` modifier appeared on the mesh (Blender adds it as part of parenting).
5. Confirm vertex groups named after bones appeared on the mesh (`mesh.vertex_groups`).

**Anything beyond this needs human authorship** — IK controllers, FK/IK switches, custom bone shapes, drivers between control bones and deform bones, corrective shape keys, facial rigs. Flag explicitly that the rig is rough-cut and a rigger should clean it up.

---

## Shape Keys — Blendshapes

Shape keys are per-vertex deltas relative to a **Basis** key. Useful for facial expression, morph targets, blendshape-based animation.

**Where they live:** `obj.data.shape_keys` is a `Key` ID. Individual keys are in `obj.data.shape_keys.key_blocks`.

**Adding shape keys:**
```python
obj.shape_key_add(name='Basis')              # baseline; only once
sk = obj.shape_key_add(name='Smile')
sk.value = 0.0                                # 0 = off, 1 = fully applied
```

**Animating shape key value:**
```python
sk = obj.data.shape_keys.key_blocks['Smile']
# Keyframe via the shape_keys AnimData (NOT the object's):
obj.data.shape_keys.animation_data_create()
sk.value = 0.0
obj.data.shape_keys.keyframe_insert(data_path='key_blocks["Smile"].value', frame=1)
sk.value = 1.0
obj.data.shape_keys.keyframe_insert(data_path='key_blocks["Smile"].value', frame=12)
```

**Driver on a shape key value** — see driver recipe #3 above (bone-rotation → shape key value).

**Slider range** — by default shape key values clamp to 0..1. To allow over-shoot or negative, set `sk.slider_min` and `sk.slider_max`.

---

## Constraints — Object-Level and Bone-Level

Constraints declare a **relationship** ("track this target," "stay within this radius") that resolves every frame. Stamping a constraint is far more reliable than keyframing the relationship by hand.

**Common types** (`obj.constraints.new(type=...)` or `pose_bone.constraints.new(type=...)`):

- **COPY_LOCATION** — mirror target location. `target`, `subtarget`, `use_x/y/z`, `invert_x/y/z`, `target_space`, `owner_space`.
- **COPY_ROTATION** — mirror target rotation. Same axis flags.
- **COPY_SCALE** — mirror target scale.
- **TRACK_TO** — point an axis at the target. Older, uses a roll-up vector; **prefer DAMPED_TRACK** for most cases.
- **DAMPED_TRACK** — point one axis at target, minimum-rotation interpolation. Less gimbal-prone than TRACK_TO.
- **LIMIT_DISTANCE** — bound distance to target. `limit_mode ∈ {'LIMITDIST_INSIDE','LIMITDIST_OUTSIDE','LIMITDIST_ONSURFACE'}`, `distance`.
- **STRETCH_TO** — scale along a target-pointing axis to reach the target. The classic ribbon-bone constraint.
- **IK** — pose-bone-only. Defined above under armatures.
- **SPLINE_IK** — pose-bone-only. IK along a curve.
- **CHILD_OF** — parent-of relationship with per-channel inheritance.
- **FLOOR** — clamp object to be above/below a plane through target.
- **FOLLOW_PATH** — ride a Curve. Set `Curve.use_path` on the target and animate `Curve.path_duration` for travel.

**Example — camera tracks an Empty:**
```python
cam = bpy.data.objects['Camera']
empty = bpy.data.objects['Target']
c = cam.constraints.new(type='DAMPED_TRACK')
c.target = empty
c.track_axis = 'TRACK_NEGATIVE_Z'   # camera looks down -Z
```

**Example — object follows a curve at constant speed:**
```python
curve = bpy.data.objects['BezierCircle']
curve.data.use_path = True
curve.data.path_duration = 200      # frames to complete one traversal

c = obj.constraints.new(type='FOLLOW_PATH')
c.target = curve
c.use_curve_follow = True
```

**Example — Child Of with rotation-only inheritance:**
```python
c = obj.constraints.new(type='CHILD_OF')
c.target = bpy.data.objects['Parent']
c.use_location_x = False
c.use_location_y = False
c.use_location_z = False
c.use_scale_x = False
c.use_scale_y = False
c.use_scale_z = False
# Reset inverse: requires operator context (Set Inverse button equivalent)
```

---

## Audio-to-F-Curve Bake Pipeline

This is the **single most agent-friendly path to audio-driven motion in Blender**. Use it whenever the user wants visuals tied to a known audio file (music, voiceover, SFX).

**Pipeline overview:**

1. Pick a property to drive — typically a scalar on a helper Empty (e.g. `Empty.location.z`).
2. In the Graph Editor with that F-curve selected, run **Channel → Bake Sound to F-Curves**.
3. Configure frequency band, attack, release, threshold.
4. Bake. The F-curve now holds **one keyframe per frame** computed from the audio envelope.
5. Read that F-curve from drivers on any property in the scene.

**Step-by-step:**

**Step 1.** Add a helper Empty (or use a Speaker; Speakers also play audio at render time, Empties don't):
```python
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
audio = bpy.context.object
audio.name = 'AudioBake_Sub'
audio.animation_data_create()
```

**Step 2.** Insert one keyframe on `location.z` so an F-curve exists to bake into:
```python
audio.location.z = 0.0
audio.keyframe_insert(data_path='location', index=2, frame=1)
```

**Step 3.** Switch a Graph Editor area's context to that F-curve and select it. With `temp_override` (4.2+):
```python
fc = audio.animation_data.action.fcurves.find('location', index=2)
fc.select = True

# Find a Graph Editor area or create override context
for area in bpy.context.screen.areas:
    if area.type == 'GRAPH_EDITOR':
        with bpy.context.temp_override(area=area):
            bpy.ops.graph.sound_bake(
                filepath='/path/to/audio.wav',
                low=50, high=200,            # sub-bass band
                attack=0.005, release=0.2,
                threshold=0.0,
                use_accumulate=False,
                use_additive=False,
                use_square=False,
                sthreshold=0.1,
            )
        break
```

**Step 4 — frequency band recipes:**
- **Sub-bass (kick energy):** `low=20, high=80`
- **Bass:** `low=50, high=200`
- **Low-mid:** `low=200, high=800`
- **Mid (vocals, snares):** `low=800, high=2500`
- **High-mid (hats, transients):** `low=2500, high=8000`
- **Brilliance:** `low=8000, high=16000`
- **Full broadband (loudness curve):** `low=20, high=20000`

Bake the **same audio file into multiple Empties**, each on a different band. Now you have a per-band amplitude source ready for drivers.

**Step 5 — drive any property from the bake.** Use a driver of type `'SCRIPTED'` with a `'SINGLE_PROP'` variable pointing at `AudioBake_Sub.location.z`. Multiple properties can drive off the same Empty — **single source of truth, multi-property drive**.

**Bake parameters in detail:**
- `low`, `high` — frequency band in Hz. The bake integrates energy in this band per frame.
- `attack` — envelope follower attack time (seconds). Lower = snappier response to transients.
- `release` — release time. Higher = smoother decay.
- `threshold` — minimum amplitude to register; below this the curve sits at zero.
- `use_accumulate` — sum into existing values instead of replacing.
- `use_additive` — add new bake on top of existing F-curve keyframes.
- `use_square` — square the rectified signal (boosts loud parts).
- `sthreshold` — square threshold; only used with `use_square`.

**Limitations and tradeoffs:**
- **Offline only.** The bake writes keyframes at the time you run it. If the audio file changes, re-bake.
- **FPS-bound precision.** The curve has one sample per frame. At 24 FPS, you have 24 datapoints per second of audio.
- **Replaces existing keyframes** by default. To layer, set `use_accumulate` or `use_additive`.
- **Not real-time reactivity.** For live audio-reactive visuals, use TouchDesigner or a Sound input via the Sequencer + speakers; Blender's audio reactivity is fundamentally batch.
- **No phase/spectrum content** — just band-integrated amplitude over time.

---

## Playback and Frame Advancement

**Scrubbing in scripts:**
```python
scene = bpy.context.scene
scene.frame_current = 50    # changes the cursor but does NOT update drivers/constraints
scene.frame_set(50)         # forces full evaluation; use this when you need values
```

**Live playback:**
```python
bpy.ops.screen.animation_play()
bpy.ops.screen.animation_cancel()   # to stop
```

**Range and stride:**
```python
scene.frame_start = 1
scene.frame_end = 240
scene.frame_step = 1
scene.render.fps = 24
scene.render.fps_base = 1.0   # actual fps = fps / fps_base
```

**Iterating frames to bake or sample:**
```python
for f in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(f)
    # read evaluated property values here
    val = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation
```

---

## Animation Rendering

Render an animation sequence:
```python
scene.render.filepath = '/path/to/output_####.png'  # # → padded frame number
scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(animation=True, write_still=False)
```

Render-output settings (resolution, file format, color management) are shared with stills — see [[BLENDER_RENDER_CYCLES]] and [[BLENDER_RENDER_EEVEE]] for the engine-specific knobs.

**Frame numbering:**
- `####` in the filepath → zero-padded frame number.
- Width = number of `#` chars. Five → `00001`, three → `001`.

**Skip frames:**
```python
scene.frame_step = 2    # render every other frame (good for previz)
```

---

## bpy API Surface — Paste-Ready Snippets

**Insert a keyframe on location at current frame:**
```python
obj.keyframe_insert(data_path='location', frame=bpy.context.scene.frame_current)
```

**Insert keyframes on a single vector component:**
```python
obj.keyframe_insert(data_path='location', index=2, frame=24)
```

**Insert keyframes on all components of a vector:**
```python
obj.keyframe_insert(data_path='rotation_euler', frame=1)
```

**Insert a keyframe on a custom property:**
```python
obj['energy'] = 0.5
obj.keyframe_insert(data_path='["energy"]', frame=1)
```

**Insert a keyframe on a modifier parameter:**
```python
obj.modifiers["Subsurf"].levels = 1
obj.keyframe_insert(data_path='modifiers["Subsurf"].levels', frame=1)
```

**Insert a keyframe on a shape key:**
```python
sk = obj.data.shape_keys
sk.animation_data_create()
sk.key_blocks['Smile'].value = 1.0
sk.keyframe_insert(data_path='key_blocks["Smile"].value', frame=12)
```

**Insert a bone keyframe (rotation):**
```python
arm = bpy.data.objects['Armature']
arm.pose.bones['UpperArm'].rotation_quaternion = (0.707, 0, 0.707, 0)
arm.keyframe_insert(data_path='pose.bones["UpperArm"].rotation_quaternion', frame=1)
```

**Set a driver with an expression and a variable:**
```python
fc = obj.driver_add('location', 2)
d = fc.driver
d.type = 'SCRIPTED'
d.expression = "amp * 5.0"
v = d.variables.new(); v.name = 'amp'; v.type = 'SINGLE_PROP'
t = v.targets[0]
t.id_type = 'OBJECT'; t.id = bpy.data.objects['AudioBake_Sub']
t.data_path = 'location.z'
```

**Read F-curve keyframe values:**
```python
fc = obj.animation_data.action.fcurves.find('location', index=2)
for kp in fc.keyframe_points:
    print(kp.co.x, kp.co.y, kp.interpolation)
```

**Set F-curve interpolation for all keyframes:**
```python
for kp in fc.keyframe_points:
    kp.interpolation = 'LINEAR'
fc.update()
```

**Add an F-curve Noise modifier:**
```python
mod = fc.modifiers.new(type='NOISE')
mod.scale = 8.0
mod.strength = 0.5
mod.depth = 2
mod.phase = 0.0
```

**Add an F-curve Generator (linear function):**
```python
mod = fc.modifiers.new(type='GENERATOR')
mod.mode = 'POLYNOMIAL'
mod.poly_order = 1
mod.coefficients = [0.0, 1.0]   # value = 0 + 1*frame
```

**Add a Cycles modifier (loop the keyframed range):**
```python
mod = fc.modifiers.new(type='CYCLES')
mod.mode_before = 'REPEAT'
mod.mode_after = 'REPEAT'
```

**Add a Stepped modifier (snap to every 4 frames):**
```python
mod = fc.modifiers.new(type='STEPPED')
mod.frame_step = 4
```

**Bake sound to an F-curve (in a Graph Editor override):**
```python
fc = obj.animation_data.action.fcurves.find('location', index=2)
fc.select = True
for area in bpy.context.screen.areas:
    if area.type == 'GRAPH_EDITOR':
        with bpy.context.temp_override(area=area):
            bpy.ops.graph.sound_bake(
                filepath='/audio.wav', low=20, high=80,
                attack=0.005, release=0.2,
            )
        break
```

**Switch the active Action on an Object:**
```python
obj.animation_data_create()
obj.animation_data.action = bpy.data.actions['Run']
```

**4.4+: bind a specific slot of the Action:**
```python
slot = obj.animation_data.action.slots[0]
obj.animation_data.action_slot = slot
```

**Push the active Action to NLA and clear active:**
```python
ad = obj.animation_data
trk = ad.nla_tracks.new()
trk.strips.new(name=ad.action.name + "_strip", start=1, action=ad.action)
ad.action = None
```

**Create a new NLA strip from a library Action:**
```python
ad = obj.animation_data
trk = ad.nla_tracks.new()
trk.name = "Layer_Idle"
s = trk.strips.new(name="Idle", start=50, action=bpy.data.actions['Idle'])
s.blend_type = 'COMBINE'
s.influence = 1.0
```

**Set per-bone pose transforms:**
```python
pb = arm.pose.bones['Hand.L']
pb.rotation_mode = 'QUATERNION'
pb.rotation_quaternion = (1, 0, 0, 0)
pb.location = (0.1, 0, 0)
pb.scale = (1, 1, 1)
```

**Add an IK constraint with target and chain length:**
```python
pb = arm.pose.bones['Hand.L']
c = pb.constraints.new(type='IK')
c.target = bpy.data.objects['IK_Hand.L']
c.chain_count = 3
c.use_stretch = False
```

**Add a Child Of constraint:**
```python
c = obj.constraints.new(type='CHILD_OF')
c.target = bpy.data.objects['Parent']
# Per-channel inheritance toggles
c.use_location_x = c.use_location_y = c.use_location_z = True
c.use_rotation_x = c.use_rotation_y = c.use_rotation_z = True
c.use_scale_x = c.use_scale_y = c.use_scale_z = False
```

**Add a Follow Path constraint:**
```python
c = obj.constraints.new(type='FOLLOW_PATH')
c.target = bpy.data.objects['BezierCurve']
c.use_curve_follow = True
c.forward_axis = 'FORWARD_Y'
c.up_axis = 'UP_Z'
```

**Read the current evaluated value of a driven property:**
```python
dg = bpy.context.evaluated_depsgraph_get()
obj_eval = obj.evaluated_get(dg)
print(obj_eval.location.z)
```

**Iterate all F-curves on an Action:**
```python
for fc in bpy.data.actions['Walk'].fcurves:
    print(fc.data_path, fc.array_index, len(fc.keyframe_points), [m.type for m in fc.modifiers])
```

**Bulk-set keyframe interpolation across an Action:**
```python
for fc in bpy.data.actions['Walk'].fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'
    fc.update()
```

---

## Common Animation Recipes

**Procedural constant rotation (no keyframes):**
```python
obj.animation_data_create()
act = bpy.data.actions.new('Spin')
obj.animation_data.action = act
fc = act.fcurves.new(data_path='rotation_euler', index=2)
mod = fc.modifiers.new(type='GENERATOR')
mod.mode = 'POLYNOMIAL'
mod.poly_order = 1
mod.coefficients = [0.0, 0.05]   # 0.05 rad per frame
```

**Looping noise wiggle on Z (handheld camera feel):**
```python
fc = obj.animation_data.action.fcurves.new(data_path='location', index=2)
m = fc.modifiers.new(type='NOISE')
m.scale = 30.0
m.strength = 0.02
m.depth = 1
```

**Audio-driven scale pulse (full chain):**
1. Empty `AudioBake_Sub`, baked from `low=20, high=80` (kick band).
2. Driver on `obj.scale[0]`, `obj.scale[1]`, `obj.scale[2]`, each reading `AudioBake_Sub.location.z`, expression `"1.0 + amp * 0.5"`.

**Camera follows a curve:**
1. Add Bezier curve, shape the path.
2. `cam.constraints.new(type='FOLLOW_PATH')` targeting the curve.
3. Set `curve.data.path_duration` for total frames per traversal.
4. Optionally keyframe `evaluation_time` on the curve for non-linear pacing.

**Camera shake on impact:**
1. Parent the actual Camera to an Empty named `CameraShake`.
2. On `CameraShake.location.x/y/z`, add three F-curves each with a Noise modifier.
3. Keyframe the Noise `strength` from 0 → 1 → 0 at the impact frame for a localized burst.

**Snap-to-step animation (stop-motion look):**
1. Keyframe normally.
2. Add a Stepped modifier (`frame_step=2`) to every F-curve. The animation now reads only every other frame.

**Eye-track-to-target:**
1. `eye.constraints.new(type='DAMPED_TRACK')`, target = a Target Empty.
2. `track_axis = 'TRACK_NEGATIVE_Z'` if the eye geometry's negative-Z points outward.

**Cycle a walk loop with NLA:**
1. Author a 24-frame Walk Action.
2. Push to NLA.
3. Set `strip.repeat = 10` for 240 frames.
4. Set `strip.use_auto_blend = True` between this and adjacent strips.

**Driver-driven shapekey on bone rotation:** see driver recipe #3 above.

**Frame-stepped reveal (count-up counter):**
1. Keyframe a custom property at frames 1, 2, 3… with integer values.
2. Set each keyframe's `interpolation = 'CONSTANT'`.
3. Drive a text object's body via a driver reading the custom property.

**Material emission pulses on hi-hats:**
1. Bake audio at `low=8000, high=16000` into a second Empty `AudioBake_Hat`.
2. Driver on `mat.node_tree.nodes["Emission"].inputs[1].default_value`, expression `"amp * 12.0"`.

---

## Agent-Friendly vs Human-Only — Where to Draw the Line

| Task | Agent-reliable? | Notes |
|------|-----------------|-------|
| Insert keyframes on simple properties (loc/rot/scale, custom props) | YES | Trivial. `keyframe_insert`. |
| Author a 12-keyframe transform sequence with specified values | YES | Provide the (frame, value) pairs explicitly. |
| Set up an F-curve modifier (Noise, Cycles, Generator, Stepped) | YES | One-call setup, deterministic result. |
| Wire a driver with a SINGLE_PROP variable and an expression | YES | The most powerful agent-friendly tool. |
| Wire TRANSFORMS / LOC_DIFF / ROTATION_DIFF drivers | YES | Slightly more setup; still scripted. |
| Bake audio to F-curves | YES | One call once you have the file path. |
| Add a constraint (CopyLoc/Rot/Scale, TrackTo, FollowPath, LimitDistance) | YES | Stamp-and-go. |
| Add an IK constraint with target + chain_count | YES | Setup is mechanical. |
| Create NLA tracks and strips from existing Actions | YES | Sequencing is data-shaped. |
| Auto-weight a mesh to an armature | YES | One operator. Output may need human cleanup. |
| Animate shape key values with keyframes or drivers | YES | Mechanical. |
| Author an Action with multiple Slots (4.4+) | YES | New API but well-defined. |
| Walk cycle animation | NO | Performance animation. Use mocap or human authorship. |
| Run/jump/impact timing | NO | Anticipation, overshoot, settle — needs taste. |
| Facial animation (lip sync, expressions) | NO | Performance. Even with audio bake, character lipsync needs human shapes. |
| Character rig with FK/IK switches, custom bone shapes, controllers | NO | Complex topology of constraints + drivers. Human rigger required. |
| Animation handle tweaks (timing/spacing, hold-and-snap) | NO | Visual judgment task. |
| Cleaning up auto-generated vertex weights | NO | Hand-painting; agent can only refer the user to a viewport task. |
| Authoring a believable "weighty" bounce | NO | Squash-stretch values are taste-driven. |
| Cleaning up motion-capture noise | NO | Per-curve eyeball editing. |

**Heuristic for agents:** if the task can be expressed as "set these properties to these values on these frames" or "wire this property to that property," it's agent-deliverable. If the task description contains words like "feel," "natural," "believable," "snappy," "smooth," "with weight" — that's an authorship task and you need the human in the loop.

---

## Common Footguns

1. **`scene.frame_current = N` does not update dependent properties.** Use `scene.frame_set(N)`. Without it, drivers and constraints still report their old-frame values.

2. **Driver expressions are sandboxed.** No `import`, no dunder access, no `eval`, restricted module list. Use `bpy.app.driver_namespace['fn'] = my_fn` if you need a custom function.

3. **Drivers are disabled on file open until the user enables Python.** Until they do, every driver evaluates to 0 and the scene looks broken. Tell the user to allow auto-run when prompted, or to enable it in Preferences.

4. **Rotation mode mismatches silently break.** Writing `rotation_quaternion` on a bone whose `rotation_mode = 'XYZ'` updates the data but doesn't drive the pose. Always read `pb.rotation_mode` first, write to the matching field.

5. **F-curve `data_path` for vector components is `'location'`, not `'location[0]'`.** The `array_index` parameter selects the component. `keyframe_insert(data_path='location[0]', ...)` produces an error or unexpected behavior depending on version.

6. **`bpy.ops.graph.sound_bake` clears existing keyframes on the selected F-curve.** Use `use_accumulate=True` or `use_additive=True` to layer onto existing data. Always select **only** the target F-curve before baking — other selected curves get baked too.

7. **`bpy.ops.graph.sound_bake` requires Graph Editor context.** Wrap in `bpy.context.temp_override(area=graph_area)` or the operator fails with `RuntimeError: Operator bpy.ops.graph.sound_bake.poll() failed`.

8. **NLA strips contribute only within their frame range** unless `extrapolation` is `'HOLD'` or `'HOLD_FORWARD'`. A strip ending at frame 100 with `'NOTHING'` extrapolation contributes nothing at frame 101.

9. **An Action assigned but no NLA, no slot bound (4.4+) silently produces no animation.** Always set `action_slot` after assignment, or accept the legacy behavior of binding to slot 0.

10. **AnimData on `obj` vs `obj.data` vs `obj.data.shape_keys`** — different ID, different AnimData. Shape key animation lives on `obj.data.shape_keys.animation_data`, not on the object's. Material animation lives on `mat.animation_data`; shader node animation on `mat.node_tree.animation_data`.

11. **`obj.animation_data` is `None` until something animates it.** Call `obj.animation_data_create()` defensively before assigning Actions or drivers.

12. **Pushing an Action to NLA and leaving it also assigned to AnimData double-evaluates.** Pattern: `ad.nla_tracks.new() … strip = trk.strips.new(...) … ad.action = None`.

13. **Bone names in `data_path` must be escaped if they contain quotes.** Standard Blender naming (letters, digits, dots, underscores) is safe. Avoid quotes and brackets in bone names.

14. **`bpy.ops.object.parent_set(type='ARMATURE_AUTO')` requires correct selection state** — the mesh selected first, the armature active. Without that, the operator parents incorrectly or fails the poll.

15. **F-curve modifier order matters.** Modifiers apply top-down. A Generator at top followed by Noise produces noisy linear motion; reversed produces linear-on-noisy. Check `fc.modifiers` order if results look wrong.

16. **`fc.update()` is required after batch keyframe edits.** Without it, cached curve evaluations return stale values.

17. **Pose-bone constraints stamp on the PoseBone, not the Bone.** `arm.pose.bones[name].constraints.new(...)`, not `arm.data.bones[name].constraints` (which doesn't exist).

18. **`scene.render.fps` is an int, `fps_base` is a float.** Effective FPS = `fps / fps_base`. To get 29.97 set `fps=30, fps_base=1.001`. Don't try to set `fps = 29.97` — it rounds to 30 and silently loses precision.

19. **The 4.4+ Action Slot API and the legacy API coexist.** Scripts that walk `action.fcurves` directly get the slot-0 curves only. For new code targeting 4.4+, use `action.layers[0].strips[0].channelbag(slot).fcurves` to be explicit; for compatibility code, keep using `action.fcurves`.

20. **Render output frame range honors `scene.frame_start`..`frame_end`, not the timeline preview range.** Set both before calling `bpy.ops.render.render(animation=True)`.

---

## See Also

- [[BLENDER_LIBRARY_INDEX]] — when to pull this file vs related references.
- [[BLENDER_PYTHON_API]] — general bpy patterns, depsgraph, context overrides.
- [[BLENDER_DATA_MODEL]] — how Objects, Data, AnimData, and bpy.data collections fit together.
- [[BLENDER_RENDER_CYCLES]] / [[BLENDER_RENDER_EEVEE]] — per-engine animation render settings.

**Source references:**
- Blender Manual — [Animation overview](https://docs.blender.org/manual/en/latest/animation/index.html), [Keyframes editing](https://docs.blender.org/manual/en/latest/animation/keyframes/editing.html), [Markers](https://docs.blender.org/manual/en/latest/animation/markers.html), [Armatures](https://docs.blender.org/manual/en/latest/animation/armatures/index.html), [Drivers Panel](https://docs.blender.org/manual/en/latest/animation/drivers/drivers_panel.html).
- Blender Python API — `bpy.types.AnimData`, `bpy.types.Action`, `bpy.types.FCurve`, `bpy.types.Driver`, `bpy.types.DriverVariable`, `bpy.types.ActionSlot`, `bpy.types.PoseBoneConstraints`, `bpy.ops.graph.sound_bake`, `bpy.ops.nla.*`.
- Blender 4.4 Release Notes — [Slotted Actions](https://developer.blender.org/docs/release_notes/4.4/upgrading/slotted_actions/), [Animation & Rigging](https://developer.blender.org/docs/release_notes/4.4/animation_rigging/).
- Blender 4.5 LTS Release Notes — [4.5 LTS](https://developer.blender.org/docs/release_notes/4.5/).
