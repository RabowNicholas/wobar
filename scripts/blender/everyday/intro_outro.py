"""Everyday intro + outro. Run inside everyday_tunnel_v1.blend after break_chaos.py. Idempotent.

INTRO (bars 1-16): frame 1 is black with only the vanishing light, which breathes with the sub.
  The music builds the tunnel: each hat switches on single shapes (reveal_h), each kick/snare
  switches on whole rings (reveal_r). Shapes pop in (scale overshoot + a warm flash) as they appear.
  Complete by bar 15; held through the 15-16 silence; the drop lands on a finished tunnel.
  The tunnel keeps its gentle intro travel throughout (Nick: the intro should have light motion).
OUTRO (bars 113-128): the camera backs straight out of the tunnel mouth (outside 0->1, bars 113-125),
  so for the first time the tunnel is seen whole, as one object in black around the light. The same
  reveal runs in reverse, hit by hit (the 119-120 and 127-128 kick fills knock out big pieces), until
  the light is alone. Cut to black on the last kick (cut, frame 6573).
Why (2026-11-08): start and end on the same image, the light alone, seen from a different place:
the song changed where the listener stands. Chosen over turning around / reversing travel.
"""
import bpy
import numpy as np

BPM, FPS, N = 140, 30, 6583
TUNE = dict(reveal_soft=0.005, pop_amp=0.6, pop_glow=6.0, light_sub=0.8, outside_dist=45.0)
LAST_KICK = 6573          # frame of the final kick (from everyday_curves.json kick_idx)
CLEAR_KICK = 6559         # the kick that removes the last pieces; light alone until LAST_KICK


def bar_frame(b):
    return round((b - 1) * 60 / BPM * 4 * FPS) + 1


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


c = bpy.data.objects["WOBAR_CTRL"]
ad = c.animation_data
act, slot = ad.action, ad.action_slot
fcs = {fc.data_path: fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves}
fr = np.arange(1, N + 1).astype(float)
F15, F17, F113, F125 = bar_frame(15), bar_frame(17), bar_frame(113), bar_frame(125)


def ch(name):
    return np.array([fcs[f'["{name}"]'].evaluate(f) for f in fr])


hats = ch("hat_step")
drums = ch("kick_shove") + ch("snare_step")


def norm(x, a, b):
    i, j = int(a) - 1, int(b) - 1
    return np.clip((x - x[i]) / max(1e-9, x[j] - x[i]), 0, 1)


ease_end = CLEAR_KICK + 9                      # kick ease is 0.3 s
rev_r = np.ones(N); rev_h = np.ones(N)
intro = fr < F15
rev_r[intro] = norm(drums, 1, F15 - 1)[intro]
rev_h[intro] = 0.6 * norm(hats, 1, F15 - 1)[intro]
outro = fr >= F113
rev_r[outro] = (1 - norm(drums, F113, ease_end))[outro]
rev_h[outro] = (1 - norm(hats, F113, ease_end))[outro]
rev_r[fr >= ease_end] = 0; rev_h[fr >= ease_end] = 0
intro_mask = 1 - smooth((fr - F17) / (60 / BPM * FPS))
outside = smooth((fr - F113) / (F125 - F113))
cut = (fr >= LAST_KICK).astype(float)

for name, arr in (("reveal_r", rev_r), ("reveal_h", rev_h), ("intro_mask", intro_mask),
                  ("outside", outside), ("cut", cut)):
    c[name] = 0.0
    fc = act.fcurve_ensure_for_datablock(c, f'["{name}"]')
    fc.keyframe_points.clear()
    fc.keyframe_points.add(N)
    co = np.empty(2 * N)
    co[0::2], co[1::2] = fr, arr
    fc.keyframe_points.foreach_set("co", co)
    if name == "cut":
        fc.keyframe_points.foreach_set("interpolation", [0] * N)   # CONSTANT: a hard cut, no motion-blur smear
    fc.update()
ad.action = None; ad.action = act; ad.action_slot = slot     # FOOTGUNS V-11
for k, v in TUNE.items():
    if k not in c: c[k] = v

# ---------- geometry nodes: reveal stage ----------
ng = bpy.data.node_groups["TunnelWalls_AV"]
N_ = ng.nodes
if ng.animation_data:
    for d in list(ng.animation_data.drivers):
        if d.data_path.startswith('nodes["Reveal'):
            ng.animation_data.drivers.remove(d)
