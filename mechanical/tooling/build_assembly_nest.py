"""Split manufacturing nest: locate the housing and hold the retainer BEFORE bearing insertion.
Tooling only. Clamp the two halves gently in a vice; open by >=3 mm per side to eject.
Remove tooling before rotational drag checks.
"""
from pathlib import Path
import json,math,hashlib,shutil
import cadquery as cq
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'mechanical/export/Tooling';OUT.mkdir(exist_ok=True)
p=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text());z=p['bearing']['bottom_z_mm']-1.5
# Broad split block, 0.2 mm nominal radial housing clearance, 0.2 mm lower datum.
nest=cq.Workplane('XY').box(80,80,9.6).val().translate((0,0,-3.2))
pocket=cq.Workplane('XY').workplane(offset=.2).circle(29.2).extrude(2).val();nest=nest.cut(pocket)
# Adhesive/magnet relief lies below the nominal phone-facing magnetic ring.
relief=cq.Workplane('XY').workplane(offset=-.8).circle(27.5).circle(22.5).extrude(1.1).val();nest=nest.cut(relief)
for angle in [0,120,240]:
 # Columns stay outside the base. Tips support the outer edge of the ring.
 column=cq.Workplane('XY').box(3.65,2.6,3.5).val().translate((31.175,0,3.35))
 finger=cq.Workplane('XY').box(4.9,2.6,1.0).val().translate((30.55,0,z-.5))
 nest=nest.fuse(column.fuse(finger).rotate((0,0,0),(0,0,1),angle))
mark=cq.Workplane('XY').workplane(offset=1.35).center(0,-35).text('JST',2.2,.4,combine=False).val();nest=nest.cut(mark).clean()
left=nest.intersect(cq.Workplane('XY').box(40,90,30).val().translate((-20,0,0))).clean()
right=nest.intersect(cq.Workplane('XY').box(40,90,30).val().translate((20,0,0))).clean()
for name,shape in [('Nest_Left',left),('Nest_Right',right)]:
 assert shape.isValid() and len(shape.Solids())==1,name
 cq.exporters.export(shape,str(OUT/(name+'.step')))
 oriented=shape.translate((0,0,8));f=OUT/(name+'.stl');cq.exporters.export(oriented,str(f),tolerance=.035,angularTolerance=.09)
 mesh=trimesh.load_mesh(f,process=True);assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,name
 distributed=ROOT/'mechanical/Print_STL/Tooling';distributed.mkdir(exist_ok=True)
 shutil.copyfile(f,distributed/f.name)
# Exact contact/clearance against every rigid product STEP, all cap variants.
checks=[]
for f in (ROOT/'mechanical/STEP_Parts').glob('*.step'):
 shape=cq.importers.importStep(str(f)).val();v=nest.intersect(shape).Volume();assert v<.002,(f.name,v);checks.append({'part':f.stem,'intersection_mm3':v})
# Opening the halves clears a conservative complete vertical base-ejection sweep.
sweep=cq.Workplane('XY').workplane(offset=.201).circle(29.05).extrude(12).val()
for name,half,shift in [('left',left,-3),('right',right,3)]:
 volume=half.translate((shift,0,0)).intersect(sweep).Volume();assert volume<.002,(name,'cannot eject',volume)
# The supports contact only the underside of the retainer, at its fixed Z.
retainer=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts/Outer_Race_Retainer.step')).val()
for angle in [0,120,240]:
 t=math.radians(angle);x,y=28.4*math.cos(t),28.4*math.sin(t)
 assert nest.isInside(cq.Vector(x,y,z-.05),1e-6) and retainer.isInside(cq.Vector(x,y,z+.05),1e-6),angle
assert left.intersect(right).Volume()<.002
report={'passed':True,'tooling_physical_tested':False,'product_geometry_modified':False,'purpose':'Support loose outer-race retainer at Z5.1 before bearing insertion and cap screw starting','retainer_support_z_mm':z,'housing_radial_clearance_mm':.2,'minimum_opening_per_half_mm':3.0,'clearance_checks':checks,'use':['Clamp halves gently in a nonmagnetic or suitably isolated vice','Place base and retainer before installing bearing','Align JST direction with the visual mark; it is not a mechanical orientation key','Start all three cap screws before applying qualified torque','Open both halves by at least3 mm and lift product','Perform rotation tests only AFTER removing the fixture'],'limits':['Tooling print fit and handling are untested','No torque or pull-out strength qualification is implied'],'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.iterdir() if f.suffix in ['.step','.stl']}}
report['source_sha256']={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),ROOT/'mechanical/enclosure-parameters.json',*sorted((ROOT/'mechanical/STEP_Parts').glob('*.step'))]}
(OUT/'nest-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Pass: two closed split-nest halves; all product STEP envelopes clear; retainer supported; 3 mm opening clears ejection')
