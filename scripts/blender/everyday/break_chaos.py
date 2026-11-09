"""Everyday break (bars 49-64): the form wanders, breaks shape, goes chaotic, then snaps back into
formation on the drop 2 downbeat. Run inside everyday_tunnel_v1.blend after break_void.py
(it reuses brk / brk_acc for the travel hold). Idempotent.

Three layers, each a baked 0-1 curve on WOBAR_CTRL, scaled by a tunable amplitude:
  c_wander   49->   the tunnel snakes: every ring moves together on a slow noise along the axis
  c_shape    53->   rings deform: a 3D noise field pushes shapes off their rings
  c_scatter  61->   shapes scatter (random direction per shape) and tumble on random axes
chaos_t evolves the noise: a slow base drift, plus a jolt on every snare and kick in the break;
it almost stops in 63-64 so the scatter hangs. All three snap from 1 to 0 over 3 frames ending on
the downbeat +1, overshoot to -0.12 (the pieces pass through home) and settle over 9 frames.

Colour is stored before the offset, so every shape keeps its colour while it drifts.
Supersedes the drain + void look (2026-11-08: Nick wanted the form to wander instead):
break_desat, break_dim and void_on go to 0, break_hold to 0.5.
"""
import bpy
import numpy as np

BPM, FPS, N = 140, 30, 6583
TUNE = dict(wander_amp=3.0, wander_freq=0.04, shape_amp=1.6, shape_freq=0.18, scatter_amp=4.0,
            tumble_amp=3.0, chaos_rate=0.12, chaos_snare=0.35, chaos_kick=0.2)
OVERRIDE = dict(break_desat=0.0, break_dim=0.0, void_on=0.0, break_hold=0.5)


def bar_frame(b):
    return round((b - 1) * 60 / BPM * 4 * FPS) + 1


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


c = bpy.data.objects["WOBAR_CTRL"]
ad = c.animation_data
act, slot = ad.action, ad.action_slot
fcs = {fc.data_path: fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves}
F49, F53, F61, F63, F65 = (bar_frame(b) for b in (49, 53, 61, 63, 65))
fr = np.arange(1, N + 1).astype(float)


def seg(a, b):
    return smooth((fr - a) / (b - a))


wander = 0.6 * seg(F49, F53) + 0.4 * seg(F53, F61)
shape = 0.7 * seg(F53, F61) + 0.3 * seg(F61, F63)
scatter = seg(F61, F63)
# magnetic snap: 1 -> -0.12 over 3 frames (lands on downbeat +1), then settle to 0 over 9 frames
k = fr - (F65 - 2)
snap = np.where(k < 0, 1.0, np.where(k <= 3, 1 - 1.12 * smooth(k / 3), -0.12 * (1 - smooth((k - 3) / 9))))
in_break = (fr >= F49) & (fr < F65)
wander, shape, scatter = (np.where(fr < F65 - 2, x, x[int(F65) - 4] * snap) * (fr >= F49) for x in (wander, shape, scatter))


def ch(name):
    return np.array([fcs[f'["{name}"]'].evaluate(f) for f in fr])


for kk, v in TUNE.items():
    if kk not in c: c[kk] = v
for kk, v in OVERRIDE.items():
    c[kk] = v
rate = np.where((fr >= F49) & (fr < F63), c["chaos_rate"], np.where((fr >= F63) & (fr < F65), 0.015, 0.0)) / FPS
jolt = (c["chaos_snare"] * np.diff(ch("snare_step"), prepend=0) + c["chaos_kick"] * np.diff(ch("kick_shove"), prepend=0))
jolt = np.where((fr >= F49) & (fr < F63), jolt, 0.0)
chaos_t = np.cumsum(rate + jolt)

for name, arr in (("c_wander", wander), ("c_shape", shape), ("c_scatter", scatter), ("chaos_t", chaos_t)):
    c[name] = 0.0
    fc = act.fcurve_ensure_for_datablock(c, f'["{name}"]')
    fc.keyframe_points.clear()
    fc.keyframe_points.add(N)
    co = np.empty(2 * N)
    co[0::2], co[1::2] = fr, arr
    fc.keyframe_points.foreach_set("co", co)
    fc.update()
ad.action = None; ad.action = act; ad.action_slot = slot     # FOOTGUNS V-11

