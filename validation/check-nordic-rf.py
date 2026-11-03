"""Check the physical C3 ground return, including copper pours and bypasses."""
from pathlib import Path
import copy,hashlib,json,math
from shapely.geometry import Point,Polygon,LineString,box
from shapely.affinity import rotate
from shapely.ops import unary_union

R=Path(__file__).resolve().parents[1]
def pad(e):
 x,y=e['x'],e['y']
 if e['shape']=='circle':return Point(x,y).buffer(e['radius'],resolution=128)
 w,h=e['width'],e['height']
 if e['shape'] in ['pill','rotated_pill']:
  rad=min(w,h)/2
  q=LineString([(x-(w-h)/2,y),(x+(w-h)/2,y)]).buffer(rad,resolution=128) if w>=h else LineString([(x,y-(h-w)/2),(x,y+(h-w)/2)]).buffer(rad,resolution=128)
 else:
  assert e['shape'] in ['rect','rotated_rect'],e['shape'];q=box(x-w/2,y-h/2,x+w/2,y+h/2)
 return rotate(q,e.get('ccw_rotation',0),origin=(x,y))
def copper(e,layer):
 if e['type']=='pcb_smtpad':return pad(e) if e['layer']==layer else Polygon()
 if e['type'] in ['pcb_via','pcb_plated_hole']:return Point(e['x'],e['y']).buffer(e['outer_diameter']/2,resolution=128) if layer in e['layers'] else Polygon()
 if e['type']=='pcb_copper_pour':
  b=e['brep_shape'];return Polygon([(v['x'],v['y'])for v in b['outer_ring']['vertices']], [[(v['x'],v['y'])for v in h['vertices']]for h in b.get('inner_rings',[])]).buffer(0) if e['layer']==layer else Polygon()
 if e['type']=='pcb_trace':
  return unary_union([LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(max(a['width'],b['width'])/2,resolution=128) for a,b in zip(e['route'],e['route'][1:]) if a['route_type']==b['route_type']=='wire' and a['layer']==b['layer']==layer])
 return Polygon()
def verify(c):
 owners={e['source_component_id']:e['name']for e in c if e['type']=='source_component'}
 sp={e['source_port_id']:e for e in c if e['type']=='source_port'};pp={e['pcb_port_id']:sp[e['source_port_id']]for e in c if e['type']=='pcb_port'}
 pads={f"{owners.get(pp[e['pcb_port_id']].get('source_component_id'))}.{pp[e['pcb_port_id']]['pin_number']}":e for e in c if e['type']=='pcb_smtpad' and e.get('pcb_port_id')in pp}
 gnd=next(e for e in c if e['type']=='source_net'and e['name']=='GND');key=gnd['subcircuit_connectivity_map_key']
 sources={e['source_trace_id']:e for e in c if e['type']=='source_trace'}
 rt=next(e for e in sources.values()if e.get('name')=='C3_VSS2_RETURN')
 traces=[e for e in c if e['type']=='pcb_trace'and e.get('source_trace_id')==rt['source_trace_id']];assert len(traces)==1
 trace=traces[0];assert all(p['route_type']=='wire'and p['layer']=='top'and p['width']==.18 for p in trace['route'])
 length=sum(math.hypot(b['x']-a['x'],b['y']-a['y'])for a,b in zip(trace['route'],trace['route'][1:]));assert length<=1.5
 target=pads['C3.2'];vss=pads['U1.31'];local=pad(target).union(copper(trace,'top'))
 assert local.intersection(pad(vss)).area>1e-4,'C3 return must reach the actual VSS31 land'
 isolation=box(-4.15,4.93,-1.65,5.9)
 def ground(e):
  return e.get('source_net_id')==gnd['source_net_id'] or e.get('subcircuit_connectivity_map_key',sources.get(e.get('source_trace_id'),{}).get('subcircuit_connectivity_map_key'))==key or pp.get(e.get('pcb_port_id'),{}).get('subcircuit_connectivity_map_key')==key or e.get('connection_name')==gnd['source_net_id']
 contacts=[]
 for e in c:
  if e['type']=='pcb_copper_pour':assert copper(e,e['layer']).intersection(isolation.buffer(-.002)).area<1e-8,'Ground pour bypasses the isolated return'
  if e['type']in ['pcb_via','pcb_plated_hole']:assert not copper(e,'top').intersects(isolation),'Via bypasses the local return'
  if e is trace or e is target or e is vss or not ground(e):continue
  hit=local.intersection(copper(e,'top')).difference(pad(vss).buffer(.002)).area
  assert hit<1e-8,('C3 return contacts another ground conductor away from VSS31',e.get('pcb_trace_id',e.get('type')),hit)
  if local.intersects(copper(e,'top')):contacts.append(e.get('pcb_trace_id',e['type']))
 feed=next(e for e in sources.values()if e.get('name')=='RF_FEED')
 route=next(e['route']for e in c if e['type']=='pcb_trace'and e.get('source_trace_id')==feed['source_trace_id'])
 feed_length=sum(math.hypot(b['x']-a['x'],b['y']-a['y'])for a,b in zip(route,route[1:]));assert all(p['route_type']=='wire'and p['layer']=='top'and p['width']==.5 for p in route)
 return {'passed':True,'C3_return_length_mm':length,'return_width_mm':.18,'return_vias':0,'only_ground_connection_through':'U1 VSS physical pin31 land','pour_isolation_both_layers_mm':[-4.15,4.93,-1.65,5.9],'RF_feed_length_mm':feed_length,'RF_feed_width_mm':.5,'RF_feed_vias':0,'impedance_verified':False,'physical_qualified':False,'remaining_RF_gate':'Supplier-confirmed actual dielectric/copper stackup and CPWG field solution; VNA matching and BLE range/harmonic testing in the complete bearing/ring/phone assembly'}

if __name__=='__main__':
 c=json.loads((R/'published.circuit.json').read_text());report=verify(c);negative=[]
 for kind in ['direct_ground_pour','extra_ground_branch','ground_via']:
  bad=copy.deepcopy(c);original=next(e for e in bad if e['type']=='pcb_trace'and e.get('source_trace_id')==next(e['source_trace_id']for e in bad if e['type']=='source_trace'and e.get('name')=='C3_VSS2_RETURN'))
  if kind=='direct_ground_pour':
   e=copy.deepcopy(next(e for e in bad if e['type']=='pcb_copper_pour'and e['layer']=='top'));e['brep_shape']={'outer_ring':{'vertices':[{'x':x,'y':y}for x,y in box(-3.4,5.3,-3.2,5.5).exterior.coords[:-1]]},'inner_rings':[]};bad.append(e)
  elif kind=='extra_ground_branch':
   e=copy.deepcopy(original);e['pcb_trace_id']='bad-bypass';bad.append(e)
  else:bad.append({'type':'pcb_via','x':-3.26,'y':5.46,'outer_diameter':.55,'layers':['top','bottom']})
  try:verify(bad)
  except AssertionError:negative.append(kind)
  else:raise AssertionError('Accepted physical RF bypass: '+kind)
 report['negative_checks_passed']=negative
 report['source_sha256']={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'published.circuit.json',R/'index.circuit.tsx',R/'parts.tsx',R/'critical-routes.json']}
 (R/'validation/nordic-rf-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f"PASS: C3 ground isolated from both pours;{report['C3_return_length_mm']:.3f}mm top return through VSS31 only;three physical bypass mutations rejected. Actual RF tuning remains unverified.")
