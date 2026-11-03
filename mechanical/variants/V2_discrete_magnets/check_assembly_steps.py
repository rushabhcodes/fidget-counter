"""Verify delivered exact STEP assemblies, including imported component poses."""
from pathlib import Path
import hashlib,json
import cadquery as cq

H=Path(__file__).resolve().parent;R=H.parents[2];G=H/'generated';results=[]
for state in ['Assembled','Exploded']:
    path=G/'Assemblies'/('V2_'+state+'.step')
    assembly=cq.Assembly.load(str(path))
    objects={obj.name:obj.toCompound() for obj in assembly.children}
    assert len(objects)==72 and len([name for name in objects if name.startswith('Electronic_')])==27
    for name,source in [('Base_V2_Discrete',G/'STEP/Base_V2_Discrete.step'),('Magnet_Carrier_V2',G/'STEP/Magnet_Carrier_V2.step'),('Cap_circular',R/'mechanical/STEP_Parts/Cap_circular.step')]:
        original=cq.importers.importStep(str(source)).val()
        offset=(-22 if name=='Magnet_Carrier_V2' else (42 if name=='Cap_circular' else 0)) if state=='Exploded' else 0
        delivered=objects[name].translate((0,0,-offset))
        assert original.cut(delivered).Volume()+delivered.cut(original).Volume()<.002,(state,name)
        assert max(abs(getattr(original.BoundingBox(),k)-getattr(delivered.BoundingBox(),k)) for k in ['xmin','xmax','ymin','ymax','zmin','zmax'])<1e-5
    assert abs(objects['Steel_Backing_V2'].BoundingBox().zmin-(1.55 if state=='Assembled' else -5.45))<1e-5
    assert abs(objects['Bearing_6808'].BoundingBox().zmin-(6.1 if state=='Assembled' else 21.1))<1e-5
    results.append({'state':state,'objects':len(objects),'supplier_bodies':27,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'critical_poses_and_printed_solids_match':True})
(G/'assembly-step-audit.json').write_text(json.dumps({'passed':True,'physical_tested':False,'assemblies':results},indent=2)+'\n')
print('PASS: both exact V2 STEP assemblies;72 objects each; base/carrier/cap geometry and critical poses retained')
