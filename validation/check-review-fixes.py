"""Regression checks for the datasheet review; does not certify RF/materials."""
import csv, hashlib, json, math
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union

circuit_path=Path('dist/index/circuit.json')
c=json.loads(circuit_path.read_text())
sc={e['source_component_id']:e for e in c if e['type']=='source_component'}
byname={e['name']:e for e in sc.values()}
sp={e['source_port_id']:e for e in c if e['type']=='source_port'}
pp={e['pcb_port_id']:e for e in c if e['type']=='pcb_port'}
pc={e['pcb_component_id']:e for e in c if e['type']=='pcb_component'}
st={e['source_trace_id']:e for e in c if e['type']=='source_trace'}
traces=[e for e in c if e['type']=='pcb_trace']

def port(name,label):
 return next(e for e in sp.values() if e['source_component_id']==byname[name]['source_component_id'] and label in [e['name'],*e.get('port_hints',[])])
def pad(name,label):
 ids={e['pcb_port_id'] for e in pp.values() if e['source_port_id']==port(name,label)['source_port_id']}
 return next(e for e in c if e['type']=='pcb_smtpad' and e.get('pcb_port_id') in ids)
def padgeom(e):
 x,y=e['x'],e['y']
 if e['shape']=='circle':return Point(x,y).buffer(e['radius'])
 w,h=e['width'],e['height']
 if e['shape'] in ['pill','rotated_pill']:
  r=min(w,h)/2
  g=(LineString([(-w/2+r,0),(w/2-r,0)]) if w>h else LineString([(0,-h/2+r),(0,h/2-r)]) if h>w else Point(0,0)).buffer(r)
 else:g=box(-w/2,-h/2,w/2,h/2)
 return translate(rotate(g,e.get('ccw_rotation',0),origin=(0,0)),x,y)
def segments(t,layer='top'):
 return [LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(max(a['width'],b['width'])/2)
  for a,b in zip(t['route'],t['route'][1:]) if a['route_type']==b['route_type']=='wire' and a['layer']==b['layer']==layer]

dec2=port('U1','DEC2')
assert 'C7' not in byname
assert not any(dec2['source_port_id'] in e['connected_source_port_ids'] for e in st.values()), 'DEC2 must have no trace'
assert abs(byname['C8']['capacitance']-100e-12)<1e-15
assert port('C8','pin1')['subcircuit_connectivity_map_key']==port('U1','DEC3')['subcircuit_connectivity_map_key']
assert port('C8','pin2')['subcircuit_connectivity_map_key']==port('U1','VSS2')['subcircuit_connectivity_map_key']
# Every displayed U1 terminal must show the original physical QFAA pin number.
u1ports={e['source_port_id']:e for e in sp.values() if e['source_component_id']==byname['U1']['source_component_id']}
shown=[]
for e in c:
 if e['type']=='schematic_port' and e.get('source_port_id') in u1ports:
  physical=int(next(h[3:] for h in u1ports[e['source_port_id']]['port_hints'] if h.startswith('pin')))
  assert e['pin_number']==physical,(e,physical)
  shown.append({'label':e['display_pin_label'],'pin':physical})
assert len(shown)==22, len(shown)

# Geometric isolation test: cut away pin 31 itself. C3's return must then form
# a small island, disconnected from the top ground plane and every other GND pad.
gnd=port('U1','VSS2')['subcircuit_connectivity_map_key']
gnd_net=next(e['source_net_id'] for e in c if e['type']=='source_net' and e['name']=='GND')
polys=[]
for e in c:
 if e['type']=='pcb_copper_pour' and e['layer']=='top' and e['source_net_id']==gnd_net:
  b=e['brep_shape'];polys.append(Polygon([(p['x'],p['y']) for p in b['outer_ring']['vertices']],
   [[(p['x'],p['y']) for p in r['vertices']] for r in b.get('inner_rings',[])]).buffer(0))
 if e['type']=='pcb_smtpad' and e.get('layer')=='top' and sp[pp[e['pcb_port_id']]['source_port_id']].get('subcircuit_connectivity_map_key')==gnd:
  polys.append(padgeom(e))
 if e['type']=='pcb_trace' and (st.get(e.get('source_trace_id'),{}).get('subcircuit_connectivity_map_key')==gnd or e.get('subcircuit_connectivity_map_key')==gnd):polys.extend(segments(e))
 if e['type']=='pcb_via' and e.get('subcircuit_connectivity_map_key')==gnd:polys.append(Point(e['x'],e['y']).buffer(e['outer_diameter']/2))
all_top_gnd=unary_union(polys)
vss=pad('U1','VSS2');vss_shape=padgeom(vss)
cut=box(-5.05,4.9,-4.0,5.5)
after=all_top_gnd.difference(cut)
c3=pad('C3','pin2');seed=Point(c3['x'],c3['y'])
islands=list(after.geoms) if hasattr(after,'geoms') else [after]
island=next(p for p in islands if p.buffer(1e-6).contains(seed))
assert island.area<2, f'C3 bypasses VSS31: island area={island.area}'
assert island.distance(padgeom(pad('U1','EP')))>.1
for e in c:
 if e['type']=='pcb_via':assert not island.intersects(Point(e['x'],e['y']).buffer(e['outer_diameter']/2)), 'C3 return bypass via'
assert any(e.get('name')=='RF_C3_VSS31_RETURN' for e in st.values())
rf_return=next(t for t in traces if st.get(t.get('source_trace_id'),{}).get('name')=='RF_C3_VSS31_RETURN')
assert not any(p['route_type']=='via' for p in rf_return['route'])

