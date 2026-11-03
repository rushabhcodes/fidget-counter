"""Approve only local ground-pour removal around the existing mounting drills."""
from pathlib import Path
import copy,hashlib,json,subprocess,sys
from shapely.geometry import Point,Polygon
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
BASE='a7c29c470c439e6f4e35314b9c68bba5c8d8c100'
def regions(c):
 nets={e['source_net_id']:e['name']for e in c if e['type']=='source_net'};out={}
 for e in c:
  if e['type']!='pcb_copper_pour':continue
  assert e['shape']=='brep'and nets[e['source_net_id']]=='GND'and e['covered_with_solder_mask'],'Ground net/layer/mask changed'
  b=e['brep_shape'];assert set(b)<={'outer_ring','inner_rings'},'Unknown BREP boundary schema'
  p=Polygon([(v['x'],v['y'])for v in b['outer_ring']['vertices']], [[(v['x'],v['y'])for v in h['vertices']]for h in b.get('inner_rings',[])]).buffer(0)
  out.setdefault(e['layer'],[]).append(p)
 return {k:unary_union(v)for k,v in out.items()}
def verify(before,current):
 holes=lambda c:sorted((e['x'],e['y'],e['hole_diameter'])for e in c if e['type']=='pcb_hole')
 oldholes=holes(before);assert holes(current)==oldholes and len(oldholes)==4,'Mounting drills changed'
 allowed=unary_union([Point(x,y).buffer(d/2+.31,resolution=256)for x,y,d in oldholes])
 a,b=regions(before),regions(current);assert set(a)==set(b)=={'top','bottom'}
 results={}
 for layer in a:
  added=b[layer].difference(a[layer]);removed=a[layer].difference(b[layer]);outside=removed.difference(allowed)
  assert added.area<1e-6,(layer,'Unexpected added ground copper',added.area)
  assert outside.area<1e-6,(layer,'Ground copper changed outside drill annuli',outside.area)
  gaps=[b[layer].distance(Point(x,y).buffer(d/2,resolution=256))for x,y,d in oldholes]
  assert min(gaps)>=.28,(layer,'NPTH ground clearance below the corrected nominal0.30mm margin',gaps)
  results[layer]={'removed_area_mm2':removed.area,'added_area_mm2':added.area,'unexplained_removed_area_mm2':outside.area,'hole_edge_clearance_mm':gaps}
 assert results['top']['removed_area_mm2']>.5,'Regression fixture did not exercise the former mounting-hole defect'
 return {'passed':True,'comparison_commit':BASE,'method':'Actual GND BREP unions; remove only copper inside existing drill radius+0.31mm; no additions, net/layer/mask or drill changes','nominal_cutout_margin_mm':.30,'minimum_required_measured_margin_mm':.28,'source_design_trace_to_hole_minimum_mm':.25,'layers':results}
if __name__=='__main__':
 if (ROOT/'validation/fresh-routing-reference.json').exists()and '--stdin'not in sys.argv:
  current=json.loads((ROOT/'published.circuit.json').read_text())
  def approved(value):
   proc=subprocess.run(['bun','-e',"import{verifyFreshRouting}from'./validation/check-fresh-routing.mjs';verifyFreshRouting(JSON.parse(await Bun.stdin.text()))"],cwd=ROOT,input=json.dumps(value),text=True,capture_output=True)
   return proc.returncode==0
  assert approved(current),'Current copper does not match the approved fresh routing and electrical contract'
  copper=regions(current);holes=[e for e in current if e['type']=='pcb_hole'];assert len(holes)==4
  measurements={layer:[p.distance(Point(h['x'],h['y']).buffer(h['hole_diameter']/2,resolution=256))for h in holes]for layer,p in copper.items()}
  assert min(v for row in measurements.values()for v in row)>=.28,'Fresh routing lost mounting-hole clearance'
  negative=[]
  for kind in ['unrelated_cutout','layer','mask']:
   bad=copy.deepcopy(current);p=next(e for e in bad if e['type']=='pcb_copper_pour'and e['layer']=='top')
   if kind=='unrelated_cutout':
    b=p['brep_shape'];poly=Polygon([(v['x'],v['y'])for v in b['outer_ring']['vertices']], [[(v['x'],v['y'])for v in h['vertices']]for h in b.get('inner_rings',[])])
    centre=Point(0,-17);assert poly.contains(centre.buffer(.2)),'Negative cutout must remove actual copper'
    b.setdefault('inner_rings',[]).append({'vertices':[{'x':x,'y':y}for x,y in centre.buffer(.2).exterior.coords[:-1]]})
   elif kind=='layer':p['layer']='unexpected-layer'
   else:p['covered_with_solder_mask']=False
   assert not approved(bad),'Fresh copper safeguard accepted '+kind
   negative.append(kind)
  paths=[Path(__file__),ROOT/'published.circuit.json',ROOT/'index.circuit.tsx',ROOT/'validation/check-fresh-routing.mjs',ROOT/'validation/fresh-routing-reference.json']
  report={'passed':True,'physical_tested':False,'scope':'Explicit approved fresh routing; exact copper/net/layer/mask signature plus actual NPTH clearance','minimum_required_measured_margin_mm':.28,'hole_edge_clearance_mm':measurements,'negative_checks_passed':negative,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}}
  (ROOT/'validation/npth-copper-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: fresh copper matches approved geometry; actual mounting-hole clearance >=0.28mm;3 real copper/layer/mask negatives rejected');sys.exit(0)
 if '--stdin'in sys.argv:
  d=json.load(sys.stdin);print(json.dumps(verify(d['before'],d['current'])));sys.exit(0)
 before=json.loads(subprocess.check_output(['git','show',BASE+':published.circuit.json'],cwd=ROOT));current=json.loads((ROOT/'published.circuit.json').read_text());r=verify(before,current)
 negative=[]
 for kind in ['unrelated_cutout','layer','mask']:
  bad=copy.deepcopy(current);p=next(e for e in bad if e['type']=='pcb_copper_pour'and e['layer']=='top')
  if kind=='unrelated_cutout':p['brep_shape'].setdefault('inner_rings',[]).append({'vertices':[{'x':x,'y':y}for x,y in Point(0,-17).buffer(.2).exterior.coords[:-1]]})
  elif kind=='layer':p['layer']='unexpected-layer'
  else:p['covered_with_solder_mask']=False
  try:verify(before,bad)
  except AssertionError:negative.append(kind)
  else:raise AssertionError('Negative safeguard accepted '+kind)
 r['negative_checks_passed']=negative
 paths=[Path(__file__),ROOT/'index.circuit.tsx',ROOT/'published.circuit.json'];r['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}
 (ROOT/'validation/npth-copper-audit.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS: mounting-hole GND clearances corrected with only bounded local copper removal;3 negative safeguards fail as required')
