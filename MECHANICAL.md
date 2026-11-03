# Rotation-only push-fit pilot

This document describes the preserved **V1 premade-ring layout**. The new [V2 individual-magnet base](mechanical/variants/V2_discrete_magnets/README.md) has separate CAD, prints and force-test instructions. Both retain16.4 mm physical height, the same bearing/PCB/cap interfaces and1.8 mm nominal encoder gap. V2 is an experimental alternative pending an A/B holding-force test.

The Ø58 mm PETG base has an integral fixed bearing shaft and three solid support webs. A purchased **6808-ZZ / 61808-2Z, 40×52×7 mm** bearing supports the hollow rotating cap. Following [Ploopy's assembly principle](https://ploopyco.github.io/knob/assembly-instructions/), the bearing pushes into the cap and the cap/bearing pushes onto the base. Ploopy's own 6705ZZ is 25×32×4 mm and cannot surround our Ø36.5 mm board; our CAD is independent.

**One unit: two prints, two M2×4 nylon PCB screws, nine handled parts.** The other five are bearing, PCBA, cell, encoder magnet and attachment ring. There are no top screws, nut, outer retainer, spring, press mechanism or snap tabs. Adhesives, shims and reusable tools are excluded from the count. Assembly time is unmeasured.

## Fit and dimensions

Print Stationary_Base and one Cap from the [manifest](mechanical/print-ready-manifest.json). All eleven cap styles share the interface. The base is Ø58 mm; the largest cap is Ø61.6 mm; top datum is Z16.6 mm, **16.4 mm above the phone-contact face**. The CR2450 revision raises PCB/sensor/encoder internally without another exterior height increase.

The bearing is at Z6.1–13.1 mm. Nominal shaft Ø40.05 and cap bore Ø51.95 give **0.05 mm diametral interference** at each race. The inner shoulder contact land is Ø42.0, matching the NSK recommendation and ZKL maximum for this envelope. Actual shield/race geometry must match the purchased sample. The fixed shaft's Ø37.3 mm throat gives 0.4 mm radial PCB insertion clearance and 1.375 mm nominal radial shaft wall. The nominal structural cap deck remains1.3mm thick; the local roof over the fixed-height encoder magnet is1.2mm. Existing thumb dishes retain their0.9mm minimum local deck. The entire grip profile moves0.6mm lower while keeping its8mm grip height. The connector has0.78mm conservative swept clearance. See [the compact-cap review](mechanical/COMPACT_CAP_REVIEW.md).

This is a **coupon-calibrated fit-test pilot**, not a qualified press fit. It has **no positive axial lock**. PETG shrinkage, bearing tolerances and creep can make the nominal interference either loose or excessively tight. Use the ten [fit coupons](validation/bearing-fit-coupons.json) and [PETG instructions](mechanical/printing/PRINTING.md) before printing a batch. Do not scale an entire STL to correct a fit.

## Assembly

Use the illustrated [step-by-step assembly and acceptance guide](ASSEMBLY.md). The sequence below is the mechanical summary.

1. Print, clean and measure the two product parts after coupon calibration. Remove supports from the ring pocket and bearing shoulder. Confirm seating and a light hand-only push fit with the actual bearing. Reject and recalibrate an excessively tight or loose fit; do not hammer, clamp the complete assembly, or transmit pressing force through the balls/shields.
2. Verify the ring's dimensions and phone-facing polarity. Bond it into the base's integrated seat with the specified nominal 0.10 mm bondline. Bond the Ø5×1.5 mm diametric encoder magnet against the cap's integral Z15.4 stop using sidewall adhesive, with no axial glue layer. Cure both joints before loading them.
3. Program and inspect the PCBA before enclosure assembly; use the [RevC pilot firmware](firmware/README.md) and require flash verification. Remove the CR2450 before powered programming. Inspect the soldered C7525448 holder and insert the cell with verified polarity.
4. Lower the PCBA/holder/cell through the shaft onto four support posts. Align the four Ø2.2 mm drills at R16.6. Fit **two opposite M2×4 nylon screws** at 45°/225°, with head Ø3.8×1.3 mm maximum and no conductive washers. Qualify screw torque, post strength and board deflection.
5. With the cap's bearing seat supported, seat the bearing fully into the cap by hand. Lower the cap/bearing onto the fixed shaft, pushing lightly and evenly near the axis. The nominal fits are acceptable only if this hand-only operation does not load or damage the races. A high-force operation requires a revised fit and appropriate race-specific tooling, not extra force on the cap.
6. Confirm free rotation, seating, axial retention, wobble and both magnet bonds. Measure pull-off force and phone/case attachment loads. Test Hall/count/BLE with bearing, ring and phone present. No push/reset action remains.

For service, pull the cap assembly straight off evenly. The bearing may remain on either fit depending on actual tolerances; remove it with support on the appropriate race. Repeated removal can loosen PETG and must be tested. Remove the two PCB screws to lift the PCBA/holder for battery replacement or programming. If acceptable service/retention cannot coexist, revert to a positively retained joint before batch release.

## Evidence and limits

All twelve product alternatives are valid single STEP solids and watertight, consistently wound STLs. Actual PrusaSlicer2.8.1 toolpaths were generated for generic PETG/0.4 mm nozzle, 0.15 mm layers; no warnings remained. All eleven caps retain the exterior/encoder interfaces. An exact whole-solid comparison against b300e19 permits the prescribed0.6mm shell translation while restoring the established bearing plane and encoder pocket. The complete base is unchanged; unexplained material changes and either magnet/sensor movement fail. Continuous clearance and 24-angle rotation checks pass, with intended bearing-fit interference checked separately. All 27 fitted supplier electronics remain checked, including the loaded-holder contact exception described in [CR2450 revision](mechanical/CR2450_UPGRADE.md).

Actual assembled, cutaway and exploded CAD is shown in [the preview](previews/bearing-layout.png). Races, 21 balls, cage, shields, cell gasket and supplier STEP electronics are modeled; internal bearing details remain representative, not supplier drawings.

Physical print yield, seating/pull-off force, race contact, PETG creep, drop/shock, board screw retention, adhesive aging, magnetic sensing, RF, battery contacts/runtime and firmware/end-of-line tests remain open. Measure assembly time over several units. The digital checks support a controlled prototype print; they do not qualify a 10–50-unit manufacturing batch.
