# ---------------------------------------------------------------------------------------
# MOTION (2026-11-13): endless descent + swim, on the rust_fine look. Core removed (Nick).
# To be appended to scripts/blender/still_tippin/moire.py (needs its PALETTES, BASE, _hex,
# _col, _sheet_mat). Run after exec(moire.py).
#
# Descent = Shepard zoom. N sheets share ONE world scale; sheet k sits at depth
# d0·r^pos, pos = (k - u) mod N, u = speed·t. As u grows every sheet rises toward the camera
# and grows on screen; at pos→0 it wraps to the bottom. Fade w = sin(π·pos/N) hides the wrap,
# so the fall never arrives. r ≈ 1.1: adjacent sheets ~10% apart on screen — moiré range.
# Swim = each sheet's wave Phase Offset drifts at its own rate; the phantom bands move far
# faster than any line.
# Everything is keyed per frame (no drivers), so headless renders need nothing live.
# ---------------------------------------------------------------------------------------
import bpy, math

MOTION = dict(
    sheets=8,
    d0=2.0,
    r=1.10,
    speed=0.45,        # sheets per second rising past the camera
    freq=150.0,
    width=0.14,
    warp=0.7,
    warp_scale=0.6,
    angle_spread=3.0,  # degrees, alternating per sheet
    swim=(0.9, -0.6, 1.3, -1.1, 0.5, -1.4, 1.0, -0.8),   # phase rad/s per sheet
    strength=1.5,
    palette="rust",
)


def build_motion(seconds=5.0, fps=30, **overrides):
    p = dict(MOTION, **overrides)
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except TypeError as e:
        print("engine:", e)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = 100
    sc.render.fps = fps
    sc.view_settings.view_transform = "Standard"
    c = _col()
    pal = PALETTES[p["palette"]]
    w = bpy.data.worlds.get("MoireWorld") or bpy.data.worlds.new("MoireWorld")
    w.use_nodes = True
    w.node_tree.nodes.clear()
    wo = w.node_tree.nodes.new("ShaderNodeOutputWorld")
    bg = w.node_tree.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = _hex(pal[0])
    w.node_tree.links.new(bg.outputs[0], wo.inputs["Surface"])
    sc.world = w
    N, r = p["sheets"], p["r"]
    S = 1.3 * p["d0"] * r ** (N - 1)          # covers the frame at the deepest slot
    sheets = []
    for k in range(N):
        bpy.ops.mesh.primitive_plane_add(size=2)
        ob = bpy.context.active_object
        ob.name = f"Sheet{k}"
        for cc in list(ob.users_collection):
            cc.objects.unlink(ob)
        c.objects.link(ob)
        ob.scale = (S, S, 1)
        sp = dict(BASE)
        sp.update(freq=p["freq"], width=p["width"], warp_scale=p["warp_scale"],
                  angles=[p["angle_spread"] * (1 if j % 2 else -1) * (j % 3) for j in range(N)],
                  freq_mul=[1.0] * N, warp=[p["warp"]] * N, strength=[p["strength"]] * N,
                  lace=False, fog=False)
        m = _sheet_mat(sp, k, _hex(pal[1 + (k % 4)]))
        ob.data.materials.append(m)
        sheets.append(ob)
    nf = int(seconds * fps)
    sc.frame_start, sc.frame_end = 1, nf
    for f in range(1, nf + 1):
        t = (f - 1) / fps
        u = p["speed"] * t
        for k, ob in enumerate(sheets):
            pos = (k - u) % N
            ob.location.z = -p["d0"] * r ** pos
            ob.keyframe_insert("location", index=2, frame=f)
            nt = ob.data.materials[0].node_tree
            wv = next(n for n in nt.nodes if n.type == "TEX_WAVE")
            wv.inputs["Phase Offset"].default_value = p["swim"][k % len(p["swim"])] * t
            wv.inputs["Phase Offset"].keyframe_insert("default_value", frame=f)
            em = next(n for n in nt.nodes if n.type == "EMISSION")
            em.inputs["Strength"].default_value = p["strength"] * math.sin(math.pi * pos / N)
            em.inputs["Strength"].keyframe_insert("default_value", frame=f)
    cd = bpy.data.cameras.new("Cam")
    cd.lens = 30
    cd.clip_end = 2000
    cam = bpy.data.objects.new("Cam", cd)
    c.objects.link(cam)
    cam.rotation_euler = (0, 0, math.radians(8))
    sc.camera = cam
    print("motion built:", N, "sheets,", nf, "frames")
