"""Moon lights the GRUND-approach mist at half strength (Nick, 2026-10-30: "dimmer and smaller"; option A approved).

    blender -b hohlweg_3.blend -P moon_mist.py      (saves; safe to re-run)

The white pool where the lane meets the mist at 9:40-9:58 (worst 9:44-9:50, view-clip to 2.2%) is moonlight scattered
by the mist: moon off removed it (centre x0.02-0.07), mist off x0.16-0.29; cover light, sky, far valley no change.
Moon volume_factor -> VF from 9:34 to 10:02, easing over the second outside it: centre x0.62-0.68, view-clip halved,
ground and shafts keep their light. Half the valley fog was weaker (x0.72-0.76) and touched the approved GRUND depth;
no forward scatter x0.82-0.85. Tests: renders/hot_00_base, hot_01_*, hot_02_* (sheet hot_02_vf0.5/AB_glow.png).
"""
import bpy, os

VF = float(os.environ.get("VF", "0.5"))
A, B = 13777, 14449                                # 9:34, 10:02
lt = bpy.data.objects["Moon"].data

ad = lt.animation_data
if ad and ad.action:
    for L in ad.action.layers:
        for st in L.strips:
            for cb in st.channelbags:
                for fc in [f for f in cb.fcurves if f.data_path == "volume_factor"]:
                    cb.fcurves.remove(fc)
for f, v in ((A - 24, 1.0), (A, VF), (B, VF), (B + 24, 1.0)):
    lt.volume_factor = v; lt.keyframe_insert("volume_factor", frame=f)
for L in lt.animation_data.action.layers:
    for st in L.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                if fc.data_path == "volume_factor":
                    fc.extrapolation = "CONSTANT"
                    for kp in fc.keyframe_points:
                        kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
                    fc.update()
sc = bpy.context.scene
sc["moon_mist_applied"] = f"2026-10-30 {VF} {A}-{B}"
for f in (1, 13393, 13765, 13777, 14065, 14449, 14461, 14473, 15649):
    sc.frame_set(f); print("MM", f, round(lt.volume_factor, 3), round(lt.energy, 2), flush=True)

if bpy.app.background and not os.environ.get("MM_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("MM saved", bpy.data.filepath, flush=True)
