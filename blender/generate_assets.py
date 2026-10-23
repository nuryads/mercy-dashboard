"""MERCY factory diorama mesh source. Produces proper editable glTF meshes.
Run: python generate_assets.py [output/assets directory]
Needs: trimesh, numpy. Coordinates Y-up, dimensions in scene units.
"""
from __future__ import annotations
import sys, math, random, os
from collections import defaultdict
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
from PIL import Image, ImageDraw, ImageFont
from trimesh.visual.texture import TextureVisuals

random.seed(28)
DEST=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(__file__),'../assets')
os.makedirs(DEST,exist_ok=True)
COLORS={
 'mint':'#92cbbb','grass':'#91c7a3','grass2':'#80b993','edge':'#688d84','asphalt':'#63757c','roadEdge':'#81969b',
 'line':'#f6ebbd','concrete':'#e4dbca','concrete2':'#c6c7bc','tile':'#eee7dc','white':'#f8f5ed','cream':'#f0e4cc','light':'#f8eee0',
 'stone':'#bac7c6','wall':'#cadbd5','wall2':'#c3d7d9','teal':'#47998f','teal2':'#6eb7a9','blue':'#7fb7d3',
 'navy':'#325a72','sky':'#b4dde4','orange':'#e4a467','gold':'#e5c372','yellow':'#f3d794','peach':'#efbe9c',
 'pink':'#d7a1a4','wood':'#b68e65','wood2':'#d1af84','cardboard':'#ba936e','cardboard2':'#d4b18c',
 'boxgreen':'#8fb89a','boxblue':'#92afc2','boxorange':'#d6ae80','ink':'#3e5560','black':'#353b41',
 'steel':'#76868a','darksteel':'#596c72','silver':'#c7d6d7','glass':'#a9d9d7','plant':'#447d61','plant2':'#60976f',
 'tree':'#588965','tree2':'#78a776','soil':'#9a8866','red':'#d77c77','shadow':'#729e8e','water':'#82b9bd',
 'lavender':'#b5afd3','lightgrey':'#dfe6e2','lamp':'#f4e5ac','darkblue':'#44647b', 'gray':'#8a9296'
}

class Builder:
 def __init__(self):
  self.buckets=defaultdict(list)
  self.textured=[]
 def push(self,mesh,color):self.buckets[color].append(mesh)
 def box(self,x,y,z,w,h,d,c):
  if w<=0 or h<=0 or d<=0:return
  m=trimesh.creation.box(extents=(w,h,d));m.apply_translation([x,y,z]);self.push(m,c)
 def cyl(self,x,y,z,r,h,c,n=12):
  m=trimesh.creation.cylinder(radius=r,height=h,sections=n);m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation([x,y,z]);self.push(m,c)
 def cone(self,x,y,z,r,h,c,n=8):
  m=trimesh.creation.cone(radius=r,height=h,sections=n);m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi/2,[1,0,0]));m.apply_translation([x,y,z]);self.push(m,c)
 def sphere(self,x,y,z,r,c,sub=1):
  m=trimesh.creation.icosphere(subdivisions=sub,radius=r);m.apply_translation([x,y,z]);self.push(m,c)
 def beam(self,p,q,r,c,n=8):
  a,b=np.array(p),np.array(q);v=b-a;h=np.linalg.norm(v)
  if h<.0001:return
  m=trimesh.creation.cylinder(radius=r,height=h,sections=n)
  trans=trimesh.geometry.align_vectors([0,0,1],v/h);m.apply_transform(trans);m.apply_translation((a+b)/2);self.push(m,c)
 def sign(self,text,x,y,z,w=5.0,h=.62,color='#244e59',accent='#f2ca79'):
  # Screen-printed textured front fascia. Pixel data is embedded in the GLB.
  W,H=1024,160
  im=Image.new('RGBA',(W,H),color);dr=ImageDraw.Draw(im)
  dr.rounded_rectangle((10,10,W-10,H-10),radius=25,outline=accent,width=9)
  try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',68)
  except:font=ImageFont.load_default()
  box=dr.textbbox((0,0),text,font=font);tw=box[2]-box[0];th=box[3]-box[1]
  if tw>W-100:
   try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(68*(W-110)/tw))
   except:pass
   box=dr.textbbox((0,0),text,font=font);tw=box[2]-box[0];th=box[3]-box[1]
  dr.text(((W-tw)/2,(H-th)/2-box[1]),text,font=font,fill='#fffdf0')
  mesh=trimesh.Trimesh(vertices=[[x-w/2,y-h/2,z],[x+w/2,y-h/2,z],[x+w/2,y+h/2,z],[x-w/2,y+h/2,z]],faces=[[0,1,2],[0,2,3]],process=False)
  mat=PBRMaterial(baseColorTexture=im,baseColorFactor=[255,255,255,255],metallicFactor=.05,roughnessFactor=.78,doubleSided=True,name='SIGN_'+text.replace(' ','_'))
  mesh.visual=TextureVisuals(uv=[[0,1],[1,1],[1,0],[0,0]],material=mat)
  self.textured.append(('SIGN_'+text.replace(' ','_'),mesh))
 def ring(self,x,y,z,r,thick,c):
  self.cyl(x,y,z,r,thick,c,16)
 def export(self,path):
  scene=trimesh.Scene()
  for i,(color,meshes) in enumerate(self.buckets.items()):
   allmesh=trimesh.util.concatenate(meshes)
   hs=COLORS.get(color,color).lstrip('#');rgb=[int(hs[k:k+2],16) for k in (0,2,4)]
   mat=PBRMaterial(baseColorFactor=[*rgb,255],metallicFactor=.02 if color not in ('steel','silver') else .4,roughnessFactor=.82, doubleSided=False,name=color)
   allmesh.visual=trimesh.visual.TextureVisuals(material=mat)
   scene.add_geometry(allmesh,geom_name=f'MERCY_{color.upper()}',node_name=f'MERCY_{color.upper()}_{i:02d}')
  for label,mesh in self.textured:
   scene.add_geometry(mesh,geom_name=label,node_name=label)
  blob=trimesh.exchange.gltf.export_glb(scene,include_normals=True)
  with open(path,'wb') as f:f.write(blob)
  print('Export',os.path.basename(path),round(len(blob)/1048576,2),'MB',sum(len(v) for v in self.buckets.values()),'parts',len(self.buckets),'materials')

