"""MERCY factory cast: 28 deterministic, independently modelled and animated character assets.
Exports editable meshes (named arms/legs and accessories) in GLB, ready for Blender import.
Run: python blender/generate_people.py [assets_dir]
"""
import os,sys,math,random,json
from collections import defaultdict
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals
from trimesh.transformations import translation_matrix
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'../assets')
os.makedirs(OUT,exist_ok=True)
SKIN=['#eec5a7','#c98f70','#996449','#dcb296','#9e735a','#f4d2af','#b98562','#6d493b']
HAIR=['#2a2222','#573a2c','#221f22','#6c4a37','#9b7856','#323737','#4c2c29','#6e5542']
CLOTH={'production':['#245b76','#327f9e','#284a61','#597f91','#235e75'], 'qc':['#ebedec','#dfe9ed','#e8e4d8','#b8ced9'], 'warehouse':['#b45f39','#596c86','#366a5f','#aa6b39','#456e81'], 'admin':['#ede4d4','#68838b','#b98b82','#8395a1','#bec0aa'], 'supervisor':['#293b50','#2c5765'], 'driver':['#525f69','#38586a'], 'guard':['#525c67','#354653'], 'you':['#d47e38']}
JOBS=['production']*12+['warehouse']*5+['admin']*4+['supervisor']*2+['driver']*2+['guard']*2+['you']*1
N=len(JOBS)
TITLES=['Operator Tridaya 1','Operator Tridaya 2','Operator Tridaya 3','QC Tridaya','Operator Inna 1','Operator Inna 2','Operator Inna 3','QC Inna','Operator KBI 1','Operator KBI 2','Operator KBI 3','QC KBI','Logistik A','Logistik B','Penyusun Rak','Pemeriksa Barang','Petugas Packing','Admin PO','Admin Data','Staf Laporan','Staf Arsip','Supervisor Barat','Supervisor Timur','Sopir Truk','Operator Forklift','Petugas Keamanan','Petugas Kebersihan','Kamu']
MANIFEST=[]
def rgba(color):
 color=color.lstrip('#'); return [int(color[i:i+2],16) for i in (0,2,4)]+[255]
def smooth_mesh(m):
 return m

def cube(w,h,d,p=(0,0,0)):
 m=trimesh.creation.box(extents=(w,h,d));m.apply_translation(p);return m

def ball(r,p=(0,0,0),sub=2):
 m=trimesh.creation.icosphere(subdivisions=sub,radius=r);m.apply_translation(p);return m

def cylinder(radius,height,p=(0,0,0),section=14,axis='y'):
 m=trimesh.creation.cylinder(radius=radius,height=height,sections=section)
 if axis=='y':m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]))
 elif axis=='x':m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[0,1,0]))
 m.apply_translation(p);return m

def beam(a,b,r,sections=8):
 a=np.array(a);b=np.array(b);dv=b-a;h=np.linalg.norm(dv)
 m=trimesh.creation.cylinder(radius=r,height=h,sections=sections)
 m.apply_transform(trimesh.geometry.align_vectors([0,0,1],dv/h));m.apply_translation((a+b)/2);return m

def tapered(ymin,ymax,r_bottom,r_top,axis='y',segments=14):
 v=[];f=[]
 for y,r in [(ymin,r_bottom),(ymax,r_top)]:
  for n in range(segments):
   a=n/segments*2*math.pi;v.append((math.cos(a)*r,y,math.sin(a)*r))
 for i in range(segments):
  k=(i+1)%segments;f.extend([[i,k,segments+k],[i,segments+k,segments+i]])
 v.extend([(0,ymin,0),(0,ymax,0)])
 for i in range(segments):
  k=(i+1)%segments;f.extend([[2*segments,k,i],[2*segments+1,segments+i,segments+k]])
 return trimesh.Trimesh(vertices=v,faces=f,process=False)

