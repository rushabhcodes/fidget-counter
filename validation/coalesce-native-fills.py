"""Union existing native fill fragments; never run a zone filler or add copper."""
import json,sys
from shapely.geometry import Polygon
from shapely.ops import unary_union

rows=json.load(sys.stdin);result=[]
for row in rows:
 fragments=[Polygon(p['outer'],p['holes']).buffer(0)for p in row['fragments']]
 geometry=unary_union(fragments)
 polygons=list(geometry.geoms)if geometry.geom_type=='MultiPolygon'else[geometry]
 assert all(p.geom_type=='Polygon'and p.is_valid for p in polygons)
 result.append({'zone_index':row['zone_index'],'fragments_before':len(fragments),
  'polygons':[{'outer':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1]for h in p.interiors]}for p in polygons]})
json.dump(result,sys.stdout)
