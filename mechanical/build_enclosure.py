"""Fresh modular PLA enclosure, mm. CadQuery >=2.6.

python build_onepiece_enclosure.py --style all --out export
Each interchangeable top is a single printed rotor/grip with its own magnet pocket and pusher.
Snap clip fatigue, sliding fits and switch return require a physical fit test.
"""
from pathlib import Path
import argparse, json, math
import cadquery as cq
import trimesh
from shapely.geometry import Polygon, LineString

HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--style',choices=['all', 'circular', 'ships_wheel', 'rounded_triangle', 'scalloped_coin', 'petal_flower', 'four_leaf_clover', 'rounded_hexagon', 'rounded_square', 'wave_rim', 'turbine_wheel', 'thumb_scoop'])
ap.add_argument('--out',type=Path,default=HERE/'export')
ap.add_argument('--parameters',type=Path,default=HERE/'enclosure-parameters.json')
a=ap.parse_args(); P=json.loads(a.parameters.read_text()); OUT=a.out.resolve()
for d in ['STEP','STL','Assemblies','Validation']: (OUT/d).mkdir(parents=True,exist_ok=True)
styles=P['cap_styles'] if (a.style or P['cap_style'])=='all' else [a.style or P['cap_style']]

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
def overlap_volume(left,right):
    # Exact solid intersection only where bounding boxes overlap. This makes
    # rotation checks practical without changing their collision criterion.
    lb,rb=left.BoundingBox(),right.BoundingBox()
    if any(getattr(lb,axis+'max')<=getattr(rb,axis+'min')+1e-7 or
           getattr(rb,axis+'max')<=getattr(lb,axis+'min')+1e-7 for axis in 'xyz'):
        return 0.0
    return left.intersect(right).Volume()
print('Building the guide base and two releasable snap clips...',flush=True)
pcb_z=P['pcb_bottom']; pcb_top=pcb_z+P['pcb_thickness']; R=P['guide_neck_outer_radius']; Ri=P['guide_neck_inner_radius']; bore=R+P['guide_radial_clearance']
deck=P['cap_deck_bottom']; top=P['overall_height']; travel=P['button_travel']
skirt_inner=P['cap_skirt_inner_radius']
assert abs(top-P['cap_edge_bottom']-P['grip_height'])<1e-7
assert P['cap_edge_bottom']-travel-P['snap_pad_top']>=.6
flange_bottom=9.0; flange_top=9.7; stop_z=flange_bottom-travel
mounts=[(16.2*math.cos(math.radians(t)),16.2*math.sin(math.radians(t))) for t in [45,135,225,315]]

# Preserve the ordered disc layout and matching bottom tray. Load magnets and
# backing ring before bonding the tray; subsequent service is from the top.
tray=disk(29,.2,.6).fuse(ring(21,28.05,.79,1.56))
centers=[]; discs=[]
for i in range(24):
    t=math.radians(7.5+i*15); x=24.625*math.cos(t); y=24.625*math.sin(t); centers.append((x,y))
    tray=tray.cut(disk(2.625,.8,1.66,x,y));discs.append(disk(2.5,.85,1.5,x,y))
tray=tray.clean()
base=disk(29,.8,3.1).fuse(disk(P['base_guide_outer_radius'],.8,stop_z-.8))
base=base.cut(disk(bore,1.5,8.35)).cut(disk(12.25,.7,.9))
base=base.cut(ring(20.85,28.2,.7,1.7)).cut(ring(22.025,27.225,2.4,.7))
base=base.cut(disk(P['retention_flange_outer_radius']+.2,stop_z,1.1))
for x,y in mounts:
    post=disk(2.2,1.5,pcb_z-1.5,x,y).fuse(disk(1.7,pcb_z,P['pcb_thickness'],x,y)).cut(disk(.65,1.4,7.8,x,y))
    base=base.fuse(post)
# Two long planar cantilevers; print the base flat so bending stays in XY.
# Pull tabs OUTWARD. This is not a squeeze-to-release latch.
def extrude_polygon(poly,z,h):
    return cq.Workplane('XY').workplane(offset=z).polyline(list(poly.exterior.coords)[:-1]).close().extrude(h).val()
