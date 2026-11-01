"""Check reference-hardware construction and generated mesh quality/envelopes."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import trimesh
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'mechanical'))
from hardware_models import bearing_6708,coin_cell,screw
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
bearing,inner,outer,shields,parts=bearing_6708(p['bearing']['bottom_z_mm'])
assert all(shape.isValid() for _,shape,_,_ in parts)
balls=parts[2][1].Solids();assert len(balls)==25
assert all(abs(b.Volume()-4*np.pi*(2.381/2)**3/3)<1e-6 for b in balls)
# Axial symmetry makes one ball sufficient for both raceway checks. Shield
# seats and cage cavities must contain voids, not interpenetrating material.
for label,left,right in [('ball/inner race',balls[0],inner),('ball/outer race',balls[0],outer),('ball/cage',balls[0],parts[3][1]),('shields/outer race',shields,outer),('shields/inner race',shields,inner)]:
 assert left.intersect(right).Volume()<.0001,label
cell,cell_parts=coin_cell(p['pcb_bottom']-4.7)
for i,(_,left,_,_) in enumerate(cell_parts):
 assert left.isValid()
 for _,right,_,_ in cell_parts[i+1:]:assert left.intersect(right).Volume()<.0001,'Cell materials overlap'
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text());checks=[]
for row in rows:
 if row.get('nativeElectronic') or row['name']=='PCB':continue
 mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True)
 assert np.isfinite(mesh.vertices).all(),row['name']
 # An assembly may have contacting material interfaces (e.g. cell gasket/lid).
 # Check each material group as a closed shell rather than merging unlike solids.
 for group in row.get('groups',[{'first_face':0,'face_count':len(row['faces']),'label':row['name']}]):
  part=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'][group['first_face']:group['first_face']+group['face_count']],process=True)
  assert part.is_watertight and part.is_winding_consistent,(row['name'],group['label'],'Mesh is not closed/oriented')
  assert part.volume>0,(row['name'],group['label'],'Negative mesh volume')
 checks.append({'name':row['name'],'triangles':len(mesh.faces),'watertight':True,'bounds_mm':mesh.bounds.tolist(),'material_groups':len(row.get('groups',[]))})
# Detailed geometry must stay inside the existing purchased-part envelopes.
for name,lower,upper in [('Bearing_6708',[-25,-25,6.6],[25,25,12.6]),('Cell',[-10,-10,3.4],[10,10,6.6])]:
 row=next(r for r in checks if r['name']==name);bounds=np.array(row['bounds_mm'])
 assert (bounds[0]>=np.array(lower)-1e-5).all() and (bounds[1]<=np.array(upper)+1e-5).all(),name
report={'passed':True,'physical_tested':False,'bearing_balls':25,'ball_diameter_mm':2.381,'hardware_interpenetrations':0,'meshes':checks,'source_sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'mechanical/hardware_models.py',root/'mechanical/build_enclosure.py',root/'mechanical/spring_mesh.py',root/'mechanical/export_circuit_models.py',root/'mechanical/mesh_export.py']},'limits':['Representative internals, threads and spring turns; confirm purchased SKUs and force curves']}
(root/'validation/model-detail-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Pass: bearing construction, battery material separation and {len(checks)} closed mechanical meshes')
