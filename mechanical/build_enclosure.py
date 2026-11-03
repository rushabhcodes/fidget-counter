"""Rotation-only Ploopy-inspired fixed shaft and hollow rotating cap. Independent CAD for this PCB."""
from pathlib import Path
import argparse, hashlib, json, math
import cadquery as cq
import trimesh
from grip_profiles import make_grip
from hardware_models import bearing_6708, bearing_6808, screw, coin_cell, magnet as detailed_magnet, magsafe_ring

HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--style',default='all');ap.add_argument('--out',type=Path,default=HERE/'export')
ap.add_argument('--parameters',type=Path,default=HERE/'enclosure-parameters.json')
ap.add_argument('--assembly-style',default='all',help='Export all assembly STEP variants, or one style while still checking/exporting every requested cap')
a=ap.parse_args();P=json.loads(a.parameters.read_text());OUT=a.out.resolve()
for d in ['STEP','STL','Assemblies','Validation']:(OUT/d).mkdir(parents=True,exist_ok=True)
pushfit=P.get('cap_retention',{}).get('mode')=='push_fit'
styles=P['cap_styles'] if a.style=='all' else [a.style]
assert all(s in P['cap_styles'] for s in styles)
assembly_styles=styles if a.assembly_style=='all' else [a.assembly_style]
assert set(assembly_styles)<=set(styles)
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
pz=P['pcb_bottom'];pt=pz+P['pcb_thickness'];mid=pz+P['pcb_thickness']/2
B=P['bearing'];bz=B['bottom_z_mm'];bt=bz+B['width_mm'];G=P['fixed_bearing_support'];N=P['inner_race_nut']
bearing_name='Bearing_6808' if B['designation'].startswith('6808') else 'Bearing_6708'
J=P['cap_retainer_joint']
assert [J[k] for k in ['boss_radius_mm','boss_top_z_mm','socket_radius_mm','socket_roof_z_mm','nominal_thread_overlap_mm']]==[1.6,9.6,1.8,9.8,4.4],'Revalidate retainer joint before changing its geometry'
supports=[polar(G['radius_mm'],a) for a in G['angles_deg']]
M=P['pcb_mount'];mounts=[polar(M['radius_mm'],a) for a in M['angles_deg']]
pcb_screw_indices=M.get('screw_indices',[0,1,2,3])
assert pcb_screw_indices in [[0,1,2,3],[0,2]],'Only the default or opposite-pair PCB trial is supported'
assert P['base_diameter']==58 and P['overall_height']<=17.2
print('Building the single-ring seat, solid PCB screw posts and integral bearing supports...',flush=True)
R=P['attachment_ring'];ri=R['inside_mm']/2;ro=R['outside_mm']/2
ring_z=R['phone_face_z_mm'];seat_z=ring_z+R['thickness_mm']+R['bondline_mm']
assert seat_z<=2.4+1e-7 and 3.0-seat_z>=.6-1e-7
# One broad, phone-side annular seat replaces all 24 individual pockets. The
# integral 0.6 mm roof joins the inner and outer walls; no brittle retaining tabs.
tray=disk(29,.2,.6).fuse(ring(21,28.05,.79,2.21))
tray=tray.cut(ring(ri-R['radial_clearance_mm'],ro+R['radial_clearance_mm'],.1,seat_z-.1))
# The integrated ring seat retains a continuous solid roof.
tray=tray.clean();attachment=magsafe_ring(R)
base=disk(29,.8,3.1).cut(disk(20.85,1.5,3.0))
base=base.cut(ring(20.85,28.2,.7,2.45)).fuse(disk(20.85,.8,.7))
wall=ring(20.2,21.0,1.4,2.5)
for x,y in supports:wall=wall.cut(disk(4.4,1.8,2.3,x,y))
base=base.fuse(wall)
pcb_fast=[]
for index,(x,y) in enumerate(mounts):
 post=disk(M['post_radius_mm'],1.4,pz-1.4,x,y).fuse(disk(M['foot_radius_mm'],1.4,.4,x,y))
 # Two short, rigid locating collars keep the PCB centered inside the fixed bearing shaft.
 # They never flex or retain the board; the purchased nylon screws do that.
 if M['collar_height_mm']>0 and index in [0,2]:post=post.fuse(disk(1.4,pz,M['collar_height_mm'],x,y))
 post=post.cut(disk(.8,pz-5,5.6,x,y));base=base.fuse(post)
 if index in pcb_screw_indices:pcb_fast.append(screw(.98,4,1.9,1.3,nylon=True).translate((x,y,pt)))
