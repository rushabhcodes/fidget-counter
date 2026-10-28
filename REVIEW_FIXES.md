# Datasheet review and corrections — 29 October 2026

All six findings identify real problems or unresolved design risks in the local 1.0.6 files. Revision 1.0.7 corrects the design and its exports. **This remains a prototype: RF measurements, actuator material/force testing, and assembler sourcing confirmation are still required before a production order.**

| Finding | Assessment | Correction |
|---|---|---|
| DEC2 / DEC3 capacitors | Confirmed. The source fitted 100 pF to DEC2 and 100 nF to DEC3. | Removed C7 and its copper. U1 physical pin 32 is explicitly unconnected. C8 is 100 pF C0G (Murata GRM1555C1H101JA01D / C77177) on DEC3, physical pin 33. Updated BOM and assembly exports. |
| C3 RF ground return | Confirmed. C3 joined general ground routing and the pour. | Moved C3 beside the SoC network, routed its return only through VSS pin 31, and excluded the top pour around that return. Removed the former nearby ground via that would bypass it. The regression check disconnects pin 31 geometrically and verifies that C3 becomes an isolated copper island. RF harmonic testing remains required. |
| Press tolerance margin | Confirmed, with a wording correction: total cap stroke was 0.50 mm; the 0.25 mm initial gap left only 0.25 mm for switch travel. | Increased cap stroke to 0.90 mm, added a separate compliant actuator ring and selectable shim, deepened the retention groove, and lowered the flexure mounts/bushings so the longer stroke clears the fixed ring. The housing shoulder carries the stop load. Worst-case closure margin is 0.15 mm after the specified assembly adjustment and material qualification. |
| Purchasing BOM | Confirmed. The encoder row said Ø6 × 2 mm while CAD uses Ø5 × 1.5 mm. | Corrected the encoder magnet, separated it from the 24 axial attachment discs, added the actuator ring/shim, and identified SW1 as KMR223NG ULC LFG / Y78B22324FP, LCSC C2804637. Use exact-part consignment or post-reflow fitting unless the assembler confirms this exact MPN. C221681 belongs to the imported 3 N geometry reference and is not an approved substitute. |
| Antenna matching / line / clearance | Confirmed as a performance risk, not evidence of inevitable BLE failure. | Kept the Nordic L1/C3 network beside U1; moved the separate Walsin L2/C13/C14 network beside ANT1. Added a 6 × 6 mm copper exclusion toward the antenna's open end, a grounded coplanar feed with an explicit stackup assumption, and ground stitching. Rerouted the battery supply away from the feed; local digital crossings beneath the feed remain an RF discontinuity requiring review. The circular board and phone differ from Walsin's test board. |
| U1 schematic pin numbers | Confirmed. Source connectivity used the right package pins, but split symbols showed local numbers. | All U1 split-symbol keys and arrangements now use physical QFAA numbers: SWDIO 26, SWDCLK 25, reset 24, ANT 30, DEC2 32, DEC3 33, etc. A regression check compares every displayed U1 pin with the source pin. |

## Capacitor cross-check

For this **nRF52810 QFAA**, DEC1 uses 100 nF, DEC2 is unconnected, DEC3 uses 100 pF, and DEC4 uses 1 µF in LDO mode. Board designators differ from Nordic's drawing; compare pins/functions rather than matching C numbers. VDD decoupling and bulk capacitors remain. The four 12 pF crystal capacitors are initial load values and still need oscillator frequency/startup measurement. C3 0.8 pF and L1 3.9 nH remain Nordic starting values; L2 6.8 nH is the Walsin antenna starting value. Optional antenna shunts remain DNP until tuning.

## Press assembly and tolerance budget

Use the revised cap, housing, spring insert and **2.5 mm PCB spacer bushings** together. The cap's lower edge is now Z=1.5 mm, leaving 0.60 mm nominal phone clearance at full press. Sensor clearance is 1.8 mm released / 0.9 mm pressed. The silicone ring is a separate material part, not a rigid FDM print. Its STEP/STL is a shape reference; use OD27.4 / ID23.2 × 1.2 mm stock or a molded equivalent. PET shim stock uses the same annular profile.

