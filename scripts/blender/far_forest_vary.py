"""Break up the far forest (2026-11-05, realism audit, item 1).

At 5:25-5:37 the far valley reads as a barcode: FarFir_0/1/2 (cone stand-ins, FarForest GN, 300-2000 m) are hazed by
EMISSION (FV_HazeAmt * FV_HazeCol0) that depends on distance only, so every tree at a given distance glows the same,
the band sits brighter than the sky above it and the rows read as a comb. A real far forest at night is an uneven,
darker mass.

FarFir material only (FarCanopy untouched): per-instance Object Info Random drives
- the haze emission  x  HAZE * mix(FF_HMIN, 1, r1)        (r1 = Random)
- the base tone      x  mix(FF_BMIN, FF_BMAX, r2)          (r2 = fract(Random * 7.31))
    FF_DENS (0.25)  FF_HAZE FF_HMIN FF_BMIN FF_BMAX (all 1.0 = off; tested 0.45-1.8 haze and 0.1-1.6 tone: darker or varied firs
    separate into spikes and make the comb worse - density is the lever. Applied: density 0.25 only.)   FF_NOSAVE=1 for tests
"""
import bpy, os
sc = bpy.context.scene
if sc.get("far_forest_vary_applied") and not os.environ.get("FF_NOSAVE"): raise SystemExit("far_forest_vary already applied")
E = lambda k, d: float(os.environ.get(k, d))
HAZE, HMIN, BMIN, BMAX = E("FF_HAZE", 1.0), E("FF_HMIN", 1.0), E("FF_BMIN", 1.0), E("FF_BMAX", 1.0)
m = bpy.data.materials["FarFir"]; nt = m.node_tree; N = nt.nodes; L = nt.links
bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
oi = N.new("ShaderNodeObjectInfo"); oi.name = "FF_ObjInfo"
# r2 = fract(random * 7.31)
r2m = N.new("ShaderNodeMath"); r2m.operation = 'MULTIPLY'; r2m.inputs[1].default_value = 7.31; r2m.name = "FF_r2mul"
r2f = N.new("ShaderNodeMath"); r2f.operation = 'FRACT'; r2f.name = "FF_r2"
L.new(oi.outputs["Random"], r2m.inputs[0]); L.new(r2m.outputs[0], r2f.inputs[0])
# haze factor = HAZE * (HMIN + (1-HMIN) * r1)
hz = N.new("ShaderNodeMapRange"); hz.name = "FF_HazeVar"
hz.inputs["From Min"].default_value = 0; hz.inputs["From Max"].default_value = 1
hz.inputs["To Min"].default_value = HAZE * HMIN; hz.inputs["To Max"].default_value = HAZE
L.new(oi.outputs["Random"], hz.inputs["Value"])
hzm = N.new("ShaderNodeMath"); hzm.operation = 'MULTIPLY'; hzm.name = "FF_HazeMul"
src = bsdf.inputs["Emission Strength"].links[0].from_socket
L.new(src, hzm.inputs[0]); L.new(hz.outputs[0], hzm.inputs[1]); L.new(hzm.outputs[0], bsdf.inputs["Emission Strength"])
# base tone = base * mix(BMIN, BMAX, r2)
bt = N.new("ShaderNodeMapRange"); bt.name = "FF_ToneVar"
bt.inputs["To Min"].default_value = BMIN; bt.inputs["To Max"].default_value = BMAX
L.new(r2f.outputs[0], bt.inputs["Value"])
btm = N.new("ShaderNodeVectorMath"); btm.operation = 'SCALE'; btm.name = "FF_ToneMul"
bsrc = bsdf.inputs["Base Color"].links[0].from_socket
L.new(bsrc, btm.inputs[0]); L.new(bt.outputs[0], btm.inputs["Scale"]); L.new(btm.outputs[0], bsdf.inputs["Base Color"])
# density: FarForest's distance ramp (Map Range / Map Range.001 To Min/Max) and near cap (Math.001 / Math.004) x DENS.
# The comb is mostly the count of thin spires (density 0.25 in the test removed most of it; tone/haze alone did not).
DENS = E("FF_DENS", 0.25)
g = bpy.data.objects["FarForest"].modifiers[0].node_group; G = g.nodes
for n in ("Map Range", "Map Range.001"):
    for i in ("To Min", "To Max"): G[n].inputs[i].default_value *= DENS
for n in ("Math.001", "Math.004"): G[n].inputs[1].default_value *= DENS
sc["far_forest_vary_applied"] = f"2026-11-05 dens {DENS} haze {HAZE} hmin {HMIN} tone {BMIN}-{BMAX}"
print("FF", sc["far_forest_vary_applied"], flush=True)
if os.environ.get("FF_RENDER"):
    sc.render.resolution_percentage = 50; sc.eevee.taa_render_samples = 16; sc.render.image_settings.file_format = 'PNG'
    for f in map(int, os.environ["FF_RENDER"].split(",")):
        sc.frame_set(f); sc.render.filepath = os.path.join(os.environ["FF_OUT"], f"ff_{os.environ.get('FF_TAG','x')}_{f:05d}.png")
        bpy.ops.render.render(write_still=True); print("FF render", f, flush=True)
if bpy.app.background and not os.environ.get("FF_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("FF saved", bpy.data.filepath, flush=True)
