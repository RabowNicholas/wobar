"""STILL TIPPIN — Candy Coat, step 2: the panel becomes liquid.

A heightfield wave simulation on the Paint surface (GN simulation zone). Each point carries
height h and velocity v; a Repeat zone integrates the wave equation with Blur Attribute as the
neighbour average (laplacian ≈ blur(h) - h). Kicks drop impulses into v; rings travel across
the panel, reflect, interfere and damp back to the glass-smooth coat. The sub adds a slow
whole-body swell on top.

Controls live on the TIPPIN_CTRL empty (custom props, driven into the modifier):
    kick_hit   1 on a kick's onset frame, else 0 (CONSTANT keys)
    kick_x/y   where the hit lands (world XY)
    sub        0-1 low-end envelope

Sim zones go stale silently (BUILD_LOG §1): run cache_reset() after any change here.
    exec(open(PATH).read()); build(); test_pattern()
"""
import bpy, math

L = dict(
    iters=6,          # wave sub-steps per frame — sets how fast rings travel
    speed=0.45,       # wave stiffness per sub-step (stable below 1)
    damp=0.992,       # per sub-step velocity damping — how long the liquid rings
    impulse=0.035,     # kick strength (velocity, m per sub-step)
    radius=0.45,      # impact footprint, metres
    restore=0.004,    # spring back toward the rest coat per sub-step (surface tension)
    swell=0.35,       # sub swell amplitude, metres
    swell_scale=0.12, # sub swell spatial frequency
    swell_rate=0.25,  # sub swell drift speed
    # continuous version (2026-11-12): kicks fire plane waves from a line behind the camera
    # so wave trains roll forward in step; a fine flow texture streams toward the core always
    line=True,        # True: line source across X at KickY; False: point hits (first test)
    flow_amp=0.05,    # streaming surface texture height, metres
    flow_scale=0.9,   # its spatial frequency (wavelength ~1 m, >= 4x mesh spacing)
    flow_speed=2.2,   # m/s toward the core
    absorb_y=-4.5,    # waves are soaked up behind this line (no echo off the near edge)
)

TREE = "TippinLiquid"


def _ctrl():
    c = bpy.data.objects.get("TIPPIN_CTRL")
    if c is None:
        c = bpy.data.objects.new("TIPPIN_CTRL", None)
        c.empty_display_type = "PLAIN_AXES"
        c.location = (0, -6, 0)
        bpy.data.collections["STILL_TIPPIN"].objects.link(c)
    for k, v in dict(kick_hit=0.0, kick_x=0.0, kick_y=7.0, sub=0.0).items():
        if k not in c:
            c[k] = v
    return c


