"""Second-fall glide without the speed step (camera audit, 2026-11-02).

    blender -b hohlweg_3.blend -P cam_glide.py                                  (saves; safe to re-run)
    CG_NOSAVE=1 ... -P cam_glide.py -P cam_audit.py -- --out DIR                (test in memory)

The audit (scripts/blender/cam_audit.py) found one hitch in the whole camera: at 6:05.8 (f8780 -> f8781) the fall speed drops
10.1 -> 7.2 m/s in one frame. Cause, ravine_blockout.fall_z(): the glide into the notch is blended in from the
free-fall speed, then the WHOLE glide is rescaled to land the remaining distance, which breaks the blend at its start.
Here only the shaped part is scaled, so the glide leaves at the free-fall speed and still lands exactly where and when
the baked one did. Rewrites the per-frame z keys of Camera_LaneDrop and CamTarget_LaneDrop (identical curves).
"""
import bpy, os
import numpy as np

F0 = 8781                                   # first glide key (8780 is the last free-fall key)


def zcurve(name):
    act = bpy.data.objects[name].animation_data.action
    fcs = [fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
    return next(fc for fc in fcs if fc.data_path == "location" and fc.array_index == 2)


fc = zcurve("Camera_LaneDrop")
keys = {int(round(k.co[0])): k.co[1] for k in fc.keyframe_points}
fr = np.array(sorted(keys)); z = np.array([keys[f] for f in fr])
dense = fr[(fr >= F0 - 3)]
# glide end: the first key after F0 from which z no longer changes
zz = np.array([keys[f] for f in dense])
still = np.where(np.abs(np.diff(zz)) < 1e-5)[0]
FE = int(dense[still[0]]) if len(still) else int(dense[-1])
zA, zE = keys[F0 - 1], keys[FE]
v0 = keys[F0 - 1] - keys[F0 - 2]            # m per frame leaving the free fall (negative = down)
n = FE - (F0 - 1)                           # frame steps from F0-1 to FE
u = (np.arange(n) + 0.5) / n
shape = 1 - u * u * (3 - 2 * u)
b = np.clip(u / 0.15, 0, 1)
k = ((zE - zA) - v0 * (1 - b).sum()) / (b * shape).sum()
step = (1 - b) * v0 + b * k * shape         # per-frame dz
assert np.all(step <= 1e-9), "glide would rise"
newz = zA + np.cumsum(step)
print(f"CG glide f{F0}-f{FE}: z {zA:.3f} -> {zE:.3f}, v0 {v0 * 24:.2f} m/s, end check {newz[-1] - zE:.2e}", flush=True)
for name in ("Camera_LaneDrop", "CamTarget_LaneDrop"):
    c = zcurve(name)
    for kp in c.keyframe_points:
        f = int(round(kp.co[0]))
        if F0 <= f <= FE:
            kp.co[1] = float(newz[f - F0]); kp.handle_left[1] = kp.handle_right[1] = kp.co[1]
    c.update()
bpy.context.scene["cam_glide_applied"] = f"2026-11-02 f{F0}-f{FE}"

if bpy.app.background and not os.environ.get("CG_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("CG saved", bpy.data.filepath, flush=True)
