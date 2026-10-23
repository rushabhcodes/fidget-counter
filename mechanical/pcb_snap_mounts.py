"""Bolt-free PCB support with clearance-fit locators and two release latches.

The only plastic within the PCB thickness is inside actual drilled holes. The
retaining lips start above the PCB top; recessed locating posts stop below it.
All dimensions come from the same parameter block as the native circuit holes.
Release shapes are clearance poses, not FEA or physical fatigue validation.
"""
import math
import cadquery as cq


def _disk(radius, z, height):
    return cq.Solid.makeCylinder(radius, height, cq.Vector(0,0,z))


def _box(sx, sy, sz, x, y, z):
    return cq.Workplane('XY').box(sx,sy,sz).val().translate((x,y,z+sz/2))


def make_pcb_mounts(parameters, mounts):
    spec=parameters['pcb_mount']
    bottom=parameters['pcb_bottom'];top=bottom+parameters['pcb_thickness']
    root=1.5;ledge=top+spec['axial_float_mm'];tip=ledge+.75
    release=spec['release_displacement_mm'];width=spec['beam_width_mm']
    outer=1.15;inner=outer-spec['beam_thickness_mm']
    hole_radius=spec['hole_diameter_mm']/2
    clip_pairs=[];posts=[];clip_centers=[]
    for i,(x,y) in enumerate(mounts):
        angle=math.degrees(math.atan2(y,x))
        shoulder=_disk(spec['shoulder_radius_mm'],root,bottom-root)
        locator=_disk(spec['locator_radius_mm'],bottom,spec['locator_height_mm'])
        if i not in (0,2):
            posts.append(shoulder.fuse(locator).translate((x,y,0)))
            continue
        # An open inner slot frees the latch; the shoulder and remaining locator
        # cheeks carry the board. Nothing rigid bridges across the FR4.
        channel=_box(2.8,1.8,tip-1.9+.1,-1.05,0,1.9)
        rigid=shoulder.fuse(locator).cut(channel).clean()

        def beam(displacement):
            def bend(z):
                q=max(0,min(1,(z-root)/(ledge-root)))
                return displacement*q*q*(3-2*q)
            levels=[root+(ledge-root)*j/24 for j in range(25)]+[tip]
            outline=[(-outer+bend(z),z) for z in levels]
            outline += [(-inner+bend(z),z) for z in reversed(levels)]
            stem=cq.Workplane('XZ').polyline(outline).close().extrude(width).val().translate((0,width/2,0))
            reach=spec['retaining_outer_radius_mm']
            hook=[(-reach,ledge),(-inner,ledge),(-inner,tip),(-outer,tip),(-reach,ledge+.3)]
            barb=cq.Workplane('XZ').polyline(hook).close().extrude(width).val().translate((displacement,width/2,0))
            return stem.fuse(barb).clean()

        def pose(shape):
            return shape.rotate((0,0,0),(0,0,1),angle).translate((x,y,0))
        locked,released=beam(0),beam(release)
        posts.append(pose(rigid.fuse(locked).clean()))
        clip_pairs.append((pose(locked),pose(released)))
        clip_centers.append([x,y])
    audit={
        'system':'Two clearance-fit snap latches and two recessed locating posts; no bolts',
        'pcb_screws':0,'separate_pcb_retainers':0,'lock_count':2,
        'mount_centers_mm':[list(p) for p in mounts],
        'mount_radius_mm':spec['radius_mm'],'clip_centers_mm':clip_centers,
        'pcb_hole_diameter_mm':spec['hole_diameter_mm'],
        'nominal_pcb_edge_web_mm':parameters['pcb_diameter']/2-spec['radius_mm']-hole_radius,
        'release_direction':'Push both diagonal latch tips radially OUTWARD, then lift the board',
        'release_displacement_mm':release,'retention_ledge_z_mm':ledge,
        'axial_float_mm':ledge-top,'latch_top_z_mm':tip,
        'locator_top_z_mm':bottom+spec['locator_height_mm'],
        'locator_recess_below_board_top_mm':parameters['pcb_thickness']-spec['locator_height_mm'],
        'rigid_locator_to_hole_radial_clearance_mm':hole_radius-spec['locator_radius_mm'],
        'minimum_locked_feature_to_hole_clearance_mm':min(hole_radius-spec['locator_radius_mm'],hole_radius-math.hypot(outer,width/2)),
        'minimum_released_hook_to_hole_clearance_mm':hole_radius-math.hypot(spec['retaining_outer_radius_mm']-release,width/2),
        'inward_retention_overlap_mm':spec['retaining_outer_radius_mm']-hole_radius,
        'beam_thickness_mm':spec['beam_thickness_mm'],'beam_width_mm':width,
        'straight_beam_strain_estimate_percent':100*1.5*spec['beam_thickness_mm']*release/(ledge-root)**2,
        'validation_limit':'Prescribed clearance poses; no FEA, measured force, fatigue or printed fit validation',
        'physical_tested':False,
    }
    assert audit['minimum_released_hook_to_hole_clearance_mm']>.15
    assert audit['minimum_locked_feature_to_hole_clearance_mm']>.2
    assert audit['nominal_pcb_edge_web_mm']>1.5
    assert audit['locator_recess_below_board_top_mm']>.3
    assert all(p.isValid() and len(p.Solids())==1 for p in posts)
    return posts,clip_pairs,audit
