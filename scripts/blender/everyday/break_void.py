"""Everyday break (bars 49-64): hold and drain, then a void before drop 2. Run inside
everyday_tunnel_v1.blend after the stem curves are baked. Idempotent.

  49-62  brk 0->1 over one bar: forward travel nearly stops (the tunnel breathes in place), colour drains
         (saturation and value down). The kick roll in 61-62 still jolts it forward through kick_shove.
  63-64  void 0->1 over half a beat: the glass goes black, only the vanishing light and orb remain.
  65     brk and void snap to 0 on the drop 2 downbeat.

Travel stays tunable: brk_acc is the share of travel the break removes, so
  travel = travel_rate * (low_acc - break_hold * brk_acc) + kick_push * kick_shove
Why (2026-11-08): the break was drop 1 slowed down, and bars 63-64 (no sub, one hat per bar) were
the biggest wasted moment. Chosen over a camera pull-out so drop 2 adds only one new thing (the counter-roll).
"""
import bpy
import numpy as np

BPM, FPS, N = 140, 30, 6583
TUNE = dict(break_hold=0.85, break_desat=0.6, break_dim=0.5)


def bar_frame(b):
    return round((b - 1) * 60 / BPM * 4 * FPS) + 1


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


c = bpy.data.objects["WOBAR_CTRL"]
ad = c.animation_data
act, slot = ad.action, ad.action_slot
fcs = {fc.data_path: fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves}
F49, F63, F65 = bar_frame(49), bar_frame(63), bar_frame(65)
fr = np.arange(1, N + 1)
bar, beat = 4 * 60 / BPM * FPS, 60 / BPM * FPS
brk = smooth((fr - F49) / bar) * (fr < F65)
void = smooth((fr - F63) / (beat / 2)) * (fr < F65)
low_acc = np.array([fcs['["low_acc"]'].evaluate(f) for f in fr])
speed = np.diff(low_acc, append=low_acc[-1])                   # per-frame travel increment
brk_acc = np.concatenate([[0.0], np.cumsum((speed * brk)[:-1])])

for name, arr in (("brk", brk), ("void", void), ("brk_acc", brk_acc)):
    c[name] = 0.0
    fc = act.fcurve_ensure_for_datablock(c, f'["{name}"]')
    fc.keyframe_points.clear()
    fc.keyframe_points.add(N)
    co = np.empty(2 * N)
    co[0::2], co[1::2] = fr, arr
    fc.keyframe_points.foreach_set("co", co)
    fc.update()
ad.action = None; ad.action = act; ad.action_slot = slot     # FOOTGUNS V-11
for k, v in TUNE.items():
    if k not in c: c[k] = v


def var(d, name):
    if name not in [v.name for v in d.driver.variables]:
        v = d.driver.variables.new(); v.name = name; v.type = "SINGLE_PROP"
        v.targets[0].id = c; v.targets[0].data_path = f'["{name}"]'


def drive(idb, path, expr, names, index=-1):
    try:
        idb.driver_remove(path, index)
    except TypeError:
        pass
    d = idb.driver_add(path, index) if index >= 0 else idb.driver_add(path)
    d.driver.type = "SCRIPTED"
    for n in names:
        var(d, n)
    d.driver.expression = expr
    return d


# travel: subtract the held share during the break
ng = bpy.data.node_groups["TunnelWalls_AV"]
dt = next(d for d in ng.animation_data.drivers if d.data_path == 'nodes["TravelPhase"].outputs[0].default_value')
for n in ("break_hold", "brk_acc"):
    var(dt, n)
dt.driver.expression = "travel_rate * (low_acc - break_hold * brk_acc) + kick_push * kick_shove"
dt.driver.is_valid = True

# colour drain on the existing Psych Saturation node (feeds Emission + Transparent tint)
nt = bpy.data.materials["ColorGlass"].node_tree
ds = next(d for d in nt.animation_data.drivers if d.data_path == 'nodes["Psych Saturation"].inputs[1].default_value')
var(ds, "break_desat"); var(ds, "brk")
base = ds.driver.expression.split(") * (1.0 - break_desat")[0].lstrip("(")
ds.driver.expression = f"({base}) * (1.0 - break_desat * brk)"
ds.driver.is_valid = True
drive(nt, 'nodes["Psych Saturation"].inputs[2].default_value', "1.0 - break_dim * brk", ("break_dim", "brk"))

# void: mix the whole surface to black emission
out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
mix = nt.nodes.get("Void Mix")
if mix is None:
    src = next(l.from_socket for l in nt.links if l.to_node == out and l.to_socket.name == "Surface")
    black = nt.nodes.new("ShaderNodeEmission"); black.name = black.label = "Void Black"
    black.inputs["Color"].default_value = (0, 0, 0, 1); black.inputs["Strength"].default_value = 0.0
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.name = mix.label = "Void Mix"
    mix.location = (out.location.x - 200, out.location.y); black.location = (mix.location.x - 200, mix.location.y - 200)
    out.location.x += 200
    nt.links.new(src, mix.inputs[1]); nt.links.new(black.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
drive(nt, 'nodes["Void Mix"].inputs[0].default_value', "void", ("void",))

c.update_tag(); ng.update_tag(); nt.update_tag(); bpy.context.view_layer.update()
bad = [d.data_path for idb in (nt, ng) for d in idb.animation_data.drivers if not d.driver.is_valid]
print("break_void:", F49, F63, F65, "invalid", bad)
