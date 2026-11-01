"""Check the actual single-ring seat and preserve unrelated printed hardware."""
from pathlib import Path
import hashlib,json,subprocess,sys
import cadquery as cq
import numpy as np
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'mechanical'))
from hardware_models import magsafe_ring
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text());r=p['attachment_ring']
old=json.loads(subprocess.check_output(['git','show','157a36b62ba084e0a812fcc93dbe21a016904da8:mechanical/enclosure-parameters.json'],cwd=root))
assert {k:v for k,v in p.items() if k not in ['attachment_ring','publication']}=={k:v for k,v in old.items() if k!='publication'},'Unrelated mechanical parameters changed'
assert [p['base_diameter'],p['overall_height'],p['button_travel']]==[58,17.2,.8]
assert [r['outside_mm'],r['inside_mm'],r['thickness_mm']]==[54,45.8,1.9]
base,tray=[cq.importers.importStep(str(root/'mechanical/STEP_Parts'/f'{n}.step')).val() for n in ['Stationary_Base','Bottom_Tray']]
ring=magsafe_ring(r)
ri=r['inside_mm']/2;ro=r['outside_mm']/2;z=r['phone_face_z_mm'];top=z+r['thickness_mm'];seat=top+r['bondline_mm']
def annulus(a,b,c,h):return cq.Workplane('XY').workplane(offset=c).circle(b).circle(a).extrude(h).val()
envelope=annulus(ri,ro,z,r['thickness_mm'])
for label,left,right in [('tray/base',tray,base),('ring/tray',envelope,tray),('ring/base',envelope,base)]:assert left.intersect(right).Volume()<.002,label
assert abs(ring.BoundingBox().zmin-z)<1e-6 and abs(ring.BoundingBox().zmax-top)<1e-6
# Check the entire annulus, including all representative segment grooves.
void=annulus(ri-r['radial_clearance_mm']+.001,ro+r['radial_clearance_mm']-.001,.201,seat-.202)
assert tray.intersect(void).Volume()<.002,'Pocket intrudes into the purchased-ring clearance'
roof=annulus(ri-r['radial_clearance_mm'],ro+r['radial_clearance_mm'],seat+.001,3.-seat-.002)
assert abs(tray.intersect(roof).Volume()-roof.Volume())<.002,'Discontinuous or thin bonding roof'
assert 3.-seat>=.6-1e-6 and 28.05-ro-r['radial_clearance_mm']>=.9-1e-6
changed=[];unchanged=[]
for f in sorted((root/'mechanical/Print_STL').glob('*.stl')):
 previous=subprocess.check_output(['git','show',f'157a36b62ba084e0a812fcc93dbe21a016904da8:{f.relative_to(root)}'],cwd=root)
 (unchanged if f.read_bytes()==previous else changed).append(f.name)
assert set(changed)=={'Stationary_Base.stl','Bottom_Tray.stl'},changed
manifest=json.loads((root/'mechanical/Circuit_Models/manifest.json').read_text())
assert manifest['modelsPerSelectedStyle']==16 and manifest['totalAssets']==26
assert 'MagSafe_Ring.glb' in manifest['modelSha256']
assert not any(n.startswith(('Backing_Ring','Attachment_Magnets')) for n in manifest['modelSha256'])
rows=json.loads((root/'mechanical/export/Validation/scene_meshes.json').read_text())
electronics=[row for row in rows if row.get('nativeElectronic')]
assert len(electronics)==31
clearances=[]
for row in [*electronics,next(row for row in rows if row['name']=='Cell')]:
 v=np.asarray(row['vertices']);low=v.min(axis=0);high=v.max(axis=0)
 for label,part in [('Bottom_Tray',tray),('MagSafe_Ring',envelope)]:
  bounds=part.BoundingBox()
  if high[2]<=bounds.zmin or low[2]>=bounds.zmax:volume=0.
  else:
   component=cq.Workplane('XY').box(*np.maximum(high-low,.001)).val().translate(tuple((low+high)/2))
   volume=part.intersect(component).Volume()
  assert volume<.003,(label,row['name'],volume)
 clearances.append({'component':row['name'],'minimum_z_mm':float(low[2]),'tray_vertical_gap_mm':float(low[2]-tray.BoundingBox().zmax),'rigid_intersections':0})
report={'passed':True,'physical_tested':False,'source_reference_commit':'157a36b62ba084e0a812fcc93dbe21a016904da8','purchased_ring_assemblies':1,'individual_magnet_pockets':0,'separate_backing_rings':0,'nominal_ring_mm':[54,45.8,1.9],'pocket_mm':[2*(ro+r['radial_clearance_mm']),2*(ri-r['radial_clearance_mm'])],'radial_clearance_mm':r['radial_clearance_mm'],'bondline_mm':r['bondline_mm'],'face_setback_mm':z-.2,'roof_mm':3.-seat,'outer_wall_mm':28.05-ro-r['radial_clearance_mm'],'changed_printed_files':changed,'unchanged_printed_files':unchanged,'envelope_mm':{'diameter':58,'height':17.2,'press':.8},'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'mechanical/enclosure-parameters.json',root/'mechanical/STEP_Parts/Stationary_Base.step',root/'mechanical/STEP_Parts/Bottom_Tray.step',root/'mechanical/Circuit_Models/MagSafe_Ring.glb']},'unqualified':['Supplier sample dimensions and working-face polarity','Adhesive peel/shear retention and tray bond','Hall error, RF and phone/case compatibility']}
report['fitted_electronic_components_checked']=31
report['fixed_hardware_clearances']=clearances
report['source_scene_sha256']=hashlib.sha256((root/'mechanical/export/Validation/scene_meshes.json').read_bytes()).hexdigest()
(root/'validation/attachment-ring-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('Pass: one ring, continuous roof and clear seat; exactly two printed parts changed; envelope and encoder unchanged')
