"""The full render, resumable (2026-10-21).

Why: about one `blender -b` launch in ten exits without saving and without an error line (BLENDER_BUILD_LOG §2),
and the 4K piece is 15,717 frames at ~45-60 s each - days of rendering. So every frame is its own unit of work:

  resume    a frame is done when its beauty PNG and forms PNG both exist and end in a PNG IEND chunk (a crash mid-
            write leaves no IEND); everything else is rendered again. The beauty is written to a temp name and
            renamed, so a half-written file never looks done.
  checks    after each frame: the beauty must not be all black or contain NaN/inf; a frame far darker than its
            predecessor is logged as a warning (ABGRUND is legitimately near black between hits, so not retried)
  log       <out>/render_log.csv: frame, seconds, beauty and forms bytes, mean, max, warnings - and an ETA line
  stop      touch <out>/STOP to finish the current frame and exit cleanly; disk below --min-free-gb also stops
  chunks    one launch renders at most --chunk frames then exits (render_piece.sh relaunches), which keeps a
            slow leak or a stuck launch from costing more than one chunk
  animation (2026-11-02) a launch renders its chunk - the first unbroken run of missing frames, up to --chunk - as
            ONE animation render. A still render per frame rebuilds the render scene every frame (~25 s of a ~53 s
            4K frame); an animation render keeps it, ~19-26 s per frame, pixels identical (BLENDER_BUILD_LOG §3).
            Checks, log, STOP and the disk guard run in a render_write handler after each frame is written; a frame
            that fails the checks is deleted and left for the next launch. --stills restores the old per-frame mode.

Render (inside Blender, normally through render_piece.sh):
    blender -b hohlweg_final.blend -P render_piece.py -- --out DIR [--start 1] [--end 15717] [--chunk 200]
Check only (plain python, no Blender):
    python3 render_piece.py --out DIR [--start 1] [--end 15717]      -> prints missing/bad frames, exit 1 if any
"""
import os, sys, time, argparse, shutil, csv

IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"
BEAUTY = "beauty/hohlweg_{:05d}.png"
FORMS = "forms/forms_{:05d}.png"


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="/Volumes/music/assets/visualizers/hohlweg_v2")
    p.add_argument("--start", type=int, default=None)
    p.add_argument("--end", type=int, default=None)
    p.add_argument("--chunk", type=int, default=200)
    p.add_argument("--min-free-gb", type=float, default=25.0)
    p.add_argument("--no-forms", action="store_true", help="the forms pass is not written (FormsOut muted)")
    p.add_argument("--percent", type=int, default=None, help="resolution percentage, for tests only")
    p.add_argument("--samples", type=int, default=None, help="EEVEE render samples, for previews only")
    p.add_argument("--step", type=int, default=1, help="render every Nth frame (previews); files keep real frame numbers")
    p.add_argument("--stills", action="store_true", help="old mode: one still render per frame (slower, same pixels)")
    return p.parse_args(argv)


def png_ok(path, min_bytes=10_000):
    try:
        if os.path.getsize(path) < min_bytes:
            return False
        with open(path, "rb") as f:
            f.seek(-12, 2)
            return f.read() == IEND
    except OSError:
        return False


def done(out, f, forms=True):
    return png_ok(os.path.join(out, BEAUTY.format(f))) and (not forms or png_ok(os.path.join(out, FORMS.format(f)), 100))


def todo(out, start, end, forms=True, step=1):
    return [f for f in range(start, end + 1, step) if not done(out, f, forms)]


def check_main(a):
    start, end = a.start or 1, a.end or 15717
    miss = todo(a.out, start, end, not a.no_forms, a.step)
    n = len(range(start, end + 1, a.step))
    print(f"{n - len(miss)}/{n} frames done in {a.out}")
    if miss:
        runs, s = [], miss[0]
        for x, y in zip(miss, miss[1:] + [None]):
            if y != x + 1:
                runs.append(f"{s}-{x}" if x != s else f"{s}"); s = y
        print(f"TODO {len(miss)}: " + ", ".join(runs[:40]) + (" ..." if len(runs) > 40 else ""))
    free = shutil.disk_usage(a.out if os.path.isdir(a.out) else os.path.dirname(a.out)).free / 1e9
    print(f"free {free:.0f} GB")
    sys.exit(1 if miss else 0)


