"""Softer tree-cage snare light (Nick, 2026-11-02: took the recommendation, radius 1.2 only).

    blender -b hohlweg_3.blend -P snare_soft.py                          (saves; safe to re-run)
    SR=1.2 SS_NOSAVE=1 ... -P snare_soft.py -P review_stills.py -- ...   (test in memory)

The 1:54.4 snare (f2747) burned a fir trunk near-white: FormLight_Snare (360 W in ERNSTFALL, radius 0.4 m) sits on
the trunk axis 2.8 m up (bank firs 1.3 m), inside its cage, so the bark and near needles take a small hot source.
Test (renders/ss_base, ss_r12, ss_r12o07; sheets ss_base/compare_*.png), near-white share of the most-changed crop:
    1:54  15.4% -> radius 1.2: 4.1%  -> + 0.7 m off trunk: 2.8%
    1:00  25.3% -> 19.9%             -> 20.7%, and a NEW pale streak: the offset lands next to a neighbouring trunk
Frame mean on hits drops 13-18% (the hot near-field going). Render time unchanged. Offset rejected.
    SR  FormLight_Snare radius (shadow_soft_size), was 0.4
"""
import bpy, os

SR = float(os.environ.get("SR", "1.2"))
bpy.data.lights["FormLight_Snare"].shadow_soft_size = SR
print("SS radius", SR, flush=True)
bpy.context.scene["snare_soft_applied"] = f"2026-11-02 radius {SR}"

if bpy.app.background and not os.environ.get("SS_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("SS saved", bpy.data.filepath, flush=True)
