"""Slip-floor ground v3 (Nick, 2026-10-27: "it looks like sand. it is very bright and very visible").

    blender -b hohlweg_3_light.blend -P ground_v3.py      (after light_v3.py, on the same fresh copy; saves)

Why it read as sand: `SlideGround`'s main layer is a dry pine-needle litter (forrest_ground_03, tan/orange),
lifted 3x by the v2 colour pass (V2_MudLift, meant for the lane's wet mud), with nothing on the floor but trees.
From 20-50 m up in moonlight that is a flat sandy plain. This is an old slide that rain has just soaked:
1. no 3x lift on the slide ground (wet raw soil reads dark again)
2. wet litter: the needle layer at 45% value and 70% saturation (wet needles are dark brown), roughness x0.75
3. moss: about half the moved ground under dark moss mats, value-varied
Raw soil on the torn faces is unchanged apart from (1). All new nodes are named G3_*.
"""
import bpy

P = dict(lift=1.0, litter_val=0.45, litter_sat=0.7, rough=0.75,
         moss_rgb=(0.10, 0.14, 0.06), moss_noise=(0.35, 3.0), moss_cover=(0.45, 0.60, 0.0, 0.65), moss_var=(0.7, 1.3))

sc = bpy.context.scene
assert "ground_v3" not in sc, "already applied - run on a fresh copy"
nt = bpy.data.materials["SlideGround"].node_tree
N, L = nt.nodes, nt.links


def node(kind, name, **kw):
    n = N.new(kind); n.name = n.label = name
    for k, v in kw.items():
        setattr(n, k, v)
    return n


# 1. no 3x lift
N["V2_MudLift"].inputs["Value"].default_value = P["lift"]

# 2. wet litter, 3. moss - spliced between the litter mix (Mix) and the litter/raw mix (Mix.001 A)
lk = [l for l in L if l.to_node == N["Mix.001"] and l.to_socket.identifier == N["Mix.001"].inputs[6].identifier
      and l.from_node == N["Mix"]][0]
litter = lk.from_socket; target = lk.to_socket; L.remove(lk)
wet = node("ShaderNodeHueSaturation", "G3_WetLitter")
wet.inputs["Saturation"].default_value = P["litter_sat"]; wet.inputs["Value"].default_value = P["litter_val"]
L.new(litter, wet.inputs["Color"])
tc = N["Texture Coordinate"]
mn = node("ShaderNodeTexNoise", "G3_MossNoise")
mn.inputs["Scale"].default_value, mn.inputs["Detail"].default_value = P["moss_noise"]
L.new(tc.outputs["Object"], mn.inputs["Vector"])
cover = node("ShaderNodeMapRange", "G3_MossCover", clamp=True, interpolation_type="SMOOTHSTEP")
L.new(mn.outputs["Fac"], cover.inputs["Value"])
for k, v in zip(("From Min", "From Max", "To Min", "To Max"), P["moss_cover"]):
    cover.inputs[k].default_value = v
mv = node("ShaderNodeTexNoise", "G3_MossVarNoise"); mv.inputs["Scale"].default_value = 2.5
L.new(tc.outputs["Object"], mv.inputs["Vector"])
mvr = node("ShaderNodeMapRange", "G3_MossVar", clamp=True)
L.new(mv.outputs["Fac"], mvr.inputs["Value"])
mvr.inputs["To Min"].default_value, mvr.inputs["To Max"].default_value = P["moss_var"]
mc = node("ShaderNodeRGB", "G3_MossColor"); mc.outputs[0].default_value = (*P["moss_rgb"], 1.0)
mcs = node("ShaderNodeVectorMath", "G3_MossShade", operation="SCALE")
L.new(mc.outputs[0], mcs.inputs[0]); L.new(mvr.outputs[0], mcs.inputs["Scale"])
mix = node("ShaderNodeMix", "G3_Moss", data_type="RGBA")
L.new(cover.outputs[0], mix.inputs["Factor"])
L.new(wet.outputs[0], mix.inputs[6]); L.new(mcs.outputs[0], mix.inputs[7])
L.new(mix.outputs[2], target)
# wet sheen on the moved ground: roughness x0.75 before the damp-edge mix
rl = [l for l in L if l.to_node == N["V2_DampRough"] and l.from_node == N["Math.002"]][0]
to = rl.to_socket; L.remove(rl)
r = node("ShaderNodeMath", "G3_WetRough", operation="MULTIPLY"); r.inputs[1].default_value = P["rough"]
L.new(N["Math.002"].outputs[0], r.inputs[0]); L.new(r.outputs[0], to)

sc["ground_v3"] = str(P)
print("GV3 applied", P, flush=True)
if bpy.app.background:
    import os, sys
    bpy.ops.wm.save_mainfile()
    print("GV3 saved", bpy.data.filepath, flush=True)
    sys.stdout.flush()
    os._exit(0)