def _tree(p):
    nt = bpy.data.node_groups.get(TREE)
    if nt:
        bpy.data.node_groups.remove(nt)
    nt = bpy.data.node_groups.new(TREE, "GeometryNodeTree")
    I = nt.interface
    I.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    I.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    for name, val in (("Impulse", p["impulse"]), ("Restore", p["restore"]), ("Radius", p["radius"]),
                      ("Speed", p["speed"]), ("Damp", p["damp"]),
                      ("Swell", p["swell"]), ("SwellScale", p["swell_scale"]),
                      ("SwellRate", p["swell_rate"]),
                      ("FlowAmp", p["flow_amp"]), ("FlowScale", p["flow_scale"]),
                      ("FlowSpeed", p["flow_speed"])):
        s = I.new_socket(name, in_out="INPUT", socket_type="NodeSocketFloat")
        s.default_value = val
    I.new_socket("Iterations", in_out="INPUT", socket_type="NodeSocketInt").default_value = p["iters"]

    N, Lk = nt.nodes.new, nt.links.new
    gi = N("NodeGroupInput")
    go = N("NodeGroupOutput")
    # audio controls: Value nodes driven from TIPPIN_CTRL (MAKYO pattern; FOOTGUNS V-2)
    ctl = {}
    for name in ("Kick", "KickX", "KickY", "Sub"):
        vn = N("ShaderNodeValue")
        vn.name = vn.label = name
        ctl[name] = vn.outputs[0]

    def math_(op, a=None, b=None):
        m = N("ShaderNodeMath")
        m.operation = op
        if a is not None:
            (Lk(a, m.inputs[0]) if not isinstance(a, (int, float)) else
             m.inputs[0].__setattr__("default_value", a))
        if b is not None:
            (Lk(b, m.inputs[1]) if not isinstance(b, (int, float)) else
             m.inputs[1].__setattr__("default_value", b))
        return m.outputs[0]

    def named(name):
        n = N("GeometryNodeInputNamedAttribute")
        n.data_type = "FLOAT"
        n.inputs["Name"].default_value = name
        return n.outputs["Attribute"]

    def store(geo, name, val):
        s = N("GeometryNodeStoreNamedAttribute")
        s.data_type = "FLOAT"
        s.domain = "POINT"
        s.inputs["Name"].default_value = name
        Lk(geo, s.inputs["Geometry"])
        Lk(val, s.inputs["Value"])
        return s.outputs["Geometry"]

    # --- simulation zone
    si = N("GeometryNodeSimulationInput")
    so = N("GeometryNodeSimulationOutput")
    si.pair_with_output(so)
    Lk(gi.outputs["Geometry"], si.inputs["Geometry"])

    # impulse into v: kick * impulse * exp(-(d/r)^2), d = XY distance to the hit
    pos = N("GeometryNodeInputPosition")
    sep = N("ShaderNodeSeparateXYZ")
    Lk(pos.outputs[0], sep.inputs[0])
    dx = math_("SUBTRACT", sep.outputs[0], ctl["KickX"])
    dy = math_("SUBTRACT", sep.outputs[1], ctl["KickY"])
    d2 = math_("ADD", math_("MULTIPLY", dx, dx), math_("MULTIPLY", dy, dy))
    r2 = math_("MULTIPLY", gi.outputs["Radius"], gi.outputs["Radius"])
    # mexican hat (1 - d²/r²)·exp(-d²/r²): zero net volume in 2D, so the hit leaves rings
    # and the surface returns, instead of the one-signed 2D Green's function's permanent hole
    if p["line"]:
        # 1D: (1 - 2q)·exp(-q), q = dy²/r² — zero net volume along Y, a clean wave front
        q = math_("DIVIDE", math_("MULTIPLY", dy, dy), r2)
        fall = math_("MULTIPLY", math_("SUBTRACT", 1.0, math_("MULTIPLY", q, 2.0)),
                     math_("EXPONENT", math_("MULTIPLY", q, -1.0)))
    else:
        q = math_("DIVIDE", d2, r2)
        fall = math_("MULTIPLY", math_("SUBTRACT", 1.0, q),
                     math_("EXPONENT", math_("MULTIPLY", q, -1.0)))
    kick = math_("MULTIPLY", math_("MULTIPLY", ctl["Kick"], gi.outputs["Impulse"]), fall)
    v_in = math_("SUBTRACT", named("v"), kick)          # down-push: a dent, like a drop hitting
    g = store(si.outputs["Geometry"], "v", v_in)

    # --- repeat zone: the wave equation
    ri = N("GeometryNodeRepeatInput")
    ro = N("GeometryNodeRepeatOutput")
    ri.pair_with_output(ro)
    Lk(gi.outputs["Iterations"], ri.inputs["Iterations"])
    Lk(g, ri.inputs["Geometry"])
    blur = N("GeometryNodeBlurAttribute")
    blur.data_type = "FLOAT"
    blur.inputs["Iterations"].default_value = 1
    h = named("h")
    Lk(h, blur.inputs["Value"])
    lap = math_("SUBTRACT", blur.outputs["Value"], h)
    force = math_("SUBTRACT", math_("MULTIPLY", lap, gi.outputs["Speed"]),
                  math_("MULTIPLY", h, gi.outputs["Restore"]))
    # absorbing strip near the camera-side edge: damping ramps up behind absorb_y
    ps2 = N("ShaderNodeSeparateXYZ")
    Lk(N("GeometryNodeInputPosition").outputs[0], ps2.inputs[0])
    edge = N("ShaderNodeMapRange")
    edge.inputs["From Min"].default_value = p["absorb_y"] - 3.0
    edge.inputs["From Max"].default_value = p["absorb_y"]
    edge.inputs["To Min"].default_value = 0.85
    edge.inputs["To Max"].default_value = 1.0
    Lk(ps2.outputs[1], edge.inputs["Value"])
    dampf = math_("MULTIPLY", gi.outputs["Damp"], edge.outputs[0])
    v_new = math_("MULTIPLY", math_("ADD", named("v"), force), dampf)
    g2 = store(ri.outputs["Geometry"], "v", v_new)
    h_new = math_("ADD", named("h"), named("v"))          # reads the v just stored
    g3 = store(g2, "h", h_new)
    Lk(g3, ro.inputs["Geometry"])
    Lk(ro.outputs["Geometry"], so.inputs["Geometry"])

    # --- after the zone: displace by h + sub swell
    t = N("GeometryNodeInputSceneTime")
    nz = N("ShaderNodeTexNoise")
    nz.noise_dimensions = "4D"
    nz.inputs["Detail"].default_value = 0.0
    Lk(math_("MULTIPLY", t.outputs["Seconds"], gi.outputs["SwellRate"]), nz.inputs["W"])
    Lk(gi.outputs["SwellScale"], nz.inputs["Scale"])
    sw = math_("MULTIPLY", math_("SUBTRACT", nz.outputs["Fac"], 0.5),
               math_("MULTIPLY", gi.outputs["Swell"], ctl["Sub"]))
    # flow: fine noise advected toward the core — the paint is always running
    ps3 = N("ShaderNodeSeparateXYZ")
    Lk(N("GeometryNodeInputPosition").outputs[0], ps3.inputs[0])
    adv = math_("SUBTRACT", ps3.outputs[1], math_("MULTIPLY", t.outputs["Seconds"], gi.outputs["FlowSpeed"]))
    fv = N("ShaderNodeCombineXYZ")
    Lk(math_("MULTIPLY", ps3.outputs[0], 1.6), fv.inputs["X"])   # elongated across: ripple lines
    Lk(adv, fv.inputs["Y"])
    fn = N("ShaderNodeTexNoise")
    fn.noise_dimensions = "4D"
    fn.inputs["Detail"].default_value = 1.0
    Lk(fv.outputs[0], fn.inputs["Vector"])
    Lk(gi.outputs["FlowScale"], fn.inputs["Scale"])
    Lk(math_("MULTIPLY", t.outputs["Seconds"], 0.15), fn.inputs["W"])
    flow = math_("MULTIPLY", math_("SUBTRACT", fn.outputs["Fac"], 0.5), gi.outputs["FlowAmp"])
    dz = math_("ADD", math_("ADD", named("h"), sw), flow)
    cx = N("ShaderNodeCombineXYZ")
    Lk(dz, cx.inputs["Z"])
    sp = N("GeometryNodeSetPosition")
    Lk(so.outputs["Geometry"], sp.inputs["Geometry"])
    Lk(cx.outputs[0], sp.inputs["Offset"])
    ss = N("GeometryNodeSetShadeSmooth")
    Lk(sp.outputs[0], ss.inputs["Geometry"])
    Lk(ss.outputs[0], go.inputs["Geometry"])
    return nt


