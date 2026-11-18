"""Render the delivered STEP base: side, interior and underside views."""
from pathlib import Path
import cadquery as cq
import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray, vtk_to_numpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = Path(__file__).resolve().parent
shape = cq.importers.importStep(str(H / "generated/STEP/Base_V3_Discs.step")).val()
vertices, faces = shape.tessellate(.025, .09)
points = vtk.vtkPoints()
points.SetData(numpy_to_vtk(np.array([v.toTuple() for v in vertices]), deep=True))
cells = vtk.vtkCellArray()
cells.SetCells(len(faces), numpy_to_vtkIdTypeArray(
    np.column_stack((np.full(len(faces), 3), faces)).astype(np.int64).ravel(), deep=True))
poly = vtk.vtkPolyData()
poly.SetPoints(points)
poly.SetPolys(cells)


def snapshot(position, up):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(.95, .97, .98)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1000, 850)
    window.SetMultiSamples(8)
    window.AddRenderer(renderer)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(38)
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(.43, .58, .65)
    actor.GetProperty().SetAmbient(.25)
    actor.GetProperty().SetSpecular(.2)
    actor.GetProperty().SetSpecularPower(30)
    renderer.AddActor(actor)
    camera = renderer.GetActiveCamera()
    camera.SetFocalPoint(0, 0, 6)
    camera.SetPosition(*position)
    camera.SetViewUp(*up)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(29)
    renderer.ResetCameraClippingRange()
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.SetInputBufferTypeToRGB()
    capture.Update()
    output = capture.GetOutput()
    w, h, _ = output.GetDimensions()
    pixels = vtk_to_numpy(output.GetPointData().GetScalars()).reshape(h, w, 3)[::-1].copy()
    window.Finalize()
    return pixels


fig, axes = plt.subplots(1, 3, figsize=(16, 5.8), facecolor="#f2f7fa")
views = [((0, -100, 6), (0, 0, 1), "Continuous wall · no open windows"),
         ((70, -100, 105), (0, 0, 1), "Bearing sleeve + four PCB posts"),
         ((0, 0, -100), (0, 1, 0), "20 vented magnet pockets")]
for ax, (position, up, title) in zip(axes, views):
    ax.imshow(snapshot(position, up))
    ax.axis("off")
    ax.set_title(title, color="#203642", fontsize=14, loc="left")
fig.suptitle("V3 magnet base · print phone face down · zero supports", x=.04, ha="left",
             fontsize=20, color="#203642", weight="bold")
fig.text(.04, .04, "Actual delivered STEP geometry · Ø58 mm · bearing and magnet seats preserved · 45° pocket vents · no closed roof bridges",
         fontsize=11, color="#536b7b")
fig.subplots_adjust(left=.025, right=.98, top=.82, bottom=.12, wspace=.04)
fig.savefig(H / "base-support-free.png", dpi=150, facecolor=fig.get_facecolor())
plt.close(fig)
print(H / "base-support-free.png")
