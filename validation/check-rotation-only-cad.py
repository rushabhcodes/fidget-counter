"""Bound every intentional print change against the last pushed press-cap pilot."""
from pathlib import Path
import hashlib,json,math,subprocess
import cadquery as cq
ROOT=Path(__file__).resolve().parents[1];COMMIT='6224fc92863964ff770789ec086876e289d29bee'
P=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text());
if P['design'].startswith('V7'):
 import runpy
 runpy.run_path(str(ROOT/'validation/check-assembly-optimization.py'),run_name='__main__')
 raise SystemExit(0)
TMP=ROOT/'work/rotation-only/old-step';TMP.mkdir(parents=True,exist_ok=True)
def old(name):
 f=TMP/(name+'.step');f.write_bytes(subprocess.check_output(['git','show',f'{COMMIT}:mechanical/STEP_Parts/{name}.step'],cwd=ROOT));return cq.importers.importStep(str(f)).val()
def current(name):return cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/(name+'.step'))).val()
def disk(r,z,h,x=0,y=0):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def ring(ri,ro,z,h):return disk(ro,z,h).cut(disk(ri,z-.01,h+.02))
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
base=current('Stationary_Base');before=old('Stationary_Base').fuse(old('Bearing_Carrier')).clean()
added=base.cut(before);removed=before.cut(base)
allowed_add=[]
# Former upper washer counterbores cut through the shaft up toZ9.0,
# above the bosses themselves. Their full voids are now filled.
for a in [0,105,255]:
 x,y=polar(16.5,a);allowed_add.append(disk(3.451,1.249,7.752,x,y))
for a in [60,180,300]:
 x,y=polar(19.5,a);allowed_add.append(disk(1.701,1.499,3.01,x,y))
allowed_remove=[disk(2.301,4.999,1.602,*polar(19.5,a)) for a in [60,180,300]]
for s in allowed_add:added=added.cut(s)
for s in allowed_remove:removed=removed.cut(s)
assert added.Volume()<.003,('Unrelated base material added',added.Volume())
assert removed.Volume()<.003,('Unrelated base material removed',removed.Volume())
assert base.isValid() and len(base.Solids())==1 and len(base.Shells())==1
caps=[];removed_pusher=ring(3.499,6.501,12.649,2.852)
for style in P['cap_styles']:
 name='Cap_'+style;a=old(name);b=current(name)
 extra=b.cut(a).Volume();missing=a.cut(b).cut(removed_pusher).Volume()
 assert extra<.003 and missing<.003,(style,extra,missing)
 caps.append({'style':style,'unexplained_added_mm3':extra,'unexplained_removed_mm3':missing})
for name in ['Inner_Race_Nut','Outer_Race_Retainer']:
 a=old(name);b=current(name);assert a.cut(b).Volume()<.003 and b.cut(a).Volume()<.003,name
# Remove artifacts rather than leaving tempting obsolete prints in the set.
for name in ['Bearing_Carrier','Actuator_Ring_REFERENCE_ONLY','Bottom_Tray','Encoder_Spacer']:
 assert not (ROOT/'mechanical/Print_STL'/(name+'.stl')).exists(),name
 assert not (ROOT/'mechanical/STEP_Parts'/(name+'.step')).exists(),name
assert [P[k] for k in ['base_diameter','overall_height','magnet_bottom','magnet_diameter','magnet_thickness']]==[58,17.2,11.4,5.,1.5]
assert not any(k in P for k in ['button_travel','press_guide','return_springs','actuator','switch_height'])
paths=[Path(__file__),ROOT/'mechanical/build_enclosure.py',ROOT/'mechanical/enclosure-parameters.json',*sorted((ROOT/'mechanical/STEP_Parts').glob('*.step'))]
report={'passed':True,'physical_tested':False,'comparison_commit':COMMIT,'base_fixed_support':'Former base/carrier fused with only guide/spring holes filled and spring seats removed; single solid/shell','unexplained_base_added_mm3':added.Volume(),'unexplained_base_removed_mm3':removed.Volume(),'cap_results':caps,'retainer_and_nut_geometry_unchanged':True,'external_envelope_and_encoder_pose_preserved':True,'retainer_joint':P['cap_retainer_joint'],'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}}
(ROOT/'validation/rotation-only-cad-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: fixed base and11 caps contain only bounded rotation-only changes; nut/retainer and encoder pose preserved')