b=Builder()
B=b.box;C=b.cyl;S=b.sphere

def sidewalk(x,z,w,d):
 B(x,.08,z,w,.15,d,'concrete');B(x,.17,z,w,.035,d,'tile')

def patch(x,z,w,d): B(x,.16,z,w,.13,d,'grass2')

def stripe(x,z,w,d,c='line'): B(x,.23,z,w,.014,d,c)

def tree(x,z,sz=1):
 B(x,.22,z,1.6,.21,1.6,'grass2');C(x,1.15*sz,z,.16,1.9*sz,'wood',8)
 for dx,dy,dz,r,col in [(0,2.1,0,.79,'tree'),(.46,2.28,-.3,.57,'tree2'),(-.36,2.4,.13,.61,'plant'),(.1,2.82,.1,.46,'plant2')]:S(x+dx*sz,dy*sz,z+dz*sz,r*sz,col,1)

def plant(x,z,scale=1):
 C(x,.4*scale,z,.32*scale,.5*scale,'wood2',10)
 for i in range(5):
  a=2*math.pi*i/5
  S(x+math.cos(a)*.24*scale,.84*scale+random.random()*.18,z+math.sin(a)*.24*scale,.26*scale,'plant' if i%2 else 'plant2')

def pallet(x,z,w=1.25,d=.9,h=.14):
 for dz in [-d*.35,0,d*.35]:B(x,.40,z+dz,w,h,d*.2,'wood')
 B(x,.49,z,w,.13,d,'wood2')

def boxes(x,z,layers=2,col=None,boxsize=.68):
 palette=['cardboard','boxgreen','boxblue','boxorange','cardboard2']
 for j in range(layers):
  for i in range(2):
   c=(col or palette[(i+j+int(abs(x)*7))%len(palette)])
   B(x+(i-.5)*(boxsize+.04),.85+boxsize*(j+.5),z,boxsize,boxsize,boxsize,c)
   B(x+(i-.5)*(boxsize+.04),.85+boxsize*(j+.5),z+boxsize*.50+.008,.28,.04,.05,'cream')

