# Fidget Counter — One-piece V4 / registry release 1.0.8

All eleven cap options are now complete, single-piece rotor/grip modules. There are no decorative-cap screws, nuts or additional grip-to-hub joint. Each printed top includes the guide sleeve, continuous retention flange, protective underplate, annular switch pusher and blind encoder-magnet pocket. All modules use the same existing two-clip guide base and bottom attachment-magnet tray. The nominal top plane remains 15.2 mm and the gripping edges remain 8 mm deep.

## Screw-free grip swapping

Pull BOTH opposed base tabs outward about 0.8 mm, lift the entire top module straight out, align a replacement's guide sleeve and press it in until both retaining hooks have re-engaged. The module may be inserted at any rotational angle. Upper hook ramps provide the intended snap-in cam; actual insertion force and re-engagement must be confirmed in a PLA print. Do not squeeze the tabs inward. No screwdriver or separate twist-lock joint is needed to change grips.

Each top requires its OWN diametrically magnetized Ø5 × 1.5 mm encoder disc. The axial magnets in the bottom tray do not move and cannot replace the diametric encoder. Install each encoder at Z10.4–11.9 in its Ø5.2 mm blind pocket, with a 0.2 mm nonmagnetic spacer against the Z12.1 pocket roof. Bond it only after checking its fit, field and installed depth. The roof and adhesive hold it in the moving top. Extra printed caps without encoder magnets will not measure rotation. Their magnets do not add to the overall height.

Use the same type/grade of encoder disc in each module. Firmware should ignore a missing magnet during removal and re-establish the angular baseline after reattachment, to avoid counting the swap as a turn. That behavior has not been implemented or verified here; counter-reset firmware remains outside this mechanical revision.

## Pressing and battery service

The complete top descends 0.25 mm to the base hard stop. The annular pusher contacts the inward SW1 actuator at every rotation angle, and the switch dome supplies axial return. There is no separate return spring or yellow flexible ring. The base clips retain the module radially and provide 0.05 mm nominal upward float.

For a cell change, release the top as above, remove the four existing M1.6 PCB retaining screws, lift the PCB with its soldered bottom holder, then replace the CR2032. The screw-free change applies to the interchangeable tops; the PCB retainers remain. The matching circuit places SW1 at (0, −5) mm; the Hall sensor stays centered.

## Print and check

Print one Stationary_Base, one Bottom_Tray, four PCB_Retainer_Print_4 parts and any selected Cap_*.stl from mechanical/Print_STL. Each Cap_ file is a COMPLETE top module; do not print or attach the previous separate hub. Supplied STLs are already bed-oriented: the top surface of each cap faces the bed and its guide sleeve faces upward. Use localized PLA support for the base clips and any overhanging features that your slicer cannot bridge. Remove all support from the clip gaps through the underside relief channels before fitting the backing ring and bonding the tray. Use the previous bottom array, backing ring and four PCB fasteners.

The CAD checks cover valid single solids, closed STL meshes, the shared guide/flange/pusher through rotation and the 0.25 mm stroke, full-circle grip clearance, two-hook retention, prescribed outward clip release, top extraction and PCB/holder/cell extraction. The clip release pose is a clearance model, not an FEA result or measured strain/force. PLA fatigue, retention strength, tolerances, edge-press tilt and switch return require printed testing. Test one module before printing the full set. After changing shapes, verify smooth rotation, secure retention, correct sensing and complete return after pressing anywhere on the grip.

The supplier component models are unchanged. PCB routing and fabrication exports match the inward button position. The previous service collar, PETG return ring, separate rotor hub and cap screws are superseded.

## Regenerate the CAD

Use Python with mechanical/requirements.txt installed. Run `python mechanical/build_enclosure.py --style all`, then `python mechanical/export_circuit_models.py`. The builder produces all STL/STEP parts and released, pressed and exploded STEP assemblies under mechanical/export. Copy the newly checked STL/STEP parts into mechanical/Print_STL and mechanical/STEP_Parts, and the geometry audit into mechanical/enclosure-validation.json before publication. The exporter refreshes all eighteen mesh assets and the eleven-style TypeScript selector. Select a cap using CAP_STYLE near the top of index.circuit.tsx, rebuild it and refresh published.circuit.json to change the registry preview.

## PCB and cell stack

The PCB is Ø36.5 × 1.0 mm at Z7.1–8.1 with four Ø3.6 mounting holes on radius 16.2 mm. BT1 is the exact imported MYOUNG BS-08-B2AA020-R / JLCPCB C964787 underside holder. Its manufacturer maximum height is 5.8 mm; the shorter visual model is not the clearance limit. The CR2032 positive face points toward the solid bottom tray. Insert the cell after reflow. Mounting holes leave a nominal 0.25 mm FR4 edge web requiring CAM acceptance. The diametric encoder-to-sensor gap is nominal 1.8 mm released and 1.55 mm pressed. No firmware is included.