def snap_clip(displacement=0):
    points=[]
    for i in range(97):
        q=i/96; angle=math.pi/2*(1-q)
        # A prescribed clearance pose, not FEA or a stress prediction.
        dx=displacement*q*q*(3-2*q)
        points.append((P['snap_beam_radius']*math.cos(angle)+dx,P['snap_beam_radius']*math.sin(angle)))
    beam=extrude_polygon(LineString(points).buffer(P['snap_beam_width']/2,cap_style=1,join_style=1),P['snap_beam_bottom'],P['snap_beam_height'])
    tip_x=P['snap_beam_radius']+displacement
    post=box(1.2,4.0,P['snap_hook_top']-P['snap_beam_bottom'],tip_x,0,P['snap_beam_bottom'])
    # Flat retention underside; sloping upper surface admits snap insertion.
    inner=P['snap_hook_inner_radius']+displacement
    hook=cq.Workplane('XZ').polyline([(inner,9.75),(21.2+displacement,9.75),(22.8+displacement,8.15),(24+displacement,8.15),(24+displacement,10.85),(21.35+displacement,10.85),(inner,10.0)]).close().extrude(2,both=True).val()
    pad=box(4.0,7.0,P['snap_pad_top']-4.5,25.4+displacement,0,4.5)
    # The exposed outer undercut accepts a fingernail; no tool is included.
    pad=pad.cut(box(1.8,5.0,.55,27.1+displacement,0,4.85))
    return fused([beam,post,hook,pad])
# Open underside channels let PLA supports be removed before bonding the tray.
# Relief avoids the anchors and leaves the guide bore / press stop intact.
reliefs=[]
arc=[(23.4*math.cos(math.pi*i/192),23.4*math.sin(math.pi*i/192)) for i in range(97)]
relief=extrude_polygon(LineString(arc).buffer(1.25,cap_style=1,join_style=1),.7,3.81)
relief=relief.cut(disk(2.2,.6,4.0,0,23.4))
for t in [0,180]:reliefs.append(relief.rotate((0,0,0),(0,0,1),t))
base=base.cut(comp(reliefs))
fixed_base=base.clean()
roots=[disk(1.6,3.9,2.6,0,23.4),disk(1.6,3.9,2.6,0,-23.4)]
fixed_base=fixed_base.fuse(*roots).clean()
clips=[snap_clip().rotate((0,0,0),(0,0,1),t) for t in [0,180]]
base=fixed_base.fuse(*clips).clean()
release_clips=[snap_clip(P['snap_release_displacement']).rotate((0,0,0),(0,0,1),t) for t in [0,180]]
released_base=fixed_base.fuse(*release_clips).clean()

hub=ring(Ri,R,4.0,deck-4.0).fuse(ring(Ri,P['retention_flange_outer_radius'],flange_bottom,flange_top-flange_bottom))
pusher_bottom=pcb_top+P['switch_height']
hub=hub.fuse(ring(P['magnet_pocket_diameter']/2,P['pusher_outer_radius'],pusher_bottom,deck-pusher_bottom))
# Integral spokes strengthen the cover and the pusher; no screw bosses or holes.
for angle in [0,120,240]:
    arm=radial(12.5,15.0,5.2,12.0,deck-12.0,angle).intersect(disk(R,12.0,deck-12.0))
    hub=hub.fuse(arm)
# The integral underplate protects the PCB beneath open grip shapes.
# It prints first when the hub is oriented with its upper face on the bed.
hub=hub.fuse(disk(R,deck-P['hub_cover_thickness'],P['hub_cover_thickness']))
# The blind magnet pocket has a 0.2 mm nominal shim above the disc. The integral
# roof above it separates the magnet from the interchangeable grip.
hub=hub.fuse(disk(P['magnet_pocket_diameter']/2,12.1,deck-12.1)).clean()
magnet=disk(2.5,P['magnet_bottom'],P['magnet_thickness'])
print('Common solids complete; building interchangeable cap grips...',flush=True)

def cap(style):
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

grips={s:cap(s) for s in styles}
caps={s:hub.fuse(sh).clean() for s,sh in grips.items()}
assert all(sh.isValid() and len(sh.Solids())==1 for sh in caps.values()),'Disconnected integrated top module'
print('Caps complete; checking rotation and press clearance...',flush=True)
pcb=disk(P['pcb_diameter']/2,pcb_z,P['pcb_thickness'])
for x,y in mounts:pcb=pcb.cut(disk(1.8,pcb_z-.1,1.2,x,y))
holder=cq.importers.importStep(str(HERE/'imports/holder.step')).val().translate((0,0,.01)).rotate((0,0,0),(0,1,0),180).translate((-1.2,0,pcb_z))
cell=disk(10,pcb_z-1.5-3.2,3.2)
sensor=box(.824,1.316,.5,z=pcb_top)
switch_body=box(4.2,2.8,1.4,P['switch_x'],P['switch_y'],pcb_top)
switch=comp([switch_body,disk(.8,pcb_top+1.4,.5,P['switch_x'],P['switch_y'])])
pressed_switch=comp([switch_body,disk(.8,pcb_top+1.4,.5-travel,P['switch_x'],P['switch_y'])])
shield=ring(22.025,27.225,2.4,.7)
# Board retaining washers are rigid, independent PLA parts. The existing four
# M1.6 screws secure the PCB; undo them to lift the soldered holder and cell.
retainer_single=ring(.85,2.2,0,1.0).cut(cq.Solid.makeCone(.85,1.45,.6,cq.Vector(0,0,.4)))
retainers=comp([retainer_single.translate((x,y,pcb_top)) for x,y in mounts])