# ---------- geometry nodes: a Chaos Offset stage between Store Glint and Shapes On Walls ----------
ng = bpy.data.node_groups["TunnelWalls_AV"]
N_ = ng.nodes
if ng.animation_data:
    for d in list(ng.animation_data.drivers):
        if d.data_path.startswith('nodes["Chaos'):
            ng.animation_data.drivers.remove(d)
for n in [n for n in N_ if n.name.startswith("Chaos")]:
    N_.remove(n)
L = ng.links.new
glint, shapes, cube_rot = N_["Store Glint"], N_["Shapes On Walls"], N_["Cube Rotation"]
x0, y0 = glint.location.x, glint.location.y - 400


def node(t, name, dx, dy, **kw):
    n = N_.new(t); n.name = n.label = name; n.location = (x0 + dx, y0 + dy)
    for a, v in kw.items():
        setattr(n, a, v)
    return n


def val(name, dx, dy):
    return node("ShaderNodeValue", name, dx, dy)


vW, vS, vX, vT, vTu = (val(n, -800, -i * 120) for i, n in enumerate(
    ("Chaos Wander", "Chaos Shape", "Chaos Scatter", "Chaos Time", "Chaos Tumble")))
vWf, vSf = val("Chaos Wander Freq", -800, -600), val("Chaos Shape Freq", -800, -720)

pos = node("GeometryNodeInputPosition", "Chaos Pos", -600, 200)
sep = node("ShaderNodeSeparateXYZ", "Chaos Sep", -450, 200)
L(pos.outputs[0], sep.inputs[0])
# wander: noise of depth only -> whole rings move together
wy = node("ShaderNodeMath", "Chaos Wander Y", -300, 200, operation="MULTIPLY")
L(sep.outputs["Y"], wy.inputs[0]); L(vWf.outputs[0], wy.inputs[1])
wvec = node("ShaderNodeCombineXYZ", "Chaos Wander Vec", -150, 200)
L(wy.outputs[0], wvec.inputs["Y"])
wn = node("ShaderNodeTexNoise", "Chaos Wander Noise", 0, 200, noise_dimensions="4D")
L(wvec.outputs[0], wn.inputs["Vector"]); L(vT.outputs[0], wn.inputs["W"])
wn.inputs["Scale"].default_value = 1.0; wn.inputs["Detail"].default_value = 0.0
# depth weight: rings within ~4 units of the camera stay centred
dw = node("ShaderNodeMapRange", "Chaos Depth Weight", 0, 0)
L(sep.outputs["Y"], dw.inputs["Value"]); dw.inputs["From Min"].default_value = 2.0; dw.inputs["From Max"].default_value = 14.0
dw.interpolation_type = "SMOOTHSTEP"
# shape: 3D noise field on position
sp = node("ShaderNodeVectorMath", "Chaos Shape Pos", -150, -150, operation="SCALE")
L(pos.outputs[0], sp.inputs[0]); L(vSf.outputs[0], sp.inputs["Scale"])
sn = node("ShaderNodeTexNoise", "Chaos Shape Noise", 0, -150, noise_dimensions="4D")
L(sp.outputs[0], sn.inputs["Vector"]); L(vT.outputs[0], sn.inputs["W"]); sn.inputs["Detail"].default_value = 1.0
# scatter: random direction per shape, slowly rotating with time
rnd = node("FunctionNodeRandomValue", "Chaos Rand Dir", 0, -400, data_type="FLOAT_VECTOR")
rnd.inputs[0].default_value = (-1, -1, -1); rnd.inputs[1].default_value = (1, 1, 1)
rnd.inputs["Seed"].default_value = 41


def centred(noise_out, name, dx, dy):
    sub = node("ShaderNodeVectorMath", name, dx, dy, operation="MULTIPLY_ADD")
    L(noise_out, sub.inputs[0]); sub.inputs[1].default_value = (2, 2, 2); sub.inputs[2].default_value = (-1, -1, -1)
    return sub


