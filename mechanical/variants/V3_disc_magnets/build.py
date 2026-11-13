"""Build the 1.0.32 disc base from frozen 1.0.31 hardware and supplier STEP.

No V1/V2 part, circuit, bearing seat or electrical placement is rewritten.
Updated caps use the same axial attachment disc held on edge.
Bottom-entry blind pockets are confined below Z4.4 mm; no steel or carrier.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import cadquery as cq
import numpy as np
import trimesh

H = Path(__file__).resolve().parent
ROOT = H.parents[2]
G = H / "generated"
V1 = H.parent / "V1_premade_ring"
P = json.loads((H / "parameters.json").read_text())
OLD = json.loads((V1 / "enclosure-parameters.json").read_text())
M, B, E = P["magnet"], P["pockets"], P["encoder"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for folder in ["STEP", "Print_STL", "Reference_STEP", "Assemblies", "Fit_Coupons", "Circuit_Models"]:
    (G / folder).mkdir(parents=True, exist_ok=True)


def ring(ri, ro, z, h):
    return cq.Workplane("XY").workplane(offset=z).circle(ro).circle(ri).extrude(h).val()


def disc(r, z, h, x=0, y=0):
    return cq.Workplane("XY").workplane(offset=z).center(x, y).circle(r).extrude(h).val()


def overlap(a, b):
    aa, bb = a.BoundingBox(), b.BoundingBox()
    if any(getattr(aa, k + "max") <= getattr(bb, k + "min") + 1e-7 or
           getattr(bb, k + "max") <= getattr(aa, k + "min") + 1e-7 for k in "xyz"):
        return 0.0
    return a.intersect(b).Volume()


def clear(a, b, label):
    volume = overlap(a, b)
    assert volume < 0.002, (label, volume)
    return volume


frozen = json.loads((V1 / "manifest.json").read_text())
for name, entry in frozen["files"].items():
    assert sha(V1 / name) == entry["sha256"], ("Changed frozen V1 input", name)
for name, digest in frozen["supplier_STEP_sha256"].items():
    assert sha(ROOT / name) == digest, ("Changed supplier model", name)
v2 = json.loads((H.parent / "V2_discrete_magnets/parameters.json").read_text())
for name, digest in v2["unchanged_cap_STEP_sha256"].items():
    assert sha(ROOT / name) == digest, ("Changed existing cap", name)

print("Building one-piece base with 20 bottom-entry blind magnet pockets...", flush=True)
original = cq.importers.importStep(str(V1 / "Base_V1_Premade_Ring.step")).val()
# Fill the inherited premade-ring seat, then machine/print individual blind
# pockets directly in the base. The upper shaft, posts and cap seats stay put.
fill = ring(B["annulus_inner_radius_mm"], 29, B["phone_contact_z_mm"], B["base_roof_top_z_mm"] - B["phone_contact_z_mm"])
base = original.fuse(fill).clean()
magnets, centers = {}, []
for i in range(M["quantity"]):
    angle = M["first_angle_deg"] + i * 360 / M["quantity"]
    t = math.radians(angle)
    x, y = M["pitch_radius_mm"] * math.cos(t), M["pitch_radius_mm"] * math.sin(t)
    centers.append((x, y, angle))
    pocket = disc(M["pocket_diameter_mm"] / 2, 0.1, B["blind_stop_z_mm"] - 0.1, x, y)
    entry = cq.Solid.makeCone(B["entry_diameter_mm"] / 2, M["pocket_diameter_mm"] / 2,
                             B["entry_chamfer_height_mm"], cq.Vector(x, y, B["phone_contact_z_mm"]))
    base = base.cut(pocket.fuse(entry))
    magnets[f"Attachment_Disc_{i + 1:02}"] = disc(M["diameter_mm"] / 2, M["phone_face_z_mm"], M["thickness_mm"], x, y)
base = base.clean()
allowed = ring(B["annulus_inner_radius_mm"], 29.1, 0.1, B["base_roof_top_z_mm"] - 0.1)
assert base.cut(original).cut(allowed).Volume() < 0.002
assert original.cut(base).cut(allowed).Volume() < 0.002
upper = cq.Workplane("XY").box(100, 100, 40).val().translate((0, 0, B["base_roof_top_z_mm"] + 20.00001))
assert base.intersect(upper).cut(original).Volume() + original.intersect(upper).cut(base).Volume() < 0.002
min_web = 2 * M["pitch_radius_mm"] * math.sin(math.pi / M["quantity"]) - M["pocket_diameter_mm"]
inner_wall = M["pitch_radius_mm"] - M["pocket_diameter_mm"] / 2 - B["annulus_inner_radius_mm"]
outer_wall = 29 - M["pitch_radius_mm"] - M["pocket_diameter_mm"] / 2
mouth_wall = min(M["pitch_radius_mm"] - B["entry_diameter_mm"] / 2 - B["annulus_inner_radius_mm"],
                 29 - M["pitch_radius_mm"] - B["entry_diameter_mm"] / 2)
assert min(min_web, inner_wall, outer_wall, mouth_wall) >= 0.8 - 1e-7
assert abs(B["blind_stop_z_mm"] - M["phone_face_z_mm"] - M["thickness_mm"]) < 1e-7
maximum_magnet_bottom = B["blind_stop_z_mm"] - M["thickness_mm"] - M["thickness_tolerance_allowance_mm"]
assert maximum_magnet_bottom - B["phone_contact_z_mm"] >= 0.1 - 1e-7
assert M["pocket_diameter_mm"] - M["diameter_mm"] - M["diameter_tolerance_allowance_mm"] >= 0.3 - 1e-7
new = {"Base_V3_Discs": base, **magnets}
for i, (name, shape) in enumerate(new.items()):
    assert shape.isValid() and len(shape.Solids()) == 1, name
    for other, right in list(new.items())[i + 1:]:
        clear(shape, right, name + "/" + other)
# Continuous insertion path, starting below the phone-side face. A disc must
# clear the actual base at every pose until it touches its blind roof.
insertion_poses = [-4, -3, -2, -1, -0.5, -0.1, 0]
for name, magnet in magnets.items():
    for dz in insertion_poses:
        clear(base, magnet.translate((0, 0, dz)), name + "/bottom insertion")

# Always use frozen, already corrected 1.0.31 PCB component poses. Main preview
# choices must not silently move the actual supplier bodies used for fit checks.
circuit = json.loads((V1 / "source/published.circuit.json").read_text())
electronics = {}
for cad in (e for e in circuit if e["type"] == "cad_component" and e.get("model_step_url")):
    source = next(e for e in circuit if e["type"] == "source_component" and e["source_component_id"] == cad["source_component_id"])
    org, rot, pos = cad.get("model_origin_position", {}), cad.get("rotation", {}), cad["position"]
    shape = cq.importers.importStep(str(ROOT / cad["model_step_url"])).val().translate(tuple(-org.get(k, 0) for k in "xyz"))
    for axis, vector in [("x", (1, 0, 0)), ("y", (0, 1, 0)), ("z", (0, 0, 1))]:
        if rot.get(axis, 0):
            shape = shape.rotate((0, 0, 0), vector, rot[axis])
    shape = shape.translate((pos["x"], pos["y"], pos["z"] + OLD["pcb_bottom"] + 0.5))
    electronics["Electronic_" + source["name"]] = shape
    for name, fixed in new.items():
        clear(fixed, shape, name + "/" + source["name"])
assert len(electronics) == 27
sys.path.insert(0, str(V1 / "source"))
from hardware_models import coin_cell, bearing_6808, screw, magnet as encoder_magnet
cell, _ = coin_cell(OLD["battery"]["cell_bottom_z_mm"], OLD["battery"]["standard"])
cx, cy = OLD["battery"]["cell_center_mm"]
cell = cell.translate((cx, cy, 0))
bearing = bearing_6808(OLD["bearing"]["bottom_z_mm"])[0]
pcb = disc(OLD["pcb_diameter"] / 2, OLD["pcb_bottom"], OLD["pcb_thickness"])
fasteners, mount = [], OLD["pcb_mount"]
for i, angle in enumerate(mount["angles_deg"]):
    t = math.radians(angle)
    x, y = mount["radius_mm"] * math.cos(t), mount["radius_mm"] * math.sin(t)
    pcb = pcb.cut(disc(mount["hole_diameter_mm"] / 2, OLD["pcb_bottom"] - 0.1, OLD["pcb_thickness"] + 0.2, x, y))
    if i in mount["screw_indices"]:
        fasteners.append(screw(0.98, 4, 1.9, 1.3, nylon=True).translate((x, y, OLD["pcb_bottom"] + OLD["pcb_thickness"])))
for name, fixed in new.items():
    clear(fixed, cell, name + "/cell")
    clear(fixed, pcb, name + "/PCB")
    if name == "Base_V3_Discs":
        # The inherited shaft has intentional 0.05 mm diametral interference.
        assert abs(overlap(fixed, bearing) - overlap(original, bearing)) < 0.002
    else:
        clear(fixed, bearing, name + "/bearing")
    for fastener in fasteners:
        # PCB screws thread into the inherited base; those intended intersections
        # are unchanged. Other purchased parts must remain collision-free.
        if name != "Base_V3_Discs":
            clear(fixed, fastener, name + "/screw")

print("Building the keyed holder for the same axial disc, mounted on edge...", flush=True)
from grip_profiles import make_grip
cap_parameters={**OLD,"overall_height":E["cap_top_z_mm"],"cap_deck_bottom":E["cap_deck_bottom_z_mm"],
                "grip_height":E["cap_top_z_mm"]-OLD["cap_edge_bottom"]}
# Keep the calibrated bearing bore and lower shoulder. Only the roof/grip grow
# upwards to accommodate the6mm vertical diameter and the1.2mm pocket roof.
hub=ring(OLD["bearing"]["housing_diameter_mm"]/2,28.8,OLD["bearing"]["bottom_z_mm"],E["cap_deck_bottom_z_mm"]-OLD["bearing"]["bottom_z_mm"])
hub=hub.fuse(ring(OLD["bearing"]["outer_shoulder_inner_radius_mm"],28.8,OLD["bearing"]["bottom_z_mm"]+7,E["cap_deck_bottom_z_mm"]-OLD["bearing"]["bottom_z_mm"]-7))
hub=hub.fuse(disc(26.8,E["cap_deck_bottom_z_mm"],E["cap_top_z_mm"]-E["cap_deck_bottom_z_mm"]))
outer_x=E["slot_width_x_mm"]+2*E["holder_wall_mm"]
outer_y=E["slot_length_y_mm"]+2*E["holder_wall_mm"]
holder=cq.Workplane("XY").box(outer_x,outer_y,E["cap_deck_bottom_z_mm"]+.15-E["slot_mouth_z_mm"],centered=(True,True,False)).edges("|Z").fillet(.4).val().translate((0,0,E["slot_mouth_z_mm"]))
slot=cq.Workplane("XY").box(E["slot_width_x_mm"],E["slot_length_y_mm"],E["slot_stop_z_mm"]-E["slot_mouth_z_mm"]+.1,centered=(True,True,False)).val().translate((0,0,E["slot_mouth_z_mm"]-.1))
hub=hub.fuse(holder).clean()
# Model the very same axial disc as the base. Rotating90deg aboutY makes the
# magnetization axisX (parallel to PCB), rather than the spin axisZ.
encoder=encoder_magnet(E["diameter_mm"]/2,-E["thickness_mm"]/2,E["thickness_mm"]).rotate((0,0,0),(0,1,0),90).translate((0,0,E["center_z_mm"]))
assert abs(encoder.BoundingBox().zmin-E["bottom_z_mm"])<1e-7
assert abs(encoder.BoundingBox().zmax-E["top_z_mm"])<1e-7
assert abs(encoder.BoundingBox().xlen-E["thickness_mm"])<1e-7
assert E["cap_top_z_mm"]-E["slot_stop_z_mm"]>=E["minimum_roof_mm"]-1e-7
# A continuous360deg holder envelope proves clearance against the actual PCB,
# supplier bodies, base and fasteners without resampling thousands of solids.
encoder_sweep=disc(math.hypot(outer_x/2,outer_y/2),E["slot_mouth_z_mm"],E["slot_stop_z_mm"]-E["slot_mouth_z_mm"])
for name,shape in {"Base":base,"PCB":pcb,"Cell":cell,"Screws":cq.Compound.makeCompound(fasteners),**electronics}.items():
    clear(encoder_sweep,shape,"complete encoder sweep/"+name)
    bb=shape.BoundingBox()
    if name.startswith("Electronic_"):
        assert bb.zmax<E["cap_deck_bottom_z_mm"]
        assert max(math.hypot(x,y)for x in[bb.xmin,bb.xmax]for y in[bb.ymin,bb.ymax])<25
caps={};encoder_insertion=[-8,-6,-4,-2,-1,-.1,0]
for style in OLD["cap_styles"]:
    cap=hub.fuse(make_grip(style,cap_parameters)).cut(slot).clean()
    assert cap.isValid()and len(cap.Solids())==1,style
    caps["Cap_"+style]=cap
    for dz in encoder_insertion:clear(cap,encoder.translate((0,0,dz)),style+" edge-disc insertion")
    wrong_flat=encoder_magnet(E["diameter_mm"]/2,E["bottom_z_mm"],E["thickness_mm"])
    assert overlap(cap,wrong_flat)>.1,style+" does not enforce edge orientation"
    # The complete old bearing-contact zone must remain byte-for-byte geometry.
    oldcap=cq.importers.importStep(str(ROOT/"mechanical/STEP_Parts"/("Cap_"+style+".step"))).val()
    fit_zone=disc(31,OLD["bearing"]["bottom_z_mm"]-.01,7.01)
    assert cap.intersect(fit_zone).cut(oldcap).Volume()+oldcap.intersect(fit_zone).cut(cap).Volume()<.002,style+" bearing interface changed"
    for angle in range(0,360,15):
        rotated=cap.rotate((0,0,0),(0,0,1),angle)
        for name,fixed in new.items():clear(rotated,fixed,style+"/"+name)
    print("  cleared",style,flush=True)

printed=[]
old_prints={r['name']:r for r in json.loads((ROOT/'mechanical/print-ready-manifest.json').read_text())['parts']}
for name,shape in [("Base_V3_Discs",base),*caps.items()]:
    step,stl=G/'STEP'/(name+'.step'),G/'Print_STL'/(name+'.stl')
    cq.exporters.export(shape,str(step))
    invert=name.startswith('Cap_')and name!='Cap_thumb_scoop'
    oriented=shape.rotate((0,0,0),(1,0,0),180)if invert else shape
    translate_z=-oriented.BoundingBox().zmin
    oriented=oriented.translate((0,0,translate_z))
    cq.exporters.export(oriented,str(stl),tolerance=.025,angularTolerance=.09)
    mesh=trimesh.load_mesh(stl,process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume and len(mesh.split())==1,name
    info=old_prints.get(name,{})
    printed.append({'name':name,'STEP':str(step.relative_to(H)),'STEP_sha256':sha(step),'STL':str(stl.relative_to(H)),'STL_sha256':sha(stl),'volume_mm3':shape.Volume(),
                    'print_rotation_x_deg':180 if invert else 0,'print_translation_z_mm':translate_z,
                    'orientation':'deck down'if invert else('upright, cup supported'if name.startswith('Cap_')else'phone face down'),
                    'supports':info.get('supports','fixed-base'),'quantity_per_default_unit':int(name in['Base_V3_Discs','Cap_circular'])})
for diameter in [6.3, 6.4, 6.5]:
    coupon = cq.Workplane("XY").box(10, 10, B["base_roof_top_z_mm"] - B["phone_contact_z_mm"], centered=(True, True, False)).val()
    coupon = coupon.cut(disc(diameter / 2, -0.1, B["blind_stop_z_mm"] - B["phone_contact_z_mm"] + 0.1))
    coupon = coupon.cut(cq.Solid.makeCone(diameter / 2 + 0.1, diameter / 2, B["entry_chamfer_height_mm"], cq.Vector(0, 0, 0)))
    cq.exporters.export(coupon, str(G / "Fit_Coupons" / f"Disc_pocket_D{diameter:.1f}.stl"), tolerance=0.025, angularTolerance=0.09)
cq.exporters.export(cq.Compound.makeCompound(list(magnets.values())), str(G / "Reference_STEP/Attachment_Discs_V3.step"))

common = {"PCB": pcb, "Cell": cell, "PCB_Fasteners": cq.Compound.makeCompound(fasteners), **electronics,
          "Bearing_6808": bearing, "Magnet": encoder}
values = {**common, "Cap_circular": caps["Cap_circular"], **new}
colors = {"Base_V3_Discs": (0.55, 0.63, 0.69),
          "Cap_circular": (0.18, 0.48, 0.60), "PCB": (0.15, 0.43, 0.29), "Bearing_6808": (0.70, 0.73, 0.77),
          "Cell": (0.73, 0.75, 0.78), "Magnet": (0.72, 0.74, 0.75), "PCB_Fasteners": (0.85, 0.85, 0.80)}
offsets = {"Base_V3_Discs": 32,
           "Cell": 58, "PCB": 75, "PCB_Fasteners": 91, "Bearing_6808": 107, "Magnet": 130, "Cap_circular": 148}
rows = []
for name, shape in values.items():
    vertices, faces = shape.tessellate(0.035, 0.09)
    default = (0.72, 0.74, 0.75) if name.startswith("Attachment_Disc_") or name == "Electronic_BT1" else ((0.9, 0.86, 0.74) if name == "Electronic_J_DEBUG" else ((0.66, 0.49, 0.3) if name.startswith("Electronic_C") else (0.16, 0.17, 0.18)))
    rows.append({"name": name, "vertices": [list(v.toTuple()) for v in vertices], "faces": faces, "color": colors.get(name, default),
                 "exploded_dz_mm": 14 if name.startswith("Attachment_Disc_") else (75 if name.startswith("Electronic_") else offsets[name])})
(G / "scene_meshes.json").write_text(json.dumps(rows, separators=(",", ":")) + "\n")
cap_rows=[]
for name,shape in caps.items():
    vv,ff=shape.tessellate(.035,.09)
    cap_rows.append({'name':name,'vertices':[list(v.toTuple())for v in vv],'faces':ff,'color':colors.get(name,(.18,.48,.60))})
(G/'cap_meshes.json').write_text(json.dumps(cap_rows,separators=(',',':'))+'\n')

for state in ["Assembled", "Exploded"]:
    scene = trimesh.Scene()
    assembly = cq.Assembly(name="V3_" + state)
    for row in rows:
        name = row["name"]
        dz = row["exploded_dz_mm"] if state == "Exploded" else 0
        mesh = trimesh.Trimesh(vertices=row["vertices"], faces=row["faces"], process=False)
        mesh.visual.face_colors = np.array([int(255 * x) for x in row["color"]] + [255], dtype=np.uint8)
        scene.add_geometry(mesh, node_name=name, geom_name=name, transform=trimesh.transformations.translation_matrix([0, 0, dz]))
        assembly.add(values[name], name=name, color=cq.Color(*row["color"]), loc=cq.Location(cq.Vector(0, 0, dz)))
    (G / ("V3_" + state.lower() + ".glb")).write_bytes(scene.export(file_type="glb"))
    assembly.save(str(G / "Assemblies" / ("V3_" + state + ".step")))

report = {"passed": True, "physical_tested": False, "holding_force_verified": False, "release": P["release"], "variant": P["variant"],
          "source_commit": P["baseline_commit"], "builder_sha256": sha(Path(__file__)), "parameters_sha256": sha(H / "parameters.json"),
          "frozen_circuit_sha256": sha(V1 / "source/published.circuit.json"), "supplier_bodies_checked": len(electronics),
          "magnet_count": len(magnets), "pitch_circle_diameter_mm": 2 * M["pitch_radius_mm"], "angular_pitch_deg": 360 / M["quantity"],
          "minimum_pocket_web_mm": min_web, "pocket_inner_wall_mm": inner_wall, "pocket_outer_wall_mm": outer_wall,
          "minimum_entry_wall_mm": mouth_wall, "blind_roof_thickness_mm": B["base_roof_top_z_mm"] - B["blind_stop_z_mm"],
          "minimum_bearing_bottom_to_roof_mm": OLD["bearing"]["bottom_z_mm"] - B["base_roof_top_z_mm"],
          "holder_to_base_mm": base.distance(electronics["Electronic_BT1"]),
          "nominal_phone_face_recess_mm": M["phone_face_z_mm"] - B["phone_contact_z_mm"],
          "minimum_face_recess_at_maximum_magnet_thickness_mm": maximum_magnet_bottom - B["phone_contact_z_mm"],
          "bottom_insertion_poses_per_disc": len(insertion_poses), "bottom_insertion_collision_mm3": 0,
          "all_upper_interfaces_unchanged_above_z_mm": B["base_roof_top_z_mm"], "cap_styles_checked": OLD["cap_styles"], "rotation_samples_per_cap": 24,
          "physical_height_mm": P["physical_height_mm"], "encoder_gap_mm": P["nominal_encoder_gap_mm"], "printed_product_parts": 2, "handled_parts": 28,
          "steel_backing_count": 0, "separate_carrier_count": 0,
          "encoder": E, "encoder_insertion_poses_per_cap":len(encoder_insertion),"flat_wrong_orientation_rejected":True,"all_bearing_interfaces_unchanged":True,
          "new_printed_parts": printed, "scene_objects": len(rows), "polarity": M["phone_facing_polarity"]}
(G / "geometry-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2), flush=True)
