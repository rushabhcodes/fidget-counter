"""V5 bearing-supported rotor with a guided, spring-return full-cap press.

Independent geometry for this board. Ploopy informs rotation; Surface Dial
informs the separate guided press and return springs. See MECHANICAL.md.
"""
from pathlib import Path
import argparse, hashlib, json, math
from functools import lru_cache
import cadquery as cq
import trimesh
from grip_profiles import make_grip
from spring_mesh import make_spring_mesh
from hardware_models import bearing_6708, screw, washer as detailed_washer, coin_cell, magnet as detailed_magnet, compression_spring

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--style',default='all');ap.add_argument('--out',type=Path,default=HERE/'export')
ap.add_argument('--parameters',type=Path,default=HERE/'enclosure-parameters.json')
a=ap.parse_args();P=json.loads(a.parameters.read_text());OUT=a.out.resolve()
for d in ['STEP','STL','Assemblies','Validation']:(OUT/d).mkdir(parents=True,exist_ok=True)
styles=P['cap_styles'] if a.style=='all' else [a.style]
assert all(s in P['cap_styles'] for s in styles)
def disk(r,z,h,x=0,y=0):return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h).val()
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
def box(w,d,z,h,x=0,y=0):return cq.Workplane('XY').box(w,d,h).val().translate((x,y,z+h/2))
def comp(shapes):return cq.Compound.makeCompound(list(shapes))
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
def overlap(left,right):
 b,c=left.BoundingBox(),right.BoundingBox()
 if any(getattr(b,k+'max')<=getattr(c,k+'min')+1e-7 or getattr(c,k+'max')<=getattr(b,k+'min')+1e-7 for k in 'xyz'):return 0.
 return left.intersect(right).Volume()
def clear(left,right,label):
 v=overlap(left,right);assert v<.002,(label,v);return v
def down(shape,press):return shape.translate((0,0,-press))
travel=P['button_travel'];pz=P['pcb_bottom'];pt=pz+P['pcb_thickness'];mid=pz+P['pcb_thickness']/2
B=P['bearing'];bz=B['bottom_z_mm'];bt=bz+B['width_mm'];G=P['press_guide'];S=P['return_springs'];N=P['inner_race_nut'];A=P['actuator']
guides=[polar(G['radius_mm'],a) for a in G['angles_deg']]
springs_at=[polar(S['radius_mm'],a) for a in S['angles_deg']]
M=P['pcb_mount'];mounts=[polar(M['radius_mm'],a) for a in M['angles_deg']]
assert P['base_diameter']==58 and P['overall_height']<=17.2
assert abs(G['boss_bottom_z_mm']-travel-G['hard_stop_z_mm'])<1e-7
assert S['assembled_length_mm']-travel>S['maximum_solid_height_mm']
print('Building the base, solid PCB screw posts and broad press guides...',flush=True)
tray=disk(29,.2,.6).fuse(ring(21,28.05,.79,1.56));magnets=[]
for i in range(24):
 x,y=polar(24.625,7.5+i*15);tray=tray.cut(disk(2.625,.8,1.66,x,y));magnets.append(detailed_magnet(2.5,.85,1.5).translate((x,y,0)))
tray=tray.clean();shield=ring(22.025,27.225,2.4,.7)
base=disk(29,.8,3.1).cut(disk(20.85,1.5,3.0))
base=base.cut(ring(20.85,28.2,.7,1.7)).cut(ring(22.025,27.225,2.4,.7)).fuse(disk(20.85,.8,.7))
wall=ring(20.2,21.0,1.4,2.5)
for x,y in guides:wall=wall.cut(disk(4.4,1.8,2.3,x,y))
base=base.fuse(wall)
pcb_fast=[]
for index,(x,y) in enumerate(mounts):
 post=disk(2.25,1.4,pz-1.4,x,y)
 # Two short, rigid locating collars keep the PCB centered inside the carrier.
 # They never flex or retain the board; the purchased nylon screws do that.
 if index in [0,2]:post=post.fuse(disk(1.4,pz,.5,x,y))
 post=post.cut(disk(.8,pz-5,5.6,x,y));base=base.fuse(post)
 pcb_fast.append(screw(.98,4,1.9,1.3,nylon=True).translate((x,y,pt)))