def shelf(x,z,width=3.6,d=1.28):
 # Three-tier industrial steel shelving, boxes and pallets.
 for dx in [-width/2,width/2]:
  for dz in [-d/2,d/2]:B(x+dx,2.1,z+dz,.12,3.8,.14,'darksteel')
 for level in [.70,1.90,3.1]:
  B(x,level,z,width+.2,.14,d+.1,'orange');
  B(x,level+.08,z,width+.18,.035,d+.09,'steel')
  for nx in range(3):
   xx=x-width/2+.57+nx*(width/3)
   for k in range(2):
    zz=z+(k-.5)*.62
    B(xx,level+.46,zz,.85,.72,.54,['boxgreen','cardboard','boxblue','boxorange'][int(abs(x)+nx+level*4+k)%4])
    B(xx,level+.84,zz+.282,.38,.035,.015,'cream')
 # cross bracing at back
 for sy in [0,2.0]:b.beam([x-width/2,sy+.35,z-d/2],[x+width/2,sy+1.75,z-d/2],.055,'steel',6)

def station(x,z,w=2.6):
 B(x,.83,z,w,.12,1.20,'steel');B(x,.40,z,w*.8,.72,.65,'navy')
 for i in range(10):
  dx=(i-4.5)*(w-.27)/10
  C(x+dx,.925,z,.115,.06,'silver',9)
 for i in range(3):
  B(x-.75+i*.70,1.14,z,.44,.35,.40,['peach','gold','boxgreen'][i])
 for dx in [-w/2+.15,w/2-.15]:B(x+dx,1.36,z,.06,1.2,.06,'steel')
 B(x,1.94,z,w,.1,.1,'darksteel')

def factory(cx,z,color='teal',label='TRIDAYA'):
 w,d=15.1,11.4
 # raised stepped concrete foundation, two long back walls, partial roof and large side windows
 B(cx,.20,z,w+.8,.32,d+.85,'concrete2');B(cx,.41,z,w,.10,d,'tile')
 # wall back and cutaway left/right
 B(cx,2.05,z-d/2+.18,w,3.25,.35,'wall')
 B(cx-w/2+.2,2.0,z-d/2+1.55,.35,3.2,3.1,color)
 B(cx+w/2-.2,2.0,z-d/2+1.55,.35,3.2,3.1,color)
 # line of back roof panels with alternating skylights; roof cutaway visible on front
 B(cx,3.82,z-d/2+1.15,w+1.2,.28,2.9,'white')
 for i in range(4):
  xx=cx-5.9+i*3.9
  B(xx,3.985,z-d/2+1.1,2.0,.07,1.13,'sky')
  B(xx,4.04,z-d/2+.55,.13,.10,1.30,'steel')
 # structural supports and colored awnings
 for dx in [-6.8,-2.7,1.5,6.8]:B(cx+dx,2.02,z+d/2-.35,.22,3.4,.22,'steel')
 B(cx,3.7,z+d/2-.30,w,.24,.50,color)
 for i in range(5):
  xx=cx-5.8+i*2.85
  B(xx,2.03,z-d/2+.39,1.5,1.30,.08,'glass')
  B(xx,2.03,z-d/2+.35,.06,1.3,.10,'steel')
 # central walkway from entry side and parallel machine stations
 B(cx,.485,z+2.5,2.2,.035,5.4,'cream')
 for s in [-1,1]:
  for i in range(3):
   xx=cx+s*3.65
   zz=z-3.10+i*2.58
   station(xx,zz,2.65)
 # little control panel and lights
 B(cx-6.0,.95,z+3.9,.9,1.1,.55,'navy');B(cx-6.0,1.25,z+4.21,.55,.40,.08,'glass')
 for i in range(6):
  xx=cx-6+i*2.45
  B(xx,3.32,z-d/2+2.8,1.5,.08,.14,'lamp')
 # drums, colored products and safety-marked floor
 for i in range(5):C(cx+5.9, .72, z-3.8+i*1.55,.40,.58,['blue','teal','gold'][i%3])
 for i in range(5):B(cx-7.1,.47,z-3.85+i*2,.3,.027,.95,'yellow')
 # name plate above front lintel - represented raised graphic mark
 B(cx,3.83,z+d/2-.06,4.9,.34,.12,color)
 sidewalk(cx,z+d/2+1.55,13,2.1)
 for i in range(2):
  plant(cx-6.8+i*13,z+d/2+.9,.66)
 # Styled building signage and numbered safety-zone markers
 zone={'TRIDAYA':'01','INNA':'02','KBI':'03'}.get(label,'00')
 b.sign(label+' / LINE '+zone,cx,4.05,z+d/2+.12,6.2,.68,{'TRIDAYA':'#24756e','INNA':'#3f7797','KBI':'#ae783c'}.get(label,'#275a61'))
 B(cx-5.95,2.25,z+d/2+.155,.45,.95,.07,'gold')
 B(cx+5.95,2.25,z+d/2+.155,.45,.95,.07,'gold')
 # Detailed robotic palletizing cell: hinged robot arm and round industrial base
 for rx,rz in [(cx-2.9,z-2.55),(cx+2.95,z-.85)]:
  C(rx,.88,rz,.47,.72,'darksteel',14)
  C(rx,1.33,rz,.28,.20,'yellow',14)
  b.beam([rx,1.40,rz],[rx+.62,2.12,rz-.15],.17,'orange',12)
  S(rx+.62,2.12,rz-.15,.25,'steel',1)
  b.beam([rx+.62,2.12,rz-.15],[rx+1.25,1.70,rz+.23],.16,'yellow',12)
  S(rx+1.25,1.70,rz+.23,.18,'darksteel',1)
  for offset in [-.15,.15]:B(rx+1.40,1.47,rz+.23+offset,.11,.48,.10,'darksteel')
 # Pipe duct and handrail around the main station
 for xx in [cx-6.35,cx+6.35]:
  B(xx,2.7,z-4.65,.10,1.25,.10,'orange')
  B(xx,3.3,z-4.65,.42,.10,.13,'steel')
 for dx in [-3.8,-2.1,-.4,1.3,3.0]:
  B(cx+dx,.55,z+4.78,.47,.035,.52,'yellow')
 # Metallic exhaust ducts on roof; offset to avoid hiding factory interiors
 for xoff in [-5.9,5.4]:
  C(cx+xoff,4.18,z-d/2+1.30,.22,.8,'darksteel')
  C(cx+xoff,4.72,z-d/2+1.30,.38,.14,'silver')

