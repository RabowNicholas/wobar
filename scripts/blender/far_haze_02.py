"""Far forest haze glow x0.2 (2026-11-05, brightness audit follow-up; Nick: "0.2 is good").

At exposure +3 and 4K the far valley (FarFir cones + FarCanopy, 300-2000 m, 5:16-5:46) came out LIGHTER than the sky:
their distance haze is emission (FV_HazeAmt * FV_HazeCol0), so the ridge glowed as a pale sheet of identical spires.
A night forest 1-2 km off should sit a little darker than the sky. Tested x1.0 / 0.5 / 0.2 at 5:23 and 5:33
(renders/bright_probe/fh_*): 0.5 merges the ridge into the sky, 0.2 gives a dark forested ridge with single trees.
A Math multiply 'FH_K' on Emission Strength in FarFir and FarCanopy.
"""
import bpy
sc = bpy.context.scene
if sc.get("far_haze_02_applied"): raise SystemExit("far_haze_02 already applied")
K = 0.2
for mn in ("FarFir", "FarCanopy"):
    nt = bpy.data.materials[mn].node_tree; b = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    inp = b.inputs["Emission Strength"]; assert "FH_K" not in nt.nodes
    m = nt.nodes.new("ShaderNodeMath"); m.operation = 'MULTIPLY'; m.name = "FH_K"; m.inputs[1].default_value = K
    if inp.links: nt.links.new(inp.links[0].from_socket, m.inputs[0])
    else: m.inputs[0].default_value = inp.default_value
    nt.links.new(m.outputs[0], inp)
sc["far_haze_02_applied"] = f"2026-11-05 x{K}"
print("FH", sc["far_haze_02_applied"], flush=True)
if bpy.app.background:
    bpy.ops.wm.save_mainfile(); print("FH saved", bpy.data.filepath, flush=True)
