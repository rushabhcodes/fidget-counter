"""Render V5 CAD cutaway and exploded views; no generative image geometry."""
from pathlib import Path
import json,math
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
selected={r['name']:r for r in rows if not r['name'].startswith('Cap_') or r['name']=='Cap_circular'}
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(1600,1000);window.SetMultiSamples(8)
colors={'Bearing_Carrier':(.92,.57,.18),'Inner_Race_Nut':(.98,.72,.29),'Bearing_6708':(.68,.72,.78),'PCB':(.16,.5,.33),'Cap_circular':(.08,.42,.55),'Stationary_Base':(.39,.44,.49),'Bottom_Tray':(.25,.29,.33),'Return_Springs':(.75,.76,.8),'Actuator_Ring':(.38,.76,.62)}
def actor(row,offset=0,cut=False):
 v=np.asarray(row['vertices'],dtype=np.float64).copy();v[:,2]+=offset
 f=np.asarray(row['faces'],dtype=np.int64)
 points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v,deep=True))
 cells=vtk.vtkCellArray();cells.SetCells(len(f),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(f),3),f)).ravel(),deep=True))
 poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
 mapper=vtk.vtkPolyDataMapper()
 if cut:
  plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(0,1,0)
  clip=vtk.vtkClipPolyData();clip.SetInputData(poly);clip.SetClipFunction(plane);mapper.SetInputConnection(clip.GetOutputPort())
 else:mapper.SetInputData(poly)
 a=vtk.vtkActor();a.SetMapper(mapper);a.GetProperty().SetColor(colors.get(row['name'],row['color']));a.GetProperty().SetInterpolationToPhong();a.GetProperty().SetSpecular(.15);return a
for index,mode in enumerate(['Cutaway','Exploded']):
 renderer=vtk.vtkRenderer();renderer.SetViewport(index*.5,0,(index+1)*.5,1);renderer.SetBackground(.965,.974,.98);window.AddRenderer(renderer)
 offsets={'Cap_circular':36,'Magnet':31,'Encoder_Spacer':31,'Actuator_Ring':29,'Inner_Race_Nut':25,'Bearing_6708':13,'Bearing_Carrier':6,'Outer_Race_Retainer':11,'Cap_Retainer_Screws':36,'PCB_Fasteners':3,'Guide_Fasteners':4} if index else {}
 for name,row in selected.items():
  if name in ['J_DEBUG','Button','Sensor'] and index==1:continue
  renderer.AddActor(actor(row,offsets.get(name,0),cut=(index==0 and name in ['Cap_circular','Stationary_Base','Bottom_Tray','Outer_Race_Retainer','Inner_Race_Nut'])))
 cam=renderer.GetActiveCamera();cam.SetPosition(75,-110,85 if index==0 else 115);cam.SetFocalPoint(0,0,10 if index==0 else 25);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(40 if index==0 else 55)
 renderer.ResetCameraClippingRange()
 title=vtk.vtkTextActor();title.SetInput('Cutaway: bearing around the PCB' if index==0 else 'Exploded: separate rotation and press parts');title.SetPosition(30,930);title.GetTextProperty().SetFontSize(24);title.GetTextProperty().SetColor(.1,.18,.24);renderer.AddActor2D(title)
 caption=vtk.vtkTextActor();caption.SetInput('Base 58 mm | Released height 17.2 mm | Press stroke 0.8 mm' if index==0 else 'Blue: rotor | Silver: bearing | Amber: guided carrier');caption.SetPosition(30,50);caption.GetTextProperty().SetFontSize(19);caption.GetTextProperty().SetColor(.2,.28,.34);renderer.AddActor2D(caption)
 footer=vtk.vtkTextActor();footer.SetInput('Nominal CAD prototype. Bearing and spring models are reference geometry.');footer.SetPosition(30,22);footer.GetTextProperty().SetFontSize(14);footer.GetTextProperty().SetColor(.35,.4,.45);renderer.AddActor2D(footer)
window.Render();image=vtk.vtkWindowToImageFilter();image.SetInput(window);image.SetInputBufferTypeToRGB();image.ReadFrontBufferOff();image.Update()
out=root/'previews/bearing-layout.png';out.parent.mkdir(exist_ok=True)
writer=vtk.vtkPNGWriter();writer.SetFileName(str(out));writer.SetInputConnection(image.GetOutputPort());writer.Write();window.Finalize();print(out)
