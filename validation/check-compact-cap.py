"""Validate only the prescribed0.6mm cap compaction against the checked push-fit CAD."""
from pathlib import Path
import hashlib,json,math,subprocess
import cadquery as cq
import trimesh

R=Path(__file__).resolve().parents[1]
BASE='b300e196ec7e3ff56dc7dc9638462b9cf52ab772'
P=json.loads((R/'mechanical/enclosure-parameters.json').read_text())
oldP=json.loads(subprocess.check_output(['git','show',BASE+':mechanical/enclosure-parameters.json'],cwd=R))
changes={'design':'V9 compact CR2450 rotation-only push-fit pilot','overall_height':16.6,'cap_deck_bottom':15.3,'cap_edge_bottom':8.6,
 'material':'PETG for two rigid printed parts; purchased metal bearing',
 'service':'Pull cap/bearing evenly; support the appropriate race and remove two PCB screws for cell/programming access',
 'publication':'Compact fit-test pilot; physical qualification required','hub_cover_thickness':1.3,
 'cap_style_change':'Use a cap with its own encoder magnet; transfer the bearing with race-specific support and a qualified hand fit',
 'cap_mount_hardware_count':0,
 'cap_compaction':{'baseline_commit':BASE,'top_reduction_mm':.6,'minimum_main_deck_mm':1.3,'minimum_encoder_roof_mm':1.2,'minimum_connector_clearance_mm':.7}}
assert P=={**oldP,**changes},'Unapproved mechanical parameter change'
assert P['cap_retention']==oldP['cap_retention'] and P['bearing']==oldP['bearing']
assert P['pcb_bottom']==oldP['pcb_bottom'] and P['battery']==oldP['battery']
delta=oldP['overall_height']-P['overall_height']
assert abs(delta-.6)<1e-7 and abs(oldP['cap_deck_bottom']-P['cap_deck_bottom']-delta)<1e-7
assert abs(oldP['cap_edge_bottom']-P['cap_edge_bottom']-delta)<1e-7
scratch=R/'work/compact-baseline';scratch.mkdir(parents=True,exist_ok=True)
def prior(name):
 p=scratch/(name+'.step');p.write_bytes(subprocess.check_output(['git','show',BASE+':mechanical/STEP_Parts/'+p.name],cwd=R))
 return cq.importers.importStep(str(p)).val()
def current(name):return cq.importers.importStep(str(R/'mechanical/STEP_Parts'/(name+'.step'))).val()
def disk(r,z,h):return cq.Solid.makeCylinder(r,h,cq.Vector(0,0,z))
def difference(a,b,label):
 added=a.cut(b).Volume();removed=b.cut(a).Volume()
 assert added<.003 and removed<.003,(label,added,removed)
 return {'unexpected_added_mm3':added,'unexpected_removed_mm3':removed}
def probe(shape,points,want,label):assert all(shape.isInside(cq.Vector(*p),1e-6)==want for p in points),label
def polar(r,a):return r*math.cos(math.radians(a)),r*math.sin(math.radians(a))
base=current('Stationary_Base');baseOld=prior('Stationary_Base')
baseResult=difference(base,baseOld,'Base/battery/shaft/ring/screw interfaces must be unchanged')
B=P['bearing'];bottom=B['bottom_z_mm'];top=bottom+B['width_mm']
magnetTop=P['magnet_bottom']+P['magnet_thickness'];pocket=P['magnet_pocket_diameter']/2
assert abs(P['overall_height']-P['cap_deck_bottom']-1.3)<1e-7
assert abs(P['overall_height']-magnetTop-1.2)<1e-7
results=[];jst=[]
for style in P['cap_styles']:
 name='Cap_'+style;old=prior(name);cap=current(name)
 # Independent construction from the former complete solid: lower the shell,
 # restore its bearing plane and fixed encoder pocket. No broad delta masks.
 expected=old.translate((0,0,-delta))
 expected=expected.cut(disk(40,-10,bottom+10))
 expected=expected.cut(disk(B['housing_diameter_mm']/2,-10,top+10))
 expected=expected.cut(disk(pocket+.9,-10,P['magnet_bottom']-.1+10))
 expected=expected.cut(disk(pocket,-10,magnetTop+10)).clean()
 result=difference(cap,expected,name+' differs from exact translated/restored baseline')
 assert cap.isValid() and len(cap.Solids())==1 and len(cap.Shells())==1,name
 assert abs(cap.BoundingBox().zmax-P['overall_height'])<1e-6
 for attr in ['xmin','xmax','ymin','ymax']:
  assert abs(getattr(cap.BoundingBox(),attr)-getattr(old.BoundingBox(),attr))<1e-6,(name,attr)
 for angle in range(0,360,30):
  probe(cap,[(*polar(2.45,angle),magnetTop-.01)],False,'Encoder pocket changed')
  probe(cap,[(*polar(2.45,angle),magnetTop+.01)],True,'Encoder stop changed')
  probe(cap,[(*polar(10,angle),z)for z in [15.31,15.9,16.59]],True,'Main deck material missing')
  probe(cap,[(*polar(25.97,angle),z)for z in [6.5,9.,12.8]],False,'Bearing bore obstructed')
  probe(cap,[(*polar(25.98,angle),z)for z in [6.5,9.,12.8]],True,'Bearing housing interface changed')
 # The complete swept JST courtyard lies in this annulus; all caps must retain
 # the former0.7mm minimum, not just pass a sampled collision check.
 rmin=13.3-6.1/2;rmax=math.hypot(8.3/2,13.3+6.1/2)
 annulus=disk(rmax+.001,0,25).cut(disk(rmin-.001,-.01,25.02))
 floor=cap.intersect(annulus).BoundingBox().zmin
 gap=floor-(P['pcb_bottom']+P['pcb_thickness']+2.92)
 assert gap>=.7,(name,'JST clearance',gap)
 jst.append({'style':style,'floor_z_mm':floor,'minimum_clearance_mm':gap})
 mesh=trimesh.load_mesh(R/'mechanical/Print_STL'/(name+'.stl'),process=True)
 assert mesh.is_volume and mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
 assert cap.intersect(base).Volume()<.003
 results.append({'name':name,**result,'top_z_mm':cap.BoundingBox().zmax})
