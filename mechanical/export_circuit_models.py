"""Export assembly-coordinate OBJ/MTL assets from the enclosure B-rep meshes.

Run after build_enclosure.py, or pass its Validation/scene_meshes.json and an
output directory. Electronics and the imported BT1 holder are supplied by the
actual tscircuit board, so their mechanical bounding dummies are excluded.
"""
from pathlib import Path
import argparse
import hashlib
import json

EXCLUDED = {"PCB_Dummy", "Angle_Sensor_Dummy", "BLE_MCU_Dummy",
            "Tactile_Switch", "Battery_Holder", "PCB_Board", "Flexure_Neutral"}
SHELLS = {"Rotating_Cap", "Stationary_Housing", "Battery_Hatch", "Bottom_Cover"}


def export_models(meshes, output, pcb_midplane_z, parameters=None):
    if parameters is None:
        parameters = json.loads((Path(__file__).resolve().parent/"enclosure-parameters.json").read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    selected = [m for m in meshes if m["state"] in {"Released", "Detail"}
                and m["name"] not in EXCLUDED]
    assert len(selected) == 14
    manifest = {"units": "mm", "axes": "Z-up", "state": "Released",
                "pcbMidplaneZMm": pcb_midplane_z, "sourceParameters": parameters,
                "circuitPositionOffsetMm": [0, 0, -pcb_midplane_z],
                "excludedDummyModels": sorted(EXCLUDED), "parts": []}
    for mesh in selected:
        name = mesh["name"]
        obj = output / f"{name}.obj"
        mtl = output / f"{name}.mtl"
        vertices = mesh["vertices"]
        faces = mesh["faces"]
        obj.write_text(f"# Assembly coordinates in millimetres, Z-up.\nmtllib {name}.mtl\no {name}\n"
                       # Vertex colours also serve loaders that ignore external MTL.
                       + "".join("v " + " ".join(f"{x:.7f}" for x in v)
                                 + " " + " ".join(str(x) for x in mesh["color"]) + "\n" for v in vertices)
                       + f"usemtl {name}\ns off\n"
                       + "".join("f " + " ".join(str(i + 1) for i in f) + "\n" for f in faces))
        mtl.write_text(f"newmtl {name}\nKa 0.1 0.1 0.1\nKd "
                       + " ".join(str(x) for x in mesh["color"])
                       + "\nKs 0.15 0.15 0.15\nNs 20\nd 1\nillum 2\n")
        manifest["parts"].append({"name": name, "vertices": len(vertices), "triangles": len(faces),
            "boundsMm": [[min(v[i] for v in vertices) for i in range(3)],
                         [max(v[i] for v in vertices) for i in range(3)]],
            "translucent": name in SHELLS,
            "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (obj, mtl)}})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("meshes", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--pcb-midplane-z", type=float, required=True)
    parser.add_argument("--parameters", type=Path, default=Path(__file__).resolve().parent/"enclosure-parameters.json")
    args = parser.parse_args()
    result = export_models(json.loads(args.meshes.read_text()), args.output, args.pcb_midplane_z,
                           json.loads(args.parameters.read_text()))
    print(f"Exported {len(result['parts'])} enclosure models to {args.output}")
