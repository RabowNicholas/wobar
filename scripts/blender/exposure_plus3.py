"""Exposure 0 -> +3 (brightness audit, 2026-11-05; Nick: "do your recommendation").

At exposure 0 the dark frames sit ~9 stops under mid-grey in scene-linear, where AgX's toe is nearly flat: half of each
dark frame landed in 1-16 of the 16-bit PNG's codes and up to 85% of pixels wrote as exactly 0 (5:23), so a Resolve lift
showed black walls with blue/orange blotches. The linear render had no zeros - the detail was lost at the view transform.
+3 (tested 0..+4 on 7 4K EXR probes, renders/bright_probe): no crushed pixels, 73-786 codes in the bottom half, highlights
roll off in AgX's shoulder (fall 5:39 max 0.89). Render cost unchanged. The grade brings levels back down.
"""
import bpy
sc = bpy.context.scene
if sc.get("exposure_plus3_applied"): raise SystemExit("exposure_plus3 already applied")
v = sc.view_settings
assert v.view_transform == 'AgX' and abs(v.exposure) < 1e-6, (v.view_transform, v.exposure)
v.exposure = 3.0
sc["exposure_plus3_applied"] = "2026-11-05 0 -> +3"
print("EXP", sc["exposure_plus3_applied"], flush=True)
if bpy.app.background:
    bpy.ops.wm.save_mainfile(); print("EXP saved", bpy.data.filepath, flush=True)
