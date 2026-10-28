# Fidget Counter — automatic-lock release 1.0.15

All eleven cap options are now complete, single-piece rotor/grip modules. There are no decorative-cap screws, nuts or additional grip-to-hub joint. Each printed top includes the guide sleeve, continuous retention flange, protective underplate, annular switch pusher and blind encoder-magnet pocket. All modules use the same existing two-clip guide base and bottom attachment-magnet tray. The nominal top plane remains 15.2 mm and the gripping edges remain 8 mm deep.

## Screw-free grip swapping

Pull BOTH opposed base tabs outward about 0.8 mm, lift the entire top module straight out, align a replacement's guide sleeve and press it in until both retaining hooks have re-engaged. The module may be inserted at any rotational angle. Upper hook ramps provide the intended snap-in cam; actual insertion force and re-engagement must be confirmed in a PLA print. Do not squeeze the tabs inward. No screwdriver or separate twist-lock joint is needed to change grips.

Each top requires its OWN diametrically magnetized Ø5 × 1.5 mm encoder disc. The axial magnets in the bottom tray do not move and cannot replace the diametric encoder. Install each encoder at Z10.4–11.9 in its Ø5.2 mm blind pocket, with a 0.2 mm nonmagnetic spacer against the Z12.1 pocket roof. Bond it only after checking its fit, field and installed depth. The roof and adhesive hold it in the moving top. Extra printed caps without encoder magnets will not measure rotation. Their magnets do not add to the overall height.

Use the same type/grade of encoder disc in each module. Firmware should ignore a missing magnet during removal and re-establish the angular baseline after reattachment, to avoid counting the swap as a turn. That behavior has not been implemented or verified here; counter-reset firmware remains outside this mechanical revision.

## Pressing and battery service

The complete top descends 0.25 mm to the base hard stop. The annular pusher contacts the inward SW1 actuator at every rotation angle, and the switch dome supplies axial return. There is no separate return spring or yellow flexible ring. The base clips retain the module radially and provide 0.05 mm nominal upward float.

The PCB uses two inward-facing snap latches at the diagonal holes near (+10.748, +10.748) and (−10.748, −10.748) mm. Two recessed locating posts support the remaining holes. All four hole centers move radially inward from 16.2 to 15.2 mm, and the holes shrink from Ø3.6 to Ø3.0 mm. The PCB and printed base read this pattern from the same `pcb_mount` parameter block. Use the revised PCB and base together; the earlier hole pattern is superseded.

Lower the populated board onto all four support shoulders, then press near the two latches until both hooks engage. The printed features within the PCB thickness stay inside the drilled bores: the minimum nominal radial clearance is 0.203 mm. The rigid locators have 0.40 mm radial clearance and stop 0.35 mm below the PCB top. The retaining lips start 0.15 mm above the seated PCB, with 0.30 mm inward retaining overlap. There are no bolts, screws or separate retaining washers.

For a cell change, remove the cap, push BOTH diagonal PCB latch tips radially outward by about 0.60 mm, and lift the board by its edges with the soldered holder and cell. Keep the tips displaced until the board clears them. The prescribed release pose leaves 0.158 mm minimum nominal hook-to-hole clearance. The beam is 0.60 mm thick and 1.20 mm wide; its strain estimate is a sizing calculation, not FEA. Finger access, force, spring-back and repeated release need a printed/populated prototype. SW1 stays at (0, −5) mm and the Hall sensor stays centered.

[The mount section and hole-pattern drawing](previews/pcb-automatic-lock.png) shows the gap above the PCB and the material remaining around each hole. `validation/pcb-mount-clearance.json` checks the actual Circuit JSON drill pattern against the STEP base and checks that the real GLB PCB faces have open bores. It does not use a replacement PCB mesh for the circuit preview.

## Print and check

