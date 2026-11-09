"""MAKYO final render: bake the break sim over the whole song, then render all frames.
    blender -b makyo_final.blend -P scripts/blender/makyo_render_final.py -- <out_dir> [last_frame]
last_frame renders 1..last_frame only (the bake still covers the whole song); used for the intro re-render.
Resumable: existing frames are skipped (use_overwrite off + placeholders), the bake is redone each launch.
Settings come from the .blend: 2160x3840, EEVEE 48 samples, volume shadows 8, tile 4, motion blur 0.5 (1 step), 16-bit PNG
(chosen 2026-11-03 by 4K A/B: 48+8 is -26% time and visually identical to 64+16).
"""
import bpy, sys, os, time
args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, int(args[1]) if len(args) > 1 else 5452
ob = bpy.data.objects["ShardStream"]
for o in bpy.context.view_layer.objects:
    o.select_set(False)
ob.select_set(True); bpy.context.view_layer.objects.active = ob
t = time.time()
bpy.ops.object.simulation_nodes_cache_delete(selected=True)
print("bake", bpy.ops.object.simulation_nodes_cache_bake(selected=True), "%.0fs" % (time.time() - t), flush=True)
r = sc.render
r.resolution_percentage = 100; r.use_motion_blur = True   # samples/res/volume settings come from the .blend
r.image_settings.file_format = "PNG"; r.image_settings.color_depth = "16"
r.use_overwrite = False; r.use_placeholder = True
r.filepath = os.path.join(out, "makyo_####")
t = time.time()
bpy.ops.render.render(animation=True)
print("render done %.0fs" % (time.time() - t), flush=True)
sys.stdout.flush(); os._exit(0)
