"""Isolated packaging study only; supplier cover/cell fit remains unverified."""
from pathlib import Path
import json,sys,math
import cadquery as cq
R=Path(__file__).resolve().parents[2];out=R/'work/larger-battery/holder-placement';out.mkdir(exist_ok=True)
p=json.loads((R/'mechanical/enclosure-parameters.json').read_text());p['pcb_bottom']=10.6;p['magnet_bottom']=13.9;p['encoder_stop']['seated_top_z_mm']=15.4;p['pcb_mount'].update({'radius_mm':16.4,'hole_diameter_mm':2.2,'shoulder_radius_mm':1.6});p['fixed_bearing_support']['radius_mm']=18.05
spec=out/'parameters.json';spec.write_text(json.dumps(p,indent=2)+'\n')
f=R/'mechanical/build_enclosure.py';code=f.read_text().split('bearing,inner,outer,seals,bearing_parts=')[0]
changes={"post=disk(2.25,1.4,pz-1.4,x,y)":"post=disk(1.6,1.4,pz-1.4,x,y).fuse(disk(2.5,1.4,.4,x,y))","if index in [0,2]:post=post.fuse(disk(1.4,pz,.5,x,y))":"# No fragile locating collars in this trial;2.2mm holes locate M2 screws.","disk(4.,1.4,.8,x,y),disk(2.5,2.,1.2,x,y)":"disk(4.,1.4,.4,x,y),disk(2.5,1.7,1.5,x,y)","disk(4.,3.,bz-3.,x,y)":"disk(2.7,3.,bz-3.,x,y)"}
for old,new in changes.items():assert old in code,old;code=code.replace(old,new)
sys.path.insert(0,str(f.parent));sys.argv=[str(f),'--parameters',str(spec),'--style','circular','--out',str(out/'cache')];ns={'__file__':str(f),'__name__':'__fit_trial__'};exec(code,ns);base=ns['base'];assert base.isValid() and len(base.Solids())==1
raw=cq.importers.importStep(str(R/'work/assembly-opt/battery-imports/imports/BS_24_B4AK014/BS_24_B4AK014.step')).val();holder=raw.translate((-.0000127,-.1991108,.01)).rotate((0,0,0),(0,1,0),180).rotate((0,0,0),(0,0,1),180).translate((0,-.5,10.6))
v=base.intersect(holder).Volume();assert v<.002,('Full base/holder collision',v)
board=cq.Solid.makeCylinder(18.25,1,cq.Vector(0,0,10.6));sweep=cq.Solid.makeCylinder(18.25,20,cq.Vector(0,0,10.6))
for a in [45,135,225,315]:
 x,y=16.4*math.cos(math.radians(a)),16.4*math.sin(math.radians(a));board=board.cut(cq.Solid.makeCylinder(1.1,1.2,cq.Vector(x,y,10.5)));sweep=sweep.cut(cq.Solid.makeCylinder(1.1,20.2,cq.Vector(x,y,10.5)))
assert base.intersect(board).Volume()<.002 and base.intersect(sweep).Volume()<.002,'PCB cannot seat/insert'
assembly=cq.Assembly(name='Holder_placement_trial_NOT_PRINT_QUALIFIED');assembly.add(base,name='Proposed_base',color=cq.Color(.35,.4,.45));assembly.add(board,name='Proposed_drilled_PCB',color=cq.Color(.17,.44,.3));assembly.add(holder,name='Supplier_holder_reference',color=cq.Color(.8,.8,.75));assembly.save(str(out/'holder-placement-trial.step'));cq.exporters.export(base,str(out/'proposed-base.step'))
report={'status':'Placement-only study; not an integrated larger-battery revision','active_design_modified':False,'base_valid_single_solid':True,'base_holder_overlap_mm3':v,'PCB_continuous_insertion_overlap_mm3':base.intersect(sweep).Volume(),'base_diameter_mm':58,'overall_top_datum_preserved_mm':17.2,'proposed_PCB_bottom_mm':10.6,'proposed_PCB_holes':{'radius_mm':16.4,'diameter_mm':2.2,'quantity':4},'proposed_post_radius_mm':1.6,'nominal_pilot_wall_mm':.8,'holder':'MYOUNG BS-24-B4AK014 C964813','holder_center_mm':[0,-.5],'holder_floor_clearance_mm':holder.BoundingBox().zmin-1.5,'unresolved':['Exact user-selected battery/holder unspecified','Supplier cover model overlaps nominal CR2450 cylinder; no cell-fit approval','Requires new PCB holes/holder footprint and rerouted battery branches','Requires new cap/encoder height and checks on all28 fitted components','Physical tolerances, contact seating and strength untested']}
(out/'fit-trial.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