guide_fast=[]
for x,y in guides:
 foot=disk(4.,1.4,G['hard_stop_z_mm']-1.4,x,y)
 post=disk(2.5,G['hard_stop_z_mm'],G['post_top_z_mm']-G['hard_stop_z_mm'],x,y)
 base=base.fuse(foot,post).cut(disk(1.0,1.25,5.1,x,y))
 washer=detailed_washer(G['washer_inside_mm']/2,G['washer_outside_mm']/2,G['post_top_z_mm'],G['washer_thickness_mm']).translate((x,y,0))
 z=G['post_top_z_mm']+G['washer_thickness_mm']
 guide_fast.extend([washer,screw(1.2,5,G['screw_head_outside_mm']/2,G['screw_head_height_mm']).translate((x,y,z))])
for x,y in springs_at:
 base=base.cut(disk(1.7,S['seat_z_mm'],3.,x,y)).fuse(disk(2.,.8,S['seat_z_mm']-.8,x,y))
base=base.clean()
print('Building carrier, coarse inner-race nut and outer-race retainer...',flush=True)
carrier=ring(18.65,B['shaft_diameter_mm']/2,5.,bt-5.)
carrier=carrier.fuse(ring(18.65,B['inner_shoulder_outer_radius_mm'],5.,bz-5.))
for x,y in guides:
 carrier=carrier.fuse(disk(4.,G['boss_bottom_z_mm'],3.6,x,y))
 carrier=carrier.cut(disk(G['bore_diameter_mm']/2,2.8,4.2,x,y)).cut(disk(3.45,G['post_top_z_mm'],3.,x,y))
for x,y in springs_at:
 # Flat upper seat at Z5.0 preserves the specified spring preload. The base
 # pocket locates each spring; a recessed upper seat would lose preload.
 carrier=carrier.fuse(disk(2.3,5.,bz-5.,x,y))
# Real helical threads. The female groove has radial and flank clearance.
thread_start=bt+.05;thread_height=2.2;root_r=N['thread_root_radius_mm']
def ridge(clearance=0):
 path=cq.Wire.makeHelix(N['pitch_mm'],thread_height,root_r)
 w=.42+clearance;outer=root_r+N['thread_depth_mm']+clearance
 return cq.Workplane('XZ').polyline([(root_r-.08,-w),(outer,-.16-clearance),(outer,.16+clearance),(root_r-.08,w)]).close().sweep(path,isFrenet=True).val().translate((0,0,thread_start))
neck=ring(N['bore_radius_mm'],root_r,bt-.05,2.55).fuse(ridge()).intersect(disk(20.,bt,2.5)).clean()
carrier=carrier.fuse(neck).clean()
nut=ring(root_r+.05,N['outer_radius_mm'],bt+.3,2.2)
nut=nut.fuse(ring(root_r+.05,B['inner_shoulder_outer_radius_mm'],bt,.3))
nut=nut.cut(ridge(N['thread_clearance_mm']))
for angle in [0,90,180,270]:
 x,y=polar(21.6,angle);nut=nut.cut(box(2.,3.,bt+1.,1.6,x,y).rotate((x,y,0),(x,y,1),angle))
nut=nut.clean()
bearing,inner,outer,seals,bearing_parts=bearing_6708(bz)
retainer=ring(B['outer_shoulder_inner_radius_mm'],28.8,bz-1.5,1.5)
cap_holes=[polar(26.8,a) for a in [0,120,240]];cap_fast=[]
for x,y in cap_holes:
 retainer=retainer.cut(disk(.8,bz-1.6,1.7,x,y))
 # Accessible from the TOP. Bottom-entry screws would be blocked by the base.
 head_bottom=P['overall_height']-1.1
 cap_fast.append(screw(.98,10.9,1.9,1.1,countersunk=True).translate((x,y,head_bottom)))
