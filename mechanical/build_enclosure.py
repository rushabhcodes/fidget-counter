"""MagSafe BLE fidget mechanical prototype, units mm, CadQuery >=2.6.

Run: python mechanical/build_enclosure.py --out work/enclosure
The STEP assembly contains separate named components. Print STL files are
already oriented on Z=0. Reference parts and CAD solids use assembly coordinates.
Attachment geometry fits the specified discs; holding force and magnetic
compatibility require testing with the ordered magnets and intended phone.
"""
from pathlib import Path
import argparse, json, math, itertools
import cadquery as cq

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument('--out', type=Path, default=HERE/'export')
ap.add_argument('--parameters', type=Path, default=HERE/'enclosure-parameters.json')
ap.add_argument('--mesh-out', type=Path, default=None)
args = ap.parse_args()
P = json.loads(args.parameters.read_text())
OUT = args.out.resolve()
for d in ['STEP_Parts', 'Print_STL', 'Reference_STL', 'Views', 'Validation']:
    (OUT/d).mkdir(parents=True, exist_ok=True)

def disk(r, z, h, x=0, y=0):
    return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h).val()
def annulus(ri, ro, z, h):
    return cq.Workplane('XY').workplane(offset=z).circle(ro).circle(ri).extrude(h).val()
def box(sx,sy,sz,x=0,y=0,z=0):
    return cq.Workplane('XY').box(sx,sy,sz).val().translate((x,y,z+sz/2))
def compound(shapes):
    return cq.Compound.makeCompound(shapes)
def fuse_all(shapes):
    result=shapes[0]
    for sh in shapes[1:]: result=result.fuse(sh)
    return result.clean()
def sector(ri,ro,z,h,start,end):
    sh = cq.Workplane('XZ').polyline([(ri,z),(ro,z),(ro,z+h),(ri,z+h)]).close().revolve(end-start,(0,0),(0,1)).val()
    return sh.rotate((0,0,0),(0,0,1),start)
def radial_box(r,length,width,z,h,angle):
    return box(length,width,h,x=r,z=z).rotate((0,0,0),(0,0,1),angle)
def cone(rb,rt,z,h,x=0,y=0):
    return cq.Solid.makeCone(rb,rt,h,cq.Vector(x,y,z))

Rbody=P['body_diameter']/2
Rcap=P['cap_diameter']/2
Rbase=P['attachment_flange_diameter']/2
grip_bottom=P['cap_grip_bottom_z']
grip_inner=Rcap-0.6-P['cap_grip_wall']
Rskirt=P['skirt_outer_radius']
Rskirt_i=Rskirt-P['skirt_wall']
Rbore=Rskirt+P['radial_running_clearance']
Rlip=Rskirt+P['snap_lip_projection']
Rgroove=Rlip+0.3
pcb_z=P['pcb_bottom_z']; pcb_top=pcb_z+P['pcb_thickness']
deck_z=P['overall_height']-1.2
body_top=deck_z-1.8
hard_stop_z=body_top+P['button_travel']
magnet_z=pcb_top+P['sensor_height']+P['encoder_released_airgap']
pad=P['phone_pad_thickness']; skin=P['bottom_skin_thickness']
skin_top=pad+skin
mag_z=skin_top+P['magnet_adhesive_thickness']
mag_top=mag_z+P['attachment_magnet_thickness']
shield_z=mag_top+P['magnet_adhesive_thickness']
shield_top=shield_z+P['shield_thickness']
flange_top=shield_top+0.8
mag_ri=P['magnet_region_inner_diameter']/2
mag_ro=P['magnet_region_outer_diameter']/2
mc=P['attachment_pocket_clearance']
mount_r=16.2
mount_angles=[45+i*360/P['flexure_count'] for i in range(P['flexure_count'])]
mounts=[(mount_r*math.cos(math.radians(a)),mount_r*math.sin(math.radians(a))) for a in mount_angles]

assert Rskirt_i > P['pcb_diameter']/2 + 0.2, 'PCB fouls rotating skirt'
assert Rbody-Rgroove >= 0.7, 'Groove wall too thin'
assert Rbase > mag_ro+mc+1, 'Attachment flange too small'
assert P['encoder_released_airgap']-P['button_travel'] >= 0.5, 'Pressed sensor gap too small'
assert P['flexure_count'] in (3,4)
assert P['attachment_mode'] in ('envelope','vendor_sectors','disc_array')
assert P['battery_access']=='top'
assert P['snap_tab_count']==len(P['snap_tab_center_degrees'])==2
assert P['cap_service_port_bottom_z']+P['cap_service_port_height']<P['snap_lip_top_z'], 'Release port cuts the retaining roof'
assert Rskirt-P['snap_tab_wall']-P['cap_release_deflection']-P['pcb_diameter']/2>=0.2-1e-6, 'Released latch fouls PCB edge'
assert Rlip-P['cap_release_deflection']<Rbore, 'Released latch cannot pass the bore'
assert grip_inner-Rbase >= P['radial_running_clearance']-1e-6, 'Outer grip fouls lower flange'
assert grip_bottom-P['button_travel'] >= 0.5-1e-6, 'Pressed outer grip too close to phone plane'
assert P['cap_top_groove_depth'] <= 0.4, 'Top grip leaves too little deck thickness'

