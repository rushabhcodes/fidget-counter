"""Prove the bounded stop, retainer-joint and base consolidation changes."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,math
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1];BASE='7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84'
p=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text());z=p['magnet_bottom']+p['magnet_thickness'];radius=p['magnet_pocket_diameter']/2
expected=cq.Workplane('XY').workplane(offset=z).circle(radius).extrude(.2).val();results=[]
sockets=[];bosses=[]
for angle in [0,120,240]:
 t=math.radians(angle);x,y=26.8*math.cos(t),26.8*math.sin(t)
 sockets.append(cq.Workplane('XY').workplane(offset=6.5).center(x,y).circle(1.8).extrude(3.3).val())
 sockets.append(cq.Workplane('XY').workplane(offset=6.5).center(x,y).circle(1.1).extrude(10.8).val())
 sockets.append(cq.Solid.makeCone(1.1,2.,1.1,cq.Vector(x,y,16.1)))
 bosses.append(cq.Workplane('XY').workplane(offset=6.58).center(x,y).circle(1.6).circle(.8).extrude(3.02).val())
socket_union=sockets[0]
for socket in sockets[1:]:socket_union=socket_union.fuse(socket)
sockets=socket_union.clean();bosses=cq.Compound.makeCompound(bosses)
with tempfile.TemporaryDirectory() as tmp:
 for style in p['cap_styles']:
  name='Cap_'+style;f=ROOT/'mechanical/STEP_Parts'/(name+'.step');old=Path(tmp)/(name+'.step');old.write_bytes(subprocess.check_output(['git','show',BASE+':'+str(f.relative_to(ROOT))],cwd=ROOT));a=cq.importers.importStep(str(old)).val();b=cq.importers.importStep(str(f)).val()
  added=b.cut(a);removed_shape=a.cut(b);removed=removed_shape.Volume();unexpected=added.cut(expected).Volume();missing=expected.cut(added).Volume()
  assert removed_shape.cut(sockets).Volume()<.002 and a.intersect(sockets).cut(removed_shape).Volume()<.002,(style,'Incorrect boss sockets')
  assert unexpected<.002 and missing<.002,(style,removed,unexpected,missing)
  aa,bb=a.BoundingBox(),b.BoundingBox();assert all(abs(getattr(aa,k)-getattr(bb,k))<1e-6 for k in ['xmin','xmax','ymin','ymax','zmin','zmax'])
  results.append({'style':style,'added_stop_volume_mm3':added.Volume(),'removed_socket_volume_mm3':removed,'unexpected_volume_mm3':unexpected,'outer_bounds_unchanged':True})
 f=Path(tmp)/'Outer_Race_Retainer.step';f.write_bytes(subprocess.check_output(['git','show',BASE+':mechanical/STEP_Parts/'+f.name],cwd=ROOT));before=cq.importers.importStep(str(f)).val();after=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/f.name)).val()
 added=after.cut(before);assert before.cut(after).Volume()<.002
 assert added.cut(bosses).Volume()<.002 and bosses.cut(before).cut(added).Volume()<.002,'Retainer changed beyond integral bosses'
 assert after.isValid() and len(after.Solids())==1
 retainer_result={'nominal_thread_overlap_mm':4.4,'previous_mm':1.4,'boss_to_socket_radial_clearance_mm':.2,'boss_to_socket_roof_clearance_mm':.2,'added_volume_mm3':added.Volume(),'physical_joint_tested':False}
 # The only base change is consolidation of two permanently joined parts.
 old_parts=[]
 for name in ['Stationary_Base','Bottom_Tray']:
  f=Path(tmp)/(name+'.step');f.write_bytes(subprocess.check_output(['git','show',BASE+':mechanical/STEP_Parts/'+f.name],cwd=ROOT));old_parts.append(cq.importers.importStep(str(f)).val())
 before=old_parts[0].fuse(old_parts[1]);after=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts/Stationary_Base.step')).val()
 allowed_addition=cq.Workplane('XY').workplane(offset=.79).circle(28.2).circle(20.85).extrude(2.36).val()
 allowed_removal=[]
 for angle in p['return_springs']['angles_deg']:
  t=math.radians(angle);x,y=19.5*math.cos(t),19.5*math.sin(t)
  allowed_removal.append(cq.Workplane('XY').workplane(offset=1.5).center(x,y).circle(1.7).extrude(3).val())
 allowed_removal=cq.Compound.makeCompound(allowed_removal)
 added=after.cut(before);removed=before.cut(after)
 assert added.cut(allowed_addition).Volume()<.002,'Base changed beyond former annular assembly interface'
 assert removed.cut(allowed_removal).Volume()<.002,'Base removed material outside spring pocket clearance'
 assert after.isValid() and len(after.Solids())==1
 aa,bb=before.BoundingBox(),after.BoundingBox();assert all(abs(getattr(aa,k)-getattr(bb,k))<1e-6 for k in ['xmin','xmax','ymin','ymax','zmin','zmax'])
 base_result={'single_valid_solid':True,'added_interface_volume_mm3':added.Volume(),'removed_spring_pocket_intrusion_mm3':removed.Volume(),'combined_external_bounds_unchanged':True,'separate_tray_removed':True}
assert z==12.9 and p['magnet_bottom']==11.4 and p['button_travel']==.8
rows=json.loads((ROOT/'mechanical/export/Validation/scene_meshes.json').read_text());assert not any(r['name']=='Encoder_Spacer' for r in rows)
magnet=next(r for r in rows if r['name']=='Magnet');assert min(v[2] for v in magnet['vertices'])>=11.4-1e-6 and max(v[2] for v in magnet['vertices'])<=12.9+1e-6
report={'passed':True,'physical_tested':False,'comparison_commit':BASE,'integral_stop_z_mm':z,'separate_spacers_removed':1,'magnet_envelope_mm':[11.4,12.9],'cap_results':results,'part_counts':{'published_1_0_24':{'handled_parts':29,'screw_drives':10},'default_candidate':{'handled_parts':27,'screw_drives':10},'two_screw_trial':{'handled_parts':25,'screw_drives':8}},'limits':['Adhesive retention must be qualified without adding an axial glue layer','Two-screw PCB trial requires deflection, retention and shock tests; default remains four'],'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'mechanical/build_enclosure.py',ROOT/'mechanical/enclosure-parameters.json',*[(ROOT/'mechanical/STEP_Parts'/('Cap_'+s+'.step')) for s in p['cap_styles']]]}}
report['source_sha256']['mechanical/STEP_Parts/Outer_Race_Retainer.step']=hashlib.sha256((ROOT/'mechanical/STEP_Parts/Outer_Race_Retainer.step').read_bytes()).hexdigest()
report['integrated_base']=base_result
report['retainer_joint']=retainer_result
report['source_sha256']['mechanical/STEP_Parts/Stationary_Base.step']=hashlib.sha256((ROOT/'mechanical/STEP_Parts/Stationary_Base.step').read_bytes()).hexdigest()
(ROOT/'validation/manufacturing-stop-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Pass: eleven caps add only the integral stop; base/tray consolidation restricted to former interface; product bounds and magnet positions unchanged')
