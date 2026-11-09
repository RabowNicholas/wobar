"""The form control rig: kick and snare hits flash the wireframe cages and their lights.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns)
    ns["build_rig"]()                      # the FORM_CTRL empty, its knobs and every driver
    ns["set_hits"]("kick", [(sec, vel), ...])
    ns["set_hits"]("snare", [(sec, vel), ...])
    ns["load_hits"]()                      # the real hits, from the Ableton kick and snare stems
    ns["test_pattern"]()                   # placeholder hits: 140 half-time, then 174 two-step
    ns["set_colour_arc"]()                 # the colour follows the descent (keys + drivers)
    ns["add_forms_aov"]()                  # the wires also write to the `forms` AOV (for post)
    # New drivers stay invalid in a live session until the file is saved and reverted.

Everything hangs off one Empty, `FORM_CTRL` (collection FORMS), with custom properties:

    Knobs (set or keyframe these)
      strength      0-1, overall level of every flash. Keyframe it across the piece.
      fade          seconds for a flash to fall to ~5%. The knob for "mostly dark before the next hit".
      idle          level the forms hold between hits (0 = fully dark).
      wire_peak     emission strength of the cages at a full hit
      kick_light_w / snare_light_w    watts of the cast lights at a full hit
      form_r / form_g / form_b        the colour of every wire and form light (linear RGB).
                                      Keyframed by set_colour_arc(); every FormWire* material and
                                      FormLight_* light follows it.

    Written by set_hits (do not hand-edit)
      kick_t / snare_t        frame of the most recent hit (stepped)
      kick_vel / snare_vel    its velocity, 0-1 (stepped)

    Read-outs (driven)
      kick / snare            the envelope right now, 0-1

Envelope: vel * exp(-3 * (frame - hit_frame) / (fade * fps)), instant attack. A new hit restarts it.
All drivers are simple expressions, so they evaluate without Python auto-execution and in a
background render.
"""
import math

import bpy

CTRL = "FORM_CTRL"
KNOBS = dict(strength=1.0, fade=0.35, idle=0.0, wire_peak=0.7, kick_light_w=6.0, snare_light_w=120.0)
TARGETS = {
    "kick": dict(material="FormWire_Kick", light="FormLight_Kick", watts="kick_light_w"),
    "snare": dict(material="FormWire_Snare", light="FormLight_Snare", watts="snare_light_w"),
}


def _var(drv, name, ob, prop):
    v = drv.variables.new()
    v.name = name
    v.type = 'SINGLE_PROP'
    v.targets[0].id = ob
    v.targets[0].data_path = '["%s"]' % prop
    return v


def _driver(owner, path, expr, ob, props, index=-1):
    try:
        owner.driver_remove(path, index) if index >= 0 else owner.driver_remove(path)
    except TypeError:
        pass
    fc = owner.driver_add(path, index) if index >= 0 else owner.driver_add(path)
    d = fc.driver
    d.type = 'SCRIPTED'
    for name, prop in props.items():
        _var(d, name, ob, prop)
    d.expression = expr
    return fc


def build_rig():
    sc = bpy.context.scene
    ob = bpy.data.objects.get(CTRL)
    if ob is None:
        ob = bpy.data.objects.new(CTRL, None)
        ob.empty_display_type = 'SPHERE'
        ob.empty_display_size = 0.3
        bpy.data.collections["FORMS"].objects.link(ob)
    for k, v in KNOBS.items():
        if k not in ob:
            ob[k] = v
    for k in ("strength", "idle"):
        ob.id_properties_ui(k).update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0)
    ob.id_properties_ui("fade").update(min=0.02, max=4.0, soft_min=0.05, soft_max=1.5,
                                       description="Seconds for a flash to fall to about 5%")
    fps = sc.render.fps / sc.render.fps_base
    for name, tg in TARGETS.items():
        for k, v in ((name + "_t", -100000.0), (name + "_vel", 0.0), (name, 0.0)):
            if k not in ob:
                ob[k] = v
        # kick holds full for 2 frames before the fade (Nick, 2026-11-03, kick-hold A/B: "looks better"); snare doesn't
        hold = 2 if name == "kick" else 0
        env = "max(idle, strength * vel * exp(-3 * max(frame - t - %g, 0) / (fade * %g)))" % (hold, fps)
        _driver(ob, '["%s"]' % name, env, ob,
                dict(idle="idle", strength="strength", vel=name + "_vel", t=name + "_t", fade="fade"))
        mat = bpy.data.materials[tg["material"]]
        _driver(mat.node_tree, 'nodes["FormEmission"].inputs[1].default_value', "peak * e", ob,
                dict(peak="wire_peak", e=name))
        _driver(bpy.data.lights[tg["light"]], "energy", "w * e", ob, dict(w=tg["watts"], e=name))
    return ob


