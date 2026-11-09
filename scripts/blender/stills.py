"""Render review stills from the scene camera, then restore every setting touched.

Run inside Blender (via the MCP):
    ns = {}; exec(open(PATH).read(), ns)
    ns["render_stills"](out_dir, frames=[1, 450], engine="BLENDER_EEVEE", shapes=("wide", "vert"))

`look` ignores a changed render aspect and draws no overlays, so true-aspect
review frames go through a real render instead (see BLENDER_BUILD_LOG §3).
"""
import os

import bpy

SHAPES = {"wide": (960, 540), "vert": (540, 960), "square": (720, 720)}


def render_stills(out_dir, frames, engine="BLENDER_WORKBENCH", shapes=("wide",), tag="", samples=16):
    s = bpy.context.scene
    r = s.render
    os.makedirs(out_dir, exist_ok=True)
    keep = (r.engine, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath,
            r.image_settings.file_format, s.frame_current)
    keep_samples = getattr(s.eevee, "taa_render_samples", None)
    written = []
    try:
        r.engine = engine
        r.image_settings.file_format = "PNG"
        r.resolution_percentage = 100
        if engine == "BLENDER_EEVEE" and keep_samples is not None:
            s.eevee.taa_render_samples = samples
        for f in frames:
            s.frame_set(f)
            for shape in shapes:
                r.resolution_x, r.resolution_y = SHAPES[shape]
                r.filepath = os.path.join(out_dir, f"{tag}{shape}_{f:05d}.png")
                bpy.ops.render.render(write_still=True)
                written.append(r.filepath)
    finally:
        r.engine, r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath = keep[:5]
        r.image_settings.file_format = keep[5]
        if keep_samples is not None:
            s.eevee.taa_render_samples = keep_samples
        s.frame_set(keep[6])
    return written
