# PCB / enclosure interface — holder revision 1.0.3

Coordinates are millimetres in a top view, relative to the rotation axis. The board is Ø36.5 × 1.0 mm, with four Ø3.6 mm nonplated mounting holes at (±11.45513, ±11.45513). Their thin 0.25 mm nominal edge web still requires fabricator acceptance. Printed shoulders and bushings support the board.

The revised enclosure is **14.0 mm high**. PCB bottom/top planes are Z=7.1/8.1. U2 is centered at (0,0); U1 is the 6 × 6 mm QFN at (-7.5,5); SW1 is centered at (12.65,0). The encoder magnet's lower face is Z=10.4, leaving nominal sensor package clearance of 1.8 mm released and 1.3 mm pressed. The cap pocket is Ø5.2 mm with a 0.2 mm roof shim; the magnet lower face stays at Z=10.4 mm. Use a diametrically magnetized neodymium Ø5 × 1.5 mm magnet and calibrate with the final phone and cell installed.

The Ø61.6 mm cap retains its full circumference grip, extending down to Z=1.0. Its pressed lower edge remains 0.5 mm above the phone plane. The annular switch pusher uses `pcb_top + 2.15`: nominal 0.25 mm free clearance above the 1.9 mm actuator, followed by nominal 0.25 mm switch displacement during the cap's 0.5 mm travel. Fit-test the switch and printed stack; the tactile switch must not act as the structural stop.

## Commercial CR2032 holder

BT1 is **MYOUNG BS-08-B2AA020-R, JLCPCB C964787**, mounted on the PCB underside. The exact footprint, pad numbers and OBJ/STEP model come from `tsci import --jlcpcb --download --use-exact-footprint C964787`; the imported files are unchanged. The manufacturer drawing specifies 24.1 × 15.7 mm body dimensions and **5.8 mm maximum height**. Clearance uses that maximum rather than the library model's 5.3 mm height. The holder's maximum envelope leaves 0.5 mm above the hatch floor.

The footprint origin is (-1.2,0), which centers the manufacturer drawing's cell axis at (0,0) after the bottom-side mirror. Pin 1 is positive at (-12.999913,0), with a 3.5 × 3.8 mm SMT land; pin 2 is negative at (9.499915,0), with a 5.7 × 2.8 mm SMT land. These coordinates are top-view coordinates. Two regular tented routing vias at (2,-11) and (-2,-11) preserve the original power distribution; they are not battery contacts or wire attachment points.

Insert the CR2032 **positive face toward the removable bottom hatch**, negative face toward the PCB. Insert the battery after PCB reflow. The commercial holder supplies retention and contacts; the hatch carries no spring contacts or wires.

Remove the device from the phone, undo the two M2 hatch screws and remove the plain hatch. Release the cell from the holder using its open sides, fit a fresh CR2032 in the marked orientation and reinstall the hatch. The cap, PCB and holder stay assembled. Screw centers are (6,-11.3) and (-6,11.3), clear of the holder's solder tails, cell and SWD pad row. Nominal pad-edge clearance to the nearest hatch post is recorded in `mechanical/enclosure-validation.json`.

The exported holder STEP contains its unloaded negative spring contact. Its 2.62 mm³ intersection with the nominal cell is reported separately as spring preload geometry; the cell has zero intersection with the rigid holder body. Contact deflection, insertion/removal motion, retention force and printed tolerances require a physical fit test. The battery-open STEP illustrates access, not a simulated insertion trajectory.

## Programming and clearance

SWD pads are at Y=-14 and X=-4,-2,0,2,4, ordered VDD, GND, SWDIO, SWDCLK, nRESET in a top view. Viewed directly underneath, their order is **R, C, D, G, V**, matching the legend. Remove the hatch for programming. Use a fixture with narrow probes; the nearest post clearance is nominal. VDD is a target-voltage reference; remove the primary cell before deliberately powering the board from the programmer.

TP_GND has a 0.4 mm plated drill; the remaining four 1.2 mm pogo pads are undrilled. GPIO diagnostic lands use 0.30 mm drills and 0.55 mm lands, with no fitted parts. All routing vias are tented on both sides. The holder's insulating housing separates the cell from PCB copper.

The antenna keepout is X=-3.5…3.5, Y=13.6…18.0 on both layers. Keep metal and attachment parts away from this volume where practical. The phone, cell and attachment magnets still affect RF and Hall readings.

## Editable enclosure and supplied parts

`build_enclosure.py` and `enclosure-parameters.json` regenerate the assembly with CadQuery ≥2.6. Run from the project root:

```sh
python mechanical/build_enclosure.py --out work/enclosure
```

`Print_STL/` contains all five parts in print orientation: Rotating_Cap, Stationary_Housing, Flexure_Retention_System, Battery_Hatch and Bottom_Cover. Corresponding editable solids are in `STEP_Parts/`. Use the complete revised set; the previous 12.2 mm enclosure and cap are incompatible with this holder stack.

Released, pressed, exploded and battery-open assemblies are included in the downloadable mechanical handoff. Electronics other than the holder are board/key-package bounding references; the circuit now combines the actual populated PCB with the released enclosure in `previews/3d.glb`. Its 14 assembly models exclude these electronic bounding dummies and the duplicate holder. `previews/pcb-3d.glb` retains the bare board view. The four outer shells are translucent in the circuit viewer. The builder also exports aligned OBJ/MTL files in `Circuit_Models/`; copy these into `mechanical/Circuit_Models/` after a CAD revision. The attachment magnet array remains a reserved envelope, and the flexure calculation is an approximate cantilever estimate rather than FEA or a measured return force.

Sources: [MYOUNG holder drawing](https://xonstorage.z8.web.core.windows.net/pdf/myoung_bs08b2aa020_apr22_xonlink.pdf), [JLCPCB holder listing](https://jlcpcb.com/partdetail/MYOUNG-BS_08_B2AA020R/C964787), [C&K KMR2 drawing](https://www.ckswitches.com/media/1479/kmr2.pdf).