# Linear RGB, each scaled to the cover teal's luminance (0.489) so a colour change never reads as a
# brightness change. Pale ends of the brand families: the cover's teal #A0BFC9, dusty lavender
# #A085AE, a pale patina green.
COLOURS = dict(
    teal=(0.3515, 0.5210, 0.5841),
    lavender=(0.630, 0.421, 0.758),
    patina=(0.368, 0.536, 0.384),
)
# (frame, colour) - teal through ERNSTFALL; into lavender as ABGRUND goes down (3:57 -> 4:50, with the
# sky); back out through patina as GRUND opens (7:36.2 -> 7:52, with the moon); home to teal over the
# break (9:22 -> 10:05), before the forms thin out and go.
COLOUR_ARC = [(1, "teal"), (5689, "teal"), (6961, "lavender"), (10949, "lavender"), (11329, "patina"),
              (13488, "patina"), (14520, "teal")]


def set_colour_arc(arc=COLOUR_ARC):
    ob = bpy.data.objects[CTRL]
    for c, prop in enumerate(("form_r", "form_g", "form_b")):
        ob[prop] = COLOURS[arc[0][1]][c]
        try:
            ob.keyframe_delete('["%s"]' % prop)
        except RuntimeError:
            pass
        for frame, name in arc:
            ob[prop] = COLOURS[name][c]
            ob.keyframe_insert('["%s"]' % prop, frame=frame)
        fc = _fcurve(ob, prop)
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(arc))
        for kp, (frame, name) in zip(fc.keyframe_points, arc):
            kp.co = (frame, COLOURS[name][c])
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
        fc.update()
    rgb = dict(r="form_r", g="form_g", b="form_b")
    for mat in bpy.data.materials:
        if mat.name.startswith("FormWire") and mat.node_tree and "FormEmission" in mat.node_tree.nodes:
            for i, ch in enumerate("rgb"):
                _driver(mat.node_tree, 'nodes["FormEmission"].inputs[0].default_value', ch, ob,
                        {ch: rgb[ch]}, index=i)
    for light in bpy.data.lights:
        if light.name.startswith("FormLight_"):
            for i, ch in enumerate("rgb"):
                _driver(light, "color", ch, ob, {ch: rgb[ch]}, index=i)


# The wires also write themselves to a shader AOV, `forms` (colour x strength), so post can work on the
# code alone (TouchDesigner trails, composited back in Resolve). The cover form is left out on purpose:
# it is the one form that stays clean.
AOV = "forms"
AOV_MATERIALS = {"FormWire_Kick": "kick", "FormWire_Snare": "snare", "FormWire_Grass": "snare"}