# Full-footprint cap. The outer grip sleeve wraps down around the stationary
# flange; the separate inner skirt retains and guides the cap. Keep the existing
# shoulder stop so the extended sleeve cannot become the button travel stop.
cap=disk(Rcap-0.6,deck_z,1.2)
shroud=annulus(Rbody-0.85,Rcap-0.6,hard_stop_z,deck_z-hard_stop_z+0.02)
grip_sleeve=annulus(grip_inner,Rcap-0.6,grip_bottom,deck_z-grip_bottom+0.02)
cap=cap.fuse(shroud,grip_sleeve)
profile=[(Rskirt_i,P['skirt_bottom_z']), (Rskirt,P['skirt_bottom_z']),
         (Rskirt,P['snap_lip_top_z']-0.65),(Rlip,P['snap_lip_top_z']-0.4),
         (Rlip,P['snap_lip_top_z']),(Rskirt,P['snap_lip_top_z']),
         (Rskirt,deck_z+0.02),(Rskirt_i,deck_z+0.02)]
skirt=annulus(Rskirt_i,Rskirt,P['skirt_bottom_z'],deck_z+0.02-P['skirt_bottom_z'])
for angle in P['snap_tab_center_degrees']:
    half=P['snap_tab_arc_degrees']/2
    latch=cq.Workplane('XZ').polyline(profile).close().revolve(2*half,(0,0),(0,1)).val().rotate((0,0,0),(0,0,1),angle-half)
    skirt=skirt.fuse(latch)
    # Thin only the two flexing tongues. The remaining skirt still guides the cap.
    skirt=skirt.cut(sector(Rskirt_i-0.05,Rskirt-P['snap_tab_wall'],P['skirt_bottom_z']-0.05,
                         P['snap_slot_root_z']-P['skirt_bottom_z']+0.05,angle-half-2,angle+half+2))
    for boundary in [angle-half-1.5,angle+half+1.5]:
        skirt=skirt.cut(radial_box(Rskirt,3.0,P['snap_slot_width'],P['skirt_bottom_z']-0.05,
                                 P['snap_slot_root_z']-P['skirt_bottom_z']+0.05,boundary))
cap=cap.fuse(skirt)
ribs=[radial_box(Rcap-0.55,1.10,0.70,grip_bottom,P['overall_height']-grip_bottom,
                i*360/P['cap_edge_rib_count']) for i in range(P['cap_edge_rib_count'])]
cap=cap.fuse(*ribs).intersect(disk(Rcap,grip_bottom,P['overall_height']-grip_bottom)).clean()
# Recessed radial grooves give traction during thumb rotation without increasing
# height. The central magnet roof is untouched; grooves can bridge when printed
# with the top face on the bed.
groove_inner=P['cap_top_groove_inner_radius']; groove_outer=Rcap-1.7
grooves=[radial_box((groove_inner+groove_outer)/2,groove_outer-groove_inner,
          P['cap_top_groove_width'],P['overall_height']-P['cap_top_groove_depth'],
          P['cap_top_groove_depth']+0.1,i*360/P['cap_top_groove_count'])
          for i in range(P['cap_top_groove_count'])]
cap=cap.cut(compound(grooves)).clean()
# Continuous annular force transfer reaches the one stationary off-axis switch
# at every rotation angle. The cavity inside it clears the sensor and BLE MCU.
cap=cap.fuse(annulus(11.6,13.7,pcb_top+2.15,deck_z-(pcb_top+2.15)+0.02))
pocket_r=(P['encoder_diameter']+P['encoder_pocket_clearance'])/2
pocket_top=magnet_z+P['encoder_thickness']+P['encoder_roof_shim']
assert pocket_top<=deck_z, 'Encoder pocket cuts through cap roof'
boss_bottom=magnet_z-0.15
cap=cap.fuse(disk(pocket_r+1.1,boss_bottom,deck_z-boss_bottom+0.02))
cap=cap.cut(disk(pocket_r,boss_bottom-0.1,pocket_top-boss_bottom+0.1)).clean()
for angle in P['snap_tab_center_degrees']:
    cap=cap.cut(radial_box(Rcap-0.6,3.0,P['cap_grip_window_width'],P['cap_grip_window_bottom_z'],
                          P['cap_grip_window_height'],angle))
cap=cap.clean()
encoder=disk(P['encoder_diameter']/2,magnet_z,P['encoder_thickness'])

# Structural housing. Lower widened flange keeps attachment magnets outside the core.
housing=disk(Rbase,skin_top,flange_top-skin_top)
housing=housing.fuse(disk(Rbody,skin_top,body_top-skin_top-0.5))
housing=housing.fuse(cone(Rbody,Rbody-0.6,body_top-0.5,0.5))
housing=housing.cut(disk(Rbore,1.5,body_top+1.0))
housing=housing.cut(annulus(Rbore-0.02,Rgroove,P['snap_lip_top_z']-1.30,1.30))
housing=housing.cut(cone(Rbore,Rbore+0.4,body_top-0.5,0.51))
housing=housing.cut(disk(12.25,skin_top-0.1,1.5-skin_top+0.2))
for angle in P['snap_tab_center_degrees']:
    housing=housing.cut(radial_box(Rbody,3.0,P['cap_service_port_width'],P['cap_service_port_bottom_z'],
                                  P['cap_service_port_height'],angle))
