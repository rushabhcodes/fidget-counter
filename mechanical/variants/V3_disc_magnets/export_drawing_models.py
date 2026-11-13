"""Export exact audited PCBA/disc meshes for native tsCircuit drawing views."""
from pathlib import Path
import hashlib,json,sys,subprocess
import numpy as np
import trimesh
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(R/'mechanical'))
from glb_models import write_glb
rows=json.loads((H/'generated/scene_meshes.json').read_text())
P=json.loads((H/'parameters.json').read_text())
D=R/'mechanical/Circuit_Models/Drawings';D.mkdir(exist_ok=True)
body=[r for r in rows if r['name']=='PCB' or(r['name'].startswith('Electronic_')and r['name']!='Electronic_U2')]
hall=[r for r in rows if r['name']=='Electronic_U2']
assert len(body)==27 and len(hall)==1
flat=json.loads(json.dumps(next(r for r in rows if r['name']=='Attachment_Disc_01')))
flat['vertices']=(np.array(flat['vertices'])-[P['magnet']['pitch_radius_mm'],0,P['magnet']['phone_face_z_mm']]).tolist()
result=[]
for name,source in [('PCBA_Body',body),('Hall_Sensor',hall),('Flat_Disc_6x3',[flat])]:
    vertices=[];normals=[];faces=[];groups=[]
    for row in source:
        m=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True)
        m=trimesh.graph.smooth_shade(m,angle=np.radians(38),facet_minarea=None)
        color=row['color'];finish='steel'if name=='Flat_Disc_6x3'else'plastic'
        groups.append({'label':row['name'],'first_face':len(faces),'face_count':len(m.faces),'color':color,'finish':finish})
        faces.extend(m.faces+len(vertices));vertices.extend(m.vertices);normals.extend(m.vertex_normals)
    path=D/(name+'.glb')
    lines=['o '+name]+['v '+' '.join(f'{v:.7f}'for v in point)for point in vertices]+['vn '+' '.join(f'{v:.7f}'for v in normal)for normal in normals]
    lines+=['f '+' '.join(f'{int(v)+1}//{int(v)+1}'for v in f)for f in faces]
    path.with_suffix('.obj').write_text('\n'.join(lines)+'\n')
    write_glb(path,groups)
    subprocess.run(['bun',str(R/'validation/compact-glb.mjs'),str(path)],check=True)
    path.with_suffix('.obj').unlink()
    result.append({'name':name,'file':str(path.relative_to(R)),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'CAD_bodies':[r['name']for r in source]})
(D/'manifest.json').write_text(json.dumps({'passed':True,'geometry_release':P['release'],'models':result},indent=2)+'\n')
print(json.dumps(result,indent=2))