for n in [n for n in N_ if n.name.startswith("Reveal")]:
    N_.remove(n)
L = ng.links.new
shapes, chaos, cube_scale, ppr = N_["Shapes On Walls"], N_["Chaos Offset"], N_["Cube Scale"], N_["Points Per Ring"]
x0, y0 = chaos.location.x, chaos.location.y + 600


def node(t, name, dx, dy, **kw):
    n = N_.new(t); n.name = n.label = name; n.location = (x0 + dx, y0 + dy)
    for a, v in kw.items():
        setattr(n, a, v)
    return n


def math(op, name, dx, dy, a=None, b=None):
    n = node("ShaderNodeMath", name, dx, dy, operation=op)
    for sock, src in ((n.inputs[0], a), (n.inputs[1], b)):
        if isinstance(src, (int, float)):
            sock.default_value = src
        elif src is not None:
            L(src, sock)
    return n


vR, vH, vS = (node("ShaderNodeValue", n, -900, -i * 120) for i, n in enumerate(("Reveal R", "Reveal H", "Reveal Soft")))
vP = node("ShaderNodeValue", "Reveal Pop Amp", -900, -360)
idx = node("GeometryNodeInputIndex", "Reveal Index", -900, 200)
ring = math("DIVIDE", "Reveal Ring Div", -750, 200, idx.outputs[0], ppr.outputs["Point Count"])
ringf = math("FLOOR", "Reveal Ring", -600, 200, ring.outputs[0])
kr = node("FunctionNodeRandomValue", "Reveal Ring Key", -450, 200, data_type="FLOAT")
L(ringf.outputs[0], kr.inputs["ID"]); kr.inputs["Seed"].default_value = 73
ks = node("FunctionNodeRandomValue", "Reveal Shape Key", -450, 0, data_type="FLOAT")
L(idx.outputs[0], ks.inputs["ID"]); ks.inputs["Seed"].default_value = 71
# shapes switch on by key: t = clamp((reveal - key) / soft)
dr = math("SUBTRACT", "Reveal dR", -250, 200, vR.outputs[0], kr.outputs[0])
dh = math("SUBTRACT", "Reveal dH", -250, 0, vH.outputs[0], ks.outputs[0])
tr = math("DIVIDE", "Reveal tR", -100, 200, dr.outputs[0], vS.outputs[0]); tr.use_clamp = True
th = math("DIVIDE", "Reveal tH", -100, 0, dh.outputs[0], vS.outputs[0]); th.use_clamp = True
t = math("MAXIMUM", "Reveal t", 50, 100, tr.outputs[0], th.outputs[0])
# pop = sin(pi t): non-zero only while a shape is appearing / disappearing
pt = math("MULTIPLY", "Reveal pi t", 200, 0, t.outputs[0], 3.14159265)
pop = math("SINE", "Reveal Pop", 350, 0, pt.outputs[0])
popa = math("MULTIPLY", "Reveal Pop Scaled", 500, 0, pop.outputs[0], vP.outputs[0])
popk = math("ADD", "Reveal Pop Gain", 650, 0, popa.outputs[0], 1.0)
sc_ = math("MULTIPLY", "Reveal Scale", 800, 100, t.outputs[0], popk.outputs[0])
vis = math("GREATER_THAN", "Reveal Visible", 800, 250, t.outputs[0], 0.0)
store = node("GeometryNodeStoreNamedAttribute", "Reveal Store Pop", 950, -300, data_type="FLOAT", domain="POINT")
store.inputs["Name"].default_value = "pop"
L(chaos.outputs[0], store.inputs["Geometry"]); L(pop.outputs[0], store.inputs["Value"])
L(store.outputs[0], shapes.inputs["Points"])
vs = node("ShaderNodeVectorMath", "Reveal Scale Vec", 950, 100, operation="SCALE")
L(cube_scale.outputs[0], vs.inputs[0]); L(sc_.outputs[0], vs.inputs["Scale"])
L(vs.outputs[0], shapes.inputs["Scale"]); L(vis.outputs[0], shapes.inputs["Selection"])


def var(d, name):
    if name not in [v.name for v in d.driver.variables]:
        v = d.driver.variables.new(); v.name = name; v.type = "SINGLE_PROP"
        v.targets[0].id = c; v.targets[0].data_path = f'["{name}"]'