# The disc tray loads from its inside face before attaching the bottom cover.
# The housing's upper recess accepts a continuous steel backing ring first;
# locating pockets in the cover avoids trapping that ring above small holes.
attachment_centers=[]
attachment=[]; shields=[]
gap=P['attachment_gap_degrees']/2
if P['attachment_mode']=='disc_array':
    disc_r=P['attachment_disc_diameter']/2
    disc_pocket_r=(P['attachment_disc_diameter']+P['attachment_disc_pocket_diameter_clearance'])/2
    disc_pitch_r=P['attachment_disc_pitch_diameter']/2
    tray_ro=P['attachment_tray_outer_radius']
    tray_clearance=P['attachment_tray_radial_clearance']
    disc_count=P['attachment_disc_count']
    assert isinstance(disc_count,int) and disc_count>=3
    disc_web=2*disc_pitch_r*math.sin(math.pi/disc_count)-2*disc_pocket_r
    assert disc_web>=1.0, 'Less than 1 mm between adjacent magnet pockets'
    assert disc_pitch_r-disc_pocket_r-Rbody>=1.0, 'Disc tray inner wall too thin'
    assert tray_ro-disc_pitch_r-disc_pocket_r>=0.8-1e-6, 'Disc tray outer wall too thin'
    assert Rbase-tray_ro-tray_clearance>=0.8-1e-6, 'Housing outer rim too thin'
    for i in range(disc_count):
        angle=P['attachment_disc_phase_degrees']+i*360/disc_count
        x=disc_pitch_r*math.cos(math.radians(angle))
        y=disc_pitch_r*math.sin(math.radians(angle))
        attachment_centers.append({'index':i+1,'angle_degrees':angle,'x':x,'y':y})
        attachment.append(disk(disc_r,mag_z,P['attachment_magnet_thickness'],x,y))
    # Move the printed pocket walls into the cover while retaining the original
    # phone-facing skin. Both magnets and backing ring can be inserted axially.
    housing=housing.cut(annulus(Rbody-tray_clearance,tray_ro+tray_clearance,skin_top-0.1,
                               mag_top+P['magnet_adhesive_thickness']-skin_top+0.1))
    shield_ri=disc_pitch_r-disc_r-0.1
    shield_ro=disc_pitch_r+disc_r+0.1
    shields.append(annulus(shield_ri,shield_ro,shield_z,P['shield_thickness']))
    housing=housing.cut(annulus(shield_ri-mc,shield_ro+mc,mag_top-0.05,
                               shield_top+0.05-(mag_top-0.05)))
else:
    if P['attachment_mode']=='envelope':
        magnet_sectors=[{'start':gap,'end':360-gap}]
    else:
        assert P['vendor_sectors'], 'Enter supplier-defined sector footprints'
        magnet_sectors=P['vendor_sectors']
    for s in magnet_sectors:
        assert 0<=s['start']<s['end']<=360
        start=s['start']; end=s['end']
        ri=s.get('inner_radius',mag_ri); ro=s.get('outer_radius',mag_ro)
        attachment.append(sector(ri,ro,mag_z,P['attachment_magnet_thickness'],start,end))
        shields.append(sector(ri+0.1,ro-0.1,shield_z,P['shield_thickness'],start,end))
        pocket=sector(ri-mc,ro+mc,skin_top-0.1,shield_top+0.05-skin_top+0.1,start-0.5,end+0.5)
        housing=housing.cut(pocket)
attachment=compound(attachment); shield=compound(shields)
for x,y in mounts:
    # Shoulder supports PCB, upper column passes through a PCB clearance notch.
    housing=housing.fuse(disk(2.3,1.49,pcb_z-1.49,x,y))
    housing=housing.fuse(disk(1.55,pcb_z-0.01,body_top-pcb_z+0.01,x,y))
    housing=housing.cut(disk(0.625,pcb_z+0.85,3.10,x,y))
# Four perimeter notches engage fixed columns and register PCB rotation.
housing=housing.clean()

# Replaceable PETG spring insert. Neutral STL is planar under every beam.
# Assembly shapes represent prescribed elastic deflection, not an FEA result.
flex_z=body_top; flex_ri=17.1; flex_ro=18.3
beam_ri=P['flexure_mean_radius']-P['flexure_width']/2
beam_ro=P['flexure_mean_radius']+P['flexure_width']/2
fixed_root_degrees=9.0
def bending_t(degrees):
    return max(0.0,(degrees-fixed_root_degrees)/(P['flexure_arc_degrees']-fixed_root_degrees))
