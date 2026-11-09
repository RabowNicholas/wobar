"""Form wires keep their colour, never white-hot (Nick, 2026-10-28).

    blender -b hohlweg_3_forms.blend -P form_wires.py      (saves; safe to re-run)   KS_K / GPAT_K override for tests

Kick / snare: the shared FormWire_Kick and FormWire_Snare (ERNSTFALL cages, GRUND creek stones and tree cages) clip
to white under the lift; x0.4 left them white (AgX compresses: emission x0.4 is only x0.63 on screen). Emission and
the forms AOV go to x KS_K, the level the roots and slide cages already use. Their copies (FormWire_Root,
FormWire_*_Slide) carry their own "peak * e * k" drivers and are untouched.
Lights (Nick, 2026-10-29): the dimmer wires darkened the frames (ERNSTFALL x0.5-0.77), so FormLight_Kick/Snare/SnareStone
go to x KL_E before GRUND (frame 10945) and x KL_G from GRUND on; one x3 blew GRUND out (9:18 view-clip 8 -> 22%).
Grass (Nick, 2026-10-27: "hit in the green patina colour and decay back to the grass's own colour"): FormWire_Grass's
colour no longer follows the colour arc; it mixes from patina at the hit to the grass's albedo (0.06, 0.061, 0.031,
grass_medium_01_diff) scaled to the patina's luminance, by the pluck envelope (pg_emax), and its emission is x GPAT_K.
"""
import bpy, os

KS_K = float(os.environ.get("KS_K", "0.15"))
GPAT_K = float(os.environ.get("GPAT_K", "0.15"))
KL_E = float(os.environ.get("KL_E", "3"))
KL_G = float(os.environ.get("KL_G", "1.5"))
PATINA = (0.368, 0.536, 0.384, 1)           # form_rgb in GRUND (#A3C1A7 at the teal's luminance)
GRASS = (0.50, 0.51, 0.26, 1)

n = 0
for mn in ("FormWire_Kick", "FormWire_Snare"):
    for d in bpy.data.materials[mn].node_tree.animation_data.drivers:
        if d.driver.expression == "peak * e":
            d.driver.expression = f"peak * e * {KS_K}"; n += 1
print("FW kick/snare drivers scaled", n, flush=True)

n = 0
for on in ("FormLight_Kick", "FormLight_Snare", "FormLight_SnareStone"):
    for d in bpy.data.objects[on].data.animation_data.drivers:
        if d.data_path == "energy" and d.driver.expression == "w * e":
            d.driver.expression = f"w * e * ({KL_E} if frame < 10945 else {KL_G})"; n += 1
print("FW kick/snare lights scaled", n, flush=True)

nt = bpy.data.materials["FormWire_Grass"].node_tree; N, L = nt.nodes, nt.links
for d in list(nt.animation_data.drivers):
    if d.data_path == 'nodes["FormEmission"].inputs[0].default_value':
        nt.animation_data.drivers.remove(d)
mix = N.get("GP_Mix") or N.new("ShaderNodeMix"); mix.name = "GP_Mix"; mix.data_type = "RGBA"
mix.inputs["A"].default_value = GRASS; mix.inputs["B"].default_value = PATINA
L.new(N["PG_all"].outputs[0], mix.inputs["Factor"]); L.new(mix.outputs["Result"], N["FormEmission"].inputs["Color"])
k = N.get("GP_K") or N.new("ShaderNodeMath"); k.name = "GP_K"; k.operation = "MULTIPLY"; k.inputs[1].default_value = GPAT_K
L.new(N["PG_total"].outputs[0], k.inputs[0]); L.new(k.outputs[0], N["FormEmission"].inputs["Strength"])
bpy.context.scene["form_wires_applied"] = f"2026-10-29 ks {KS_K} grass {GPAT_K} lights {KL_E}/{KL_G}"
print("FW grass patina", GPAT_K, flush=True)

if bpy.app.background and not os.environ.get("FW_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("FW saved", bpy.data.filepath, flush=True)
