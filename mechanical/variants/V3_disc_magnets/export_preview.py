"""Select V3 in the native circuit viewer using the generated exact CAD meshes."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import trimesh

H = Path(__file__).resolve().parent
R = H.parents[2]
MODELS = R / "mechanical/Circuit_Models"
sys.path.insert(0, str(R / "mechanical"))
from glb_models import write_glb

rows = json.loads((H / "generated/scene_meshes.json").read_text())
selected = {r["name"]: [r] for r in rows if r["name"] in ["Base_V3_Discs", "Magnet"]}
selected.update({r["name"]:[r] for r in json.loads((H / "generated/cap_meshes.json").read_text())})
selected["Attachment_Discs_V3"] = [r for r in rows if r["name"].startswith("Attachment_Disc_")]
assert len(selected["Attachment_Discs_V3"]) == 20
manifest = json.loads((MODELS / "manifest.json").read_text())
for obsolete in ["Magnet_Carrier_V3", "Steel_Backing_V3"]:
    manifest["materialGroups"].pop(obsolete, None)
    for extension in [".glb", ".obj", ".mtl"]:
        name = obsolete + extension
        (MODELS / name).unlink(missing_ok=True)
        manifest["modelSha256"].pop(name, None)
        manifest["referenceModelSha256"].pop(name, None)
for name, source in selected.items():
    vertices, normals, faces, groups = [], [], [], []
    for row in source:
        mesh = trimesh.Trimesh(vertices=row["vertices"], faces=row["faces"], process=True)
        mesh = trimesh.graph.smooth_shade(mesh, angle=np.radians(38), facet_minarea=None)
        groups.append({"label": row["name"], "first_face": len(faces), "face_count": len(mesh.faces), "color": row["color"],
                       "finish": "steel" if name in ["Magnet", "Attachment_Discs_V3"] else "plastic"})
        faces.extend(mesh.faces + len(vertices))
        vertices.extend(mesh.vertices)
        normals.extend(mesh.vertex_normals)
    lines = ["mtllib " + name + ".mtl", "o " + name]
    lines += ["v " + " ".join(f"{v:.7f}" for v in point) for point in vertices]
    lines += ["vn " + " ".join(f"{v:.7f}" for v in normal) for normal in normals]
    for i, group in enumerate(groups):
        lines.append("usemtl " + name + "_" + str(i))
        lines += ["f " + " ".join(f"{int(v) + 1}//{int(v) + 1}" for v in f)
                  for f in faces[group["first_face"]:group["first_face"] + group["face_count"]]]
    (MODELS / (name + ".obj")).write_text("\n".join(lines) + "\n")
    (MODELS / (name + ".mtl")).write_text("\n".join("newmtl " + name + "_" + str(i) + "\nKd " + " ".join(map(str, g["color"])) + "\nd 1\n" for i, g in enumerate(groups)))
    write_glb(MODELS / (name + ".glb"), groups)
    manifest["materialGroups"][name] = groups
manifest.update({"activeVariant": "V3_disc_magnets", "activeVariantParameters": json.loads((H / "parameters.json").read_text()),
                 "modelsPerSelectedStyle": 7, "totalAssets": len(manifest["materialGroups"])})
for suffix, field in [(".glb", "modelSha256"), (".obj", "referenceModelSha256"), (".mtl", "referenceModelSha256")]:
    for path in MODELS.glob("*" + suffix):
        manifest[field][path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
(MODELS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("Exported bottom-load base,20 attachment discs, axial encoder on edge and11 updated caps")
