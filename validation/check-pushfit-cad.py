"""Fail-closed geometry review for the two-part Ploopy-inspired push-fit pilot."""
from pathlib import Path
import hashlib,json,math,subprocess,sys
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'mechanical'))
from hardware_models import bearing_6808
BASE='a7c29c470c439e6f4e35314b9c68bba5c8d8c100'
P=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text())
oldP=json.loads(subprocess.check_output(['git','show',BASE+':mechanical/enclosure-parameters.json'],cwd=ROOT))
assert P['cap_retention']['mode']=='push_fit'and P['cap_retention']['nominal_diametral_interference_mm']==.05
assert P['cap_retention']['physical_qualified']is False
expected={**oldP,'cap_retention':P['cap_retention'],'bearing':{**oldP['bearing'],'shaft_diameter_mm':40.05,'housing_diameter_mm':51.95,'inner_shoulder_outer_radius_mm':21.0}}
assert P==expected,'Unrelated mechanical parameters changed'
scratch=ROOT/'work/pushfit-baseline';scratch.mkdir(parents=True,exist_ok=True)
def before(name):
 f=scratch/(name+'.step');f.write_bytes(subprocess.check_output(['git','show',BASE+':mechanical/STEP_Parts/'+f.name],cwd=ROOT));return cq.importers.importStep(str(f)).val()
def current(name):return cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/(name+'.step'))).val()
def disk(r,z,h,x=0,y=0):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def ring(ri,ro,z,h):return disk(ro,z,h).cut(disk(ri,z-.001,h+.002))
def bounded(old,new,masks,label):
 added=new.cut(old);removed=old.cut(new);va,vr=added.Volume(),removed.Volume()
 for mask in masks:
  if added.Solids():added=added.cut(mask)
  if removed.Solids():removed=removed.cut(mask)
 assert added.Volume()<.003 and removed.Volume()<.003,(label,'Unrelated geometry changed',added.Volume(),removed.Volume())
 return {'added_volume_mm3':va,'removed_volume_mm3':vr,'unexplained_added_mm3':added.Volume(),'unexplained_removed_mm3':removed.Volume()}
def probe(shape,points,want,label):
 assert all(shape.isInside(cq.Vector(*p),1e-6)==want for p in points),label
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
base=current('Stationary_Base');baseOld=before('Stationary_Base')
baseMasks=[ring(19.849,20.026,6.099,7.002),ring(20.649,21.001,4.999,1.102),disk(20.001,13.099,2.502)]
baseDelta=bounded(baseOld,base,baseMasks,'Base shaft, contact land and obsolete neck')
for a in range(0,360,15):
 probe(base,[(*polar(20.02,a),z)for z in [6.5,9.,12.8]],True,'Missing40.05mm shaft')
 probe(base,[(*polar(20.04,a),z)for z in [6.5,9.,12.8]],False,'Oversize shaft')
 probe(base,[(*polar(18.64,a),z)for z in [6.5,9.,12.8]],False,'PCB passage obstructed')
 probe(base,[(*polar(20.95,a),5.5)],True,'Missing42mm inner-race support land')
 probe(base,[(*polar(r,a),z)for r in [18.8,19.5,20.5,21.5]for z in [13.2,14.5,15.5]],False,'Obsolete neck/nut geometry remains')
capMasks=[ring(25.974,26.101,6.099,7.002)]
for a in [0,120,240]:capMasks.append(disk(3.001,6.099,11.102,*polar(27.8,a)))
bearing,inner,outer,shields,_=bearing_6808(6.1)
fit=[];caps=[]
for style in P['cap_styles']:
 name='Cap_'+style;cap=current(name);delta=bounded(before(name),cap,capMasks,name)
 assert abs(cap.BoundingBox().zmax-17.2)<1e-6
 assert max(abs(getattr(cap.BoundingBox(),v))for v in ['xmin','xmax','ymin','ymax'])<=30.80001
 for a in range(0,360,30):
  probe(cap,[(*polar(25.97,a),z)for z in [6.5,9.,12.8]],False,'Housing bore obstructed')
  probe(cap,[(*polar(25.98,a),z)for z in [6.5,9.,12.8]],True,'Missing51.95mm housing land')
  probe(cap,[(*polar(2.45,a),15.39)],False,'Encoder pocket obstructed')
  probe(cap,[(*polar(2.45,a),15.41)],True,'Encoder seated-height stop changed')
  probe(cap,[(*polar(10,a),16.0),(*polar(16,a),16.0)],True,'Cap deck missing')
 # Former top counterbores may not survive inside otherwise continuous material.
 for a in [0,120,240]:
  x,y=polar(27.8,a)
  around=[(x+1.5*math.cos(t),y+1.5*math.sin(t),17.15)for t in [0,math.pi/2,math.pi,3*math.pi/2]]
  if all(cap.isInside(cq.Vector(*v),1e-6)for v in around):probe(cap,[(x,y,17.15)],True,'Former top fastener hole remains')
 overlap=cap.intersect(outer);allow=ring(25.974,26.001,6.099,7.002)
 assert overlap.Volume()>1 and overlap.cut(allow).Volume()<.003,'Unexpected outer-race interference'
 assert cap.intersect(inner).Volume()<.003 and cap.intersect(base).Volume()<.003
 fit.append({'style':style,'outer_race_intended_interference_volume_mm3':overlap.Volume(),'unexpected_interference_mm3':overlap.cut(allow).Volume()})
 caps.append({'name':name,**delta})
