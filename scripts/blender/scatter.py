"""Scatter kit collections over the lane / forest floor with Geometry Nodes.

Run inside Blender:
    ns = {}; exec(open(PATH).read(), ns)
    ns["build_scatter"]("Scatter_Cover", "Lane", LAYERS, cull=dict(camera="Camera", behind=10, ahead=150))
    ns["build_scatter"]("Scatter_TreeCages", "Lane", CAGE_LAYERS, collection="FORMS", cull=...,
                        points_from="Scatter_Trees")
    ns["rebuild"]("Scatter_Cover", edit=lambda layers: ...)      # retune from the stored settings

Two objects per scatter, so the work scales with what the camera sees and not with the length of the lane:

    <name>_pts   STATIC. Distributes every layer's points over the whole surface once and stores, per
                 point, `layer` (index) and `rot` (surface alignment). It depends only on the surface,
                 so Blender evaluates it once and keeps it. Hidden from viewport and render.
    <name>       PER FRAME. Reads those points, drops everything outside the camera window, and
                 instances the survivors. This is all that reruns as the camera moves.

Distributing inside the per-frame object (the first version) redid the whole lane every frame, and
cutting the surface to a window first is not an option: Distribute Points on Faces seeds each triangle
by its index, so every plant would jump whenever the window moved.

`points_from` makes a scatter reuse another scatter's points (cages and lights on the trees and ferns):
identical points and IDs, so every cage sits exactly on its plant. Its layers are matched to the
source's by name, ignoring a `cage_` / `light_` prefix.

A layer is a dict:

    name        label; also how `points_from` layers find their source layer
    collection  kit collection to instance (children picked at random)
    density     instances per square metre where the mask is 1                      [static]
    lat         (in0, in1, out1, out0): trapezoid on |lat| in metres                 [static]
    clump       (noise_scale, lo, hi) or None: patchiness                            [static]
    gap         optional dict(freq, offset, lo, hi, side, amount): clearings along the lane [static]
    along       optional (start, end) in metres along the lane: the layer exists only there      [static]
    fade        optional (in0, in1, out1, out0): density trapezoid along the lane (metres), soft edges [static]
    ring        optional (cx, cy, in0, in1, out1, out0): density trapezoid on distance (m) from a point in
                plan - (cx, cy, 7.5, 9.5, 1e6, 2e6) clears a circle, (cx, cy, 7.5, 8.5, 11, 13) plants a ring [static]
    rings       optional list of further ring tuples, multiplied in after `ring` [static]
    attr        optional (name, in0, in1, out1, out0): density trapezoid on a float surface attribute    [static]
    above       optional z in metres: nothing below it - plants out of standing water. Measured from the lane's
                own level: if the scene has `lane_zshift` = (along0, along1, dz), the step is subtracted first [static]
    steep       optional (nz_lo, nz_hi, from_along, floor): thin out on near-vertical faces - full density
                where the surface normal's z is above nz_hi, `floor` x density below nz_lo. Applies only
                past `from_along` metres (the deep walls of ABGRUND), so earlier banks are untouched. [static]
    seed        int: distribution seed [static] and the base of the per-instance randoms
    scale       (min, max) uniform instance scale
    upright     True = grows straight up; False = lies on the surface (aligned to its normal)
    sink        metres to push the instance down into the ground (negative lifts it)
    tilt        optional max lean in radians, random direction
    sway        optional (radians, speed[, flutter]): wind - rocks about the base, from position and time only;
                `flutter` adds a per-plant tremble (finer noise, 4x speed) of that many radians peak-to-peak
    show        optional dict(inside, outside, patch_scale, patch_lo, patch_hi, seed, near): keep a random
                share. `near=(lat0, lat1)` fades the share to nothing toward the lane centre (|lat| below
                lat0), so nothing shown sits right against the lens. `span=(in0, in1, out1, out0)` limits
                it to a stretch of the lane in metres along (a trapezoid), so one set of forms can hand
                over to another - it works on reused points (`points_from`), unlike `along`.
                `deep=(in0, in1, out1, out0, extra)` adds `extra` to the share over a stretch (ABGRUND's
                deepest part, where the code shows through most). `exclude=<another show dict>` drops the
                points that spec keeps, so kick and snare forms can share one set of source points.

`cull` (whole object): dict(camera="Camera", behind=10.0, ahead=150.0) - metres kept behind the
camera's view direction and the maximum distance from it.

The surface must carry float point attributes `lat` and, for `gap`, `along`.
"""
import ast
import math

