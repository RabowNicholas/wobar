"""Bake per-frame stem curves (analyze_stems.py output) onto WOBAR_CTRL. Run inside the piece's .blend.
usage (MCP / Text Editor): set CURVES, exec this file.   headless: blender -b FILE -P bake_curves.py -- CURVES

First step of the chain: bake_curves -> drop2_peak -> break_void -> break_chaos -> intro_outro -> drop1_outro.
Creates WOBAR_CTRL if the file has none (kit: append KIT_CTRL instead, it already carries every channel).
Re-baking replaces the stem channels' keys and leaves section channels and tuning constants alone.
Counts (*_idx) are CONSTANT-interpolated, everything else LINEAR. Recovered 2026-11-09 from the code that
built Everyday's control empty interactively on 2026-11-07, plus the later low_slow channel.
"""
import json
import sys
import bpy

CURVES = "/Volumes/music/blender/everyday_assets/everyday_curves.json"
if "--" in sys.argv:
    CURVES = sys.argv[sys.argv.index("--") + 1]
TUNE = dict(travel_rate=0.18, kick_push=0.05, spin_rate=0.0728, spin_step=1 / 24, color_rate=0.0874, hat_nudge=0.0,
            pulse_rate=0.17, pulse_base=0.75, pulse_depth=0.5, light_floor=0.85, light_depth=0.45, glow_floor=0.9,
            glow_depth=0.35)

D = bpy.data
sc = bpy.context.scene
js = json.load(open(CURVES))
ch, n = js["channels"], js["frames"]
ctrl = D.objects.get("WOBAR_CTRL")
if ctrl is None:
    ctrl = D.objects.new("WOBAR_CTRL", None)
    ctrl.empty_display_type = "PLAIN_AXES"; ctrl.location = (0, -5, 0)
    sc.collection.objects.link(ctrl)
for k, v in TUNE.items():
    if k not in ctrl:
        ctrl[k] = float(v)
ad = ctrl.animation_data or ctrl.animation_data_create()
act = ad.action
if act is None:
    act = D.actions.new("WOBAR_CTRL_curves"); ad.action = act
slot = ad.action_slot
frames = list(range(1, n + 1))
for k, vals in ch.items():
    ctrl[k] = 0.0
    fc = act.fcurve_ensure_for_datablock(ctrl, f'["{k}"]')
    fc.keyframe_points.clear()
    fc.keyframe_points.add(n)
    co = [0.0] * (2 * n); co[0::2] = frames; co[1::2] = vals
    fc.keyframe_points.foreach_set("co", co)
    fc.keyframe_points.foreach_set("interpolation", [0 if k.endswith("_idx") else 1] * n)   # CONSTANT / LINEAR
    fc.update()
ad.action = None; ad.action = act                     # FOOTGUNS V-11
if slot is not None:
    ad.action_slot = slot
sc.frame_start, sc.frame_end = 1, n
bad = 0
for f in (1, n // 3, 2 * n // 3, n):
    sc.frame_set(f)
    bad += sum(abs(ctrl[k] - ch[k][f - 1]) > 1e-3 for k in ch)
print("bake_curves:", len(ch), "channels x", n, "frames | mismatches vs json:", bad)