# Broad, rigid webs replace the former clearance-fit guide posts and fasteners.
# The old carrier boss envelope is preserved around the battery holder.
for x,y in supports:
 base=base.fuse(disk(G['web_foot_radius_mm'],1.4,G['web_foot_height_mm'],x,y),disk(G['web_stem_radius_mm'],G['web_stem_bottom_z_mm'],G['web_stem_height_mm'],x,y))
# Base and tray share a material and have no service separation. Merge them,
# fill their former assembly clearances, and preserve all functional pockets.
interface_fill=ring(20.85,28.2,.79,2.36)
# Preserve the original solid guide feet/posts; clearance belongs only in the
# added annular filler, not through the structural guide supports.
for x,y in supports:interface_fill=interface_fill.cut(disk(4.4,1.8,2.3,x,y))
base=base.fuse(tray,interface_fill)
base=base.cut(ring(ri-R['radial_clearance_mm'],ro+R['radial_clearance_mm'],.1,seat_z-.1))
base=base.clean()
print('Building fixed bearing shaft, coarse inner-race nut and outer-race retainer...',flush=True)
fixed_support=ring(18.65,B['shaft_diameter_mm']/2,5.,bt-5.)
fixed_support=fixed_support.fuse(ring(18.65,B['inner_shoulder_outer_radius_mm'],5.,bz-5.))
for x,y in supports:fixed_support=fixed_support.fuse(disk(G['web_head_radius_mm'],3.,bz-3.,x,y))
# Real helical threads. The female groove has radial and flank clearance.
thread_start=bt+.05;thread_height=2.2;root_r=N['thread_root_radius_mm']
def ridge(clearance=0):
 path=cq.Wire.makeHelix(N['pitch_mm'],thread_height,root_r)
 w=.42+clearance;outer=root_r+N['thread_depth_mm']+clearance
 return cq.Workplane('XZ').polyline([(root_r-.08,-w),(outer,-.16-clearance),(outer,.16+clearance),(root_r-.08,w)]).close().sweep(path,isFrenet=True).val().translate((0,0,thread_start))
assert N['shaft_bore_radius_mm']-P['pcb_diameter']/2>=.3,'PCB cannot pass through fixed shaft throat with assembly clearance'
assert root_r-N['shaft_bore_radius_mm']>=.8,'Insufficient male thread root wall'
neck=ring(N['shaft_bore_radius_mm'],root_r,bt-.05,2.55).fuse(ridge()).intersect(disk(20.,bt,2.5)).clean()
base=base.fuse(fixed_support,*([] if pushfit else [neck])).clean()
nut=ring(root_r+.05,N['outer_radius_mm'],bt+.3,2.2)
nut=nut.fuse(ring(root_r+.05,B['inner_shoulder_outer_radius_mm'],bt,.3))
nut=nut.cut(ridge(N['thread_clearance_mm']))
for angle in [0,90,180,270]:
 x,y=polar(N['outer_radius_mm']+1.-N['tool_notch_depth_mm'],angle);nut=nut.cut(box(2.,3.,bt+1.,1.6,x,y).rotate((x,y,0),(x,y,1),angle))
