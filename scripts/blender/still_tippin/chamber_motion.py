"""STILL TIPPIN — THE CHAMBER, motion test 1: stretch = light + contour colour bands (2026-11-13).
Run after exec(chamber.py).

Nick: membrane chosen. "Almost topographic psychedelic colours shifting" — filled colour bands,
soft edges, enough that you can't track one ("you have to take it in as a whole").

  breath     GN on the Chamber: radius scaled by s(θ, y) = 1 + open·w(y) + vowel lobes.
             open / lobes come from a fake formant-like filter: 8th-note targets at 140 BPM
             through a spring (overshoot = the bounce). stretch = s - 1 stored for the shader.
  bands      phase = stretch·K + crawling 4D noise + slow drift; colour = cyclic palette ramp
             with plateaus (filled bands, soft edges). Stretch pushes bands; noise never stops.
  light      emission through the wall ∝ max(stretch, 0): the wall glows where it is thin.
"""
import bpy, math, random

BRE = dict(
    open_amp=0.32,     # swell at full open
    lobe_amp=0.14,     # vowel lobe depth
    stiff=180.0,       # spring stiffness (1/s²)
    damp=9.0,          # spring damping (1/s) — low = more overshoot, bouncier
    band_k=7.0,        # bands per unit stretch
    noise_k=5.0,       # bands from the crawl field
    crawl=0.35,        # crawl speed
    drift=0.06,        # palette steps per second (slow — "look back and it's changed")
    glow=9.0,          # emission per unit stretch
)

# filled bands: each colour holds a plateau, soft blend between (Rust + muted plum, brief palettes)
BANDS = ["#8A5A3D", "#A6633D", "#C7BBA6", "#6B2E87", "#2D0546", "#6F4E3A"]