overlap=base.intersect(inner);allow=ring(19.999,20.026,6.099,7.002)
assert overlap.Volume()>1 and overlap.cut(allow).Volume()<.003
assert base.intersect(outer).Volume()<.003
names=['Stationary_Base',*['Cap_'+s for s in P['cap_styles']]]
for name in names:
 shape=current(name);mesh=trimesh.load_mesh(ROOT/'mechanical/Print_STL'/(name+'.stl'),process=True)
 assert shape.isValid()and len(shape.Solids())==1 and len(shape.Shells())==1,name
 assert mesh.is_volume and mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1,name
for name in ['Inner_Race_Nut','Outer_Race_Retainer']:assert not(ROOT/'mechanical/STEP_Parts'/(name+'.step')).exists(),'Obsolete product solid remains'
g=json.loads((ROOT/'mechanical/enclosure-validation.json').read_text());assert g['parameters']==P
assert len(g['printed_parts'])==12 and g['product_rigid_parts']==2 and g['pcb_screws']==2
assert g['cap_retainer_screws']==0 and g['handled_parts_per_unit_excluding_adhesive_and_shims']==9
assert len(g['rotation_checks'])==24 and all(x['rigid_collisions']==0 for x in g['rotation_checks'])
negative=[]
for label,bad in [('unrelated_outer_addition',base.fuse(disk(.5,17.2,.5,5,5))),('unrelated_floor_cut',base.cut(disk(.5,.2,1.,5,5)))]:
 try:bounded(baseOld,bad,baseMasks,label)
 except AssertionError:negative.append(label)
 else:raise AssertionError('Bounded guard accepted '+label)
paths=[Path(__file__),ROOT/'mechanical/build_enclosure.py',ROOT/'mechanical/grip_profiles.py',ROOT/'mechanical/enclosure-parameters.json',ROOT/'mechanical/enclosure-validation.json',*sorted((ROOT/'mechanical/STEP_Parts').glob('*.step')),*sorted((ROOT/'mechanical/Print_STL').glob('*.stl'))]
report={'passed':True,'physical_tested':False,'manufacturing_qualified':False,'comparison_commit':BASE,'retention':'Calibrated friction push fits; no positive axial lock','base_result':baseDelta,'cap_results':caps,'inner_race_intended_interference_volume_mm3':overlap.Volume(),'outer_race_checks':fit,'nominal_diametral_interference_mm':.05,'contact_land_diameter_mm':42.,'product_rigid_parts':2,'product_screws':2,'handled_parts':9,'printed_alternatives_checked':12,'external_envelope_mm':{'base_diameter':58,'cap_max_diameter':61.6,'top_z':17.2,'phone_contact_to_top':17.0},'negative_checks_passed':negative,'physical_release_gates':['Calibrate both fits with selected bearing and actual printer/material','Measure low hand seating force; never force the bearing through its balls','Measure pull-off retention against actual phone/magnet detachment loads','Wobble, rotational drag, creep, thermal cycling and removal life','Adhesive retention, loaded holder/cell, Hall/BLE/RF and firmware'],'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}}
(ROOT/'validation/pushfit-cad-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: two-part push-fit CAD;12 closed print alternatives,42mm race land,only prescribed fit/retention changes;9 handled parts and2 PCB screws; physical fit/retention unqualified')
