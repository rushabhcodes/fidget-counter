"""Bound V7 mechanical changes against the verified 1.0.25 rotation-only release.

Historical press-removal proof stays intact in check-rotation-only-cad.py.
Electronics/copper are independently guarded by check-rotation-only.mjs.
"""
from pathlib import Path
import hashlib,json,math,subprocess
import cadquery as cq
R=Path(__file__).resolve().parents[1];C='0397495f30583bb6a4501f5fb0f67bccf0f397aa'
P=json.loads((R/'mechanical/enclosure-parameters.json').read_text());tmp=R/'work/assembly-opt/baseline';tmp.mkdir(parents=True,exist_ok=True)
def old(name):
 f=tmp/(name+'.step');f.write_bytes(subprocess.check_output(['git','show',C+':mechanical/STEP_Parts/'+f.name],cwd=R));return cq.importers.importStep(str(f)).val()
def now(name):return cq.importers.importStep(str(R/'mechanical/STEP_Parts'/(name+'.step'))).val()
def disk(r,z,h,x=0,y=0):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def ring(ri,ro,z,h):return disk(ro,z,h).cut(disk(ri,z-.01,h+.02))
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
def bounded(a,b,masks,label):
 added=b.cut(a);removed=a.cut(b)
 for mask in masks:
  if added.Solids():added=added.cut(mask)
  if removed.Solids():removed=removed.cut(mask)
 assert added.Volume()<.003 and removed.Volume()<.003,(label,added.Volume(),removed.Volume())
 return {'unexplained_added_mm3':added.Volume(),'unexplained_removed_mm3':removed.Volume()}
assert [P[k] for k in ['base_diameter','overall_height','pcb_bottom','pcb_diameter','magnet_bottom','magnet_thickness']]==[58.,17.2,8.1,36.5,11.4,1.5]
assert P['pcb_mount']['screw_indices']==[0,2] and P['pcb_mount']['radius_mm']==15.2
assert [P['bearing'][k] for k in ['bore_mm','outside_mm','width_mm','bottom_z_mm','housing_diameter_mm']]==[40.,52.,7.,6.1,52.2]
assert P['cap_retainer_joint']['screw_pitch_radius_mm']==27.8
masks=[ring(18.64,20.66,6.09,.52),ring(18.19,20.01,12.59,3.02)]
masks += [disk(4.01,6.09,.52,*polar(16.5,a)) for a in [0,105,255]]
base=now('Stationary_Base');base_result=bounded(old('Stationary_Base'),base,masks,'Bearing support change')
assert base.isValid() and len(base.Solids())==1 and len(base.Shells())==1
nut=now('Inner_Race_Nut');a=old('Inner_Race_Nut').translate((0,0,.5));assert a.cut(nut).Volume()<.003 and nut.cut(a).Volume()<.003,'Nut must only shift +0.5mm'
# Cap changes are limited to bearing reliefs, thinner deck, and old/new screw
# pads/bores; shallow dishes preserve >=0.9mm roof in the selected profile.
masks=[ring(24.39,28.801,6.09,9.82),disk(30.801,15.499,.402)]
for rad in [26.8,27.8]:masks += [disk(3.001,6.09,11.12,*polar(rad,a)) for a in [0,120,240]]
results=[]
for style in P['cap_styles']:
 allowed=list(masks)
 if style=='thumb_scoop':allowed += [disk(7.8,16.599,.602,*polar(22,a)) for a in [60,180,300]]
 cap=now('Cap_'+style);delta=bounded(old('Cap_'+style),cap,allowed,style)
 assert cap.isValid() and len(cap.Solids())==1
 box=cap.BoundingBox();assert all(abs(getattr(box,k))<=30.801 for k in ['xmin','xmax','ymin','ymax']) and abs(box.zmax-17.2)<1e-6,(style,'Cap exceeds envelope')
 # Independent pocket and stop probes; the Hall/magnet interface is fixed.
 for a in range(0,360,30):
  assert not cap.isInside(cq.Vector(*polar(2.45,a),12.8),1e-6)
  assert cap.isInside(cq.Vector(*polar(2.45,a),12.91),1e-6)
 results.append({'style':style,**delta})
# Retainer independently reconstructed as a ring + three drilled broad bosses.
ret=ring(25,28.8,4.6,1.5)
for a in [0,120,240]:
 x,y=polar(27.8,a);ret=ret.fuse(disk(1.6,6.08,3.52,x,y));ret=ret.cut(disk(.8,4.5,5.3,x,y))
for ang in [60,180,300]:
 notch=cq.Workplane('XY').box(1.6,3.,.6).val().translate((28.8,0,4.8)).rotate((0,0,0),(0,0,1),ang);ret=ret.cut(notch)
a=now('Outer_Race_Retainer');assert ret.cut(a).Volume()<.003 and a.cut(ret).Volume()<.003,'Unexpected retainer geometry'
rows=json.loads((R/'mechanical/export/Validation/scene_meshes.json').read_text())
# Purchased screw count and exact centers are independent of the report count.
for name,centers in [('PCB_Fasteners',[polar(15.2,a) for a in [45,225]]),('Cap_Retainer_Screws',[polar(27.8,a) for a in [0,120,240]])]:
 import trimesh,numpy as np
 row=next(x for x in rows if x['name']==name);mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True);pieces=mesh.split();assert len(pieces)==len(centers),(name,len(pieces))
 for center in centers:assert min(np.linalg.norm(piece.bounds.mean(axis=0)[:2]-center) for piece in pieces)<.01
for name in ['Bearing_Carrier','Actuator_Ring_REFERENCE_ONLY','Bottom_Tray','Encoder_Spacer']:assert not (R/'mechanical/Print_STL'/(name+'.stl')).exists()
files=[Path(__file__),R/'validation/check-rotation-only-cad.py',R/'mechanical/build_enclosure.py',R/'mechanical/enclosure-parameters.json',*sorted((R/'mechanical/STEP_Parts').glob('*.step'))]
report={'passed':True,'physical_tested':False,'comparison_commit':C,'historical_rotation_removal_commit':'6224fc92863964ff770789ec086876e289d29bee','base_result':base_result,'cap_results':results,'nut_translation_mm':.5,'retainer_independently_reconstructed':True,'pcb_screws':2,'cap_screws':3,'external_envelope_and_encoder_pose_preserved':True,'limits':['Two-screw board retention/deflection and bearing fit require printed samples'],'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(R/'validation/rotation-only-cad-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: V7 changes bounded against verified1.0.25; nut shift, screw counts, magnet stop and four closed common solids independently checked')
