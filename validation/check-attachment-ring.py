"""Check the actual single-ring seat and preserve unrelated printed hardware."""
from pathlib import Path
import hashlib,json,subprocess,sys
import cadquery as cq
import numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'mechanical'))
from hardware_models import magsafe_ring
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text());r=p['attachment_ring']
old=json.loads(subprocess.check_output(['git','show','7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84:mechanical/enclosure-parameters.json'],cwd=root))
changed_fields={'design','publication','magnet_installation','encoder_stop','pcb_mount','integrated_base','attachment_ring','pilot_batch','cap_retainer_joint','print_process','inner_race_nut'}
assert {k:v for k,v in p.items() if k not in changed_fields}=={k:v for k,v in old.items() if k not in changed_fields},'Unrelated mechanical parameters changed'
assert {k:v for k,v in p['pcb_mount'].items() if k!='screw_indices'}==old['pcb_mount']
assert {k:v for k,v in r.items() if k!='mounting'}=={k:v for k,v in old['attachment_ring'].items() if k!='mounting'},'Ring fit or supplier envelope changed'
assert {k:v for k,v in p['inner_race_nut'].items() if k!='tool_notch_depth_mm'}==old['inner_race_nut']
assert p['inner_race_nut']['tool_notch_depth_mm']==.6
assert [p['base_diameter'],p['overall_height'],p['button_travel']]==[58,17.2,.8]
assert [r['outside_mm'],r['inside_mm'],r['thickness_mm']]==[54,45.8,1.9]
base=cq.importers.importStep(str(root/'mechanical/STEP_Parts/Stationary_Base.step')).val()
assert not (root/'mechanical/STEP_Parts/Bottom_Tray.step').exists()
ring=magsafe_ring(r)
ri=r['inside_mm']/2;ro=r['outside_mm']/2;z=r['phone_face_z_mm'];top=z+r['thickness_mm'];seat=top+r['bondline_mm']
def annulus(a,b,c,h):return cq.Workplane('XY').workplane(offset=c).circle(b).circle(a).extrude(h).val()
envelope=annulus(ri,ro,z,r['thickness_mm'])
assert envelope.intersect(base).Volume()<.002,'ring/base'
assert abs(ring.BoundingBox().zmin-z)<1e-6 and abs(ring.BoundingBox().zmax-top)<1e-6
# Check the entire annulus, including all representative segment grooves.
void=annulus(ri-r['radial_clearance_mm']+.001,ro+r['radial_clearance_mm']-.001,.201,seat-.202)
assert base.intersect(void).Volume()<.002,'Pocket intrudes into the purchased-ring clearance'
roof=annulus(ri-r['radial_clearance_mm'],ro+r['radial_clearance_mm'],seat+.001,3.9-seat-.002)
assert abs(base.intersect(roof).Volume()-roof.Volume())<.002,'Discontinuous or thin bonding roof'
assert 3.9-seat>=1.5-1e-6 and 28.05-ro-r['radial_clearance_mm']>=.9-1e-6
changed=[];unchanged=[]
for f in sorted((root/'mechanical/Print_STL').glob('*.stl')):
 previous=subprocess.check_output(['git','show',f'7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84:{f.relative_to(root)}'],cwd=root)
 (unchanged if f.read_bytes()==previous else changed).append(f.name)
assert set(changed)=={'Stationary_Base.stl','Outer_Race_Retainer.stl','Inner_Race_Nut.stl',*{'Cap_'+style+'.stl' for style in p['cap_styles']}},changed
manifest=json.loads((root/'mechanical/Circuit_Models/manifest.json').read_text())
assert manifest['modelsPerSelectedStyle']==14 and manifest['totalAssets']==24
assert 'MagSafe_Ring.glb' in manifest['modelSha256']
assert not any(n.startswith(('Backing_Ring','Attachment_Magnets')) for n in manifest['modelSha256'])
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
electronics=[row for row in rows if row.get('nativeElectronic')]
assert len(electronics)==31
clearances=[]
for row in [*electronics,next(row for row in rows if row['name']=='Cell')]:
 v=np.asarray(row['vertices']);low=v.min(axis=0);high=v.max(axis=0)
 if row['name']=='Cell':
  # A square AABB invents material at the corners outside a round coin cell
  # and falsely intersects the PCB support posts. Use a proven enclosing
  # cylinder instead; every actual cell vertex must remain inside it.
  assert (np.linalg.norm(v[:,:2],axis=1)<=10+1e-6).all()
  assert low[2]>=3.4-1e-6 and high[2]<=6.6+1e-6
  component=cq.Solid.makeCylinder(10,3.2,cq.Vector(0,0,3.4))
 else:component=cq.Workplane('XY').box(*np.maximum(high-low,.001)).val().translate(tuple((low+high)/2))
 for label,part in [('Stationary_Base',base),('MagSafe_Ring',envelope)]:
  bounds=part.BoundingBox()
  if high[2]<=bounds.zmin or low[2]>=bounds.zmax:volume=0.
  else:
   volume=part.intersect(component).Volume()
  assert volume<.003,(label,row['name'],volume)
 clearances.append({'component':row['name'],'minimum_z_mm':float(low[2]),'checked_envelope':'Proven enclosing CR2032 cylinder' if row['name']=='Cell' else 'Fitted mesh AABB','rigid_intersections':0})
report={'passed':True,'physical_tested':False,'source_reference_commit':'157a36b62ba084e0a812fcc93dbe21a016904da8','purchased_ring_assemblies':1,'individual_magnet_pockets':0,'separate_backing_rings':0,'nominal_ring_mm':[54,45.8,1.9],'pocket_mm':[2*(ro+r['radial_clearance_mm']),2*(ri-r['radial_clearance_mm'])],'radial_clearance_mm':r['radial_clearance_mm'],'bondline_mm':r['bondline_mm'],'face_setback_mm':z-.2,'roof_mm':3.9-seat,'outer_wall_mm':28.05-ro-r['radial_clearance_mm'],'changed_printed_files':changed,'unchanged_printed_files':unchanged,'envelope_mm':{'diameter':58,'height':17.2,'press':.8},'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'mechanical/enclosure-parameters.json',root/'mechanical/STEP_Parts/Stationary_Base.step',root/'mechanical/Circuit_Models/MagSafe_Ring.glb']},'unqualified':['Supplier sample dimensions and working-face polarity','Ring adhesive peel/shear retention and printed roof strength','Hall error, RF and phone/case compatibility']}
report['source_reference_commit']='7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84'
report['fitted_electronic_components_checked']=31
report['fixed_hardware_clearances']=clearances
report['source_scene_sha256']=hashlib.sha256((root/'mechanical/export/Validation/scene_meshes.json').read_bytes()).hexdigest()
(root/'validation/attachment-ring-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Pass: purchased-ring seat and consolidated base checked; 31 electronics clear the base/ring; encoder pose unchanged')