def flexure(deflection):
    pieces=[annulus(flex_ri,flex_ro,flex_z,1.1)]
    for a,(x,y) in zip(mount_angles,mounts):
        pieces.append(disk(1.7,flex_z,1.1,x,y))
        pieces.append(radial_box((beam_ri+flex_ro)/2,flex_ro-beam_ri,2.3,flex_z,P['flexure_thickness'],a))
        wires=[]
        for j in range(17):
            arc_progress=j/16; theta=math.radians(a+P['flexure_arc_degrees']*arc_progress)
            t=bending_t(P['flexure_arc_degrees']*arc_progress)
            dz=-deflection*(3*t*t-t*t*t)/2
            z0=flex_z+dz
            pts=[cq.Vector(beam_ri*math.cos(theta),beam_ri*math.sin(theta),z0),
                 cq.Vector(beam_ro*math.cos(theta),beam_ro*math.sin(theta),z0),
                 cq.Vector(beam_ro*math.cos(theta),beam_ro*math.sin(theta),z0+P['flexure_thickness']),
                 cq.Vector(beam_ri*math.cos(theta),beam_ri*math.sin(theta),z0+P['flexure_thickness'])]
            wires.append(cq.Wire.makePolygon(pts,close=True))
        pieces.append(cq.Solid.makeLoft(wires,ruled=True))
        theta=math.radians(a+P['flexure_arc_degrees']-1.5)
        xx=P['flexure_mean_radius']*math.cos(theta); yy=P['flexure_mean_radius']*math.sin(theta)
        t=bending_t(P['flexure_arc_degrees']-1.5)
        end_d=deflection*(3*t*t-t*t*t)/2
        contact_height=deck_z+P['flexure_preload']-(flex_z+P['flexure_thickness'])
        pieces.append(disk(0.90,flex_z+P['flexure_thickness']-end_d-0.06,contact_height+0.06,xx,yy))
    result=fuse_all(pieces)
    for x,y in mounts:
        result=result.cut(disk(0.85,flex_z-0.01,1.2,x,y))
        result=result.cut(cone(0.85,1.5,flex_z+0.45,0.65,x,y))
    return result.clean()
neutral_flex=flexure(0)
# Prescribed pad displacement uses the pad's actual location along the arc.
tip_t=bending_t(P['flexure_arc_degrees']-1.5)
tip_factor=(3*tip_t*tip_t-tip_t**3)/2
released_flex=flexure(P['flexure_preload']/tip_factor)
pressed_flex=flexure((P['flexure_preload']+P['button_travel'])/tip_factor)

# Circular PCB with perimeter clearance notches for fixed flexure columns.
board=disk(P['pcb_diameter']/2,pcb_z,P['pcb_thickness'])
for x,y in mounts: board=board.cut(disk(1.8,pcb_z-0.1,1.2,x,y))
board=board.clean()
passives=[]
for x,y in [(-4,-7),(-2,-7),(1,-7),(4,-7),(-8,5),(-6,5),(6,5),(9,5)]:
    passives.append(box(1.6,0.8,0.55,x,y,pcb_top))
debug=[disk(0.6,pcb_top,0.05,-5+i*2.0,-12) for i in range(6)]
antenna=[]
for i in range(4):
    x=-3+i*2
    antenna.append(box(0.35,3.3,0.05,x,15.7,pcb_top))
    if i<3: antenna.append(box(2.35,0.35,0.05,x+1,14.22 if i%2 else 17.18,pcb_top))
sensor=box(0.824,1.316,P['sensor_height'],0,0,pcb_top)
mcu=box(6,6,0.9,-7.5,5,pcb_top)
switch_base=box(2.8,4.2,1.4,12.65,0,pcb_top)
switch_button=disk(0.8,pcb_top+1.4,0.5,12.65,0)
switch=compound([switch_base,switch_button])
pressed_switch=compound([switch_base,disk(0.8,pcb_top+1.4,0.25,12.65,0)])
# Complete imported holder, oriented as the bottom-mounted PCB footprint.
# Raw STEP coordinates align the two solder tails with the manufacturer land
# drawing; its cell center is X=-1.2 before the bottom-side mirror.
holder_path=HERE.parent/'imports/BS_08_B2AA020_R/BS_08_B2AA020_R.step'
holder=cq.importers.importStep(str(holder_path)).val().translate((0,0,0.01)).rotate((0,0,0),(0,1,0),180)
holder=holder.translate((P['battery_holder_pcb_x'],P['battery_holder_pcb_y'],pcb_z))
pcb_dummy=board
# The negative face is closest to the PCB; positive face points at the solid floor.
# This is a nominal fit reference. Compliant metal contacts need a physical test.
battery=disk(10.0,pcb_z-P['battery_negative_face_depth']-3.2,3.2)

# Continuous phone-facing floor. Battery service is entirely through the top.
bottom=disk(Rbase,pad,skin)
if P['attachment_mode']=='disc_array':
    tray=annulus(Rbody,tray_ro,skin_top-0.01,mag_top-skin_top+0.01)
    pockets=[disk(disc_pocket_r,skin_top,mag_top-skin_top+0.1,c['x'],c['y'])
             for c in attachment_centers]
    tray=tray.cut(compound(pockets))
    bottom=bottom.fuse(tray).clean()
phone_pad=disk(Rbase,0,pad)
encoder_shim=disk(P['encoder_diameter']/2,magnet_z+P['encoder_thickness'],P['encoder_roof_shim'])

