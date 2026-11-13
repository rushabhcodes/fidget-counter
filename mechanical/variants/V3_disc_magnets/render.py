"""Render the exact V3 supplier/printed meshes, with every handled layer visible."""
from pathlib import Path
import json
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import trimesh

H = Path(__file__).resolve().parent
G = H / "generated"
rows = json.loads((G / "scene_meshes.json").read_text())
P=json.loads((H/"parameters.json").read_text());VERSION=P["release"];E=P["encoder"]
BG, INK, MUTED = "#f2f5f7", "#203642", "#536b7b"
TYPES = {"print": "#237d99", "buy": "#ae642a", "pcba": "#327750"}


def rgb(color):
    return matplotlib.colors.to_rgb(color)


def actor(row, exploded=False, cut=False):
    vertices = np.array(row["vertices"], dtype=np.float64)
    if exploded:
        # More separation in this orthographic drawing keeps the tiny encoder
        # visible below the cap. Display translations do not alter any solid.
        vertices[:, 2] += 120 if row["name"] == "Magnet" else row["exploded_dz_mm"]
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices, deep=True))
    faces = np.asarray(row["faces"], dtype=np.int64)
    polys = vtk.vtkCellArray()
    polys.SetCells(len(faces), numpy_to_vtkIdTypeArray(np.column_stack((np.full(len(faces), 3), faces)).ravel(), deep=True))
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(polys)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(38)
    normals.ConsistencyOn()
    if cut:
        plane = vtk.vtkPlane()
        plane.SetNormal(0, 1, 0)
        planes = vtk.vtkPlaneCollection()
        planes.AddItem(plane)
        clip = vtk.vtkClipClosedSurface()
        clip.SetInputData(poly)
        clip.SetClippingPlanes(planes)
        clip.GenerateFacesOn()
        normals.SetInputConnection(clip.GetOutputPort())
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    result = vtk.vtkActor()
    result.SetMapper(mapper)
    prop = result.GetProperty()
    prop.SetColor(*row["color"])
    prop.SetInterpolationToPhong()
    prop.SetAmbient(0.28)
    prop.SetDiffuse(0.72)
    prop.SetSpecular(0.23)
    prop.SetSpecularPower(35)
    return result


def snapshot(exploded=False, cut=False, bottom=False, encoder_detail=False, size=(1100, 1950)):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*rgb(BG))
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(*size)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    for row in rows:
        if encoder_detail and row["name"] not in ["Cap_circular","Magnet","PCB","Electronic_U2"]:
            continue
        if bottom and row["name"] != "Base_V3_Discs":
            continue
        renderer.AddActor(actor(row, exploded, cut))
    renderer.AutomaticLightCreationOff()
    lights = [((100, -160, -200), 0.8), ((-100, 40, -180), 0.45)] if bottom else [((100, -160, 280), 0.8), ((-100, 40, 220), 0.45)]
    for position, strength in lights:
        light = vtk.vtkLight()
        light.SetPosition(*position)
        light.SetFocalPoint(0, 0, 80 if exploded else 8)
        light.SetIntensity(strength)
        renderer.AddLight(light)
    camera = renderer.GetActiveCamera()
    if exploded:
        camera.SetFocalPoint(0, 0, 82)
        camera.SetPosition(140, -240, 183)
        camera.SetParallelScale(95)
    elif encoder_detail:
        camera.SetFocalPoint(0,0,16.5)
        camera.SetPosition(0,-100,16.5)
        camera.SetParallelScale(6.4)
    elif bottom:
        camera.SetFocalPoint(0, 0, 4)
        camera.SetPosition(0, 0, -100)
        camera.SetParallelScale(36)
    else:
        camera.SetFocalPoint(0, 0, 8)
        camera.SetPosition(80, -115, 90)
        camera.SetParallelScale(40)
    camera.SetViewUp(*(0, 1, 0) if bottom else (0, 0, 1))
    camera.ParallelProjectionOn()
    renderer.ResetCameraClippingRange()
    window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(window)
    image.ReadFrontBufferOff()
    image.SetInputBufferTypeToRGB()
    image.Update()
    output = image.GetOutput()
    w, h, _ = output.GetDimensions()
    pixels = vtk_to_numpy(output.GetPointData().GetScalars()).reshape(h, w, 3)[::-1].copy()
    return pixels, renderer, window