retainer=retainer.clean()
pusher_z=pt+P['switch_height']+A['free_gap_mm']
actuator=ring(A['inside_mm']/2,A['outside_mm']/2,pusher_z,A['thickness_mm'])
hub=ring(B['housing_diameter_mm']/2,28.8,bz,P['cap_deck_bottom']-bz)
hub=hub.fuse(ring(B['outer_shoulder_inner_radius_mm'],28.8,bt,P['cap_deck_bottom']-bt))
hub=hub.fuse(disk(26.8,P['cap_deck_bottom'],P['overall_height']-P['cap_deck_bottom']))
hub=hub.fuse(ring(A['inside_mm']/2,A['outside_mm']/2,pusher_z+A['thickness_mm'],P['cap_deck_bottom']-pusher_z-A['thickness_mm']))
magnet=detailed_magnet(P['magnet_diameter']/2,P['magnet_bottom'],P['magnet_thickness']);spacer_z=P['magnet_bottom']+P['magnet_thickness'];spacer=disk(2.5,spacer_z,.2)
hub=hub.fuse(ring(2.6,3.5,P['magnet_bottom']-.1,P['cap_deck_bottom']-P['magnet_bottom']+.1)).fuse(disk(3.5,spacer_z+.2,P['cap_deck_bottom']-spacer_z-.2))
for x,y in cap_holes:
 hub=hub.fuse(disk(2.5,bt,P['overall_height']-bt,x,y))
 hub=hub.cut(disk(1.1,bz-.1,P['overall_height']-bz+.2,x,y))
 hub=hub.cut(cq.Solid.makeCone(1.1,2.,1.1,cq.Vector(x,y,P['overall_height']-1.1)))
hub=hub.clean();caps={s:hub.fuse(make_grip(s,P)).clean() for s in styles}
@lru_cache(maxsize=2)
def springs(press=0):
 spring=compression_spring(S,press)
 return comp(spring.translate((x,y,0)) for x,y in springs_at)
pcb=disk(P['pcb_diameter']/2,pz,P['pcb_thickness'])
for x,y in mounts:pcb=pcb.cut(disk(M['hole_diameter_mm']/2,pz-.1,P['pcb_thickness']+.2,x,y))
holder=cq.importers.importStep(str(HERE/'imports/holder.step')).val().translate((0,0,.01)).rotate((0,0,0),(0,1,0),180).translate((-1.2,0,pz))
cell,cell_parts=coin_cell(pz-4.7);sensor=box(.824,1.316,pt,.5)
switch=comp([box(4.2,2.8,pt,1.4,P['switch_x'],P['switch_y']),disk(.8,pt+1.4,.5,P['switch_x'],P['switch_y'])])
circuit=json.loads((ROOT/'published.circuit.json').read_text())
# Place the same supplier STEP models used by the native electronic preview.
# Model origin is subtracted before XYZ rotation and board-space translation.
electronics={}; electronic_colors={}
for cad in (e for e in circuit if e['type']=='cad_component' and e.get('model_step_url')):
 source=next(e for e in circuit if e['type']=='source_component' and e['source_component_id']==cad['source_component_id'])
 name=source['name']; org=cad.get('model_origin_position',{}); rot=cad.get('rotation',{}); pos=cad['position']
 shape=cq.importers.importStep(str(ROOT/cad['model_step_url'])).val().translate(tuple(-org.get(k,0) for k in 'xyz'))
 for axis,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
  if rot.get(axis,0):shape=shape.rotate((0,0,0),vec,rot[axis])
 shape=shape.translate((pos['x'],pos['y'],pos['z']+mid))
 electronics['Electronic_'+name]=shape
 electronic_colors['Electronic_'+name]=(.69,.71,.70) if name=='BT1' else ((.88,.85,.73) if name=='J_DEBUG' else ((.65,.48,.29) if name.startswith('C') else (.16,.17,.18)))
