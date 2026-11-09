"""ABGRUND root forms read lavender, not white (2026-10-27; review: at 4:22 they clip to white).

    blender -b hohlweg_3.blend -P root_wires.py      (saves; run once)   K 0.15 locked 2026-10-28; ROOT_K overrides it for tests

The root cages (RootCages, and RootletCages' Set Material) used the shared FormWire_Kick, whose peak clips to white
at the roots' size and distance. They get their own copy, FormWire_Root, with the emission (and the forms AOV) driven
at x ROOT_K - the same fix as the slide cages (slide_forms.py). Every other kick form keeps FormWire_Kick.
The hanging rootlets (RootletCages, FormWire_Pluck - used by nothing else) are scaled by the same K in place.
"""
import bpy, os

K = float(os.environ.get("ROOT_K", "0.15"))
sc = bpy.context.scene
assert "root_wires" not in sc, "already applied"
src = bpy.data.materials["FormWire_Kick"]
m = src.copy(); m.name = "FormWire_Root"
for d in m.node_tree.animation_data.drivers:
    if d.driver.expression == "peak * e":
        d.driver.expression = f"peak * e * {K}"
done = []
ob = bpy.data.objects["RootCages"]
for s in ob.material_slots:
    if s.material == src: s.material = m; done.append("RootCages slot")
if ob.data.materials:
    for i, mm in enumerate(ob.data.materials):
        if mm == src: ob.data.materials[i] = m
for md in bpy.data.objects["RootletCages"].modifiers:
    if md.type == "NODES" and md.node_group:
        for n in md.node_group.nodes:
            if n.type == "SET_MATERIAL" and n.inputs["Material"].default_value == src:
                n.inputs["Material"].default_value = m; done.append(f"{md.node_group.name}:{n.name}")
        users = [o.name for o in bpy.data.objects for x in o.modifiers if x.type == "NODES" and x.node_group == md.node_group]
        print("RW group users", md.node_group.name, users, flush=True)
# the hanging rootlets (RootletCages' only material, FormWire_Pluck): scale the emission strength, not the on/off test
pt = bpy.data.materials["FormWire_Pluck"].node_tree
emis = pt.nodes["FormEmission"]
lk = [l for l in pt.links if l.to_node == emis and l.to_socket.name == "Strength"][0]
mul = pt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.name = mul.label = "RW_RootletK"
mul.inputs[1].default_value = K
pt.links.new(lk.from_socket, mul.inputs[0]); pt.links.remove(lk); pt.links.new(mul.outputs[0], emis.inputs["Strength"])
done.append("FormWire_Pluck x K")
sc["root_wires"] = f"root cages on FormWire_Root and rootlets (FormWire_Pluck), emission x{K}"
print("RW applied", K, done, flush=True)
if bpy.app.background and not os.environ.get("ROOT_NOSAVE"):
    import sys
    bpy.ops.wm.save_mainfile(); print("RW saved", bpy.data.filepath, flush=True)
    sys.stdout.flush(); os._exit(0)
