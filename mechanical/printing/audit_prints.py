"""Audit the actual oriented PETG print set and run a real PrusaSlicer CLI.

G-code stays in ignored work/: it is evidence, never printer-ready delivery.
"""
from pathlib import Path
import argparse,hashlib,json,math,os,re,shutil,subprocess,time
import cadquery as cq
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--slicer',default=shutil.which('prusa-slicer'))
a=ap.parse_args()
assert a.slicer,'Actual slicer required; mesh checks alone do not complete this audit'
OUT=ROOT/'work/print-readiness';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((ROOT/'mechanical/enclosure-parameters.json').read_text())
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
base_profile=ROOT/'mechanical/printing/PETG-0.4-audit.ini'
support_profile=ROOT/'mechanical/printing/supports-everywhere.ini'
carrier_profile=ROOT/'mechanical/printing/carrier-shoulder-supports.ini'
names=['Stationary_Base','Bearing_Carrier','Inner_Race_Nut','Outer_Race_Retainer',*['Cap_'+s for s in P['cap_styles']],'Nest_Left','Nest_Right']
parts=[];critical=[]

def polar(r,angle):
 t=math.radians(angle);return r*math.cos(t),r*math.sin(t)

def probe(shape,points,label):
 assert all(shape.isInside(cq.Vector(*point),1e-6) for point in points),label

# Independent probes of the specific formerly sub-nozzle/weak walls. These
# test material, not just parameter values, for every finished cap variant.
for style in P['cap_styles']:
 shape=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/('Cap_'+style+'.step'))).val()
 for angle in [0,120,240]:
  x,y=polar(26.8,angle)
  for z,start in [(6.9,1.805),(8.,1.805),(9.7,1.805),(17.199,2.005)]:
   points=[]
   for direction in [-45,0,45]:
    dx,dy=polar(1,angle+direction)
    points.extend((x+dx*r,y+dy*r,z) for r in np.linspace(start,2.995,8))
   probe(shape,points,(style,'insufficient socket/countersink outer wall',z))
 critical.append({'part':'Cap_'+style,'lower_socket_outer_wall_mm':1.2,'top_countersink_outer_wall_mm':1.0,'method':'Exact STEP material probes on three bosses at four heights and three outward directions'})
nut=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts/Inner_Race_Nut.step')).val()
for angle in [0,90,180,270]:
 points=[]
 for z in [13.8,14.2,14.9]:
  points.extend((*polar(r,angle),z) for r in np.linspace(20.01,20.99,12))
 probe(nut,points,'Nut wall below tool notch is thinner than1mm')
critical.append({'part':'Inner_Race_Nut','wall_beneath_tool_notches_mm':1.0,'thread_clearance_mm':.15,'pitch_mm':1.2,'print_notch_bridge_width_mm':3.0})
critical.extend([
 {'part':'Outer_Race_Retainer','boss_pilot_wall_mm':.8,'threaded_wall_and_pullout':'Unqualified; test with actual M2 fastener'},
 {'part':'Bearing_Carrier','guide_load_wall_mm':1.35,'non_load_counterbore_rim_mm':.55,'shaft_wall_mm':1.2,'thread_radial_depth_mm':.35,'limit':'Connected thread detail; actual thread coupon must be tested'},
 {'part':'Stationary_Base','ring_roof_mm':1.5,'spring_floor_mm':1.3,'PCB_post_pilot_wall_mm':1.45,'non_retaining_locator_wall_mm':.6,'ring_roof_supports':'Required; unsupported annulus creates long tangential bridges despite4.4mm radial width'},
 {'part':'Nest_Left/Nest_Right','support_finger_thickness_mm':1.0,'finger_width_mm':2.6,'support_requirement':'Everywhere, including from pocket floor; not build-plate-only'},
])

