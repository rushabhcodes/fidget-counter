"""Replace the supplier's bounding rectangle with a checked curved courtyard.

Keep the imported copper, models and original wrapper byte-for-byte. Only the
assembly courtyard changes: supplier STEP XY projection plus solder lands,
expanded0.20mm. A rectangle's empty corners incorrectly cross a circular PCB.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1]
source=R/'imports/BS_24_B4AA014/BS_24_B4AA014.step'
shape=cq.importers.importStep(str(source)).val()
vertices,faces=shape.tessellate(.01,.05)
points=[(v.x,v.y) for v in vertices]
projection=unary_union([p for f in faces if (p:=Polygon([points[i] for i in f])).area>1e-12])
lands=unary_union([box(x-3.3999932/2,-3.5999928/2,x+3.3999932/2,3.5999928/2) for x in [-15.550007,15.550007]])
occupied=unary_union([projection,lands]);clearance=.20
outline=occupied.buffer(clearance,quad_segs=32).simplify(.002,preserve_topology=True)
assert outline.geom_type=='Polygon' and occupied.difference(outline).area<1e-8
assert outline.buffer(.003).covers(occupied.buffer(clearance))
primitives=[{'type':'circle','radius':14.95},{'type':'rect','width':34.9,'height':7.4}]
native=unary_union([__import__('shapely').geometry.Point(0,0).buffer(14.95,quad_segs=256),box(-17.45,-3.7,17.45,3.7)])
assert occupied.buffer(clearance).difference(native.buffer(.001)).area<.001,'Native courtyard primitives miss occupied supplier geometry'
terminals=[{'x':x,'y':0,'width':3.7999932,'height':3.9999928} for x in [-15.550007,15.550007]]
data={'scope':'Native courtyards cover the solder terminals; full model-derived body courtyard is independently required by check-cr2450-holder.py because compiler outline/drill checks use bounding boxes. Imported pads/STEP/OBJ unchanged.','clearance_mm':clearance,'maximum_tessellation_error_mm':.01,'native_terminal_courtyards':terminals,'outline':[{'x':float(x),'y':float(y)} for x,y in outline.exterior.coords],'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path(__file__),source]}}
(R/'mechanical/battery-holder-courtyard.json').write_text(json.dumps(data,indent=2)+'\n')
print(f'Generated curved holder courtyard with{len(data["outline"])} points; no copper/model modification')
