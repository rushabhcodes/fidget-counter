"""Closed-bottom magnet disc and M2 insert mounts for the 1.0.7 enclosure.

Builds the original parametric enclosure in a temporary directory, then applies
the revision to its exact released/pressed solids. The original design files
and published circuit stay available as the baseline.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import itertools
import json
import math
import sys
import tempfile

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
MECHANICAL = HERE.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--out", type=Path, default=HERE / "export")
args = parser.parse_args()
out = args.out.resolve()
for directory in ("Print_STL", "STEP_Parts", "Validation"):
    (out / directory).mkdir(parents=True, exist_ok=True)
p = json.loads((HERE / "parameters.json").read_text())

print("Building reference solids for exact assembly and motion checks...", flush=True)
previous_argv = sys.argv[:]
sys.path.insert(0, str(MECHANICAL))
try:
    with tempfile.TemporaryDirectory(prefix="fidget-base-reference-") as scratch:
        sys.argv = [str(MECHANICAL / "build_enclosure.py"), "--out", scratch]
        reference_file = MECHANICAL / "build_enclosure.py"
        module = ast.parse(reference_file.read_text(), filename=str(reference_file))
        # Reuse the unmodified modeling section, stopping before the baseline
        # assembly-export loop. The revision exports and audits its own parts;
        # repeating the original tessellation/exports only adds stale artifacts.
        marker = ast.parse("for state in ['Released', 'Pressed', 'Exploded', 'Top_Service']: pass").body[0]
        stop = next(i for i, node in enumerate(module.body)
                    if isinstance(node, ast.For)
                    and ast.dump(node.target) == ast.dump(marker.target)
                    and ast.dump(node.iter) == ast.dump(marker.iter))
        modeling = ast.Module(body=module.body[:stop], type_ignores=[])
        old = {"__file__": str(reference_file), "__name__": "_base_reference"}
        exec(compile(modeling, str(reference_file), "exec"), old)
        assert {"Released", "Pressed"} <= old["states"].keys()
finally:
    sys.argv = previous_argv
    sys.path.pop(0)

P = old["P"]
disk, annulus, cone, compound = (old[name] for name in ("disk", "annulus", "cone", "compound"))
mounts = old["mounts"]
pad_z = P["phone_pad_thickness"]
skin_top = old["skin_top"]
flex_z = old["flex_z"]
flex_top = flex_z + 1.1
radius = P["attachment_flange_diameter"] / 2
pocket_r = p["magnet_pocket_diameter"] / 2
magnet_r = P["attachment_disc_diameter"] / 2
assert p["units"] == "mm"
assert 0 < 2 * (magnet_r - pocket_r) <= 0.10
assert (p["boss_diameter"] - p["insert_outer_diameter"]) / 2 >= 1.3 - 1e-6
assert p["insert_hole_depth"] >= p["insert_recess"] + p["insert_length"] + 1.0 - 1e-6
assert p["boss_taper_top_z"] <= P["skirt_bottom_z"] - P["button_travel"] - 0.1
assert 2 * old["disc_pitch_r"] * math.sin(math.pi / 24) - 2 * (pocket_r + p["magnet_entry_chamfer"]) >= 1.0
assert math.isclose(p["phone_floor_thickness"], P["bottom_skin_thickness"])
assert math.isclose(p["magnet_pocket_depth"], old["mag_top"] - skin_top)
assert p["phone_floor_thickness"] >= 0.6

print("Building closed-bottom disc and M2 insert mounts...", flush=True)
# A continuous phone-facing floor is integral with the disc. Magnets load
# from the inner/PCB-facing side before the disc is bonded to the housing.
# No steel backing ring or separate phone-side closing plate is required.
disc = disk(radius, pad_z, p["phone_floor_thickness"])
disc = disc.fuse(annulus(old["Rbody"], old["tray_ro"], skin_top - 0.01,
                         old["mag_top"] - skin_top + 0.01))
entry_start = old["mag_top"] - p["magnet_entry_chamfer"]
for center in old["attachment_centers"]:
    x, y = center["x"], center["y"]
    disc = disc.cut(disk(pocket_r, skin_top, p["magnet_pocket_depth"] + 0.1, x, y))
    disc = disc.cut(cone(pocket_r, pocket_r + p["magnet_entry_chamfer"],
                         entry_start, p["magnet_entry_chamfer"], x, y))
disc = disc.clean()
magnet_bottom = skin_top
magnet_top = magnet_bottom + P["attachment_magnet_thickness"]
magnets = compound([disk(magnet_r, magnet_bottom, P["attachment_magnet_thickness"],
                         c["x"], c["y"]) for c in old["attachment_centers"]])

# The inserts load from the underside while the disc is off. Putting them
# below the PCB allows a full 1.3 mm wall around their knurled envelope without
# enlarging the existing PCB holes or obstructing the rotating cap's skirt.
housing = old["housing"]
insert_bottom = skin_top + p["insert_recess"]
insert_top = insert_bottom + p["insert_length"]
insert_shapes = []
for x, y in mounts:
    housing = housing.fuse(disk(p["boss_diameter"] / 2, skin_top,
                                p["boss_taper_bottom_z"] - skin_top, x, y))
    housing = housing.fuse(cone(p["boss_diameter"] / 2, 2.3,
                                p["boss_taper_bottom_z"],
                                p["boss_taper_top_z"] - p["boss_taper_bottom_z"], x, y))
    housing = housing.cut(disk(p["screw_clearance_diameter"] / 2,
                               skin_top - 0.1, flex_top - skin_top + 0.2, x, y))
    housing = housing.cut(disk(p["insert_hole_diameter"] / 2,
                               skin_top - 0.1, p["insert_hole_depth"] + 0.1, x, y))
    insert_shapes.append(annulus(1.0, p["insert_outer_diameter"] / 2,
                                  insert_bottom, p["insert_length"]).translate((x, y, 0)))
housing = housing.clean()
inserts = compound(insert_shapes)

def m2_flexure(shape):
    for x, y in mounts:
        shape = shape.fuse(disk(p["flexure_mount_pad_diameter"] / 2, flex_z, 1.1, x, y))
        shape = shape.cut(disk(p["screw_clearance_diameter"] / 2, flex_z - 0.1, 1.3, x, y))
        height = (p["flexure_countersink_diameter"] - p["screw_clearance_diameter"]) / 2
        shape = shape.cut(cone(p["screw_clearance_diameter"] / 2,
                                p["flexure_countersink_diameter"] / 2,
                                flex_top - height, height + 0.00001, x, y))
    return shape.clean()

neutral_flex = m2_flexure(old["neutral_flex"])
released_flex = m2_flexure(old["released_flex"])
pressed_flex = m2_flexure(old["pressed_flex"])
screw_head_h = (p["screw_reference_head_diameter"] - 2.0) / 2
screw_head_top = flex_top - (p["flexure_countersink_diameter"] - p["screw_reference_head_diameter"]) / 2
screw_tip = screw_head_top - p["screw_length_including_head"]
screws = compound([
    disk(1.0, screw_tip, p["screw_length_including_head"] - screw_head_h, x, y).fuse(
        cone(1.0, p["screw_reference_head_diameter"] / 2,
             screw_head_top - screw_head_h, screw_head_h, x, y))
    for x, y in mounts
])
thread_engagement = min(insert_top, screw_head_top - screw_head_h) - max(insert_bottom, screw_tip)
assert thread_engagement >= 2.0
assert screw_tip > skin_top

phone_pad = old["phone_pad"]
printed = {
    "Magnetic_Base_Disc_Closed_Bottom": disc,
    "Stationary_Housing_M2_Inserts": housing,
    "Flexure_Retention_System_M2": neutral_flex,
}

# Both coupons have blind pockets opening upward. The magnet coupon reproduces
# the disc's integral phone floor and inner-side lead-in.
def coupon(diameters, thickness, spacing, width, depth, lead_in=0):
    assert 0 < depth < thickness
    length = (len(diameters) - 1) * spacing + width
    shape = cq.Workplane("XY").box(length, width, thickness, centered=(False, True, False)).val()
    for index, diameter in enumerate(diameters):
        x = width / 2 + index * spacing
        shape = shape.cut(disk(diameter / 2, thickness - depth, depth + 0.01, x))
        if lead_in:
            shape = shape.cut(cone(diameter / 2, diameter / 2 + lead_in,
                                    thickness - lead_in, lead_in, x))
    # An index notch marks the first/smallest hole without raised print labels.
    return shape.cut(disk(0.75, -0.01, thickness + 0.02, 0, -width / 2)).clean()

printed["Magnet_Fit_Coupon_4p90_4p95_5p00_5p05"] = coupon(
    p["magnet_coupon_diameters"], old["mag_top"] - pad_z, 8, 8,
    p["magnet_pocket_depth"], p["magnet_entry_chamfer"])
printed["M2_Insert_Fit_Coupon_3p10_3p20_3p30"] = coupon(
    p["insert_coupon_diameters"], 5.0, 8, p["boss_diameter"], p["insert_hole_depth"])

manifest = []
for name, shape in printed.items():
    assert shape.isValid() and len(shape.Solids()) == 1, name
    cq.exporters.export(shape, str(out / "STEP_Parts" / f"{name}.step"))
    bed_shape = shape.translate((0, 0, -shape.BoundingBox().zmin))
    stl = out / "Print_STL" / f"{name}.stl"
    cq.exporters.export(bed_shape, str(stl), tolerance=0.025, angularTolerance=0.06)
    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1, name
    # B-rep bounding boxes can include a small conservative tolerance around
    # curved Boolean faces. Put the actual exported mesh, not that padded box,
    # on the bed and verify the bytes after re-exporting.
    mesh_bed_shift = -float(mesh.bounds[0, 2])
    mesh.apply_translation((0, 0, mesh_bed_shift))
    mesh.export(stl)
    mesh = trimesh.load_mesh(stl)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1, name
    assert abs(mesh.bounds[0, 2]) < 1e-5, name
    manifest.append({"name": name, "valid_solid": True, "solids": 1,
                     "stl_watertight": True, "size_mm": mesh.extents.round(5).tolist(),
                     "mesh_bed_shift_mm": round(mesh_bed_shift, 8),
                     "sha256_stl": hashlib.sha256(stl.read_bytes()).hexdigest()})

states = {}
for state in ("Released", "Pressed"):
    parts = old["states"][state].copy()
    parts.pop("Magnetic_Shield")
    parts.update({"Stationary_Housing": housing, "Bottom_Cover": disc,
                  "MagSafe_Magnet_Array": magnets,
                  "Flexure_Retention_System": released_flex if state == "Released" else pressed_flex,
                  "Phone_Pad": phone_pad,
                  "Encoder_Roof_Shim": old["encoder_shim"].translate((0, 0, -P["button_travel"] if state == "Pressed" else 0)),
                  "M2_Fasteners": screws, "M2_Inserts": inserts,
                  "PCB_Spacer_Bushings": old["pcb_spacers"]})
    states[state] = parts
    assert all(shape.isValid() for shape in parts.values()), state

print("Checking both press states and insertion paths...", flush=True)
collisions = []
intentional_fits = []
for state, parts in states.items():
    for (name_a, a), (name_b, b) in itertools.combinations(parts.items(), 2):
        ba, bb = a.BoundingBox(), b.BoundingBox()
        if any((getattr(ba, axis + "max") <= getattr(bb, axis + "min") or
                getattr(bb, axis + "max") <= getattr(ba, axis + "min")) for axis in "xyz"):
            continue
        overlap = a.intersect(b).Volume()
        if overlap < 0.002:
            continue
        pair = {name_a, name_b}
        row = {"state": state, "parts": [name_a, name_b], "overlap_mm3": round(overlap, 6)}
        if pair == {"Bottom_Cover", "MagSafe_Magnet_Array"}:
            straight_height = max(0, min(magnet_top, entry_start) - magnet_bottom)
            taper_lo = max(magnet_bottom, entry_start)
            taper_hi = min(magnet_top, entry_start + magnet_r - pocket_r)
            taper_overlap = 0
            if taper_hi > taper_lo:
                r_lo = pocket_r + taper_lo - entry_start
                r_hi = pocket_r + taper_hi - entry_start
                taper_overlap = magnet_r**2 * (taper_hi - taper_lo) - (r_hi**3 - r_lo**3) / 3
            expected = 24 * math.pi * ((magnet_r**2 - pocket_r**2) * straight_height + taper_overlap)
            assert abs(overlap - expected) < 0.002
            intentional_fits.append(dict(row, classification=f"{2 * (magnet_r - pocket_r):.3f} mm diametral magnet press fit"))
        elif pair == {"Stationary_Housing", "M2_Inserts"}:
            expected = 4 * math.pi * ((p["insert_outer_diameter"] / 2)**2 - (p["insert_hole_diameter"] / 2)**2) * p["insert_length"]
            assert abs(overlap - expected) < 0.002
            intentional_fits.append(dict(row, classification="nominal knurl envelope displaces heated plastic"))
        elif pair == {"CR2032", "Battery_Holder"}:
            rigid_holder = max(old["holder"].Solids(), key=lambda s: s.Volume())
            assert old["battery"].intersect(rigid_holder).Volume() < 0.002
            intentional_fits.append(dict(row, classification="baseline undeformed battery spring contact"))
        else:
            collisions.append(row)

loading_checks = []
for c in old["attachment_centers"]:
    x, y = c["x"], c["y"]
    # The disc is loaded before bonding it to the housing. An inner-side gauge
    # reaches the seat, while the complete 0.6 mm phone-facing floor stays solid.
    path = disk(pocket_r - 0.001, skin_top + 0.001,
                p["magnet_pocket_depth"] + 0.2, x, y)
    assert path.intersect(disc).Volume() < 0.002
    floor_probe = disk(magnet_r, pad_z, p["phone_floor_thickness"], x, y)
    assert floor_probe.cut(disc).Volume() < 0.002
    loading_checks.append({"magnet": c["index"], "inner_side_path_clear": True, "integral_phone_floor_verified": True})

extraction = []
for lift in (0, 0.5, 1, 2, 4, 6, 10, 16, P["pcb_service_lift"]):
    overlaps = []
    for name in ("PCB_Dummy", "Battery_Holder", "CR2032", "Angle_Sensor_Dummy", "BLE_MCU_Dummy", "Tactile_Switch"):
        moving = old["parts"][name].translate((0, 0, lift))
        for fixed_name in ("Stationary_Housing", "Bottom_Cover", "M2_Inserts"):
            overlap = moving.intersect(states["Released"][fixed_name]).Volume()
            if overlap > 0.002:
                overlaps.append({"moving": name, "fixed": fixed_name, "overlap_mm3": round(overlap, 6)})
    assert not overlaps, (lift, overlaps)
    extraction.append({"lift_mm": lift, "collisions": overlaps})

# Verify each unheated insert/tool can reach its underside mouth. The part is
# heated into the smaller bore, so its nominal outer envelope is intentional.
for x, y in mounts:
    entry = disk(p["insert_outer_diameter"] / 2, skin_top - 3, 3, x, y)
    assert entry.intersect(housing).Volume() < 0.002

report = {
    "status": "CAD checked prototype; physical press fit, heat setting and pull-off strength untested",
    "parameters": p,
    "printed_parts": manifest,
    "unintended_collisions": collisions,
    "intentional_interference": intentional_fits,
    "magnet_loading": "inner / PCB-facing side, -Z; integral printed phone floor is the seating stop",
    "magnet_count": 24,
    "magnet_nominal_diameter_mm": 2 * magnet_r,
    "magnet_diametral_interference_mm": round(2 * (magnet_r - pocket_r), 5),
    "magnet_entry_diameter_mm": round(2 * (pocket_r + p["magnet_entry_chamfer"]), 5),
    "magnet_minimum_web_mm": round(2 * old["disc_pitch_r"] * math.sin(math.pi / 24) - 2 * pocket_r, 5),
    "magnet_minimum_entry_web_mm": round(2 * old["disc_pitch_r"] * math.sin(math.pi / 24) - 2 * (pocket_r + p["magnet_entry_chamfer"]), 5),
    "magnet_seated_z_mm": [magnet_bottom, magnet_top],
    "magnet_pocket_depth_mm": p["magnet_pocket_depth"],
    "magnet_recess_below_inner_face_mm": round(old["mag_top"] - magnet_top, 5),
    "loading_checks": loading_checks,
    "retainer_required": False,
    "metal_backing_ring_required": False,
    "phone_floor_thickness_mm": p["phone_floor_thickness"],
    "nominal_total_height_including_pad_mm": P["overall_height"],
    "insert_installation": "from underside before bonding magnetic disc; recess insert face 0.10 mm",
    "insert_seated_z_mm": [insert_bottom, insert_top],
    "insert_minimum_wall_after_knurl_mm": (p["boss_diameter"] - p["insert_outer_diameter"]) / 2,
    "insert_blind_relief_mm": round(skin_top + p["insert_hole_depth"] - insert_top, 5),
    "screw_thread_engagement_mm": round(thread_engagement, 5),
    "screw_tip_to_center_floor_mm": round(screw_tip - skin_top, 5),
    "screw_head_recess_mm": round(flex_top - screw_head_top, 5),
    "pcb_hole_and_mount_positions_changed": False,
    "boss_taper_to_pressed_skirt_axial_clearance_mm": round(P["skirt_bottom_z"] - P["button_travel"] - p["boss_taper_top_z"], 5),
    "pcb_extraction_checks": extraction,
    "baseline_geometry_unchanged": ["PCB", "Rotating_Cap", "Battery_Holder", "PCB_Spacer_Bushings"],
}
(out / "Validation/geometry-checks.json").write_text(json.dumps(report, indent=2) + "\n")
assert not collisions, collisions

# These outputs belong to the superseded open-hole variant and must not enter
# the new print pack. The original retrofit plate remains in its own folder.
for name in ("Magnetic_Base_Disc_Reverse_Load", "Magnet_Retainer_58mm"):
    for directory, suffix in (("Print_STL", ".stl"), ("STEP_Parts", ".step")):
        (out / directory / (name + suffix)).unlink(missing_ok=True)

colors = old["colors"] | {"M2_Inserts": (0.78, 0.56, 0.20), "M2_Fasteners": (0.45, 0.48, 0.52),
                         "Phone_Pad": (0.14, 0.17, 0.20), "Encoder_Roof_Shim": (0.6, 0.6, 0.6),
                         "PCB_Spacer_Bushings": (0.7, 0.72, 0.74)}
for state, parts in states.items():
    assembly = cq.Assembly(name="Closed_Bottom_Base_M2_" + state)
    for name, shape in parts.items():
        assembly.add(shape, name=name, color=cq.Color(*colors[name]))
    assembly.export(str(out / f"Assembly_{state}.step"))

from render import render
render(out, disc, housing, inserts, old, p)
print(json.dumps({"output": str(out), "watertight_prints": len(manifest),
                  "magnet_loading_paths": len(loading_checks), "unintended_collisions": collisions,
                  "thread_engagement_mm": thread_engagement}, indent=2), flush=True)
