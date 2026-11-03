"""Build and independently check the V2 alternative; never mutate V1 or PCB files."""
from pathlib import Path
import argparse, hashlib, json, math, sys
import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V1 = HERE.parent / 'V1_premade_ring'
P = json.loads((HERE / 'parameters.json').read_text())
BASELINE = json.loads((V1 / 'enclosure-parameters.json').read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--out', type=Path, default=HERE / 'generated')
a = ap.parse_args(); OUT = a.out.resolve()
for sub in ['STEP', 'Print_STL', 'Reference_STEP', 'Assemblies']:
    (OUT / sub).mkdir(parents=True, exist_ok=True)

def ring(ri, ro, z, h):
    return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()

def block(length, width, z, height, radius, angle):
    # Local X is radial; the long edge is tangent. Angle zero is +X.
    return cq.Workplane('XY').box(width, length, height).val().translate((radius, 0, z + height/2)).rotate((0,0,0),(0,0,1),angle)

def clear(left, right, label):
    b, c = left.BoundingBox(), right.BoundingBox()
    if any(getattr(b,k+'max') <= getattr(c,k+'min') + 1e-7 or getattr(c,k+'max') <= getattr(b,k+'min') + 1e-7 for k in 'xyz'):
        return 0.0
    volume = left.intersect(right).Volume()
    assert volume < .002, (label, volume)
    return volume

# The frozen archive, current circuit and every unchanged cap are strict inputs.
manifest = json.loads((V1/'manifest.json').read_text())
for name, entry in manifest['files'].items():
    assert sha(V1/name) == entry['sha256'], ('V1 archive changed', name)
for name, digest in manifest['supplier_STEP_sha256'].items():
    assert sha(ROOT/name) == digest, ('Supplier STEP changed', name)
assert sha(ROOT/'published.circuit.json') == manifest['files']['source/published.circuit.json']['sha256'], 'Electrical circuit changed; requalify V2 against the new PCB'
assert (ROOT/'mechanical/enclosure-parameters.json').read_bytes() == (V1/'enclosure-parameters.json').read_bytes(), 'V1 interfaces changed'
for name, digest in P['unchanged_cap_STEP_sha256'].items():
    assert sha(ROOT/name) == digest, ('Cap changed', name)

print('Building V2 base, pocketed carrier and separate steel backing...', flush=True)
original = cq.importers.importStep(str(V1/'Base_V1_Premade_Ring.step')).val()
recess = ring(P['base_recess']['inside_radius_mm'], 29.1, .1, 2.3)
base = original.cut(recess).clean()
# Strictly a subtraction inside the declared phone-side recess. Everything
# above Z2.4, including bearing shaft, posts and all interfaces, is identical.
assert base.cut(original).Volume() < 1e-6
assert original.cut(base).cut(recess).Volume() < .002
upper = cq.Workplane('XY').box(100,100,40).val().translate((0,0,22.40001))
assert original.intersect(upper).cut(base).Volume() < .002
M = P['magnet']; C = P['carrier']; S = P['backing']
carrier = ring(C['inside_diameter_mm']/2, C['outside_diameter_mm']/2, C['bottom_z_mm'], C['top_z_mm']-C['bottom_z_mm'])
backing = ring(S['inside_diameter_mm']/2, S['outside_diameter_mm']/2, S['bottom_z_mm'], S['thickness_mm'])
magnets = {}; pockets = []
for row, radius in enumerate(M['row_center_radii_mm']):
    for station in range(M['stations']):
        angle = station*360/M['stations']
        pocket = block(M['length_mm']+.3, M['radial_width_mm']+.3, M['phone_face_z_mm'], 1.2, radius, angle)
        pockets.append(pocket); carrier = carrier.cut(pocket)
        magnets[f"{'Inner_S' if row==0 else 'Outer_N'}_{station+1:02}"] = block(M['length_mm'],M['radial_width_mm'],M['phone_face_z_mm'],M['thickness_mm'],radius,angle)
carrier = carrier.clean()
assert len(magnets) == M['quantity'] == 36
min_web = min(left.distance(right) for i,left in enumerate(pockets) for right in pockets[i+1:])
assert min_web >= .8, ('Pocket web thinner than two nominal nozzle widths', min_web)
outer_corner = math.hypot(M['row_center_radii_mm'][1]+(M['radial_width_mm']+.3)/2,(M['length_mm']+.3)/2)
inner_wall = M['row_center_radii_mm'][0]-(M['radial_width_mm']+.3)/2-C['inside_diameter_mm']/2
outer_wall = C['outside_diameter_mm']/2-outer_corner
assert min(inner_wall,outer_wall) >= .8
assert abs(M['phone_face_z_mm']-C['bottom_z_mm']-C['pocket_floor_mm']) < 1e-7
new = {'Base_V2_Discrete':base,'Magnet_Carrier_V2':carrier,'Steel_Backing_V2':backing,**magnets}
for i,(name,shape) in enumerate(new.items()):
    assert shape.isValid() and len(shape.Solids()) == 1, name
    for other, right in list(new.items())[i+1:]:
        clear(shape,right,f'{name}/{other}')

# Use actual supplier bodies in their saved PCB poses, not nominal boxes.
circuit = json.loads((ROOT/'published.circuit.json').read_text())
electronics = {}
for cad in (e for e in circuit if e['type']=='cad_component' and e.get('model_step_url')):
    source = next(e for e in circuit if e['type']=='source_component' and e['source_component_id']==cad['source_component_id'])
    org=cad.get('model_origin_position',{}); rot=cad.get('rotation',{}); pos=cad['position']
    shape=cq.importers.importStep(str(ROOT/cad['model_step_url'])).val().translate(tuple(-org.get(k,0) for k in 'xyz'))
    for axis,vec in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
        if rot.get(axis,0):shape=shape.rotate((0,0,0),vec,rot[axis])
    shape=shape.translate((pos['x'],pos['y'],pos['z']+BASELINE['pcb_bottom']+.5))
    electronics['Electronic_'+source['name']]=shape
    for name,left in new.items():clear(left,shape,name+'/'+source['name'])
assert len(electronics)==27
sys.path.insert(0,str(V1/'source'))
from hardware_models import coin_cell, bearing_6808, screw, magnet as encoder_magnet
cell,_=coin_cell(BASELINE['battery']['cell_bottom_z_mm'],BASELINE['battery']['standard'])
cx,cy=BASELINE['battery']['cell_center_mm'];cell=cell.translate((cx,cy,0))
for name,left in new.items():clear(left,cell,name+'/cell')
assert S['bottom_z_mm']+S['thickness_mm'] < 2.4
# All cap geometry stays byte-identical; new magnetic parts remain below Z2.4.
cap_checks=[]
for name in BASELINE['cap_styles']:
    cap=cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts'/('Cap_'+name+'.step'))).val()
    for angle in range(0,360,15):
        rotor=cap.rotate((0,0,0),(0,0,1),angle)
        for label,left in new.items():clear(rotor,left,name+'/'+label)
    cap_checks.append(name)

printed=[]
for name,shape in [('Base_V2_Discrete',base),('Magnet_Carrier_V2',carrier)]:
    step=OUT/'STEP'/(name+'.step');cq.exporters.export(shape,str(step))
    saved=cq.importers.importStep(str(step)).val()
    assert saved.isValid() and len(saved.Solids())==1
    assert saved.cut(shape).Volume()+shape.cut(saved).Volume()<.002
    oriented=saved.translate((0,0,-saved.BoundingBox().zmin))
    stl=OUT/'Print_STL'/(name+'.stl');cq.exporters.export(oriented,str(stl),tolerance=.025,angularTolerance=.09)
    mesh=trimesh.load_mesh(stl,process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume and len(mesh.split())==1,name
    assert abs(mesh.volume-saved.Volume()) < .005*saved.Volume()
    printed.append({'name':name,'STEP':str(step.relative_to(HERE)),'STEP_sha256':sha(step),'STL':str(stl.relative_to(HERE)),'STL_sha256':sha(stl),'watertight':True,'single_solid':True,'volume_mm3':saved.Volume(),'bed_orientation':'Phone-contact face down; positive Z up','physical_fitted':False})
for name,shape in [('Steel_Backing_V2',backing),('Attachment_Magnets_V2',cq.Compound.makeCompound(list(magnets.values())))]:
    cq.exporters.export(shape,str(OUT/'Reference_STEP'/(name+'.step')))
# Manufacturing DXF is a flat profile only; stock thickness/material come from
# parameters and the drawing notes. No PETG version of this part is delivered.
profile=cq.Workplane('XY').circle(S['outside_diameter_mm']/2).circle(S['inside_diameter_mm']/2)
cq.exporters.export(profile,str(OUT/'Reference_STEP/Steel_Backing_V2_cut_profile.dxf'))

# Recreate unchanged hardware from frozen V1 source, without an ignored cache.
pcb=cq.Workplane('XY').workplane(offset=BASELINE['pcb_bottom']).circle(BASELINE['pcb_diameter']/2).extrude(BASELINE['pcb_thickness']).val()
fasteners=[];mount=BASELINE['pcb_mount']
for index,angle in enumerate(mount['angles_deg']):
    theta=math.radians(angle);x,y=mount['radius_mm']*math.cos(theta),mount['radius_mm']*math.sin(theta)
    hole=cq.Workplane('XY').workplane(offset=BASELINE['pcb_bottom']-.1).center(x,y).circle(mount['hole_diameter_mm']/2).extrude(BASELINE['pcb_thickness']+.2).val()
    pcb=pcb.cut(hole)
    if index in mount['screw_indices']:
        fasteners.append(screw(.98,4,1.9,1.3,nylon=True).translate((x,y,BASELINE['pcb_bottom']+BASELINE['pcb_thickness'])))
kept={'PCB':pcb,'Cell':cell,'PCB_Fasteners':cq.Compound.makeCompound(fasteners),**electronics,
      'Bearing_6808':bearing_6808(BASELINE['bearing']['bottom_z_mm'])[0],
      'Magnet':encoder_magnet(BASELINE['magnet_diameter']/2,BASELINE['magnet_bottom'],BASELINE['magnet_thickness']),
      'Cap_circular':cq.importers.importStep(str(ROOT/'mechanical/STEP_Parts/Cap_circular.step')).val()}
assert len(kept)==33
rows=[]
colors={'Base_V2_Discrete':(.34,.4,.45),'Magnet_Carrier_V2':(.24,.39,.48),'Steel_Backing_V2':(.55,.57,.6)}
colors.update({'Cap_circular':(.12,.38,.48),'PCB':(.17,.44,.3),'Bearing_6808':(.7,.73,.77),'Cell':(.73,.75,.78),'Magnet':(.79,.8,.82),'PCB_Fasteners':(.8,.81,.8)})
for name,shape in {**kept,**new}.items():
    vertices,faces=shape.tessellate(.035,.09)
    color=(.69,.71,.7) if name=='Electronic_BT1' else ((.88,.85,.73) if name=='Electronic_J_DEBUG' else ((.65,.48,.29) if name.startswith('Electronic_C') else (.16,.17,.18)))
    rows.append({'name':name,'vertices':[list(v.toTuple())for v in vertices],'faces':faces,'color':colors.get(name,(.8,.81,.82) if name in magnets else color)})
(OUT/'scene_meshes.json').write_text(json.dumps(rows,separators=(',',':'))+'\n')
# A complete actual-mesh assembly can be opened independently of the V1
# circuit preview. STEP assemblies use exact new bodies and unchanged supplier
# bodies; the display GLB uses the same source tessellations as the review.
chosen=[r for r in rows if not r['name'].startswith('Cap_') or r['name']=='Cap_circular']
scene=trimesh.Scene()
for row in chosen:
    mesh=trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=False)
    mesh.visual.face_colors=np.array([int(255*x)for x in row['color']]+[255],dtype=np.uint8)
    scene.add_geometry(mesh,node_name=row['name'],geom_name=row['name'])
(OUT/'V2_assembled.glb').write_bytes(scene.export(file_type='glb'))
# Keep purchased products as named groups, including their detailed solids.
# Flattening STEP leaves loses the bearing/cell exploded offsets.
assert 'Cap_circular' in kept and 'PCB' in kept and len([n for n in kept if n.startswith('Electronic_')])==27, list(kept)
for state in ['Assembled','Exploded']:
    assembled=cq.Assembly(name='V2_'+state)
    values={**kept,**new}
    for name,shape in values.items():
        dz=0
        if state=='Exploded':
            dz=(-22 if name=='Magnet_Carrier_V2' else (-14 if name in magnets else (-7 if name=='Steel_Backing_V2' else (42 if name=='Cap_circular' else (35 if name=='Magnet' else (15 if name.startswith('Bearing_') else (5 if name.startswith('Electronic_') or name in ['PCB','PCB_Fasteners','Cell'] else 0)))))))
        assembled.add(shape,name=name,color=cq.Color(*colors.get(name,(.7,.72,.74))),loc=cq.Location(cq.Vector(0,0,dz)))
    assembled.save(str(OUT/'Assemblies'/('V2_'+state+'.step')))
report={'passed':True,'physical_tested':False,'force_verified':False,'variant':P['variant'],'parameters_sha256':sha(HERE/'parameters.json'),'builder_sha256':sha(Path(__file__)),'source_circuit_sha256':sha(ROOT/'published.circuit.json'),'preserved_V1_manifest_sha256':sha(V1/'manifest.json'),'changes_confined_to_base_recess':True,'all_caps_byte_identical':True,'cap_styles_checked':cap_checks,'rotation_samples_per_cap':24,'supplier_bodies_checked':len(electronics),'magnet_count':len(magnets),'minimum_pocket_to_pocket_web_mm':min_web,'carrier_inner_wall_mm':inner_wall,'carrier_outer_wall_mm':outer_wall,'carrier_floor_mm':C['pocket_floor_mm'],'base_roof_z_mm':2.4,'steel_to_base_bondline_mm':2.4-S['bottom_z_mm']-S['thickness_mm'],'physical_height_mm':16.4,'encoder_gap_mm':1.8,'printed_product_parts':3,'handled_parts':46,'new_printed_parts':printed,'buy_or_fabricate_not_rigid_print':['36 M0601 magnets','1 low-carbon steel backing ring'],'retained_parts':['one existing Cap variant','6808-ZZ bearing','existing PCBA with CR2450 holder','CR2450 cell','two M2 nylon PCB screws','diametric encoder magnet']}
(OUT/'geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['new_printed_parts','retained_parts','cap_styles_checked']},indent=2),flush=True)
