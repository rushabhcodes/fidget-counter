"""Independently audit bottom entry, blind roofs, exact assemblies and slicer paths."""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString
from shapely.ops import unary_union
from shapely.affinity import translate

H=Path(__file__).resolve().parent; R=H.parents[2]; G=H/'generated'
P=json.loads((H/'parameters.json').read_text()); M=P['magnet']; B=P['pockets']; E=P['encoder']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slicer',required=True);a=ap.parse_args()
report=json.loads((G/'geometry-audit.json').read_text())
assert report['parameters_sha256']==sha(H/'parameters.json') and report['builder_sha256']==sha(H/'build.py')
assert report['frozen_circuit_sha256']==sha(H.parent/'V1_premade_ring/source/published.circuit.json')
assert report['magnet_count']==20 and report['steel_backing_count']==report['separate_carrier_count']==0
assert report['printed_product_parts']==2 and report['handled_parts']==28
assert report['encoder']==E and E['same_part_as_attachment_discs']
assert E['axis_in_rotor']==[1,0,0] and E['diameter_mm']==6 and E['thickness_mm']==3
original=cq.importers.importStep(str(H.parent/'V1_premade_ring/Base_V1_Premade_Ring.step')).val()
base=cq.importers.importStep(str(G/'STEP/Base_V3_Discs.step')).val()
allowed=cq.Workplane('XY').workplane(offset=.1).circle(29.1).circle(B['annulus_inner_radius_mm']).extrude(B['base_roof_top_z_mm']-.1).val()

def bounded(shape):
    assert shape.isValid() and len(shape.Solids())==1
    assert shape.cut(original).cut(allowed).Volume()<.002,'Added material outside attachment region'
    assert original.cut(shape).cut(allowed).Volume()<.002,'Changed retained upper interface'

def blind_roofs(shape):
    for i in range(M['quantity']):
        t=math.radians(M['first_angle_deg']+i*360/M['quantity'])
        x,y=M['pitch_radius_mm']*math.cos(t),M['pitch_radius_mm']*math.sin(t)
        for z in [.25,1.,3.39]:
            assert not shape.isInside(cq.Vector(x,y,z),1e-6),'Bottom entry or pocket blocked'
        for z in [3.41,3.8,4.39]:
            assert shape.isInside(cq.Vector(x,y,z),1e-6),'Blind stop or roof missing'
        # Inspect the chamfer and cylindrical wall, not only the pocket center.
        assert not shape.isInside(cq.Vector(x+3.24,y,.25),1e-6),'Entry chamfer missing'
        assert shape.isInside(cq.Vector(x+3.24,y,.6),1e-6),'Pocket sidewall missing'

bounded(base);blind_roofs(base)
mutants=[('bearing-interface-loss',lambda:bounded(base.cut(cq.Workplane('XY').box(3,3,3).val().translate((19.5,0,10))))),
         ('punctured-blind-roof',lambda:blind_roofs(base.cut(cq.Workplane('XY').workplane(offset=3.3).center(M['pitch_radius_mm'],0).circle(.5).extrude(2).val())))]
for label,run in mutants:
    try:run()
    except AssertionError:pass
    else:raise AssertionError('Safeguard accepted '+label)