nut=nut.clean()
bearing,inner,outer,seals,bearing_parts=(bearing_6808 if bearing_name=='Bearing_6808' else bearing_6708)(bz)
retainer=ring(B['outer_shoulder_inner_radius_mm'],28.8,bz-1.5,1.5)
cap_holes=[] if pushfit else [polar(J['screw_pitch_radius_mm'],a) for a in [0,120,240]];cap_fast=[]
for x,y in cap_holes:
 # Integral upper bosses put 4.4 mm of nominal M2 engagement in the same
 # envelope. The former 1.5 mm ring alone supplied only 1.4 mm engagement.
 retainer=retainer.fuse(disk(1.6,bz-.02,J['boss_top_z_mm']-bz+.02,x,y))
 retainer=retainer.cut(disk(.8,bz-1.6,J['boss_top_z_mm']-bz+1.8,x,y))
 # Accessible from the TOP. Bottom-entry screws would be blocked by the base.
 head_bottom=P['overall_height']-1.1
 cap_fast.append(screw(.98,10.9,1.9,1.1,countersunk=True).translate((x,y,head_bottom)))
# Three shallow outer-edge saddles preserve1mm-thick reusable nest fingers
# above the base roof; they do not touch race lands or screw bosses.
for angle in J['fixture_angles_deg']:
 notch=box(1.6,J['fixture_notch_width_mm'],bz-1.6,J['fixture_support_z_mm']-(bz-1.6),28.8).rotate((0,0,0),(0,0,1),angle)
 retainer=retainer.cut(notch)
retainer=retainer.clean()
hub=ring(B['housing_diameter_mm']/2,28.8,bz,P['cap_deck_bottom']-bz)
hub=hub.fuse(ring(B['outer_shoulder_inner_radius_mm'],28.8,bt,P['cap_deck_bottom']-bt))
hub=hub.fuse(disk(26.8,P['cap_deck_bottom'],P['overall_height']-P['cap_deck_bottom']))
magnet=detailed_magnet(P['magnet_diameter']/2,P['magnet_bottom'],P['magnet_thickness']);magnet_top=P['magnet_bottom']+P['magnet_thickness']
assert P['encoder_stop']['mode']=='integral_cap' and abs(P['encoder_stop']['seated_top_z_mm']-magnet_top)<1e-7
# The cap itself now locates the magnet at the same Z. Remove the separate
# 0.2 mm spacer and bond only in the existing radial pocket clearance.
pocket_r=P['magnet_pocket_diameter']/2
hub=hub.fuse(ring(pocket_r,pocket_r+.9,P['magnet_bottom']-.1,max(P['cap_deck_bottom'],magnet_top)-P['magnet_bottom']+.1))
if P['cap_deck_bottom']>magnet_top+1e-7:
 hub=hub.fuse(disk(pocket_r+.9,magnet_top,P['cap_deck_bottom']-magnet_top))
# A lower roof must keep the established magnet seat, including after the
# exterior grip union. Preserve the magnet/sensor gap rather than moving it.
magnet_pocket_cut=disk(pocket_r,P['magnet_bottom']-.1,P['magnet_thickness']+.1)
hub=hub.cut(magnet_pocket_cut)
assert P['overall_height']-P['cap_deck_bottom']>=1.3-1e-7,'Main cap deck too thin'
assert P['overall_height']-magnet_top>=1.2-1e-7,'Encoder pocket roof too thin'
for x,y in cap_holes:
 hub=hub.fuse(disk(2.5,bt,P['overall_height']-bt,x,y))
 hub=hub.cut(disk(1.1,bz-.1,P['overall_height']-bz+.2,x,y))
 hub=hub.cut(disk(1.8,bz-.1,J['socket_roof_z_mm']-bz+.1,x,y))
 hub=hub.cut(cq.Solid.makeCone(1.1,2.,1.1,cq.Vector(x,y,P['overall_height']-1.1)))