def drive(idb, path, expr, names, index=None):
    try:
        idb.driver_remove(path) if index is None else idb.driver_remove(path, index)
    except TypeError:
        pass
    d = idb.driver_add(path) if index is None else idb.driver_add(path, index)
    d.driver.type = "SCRIPTED"
    for n in names:
        var(d, n)
    d.driver.expression = expr
    d.driver.is_valid = True
    return d


V = 'nodes["{}"].outputs[0].default_value'
drive(ng, V.format("Reveal R"), "reveal_r", ("reveal_r",))
drive(ng, V.format("Reveal H"), "reveal_h", ("reveal_h",))
drive(ng, V.format("Reveal Soft"), "reveal_soft", ("reveal_soft",))
drive(ng, V.format("Reveal Pop Amp"), "pop_amp", ("pop_amp",))

# ---------- material: warm flash on appearing shapes; cut ----------
nt = bpy.data.materials["ColorGlass"].node_tree
for n in [n for n in nt.nodes if n.name.startswith("Reveal")]:
    nt.nodes.remove(n)
vm = nt.nodes["Void Mix"]
src = next(l.from_socket for l in nt.links if l.to_node == vm and l.to_socket == vm.inputs[1])
at = nt.nodes.new("ShaderNodeAttribute"); at.name = at.label = "Reveal Pop Attr"
at.attribute_type = "INSTANCER"; at.attribute_name = "pop"
pg = nt.nodes.new("ShaderNodeValue"); pg.name = pg.label = "Reveal Pop Glow"
mul = nt.nodes.new("ShaderNodeMath"); mul.name = mul.label = "Reveal Flash Strength"; mul.operation = "MULTIPLY"
em = nt.nodes.new("ShaderNodeEmission"); em.name = em.label = "Reveal Flash"
em.inputs["Color"].default_value = (1.0, 0.97, 0.92, 1)
add = nt.nodes.new("ShaderNodeAddShader"); add.name = add.label = "Reveal Add"
for i, n in enumerate((at, pg, mul, em, add)):
    n.location = (vm.location.x - 900 + i * 170, vm.location.y - 350)
nt.links.new(at.outputs["Fac"], mul.inputs[0]); nt.links.new(pg.outputs[0], mul.inputs[1])
nt.links.new(mul.outputs[0], em.inputs["Strength"])
nt.links.new(src, add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1]); nt.links.new(add.outputs[0], vm.inputs[1])
drive(nt, V.format("Reveal Pop Glow"), "pop_glow", ("pop_glow",))
drive(nt, 'nodes["Void Mix"].inputs[0].default_value', "min(1.0, void * void_on + cut)", ("void", "void_on", "cut"))
gf = next(d for d in nt.animation_data.drivers if d.data_path == V.format("GlintFocus"))
var(gf, "outside_dist"); var(gf, "outside")
gf.driver.expression = "x + outside_dist * outside"

# ---------- lights: intro breath on the sub, cut ----------
light = bpy.data.lights[bpy.data.objects["VanishingLight"].data.name]
drive(light, "energy", "71308.96 * (light_floor + light_depth * snare) * (1.0 + light_sub * low * intro_mask) * (1.0 - cut)",
      ("light_floor", "light_depth", "snare", "light_sub", "low", "intro_mask", "cut"))
orb = bpy.data.materials["OrbGlow"].node_tree
drive(orb, 'nodes["Emission"].inputs[1].default_value',
      "30.654 * (light_floor + light_depth * snare) * (1.0 + light_sub * low * intro_mask) * (1.0 - cut)",
      ("light_floor", "light_depth", "snare", "light_sub", "low", "intro_mask", "cut"))

# ---------- camera: back out of the mouth ----------
cam = bpy.context.scene.camera
drive(cam, "location", "-outside_dist * outside", ("outside_dist", "outside"), index=1)
drive(cam.data, "dof.focus_distance", "16.0 + outside_dist * outside", ("outside_dist", "outside"))

c.update_tag(); ng.update_tag(); nt.update_tag(); bpy.context.view_layer.update()
bad = [d.data_path for idb in (nt, ng, orb, light, cam, cam.data) if idb.animation_data
       for d in idb.animation_data.drivers if not d.driver.is_valid]
print("intro_outro:", F15, F17, F113, F125, "invalid", bad)
