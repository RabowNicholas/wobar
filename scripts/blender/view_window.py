"""Draw only the stretch of a big static mesh that is near the camera.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns)
    ns["window"]("Lane")            # -> LaneView, and Lane stops rendering
    ns["window"]("ForestFloor")

The source object keeps building the full-length mesh (the scatter points read it, and it is static,
so Blender evaluates it once). It is hidden from render; a `<name>View` object reads it each frame and
deletes everything behind the camera or beyond `ahead` metres. The ground for the whole lane was being
drawn in every pass of every frame: 7.0 s per frame on the 100 m proof, 8.6 s at 1 km, 10.4 s at 2 km.
"""
import bpy

def _group(name, source, camera, behind, ahead):
    # One group per source, with the objects and distances set on the nodes. (Setting a modifier's
    # group inputs by `mod[identifier] = value` raises "id properties not supported" in 5.2.)
    ng = bpy.data.node_groups.get(name) or bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.nodes.clear()
    if not ng.interface.items_tree:
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    go = N.new('NodeGroupOutput')
    src = N.new('GeometryNodeObjectInfo')
    src.transform_space = 'RELATIVE'
    src.inputs['Object'].default_value = source
    cam = N.new('GeometryNodeObjectInfo')
    cam.transform_space = 'RELATIVE'
    cam.inputs['Object'].default_value = camera
    pos = N.new('GeometryNodeInputPosition')
    fwd = N.new('FunctionNodeRotateVector')
    fwd.inputs['Vector'].default_value = (0.0, 0.0, -1.0)
    L.new(cam.outputs['Rotation'], fwd.inputs['Rotation'])
    rel = N.new('ShaderNodeVectorMath')
    rel.operation = 'SUBTRACT'
    L.new(pos.outputs[0], rel.inputs[0])
    L.new(cam.outputs['Location'], rel.inputs[1])
    dot = N.new('ShaderNodeVectorMath')
    dot.operation = 'DOT_PRODUCT'
    L.new(rel.outputs[0], dot.inputs[0])
    L.new(fwd.outputs[0], dot.inputs[1])
    ln = N.new('ShaderNodeVectorMath')
    ln.operation = 'LENGTH'
    L.new(rel.outputs[0], ln.inputs[0])
    behind_n = N.new('ShaderNodeMath')
    behind_n.operation = 'LESS_THAN'
    L.new(dot.outputs['Value'], behind_n.inputs[0])
    behind_n.inputs[1].default_value = -behind
    far = N.new('ShaderNodeMath')
    far.operation = 'GREATER_THAN'
    L.new(ln.outputs['Value'], far.inputs[0])
    far.inputs[1].default_value = ahead
    out = N.new('ShaderNodeMath')
    out.operation = 'MAXIMUM'
    L.new(behind_n.outputs[0], out.inputs[0])
    L.new(far.outputs[0], out.inputs[1])
    dl = N.new('GeometryNodeDeleteGeometry')
    dl.domain = 'FACE'
    # a face goes only when all of its corners are outside, so the cut edge never opens a hole
    fsel = N.new('GeometryNodeFieldOnDomain') if hasattr(bpy.types, 'GeometryNodeFieldOnDomain') else None
    if fsel:
        fsel.domain = 'FACE'
        fsel.data_type = 'BOOLEAN'
        L.new(out.outputs[0], fsel.inputs[0])
        L.new(fsel.outputs[0], dl.inputs['Selection'])
    else:
        L.new(out.outputs[0], dl.inputs['Selection'])
    L.new(src.outputs['Geometry'], dl.inputs['Geometry'])
    L.new(dl.outputs['Geometry'], go.inputs['Geometry'])
    return ng


def window(source_name, camera="Camera", behind=25.0, ahead=200.0):
    src = bpy.data.objects[source_name]
    name = source_name + "View"
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, bpy.data.meshes.new(name))
        src.users_collection[0].objects.link(ob)
        ob.modifiers.new("ViewWindow", 'NODES')
    ob.modifiers[0].node_group = _group("ViewWindow_" + source_name, src, bpy.data.objects[camera], behind, ahead)
    for attr in ("visible_shadow", "hide_probe_plane", "hide_probe_volume", "hide_probe_sphere", "visible_camera"):
        setattr(ob, attr, getattr(src, attr))
    src.hide_render = True
    return ob
