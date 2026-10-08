"""Check keys against the rigid cap outside its intentionally flexing latches.

Run with the current CadQuery export directory. Latch deformation and friction
are not simulated; this checks the outer grip/windows during the initial lift.
"""
import argparse, json
from pathlib import Path
import cadquery as cq

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('cad_output',type=Path)
parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args()
audit=json.loads((args.cad_output/'Validation/geometry_checks.json').read_text())
p=audit['parameters_mm']
cap=cq.importers.importStep(str(args.cad_output/'STEP_Parts/Rotating_Cap.step')).val()
key=cq.importers.importStep(str(args.cad_output/'STEP_Parts/Cap_Release_Key.step')).val()
# Each exclusion encloses one isolated latch only, which the key deliberately
# presses inward. Remaining rigid material includes the full outer grip sleeve.
for angle in p['snap_tab_center_degrees']:
    zone=cq.Workplane('XZ').polyline([(18.65,6.8),(20.05,6.8),(20.05,12.66),(18.65,12.66)]).close().revolve(24,(0,0),(0,1)).val().rotate((0,0,0),(0,0,1),angle-12)
    cap=cap.cut(zone)
rows=[]
lip=p['skirt_outer_radius']+p['snap_lip_projection']
key_z=p['cap_service_port_bottom_z']+p['cap_service_port_height']-p['cap_release_key_blade_thickness']-0.15
for angle in p['snap_tab_center_degrees']:
    installed=key.translate((lip-p['cap_release_deflection'],0,key_z)).rotate((0,0,0),(0,0,1),angle)
    for lift in [0,0.15,0.3,0.5]:
        overlap=cap.translate((0,0,lift)).intersect(installed).Volume()
        assert overlap<0.002,(angle,lift,overlap)
        rows.append({'angle_degrees':angle,'cap_lift_mm':lift,'nonlatch_cap_overlap_mm3':round(overlap,6)})
report={'method':'Exact STEP intersections; only the two intentionally flexing latch zones excluded',
        'initial_cap_lift_mm':0.5,'remove_keys_after_initial_lift':True,
        'samples':rows,'physical_release_and_friction_tested':False}
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,indent=2)+'\n')
print('Pass: both keys clear the rigid grip/windows through the initial 0.5 mm cap lift')
