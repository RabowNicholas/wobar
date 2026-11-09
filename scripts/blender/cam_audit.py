"""Camera audit (2026-11-02): the camera's exact transform and focus on every frame, no rendering.

    blender -b --factory-startup hohlweg_3.blend -P cam_audit.py -- --out DIR [--start 1 --end 15717]
Writes DIR/cam.npz: frame, loc (n,3), fwd (n,3), up (n,3), focus (n). Mesh modifiers are switched off in memory
first (the camera rides Spine and empties only), so a frame costs milliseconds. Never saves the .blend.
"""
import bpy, sys, time, argparse
import numpy as np
argv = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser(); p.add_argument("--out", required=True)
p.add_argument("--start", type=int, default=None); p.add_argument("--end", type=int, default=None)
a = p.parse_args(argv)
sc = bpy.context.scene; cam = sc.camera
for o in bpy.data.objects:
    if o.type in ("MESH", "POINTCLOUD", "VOLUME", "CURVES"):
        for m in o.modifiers:
            m.show_viewport = False
fs, fe = a.start or sc.frame_start, a.end or sc.frame_end
F, L, FW, UP, FO = [], [], [], [], []
t = time.time()
for f in range(fs, fe + 1):
    sc.frame_set(f)
    M = cam.matrix_world
    F.append(f); L.append(tuple(M.translation))
    FW.append(tuple(-M.col[2].xyz)); UP.append(tuple(M.col[1].xyz)); FO.append(cam.data.dof.focus_distance)
    if f % 2000 == 0: print("CA", f, f"{time.time() - t:.0f}s", flush=True)
np.savez(f"{a.out}/cam.npz", frame=np.array(F), loc=np.array(L), fwd=np.array(FW), up=np.array(UP), focus=np.array(FO))
print("CA done", len(F), f"{time.time() - t:.0f}s", flush=True)
import os; os._exit(0)
