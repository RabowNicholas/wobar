"""ABGRUND ambient hold and a quieter cover glow (2026-10-28, from the review_15_night pass).

    blender -b hohlweg_3.blend -P ambient_cover.py      (saves; safe to re-run)

Ambient: the world AmbientScale keys decayed from 0.4 at 5689 to 0.08 by 6937 (no documented decision), so the
moon-shadowed ground and fog rendered exact black (40% of ABGRUND pixels). Every key in 5689-11328 is held at
least AMB_HOLD (0.4, the documented ABGRUND value).
Cover: FormLight_Cover 150 W and FormWire_Cover strength 1 blew out 10:48-10:54. Both go to x COVER_K (0.33,
Nick's pick over 0.6), light radius 0.5 -> 1.5. Set absolutely, so re-running does not compound.
"""
import bpy, os

AMB_HOLD = 0.4
COVER_K = 0.33
COVER_W = 150.0

sc = bpy.context.scene
a = sc.world.node_tree.animation_data.action
n = 0
for L in a.layers:
    for s in L.strips:
        for cb in s.channelbags:
            for fc in cb.fcurves:
                if "AmbientScale" in fc.data_path:
                    for k in fc.keyframe_points:
                        if 5689 <= k.co[0] <= 11328 and k.co[1] < AMB_HOLD:
                            k.co[1] = AMB_HOLD; k.handle_left[1] = AMB_HOLD; k.handle_right[1] = AMB_HOLD; n += 1
                    fc.update()
print("AC ambient keys raised", n, flush=True)

L = bpy.data.objects["FormLight_Cover"].data
L.energy = COVER_W * COVER_K; L.shadow_soft_size = 1.5
bpy.data.materials["FormWire_Cover"].node_tree.nodes["FormEmission"].inputs["Strength"].default_value = COVER_K
sc["ambient_cover_applied"] = "2026-10-28"
print("AC cover", L.energy, flush=True)

if bpy.app.background and not os.environ.get("AC_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("AC saved", bpy.data.filepath, flush=True)