# Vertical pads retain at least 1.0 mm around the countersinks and 1.2 mm
# outside the lower sockets. Clip their inner faces to the existing stepped
# bearing bore; extend the complete pads through the grip/deck union above it.
if not pushfit:
 reinforcement=comp(disk(J['cap_reinforcement_radius_mm'],bz,P['overall_height']-bz,x,y) for x,y in cap_holes)
 reinforcement=reinforcement.cut(disk(B['housing_diameter_mm']/2,bz-.1,bt-bz+.1))
 reinforcement=reinforcement.cut(disk(B['outer_shoulder_inner_radius_mm'],bt,P['cap_deck_bottom']-bt))
 hub=hub.fuse(reinforcement)
 for x,y in cap_holes:
  hub=hub.cut(disk(1.1,bz-.1,P['overall_height']-bz+.2,x,y))
  hub=hub.cut(disk(1.8,bz-.1,J['socket_roof_z_mm']-bz+.1,x,y))
  hub=hub.cut(cq.Solid.makeCone(1.1,2.,1.1,cq.Vector(x,y,P['overall_height']-1.1)))
hub=hub.clean();caps={}
for style in styles:
 cap=hub.fuse(make_grip(style,P)).cut(magnet_pocket_cut)
 # Apply assembly holes AFTER the exterior grip union. Otherwise that union
 # fills part of the screw bore, head recess and lower boss sockets again.
 for x,y in cap_holes:
  cap=cap.cut(disk(1.1,bz-.1,P['overall_height']-bz+.2,x,y))
  cap=cap.cut(disk(1.8,bz-.1,J['socket_roof_z_mm']-bz+.1,x,y))
  cap=cap.cut(cq.Solid.makeCone(1.1,2.,1.1,cq.Vector(x,y,P['overall_height']-1.1)))
 caps[style]=cap.clean()
 if not pushfit:
  screw_envelope=comp(disk(.98,5.2,10.9,x,y).fuse(cq.Solid.makeCone(.98,1.9,1.1,cq.Vector(x,y,16.1))) for x,y in cap_holes)
  clear(caps[style],retainer,style+' finished cap/retainer bosses')
  clear(caps[style],screw_envelope,style+' finished cap/screw envelopes')
pcb=disk(P['pcb_diameter']/2,pz,P['pcb_thickness'])
for x,y in mounts:pcb=pcb.cut(disk(M['hole_diameter_mm']/2,pz-.1,P['pcb_thickness']+.2,x,y))
cell,cell_parts=coin_cell(P['battery']['cell_bottom_z_mm'],P['battery']['standard'])
cx,cy=P['battery']['cell_center_mm'];cell=cell.translate((cx,cy,0));cell_parts=[(label,shape.translate((cx,cy,0)),color,finish) for label,shape,color,finish in cell_parts]
sensor=box(.824,1.316,pt,.5)
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
assert len(electronics)==27
holder=electronics['Electronic_BT1']; sensor=electronics['Electronic_U2'];jst=electronics['Electronic_J_DEBUG']
jst_box=box(8.3,6.1,pt,2.92,0,-13.3)
physical={'Stationary_Base':base,**({} if pushfit else {'Inner_Race_Nut':nut,'Outer_Race_Retainer':retainer}),**{'Cap_'+s:c for s,c in caps.items()}}
for name,shape in physical.items():assert shape.isValid() and len(shape.Solids())==1,(name,'Invalid/disconnected printed part',len(shape.Solids()))
stationary={'Stationary_Base':base,'PCB':pcb,'Cell':cell,'MagSafe_Ring':attachment,'PCB_Fasteners':comp(pcb_fast),**({} if pushfit else {'Inner_Race_Nut':nut}),**electronics}
moving={bearing_name:bearing,**({} if pushfit else {'Outer_Race_Retainer':retainer,'Cap_Retainer_Screws':comp(cap_fast)}),'Magnet':magnet}
print('Checking all 28 electronic models, fixed shaft, bearing-race separation and rotation...',flush=True)
for name,shape in electronics.items():
 clear(base,shape,'integrated base/'+name)
 if not pushfit:clear(nut,shape,'nut/'+name)
 for other,rotor in {**moving,**{'Cap_'+k:v for k,v in caps.items()}}.items():
  checked=ring(B['bore_mm']/2,B['outside_mm']/2,bz,B['width_mm']) if other.startswith('Bearing_') else rotor
  clear(checked,shape,other+'/'+name)