# Thick plinth under everything: smooth-edge 3D tabletop and distinct decorative topsoil
B(0,-.59,0,65,1.1,51,'edge')
B(0,-.015,0,64.5,.12,50.5,'grass')
# plot perimeter concrete path
for x,z,w,d in [(0,-23.4,62,1.2),(0,23.5,62,1.2),(-31.2,0,1.2,45),(31.2,0,1.2,45)]:B(x,.12,z,w,.14,d,'concrete2')
# Main horizontal roadway z 1.75 and northern loading spur to warehouse
B(0,.10,1.4,63,0.14,6.6,'roadEdge')
B(0,.19,1.4,63,.035,5.95,'asphalt')
B(7.3,.10,8.6,6.5,.14,15.8,'roadEdge')
B(7.3,.194,8.6,5.75,.04,15.8,'asphalt')
for x in np.arange(-27,31,4.8):stripe(float(x),1.36,2.4,.10)
for z in np.arange(5,14,3.2):stripe(7.3,float(z),.12,1.45)
# striped pedestrian crosswalk at x=-7 (road z -1.6 to 4.6)
for i in range(7):B(-7.5+i*.62,.233,1.4,.36,.016,5.2,'white')
# main pedestrian sidewalks under factory doors and across front of offices
sidewalk(0,-5.65,61,1.70)
sidewalk(-12.8,6.1,30,1.45)
sidewalk(-19.2,8.18,2.6,5.7)
sidewalk(-.85,8.18,2.6,5.7)
# bright angled safety bollards and signs by road
for x in [-29.0,29.0,4.0,10.0]:
 for z in [-2.4,5.1]:
  C(x,.71,z,.14,1.0,'gold');C(x,1.22,z,.18,.14,'white')
# factory footprints
for cx,co,lab in [(-19,'teal','TRIDAYA'),(0,'blue','INNA'),(19,'orange','KBI')]:factory(cx,-13.2,co,lab)
# Warehousing shell open-cutaway: west-facing loading dock door, rack grid
wx,wz=19,16.5
B(wx,.20,wz,19,.3,14.4,'concrete2');B(wx,.42,wz,18.3,.16,13.8,'tile')
B(wx,.81,23.22,19.2,.95,.40,'wall')
B(28.3,2.15,wz,.38,3.32,13.7,'wall')
B(10.2,2.12,20.66,.38,3.4,5.4,'wall')  # west wall rear, open for loading dock
# partial ceiling stripes and warehouse roof ridge
B(wx,4.1,23.1,19.8,.20,.30,'cream')
for xx in np.arange(10.8,28.1,3.4):B(xx,2.35,23.15,.16,3.20,.16,'steel')
B(wx,3.85,23.4,19.8,.25,.35,'teal')
# door jambs/loading bollards
for z in [11.7,15.5,20.0]:
 B(10.15,2.0,z,.19,3.3,.21,'steel');C(9.75,.64,z,.14,.9,'gold')