# Re-import the delivered exact assemblies. Check poses for each disc and
# printed base/cap; prohibit a hidden backing or carrier in either deliverable.
assembly_reports=[]
for state in ['Assembled','Exploded']:
    path=G/'Assemblies'/('V3_'+state+'.step')
    assembly=cq.Assembly.load(str(path));objects={o.name:o.toCompound()for o in assembly.children}
    assert len(objects)==54 and len([n for n in objects if n.startswith('Electronic_')])==27
    assert not any('Backing' in n or 'Carrier' in n or 'MagSafe_Ring' in n for n in objects)
    discs={n:s for n,s in objects.items()if n.startswith('Attachment_Disc_')};assert len(discs)==20
    for i,(name,shape)in enumerate(sorted(discs.items())):
        box=shape.BoundingBox();angle=math.radians(M['first_angle_deg']+i*360/20)
        assert abs((box.xmax+box.xmin)/2-M['pitch_radius_mm']*math.cos(angle))<1e-5
        assert abs((box.ymax+box.ymin)/2-M['pitch_radius_mm']*math.sin(angle))<1e-5
        assert abs(box.zmin-(M['phone_face_z_mm']+(14 if state=='Exploded' else 0)))<1e-5
        assert abs(box.xlen-6)<1e-5 and abs(box.ylen-6)<1e-5 and abs(box.zlen-3)<1e-5
    delivered=objects['Base_V3_Discs'].translate((0,0,-32 if state=='Exploded' else 0))
    assert base.cut(delivered).Volume()+delivered.cut(base).Volume()<.002
    assert abs(objects['Bearing_6808'].BoundingBox().zmin-(6.1+(107 if state=='Exploded' else 0)))<1e-5
    encoder=objects['Magnet'].BoundingBox()
    assert abs(encoder.xlen-3)<1e-5 and abs(encoder.ylen-6)<1e-5 and abs(encoder.zlen-6)<1e-5
    assert abs(encoder.zmin-(E['bottom_z_mm']+(130 if state=='Exploded' else 0)))<1e-5
    scene=trimesh.load(G/('V3_'+state.lower()+'.glb'),force='scene')
    assert set(scene.graph.nodes_geometry)==set(objects),'GLB and STEP contain different parts'
    for name,shape in objects.items():
        transform,geometry=scene.graph[name]
        vertices=trimesh.transform_points(scene.geometry[geometry].vertices,transform)
        bb=shape.BoundingBox()
        expected=np.array([[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]])
        assert np.max(np.abs(np.array([vertices.min(axis=0),vertices.max(axis=0)])-expected))<.04,(state,name,'GLB pose differs from STEP')
    assembly_reports.append({'state':state,'objects':54,'discs':20,'supplier_bodies':27,'sha256':sha(path),'GLB_sha256':sha(G/('V3_'+state.lower()+'.glb')),'GLB_matches_STEP_bounds':True})
