"""Keep the complete magnet and Hall-sensor poses, not just a nominal gap label."""
from pathlib import Path
import copy,hashlib,json,subprocess
import cadquery as cq
R=Path(__file__).resolve().parents[1];BASE='b300e196ec7e3ff56dc7dc9638462b9cf52ab772'
P=json.loads((R/'mechanical/enclosure-parameters.json').read_text());C=json.loads((R/'published.circuit.json').read_text())
oldP=json.loads(subprocess.check_output(['git','show',BASE+':mechanical/enclosure-parameters.json'],cwd=R))
oldC=json.loads(subprocess.check_output(['git','show',BASE+':published.circuit.json'],cwd=R))
def sensor(c):
 sid=next(e['source_component_id']for e in c if e['type']=='source_component'and e['name']=='U2')
 return next(e for e in c if e['type']=='cad_component'and e['source_component_id']==sid)
def verify(p,c):
 for key in ['pcb_bottom','pcb_thickness','magnet_bottom','magnet_diameter','magnet_thickness','magnet_pocket_diameter','encoder_stop']:
  assert p[key]==oldP[key],('Magnet/board position or interface changed',key)
 cad,old=sensor(c),sensor(oldC)
 for key in ['position','rotation','model_origin_position','model_step_url']:
  assert cad[key]==old[key],('Hall sensor pose or model changed',key)
 source=R/cad['model_step_url']
 assert source.read_bytes()==subprocess.check_output(['git','show',BASE+':'+cad['model_step_url']],cwd=R)
 return cad,source
cad,source=verify(P,C);org=cad['model_origin_position'];pos=cad['position']
shape=cq.importers.importStep(str(source)).val().translate(tuple(-org.get(k,0)for k in'xyz'))
for axis,vector in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
 if cad['rotation'].get(axis,0):shape=shape.rotate((0,0,0),vector,cad['rotation'][axis])
shape=shape.translate((pos['x'],pos['y'],pos['z']+P['pcb_bottom']+P['pcb_thickness']/2))
gap=P['magnet_bottom']-shape.BoundingBox().zmax
assert abs(gap-1.799)<1e-6
negative=[]
bad=copy.deepcopy(P);bad['magnet_bottom']-=.1
try:verify(bad,C)
except AssertionError:negative.append('magnet_lowered_0.1mm')
else:raise AssertionError('Accepted changed magnet height')
bad=copy.deepcopy(C);sensor(bad)['position']['z']+=.1
try:verify(P,bad)
except AssertionError:negative.append('sensor_raised_0.1mm')
else:raise AssertionError('Accepted changed Hall sensor height')
paths=[Path(__file__),R/'mechanical/enclosure-parameters.json',R/'published.circuit.json',source]
report={'passed':True,'physical_tested':False,'comparison_commit':BASE,'magnet_and_sensor_world_poses_unchanged':True,
 'nominal_body_gap_mm':1.8,'actual_supplier_STEP_body_gap_mm':gap,'magnet_bottom_z_mm':P['magnet_bottom'],
 'magnet_top_z_mm':P['magnet_bottom']+P['magnet_thickness'],'Hall_model_top_z_mm':shape.BoundingBox().zmax,
 'gap_definition':'Air gap to supplier model body top; active Hall die-plane height is not inferred from the mesh',
 'negative_checks_passed':negative,'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}}
(R/'validation/encoder-gap-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: magnet and Hall poses/model bytes unchanged; nominal1.8mm, supplier-body gap{gap:.6f}mm; both0.1mm movement regressions rejected')
