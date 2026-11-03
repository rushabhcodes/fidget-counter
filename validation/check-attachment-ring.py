"""Check the actual single-ring seat and preserve unrelated printed hardware."""
from pathlib import Path
import hashlib,json,subprocess,sys
import cadquery as cq
import numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'mechanical'))
from hardware_models import magsafe_ring
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text());r=p['attachment_ring']
old=json.loads(subprocess.check_output(['git','show','7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84:mechanical/enclosure-parameters.json'],cwd=root))
assert p['attachment_ring']==old['attachment_ring'] or {k:v for k,v in p['attachment_ring'].items() if k!='mounting'}=={k:v for k,v in old['attachment_ring'].items() if k!='mounting'}
assert p['base_diameter']==58
assert p['overall_height']==(16.6 if p.get('cap_compaction') else 17.2)
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
manifest=json.loads((root/'mechanical/Circuit_Models/manifest.json').read_text())
pushfit=p.get('cap_retention',{}).get('mode')=='push_fit'
assert manifest['modelsPerSelectedStyle']==(7 if pushfit else 10) and manifest['totalAssets']==(17 if pushfit else 20)
assert 'MagSafe_Ring.glb' in manifest['modelSha256']
assert not any(n.startswith(('Backing_Ring','Attachment_Magnets')) for n in manifest['modelSha256'])
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
electronics=[row for row in rows if row.get('nativeElectronic')]
assert len(electronics)==28
clearances=[]
for row in [*electronics,next(row for row in rows if row['name']=='Cell')]:
 v=np.asarray(row['vertices']);low=v.min(axis=0);high=v.max(axis=0)
 if row['name']=='Cell':
  # A square AABB invents material at the corners outside a round coin cell
  # and falsely intersects the PCB support posts. Use a proven enclosing
  # cylinder instead; every actual cell vertex must remain inside it.
  cell=p['battery'];center=np.asarray(cell['cell_center_mm']);rad=cell['diameter_mm']/2;bottom=cell['cell_bottom_z_mm']
  assert (np.linalg.norm(v[:,:2]-center,axis=1)<=rad+1e-6).all()
  assert low[2]>=bottom-1e-6 and high[2]<=bottom+cell['thickness_mm']+1e-6
  component=cq.Solid.makeCylinder(rad,cell['thickness_mm'],cq.Vector(*center,bottom))
 else:component=cq.Workplane('XY').box(*np.maximum(high-low,.001)).val().translate(tuple((low+high)/2))
 for label,part in [('Stationary_Base',base),('MagSafe_Ring',envelope)]:
  bounds=part.BoundingBox()
  if high[2]<=bounds.zmin or low[2]>=bounds.zmax:volume=0.
  else:
   volume=part.intersect(component).Volume()
  if volume>=.003 and row['name']=='Electronic_BT1':
   c=json.loads((root/'dist/index/circuit.json').read_text());sid=next(e['source_component_id']for e in c if e['type']=='source_component'and e['name']=='BT1');cad=next(e for e in c if e['type']=='cad_component'and e['source_component_id']==sid);org=cad['model_origin_position'];rot=cad['rotation'];pos=cad['position'];actual=cq.importers.importStep(str(root/cad['model_step_url'])).val().translate(tuple(-org.get(k,0)for k in'xyz'))
   for axis,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
    if rot.get(axis,0):actual=actual.rotate((0,0,0),vec,rot[axis])
   actual=actual.translate((pos['x'],pos['y'],pos['z']+p['pcb_bottom']+p['pcb_thickness']/2));volume=part.intersect(actual).Volume()
  assert volume<.003,(label,row['name'],volume)
 clearances.append({'component':row['name'],'minimum_z_mm':float(low[2]),'checked_envelope':'Proven enclosing '+p['battery']['standard']+' cylinder' if row['name']=='Cell' else ('AABB broad phase; exact supplier STEP narrow phase'if row['name']=='Electronic_BT1'else'Fitted mesh AABB'),'rigid_intersections':0})
report={'passed':True,'physical_tested':False,'source_reference_commit':'157a36b62ba084e0a812fcc93dbe21a016904da8','purchased_ring_assemblies':1,'individual_magnet_pockets':0,'separate_backing_rings':0,'nominal_ring_mm':[54,45.8,1.9],'pocket_mm':[2*(ro+r['radial_clearance_mm']),2*(ri-r['radial_clearance_mm'])],'radial_clearance_mm':r['radial_clearance_mm'],'bondline_mm':r['bondline_mm'],'face_setback_mm':z-.2,'roof_mm':3.9-seat,'outer_wall_mm':28.05-ro-r['radial_clearance_mm'],'envelope_mm':{'diameter':58,'height':p['overall_height'],'press':0},'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'mechanical/enclosure-parameters.json',root/'mechanical/STEP_Parts/Stationary_Base.step',root/'mechanical/Circuit_Models/MagSafe_Ring.glb']},'unqualified':['Supplier sample dimensions and working-face polarity','Ring adhesive peel/shear retention and printed roof strength','Hall error, RF and phone/case compatibility']}
report['source_reference_commit']='7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84'
report['fitted_electronic_components_checked']=28
report['fixed_hardware_clearances']=clearances
report['source_scene_sha256']=hashlib.sha256((root/'mechanical/export/Validation/scene_meshes.json').read_bytes()).hexdigest()
(root/'validation/attachment-ring-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Pass: purchased-ring seat unchanged;28 electronics and selected cell clear the base/ring; encoder relative sensor gap checked separately')
