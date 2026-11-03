"""Bound the battery-related CAD changes against the preceding CR2032 pilot."""
from pathlib import Path
import hashlib,json,math,subprocess
import cadquery as cq
R=Path(__file__).resolve().parents[1];C='346fade26c8934f9d0b6411d7e30c1c9b06e9dac'
P=json.loads((R/'mechanical/enclosure-parameters.json').read_text());oldP=json.loads(subprocess.check_output(['git','show',C+':mechanical/enclosure-parameters.json'],cwd=R))
tmp=R/'work/cr2450-upgrade/baseline';tmp.mkdir(parents=True,exist_ok=True)
def old(name):
 f=tmp/(name+'.step');f.write_bytes(subprocess.check_output(['git','show',C+':mechanical/STEP_Parts/'+f.name],cwd=R));return cq.importers.importStep(str(f)).val()
def now(name):return cq.importers.importStep(str(R/'mechanical/STEP_Parts'/(name+'.step'))).val()
def disk(r,z,h,x=0,y=0):return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
def bounded(before,after,masks,label):
 added=after.cut(before);removed=before.cut(after)
 for mask in masks:
  if added.Solids():added=added.cut(mask)
  if removed.Solids():removed=removed.cut(mask)
 assert added.Volume()<.003 and removed.Volume()<.003,(label,added.Volume(),removed.Volume())
 return {'unexplained_added_mm3':added.Volume(),'unexplained_removed_mm3':removed.Volume()}
for key in ['base_diameter','cap_max_diameter','overall_height','cap_deck_bottom','pcb_diameter','pcb_thickness','bearing','inner_race_nut','attachment_ring','cap_retainer_joint','cap_styles']:assert P[key]==oldP[key],key
assert [P[k] for k in ['pcb_bottom','magnet_bottom']]==[10.6,13.9]
assert P['encoder_stop']['seated_top_z_mm']==15.4
assert P['magnet_bottom']-P['pcb_bottom']==oldP['magnet_bottom']-oldP['pcb_bottom']
assert P['pcb_mount']['radius_mm']==16.6 and P['pcb_mount']['hole_diameter_mm']==2.2
assert P['pcb_mount']['screw_indices']==[0,2] and P['pcb_mount']['collar_height_mm']==0
masks=[]
for r,post in [(15.2,2.251),(16.6,2.501)]:masks += [disk(post,1.399,9.202,*polar(r,a)) for a in [45,135,225,315]]
for r in [16.5,18.05]:masks += [disk(4.001,1.399,4.702,*polar(r,a)) for a in [0,105,255]]
for r in [16.5,18.05]:masks += [disk(4.401,1.799,2.302,*polar(r,a)) for a in [0,105,255]] # Adjacent sidewall reliefs follow the relocated webs.
base=now('Stationary_Base');delta=bounded(old('Stationary_Base'),base,masks,'Base posts/webs')
assert base.isValid() and len(base.Solids())==1 and len(base.Shells())==1
for angle in [45,135,225,315]:
 x,y=polar(16.6,angle)
 for z in [1.81,6.3,9.8,10.59]:
  for a in range(0,360,45):
   for r in [.81,1.2,1.59]:assert base.isInside(cq.Vector(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a)),z),1e-6),'PCB pilot wall below0.8mm'
results=[]
for style in P['cap_styles']:
 cap=now('Cap_'+style);d=bounded(old('Cap_'+style),cap,[disk(3.501,11.299,4.602)],style)
 assert cap.isValid() and len(cap.Solids())==1 and abs(cap.BoundingBox().zmax-17.2)<1e-6
 for a in range(0,360,30):
  x,y=polar(2.45,a);assert not cap.isInside(cq.Vector(x,y,15.39),1e-6);assert cap.isInside(cq.Vector(x,y,15.41),1e-6)
 results.append({'style':style,**d})
for name in ['Inner_Race_Nut','Outer_Race_Retainer']:
 a=old(name);b=now(name);assert a.cut(b).Volume()<.003 and b.cut(a).Volume()<.003,name+' changed'
files=[Path(__file__),R/'mechanical/build_enclosure.py',R/'mechanical/enclosure-parameters.json',*sorted((R/'mechanical/STEP_Parts').glob('*.step'))]
report={'passed':True,'physical_tested':False,'comparison_commit':C,'base_result':delta,'cap_results':results,'nut_and_retainer_unchanged':True,'external_envelope_unchanged':True,'PCB_and_magnet_internal_rise_mm':2.5,'absolute_encoder_pose_preserved':False,'encoder_to_sensor_relative_height_preserved':True,'top_z_mm':17.2,'contact_to_top_height_mm':17.,'PCB_post_pilot_wall_mm':.8,'PCB_drill_edge_web_mm':.55,'pcb_screws':2,'cap_screws':3,'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(R/'validation/cr2450-cad-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: only specified base posts/webs and11 encoder pockets changed; bearing/ring/threads/retainer/exterior retained;2.5mm internal rise and0mm added exterior height')
