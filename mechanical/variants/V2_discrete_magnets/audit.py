"""Independent V2 geometry/print audit; actual slicer execution is required."""
from pathlib import Path
import argparse, hashlib, json, math, re, subprocess
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString
from shapely.ops import unary_union
from shapely.affinity import translate

H=Path(__file__).resolve().parent; R=H.parents[2]; G=H/'generated'
P=json.loads((H/'parameters.json').read_text()); M=P['magnet']; C=P['carrier']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--slicer',required=True);a=ap.parse_args()
report=json.loads((G/'geometry-audit.json').read_text())
assert report['parameters_sha256']==sha(H/'parameters.json') and report['builder_sha256']==sha(H/'build.py')
assert report['source_circuit_sha256']==sha(R/'published.circuit.json')
original=cq.importers.importStep(str(H.parent/'V1_premade_ring/Base_V1_Premade_Ring.step')).val()
base=cq.importers.importStep(str(G/'STEP/Base_V2_Discrete.step')).val()
carrier=cq.importers.importStep(str(G/'STEP/Magnet_Carrier_V2.step')).val()
allowed=cq.Workplane('XY').workplane(offset=.1).circle(29.1).circle(21.15).extrude(2.3).val()

def bounded(shape):
    assert shape.isValid() and len(shape.Solids())==1
    assert shape.cut(original).Volume()<.002, 'Added material outside the inherited base'
    assert original.cut(shape).cut(allowed).Volume()<.002, 'Changed a retained interface'

def floor_present(shape):
    for radius in M['row_center_radii_mm']:
        for station in range(M['stations']):
            t=math.radians(station*360/M['stations'])
            for z in [.21,.35,.49]:
                assert shape.isInside(cq.Vector(radius*math.cos(t),radius*math.sin(t),z),1e-6), 'Missing carrier floor'
            assert not shape.isInside(cq.Vector(radius*math.cos(t),radius*math.sin(t),.51),1e-6), 'Pocket too shallow'

bounded(base);floor_present(carrier)
# Prove safeguards reject actual off-scope geometry loss and a punctured floor.
mutants=[('bearing-interface-loss',lambda:bounded(base.cut(cq.Workplane('XY').box(4,4,4).val().translate((19.7,0,10))))),
         ('punctured-pocket-floor',lambda:floor_present(carrier.cut(cq.Workplane('XY').workplane(offset=.1).center(23.3,0).circle(.5).extrude(1).val())))]
for label,run in mutants:
    try:run()
    except AssertionError:pass
    else:raise AssertionError('Safeguard accepted '+label)
assert M['phone_facing_poles']==['S','N'] and M['magnetization']=='through 1 mm thickness'
work=R/'work/V2-print-audit';work.mkdir(parents=True,exist_ok=True)
version=subprocess.run([a.slicer,'--help'],text=True,capture_output=True,check=True).stdout.splitlines()[0]
parts=[]
for row in report['new_printed_parts']:
    step=H/row['STEP'];stl=H/row['STL'];name=row['name']
    assert sha(step)==row['STEP_sha256'] and sha(stl)==row['STL_sha256']
    shape=cq.importers.importStep(str(step)).val();mesh=trimesh.load_mesh(stl,process=True)
    assert shape.isValid() and len(shape.Solids())==1
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume and len(mesh.split())==1
    assert np.isfinite(mesh.vertices).all() and abs(mesh.bounds[0,2])<1e-5
    points=mesh.vertices[np.linspace(0,len(mesh.vertices)-1,60,dtype=int)].copy();points[:,2]+=shape.BoundingBox().zmin
    assert max(cq.Vertex.makeVertex(*p).distance(shape)for p in points)<.002, 'STL differs from STEP'
    sections={}
    for z in ([.075,.225] if name=='Magnet_Carrier_V2' else [.1,2.35,3.0,5.0,9.0]):
        section=mesh.section(plane_origin=[0,0,z],plane_normal=[0,0,1]);assert section is not None,(name,z)
        planar,_=section.to_2D();polygons=planar.polygons_full
        assert polygons and all(p.is_valid for p in polygons),(name,z)
        sections[str(z)]=sum(p.area for p in polygons)
    gcode=work/(name+'.gcode');profiles=[R/'mechanical/printing/PETG-0.4-audit.ini']
    if name=='Base_V2_Discrete':profiles.append(R/'mechanical/printing/base-fixed-supports.ini')
    command=[a.slicer]
    for profile in profiles:command+=['--load',str(profile)]
    if name=='Magnet_Carrier_V2':command+=['--first-layer-height','0.15']
    command+=['--export-gcode','--center','110,110','--output',str(gcode),str(stl)]
    result=subprocess.run(command,text=True,capture_output=True,timeout=180)
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
                polygons.append(translate(solid,xoff=110,yoff=110))
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
    if name=='Base_V2_Discrete':assert max(without_supports,default=0)>5, 'Support-removal safeguard was not exercised'
    assert (supports>0) if name=='Base_V2_Discrete' else (supports==0)
    parts.append({'name':name,'STL_sha256':sha(stl),'slicer_profiles_sha256':{str(p.relative_to(R)):sha(p)for p in profiles},'first_layer_mm':.15 if name=='Magnet_Carrier_V2' else .2,'layers':len(layerz),'extrusion_segments':extrusions,'support_segments':supports,'maximum_bridge_labelled_line_mm':max(bridges,default=0),'maximum_actual_unsupported_bridge_gap_mm':max_air,'maximum_gap_if_supports_removed_mm':max(without_supports,default=0),'section_areas_mm2':sections,'slicer_estimates_not_measurements':meta,'gcode_sha256':sha(gcode),'gcode_not_distributed':True})
