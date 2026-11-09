"""Review pass stills (2026-10-26): one frame every N across the piece, quarter res, compositing on, resumable.

    blender -b hohlweg_3.blend -P review_stills.py -- --out DIR [--every 48] [--percent 25] [--samples 16]
Frames already on disk (a complete PNG) are skipped. Log: <out>/stills_log.csv (frame, seconds, mean).

2026-11-02: each unbroken run of frames is rendered as ONE animation render, which keeps the render scene between
frames (~2x faster on consecutive frames, pixels identical; BLENDER_BUILD_LOG §3). Frames far apart still cost a full
scene build each. --stills restores the old one-still-per-frame loop.
"""
import bpy, os, sys, time, argparse
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--every", type=int, default=48)
p.add_argument("--percent", type=int, default=25)
p.add_argument("--samples", type=int, default=16)
p.add_argument("--frames", default=None, help="comma list, overrides --every")
p.add_argument("--stills", action="store_true", help="old mode: one still render per frame")
a = p.parse_args(argv)

IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def png_ok(path):
    try:
        with open(path, "rb") as fh:
            fh.seek(-12, 2)
            return fh.read() == IEND
    except OSError:
        return False


def mean_of(path):
    # OpenImageIO, not bpy.data.images: a datablock added in render_write mid-animation crashes Blender 5.2
    import OpenImageIO as oiio
    px = np.asarray(oiio.ImageBuf(path).get_pixels(oiio.FLOAT), dtype=np.float32)
    return px.reshape(-1, px.shape[-1])[:, :3].mean()


sc = bpy.context.scene
os.makedirs(a.out, exist_ok=True)
for n in sc.compositing_node_group.nodes:
    if n.bl_idname == "CompositorNodeOutputFile":
        n.mute = True
sc.render.resolution_percentage = a.percent
sc.eevee.taa_render_samples = a.samples
frames = [int(x) for x in a.frames.split(",")] if a.frames else list(range(sc.frame_start, sc.frame_end + 1, a.every))
log = open(os.path.join(a.out, "stills_log.csv"), "a", buffering=1)
todo = [f for f in frames if not png_ok(os.path.join(a.out, f"s_{f:05d}.png"))]
print(f"RS {len(todo)} of {len(frames)} to render", flush=True)

if a.stills:
    for f in todo:
        t = time.time()
        sc.frame_set(f)
        bpy.ops.render.render(write_still=False)
        path = os.path.join(a.out, f"s_{f:05d}.png")
        bpy.data.images["Render Result"].save_render(path + ".part.png", scene=sc)
        os.replace(path + ".part.png", path)
        log.write(f"{f},{time.time() - t:.1f},{mean_of(path):.5f}\n")
        print(f"RS {f} {time.time() - t:.1f}s", flush=True)
else:
    runs = []
    for f in sorted(todo):
        if runs and f == runs[-1][-1] + 1:
            runs[-1].append(f)
        else:
            runs.append([f])
    r = sc.render
    r.filepath = os.path.join(os.path.abspath(a.out), "s_#####")
    r.use_file_extension, r.use_overwrite, r.use_placeholder = True, True, False
    st = {"t": time.time()}

    def on_write(scene, *_):
        f = scene.frame_current
        dt = time.time() - st["t"]; st["t"] = time.time()
        log.write(f"{f},{dt:.1f},{mean_of(os.path.join(a.out, f's_{f:05d}.png')):.5f}\n")
        print(f"RS {f} {dt:.1f}s", flush=True)

    bpy.app.handlers.render_write.append(on_write)
    for run in runs:
        sc.frame_start, sc.frame_end, sc.frame_step = run[0], run[-1], 1
        print(f"RS run {run[0]}-{run[-1]} ({len(run)})", flush=True)
        st["t"] = time.time()
        bpy.ops.render.render(animation=True)
log.close()
sys.stdout.flush()
os._exit(0)
