"""Offline MODEL PREVIEW (not an actual Blender render): projects the real GLB meshes.
This visualization includes a static frame of the truck/forklift/worker assets.
"""
from pathlib import Path
import math, numpy as np, trimesh, cv2
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from trimesh.transformations import rotation_matrix,translation_matrix
root=Path(__file__).resolve().parent.parent
W,H=1500,960
E=np.array([61.,66.,85.]);target=np.array([0.,0.,0.]);front=target-E;front/=np.linalg.norm(front)
right=np.cross(front,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,front)
scale=17.4;camcx=W*.50;camcy=H*.54
light=np.array([-0.4,.9,.3]);light/=np.linalg.norm(light)

def projected(pts):
 a=np.asarray(pts);return np.stack([camcx+np.dot(a,right)*scale,camcy-np.dot(a,up)*scale],axis=-1)

def meshes_for(name,offset=(0,0,0),yaw=0):
 scene=trimesh.load(str(root/'assets'/name),force='scene')
 mat=translation_matrix(offset)@rotation_matrix(yaw,[0,1,0])
 out=[]
 for mesh in scene.dump():
  if not isinstance(mesh,trimesh.Trimesh):continue
  mm=mesh.copy();mm.apply_transform(mat);out.append(mm)
 return out

items=meshes_for('mercy_factory_diorama.glb')
items+=meshes_for('mercy_truck.glb',(7.3,0,10.3),math.pi/2)
items+=meshes_for('mercy_forklift.glb',(13.6,0,14.9),math.pi)
for x,z in [(-20,-6.2),(-4.3,-12.4),(20,-7.1),(-16.0,16.1),(15.8,12.2)]:
 items+=meshes_for('mercy_worker.glb',(x,0,z),0)
# Build triangles using painter's ordering with artist-style studio illumination.
faces=[]
for mesh in items:
 tri=np.asarray(mesh.vertices)[np.asarray(mesh.faces)]
 nm=mesh.face_normals
 bright=np.clip(.67+np.maximum(0,(nm*light).sum(axis=1))*.33,.56,1)
 vis=mesh.visual
 col=np.array(getattr(vis.material,'baseColorFactor',[160,194,180,255])[:3],dtype=float)
 tex=getattr(vis.material,'baseColorTexture',None)
 if tex is not None:
  im=np.asarray(tex.convert('RGB'));col=np.median(im.reshape(-1,3),axis=0).astype(float)
 pts=projected(tri)
 depth=(tri.mean(axis=1)*front).sum(axis=1)
 for ix in range(len(tri)):
  q=pts[ix]
  if np.any(np.abs(q)>4000):continue
  c=tuple(np.maximum(0,np.minimum(255,col*bright[ix])).astype('uint8').tolist())
  ground=(getattr(vis.material,'name','') or '').lower() in ('edge','grass','grass2','roadedge','asphalt')
  faces.append((float(depth[ix])+(150 if ground else 0),q,c))
faces.sort(reverse=True)
img=Image.new('RGB',(W,H),(232,247,242)).convert('RGBA')
sha=Image.new('RGBA',(W,H),(0,0,0,0));ImageDraw.Draw(sha).ellipse((170,300,1330,885),fill=(23,70,53,44))
img=Image.alpha_composite(img,sha.filter(ImageFilter.GaussianBlur(80)))
draw=ImageDraw.Draw(img)
for _,pts,col in faces:
 draw.polygon([tuple(map(int,p)) for p in pts],fill=col)
# Painter overlay projected textured signs (labels are part of the actual embedded GLBs)
for mesh in items:
 mat=mesh.visual.material
 tex=getattr(mat,'baseColorTexture',None)
 if tex is None:continue
 v=np.asarray(mesh.vertices)
 if len(v)!=4:continue
 pts=projected(v).astype('float32')
 src=np.asarray(tex.convert('RGBA'))
 h,w=src.shape[:2]
 source=np.float32([[0,h-1],[w-1,h-1],[w-1,0],[0,0]])
 transform=cv2.getPerspectiveTransform(source,pts)
 warped=cv2.warpPerspective(src,transform,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 lay=Image.fromarray(warped,'RGBA');img=Image.alpha_composite(img,lay)
# Small layout notes, clearly visualization; no claim of Blender render.
draw=ImageDraw.Draw(img)
try:
 font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',35)
 sub=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
except:font=sub=ImageFont.load_default()
draw.rounded_rectangle((54,32,660,132),radius=19,fill=(255,255,255,221),outline=(154,208,185,170),width=2)
draw.text((80,52),'MERCY FACTORY STUDIO',fill=(31,93,84),font=font)
draw.text((82,101),'3D GLB model preview  •  Tridaya  /  Inna  /  KBI',fill=(98,143,128),font=sub)
draw.rounded_rectangle((120,893,1380,940),radius=18,fill=(255,255,255,214))
draw.text((153,909),'PABRIK 3D    •    STAF BERJALAN    •    TRUK & FORKLIFT    •    KANTOR LAPORAN    •    GUDANG',fill=(66,115,101),font=sub)
out=root/'MERCY-Factory-Studio-Preview.png';img.convert('RGB').save(out,optimize=True)
print('Wrote model preview',out,'shapes:',len(items),'triangles:',len(faces))
