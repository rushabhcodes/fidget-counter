# PCB / enclosure interface — top-access revision 1.0.6

Coordinates are millimetres in a top view, relative to the rotation axis. The board is Ø36.5 × 1.0 mm, with four Ø3.6 mm nonplated mounting holes at (±11.45513, ±11.45513). Their thin 0.25 mm nominal edge web still requires fabricator acceptance. Printed shoulders and bushings support the board.

The revised enclosure is **14.0 mm high**. PCB bottom/top planes are Z=7.1/8.1. U2 is centered at (0,0); U1 is the 6 × 6 mm QFN at (-7.5,5); SW1 is centered at (12.65,0). The encoder magnet's lower face is Z=10.4, leaving nominal sensor package clearance of 1.8 mm released and 1.3 mm pressed. The cap pocket is Ø5.2 mm with a 0.2 mm roof shim; the magnet lower face stays at Z=10.4 mm. Use a diametrically magnetized neodymium Ø5 × 1.5 mm magnet and calibrate with the final phone and cell installed.

The Ø61.6 mm cap retains its full circumference grip, extending down to Z=1.0. Its pressed lower edge remains 0.5 mm above the phone plane. The annular switch pusher uses `pcb_top + 2.15`: nominal 0.25 mm free clearance above the 1.9 mm actuator, followed by nominal 0.25 mm switch displacement during the cap's 0.5 mm travel. Fit-test the switch and printed stack; the tactile switch must not act as the structural stop.

## Commercial CR2032 holder

BT1 is **MYOUNG BS-08-B2AA020-R, JLCPCB C964787**, mounted on the PCB underside. The exact footprint, pad numbers and OBJ/STEP model come from `tsci import --jlcpcb --download --use-exact-footprint C964787`; the imported files are unchanged. The manufacturer drawing specifies 24.1 × 15.7 mm body dimensions and **5.8 mm maximum height**. Clearance uses that maximum rather than the library model's 5.3 mm height. The holder's maximum envelope leaves 0.5 mm above the solid floor.

The footprint origin is (-1.2,0), which centers the manufacturer drawing's cell axis at (0,0) after the bottom-side mirror. Pin 1 is positive at (-12.999913,0), with a 3.5 × 3.8 mm SMT land; pin 2 is negative at (9.499915,0), with a 5.7 × 2.8 mm SMT land. These coordinates are top-view coordinates. Two regular tented routing vias at (2,-11) and (-2,-11) preserve the original power distribution; they are not battery contacts or wire attachment points.

Insert the CR2032 **positive face toward the solid bottom cover**, negative face toward the PCB. Insert the battery after PCB reflow. The commercial holder supplies retention and contacts. The bottom cover is permanently closed.

## Top battery access and cap release

The cap now has **two 0.6 mm PETG latch tongues** instead of six broad retention segments. Two 6 × 3.5 mm windows in the grip line up with two 3 × 1.4 mm radial ports in the housing, at 90° and 270°. The retention roof above the ports remains continuous, so aligning the ports alone does not unlock the cap. The 0.25 mm nominal lip engagement and 0.5 mm button travel are retained. Use PETG for the cap and flexure; repeated release of the thin latches has not been physically tested.

1. Remove the device from the phone. Rotate the cap until both grip windows align with the housing ports.
2. Insert the two printed `Cap_Release_Key_Print_2` keys through the windows and ports. Press both keys inward until their shoulders meet the housing, then gently lift the cap about 0.5 mm. Withdraw the keys and lift the cap clear. Do not force a latch that does not release; fit-test the port/key pair first.
3. Undo the **four M1.6 screws** securing the flexure and PCB spacers. Lift away the flexure and four bushings. Keep the loose bushings together.
4. Use the nonconductive `PCB_Lift_Pick` at the PCB edges near 0° and 180°, away from the parts. Raise both edges gradually, then lift the PCB, soldered holder and cell together straight upward along the four columns. Grip the PCB edge; do not pull on components or solder tails.
5. Turn the lifted PCB over, release the cell from the holder's open sides and fit a fresh CR2032. Positive face points away from the PCB.
6. Lower the board onto its shoulders and columns, refit the four bushings, flexure and screws, then snap the cap back on. Confirm free rotation, return travel and cap retention before use.

The keys have 1.0 × 2.4 mm blades and shoulders that limit nominal latch deflection to 0.35 mm. At that deflection the lip clears the bore by 0.10 mm and the latch inner face clears the PCB by 0.20 mm. The approximate release strain is 1.87%; this is not FEA or a measured fatigue limit. CAD checks both key paths, the intact retention roof and nine upward board/holder/cell positions from 0 to 24 mm. The initial edge-pick corridors clear rigid solids; actual pick leverage and component clearances require a printed/populated prototype.

There is **no bottom hatch, hatch seam, hatch post or M2 hatch screw**. The bottom cover and protective pad are continuous. The four existing top fasteners remain the reusable PCB mount.

