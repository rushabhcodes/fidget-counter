# PCB Rev A validation — 7 October 2026

The final source and supplied routed circuit were checked using the pinned local tscircuit 0.0.2748 / CLI 0.1.2253. All previews and fabrication exports use this same routed JSON. SHA-256 hashes are recorded in `validation/summary.json`.

| Check | Result |
|---|---|
| TypeScript typecheck | Pass |
| Netlist | 0 errors, 0 warnings |
| Pin specification | 0 errors, 0 warnings |
| Source diagnostics | 0 errors, 0 warnings |
| Schematic placement | Pass; no placement violations reported |
| PCB placement | 0 errors, 0 warnings |
| Routing difficulty | Advisory congestion estimate; completed routing validated below |
| Routed build | 0 errors, 0 warnings; 87 routed traces and 48 vias |
| Full tscircuit library validator | 0 errors, 0 warnings |
| Trace-length analysis | All 20 electrical nets analyzed |
| Crystal routing | All eight signal branches at most 10 mm, with zero vias |
| Gerber-derived copper shorts, both layers | 0 shorts |
| Cap solid and pusher change | Valid single solid; 0.30 mm annular removal verified |
| Fitted component positions | 29 top-side components; DNP/bare lands excluded |

All eight CLI check types passed. The complete routed build and the separate full library validator contain zero errors and zero warnings. The full trace-length reports, individual crystal branch lengths and exact source hashes are included in `validation/`. `bun run check:all` repeats the checks and rejects actionable placement issues, asynchronous tool exceptions, error records and warning records.

The CLI's `net.SWDCLK` length report omits its manually linked source branch and reports 0 mm. The supplied routed JSON contains that complete copper connection, with a planar length of 23.13246 mm. `validation/routing-geometry.json` independently totals the routed copper in each of the 20 connectivity groups; the raw CLI output is retained. Connectivity and both-layer shorts checks pass.

The MCU and sensor pins explicitly define power, ground, open-drain I2C, pull-up and required connections. Crystals use native electrical models; both signal pairs and their load-cap branches stay on the top layer. Passive manufacturer parts are specified in BOM.csv. Bare copper test points are excluded from physical component assembly. The explicit parts engine preserves authored supplier identifiers and datasheet pin models; no DRC is disabled.

## Physical and fabrication review still required

- The mounting-hole pattern inherited from the enclosure leaves only 0.25 mm nominal FR4 outside each hole. Obtain fabricator acceptance for this prototype; revise the mounting pattern/enclosure together for a stronger production web.
- The WCSP sensor lands, QFN exposed-pad stencil aperture, selected passive land patterns and authored assembly rotations need assembler review. The supplied position CSV is a coordinate reference, not a supplier-qualified machine file.
- The new RF feed/ground layout has not been measured for impedance or BLE performance. Tune matching and verify crystal startup in the populated, final phone/MagSafe assembly.
- Verify Hall field range, offsets, rotation accuracy and power consumption with the actual diametric magnet, coin cell and attachment magnets installed.
- Fit-test the custom spring contacts, hatch service slack, cap pusher tolerance and printed flexure return. The compatible cap retains the full circumference grip.
- Firmware and the phone application are not part of this PCB deliverable. Firmware must keep the MCU in LDO mode (DCDCEN = 0), configure the sensor address override for sleep operation, integrate wrapped angles and implement the two-second reset hold.

This is a checked prototype design and editable handoff; the populated hardware has not been tested. No PCB order was made. This publication uses the earlier 0.20 mm via prototype.

## Publication of the earlier prototype

This publication preserves the 0.20 mm drill / 0.45 mm via-land prototype. The historical hashes in `validation/summary.json` describe the original handoff; source TSX and routed geometry are unchanged. Publication-only package metadata, entrypoint configuration, documentation and verification commands have separate hashes in `validation/publication/`. The default build uses the exact saved routing instead of rerunning the autorouter.
