# PETG pilot print set

Use `mechanical/print-ready-manifest.json` and the matching STL hashes. A unit uses **five rigid prints**: Stationary_Base, Bearing_Carrier, Inner_Race_Nut, Outer_Race_Retainer, and **one** chosen cap. Circular is the starter cap. The other ten caps are alternatives, not additional unit parts. The two split-nest halves are separate tooling.

Do **not** rigid-print `Actuator_Ring_REFERENCE_ONLY.stl`, electronic/display models, or purchased bearings, springs, screws, washers, cells and magnets. The silicone reference remains outside the printable manifest and print-only ZIP. The full assembly CAD is for inspection, not a single print-in-place object.

## Checked process assumptions

The provisional process is a Cartesian FDM printer with a **0.4 mm nozzle**, 1.75 mm PETG and at least a 220×220×200 mm build volume. The audit profile uses 0.15 mm layers, 0.20 mm first layer, nominal 0.45 mm extrusion width, four requested perimeters, six top/bottom layers and 100% rectilinear infill. Thick bridges are disabled so supported bonding/fixture roofs use the selected layer height rather than a round nozzle-width bridge bead projecting below the nominal face. Arachne varies line widths/count where features cannot hold four perimeters. Thin non-retaining rims are therefore not four-wall structures.

Starting temperatures are 230°C first layer, 240°C thereafter and 85°C bed; fan 30–50%, with bridge fan 100% after the first three layers. These are starting assumptions, not a qualified recipe for every PETG/printer. Use the actual machine/filament profile, correct bed surface/release treatment, calibrated extrusion and dimensional coupons. See [Prusa's PETG guidance](https://help.prusa3d.com/article/petg_2059), especially its bridging/overhang limitations.

`PETG-0.4-audit.ini` is a reproducible **geometry/slicing audit profile**, not complete machine setup. It has no printer-specific homing, probing or end sequence. The audit G-code stays in ignored `work/print-readiness`; **no machine G-code is shipped**. During qualification, slice each part separately with the listed mode. Import the meshes in the actual printer's slicer, apply its machine profile plus these support/orientation choices and inspect every layer before printing. Once qualified, batch using explicit per-object overrides; do not apply the carrier's early-only supports globally to a base or fixture. Never run audit G-code directly on a printer. Do not import the full audit INI over a qualified machine preset: retain its homing/probing/start/end sequences and copy only the relevant print/material/support settings.

## Orientation and supports

The supplied STLs already have the correct bed pose and Z minimum of zero. Do not use automatic orientation or scale them to fix a fit. A 3 mm outer brim is included in the audit profile; inspect adhesion and removal for the actual bed/material.

| File | Bed orientation | Support settings | Cleanup/check |
| --- | --- | --- | --- |
| Stationary_Base | Phone face down, posts up | `supports-everywhere.ini`; supports enabled under bridges | Remove support from the annular magnet seat; inspect/clean the roof and verify ring/bondline seating. |
| Bearing_Carrier | Three guide feet down | `carrier-shoulder-supports.ini`; enforce supports for first 16 layers, build-plate only, automatic upper supports off | Support the floating annular shoulder. Keep support out of guide bores, bearing shaft and male thread; the audit limits support height below the thread region. |
| Inner_Race_Nut | Wide notched face down; **flipped from the earlier STL** | Base profile, no supports | The short tool-notch roofs bridge about 3 mm. Verify the coarse-thread coupon by hand. |
| Outer_Race_Retainer | Flat ring down, three bosses up | Base profile, no supports | Clean pilot holes; qualify actual screw preparation and torque. |
| Cap_circular, scalloped_coin, rounded_hexagon, wave_rim, turbine_wheel | Flat deck face down | Base profile, no supports | Bridge-labelled line lengths stay below the chosen 5 mm unsupported audit limit; inspect the actual printer preview. |
| Cap_ships_wheel, rounded_triangle, petal_flower, four_leaf_clover, rounded_square | Flat deck face down | `carrier-shoulder-supports.ini`, reused for early rim support | Support the first annular drum expansion; remove from the exterior underside. Upper automatic supports remain off. |
| Cap_thumb_scoop | Upright, cup opening on bed, finger dishes up | `supports-everywhere.ini` inside the cup | Remove internal support; inspect bearing land, pusher seat and encoder pocket. This avoids treating shallow finger dishes as unsupported underside roofs. |
| Tooling/Nest_Left and Nest_Right | Broad flat bottom down | `supports-everywhere.ini` | Finger supports must grow from the pocket floor; build-plate-only support is insufficient. Clean underside of fingers and pocket. The small JST engraving is only a visual aid; add a clear marker label if the actual nozzle does not resolve it. |

The base's magnet pocket is only 4.4 mm wide radially, but parallel toolpaths can span much longer tangential chords of the annulus. An unsupported control slice reported **floating bridge anchors and long bridging extrusions**. Therefore this PETG set explicitly supports the roof instead of calling it a 4.4 mm unsupported bridge.

For five noncircular caps, the first circular drum expansion has bridge-labelled spans of about 11–15 mm. The slicer did not warn about them, but this PETG audit conservatively adds early supports rather than assuming those free bridges will print well. The 5 mm unsupported criterion is a process assumption, not measured bridging qualification.

Print the bearing housing/shaft, guide post/bore and thread/nut coupons first with the same process. The matching nut coupon now uses its wide face down. Coupon filenames and SHA-256 values are listed separately in [bearing-fit-coupons.json](../../validation/bearing-fit-coupons.json); coupons are not product parts. Confirm hand assembly, free sliding and bearing seating; do not hammer a bearing or force printed threads. The 0.15 mm radial guide/shaft allowance, 0.10 mm radial bearing-housing allowance and 0.15 mm thread clearance remain nominal allowances, not measured printer tolerances. If adjustment is required, change explicit parameters and regenerate matching parts rather than scaling a whole STL.

## Printability corrections

- Three enclosed **0.01 mm** legacy tray-relief voids were filled. They were negative-volume cavity shells, not loose guide posts; they are irrelevant features for a 0.15 mm layer process and are now absent.
- Three vertical exterior pads strengthen every cap around its screw recesses: nominal outer material is **1.2 mm at the lower sockets and 1.0 mm at the countersinks**, replacing the former 0.2 mm lower skin. Bearing lands, magnet/pusher interfaces, screw positions, Ø58 mm base, maximum Ø61.6 mm cap envelope and height are retained. The local lower cap outline gains three reinforcing lobes; no additional handled part is introduced.
- Nut tool notches are shallower (0.6 mm), leaving **1.0 mm** radial wall beneath them; the thread fit is retained. Flipping the nut removes its former bottom overhang from the first layers.

The source model has a 0.55 mm non-retaining carrier counterbore rim and 0.60 mm non-retaining PCB locating collar wall. They require resolved extrusion paths with the selected nozzle. The carrier's 0.35 mm radial thread detail is attached to a thicker wall, not a separate printable wire; actual thread fit/strength must be established by the coupon and hardware tests. Retainer pilot walls are nominally 0.8 mm before screw forming/tapping. Do not infer post-tapping strength from the pilot mesh.

## Reproduce the checks

With the Python requirements, Bun dependencies and a working PrusaSlicer CLI available:

```sh
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/tooling/build_assembly_nest.py
python mechanical/build_fit_coupons.py
python mechanical/printing/audit_prints.py --slicer /path/to/prusa-slicer
```

The audit checks all fifteen rigid product alternatives and both tooling halves: valid single STEP solids, single closed oriented STL boundaries, source/bed transform and volume agreement, source-derived wall probes, bed contact and actual slicer execution. It requires no slicer print warnings, verifies support extrusion where required, and rejects unexpected supports on support-free parts. Reports and the manifest bind results to exact source/STL/profile hashes. Slicing is performed with the recorded CLI version; it is distinct from mesh checks and from a physical print test.

Inspect every layer of the actual machine's sliced job, especially the base roof, carrier shoulder, thumb-cap interior and fixture fingers. Support removal may alter a mating/bonding surface; inspect and measure it before assembly. The fixture must be opened at least 3 mm per half for removal, and must be removed before testing cap presses.

This set is for **controlled fit-test prints**. Physical print yield, thread strength, bearing fits, spring/actuator behavior, magnetic bias, adhesive retention, Hall/BLE performance and firmware/end-of-line qualification remain separate production gates. Assembly-time savings are still estimates.
