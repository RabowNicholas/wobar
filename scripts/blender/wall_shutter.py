"""Shorter shutter where the trench walls are close (Nick, 2026-10-29: approved).

    blender -b hohlweg_3.blend -P wall_shutter.py      (saves; safe to re-run)

The trench walls sit 4-5 m from a camera moving ~0.12 m/frame; at shutter 0.5 (180 deg) motion blur dragged their
fine loam grain into streaks ("fur", 5:14, 6:14-6:48). Grooves, stains, relief, normals, wall colour and moon shadows
were each ruled out; mboff gave crisp loam (renders/wall_00_base/crop_r4.png, crop_shutter.png). The shutter goes to
SH (0.25, 90 deg) through 5:00-5:30 and 6:12-7:36, easing from/to 0.5 over the second outside each stretch. The fall
(5:30-6:12) and the rest of the piece stay at 0.5. Tests: renders/wall_12_sh025, wall_13_sh035, wall_01_mboff.
"""
import bpy, os

SH = float(os.environ.get("SH", "0.25"))
OPEN = 0.5
STRETCHES = ((7201, 7921), (8929, 10945))     # 5:00-5:30, 6:12-7:36
sc = bpy.context.scene; r = sc.render

ad = sc.animation_data
if ad and ad.action:
    for L in ad.action.layers:
        for st in L.strips:
            for cb in st.channelbags:
                for fc in [f for f in cb.fcurves if f.data_path == "render.motion_blur_shutter"]:
                    cb.fcurves.remove(fc)
keys = []
for a, b in STRETCHES:
    keys += [(a - 24, OPEN), (a, SH), (b, SH), (b + 24, OPEN)]
for f, v in keys:
    r.motion_blur_shutter = v; sc.keyframe_insert("render.motion_blur_shutter", frame=f)
for L in sc.animation_data.action.layers:
    for st in L.strips:
        for cb in st.channelbags:
            for fc in cb.fcurves:
                if fc.data_path == "render.motion_blur_shutter":
                    fc.extrapolation = "CONSTANT"
                    for kp in fc.keyframe_points:
                        kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
                    fc.update()
sc["wall_shutter_applied"] = f"2026-10-29 {SH} {STRETCHES}"
for f in (1, 7189, 7201, 7537, 7921, 8401, 8929, 9361, 10945, 10957, 12000):
    sc.frame_set(f); print("WS", f, round(r.motion_blur_shutter, 3), flush=True)

if bpy.app.background and not os.environ.get("WS_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("WS saved", bpy.data.filepath, flush=True)