def add_forms_aov(view_layer=None):
    vl = view_layer or bpy.context.view_layer
    if AOV not in [a.name for a in vl.aovs]:
        a = vl.aovs.add()
        a.name = AOV
        a.type = 'COLOR'
    ob = bpy.data.objects[CTRL]
    for name, env in AOV_MATERIALS.items():
        mat = bpy.data.materials.get(name)
        if not mat:
            continue
        nt = mat.node_tree
        sc = nt.nodes.get("FormAOVColor") or nt.nodes.new("ShaderNodeVectorMath")
        sc.name = "FormAOVColor"
        sc.operation = 'SCALE'
        out = nt.nodes.get("FormAOV") or nt.nodes.new("ShaderNodeOutputAOV")
        out.name = "FormAOV"
        out.aov_name = AOV
        nt.links.new(sc.outputs["Vector"], out.inputs["Color"])
        for i, ch in enumerate("rgb"):
            _driver(nt, 'nodes["FormAOVColor"].inputs[0].default_value', ch, ob, {ch: "form_" + ch}, index=i)
        scale = next(s for s in sc.inputs if s.name == "Scale")
        _driver(nt, 'nodes["FormAOVColor"].inputs[%d].default_value' % list(sc.inputs).index(scale), "peak * e", ob,
                {"peak": "wire_peak", "e": env})


def _fcurve(ob, prop):
    ad = ob.animation_data
    bag = ad.action.layers[0].strips[0].channelbag(ad.action_slot)
    return next(fc for fc in bag.fcurves if fc.data_path == '["%s"]' % prop)


def set_hits(name, hits):
    """hits: [(seconds_from_frame_1, velocity 0-1), ...]. Replaces any earlier hits for `name`."""
    sc = bpy.context.scene
    fps = sc.render.fps / sc.render.fps_base
    ob = bpy.data.objects[CTRL]
    for prop in (name + "_t", name + "_vel"):
        ob[prop] = -100000.0 if prop.endswith("_t") else 0.0
        ob.keyframe_insert('["%s"]' % prop, frame=0)
        fc = _fcurve(ob, prop)
        fc.keyframe_points.clear()
        rows = [(0.0, ob[prop])]
        for sec, vel in sorted(hits):
            # Snapped to the nearest frame (at most 21 ms off at 24 fps). With the exact fractional
            # frame, the first rendered frame of a hit caught it part-decayed, so equal hits peaked
            # anywhere from 0.7 to 1.0.
            f = round(1.0 + sec * fps)
            rows.append((f, f if prop.endswith("_t") else vel))
        fc.keyframe_points.add(len(rows))
        for kp, (frame, value) in zip(fc.keyframe_points, rows):
            kp.co = (frame, value)
            kp.interpolation = 'CONSTANT'
        fc.update()
    return len(hits)


HITS_JSON = "/Volumes/music/blender/hohlweg_assets/audio/hohlweg_hits.json"


def load_hits(path=HITS_JSON):
    """Kick and snare from the soloed stems (hohlweg_kick_stem / hohlweg_snare_stem, re-exported 14 Oct to
    line up with the stitched master at 0 ms), built by scripts/post/stem_hits.py: onset time in master seconds,
    velocity = RMS of the first 50 ms over that song's 90th-percentile hit (clipped at 1), so the three songs
    flash equally and quieter hits inside a song stay dimmer; echoes the previous flash would mask (at fade
    0.35) are dropped. hohlweg_hits_oldstems.json is the earlier set from the mismatched stems."""
    import json
    hits = json.load(open(path))
    return {name: set_hits(name, [tuple(h) for h in hits[name]]) for name in ("kick", "snare")}


def test_pattern(switch_sec=36.0, end_sec=72.0):
    """Placeholder drums: 140 BPM half-time (kick on 1, snare on 3) up to `switch_sec`,
    then 174 BPM two-step (kick on 1 and the 'and' of 3, snare on 2 and 4)."""
    kick, snare = [], []
    t, bar = 0.0, 4 * 60.0 / 140
    while t < switch_sec - 1e-6:
        kick.append((t, 1.0))
        snare.append((t + bar / 2, 1.0))
        t += bar
    beat = 60.0 / 174
    while t < end_sec:
        kick += [(t, 1.0), (t + 2.5 * beat, 0.8)]
        snare += [(t + beat, 1.0), (t + 3 * beat, 0.9)]
        t += 4 * beat
    return set_hits("kick", kick), set_hits("snare", snare), t
