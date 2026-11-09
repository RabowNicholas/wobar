"""Soften the trench-mist lid (2026-11-05, realism audit).

The trench layer (TrenchDensity 0.1/m) hands over to the forest layer (0.016/m) in one 0.8 m band, 2.6-3.4 m above
the lane, and the band reads the RAW height (Z_above_lane), not the noise-uneven height (Math.005) the exponential
falloffs use. So the mist has a level, crisp top: a box of fog filling the lane at 1:37 and a flat slab over the GRUND
floor at 10:35.

Fix, values only (no new noise):
- both cut-offs (Map Range: trench, Map Range.001: forest) read the uneven height (Math.005) instead of Z_above_lane;
- the trench fade widens to MT_T0..MT_T1 (default 1.8..3.6 m), the forest fade-in to MT_F0..MT_F1 (2.6..3.9 m);
- top unevenness 1.1 -> MT_UNEV (1.8 m).
    MT_T0 MT_T1 MT_F0 MT_F1 MT_UNEV, MT_NOSAVE=1 for tests
"""
import bpy, os
sc = bpy.context.scene
if sc.get("mist_top_soft_applied") and not os.environ.get("MT_NOSAVE"): raise SystemExit("mist_top_soft already applied")
E = lambda k, d: float(os.environ.get(k, d))
T0, T1, F0, F1, UNEV = E("MT_T0", 1.8), E("MT_T1", 3.6), E("MT_F0", 2.6), E("MT_F1", 3.9), E("MT_UNEV", 1.8)
nt = bpy.data.materials["MistVolume"].node_tree; N = nt.nodes
uneven = N["Math.005"]
for name, (a, b) in (("Map Range", (T0, T1)), ("Map Range.001", (F0, F1))):
    mr = N[name]; inp = mr.inputs["Value"]
    for l in list(inp.links): nt.links.remove(l)
    nt.links.new(uneven.outputs[0], inp)
    mr.inputs["From Min"].default_value = a; mr.inputs["From Max"].default_value = b
N["TopUnevenness_m"].inputs[1].default_value = UNEV
sc["mist_top_soft_applied"] = f"2026-11-05 trench {T0}-{T1} forest {F0}-{F1} unev {UNEV}"
print("MT", sc["mist_top_soft_applied"], flush=True)
if os.environ.get("MT_RENDER"):
    sc.render.resolution_percentage = 50; sc.eevee.taa_render_samples = 16; sc.render.image_settings.file_format = 'PNG'
    for f in map(int, os.environ["MT_RENDER"].split(",")):
        sc.frame_set(f); sc.render.filepath = os.path.join(os.environ["MT_OUT"], f"mt_{f:05d}.png")
        bpy.ops.render.render(write_still=True); print("MT render", f, flush=True)
if bpy.app.background and not os.environ.get("MT_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("MT saved", bpy.data.filepath, flush=True)
