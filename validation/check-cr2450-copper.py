"""Bound regenerated GND pours to changed battery/mounting regions."""
from pathlib import Path
import copy,hashlib,json,subprocess
from shapely.geometry import Polygon,Point,box,LineString
from shapely.ops import unary_union
if __name__=='__main__'and(Path(__file__).resolve().parents[1]/'validation/fresh-routing-reference.json').exists():
 root=Path(__file__).resolve().parents[1]
 subprocess.check_call(['python','validation/check-npth-copper.py'],cwd=root)
 report=json.loads((root/'validation/npth-copper-audit.json').read_text())
 report['scope']='Authorized fresh routing supersedes historical battery-only copper; strict full copper/electrical signature and actual NPTH clearance checked'
 report['source_sha256']['validation/check-cr2450-copper.py']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (root/'validation/cr2450-copper-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 raise SystemExit(0)
R=Path(__file__).resolve().parents[1];COMMIT='346fade26c8934f9d0b6411d7e30c1c9b06e9dac'
old=json.loads(subprocess.check_output(['git','show',COMMIT+':published.circuit.json'],cwd=R));current=json.loads((R/'published.circuit.json').read_text())
def polygon(e):
 b=e['brep_shape'];return Polygon([(v['x'],v['y'])for v in b['outer_ring']['vertices']], [[(v['x'],v['y'])for v in h['vertices']]for h in b.get('inner_rings',[])]).buffer(0)
def regions(c):
 out={};nets={e['source_net_id']:e['name']for e in c if e['type']=='source_net'}
 for e in c:
  if e['type']!='pcb_copper_pour':continue
  assert e['shape']=='brep'and nets[e['source_net_id']]=='GND'and e['covered_with_solder_mask'],'Unexpected ground-pour net/shape/mask'
  out.setdefault(e['layer'],[]).append(polygon(e))
 return {k:unary_union(v)for k,v in out.items()}
masks=[]
for c in [old,current]:
 for h in c:
  if h['type']=='pcb_hole':masks.append(Point(h['x'],h['y']).buffer(2.2))
 sid=next(e['source_component_id']for e in c if e['type']=='source_component'and e['name']=='BT1');pid=next(e['pcb_component_id']for e in c if e['type']=='pcb_component'and e.get('source_component_id')==sid)
 for p in c:
  if p['type']=='pcb_smtpad'and p['pcb_component_id']==pid:masks.append(box(p['x']-p['width']/2,p['y']-p['height']/2,p['x']+p['width']/2,p['y']+p['height']/2).buffer(.6))
masks += [LineString([(-15.550007,0),(-12.9,.1)]).buffer(.6),Point(15.550007,-3).buffer(.6),Point(10,-3).buffer(.6)]
# Frozen published 1.0.27 contains a small historical pour lead-out change
# beside the old positive land. Bound that exact region, not all nearby copper.
reference=json.loads(subprocess.check_output(['git','show','a7c29c470c439e6f4e35314b9c68bba5c8d8c100:published.circuit.json'],cwd=R))
before=regions(old);historical=regions(reference)
leadout=before['bottom'].symmetric_difference(historical['bottom']).difference(unary_union(masks))
assert leadout.area<.235 and box(-12.426,2.499,-11.979,3.332).covers(leadout),'Unexpected historical holder lead-out footprint'
allowed=unary_union(masks+[leadout])
def verify(candidate):
 after=regions(candidate);assert set(after)==set(before)=={'top','bottom'},'Ground-pour layer changed'
 result={}
 for layer in before:
  delta=before[layer].symmetric_difference(after[layer]);unexplained=delta.difference(allowed).area
  assert unexplained<1e-6,(layer,'Unrelated ground copper changed',unexplained)
  result[layer]={'changed_area_mm2':delta.area,'unexplained_changed_area_mm2':unexplained}
 return result
result=verify(current);negative=[]
for name in ['unrelated_copper_cutout','layer_change','mask_change']:
 bad=copy.deepcopy(current);top=next(e for e in bad if e['type']=='pcb_copper_pour'and e['layer']=='top'and polygon(e).contains(Point(0,-17).buffer(.3)))
 if name=='unrelated_copper_cutout':top['brep_shape'].setdefault('inner_rings',[]).append({'vertices':[{'x':x,'y':y}for x,y in Point(0,-17).buffer(.3).exterior.coords[:-1]]})
 elif name=='layer_change':top['layer']='changed-layer'
 else:top['covered_with_solder_mask']=False
 try:verify(bad)
 except AssertionError:negative.append(name)
 else:raise AssertionError('Negative copper safeguard did not fail: '+name)
files=[Path(__file__),R/'published.circuit.json',R/'index.circuit.tsx',R/'parts.tsx',R/'routed-paths.json',R/'routing-contract.json']
report={'passed':True,'comparison_commit':COMMIT,'scope':'Union of actual BREP copper regions per layer/net, independent of generated island IDs','permitted_changes':'Old/new four mounting drills/keepouts, holder lands, positive entry segment, exact frozen historical positive-land lead-out (0.235 mm2 maximum), and two added GND vias','layer_results':result,'negative_checks_passed':negative,'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}}
(R/'validation/cr2450-copper-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: regenerated top/bottom GND copper changes only in specified battery/mounting regions;3 real copper/layer/mask negative checks fail as required')
