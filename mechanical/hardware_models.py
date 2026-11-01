"""Detailed, bounded reference geometry for purchased V5 hardware.

Bearing envelope/ball complement: AST 6708 catalog (40 x 50 x 6,
25 x 2.381 mm balls, minimum 0.3 mm corner radius). Shield and cage
construction is representative of a ZZ bearing, not supplier production CAD.
Fastener drives/threads and CR2032 can details are representative; all stay
inside the previously checked hardware envelopes. No manufactured SKU implied.
"""
import math
from functools import lru_cache
import cadquery as cq

STEEL=(.66,.69,.72); CHROME=(.78,.8,.82); SHIELD=(.52,.56,.59)
NYLON=(.83,.84,.8); BRASS=(.62,.47,.25); GASKET=(.10,.11,.12)
def disk(r,z,h):return cq.Workplane('XY').workplane(offset=z).circle(r).extrude(h).val()
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
def compound(shapes):return cq.Compound.makeCompound(list(shapes))
def chamfer(shape,amount):return cq.Workplane(obj=shape).edges().chamfer(amount).val()
def bearing_6708(z):
 mid=z+3
 groove=cq.Solid.makeTorus(22.5,1.211,cq.Vector(0,0,mid))
 inner=chamfer(ring(20,21.65,z,6),.3).cut(groove).clean()
 outer=chamfer(ring(23.35,25,z,6),.3).cut(groove)
 # Shield seats are cut into the outer race, rather than overlapping its metal.
 outer=outer.cut(ring(23.30,24.73,z+.18,.33)).cut(ring(23.30,24.73,z+5.49,.33)).clean()
 balls=[cq.Solid.makeSphere(2.381/2,cq.Vector(22.5*math.cos(i*2*math.pi/25),22.5*math.sin(i*2*math.pi/25),mid),angleDegrees1=-90) for i in range(25)]
 # Paired stamped cage ribbons and non-contact shields, including a raised rim.
 cage=compound([ring(21.7,23.3,mid-1.22,.18),ring(21.7,23.3,mid+1.04,.18)])
 for i in range(25):
  cage=cage.cut(cq.Solid.makeSphere(1.22,cq.Vector(22.5*math.cos(i*2*math.pi/25),22.5*math.sin(i*2*math.pi/25),mid),angleDegrees1=-90))
 rivets=[disk(.16,mid-1.04,2.08).translate((22.5*math.cos((i+.5)*2*math.pi/25),22.5*math.sin((i+.5)*2*math.pi/25),0)) for i in range(25)]
 cage=compound([cage,*rivets])
 shields=compound([ring(21.78,24.70,z+.22,.15).fuse(ring(24.35,24.70,z+.20,.28)).clean(),ring(21.78,24.70,z+5.63,.15).fuse(ring(24.35,24.70,z+5.52,.28)).clean()])
 parts=[('Inner race',inner,STEEL,'steel'),('Outer race',outer,STEEL,'steel'),('25 balls',compound(balls),CHROME,'polished'),('Stamped cage',cage,BRASS,'steel'),('ZZ shields',shields,SHIELD,'steel')]
 return compound(p[1] for p in parts),inner,outer,shields,parts

@lru_cache(maxsize=8)
def screw(radius,length,head_radius,head_height,countersunk=False,nylon=False):
 """Screw at origin, underside of head Z0, stem downward, envelope unchanged."""
 pitch=.4 if radius<1.1 else .45
 stem=cq.Workplane(obj=disk(radius,-length,length)).edges('<Z').chamfer(.10).val()
 # Real helical root grooves, truncated before the tip and under-head land.
 thread_height=length-.55
 cutter_path=cq.Wire.makeHelix(pitch,thread_height,radius-.10)
 cutter=cq.Workplane('XZ').polyline([(radius+.035,-pitch*.35),(radius-.19,0),(radius+.035,pitch*.35)]).close().sweep(cutter_path,isFrenet=True).val().translate((0,0,-length+.22))
 stem=stem.cut(cutter).clean()
 if countersunk:head=cq.Solid.makeCone(radius,head_radius,head_height)
 else:head=cq.Workplane(obj=disk(head_radius,0,head_height)).edges('>Z').fillet(.18).val()
 # Cross recess with a shallow central pilot. The dimensions are illustrative.
 cross=cq.Workplane('XY').workplane(offset=head_height-.55).rect(head_radius*1.35,.42).extrude(.65).val()
 cross=cross.fuse(cross.rotate((0,0,0),(0,0,1),90))
 head=head.cut(cross)
 shape=stem.fuse(head).clean()
 assert shape.isValid() and len(shape.Solids())==1
 return shape

def washer(ri,ro,z,h):return cq.Workplane(obj=ring(ri,ro,z,h)).edges().chamfer(.035).val()
def coin_cell(z):
 # Positive can below; recessed negative lid faces the holder above. OD and
 # total thickness remain exactly 20 x 3.2 mm, as in CR2032 data sheets.
 can=cq.Workplane(obj=disk(10,z,3.07)).edges('<Z').fillet(.18).val()
 can=cq.Workplane(obj=can.cut(disk(9.4,z+2.82,.5))).edges('>Z').fillet(.12).val()
 gasket=ring(8.85,9.35,z+2.84,.20)
 lid=disk(8.85,z+2.84,.36)
 # Engraving lies inside the metal envelope; generic chemistry/size marking.
 text=cq.Workplane('XY').workplane(offset=z+3.16).text('CR2032',2.1,.08,combine=False).val()
 lid=lid.cut(text)
 parts=[('Positive can',can,STEEL,'steel'),('Insulating gasket',gasket,GASKET,'rubber'),('Negative lid',lid,CHROME,'steel')]
 return compound(p[1] for p in parts),parts

def magnet(r,z,h):return cq.Workplane(obj=disk(r,z,h)).edges().chamfer(.06).val()

def spring_path(spec,press=0,segments=280):
 """Seven turns: five active turns and one close-wound turn at each end."""
 height=spec['assembled_length_mm']-press;wire=spec['wire_mm'];radius=(spec['outside_mm']-wire)/2
 points=[]
 for i in range(segments+1):
  turns=7*i/segments
  if turns<1:rise=wire*turns
  elif turns<=6:rise=wire+(height-3*wire)*(turns-1)/5
  else:rise=height-2*wire+wire*(turns-6)
  theta=turns*2*math.pi
  points.append((radius*math.cos(theta),radius*math.sin(theta),spec['seat_z_mm']+wire/2+rise))
 return points

def compression_spring(spec,press=0):
 points=spring_path(spec,press,segments=140)
 path=cq.Wire.assembleEdges([cq.Edge.makeSpline([cq.Vector(*p) for p in points])])
 tangent=cq.Vector(*points[1]).sub(cq.Vector(*points[0]))
 plane=cq.Plane(origin=cq.Vector(*points[0]),normal=tangent)
 return cq.Workplane(plane).circle(spec['wire_mm']/2).sweep(path,isFrenet=True).val()
