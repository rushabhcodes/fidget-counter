"""Export and check a glue-on magnet retainer for the existing 58 mm base.

Run with Python containing CadQuery >=2.6, trimesh, numpy and matplotlib.
The existing enclosure is read as STEP; none of its parts are regenerated.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
MECHANICAL = HERE.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", type=Path, default=HERE / "export")
args = parser.parse_args()
out = args.out.resolve()
out.mkdir(parents=True, exist_ok=True)
p = json.loads((HERE / "parameters.json").read_text())
enclosure = json.loads((MECHANICAL / "enclosure-parameters.json").read_text())
r = p["diameter"] / 2
t = p["thickness"]
gap = p["nominal_glue_gap"]
assert p["units"] == "mm"
assert p["diameter"] == enclosure["attachment_flange_diameter"]
assert t >= 0.6 and 0 <= p["phone_edge_chamfer"] < t
assert 0 < gap <= 0.1
assert math.isclose(t / p["print_layer_height"], round(t / p["print_layer_height"]))

# Flat bonding face, continuous floor, no lip in the moving cap's running gap.
# The small underside bevel removes the sharp phone-facing perimeter.
plate = (
    cq.Workplane("XY")
    .circle(r)
    .extrude(t)
    .faces("<Z")
    .edges()
    .chamfer(p["phone_edge_chamfer"])
    .val()
)
assert plate.isValid() and len(plate.Solids()) == 1
stl_file = out / "Magnet_Retainer_58mm.stl"
step_file = out / "Magnet_Retainer_58mm.step"
cq.exporters.export(plate, str(stl_file), tolerance=0.015, angularTolerance=0.04)
cq.exporters.export(plate, str(step_file))

def source(name):
    return cq.importers.importStep(str(MECHANICAL / "STEP_Parts" / f"{name}.step")).val()

bottom = source("Bottom_Cover")
housing = source("Stationary_Housing")
cap = source("Rotating_Cap")
magnets = source("MagSafe_Magnet_Array")
backing = source("Magnetic_Shield")
base_z = bottom.BoundingBox().zmin
assert math.isclose(base_z, enclosure["phone_pad_thickness"], abs_tol=1e-6)
plate_bottom = base_z - gap - t
installed = plate.translate((0, 0, plate_bottom))

# The protective pad moves below the new plate; it cannot remain in the glue joint.
pad_t = enclosure["phone_pad_thickness"]
pad = cq.Workplane("XY").circle(r).extrude(pad_t).val().translate((0, 0, plate_bottom - pad_t))
glue = cq.Workplane("XY").circle(r).extrude(gap).val().translate((0, 0, base_z - gap))
assy = cq.Assembly(name="Glue_On_Magnet_Retainer")
for name, shape, color in [
    ("Stationary_Housing_Existing", housing, (0.68, 0.73, 0.76)),
    ("Bottom_Cover_Existing", bottom, (0.40, 0.48, 0.53)),
    ("Attachment_Magnets_Existing", magnets, (0.66, 0.70, 0.74)),
    ("Backing_Ring_Existing", backing, (0.52, 0.55, 0.60)),
    ("Magnet_Retainer_New", installed, (0.10, 0.62, 0.62)),
    ("Glue_Bondline_Reference", glue, (0.95, 0.67, 0.22)),
    ("Protective_Pad_Relocated_Reference", pad, (0.13, 0.16, 0.20)),
]:
    assy.add(shape, name=name, color=cq.Color(*color))
assy.export(str(out / "Retainer_Installed_Reference.step"))

mesh = trimesh.load_mesh(stl_file)
assert mesh.is_watertight and mesh.is_winding_consistent
assert mesh.body_count == 1 and mesh.volume > 0
assert abs(mesh.bounds[0, 2]) < 1e-6
assert abs(mesh.extents[2] - t) < 1e-6
assert max(abs(mesh.extents[:2] - p["diameter"])) < 0.02

checks = []
for name, shape in [
    ("Bottom_Cover", bottom),
    ("Stationary_Housing", housing),
    ("MagSafe_Magnet_Array", magnets),
    ("Magnetic_Shield", backing),
    ("Rotating_Cap_Released", cap),
    ("Rotating_Cap_Pressed", cap.translate((0, 0, -enclosure["button_travel"]))),
]:
    overlap = installed.intersect(shape).Volume()
    assert overlap < 1e-6, (name, overlap)
    checks.append({"existing_part": name, "retainer_overlap_mm3": round(overlap, 8)})

# Check actual exported solids under every disc footprint, including the bevel.
coverage = []
for index, magnet in enumerate(magnets.Solids(), start=1):
    center = magnet.Center()
    probe = cq.Workplane("XY").center(center.x, center.y).circle(
        enclosure["attachment_disc_diameter"] / 2
    ).extrude(t).val()
    missing = probe.cut(plate).Volume()
    assert missing < 1e-6, (index, missing)
    coverage.append({"magnet": index, "uncovered_volume_mm3": round(missing, 8)})
assert len(coverage) == enclosure["attachment_disc_count"] == 24

# The entire bonding face must contact the original solid underside in projection.
probe_h = 0.001
bond_probe = cq.Workplane("XY").circle(r).extrude(probe_h).val().translate((0, 0, base_z))
missing_bond = bond_probe.cut(bottom).Volume()
assert missing_bond < 1e-6
reloaded = cq.importers.importStep(str(step_file)).val()
assert reloaded.isValid() and len(reloaded.Solids()) == 1
assert abs(reloaded.Volume() - plate.Volume()) < 1e-5

report = {
    "status": "CAD and exported mesh checks passed; physical fit and strength untested",
    "parameters": p,
    "existing_model": "mechanical/STEP_Parts; enclosure-parameters.json",
    "existing_bottom_already_has_continuous_floor": True,
    "retainer_valid_solid": plate.isValid(),
    "retainer_solids": len(plate.Solids()),
    "volume_mm3": round(plate.Volume(), 4),
    "print_bounds_mm": mesh.bounds.round(5).tolist(),
    "stl_watertight": bool(mesh.is_watertight),
    "stl_winding_consistent": bool(mesh.is_winding_consistent),
    "stl_bodies": mesh.body_count,
    "full_bond_face_area_mm2": round(math.pi * r**2, 3),
    "nominal_added_phone_separation_mm": round(t + gap, 3),
    "installed_retainer_z_mm": [round(plate_bottom, 3), round(base_z - gap, 3)],
    "new_phone_plane_z_mm": round(plate_bottom - pad_t, 3),
    "new_overall_height_including_relocated_pad_mm": round(
        enclosure["overall_height"] - (plate_bottom - pad_t), 3
    ),
    "original_pad_removed_from_glue_joint": True,
    "rigid_collision_checks": checks,
    "magnet_coverage": coverage,
    "physical_checks_required": [
        "Flat print and dry fit against the actual stationary base",
        "Glue bond and plate resistance to repeated phone pull-off and edge peeling",
        "Phone holding, sliding and rotation force after adding 0.65 mm separation",
    ],
    "files": {
        file.name: {"sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        for file in (stl_file, step_file)
    },
}
(out / "geometry-checks.json").write_text(json.dumps(report, indent=2) + "\n")

# Engineering preview: actual STEP meshes plus a dimensioned local section.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

background = "#f5f4ef"
ink = "#19343d"
muted = "#53666c"
teal = "#138c8c"
fig = plt.figure(figsize=(13.6, 8), facecolor=background)
fig.text(0.045, 0.925, "A thin base that keeps the magnets covered", fontsize=22, weight="bold", color=ink)
fig.text(0.045, 0.88, "Glue-on retainer for the existing 58 mm stationary base", fontsize=13, color=muted)

def draw_solid(ax, shape, color):
    vertices, faces = shape.tessellate(0.06, 0.08)
    points = np.array([[v.x, v.y, v.z] for v in vertices])
    triangles = points[np.asarray(faces)]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-9)
    light = np.array([0.3, -0.5, 0.81])
    shade = 0.58 + 0.42 * np.abs(normals @ light)
    ax.add_collection3d(Poly3DCollection(triangles, facecolors=shade[:, None] * np.array(color), edgecolors="none"))

ax = fig.add_axes([0.015, 0.32, 0.51, 0.48], projection="3d", facecolor=background)
draw_solid(ax, bottom.translate((0, 0, 5)), (0.56, 0.64, 0.67))
draw_solid(ax, magnets.translate((0, 0, 9)), (0.72, 0.75, 0.77))
draw_solid(ax, installed.translate((0, 0, -2.5)), (0.08, 0.64, 0.63))
ax.set(xlim=(-32, 32), ylim=(-32, 32), zlim=(-5, 13))
ax.set_box_aspect((64, 64, 30))
ax.view_init(elev=28, azim=-60)
ax.set_axis_off()
fig.text(0.055, 0.79, "Exploded view", fontsize=14, weight="bold", color=ink)
fig.text(0.055, 0.305, "Silver: existing magnets   /   Gray: existing bottom cover", fontsize=10, color=muted)
fig.text(0.055, 0.27, "Teal: new continuous retainer plate", fontsize=12, weight="bold", color=teal)

detail = fig.add_axes([0.565, 0.43, 0.39, 0.28], facecolor=background)
detail.add_patch(Rectangle((0, 1.65), 12, 0.6, facecolor="#91a1a8"))
detail.add_patch(Rectangle((3.5, 2.30), 5, 1.5, facecolor="#c5cbd0", edgecolor="#7b898f"))
detail.add_patch(Rectangle((0, 1.60), 12, 0.05, facecolor="#d69c32"))
detail.add_patch(Rectangle((0, 1.0), 12, 0.6, facecolor=teal))
detail.add_patch(Rectangle((0, 0.8), 12, 0.2, facecolor="#293d45"))
detail.text(6, 3.0, "Magnet", ha="center", fontsize=10, color=ink)
detail.text(6, 1.94, "Existing solid floor", ha="center", va="center", fontsize=9, color=ink)
detail.text(6, 1.30, "New retainer", ha="center", va="center", fontsize=9, color="white")
detail.text(0.1, 0.45, "Protective film moved below the retainer", fontsize=9, color=muted)
detail.annotate("", xy=(12.8, 1.0), xytext=(12.8, 1.6), arrowprops={"arrowstyle": "|-|", "color": ink})
detail.text(13.2, 1.30, "0.60 mm", va="center", fontsize=10, color=ink)
detail.annotate("Thin CA glue layer", xy=(10.2, 1.625), xytext=(11.8, 2.7), fontsize=9, color=muted, arrowprops={"arrowstyle": "-", "color": muted})
detail.set(xlim=(-0.4, 16), ylim=(0.3, 4.3))
detail.set_axis_off()
fig.text(0.565, 0.79, "Through one magnet pocket", fontsize=14, weight="bold", color=ink)
fig.text(0.565, 0.745, "Section diagram · thicknesses enlarged for clarity", fontsize=10, color=muted)
fig.text(0.565, 0.34, "58 mm diameter  ×  0.60 mm thick", fontsize=17, weight="bold", color=ink)
fig.text(0.565, 0.29, "Flat glue face · no holes · no raised rim", fontsize=11, color=muted)
fig.text(0.565, 0.245, "Print flat, 100% solid, three 0.20 mm layers.", fontsize=11, color=muted)
fig.text(0.045, 0.155, "Bonds to the fixed base. The rotating cap remains clear.", fontsize=13, weight="bold", color=ink)
fig.text(0.045, 0.105, "+0.65 mm nominal thickness including glue. Recheck phone holding force after fitting.", fontsize=11, color=muted)
fig.text(0.045, 0.06, "CAD checked against the saved enclosure. Glue strength, printing tolerances and phone pull-off force still need a physical test.", fontsize=10, color=muted)
fig.savefig(out / "retainer-preview.png", dpi=170, facecolor=background)
plt.close(fig)
print(json.dumps({"output": str(out), "solid": report["retainer_solids"], "watertight": report["stl_watertight"], "covered_magnets": len(coverage), "collision_checks": len(checks)}, indent=2))
