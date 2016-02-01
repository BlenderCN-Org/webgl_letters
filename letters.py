import bpy

def make_letter(letter, **options):
    bpy.ops.object.text_add()
    text_object = bpy.context.object
    text = text_object.data
    
    text.body = letter
    
    text.resolution_u = options.get('resolution', 5)
    text.resolution_v = options.get('resolution', 5)
    
    text.offset = options.get('offset', 0)
    text.extrude = options.get('extrude', 0)
    
    text.bevel_depth = options.get('bevel_depth', 0)
    text.bevel_resolution = options.get('bevel_resolution', 0)
    
    text.size = options.get('size', 1)
    text.shear = options.get('shear', 0)
    
    text.font = options.get('font', bpy.data.fonts[0])
    
    bpy.ops.object.convert(target='MESH')
    
    return text_object


make_letter('gs', resolution=10)