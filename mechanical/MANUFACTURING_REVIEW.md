# Rotation-only printed pilot review

Scope: confirmed10–50-unit 3D-printed pilot. This supersedes the spring/press recommendation for the earlier full-cap-click design: the user has removed the push action entirely. There is no mechanical reason to keep return springs once the carrier is fixed to the base. A software count-clear action is not supplied in this repository; no replacement physical input is added. Hardware nRESET remains for programming/service and is distinct from count clearing.

| Per-unit inventory | Prior press pilot6224fc9 | Rotation-only |
| --- | ---: | ---: |
| Rigid printed parts |5|4|
| Screws / screw-driving operations |10|7|
| Loose return springs |3|0|
| Guide washers |3|0|
| Silicone actuator |1|0|
| Handled parts, PCBA counted as one |27|16|
| Adhesive joints |3 including actuator|2|
| Fitted electronic components |31|28|

The16 handled parts are four prints, four PCB screws, three cap screws, one bearing, one cell, one encoder magnet, one attachment ring and one PCBA. Adhesive, consumables, optional shims and reusable fixture halves are excluded. No measured assembly time is claimed. The three removed screw drives and11 fewer handled pieces should reduce touch time; log kitting, preparation, curing, assembly, inspection and rework separately in ASSEMBLY_TIME_STUDY.csv.

The integrated base retains the bearing shaft via three solid webs in the former guide locations. A removable nut retains the inner race; three cap screws and the outer ring retain the rotating outer race. These interfaces preserve service access and the validated envelope without tiny snap components. Four nylon PCB screws are the only supported board-retention configuration. Do not mix older press parts or optional two-screw trials into this print set.

The base remainsØ58 mm and the topZ17.2 mm, with a17.0 mm contact-to-top height. The bearing, board, antenna and encoder poses are unchanged. Shaft diameter39.7 mm gives nominal0.15 mm radial clearance to the40 mm bearing bore; housing50.2 gives nominal0.10 mm radial clearance around the50 mm outer race. Coarse-thread pitch1.2 mm and groove allowance0.15 mm need an actual printer/coupon fit. The retainer's M2 pilot wall is0.8 mm; cap socket outer wall1.2 mm and countersink rim1.0 mm. Nominal cap screw overlap4.4 mm is geometry, not tested thread strength. The reusable split nest supports the retainer before bearing insertion and opens≥3 mm per half for ejection.

The [Ploopy assembly reference](https://ploopyco.github.io/knob/assembly-instructions/) and [hardware list](https://ploopyco.github.io/knob/appendices/hardware/) support the fixed-housing/bearing/rotating-top approach. Its25×32×4 mm bearing and press-fit top are not interchangeable with ours. Our larger purchased bearing and reversible fasteners serve the hollow36.5 mm PCB enclosure. No evidence establishes this as an objectively best or manufacturing-qualified design.

Before releasing the batch:

1. Confirm the actual printer/nozzle/filament and fit coupons; print one circular prototype. Remove supports completely and measure fits/warpage.
2. Qualify bearing shaft/housing/shoulder contact, nut and cap screw torque, pull-out, drag, wobble and repeated service. Do not force fits or load shields.
3. Confirm actual purchased bearing, screws and ring drawings/sample dimensions, ring working face and central magnet specification. No purchase/order was made.
4. Qualify the two adhesive joints for print material, cure, peel/shear and aging. Verify magnet retention.
5. Measure Hall angle/count accuracy, interference from the steel bearing, both magnet assemblies and intended phone/case. Verify BLE and battery performance. Firmware and count-clear UX remain separate work.
6. Record assembly time and rework for several units; then approve the10–50-unit pilot. CAD, meshes and a slicer do not replace these physical gates.

Current machine-readable evidence is validation/rotation-only-status.json, validation/rotation-only-cad-audit.json and validation/print-readiness.json. Earlier force/press and two-screw reports remain historical and are not current acceptance evidence.