pixels, renderer, window = snapshot(exploded=True)
fig = plt.figure(figsize=(15.5, 16), facecolor=BG)
view = fig.add_axes([0.015, 0.07, 0.49, 0.80])
view.imshow(pixels)
view.axis("off")
fig.text(0.055, 0.954, f"v{VERSION} · one magnet type, two orientations", color=INK, fontsize=25, weight="bold")
fig.text(0.055, 0.922, "21 identical Ø6 × 3 mm axial discs · 20 underneath + 1 on edge in the cap", color=MUTED, fontsize=12)
for x, kind, label in [(0.055, "print", "3D PRINT"), (0.23, "buy", "BUY / FABRICATE"), (0.47, "pcba", "ASSEMBLED PCB")]:
    fig.text(x, 0.891, "●  " + label, color=TYPES[kind], fontsize=10.5, weight="bold")
labels = [
    ("print", "Rotating cap", "1 PETG cap · keyed encoder slot · 11 updated styles", [28, 0, 164]),
    ("buy", "Encoder magnet", "1 × same Ø6 × 3 mm AXIAL disc · mounted on edge", [1.5, 0, 137]),
    ("buy", "Thin-section ball bearing", "1 × 6808-ZZ / 61808-2Z · 40 × 52 × 7 mm", [26, 0, 117]),
    ("buy", "PCB screws", "2 × M2 × 4 mm nylon · head ≤Ø3.8 × 1.3 mm", [11.74, 11.74, 103]),
    ("pcba", "Populated RevC PCB + underside holder", "1 × Ø36.5 × 1.0 mm · all 27 fitted components", [18, 0, 86.5]),
    ("buy", "CR2450 battery", "1 × 3 V primary cell · Ø24.5 × 5 mm", [12.25, 0, 63]),
    ("print", "One-piece stationary base", "20 blind Ø6.4 mm pockets open on the underside", [28, 0, 37]),
    ("buy", "20 bottom-insert attachment discs", "Ø6 × 3 mm N52 AXIAL · sidewall bond · 0.2 mm recess", [27.5, 0, 15.9]),
]
for number, (kind, title, detail, point) in enumerate(labels, 1):
    renderer.SetWorldPoint(*point, 1)
    renderer.WorldToDisplay()
    sx, sy, _ = renderer.GetDisplayPoint()
    x, y = fig.transFigure.inverted().transform(view.transData.transform([sx, pixels.shape[0] - 1 - sy]))
    label_y = y - (0.008 if number == 4 else 0)
    fig.add_artist(Line2D([x + 0.008, 0.497, 0.528], [y, label_y, label_y], transform=fig.transFigure, color="#a4b2bc", linewidth=0.9))
    fig.text(0.542, label_y + 0.002, f"{number:02d}", color=TYPES[kind], fontsize=11, weight="bold", va="center")
    fig.text(0.58, label_y + 0.005, title, color=INK, fontsize=12.5, weight="bold", va="center")
    fig.text(0.58, label_y - 0.014, detail, color=MUTED, fontsize=9.4, va="center")
fig.add_artist(Line2D([0.055, 0.95], [0.065, 0.065], transform=fig.transFigure, color="#c6cfd5", linewidth=1))
fig.text(0.055, 0.043, "Assembled: Ø58 mm base · up to Ø61.6 mm cap · 20.9 mm high. Two printed parts; no steel backing or separate magnet carrier.", color=INK, fontsize=10)
fig.text(0.055, 0.024, "Nominal CAD; separations exaggerated. Verify printed fits, polarity, phone holding force and Hall/BLE performance on a prototype.", color=MUTED, fontsize=9.5)
fig.savefig(H / f"exploded-v{VERSION}.png", dpi=160, facecolor=BG)
plt.close(fig)
window.Finalize()

fig, axes = plt.subplots(1, 3, figsize=(16, 5.8), facecolor=BG)
for ax, cut, bottom, title in zip(axes, [False, False, True], [False, True, False], ["Assembled V3", "Underside · empty pockets", "Cutaway · blind stops"]):
    pixels, _, window = snapshot(cut=cut, bottom=bottom, size=(1000, 820))
    ax.imshow(pixels)
    ax.axis("off")
    ax.set_title(title, color=INK, fontsize=15, loc="left", pad=10)
    window.Finalize()
