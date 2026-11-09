"""Trench mist 0.10 -> 0.06 /m (Nick, 2026-11-05: "0.06"; realism audit item 3).

Looking down a straight stretch (1:37, 10:35) the far end read as a flat, bright block of mist with a ruler-straight
top. Bisected: it is the ground - rays below the far bank's crest travel inside the dense trench layer all the way to
the bank wall facing the camera, rays above it leave the layer into the thin forest mist. Physically right; the CG
tell was how even and opaque the block was at 0.1/m. Tested 0.10 / 0.06 / 0.035 (renders/... scratchpad audit/mist/td.jpg).
Ruled out first: the 2.6-3.4 m trench cut-off, bare skyline, volume shadows, volume tile size, volumetric_end.
Whole piece: MistVolume node TrenchDensity input[1].
"""
import bpy, os
sc = bpy.context.scene
if sc.get("trench_mist_06_applied"): raise SystemExit("trench_mist_06 already applied")
n = bpy.data.materials["MistVolume"].node_tree.nodes["TrenchDensity"]
old = n.inputs[1].default_value
assert abs(old - 0.1) < 1e-4, old
n.inputs[1].default_value = 0.06
sc["trench_mist_06_applied"] = f"2026-11-05 {old:.3f} -> 0.06"
print("TM", sc["trench_mist_06_applied"], flush=True)
if bpy.app.background:
    bpy.ops.wm.save_mainfile(); print("TM saved", bpy.data.filepath, flush=True)
