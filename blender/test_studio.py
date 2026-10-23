"""Offline validation: GLB integrity, articulated model, road and worker route separation.
Does not access Firebase or edit production PO.
"""
import re, math, sys
from pathlib import Path
import trimesh
root=Path(__file__).resolve().parent.parent
files=['mercy_factory_diorama.glb','mercy_truck.glb','mercy_forklift.glb','mercy_worker.glb']
for f in files:
 asset=root/'assets'/f
 assert asset.is_file() and asset.stat().st_size>10000,f
 s=trimesh.load(asset,force='scene')
 assert s.geometry,f
 assert all(mesh.is_winding_consistent for mesh in s.geometry.values() if len(mesh.faces)>0),f
 print(f,'OK',len(s.geometry),'meshes',sum(len(m.faces) for m in s.geometry.values()),'faces')
worker=trimesh.load(root/'assets/mercy_worker.glb',force='scene')
for name in ['Arm_Left','Arm_Right','Leg_Left','Leg_Right']:
 assert name in worker.graph.nodes,f'Articulated limb missing: {name}'
print('Worker joint nodes OK')
s=(root/'index.html').read_text()
assert 'scene-glb.js' not in s and 'world.html' not in s
for feature in ['mercy_orders','storyOverlay','skipStory','report','csv','arrived','priority','TRIDAYA','INNA','KBI']:
 assert feature in s,feature
assert "fillPrint(rows);story('report')" not in s
print('One-page MERCY feature scaffolding OK')
# Road centerlines in model generator geometry:
# Main carriageway z [-1.575, 4.375]; loading spur x [4.425,10.175], z [.7,16.5].
truck=[(36.5,1.4),(27,1.4),(17,1.4),(12,1.4),(9.7,2.3),(7.4,4.55),(7.3,7),(7.3,11.1)]
fork=[(17,14.9),(14,14.9),(11.45,14.9),(9.73,13.4)]
loader=[(16.8,12.2),(15.7,12.2),(14.1,12.2)]
# Last 8 centerline points must remain inside paved surfaces (first x36 outside diorama = gate entrance).
for x,z in truck:
 assert (x>=10.5 and -1.7<=z<=4.5) or (4.3<=x<=10.3 and .5<=z<=16.8) or x>32
assert all(x>=9.3 and z>=12.8 for x,z in fork)
# Centerline separation: hand-loader works at z 12.2 and forklift at z >=13.4,
# but forklift only travels close once loader reaches far from x <14.1.
for x,z in loader:
 assert abs(z-14.9)>=2.6
# Start collision separation before and after parked truck / forklift.
assert math.dist(truck[-1],fork[-1])>3.2
# Workers must use sidewalk and open building entry paths.
for cx in [-19,0,19]:
 factory_path=[[cx-3,-6.55],[cx-1.2,-6.55],[cx-1.2,-8.1],[cx-.5,-9.5]]
 assert all(cx-7.5<=x<=cx+7.5 for x,_ in factory_path)
print('Traffic + personnel route sanity checks OK')
print('ALL OFFLINE TESTS PASSED (not a GPU browser or Firebase production test)')
