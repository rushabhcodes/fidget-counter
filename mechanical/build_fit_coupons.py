"""Generate small calibration prints before the full V5 enclosure."""
from pathlib import Path
import json,hashlib
import cadquery as cq
import trimesh
r=Path(__file__).resolve().parent;p=json.loads((r/'enclosure-parameters.json').read_text());b=p['bearing'];out=r/'Print_STL/Coupons';out.mkdir(parents=True,exist_ok=True)
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
parts={'Bearing_Housing_Coupon':ring(b['housing_diameter_mm']/2,28.8,0,3),
 'Bearing_Shaft_Coupon':ring(18.65,b['shaft_diameter_mm']/2,0,3),
 'Guide_Post_Coupon':cq.Workplane('XY').box(12,12,1.6).val().translate((0,0,.8)).fuse(cq.Solid.makeCylinder(2.5,4,cq.Vector(0,0,1.6))),
 'Guide_Bore_Coupon':ring(p['press_guide']['bore_diameter_mm']/2,4,0,3)}
carrier=cq.importers.importStep(str(r/'STEP_Parts/Bearing_Carrier.step')).val();z=b['bottom_z_mm']+b['width_mm']
parts['Inner_Thread_Coupon']=carrier.intersect(cq.Solid.makeCylinder(20,2.5,cq.Vector(0,0,z))).translate((0,0,-z))
parts['Inner_Race_Nut']=cq.importers.importStep(str(r/'STEP_Parts/Inner_Race_Nut.step')).val()
reports=[]
for name,shape in parts.items():
 shape=shape.translate((0,0,-shape.BoundingBox().zmin));file=out/f'{name}.stl';cq.exporters.export(shape,str(file),tolerance=.025,angularTolerance=.09)
 m=trimesh.load_mesh(file,process=True);mask=m.nondegenerate_faces(height=1e-6)
 if not mask.all():m.update_faces(mask);m.remove_unreferenced_vertices();m.export(file)
 assert m.is_watertight and m.is_winding_consistent and m.volume>0,name
 reports.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
(out/'README.txt').write_text('Print at 100% scale in mm, using the same material/settings as the enclosure.\n\n1. Test the actual bearing in Housing and Shaft coupons. It should seat by hand with the chosen assembly fit; do not force it.\n2. Slide the Guide Bore over the Guide Post. It must travel freely without excessive rock.\n3. Test the Inner Race Nut on the Inner Thread Coupon. It must screw through the full engagement by hand without splitting.\n4. Adjust explicit fit parameters and regenerate matching complete parts if necessary.\n\nThese coupons do not validate bearing seal lands, spring forces, the actuator, printed endurance, magnetic sensing or RF.\n')
(r.parent/'validation/bearing-fit-coupons.json').write_text(json.dumps({'passed':True,'physical_tested':False,'coupons':reports},indent=2)+'\n');print(out)