Print one revised Stationary_Base, one Bottom_Tray and any selected Cap_*.stl from mechanical/Print_STL. Each Cap_ file is a COMPLETE top module. Supplied STLs are bed-oriented: the top surface of each cap faces the bed and its guide sleeve faces upward. Keep the PCB latch channels free of support residue. Use localized support for base overhangs that your slicer cannot bridge. Clear both cap-release channels before fitting the backing ring and bonding the tray. Retain the previous bottom magnet array and backing ring.

The CAD checks cover valid single solids, closed STL meshes, the shared guide/flange/pusher/spacer through rotation and the 0.25 mm stroke, full-circle grip clearance, cap-hook retention, PCB-hook retaining overlap, prescribed release poses, top extraction and thirteen PCB/holder/cell extraction heights. Release poses are clearance models, not FEA or measured force. PLA fatigue, retention strength, tolerances, edge-press tilt and switch return require printed testing. Test one base and one cap before printing the full set. Verify that both PCB hooks automatically return after insertion, retain the board, and can be released for cell changes.

The supplier component models are unchanged. PCB routing and fabrication exports match the inward button position. The previous service collar, PETG return ring, separate rotor hub and cap screws are superseded.

## Regenerate the CAD

Use Python with mechanical/requirements.txt installed. Run `python mechanical/build_enclosure.py --style all`, then `python mechanical/export_circuit_models.py`. The builder produces all STL/STEP parts and released, pressed and exploded STEP assemblies under mechanical/export. Copy the newly checked STL/STEP parts into mechanical/Print_STL and mechanical/STEP_Parts, and the geometry audit into mechanical/enclosure-validation.json before publication. The exporter refreshes all eighteen mesh assets and the eleven-style TypeScript selector. Select a cap using CAP_STYLE near the top of index.circuit.tsx, rebuild it and refresh published.circuit.json to change the registry preview.

## PCB and cell stack

The PCB is Ø36.5 × 1.0 mm at Z7.1–8.1 with four Ø3.0 mounting holes on radius 15.2 mm. BT1 is the exact imported MYOUNG BS-08-B2AA020-R / JLCPCB C964787 underside holder. Its manufacturer maximum height is 5.8 mm; the shorter visual model is not the clearance limit. The CR2032 positive face points toward the solid bottom tray. Insert the cell after reflow. Mounting holes leave a nominal 1.55 mm FR4 edge web, increased from the earlier 0.25 mm. Manufacturing tolerances and printed fit still need supplier/prototype review. The diametric encoder-to-sensor gap is nominal 1.8 mm released and 1.55 mm pressed. No firmware is included.

## Five-pin JST-SH programming access

J_DEBUG is a fitted SM05B-SRSS-TB(LF)(SN) five-pin, 1.0 mm pitch side-entry connector on the PCB top at (0, −13.3) mm, with its cable entry facing −Y. Its 7.0 × 4.25 × 2.9 mm body and approximately 8.30 × 6.04 mm footprint courtyard replace the TC2030 lands and all three alignment holes. The PCB now has only the four enclosure mounting holes. The original thirty fitted components and enclosure solids are retained; J_DEBUG adds one fitted component.

The supplier STEP is about 2.911 mm high after its library mounting offset. Its nominal minimum clearance beneath the fully pressed cap ribs is about 0.74 mm. A conservative 8.3 × 6.1 × 2.92 mm envelope clears the base and all eleven caps by at least 0.73 mm throughout a continuous 360° rotation and the full 0.25 mm stroke. The imported preview mesh is checked against the supplier STEP. See `validation/jst-connector-clearance.json`; regenerate it with `python validation/check-jst-fit.py` after building the source with GLB output and installing `mechanical/requirements.txt`.

Remove the cap, release both PCB latches and lift the board for programming; the base has no lateral cable opening. Remove the CR2032, select **3V3** on programmer J3 and connect a straight-through five-way JST-SH cable with SHR-05V-S-B housings. Disconnect the cable before reseating the PCB and cap. Pin 1 follows the programmer voltage selector, so 5V must never be selected with this board connected. Cable mating, retention and printed tolerances need a populated prototype. See [PROGRAMMING.md](PROGRAMMING.md).