The unadjusted worst-case resting-gap error is ±0.50 mm: switch height ±0.20, PCB seating ±0.10, printed pusher ±0.10, and ring thickness ±0.10 mm. A fixed pusher cannot absorb this stack. Select a 0–1.20 mm shim stack in 0.05 mm increments (0.60 mm nominal), and measure a **0.10–0.15 mm free gap at every cap angle**. Reject excessive cap runout or a print that cannot meet this gap. Confirm no electrical closure at rest.

After adjustment, minimum available stroke is 0.90 − 0.05 = **0.85 mm**. Latest closure budget is 0.15 mm gap + 0.35 mm maximum electrical travel + 0.20 mm allowed ring compression at the maximum 2.5 N operating force = **0.70 mm**, leaving **0.15 mm**. Maximum required local ring compression at full stroke is 0.95 − 0.10 − 0.15 = **0.70 mm**. The cap reaches its housing shoulder before any rigid actuator backing could contact the switch.

**Material qualification remains open:** measure the ring's actual force/compression curve, confirm ≤0.20 mm compression at 2.5 N, obtain a permissible full-stroke switch load from the manufacturer, and verify the assembled force stays below it. Exercise and release the button through repeated cycles at all angles. The CAD's locally deformed silicone shape is prescribed geometry, not FEA or evidence of a qualified material. The calculated margin is conditional on these measured requirements.

## RF qualification

`rf-stackup.json` records the 50 Ω design target, 0.75 mm trace, 0.15 mm coplanar gap, 1.0 mm finished board, 35 µm copper, and assumed FR-4 Dk=4.3. A grounded-CPW calculation including a first-order conductor-thickness correction gives approximately 50 Ω. The bottom plane has local gaps at the digital crossings beneath the feed; the top coplanar return and stitching remain. The exact gap areas and bounds are recorded in validation/review-fixes.json. A uniform-line calculation does not certify these discontinuities. Soldermask, bends, launches, real dielectric properties and the antenna transition also require measurement. Ask the fabricator to solve the actual stackup and confirm it with a coupon/TDR before treating the line as controlled impedance.

Tune L2 and the optional shunts with a VNA in the final enclosure, with battery, magnets, shield and intended phone attached. Check BLE performance and radiated harmonics across the band and relevant hand/phone orientations. Recheck crystal startup/frequency and sleep/active current. A shorts check cannot establish any of these properties.

## Evidence

- [Nordic nRF52810 QFAA reference circuitry and BOM](https://docs.nordicsemi.com/r/bundle/ps_nrf52810/page/ref_circuitry.html?contentId=rrhhkNhja5o3MUK3azOE4w)
- [Nordic: adding a DEC2 capacitor affects receiver sensitivity](https://devzone.nordicsemi.com/f/nordic-q-a/81621/nrf52810-qcaa-dc-dc-dec2)
- [Nordic: DEC3 100 nF versus 100 pF deviation](https://devzone.nordicsemi.com/f/nordic-q-a/86334/capacitor-values-on-dec-pins/361018)
- [Nordic reference layout and C3 grounding guidance](https://docs.nordicsemi.com/r/bundle/ps_nrf52810/page/nrf52810-product-specification/hardware-and-layout)
- [Nordic matching-network track explanation](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/nRF52-matching-network.pdf)
- [C&K / Littelfuse KMR2 manufacturer datasheet](https://www.ck-components.com/media/1479/kmr2.pdf), dimensions and Y78B22324FP mechanical row
- [Walsin RFANT3216120A5T approval sheet](https://atta.szlcsc.com/upload/public/pdf/source/20180326/C127629_E7A81F7A36316F7BB6F0FA74BB27F225.pdf), page 3
- [Grounded coplanar waveguide equations](https://qucs.sourceforge.net/tech/node86.html)
- [Exact SW1 catalog identity](https://www.lcsc.com/product-detail/C2804637.html)

The pre-edit files are archived in `work/review-2026-10-29/before-fixes.tar.gz`. No order or publication was placed.
