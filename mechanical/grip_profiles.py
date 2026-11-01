"""Interchangeable exterior grip profiles; the bearing drum carries their loads."""
import math
import cadquery as cq
from shapely.geometry import Polygon, LineString

def disk(r,z,h,x=0,y=0):return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h).val()
def ring(ri,ro,z,h):return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
def box(sx,sy,sz,x=0,y=0,z=0):return cq.Workplane('XY').box(sx,sy,sz).val().translate((x,y,z+sz/2))
def radial(r,length,width,z,h,angle):return box(length,width,h,x=r,z=z).rotate((0,0,0),(0,0,1),angle)
def comp(shapes):return cq.Compound.makeCompound(shapes)
def fused(shapes):
    result=shapes[0]
    for s in shapes[1:]:result=result.fuse(s)
    return result.clean()
def hex_prism(x,y,z,h,across_flats):
    return cq.Workplane('XY').workplane(offset=z).center(x,y).polygon(6,across_flats/math.cos(math.pi/6)).extrude(h).val()
def extrude_polygon(poly,z,h):
    return cq.Workplane("XY").workplane(offset=z).polyline(list(poly.exterior.coords)[:-1]).close().extrude(h).val()

def make_grip(style, parameters):
    P=parameters
    deck=P["cap_deck_bottom"];top=P["overall_height"];skirt_inner=P["cap_skirt_inner_radius"]
    radius=P['cap_max_diameter']/2
    if style=='circular':
        shape=disk(radius-.45,deck,top-deck).fuse(ring(skirt_inner,radius-.45,P['cap_edge_bottom'],deck-P['cap_edge_bottom']))
        shape=shape.fuse(*[radial(radius-.35,.7,.6,P['cap_edge_bottom'],top-P['cap_edge_bottom'],i*7.5) for i in range(48)])
        shape=shape.intersect(disk(radius,P['cap_edge_bottom'],top-P['cap_edge_bottom']))
        for i in range(24):shape=shape.cut(radial(23.0,9.0,.8,top-.25,.4,i*15))
    elif style=='ships_wheel':
        shapes=[disk(9.0,deck,top-deck),ring(27.0,29.0,P['cap_edge_bottom'],top-P['cap_edge_bottom'])]
        for i in range(6):
            angle=i*60; t=math.radians(angle)
            shapes.extend([radial(19.0,22.0,5.0,deck,top-deck,angle),disk(1.8,P['cap_edge_bottom'],top-P['cap_edge_bottom'],29.0*math.cos(t),29.0*math.sin(t))])
        shape=fused(shapes)
    elif style=='turbine_wheel':
        shapes=[disk(17.5,deck,top-deck),ring(27,30.35,P['cap_edge_bottom'],top-P['cap_edge_bottom'])]
        for i in range(8):
            path=[]
            for j in range(33):
                q=j/32; r=15.0+13.5*q; theta=math.radians(i*45+34*q)
                path.append((r*math.cos(theta),r*math.sin(theta)))
            shapes.append(extrude_polygon(LineString(path).buffer(2.0,cap_style=1,join_style=1),deck,top-deck))
        shape=fused(shapes)
    else:
        if style in ['rounded_triangle','rounded_hexagon','rounded_square']:
            n={'rounded_triangle':3,'rounded_hexagon':6,'rounded_square':4}[style]
            r,b={'rounded_triangle':(21,9.8),'rounded_hexagon':(26.3,4.5),'rounded_square':(22.0,8.8)}[style]
            poly=Polygon([(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n)) for i in range(n)]).buffer(b,quad_segs=32)
        else:
            n,minimum={'scalloped_coin':(12,28.0),'petal_flower':(6,25.8),'four_leaf_clover':(4,24.0),'wave_rim':(8,28.4),'thumb_scoop':(6,29.2)}[style]
            points=[]
            for i in range(720):
                theta=i*2*math.pi/720
                r=minimum+(radius-minimum)*(.5+.5*math.cos(n*theta))
                points.append((r*math.cos(theta),r*math.sin(theta)))
            poly=Polygon(points)
        shape=extrude_polygon(poly,P['cap_edge_bottom'],top-P['cap_edge_bottom'])
        shape=shape.cut(disk(skirt_inner,P['cap_edge_bottom']-.1,deck-P['cap_edge_bottom']+.1))
        shape=shape.intersect(disk(radius,P['cap_edge_bottom'],top-P['cap_edge_bottom']))
        if style=='thumb_scoop':
            # Three 0.6 mm deep spherical dishes, in the upper grip surface.
            for angle in [60,180,300]:
                t=math.radians(angle); sphere=cq.Solid.makeSphere(50,cq.Vector(22*math.cos(t),22*math.sin(t),top+49.4),angleDegrees1=-90,angleDegrees2=90)
                shape=shape.cut(sphere)
    # A common keep-out clears the stationary guide and snap clips during rotation
    # and the full press stroke, for every interchangeable shape.
    shape=shape.cut(disk(skirt_inner,P['cap_edge_bottom']-.1,deck-P['cap_edge_bottom']+.1))
    return shape.clean()
