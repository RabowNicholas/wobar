"""Water at real water's Fresnel, not a mirror (Nick, 2026-10-29: puddles "Yes, 1.33"; creek "Dark creek is right").

    blender -b hohlweg_3.blend -P water_ior.py      (saves; safe to re-run)

The 10-20 "mirror material" left the Fresnel at IOR 1000 on both water materials: every puddle reflected at full
strength right at the camera's feet, so near puddles were hard white sky cut-outs 4-19x the ground around them
(0:06, 0:24, 0:28) and the creek a pale flat ribbon (7:48-8:52, 9:30). At 1.33 near water shows the mud through it and
only grazing water mirrors: puddles 0.9-2x the ground, the creek a dark strip (0.3-1.3x). Tests: renders/water_00_base
vs water_02_ior133. The creek's mist glow stays at 0.
"""
import bpy, os

IOR = 1.33
for mn in ("RutWater_real", "CreekWater"):
    bpy.data.materials[mn].node_tree.nodes["Fresnel"].inputs["IOR"].default_value = IOR
bpy.context.scene["water_ior_applied"] = f"2026-10-29 {IOR}"
print("WI applied", IOR, flush=True)

if bpy.app.background and not os.environ.get("WI_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("WI saved", bpy.data.filepath, flush=True)