def flat_screw(x,y,head_z,dia,length,head_d):
    head_h=(head_d-dia)/2
    return cone(head_d/2,dia/2,head_z,head_h,x,y).fuse(disk(dia/2,head_z+head_h,length,x,y)).clean()
flex_screws=compound([flat_screw(x,y,body_top+0.46,1.6,3.0,2.8).rotate((x,y,body_top+0.78),(x+1,y,body_top+0.78),180) for x,y in mounts])
# Four bushings clamp the PCB against its shoulders when the spring insert is
# screwed down. The board cannot lift toward the encoder when the phone flips.
pcb_spacers=compound([annulus(1.7,2.2,pcb_top,body_top-pcb_top).translate((x,y,0)) for x,y in mounts])
spacer_print=annulus(1.7,2.2,0,body_top-pcb_top)
cq.exporters.export(spacer_print,str(OUT/'Print_STL'/'PCB_Spacer_Print_4.stl'),tolerance=0.025,angularTolerance=0.06)
cq.exporters.export(pcb_spacers,str(OUT/'STEP_Parts'/'PCB_Spacer_Bushings.step'))
# Two reusable flat keys enter the aligned side ports. A shoulder limits inward
# latch displacement; a separate handle stays outside the full grip sleeve.
key_tip=Rbody-(Rlip-P['cap_release_deflection'])
key_handle_start=Rcap-(Rlip-P['cap_release_deflection'])+0.8
key_width=P['cap_release_key_blade_width'];key_thickness=P['cap_release_key_blade_thickness']
release_key=box(key_handle_start+7,key_width,key_thickness,x=(key_handle_start+7)/2)
release_key=release_key.fuse(box(2.0,key_width,2.5,x=key_tip+1),
                           box(7,8,2.5,x=key_handle_start+3.5)).clean()
cq.exporters.export(release_key,str(OUT/'Print_STL'/'Cap_Release_Key_Print_2.stl'),tolerance=0.025,angularTolerance=0.06)
cq.exporters.export(release_key,str(OUT/'STEP_Parts'/'Cap_Release_Key.step'))
lift_pick=box(20,2.4,0.8,x=10).fuse(box(7,8,2.5,x=16.5)).clean()
cq.exporters.export(lift_pick,str(OUT/'Print_STL'/'PCB_Lift_Pick.stl'),tolerance=0.025,angularTolerance=0.06)
cq.exporters.export(lift_pick,str(OUT/'STEP_Parts'/'PCB_Lift_Pick.step'))

parts={
 'Rotating_Cap':cap,'Encoder_Magnet':encoder,'Stationary_Housing':housing,
 'Flexure_Retention_System':released_flex,'PCB_Dummy':pcb_dummy,
 'Angle_Sensor_Dummy':sensor,'BLE_MCU_Dummy':mcu,'Tactile_Switch':switch,
 'CR2032':battery,'Battery_Holder':holder,
 'MagSafe_Magnet_Array':attachment,'Magnetic_Shield':shield,'Bottom_Cover':bottom}
colors={'Rotating_Cap':(0.13,0.19,0.26),'Encoder_Magnet':(0.88,0.31,0.22),
 'Stationary_Housing':(0.77,0.82,0.84),'Flexure_Retention_System':(0.96,0.64,0.18),
 'PCB_Dummy':(0.07,0.40,0.28),'Angle_Sensor_Dummy':(0.10,0.12,0.16),
 'BLE_MCU_Dummy':(0.10,0.12,0.16),'Tactile_Switch':(0.68,0.71,0.73),
 'CR2032':(0.63,0.68,0.73),'Battery_Holder':(0.29,0.30,0.32),'Battery_Hatch':(0.29,0.40,0.46),
 'MagSafe_Magnet_Array':(0.24,0.63,0.74),'Magnetic_Shield':(0.47,0.53,0.60),
 'Bottom_Cover':(0.46,0.55,0.60)}
print_parts=['Rotating_Cap','Stationary_Housing','Flexure_Retention_System','Bottom_Cover']
states={'Released':parts.copy(),'Pressed':parts.copy(),'Exploded':{},'Top_Service':parts.copy()}
states['Pressed']['Rotating_Cap']=cap.translate((0,0,-P['button_travel']))
states['Pressed']['Encoder_Magnet']=encoder.translate((0,0,-P['button_travel']))
states['Pressed']['Flexure_Retention_System']=pressed_flex
states['Pressed']['Tactile_Switch']=pressed_switch
explode={'Rotating_Cap':66,'Encoder_Magnet':45,'Flexure_Retention_System':30,
 'Angle_Sensor_Dummy':23,'BLE_MCU_Dummy':23,'Tactile_Switch':23,
 'PCB_Dummy':17,'Battery_Holder':17,'CR2032':8,'Stationary_Housing':0,
 'Magnetic_Shield':-14,'MagSafe_Magnet_Array':-28,'Bottom_Cover':-42}
