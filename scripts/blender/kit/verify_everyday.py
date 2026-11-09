"""Render-diff KIT_Everyday against its source.  usage: blender -b everyday_tunnel_v1.blend -P verify_everyday.py -- KIT OUTDIR FRAME
Renders the source at FRAME, then (without saving) deletes the source parts and control empty, appends
KIT_Everyday + KIT_CTRL + EverydayWorld + EverydayComp from the kit, copies the source control values at FRAME
onto the kit WOBAR_CTRL, renders again. Both 8-bit PNG (FOOTGUNS V-6) at 25%, 8 samples, no motion blur."""
import bpy, sys
kit, out, frame = sys.argv[sys.argv.index("--") + 1:][:3]
frame = int(frame)
D = bpy.data; sc = bpy.context.scene; r = sc.render
sc.eevee.taa_render_samples = 8; r.resolution_percentage = 25; r.use_motion_blur = False
r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGB"; r.image_settings.color_depth = "8"
sc.frame_set(frame)
r.filepath = f"{out}/ev_src_{frame}.png"; bpy.ops.render.render(write_still=True)
vals = {k: D.objects["WOBAR_CTRL"][k] for k in D.objects["WOBAR_CTRL"].keys()}
for n in ("Tunnel", "Tunnel_Mid", "Tunnel_Inner", "VanishingLight", "VanishingOrb", "Camera", "WOBAR_CTRL"):
    D.objects.remove(D.objects[n])
for o in [o for o in D.objects if o.name.startswith("Shape_")]:
    D.objects.remove(o)
with D.libraries.load(kit, link=False) as (src, dst):
    dst.collections = ["KIT_Everyday", "KIT_CTRL"]; dst.worlds = ["EverydayWorld"]; dst.node_groups = ["EverydayComp"]
for c in dst.collections:
    sc.collection.children.link(c)
ctrl = D.objects["WOBAR_CTRL"]
for k, v in vals.items():
    ctrl[k] = v
sc.camera = D.objects["EverydayCam"]; sc.world = D.worlds["EverydayWorld"]
sc.compositing_node_group = D.node_groups["EverydayComp"]
ctrl.update_tag(); sc.frame_set(frame + 1); sc.frame_set(frame)
bad = [(i.name, d.data_path) for coll in (D.objects, D.node_groups, D.materials, D.lights, D.cameras)
       for i in coll if i.animation_data for d in i.animation_data.drivers if not d.is_valid]
print("INVALID", bad, "ctrl objects", [o.name for o in D.objects if o.name.startswith("WOBAR_CTRL")])
r.filepath = f"{out}/ev_kit_{frame}.png"; bpy.ops.render.render(write_still=True)
