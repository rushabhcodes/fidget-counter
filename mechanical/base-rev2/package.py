"""Package the checked revision and reused prints into one download."""
from pathlib import Path
import hashlib
import json
import zipfile

here = Path(__file__).resolve().parent
out = here / "export"
report = json.loads((out / "Validation/geometry-checks.json").read_text())
assert not report["unintended_collisions"], "Regenerate and resolve collisions before packaging"
assert report["parameters"] == json.loads((here / "parameters.json").read_text())
for part in report["printed_parts"]:
    file = out / "Print_STL" / (part["name"] + ".stl")
    assert hashlib.sha256(file.read_bytes()).hexdigest() == part["sha256_stl"], file

notes = """REVERSE-LOADING BASE, REVISION 2 — FOR THE 1.0.7 ENCLOSURE

Print one each:
  Magnetic_Base_Disc_Reverse_Load
  Stationary_Housing_M2_Inserts
  Flexure_Retention_System_M2
  Magnet_Retainer_58mm
  Rotating_Cap (reused original)
Print four PCB_Spacer_Print_4, two Cap_Release_Key_Print_2, one PCB_Lift_Pick.
Print the two fit coupons first. All STLs are already on the bed.

Magnets: 24 axial 5 x 1.5 mm attachment discs, 1 diametric 5 x 1.5 mm encoder disc.
Default attachment pockets: 4.95 mm, trial 0.05 mm diametral interference.
The 4.90 / 4.95 / 5.00 / 5.05 magnet coupon starts at its notched end.
The 3.10 / 3.20 / 3.30 insert coupon starts at its notched end.
Inserts: 4 CNC Kitchen M2 x 3 references, OD3.6 x length3.0, hole3.2 x depth4.1.
Screws: 4 M2 x 10 countersunk, 3.8 mm head diameter, 90 degrees (DIN 965H).

Install inserts from the housing UNDERSIDE before bonding the magnetic disc.
Fit and bond the steel backing ring, then bond the empty magnetic disc.
Press attachment magnets from the PHONE-FACING SIDE toward the steel stop.
Glue on the solid retainer and fit the protective pad below it.
The retainer is REQUIRED for the new open-hole disc.
Print the retainer flat at 0.20 mm layers, 100% solid, no supports.
The complete assembly is nominally 14.65 mm high including the relocated pad.

Reuse the original PCB, steel backing ring ID44.05 OD54.45 x0.7, battery/holder,
silicone actuator ring, PET actuator and encoder shims, and protective pad.
Adjust actuator gap and check rotation/press return before use.

See DESIGN.md for full hardware details, dimensions and assembly instructions.
Links in DESIGN.md are relative to the repository; all new prints and CAD are
included directly in this ZIP. Original published circuit exports remain the
baseline, not this revised mechanical assembly.

CAD and mesh checks are included under Validation. Physical printed fit,
heat-setting, screw/plate retention and phone pull-off force are untested.
"""

archive = out / "Base_Rev2_Print_Pack.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("PRINTING.txt", notes)
    z.write(here / "README.md", "DESIGN.md")
    for directory in ("Print_STL", "STEP_Parts", "Validation"):
        for file in sorted((out / directory).iterdir()):
            if file.is_file():
                z.write(file, str(file.relative_to(out)))
    for name in ("Rotating_Cap.stl", "PCB_Spacer_Print_4.stl", "Cap_Release_Key_Print_2.stl", "PCB_Lift_Pick.stl"):
        z.write(here.parent / "Print_STL" / name, "Print_STL/" + name)
    for file in (out / "Assembly_Released.step", out / "Assembly_Pressed.step", out / "base-rev2-preview.png"):
        z.write(file, file.name)
print(archive)
