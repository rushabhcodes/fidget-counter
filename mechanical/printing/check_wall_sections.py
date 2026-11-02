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
for angle in [0,120,240]:results.append(check(retainer,tube(*polar(P['cap_retainer_joint']['screw_pitch_radius_mm'],angle),[.81,1.2,1.59],[7.,8.8]),f'Retainer pilot wall0.8mm at{angle}deg'))
for angle in P['cap_retainer_joint']['fixture_angles_deg']:
 x,y=polar(28.4,angle);dx,dy=polar(1,angle+90)
 points=[(x+dx*t,y+dy*t,z) for t in [-1.29,0,1.29] for z in [5.105,5.6,6.095]]
 results.append(check(retainer,points,f'Retainer fixture saddle roof1mm at{angle}deg'))
base=load('Stationary_Base');assert len(base.Shells())==1,'Enclosed cavities remain'
for angle in P['fixed_bearing_support']['angles_deg']:
 x,y=polar(16.5,angle)
 results.append(check(base,tube(x,y,[0,1.2,2.49],[1.5,2.5,3.1,5.5]),f'Solid fixed bearing web5mm at{angle}deg'))
results.append(check(base,tube(0,0,[18.66,19.2,19.84],[11.]),'Bearing shaft wall1.2mm'))
results.append(check(base,tube(0,0,[22.76,25,27.14],[2.405,3.,3.895]),'Continuous ring bonding roof1.5mm'))
for i,angle in enumerate(P['pcb_mount']['angles_deg']):
 x,y=polar(15.2,angle)
 results.append(check(base,tube(x,y,[.81,1.5,2.24],[7.]),f'PCB post pilot wall1.45mm at{angle}deg'))
 if i in [0,2]:results.append(check(base,tube(x,y,[.81,1.1,1.39],[8.3]),f'Non-retaining locator wall0.6mm at{angle}deg'))
paths=[ROOT/'mechanical/export/Tooling'/(name+'.step') for name in ['Nest_Left','Nest_Right']]
nest=cq.Compound.makeCompound([cq.importers.importStep(str(path)).val() for path in paths])
for angle in P['cap_retainer_joint']['fixture_angles_deg']:
 x,y=polar(28.4,angle);dx,dy=polar(1,angle+90)
 points=[(x+dx*offset,y+dy*offset,z) for offset in [-1.29,0,1.29] for z in [4.105,4.6,5.095]]
 results.append(check(nest,points,f'Fixture finger1mm thick2.6mm wide at{angle}deg'))
paths += [ROOT/'mechanical/STEP_Parts'/(name+'.step') for name in ['Stationary_Base','Outer_Race_Retainer']]
paths += [Path(__file__),ROOT/'mechanical/enclosure-parameters.json']
out={'passed':True,'physical_tested':False,'method':'Material point probes across known critical analytic STEP wall/floor sections; no physical strength inference','sections':results,'cap_and_nut_wall_checks':'validation/print-readiness.json','limits':['Thread forming removes material not represented by the pilot bore','Single variable-width non-load rims need printer qualification','Section sampling is not a global minimum-thickness proof of all decorative features'],'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}}
(ROOT/'validation/print-wall-sections.json').write_text(json.dumps(out,indent=2)+'\n');print(f'PASS: {len(results)} common/fixture wall and floor sections; cap/nut probes recorded separately')