for n,s in parts.items(): states['Exploded'][n]=s.translate((0,0,explode[n]))
states['Top_Service']['Rotating_Cap']=cap.translate((-65,0,20))
states['Top_Service']['Encoder_Magnet']=encoder.translate((-65,0,20))
states['Top_Service']['Flexure_Retention_System']=released_flex.translate((0,0,30))
for name in ['PCB_Dummy','Battery_Holder','CR2032','Angle_Sensor_Dummy','BLE_MCU_Dummy','Tactile_Switch']:
    states['Top_Service'][name]=parts[name].rotate((0,0,pcb_z+0.5),(0,1,pcb_z+0.5),180).translate((58,0,P['pcb_service_lift']))

for state in ['Released','Pressed','Exploded','Top_Service']:
    assy=cq.Assembly(name='MagSafe_BLE_Fidget_'+state)
    for name,s in states[state].items(): assy.add(s,name=name,color=cq.Color(*colors[name]))
    if state!='Exploded':
        assy.add(flex_screws.translate((0,0,30 if state=='Top_Service' else 0)),name='Flexure_M1_6_Fasteners',color=cq.Color(0.4,0.44,0.48))
        assy.add(phone_pad,name='Protective_Film',color=cq.Color(0.16,0.18,0.20))
        shim_shift=(-65,0,20) if state=='Top_Service' else (0,0,-P['button_travel'] if state=='Pressed' else 0)
        assy.add(encoder_shim.translate(shim_shift),name='Encoder_Roof_Shim',color=cq.Color(0.6,0.6,0.6))
        assy.add(pcb_spacers.translate((0,0,20 if state=='Top_Service' else 0)),name='PCB_Spacer_Bushings',color=cq.Color(0.7,0.72,0.74))
    else:
        assy.add(pcb_spacers.translate((0,0,23)),name='PCB_Spacer_Bushings',color=cq.Color(0.7,0.72,0.74))
    assy.export(str(OUT/f'Fidget_Assembly_{state}.step'))

