"""Regenerate the GLB assets imported by enclosure.tsx from current CAD meshes."""
from pathlib import Path
import json
import argparse
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / 'dist/mechanical'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, default=ROOT / 'mechanical/models')
OUT = parser.parse_args().output
OUT.mkdir(parents=True, exist_ok=True)
rows = json.loads((GENERATED / 'scene_meshes.json').read_text())
caps = json.loads((GENERATED / 'cap_meshes.json').read_text())
by_name = {row['name']: row for row in rows}

def export(name, selected):
    scene = trimesh.Scene()
    for row in selected:
        mesh = trimesh.Trimesh(vertices=row['vertices'], faces=row['faces'], process=True)
        if name == 'Bearing_6808':
            # Viewer detail only; exact purchased-part geometry stays in STEP.
            bounds = mesh.bounds.copy()
            mesh = mesh.simplify_quadric_decimation(face_count=max(4000, int(len(mesh.faces)*.16)), aggression=3)
            assert np.max(np.abs(mesh.bounds-bounds)) < .06
        mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
            name=row['name'], baseColorFactor=np.array([*row['color'], 1.]),
            metallicFactor=.65 if row['name'] in ['Bearing_6808', 'Cell', 'Magnet'] or row['name'].startswith('Attachment_Disc_') else 0.,
            roughnessFactor=.38))
        scene.add_geometry(mesh, geom_name=row['name'], node_name=row['name'])
    def metadata(tree):
        tree['asset']['extras'] = {'cadUnits': 'mm', 'cadUpAxis': 'Z'}
    (OUT / (name + '.glb')).write_bytes(trimesh.exchange.gltf.export_glb(scene, tree_postprocessor=metadata))

for name in ['Base_V3_Discs', 'Cell', 'PCB_Fasteners', 'Bearing_6808', 'Magnet']:
    export(name, [by_name[name]])
export('Attachment_Discs_V3', [row for row in rows if row['name'].startswith('Attachment_Disc_')])
for row in caps:
    export(row['name'], [row])
# The default output is the source runtime asset directory. STEP/STL,
# reports and intermediate tessellations stay in ignored dist/.
print(f'Wrote 17 imported GLB assets to {OUT}')
