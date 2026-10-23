import vtk,trimesh,os,sys,math,numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'assets'
ren=vtk.vtkRenderer();ren.SetBackground(.80,.86,.83);ren.SetBackground2(.94,.95,.91);ren.GradientBackgroundOn();ren.SetUseShadows(False)
win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1600,1000);win.AddRenderer(ren);win.SetMultiSamples(8)

def add_model(file, pos=(0,0,0),rot=0,scale=1):
 s=trimesh.load(str(ASSETS/file),force='scene')
 for name in s.graph.nodes_geometry:
  transform,gn=s.graph.get(name);mesh=s.geometry[gn]
  if 'SIGN_' in name:continue
  points=vtk.vtkPoints(); v=trimesh.transform_points(mesh.vertices,transform)
  points.SetNumberOfPoints(len(v))
  for i,p in enumerate(v):
   x,y,z=p;x*=scale;y*=scale;z*=scale
   x,z=x*math.cos(rot)-z*math.sin(rot),x*math.sin(rot)+z*math.cos(rot)
   points.SetPoint(i,float(x+pos[0]),float(y+pos[1]),float(z+pos[2]))
  faces=vtk.vtkCellArray()
  for tri in mesh.faces:
   faces.InsertNextCell(3)
   for idx in tri:faces.InsertCellPoint(int(idx))
  poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(faces)
  normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.AutoOrientNormalsOn();normals.ConsistencyOn();normals.SplittingOff();normals.Update()
  mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());act=vtk.vtkActor();act.SetMapper(mapper)
  mat=getattr(mesh.visual,'material',None)
  if mat is not None and hasattr(mat,'baseColorFactor'):
   factor=np.array(mat.baseColorFactor if mat.baseColorFactor is not None else [255,255,255,255]).astype(float)[:3]/255
   act.GetProperty().SetColor(*tuple(map(float,factor)))
  else:act.GetProperty().SetColor(.8,.7,.6)
  act.GetProperty().SetAmbient(.45);act.GetProperty().SetDiffuse(.55)
  act.GetProperty().SetSpecular(.09);act.GetProperty().SetSpecularPower(16)
  ren.AddActor(act)

print('Loading environment...')
add_model('mercy_factory_diorama.glb')
locations=[(-22.0,-16.3),(-16.5,-16.3),(-21,-11.3),(-16,-11.5),(-3.2,-16.3),(3.2,-16.3),(-3,-11.2),(2.9,-11.2),(15.8,-16.3),(21.8,-16.3),(15.7,-11.3),(21.3,-11.5),(12.7,18.4),(17.5,18.0),(21.5,18.5),(26,18.2),(24,12.6),(-23.4,15.0),(-20.2,14.8),(-22,12.0),(-14.5,15.0),(-8.0,-6.5),(8.0,-6.5),(6.0,1.0),(15.2,14.0),(30,6.5),(-29,6.2),(0,-4.6)]
print('Loading 28 unique people...')
for i,(x,z) in enumerate(locations):
 add_model('mercy_person_%02d.glb'%i,(x,0,z),rot=0.2*i)
add_model('mercy_truck.glb',(1.5,0,1.4))
add_model('mercy_forklift.glb',(13.0,0,14.8))
cam=ren.GetActiveCamera();cam.SetPosition(59,77,71);cam.SetFocalPoint(0,1,0);cam.SetViewUp(0,1,0);cam.ParallelProjectionOn();cam.SetParallelScale(38)
light=vtk.vtkLight();light.SetLightTypeToSceneLight();light.SetPosition(-20,65,50);light.SetFocalPoint(0,0,0);light.SetIntensity(1.2);ren.AddLight(light)
light2=vtk.vtkLight();light2.SetLightTypeToSceneLight();light2.SetPosition(20,43,-40);light2.SetIntensity(.5);ren.AddLight(light2)
print('rendering');win.Render()
f=vtk.vtkWindowToImageFilter();f.SetInput(win);f.Update()
out=ROOT/'previews'/'factory-studio-v6.png';writer=vtk.vtkPNGWriter();writer.SetFileName(str(out));writer.SetInputConnection(f.GetOutputPort());writer.Write();print('Saved',out)