wc = centred(wn.outputs["Color"], "Chaos Wander C", 200, 200)
wflat = node("ShaderNodeVectorMath", "Chaos Wander Flat", 350, 200, operation="MULTIPLY")
L(wc.outputs[0], wflat.inputs[0]); wflat.inputs[1].default_value = (1, 0, 1)      # bend sideways only
wamt = node("ShaderNodeMath", "Chaos Wander Amt", 350, 50, operation="MULTIPLY")
L(vW.outputs[0], wamt.inputs[0]); L(dw.outputs[0], wamt.inputs[1])
wfin = node("ShaderNodeVectorMath", "Chaos Wander Out", 500, 200, operation="SCALE")
L(wflat.outputs[0], wfin.inputs[0]); L(wamt.outputs[0], wfin.inputs["Scale"])
sc_ = centred(sn.outputs["Color"], "Chaos Shape C", 200, -150)
sfin = node("ShaderNodeVectorMath", "Chaos Shape Out", 500, -150, operation="SCALE")
L(sc_.outputs[0], sfin.inputs[0]); L(vS.outputs[0], sfin.inputs["Scale"])
xfin = node("ShaderNodeVectorMath", "Chaos Scatter Out", 500, -400, operation="SCALE")
L(rnd.outputs[0], xfin.inputs[0]); L(vX.outputs[0], xfin.inputs["Scale"])
add1 = node("ShaderNodeVectorMath", "Chaos Sum A", 650, 0, operation="ADD")
L(wfin.outputs[0], add1.inputs[0]); L(sfin.outputs[0], add1.inputs[1])
add2 = node("ShaderNodeVectorMath", "Chaos Sum", 800, 0, operation="ADD")
L(add1.outputs[0], add2.inputs[0]); L(xfin.outputs[0], add2.inputs[1])
setp = node("GeometryNodeSetPosition", "Chaos Offset", 950, 300)
L(glint.outputs[0], setp.inputs["Geometry"]); L(add2.outputs[0], setp.inputs["Offset"])
L(setp.outputs[0], shapes.inputs["Points"])
# tumble: extra rotation on a random axis per shape
tax = node("FunctionNodeRandomValue", "Chaos Tumble Axis", 650, -600, data_type="FLOAT_VECTOR")
tax.inputs[0].default_value = (-1, -1, -1); tax.inputs[1].default_value = (1, 1, 1); tax.inputs["Seed"].default_value = 59
tnorm = node("ShaderNodeVectorMath", "Chaos Tumble Unit", 800, -600, operation="NORMALIZE")
L(tax.outputs[0], tnorm.inputs[0])
trot = node("FunctionNodeAxisAngleToRotation", "Chaos Tumble Rot", 950, -600)
L(tnorm.outputs[0], trot.inputs["Axis"]); L(vTu.outputs[0], trot.inputs["Angle"])
rr = node("FunctionNodeRotateRotation", "Chaos Rotate", 1100, -300)
L(cube_rot.outputs[0], rr.inputs["Rotation"]); L(trot.outputs[0], rr.inputs["Rotate By"])
L(rr.outputs[0], shapes.inputs["Rotation"])


def var(d, name):
    if name not in [v.name for v in d.driver.variables]:
        v = d.driver.variables.new(); v.name = name; v.type = "SINGLE_PROP"
        v.targets[0].id = c; v.targets[0].data_path = f'["{name}"]'


def drive(idb, path, expr, names):
    try:
        idb.driver_remove(path)
    except TypeError:
        pass
    d = idb.driver_add(path)
    d.driver.type = "SCRIPTED"
    for n in names:
        var(d, n)
    d.driver.expression = expr
    d.driver.is_valid = True
    return d


V = 'nodes["{}"].outputs[0].default_value'
drive(ng, V.format("Chaos Wander"), "wander_amp * c_wander", ("wander_amp", "c_wander"))
drive(ng, V.format("Chaos Shape"), "shape_amp * c_shape", ("shape_amp", "c_shape"))
drive(ng, V.format("Chaos Scatter"), "scatter_amp * c_scatter", ("scatter_amp", "c_scatter"))
drive(ng, V.format("Chaos Time"), "chaos_t", ("chaos_t",))
drive(ng, V.format("Chaos Tumble"), "tumble_amp * c_scatter + c_shape * chaos_t", ("tumble_amp", "c_scatter", "c_shape", "chaos_t"))
drive(ng, V.format("Chaos Wander Freq"), "wander_freq", ("wander_freq",))
drive(ng, V.format("Chaos Shape Freq"), "shape_freq", ("shape_freq",))

# the void goes behind a switch (off)
nt = bpy.data.materials["ColorGlass"].node_tree
drive(nt, 'nodes["Void Mix"].inputs[0].default_value', "void * void_on", ("void", "void_on"))

c.update_tag(); ng.update_tag(); nt.update_tag(); bpy.context.view_layer.update()
bad = [d.data_path for idb in (nt, ng) for d in idb.animation_data.drivers if not d.driver.is_valid]
print("break_chaos:", F49, F53, F61, F63, F65, "chaos_t end", round(float(chaos_t[-1]), 2), "invalid", bad)
