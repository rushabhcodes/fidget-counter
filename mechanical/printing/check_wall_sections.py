"""Check common-part wall/floor material in exact STEP geometry, independently of slicing."""
from pathlib import Path
import json,math,hashlib
import cadquery as cq
ROOT=Path(__file__).resolve().parents[2]
P=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text())
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
def load(name):return cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/(name+'.step'))).val()
def check(shape,points,label):
 assert all(shape.isInside(cq.Vector(*point),1e-6) for point in points),label
 return {'section':label,'sampled_material_points':len(points),'passed':True}
def tube(x,y,radii,zs):return [(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a)),z) for r in radii for z in zs for a in range(0,360,45)]
results=[]
retainer=load('Outer_Race_Retainer')
for angle in [0,120,240]:results.append(check(retainer,tube(*polar(26.8,angle),[.81,1.2,1.59],[7.,8.8]),f'Retainer pilot wall0.8mm at{angle}deg'))
carrier=load('Bearing_Carrier')
for angle in P['press_guide']['angles_deg']:
 x,y=polar(16.5,angle)
 results.append(check(carrier,tube(x,y,[2.66,3.3,3.99],[3.2,5.5]),f'Guide load wall1.35mm at{angle}deg'))
 results.append(check(carrier,tube(x,y,[3.46,3.72,3.99],[6.3]),f'Non-load guide rim0.55mm at{angle}deg'))
results.append(check(carrier,tube(0,0,[18.66,19.2,19.84],[11.]),'Bearing shaft wall1.2mm'))
base=load('Stationary_Base');assert len(base.Shells())==1,'Enclosed sliver cavities remain'
results.append(check(base,tube(0,0,[22.76,25,27.14],[2.405,3.,3.895]),'Continuous ring bonding roof1.5mm'))
for angle in P['return_springs']['angles_deg']:
 x,y=polar(19.5,angle)
 results.append(check(base,tube(x,y,[0,1.69],[.205,.795,1.495]),f'Spring floor1.3mm at{angle}deg'))
 results.append(check(base,tube(x,y,[2.1],[.795]),f'Legacy trapped relief filled at{angle}deg'))
for i,angle in enumerate(P['pcb_mount']['angles_deg']):
 x,y=polar(15.2,angle)
 results.append(check(base,tube(x,y,[.81,1.5,2.24],[7.]),f'PCB post pilot wall1.45mm at{angle}deg'))
 if i in [0,2]:results.append(check(base,tube(x,y,[.81,1.1,1.39],[8.3]),f'Non-retaining locator wall0.6mm at{angle}deg'))
paths=[ROOT/'mechanical/export/Tooling'/(name+'.step') for name in ['Nest_Left','Nest_Right']]
nest=cq.Compound.makeCompound([cq.importers.importStep(str(path)).val() for path in paths])
for angle in [0,120,240]:
 x,y=polar(28.4,angle);dx,dy=polar(1,angle+90)
 points=[(x+dx*offset,y+dy*offset,z) for offset in [-1.29,0,1.29] for z in [4.105,4.6,5.095]]
 results.append(check(nest,points,f'Fixture finger1mm thick2.6mm wide at{angle}deg'))
paths += [ROOT/'mechanical/STEP_Parts'/(name+'.step') for name in ['Stationary_Base','Bearing_Carrier','Outer_Race_Retainer']]
paths += [Path(__file__),ROOT/'mechanical/enclosure-parameters.json']
out={'passed':True,'physical_tested':False,'method':'Material point probes across known critical analytic STEP wall/floor sections; no physical strength inference','sections':results,'cap_and_nut_wall_checks':'validation/print-readiness.json','limits':['Thread forming removes material not represented by the pilot bore','Single variable-width non-load rims need printer qualification','Section sampling is not a global minimum-thickness proof of all decorative features'],'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}}
(ROOT/'validation/print-wall-sections.json').write_text(json.dumps(out,indent=2)+'\n');print(f'PASS: {len(results)} common/fixture wall and floor sections; cap/nut probes recorded separately')
