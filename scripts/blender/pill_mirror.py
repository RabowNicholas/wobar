"""Pill mirror — a copy of reference clip 9 (kishimisu-style folded pill field) as a
seamless VJ loop. Everything is one emission shader on a 9:16 plane under an ortho camera.

    Blender -b --factory-startup -P scripts/blender/pill_mirror.py -- [out.blend] [k=v ...]

Builds a fresh scene, saves it. Tuning = change a value in P (or pass k=v), rerun.
Loop: every animated value is periodic over P["frames"], so frame frames+1 == frame 1.
"""
import bpy, os, sys

P = dict(
    frames=240, fps=30,          # 8 s loop
    warp=0.35,                   # rows fan out from the centre: u = q * (r + 0.3)^-warp
    stretch_x=0.42,              # < 1 stretches cells sideways into pills (aspect = 1 / stretch_x)
    scale=3.0,                   # cell density
    randomness=0.6,
    smooth=0.4,                  # Smooth F1: how much neighbouring pills melt together
    exponent=4.0,                # Minkowski: 2 = ellipse, 4 = rounded rect
    drift=1.5,                   # radius, in cells, of the circle the field travels per loop
    dims="2D",                   # 2D: pills persist; 4D: pills also morph in and out of the slice
    morph=0.18,                  # 4D only: radius of the (z, w) circle
    pill_r=0.24,                 # distance below which a pixel is inside a pill
    pill_aa=0.012,
    band_freq=7.0,               # rainbow rings per unit distance
    band_cycles=3,               # ring phase turns per loop (integer, keeps the loop seamless)
    seam_w=0.15,                 # width of the line band along the fold cross (world units)
    seam_freq=45.0,
)


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = None
    for a in argv:
        if "=" in a:
            k, v = a.split("=", 1)
            P[k] = type(P[k])(v)
        else:
            out = a
    return out