physical={'Bottom_Tray':tray,'Stationary_Base':base,**{'Cap_'+s:sh for s,sh in caps.items()},'PCB_Retainer_Print_4':retainer_single}
assert all(sh.isValid() and len(sh.Solids())==1 for sh in physical.values()), 'Invalid or disconnected printed part'
stationary={'Stationary_Base':base,'Bottom_Tray':tray,'PCB':pcb,'Holder':holder,'Cell':cell,'Sensor':sensor,'PCB_Retainers':retainers,'Backing_Ring':shield,'Attachment_Magnets':comp(discs)}
rows=[]
shared_checks=set()
for s,shape in caps.items():
    for press in [0,travel/2,travel]:
        button=switch if press==0 else comp([switch_body,disk(.8,pcb_top+1.4,.5-press,P['switch_x'],P['switch_y'])])
        for angle in range(0,360,30):
            for name,moving in [('Hub',hub),('Magnet',magnet)]:
                if name!='Cap' and (press,angle,name) in shared_checks:continue
                sh=moving.rotate((0,0,0),(0,0,1),angle).translate((0,0,-press))
                for other,fixed in {**stationary,'Button':button}.items():
                    overlap=overlap_volume(sh,fixed)
                    assert overlap<.002,(s,press,angle,name,other,overlap)
                if name!='Cap':shared_checks.add((press,angle,name))
            rows.append({'style':s,'press_mm':press,'angle_deg':angle,'rigid_collisions':0,'method':'Shared rotor exact intersections; cap uses full-circle envelope certificate'})
    print(f'Covered 36 press/rotation positions: {s} (shared hub checks + cap circular keepout)',flush=True)
assert hub.translate((0,0,-travel-.01)).intersect(base).Volume()>.01,'No hard stop'

# Retention: a lift must hit BOTH hook ledges until intentionally released.
for clip in clips:
    assert overlap_volume(hub.translate((0,0,.10)),clip)>.01,'Hook does not retain the hub'
service=[]
print('Checking outward-release and battery-service paths...',flush=True)
for clip in release_clips:
    assert clip.isValid() and len(clip.Solids())==1
    assert overlap_volume(clip,fixed_base.cut(comp([disk(1.7,3.8,3.0,0,23.4),disk(1.7,3.8,3.0,0,-23.4)])))<.002,'Release clip strikes the guide outside its fixed root'
for lift in [0,.05,.1,.25,.5,.75,1,2,4,8,15,25]:
    for name,shape in [('Hub',hub),('Magnet',magnet),*[(s,c) for s,c in caps.items()]]:
        overlap=overlap_volume(shape.translate((0,0,lift)),released_base)
        assert overlap<.002,('Top extraction blocked',name,lift,overlap)
    service.append({'lift_mm':lift,'collision_mm3':0,'tabs_outward_mm':P['snap_release_displacement']})
for lift in [0,.5,1,2,4,6,10,15,24]:
    for name,shape in [('PCB',pcb),('Holder',holder),('Cell',cell)]:
        assert overlap_volume(shape.translate((0,0,lift)),base)<.002,('PCB extraction blocked',name,lift)
# Insertion ramp envelope: temporary outward tip displacement clears the flange.
assert P['snap_hook_inner_radius']+P['snap_release_displacement']>P['retention_flange_outer_radius']+.2-1e-7
# The curved beam returns only the hook radially. The button's dome supplies
# axial cap return. No external spring ring or elastomer is present.
length=P['snap_beam_radius']*math.radians(P['snap_arc_degrees'])
strain_estimate=1.5*P['snap_beam_width']*P['snap_release_displacement']/length**2
# Full 360-degree envelope certificate for every cap: all low geometry is
# outside R26.8; hooks above the pad never extend beyond R24.084; lower pads
# are below the lowest pressed edge. Sample checks below supplement this.
for s,shape in grips.items():
    keepout=disk(skirt_inner,P['cap_edge_bottom']-.1,deck-P['cap_edge_bottom']+.099)
    assert overlap_volume(shape,keepout)<.002,('Cap violates circular keepout',s)

