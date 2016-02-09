import bpy
import json
import bmesh

def object_width(object):
    bpy.context.scene.update()
    return object.dimensions.x

def triangulate(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

def build_letter_object(letter, **options):
    bpy.ops.object.text_add()
    text_object = bpy.context.object
    text = text_object.data
    
    text.resolution_u = options.get('resolution', 5)
    text.resolution_v = options.get('resolution', 5)
    
    text.offset = options.get('offset', 0)
    text.extrude = options.get('extrude', 0)
    
    text.bevel_depth = options.get('bevel_depth', 0)
    text.bevel_resolution = options.get('bevel_resolution', 0)
    
    text.size = options.get('size', 1)
    text.shear = options.get('shear', 0)
    
    text.font = options.get('font', bpy.data.fonts[0])
    
    padding = options.get('width_padding', 'gs')
    
    text.body = padding + padding
    padding_width = object_width(text_object)
    
    text.body = padding + letter + padding
    width = object_width(text_object) - padding_width
    
    text.body = letter
    
    bpy.ops.object.convert(target='MESH')
    if text_object.type != 'MESH':
        # unprintable character
        return (None, width)
    
    triangulate(text_object.data)
    
    return (text_object, width)

def make_vertex(mesh, face, index):
    vertex = mesh.vertices[mesh.loops[index].vertex_index]
    uv_layer = mesh.uv_layers.active
    data = {
        'point': list(vertex.co),
    }
    if face.use_smooth:
        data['normal'] = list(vertex.normal)
    if uv_layer:
        data['uv'] = list(uv_layer.data[index].uv)
    return data

def make_simple_vertex(mesh, face, index):
    vertex = mesh.vertices[mesh.loops[index].vertex_index]

    return list(vertex.co)

def make_face(mesh, face):
    face_vertices = face.loop_indices
    if (len(face_vertices) != 3):
        print("Warning: face is not a triangle")
    return [make_simple_vertex(mesh, face, index) for index in face_vertices]


def make_mesh(mesh):
    return [make_face(mesh, face) for face in mesh.polygons]

def make_letter(letter, **options):
    letter_object, width = build_letter_object(letter, **options)
    if letter_object:
        mesh = make_mesh(letter_object.data)
    else:
        mesh = []
    
    bpy.ops.object.delete()
    
    letter_data = {
        'kerning_width': width,
        'mesh': mesh
    }
    return (letter, letter_data)

def make_font(letters, **options):
    return dict([make_letter(letter, **options) for letter in letters])

def json_to_file(data, name, file):
    with open(file, 'w') as f:
        f.write("registerFont('" + name + "',")
        json.dump(data, f, separators=(',', ':'))
        f.write(");\n")

    

json_to_file(make_font('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456890.? ', resolution=3, extrude=0.2), 'uglyFont', '/tmp/testfont.js')