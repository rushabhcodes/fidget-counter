"""Prove straight PCBA insertion with continuous conservative swept volumes.

The PCB sweep uses its real outline/drills. Every electronic STEP bounding box
is extruded through20mm; the cell uses its purchased cylindrical envelope.
A bounded old/new STEP comparison rejects changes outside the fixed throat.
"""
from pathlib import Path
import hashlib,json,subprocess,math
import cadquery as cq
R=Path(__file__).resolve().parents[1];P=json.loads((R/'mechanical/enclosure-parameters.json').read_text());C=json.loads((R/'published.circuit.json').read_text());B=P['bearing'];N=P['inner_race_nut'];travel=20.
pz=P['pcb_bottom'];mid=pz+P['pcb_thickness']/2
base=cq.importers.importStep(str(R/'mechanical/STEP_Parts/Stationary_Base.step')).val()
oldfile=R/'work/pcb-insertion/previous-base.step';oldfile.parent.mkdir(parents=True,exist_ok=True);oldfile.write_bytes(subprocess.check_output(['git','show','bab8aa4b2011a14873aea0a3094a3c7ed4d9e685:mechanical/STEP_Parts/Stationary_Base.step'],cwd=R));before=cq.importers.importStep(str(oldfile)).val()
# Only enlarge the inner passage. The male thread and female nut stay intact.
bottom=B['bottom_z_mm']+B['width_mm'];cut=cq.Solid.makeCylinder(18.65,2.502,cq.Vector(0,0,bottom-.001));expected=before.cut(cut)
assert expected.cut(base).Volume()<.002 and base.cut(expected).Volume()<.002,'Unrelated base change'
assert base.cut(before).Volume()<.002,'Insertion fix must add no material'
assert abs(N['shaft_bore_radius_mm']-18.65)<1e-9 and N['thread_root_radius_mm']-18.65>=.8
for z in [bottom+.01,bottom+1.1,bottom+2.49]:
 for a in range(0,360,15):
  for rad in [18.66,19.05,19.49]:assert base.isInside(cq.Vector(rad*math.cos(math.radians(a)),rad*math.sin(math.radians(a)),z),1e-6),'Missing thread root wall'
board=next(e for e in C if e['type']=='pcb_board');outline=[(v['x'],v['y']) for v in board['outline']]
sweep=cq.Workplane('XY').workplane(offset=pz).polyline(outline).close().extrude(board['thickness']+travel).val()
for hole in [e for e in C if e['type']=='pcb_hole']:sweep=sweep.cut(cq.Solid.makeCylinder(hole['hole_diameter']/2,board['thickness']+travel+.02,cq.Vector(hole['x'],hole['y'],pz-.01)))
old_hit=before.intersect(sweep).Volume();assert old_hit>1,'Regression fixture must detect the old insertion obstruction'
volume=base.intersect(sweep).Volume();assert volume<.002,('PCB motion blocked',volume)
rows=[];paths=[]
for cad in (e for e in C if e['type']=='cad_component' and e.get('model_step_url')):
 source=next(e for e in C if e['type']=='source_component' and e['source_component_id']==cad['source_component_id']);org=cad.get('model_origin_position',{});rot=cad.get('rotation',{});pos=cad['position'];path=R/cad['model_step_url'];shape=cq.importers.importStep(str(path)).val().translate(tuple(-org.get(k,0) for k in 'xyz'))
 for axis,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
  if rot.get(axis,0):shape=shape.rotate((0,0,0),vec,rot[axis])
 shape=shape.translate((pos['x'],pos['y'],pos['z']+mid));bounds=shape.BoundingBox();motion=cq.Workplane('XY').box(bounds.xlen,bounds.ylen,bounds.zlen+travel).val().translate(((bounds.xmin+bounds.xmax)/2,(bounds.ymin+bounds.ymax)/2,(bounds.zmin+bounds.zmax+travel)/2));v=base.intersect(motion).Volume();assert v<.002,(source['name'],'Swept supplier bounding box intersects base',v)
 rows.append({'component':source['name'],'swept_bbox_intersection_mm3':v});paths.append(path)
assert len(rows)==28
cell=cq.Solid.makeCylinder(10,3.2+travel,cq.Vector(0,0,pz-4.7));assert base.intersect(cell).Volume()<.002,'Cell insertion blocked'
files=[Path(__file__),R/'mechanical/build_enclosure.py',R/'mechanical/enclosure-parameters.json',R/'mechanical/STEP_Parts/Stationary_Base.step',R/'published.circuit.json',*paths]
report={'passed':True,'physical_tested':False,'method':'Continuous Z-prism of actual drilled PCB; continuous conservative Z-prisms of28 supplier STEP bounding boxes; cylindrical cell sweep','motion_upward_from_seated_mm':travel,'previous_comparison_commit':'bab8aa4b2011a14873aea0a3094a3c7ed4d9e685','previous_obstruction_volume_mm3':old_hit,'PCB_swept_intersection_mm3':volume,'fixed_throat_diameter_mm':37.3,'PCB_diameter_mm':36.5,'nominal_radial_insertion_clearance_mm':.4,'minimum_male_root_wall_mm':.85,'unrelated_base_changes':False,'electronics':rows,'remaining_physical':['Printed throat/PCB outline tolerance and handling','Male thread strength/torque/life with0.85mm root wall','Battery/holder and populated board physical fit'],'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(R/'validation/pcb-insertion-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: continuous20mm insertion sweeps clear PCB,28 supplier bounds and CR2032; previous throat obstructed{old_hit:.4f}mm3')