(G/'assembly-step-audit.json').write_text(json.dumps({'passed':True,'physical_tested':False,'assemblies':assembly_reports},indent=2)+'\n')
work=R/'work/V3-print-audit';work.mkdir(parents=True,exist_ok=True)
version=subprocess.run([a.slicer,'--help'],text=True,capture_output=True,check=True).stdout.splitlines()[0]
parts=[]
for row in report['new_printed_parts']:
    step=H/row['STEP'];stl=H/row['STL'];name=row['name']
    assert name=='Base_V3_Discs' or name.startswith('Cap_')
    assert sha(step)==row['STEP_sha256'] and sha(stl)==row['STL_sha256']
    shape=cq.importers.importStep(str(step)).val();mesh=trimesh.load_mesh(stl,process=True)
    assert shape.isValid() and len(shape.Solids())==1
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume and len(mesh.split())==1
    assert np.isfinite(mesh.vertices).all() and abs(mesh.bounds[0,2])<1e-5
    points=mesh.vertices[np.linspace(0,len(mesh.vertices)-1,60,dtype=int)].copy()
    points[:,2]-=row['print_translation_z_mm']
    if row['print_rotation_x_deg']==180:points[:,1:]*=-1
    assert max(cq.Vertex.makeVertex(*p).distance(shape)for p in points)<.002, 'STL differs from STEP'
    sections={}
    for z in ([.1,2.35,3.0,3.3,4.1,5.0,9.0] if name=='Base_V3_Discs' else [.1,.7,1.25,3.,6.,9.,12.]):
        section=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1]);assert section is not None,(name,z)
        planar,_=section.to_2D();polygons=planar.polygons_full
        assert polygons and all(p.is_valid for p in polygons),(name,z)
        sections[str(z)]=sum(p.area for p in polygons)
    gcode=work/(name+'.gcode');profiles=[R/'mechanical/printing/PETG-0.4-audit.ini']
    support=row['supports']
    if support=='fixed-base':profiles.append(R/'mechanical/printing/base-fixed-supports.ini')
    elif support=='early-rim':profiles.append(R/'mechanical/printing/cap-early-rim-supports.ini')
    elif support=='everywhere':profiles.append(R/'mechanical/printing/supports-everywhere.ini')
    if name=='Cap_thumb_scoop':profiles.append(R/'mechanical/printing/V3-edge-cap-supports.ini')
    if name.startswith('Cap_'):
        assert not shape.isInside(cq.Vector(0,0,E['slot_stop_z_mm']-.01),1e-6),'Edge slot blocked'
        assert shape.isInside(cq.Vector(0,0,E['slot_stop_z_mm']+.01),1e-6),'Slot roof missing'
        assert shape.isInside(cq.Vector(2.2,0,17),1e-6),'Keyed sidewall missing'
    command=[a.slicer]
    for profile in profiles:command+=['--load',str(profile)]
    command+=['--export-gcode','--center','110,110','--output',str(gcode),str(stl)]
    # The headless slicer can stall during startup on this worker. Retry one
    # timeout; never accept partial G-code or waive a nonzero exit status.
    slicer_timeout_retries=0
    for attempt in range(2):
        try:
            result=subprocess.run(command,text=True,capture_output=True,timeout=60)
            break
        except subprocess.TimeoutExpired:
            if attempt:raise
            slicer_timeout_retries+=1
    (work/(name+'.log')).write_text(result.stdout+result.stderr)
    assert result.returncode==0,(name,result.stdout[-1000:],result.stderr[-1000:])
    text=gcode.read_text();assert 'G1' in text and ';TYPE:' in text
    assert not re.search(r'(repaired|non.manifold|empty layers|no extrusions)',result.stdout+result.stderr,re.I), 'Slicer reported a mesh defect'
    kind='';x=y=z=0.;bridges=[];bridge_paths=[];support_paths=[];supports=extrusions=0;layerz=set();meta=[]
    for line in text.splitlines():
        if line.startswith(';TYPE:'):kind=line[6:].strip()
        if line.startswith(';Z:'):layerz.add(float(line[3:]))
        if line.startswith('; estimated printing time') or line.startswith('; filament used [g]'):meta.append(line[2:])
        if not re.match(r'G[01]\s',line):continue
        v={k:float(n)for k,n in re.findall(r'([XYZE])(-?(?:\d+(?:\.\d*)?|\.\d+))',line)}
        nx,ny=v.get('X',x),v.get('Y',y);z=v.get('Z',z)
        length=math.hypot(nx-x,ny-y)
        if v.get('E',0)>0 and length>1e-6:
            extrusions+=1
            if kind.startswith('Support material'):
                supports+=1;support_paths.append((z,LineString([(x,y),(nx,ny)])))
            if kind=='Bridge infill':
                bridges.append(length);bridge_paths.append((z,LineString([(x,y),(nx,ny)])))
        x,y=nx,ny
    assert extrusions>100 and len(layerz)>5,(name,'Missing toolpaths')
    # A bridge-labelled stroke may cross many support interfaces. Audit its
    # actual unsupported gaps instead of treating that entire stroke as air.
    # Use the actual model section under the preceding layer plus actual
    # support extrusions within the configured contact gap; no invented pads.
    coverage={};unsupported=[];without_supports=[]
    for bz,line in bridge_paths:
        if bz not in coverage:
            section=mesh.section(plane_origin=[0,0,bz-.1501],plane_normal=[0,0,1])
            polygons=[]
            if section is not None:
                # Mesh sections are already XY; retain their exact world XY
                # coordinates instead of the section's arbitrary local frame.
                from shapely.geometry import Polygon
                paths=section.discrete
                loops=[Polygon(path[:,:2])for path in paths if len(path)>3]
                solid=unary_union([])
                for loop in loops:solid=solid.symmetric_difference(loop)
                # --center centers the mesh bounding box, which is offset
                # from the rotor axis for asymmetric caps such as triangle.
                polygons.append(translate(solid,xoff=110-mesh.bounds[:,0].mean(),yoff=110-mesh.bounds[:,1].mean()))
            solid=unary_union(polygons)
            near=[path.buffer(.19,cap_style=2)for sz,path in support_paths if bz-.375<=sz<=bz-.125]
            coverage[bz]=(unary_union([solid,*near]),solid)
        supported,solid=coverage[bz]
        def spans(geometry):
            return [g.length for g in getattr(geometry,'geoms',[geometry]) if g.geom_type=='LineString']
        unsupported.extend(spans(line.difference(supported)))
        without_supports.extend(spans(line.difference(solid)))
    max_air=max(unsupported,default=0)
    assert max_air<=5,(name,'Actual unsupported bridge gap exceeds 5mm',max_air)
    if name=='Base_V3_Discs':assert max(without_supports,default=0)>5, 'Support-removal safeguard was not exercised'
    # Automatic supports may legitimately generate no paths on a rim that
    # meets the bridge bound unaided. The base and upright scoop need them.
    if row['supports'] in ['fixed-base','everywhere']:assert supports>0,(name,'Required support paths missing')
    elif support=='none':assert supports==0,(name,'Unexpected support paths')
    parts.append({'name':name,'STL_sha256':sha(stl),'slicer_profiles_sha256':{str(p.relative_to(R)):sha(p)for p in profiles},'first_layer_mm':.2,'layers':len(layerz),'extrusion_segments':extrusions,'support_segments':supports,'maximum_bridge_labelled_line_mm':max(bridges,default=0),'maximum_actual_unsupported_bridge_gap_mm':max_air,'maximum_gap_if_supports_removed_mm':max(without_supports,default=0),'section_areas_mm2':sections,'slicer_estimates_not_measurements':meta,'gcode_sha256':sha(gcode),'gcode_not_distributed':True,'slicer_timeout_retries':slicer_timeout_retries})
