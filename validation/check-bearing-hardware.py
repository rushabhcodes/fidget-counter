"""Conservatively check new mechanical hardware against every fitted native CAD mesh."""
from pathlib import Path
import hashlib,json
import cadquery as cq
import numpy as np
import trimesh
root=Path(__file__).resolve().parents[1]
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
mid=p['pcb_bottom']+p['pcb_thickness']/2
c=json.loads((root/'dist/index/circuit.json').read_text())
sources={e['source_component_id']:e for e in c if e['type']=='source_component'}
names=[sources[e['source_component_id']]['name'] for e in c if e['type']=='pcb_component' and not e.get('do_not_place') and e.get('source_component_id') in sources]
assert len(names)==31
scene=trimesh.load(root/'dist/index/3d.glb',force='scene')
parts={name:cq.importers.importStep(str(root/'mechanical/STEP_Parts'/f'{name}.step')).val() for name in ['Stationary_Base','Bearing_Carrier','Inner_Race_Nut','Outer_Race_Retainer',*['Cap_'+s for s in p['cap_styles']]]}
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
# Retaining screws and washers are real volumes, including their under-PCB heads.
for name in ['Guide_Fasteners','PCB_Fasteners']:
 row=next(r for r in rows if r['name']==name)
 # Individual disconnected hardware pieces must not be replaced by one huge box.
 mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True)
 for i,piece in enumerate(mesh.split(only_watertight=False)):
  low,high=piece.bounds
  parts[f'{name}_{i}']=cq.Workplane('XY').box(*(high-low)).val().translate(tuple((low+high)/2))
checks=[]
for name in names:
 nodes=[n for n in scene.graph.nodes_geometry if n==name or n.startswith(name+'_')]
 assert nodes,('Missing actual fitted model',name)
 vertices=[]
 for node in nodes:
  transform,geometry=scene.graph[node];mesh=scene.geometry[geometry].copy();mesh.apply_transform(transform);vertices.append(mesh.vertices)
 v=np.concatenate(vertices);world=np.column_stack((-v[:,0],v[:,2],v[:,1]+mid))
 low=world.min(axis=0);high=world.max(axis=0)
 envelope=cq.Workplane('XY').box(*np.maximum(high-low,.001)).val().translate(tuple((low+high)/2))
 for part,shape in parts.items():
  poses=[0] if part.startswith(('Stationary','Guide_','PCB_')) else [0,p['button_travel']]
  for press in poses:
   volume=shape.translate((0,0,-press)).intersect(envelope).Volume()
   assert volume<.003,(part,name,press,volume)
 checks.append({'component':name,'bounds_mm':[low.tolist(),high.tolist()],'rigid_intersections':0})
report={'passed':True,'physical_tested':False,'method':'Every fitted native GLB model conservative axis-aligned bounds vs exact structural STEP solids and hardware-piece envelopes','fitted_components':checks,'structural_parts':len(parts),'press_positions_mm':[0,p['button_travel']],'limits':['Elastomer deformation and bearing magnetic/RF influence need physical qualification'],'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'dist/index/circuit.json',root/'dist/index/3d.glb',root/'mechanical/enclosure-parameters.json']}}
(root/'validation/bearing-hardware-clearance.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Pass: new structural parts and fixed fasteners clear all {len(names)} fitted component envelopes')