def node(nt, kind, loc, **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def drive(sock, expr, index=-1):
    fc = sock.driver_add("default_value", index) if index >= 0 else sock.driver_add("default_value")
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = expr
    return fc


def ramp(nt, loc, stops):
    r = node(nt, "ShaderNodeValToRGB", loc)
    els = r.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
    for pos, col in stops[1:]:
        e = els.new(pos)
        e.color = (*col, 1)
    return r


def hexc(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def build_material():
    mat = bpy.data.materials.new("PillMirror")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    L = nt.links.new
    N = P["frames"]

    tc = node(nt, "ShaderNodeTexCoord", (-1800, 0))
    fold = node(nt, "ShaderNodeVectorMath", (-1600, 0), operation="ABSOLUTE", name="Fold")
    L(tc.outputs["Object"], fold.inputs[0])

    # fan: scale coordinates by (r + 0.3)^-warp so cells grow toward the edges
    rlen = node(nt, "ShaderNodeVectorMath", (-1400, -200), operation="LENGTH")
    L(fold.outputs[0], rlen.inputs[0])
    radd = node(nt, "ShaderNodeMath", (-1250, -200), operation="ADD")
    radd.inputs[1].default_value = 0.3
    L(rlen.outputs["Value"], radd.inputs[0])
    rpow = node(nt, "ShaderNodeMath", (-1100, -200), operation="POWER", name="Warp")
    rpow.inputs[1].default_value = -P["warp"]
    L(radd.outputs[0], rpow.inputs[0])
    fan = node(nt, "ShaderNodeVectorMath", (-1100, 0), operation="SCALE")
    L(fold.outputs[0], fan.inputs[0])
    L(rpow.outputs[0], fan.inputs["Scale"])
    squash = node(nt, "ShaderNodeVectorMath", (-950, 0), operation="MULTIPLY", name="Stretch")
    squash.inputs[1].default_value = (P["stretch_x"], 1.0, 0.0)
    L(fan.outputs[0], squash.inputs[0])

    # loop: the field travels a closed circle, so the last frame meets the first.
    # (Scrolling by whole cells does NOT loop - Voronoi re-randomises per cell.)
    circ = node(nt, "ShaderNodeCombineXYZ", (-950, -250), name="LoopDrift")
    rad = P["drift"] / P["scale"]
    drive(circ.inputs["X"], f"{rad:.4f}*cos(2*pi*frame/{N})")
    drive(circ.inputs["Y"], f"{rad:.4f}*sin(2*pi*frame/{N})")
    if P["dims"] == "4D":
        drive(circ.inputs["Z"], f"{P['morph']}*cos(2*pi*frame/{N})")
    u = node(nt, "ShaderNodeVectorMath", (-800, 0), operation="ADD")
    L(squash.outputs[0], u.inputs[0])
    L(circ.outputs[0], u.inputs[1])

    vor = node(nt, "ShaderNodeTexVoronoi", (-600, 0), name="Pills",
               voronoi_dimensions=P["dims"], feature="SMOOTH_F1", distance="MINKOWSKI")
    vor.inputs["Scale"].default_value = P["scale"]
    vor.inputs["Smoothness"].default_value = P["smooth"]
    vor.inputs["Exponent"].default_value = P["exponent"]
    vor.inputs["Randomness"].default_value = P["randomness"]
    if P["dims"] == "4D":
        drive(vor.inputs["W"], f"{P['morph']}*sin(2*pi*frame/{N})")
    L(u.outputs[0], vor.inputs["Vector"])
    d = vor.outputs["Distance"]

    # inside-a-pill mask
    inside = node(nt, "ShaderNodeMapRange", (-300, 300), interpolation_type="SMOOTHSTEP", name="PillMask")
    inside.inputs["From Min"].default_value = P["pill_r"] - P["pill_aa"]
    inside.inputs["From Max"].default_value = P["pill_r"] + P["pill_aa"]
    inside.inputs["To Min"].default_value = 1.0
    inside.inputs["To Max"].default_value = 0.0
    L(d, inside.inputs["Value"])

    # rainbow rings: fract(d * freq - phase); dark stop at the wrap draws the contour line
    bmul = node(nt, "ShaderNodeMath", (-350, -150), operation="MULTIPLY", name="BandFreq")
    bmul.inputs[1].default_value = P["band_freq"]
    L(d, bmul.inputs[0])
    bsub = node(nt, "ShaderNodeMath", (-200, -150), operation="SUBTRACT", name="BandPhase")
    drive(bsub.inputs[1], f"{P['band_cycles']}*frame/{N}")
    L(bmul.outputs[0], bsub.inputs[0])
    bfr = node(nt, "ShaderNodeMath", (-50, -150), operation="FRACT")
    L(bsub.outputs[0], bfr.inputs[0])
    band = ramp(nt, (100, -150), [
        (0.00, hexc("#2a2a2e")), (0.05, hexc("#2b1d5c")), (0.18, hexc("#2349a8")),
        (0.32, hexc("#2a8c8a")), (0.46, hexc("#5f8a3a")), (0.58, hexc("#9a8a35")),
        (0.70, hexc("#b5652a")), (0.82, hexc("#8a2e2a")), (0.93, hexc("#4a1e4e")),
        (1.00, hexc("#2a2a2e")),
    ])
    band.name = "BandRamp"
    L(bfr.outputs[0], band.inputs["Fac"])

    # pill fill: one random hue per cell, brighter toward the centre of the pill
    sep = node(nt, "ShaderNodeSeparateColor", (-300, 500))
    L(vor.outputs["Color"], sep.inputs[0])
    fill = ramp(nt, (-100, 500), [
        (0.00, hexc("#0d1f6b")), (0.18, hexc("#1f5fd1")), (0.36, hexc("#7cd3f2")),
        (0.50, hexc("#f2e6b8")), (0.66, hexc("#f2a23a")), (0.82, hexc("#c25418")),
        (1.00, hexc("#5a1414")),
    ])
    fill.name = "FillRamp"
    L(sep.outputs[0], fill.inputs["Fac"])
    shade = node(nt, "ShaderNodeMapRange", (-100, 750), name="PillShade")
    shade.inputs["From Min"].default_value = 0.0
    shade.inputs["From Max"].default_value = P["pill_r"]
    shade.inputs["To Min"].default_value = 1.35
    shade.inputs["To Max"].default_value = 0.75
    L(d, shade.inputs["Value"])
    lit = node(nt, "ShaderNodeMix", (200, 500), data_type="RGBA", blend_type="MULTIPLY")
    lit.inputs["Factor"].default_value = 1.0
    L(fill.outputs["Color"], lit.inputs["A"])
    L(shade.outputs["Result"], lit.inputs["B"])

    mix = node(nt, "ShaderNodeMix", (450, 200), data_type="RGBA", name="Composite")
    L(inside.outputs["Result"], mix.inputs["Factor"])
    L(band.outputs["Color"], mix.inputs["A"])
    L(lit.outputs["Result"], mix.inputs["B"])

    # seam: tight grey lines along the fold cross, fading out from the axes
    sxy = node(nt, "ShaderNodeSeparateXYZ", (-1400, -500))
    L(fold.outputs[0], sxy.inputs[0])
    smin = node(nt, "ShaderNodeMath", (-1200, -500), operation="MINIMUM")
    L(sxy.outputs["X"], smin.inputs[0])
    L(sxy.outputs["Y"], smin.inputs[1])
    smask = node(nt, "ShaderNodeMapRange", (200, -500), interpolation_type="SMOOTHSTEP", name="SeamMask")
    smask.inputs["From Min"].default_value = 0.0
    smask.inputs["From Max"].default_value = P["seam_w"]
    smask.inputs["To Min"].default_value = 1.0
    smask.inputs["To Max"].default_value = 0.0
    L(smin.outputs[0], smask.inputs["Value"])
    sfreq = node(nt, "ShaderNodeMath", (-1000, -500), operation="MULTIPLY")
    sfreq.inputs[1].default_value = P["seam_freq"]
    L(smin.outputs[0], sfreq.inputs[0])
    sfr = node(nt, "ShaderNodeMath", (-850, -500), operation="PINGPONG")
    sfr.inputs[1].default_value = 0.5
    L(sfreq.outputs[0], sfr.inputs[0])
    sline = ramp(nt, (-650, -500), [(0.0, hexc("#15151a")), (0.36, hexc("#1c1c22")), (0.5, hexc("#9a9aa0"))])
    sline.name = "SeamRamp"
    L(sfr.outputs[0], sline.inputs["Fac"])
    seam = node(nt, "ShaderNodeMix", (450, -100), data_type="RGBA", name="Seam")
    L(smask.outputs["Result"], seam.inputs["Factor"])
    L(mix.outputs["Result"], seam.inputs["A"])
    L(sline.outputs["Color"], seam.inputs["B"])

    em = node(nt, "ShaderNodeEmission", (650, 200))
    L(seam.outputs["Result"], em.inputs["Color"])
    out = node(nt, "ShaderNodeOutputMaterial", (850, 200))
    L(em.outputs[0], out.inputs["Surface"])
    return mat


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "PillMirror"

    # 9 x 16 plane with object coords = world units, centred on the fold
    me = bpy.data.meshes.new("Field")
    me.from_pydata([(-4.5, -8, 0), (4.5, -8, 0), (4.5, 8, 0), (-4.5, 8, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new("Field", me)
    sc.collection.objects.link(ob)
    me.materials.append(build_material())

    cam_d = bpy.data.cameras.new("Cam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = 16
    cam = bpy.data.objects.new("Cam", cam_d)
    cam.location = (0, 0, 10)
    sc.collection.objects.link(cam)
    sc.camera = cam

    w = bpy.data.worlds.new("Black")
    w.color = (0, 0, 0)
    sc.world = w

    r = sc.render
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            r.engine = eng
            break
        except TypeError:
            pass
    sc.eevee.taa_render_samples = 16
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1080, 1920, 100
    r.fps = P["fps"]
    sc.frame_start, sc.frame_end = 1, P["frames"]
    sc.view_settings.view_transform = "Standard"
    sc["params"] = repr(P)


if __name__ == "__main__":
    out = parse_args()
    build()
    if out:
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print("saved", out, flush=True)
    sys.stdout.flush()
    os._exit(0)