clear(base,pcb,'PCB seating');clear(base,cell,'cell/base');clear(base,attachment,'ring/integrated base')
assert abs(attachment.BoundingBox().zmin-ring_z)<1e-6
assert abs(seat_z-attachment.BoundingBox().zmax-R['bondline_mm'])<1e-6
for label,left,right in [('base/outer race',base,outer),('cap/inner race',hub,inner),('base/cap',base,hub)]+([] if pushfit else [('nut/seals',nut,seals),('retainer/inner race',retainer,inner),('base/nut thread',base,nut),('nut/cap',nut,hub)]):clear(left,right,label)
if not pushfit:
 clear(retainer,hub,'retainer boss/cap socket');clear(retainer,outer,'retainer boss/bearing')
rotation=[]
# The stepped bore and deck are axisymmetric. Every exterior grip lies outside
# the 26.8mm radial keepout. The small screw pads are inside the same stepped
# radial envelope; sample the final hub to supplement this continuous argument.
for angle in range(0,360,15):
 rotor=hub.rotate((0,0,0),(0,0,1),angle)
 for name,fixed in stationary.items():clear(rotor,fixed,f'rotor/{name} {angle}')
 rotation.append({'angle_deg':angle,'rigid_collisions':0})
for style,cap in caps.items():
 for name in ['Stationary_Base','PCB_Fasteners']+([] if pushfit else ['Inner_Race_Nut']):clear(cap,stationary[name],style+'/'+name)
 clear(cap,jst_box,style+'/JST courtyard')
for style in styles:clear(make_grip(style,P),disk(26.8,P['cap_edge_bottom']-.01,P['cap_deck_bottom']-P['cap_edge_bottom']),style+' grip keepout')
floor=hub.intersect(ring(10.24,16.9,0,25)).BoundingBox().zmin;jst_gap=floor-pt-2.92
assert jst_gap>=.7,('JST full-sweep gap',jst_gap)
print('Exporting printable STLs and assembled/exploded STEP assemblies...',flush=True)
manifest=[]
# Save every source solid before tessellation so an export failure leaves a
# complete CAD set for diagnosis; distribution still requires all mesh checks.
for name,shape in physical.items():cq.exporters.export(shape,str(OUT/'STEP'/f'{name}.step'))
for name,shape in physical.items():
 # The shallow thumb dishes face upwards and need internal cup supports.
 # All other caps print deck-down. Flip the nut so its wide face is on the bed.
 invert=(name.startswith('Cap_') and name!='Cap_thumb_scoop') or name=='Inner_Race_Nut'
 # Tessellate the distributed STEP, not a cached Boolean triangulation.
 # This also makes the printable mesh reproducible from the delivered CAD.
 printable=cq.importers.importStep(str(OUT/'STEP'/f'{name}.step')).val()
 serialization_delta=printable.Volume()-shape.Volume()
 serialization_difference=shape.cut(printable).Volume()+printable.cut(shape).Volume()
 assert printable.isValid() and len(printable.Solids())==1 and abs(serialization_delta)<.01 and serialization_difference<.002,(name,'STEP serialization changed geometry',serialization_delta,serialization_difference)
 assert max(abs(getattr(printable.BoundingBox(),k)-getattr(shape.BoundingBox(),k)) for k in ['xmin','xmax','ymin','ymax','zmin','zmax'])<1e-5,(name,'STEP bounds changed')
 oriented=printable.rotate((0,0,0),(1,0,0),180) if invert else printable
 oriented=oriented.translate((0,0,-oriented.BoundingBox().zmin));path=OUT/'STL'/f'{name}.stl'
 cq.exporters.export(oriented,str(path),tolerance=.035,angularTolerance=.09)
 mesh=trimesh.load_mesh(path,process=True);mask=mesh.nondegenerate_faces(height=1e-6)
 if not mask.all():mesh.update_faces(mask);mesh.remove_unreferenced_vertices();mesh.export(path)
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,(name,'Invalid STL')
 b=shape.BoundingBox();manifest.append({'name':name,'valid':shape.isValid(),'solids':len(shape.Solids()),'volume_mm3':shape.Volume(),'step_serialization_volume_difference_mm3':serialization_delta,'step_serialization_symmetric_difference_mm3':serialization_difference,'print_mesh_source':'Distributed STEP','file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds_mm':[[getattr(b,k+'min') for k in 'xyz'],[getattr(b,k+'max') for k in 'xyz']]})
