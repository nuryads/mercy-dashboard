"""Build an editable Blender project from all 31 GLB assets of MERCY Factory Studio V6.

Run in Blender 3.6+ or 4.x:
    blender --background --python blender/build_blend.py -- /absolute/path/to/MERCY-FACTORY-REALISM-V6
or open Blender -> Scripting -> Run Script (pass folder via -- if required).

Creates MERCY_Factory_Studio_V6.blend in the project directory.
No Firebase/account data is accessed or changed.
"""
import bpy, os, math, sys
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
root = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__), '..'))
assets = os.path.join(root, 'assets')
out = os.path.join(root, 'MERCY_Factory_Studio_V6.blend')

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
sc = bpy.context.scene
sc.frame_start, sc.frame_end, sc.render.fps = 1, 1200, 24
sc.render.resolution_x, sc.render.resolution_y = 1920, 1200
sc.render.resolution_percentage = 100
try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: sc.render.engine = 'BLENDER_EEVEE'
try: sc.view_settings.view_transform = 'AgX'
except Exception: pass

def import_asset(file, title, make_controller=True):
    path = os.path.join(assets, file)
    if not os.path.isfile(path): raise FileNotFoundError(path)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o not in before]
    collection = bpy.data.collections.new('MODEL | ' + title)
    sc.collection.children.link(collection)
    for obj in objs:
        for owner in list(obj.users_collection): owner.objects.unlink(obj)
        collection.objects.link(obj)
    if not make_controller: return None
    empty = bpy.data.objects.new('CTRL | ' + title, None)
    collection.objects.link(empty)
    empty.empty_display_type = 'CIRCLE'
    empty.empty_display_size = .55
    for obj in objs:
        if obj.parent is None:
            transform = obj.matrix_world.copy()
            obj.parent = empty
            obj.matrix_world = transform
    return empty

import_asset('mercy_factory_diorama.glb', 'FACILITY', False)
truck = import_asset('mercy_truck.glb', 'TRUCK')
forklift = import_asset('mercy_forklift.glb', 'FORKLIFT')
coords = [(-22,-16.3),(-16.5,-16.3),(-21,-11.3),(-16,-11.5),
          (-3.2,-16.3),(3.2,-16.3),(-3,-11.2),(2.9,-11.2),
          (15.8,-16.3),(21.8,-16.3),(15.7,-11.3),(21.3,-11.5),
          (12.7,18.4),(17.5,18.0),(21.5,18.5),(26,18.2),(24,12.6),
          (-23.4,15),(-20.2,14.8),(-22,12),(-14.5,15),
          (-8,-6.5),(8,-6.5),(6,1),(15.2,14),(30,6.5),(-29,6.2),(0,-4.6)]
roles = ['Operator T1','Operator T2','Operator T3','QC T','Operator I1','Operator I2',
         'Operator I3','QC I','Operator K1','Operator K2','Operator K3','QC K',
         'Warehouse A','Warehouse B','Racking','Inspector','Packing',
         'Admin 1','Admin 2','Report','Archive','Supervisor 1','Supervisor 2',
         'Truck Driver','Forklift Driver','Guard','Cleaner','KAMU']
people=[]
for i,(x,z) in enumerate(coords):
    worker=import_asset('mercy_person_%02d.glb' % i, 'PERSON %02d | %s' % (i,roles[i]))
    worker.location = (x,-z,0)
    people.append(worker)

# In Blender GLTF assets are Z-up, and browser-world (X,Y,Z) maps to (X,-Z,Y).
def kf_path(obj, stops, facing=-1):
    for j,(sec,x,z) in enumerate(stops):
        frame = round(sec*sc.render.fps)+1
        obj.location = (x,-z,0)
        if j+1 < len(stops):
            nx,nz=stops[j+1][1:]
        elif j: nx,nz=stops[j-1][1:]
        else:nx,nz=x+1,z
        dx,dz = (nx-x,nz-z) if j+1<len(stops) else (x-nx,z-nz)
        if abs(dx)+abs(dz)>.0001:
            obj.rotation_euler = (0,0,math.atan2(-dz,dx)+(math.pi if facing<0 else 0))
        obj.keyframe_insert(data_path='location',frame=frame)
        obj.keyframe_insert(data_path='rotation_euler',frame=frame)
    ad=obj.animation_data
    if ad and ad.action:
        try:
            for c in ad.action.fcurves:
                for k in c.keyframe_points: k.interpolation='LINEAR'
        except (AttributeError,TypeError):pass

kf_path(truck, [(0,36.8,1.4),(3,28,1.4),(6,17,1.4),(8.5,10,1.4),
                (10,7.3,5.5),(13.5,7.3,11.05),(23,7.3,11.05),
                (34,7.3,11.05),(37.5,7.3,5.5),(39.5,10,1.4),
                (44,22,1.4),(50,36.8,1.4)])
kf_path(forklift,[(0,17,14.9),(15,17,14.9),(18,13,14.9),
                  (21,9.74,13.55),(26,9.74,13.55),
                  (30,13,14.9),(36,17,14.9)],1)
kf_path(people[-1],[(0,0,-4.6),(3,0,-5.65),(8,-7,-5.65),
                    (12,-7,4.65),(16,-19,6.15),(20,-19,14.7),(25,-19,14.7)],1)

# Independent looping patrols for active workers.
for idx,stops in [(2,[(-21,-11.3),(-20.7,-10.1),(-19.8,-10.1)]),
                  (5,[(3.2,-16.3),(3.2,-15.35),(2.7,-14.9)]),
                  (10,[(15.7,-11.3),(16.1,-10.2),(17,-10.2)]),
                  (12,[(12.7,18.4),(12.7,17.7),(13.3,17.3)]),
                  (14,[(21.5,18.5),(21.4,19.7),(22,20.1)]),
                  (19,[(-22,12),(-20.5,11.9),(-18.3,12),(-16.3,15.3)]),
                  (21,[(-8,-6.5),(-5,-6.5),(-3.1,-6.5)]),
                  (22,[(8,-6.5),(5.3,-6.5),(3.9,-6.5)])]:
    kf_path(people[idx],[(1,*stops[0]),(10,*stops[-1]),(15,*stops[-1]),(24,*stops[0])],1)

cam_data=bpy.data.cameras.new('Orthographic Isometric Camera')
cam=bpy.data.objects.new('CAMERA | Factory Overview',cam_data)
sc.collection.objects.link(cam);cam.location=(65,-76,81)
cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO';cam_data.ortho_scale=87;sc.camera=cam

def softbox(name,position,energy,rgb,size):
    light=bpy.data.lights.new(name,'AREA')
    light.energy=energy;light.shape='DISK';light.size=size
    light.color=rgb
    obj=bpy.data.objects.new(name,light);sc.collection.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector((0,0,0))-obj.location).to_track_quat('-Z','Y').to_euler()
softbox('Warm key light',(-34,-49,80),9500,(1,.88,.73),45)
softbox('Cool ambient fill',(35,30,65),5600,(.76,.89,1),50)
world=bpy.data.worlds.new('Studio daylight')
sc.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.78,.89,.87,1)
bg.inputs['Strength'].default_value=.83
sc.render.image_settings.file_format='PNG'
sc.render.filepath=os.path.join(root,'previews','Blender-render.png')
sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=out,check_existing=False)
print('Saved',out)
print('Imported 28 separate people plus facility, truck and forklift. Use Timeline to explore animations.')