# racks: 2 aisles arranged x side-by-side; forklift goes west-east through dock z=14.5
for x in [14.4,19.2,24.0]:
 for z in [18.6,22.25]:
  shelf(x,z,3.5,1.25)
for (x,z,n) in [(14.0,12.4,1),(18.4,12.0,2),(25.2,12.3,1),(26.2,16.2,2)]:pallet(x,z);boxes(x,z,n)
# Warehouse parcel sorting conveyor and colored inventory packing stations
for x in [12.6,14.0,15.4,16.8,18.2]:
 B(x,1.02,16.45,1.20,.15,.92,'steel')
 B(x,1.18,16.45,.94,.05,.75,'darksteel')
 C(x-.33,1.24,16.45,.10,.10,'silver',10)
 B(x,1.40,16.45,.52,.33,.46,['boxblue','boxorange','cardboard'][int(x*10)%3])
for x in [14.4,19.2,24.0]:
 for z in [18.6,22.25]:
  # hazard safety beams on ends of each shelving unit
  for h in [.8,1.25,1.7]:
   B(x-1.79,h,z+.70,.06,.11,.05,'yellow')
B(24.5,.74,13.7,1.4,.82,1.2,'teal')
B(24.5,1.23,14.31,1.1,.20,.07,'glass')
# shrink wrap loading station and scanner
B(24.8,.75,15.0,2.4,.18,1.2,'steel');B(24.8,.39,15.0,2.1,.75,.85,'navy')
B(25.4,1.65,15.0,.75,1.1,.10,'darkblue');B(25.4,1.67,15.07,.62,.75,.06,'glass')
B(11.0,.45,10.3,5.7,.16,1.35,'concrete2')  # loading apron, edge outside rack
for i in range(8):
 B(11.0+i*.66-2.3,.55,9.72,.37,.03,.11,'gold')
# Visual warehouse identity: mounted facade fascia on back wall
b.sign('GUDANG / LOADING',19,3.47,23.54,8.0,.69,'#305e6a','#f3cc83')
# Office cutaway on left + printer scene, no roof above front
ox,oz=-19,16.1
B(ox,.23,oz,17,.35,14.1,'concrete2');B(ox,.45,oz,16.5,.09,13.55,'wood2')
B(ox,.92,22.86,17.2,.96,.30,'cream')
B(-27.34,2.22,oz,.28,3.4,13.8,'cream')
B(-10.69,2.22,19.25,.28,3.4,7.1,'wall2')
B(ox,3.95,22.88,17.6,.22,.32,'white')
# long back panel window band
for xx in [-26.4,-22.2,-18,-13.2]:
 B(xx,2.33,22.77,.11,2.73,.13,'steel')
# office carpets, desks on back and side
for x,z in [(-23.5,17.3),(-20.3,17.3),(-23.0,12.8)]:
 B(x,.52,z,2.9,.065,2.1,'lavender')
 B(x,1.32,z,2.2,.13,.97,'wood')
 for dx in [-.90,.90]: B(x+dx,.92,z,.12,.72,.12,'steel')
 B(x,1.64,z-.35,1.02,.79,.09,'ink');B(x,1.65,z-.29,.87,.63,.02,'glass')
 B(x,1.25,z+.29,.71,.04,.38,'lightgrey')
 B(x,.81,z+1.10,.86,.17,.90,'navy');B(x,.49,z+1.10,.17,.48,.17,'steel')
 # lamp hanging over each workstation
 S(x,3.20,z,.20,'lamp');C(x,3.53,z,.033,.42,'steel')
