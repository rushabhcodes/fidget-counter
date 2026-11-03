"""Conservatively check new mechanical hardware against every fitted native CAD mesh."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
import numpy as np
import trimesh
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'mechanical'))
from hardware_models import screw
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
mid=p['pcb_bottom']+p['pcb_thickness']/2
c=json.loads((root/'dist/index/circuit.json').read_text())
sources={e['source_component_id']:e for e in c if e['type']=='source_component'}
names=[sources[e['source_component_id']]['name'] for e in c if e['type']=='pcb_component' and not e.get('do_not_place') and e.get('source_component_id') in sources]
assert len(names)==28
scene=trimesh.load(root/'dist/index/3d.glb',force='scene')
parts={name:cq.importers.importStep(str(root/'mechanical/STEP_Parts'/f'{name}.step')).val() for name in ['Stationary_Base','Inner_Race_Nut','Outer_Race_Retainer',*['Cap_'+s for s in p['cap_styles']]]}
exact_hardware={}
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
# Retaining screws and washers are real volumes, including their under-PCB heads.
for name in ['PCB_Fasteners']:
 row=next(r for r in rows if r['name']==name)
 # Individual disconnected hardware pieces must not be replaced by one huge box.
 mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True)
 for i,piece in enumerate(mesh.split(only_watertight=False)):
  low,high=piece.bounds
  parts[f'{name}_{i}']=cq.Workplane('XY').box(*(high-low)).val().translate(tuple((low+high)/2))
  x,y=((low+high)/2)[:2];actual=screw(.98,4,1.9,1.3,nylon=True).translate((float(x),float(y),p['pcb_bottom']+p['pcb_thickness']))
  bounds=actual.BoundingBox();assert max(abs(getattr(bounds,k+'min')-low[j]) for j,k in enumerate('xyz'))<.01 and max(abs(getattr(bounds,k+'max')-high[j]) for j,k in enumerate('xyz'))<.01,'Exact hardware does not match exported piece'
  exact_hardware[f'{name}_{i}']=actual
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
  poses=[0]
  for press in poses:
   volume=shape.translate((0,0,-press)).intersect(envelope).Volume()
   if volume>=.003 and name=='BT1':
    # A round holder's AABB has empty corners at the PCB posts. Narrow-phase
    # against the unmodified supplier STEP; never waive a real intersection.
    source=next(e for e in c if e['type']=='source_component'and e['name']=='BT1');cad=next(e for e in c if e['type']=='cad_component'and e['source_component_id']==source['source_component_id']);org=cad['model_origin_position'];rot=cad['rotation'];pos=cad['position'];actual=cq.importers.importStep(str(root/cad['model_step_url'])).val().translate(tuple(-org.get(k,0) for k in 'xyz'))
    for axis,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
     if rot.get(axis,0):actual=actual.rotate((0,0,0),vec,rot[axis])
    actual=actual.translate((pos['x'],pos['y'],pos['z']+mid));volume=exact_hardware.get(part,shape).translate((0,0,-press)).intersect(actual).Volume()
   assert volume<.003,(part,name,press,volume)
 checks.append({'component':name,'bounds_mm':[low.tolist(),high.tolist()],'rigid_intersections':0})
report={'passed':True,'physical_tested':False,'method':'Every fitted native GLB model conservative axis-aligned bounds vs exact structural STEP solids and hardware-piece envelopes','fitted_components':checks,'structural_parts':len(parts),'axial_positions_mm':[0],'limits':['Bearing magnetic/RF influence need physical qualification'],'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'dist/index/circuit.json',root/'dist/index/3d.glb',root/'mechanical/enclosure-parameters.json',Path(__file__),root/'mechanical/hardware_models.py',root/'imports/BS_24_B4AA014/BS_24_B4AA014.step']}}
(root/'validation/bearing-hardware-clearance.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'Pass: new structural parts and fixed fasteners clear all {len(names)} fitted component envelopes')
