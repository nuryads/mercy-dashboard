"""Create MERCY_Factory_World.blend with an editable 3D diorama and cinematic keyframes.
Needs the real Blender executable (3.6+); run as:
  blender --background --python blender/build_blend.py -- /path/to/project
This script runs INSIDE Blender, not in regular Python. Nothing touches Firebase.
"""
import bpy, os, sys, math
from mathutils import Vector

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
root=os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__),'..'))
assets=os.path.join(root,'assets')
output=os.path.join(root,'MERCY_Factory_World.blend')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.film_transparent=False
scene.frame_start=1
scene.frame_end=520
scene.render.fps=24

studio=bpy.data.collections.new('MERCY | MINIATURE FACTORY')
scene.collection.children.link(studio)

controls={}
for filename,display in [
 ('mercy_factory_diorama.glb','FACILITY'),
 ('mercy_truck.glb','DELIVERY_TRUCK'),
 ('mercy_forklift.glb','FORKLIFT'),
 ('mercy_worker.glb','REPORT_WORKER')
]:
    path=os.path.join(assets,filename)
    if not os.path.isfile(path):raise FileNotFoundError('Missing model: '+path)
    seen=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    imported=[obj for obj in bpy.data.objects if obj not in seen]
    layer=bpy.data.collections.new('ASSET | '+display)
    studio.children.link(layer)
    for obj in imported:
        for col in list(obj.users_collection):col.objects.unlink(obj)
        layer.objects.link(obj)
        if obj.type=='MESH':
            for polygon in obj.data.polygons:polygon.use_smooth=False
    if display!='FACILITY':
        controller=bpy.data.objects.new('CTRL_'+display,None)
        layer.objects.link(controller)
        controller.empty_display_type='SPHERE';controller.empty_display_size=.4
        for obj in imported:
            if obj.parent is None:
                mat=obj.matrix_world.copy()
                obj.parent=controller
                obj.matrix_world=mat
        controls[display]=controller
    print('IMPORTED',display,len(imported),'objects')

# In GLB up is Y and screen space is X/Z. Blender glTF importer converts GLB Z -> Blender -Y.
# For any route point (x,z) in the browser scene, its Blender coordinate is (x,-z,0).
def key_route(controller,waypoints,heading='truck'):
    """Waypoints are (seconds, X, Z) in browser-world coordinates."""
    previous=None
    for i,(seconds,x,z) in enumerate(waypoints):
        frame=round(seconds*24)+1
        controller.location=(x,-z,0.0)
        if i+1<len(waypoints):
            dx=waypoints[i+1][1]-x; dz=waypoints[i+1][2]-z
        elif previous:
            dx=x-previous[1];dz=z-previous[2]
        else:dx=-1;dz=0
        if abs(dx)+abs(dz)>.0001:
            # Truck mesh nose local -X, forklift local +X, worker local +Z.
            if heading=='truck':theta=math.pi-math.atan2(dz,dx)
            elif heading=='forklift':theta=math.atan2(-dz,dx)
            else:theta=math.atan2(-dz,dx)-math.pi/2
            controller.rotation_euler=(0,0,theta)
        controller.keyframe_insert(data_path='location',frame=frame)
        controller.keyframe_insert(data_path='rotation_euler',frame=frame)
        previous=(seconds,x,z)
    if controller.animation_data and controller.animation_data.action:
        action=controller.animation_data.action
        try:
            for fcurve in action.fcurves:
                for p in fcurve.keyframe_points:p.interpolation='LINEAR'
        except AttributeError:
            # Blender 4.x/5.x Actions API may wrap curves in slots; default Bezier remains valid.
            pass

# Filmable safe routes: truck arrives, forklift unloads, office worker prints.
key_route(controls['DELIVERY_TRUCK'],[
 (0,36.5,1.4),(2.0,27,1.4),(4,17,1.4),(5.4,12,1.4),
 (7.0,9.7,2.3),(8.1,7.4,4.55),(9.25,7.3,7.0),(11.0,7.3,11.1),
 (20,7.3,11.1)],'truck')
key_route(controls['FORKLIFT'],[
 (0,17.0,14.9),(11.5,17.0,14.9),(12.3,14.0,14.9),
 (13.5,11.45,14.9),(14.6,9.73,13.4),
 (15.3,9.73,13.4),(16.6,11.45,14.9),(17.7,14.0,14.9),
 (18.6,17.0,14.9),(20,17.0,14.9)],'forklift')
key_route(controls['REPORT_WORKER'],[
 (0,-19,7.8),(1.6,-19,9.2),(3,-19,10.2),
 (4,-17.45,10.2),(6,-17.45,16.2),(7.3,-15.9,16.2),
 (14,-15.9,16.2)],'worker')

# Studio lighting, soft pastel atmosphere, orthographic miniature camera.
camera_data=bpy.data.cameras.new('Isometric • Studio Camera')
camera=bpy.data.objects.new('Isometric • Studio Camera',camera_data)
scene.collection.objects.link(camera)
camera.location=(64,-84,76)
camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';camera_data.ortho_scale=80
scene.camera=camera

def area(name,loc,power,size,rgb):
    datablock=bpy.data.lights.new(name,'AREA')
    datablock.energy=power;datablock.shape='DISK';datablock.size=size;datablock.color=rgb
    light=bpy.data.objects.new(name,datablock);scene.collection.objects.link(light)
    light.location=loc;light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat('-Z','Y').to_euler()

area('Key | warm softbox',(-26,-39,66),7500,44,(1.0,.89,.77))
area('Fill | cool studio',(39,30,64),4600,48,(.79,.94,1.0))
world=bpy.data.worlds.new('MERCY Studio • daylight')
scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.82,.93,.88,1)
bg.inputs['Strength'].default_value=.85
try:scene.render.engine='BLENDER_EEVEE_NEXT'
except Exception:scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1920;scene.render.resolution_y=1280
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(root,'MERCY_Factory_World_Render.png')
try:scene.view_settings.view_transform='AgX'
except Exception:pass
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=output,check_existing=False)
print('CREATED BLENDER PROJECT',output)
print('Timeline 1..520 frames, 24 fps. Scrub frames to watch truck, forklift and office worker.')
