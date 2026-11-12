"""Package the checked two-print, bottom-loaded v1.0.32 enclosure."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[1]
H = R / "mechanical/variants/V3_disc_magnets"
G = H / "generated"
D = R / "manufacturing"
version = json.loads((R / "package.json").read_text())["version"]
sha = lambda data: hashlib.sha256(data).hexdigest()
geometry = json.loads((G / "geometry-audit.json").read_text())
audit = json.loads((G / "print-audit.json").read_text())
native = json.loads((R / "work/disc-native-preview-audit.json").read_text())
assert geometry["passed"] and audit["passed"] and audit["actual_slicer_executed"] and native["passed"]
assert geometry["parameters_sha256"] == sha((H / "parameters.json").read_bytes())
assert geometry["builder_sha256"] == sha((H / "build.py").read_bytes())
assert audit["geometry_audit_sha256"] == sha((G / "geometry-audit.json").read_bytes())
assert audit["audit_source_sha256"] == sha((H / "audit.py").read_bytes())
assert native["pcb_records_identical"] and native["fitted_components_identical"] == 27
assert native["circuit_sha256"] == sha((R / "dist/index/circuit.json").read_bytes())
(G / "native-preview-audit.json").write_text(json.dumps(native, indent=2) + "\n")
manifest = json.loads((G / "print-ready-manifest.json").read_text())
default = [R / p for p in manifest["default_files"]]
assert len(default) == 2
assert {p.name for p in default} == {"Base_V3_Discs.stl", "Cap_circular.stl"}
for part in manifest["parts"]:
    assert sha((R / part["file"]).read_bytes()) == part["sha256"]
    assert sha((R / part["STEP_file"]).read_bytes()) == part["STEP_sha256"]


def archive(label, files, instructions):
    entries = {str(p.relative_to(R)): p.read_bytes() for p in files}
    entries["START_HERE.txt"] = instructions.encode()
    path = D / f"fidget-counter-{label}-{version}.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for name, data in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 12, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            output.writestr(info, data)
    with zipfile.ZipFile(path) as verify:
        assert verify.testzip() is None
        for name, data in entries.items():
            assert sha(verify.read(name)) == sha(data)
    return {"file": str(path.relative_to(R)), "bytes": path.stat().st_size, "sha256": sha(path.read_bytes()),
            "members": {name: sha(data) for name, data in sorted(entries.items())}}


docs = [H / name for name in ["README.md", "ORDER_LIST.csv", "parameters.json", "polarity-map.csv", "review.png", "exploded-v1.0.32.png", "review.html"]]
docs += [G / name for name in ["geometry-audit.json", "print-audit.json", "print-ready-manifest.json", "assembly-step-audit.json", "native-preview-audit.json"]]
docs += [R / "ASSEMBLY.md", R / "PROGRAMMING.md", R / "mechanical/MECHANICAL_BOM.csv"]
profiles = list((R / "mechanical/printing").glob("*.ini"))
coupons = list((G / "Fit_Coupons").glob("*.stl")) + list((R / "mechanical/Print_STL/Coupons").glob("*.stl"))
prints = archive("V3-discs-print-test", [*docs, *default, *coupons, *profiles],
    "V1.0.32 V3: BOTTOM-INSERT ROUND DISCS. Print exactly Base_V3_Discs.stl and Cap_circular.stl for one device (2 product parts). "
    "Fit coupons are tests, not device parts. Source20 diameter6 x thickness3 mm AXIAL N52 magnets. Insert from underside into blind pockets and retain with qualified sidewall adhesive. "
    "NO steel backing, premade ring or separate magnet carrier. Read V3 README first. Clear base supports from all blind stops; faces must remain recessed. "
    "Use the provisional PETG profiles and re-slice for your actual printer; no machine G-code is supplied. "
    "Holding force, phone pole arrangement, adhesive retention and physical fit require prototype measurements.\n")

# Include every frozen input the V3 builder verifies, plus all unchanged cap
# alternatives, so the CAD archive is independently editable/rebuildable.
v1 = R / "mechanical/variants/V1_premade_ring"
frozen = json.loads((v1 / "manifest.json").read_text())
inputs = [v1 / "manifest.json", *[v1 / name for name in frozen["files"]], *[R / name for name in frozen["supplier_STEP_sha256"]]]
inputs += [R / "mechanical/variants/V2_discrete_magnets/parameters.json", R / "mechanical/requirements.txt", R / "mechanical/glb_models.py"]
sources = [p for p in H.glob("*.py")] + [Path(__file__).resolve()]
caps = [R / part[key] for part in manifest["parts"] if part["name"].startswith("Cap_") for key in ["file", "STEP_file"]]
cad = archive("V3-discs-CAD", [*docs, *profiles, *coupons, *inputs, *sources, *caps,
    *list((G / "STEP").glob("*.step")), *list((G / "Reference_STEP").glob("*.step")),
    *list((G / "Assemblies").glob("*.step")), G / "V3_assembled.glb", G / "V3_exploded.glb", R / "BOM.csv"],
    "V1.0.32 V3 EXACT CAD AND SOURCE. Current assemblies contain20 bottom-loaded round magnets, one base and one cap; NO steel backing or carrier. "
    "Use only the V3 print manifest for printing. Assembled/exploded STEP, purchased-part references and frozen V1/V2 source inputs are for review/rebuilding, NOT product printing. "
    "V1/V2 files under their named folders are immutable historic build inputs, not alternate parts to mix into V3. "
    "All11 current cap STEP/STL alternatives are included. Rebuild from archive root with the documented CAD Python requirements. "
    "Holding force and physical qualification remain unverified. No order has been placed.\n")

old_fab = D / "fidget-counter-fabrication-1.0.31.zip"
new_fab = D / f"fidget-counter-fabrication-{version}.zip"
with zipfile.ZipFile(old_fab) as original, zipfile.ZipFile(new_fab, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
    for item in original.infolist():
        output.writestr(item, original.read(item.filename))
    output.writestr("V3_VERSION.txt", f"Enclosure release{version}; corrected RevC electrical Gerber/BOM/CPL payload is byte-identical to1.0.31. V3 uses bottom-loaded discs. Holder/header are included among27 FIT parts.\n")
with zipfile.ZipFile(old_fab) as original, zipfile.ZipFile(new_fab) as revised:
    assert revised.testzip() is None
    for name in original.namelist():
        assert original.read(name) == revised.read(name)
fabrication = {"file": str(new_fab.relative_to(R)), "bytes": new_fab.stat().st_size, "sha256": sha(new_fab.read_bytes()), "payload_identical_to": old_fab.name}
result = {"version": version, "variant": "V3 bottom-loaded discs", "physical_qualified": False, "holding_force_verified": False,
          "printed_product_parts": 2, "attachment_discs": 20, "steel_backing_count": 0, "separate_carrier_count": 0,
          "print": prints, "CAD": cad, "fabrication": fabrication}
(D / "disc-variant-manifest.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: {n: v[n] for n in ["file", "bytes", "sha256"]} for k, v in result.items() if k in ["print", "CAD", "fabrication"]}, indent=2))