# The matching network belongs beside the antenna, after the long 50-ohm run.
ant=pad('ANT1','feed')
near={}
for name in ['L2','C13','C14']:
 e=next(e for e in pc.values() if e['source_component_id']==byname[name]['source_component_id'])
 distance=math.hypot(e['center']['x']-ant['x'],e['center']['y']-ant['y'])
 assert distance<5, (name,distance)
 near[name]=round(distance,4)
# L1/C3 are the Nordic SoC network and intentionally remain beside U1.
feed=next(t for t in traces if st.get(t.get('source_trace_id'),{}).get('name')=='RF_50OHM_FEED')
rf=json.loads(Path('rf-stackup.json').read_text())
assert all(p['route_type']=='wire' and p['layer']=='top' and abs(p['width']-rf['traceWidthMm'])<1e-8 for p in feed['route'])

def K(k):
 a,b=1,math.sqrt(1-k*k)
 for _ in range(20):a,b=(a+b)/2,math.sqrt(a*b)
 return math.pi/(2*a)
def impedance(er):
 w=rf['traceWidthMm'];s=rf['coplanarGapMm'];h=rf['dielectricHeightMm'];t=rf['copperThicknessMm']
 k=w/(w+2*s);k3=math.tanh(math.pi*w/(4*h))/math.tanh(math.pi*(w+2*s)/(4*h))
 ratio=lambda k:K(k)/K(math.sqrt(1-k*k))
 r,r3=ratio(k),ratio(k3);ee=1+(er-1)*r3/(r+r3)
 delta=1.25*t/math.pi*(1+math.log(4*math.pi*w/t))
 ke=k+(1-k*k)*delta/(2*s)
 eet=ee-.7*(ee-1)*(t/s)/(r+.7*t/s)
 return 60*math.pi/math.sqrt(eet)/(ratio(ke)+r3)
z=impedance(rf['assumedRelativePermittivity'])
assert 48<z<52
# Quantify bottom reference interruptions. A uniform backed-CPW calculation
# cannot certify these crossings. Keep the qualification result explicit.
bottom=[]
for e in c:
 if e['type']=='pcb_copper_pour' and e['layer']=='bottom' and e['source_net_id']==gnd_net:
  b=e['brep_shape'];bottom.append(Polygon([(p['x'],p['y']) for p in b['outer_ring']['vertices']],
   [[(p['x'],p['y']) for p in r['vertices']] for r in b.get('inner_rings',[])]).buffer(0))
footprint=unary_union(segments(feed)).buffer(-.01)
bottom_missing=footprint.difference(unary_union(bottom)).area
reference_interruptions=[]
for p in getattr(footprint.difference(unary_union(bottom)),'geoms',[footprint.difference(unary_union(bottom))]):
 if p.area>1e-6:reference_interruptions.append({'areaMm2':p.area,'boundsMm':list(p.bounds)})

bom=list(csv.DictReader(Path('BOM.csv').open()))
assert next(r for r in bom if r['References']=='ENCODER_MAGNET')['Package']=='5x1.5mm'
fitted={ref for r in bom if r['Assembly']=='FIT' for ref in r['References'].split()}
actual={sc[e['source_component_id']]['name'] for e in pc.values() if not e.get('do_not_place') and e['source_component_id'] in sc}
assert fitted==actual,(fitted-actual,actual-fitted)
assert len(actual)==29
sw=next(r for r in bom if r['References']=='SW1')
assert 'C2804637' in sw['Source_url'] and not sw['JLCPCB_part_number']
assert byname['SW1']['manufacturer_part_number']=='KMR223NG ULC LFG / Y78B22324FP'
P=json.loads(Path('mechanical/enclosure-parameters.json').read_text())
g=json.loads(Path('mechanical/enclosure-validation.json').read_text())
assert P==g['parameters_mm'] and not g['collision_audit']
press=g['press_tolerance_stack']
assert press['minimum_closure_margin_mm']>=.1499
assert P['actuator_shim_nominal']-P['actuator_shim_min']>=press['unadjusted_worst_case_gap_error_mm']
assert P['actuator_shim_max']-P['actuator_shim_nominal']>=press['unadjusted_worst_case_gap_error_mm']
assert g['sensor_gap_pressed_mm']>=.8
report={'checkedAt':'2026-10-29','circuitSha256':hashlib.sha256(circuit_path.read_bytes()).hexdigest(),
 'dec2Unconnected':True,'dec3CapacitancePf':100,'physicalPinLabels':shown,
 'c3GroundIslandAreaAfterRemovingVss31Mm2':island.area,'antennaMatchingDistanceToFeedMm':near,
 'rfNominalEstimateOhms':z,'rfDkSensitivityOhms':{str(er):impedance(er) for er in [3.8,4.3,4.8]},
 'rfBottomGroundVoidUnderFeedMm2':bottom_missing,'rfReferenceInterruptions':reference_interruptions,'rfControlledImpedanceQualified':False,'fittedBomParts':len(actual),'pressToleranceStack':press,
 'externalValidationPending':['resolve/EM-review local digital crossings in bottom RF reference; fabricator stackup and impedance coupon','VNA antenna tuning and BLE/harmonics with phone and enclosure','silicone force curve, switch overload and press cycle/print fit test','assembler confirmation of SW1 exact-MPN supply/consignment']}
Path('validation/review-fixes.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['physicalPinLabels','pressToleranceStack']},indent=2))