result={'passed':True,'physically_printed':False,'force_tested':False,'slicer':version,'actual_slicer_executed':True,'geometry_audit_sha256':sha(G/'geometry-audit.json'),'audit_source_sha256':sha(Path(__file__)),'negative_safeguards_rejected':[x[0]for x in mutants],'profile':'Provisional PETG, 0.4mm nozzle, 0.15mm layers, 4 perimeters; configure actual printer','parts':parts,'unchanged_cap_prints':'Use existing cap-specific print manifest and slicer results; every cap STEP hash retained by V2 builder'}
(G/'print-audit.json').write_text(json.dumps(result,indent=2)+'\n')
cap_manifest=json.loads((R/'mechanical/print-ready-manifest.json').read_text())
cap_parts=[part for part in cap_manifest['parts'] if part['name'].startswith('Cap_')]
assert len(cap_parts)==11
manifest_parts=[]
for part in report['new_printed_parts']:
    manifest_parts.append({'name':part['name'],'file':str((H/part['STL']).relative_to(R)),'sha256':part['STL_sha256'],'STEP_file':str((H/part['STEP']).relative_to(R)),'STEP_sha256':part['STEP_sha256'],'quantity_per_default_unit':1,'orientation':'Phone face down','supports':'fixed-base' if part['name']=='Base_V2_Discrete' else 'none','first_layer_mm':.2 if part['name']=='Base_V2_Discrete' else .15})
for part in cap_parts:
    for key in ['file','STEP_file']:assert sha(R/part[key])==part['sha256' if key=='file' else 'STEP_sha256']
    manifest_parts.append({key:part[key]for key in ['name','file','sha256','STEP_file','STEP_sha256','quantity_per_default_unit','orientation','supports']})
print_manifest={'variant':'V2 individual magnets','physical_qualified':False,'holding_force_verified':False,'default_rigid_part_count':3,'default_cap':'circular','default_files':[p['file']for p in manifest_parts if p['quantity_per_default_unit']],'parts':manifest_parts,'excluded_from_rigid_printing':['36 attachment magnets','Steel backing STEP/DXF','Bearings, PCBA, cell, screws and encoder magnet','Assembled/exploded STEP and GLB'],'geometry_audit_sha256':sha(G/'geometry-audit.json'),'actual_slicer_audit_sha256':sha(G/'print-audit.json'),'unchanged_caps_slicer_audit_sha256':sha(R/'validation/print-readiness.json'),'machine_Gcode_included':False}
(G/'print-ready-manifest.json').write_text(json.dumps(print_manifest,indent=2)+'\n')
print(json.dumps(result,indent=2),flush=True)
