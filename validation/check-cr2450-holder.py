"""Full curved holder-body clearance, independent of compiler courtyard AABBs.

Native PCB courtyards cover the two solder terminals. This mandatory audit
retains the complete model-derived body courtyard and loaded-cell checks.
Free-state metal contact deflection is bounded, not presented as rigid clearance.
"""
from pathlib import Path
import hashlib,json,math
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import Polygon,Point,box
from shapely.affinity import scale
R=Path(__file__).resolve().parents[1];P=json.loads((R/'mechanical/enclosure-parameters.json').read_text());spec=P['battery'];C=json.loads((R/'dist/index/circuit.json').read_text());meta=json.loads((R/'mechanical/battery-holder-courtyard.json').read_text())
sid=next(e['source_component_id'] for e in C if e['type']=='source_component'and e['name']=='BT1');pcb=next(e for e in C if e['type']=='pcb_component'and e.get('source_component_id')==sid);cad=next(e for e in C if e['type']=='cad_component'and e.get('source_component_id')==sid)
assert pcb['center']=={'x':0,'y':0} and pcb['layer']=='bottom'
assert cad['rotation']=={'x':0,'y':180,'z':0} and cad['model_origin_position']=={'x':0,'y':0,'z':-.9}
path=R/cad['model_step_url'];raw=cq.importers.importStep(str(path)).val();rb=raw.BoundingBox();assert raw.isValid() and abs(rb.zlen-7.6)<1e-5
holder=raw.translate((0,0,.9)).rotate((0,0,0),(0,1,0),180).translate((0,0,P['pcb_bottom']))
outline=scale(Polygon([(v['x'],v['y']) for v in meta['outline']]),xfact=-1,yfact=1,origin=(0,0));assert outline.is_valid
board=next(e for e in C if e['type']=='pcb_board');board_polygon=Polygon([(p['x'],p['y']) for p in board['outline']]);assert outline.difference(board_polygon.buffer(-.3)).area<1e-7,'Holder courtyard extends beyond board edge reserve'
for path,sha in meta['source_sha256'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==sha,('Stale body courtyard',path)
for h in [e for e in C if e['type']=='pcb_hole']:assert outline.intersection(Point(h['x'],h['y']).buffer(h['hole_diameter']/2)).area<1e-7,'Holder body/drill collision'
for k in [e for e in C if e['type']=='pcb_keepout' and e['shape']=='circle' and 'bottom'in e['layers']]:assert outline.intersection(Point(k['center']['x'],k['center']['y']).buffer(k['radius'])).area<1e-7,'Holder body/post keepout collision'
# The drawing confines both phosphor-bronze terminals to the central strip.
# The white LCP housing enters the antenna's XY reserve; do not claim RF
# qualification from that conductor-only clearance.
rf=next(e for e in C if e['type']=='pcb_keepout'and e['shape']=='rect'and e['center']=={'x':0,'y':15.8})
rfshape=box(-rf['width']/2,15.8-rf['height']/2,rf['width']/2,15.8+rf['height']/2)
conductor_strip=box(-17.25,-3.6,17.25,3.6);assert not conductor_strip.intersects(rfshape)
assert not Point(0,0).buffer(spec['diameter_mm']/2).intersects(rfshape),'Cell enters antenna copper reserve'
plastic_rf_overlap=outline.intersection(rfshape).area
others=[e for e in C if e['type']=='pcb_component'and not e.get('do_not_place')and e.get('source_component_id')!=sid and any(s['type']=='source_component'and s['source_component_id']==e.get('source_component_id') for s in C)]
assert len(others)==26 and all(e['layer']=='top'for e in others),'New bottom fitted part requires a holder-body clearance check'
base=cq.importers.importStep(str(R/'mechanical/STEP_Parts/Stationary_Base.step')).val();assert base.intersect(holder).Volume()<.002
post_gaps=[]
for a in P['pcb_mount']['angles_deg']:
 x,y=spec['cell_center_mm'];r=P['pcb_mount']['radius_mm'];x+=r*math.cos(math.radians(a));y+=r*math.sin(math.radians(a));post=cq.Solid.makeCylinder(1.6,P['pcb_bottom']-1.4,cq.Vector(x,y,1.4));gap=holder.distance(post);assert gap>=.24,(a,gap);post_gaps.append(gap)
cellraw=cq.Solid.makeCylinder(12.25,5,cq.Vector(0,0,2.7));contact=raw.intersect(cellraw)
def cuboid(x0,x1,y0,y1,z0,z1):return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0).val().translate(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
allowed=cuboid(-10.1,-4.4,-1.85,1.85,2.699,5.4).fuse(cuboid(11.05,12.3,-1.85,1.85,2.699,5.4))
assert contact.Volume()<4 and contact.cut(allowed).Volume()<.002,'Cell hits rigid housing or an undocumented contact region'
cell=cq.Solid.makeCylinder(12.25,5,cq.Vector(0,0,2.0));assert base.intersect(cell).Volume()<.002
assert abs(P['pcb_bottom']-spec['holder_loaded_height_mm']-spec['cell_bottom_z_mm'])<1e-9
scene=trimesh.load(R/'dist/index/3d.glb',force='scene');vertices=[]
for node in scene.graph.nodes_geometry:
 if node=='BT1'or node.startswith('BT1_'):
  transform,name=scene.graph[node];m=scene.geometry[name].copy();m.apply_transform(transform);vertices.append(m.vertices)
v=np.concatenate(vertices);world=np.column_stack((-v[:,0],v[:,2],v[:,1]+P['pcb_bottom']+.5));b=holder.BoundingBox();bounds=np.array([[getattr(b,k+'min')for k in'xyz'],[getattr(b,k+'max')for k in'xyz']]);assert np.abs(np.array([world.min(axis=0),world.max(axis=0)])-bounds).max()<.02,'Native holder preview differs from supplier pose'
files=[Path(__file__),R/'parts.tsx',R/'mechanical/enclosure-parameters.json',R/'mechanical/battery-holder-courtyard.json',R/'mechanical/build_battery_courtyard.py',R/'mechanical/references/MYOUNG_BS-24-B4AA014_MY-CP-0246_A0.pdf',R/'dist/index/circuit.json',R/'dist/index/3d.glb',R/'mechanical/STEP_Parts/Stationary_Base.step',R/'imports/BS_24_B4AA014/BS_24_B4AA014.step',R/'imports/BS_24_B4AA014/BS_24_B4AA014.obj',R/'imports/BS_24_B4AA014/BS_24_B4AA014.tsx']
report={'passed':True,'physical_tested':False,'holder':spec['holder_mpn'],'supplier_drawing':'MY-CP-0246 A/0 2022-03-26','body_height_mm':7.6,'loaded_height_mm':8.6,'cell_floor_clearance_mm':.5,'minimum_holder_post_clearance_mm':min(post_gaps),'full_curved_body_courtyard_checked':True,'native_courtyard_scope':'Two solder terminals only; compiler outline/drill AABB limitation covered by independent full-body audit','loaded_cell_rigid_housing_collision_mm3':contact.cut(allowed).Volume(),'free_state_contact_intrusion_mm3':contact.Volume(),'free_state_contact_regions_only':True,'RF_conductor_strip_clear':True,'LCP_body_RF_reserve_overlap_mm2':plastic_rf_overlap,'limits':['Loaded spring-contact force, polarity, cell seating and retention require the selected physical holder/cell sample','LCP housing affects antenna loading; full populated Hall/BLE/RF qualification and matching remain required','Printed post/board fit,0.55mm PCB edge web and retention need physical qualification'],'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}}
(R/'validation/cr2450-holder-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: complete curved body, four holes/posts, loaded-cell envelope and native pose; free-state contact intrusion explicitly bounded, RF/physical qualification pending')
