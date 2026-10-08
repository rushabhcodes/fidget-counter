# PCB Rev A — top-access revision 1.0.6 validation — 8 October 2026

The final source and supplied routed circuit were checked using the pinned local tscircuit 0.0.2748 / CLI 0.1.2253. All previews and fabrication exports use this same routed JSON. The source-build SHA-256 hashes are recorded in `validation/summary.json`; previous publication reports are archived under `validation/history/`.

| Check | Result |
|---|---|
| TypeScript typecheck | Pass |
| Netlist | 0 errors, 0 warnings |
| Pin specification | 0 errors, 0 warnings |
| Source diagnostics | 0 errors, 0 warnings |
| Schematic placement | Pass; no placement violations reported |
| PCB placement | 0 errors, 0 warnings |
| Routing difficulty | Advisory congestion estimate; completed routing validated below |
| Routed build | 0 errors, 0 warnings; 89 routed traces and 47 vias |
| Full tscircuit library validator | 0 errors, 0 warnings |
| Trace-length analysis | All 20 electrical nets analyzed |
| Crystal routing | All eight signal branches at most 10 mm, with zero vias |
| Gerber-derived copper shorts, both layers | 0 shorts |
| Revised 14.0 mm enclosure | All 13 reference solids valid; 4 main printable parts; zero unintended solid collisions |
| Fitted component positions | 30 components: 29 top and 1 bottom; DNP/bare lands excluded |
| Enclosure in circuit 3D | 12 mechanical models aligned within 0.0001 mm of CAD mesh bounds; portable OBJ/MTL URLs |
| Electrical revision comparison | All electrical, PCB and imported component CAD records identical to checked v1.0.3; metadata hash excluded |

All eight CLI check types passed. The complete routed build and the separate full library validator contain zero errors and zero warnings. The full trace-length reports, individual crystal branch lengths and exact source hashes are included in `validation/`. `bun run check:all` repeats the checks and rejects actionable placement issues, asynchronous tool exceptions, error records and warning records.

The CLI's `net.SWDCLK` length report omits its manually linked source branch and reports 0 mm. The supplied routed JSON contains that complete copper connection, with a planar length of 23.13246 mm. `validation/routing-geometry.json` independently totals the routed copper in each of the 20 connectivity groups; the raw CLI output is retained. Connectivity and both-layer shorts checks pass.

The unmodified TSCI JLCPCB imports and all 30 fitted component meshes pass `validation/check-imports.mjs`. SW1 uses shared imported KMR2 geometry while retaining its original 2 N manufacturer part number; the substitute’s catalog identifier is deliberately not assigned.

The source now uses `assembly.device` and 12 named `assembly.cadassembly` elements to include the released enclosure beside the populated PCB. Mechanical electronics/holder dummies are excluded. The three outer shells are translucent in the circuit view; print STL and STEP geometry remains solid. `validation/check-enclosure.mjs` verifies asset hashes, current CAD parameters, model positions and exported GLB bounds, and is included in `bun run check:all`.

`validation/compact-glb-audit.json` verifies the downloadable GLB reduction to fit the registry upload limit. All retained geometry buffers, triangle order, node transforms, electronic normals and PCB textures are unchanged. Identical buffers share storage and sequential enclosure indices are implicit. Optional enclosure normals and unused UV arrays are omitted; GLTF viewers derive the flat face normals. The full CLI build remains available locally in `dist/index/3d.glb`.

The confirmed encoder is a diametrically magnetized neodymium Ø5 × 1.5 mm disc. The revised cap uses a Ø5.2 mm pocket and 0.2 mm roof shim. Its nominal sensor air gaps remain 1.8 mm released and 1.3 mm pressed. CAD regeneration found zero unintended solid intersections. Magnet grade, sensor field margin and rotation accuracy still require a prototype measurement.

The bottom cover has 24 Ø5.25 × 1.55 mm pockets for the ordered Ø5 × 1.5 mm discs, on a Ø49.25 mm pitch circle. The geometry audit checks the actual disc count/volume, open pocket interiors, intact 0.6 mm pocket floors, minimum 1.178 mm pocket webs, 0.8 mm tray/housing rims and clearance in released/pressed states. The continuous backing-ring recess remains accessible with the tray removed. Its shielding performance, the discs' magnetization, attachment force and phone/Hall compatibility have not been measured. The new cap, housing and solid bottom cover form a matched set.

Top service removes the hatch, hatch posts and two M2 screws. Two deliberate release ports operate the cap latches without interrupting the retaining roof. The geometry audit checks key/housing clearance, nominal 0.10 mm released lip clearance, 0.20 mm latch/PCB clearance, the solid center floor and nine upward board/holder/cell extraction positions. No rigid intersections occur along this sampled path. `validation/top-access-key-lift-audit.json` separately checks the keys against rigid cap/grip material at 0, 0.15, 0.3 and 0.5 mm lift; the two intentionally flexing latch zones are explicitly excluded. Withdraw the keys after the initial 0.5 mm lift. Repeated latch cycles, screw retention and populated-board removal still require physical testing.

