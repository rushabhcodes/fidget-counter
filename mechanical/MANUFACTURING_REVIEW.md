# Rotation-only printed pilot review

Scope: confirmed10–50-unit PETG pilot, with rotation only. No springs, sliding carrier, pusher, actuator or user push button remain. Hardware nRESET is retained for programming/service. Firmware and count-clear UX are not supplied.

| Per-unit inventory | Press pilot6224fc9 | Hosted1.0.25 | Local V7 |
| --- | ---: | ---: | ---: |
| Rigid prints |5|4|4|
| Screw drives |10|7|5|
| Return springs |3|0|0|
| Guide washers |3|0|0|
| Silicone actuator |1|0|0|
| Handled parts; PCBA counted as one |27|16|14|
| Adhesive joints |3|2|2|
| Fitted electronics |31|28|28|

The14parts are four prints, two nylon PCB screws, three cap screws, one bearing, one cell, one encoder magnet, one attachment ring and one PCBA. Adhesive, shims, consumables and reusable tooling are excluded. Log preparation, curing, assembly and rework separately in ASSEMBLY_TIME_STUDY.csv; no measured touch-time claim is made.

The base retains three solid bearing webs. A coarse removable nut retains only the inner race; three top-entry screws join the cap to the outer-race retainer. All four board posts and two rigid collars remain, with opposite PCB screws at45°/225°. Board retention and deflection must be tested physically. Bayonet/snap-fit alternatives were evaluated but not selected for this supported-print pilot; see [battery and assembly review](BATTERY_AND_ASSEMBLY_REVIEW.md) for reasons, sources and the larger-cell assessment.

The base remainsØ58mm and topZ17.2mm,17.0mm above phone-contact face. The standard6808-ZZ /61808-2Z bearing is40×52×7mm atZ6.1–13.1. Nut moves up0.5mm; PCB and encoder poses remain unchanged. ShaftØ39.7 and housingØ52.2 give nominal radial clearances0.15 and0.10mm. Cap screw pitch radius is27.8mm; nominal thread overlap4.4mm, pilot wall0.8mm, socket outer wall1.2mm and countersink rim1.0mm. The common cap deck is1.3mm thick; decorative thumb-dish cuts do not remove its protected material. Thread pitch1.2mm/groove allowance0.15mm require actual printer coupons. The split nest supports the retainer’s three shallow saddles atZ5.1 before bearing insertion and opens≥3mm per half.

Before batch release:

1. Confirm printer/nozzle/filament; print fit coupons then one circular prototype. Current slicer assumption is generic0.4mm nozzle,PETG,0.15mm layers,0.20mm first layer and four walls. Remove supports and measure fits/warpage.
2. Qualify bearing land contact, drag/wobble/retention, thread torque/pull-out and repeated service. Confirm the actual bearing/screws/ring drawings and samples; avoid loading bearing shields.
3. Test two-screw board retention, bending, shock and vibration before accepting the reduced count. All four original holes remain if testing calls for four screws.
4. Qualify both adhesive joints, encoder retention, supplier ring dimensions and phone-facing polarity, peel/shear/cure/aging.
5. Measure Hall/count accuracy, steel/magnetic/phone interference, BLE and battery performance. Firmware and actual runtime remain unverified.
6. Measure assembly time and rework across several units before approving the10–50-unit pilot. Digital CAD/mesh/slicer checks do not qualify physical production.

V7 geometry comparison is pinned to verified1.0.25 commit0397495; the earlier rotation-removal electrical proof against6224fc9 remains active. The latest local evidence is validation/assembly-optimization-status.json, validation/rotation-only-cad-audit.json and validation/print-readiness.json. Earlier press/two-screw reports remain historical. No new GitHub or tsCircuit publication is claimed by this review.

The fixed threaded throat isØ37.3mm, matching the lower shaft bore and giving0.4mm nominal radial PCB insertion clearance. The formerØ36.4mm throat blocked theØ36.5mm board during assembly despite clearing it in the seated pose. The male thread root now has0.85mm nominal radial wall; print-coupon torque/life testing is still required. Continuous swept-volume checks cover the actual drilled PCB, all28 fitted supplier-model bounds and the cell, and retain a failing comparison with the former throat. See validation/pcb-insertion-audit.json.
