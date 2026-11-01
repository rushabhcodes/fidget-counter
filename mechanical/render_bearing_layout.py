"""Studio renders of actual released, sectioned and exploded source CAD."""
from pathlib import Path
import json
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
selected={r['name']:r for r in rows if not r['name'].startswith('Cap_') or r['name']=='Cap_circular'}

def actor(row,offset=0,cut=False,group=None):
 v=np.asarray(row['vertices'],dtype=np.float64).copy();v[:,2]+=offset
 faces=row['faces'] if group is None else row['faces'][group['first_face']:group['first_face']+group['face_count']]
 f=np.asarray(faces,dtype=np.int64)
 points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v,deep=True))
 cells=vtk.vtkCellArray();cells.SetCells(len(f),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(f),3),f)).ravel(),deep=True))
 poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
 normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(38);normals.SplittingOn();normals.ConsistencyOn();normals.Update()
 mapper=vtk.vtkPolyDataMapper()
 if cut:
  plane=vtk.vtkPlane();plane.SetOrigin(0,0,0);plane.SetNormal(0,1,0)
  planes=vtk.vtkPlaneCollection();planes.AddItem(plane)
  clip=vtk.vtkClipClosedSurface();clip.SetInputData(poly);clip.SetClippingPlanes(planes);clip.GenerateFacesOn();normals.SetInputConnection(clip.GetOutputPort());mapper.SetInputConnection(normals.GetOutputPort())
 else:mapper.SetInputConnection(normals.GetOutputPort())
 a=vtk.vtkActor();a.SetMapper(mapper)
 prop=a.GetProperty();prop.SetColor(group['color'] if group else row['color']);prop.SetInterpolationToPBR()
 finish=group.get('finish','plastic') if group else 'plastic'
 metallic,roughness={'polished':(1,.18),'steel':(.85,.32),'nylon':(0,.52),'rubber':(0,.72),'plastic':(0,.4)}[finish]
 prop.SetMetallic(metallic);prop.SetRoughness(roughness);prop.SetAmbient(.22);prop.SetDiffuse(.8)
 return a

def studio_environment():
 # Procedural HDR light rig: neutral room plus broad softboxes. This controls
 # reflections only; every visible product surface comes from the source CAD.
 width,height=512,256
 yy,xx=np.mgrid[0:height,0:width];u=xx/width;v=yy/height
 light=np.full((height,width,3),.32,dtype=np.float32)
 for x,y,sx,sy,power in [(.2,.25,.09,.13,3.0),(.72,.3,.13,.18,2.2),(.48,.72,.17,.08,1.0)]:
  du=np.minimum(abs(u-x),1-abs(u-x));patch=np.exp(-((du/sx)**8+((v-y)/sy)**8))
  light+=patch[:,:,None]*power
 image=vtk.vtkImageData();image.SetDimensions(width,height,1);image.GetPointData().SetScalars(numpy_to_vtk(light.reshape(-1,3),deep=True))
 texture=vtk.vtkTexture();texture.SetInputData(image);texture.SetColorModeToDirectScalars();texture.InterpolateOn();texture.MipmapOn()
 return texture

def render(modes,path,size):
 window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(*size);window.SetMultiSamples(8);environment=studio_environment()
 for index,mode in enumerate(modes):
  renderer=vtk.vtkRenderer();renderer.SetViewport(index/len(modes),0,(index+1)/len(modes),1);renderer.SetBackground(.94,.953,.965);renderer.SetBackground2(.995,.997,1);renderer.GradientBackgroundOn();renderer.SetEnvironmentTexture(environment);renderer.UseImageBasedLightingOn();window.AddRenderer(renderer)
  offsets={'Cap_circular':42,'Magnet':36,'Encoder_Spacer':36,'Actuator_Ring':33,'Inner_Race_Nut':29,'Bearing_6708':15,'Bearing_Carrier':8,'Outer_Race_Retainer':10,'Cap_Retainer_Screws':42,'PCB_Fasteners':3,'Guide_Fasteners':4} if mode=='Exploded' else {}
  for name,row in selected.items():
   if mode=='Bearing detail' and name!='Bearing_6708':continue
   # Section the whole assembly consistently, including metal shields, so the
   # bearing's balls, raceways and cage are visible without changing the model.
   for group in row.get('groups',[None]):
    if mode=='Bearing detail' and group['label']=='ZZ shields':continue
    cut=mode=='Cutaway' or (mode=='Bearing detail' and group['label'] in ['Inner race','Outer race'])
    renderer.AddActor(actor(row,offsets.get(name,5 if mode=='Exploded' and name.startswith('Electronic_') else 0),cut,group))
  cam=renderer.GetActiveCamera();cam.SetPosition(80,-115,100 if mode!='Bearing detail' else 65);cam.SetFocalPoint(0,0,27 if mode=='Exploded' else 9.6);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(48 if mode=='Exploded' else (29 if mode=='Bearing detail' else 45));renderer.ResetCameraClippingRange()
  # Large, soft studio lights reveal thread flanks and metallic race details.
  renderer.AutomaticLightCreationOff()
  for xyz,intensity in [((50,-70,110),1.1),((-70,-20,60),.75),((20,70,90),1.0)]:
   light=vtk.vtkLight();light.SetPosition(*xyz);light.SetFocalPoint(0,0,10);light.SetIntensity(intensity);renderer.AddLight(light)
  title=vtk.vtkTextActor();title.SetInput(mode);title.SetPosition(24,size[1]-60);title.GetTextProperty().SetFontSize(27);title.GetTextProperty().SetColor(.1,.18,.24);renderer.AddActor2D(title)
  caption=vtk.vtkTextActor();caption.SetInput({'Assembled':'58 mm base | 17.2 mm height | 0.8 mm press','Cutaway':'Source CAD section | supplier STEP electronics','Exploded':'Common bearing and spring-supported carrier','Bearing detail':'Race section, shields omitted | 25 balls | representative internals'}[mode]);caption.SetPosition(24,40);caption.GetTextProperty().SetFontSize(16);caption.GetTextProperty().SetColor(.22,.28,.34);renderer.AddActor2D(caption)
  footer=vtk.vtkTextActor();footer.SetInput('Nominal CAD; physical fit and force verification pending.');footer.SetPosition(24,18);footer.GetTextProperty().SetFontSize(12);footer.GetTextProperty().SetColor(.4,.44,.48);renderer.AddActor2D(footer)
 window.Render();im=vtk.vtkWindowToImageFilter();im.SetInput(window);im.SetInputBufferTypeToRGB();im.ReadFrontBufferOff();im.Update()
 writer=vtk.vtkPNGWriter();writer.SetFileName(str(path));writer.SetInputConnection(im.GetOutputPort());writer.Write();window.Finalize();print(path)

out=root/'previews';out.mkdir(exist_ok=True)
render(['Assembled','Cutaway','Exploded'],out/'bearing-layout.png',(2400,1050))
render(['Bearing detail'],out/'bearing-detail.png',(1200,850))