print('Exporting parts...',flush=True)
manifest=[]
meshes=[]
for name,s in parts.items():
    src=neutral_flex if name=='Flexure_Retention_System' else s
    cq.exporters.export(src,str(OUT/'STEP_Parts'/f'{name}.step'))
    print_shape=src
    if name=='Rotating_Cap':
        print_shape=src.rotate((0,0,0),(1,0,0),180)
    zmin=print_shape.BoundingBox().zmin
    print_shape=print_shape.translate((0,0,-zmin))
    if name in print_parts:
        cq.exporters.export(print_shape,str(OUT/'Print_STL'/f'{name}.stl'),tolerance=0.025,angularTolerance=0.06)
    else:
        cq.exporters.export(src,str(OUT/'Reference_STL'/f'{name}.stl'),tolerance=0.03,angularTolerance=0.06)
    bb=src.BoundingBox()
    manifest.append({'name':name,'print':name in print_parts,'cad_valid':src.isValid(),
      'solids':len(src.Solids()),'volume_mm3':round(src.Volume(),3),
      'size_mm':[round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3)],'color':colors[name]})
    for state,items in states.items():
        sh=items[name]
        vs,fs=sh.tessellate(0.04,0.08)
        meshes.append({'name':name,'state':state,'color':colors[name],
             'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
    # Exact half-section meshes, evaluated from the same B-rep, XZ plane Y=0.
    cutter=box(160,80,160,0,40,-40)
    for state in ['Released','Pressed']:
        sh=states[state][name].intersect(cutter)
        if sh.Volume()>1e-7:
            vs,fs=sh.tessellate(0.04,0.08)
            meshes.append({'name':name,'state':state+'_Section','color':colors[name],
              'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})

# Additional rendering meshes keep package parts named and reference electronics
# visibly distinct without splitting the 13 required component exports.
for n,s,c in [('PCB_Board',board,colors['PCB_Dummy']),('Flexure_Neutral',neutral_flex,colors['Flexure_Retention_System']),
              ('Flexure_Fasteners',flex_screws,(0.44,0.48,0.52)),
              ('Phone_Pad',phone_pad,(0.16,0.18,0.20)),
              ('Encoder_Shim',encoder_shim,(0.6,0.6,0.6)),
              ('PCB_Spacers',pcb_spacers,(0.7,0.72,0.74))]:
    vs,fs=s.tessellate(0.04,0.08)
    meshes.append({'name':n,'state':'Detail','color':c,'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
mesh_path=args.mesh_out or (OUT/'Validation'/'scene_meshes.json')
mesh_path.parent.mkdir(parents=True,exist_ok=True)
mesh_path.write_text(json.dumps(meshes))
from export_circuit_models import export_models
export_models(meshes, OUT/'Circuit_Models', pcb_z+P['pcb_thickness']/2, P)

# Physical collision audit, both end states. Report unloaded spring-contact
# interference separately, after confirming the cell clears the rigid holder.
contact_fit=[]
collisions=[]
for state in ['Released','Pressed']:
    for (na,sa),(nb,sb) in itertools.combinations(states[state].items(),2):
        ba,bb=sa.BoundingBox(),sb.BoundingBox()
        if (ba.xmax<bb.xmin or bb.xmax<ba.xmin or ba.ymax<bb.ymin or bb.ymax<ba.ymin or ba.zmax<bb.zmin or bb.zmax<ba.zmin): continue
        v=sa.intersect(sb).Volume()
        if v>0.002:
            row={'state':state,'parts':[na,nb],'overlap_mm3':round(v,5)}
            if set([na,nb])=={'CR2032','Battery_Holder'}:
                holder_solids=states[state]['Battery_Holder'].Solids()
                spring=min(holder_solids,key=lambda s:s.Volume())
                rigid=max(holder_solids,key=lambda s:s.Volume())
                rigid_overlap=states[state]['CR2032'].intersect(rigid).Volume()
                assert rigid_overlap<0.002, 'Battery intersects rigid holder housing'
                contact_fit.append(dict(row,classification='undeformed negative spring contact',rigid_housing_overlap_mm3=round(rigid_overlap,5)))
            else: collisions.append(row)
for state in ['Released','Pressed']:
    for n,s in states[state].items():
        v=pcb_spacers.intersect(s).Volume()
        if v>0.002: collisions.append({'state':state,'parts':['PCB_Spacer_Bushings',n],'overlap_mm3':round(v,5)})
# The top service path uses the existing four mounting holes and screws.
# After removing the cap, flexure, screws and spacers, the complete board/cell/
# holder stack must translate straight upward without touching fixed solids.
extraction=[]
lift_parts=['PCB_Dummy','Battery_Holder','CR2032','Angle_Sensor_Dummy','BLE_MCU_Dummy','Tactile_Switch']
fixed_parts=['Stationary_Housing','Bottom_Cover','MagSafe_Magnet_Array','Magnetic_Shield']
for lift in [0,0.5,1,2,4,6,10,16,P['pcb_service_lift']]:
    rows=[]
    for name in lift_parts:
        moved=parts[name].translate((0,0,lift))
        for fixed in fixed_parts:
            volume=moved.intersect(parts[fixed]).Volume()
            if volume>0.002: rows.append({'moving':name,'fixed':fixed,'overlap_mm3':round(volume,5)})
    assert not rows, f'Top service path blocked at lift {lift}: {rows}'
    extraction.append({'lift_mm':lift,'rigid_collisions':rows})
key_checks=[]
for angle in P['snap_tab_center_degrees']:
    installed_key=release_key.translate((Rlip-P['cap_release_deflection'],0,7.35)).rotate((0,0,0),(0,0,1),angle)
    overlap=installed_key.intersect(housing).Volume()
    assert overlap<0.002, 'Release key collides with housing outside its service port'
    roof=sector(Rbore+0.05,Rbody,P['snap_lip_top_z']+0.05,0.35,angle-3,angle+3)
    assert abs(housing.intersect(roof).Volume()-roof.Volume())<0.001, 'Retaining roof missing above release port'
    key_checks.append({'angle_degrees':angle,'housing_overlap_mm3':round(overlap,5),'retaining_roof_intact':True})
pick_checks=[]
for angle in [0,180]:
    corridor=radial_box(18.9,1.0,2.4,5.9,body_top+0.5-5.9,angle)
    for name in ['Stationary_Housing','PCB_Dummy','Battery_Holder','CR2032']:
        assert corridor.intersect(parts[name]).Volume()<0.002, f'PCB lift pick corridor blocked by {name}'
    pick_checks.append({'angle_degrees':angle,'radial_bounds_mm':[18.4,19.4],'width_mm':2.4,'rigid_collisions':0})
floor_probe=disk(12.25,pad,skin)
assert abs(bottom.intersect(floor_probe).Volume()-floor_probe.Volume())<0.001, 'Solid bottom retains a hatch opening'
L=P['flexure_mean_radius']*math.radians(P['flexure_arc_degrees']-fixed_root_degrees)
k=P['petg_modulus_estimate_mpa']*P['flexure_width']*P['flexure_thickness']**3/(4*L**3)
validation={'parameters_mm':P,'manifest':manifest,'collision_audit':collisions,'contact_fit_estimates':contact_fit,
 'swd_pad_row_mm':{'x':[-4,-2,0,2,4],'y':-14,'pad_diameter':1.2},
 'button_travel_mm':P['button_travel'],
 'sensor_gap_released_mm':P['encoder_released_airgap'],
 'sensor_gap_pressed_mm':P['encoder_released_airgap']-P['button_travel'],
 'snap_radial_engagement_mm':Rlip-Rbore,'retention_groove_wall_mm':Rbody-Rgroove,
 'skirt_running_clearance_radial_mm':P['radial_running_clearance'],
 'outer_grip_height_mm':P['overall_height']-grip_bottom,
 'outer_grip_flange_clearance_radial_mm':round(grip_inner-Rbase,4),
 'outer_grip_phone_clearance_pressed_mm':grip_bottom-P['button_travel'],
 'snap_strain_estimate':1.5*P['snap_tab_wall']*(Rlip-Rbore)/(P['snap_slot_root_z']-P['snap_lip_top_z'])**2,
 'flexure_estimate':{'method':'straight cantilever approximation; curved beam and FDM anisotropy not solved',
   'length_mm':round(L,3),'four_beam_stiffness_n_per_mm':round(k*P['flexure_count'],3),
   'rest_force_n':round(k*P['flexure_count']*P['flexure_preload'],3),
   'pressed_force_n':round(k*P['flexure_count']*(P['flexure_preload']+P['button_travel']),3),
   'surface_strain_estimate':round(1.5*P['flexure_thickness']*(P['flexure_preload']+P['button_travel'])/L**2,5)},
 'magnet_layout_status':('Disc-array mechanical prototype; ordered magnetization, holding force, Hall bias and MagSafe compatibility unverified'
     if P['attachment_mode']=='disc_array' else 'Supplier envelope; magnetic compatibility unverified'),
 'encoder_magnet_status':{'diameter_mm':P['encoder_diameter'],'thickness_mm':P['encoder_thickness'],'magnetization':P['encoder_magnetization'],'material':'neodymium, grade unspecified; field and counting accuracy require prototype calibration'},
 'electronics_status':'STEP assemblies use mechanical electronics bounding dummies. The tscircuit assembly replaces these with the actual populated board. No physical RF or firmware validation.',
 'contact_hardware_status':'JLCPCB C964787 BS-08-B2AA020-R fitted below PCB; manufacturer 5.8 mm maximum height used for clearance',
 'holder_conservative_bottom_clearance_mm':round(pcb_z-P['battery_holder_max_height']-skin_top,4),
 'battery_positive_face':'toward solid bottom cover',
 'top_service':{'access':'top','bottom_hatch':False,'hatch_fasteners':0,'pcb_retaining_screws':4,
    'screw_size':'M1.6','cap_release_latches':P['snap_tab_count'],'release_keys_required':2,
    'release_deflection_mm':P['cap_release_deflection'],
    'release_strain_estimate':1.5*P['snap_tab_wall']*P['cap_release_deflection']/(P['snap_slot_root_z']-P['snap_lip_top_z'])**2,
    'released_latch_to_pcb_clearance_mm':Rskirt-P['snap_tab_wall']-P['cap_release_deflection']-P['pcb_diameter']/2,
    'released_lip_to_bore_clearance_mm':Rbore-(Rlip-P['cap_release_deflection']),
    'release_key_tip_to_shoulder_mm':key_tip,'release_key_checks':key_checks,
    'pcb_pick_corridors':pick_checks,'pcb_holder_cell_extraction':extraction,
    'pcb_removal_motion':'straight +Z after cap, flexure, screws and spacers are removed',
    'solid_center_floor_verified':True,'physical_cycle_tested':False},
 'holder_contact_model_note':'Library contacts are undeformed. Battery/holder overlap is reported separately as a contact-fit estimate, not certified retention or spring-force validation.'}
if P['attachment_mode']=='disc_array':
    validation['attachment_disc_array']={
        'count':disc_count,'diameter_mm':P['attachment_disc_diameter'],
        'thickness_mm':P['attachment_magnet_thickness'],
        'pitch_circle_diameter_mm':P['attachment_disc_pitch_diameter'],
        'pocket_diameter_mm':2*disc_pocket_r,'pocket_depth_mm':mag_top-skin_top,
        'adhesive_allowance_mm':P['magnet_adhesive_thickness'],
        'minimum_pocket_web_mm':disc_web,
        'inner_wall_mm':disc_pitch_r-disc_pocket_r-Rbody,
        'outer_wall_mm':tray_ro-disc_pitch_r-disc_pocket_r,
        'housing_outer_rim_mm':Rbase-tray_ro-tray_clearance,
        'tray_outer_diameter_mm':2*tray_ro,'tray_radial_clearance_mm':tray_clearance,
        'floor_thickness_mm':skin,'magnet_bottom_z_mm':mag_z,'magnet_top_z_mm':mag_top,
        'shield_inner_diameter_mm':2*shield_ri,'shield_outer_diameter_mm':2*shield_ro,
        'shield_bottom_z_mm':shield_z,'shield_top_z_mm':shield_top,
        'flange_top_z_mm':flange_top,
        'centers_mm':attachment_centers,
        'installation':'Insert backing ring in housing recess; orient and glue discs into inside-face cover pockets; bond cover after fit testing.'}
    assert len(attachment.Solids())==disc_count, 'Attachment disc count differs from parameters'
    assert abs(attachment.Volume()-disc_count*math.pi*disc_r**2*P['attachment_magnet_thickness'])<0.001
    # The pocket floor must remain solid and each disc must clear all printed parts.
    for c in attachment_centers:
        floor=disk(disc_pocket_r,pad,skin,c['x'],c['y'])
        assert abs(bottom.intersect(floor).Volume()-floor.Volume())<0.001, 'Magnet pocket penetrates phone-facing skin'
        cavity=disk(disc_pocket_r,skin_top+0.001,mag_top-skin_top-0.002,c['x'],c['y'])
        assert bottom.intersect(cavity).Volume()<0.001, 'Magnet pocket is obstructed'
(OUT/'Validation'/'geometry_checks.json').write_text(json.dumps(validation,indent=2))
(OUT/'parts_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'parts':len(parts),'collisions':collisions,'valid':all(x['cad_valid'] for x in manifest),'output':str(OUT)},indent=2),flush=True)
assert not collisions, 'Unintended rigid part collisions remain'
assert all(x['cad_valid'] for x in manifest), 'Invalid CAD solid remains'