The MCU and sensor pins explicitly define power, ground, open-drain I2C, pull-up and required connections. Crystals use native electrical models; both signal pairs and their load-cap branches stay on the top layer. Passive manufacturer parts are specified in BOM.csv. Bare copper test points are excluded from physical component assembly. The explicit parts engine preserves authored supplier identifiers and datasheet pin models; no DRC is disabled.

## JLCPCB review — current sensor retained

The rerouted board uses regular-size **0.30 mm drill / 0.55 mm land** vias. Green soldermask accommodates the sensor's **0.20 mm** mask bridges. The sensor remains TMAG3001A2YBGR as requested; target **Standard assembly, both sides, ENIG**. [JLCPCB's current rigid-board requirements](https://jlcpcb.com/capabilities/pcb-capabilities) and [assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) were reviewed on 7 October 2026.

| Independent measurement | Result |
|---|---|
| Minimum routed trace width | 0.11 mm |
| Minimum copper-to-outline clearance | 0.350 mm |
| Copper, pad, drill and hole clearance checks | 0 violations; details in `validation/jlc-geometry-audit.json` |
| Actual exported mask bridges and legend strokes/clearances | Pass; details in `validation/jlc-gerber-audit.json` |
| Complete SMT mask and paste coverage | Every exposed SMT land has an opening; all fitted lands have paste; bare/DNP pads have none |
| Single-board drill density | 52585 holes/m² |
| Conservative exposed ENIG area upper bound, both sides combined / single board area | 16.97% |

These measurements cover the single board. The carrier panel's tooling holes, breakaway tabs and fiducials require CAM review. The single-board Gerbers need JLCPCB panelization into a carrier at least 70 × 70 mm with 5 mm rails. `README.md` contains order settings and the unresolved sourcing/assembly details. The two `JLCPCB_*_Quote_Draft.csv` files have 30 matching fitted designators (BT1 bottom); rotations need supplier-model review.

BT1 is the exact imported MYOUNG BS-08-B2AA020-R / C964787. Its maximum manufacturer height of 5.8 mm determines the enclosure stack; the imported visual model is shorter. The cell clears the rigid holder body. An unloaded negative spring contact overlaps the nominal cell by 2.62 mm³, recorded separately as a contact-fit estimate; retention and deflection require a physical test. Hatch posts leave 0.260 mm nominal clearance to the nearest SWD pad edge. The supplied enclosure is a prototype fit handoff.

The core omitted paste for the 48 rounded QFN lead pads. `export-gerbers.mjs` adds these at the core’s usual 70% linear reduction and removes bare/DNP paste. Imported copper geometry is unchanged; the exported mask and paste completeness are independently audited. The QFN exposed-pad aperture remains a single 3.22 mm square, pending assembler segmentation review.

Bottom-side holder mounting adds a second assembly side. Confirm reflow order, retention/fixture needs and costs with JLCPCB. Normal Standard PCBA, stencil, feeder, inspection, ENIG and panelization costs remain. See [JLCPCB's surcharge rules](https://jlcpcb.com/help/article/in-what-cases-will-there-be-charged-extra) and [assembly pricing](https://jlcpcb.com/help/article/pcb-assembly-price). No final supplier quote or CAM approval has been obtained. This package is for quotation and engineering review; it is not released for an assembly order.

## Physical and fabrication review still required

- The mounting-hole pattern inherited from the enclosure leaves only 0.25 mm nominal FR4 outside each hole. Obtain fabricator acceptance for this prototype; revise the mounting pattern/enclosure together for a stronger production web.
- The imported WCSP has 0.20 mm lands versus TI’s recommended 0.23 mm; the assembler must accept or resolve that difference. The QFN exposed-pad stencil aperture and authored assembly rotations also need review. The supplied position CSV is a coordinate reference, not a supplier-qualified machine file.
- The new RF feed/ground layout has not been measured for impedance or BLE performance. Tune matching and verify crystal startup in the populated, final phone/MagSafe assembly.
- Verify Hall field range, offsets, rotation accuracy and power consumption with the actual diametric magnet, coin cell and attachment magnets installed.
- Fit-test the commercial holder contacts, battery insertion/removal, cap pusher tolerance and printed flexure return. The compatible cap retains the full circumference grip.
- Firmware and the phone application are not part of this PCB deliverable. Firmware must keep the MCU in LDO mode (DCDCEN = 0), configure the sensor address override for sleep operation, integrate wrapped angles and implement the two-second reset hold.

This is a checked prototype design and editable handoff; the populated hardware has not been tested. No PCB order has been placed.


## Registry publication

The registry entrypoint `published.circuit.json` preserves this exact 0.30 mm drill / 0.55 mm land board. It is byte-identical to the checked `dist/index/circuit.json` output recorded above. The saved-board build is checked again for publication. Current reports are in `validation/`; the previous release’s reports are archived under `validation/history/`.
