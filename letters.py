import bpy
import bpy_extras
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

def initProperties(scene):
    bpy.types.Scene.webgl_font_filename = bpy.props.StringProperty(
        name = "Font file",
        description = "TTF file from which to get data",
        subtype = "FILE_PATH"
    )
    scene['webgl_font_filename'] = 'epic_font.ttf'
    
    bpy.types.Scene.webgl_font_resolution = bpy.props.IntProperty(
        name = "Resolution",
        description = "Number of subdivisions",
        min = 0,
        max = 15
    )
    scene['webgl_font_resolution'] = 5
    
    bpy.types.Scene.webgl_font_offset = bpy.props.FloatProperty(
        name = "Offset",
        description = "Make letters thinner (lighter) or fatter",
    )
    scene['webgl_font_offset'] = 0.0
    
    bpy.types.Scene.webgl_font_extrude = bpy.props.FloatProperty(
        name = "Extrude depth",
        description = "Depth of letters (0 for flat)",
    )
    scene['webgl_font_extrude'] = 1.0
    
    bpy.types.Scene.webgl_font_bevel_depth = bpy.props.FloatProperty(
        name = "Bevel depth",
        description = "Bevel the edges of letters",
    )
    scene['webgl_font_bevel_depth'] = 0.0
    
    bpy.types.Scene.webgl_font_bevel_resolution = bpy.props.IntProperty(
        name = "Bevel resolution",
        description = "Number of subdivisions on letter edges",
        min = 0,
        max = 15
    )
    scene['webgl_font_bevel_resolution'] = 0
    
    bpy.types.Scene.webgl_font_size = bpy.props.FloatProperty(
        name = "Size",
        description = "Size (scale) of letters",
    )
    scene['webgl_font_size'] = 1.0

    bpy.types.Scene.webgl_font_characters = bpy.props.StringProperty(
        name = "Characters",
        description = "Symbols to include in the font",
    )
    scene['webgl_font_characters'] = \
            'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' + \
            'абвгдежзийклмнопрстуфхцчшщъьюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪѝЮЯ' + \
            '.,;:?! '

    bpy.types.Scene.webgl_font_character_file = bpy.props.StringProperty(
        name = "File with characters",
        description = "File to read characters from (instead of the above field)",
        subtype = "FILE_PATH"
    )
    scene['webgl_font_character_file'] = ''

    bpy.types.Scene.webgl_font_name = bpy.props.StringProperty(
        name = "Object name",
        description = "Javascript object name that will be created",
    )
    scene['webgl_font_name'] = 'uglyFont'

    bpy.types.Scene.webgl_font_export_filename = bpy.props.StringProperty(
        name = "Save to",
        description = "Javascript file to export data to",
        subtype = "FILE_PATH"
    )
    scene['webgl_font_export_filename'] = 'epic_font.js'

initProperties(bpy.context.scene)

class UIPanel(bpy.types.Panel):
    bl_label = "WebGL font generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        self.layout.prop(context.scene, 'webgl_font_filename')
        self.layout.prop(context.scene, 'webgl_font_resolution')
        self.layout.prop(context.scene, 'webgl_font_offset')
        self.layout.prop(context.scene, 'webgl_font_extrude')
        self.layout.prop(context.scene, 'webgl_font_bevel_depth')
        self.layout.prop(context.scene, 'webgl_font_bevel_resolution')
        self.layout.prop(context.scene, 'webgl_font_size')
        self.layout.prop(context.scene, 'webgl_font_characters')
        self.layout.prop(context.scene, 'webgl_font_character_file')
        self.layout.prop(context.scene, 'webgl_font_name')
        self.layout.prop(context.scene, 'webgl_font_export_filename')
        self.layout.operator("webgl_font.generate")
 

class WEBGL_FONT_OT_generate(bpy.types.Operator):
    bl_idname = "webgl_font.generate"
    bl_label = "Generate WebGL font"
    
    def execute(self, context):
        scn = bpy.context.scene

        char_file = scn['webgl_font_character_file']
        if char_file:
            with open(bpy.path.abspath(char_file), 'r') as f:
                characters = f.read()
        else:
            characters = scn['webgl_font_characters']

        json_to_file(make_font(
            characters,
            resolution = scn['webgl_font_resolution'],
            offset = scn['webgl_font_offset'],
            extrude = scn['webgl_font_extrude'],
            bevel_depth = scn['webgl_font_bevel_depth'],
            bevel_resolution = scn['webgl_font_bevel_resolution'],
            size = scn['webgl_font_size'],
            font = bpy.data.fonts.load(scn['webgl_font_filename'])
        ), 
        scn['webgl_font_name'],
        bpy.path.abspath(scn['webgl_font_export_filename'])
)
            
                
        return {'FINISHED'}

bpy.utils.register_module(__name__)

#json_to_file(make_font('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456890.? ', resolution=3, extrude=0.2), 'uglyFont', '/tmp/testfont.js')
