"""Everyday drop 1 (held breath -> lunge) and the dissipating outro. Run inside everyday_tunnel_v1.blend
LAST in the chain: analyze_stems -> drop2_peak -> break_void -> break_chaos -> intro_outro -> this.
It rewrites the phase, psych and chaos drivers, so re-running an earlier script means re-running the
chain from there. Idempotent.

DROP 1 (testing, 2026-11-09):
  bars 15-16  travel eases to a stop over two beats and the tunnel draws back slightly toward the light
              (lunge < 0): the held breath in the near-silence.
  bar 17      one-beat lunge forward (lunge_amt) and the colour floods in at once (flood = 1 on the downbeat,
              handing over to the low_slow psych over one bar) instead of ramping over 0.4 s.
OUTRO (supersedes the camera pull-out, which is switched off with outside_dist = 0):
  from bar 113 the tunnel lets go: shapes drift apart (the break's chaos stage, gently: dissolve) and
  shrink away on the hits with no flash and no pop (pop gated by intro_mask). Travel, spin, colour and
  pulse all slow to a full stop by bar 127 (ostop), the first stillness since frame 1. Last image is the
  light alone from the same place as frame 1; cut to black on the last kick (cut, from intro_outro.py).
"""
import bpy
import numpy as np

BPM, FPS, N = 140, 30, 6583
TUNE = dict(lunge_amt=0.5, lunge_pull=0.12, dis_shape=1.2, dis_scatter=3.0, dis_tumble=1.0, dis_rate=0.15)
OVERRIDE = dict(outside_dist=0.0)


def bar_frame(b):
    return round((b - 1) * 60 / BPM * 4 * FPS) + 1


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def ease_out(u):
    u = np.clip(u, 0, 1)
    return 1 - (1 - u) ** 3


c = bpy.data.objects["WOBAR_CTRL"]
ad = c.animation_data
act, slot = ad.action, ad.action_slot
fcs = {fc.data_path: fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves}
fr = np.arange(1, N + 1).astype(float)
F15, F17, F113, F127 = bar_frame(15), bar_frame(17), bar_frame(113), bar_frame(127)
beat = 60 / BPM * FPS
for k, v in TUNE.items():
    if k not in c: c[k] = v
for k, v in OVERRIDE.items():
    c[k] = v


def ch(name):
    return np.array([fcs[f'["{name}"]'].evaluate(f) for f in fr])


def accum(rate):                     # running sum, value at frame f excludes f itself
    return np.concatenate([[0.0], np.cumsum(rate[:-1])])


low_acc, kick, snare = ch("low_acc"), ch("kick_shove"), ch("snare_step")
speed = np.diff(low_acc, append=low_acc[-1])
hold1 = smooth((fr - F15) / (2 * beat)) * (fr < F17)
ostop = smooth((fr - F113) / (F127 - F113))
stop = hold1 + ostop
xhold_acc = accum(speed * stop)                                   # travel / pulse removed by the holds
kick_hold = accum(np.diff(kick, append=kick[-1]) * ostop)          # kick shoves removed in the outro
snare_hold = accum(np.diff(snare, append=snare[-1]) * ostop)       # snare turns removed in the outro
ostop_t = accum(ostop / FPS)                                       # seconds of stopped clock
pull = -c["lunge_pull"] * smooth((fr - F15) / (8 * beat)) * (fr < F17)
surge = ease_out((fr - F17) / beat) * (fr >= F17)
lunge = pull + (1.0 + c["lunge_pull"]) * surge                     # net +1 after the lunge; x lunge_amt
flood = (fr >= F17) * (1 - smooth((fr - F17) / (4 * beat)))   # one bar: low_slow needs that long to catch up
dissolve = smooth((fr - F113) / (F127 - F113))
outro_t = np.maximum(0, fr - F113) / FPS

for name, arr in (("xhold_acc", xhold_acc), ("kick_hold", kick_hold), ("snare_hold", snare_hold),
                  ("ostop_t", ostop_t), ("lunge", lunge), ("flood", flood), ("dissolve", dissolve),
                  ("outro_t", outro_t)):
    c[name] = 0.0
    fc = act.fcurve_ensure_for_datablock(c, f'["{name}"]')
    fc.keyframe_points.clear()
    fc.keyframe_points.add(N)
    co = np.empty(2 * N)
    co[0::2], co[1::2] = fr, arr
    fc.keyframe_points.foreach_set("co", co)
    fc.update()
ad.action = None; ad.action = act; ad.action_slot = slot     # FOOTGUNS V-11


def var(d, name):
    if name not in [v.name for v in d.driver.variables]:
        v = d.driver.variables.new(); v.name = name; v.type = "SINGLE_PROP"
        v.targets[0].id = c; v.targets[0].data_path = f'["{name}"]'


def set_expr(idb, path, expr):
    d = next(x for x in idb.animation_data.drivers if x.data_path == path)
    for n in sorted(set(__import__("re").findall(r"[A-Za-z_][A-Za-z_0-9]*", expr)) - {"frame", "max", "min", "pi"}):
        if n in c.keys():
            var(d, n)
    d.driver.expression = expr
    d.driver.is_valid = True


ng = bpy.data.node_groups["TunnelWalls_AV"]
V = 'nodes["{}"].outputs[0].default_value'
T = "((frame - 1) / 30 - ostop_t)"
set_expr(ng, V.format("TravelPhase"),
         "travel_rate * (low_acc - break_hold * brk_acc - xhold_acc) + kick_push * (kick_shove - kick_hold) + lunge_amt * lunge")
set_expr(ng, V.format("SpinPhase"), f"spin_rate * {T} + spin_step * (snare_step - snare_hold)")
set_expr(ng, V.format("ColorPhase"), f"color_rate * {T} + hat_nudge * hat_step")
set_expr(ng, V.format("PulsePhase"), "pulse_rate * (low_acc - xhold_acc)")
set_expr(ng, V.format("Chaos Shape"), "shape_amp * c_shape + dis_shape * dissolve")
set_expr(ng, V.format("Chaos Scatter"), "scatter_amp * c_scatter + dis_scatter * dissolve")
set_expr(ng, V.format("Chaos Time"), "chaos_t + dis_rate * outro_t")
set_expr(ng, V.format("Chaos Tumble"), "tumble_amp * c_scatter + c_shape * chaos_t + dis_tumble * dissolve")
set_expr(ng, V.format("Reveal Pop Amp"), "pop_amp * intro_mask")

nt = bpy.data.materials["ColorGlass"].node_tree
P = "min(1.0, max(0.0, (low_slow - psych_lo) / psych_span))"
set_expr(nt, 'nodes["Psych Saturation"].inputs[1].default_value',
         f"(1.0 + sat_depth * max({P}, peak, flood) + peak_sat * peak) * (1.0 - break_desat * brk)")
set_expr(nt, 'nodes["Rim Shift"].inputs[1].default_value',
         f"1.5 * (1.0 + rim_depth * max({P}, peak, flood) + peak_rim * peak)")
set_expr(nt, V.format("Reveal Pop Glow"), "pop_glow * intro_mask")

c.update_tag(); ng.update_tag(); nt.update_tag(); bpy.context.view_layer.update()
bad = [d.data_path for idb in (nt, ng) for d in idb.animation_data.drivers if not d.driver.is_valid]
print("drop1_outro:", F15, F17, F113, F127, "invalid", bad)