assert len(electronics)==31
holder=electronics['Electronic_BT1']; sensor=electronics['Electronic_U2']; switch=electronics['Electronic_SW1'];jst=electronics['Electronic_J_DEBUG']
jst_box=box(8.3,6.1,pt,2.92,0,-13.3)
physical={'Stationary_Base':base,'Bottom_Tray':tray,'Bearing_Carrier':carrier,'Inner_Race_Nut':nut,'Outer_Race_Retainer':retainer,**{'Cap_'+s:c for s,c in caps.items()}}
for name,shape in physical.items():assert shape.isValid() and len(shape.Solids())==1,(name,'Invalid/disconnected printed part',len(shape.Solids()))
stationary={'Stationary_Base':base,'Bottom_Tray':tray,'PCB':pcb,'Holder':holder,'Cell':cell,'Sensor':sensor,'Button':switch,'Backing_Ring':shield,'Attachment_Magnets':comp(magnets),'Guide_Fasteners':comp(guide_fast),'PCB_Fasteners':comp(pcb_fast),'J_DEBUG':jst}
moving={'Bearing_Carrier':carrier,'Inner_Race_Nut':nut,'Bearing_6708':bearing,'Outer_Race_Retainer':retainer,'Cap_Retainer_Screws':comp(cap_fast),'Magnet':magnet,'Encoder_Spacer':spacer,'Actuator_Ring':actuator}
print('Checking PCB, holder, JST, full-cap pressing and bearing-race separation...',flush=True)
clear(base,pcb,'PCB seating');clear(base,holder,'holder/base');clear(base,cell,'cell/base')
press_checks=[]
for press in [0,travel/2,travel]:
 for name,shape in moving.items():
  if name=='Actuator_Ring':continue # Force/compression requires material qualification, not rigid CAD.
  # Conservative annular envelope avoids expensive per-ball booleans.
  checked=ring(20,25,bz,6) if name=='Bearing_6708' else shape
  for other,fixed in stationary.items():clear(down(checked,press),fixed,f'{name}/{other} at {press}')
 for style,cap in caps.items():
  for name,fixed in stationary.items():clear(down(cap,press),fixed,f'{style}/{name} at {press}')
  clear(down(cap,press),jst_box,f'{style}/JST courtyard at {press}')
 press_checks.append({'press_mm':press,'rigid_collisions':0})
for label,left,right in [('carrier/outer race',carrier,outer),('nut/seals',nut,seals),('cap/inner race',hub,inner),('retainer/inner race',retainer,inner),('carrier/nut thread',carrier,nut),('carrier/cap',carrier,hub),('nut/cap',nut,hub)]:clear(left,right,label)
assert overlap(down(carrier,travel+.03),base)>.01,'No housing hard stop'
assert overlap(carrier.translate((0,0,.1)),stationary['Guide_Fasteners'])>.01,'No carrier upward retention'
print('Checking rotation at 24 angles and three press positions...',flush=True)
rotation=[]
for press in [0,travel/2,travel]:
 for angle in range(0,360,15):
  rotor=down(hub.rotate((0,0,0),(0,0,1),angle),press)
  for name,fixed in stationary.items():clear(rotor,fixed,f'rotor/{name} {press}/{angle}')
  for name in ['Bearing_Carrier','Inner_Race_Nut']:clear(rotor,down(moving[name],press),f'rotor/{name} {angle}')
  rotation.append({'press_mm':press,'angle_deg':angle,'rigid_collisions':0})
