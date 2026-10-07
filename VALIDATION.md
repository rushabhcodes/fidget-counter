# PCB Rev A validation — 7 October 2026

The final source and supplied routed circuit were checked using the pinned local tscircuit 0.0.2748 / CLI 0.1.2253. All previews and fabrication exports use this same routed JSON. The source-build SHA-256 hashes are recorded in `validation/summary.json`; publication metadata hashes are recorded separately in `validation/publication/summary.json`.

| Check | Result |
|---|---|
| TypeScript typecheck | Pass |
| Netlist | 0 errors, 0 warnings |
| Pin specification | 0 errors, 0 warnings |
| Source diagnostics | 0 errors, 0 warnings |
| Schematic placement | Pass; no placement violations reported |
| PCB placement | 0 errors, 0 warnings |
| Routing difficulty | Advisory congestion estimate; completed routing validated below |
| Routed build | 0 errors, 0 warnings; 87 routed traces and 41 vias |
| Full tscircuit library validator | 0 errors, 0 warnings |
| Trace-length analysis | All 20 electrical nets analyzed |
| Crystal routing | All eight signal branches at most 10 mm, with zero vias |
| Gerber-derived copper shorts, both layers | 0 shorts |
| Cap solid and pusher change | Valid single solid; 0.30 mm annular removal verified |
| Fitted component positions | 29 top-side components; DNP/bare lands excluded |

All eight CLI check types passed. The complete routed build and the separate full library validator contain zero errors and zero warnings. The full trace-length reports, individual crystal branch lengths and exact source hashes are included in `validation/`. `bun run check:all` repeats the checks and rejects actionable placement issues, asynchronous tool exceptions, error records and warning records.

The CLI's `net.SWDCLK` length report omits its manually linked source branch and reports 0 mm. The supplied routed JSON contains that complete copper connection, with a planar length of 23.13246 mm. `validation/routing-geometry.json` independently totals the routed copper in each of the 20 connectivity groups; the raw CLI output is retained. Connectivity and both-layer shorts checks pass.

The MCU and sensor pins explicitly define power, ground, open-drain I2C, pull-up and required connections. Crystals use native electrical models; both signal pairs and their load-cap branches stay on the top layer. Passive manufacturer parts are specified in BOM.csv. Bare copper test points are excluded from physical component assembly. The explicit parts engine preserves authored supplier identifiers and datasheet pin models; no DRC is disabled.

## JLCPCB review — current sensor retained

The rerouted board uses regular-size **0.30 mm drill / 0.55 mm land** vias. Green soldermask accommodates the sensor's **0.12 mm** mask bridges. The sensor remains TMAG3001A2YBGR as requested; target **Standard assembly, top only, ENIG**. [JLCPCB's current rigid-board requirements](https://jlcpcb.com/capabilities/pcb-capabilities) and [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) were reviewed on 7 October 2026.

| Independent measurement | Result |
|---|---|
| Minimum routed trace width | 0.11 mm |
| Minimum copper-to-outline clearance | 0.350 mm |
| Copper, pad, drill and hole clearance checks | 0 violations; details in `validation/jlc-geometry-audit.json` |
| Actual exported mask bridges and legend strokes/clearances | Pass; details in `validation/jlc-gerber-audit.json` |
| Single-board drill density | 48761 holes/m² |
| Conservative exposed ENIG area upper bound, both sides combined / single board area | 15.58% |

These measurements cover the single board. The carrier panel's tooling holes, breakaway tabs and fiducials require CAM review. The single-board Gerbers need JLCPCB panelization into a carrier at least 70 × 70 mm with 5 mm rails. `README.md` contains order settings and the unresolved sourcing/assembly details. The two `JLCPCB_*_Quote_Draft.csv` files have 29 matching fitted designators; rotations need supplier-model review.

Normal Standard PCBA, stencil, feeder, inspection, ENIG and panelization costs remain. See [JLCPCB's surcharge rules](https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra) and [assembly pricing](https://jlcpcb.com/help/article/pcb-assembly-price). No final supplier quote or CAM approval has been obtained. This package is for quotation and engineering review; it is not released for an assembly order.

## Physical and fabrication review still required

- The mounting-hole pattern inherited from the enclosure leaves only 0.25 mm nominal FR4 outside each hole. Obtain fabricator acceptance for this prototype; revise the mounting pattern/enclosure together for a stronger production web.
- The WCSP sensor lands, QFN exposed-pad stencil aperture, selected passive land patterns and authored assembly rotations need assembler review. The supplied position CSV is a coordinate reference, not a supplier-qualified machine file.
- The new RF feed/ground layout has not been measured for impedance or BLE performance. Tune matching and verify crystal startup in the populated, final phone/MagSafe assembly.
- Verify Hall field range, offsets, rotation accuracy and power consumption with the actual diametric magnet, coin cell and attachment magnets installed.
- Fit-test the custom spring contacts, hatch service slack, cap pusher tolerance and printed flexure return. The compatible cap retains the full circumference grip.
- Firmware and the phone application are not part of this PCB deliverable. Firmware must keep the MCU in LDO mode (DCDCEN = 0), configure the sensor address override for sleep operation, integrate wrapped angles and implement the two-second reset hold.

This is a checked prototype design and editable handoff; the populated hardware has not been tested. No PCB order or registry publication was made.


## Registry publication

The registry entrypoint `published.circuit.json` preserves this exact 0.30 mm drill / 0.55 mm land board. It is byte-identical to the checked `dist/index/circuit.json` output recorded above. Repository metadata and the saved-board build are checked again for publication; their reports are in `validation/publication/`.
