"""Generate small calibration prints before the full V5 enclosure."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
r=Path(__file__).resolve().parent;p=json.loads((r/'assembly-parameters.json').read_text());b=p['bearing'];out=r.parent/'dist/mechanical/Bearing_Coupons';out.mkdir(parents=True,exist_ok=True)
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
parts={'Bearing_Housing_Coupon':ring(b['housing_diameter_mm']/2,28.8,0,3),
 'Bearing_Shaft_Coupon':ring(18.65,b['shaft_diameter_mm']/2,0,3)}
for diameter in [39.90,40.00,40.05,40.10]:parts['Shaft_'+f'{diameter:.2f}'.replace('.','p')]=ring(18.65,diameter/2,0,3)
for diameter in [52.10,52.00,51.95,51.90]:parts['Housing_'+f'{diameter:.2f}'.replace('.','p')]=ring(diameter/2,28.8,0,3)
for old in out.glob('*.stl'):
 if old.stem not in parts:old.unlink()
reports=[]
for name,shape in parts.items():
 shape=shape.translate((0,0,-shape.BoundingBox().zmin));file=out/f'{name}.stl';cq.exporters.export(shape,str(file),tolerance=.025,angularTolerance=.09)
 m=trimesh.load_mesh(file,process=True);mask=m.nondegenerate_faces(height=1e-6)
 if not mask.all():m.update_faces(mask);m.remove_unreferenced_vertices();m.export(file)
 assert m.is_watertight and m.is_winding_consistent and m.volume>0,name
 reports.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(out/'README.txt').write_text('Print at 100% mm scale using the enclosure material and settings. Test actual 6808-ZZ bearings, starting with the looser variants. Choose a hand push fit that stays seated, rotates freely and has no wobble. Default shaft 40.05mm and housing 51.95mm give nominal 0.05mm diametral interference. Never force a fit or scale complete parts; adjust dimensions and regenerate the base/cap. Measure pull-off, creep and service retention on physical prototypes.\n')
(r.parent/'dist/mechanical/bearing-fit-coupons.json').write_text(json.dumps({'passed':True,'physical_tested':False,'coupons':reports},indent=2)+'\n');print(out)