for ident,job in enumerate(JOBS):
 rng=random.Random(81618+ident*617)
 skin=SKIN[(ident*5+ident//3)%len(SKIN)];hair=HAIR[(ident*7+ident//2)%len(HAIR)]
 role='qc' if ident in (3,7,11) else job
 jacket=CLOTH.get(role,CLOTH['production'])[(ident+ident//3)%len(CLOTH.get(role,CLOTH['production']))]
 pants=['#32424b','#374653','#53544f','#4b565e','#3d5668','#65534c'][(ident*3+ident//4)%6]
 shoes=['#33373c','#4a4140','#453b35','#414a4c'][ident%4]
 vest='#dde43f' if role in ('supervisor','warehouse','guard') else '#efc64f' if role=='you' else '#8dc9c1'
 visor=role not in ('admin',)
 helmet=role in ('production','qc','warehouse','supervisor','driver','guard','you')
 helmetcolor=('#faf2c3' if role in ('supervisor','qc') else '#f5c44e' if role=='warehouse' else '#7bb6cc' if role=='production' else '#e4ded6' if role=='guard' else '#e99044' if role=='you' else '#dfbc66')
 glasses=ident in (1,4,7,12,15,18,19,21,25,27)
 facialhair=ident in (2,6,9,13,14,22,23,25)
 female=ident in (1,3,5,7,10,11,16,18,19,20,24)
 bodyw=(.64+.12*rng.random())*(.84 if female else 1.05)
 scale=(.91 +rng.random()*.16) if role!='you' else 1.0
 wide=bodyw
 sh=1.43
 scene=trimesh.Scene()
 static_parts=defaultdict(list)
 animated_parts={'Arm_Left','Arm_Right','Leg_Left','Leg_Right','Hand_Left','Hand_Right','Boot_Left','Boot_Right'}
 def add(name,mesh,color,pivot=(0,0,0),rough=.79,metal=.01):
  # Arms, legs, hands and boots remain rig nodes; static accessories are batched
  # by material to keep draw calls manageable on mobile GPUs.
  if name in animated_parts:
   mesh.visual=TextureVisuals(material=PBRMaterial(baseColorFactor=rgba(color),roughnessFactor=rough,metallicFactor=metal,name=name+'_'+color[1:]))
   scene.add_geometry(mesh,geom_name=name,node_name=name,transform=translation_matrix(pivot))
  else:
   mesh.apply_translation(pivot)
   static_parts[color].append(mesh)
 # legs hip pivot = 0.9 world y
 for side in ('Left','Right'):
  sign=-1 if side=='Left' else 1
  px=sign*.19
  parts=[cylinder(.155,.64,(0,-.27,0)),ball(.159,(0,-.62,0))]
  leg=trimesh.util.concatenate(parts)
  add('Leg_'+side,leg,pants,(px,.84,0))
  add('Boot_'+side,cube(.30,.17,.47,(px,.15,.11)),shoes)
 # torso: layered tapered shapes, curving shoulders and neck
 add('Torso',cube(wide,.74,.38,(0,1.24,0)),jacket)
 add('Hips',ball(.29,(0,.91,0)),pants)
 add('Collar',cylinder(.17,.18,(0,1.66,0)),jacket)
 add('Neck',cylinder(.115,.18,(0,1.72,0)),skin)
 # jacket seam, shirt / overall strips
 add('Jacket_Center',cube(.032,.58,.015,(0,1.26,.202)),'#d5d1bb')
 add('Jacket_Pocket_Left',cube(.16,.10,.028,(-.19,1.33,.211)),'#bfc8bb')
 add('Jacket_Pocket_Right',cube(.16,.10,.028,(.19,1.33,.211)),'#bfc8bb')
 if role in ('production','warehouse','supervisor','guard','you'):
  add('Reflective_Left',cube(.10,.57,.039,(-.23,1.31,.227)),vest)
  add('Reflective_Right',cube(.10,.57,.039,(.23,1.31,.227)),vest)
  add('Reflective_Belt',cube(.58,.069,.044,(0,1.17,.223)),vest)
 # articulated sleeves and gloves; relative meshes anchored at shoulder pivot
 for side in ('Left','Right'):
  sx=(-1 if side=='Left' else 1)*(wide/2+.09)
  pivot=(sx,1.56,0)
  arm=cylinder(.146,.43,(0,-.24,0))
  hand=ball(.133,(0,-.57,0))
  parts=trimesh.util.concatenate([arm,hand])
  add('Arm_'+side,parts,jacket,pivot)
  add('Hand_'+side,ball(.105,(sx,1.00,.003)),skin)
 # head elongated sphere; random face shapes but no cloning
 head=ball(.36,(0,1.95,0),2)
 head.apply_scale((.89+(.05*rng.random()),1.12,.84))
 add('Head',head,skin)
 add('Nose',ball(.058,(0,1.96,.326)),skin)
 for sign in (-1,1):
  add(('EarLeft' if sign<0 else 'EarRight'),ball(.086,(sign*.34,1.94,0)),skin)
  if glasses:
   add(('GlassLeft' if sign<0 else 'GlassRight'),cylinder(.118,.024,(sign*.144,2.015,.315),18,'z'),'#293139',rough=.29)
   add(('GlassLensLeft' if sign<0 else 'GlassLensRight'),cylinder(.096,.028,(sign*.144,2.017,.334),18,'z'),'#adc5ca',rough=.11)
  else:
   add(('EyeLeft' if sign<0 else 'EyeRight'),ball(.029,(sign*.131,2.027,.314),2),'#242a2a')
   add(('BrowLeft' if sign<0 else 'BrowRight'),cube(.106,.019,.024,(sign*.134,2.103,.327)),hair)
 add('Mouth',cube(.13,.017,.021,(0,1.823,.307)),'#875e56')
 if facialhair:add('Beard',ball(.175,(0,1.756,.136)),HAIR[(ident*3+2)%len(HAIR)]) 
 # hairstyle unique by hairstyle type; helmets do not hide all hair at temples
 style=ident%7
 if (not helmet) or style==3:
  if style%3==0:
   add('HairPart',ball(.335,(0,2.219,-.025),2),hair)
   for k in range(3):add('HairStrand'+str(k),ball(.105,(-.19+k*.19,2.25,.19)),hair)
  elif style%3==1:
   add('SideHairL',ball(.17,(-.26,2.10,-.09)),hair)
   add('SideHairR',ball(.17,(.26,2.10,-.09)),hair)
   add('HairCrown',ball(.30,(0,2.26,-.05)),hair)
  else:
   for k in range(7):
    a=k*2*math.pi/7
    add('Curl'+str(k),ball(.13,(math.cos(a)*.20,2.26,math.sin(a)*.16)),hair)
 else:
  add('HairBehind',ball(.25,(0,2.17,-.19)),hair)
 if helmet:
  add('HardHat_Crown',ball(.40,(0,2.31,-.035),2),helmetcolor)
  add('HardHat_Brim',cube(.87,.080,.75,(0,2.227,.12)),helmetcolor)
  add('HardHat_Strap',cube(.023,.14,.01,(.31,2.05,.14)),'#46494a')
 if role in ('qc','supervisor'):
  add('Clipboard',cube(.26,.42,.05,(-.43,.78,.29)),'#a18458')
  add('Clipboard_Paper',cube(.215,.35,.055,(-.43,.785,.323)),'#f6efdb')
 if role in ('admin',):
  add('Badge',cube(.14,.14,.015,(.23,1.45,.23)),'#ede4d4')
  add('Badge_Strip',cube(.12,.023,.02,(.23,1.425,.246)),'#347b9a')
 if ident in (12,14,15,16):
  add('Toolbag',cube(.35,.28,.24,(.49,.90,.16)),'#a66b37')
  add('Toolbag_Handle',beam((.32,1.07,.18),(.66,1.07,.18),.025),'#4b423d')
 if role=='guard':
  add('Radio',cube(.15,.28,.1,(.32,1.38,.08)),'#2a383d')
 if role=='you':
  add('Armband',cube(.20,.12,.04,(.43,1.38,.1)),'#f4d94b')
  add('Headset',beam((-.34,2.2,.0),(.34,2.2,.0),.032),'#222c32')
 # Convert all non-articulated body components into color-batched meshes.
 for batchid,(color,meshes) in enumerate(static_parts.items()):
  merged=trimesh.util.concatenate(meshes)
  merged.visual=TextureVisuals(material=PBRMaterial(baseColorFactor=rgba(color),roughnessFactor=.78,metallicFactor=.02,name='CLOTHING_'+color[1:]))
  scene.add_geometry(merged,geom_name='SkinClothing_'+str(batchid),node_name='SkinClothing_'+str(batchid))
 # all characters have color/accessories/body proportions/face combination unique
 # scale scene by editing vertex geometries relative to origin without altering node hierarchy
 if scale!=1:
  for node_name in list(scene.graph.nodes_geometry):
   matrix,geomname=scene.graph.get(node_name)
   sc=translation_matrix((0,0,0));sc[:3,:3]*=scale
   scene.graph.update(frame_to=node_name,matrix=sc@matrix)
 path=os.path.join(OUT,f'mercy_person_{ident:02d}.glb')
 with open(path,'wb') as f:f.write(trimesh.exchange.gltf.export_glb(scene,include_normals=True))
 MANIFEST.append({'id':ident,'title':TITLES[ident],'role':role,'height':round(scale,3),'file':f'mercy_person_{ident:02d}.glb','uniform':jacket,'skin':skin,'glasses':glasses,'helmet':helmet})
print(f'Exported {N} individual GLB miniature workers')
with open(os.path.join(OUT,'mercy_people_manifest.json'),'w') as fp:json.dump(MANIFEST,fp,ensure_ascii=False,indent=2)