def build(**overrides):
    p = dict(L, **overrides)
    ob = bpy.data.objects["Paint"]
    ctrl = _ctrl()
    nt = _tree(p)
    md = ob.modifiers.get("Liquid") or ob.modifiers.new("Liquid", "NODES")
    md.node_group = nt
    # set every input explicitly (BUILD_LOG: new sockets on a used group arrive as 0)
    for item in nt.interface.items_tree:
        if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.socket_type != "NodeSocketGeometry":
            getattr(md.properties.inputs, item.identifier).value = item.default_value
    # drivers: ctrl props -> Value nodes in the tree
    for node, prop in (("Kick", "kick_hit"), ("KickX", "kick_x"), ("KickY", "kick_y"), ("Sub", "sub")):
        fc = nt.nodes[node].outputs[0].driver_add("default_value")
        dr = fc.driver
        dr.type = "SCRIPTED"
        v = dr.variables.new()
        v.name = "x"
        v.targets[0].id = ctrl
        v.targets[0].data_path = f'["{prop}"]'
        dr.expression = "x"
    print("liquid built", p)


def test_pattern(seconds=8.0, fps=30, bpm=140, line=True, emitter_y=-2.5):
    """Fake controls for judging the liquid before the real audio: half-time kick on 1 and the
    'and' of 2 at 140, hits wandering along the crown, sub ramping in from bar 2."""
    import random
    sc = bpy.context.scene
    sc.render.fps = fps
    n = int(seconds * fps)
    sc.frame_start, sc.frame_end = 1, n
    c = _ctrl()
    ad = c.animation_data or c.animation_data_create()
    if ad.action:
        bpy.data.actions.remove(ad.action)
    beat = 60.0 / bpm
    hits = []
    t = 0.0
    bar = beat * 4
    while t < seconds:
        for off in (0.0, beat * 2.5):     # half-time: 1, and-of-3 (bar of 4 beats)
            if t + off < seconds:
                hits.append(t + off)
        t += bar
    rnd = random.Random(7)
    for f in range(1, n + 1):
        c["kick_hit"] = 0.0
        c.keyframe_insert('["kick_hit"]', frame=f)
        c["sub"] = min(1.0, max(0.0, ((f - 1) / fps - bar) / bar))
        c.keyframe_insert('["sub"]', frame=f)
    for ht in hits:
        f = 1 + int(round(ht * fps))
        c["kick_hit"] = 1.0
        c.keyframe_insert('["kick_hit"]', frame=f)
        if line:
            c["kick_x"], c["kick_y"] = 0.0, emitter_y
        else:
            # on the lit crown near camera: ripples only read where they bend a reflection
            c["kick_x"] = rnd.uniform(-1.4, 0.6)
            c["kick_y"] = rnd.uniform(0.5, 6.0)
        c.keyframe_insert('["kick_x"]', frame=f)
        c.keyframe_insert('["kick_y"]', frame=f)
    act = c.animation_data.action
    for bag in (s.channelbag(c.animation_data.action_slot) for l in act.layers for s in l.strips):
        for fc in bag.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"
    print("test pattern:", len(hits), "kicks over", n, "frames")



def cache_reset():
    ob = bpy.data.objects["Paint"]
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.simulation_nodes_cache_delete(selected=True)
    bpy.context.scene.frame_set(1)