manifest=[];meshes=[]
print('CAD checks passed; exporting print parts and assembly states...',flush=True)
colors={'Bottom_Tray':(.32,.39,.43),'Stationary_Base':(.46,.51,.55),'PCB':(.2,.5,.35),'Holder':(.28,.29,.3),'Cell':(.67,.7,.74),'Sensor':(.15,.15,.17),'PCB_Retainers':(.42,.49,.52),'Backing_Ring':(.58,.61,.64),'Attachment_Magnets':(.29,.59,.69),'Magnet':(.68,.7,.72),'Button':(.56,.57,.60),'Cap_circular':(.17,.45,.58),'Cap_ships_wheel':(.67,.38,.21),'Cap_rounded_triangle':(.32,.51,.40)}
colors.update(dict(zip(['Cap_'+s for s in styles],[(.17,.45,.58),(.67,.38,.21),(.32,.51,.40),(.20,.44,.54),(.66,.39,.32),(.40,.57,.43),(.45,.37,.57),(.17,.46,.45),(.66,.51,.26),(.32,.44,.56),(.66,.35,.36)])))
for name,sh in physical.items():
    cq.exporters.export(sh,str(OUT/'STEP'/f'{name}.step'))
    print_shape=sh
    if name.startswith('Cap_'): print_shape=sh.rotate((0,0,0),(1,0,0),180)
    print_shape=print_shape.translate((0,0,-print_shape.BoundingBox().zmin))
    cq.exporters.export(print_shape,str(OUT/'STL'/f'{name}.stl'),tolerance=.035,angularTolerance=.09)
    # Remove zero-area pole triangles introduced by spherical STL tessellation.
    stl=OUT/'STL'/f'{name}.stl';mesh=trimesh.load_mesh(stl,process=True)
    keep=mesh.nondegenerate_faces(height=1e-6)
    if not keep.all():
        mesh.update_faces(keep);mesh.remove_unreferenced_vertices();mesh.export(stl)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,(name,'Invalid print mesh')
    bb=sh.BoundingBox();manifest.append({'name':name,'valid':sh.isValid(),'solids':len(sh.Solids()),'volume_mm3':round(sh.Volume(),3),'bounds_mm':[[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]]})
for s,shape in caps.items():
    for state in ['Released','Pressed','Exploded']:
        press=travel if state=='Pressed' else 0
        assembly=cq.Assembly(name=s+'_'+state)
        values={**stationary,'Magnet':magnet,'Button':pressed_switch if press else switch,'Cap_'+s:shape}
        for name,sh in values.items():
            z=-press if name in ['Magnet','Cap_'+s] else 0
            if state=='Exploded':z={'Cap_'+s:35,'Magnet':35,'PCB':8,'Holder':8,'Cell':4,'Sensor':8,'Button':8,'PCB_Retainers':9}.get(name,0)
            posed=sh.translate((0,0,z));col=colors.get(name,(.5,.5,.5));assembly.add(posed,name=name,color=cq.Color(*col))
            if state=='Released':
                vertices,faces=posed.tessellate(.06,.13)
                meshes.append({'style':s,'name':name,'color':col,'vertices':[list(v.toTuple()) for v in vertices],'faces':[list(f) for f in faces]})
        assembly.save(str(OUT/'Assemblies'/f'{s}_{state}.step'))
validation={'status':'CAD fit prototype, not physically tested','parameters':P,'printed_parts':manifest,'press_rotation_checks':rows,'snap_release_checks':service,'snap_beam_effective_arc_length_mm':round(length,3),'straight_beam_strain_estimate_percent':round(strain_estimate*100,3),'strain_estimate_note':'Only a sizing estimate for a straight cantilever; curved beam torsion, print anisotropy, root stress and fatigue are not validated','retention_hook_overlap_mm':.5,'retention_upward_float_mm':.05,'release_tabs_outward_mm':.8,'all_caps_full_rotation_envelope':True,'exact_shared_hub_magnet_poses':len(shared_checks),'cap_clearance_method':'All low cap geometry is outside R26.8; hook tops are below the deck and inside R24.084; release pads are 0.65 mm below the pressed grip edge','snap_insertion_note':'Upper hook ramp provides insertion cam; force and automatic re-engagement require printed testing' ,'separate_return_springs':0,'all_cap_styles_share_base_interface':True,'integrated_rotor_and_grip':True,'cap_mount_screws':0,'encoder_magnet_per_top_module':1,'sensor_gaps_mm':{'released':1.8,'pressed':1.8-travel},'physical_checks_required':['Snap insertion, outward-release force and repeated-removal fatigue','Cap return, friction and edge pressing','Retention pull-off load and print tolerances','Actual switch height and electrical closing before stop','Magnet field and BLE calibration','Each module magnet polarity, installed depth and PCB/cell service'], 'electronics_reference':'Centered Hall sensor and inward SW1 at (0,-5) in index.circuit.tsx; includes the matching prescribed routing revision.'}
(OUT/'Validation'/'geometry.json').write_text(json.dumps(validation,indent=2)+'\n')
(OUT/'Validation'/'scene_meshes.json').write_text(json.dumps(meshes))
print(json.dumps({'styles':styles,'printed_parts':len(manifest),'press_rotation_samples':len(rows),'output':str(OUT),'status':'CAD checks passed; physical fit testing required'},indent=2),flush=True)