# large printer in lower right (inside room)
px,pz=-14.9,17.1
B(px,.80,pz,1.65,1.05,1.10,'silver')
B(px,1.40,pz,1.52,.30,1.01,'lightgrey')
B(px,1.52,pz-.19,1.48,.20,.32,'navy')
B(px,1.54,pz+.53,.75,.04,.1,'white')
B(px,1.13,pz+.61,.95,.04,.25,'cream')
for ix in range(5):B(px-.50+ix*.23,1.62,pz-.5,.12,.03,.10,'teal')
# Paper stack, printer digital screen and extra sheet feeder
B(px,1.61,pz-.37,.41,.12,.045,'glass')
for i in range(6):B(px-.42+i*.16,1.64,pz+.54,.10,.016,.04,'white')
B(-16.7,.57,18.80,1.3,.12,1.1,'wood')
for i in range(7):B(-16.7,0.72+i*.035,18.8,1.06,.035,.82,'white')
# shelf and report documents
B(-13.2,1.92,21.9,2.6,3.15,.42,'wood')
for iy in [1.10,1.9,2.75]:
 B(-13.2,iy,21.5,2.52,.11,.63,'cream')
 for n in range(5):B(-14.25+n*.51,iy+.25,21.5,.35,.4,.38,['boxblue','lavender','peach'][n%3])
plant(-26.15,11,.8);plant(-12.5,11,.7)
b.sign('KANTOR / LAPORAN',ox,3.60,23.065,8.6,.71,'#346e65','#f9deac')
# Small notice board, clocks and office partition details
B(-25.8,2.3,22.57,1.35,.85,.045,'teal2')
C(-21.5,3.10,22.56,.34,.055,'white',20)
for x in [-24.6,-21.4,-18.2,-15.0]:B(x,.53,10.10,1.6,.035,.16,'cream')
# Administrative glass cubicle at 0,16, open front (users see monitors)
ax,az=0,16.0
B(ax,.22,az,11.2,.34,11.8,'concrete2');B(ax,.41,az,10.8,.07,11.4,'cream')
B(ax,.88,az+5.65,11.1,.98,.25,'wall2')
for sx in [-5.5,5.5]:B(ax+sx,2.1,az,.22,3.3,4.1,'wall2')
B(ax,3.85,az+5.55,11.5,.18,.30,'white')
for xx in [-3.2,0,3.2]:
 B(xx,1.21,17.5,2.3,.13,1.35,'wood')
 B(xx,1.8,18,1.25,.85,.1,'navy');B(xx,1.8,18.10,1.05,.68,.03,'glass')
 B(xx,1.06,16.5,.82,.95,.77,'teal')
for x in [-4.2,4.1]:plant(x,11.5,.65)
b.sign('ADMIN / DATABASE PO',0,3.56,21.83,9.2,.70,'#3f7d88','#f3db97')
# gate guard booth & sign in outer right road
B(30,.35,3.80,1.8,.6,2.0,'concrete2')
B(30,1.36,3.8,1.75,1.9,2.0,'white')
B(30,2.43,3.8,2.15,.20,2.26,'teal')
B(29.99,1.57,2.8,1.5,.75,.08,'glass')
B(30,2.59,3.84,1.3,.12,.5,'navy')
# Stronger gate details: scanner, boom barrier at outer right perimeter
B(30.5,.50,-.9,.48,.65,.48,'steel')
B(30.5,1.12,-.9,.48,.18,.48,'gold')
B(30.5,1.30,-3.10,.16,.17,4.65,'white')
for z in [-1.4,-2.5,-3.65]:B(30.5,1.37,z,.18,.04,.31,'red')
# Yard safe-route chevrons and bollards, restricted to road shoulders
for x in [-27.7,-12.2,11.2,25.0]:
 for z in [-3.28,5.15]:
  B(x,.30,z,.98,.020,.12,'white')
for z in [9.3,12.3,15.3]:B(4.20,.25,z,.23,.024,1.12,'yellow')
# environmental landscaping throughout outside transport corridors, including flower planters
for x,z in [(-29,-19),(-29,-11),(-29,20),(-6,-22.8),(8,-22.8),(29,-22.8),(29,-7),(-3,22.4),(4,23),(28,22.5),(-29,6.5),(30,18.4)]:tree(x,z,random.uniform(.72,1.08))
for x,z in [(-9,20),(-9,11),(-7,22),(11,-22),(25,-22)]:plant(x,z,.68)
for i in range(24):
 x,z=random.choice([(-30,-20),(-30,20),(29,-21),(29,22),(-2,23)]);x+=random.uniform(-1.2,1.2);z+=random.uniform(-1.1,1.1)
 S(x,.33,z,.13,['gold','pink','peach','white'][i%4])
