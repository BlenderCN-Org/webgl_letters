import bpy

def object_width(object):
    bpy.context.scene.update()
    return object.dimensions.x

def make_letter(letter, **options):
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
    
    return (text_object, width)


print(make_letter('Q', resolution=10))