negative=[]
for label,a,b in [('base_floor_cut',base.cut(disk(.5,.2,1)),baseOld),
                  ('cap_encoder_stop_cut',cap.cut(disk(pocket,magnetTop,.1)),expected),
                  ('cap_extra_material',cap.fuse(disk(.5,P['overall_height'],.5)),expected)]:
 try:difference(a,b,label)
 except AssertionError:negative.append(label)
 else:raise AssertionError('Guard accepted '+label)
g=json.loads((R/'mechanical/enclosure-validation.json').read_text())
assert g['parameters']==P and g['product_rigid_parts']==2 and g['pcb_screws']==2
assert g['handled_parts_per_unit_excluding_adhesive_and_shims']==9 and g['sensor_gap_mm']==1.8
assert len(g['rotation_checks'])==24 and all(x['rigid_collisions']==0 for x in g['rotation_checks'])
paths=[Path(__file__),R/'validation/check-pushfit-cad.py',R/'mechanical/build_enclosure.py',R/'mechanical/grip_profiles.py',R/'mechanical/enclosure-parameters.json',R/'mechanical/enclosure-validation.json',*sorted((R/'mechanical/STEP_Parts').glob('*.step')),*sorted((R/'mechanical/Print_STL').glob('*.stl'))]
report={'passed':True,'physical_tested':False,'manufacturing_qualified':False,'comparison_commit':BASE,
 'method':'Exact whole-solid translation/restoration comparison, unchanged base, unchanged bearing and encoder interfaces; no waived shape changes',
 'base_result':baseResult,'cap_results':results,'nominal_diametral_interference_mm':.05,'contact_land_diameter_mm':42.,
 'product_rigid_parts':2,'product_screws':2,'handled_parts':9,'printed_alternatives_checked':12,
 'previous_phone_contact_height_mm':17.0,'phone_contact_height_mm':16.4,'height_reduction_mm':delta,
 'minimum_main_deck_mm':1.3,'minimum_encoder_roof_mm':1.2,'minimum_thumb_dish_deck_mm':.9,
 'jst_checks':jst,'minimum_connector_clearance_mm':min(x['minimum_clearance_mm']for x in jst),
 'retention':'Unchanged calibrated friction fits; no positive axial lock','negative_checks_passed':negative,
 'external_envelope_mm':{'base_diameter':58,'cap_max_diameter':61.6,'top_z':P['overall_height'],'phone_contact_to_top':P['overall_height']-.2},
 'physical_release_gates':['Confirm printed cap thickness/warp and actual connector clearance','Keep the established bearing, adhesive, pull-off, creep and service qualification gates','Magnetic/count/BLE/RF/current testing on the final prototype'],
 'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}}
for name in ['compact-cap-audit.json','pushfit-cad-audit.json']:(R/'validation'/name).write_text(json.dumps(report,indent=2)+'\n')
print('PASS: all11 compact caps exactly match prescribed0.6mm reduction;16.4mm height,1.3mm deck,1.2mm encoder roof,0.78mm JST clearance; unchanged base/bearing/magnet interfaces')
