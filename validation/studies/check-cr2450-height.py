"""Nominal external height study; not a PCB/cell-contact manufacturing release."""
from pathlib import Path
import json,sys,math,hashlib
import cadquery as cq
R=Path(__file__).resolve().parents[2];trial=R/'work/larger-battery';sys.path.insert(0,str(R/'mechanical'))
# Reuse the isolated base trial's namespace and actual cap-generating source.
sys.argv=[];ns={'__file__':str(R/'validation/studies/cr2450-placement.py'),'__name__':'__height_trial__'};exec((R/'validation/studies/cr2450-placement.py').read_text(),ns)
p=ns['p'];out=ns['out'];holder=ns['holder'];base=ns['base'];board=ns['board'];ns=ns['ns'];f=R/'mechanical/build_enclosure.py';code=f.read_text();ns['styles']=p['cap_styles'];exec(code[code.index('retainer=ring('):code.index('pcb=disk(')],ns)
hub=ns['hub'];caps=ns['caps'];c=json.loads((R/'published.circuit.json').read_text());mid=p['pcb_bottom']+.5;models={};rows=[]
for cad in [e for e in c if e['type']=='cad_component' and e.get('model_step_url')]:
 src=next(e for e in c if e['type']=='source_component' and e['source_component_id']==cad['source_component_id']);name=src['name']
 if name=='BT1':shape=holder
 else:
  org=cad.get('model_origin_position',{});rot=cad.get('rotation',{});pos=cad['position'];shape=cq.importers.importStep(str(R/cad['model_step_url'])).val().translate(tuple(-org.get(k,0) for k in 'xyz'))
  for ax,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
   if rot.get(ax,0):shape=shape.rotate((0,0,0),vec,rot[ax])
  shape=shape.translate((pos['x'],pos['y'],pos['z']+mid))
 ns['clear'](hub,shape,'Cap common housing/'+name);ns['clear'](ns['nut'],shape,'Inner nut/'+name);ns['clear'](base,shape,'Base/'+name)
 b=shape.BoundingBox();rmax=max(math.hypot(x,y) for x in [b.xmin,b.xmax] for y in [b.ymin,b.ymax]);overflow=shape.cut(cq.Solid.makeCylinder(18.65,b.zlen+.02,cq.Vector(0,0,b.zmin-.01))).Volume() if rmax>=18.65 else 0.;assert overflow<.002,(name,'outside interior radial keepout');assert b.zmax<p['cap_deck_bottom'],(name,'above cap deck')
 rows.append({'component':name,'world_z_mm':[b.zmin,b.zmax],'bounding_box_corner_radius_mm':rmax,'actual_shape_outside18_65mm_radius_mm3':overflow});models[name]=shape
assert len(rows)==28
# Additional grip material is either outside the electronics radius or above
# their maximum height; verify this continuously for every finished cap.
interior=cq.Solid.makeCylinder(18.65,15.899,cq.Vector(0,0,0));styles=[]
for style,cap in caps.items():
 extra=cap.cut(hub);v=extra.intersect(interior).Volume() if extra.Solids() else 0.;assert v<.002,(style,v)
 b=cap.BoundingBox();assert abs(b.zmax-17.2)<1e-6;styles.append({'style':style,'top_z_mm':b.zmax,'unexplained_interior_material_mm3':v})
sensor=models['U2'].BoundingBox();gap=p['magnet_bottom']-sensor.zmax;assert gap>0;assert abs(gap-(11.4-(sensor.zmax-2.5)))<1e-6
jst=p['cap_deck_bottom']-(p['pcb_bottom']+1+2.92);assert jst>.7
cq.exporters.export(caps['circular'],str(out/'proposed-cap.step'))
a=cq.Assembly(name='CR2450_external_packaging_NOT_RELEASED');a.add(base,name='Base',color=cq.Color(.35,.4,.45));a.add(caps['circular'],name='Cap',color=cq.Color(.12,.47,.58));a.add(board,name='PCB',color=cq.Color(.17,.44,.3));a.add(holder,name='Holder_supplier_reference',color=cq.Color(.8,.8,.75));a.add(ns['nut'],name='Nut',color=cq.Color(.9,.65,.25));a.add(ns['retainer'],name='Retainer',color=cq.Color(.12,.38,.48));a.save(str(out/'external-height-study.step'))
report={'scope':'Nominal CR2450 external packaging and28-electronic CAD clearance study; not an integrated circuit release','status':'external_height_verified_nominal_CAD_only','active_battery_remains':'CR2032 pending exact user battery/holder details','old_top_z_mm':17.2,'new_top_z_mm':17.2,'height_increase_mm':0,'contact_face_z_mm':.2,'old_contact_to_top_height_mm':17.,'new_contact_to_top_height_mm':17.,'PCB_internal_rise_mm':2.5,'new_PCB_bottom_mm':10.6,'new_magnet_bottom_mm':13.9,'sensor_supplier_gap_preserved_mm':gap,'sensor_conservative_gap_mm':1.8,'JST_conservative_cap_clearance_mm':jst,'holder_reference':'MYOUNG BS-24-B4AK014 C964813','holder_floor_clearance_mm':holder.BoundingBox().zmin-1.5,'cap_styles':styles,'fitted_model_checks':rows,'required_changes':['Different PCB mounting-hole positions/diameters and holder footprint','New battery branch routing','New printed base and higher encoder pocket in all cap styles'],'not_verified':['Actual user battery model and saved changes','Supplier internal cell/cover seating; supplier model has a cover/cell-volume conflict','Physical print tolerances, contact force, retention and operation'],'physical_tested':False,'new_battery_integrated_into_active_project':False}
report['source_sha256']={str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [R/'validation/studies/check-cr2450-height.py',R/'validation/studies/cr2450-placement.py',R/'mechanical/build_enclosure.py',R/'mechanical/enclosure-parameters.json',R/'mechanical/grip_profiles.py',R/'published.circuit.json',R/'work/assembly-opt/battery-imports/imports/BS_24_B4AK014/BS_24_B4AK014.step']}
(out/'height-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','height_increase_mm','new_contact_to_top_height_mm','PCB_internal_rise_mm','JST_conservative_cap_clearance_mm']},indent=2),flush=True)
