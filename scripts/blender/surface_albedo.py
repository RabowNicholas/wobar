"""Trench walls and lane soil into the real albedo range (Nick, 2026-11-02: review finding, "do 1-3").

    blender -b hohlweg_3.blend -P surface_albedo.py            (saves; safe to re-run - sets absolute values)
    SA_NOSAVE=1 ... -P surface_albedo.py -P review_kit.py ...  (test in memory)

Review kit (renders/rv_kit_00): ABGRUND trench albedo median 0.015, 71-77% of surface below 0.02 (charcoal);
reflections carried 30-58% of the image, so walls read as colourless grey sheen. Lane soil below 0.02 in every song.
Damp loam / forest soil is ~0.08-0.15. Causes: the V2R wall colours were hand-set at 0.02-0.055 before groove,
stain and moss darkening; the lane runs through rut x0.55, wet band x0.6, damp edge x0.55 after V2_MudLift.

    KW  scale on every V2R wall colour (loam A/B, stain, moss)      base values are the 2026-10-20 ones below
    KL  V2_MudLift value (was 3.0) - lifts the whole lane/bank colour chain
"""
import bpy, os

KW = float(os.environ.get("KW", "3.0"))
KL = float(os.environ.get("KL", "6.0"))
BASE = {("V2R_WallLoam", "A"): (0.02, 0.014, 0.009), ("V2R_WallLoam", "B"): (0.055, 0.038, 0.024),
        ("V2R_WallStainMul", "B"): (0.02, 0.014, 0.009), ("V2R_WallMossMix", "B"): (0.016, 0.026, 0.008)}

nt = bpy.data.materials["LaneGround"].node_tree
for (node, sock), rgb in BASE.items():
    n = nt.nodes[node]
    s = next(i for i in n.inputs if i.name == sock and i.type == "RGBA" and i.enabled)
    s.default_value = (*(c * KW for c in rgb), 1.0)
    print("SA", node, sock, tuple(round(c, 4) for c in s.default_value[:3]), flush=True)
hsv = nt.nodes["V2_MudLift"]
hsv.inputs["Value"].default_value = KL
print("SA V2_MudLift value", KL, flush=True)
bpy.context.scene["surface_albedo_applied"] = f"2026-11-02 KW {KW} KL {KL}"

if bpy.app.background and not os.environ.get("SA_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("SA saved", bpy.data.filepath, flush=True)