def _gn(ob):
    nt = bpy.data.node_groups.get("ChamberBreath")
    if nt:
        bpy.data.node_groups.remove(nt)
    nt = bpy.data.node_groups.new("ChamberBreath", "GeometryNodeTree")
    nt.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    nt.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, Lk = nt.nodes.new, nt.links.new
    gi, go = N("NodeGroupInput"), N("NodeGroupOutput")
    val = {}
    for k in ("Open", "A2", "A3", "Phi"):
        v = N("ShaderNodeValue")
        v.name = v.label = k
        val[k] = v.outputs[0]

    def M(op, a, b=None):
        m = N("ShaderNodeMath")
        m.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                Lk(x, m.inputs[i])
        return m.outputs[0]

    pos = N("GeometryNodeInputPosition")
    sep = N("ShaderNodeSeparateXYZ")
    Lk(pos.outputs[0], sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    th = M("ARCTAN2", z, x)
    # w(y): swell weighted toward the near chamber, still present far down
    wy = M("ADD", 0.55, M("MULTIPLY", 0.45, M("EXPONENT", M("MULTIPLY", -1.0,
           M("POWER", M("DIVIDE", M("SUBTRACT", y, 3.5), 2.5), 2.0)))))
    swell = M("MULTIPLY", val["Open"], wy)
    l2 = M("MULTIPLY", val["A2"], M("COSINE", M("ADD", M("MULTIPLY", th, 2.0), val["Phi"])))
    l3 = M("MULTIPLY", val["A3"], M("COSINE", M("SUBTRACT", M("MULTIPLY", th, 3.0), val["Phi"])))
    stretch = M("ADD", swell, M("ADD", l2, l3))
    s = M("ADD", 1.0, stretch)
    cx = N("ShaderNodeCombineXYZ")
    Lk(M("MULTIPLY", x, s), cx.inputs["X"])
    Lk(y, cx.inputs["Y"])
    Lk(M("MULTIPLY", z, s), cx.inputs["Z"])
    sp = N("GeometryNodeSetPosition")
    Lk(gi.outputs[0], sp.inputs["Geometry"])
    Lk(cx.outputs[0], sp.inputs["Position"])
    st = N("GeometryNodeStoreNamedAttribute")
    st.data_type = "FLOAT"
    st.domain = "POINT"
    st.inputs["Name"].default_value = "stretch"
    Lk(sp.outputs[0], st.inputs["Geometry"])
    Lk(stretch, st.inputs["Value"])
    Lk(st.outputs[0], go.inputs[0])
    md = ob.modifiers.get("Breath") or ob.modifiers.new("Breath", "NODES")
    md.node_group = nt
    return nt


def _band_mat(p):
    m = bpy.data.materials.new("MembraneBands")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, Lk = nt.nodes.new, nt.links.new
    out = N("ShaderNodeOutputMaterial")

    def M(op, a, b=None):
        mm = N("ShaderNodeMath")
        mm.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                mm.inputs[i].default_value = x
            else:
                Lk(x, mm.inputs[i])
        return mm.outputs[0]

    at = N("ShaderNodeAttribute")
    at.attribute_name = "stretch"
    tval = N("ShaderNodeValue"); tval.name = tval.label = "Time"
    dval = N("ShaderNodeValue"); dval.name = dval.label = "Drift"
    # crawl field: 4D noise, slid along the tube, stretched along it (fibres not rings)
    tc = N("ShaderNodeTexCoord")
    mp = N("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.4, 0.45, 1.4)
    Lk(tc.outputs["Object"], mp.inputs["Vector"])
    nz = N("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 2.0
    nz.inputs["Distortion"].default_value = 0.6
    Lk(mp.outputs[0], nz.inputs["Vector"])
    Lk(M("MULTIPLY", tval.outputs[0], p["crawl"]), nz.inputs["W"])
    phase = M("ADD", M("ADD", M("MULTIPLY", at.outputs["Fac"], p["band_k"]),
                       M("MULTIPLY", nz.outputs["Fac"], p["noise_k"])), dval.outputs[0])
    fr = M("FRACT", phase)
    ramp = N("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "EASE"
    els = ramp.color_ramp.elements
    n = len(BANDS)
    stops = []
    for i, h in enumerate(BANDS + [BANDS[0]]):
        c0 = i / n
        stops.append((max(0.0, c0 - 0.03), h))
        stops.append((min(1.0, c0 + 0.03), h))
    stops = [s for s in stops if 0.0 <= s[0] <= 1.0]
    els[0].position, els[0].color = stops[0][0], _hex(stops[0][1])
    els[1].position, els[1].color = stops[-1][0], _hex(stops[-1][1])
    for pos_, h in stops[1:-1]:
        e = els.new(pos_)
        e.color = _hex(h)
    Lk(fr, ramp.inputs["Fac"])
    bs = N("ShaderNodeBsdfPrincipled")
    Lk(ramp.outputs["Color"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.3
    bs.inputs["Subsurface Weight"].default_value = 1.0
    bs.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.18)
    bs.inputs["Subsurface Scale"].default_value = 0.25
    bs.inputs["Coat Weight"].default_value = 0.5
    bs.inputs["Coat Roughness"].default_value = 0.08
    # light through the wall where it is stretched thin
    em = N("ShaderNodeEmission")
    Lk(ramp.outputs["Color"], em.inputs["Color"])
    Lk(M("MULTIPLY", M("MAXIMUM", at.outputs["Fac"], 0.0), p["glow"]), em.inputs["Strength"])
    add = N("ShaderNodeAddShader")
    Lk(bs.outputs[0], add.inputs[0])
    Lk(em.outputs[0], add.inputs[1])
    Lk(add.outputs[0], out.inputs["Surface"])
    return m


def _filter_curve(seconds, fps, bpm=140, seed=3):
    """Fake formant-like filter: a target per 8th note (open amount + vowel), through a
    damped spring so every move overshoots and wobbles — the bounce."""
    rnd = random.Random(seed)
    step = 60.0 / bpm / 2
    n = int(seconds * fps)
    tgt_open, tgt_a2, tgt_a3, tgt_phi = [], [], [], []
    k = 0
    while k * step < seconds + step:
        # talk in phrases: 2 bars talking, then a held breath for 2 beats
        tgt_open.append(rnd.choice((0.05, 0.3, 0.6, 0.9, 1.0, 0.15)))
        tgt_a2.append(rnd.uniform(-1, 1))
        tgt_a3.append(rnd.uniform(-1, 1))
        tgt_phi.append(rnd.uniform(0, 6.28))
        k += 1
    out = {"Open": [], "A2": [], "A3": [], "Phi": []}
    st = {kk: [0.0, 0.0] for kk in out}
    dt = 1.0 / fps
    for f in range(n):
        t = f * dt
        i = int(t / step)
        tg = {"Open": tgt_open[i], "A2": tgt_a2[i], "A3": tgt_a3[i], "Phi": tgt_phi[i]}
        for kk in out:
            x, v = st[kk]
            for _ in range(4):           # substeps
                h = dt / 4
                a = BRE["stiff"] * (tg[kk] - x) - BRE["damp"] * v
                v += a * h
                x += v * h
            st[kk] = [x, v]
            out[kk].append(x)
    return out


def build_motion(seconds=8.0, fps=30):
    p = dict(BRE)
    sc = bpy.context.scene
    sc.render.fps = fps
    build("membrane")                    # chamber.py
    ob = bpy.data.objects["Chamber"]
    gn = _gn(ob)
    ob.data.materials.clear()
    mat = _band_mat(p)
    ob.data.materials.append(mat)
    curves = _filter_curve(seconds, fps)
    n = len(curves["Open"])
    sc.frame_start, sc.frame_end = 1, n
    scale = {"Open": p["open_amp"], "A2": p["lobe_amp"], "A3": p["lobe_amp"] * 0.6, "Phi": 1.0}
    for f in range(n):
        for kk in ("Open", "A2", "A3", "Phi"):
            sock = gn.nodes[kk].outputs[0]
            sock.default_value = curves[kk][f] * scale[kk]
            sock.keyframe_insert("default_value", frame=f + 1)
        t = f / fps
        for kk, v in (("Time", t), ("Drift", p["drift"] * t)):
            sock = mat.node_tree.nodes[kk].outputs[0]
            sock.default_value = v
            sock.keyframe_insert("default_value", frame=f + 1)
    # outside lights breathe with the opening too
    for o in bpy.data.collections["STILL_TIPPIN"].objects:
        if o.name.startswith("Out"):
            for f in range(n):
                o.data.energy = 60 + 400 * max(0.0, curves["Open"][f])
                o.data.keyframe_insert("energy", frame=f + 1)
    print("chamber motion:", n, "frames")
