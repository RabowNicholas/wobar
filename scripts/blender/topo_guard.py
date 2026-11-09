"""Stop motion-blur smears from the camera-windowed ground (2026-11-05, realism audit).

5:11 (f7465) rendered as a pink, stair-stepped smear over half the frame. Cause: LaneView is rebuilt each (sub)frame
from a window around the camera, so its topology changes; EEVEE pairs vertices between the two shutter samples by
index whenever the vertex COUNT matches, and on f7465 both samples had exactly 162,260 vertices -> matched vertices
up to 111 m apart -> giant velocities (the steps are EEVEE's velocity tiles). Neighbouring frames differ in count, so
EEVEE drops deformation blur there and the frame is clean. EEVEE ignores the per-object cycles blur switches and a
`velocity` attribute on meshes (both tested).

Fix: a TopoGuard GN modifier (last in the stack) joins (floor(frame*16) mod 7) * 1000 loose vertices at the object
origin. Shutter samples 0.25 frame apart (shutter 0.25 -> 4/16) or 0.5 apart (shutter 0.5 -> 8/16) always land on
different residues mod 7, so the totals differ by >= 1000 - more than the window's own count moves between samples
(~0-20) - and EEVEE always treats these objects as static: camera blur stays, deformation blur goes (it was never
real: the ground does not move). Loose vertices have no faces and do not render.
Applied to LaneView, ForestFloorView, BankRootsView.
"""
import bpy, os
import numpy as np
sc = bpy.context.scene
if sc.get("topo_guard_applied"): raise SystemExit("topo_guard already applied")
TARGETS = ("LaneView", "ForestFloorView", "BankRootsView")


def guard():
    g = bpy.data.node_groups.get("TopoGuard")
    if g: return g
    g = bpy.data.node_groups.new("TopoGuard", "GeometryNodeTree")
    g.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    g.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, Lk = g.nodes, g.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    t = N.new("GeometryNodeInputSceneTime")
    m1 = N.new("ShaderNodeMath"); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 16
    fl = N.new("ShaderNodeMath"); fl.operation = 'FLOOR'
    md = N.new("ShaderNodeMath"); md.operation = 'FLOORED_MODULO'; md.inputs[1].default_value = 7
    m2 = N.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 1000
    ml = N.new("GeometryNodeMeshLine"); ml.mode = 'OFFSET'; ml.inputs["Offset"].default_value = (0, 0, 0)
    j = N.new("GeometryNodeJoinGeometry")
    Lk.new(t.outputs["Frame"], m1.inputs[0]); Lk.new(m1.outputs[0], fl.inputs[0]); Lk.new(fl.outputs[0], md.inputs[0])
    Lk.new(md.outputs[0], m2.inputs[0]); Lk.new(m2.outputs[0], ml.inputs["Count"])
    Lk.new(gi.outputs[0], j.inputs[0]); Lk.new(ml.outputs[0], j.inputs[0]); Lk.new(j.outputs[0], go.inputs[0])
    return g


g = guard()
for n in TARGETS:
    ob = bpy.data.objects[n]
    if "TopoGuard" not in ob.modifiers:
        m = ob.modifiers.new("TopoGuard", "NODES"); m.node_group = g
# verify on the frame that smeared: counts at the two shutter samples must differ
bad = []
for f in (7463, 7465, 7467):
    for n in TARGETS:
        r = []
        for s in (-0.125, 0.125):
            ff = f + s; sc.frame_set(int(np.floor(ff)), subframe=ff - np.floor(ff))
            e = bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get()); m = e.to_mesh(); r.append(len(m.vertices)); e.to_mesh_clear()
        if r[0] == r[1] and r[0] > 0: bad.append((f, n, r))
print("TG same-count pairs after guard:", bad, flush=True)
assert not bad
sc["topo_guard_applied"] = "2026-11-05"
if bpy.app.background and not os.environ.get("TG_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("TG saved", bpy.data.filepath, flush=True)