colors={'Stationary_Base':(.34,.4,.45),'Bottom_Tray':(.25,.3,.34),'Inner_Race_Nut':(.92,.68,.28),'Outer_Race_Retainer':(.12,.38,.48),bearing_name:(.7,.73,.77),'PCB':(.17,.44,.3)}
meshes=[];seen_meshes=set()
for style,cap in caps.items():
 for state in ['Assembled','Exploded']:
  if style not in assembly_styles and state!='Assembled':continue
  assembly=cq.Assembly(name=style+'_'+state)
  values={**stationary,**moving,'Cap_'+style:cap}
  for name,shape in values.items():
   z=0
   if state=='Exploded':z={'MagSafe_Ring':-10,'Bottom_Tray':-4,'Inner_Race_Nut':36,bearing_name:22,'Outer_Race_Retainer':6,'Cap_'+style:50,'Magnet':45,'PCB':5,'PCB_Fasteners':10,'Cap_Retainer_Screws':50}.get(name,5 if name.startswith('Electronic_') else 0)
   posed=shape.translate((0,0,z));color=(.12,.47,.58) if name.startswith('Cap_') else electronic_colors.get(name,colors.get(name,(.58,.6,.63)))
   detailed=bearing_parts if name.startswith('Bearing_') else (cell_parts if name=='Cell' else None)
   if detailed:
    detail=cq.Assembly(name=name)
    for i,(label,part,part_color,finish) in enumerate(detailed):detail.add(part,name=f'Part_{i}',color=cq.Color(*part_color))
    assembly.add(detail,name=name,loc=cq.Location(cq.Vector(0,0,z)))
   else:assembly.add(posed,name=name,color=cq.Color(*color))
   if state=='Assembled' and name not in seen_meshes:
    parts=bearing_parts if name.startswith('Bearing_') else (cell_parts if name=='Cell' else [(name,posed,color,'nylon' if name=='PCB_Fasteners' else ('steel' if name in ['Cap_Retainer_Screws','MagSafe_Ring','Magnet'] else 'plastic'))])
    vertices=[];faces=[];groups=[]
    for label,part,part_color,finish in parts:
     if name in physical:part=cq.importers.importStep(str(OUT/'STEP'/f'{name}.step')).val()
     vv,ff=part.tessellate(.035,.13);vv=[list(v.toTuple()) for v in vv]
     start=len(faces);offset=len(vertices);vertices.extend(vv);faces.extend([[i+offset for i in f] for f in ff])
     groups.append({'label':label,'first_face':start,'face_count':len(ff),'color':part_color,'finish':finish})
    meshes.append({'style':style,'name':name,'nativeElectronic':name.startswith('Electronic_'),'color':color,'vertices':vertices,'faces':faces,'groups':groups});seen_meshes.add(name)
  if style in assembly_styles:assembly.save(str(OUT/'Assemblies'/f'{style}_{state}.step'))
