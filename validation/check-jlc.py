"""Measure routed copper against JLCPCB's published rigid-board limits."""
import hashlib, json, math, sys
from pathlib import Path
from shapely.geometry import Point, Polygon, LineString, box
from shapely import make_valid

path = Path(sys.argv[1] if len(sys.argv)>1 else 'dist/index/circuit.json')
c = json.loads(path.read_text())
sources = {e['source_port_id']:e for e in c if e['type']=='source_port'}
for connection in [e for e in c if e['type']=='source_component_internal_connection']:
    peers=[sources[p] for p in connection['source_port_ids']]
    connected=next((p.get('subcircuit_connectivity_map_key') for p in peers if p.get('subcircuit_connectivity_map_key')),None)
    if connected:
        for p in peers: p['subcircuit_connectivity_map_key']=connected
ports = {e['pcb_port_id']:e for e in c if e['type']=='pcb_port'}
traces = {e['source_trace_id']:e for e in c if e['type']=='source_trace'}
nets = {e['source_net_id']:e for e in c if e['type']=='source_net'}
components = {e['pcb_component_id']:e for e in c if e['type']=='pcb_component'}
sc = {e['source_component_id']:e for e in c if e['type']=='source_component'}
def ref(e):
    pc = components.get(e.get('pcb_component_id'),{})
    return sc.get(pc.get('source_component_id'),{}).get('name',e['type'])
def group(e):
    if e.get('pcb_port_id'):
        p = sources[ports[e['pcb_port_id']]['source_port_id']]
        return p.get('subcircuit_connectivity_map_key',p['source_port_id'])
    if e.get('source_trace_id'):
        return traces[e['source_trace_id']]['subcircuit_connectivity_map_key']
    if e.get('source_net_id'):
        return nets[e['source_net_id']]['subcircuit_connectivity_map_key']
    return e.get('subcircuit_connectivity_map_key',next(v for k,v in e.items() if k.endswith('_id')))
def pad(e):
    if e['shape']=='circle':
        return Point(e['x'],e['y']).buffer(e.get('radius',e.get('outer_diameter',0)/2),quad_segs=64)
    assert e['shape']=='rect',e
    return box(e['x']-e['width']/2,e['y']-e['height']/2,e['x']+e['width']/2,e['y']+e['height']/2)
cu=[]; holes=[]; vias=[]; smds=[]; wires=[]
board=Polygon([(p['x'],p['y']) for p in next(e for e in c if e['type']=='pcb_board')['outline']])
for e in c:
    t=e['type']
    if t in ('pcb_smtpad','pcb_plated_hole','pcb_via'):
        geom=pad(dict(e,shape=e.get('shape','circle')))
        layers=e.get('layers',[e.get('layer')])
        ident=next(v for k,v in e.items() if k==t+'_id')
        item={'id':ident,'ref':ref(e),'kind':t,'g':group(e),'geom':geom,'layers':layers,'raw':e}
        cu.append(item)
        if t=='pcb_smtpad': smds.append(item)
        else:
            h=dict(item,geom=Point(e['x'],e['y']).buffer(e['hole_diameter']/2,quad_segs=64))
            holes.append(h)
            # GPIO_* copper lands are routing vias, with no inserted component.
            if t=='pcb_via' or ref(e).startswith('GPIO_'): vias.append(h)
    elif t=='pcb_hole':
        holes.append({'id':e['pcb_hole_id'],'ref':'mounting','kind':t,'g':None,'geom':Point(e['x'],e['y']).buffer(e['hole_diameter']/2,quad_segs=64),'layers':['top','bottom'],'raw':e})
    elif t=='pcb_trace':
        for i,(a,b) in enumerate(zip(e['route'],e['route'][1:])):
            if a['route_type']!='wire' or b['route_type']!='wire' or a['layer']!=b['layer'] or a==b: continue
            line=LineString([(a['x'],a['y']),(b['x'],b['y'])])
            w=a['width']
            item={'id':e['pcb_trace_id']+':'+str(i),'ref':traces[e['source_trace_id']].get('name','trace'),'kind':t,'g':group(e),'geom':line.buffer(w/2,quad_segs=32),'layers':[a['layer']],'width':w}
            cu.append(item);wires.append(item)
    elif t=='pcb_copper_pour':
        b=e['brep_shape']
        geom=make_valid(Polygon([(p['x'],p['y']) for p in b['outer_ring']['vertices']],
            [[(p['x'],p['y']) for p in r['vertices']] for r in b['inner_rings']]))
        cu.append({'id':e['pcb_copper_pour_id'],'ref':'GND pour','kind':t,'g':group(e),'geom':geom,'layers':[e['layer']]})
