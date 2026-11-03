"""Render actual V2 CAD meshes and the phone-side polarity assembly template."""
from pathlib import Path
import json,math
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
H=Path(__file__).resolve().parent;G=H/'generated'
rows=json.loads((G/'scene_meshes.json').read_text());P=json.loads((H/'parameters.json').read_text())
rows=[r for r in rows if not r['name'].startswith('Cap_') or r['name']=='Cap_circular']

def actor(row,dz=0,cut=False):
    v=np.array(row['vertices'],dtype=np.float64);v[:,2]+=dz;f=np.asarray(row['faces'],dtype=np.int64)
    points=vtk.vtkPoints();points.SetData(numpy_to_vtk(v,deep=True))
    cells=vtk.vtkCellArray();cells.SetCells(len(f),numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(f),3),f)).ravel(),deep=True))
    poly=vtk.vtkPolyData();poly.SetPoints(points);poly.SetPolys(cells)
    normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SetFeatureAngle(38);normals.ConsistencyOn();normals.SplittingOn()
    if cut:
        plane=vtk.vtkPlane();plane.SetNormal(0,1,0);planes=vtk.vtkPlaneCollection();planes.AddItem(plane)
        clip=vtk.vtkClipClosedSurface();clip.SetInputData(poly);clip.SetClippingPlanes(planes);clip.GenerateFacesOn();normals.SetInputConnection(clip.GetOutputPort())
    mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());a=vtk.vtkActor();a.SetMapper(mapper)
    prop=a.GetProperty();prop.SetColor(*row['color']);prop.SetInterpolationToPBR();metal=any(s in row['name']for s in ['Bearing','Backing','Inner_S','Outer_N','Cell','Magnet'])
    prop.SetMetallic(.8 if metal else 0);prop.SetRoughness(.32 if metal else .5);prop.SetAmbient(.24)
    return a

def label(renderer,text,x,y,size=21):
    t=vtk.vtkTextActor();t.SetInput(text);t.SetPosition(x,y);t.GetTextProperty().SetFontSize(size);t.GetTextProperty().SetColor(.12,.18,.23);renderer.AddActor2D(t)

window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.SetSize(2400,1050);window.SetMultiSamples(8)
for i,mode in enumerate(['Assembled V2','Cutaway','Exploded']):
    renderer=vtk.vtkRenderer();renderer.SetViewport(i/3,0,(i+1)/3,1);renderer.SetBackground(.95,.965,.975);window.AddRenderer(renderer)
    for row in rows:
        name=row['name'];dz=0
        if mode=='Exploded':
            dz=(-22 if name=='Magnet_Carrier_V2' else (-14 if name.startswith(('Inner_S','Outer_N')) else (-7 if name=='Steel_Backing_V2' else (42 if name=='Cap_circular' else (35 if name=='Magnet' else (15 if name.startswith('Bearing_') else (5 if name.startswith('Electronic_') or name in ['PCB','Cell','PCB_Fasteners'] else 0)))))))
        renderer.AddActor(actor(row,dz,mode=='Cutaway'))
    cam=renderer.GetActiveCamera();cam.SetPosition(80,-115,100);cam.SetFocalPoint(0,0,15 if mode=='Exploded' else 8);cam.SetViewUp(0,0,1);cam.ParallelProjectionOn();cam.SetParallelScale(59 if mode=='Exploded' else 45);renderer.ResetCameraClippingRange()
    renderer.AutomaticLightCreationOff()
    for xyz,intensity in [((50,-70,110),1.1),((-70,-20,60),.8),((20,70,90),1.1)]:
        light=vtk.vtkLight();light.SetPosition(*xyz);light.SetFocalPoint(0,0,8);light.SetIntensity(intensity);renderer.AddLight(light)
    label(renderer,mode,24,990,28)
    label(renderer,{'Assembled V2':'58 mm base | 16.4 mm physical height','Cutaway':'Actual supplier CAD | encoder gap unchanged','Exploded':'36 magnets + steel backing + printed carrier'}[mode],24,48,18)
    label(renderer,'Prototype alternative: pull-force and physical fit unverified',24,22,14)
window.Render();im=vtk.vtkWindowToImageFilter();im.SetInput(window);im.ReadFrontBufferOff();im.Update();writer=vtk.vtkPNGWriter();writer.SetFileName(str(H/'review.png'));writer.SetInputConnection(im.GetOutputPort());writer.Write();window.Finalize()

svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="650" viewBox="0 0 1100 650"><rect width="1100" height="650" fill="white"/>']
for index,(title,poles) in enumerate([('Phone-facing underside',['S','N']),('Top / loading side',['N','S'])]):
    cx=275+550*index;cy=305;scale=7.2
    svg.append(f'<text x="{cx}" y="40" text-anchor="middle" font-family="sans-serif" font-size="25">{title}</text>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{29*scale}" fill="#dbe4e9" stroke="#405a6b"/><circle cx="{cx}" cy="{cy}" r="{21.3*scale}" fill="white" stroke="#405a6b"/>')
    for row,radius in enumerate(P['magnet']['row_center_radii_mm']):
        pole=poles[row];color='#3d78b3' if pole=='S' else '#c9514c'
        for station in range(18):
            angle=station*20;theta=math.radians(angle);x=cx+radius*scale*math.cos(theta);y=cy+radius*scale*math.sin(theta)
            svg.append(f'<g transform="translate({x},{y}) rotate({angle})"><rect x="{-scale}" y="{-3*scale}" width="{2*scale}" height="{6*scale}" rx="1" fill="{color}" stroke="white"/><text text-anchor="middle" y="5" fill="white" font-family="sans-serif" font-size="13">{pole}</text></g>')
    svg.append(f'<text x="{cx}" y="305" text-anchor="middle" font-family="sans-serif" font-size="19">18 magnets per row</text>')
    svg.append(f'<text x="{cx}" y="340" text-anchor="middle" font-family="sans-serif" font-size="16">All magnets in each row have the same pole</text>')
svg.append('<text x="550" y="585" text-anchor="middle" font-family="sans-serif" font-size="20">Polarity assembly template — actual purchased magnets are unmarked nickel, not red/blue.</text><text x="550" y="620" text-anchor="middle" font-family="sans-serif" font-size="18">Verify every magnet with a pole indicator before bonding. Do not alternate around the circle.</text></svg>')
(H/'polarity.svg').write_text(''.join(svg)+'\n');print(H/'review.png');print(H/'polarity.svg')
