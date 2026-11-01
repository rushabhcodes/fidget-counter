"""Clean CAD tessellations per material, preserving contacting assembly shells."""
import json
from pathlib import Path
import trimesh


def clean_scene_file(path):
 path=Path(path);rows=json.loads(path.read_text())
 for row in rows:
  vertices=[];faces=[];groups=[]
  for group in row.get('groups',[{'first_face':0,'face_count':len(row['faces']),'label':row['name'],'color':row['color'],'finish':'plastic'}]):
   mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'][group['first_face']:group['first_face']+group['face_count']],process=True)
   # OpenCascade emits zero-area pole triangles for spheres. Remove those from
   # the actual exported assets, then require closed, positively oriented shells.
   mesh.update_faces(mesh.nondegenerate_faces(height=1e-8));mesh.remove_unreferenced_vertices()
   if not row.get('nativeElectronic'):
    assert mesh.is_watertight and mesh.is_winding_consistent,(row['name'],group['label'],'Invalid CAD tessellation')
    assert mesh.volume>0,(row['name'],group['label'],'Invalid CAD tessellation volume')
   finish={'Actuator_Ring':'rubber','Encoder_Spacer':'nylon'}.get(row['name'],group.get('finish','plastic'))
   groups.append({**group,'finish':finish,'first_face':len(faces),'face_count':len(mesh.faces)})
   offset=len(vertices);vertices.extend(mesh.vertices.tolist());faces.extend((mesh.faces+offset).tolist())
  row.update(vertices=vertices,faces=faces,groups=groups)
 path.write_text(json.dumps(rows))
 return rows
