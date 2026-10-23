"""Check real Circuit JSON holes, exact base solid, and the exported PCB mesh."""
from pathlib import Path
import hashlib,json,math
import numpy as np
import cadquery as cq
import trimesh

root=Path(__file__).resolve().parents[1]
c=json.loads((root/'dist/index/circuit.json').read_text())
p=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
audit=json.loads((root/'mechanical/enclosure-validation.json').read_text())['pcb_retention']
board=next(e for e in c if e['type']=='pcb_board')
mounts=[e for e in c if e['type']=='pcb_hole' and abs(e['hole_diameter']-p['pcb_mount']['hole_diameter_mm'])<1e-7]
assert len(mounts)==4
for x,y in audit['mount_centers_mm']:
    assert any(math.hypot(h['x']-x,h['y']-y)<1e-6 for h in mounts),'Circuit and base hole patterns differ'
outline=[(v['x'],v['y']) for v in board['outline']]
pcb=cq.Workplane('XY').workplane(offset=p['pcb_bottom']).polyline(outline).close().extrude(board['thickness']).val()
holes=[e for e in c if e['type']=='pcb_hole']
for h in holes:
    bore=cq.Solid.makeCylinder(h['hole_diameter']/2,board['thickness']+.2,cq.Vector(h['x'],h['y'],p['pcb_bottom']-.1))
    pcb=pcb.cut(bore)
base=cq.importers.importStep(str(root/'mechanical/STEP_Parts/Stationary_Base.step')).val()
intersection=pcb.intersect(base).Volume()
assert intersection<.002,('Printed base passes through real PCB material',intersection)

def hits_material(point,triangles):
    # Barycentric point test against the actual GLB triangles, not a proxy disc.
    a=triangles[:,0];v0=triangles[:,1]-a;v1=triangles[:,2]-a;v2=np.array(point)-a
    den=v0[:,0]*v1[:,1]-v0[:,1]*v1[:,0]
    good=np.abs(den)>1e-12
    u=np.zeros_like(den);v=np.zeros_like(den)
    u[good]=(v2[good,0]*v1[good,1]-v2[good,1]*v1[good,0])/den[good]
    v[good]=(v0[good,0]*v2[good,1]-v0[good,1]*v2[good,0])/den[good]
    return bool(np.any(good&(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)))

def check_glb(file):
    scene=trimesh.load(file,force='scene')
    surfaces=[]
    for node in scene.graph.nodes_geometry:
        transform,name=scene.graph[node]
        mesh=scene.geometry[name].copy();mesh.apply_transform(transform)
        ext=mesh.extents
        if ext[0]>36 and ext[2]>36 and ext[1]<1e-5:
            surfaces.append(mesh.triangles[:,:,[0,2]])
    assert len(surfaces)==2,('Could not identify both native PCB face meshes',len(surfaces))
    reports=[]
    for h in holes:
        inside=0;outside=0
        for triangles in surfaces:
            for angle in np.linspace(0,2*math.pi,24,endpoint=False):
                for scale in [0,.5,.85]:
                    r=h['hole_diameter']/2*scale
                    # The native GLB uses X-left, Y-up, Z-forward.
                    q=[-(h['x']+r*math.cos(angle)),h['y']+r*math.sin(angle)]
                    assert not hits_material(q,triangles),('GLB fills a native drill hole',h['pcb_hole_id'],scale,angle)
                    inside+=1
                r=h['hole_diameter']/2*1.1
                q=[-(h['x']+r*math.cos(angle)),h['y']+r*math.sin(angle)]
                assert hits_material(q,triangles),('GLB drill rim differs from native hole',h['pcb_hole_id'])
                outside+=1
        reports.append({'center_mm':[h['x'],h['y']],'diameter_mm':h['hole_diameter'],'empty_bore_samples':inside,'material_rim_samples':outside})
    return reports

reports=check_glb(root/"dist/index/3d.glb")
published_reports=check_glb(root/"dist/published/3d.glb")
assert audit['pcb_screws']==0 and audit['separate_pcb_retainers']==0
assert audit['minimum_locked_feature_to_hole_clearance_mm']>.2
assert audit['minimum_released_hook_to_hole_clearance_mm']>.15
assert audit['locator_recess_below_board_top_mm']>.3
assert audit['axial_float_mm']>=.15-1e-7
result={'passed':True,'physical_tested':False,'base_to_actual_pcb_intersection_mm3':intersection,
    'mount_centers_mm':audit['mount_centers_mm'],'nominal_edge_web_mm':audit['nominal_pcb_edge_web_mm'],
    'minimum_locked_feature_to_hole_clearance_mm':audit['minimum_locked_feature_to_hole_clearance_mm'],
    'minimum_released_hook_to_hole_clearance_mm':audit['minimum_released_hook_to_hole_clearance_mm'],
    'locator_recess_below_board_top_mm':audit['locator_recess_below_board_top_mm'],
    'retaining_lip_above_board_top_mm':audit['axial_float_mm'],'native_glb_holes':reports,'published_glb_holes':published_reports,
    'sha256':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [root/'dist/index/circuit.json',root/'dist/index/3d.glb',root/'dist/published/circuit.json',root/'dist/published/3d.glb',root/'mechanical/STEP_Parts/Stationary_Base.step']}}
(root/'validation/pcb-mount-clearance.json').write_text(json.dumps(result,indent=2)+'\n')
print('Pass: base has no intersection with real PCB material; all seven native drill holes are open in both GLB faces; no bolts')