def render_main(a):
    import bpy
    import numpy as np
    sc = bpy.context.scene
    start, end = a.start or sc.frame_start, a.end or sc.frame_end
    for d in ("beauty", "forms"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    if a.percent:
        sc.render.resolution_percentage = a.percent
    if a.samples:
        sc.eevee.taa_render_samples = a.samples
    forms = False
    fo = [n for n in sc.compositing_node_group.nodes if n.bl_idname == "CompositorNodeOutputFile"]
    for n in fo:
        if n.name == "FormsOut":
            n.directory = os.path.join(a.out, "forms") + "/"
            n.file_name = "forms_#####"
            forms = not n.mute and not a.no_forms
    log_path = os.path.join(a.out, "render_log.csv")
    new_log = not os.path.exists(log_path)
    log = open(log_path, "a", newline="")
    w = csv.writer(log)
    if new_log:
        w.writerow(["frame", "seconds", "beauty_bytes", "forms_bytes", "mean", "max", "warn", "when"])
    queue = todo(a.out, start, end, forms, a.step)
    print(f"RP {len(queue)} frames to render in {start}-{end}; this launch takes up to {a.chunk}", flush=True)
    prev_mean, times = None, []
    if not a.stills:
        animation_main(a, sc, queue, forms, w, log)
        return
    for k, f in enumerate(queue[:a.chunk]):
        if os.path.exists(os.path.join(a.out, "STOP")):
            print("RP STOP file found; exiting", flush=True); break
        free = shutil.disk_usage(a.out).free / 1e9
        if free < a.min_free_gb:
            print(f"RP disk low ({free:.0f} GB free < {a.min_free_gb}); exiting", flush=True)
            log.close(); sys.stdout.flush()
            os._exit(3)    # render_piece.sh stops instead of relaunching; sys.exit() in a -P script hangs Blender 5.2
        t = time.time()
        sc.frame_set(f)
        bpy.ops.render.render(write_still=False)
        final = os.path.join(a.out, BEAUTY.format(f))
        tmp = final[:-4] + ".part.png"
        bpy.data.images["Render Result"].save_render(tmp, scene=sc)
        # checks on the written beauty
        im = bpy.data.images.load(tmp, check_existing=False)
        px = np.empty(len(im.pixels), dtype=np.float32); im.pixels.foreach_get(px)
        bpy.data.images.remove(im)
        rgb = px.reshape(-1, 4)[:, :3]
        warn = []
        if not np.isfinite(rgb).all():
            warn.append("nonfinite")
        mean, mx = float(np.nanmean(rgb)), float(np.nanmax(rgb))
        if mx <= 0.0:
            warn.append("black")
        if "nonfinite" in warn or "black" in warn:
            os.remove(tmp)
            print(f"RP frame {f} FAILED checks ({', '.join(warn)}); left for the next launch", flush=True)
            w.writerow([f, f"{time.time() - t:.1f}", 0, 0, f"{mean:.5f}", f"{mx:.5f}", "|".join(warn), time.strftime("%F %T")]); log.flush()
            continue
        if prev_mean and mean < 0.05 * prev_mean:
            warn.append("dark_jump")
        os.replace(tmp, final)
        fpath = os.path.join(a.out, FORMS.format(f))
        if forms and not png_ok(fpath, 100):
            warn.append("forms_missing")
        prev_mean = mean
        dt = time.time() - t; times.append(dt)
        w.writerow([f, f"{dt:.1f}", os.path.getsize(final), os.path.getsize(fpath) if os.path.exists(fpath) else 0,
                    f"{mean:.5f}", f"{mx:.5f}", "|".join(warn), time.strftime("%F %T")]); log.flush()
        left = len(queue) - k - 1
        eta = left * float(np.median(times[-20:]))
        print(f"RP frame {f} {dt:.1f}s {'WARN ' + ','.join(warn) if warn else ''}| {left} left, ETA {eta / 3600:.1f} h", flush=True)
    log.close()
    print("RP launch done", flush=True)


def check_frame(path):
    """Mean, max and warnings for a written beauty PNG (inside Blender).
    Read with OpenImageIO, not bpy.data.images: adding/removing an image datablock inside render_write during an
    animation render crashes Blender 5.2 on the next frame's depsgraph update (2026-11-03)."""
    import numpy as np
    import OpenImageIO as oiio
    px = np.asarray(oiio.ImageBuf(path).get_pixels(oiio.FLOAT), dtype=np.float32)
    if px.size == 0:
        raise OSError("empty read")
    rgb = px.reshape(-1, px.shape[-1])[:, :3]
    warn = []
    if not np.isfinite(rgb).all():
        warn.append("nonfinite")
    mean, mx = float(np.nanmean(rgb)), float(np.nanmax(rgb))
    if mx <= 0.0:
        warn.append("black")
    return mean, mx, warn


def animation_main(a, sc, queue, forms, w, log):
    import bpy
    import numpy as np
    if not queue:
        print("RP launch done", flush=True); return
    run = [queue[0]]                                   # first unbroken run of missing frames, up to --chunk
    for f in queue[1:a.chunk]:
        if f != run[-1] + a.step:
            break
        run.append(f)
    r = sc.render
    sc.frame_start, sc.frame_end, sc.frame_step = run[0], run[-1], a.step
    r.filepath = os.path.join(a.out, "beauty", "hohlweg_#####")
    r.use_file_extension, r.use_overwrite, r.use_placeholder = True, True, False
    print(f"RP animation render {run[0]}-{run[-1]} ({len(run)} frames)", flush=True)
    st = {"t": time.time(), "prev": None, "times": [], "left": len(queue)}

    def stop(code):
        log.flush(); log.close(); sys.stdout.flush()
        os._exit(code)

    def on_write(scene, *_):
        f = scene.frame_current
        final = os.path.join(a.out, BEAUTY.format(f))
        fpath = os.path.join(a.out, FORMS.format(f))
        dt = time.time() - st["t"]; st["t"] = time.time()
        try:
            mean, mx, warn = check_frame(final)
        except Exception as ex:                        # unreadable file: treat as failed
            mean, mx, warn = 0.0, 0.0, [f"unreadable:{type(ex).__name__}"]
        if "nonfinite" in warn or "black" in warn or any(x.startswith("unreadable") for x in warn):
            for pth in (final, fpath):
                if os.path.exists(pth):
                    os.remove(pth)
            print(f"RP frame {f} FAILED checks ({', '.join(warn)}); left for the next launch", flush=True)
            w.writerow([f, f"{dt:.1f}", 0, 0, f"{mean:.5f}", f"{mx:.5f}", "|".join(warn), time.strftime("%F %T")]); log.flush()
        else:
            if st["prev"] and mean < 0.05 * st["prev"]:
                warn.append("dark_jump")
            if forms and not png_ok(fpath, 100):
                warn.append("forms_missing")
            st["prev"] = mean
            st["times"].append(dt)
            w.writerow([f, f"{dt:.1f}", os.path.getsize(final), os.path.getsize(fpath) if os.path.exists(fpath) else 0,
                        f"{mean:.5f}", f"{mx:.5f}", "|".join(warn), time.strftime("%F %T")]); log.flush()
        st["left"] -= 1
        eta = st["left"] * float(np.median(st["times"][-20:])) if st["times"] else 0
        print(f"RP frame {f} {dt:.1f}s {'WARN ' + ','.join(warn) if warn else ''}| {st['left']} left, ETA {eta / 3600:.1f} h", flush=True)
        if f == run[-1]:
            print("RP launch done", flush=True); stop(0)
        if os.path.exists(os.path.join(a.out, "STOP")):
            print("RP STOP file found; exiting", flush=True); stop(0)
        free = shutil.disk_usage(a.out).free / 1e9
        if free < a.min_free_gb:
            print(f"RP disk low ({free:.0f} GB free < {a.min_free_gb}); exiting", flush=True); stop(3)

    bpy.app.handlers.render_write.append(on_write)
    free = shutil.disk_usage(a.out).free / 1e9
    if free < a.min_free_gb:
        print(f"RP disk low ({free:.0f} GB free < {a.min_free_gb}); exiting", flush=True); stop(3)
    if os.path.exists(os.path.join(a.out, "STOP")):
        print("RP STOP file found; exiting", flush=True); stop(0)
    bpy.ops.render.render(animation=True)
    print("RP launch done", flush=True); stop(0)


if __name__ == "__main__":
    a = args()
    try:
        import bpy  # noqa: F401
        in_blender = True
    except ImportError:
        in_blender = False
    (render_main if in_blender else check_main)(a)
