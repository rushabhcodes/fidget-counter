# CAD assembly review — inward-hole snap release 1.0.15

Reviewed 21 October 2026 against the current tscircuit/TSCI documentation and published assembly examples. The baseline is `rushabhcodes/fidget-counter` **1.0.9**, registry release `83816545-a250-44e1-84dc-c80f5abda733`. Updated 23 October 2026 with the TC2030 interface and inward, clearance-fit PCB mounts. The online 1.0.9 release has not been changed.

## Documentation and examples used

- [Device assembly](https://docs.tscircuit.com/elements/assembly-device), [subassembly](https://docs.tscircuit.com/elements/assembly-subassembly) and [CAD assembly alias](https://docs.tscircuit.com/elements/assembly-cadassembly): retain the real board and place mechanical models beside it in `assembly.device`. `assembly.cadassembly` is a supported alias of `assembly.subassembly`.
- [Mounting 3D models](https://docs.tscircuit.com/guides/tscircuit-essentials/mounting-3d-models): align mechanical features with actual board holes; use millimetres and the PCB midplane as Z=0. Rendering hardware does not create PCB holes.
- [Advanced assembly](https://docs.tscircuit.com/guides/advanced-assembly): explicit model placement is distinct from face mating. Mounting does not automatically certify collisions or mechanical fit.
- [Abse's smartwatch](https://tscircuit.com/abse/smartwatch-flex-top-only/blob/watch.circuit.tsx), version 0.2.22: native board plus named mechanical siblings and a shared case-to-PCB frame. Its newer `assembly.part` API is not required to use the supported `cadassembly` alias in this project's pinned core.
- [ShiboSoftwareDev's Linux Game Boy](https://tscircuit.com/ShiboSoftwareDev/linux-gameboy-advance/blob/mechanical/GbaEnclosure.tsx), version 1.0.149: named mechanical parts, explicit retention/clearance models and separate physical qualification. Its screws are examples of that product's retention, not a requirement to add screws here.
- [Book-reading clip lamp](https://tscircuit.com/muse/book-reading-clip-lamp/blob/lamp-enclosure.tsx), version 0.4.4: imported/generated models in `assembly.cadassembly`, real PCB geometry and translucent enclosure shells. This directly matches the API pattern retained here.

Reference source files were read from the public registry API and recorded by release ID and SHA-256 in the parent review folder. Current web documentation may describe APIs newer than the pinned `tscircuit` 0.0.2748 / core 0.0.2097 / props 0.0.689. The assembly uses supported installed props; no speculative props or dependency upgrade were introduced.

## Changes

The 1.0.9 cap already used automatic snap retention. Its PCB still depended on four M1.6 screws and four separate printed retaining washers. Those PCB fasteners are replaced with **two integral automatic snap latches**, with two other posts providing location. The barbs face inward, away from the thin outer FR4 hole webs. Insertion ramps let the board press into place; push both diagonal latch tips radially outward to release it. The current four native mounting holes are Ø3.0 mm on R15.2 mm, as detailed below.

The 0.2 mm nonmagnetic encoder spacer listed in the BOM was missing from the native CAD assembly. It is now represented and moves with the rotor/magnet in pressed and exploded CAD states. The selected assembly has eight mechanical models: base, tray, cell, backing ring, attachment magnets, encoder magnet, spacer and one selected cap. The printable set is thirteen parts: the shared base/tray and eleven cap variants.

## Verification scope

| Item | Verification |
|---|---|
| Native circuit | Actual routed board remains inside `assembly.device`; no replacement PCB mesh or duplicated electronics |
| Mechanical identities | All eleven cap selectors render eight uniquely named CAD-only parts; no electrical ports, PCB footprints or screw parts |
| Coordinate frame | Millimetres, Z-up; −7.6 mm case-to-PCB offset; each built model's exported bounds checked against its OBJ |
| PCB mounting | Four native Ø3.0 mm holes on R15.2 mm match the posts; the base has zero intersection with actual PCB material and both GLB PCB faces have open drills |
| Electrical preservation | All thirty fitted component identities, footprints, placement and CAD compared with the pre-TC2030 baseline; updated drill geometry and SWDIO routing validated separately |
| Moving assembly | Eleven caps × three press positions × twelve rotation angles; shared rotor, magnet and spacer checked by exact intersections plus full-circle cap envelopes |
| PCB service | Retention tested with a small board lift; thirteen released PCB/holder/cell extraction heights checked |
| Print meshes | Thirteen printable STL meshes checked for closed topology, consistent winding and positive volume |
| Supplier models | Original imports and all thirty fitted part meshes checked separately |
| Cloud artifacts | Checked source/model hashes bind the saved circuit and preview artifacts; cloud restore verified locally |

Use the fresh JSON reports under `validation/` for measured results. The original public 1.0.9 viewer was inspected and did render its assembly; release 1.0.15 includes the revised snap-lock assembly.

## Physical limits

This is a nominal CAD prototype. The PCB latch deflection is a prescribed clearance pose, not FEA; printed insertion force, spring-back, release access, pull-off strength and fatigue remain untested. Test one base and one cap with the populated board before printing every grip. The mounting-hole edge web is now 1.55 mm nominal, increased from 0.25 mm. Latch retention and actual board strength still need physical testing. Cap return, edge pressing, magnetic calibration and BLE performance also require a populated prototype.

See [MECHANICAL.md](MECHANICAL.md) for assembly/release directions and [PROGRAMMING.md](PROGRAMMING.md) for SWD programming.

## Programming interface revision — 23 October 2026

Release 1.0.15 replaces the custom five-pad SWD row with the exact `StandardTagConnectSwd` geometry/pinout from `@tsci/tscircuit.standard-jst-programmer@0.8.0`. It is placed on the PCB top face at (0, −13.3) mm, with three alignment holes and no fitted connector or added height. The target wrapper declares electrical pin roles, the connector element and top-entry direction; the library pad, hole and courtyard geometry is preserved. Programmer pin 1 supplies fixed 3.3 V to VBAT with the CR2032 removed; pin 6 (USB 5 V) is NC. The programming guide now includes the programmer's CMSIS-DAP/OpenOCD workflow.

The earlier electrical-preservation comparison describes the snap-lock-only revision. It is superseded for programming copper and contact geometry by `validation/programming-interface.json` and `validation/programming-check-summary.json`. All thirty fitted components and the enclosure geometry are retained. The revised saved circuit and previews require local validation and refreshed cloud artifacts; this edit does not authorize publication.

## Inward mounting holes and clearance-fit latches — 23 October 2026

The PCB remains bolt-free. Four mounting holes move from R16.2 to R15.2 mm and shrink from Ø3.6 to Ø3.0 mm, increasing the nominal edge web from 0.25 to 1.55 mm. The PCB and base now read the same `pcb_mount` parameter block. The earlier mounting geometry above is superseded.

The two rigid locators stop 0.35 mm below the PCB top and have 0.40 mm radial clearance. Latch features within the drilled holes have at least 0.203 mm nominal radial clearance. Retaining lips start 0.15 mm above the board and overlap it by 0.30 mm; a 0.60 mm outward release leaves 0.158 mm minimum nominal clearance. No hardware has been added. The SWDIO branch was adjusted around the moved lower-left latch. The recessed locators use the native circular hole-clearance rule; additional assembly keepouts apply to the two above-board retaining lips; all thirty fitted component records are retained.

The final verification compares the actual Circuit JSON outline/drills with the base STEP solid and samples both native GLB PCB faces around all seven non-plated holes. See `validation/pcb-mount-clearance.json` and `validation/pcb-mount-check-summary.json`. Printed tolerances, insertion/release force and fatigue remain prototype tests. These changes are included in release 1.0.15.

## Five-pin JST-SH replacement — 29 October 2026

Release 1.0.18 supersedes the TC2030 programming interface described above. J_DEBUG now uses the exact `StandardJstSwdResetSide` footprint and five-signal pinout from programmer package 0.8.0: JST SM05B-SRSS-TB(LF)(SN), JLCPCB C136657, mounted on top at (0, −13.3) mm with cable entry toward −Y. The matching supplier OBJ/STEP are cached under `imports/SM05B_SRSS_TB` and recorded in `validation/jlc-imports.json`. Five signal lands and two mounting tabs receive solder paste; all six bare contacts and three alignment holes are removed. The two battery junction vias move to Y=−9.4 mm, and the five programming branches and adjacent battery-junction branches are rerouted for the new lands.

The original thirty fitted components are still compared against their existing preservation baseline. J_DEBUG is checked separately as the thirty-first fitted component. The unchanged base and all eleven cap STEP solids are checked against a conservative connector courtyard envelope over a continuous 360° rotation and full 0.25 mm press. The supplier STEP and fitted GLB agree; nominal minimum clearance is about 0.74 mm for the supplier model and 0.73 mm for the envelope. See `validation/programming-interface.json`, `validation/jst-connector-clearance.json` and `validation/jst-check-summary.json` for current checks. Older release logs remain historical evidence.

Use a straight-through five-pin JST-SH cable from programmer J3 / 5PIN, select **3V3** and remove the CR2032. Unlike the previous J4 pin 1, J3 pin 1 follows the programmer's voltage selector. Remove the cap and lift the PCB for cable access. This validated JST revision is prepared for release 1.0.18 on GitHub and TSCI. Physical connector fit, retention and programming remain prototype checks.
