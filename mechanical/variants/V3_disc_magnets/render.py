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

H = Path(__file__).resolve().parent
G = H / "generated"
rows = json.loads((G / "scene_meshes.json").read_text())
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


def snapshot(exploded=False, cut=False, bottom=False, size=(1100, 1950)):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*rgb(BG))
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(*size)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    for row in rows:
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
fig.text(0.055, 0.954, "v1.0.32 · bottom-loaded disc magnets", color=INK, fontsize=25, weight="bold")
fig.text(0.055, 0.922, "V3 · 20 × Ø6 × 3 mm discs insert directly into the base · actual CAD exploded", color=MUTED, fontsize=12)
for x, kind, label in [(0.055, "print", "3D PRINT"), (0.23, "buy", "BUY / FABRICATE"), (0.47, "pcba", "ASSEMBLED PCB")]:
    fig.text(x, 0.891, "●  " + label, color=TYPES[kind], fontsize=10.5, weight="bold")
labels = [
    ("print", "Rotating cap", "1 PETG cap · all 11 existing styles still fit", [28, 0, 160]),
    ("buy", "Encoder magnet", "1 × Ø5 × 1.5 mm DIAMETRIC disc · seated in cap", [2.5, 0, 134.5]),
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
fig.text(0.055, 0.043, "Assembled: Ø58 mm base · up to Ø61.6 mm cap · 16.4 mm high. Two printed parts; no steel backing or separate magnet carrier.", color=INK, fontsize=10)
fig.text(0.055, 0.024, "Nominal CAD; separations exaggerated. Verify printed fits, polarity, phone holding force and Hall/BLE performance on a prototype.", color=MUTED, fontsize=9.5)
fig.savefig(H / "exploded-v1.0.32.png", dpi=160, facecolor=BG)
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
fig.text(0.04, 0.06, "v1.0.32 · insert 20 Ø6 × 3 mm discs from the bottom · 16.4 mm height · 1.8 mm encoder gap", fontsize=11, color=INK)
fig.savefig(H / "review.png", dpi=160, facecolor=BG)
print(H / "exploded-v1.0.32.png")
print(H / "review.png")