import bpy


def _tools(ng):
    N, L = ng.nodes, ng.links

    def M(op, a, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def ramp(v, a, b, lo=0.0, hi=1.0):
        n = N.new('ShaderNodeMapRange')
        n.data_type = 'FLOAT'
        n.interpolation_type = 'SMOOTHSTEP'
        L.new(v, n.inputs['Value'])
        n.inputs['From Min'].default_value = a
        n.inputs['From Max'].default_value = b
        n.inputs['To Min'].default_value = lo
        n.inputs['To Max'].default_value = hi
        return n.outputs['Result']

    def rand(lo, hi, seed):
        n = N.new('FunctionNodeRandomValue')
        n.data_type = 'FLOAT'
        # 5.2: one Min / Max / Value socket set that follows data_type (no Min_001 identifiers)
        n.inputs['Min'].default_value = lo
        n.inputs['Max'].default_value = hi
        n.inputs['Seed'].default_value = seed
        return n.outputs['Value']

    return N, L, M, ramp, rand


def _noise_pos(N, L, pos):
    """Position for pattern noises (clumps, show patches, wind), with the lane's step taken out, so lowering a
    stretch of the lane (scene `lane_zshift` = (along0, along1, dz)) moves its plants without reshuffling them."""
    zs = bpy.context.scene.get("lane_zshift")
    if not zs:
        return pos
    al = N.new('GeometryNodeInputNamedAttribute')
    al.data_type = 'FLOAT'
    al.inputs['Name'].default_value = "along"
    mr = N.new('ShaderNodeMapRange')
    mr.clamp = True
    mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = zs[0], zs[1]
    mr.inputs['To Min'].default_value, mr.inputs['To Max'].default_value = 0.0, zs[2]
    L.new(al.outputs[0], mr.inputs['Value'])
    cz = N.new('ShaderNodeCombineXYZ')
    L.new(mr.outputs['Result'], cz.inputs['Z'])
    sub = N.new('ShaderNodeVectorMath')
    sub.operation = 'SUBTRACT'
    L.new(pos, sub.inputs[0])
    L.new(cz.outputs[0], sub.inputs[1])
    return sub.outputs[0]


def _group(name):
    ng = bpy.data.node_groups.get(name) or bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.nodes.clear()
    if not ng.interface.items_tree:
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    return ng


def _object(name, ng, collection):
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        bpy.data.collections[collection].objects.link(ob)
        ob.modifiers.new(name, 'NODES')
    ob.modifiers[0].node_group = ng
    return ob


def build_points(obj_name, surface_name, layers, collection="LANE"):
    """The static half: every layer's points over the whole surface, tagged with `layer` and `rot`."""
    ng = _group(obj_name + "_pts")
    N, L, M, ramp, rand = _tools(ng)
    oi = N.new('GeometryNodeObjectInfo')
    oi.transform_space = 'RELATIVE'
    oi.inputs['Object'].default_value = bpy.data.objects[surface_name]
    src = oi.outputs['Geometry']
    lat = N.new('GeometryNodeInputNamedAttribute')
    lat.data_type = 'FLOAT'
    lat.inputs['Name'].default_value = "lat"
    alat = M('ABSOLUTE', lat.outputs[0])
    pos = N.new('GeometryNodeInputPosition').outputs[0]
    npos = _noise_pos(N, L, pos)
    join = N.new('GeometryNodeJoinGeometry')

    for index, lyr in enumerate(layers):
        a0, a1, b1, b0 = lyr["lat"]
        mask = M('MULTIPLY', ramp(alat, a0, a1), ramp(alat, b1, b0, 1.0, 0.0))
        if lyr.get("gap"):
            # Clearings: stretches along the lane where this layer is thinned out, so light gets in.
            # Every layer using the same freq/offset opens in the same places.
            gp = lyr["gap"]
            al = N.new('GeometryNodeInputNamedAttribute')
            al.data_type = 'FLOAT'
            al.inputs['Name'].default_value = "along"
            gn = N.new('ShaderNodeTexNoise')
            gn.noise_dimensions = '1D'
            gn.inputs['Scale'].default_value = 1.0
            gn.inputs['Detail'].default_value = 0.0
            L.new(M('ADD', M('MULTIPLY', al.outputs[0], gp.get("freq", 0.06)), gp.get("offset", 3.0)), gn.inputs['W'])
            g = ramp(gn.outputs[0], gp.get("lo", 0.52), gp.get("hi", 0.60))
            if gp.get("side"):   # +1 / -1: only thin that side of the lane (sign of `lat`)
                g = M('MULTIPLY', g, M('GREATER_THAN', M('MULTIPLY', lat.outputs[0], gp["side"]), 0.0))
            mask = M('MULTIPLY', mask, M('SUBTRACT', 1.0, M('MULTIPLY', g, gp.get("amount", 1.0))))
        if lyr.get("steep"):
            nz_lo, nz_hi, from_along, floor = lyr["steep"]
            nrm = N.new('GeometryNodeInputNormal')
            sep = N.new('ShaderNodeSeparateXYZ')
            L.new(nrm.outputs[0], sep.inputs[0])
            sa = N.new('GeometryNodeInputNamedAttribute')
            sa.data_type = 'FLOAT'
            sa.inputs['Name'].default_value = "along"
            ok = ramp(sep.outputs['Z'], nz_lo, nz_hi, floor, 1.0)
            gate = ramp(sa.outputs[0], from_along - 20.0, from_along)
            mask = M('MULTIPLY', mask, M('ADD', M('SUBTRACT', 1.0, gate), M('MULTIPLY', gate, ok)))
        def trap(value, q):
            q0, q1, q2, q3 = q
            return M('MULTIPLY', ramp(value, q0, q1), ramp(value, q2, q3, 1.0, 0.0))

        def named(nm):
            na = N.new('GeometryNodeInputNamedAttribute')
            na.data_type = 'FLOAT'
            na.inputs['Name'].default_value = nm
            return na.outputs[0]
        if lyr.get("fade"):
            mask = M('MULTIPLY', mask, trap(named("along"), lyr["fade"]))
        for ring in ([lyr["ring"]] if lyr.get("ring") else []) + list(lyr.get("rings", [])):
            cx, cy = ring[:2]
            dv = N.new('ShaderNodeVectorMath')
            dv.operation = 'DISTANCE'
            L.new(pos, dv.inputs[0])
            ctr = N.new('ShaderNodeCombineXYZ')
            ctr.inputs['X'].default_value = cx
            ctr.inputs['Y'].default_value = cy
            flat = N.new('ShaderNodeVectorMath')
            flat.operation = 'MULTIPLY'
            L.new(pos, flat.inputs[0])
            flat.inputs[1].default_value = (1.0, 1.0, 0.0)
            L.new(flat.outputs[0], dv.inputs[0])
            L.new(ctr.outputs[0], dv.inputs[1])
            mask = M('MULTIPLY', mask, trap(dv.outputs['Value'], ring[2:]))
        if lyr.get("attr"):
            mask = M('MULTIPLY', mask, trap(named(lyr["attr"][0]), lyr["attr"][1:]))
        if lyr.get("above") is not None:
            pz = N.new('ShaderNodeSeparateXYZ')
            L.new(pos, pz.inputs[0])
            z = pz.outputs['Z']
            zs = bpy.context.scene.get("lane_zshift")   # (along0, along1, dz): the lane steps down by dz over that stretch
            if zs:
                za = N.new('GeometryNodeInputNamedAttribute')
                za.data_type = 'FLOAT'
                za.inputs['Name'].default_value = "along"
                zr = N.new('ShaderNodeMapRange')
                zr.clamp = True
                zr.inputs['From Min'].default_value, zr.inputs['From Max'].default_value = zs[0], zs[1]
                zr.inputs['To Min'].default_value, zr.inputs['To Max'].default_value = 0.0, zs[2]
                L.new(za.outputs[0], zr.inputs['Value'])
                z = M('SUBTRACT', z, zr.outputs['Result'])   # height above the lane's own level, not above zero
            mask = M('MULTIPLY', mask, M('GREATER_THAN', z, lyr["above"]))
        if lyr.get("along"):
            a_lo, a_hi = lyr["along"]
            aw = N.new('GeometryNodeInputNamedAttribute')
            aw.data_type = 'FLOAT'
            aw.inputs['Name'].default_value = "along"
            mask = M('MULTIPLY', mask, M('MULTIPLY', M('GREATER_THAN', aw.outputs[0], a_lo), M('LESS_THAN', aw.outputs[0], a_hi)))
        if lyr.get("clump"):
            sc, lo, hi = lyr["clump"]
            nz = N.new('ShaderNodeTexNoise')
            nz.noise_dimensions = '3D'
            nz.inputs['Scale'].default_value = sc
            nz.inputs['Detail'].default_value = 1.0
            off = N.new('ShaderNodeVectorMath')
            off.operation = 'ADD'
            L.new(npos, off.inputs[0])
            off.inputs[1].default_value = (lyr["seed"] * 7.3, lyr["seed"] * 3.1, 0.0)
            L.new(off.outputs[0], nz.inputs['Vector'])
            mask = M('MULTIPLY', mask, ramp(nz.outputs[0], lo, hi))
        dp = N.new('GeometryNodeDistributePointsOnFaces')
        dp.distribute_method = 'RANDOM'
        L.new(src, dp.inputs['Mesh'])
        L.new(M('MULTIPLY', mask, lyr["density"]), dp.inputs['Density'])
        dp.inputs['Seed'].default_value = lyr["seed"]

        tag = N.new('GeometryNodeStoreNamedAttribute')
        tag.data_type = 'INT'
        tag.domain = 'POINT'
        tag.inputs['Name'].default_value = "layer"
        tag.inputs['Value'].default_value = index
        L.new(dp.outputs['Points'], tag.inputs['Geometry'])
        rot = N.new('GeometryNodeStoreNamedAttribute')
        rot.data_type = 'QUATERNION'
        rot.domain = 'POINT'
        rot.inputs['Name'].default_value = "rot"
        L.new(tag.outputs['Geometry'], rot.inputs['Geometry'])
        L.new(dp.outputs['Rotation'], rot.inputs['Value'])
        L.new(rot.outputs['Geometry'], join.inputs[0])

    out = N.new('NodeGroupOutput')
    L.new(join.outputs[0], out.inputs[0])
    ob = _object(obj_name + "_pts", ng, collection)
    ob.hide_render = True
    ob.hide_viewport = True
    ob["layers"] = repr(layers)
    return ob


def _source_index(lyr, source_layers):
    key = lyr["name"]
    for prefix in ("cage_", "light_"):
        if key.startswith(prefix):
            key = key[len(prefix):]
    names = [s["name"] for s in source_layers]
    if key not in names:
        raise KeyError("layer %r has no source layer %r in %r" % (lyr["name"], key, names))
    return names.index(key)


def build_scatter(obj_name, surface_name, layers, collection="LANE", cull=None, points_from=None):
    if points_from:
        pts = bpy.data.objects[points_from + "_pts"]
        source_layers = ast.literal_eval(pts["layers"])
        index_of = [_source_index(lyr, source_layers) for lyr in layers]
    else:
        pts = build_points(obj_name, surface_name, layers, collection)
        index_of = list(range(len(layers)))

    ng = _group(obj_name)
    N, L, M, ramp, rand = _tools(ng)
    oi = N.new('GeometryNodeObjectInfo')
    oi.transform_space = 'RELATIVE'
    oi.inputs['Object'].default_value = pts
    points = oi.outputs['Geometry']
    # Points standing on ground the surface marks `cut` (e.g. the lane inside ABGRUND's landslide) are dropped
    # here, not by deleting surface faces - that would renumber triangles and reshuffle every plant after them.
    cut = N.new('GeometryNodeInputNamedAttribute')
    cut.data_type = 'FLOAT'
    cut.inputs['Name'].default_value = "cut"
    dcut = N.new('GeometryNodeDeleteGeometry')
    dcut.domain = 'POINT'
    L.new(points, dcut.inputs['Geometry'])
    L.new(M('GREATER_THAN', cut.outputs[0], 0.5), dcut.inputs['Selection'])
    points = dcut.outputs['Geometry']
    pos = N.new('GeometryNodeInputPosition').outputs[0]
    npos = _noise_pos(N, L, pos)
    join = N.new('GeometryNodeJoinGeometry')
    scene_time = N.new('GeometryNodeInputSceneTime')
    layer_attr = N.new('GeometryNodeInputNamedAttribute')
    layer_attr.data_type = 'INT'
    layer_attr.inputs['Name'].default_value = "layer"
    rot_attr = N.new('GeometryNodeInputNamedAttribute')
    rot_attr.data_type = 'QUATERNION'
    rot_attr.inputs['Name'].default_value = "rot"

    # Camera window: drop points behind the camera or too far from it, once, before the layers split.
    if cull:
        cam = N.new('GeometryNodeObjectInfo')
        cam.transform_space = 'RELATIVE'
        cam.inputs['Object'].default_value = bpy.data.objects[cull.get("camera", "Camera")]
        fwd = N.new('FunctionNodeRotateVector')
        fwd.inputs['Vector'].default_value = (0.0, 0.0, -1.0)
        L.new(cam.outputs['Rotation'], fwd.inputs['Rotation'])
        rel = N.new('ShaderNodeVectorMath')
        rel.operation = 'SUBTRACT'
        L.new(pos, rel.inputs[0])
        L.new(cam.outputs['Location'], rel.inputs[1])
        dot = N.new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        L.new(rel.outputs[0], dot.inputs[0])
        L.new(fwd.outputs[0], dot.inputs[1])
        ln = N.new('ShaderNodeVectorMath')
        ln.operation = 'LENGTH'
        L.new(rel.outputs[0], ln.inputs[0])
        outside = M('MAXIMUM', M('LESS_THAN', dot.outputs['Value'], -cull.get("behind", 10.0)),
                    M('GREATER_THAN', ln.outputs['Value'], cull.get("ahead", 150.0)))
        dl = N.new('GeometryNodeDeleteGeometry')
        dl.domain = 'POINT'
        L.new(points, dl.inputs['Geometry'])
        L.new(outside, dl.inputs['Selection'])
        points = dl.outputs['Geometry']

    for lyr, src_index in zip(layers, index_of):
        pick = N.new('FunctionNodeCompare')
        pick.data_type = 'INT'
        pick.operation = 'NOT_EQUAL'
        L.new(layer_attr.outputs[0], pick.inputs['A'])
        pick.inputs['B'].default_value = src_index
        mine = N.new('GeometryNodeDeleteGeometry')
        mine.domain = 'POINT'
        L.new(points, mine.inputs['Geometry'])
        L.new(pick.outputs['Result'], mine.inputs['Selection'])
        pts_l = mine.outputs['Geometry']

        def show_keep(sh):
            """(random, probability) for a `show` spec: a point is kept where random <= probability."""
            rv = N.new('FunctionNodeRandomValue')
            rv.data_type = 'FLOAT'
            rv.inputs['Min'].default_value = 0.0
            rv.inputs['Max'].default_value = 1.0
            rv.inputs['Seed'].default_value = sh.get("seed", 900)
            pn = N.new('ShaderNodeTexNoise')
            pn.noise_dimensions = '3D'
            pn.inputs['Scale'].default_value = sh.get("patch_scale", 0.07)
            pn.inputs['Detail'].default_value = 1.0
            L.new(npos, pn.inputs['Vector'])
            prob = ramp(pn.outputs[0], sh.get("patch_lo", 0.52), sh.get("patch_hi", 0.60),
                        sh.get("outside", 0.0), sh.get("inside", 0.3))
            if sh.get("deep"):
                d0, d1, d2, d3, extra = sh["deep"]
                da = N.new('GeometryNodeInputNamedAttribute')
                da.data_type = 'FLOAT'
                da.inputs['Name'].default_value = "along"
                prob = M('ADD', prob, M('MULTIPLY', M('MULTIPLY', ramp(da.outputs[0], d0, d1), ramp(da.outputs[0], d2, d3, 1.0, 0.0)), extra))
            if sh.get("span"):
                s0, s1, s2, s3 = sh["span"]
                sa = N.new('GeometryNodeInputNamedAttribute')
                sa.data_type = 'FLOAT'
                sa.inputs['Name'].default_value = "along"
                prob = M('MULTIPLY', prob, M('MULTIPLY', ramp(sa.outputs[0], s0, s1), ramp(sa.outputs[0], s2, s3, 1.0, 0.0)))
            if sh.get("near"):
                la = N.new('GeometryNodeInputNamedAttribute')
                la.data_type = 'FLOAT'
                la.inputs['Name'].default_value = "lat"
                prob = M('MULTIPLY', prob, ramp(M('ABSOLUTE', la.outputs[0]), sh["near"][0], sh["near"][1]))
            return rv.outputs['Value'], prob

        if lyr.get("show"):
            # Keep only some of the points - for cages, where only part of the world shows its wireframe.
            # `exclude` (another layer's show spec on the same points) drops the points that layer keeps,
            # so two sets of forms never sit on the same object.
            sh = lyr["show"]
            r, prob = show_keep(sh)
            drop = M('GREATER_THAN', r, prob)
            if sh.get("exclude"):
                r2, prob2 = show_keep(sh["exclude"])
                drop = M('MAXIMUM', drop, M('LESS_THAN', r2, M('ADD', prob2, 1e-6)))
            ds = N.new('GeometryNodeDeleteGeometry')
            ds.domain = 'POINT'
            L.new(pts_l, ds.inputs['Geometry'])
            L.new(drop, ds.inputs['Selection'])
            pts_l = ds.outputs['Geometry']

        ci = N.new('GeometryNodeCollectionInfo')
        ci.transform_space = 'ORIGINAL'
        ci.inputs['Collection'].default_value = bpy.data.collections[lyr["collection"]]
        ci.inputs['Separate Children'].default_value = True
        ci.inputs['Reset Children'].default_value = True
        iop = N.new('GeometryNodeInstanceOnPoints')
        L.new(pts_l, iop.inputs['Points'])
        L.new(ci.outputs[0], iop.inputs['Instance'])
        iop.inputs['Pick Instance'].default_value = True
        if not lyr.get("upright", True):
            L.new(rot_attr.outputs[0], iop.inputs['Rotation'])
        L.new(rand(lyr["scale"][0], lyr["scale"][1], lyr["seed"] + 1), iop.inputs['Scale'])

        spin = N.new('ShaderNodeCombineXYZ')
        L.new(rand(0.0, math.tau, lyr["seed"] + 2), spin.inputs['Z'])
        lean = [None, None]
        if lyr.get("tilt"):
            lean = [rand(-lyr["tilt"], lyr["tilt"], lyr["seed"] + 3), rand(-lyr["tilt"], lyr["tilt"], lyr["seed"] + 4)]
        if lyr.get("sway"):
            amp, speed, *more = lyr["sway"]
            flutter = more[0] if more else 0.0
            wn = N.new('ShaderNodeTexNoise')
            wn.noise_dimensions = '4D'
            wn.inputs['Scale'].default_value = 0.12        # gusts ~8 m across
            wn.inputs['Detail'].default_value = 1.0
            L.new(npos, wn.inputs['Vector'])
            L.new(M('MULTIPLY', scene_time.outputs['Seconds'], speed), wn.inputs['W'])
            sep = N.new('ShaderNodeSeparateXYZ')
            L.new(wn.outputs['Color'], sep.inputs[0])
            if flutter:
                # per-plant flutter on top of the gusts: finer noise, 4x the speed
                fn = N.new('ShaderNodeTexNoise')
                fn.noise_dimensions = '4D'
                fn.inputs['Scale'].default_value = 1.5
                fn.inputs['Detail'].default_value = 0.0
                L.new(npos, fn.inputs['Vector'])
                L.new(M('MULTIPLY', M('MULTIPLY', scene_time.outputs['Seconds'], speed), 4.0), fn.inputs['W'])
                fsep = N.new('ShaderNodeSeparateXYZ')
                L.new(fn.outputs['Color'], fsep.inputs[0])
            for i, ax in enumerate(('X', 'Y')):
                w = M('MULTIPLY', M('SUBTRACT', sep.outputs[ax], 0.5), 2.0 * amp)
                if flutter:
                    w = M('ADD', w, M('MULTIPLY', M('SUBTRACT', fsep.outputs[ax], 0.5), flutter))
                lean[i] = w if lean[i] is None else M('ADD', lean[i], w)
        for sock, v in zip(('X', 'Y'), lean):
            if v is not None:
                L.new(v, spin.inputs[sock])
        ri = N.new('GeometryNodeRotateInstances')
        L.new(iop.outputs['Instances'], ri.inputs['Instances'])
        L.new(spin.outputs[0], ri.inputs['Rotation'])
        ri.inputs['Local Space'].default_value = True
        geo = ri.outputs['Instances']
        if lyr.get("sink"):
            ti = N.new('GeometryNodeTranslateInstances')
            L.new(geo, ti.inputs['Instances'])
            if lyr.get("upright", True):
                ti.inputs['Translation'].default_value = (0.0, 0.0, -lyr["sink"])
            else:
                # Things lying on the surface sink along its normal. Straight down (the first version)
                # slid moss and stones along steep walls instead of into them, and they hovered.
                into = N.new('FunctionNodeRotateVector')
                into.inputs['Vector'].default_value = (0.0, 0.0, -lyr["sink"])
                L.new(rot_attr.outputs[0], into.inputs['Rotation'])
                L.new(into.outputs[0], ti.inputs['Translation'])
            ti.inputs['Local Space'].default_value = False
            geo = ti.outputs['Instances']
        L.new(geo, join.inputs[0])

    out = N.new('NodeGroupOutput')
    L.new(join.outputs[0], out.inputs[0])
    ob = _object(obj_name, ng, collection)
    ob["layers"] = repr(layers)
    ob["cull"] = repr(cull)
    ob["points_from"] = points_from or ""
    ob["surface"] = surface_name
    return ob


def rebuild(obj_name, edit=None):
    """Rebuild a scatter from the settings stored on it. `edit(layers)` may change the layer list first."""
    ob = bpy.data.objects[obj_name]
    layers = ast.literal_eval(ob["layers"])
    cull = ast.literal_eval(ob["cull"]) if ob.get("cull") else None
    if edit:
        edit(layers)
    return build_scatter(obj_name, ob["surface"], layers, collection=ob.users_collection[0].name, cull=cull,
                         points_from=ob.get("points_from") or None)


def count_instances(obj_name):
    """Instances per source object, from the evaluated depsgraph."""
    ob = bpy.data.objects[obj_name]
    dg = bpy.context.evaluated_depsgraph_get()
    counts = {}
    for inst in dg.object_instances:
        if inst.is_instance and inst.parent and inst.parent.original == ob:
            counts[inst.object.original.name] = counts.get(inst.object.original.name, 0) + 1
    return counts