result={'passed':True,'physically_printed':False,'force_tested':False,'slicer':version,'actual_slicer_executed':True,'geometry_audit_sha256':sha(G/'geometry-audit.json'),'audit_source_sha256':sha(Path(__file__)),'negative_safeguards_rejected':[x[0]for x in mutants],'profile':'Provisional PETG, 0.4mm nozzle, 0.15mm layers, 4 perimeters; configure actual printer','parts':parts,'updated_caps_sliced':11,'encoder_orientation':'Axial disc on edge; axisX in rotor frame'}
(G/'print-audit.json').write_text(json.dumps(result,indent=2)+'\n')
manifest_parts=[]
for part in report['new_printed_parts']:
    manifest_parts.append({'name':part['name'],'file':str((H/part['STL']).relative_to(R)),'sha256':part['STL_sha256'],'STEP_file':str((H/part['STEP']).relative_to(R)),'STEP_sha256':part['STEP_sha256'],'quantity_per_default_unit':part['quantity_per_default_unit'],'orientation':part['orientation'],'supports':part['supports'],'first_layer_mm':.2})
    manifest_parts[-1]['slicer_profiles']=list(next(row for row in parts if row['name']==part['name'])['slicer_profiles_sha256'])
assert len(manifest_parts)==12 and sum(p['quantity_per_default_unit']for p in manifest_parts)==2
print_manifest={'variant':'V3 bottom discs and same axial encoder on edge','release':P['release'],'physical_qualified':False,'holding_force_verified':False,'default_rigid_part_count':2,'default_cap':'circular','default_files':[p['file']for p in manifest_parts if p['quantity_per_default_unit']],'parts':manifest_parts,'excluded_from_rigid_printing':['21 diameter6x3 axial NdFeB discs','Bearings, PCBA, cell and screws','Assembled/exploded STEP and GLB'],'geometry_audit_sha256':sha(G/'geometry-audit.json'),'actual_slicer_audit_sha256':sha(G/'print-audit.json'),'machine_Gcode_included':False}
(G/'print-ready-manifest.json').write_text(json.dumps(print_manifest,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
