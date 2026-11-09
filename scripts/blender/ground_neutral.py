"""Ground pulled away from warm orange (Nick, 2026-11-04, on the 4K reel: "the ground is very orange with the raised
brightness i want to push it away from the warm earth and more towards an actual ground color").

    blender -b hohlweg_3.blend -P ground_neutral.py        (saves; refuses a second run - scene key ground_neutral_applied)

Test `scratchpad/ground/ground_sheet.png` (lane 0:32, trench 6:16, grass 8:32): saturation 60 / 40 / 45% + hue off
orange; Nick chose 60% ("B is what i want") - a dark brown with grey in it; 40% read as ash. One Hue/Saturation node
(`G4_GroundNeutral`, hue 0.5, saturation 0.6) right before the Base Color of `LaneGround` (lane, banks, trench walls,
forest floor) and `SlideGround` (the landslide). Logs, debris and roots keep their own colour.
"""
import bpy, os
SAT = float(os.environ.get("GN_SAT", "0.6"))
sc = bpy.context.scene
if sc.get("ground_neutral_applied"):
    raise SystemExit("ground_neutral already applied")
for mn in ("LaneGround", "SlideGround"):
    nt = bpy.data.materials[mn].node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    src = b.inputs["Base Color"].links[0].from_socket
    hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.name = hs.label = "G4_GroundNeutral"
    hs.inputs["Hue"].default_value, hs.inputs["Saturation"].default_value = 0.5, SAT
    hs.location = (b.location.x - 220, b.location.y - 300)
    nt.links.new(src, hs.inputs["Color"]); nt.links.new(hs.outputs["Color"], b.inputs["Base Color"])
    print("GN", mn, "<-", src.node.name, "sat", SAT, flush=True)
sc["ground_neutral_applied"] = f"2026-11-04 saturation {SAT}"
if bpy.app.background and not os.environ.get("GN_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("GN saved", bpy.data.filepath, flush=True)