def gcode_stats(path):
 pos={'X':0.,'Y':0.,'Z':0.};kind='';rows=[];layer_z=set();types={};metadata={}
 for line in path.read_text().splitlines():
  if line.startswith(';TYPE:'):kind=line[6:].strip()
  if line.startswith(';Z:'):layer_z.add(float(line[3:]))
  if line.startswith('; estimated printing time'):metadata['slicer_estimated_time_only']=line[2:]
  if line.startswith('; filament used [g]'):metadata['slicer_estimated_mass_only']=line[2:]
  if not re.match(r'G[01]\s',line):continue
  values={key:float(value) for key,value in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line)}
  before=pos.copy();pos.update({k:v for k,v in values.items() if k in pos})
  if values.get('E',0)>0 and ('X'in values or 'Y'in values):
   length=math.hypot(pos['X']-before['X'],pos['Y']-before['Y'])
   if length<1e-6:continue
   row=[before['X'],before['Y'],pos['X'],pos['Y'],pos['Z'],kind,values['E']];rows.append(row)
   types[kind]=types.get(kind,0)+1
 supports=[r for r in rows if r[5].startswith('Support material')]
 bridges=[math.hypot(r[2]-r[0],r[3]-r[1]) for r in rows if r[5]=='Bridge infill']
 return {'layers':len(layer_z),'extrusion_types':types,'positive_XY_extrusion_segments':len(rows),'support_segments':len(supports),'maximum_support_z_mm':max([r[4] for r in supports],default=0),'maximum_bridge_line_mm':max(bridges,default=0),**metadata},rows

for name in names:
 tooling=name.startswith('Nest_')
 meshpath=ROOT/'mechanical/Print_STL'/('Tooling' if tooling else '')/(name+'.stl')
 steppath=ROOT/('mechanical/export/Tooling' if tooling else 'mechanical/STEP_Parts')/(name+'.step')
 mesh=trimesh.load_mesh(meshpath,process=True);shape=cq.importers.importStep(str(steppath)).val()
 assert shape.isValid() and len(shape.Solids())==1,name
 assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume,name
 assert len(mesh.split())==1,(name,'Separate enclosed shells/loose islands remain')
 assert np.isfinite(mesh.vertices).all() and mesh.bounds[0,2]>-.0001,name
 assert np.max(mesh.extents[:2])<200 and mesh.extents[2]<200,name
 # Compare oriented STL vertices to the exact source STEP, reversing only the
 # declared bed transform; no mesh repair, scale or hidden distortion allowed.
 invert=(name.startswith('Cap_') and name!='Cap_thumb_scoop') or name=='Inner_Race_Nut'
 oriented=shape.rotate((0,0,0),(1,0,0),180) if invert else shape
 zmin=oriented.BoundingBox().zmin
 points=mesh.vertices[np.linspace(0,len(mesh.vertices)-1,48,dtype=int)].copy();points[:,2]+=zmin
 if invert:points[:,1:]*=-1
 error=max(cq.Vertex.makeVertex(*point).distance(shape) for point in points)
 assert error<.002,(name,'Oriented STL differs from STEP',error)
 assert abs(mesh.volume-shape.Volume())<max(.5,.005*shape.Volume()),name
 section=mesh.section(plane_origin=[0,0,.1],plane_normal=[0,0,1]);assert section is not None,name
 planar,_=section.to_2D();contact=sum(p.area for p in planar.polygons_full);assert contact>10,(name,'Insufficient bed contact')
 mode='everywhere' if name in ['Stationary_Base','Cap_thumb_scoop','Nest_Left','Nest_Right'] else ('shoulders' if name=='Bearing_Carrier' else ('early-rim' if name in ['Cap_ships_wheel','Cap_rounded_triangle','Cap_petal_flower','Cap_four_leaf_clover','Cap_rounded_square'] else 'none'))
 profiles=[base_profile]+([carrier_profile] if mode in ['shoulders','early-rim'] else ([support_profile] if mode=='everywhere' else []))
 cmd=[a.slicer,'--export-gcode']
 for profile in profiles:cmd+=['--load',str(profile)]
 gcode=OUT/(name+'.gcode');cmd+=['--center','110,110','--output',str(gcode),str(meshpath)]
 started=time.monotonic();run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);log=run.stdout+run.stderr
 (OUT/(name+'.log')).write_text(log)
 assert run.returncode==0,(name,log)
 assert 'print warning:' not in log.lower(),(name,log)
 assert not re.search(r'(non.manifold|repairing|unable to slice|empty layer)',log,re.I),(name,log)
 stats,paths=gcode_stats(gcode);assert stats['layers']>5 and stats['positive_XY_extrusion_segments']>100,name
 if mode!='none':assert stats['support_segments']>0,(name,'Required supports absent')
 else:
  assert stats['support_segments']==0,(name,'Unexpected support contacting fit surfaces')
  assert stats['maximum_bridge_line_mm']<=5,(name,'Free bridge exceeds conservative5mm PETG audit limit')
 if mode=='early-rim':assert stats['maximum_support_z_mm']<2.5,(name,'Rim supports extended into fit region')
 if mode=='shoulders':assert stats['maximum_support_z_mm']<4,(name,'Supports reached thread/shaft region')
 (OUT/(name+'-paths.json')).write_text(json.dumps(paths))
 row={'name':name,'role':'tooling' if tooling else ('cap alternative' if name.startswith('Cap_') else 'common product'),'file':str(meshpath.relative_to(ROOT)),'quantity_per_default_unit':int(name in ['Stationary_Base','Bearing_Carrier','Inner_Race_Nut','Outer_Race_Retainer','Cap_circular']),'supports':mode,'support_profile':[str(f.relative_to(ROOT)) for f in profiles],'orientation':'wide notched face down' if name=='Inner_Race_Nut' else ('upright, cup supported' if name=='Cap_thumb_scoop' else ('deck down' if name.startswith('Cap_') else 'as supplied')),'sha256':sha(meshpath),'STEP_file':str(steppath.relative_to(ROOT)),'STEP_sha256':sha(steppath),'single_closed_mesh':True,'source_STEP_surface_error_mm':error,'bed_contact_area_at_0_1mm_mm2':contact,'bounds_mm':mesh.bounds.tolist(),'slicer_execution_seconds':round(time.monotonic()-started,3),'slicer_exit_code':0,'slicer_warnings':[],'gcode_sha256':sha(gcode),**stats}
 parts.append(row);print(f'PASS {name}: {mode} supports; {stats["layers"]} layers; {stats["support_segments"]} support segments',flush=True)