# lights along avenues, steel pipes near factories
for x,z in [(-29,-4.8),(-6,-4.8),(28,-4.8),(28,5.8),(7.1,21),(-8.2,7.8)]:
 C(x,1.75,z,.095,3.4,'steel')
 B(x,3.49,z,.85,.15,.65,'lamp')
for x in [-25,-7,11]:
 C(x,4.3,-20,.30,1.0,'steel')
 B(x,4.81,-20,.9,.10,.85,'silver')
# tools: hand trucks, wooden pallets, yellow waste bins on perimeter
for x,z in [(-26,-7.7),(-10,-8.2),(12,-7.9),(26,-7.9),(28,10)]:
 B(x,.41,z,.8,.75,.72,'gold');B(x,.82,z,.83,.05,.77,'darksteel')
# loader hazard signal
C(10.5,2.4,7.4,.17,3.9,'steel')
S(10.5,4.43,7.4,.31,'red')
b.export(os.path.join(DEST,'mercy_factory_diorama.glb'))

# Driveable truck asset: +X = forward, yaw driven by animation
v=Builder();b=v
B=v.box;C=v.cyl;S=v.sphere
B(.9,.87,0,4.12,1.48,2.38,'white')
B(.9,2.03,0,4.18,1.16,2.46,'cream')
B(.85,2.67,0,4.2,.16,2.52,'teal')
B(-2.18,1.10,0,2.00,1.47,2.30,'teal')
B(-2.18,1.99,0,2.07,.35,2.38,'teal2')
B(-3.15,1.20,0,.14,.72,2.01,'navy')
B(-2.35,1.65,-1.17,1.06,.65,.07,'glass');B(-2.35,1.65,1.17,1.06,.65,.07,'glass')
B(-3.08,1.65,0,.06,.65,1.52,'glass')
B(-2.38,.65,0,1.94,.20,2.43,'darksteel')
B(1.5,.52,0,3.75,.21,2.5,'steel')
for xx in [-2.2,1.4,2.4]:
 for zz in [-1.23,1.23]:
  # wheels rotate around z axis
  m=trimesh.creation.cylinder(radius=.44,height=.24,sections=18)
  m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation([xx,.46,zz]);v.push(m,'black')
  m=trimesh.creation.cylinder(radius=.21,height=.255,sections=12)
  m.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));m.apply_translation([xx,.46,zz]);v.push(m,'silver')
for zz in [-.86,.86]:B(-3.22,.71,zz,.11,.19,.27,'lamp')
B(3.08,1.38,0,.04,2.37,2.39,'steel')
B(.85,2.04,-1.28,1.5,.15,.06,'teal')
B(.85,2.04,1.28,1.5,.15,.06,'teal')
B(.9,2.22,-1.28,2.82,.03,.07,'gold')
# Side door, side mirror and running board
B(-1.80,.44,-1.23,1.12,.13,.21,'darksteel')
B(-1.80,.44,1.23,1.12,.13,.21,'darksteel')
B(-2.72,1.63,-1.34,.33,.21,.09,'black')
B(-2.72,1.63,1.34,.33,.21,.09,'black')
for xx in [-.7,1.3]:
 B(xx,1.05,-1.30,.18,.08,.04,'steel');B(xx,1.05,1.30,.18,.08,.04,'steel')
for zz in [-1.15,1.15]:
 B(3.05,.80,zz,.04,.28,.21,'red')
# Textured delivery company sign (truck's right side)
v.sign('MERCY LOGISTIK',.6,1.75,1.273,3.38,.47,'#3d867e','#f4e4b7')
v.export(os.path.join(DEST,'mercy_truck.glb'))
# forklift with windshield, protective frame, forks and loaded pallet
v=Builder();B=v.box;C=v.cyl;S=v.sphere
B(0,.72,0,1.62,.65,1.19,'gold')
B(.53,1.18,0,.68,.47,1.03,'orange')
B(-.54,1.13,0,.40,.66,1.12,'navy')
for xx in [-.53,.54]:
 for zz in [-.57,.57]:
  S(xx,.36,zz,.34,'black');S(xx,.36,zz,.15,'silver')
for xx in [-.62,.52]:
 for zz in [-.58,.58]:B(xx,1.72,zz,.07,1.57,.07,'steel')
