"""Generate small calibration prints before the full V5 enclosure."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
r=Path(__file__).resolve().parent;p=json.loads((r/'enclosure-parameters.json').read_text());b=p['bearing'];out=r/'Print_STL/Coupons';out.mkdir(parents=True,exist_ok=True)
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
parts={'Bearing_Housing_Coupon':ring(b['housing_diameter_mm']/2,28.8,0,3),
 'Bearing_Shaft_Coupon':ring(18.65,b['shaft_diameter_mm']/2,0,3)}
if p.get('cap_retention',{}).get('mode')=='push_fit':
 for diameter in [39.90,40.00,40.05,40.10]:parts['Shaft_'+f'{diameter:.2f}'.replace('.','p')]=ring(18.65,diameter/2,0,3)
 for diameter in [52.10,52.00,51.95,51.90]:parts['Housing_'+f'{diameter:.2f}'.replace('.','p')]=ring(diameter/2,28.8,0,3)
else:
 carrier=cq.importers.importStep(str(r/'STEP_Parts/Stationary_Base.step')).val();z=b['bottom_z_mm']+b['width_mm']
 parts['Inner_Thread_Coupon']=carrier.intersect(cq.Solid.makeCylinder(20,2.5,cq.Vector(0,0,z))).translate((0,0,-z))
 parts['Inner_Race_Nut']=cq.importers.importStep(str(r/'STEP_Parts/Inner_Race_Nut.step')).val()
for old in out.glob('*.stl'):
 if old.stem not in parts:old.unlink()
reports=[]
for name,shape in parts.items():
 if name=='Inner_Race_Nut':shape=shape.rotate((0,0,0),(1,0,0),180)
 shape=shape.translate((0,0,-shape.BoundingBox().zmin));file=out/f'{name}.stl';cq.exporters.export(shape,str(file),tolerance=.025,angularTolerance=.09)
 m=trimesh.load_mesh(file,process=True);mask=m.nondegenerate_faces(height=1e-6)
 if not mask.all():m.update_faces(mask);m.remove_unreferenced_vertices();m.export(file)
 assert m.is_watertight and m.is_winding_consistent and m.volume>0,name
 reports.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(out/'README.txt').write_text('Print at 100% scale in mm, using the same material/settings as the enclosure.\n\n1. Test the actual bearing in Housing and Shaft coupons. It should seat by hand with the chosen assembly fit; do not force it.\n2. Test the Inner Race Nut on the Inner Thread Coupon. It must screw through the full engagement by hand without splitting.\n3. Adjust explicit fit parameters and regenerate matching complete parts if necessary.\n\nThese coupons do not validate bearing seal lands, printed endurance, magnetic sensing or RF.\n')
(r.parent/'validation/bearing-fit-coupons.json').write_text(json.dumps({'passed':True,'physical_tested':False,'coupons':reports},indent=2)+'\n');print(out)

if p.get('cap_retention',{}).get('mode')=='push_fit':
 (out/'README.txt').write_text('PETG fit coupons; print at100% mm scale with the same orientation and profile as the product.\nTest actual6808-ZZ samples in the shaft/housing diameter variants. Start from the looser fits. Select a light hand push fit that stays seated, rotates freely and shows no wobble. Never force a tight fit; adjust explicit diameter parameters and regenerate matching base/cap. The default is40.05mm shaft and51.95mm housing, nominal0.05mm diametral interference.\nCalibrated diameter choice, assembly/pull-off force, creep, endurance, shield/race contact and Hall/RF performance remain unqualified. There are no thread or nut coupons in this revision.\n')