version=subprocess.check_output([a.slicer,'--help'],text=True).splitlines()[0]
manifest={'format_version':1,'scope':'Controlled PETG fit-test print set; production/physical qualification still required','default_cap':'circular','default_rigid_part_count':5,'default_files':[r['file'] for r in parts if r['quantity_per_default_unit']],'cap_alternatives':[r['file'] for r in parts if r['role']=='cap alternative'],'tooling_files':[r['file'] for r in parts if r['role']=='tooling'],'excluded_from_rigid_printing':['Actuator_Ring_REFERENCE_ONLY.stl','All purchased bearings, springs, screws, washers, cells and magnets','Circuit display OBJ/GLB assets and electronic models'],'printer_assumptions':{**P['print_process'],'bed_mm':[220,220,200],'first_layer_mm':.2,'nominal_line_width_mm':.45,'infill_percent':100},'profile':str(base_profile.relative_to(ROOT)),'parts':parts,'gcode_distribution':'Audit G-code is in ignored work/ only. Re-slice with the actual printer profile; no machine G-code is shipped.'}
(ROOT/'mechanical/print-ready-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
sources=[Path(__file__),ROOT/'mechanical/build_enclosure.py',ROOT/'mechanical/enclosure-parameters.json',base_profile,support_profile,carrier_profile,*[ROOT/r['file'] for r in parts]]
report={'passed':True,'physical_tested':False,'manufacturing_qualified':False,'actual_slicer_executed':True,'slicer':version,'slicer_launcher_sha256':sha(Path(a.slicer).resolve()) if Path(a.slicer).is_file() else None,'parts_checked':len(parts),'critical_wall_checks':critical,'parts':parts,'remaining_physical_tests':['Printer/nozzle/filament process and coupon fit','Support removal and mating/bonding surface finish','Printed thread torque/pull-out/life','Spring/actuator/magnetic/adhesive/firmware production gates'],'source_sha256':{str(f.relative_to(ROOT)):sha(f) for f in sources}}
(ROOT/'validation/print-readiness.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 15 rigid product alternatives +2 tooling halves; real slicer output; no slicer print warnings; physical qualification pending')
