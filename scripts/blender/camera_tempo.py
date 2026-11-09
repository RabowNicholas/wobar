"""Full-length spine and the tempo-following camera.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns)
    ns["extend_spine"](1075.0)            # adds gentle bends after the signed-off first 100 m
    ns["key_camera"]()                    # camera + aim target keyed per frame from the tempo map
    ns["distance_at"](seconds)            # metres along the lane at a time in the piece

The camera is indifferent to the music except in speed (HOHLWEG_VISUALIZER section 1). Speed is looked
up from the tempo through SPEEDS, a table of (BPM, metres per second) with straight lines between the
entries - one number per tempo, so each section's pace can be set on its own.

    WALK    the first mapping: 1.37 m/s at 140, 3.4 at 174. Nick, on the fly-through with the music:
            "it feels really slow throughout."
    RUN     his replacement: a slow run at 140, a sprint at 174, a slower run at 128, easing down to
            the original walking pace at the very end (64).
"""
import math

import bpy

FPS = 24.0
V140 = 1.369                  # m/s on the signed-off proof segment
END = 654.86                 # length of the stitched EP
# (seconds, BPM). Tempo is linear between entries. Measured from the stitched EP audio on 2026-10-13
# (onset autocorrelation, 10 s windows; good to about +-2 s). Nick's own timings, which he called
# approximate, ran 6-8 s later: 103 / 142 / 189 / 214 / 420 / 462 / 612.
TEMPO = [(0.0, 140), (97.0, 140), (135.5, 174), (183.5, 174), (207.0, 140),
         (411.5, 140), (455.5, 128), (605.0, 128), (654.86, 64)]
WALK = [(64, 0.63), (128, 1.25), (140, 1.369), (174, 3.4)]
RUN = [(64, 1.369), (128, 2.4), (140, 2.8), (174, 7.0)]
SPEEDS = RUN
AIM_AHEAD = 8.0               # metres the aim target leads the camera


def bpm_at(t):
    for (t0, b0), (t1, b1) in zip(TEMPO, TEMPO[1:]):
        if t <= t1:
            return b0 + (b1 - b0) * (t - t0) / (t1 - t0) if t1 > t0 else b1
    return TEMPO[-1][1]


SETTLE = 7.0                  # seconds over which the camera glides to rest at the very end (Nick:
                              # "coming to a stop at the clearing", settling as the music ends)


def _speed_from_tempo(t, speeds):
    bpm = bpm_at(t)
    if bpm <= speeds[0][0]:
        return speeds[0][1]
    for (b0, v0), (b1, v1) in zip(speeds, speeds[1:]):
        if bpm <= b1:
            return v0 + (v1 - v0) * (bpm - b0) / (b1 - b0)
    return speeds[-1][1]


def speed_at(t, speeds=None):
    v = _speed_from_tempo(t, speeds or SPEEDS)
    u = min(max((t - (END - SETTLE)) / SETTLE, 0.0), 1.0)
    return v * (1.0 - u * u * (3 - 2 * u))


def distances(felt=None):
    """Metres travelled at the start of each frame, frame 1 = 0 m."""
    n = int(round(END * FPS))
    out, d = [0.0], 0.0
    for i in range(n):
        d += 0.5 * (speed_at(i / FPS, felt) + speed_at((i + 1) / FPS, felt)) / FPS
        out.append(d)
    return out


def distance_at(seconds, felt=None):
    return distances(felt)[int(round(seconds * FPS))]


def extend_spine(target_length, step=27.0, seed_phase=0.9):
    """Add Bezier points after the existing ones until the path is `target_length` metres long.
    Existing points are frozen first (handles set to FREE), so the built segment keeps its exact shape."""
    spl = bpy.data.objects["Spine"].data.splines[0]
    for p in spl.bezier_points:
        p.handle_left_type = p.handle_right_type = 'FREE'
    last = spl.bezier_points[-1]
    y0, x0 = last.co.y, last.co.x
    slope0 = (last.handle_right.x - last.co.x) / (last.handle_right.y - last.co.y)

    def swing(y):             # two slow sines: bends of radius ~40 m and up
        u = y - y0
        return 9.0 * math.sin(2 * math.pi * u / 176.0 + seed_phase) + 5.5 * math.sin(2 * math.pi * u / 103.0 + 2.1)

    base = swing(y0)
    y = y0
    while spl.calc_length() < target_length:
        y += step
        u = y - y0
        ease = min(u / 60.0, 1.0)                     # leave the old end along its own tangent, then join the sines
        x = x0 + slope0 * u * (1 - ease) * 0.5 + (swing(y) - base) * ease
        spl.bezier_points.add(1)
        p = spl.bezier_points[-1]
        p.co = (x, y, 0.0)
        p.handle_left_type = p.handle_right_type = 'AUTO'
    return len(spl.bezier_points), spl.calc_length()


def _fcurve(ob):
    ad = ob.animation_data
    bag = ad.action.layers[0].strips[0].channelbag(ad.action_slot)
    return next(fc for fc in bag.fcurves if "offset_factor" in fc.data_path)


def key_camera(felt=None):
    sc = bpy.context.scene
    length = bpy.data.objects["Spine"].data.splines[0].calc_length()
    dist = distances(felt)
    if dist[-1] + AIM_AHEAD > length:
        raise ValueError("spine is %.0f m; the camera needs %.0f m" % (length, dist[-1] + AIM_AHEAD))
    for name, lead in (("Camera", 0.0), ("CamTarget", AIM_AHEAD)):
        fc = _fcurve(bpy.data.objects[name])
        fc.keyframe_points.clear()
        fc.keyframe_points.add(len(dist))
        for i, (kp, d) in enumerate(zip(fc.keyframe_points, dist)):
            kp.co = (i + 1, (d + lead) / length)
            kp.interpolation = 'LINEAR'
        fc.update()
    sc.frame_start, sc.frame_end = 1, len(dist) - 1
    sc["camera_speeds"] = repr(felt or SPEEDS)
    return dist[-1], length, sc.frame_end