for style in styles:clear(make_grip(style,P),disk(26.8,P['cap_edge_bottom']-.01,P['cap_deck_bottom']-P['cap_edge_bottom']),style+' grip keepout')
floor=hub.intersect(ring(10.24,16.9,0,25)).BoundingBox().zmin-travel;jst_gap=floor-pt-2.92
assert jst_gap>=.7,('JST full-sweep gap',jst_gap)
print('Exporting printable STLs and released/pressed/exploded STEP assemblies...',flush=True)
manifest=[]
for name,shape in physical.items():
 cq.exporters.export(shape,str(OUT/'STEP'/f'{name}.step'))
 oriented=shape.rotate((0,0,0),(1,0,0),180) if name.startswith('Cap_') else shape
 oriented=oriented.translate((0,0,-oriented.BoundingBox().zmin));path=OUT/'STL'/f'{name}.stl'
 cq.exporters.export(oriented,str(path),tolerance=.035,angularTolerance=.09)
 mesh=trimesh.load_mesh(path,process=True);mask=mesh.nondegenerate_faces(height=1e-6)
 if not mask.all():mesh.update_faces(mask);mesh.remove_unreferenced_vertices();mesh.export(path)
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,(name,'Invalid STL')
 b=shape.BoundingBox();manifest.append({'name':name,'valid':shape.isValid(),'solids':len(shape.Solids()),'volume_mm3':shape.Volume(),'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds_mm':[[getattr(b,k+'min') for k in 'xyz'],[getattr(b,k+'max') for k in 'xyz']]})
cq.exporters.export(actuator,str(OUT/'STEP'/'Actuator_Ring_REFERENCE_ONLY.step'))
cq.exporters.export(actuator.translate((0,0,-pusher_z)),str(OUT/'STL'/'Actuator_Ring_REFERENCE_ONLY.stl'))
colors={'Stationary_Base':(.34,.4,.45),'Bottom_Tray':(.25,.3,.34),'Bearing_Carrier':(.83,.54,.2),'Inner_Race_Nut':(.92,.68,.28),'Outer_Race_Retainer':(.12,.38,.48),'Bearing_6708':(.7,.73,.77),'PCB':(.17,.44,.3),'Actuator_Ring':(.7,.85,.8)}
meshes=[];seen_meshes=set()
for style,cap in caps.items():
 for state in ['Released','Pressed','Exploded']:
  press=travel if state=='Pressed' else 0;assembly=cq.Assembly(name=style+'_'+state)
  values={**{k:v for k,v in stationary.items() if k not in ['Holder','Sensor','Button','J_DEBUG']},**electronics,**moving,'Return_Springs':springs(press),'Cap_'+style:cap}
  for name,shape in values.items():
   z=-press if name in moving or name.startswith('Cap_') else 0
   if state=='Exploded':z={'Bearing_Carrier':12,'Inner_Race_Nut':36,'Bearing_6708':22,'Outer_Race_Retainer':6,'Cap_'+style:50,'Magnet':45,'Encoder_Spacer':45,'Actuator_Ring':42,'PCB':5,'Guide_Fasteners':8,'PCB_Fasteners':10,'Cap_Retainer_Screws':50}.get(name,5 if name.startswith('Electronic_') else 0)
   posed=shape.translate((0,0,z));color=(.12,.47,.58) if name.startswith('Cap_') else electronic_colors.get(name,colors.get(name,(.58,.6,.63)))
   detailed=bearing_parts if name=='Bearing_6708' else (cell_parts if name=='Cell' else None)
   if detailed:
    detail=cq.Assembly(name=name)
    for i,(label,part,part_color,finish) in enumerate(detailed):detail.add(part,name=f'Part_{i}',color=cq.Color(*part_color))
    assembly.add(detail,name=name,loc=cq.Location(cq.Vector(0,0,z)))
   else:assembly.add(posed,name=name,color=cq.Color(*color))
   if state=='Released' and name not in seen_meshes:
    parts=bearing_parts if name=='Bearing_6708' else (cell_parts if name=='Cell' else [(name,posed,color,'nylon' if name=='PCB_Fasteners' else ('steel' if name in ['Guide_Fasteners','Cap_Retainer_Screws','Return_Springs','Backing_Ring','Attachment_Magnets','Magnet'] else 'plastic'))])
    vertices=[];faces=[];groups=[]
    for label,part,part_color,finish in parts:
     if name=='Return_Springs':vv,ff=make_spring_mesh(P)
     else:
      vv,ff=part.tessellate(.035,.13);vv=[list(v.toTuple()) for v in vv]
     start=len(faces);offset=len(vertices);vertices.extend(vv);faces.extend([[i+offset for i in f] for f in ff])
     groups.append({'label':label,'first_face':start,'face_count':len(ff),'color':part_color,'finish':finish})
    meshes.append({'style':style,'name':name,'nativeElectronic':name.startswith('Electronic_'),'color':color,'vertices':vertices,'faces':faces,'groups':groups});seen_meshes.add(name)
  assembly.save(str(OUT/'Assemblies'/f'{style}_{state}.step'))