fig.subplots_adjust(left=0.025, right=0.975, top=0.88, bottom=0.12, wspace=0.04)
fig.text(0.04, 0.06, f"v{VERSION} · 20 bottom discs + same disc on edge in the cap · 20.9 mm height · 1.8 mm sensor clearance", fontsize=11, color=INK)
fig.savefig(H / "review.png", dpi=160, facecolor=BG)
print(H / f"exploded-v{VERSION}.png")
print(H / "review.png")

# True center sections avoid an opaque back wall hiding the slot clearance.
fig,ax=plt.subplots(figsize=(11,8.4),facecolor=BG)
ax.set_facecolor(BG)
for row in rows:
    if row['name'] not in ['Cap_circular','Magnet','PCB','Electronic_U2']:continue
    mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=False)
    section=mesh.section(plane_origin=[0,0,0],plane_normal=[0,1,0])
    if section is None:continue
    for path in section.discrete:
        ax.add_patch(Polygon(path[:,[0,2]],closed=True,facecolor=row['color'],edgecolor=INK,linewidth=.9))
ax.set_xlim(-7.5,7.5);ax.set_ylim(10.5,23);ax.set_aspect('equal');ax.axis('off')
fig.subplots_adjust(left=.02,right=.98,bottom=.14,top=.88)
fig.text(.05,.945,'Same Ø6 × 3 mm axial disc · mounted on edge',fontsize=20,weight='bold',color=INK)
fig.text(.05,.905,'Actual center section through the keyed slot, upper stop and unchanged Hall sensor',fontsize=11,color=MUTED)
ax.annotate('',xy=(1.35,16.9),xytext=(-1.35,16.9),arrowprops=dict(arrowstyle='<->',color='white',lw=2))
ax.text(-1.15,17.65,'N',color='#fff1e8',weight='bold',fontsize=16,ha='center')
ax.text(1.15,17.65,'S',color='#d6edff',weight='bold',fontsize=16,ha='center')
ax.annotate('3 mm pole-to-pole axis\nparallel to PCB',xy=(0,16.9),xytext=(-6.6,15.8),color=INK,fontsize=11,ha='left',arrowprops=dict(arrowstyle='-',color=MUTED),bbox=dict(facecolor=BG,edgecolor='none',pad=3))
ax.annotate('Keyed slot\n3.4 × 6.4 mm',xy=(2.15,18.9),xytext=(3.25,18.3),color=INK,fontsize=11,arrowprops=dict(arrowstyle='-',color=MUTED))
ax.annotate('1.2 mm roof',xy=(0,20.5),xytext=(-5.5,22),color=INK,fontsize=11,arrowprops=dict(arrowstyle='-',color=MUTED))
ax.annotate('',xy=(3.5,E['bottom_z_mm']),xytext=(3.5,E['sensor_top_z_mm']),arrowprops=dict(arrowstyle='<->',color=MUTED))
ax.plot([1.6,3.8],[E['bottom_z_mm']]*2,color=MUTED,lw=.7)
ax.plot([.45,3.8],[E['sensor_top_z_mm']]*2,color=MUTED,lw=.7)
ax.text(3.9,12.7,'1.8 mm\nclearance',fontsize=10,color=INK,va='center')
ax.annotate('Hall sensor',xy=(0,11.9),xytext=(-6.6,12.6),color=INK,fontsize=11,arrowprops=dict(arrowstyle='-',color=MUTED))
ax.text(-6.5,10.85,'PCB',color='white',fontsize=11,va='center')
fig.text(.05,.085,'21 identical axial discs: 20 flat underneath + 1 on edge in the rotating cap. Overall height: 20.9 mm.',fontsize=11,color=INK)
fig.text(.05,.05,'The magnetic axis rotates in the PCB plane. N/S assignment shown is illustrative; qualify field strength and counting on a prototype.',fontsize=10,color=MUTED)
fig.savefig(H/'encoder-orientation.png',dpi=160,facecolor=BG)
print(H/'encoder-orientation.png')
