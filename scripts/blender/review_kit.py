"""Review kit (2026-11-02): one render per frame, every pass, for the per-aspect review (light, surfaces, forms).

    blender -b --factory-startup hohlweg_3.blend -P review_kit.py -- --out DIR --frames 13297,15361 [--percent 100]

Per frame writes DIR/s_#####.png (the composited beauty, 16-bit) and DIR/p_#####.exr (multilayer: every pass below,
plus light groups moon / forms / other lights / world if EEVEE fills them). Resumable: a frame is done when both
files exist. Never saves the .blend. Sheets are cut from the EXRs by scripts/post/review_sheets.py.
"""
import bpy, os, sys, time, argparse

argv = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--frames", required=True)
p.add_argument("--percent", type=int, default=100)
p.add_argument("--samples", type=int, default=16)
a = p.parse_args(argv)

sc = bpy.context.scene; vl = sc.view_layers[0]; r = sc.render
os.makedirs(a.out, exist_ok=True)
r.resolution_percentage = a.percent
sc.eevee.taa_render_samples = a.samples
for n in sc.compositing_node_group.nodes:
    if n.bl_idname == "CompositorNodeOutputFile":
        n.mute = True
for k in ("diffuse_direct", "diffuse_indirect", "diffuse_color", "glossy_direct", "glossy_indirect", "glossy_color",
          "emit", "environment", "shadow", "z", "transmission_direct", "transmission_color"):
    setattr(vl, "use_pass_" + k, True)
vl.eevee.use_pass_volume_direct = True

# light groups: moon / forms / other lights / world
for name in ("moon", "forms", "other", "world"):
    if name not in vl.lightgroups:
        vl.lightgroups.add(name=name)
for ob in bpy.data.objects:
    if ob.type == "LIGHT":
        ob.lightgroup = "moon" if ob.name == "Moon" else "forms" if ob.name.startswith("FormLight") else "other"
if sc.world:
    sc.world.lightgroup = "world"
print("RK lights", sorted({(o.lightgroup) for o in bpy.data.objects if o.type == "LIGHT"}),
      "other:", [o.name for o in bpy.data.objects if o.type == "LIGHT" and o.lightgroup == "other"][:12], flush=True)

im = r.image_settings
frames = [int(x) for x in a.frames.split(",")]
todo = [f for f in frames if not (os.path.exists(f"{a.out}/s_{f:05d}.png") and os.path.exists(f"{a.out}/p_{f:05d}.exr"))]
print(f"RK {len(todo)} of {len(frames)} to render", flush=True)
log = open(os.path.join(a.out, "kit_log.csv"), "a", buffering=1)
for f in todo:
    t = time.time()
    sc.frame_set(f)
    bpy.ops.render.render(write_still=False)
    rr = bpy.data.images["Render Result"]
    im.media_type = "IMAGE"; im.file_format = "PNG"; im.color_depth = "16"
    rr.save_render(f"{a.out}/s_{f:05d}.part.png", scene=sc); os.replace(f"{a.out}/s_{f:05d}.part.png", f"{a.out}/s_{f:05d}.png")
    im.media_type = "MULTI_LAYER_IMAGE"; im.color_depth = "16"; im.exr_codec = "ZIP"
    rr.save_render(f"{a.out}/p_{f:05d}.part.exr", scene=sc); os.replace(f"{a.out}/p_{f:05d}.part.exr", f"{a.out}/p_{f:05d}.exr")
    log.write(f"{f},{time.time() - t:.1f}\n")
    print(f"RK {f} {time.time() - t:.1f}s", flush=True)
log.close()
sys.stdout.flush()
os._exit(0)