report={'status':'Nominal rotation-only CAD pilot; physical qualification required','physical_tested':False,'manufacturing_qualified':False,'parameters':P,'printed_parts':manifest,'rotation_checks':rotation,'continuous_rotation_deg':360,'rotation_method':'Axisymmetric stepped rotor and exterior grip keepout, supplemented by24 sampled final-hub angles','base_diameter_mm':58,'overall_height_mm':P['overall_height'],'height_increase_mm':P['overall_height']-15.2,'pcb_midplane_z_mm':mid,'pcb_screws':len(pcb_fast),'pcb_support_posts':4,'pcb_screw_indices':pcb_screw_indices,'flexible_printed_latches':0,'return_springs':0,'press_travel_mm':0,'cap_retainer_screws':3,'jst_swept_clearance_mm':jst_gap,'sensor_gap_mm':1.8,'separate_encoder_spacers':0,'encoder_stop_z_mm':magnet_top,'handled_parts_per_unit_excluding_adhesive_and_shims':12+len(pcb_fast),'screw_driving_operations':3+len(pcb_fast),'finished_cap_retainer_and_screw_clearance_checks':len(caps),'assembly_step_styles':assembly_styles,'references':{'rotation':'https://ploopyco.github.io/knob/assembly-instructions/','bearing':'https://ploopyco.github.io/knob/appendices/hardware/'},'scope':'Rotation only; SW1, R5 and C17 removed. SWD hardware reset retained. Pilot firmware is included separately.','model_detail':{'bearing':'21 balls (AST6808 reference), grooved/chamfered races, cage and shields; representative internals','electronics':'All27 fitted supplier STEP models at native poses'},'physical_checks_required':['Printed bearing shaft/housing coupon fit and support removal','Bearing seating/pull-off retention, rotational drag, PETG creep and PCB screw strength','Magnet retention, Hall calibration, phone attachment and RF','Rotation/removal endurance, assembly timing and firmware']}
if pushfit:
 report.update({'cap_retention':P['cap_retention'],'cap_retainer_screws':0,'handled_parts_per_unit_excluding_adhesive_and_shims':9,'screw_driving_operations':len(pcb_fast),'finished_cap_retainer_and_screw_clearance_checks':0,'product_rigid_parts':2,'separate_inner_race_nuts':0,'separate_outer_race_retainers':0})
report['bearing_designation']=B['designation']
report['pcb_retention_qualification']='Two opposite screws on four rigid posts; physical board deflection and retention untested'
report['battery']={'type':'Primary lithium CR2032','voltage_v':3,'diameter_mm':20,'thickness_mm':3.2,'reference_nominal_capacity_mah':225,'larger_cell_assessed':'CR2450 24.5x5 mm, 620mAh; complete-holder trial interferes with PCB posts; not a drop-in replacement','fit_study':'mechanical/BATTERY_AND_ASSEMBLY_REVIEW.md'}
report['battery']={**P['battery'],'physical_qualified':False}
report['attachment_ring']={'supplier':R['supplier'],'purchased_assemblies':1,'individual_magnet_pockets':0,'separate_backing_rings':0,'nominal_dimensions_mm':[R['outside_mm'],R['inside_mm'],R['thickness_mm']],'phone_face_setback_mm':ring_z-.2,'radial_clearance_mm':R['radial_clearance_mm'],'bondline_mm':R['bondline_mm'],'roof_thickness_mm':3.9-seat_z,'outer_wall_mm':28.05-ro-R['radial_clearance_mm'],'physical_qualified':False,'separate_trays':0,'separate_tray_bonds':0,'display_note':'Purchased segmented ring reference; confirm supplier dimensions and working face.'}
(OUT/'Validation'/'geometry.json').write_text(json.dumps(report,indent=2)+'\n');(OUT/'Validation'/'scene_meshes.json').write_text(json.dumps(meshes))
if set(styles)==set(P['cap_styles']):
 from sync_checked_exports import sync_checked_exports
 sync_checked_exports(HERE,OUT)
print(json.dumps({'printed_parts':len(manifest),'height_mm':P['overall_height'],'base_diameter_mm':58,'styles':styles,'output':str(OUT)},indent=2),flush=True)
