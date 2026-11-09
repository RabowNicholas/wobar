"""Render-time profiling (2026-11-02). Consecutive frames, one variant per launch, nothing saved to the .blend.

    BV=base blender -b --factory-startup hohlweg_3.blend -P bench.py -- --out DIR --start 13297 --n 6
Per frame logs: frame_set time, render time, and the render's own stages (render_stats messages, timestamped),
peak process memory. Writes DIR/<variant>.csv and DIR/<variant>_stats.txt; images to DIR/<variant>/s_#####.png.
Variants (env BV, comma-joined to combine):
    base        as the file is
    noset       advance with frame_current instead of frame_set (skips the view-layer evaluation)
    s1          1 TAA sample (cost of everything that is not sampling)
    p25         25% resolution
    vs64/vs96   volumetric_samples 64 / 96          vss8   volumetric_shadow_samples 8
    vrd8        volumetric_ray_depth 8               nomb   motion blur off (reference only)
    anim        render the frames as one animation render (render depsgraph kept between frames)
"""
import bpy, os, sys, time, argparse, resource
argv = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser(); p.add_argument("--out", required=True)
p.add_argument("--start", type=int, required=True); p.add_argument("--n", type=int, default=6)
a = p.parse_args(argv)
V = os.environ.get("BV", "base").split(",")
name = "_".join(V)
sc = bpy.context.scene; e = sc.eevee; r = sc.render
for n in sc.compositing_node_group.nodes:
    if n.bl_idname == "CompositorNodeOutputFile":
        n.mute = True
if "s1" in V: e.taa_render_samples = 1
if "p25" in V: r.resolution_percentage = 25
if "vs64" in V: e.volumetric_samples = 64
if "vs96" in V: e.volumetric_samples = 96
if "vss8" in V: e.volumetric_shadow_samples = 8
if "vrd8" in V: e.volumetric_ray_depth = 8
if "nomb" in V: r.use_motion_blur = False
os.makedirs(f"{a.out}/{name}", exist_ok=True)
stats = open(f"{a.out}/{name}_stats.txt", "w", buffering=1)
T0 = [time.time()]
last = [None]
def on_stats(s, *_):
    s = str(s)
    stage = s.split("|")[-1].strip()
    if stage != last[0]:
        stats.write(f"{time.time() - T0[0]:8.2f} {stage}\n"); last[0] = stage
bpy.app.handlers.render_stats.append(on_stats)
log = open(f"{a.out}/{name}.csv", "w", buffering=1); log.write("frame,set_s,render_s,save_s,maxrss_gb\n")
if "anim" in V:      # one animation render: Blender keeps the render depsgraph between frames
    sc.frame_start, sc.frame_end = a.start, a.start + a.n - 1
    r.filepath = f"{a.out}/{name}/s_"; r.image_settings.file_format = "PNG"
    tl = [time.time()]
    def post(scene, *_):
        t = time.time(); rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9
        log.write(f"{scene.frame_current},0,{t - tl[0]:.2f},0,{rss:.1f}\n")
        print(f"BN {name} {scene.frame_current} frame {t - tl[0]:.1f} rss {rss:.1f}GB", flush=True); tl[0] = t; T0[0] = t
        stats.write(f"--- frame {scene.frame_current + 1}\n")
    bpy.app.handlers.render_write.append(post)
    bpy.ops.render.render(animation=True)
    sys.stdout.flush(); os._exit(0)
for f in range(a.start, a.start + a.n):
    t = time.time(); T0[0] = t; stats.write(f"--- frame {f}\n")
    if "noset" in V:
        sc.frame_current = f
    else:
        sc.frame_set(f)
    t1 = time.time()
    bpy.ops.render.render(write_still=False)
    t2 = time.time()
    bpy.data.images["Render Result"].save_render(f"{a.out}/{name}/s_{f:05d}.png", scene=sc)
    t3 = time.time()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9      # bytes on macOS
    log.write(f"{f},{t1 - t:.2f},{t2 - t1:.2f},{t3 - t2:.2f},{rss:.1f}\n")
    print(f"BN {name} {f} set {t1 - t:.1f} render {t2 - t1:.1f} save {t3 - t2:.1f} rss {rss:.1f}GB", flush=True)
sys.stdout.flush(); os._exit(0)