B(-.06,2.49,0,1.33,.12,1.3,'black')
B(1.12,1.20,0,.17,2.0,1.13,'darksteel')
for zz in [-.42,.42]:B(1.78,.28,zz,1.6,.09,.17,'steel')
B(1.09,1.22,0,.15,1.10,.12,'steel')
B(.24,1.13,0,.66,.19,.72,'navy')
S(-.15,1.8,0,.22,'lamp')
# Forklift hazard beacon, forks mast rollers and cabin display
C(-.40,2.61,0,.18,.13,'yellow',12)
B(.38,1.42,-.58,.52,.35,.035,'glass')
B(.38,1.42,.58,.52,.35,.035,'glass')
for yy in [.5,1.4]:
 B(1.23,yy,0,.12,.12,1.02,'steel')
B(-.32,1.0,.59,.54,.31,.05,'navy')
v.export(os.path.join(DEST,'mercy_forklift.glb'))

# Articulated miniature worker: arms and legs exported as independent GLB nodes.
# Web Three.js rotates these nodes at hips/shoulders rather than bobbing whole objects.
from trimesh.transformations import translation_matrix
worker=trimesh.Scene()

def rgba(c):
 hex=COLORS.get(c,c).lstrip('#');return [int(hex[i:i+2],16) for i in (0,2,4)] + [255]

def add_part(name,mesh,color,pivot=(0,0,0)):
 mesh.visual=trimesh.visual.TextureVisuals(material=PBRMaterial(baseColorFactor=rgba(color),roughnessFactor=.85,metallicFactor=.02,name='WORKER_'+color))
 worker.add_geometry(mesh,geom_name=name,node_name=name,transform=translation_matrix(pivot))

def geo_box(w,h,d,xyz=(0,0,0)):
 m=trimesh.creation.box(extents=(w,h,d));m.apply_translation(xyz);return m

def geo_sphere(r,xyz=(0,0,0),sub=2):
 m=trimesh.creation.icosphere(subdivisions=sub,radius=r);m.apply_translation(xyz);return m

add_part('Body_Torso',geo_box(.70,.76,.45,(0,1.14,0)),'blue')
add_part('Body_ReflectiveVest',geo_box(.51,.50,.052,(0,1.10,.24)),'gold')
for x in [-.205,.205]:
 add_part('Reflector_'+str(x),geo_box(.09,.62,.055,(x,1.14,.277)),'white')
add_part('Belt',geo_box(.66,.11,.48,(0,.78,0)),'darksteel')
add_part('Neck',geo_box(.19,.20,.22,(0,1.58,0)),'peach')
add_part('Head',geo_sphere(.29,(0,1.80,0),2),'peach')
add_part('Helmet',geo_box(.82,.11,.59,(0,2.05,-.02)),'yellow')
helmet=trimesh.creation.cylinder(radius=.36,height=.21,sections=24);helmet.apply_transform(trimesh.transformations.rotation_matrix(math.pi/2,[1,0,0]));helmet.apply_translation((0,2.16,-.02));add_part('Hardhat_Dome',helmet,'yellow')
for x in [-.125,.125]:add_part('Face_Eye'+str(x),geo_sphere(.033,(x,1.84,.277),1),'black')
add_part('Face_Nose',geo_sphere(.038,(0,1.76,.29),1),'peach')
add_part('Mouth',geo_box(.13,.015,.013,(0,1.66,.291)),'red')
for side,pref in [(-1,'Left'),(1,'Right')]:
 x=side*.49
 # shoulder pivot at (x,1.43,0), lower limb mesh in its own local coordinates
 arm=trimesh.util.concatenate([geo_box(.23,.57,.25,(0,-.29,0)),geo_sphere(.14,(0,-.59,.015),1),geo_sphere(.135,(0,-.73,.016),1)])
 add_part('Arm_'+pref,arm,'blue',(x,1.44,0))
 leg=trimesh.util.concatenate([geo_box(.29,.53,.36,(0,-.30,0)),geo_box(.36,.17,.48,(0,-.64,.08))])
 add_part('Leg_'+pref,leg,'darkblue',(side*.20,.75,0))
for name in ['Arm_Left','Arm_Right','Leg_Left','Leg_Right']:
 assert name in worker.graph.nodes
blob=trimesh.exchange.gltf.export_glb(worker,include_normals=True)
path=os.path.join(DEST,'mercy_worker.glb');open(path,'wb').write(blob)
print('Export mercy_worker.glb',round(len(blob)/1048576,2),'MB, articulated nodes:',len(worker.graph.nodes))
