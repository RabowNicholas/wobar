"""The yellow-green strip in the lane (2026-10-27, review: 3:06 and 7:42).

    blender -b hohlweg_3.blend -P lane_strip.py      (saves; run once)

Two LaneGround layers went lime under the v2 pass's 3x mud lift (V2_MudLift), found by tracer colours
(renders/strip_03_trace, strip_04_trace2):
- 3:06: the leaf litter (forest_leaves_02 via Hue/Saturation/Value.002, hue +0.07) - a yellowish texture pushed further
  toward yellow-green. Now wet brown: hue 0.47, saturation 0.55, value 0.28.
- 7:42: the band of moss 0.9-3 m up the bank (Color.001, (0.02, 0.04, 0.014)) - x3 lifted it to lime. Now near-neutral
  dark (0.010, 0.012, 0.009).
Frame brightness unchanged (x0.99-1.00); before/after renders/strip_05_fix/AB.png.
"""
import bpy

sc = bpy.context.scene
assert "lane_strip" not in sc, "already applied"
N = bpy.data.materials["LaneGround"].node_tree.nodes
h = N["Hue/Saturation/Value.002"]
h.inputs["Hue"].default_value = 0.47; h.inputs["Saturation"].default_value = 0.55; h.inputs["Value"].default_value = 0.28
N["Color.001"].outputs[0].default_value = (0.010, 0.012, 0.009, 1.0)
sc["lane_strip"] = "leaves h0.47 s0.55 v0.28; bank moss (0.010, 0.012, 0.009)"
print("LS applied", flush=True)
if bpy.app.background:
    import os, sys
    bpy.ops.wm.save_mainfile(); print("LS saved", bpy.data.filepath, flush=True)
    sys.stdout.flush(); os._exit(0)
