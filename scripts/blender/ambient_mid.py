"""World ambient lifted so shadows carry signal instead of dead black (Nick, 2026-11-03: "i dont want this to be crushed
blacks the whole time ... a nice dynamic range but also hide all of the details that make it not realistic").

    blender -b hohlweg_3.blend -P ambient_mid.py                 (saves; NOT safe to re-run - it scales the keys again)
    AM_NOSAVE=1 ... -P ambient_mid.py -P review_stills.py -- ... (test in memory)

Measured on the 10-28 review stills: 58-73% of ERNSTFALL frames held no signal at all (max channel < 16/65535), so no
grade could open them; ABGRUND/trench walls and GRUND foreground 4-16%. Test `renders/amb_base|mid|high` (Nick chose
mid, with the "night" toe curve as the grade target, colour pushed toward the green patina in post):
    ERNSTFALL     0.25 -> 0.4 (ABGRUND's 10-28 level)            dead black 58-73% -> 14-22%
    ABGRUND       x1.25 (0.4 -> 0.5)                              trench 16% -> 8%
    GRUND         x1.25 (0.4 -> 0.5, tail 0.25 -> 0.31)           16% -> 7%
    kept as is    the vista/fall window 7552-8990 (0.08 inside, Nick "lock it" 10-28; only its 0.4 end keys scale),
                  the clearing (>= 14881, 0.25)
    the ERNSTFALL -> ABGRUND ramp (5641-5689) is remapped 0.4 -> 0.5 so it rises instead of dipping.
"""
import bpy, os

AE, K = 0.4, 1.25
nt = bpy.context.scene.world.node_tree
if bpy.context.scene.get("ambient_mid_applied"):
    raise SystemExit("ambient_mid already applied - would scale twice")
fc = next(fc for l in nt.animation_data.action.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves
          if fc.data_path == 'nodes["AmbientScale"].inputs[0].default_value')
n = {"ern": 0, "ramp": 0, "scaled": 0, "kept": 0}
for k in fc.keyframe_points:
    f, v = k.co[0], k.co[1]
    if f < 5641:
        new = AE if abs(v - 0.25) < 1e-4 else v; n["ern"] += 1
    elif f < 5689:                                   # 0.25 -> 0.4 ramp becomes 0.4 -> 0.5
        new = AE + (v - 0.25) / 0.15 * (0.4 * K - AE); n["ramp"] += 1
    elif 7552 < f < 8990 or f >= 14881:
        n["kept"] += 1; continue
    else:
        new = min(v * K, 1.0); n["scaled"] += 1
    d = new - v; k.co[1] = new; k.handle_left[1] += d; k.handle_right[1] += d
fc.update()
bpy.context.scene["ambient_mid_applied"] = "2026-11-03 ERNSTFALL 0.4, ABGRUND/GRUND x1.25, vista window + clearing kept"
print("AM", n, flush=True)
if bpy.app.background and not os.environ.get("AM_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("AM saved", bpy.data.filepath, flush=True)
