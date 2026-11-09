"""The cover form writes the `forms` AOV like every other form (2026-11-02 review finding).

    blender -b hohlweg_3.blend -P cover_aov.py            (saves; safe to re-run)
    CA_NOSAVE=1 ... -P cover_aov.py -P review_kit.py ...  (test in memory)

FormWire_Cover had no AOV output, so at 10:52 the cover was 31% of the glow and 0 form pixels: anything built from
the forms pass (sub trails in post) skipped it. Other forms write AOV = form colour (FORM_CTRL form_r/g/b drivers)
x emission strength, through a Vector Math SCALE whose inputs are DRIVEN, not linked (a plain node copy gives 0).
The cover's strength is a constant (0.33, ambient_cover.py), so its Scale is set to that value. (First pass drove it from
its own FormEmission strength: a driver reading its own node tree is a dependency cycle; fixed 2026-11-02.)
"""
import bpy, os

mat = bpy.data.materials["FormWire_Cover"]
nt = mat.node_tree
ctrl = bpy.data.objects["FORM_CTRL"]
for nm in ("FormAOVColor", "FormAOV"):
    if nm in nt.nodes:
        nt.nodes.remove(nt.nodes[nm])
if nt.animation_data:
    for d in [d for d in nt.animation_data.drivers if 'FormAOVColor' in d.data_path]:
        nt.animation_data.drivers.remove(d)
vm = nt.nodes.new("ShaderNodeVectorMath"); vm.name = vm.label = "FormAOVColor"; vm.operation = "SCALE"
aov = nt.nodes.new("ShaderNodeOutputAOV"); aov.name = "FormAOV"; aov.aov_name = "forms"
out = nt.nodes["Material Output"]
vm.location = (out.location.x, out.location.y - 220); aov.location = (vm.location.x + 220, vm.location.y)
nt.links.new(vm.outputs["Vector"], aov.inputs["Color"])

for k, prop in enumerate(("form_r", "form_g", "form_b")):
    fc = vm.inputs[0].driver_add("default_value", k); dr = fc.driver; dr.type = "SCRIPTED"
    v = dr.variables.new(); v.name = "c"; v.type = "SINGLE_PROP"
    v.targets[0].id_type = "OBJECT"; v.targets[0].id = ctrl; v.targets[0].data_path = f'["{prop}"]'
    dr.expression = "c"
scale = next(i for i in vm.inputs if i.name == "Scale")
scale.default_value = nt.nodes["FormEmission"].inputs[1].default_value   # constant; a driver on its own tree is a dependency cycle
bpy.context.scene.frame_set(15649)
print("CA cover AOV colour", tuple(round(x, 3) for x in vm.inputs[0].default_value), "scale", round(scale.default_value, 3),
      "drivers", len(nt.animation_data.drivers), flush=True)
bpy.context.scene["cover_aov_applied"] = "2026-11-02"

if bpy.app.background and not os.environ.get("CA_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("CA saved", bpy.data.filepath, flush=True)
