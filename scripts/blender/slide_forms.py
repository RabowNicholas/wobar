"""I-6: the fall's light from below (2026-10-27). The design (HOHLWEG_VISUALIZER §4, 2026-10-19): forms at the bottom
of the slide - toppled trunks on the kick, boulders on the snare, ABGRUND lavender - lit from beneath through the
mist, placed where the camera looks; the exposure crests with the snare roll. Never integrated until now: the
thick bowl fog had hidden that the fall had no reactive light at all.

    blender -b hohlweg_3_xxx.blend -P slide_forms.py      (saves the file it runs on; run once)

Forms are cages fitted to the real slide dressing (Scatter_Slide's dead_tree_trunk_02_slide and rock_moss_set_02
instances), chosen by a visibility survey of the fall 5:30-6:12 (renders/cut_signal_01/slide_vis.json: 79 seen,
21 trunks / 58 boulders; most 30-50 m out). The wires use the existing FormWire_Kick / FormWire_Snare materials,
so they flash from FORM_CTRL's kick / snare envelopes in the song's colour like every other form. Each form gets
its own point light, driven by the same envelopes through FORM_CTRL["slide_kick_w"] / ["slide_snare_w"].
Levels after Nick's "a little too hot" (rollforms_05): wires on their own *_Slide copies at x0.15 emission (lavender,
not clipped white), lights 260 / 120 W, 2.5 m above the cage centre with a 1.5 m radius (at 0.8 m they burned an
orange spot into the bark / rock under them).
"""
import bpy, json
from mathutils import Matrix, Vector

P = dict(vis="/Volumes/music/blender/renders/cut_signal_01/slide_vis.json",
         cages="/Users/nicholasrabow/Desktop/vaults/Vaults/wobar/wobar/scripts/blender/cages.py",
         n_kick=11, n_snare=20, thick=0.04, faces_kick=60, faces_snare=40, inflate=0.05,
         kick_w=260.0, kick_reach=22.0, snare_w=120.0, snare_reach=14.0, light_up=2.5, light_radius=1.5,
         wire_k=0.15)

sc = bpy.context.scene
assert "slide_forms" not in sc, "already applied"
ns = {}
exec(open(P["cages"]).read(), ns)
vis = sorted(json.load(open(P["vis"])), key=lambda e: -e["frames"])
kick = [e for e in vis if e["name"].startswith("dead_tree")][:P["n_kick"]]
snare = [e for e in vis if e["name"].startswith("rock")][:P["n_snare"]]

ctrl = bpy.data.objects["FORM_CTRL"]
ctrl["slide_kick_w"] = P["kick_w"]; ctrl["slide_snare_w"] = P["snare_w"]


def light_data(name, env, wprop, reach):
    d = bpy.data.lights.get(name) or bpy.data.lights.new(name, "POINT")
    d.use_shadow = False; d.specular_factor = 0.0; d.volume_factor = 1.0
    d.use_custom_distance = True; d.cutoff_distance = reach; d.shadow_soft_size = P["light_radius"]
    fc = d.driver_add("energy"); dr = fc.driver; dr.type = "SCRIPTED"
    for vn, path in (("w", f'["{wprop}"]'), ("e", f'["{env}"]')):
        v = dr.variables.new(); v.name = vn; v.targets[0].id = ctrl; v.targets[0].data_path = path
    dr.expression = "w * e"
    for i, c in enumerate("rgb"):
        fc = d.driver_add("color", i); dr = fc.driver; dr.type = "SCRIPTED"
        v = dr.variables.new(); v.name = c; v.targets[0].id = ctrl; v.targets[0].data_path = f'["form_{c}"]'
        dr.expression = c
    return d


col = bpy.data.collections.get("CAGE_SLIDE_FORMS") or bpy.data.collections.new("CAGE_SLIDE_FORMS")
if col.name not in [c.name for c in bpy.data.collections["FORMS"].children]:
    bpy.data.collections["FORMS"].children.link(col)
# own copies of the form wires, dimmer: at the shared materials' level the cages clipped white
slide_mat = {}
for src in ("FormWire_Kick", "FormWire_Snare"):
    m = bpy.data.materials[src].copy(); m.name = src + "_Slide"
    for d in m.node_tree.animation_data.drivers:
        if d.driver.expression == "peak * e":
            d.driver.expression = f"peak * e * {P['wire_k']}"
    slide_mat[src] = m.name
made = {"kick": 0, "snare": 0}
for kind, sel, mat, faces, env, wprop, reach in (
        ("kick", kick, slide_mat["FormWire_Kick"], P["faces_kick"], "kick", "slide_kick_w", P["kick_reach"]),
        ("snare", snare, slide_mat["FormWire_Snare"], P["faces_snare"], "snare", "slide_snare_w", P["snare_reach"])):
    ld = light_data(f"FormLight_Slide{kind.title()}", env, wprop, reach)
    protos = {}
    for i, e in enumerate(sel):
        src = e["name"]
        if src not in protos:   # one cage mesh per kit object, in that object's mesh space
            proto = ns["rock_cage"](src, f"slidecage_proto_{src}", collection="CAGE_SLIDE_PROTO", target_faces=faces,
                                    thickness=P["thick"], inflate=P["inflate"], mat_name=mat)
            proto.hide_render = True; proto.hide_viewport = True
            protos[src] = proto
        proto = protos[src]
        ob = bpy.data.objects.new(f"slidecage_{kind}_{i:02d}", proto.data)
        col.objects.link(ob)
        ob.matrix_world = Matrix(e["M"])
        wf = ob.modifiers.new("Beams", "WIREFRAME"); wf.thickness = P["thick"]; wf.use_replace = True; wf.use_even_offset = False
        ob.visible_shadow = False
        c = Matrix(e["M"]) @ (sum((v.co for v in proto.data.vertices), Vector()) / len(proto.data.vertices))
        lo = bpy.data.objects.new(f"slidelight_{kind}_{i:02d}", ld); col.objects.link(lo)
        lo.location = c + Vector((0, 0, P["light_up"]))
        made[kind] += 1
sc["slide_forms"] = str(P)
print("SF made", made, flush=True)
if bpy.app.background:
    import os, sys
    bpy.ops.wm.save_mainfile(); print("SF saved", bpy.data.filepath, flush=True)
    sys.stdout.flush(); os._exit(0)
