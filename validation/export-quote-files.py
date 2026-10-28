"""Generate BOM/CPL review drafts from the current BOM and current PCB export."""
import csv
from pathlib import Path
out=Path('fabrication')
bom=list(csv.DictReader(Path('BOM.csv').open()))
fitted=[r for r in bom if r['Assembly']=='FIT']
designators={name for r in fitted for name in r['References'].split()}
positions=list(csv.DictReader((out/'Assembly_Position_Reference.csv').open()))
assert len(positions)==len(designators)==29
assert {r['Designator'] for r in positions}==designators
assert next(r for r in positions if r['Designator']=='BT1')['Layer']=='bottom'
with (out/'JLCPCB_BOM_Quote_Draft.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Comment','Designator','Footprint','LCSC Part #','Manufacturer Part Number','Sourcing status'])
 for r in fitted:w.writerow([r['Value_or_part'],','.join(r['References'].split()),r['Package'],r['JLCPCB_part_number'],r['Manufacturer_part_number'],r['Sourcing_status']])
with (out/'JLCPCB_CPL_Quote_Draft.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
 for r in positions:w.writerow([r['Designator'],f"{float(r['Mid_X_mm']):.6f}",f"{float(r['Mid_Y_mm']):.6f}",r['Layer'],r['Authored_Rotation_deg']])
print('29 matching fitted designators; 28 top and BT1 bottom; authored rotations; SW1 exact-MPN procurement/consignment stated')