report={'status':'Nominal CAD prototype; physical qualification required','physical_tested':False,'parameters':P,'printed_parts':manifest,'press_checks':press_checks,'rotation_checks':rotation,'continuous_rotation_deg':360,'rotation_method':'Axisymmetric structural rotor and exterior grip keepout; sampled angles supplement the envelope','base_diameter_mm':58,'overall_height_mm':P['overall_height'],'height_increase_mm':P['overall_height']-15.2,'pcb_midplane_z_mm':mid,'pcb_screws':4,'flexible_printed_latches':0,'return_springs':3,'cap_retainer_screws':3,'press_travel_mm':travel,'guide_engagement_mm':3.,'guide_radial_clearance_mm':.15,'jst_swept_clearance_mm':jst_gap,'sensor_gap_mm':{'released':1.8,'pressed':1.8-travel},'spring_preload_each_n':(S['free_length_mm']-S['assembled_length_mm'])*S['rate_n_per_mm'],'spring_solid_height_clearance_mm':S['assembled_length_mm']-travel-S['maximum_solid_height_mm'],'actuator_qualified':False,'actuator_note':A['qualification'],'references':{'rotation':'https://ploopyco.github.io/knob/assembly-instructions/','press':'https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808'},'scope':'Independent geometry for this PCB; electrical layout unchanged','model_detail':{'bearing':'25 balls of diameter 2.381 mm, grooved/chamfered races, stamped cage and non-contact metal shields; representative internals','fasteners':'Helical thread roots and recessed cross drives within existing envelopes','battery':'Rolled can, gasket, negative lid and recessed generic CR2032 marking','electronics':'All 31 fitted supplier STEP models, placed using native model origins and XYZ rotations','spring':'Five active turns plus two close-wound end turns; reference geometry, not a sourced SKU'},'detail_reference_urls':['https://www.astbearings.com/catalog/root/6708','https://iskbearing.com/product-details/6708zz','https://www.leespring.com/learn-about-compression-springs','https://www.duracell.com/wp-content/uploads/2016/04/LI2032US10141.pdf'],'physical_checks_required':['Chosen bearing fits, shoulder lands, seal clearance and corner radii','Spring return, tilt and guide friction','Actuator force, switch overtravel and all-angle closure','Rotation/press/removal endurance','Bearing and fastener influence on Hall sensing, phone attachment and RF','Actual spring/fastener sourcing']}
(OUT/'Validation'/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'Validation'/'scene_meshes.json').write_text(json.dumps(meshes))
if set(styles)==set(P['cap_styles']):
 from sync_checked_exports import sync_checked_exports
 sync_checked_exports(HERE,OUT)
print(json.dumps({'printed_parts':len(manifest),'height_mm':P['overall_height'],'base_diameter_mm':58,'styles':styles,'output':str(OUT)},indent=2),flush=True)
