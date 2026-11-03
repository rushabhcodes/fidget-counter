# PETG pilot print set

Use `mechanical/print-ready-manifest.json` and matching STL hashes. A unit uses **two rigid prints: Stationary_Base and one chosen Cap**. Circular is the starter; ten other caps are alternatives. No nut, retainer, top screws or split nest are used. Ten fit coupons are calibration prints.

Do **not** rigid-print electronic/display models or purchased bearings, screws, cells and magnets. The full assembly CAD is for inspection, not a single print-in-place object.

## Checked process assumptions

The provisional process is a Cartesian FDM printer with a **0.4 mm nozzle**, 1.75 mm PETG and at least a 220×220×200 mm build volume. The audit profile uses 0.15 mm layers, 0.20 mm first layer, nominal 0.45 mm extrusion width, four requested perimeters, six top/bottom layers and 100% rectilinear infill. Thick bridges are disabled so supported bonding/fixture roofs use the selected layer height rather than a round nozzle-width bridge bead projecting below the nominal face. Arachne varies line widths/count where features cannot hold four perimeters. Thin non-retaining rims are therefore not four-wall structures.

Starting temperatures are 230°C first layer, 240°C thereafter and 85°C bed; fan 30–50%, with bridge fan 100% after the first three layers. These are starting assumptions, not a qualified recipe for every PETG/printer. Use the actual machine/filament profile, correct bed surface/release treatment, calibrated extrusion and dimensional coupons. See [Prusa's PETG guidance](https://help.prusa3d.com/article/petg_2059), especially its bridging/overhang limitations.

`PETG-0.4-audit.ini` is a reproducible **geometry/slicing audit profile**, not complete machine setup. It has no printer-specific homing, probing or end sequence. The audit G-code stays in ignored `work/print-readiness`; **no machine G-code is shipped**. During qualification, slice each part separately with the listed mode. Import the meshes in the actual printer's slicer, apply its machine profile plus these support/orientation choices and inspect every layer before printing. Once qualified, batch using explicit per-object overrides; do not apply the noncircular caps’ early-only supports globally to a base. Never run audit G-code directly on a printer. Do not import the full audit INI over a qualified machine preset: retain its homing/probing/start/end sequences and copy only the relevant print/material/support settings.

## Orientation and supports

The supplied STLs already have the correct bed pose and Z minimum of zero. Do not use automatic orientation or scale them to fix a fit. A 3 mm outer brim is included in the audit profile; inspect adhesion and removal for the actual bed/material.

| File | Bed orientation | Support settings | Cleanup/check |
| --- | --- | --- | --- |
| Stationary_Base | Phone face down, fixed shaft up | `base-fixed-supports.ini`; enforce the first34 layers, support from bed and pocket floor, upper automatic supports off | Remove support from both the annular magnet seat and fixed bearing shoulder; inspect/clean the roof and verify ring/bondline seating. |
| Cap_circular, scalloped_coin, rounded_hexagon, wave_rim, turbine_wheel | Flat deck face down | Base profile, no supports | Bridge-labelled line lengths stay below the chosen 5 mm unsupported audit limit; inspect the actual printer preview. |
| Cap_ships_wheel, rounded_triangle, petal_flower, four_leaf_clover, rounded_square | Flat deck face down | `cap-early-rim-supports.ini`, reused for early rim support | Support the first annular drum expansion; remove from the exterior underside. Upper automatic supports remain off. |
| Cap_thumb_scoop | Upright, cup opening on bed, finger dishes up | `supports-everywhere.ini` inside the cup | Remove internal support; inspect bearing land, encoder pocket. This avoids treating shallow finger dishes as unsupported underside roofs. |

The base's magnet pocket is only 4.4 mm wide radially, but parallel toolpaths can span much longer tangential chords of the annulus. An unsupported control slice reported **floating bridge anchors and long bridging extrusions**. Therefore this PETG set explicitly supports the roof instead of calling it a 4.4 mm unsupported bridge.

Five noncircular caps use the early-rim support profile. The new ships-wheel geometry needs no support extrusion and slices without a warning; the other four still receive early support. Check the exact per-part results in the manifest rather than assuming all grip styles have identical support needs. The 5 mm unsupported criterion is a process assumption, not measured bridging qualification.

Print the ten bearing coupons first with the same process. The variants span shaftØ39.90/40.00/40.05/40.10 and housingØ52.10/52.00/51.95/51.90, plus the two nominal reference coupons. Their hashes are in [bearing-fit-coupons.json](../../validation/bearing-fit-coupons.json). Nominal product shaftØ40.05 and housingØ51.95 give0.05mm diametral interference on each race. This is not a qualified printer tolerance. Require hand-only seating, no hammer/press force through balls or shields, and measured pull-off/creep/service retention. Change explicit parameters and regenerate matching parts if needed; never scale a complete STL. There is no positive axial lock.

The new cap has no fastener recesses or reinforcing screw pads; bearing and encoder interfaces and exterior height remain checked. The fixed shaft has1.375mm nominal radial wall. Four PCB posts have0.8mm nominal pilot walls before screw forming/tapping; test actual screw retention. The common cap deck is1.3mm thick. Detailed source wall probes and actual toolpath results are in the validation reports.

## Reproduce the checks

With the Python requirements, Bun dependencies and a working PrusaSlicer CLI available:

```sh
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/build_fit_coupons.py
python mechanical/printing/audit_prints.py --slicer /path/to/prusa-slicer
```

The audit checks all twelve rigid product alternatives: valid single STEP solids, single closed oriented STL boundaries, source/bed transform and volume agreement, source-derived wall probes, bed contact and actual slicer execution. It requires no slicer print warnings, verifies support extrusion where required, and rejects unexpected supports on support-free parts. Reports and the manifest bind results to exact source/STL/profile hashes. Slicing is performed with the recorded CLI version; it is distinct from mesh checks and from a physical print test.

Inspect every layer of the actual machine's sliced job, especially the base roof and integral bearing shoulder and thumb-cap interior. Support removal may alter a mating/bonding surface; inspect and measure it before assembly. No split fixture is required for the selected light hand-only push-fit.

This set is for **controlled fit-test prints**. Physical print yield, bearing seating/pull-off force, creep, bearing fits and retention, magnetic bias, adhesive retention, Hall/BLE performance and firmware/end-of-line qualification remain separate production gates. Assembly-time savings are still estimates.
