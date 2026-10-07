"""Audit actual mask and legend primitives in this project's Gerber export."""
import hashlib, json, re, sys, zipfile
from pathlib import Path
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union

archive=Path(sys.argv[1])
circuit_path=Path(sys.argv[2] if len(sys.argv)>2 else 'dist/index/circuit.json')
c=json.loads(circuit_path.read_text())
def read_primitives(data):
    apertures={}; shapes=[]; widths=[]; dcode=None; previous=None
    for line in data.splitlines():
        m=re.fullmatch(r'%ADD(\d+)([CR]),([\d.]+)(?:X([\d.]+))?\*%',line)
        if m:
            apertures[int(m[1])]=(m[2],float(m[3]),float(m[4] or m[3]));continue
        if line.startswith('%') or line.startswith('G04'):continue
        m=re.fullmatch(r'D(\d+)\*',line)
        if m:dcode=int(m[1]);continue
        assert not line.startswith(('G02','G03','G36','G37')), 'Unsupported mask/legend primitive: '+line
        m=re.fullmatch(r'X([+-]?\d+)Y([+-]?\d+)D0([123])\*',line)
        if not m:continue
        x,y=float(m[1])/1e6,float(m[2])/1e6;op=int(m[3])
        if op in (1,3):
            kind,w,h=apertures[dcode]
            if op==3:
                g=Point(x,y).buffer(w/2,quad_segs=64) if kind=='C' else box(x-w/2,y-h/2,x+w/2,y+h/2)
            else:
                assert kind=='C' and previous is not None
                g=LineString([previous,(x,y)]).buffer(w/2,quad_segs=32)
                widths.append(w)
            shapes.append(g)
        previous=(x,y)
    return shapes,widths

with zipfile.ZipFile(archive) as z:
    mask={layer:read_primitives(z.read(name).decode())[0] for layer,name in [('top','F_Mask.gbr'),('bottom','B_Mask.gbr')]}
    silk={layer:read_primitives(z.read(name).decode()) for layer,name in [('top','F_SilkScreen.gbr'),('bottom','B_SilkScreen.gbr')]}
board=next(e for e in c if e['type']=='pcb_board')
u2=next(e for e in c if e['type']=='pcb_component' and e['center']=={'x':0,'y':0})
sensor=[]
for g in mask['top']:
    if abs(g.centroid.x)<=.201 and abs(g.centroid.y)<=.401:sensor.append(g)
assert len(sensor)==6,len(sensor)
bridge=min(a.distance(b) for i,a in enumerate(sensor) for b in sensor[i+1:])
legend={}
for layer,(shapes,widths) in silk.items():
    openings=unary_union(mask[layer])
    violations=[{'bounds':list(g.bounds),'maskClearanceMm':round(g.distance(openings),6)} for g in shapes if g.distance(openings)<.15-1e-5]
    legend[layer]={'minimumDrawStrokeMm':min(widths),'minimumMaskClearanceMm':min(g.distance(openings) for g in shapes),'violations':violations}

# Conservative upper bound: every opening is counted as exposed copper,
# including mounting holes and other non-copper areas.
exposed_bound=sum(unary_union(openings).area for openings in mask.values())
from shapely.geometry import Polygon
area=Polygon([(p['x'],p['y']) for p in board['outline']]).area
drill_count=sum(e['type'] in ('pcb_via','pcb_plated_hole','pcb_hole') for e in c)
result={'circuitJsonSha256':hashlib.sha256(circuit_path.read_bytes()).hexdigest(),
    'gerberZipSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
    'sensorMaskBridgeMm':round(bridge,6),'minimumGreenMaskBridgeMm':.1,
    'silkscreen':legend,'boardAreaMm2':area,'drillCount':drill_count,
    'drillDensityPerSquareMetre':drill_count/area*1e6,
    'exposedEnigAreaUpperBoundPercentOfSingleBoardArea':exposed_bound/area*100,
    'panelToolingAndTabsExcludedFromDensity':True}
Path('work/jlc-gerber-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
assert bridge>=.1-1e-5
assert all(v['minimumDrawStrokeMm']>=.15-1e-5 and not v['violations'] for v in legend.values()), 'Legend requires repair'
assert result['drillDensityPerSquareMetre']<150000
assert result['exposedEnigAreaUpperBoundPercentOfSingleBoardArea']<30