def measure(name,left,right,limit,same_collection=False,different=True):
    rows=[]; minimum=1e9; nearest=None
    for i,a in enumerate(left):
        for j,b in enumerate(right):
            if same_collection and j<=i: continue
            if a['id']==b['id'] or not set(a['layers'])&set(b['layers']): continue
            if different and a['g']==b['g']: continue
            d=a['geom'].distance(b['geom'])
            pair={'a':a['id'],'aRef':a['ref'],'b':b['id'],'bRef':b['ref'],'distanceMm':round(d,6)}
            if d<minimum: minimum=d;nearest=pair
            if d<limit-1e-5: rows.append(pair)
    return {'check':name,'limitMm':limit,'minimumMm':round(minimum,6),'nearest':nearest,'violations':sorted(rows,key=lambda r:r['distanceMm'])}
mask_pads=[]
for item in smds:
    raw=item['raw']; margin=raw.get('soldermask_margin',0)
    geometry=item['geom'].buffer(margin,quad_segs=64) if raw['shape']=='circle' else box(
        raw['x']-raw['width']/2-margin,raw['y']-raw['height']/2-margin,
        raw['x']+raw['width']/2+margin,raw['y']+raw['height']/2+margin)
    mask_pads.append(dict(item,geom=geometry))
checks=[measure('different-net copper spacing',cu,cu,.1,True),
    measure('different-net SMT pad spacing',smds,smds,.15,True),
    measure('SMT mask opening to different-net track',mask_pads,wires,.09),
    measure('via drill to different-net track',vias,wires,.2),
    measure('via drill to via drill',vias,vias,.2,True,False),
    measure('NPTH drill to copper',[h for h in holes if h['kind']=='pcb_hole'],cu,.2,different=False),
    measure('wire-contact PTH drill to different-net track',[h for h in holes if h['kind']=='pcb_plated_hole' and not h['ref'].startswith('GPIO_')],wires,.28)]
edge=[]
for a in cu:
    d=board.boundary.distance(a['geom']) if board.covers(a['geom']) else -1
    edge.append({'id':a['id'],'ref':a['ref'],'distanceMm':round(d,6)})
via_counts={}
for h in holes:
    e=h['raw']; hd=e['hole_diameter'];od=e.get('outer_diameter')
    key=f'{hd:.2f} mm drill / {od:.2f} mm land' if od else f'{hd:.2f} mm NPTH'
    via_counts[key]=via_counts.get(key,0)+1
result={'input':str(path),'circuitJsonSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'copperChecks':checks,'minimumTraceWidthMm':min(w['width'] for w in wires),
    'minimumCopperToBoardEdge':min(edge,key=lambda r:r['distanceMm']),
    'minimumMountingWebMm':min(board.boundary.distance(h['geom']) for h in holes if h['kind']=='pcb_hole'),
    'drillInventory':via_counts,
    'silkscreenTextBelow1mm':[{'text':e['text'],'fontSizeMm':e['font_size']} for e in c if e['type']=='pcb_silkscreen_text' and e['font_size']<1]}
Path('work/jlc-geometry-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({**{k:v for k,v in result.items() if k!='copperChecks'},'copperChecks':[{k:v for k,v in r.items() if k!='violations'}|{'violationCount':len(r['violations']),'firstViolations':r['violations'][:6]} for r in checks]},indent=2))

assert all(not row['violations'] for row in checks), 'JLCPCB clearance violations remain'
assert result['minimumTraceWidthMm']>=.1 and result['minimumCopperToBoardEdge']['distanceMm']>=.2
assert not result['silkscreenTextBelow1mm']