The exported holder STEP contains its unloaded negative spring contact. Its 2.62 mm³ intersection with the nominal cell is reported separately as spring preload geometry; the cell has zero intersection with the rigid holder body. Contact deflection, insertion/removal motion, retention force and printed tolerances require a physical fit test. The top-service STEP illustrates the lifted and flipped board; cell insertion/removal from the spring holder is not a simulated trajectory.

## Programming and clearance

SWD pads are at Y=-14 and X=-4,-2,0,2,4, ordered VDD, GND, SWDIO, SWDCLK, nRESET in a top view. Viewed directly underneath, their order is **R, C, D, G, V**, matching the legend. Lift the PCB through the top and turn it over for programming. Use a fixture with narrow probes. VDD is a target-voltage reference; remove the primary cell before deliberately powering the board from the programmer.

TP_GND has a 0.4 mm plated drill; the remaining four 1.2 mm pogo pads are undrilled. GPIO diagnostic lands use 0.30 mm drills and 0.55 mm lands, with no fitted parts. All routing vias are tented on both sides. The holder's insulating housing separates the cell from PCB copper.

The antenna keepout is X=-3.5…3.5, Y=13.6…18.0 on both layers. Keep metal and attachment parts away from this volume where practical. The phone, cell and attachment magnets still affect RF and Hall readings.

## Bottom disc magnet tray

The ordered Ø5 × 1.5 mm discs replace the reserved segmented-ring magnet envelope. **24 inside-face pockets** in `Bottom_Cover` sit on a Ø49.25 mm pitch circle, spaced 15° apart with the first center at 7.5°. Each pocket is **Ø5.25 mm, 1.55 mm deep**: 1.5 mm magnet plus 0.05 mm nominal adhesive thickness. Diametral clearance is 0.25 mm. Adjacent pockets have 1.178 mm nominal plastic web, with 1.000 mm inner and 0.800 mm outer tray walls; a 0.800 mm continuous housing rim supports the flange above. The phone-facing skin remains 0.6 mm, plus the separate 0.2 mm protective pad. Print a fit coupon or test one pocket before committing the magnets; printer and magnet tolerances may need adjustment.

The pocket walls are a raised tray integral with the bottom cover. The stationary housing has clearance for that tray and an upper recess for a continuous **steel backing ring, ID44.05 × OD54.45 × 0.7 mm**. This is a separate metal reference part, not a printed magnet or a verified magnetic shield. Both it and the discs load from below while the cover is off. A backing ring cannot pass through individual Ø5.25 mm holes, which is why the locating pockets are in the separate cover rather than trapped under a housing roof.

Insert the backing ring into the housing recess first. Check the ordered magnets' axial polarity and attraction against the intended phone or case before gluing. Fit 24 discs into the cover pockets with a thin adhesive layer beneath each disc. Their upper faces sit flush with the tray at Z=2.35 mm, and the backing ring starts at Z=2.40 mm. Dry-fit the loaded cover, then bond it to the housing's mating faces. Subsequent battery service uses the top opening. Use the **new cap, housing and solid bottom cover together**. The PCB, soldered holder and flexure retain their geometry and assembled height.

The custom disc layout is a mechanical prototype, not a MagSafe-qualified array. The purchased part's magnetization direction has not been confirmed. Polarity distribution, holding/sliding/rotation force, sensor offset/saturation and BLE performance require tests with the actual assembled phone. Do not assume that a uniform axial-disc circle reproduces Apple's prescribed ring polarity. The central encoder magnet remains diametrically magnetized and separate from these attachment magnets.

## Editable enclosure and supplied parts

`build_enclosure.py` and `enclosure-parameters.json` regenerate the assembly with CadQuery ≥2.6. Run from the project root:

```sh
python mechanical/build_enclosure.py --out work/enclosure
```

`Print_STL/` contains four main enclosure parts: Rotating_Cap, Stationary_Housing, Flexure_Retention_System and Bottom_Cover. Also print four PCB spacers, two cap release keys and one PCB lift pick from their named STL files. Corresponding editable solids are in `STEP_Parts/`. Use the complete revised cap/housing/cover set; older caps and housing ports do not form the new release mechanism.

Released, pressed, exploded and top-service assemblies are included in the downloadable mechanical handoff. Electronics other than the holder are board/key-package bounding references; the circuit now combines the actual populated PCB with the released enclosure in `previews/3d.glb`. Its 12 assembly models exclude these electronic bounding dummies and the duplicate holder. `previews/pcb-3d.glb` retains the bare board view. The three outer shells are translucent in the circuit viewer. The builder also exports aligned OBJ/MTL files in `Circuit_Models/`; copy these into `mechanical/Circuit_Models/` after a CAD revision. Attachment discs now match the ordered dimensions; magnetic performance is untested. The flexure calculation is an approximate cantilever estimate rather than FEA or a measured return force.

Sources: [MYOUNG holder drawing](https://xonstorage.z8.web.core.windows.net/pdf/myoung_bs08b2aa020_apr22_xonlink.pdf), [JLCPCB holder listing](https://jlcpcb.com/partdetail/MYOUNG-BS_08_B2AA020R/C964787), [C&K KMR2 drawing](https://www.ckswitches.com/media/1479/kmr2.pdf).
