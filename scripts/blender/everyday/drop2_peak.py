"""Everyday drop 2 escalation + bar-97 peak. Run inside everyday_tunnel_v1.blend (MCP or Text Editor),
after the stem curves are baked onto WOBAR_CTRL. Idempotent: re-running re-bakes and re-wires.

Drop 2 (bar 65-112): the inner tunnel layer rolls against the other two, one step per snare
  (Tunnel_Inner rotation about the tunnel axis Y = -2pi * inner_shear * shear).
Peak (bar 97, one-beat ease in; eases out over 2 bars from bar 113): psychedelic level forced to max
  and pushed past it (peak_sat / peak_rim), glints fewer (x(1-peak_glint_frac)) and brighter (x(1+peak_glint_gain)).

Why: in the audio, drop 2 matches drop 1 hit for hit and the last 16 bars thin out (hats 8 -> 3.5/bar),
so the escalation has to come from section channels, not the stems. Decided 2026-11-08: "add one new
behaviour" over "turn everything up", and treat bar 97 as the peak rather than letting it sag.
"""
import math
import bpy
import numpy as np

BPM, FPS, N = 140, 30, 6583
TUNE = dict(inner_shear=1 / 16, peak_sat=0.35, peak_rim=0.4, peak_glint_frac=0.5, peak_glint_gain=0.6)


def bar_frame(b):
    return round((b - 1) * 60 / BPM * 4 * FPS) + 1


def smooth(u):
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


c = bpy.data.objects["WOBAR_CTRL"]
ad = c.animation_data
act, slot = ad.action, ad.action_slot
fcs = {fc.data_path: fc for l in act.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves}
F65, F97, F113 = bar_frame(65), bar_frame(97), bar_frame(113)
fr = np.arange(1, N + 1)
snare = np.array([fcs['["snare_step"]'].evaluate(f) for f in fr])
shear = np.where(fr < F65, 0.0, snare - snare[F65 - 1])
shear = np.where(fr >= F113, shear[F113 - 2], shear)          # hold the final angle through the outro
beat = 60 / BPM * FPS
peak = smooth((fr - F97) / beat) * (1 - smooth((fr - F113) / (beat * 8)))

for name, arr in (("shear", shear), ("peak", peak)):
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
    c.setdefault(k, v)                                        # keep values already tuned in the file


def var(d, name):
    if name not in [v.name for v in d.driver.variables]:
        v = d.driver.variables.new(); v.name = name; v.type = "SINGLE_PROP"
        v.targets[0].id = c; v.targets[0].data_path = f'["{name}"]'


nt = bpy.data.materials["ColorGlass"].node_tree
P = "min(1.0, max(0.0, (low_slow - psych_lo) / psych_span))"
EXPR = {
    'nodes["Psych Saturation"].inputs[1].default_value': f"1.0 + sat_depth * max({P}, peak) + peak_sat * peak",
    'nodes["Rim Shift"].inputs[1].default_value': f"1.5 * (1.0 + rim_depth * max({P}, peak) + peak_rim * peak)",
    'nodes["GlintFrac"].outputs[0].default_value': "x * (1.0 - peak_glint_frac * peak)",
    'nodes["GlintStrength"].outputs[0].default_value': "x * (1.0 + peak_glint_gain * peak)",
}
for d in nt.animation_data.drivers:
    if d.data_path in EXPR:
        for n in ("peak", *TUNE):
            if n in EXPR[d.data_path]:
                var(d, n)
        d.driver.expression = EXPR[d.data_path]
        d.driver.is_valid = True                              # FOOTGUNS V-12

inner = bpy.data.objects["Tunnel_Inner"]
inner.driver_remove("rotation_euler", 1)
d = inner.driver_add("rotation_euler", 1)
d.driver.type = "SCRIPTED"
var(d, "inner_shear"); var(d, "shear")
d.driver.expression = "-2 * pi * inner_shear * shear"

c.update_tag(); nt.update_tag(); bpy.context.view_layer.update()
bad = [x.data_path for x in nt.animation_data.drivers if not x.driver.is_valid] + ([] if d.driver.is_valid else ["Tunnel_Inner roll"])
print("drop2_peak:", F65, F97, F113, "total roll turns", round(float(shear[-1]) * c["inner_shear"], 2), "invalid", bad)
