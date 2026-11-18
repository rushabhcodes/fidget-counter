# Printing the current enclosure

Generate parts with `python mechanical/build_enclosure.py`. Files are under `dist/mechanical/Print_STL/`; print one `Base_V3_Discs` and one selected `Cap`. STLs already have the bed orientation and Z minimum of zero. Do not print the complete assembly as a single object.

The geometry audit uses a 0.4 mm nozzle, PETG, 0.15 mm layers, 0.20 mm first layer and nominal 0.45 mm extrusion width. `PETG-0.4-audit.ini` provides reproducible slicing settings. Apply the actual printer's machine profile and inspect every layer before printing; the audit profile does not contain machine startup/end routines.

| Part | Orientation | Profiles loaded after PETG audit profile |
| --- | --- | --- |
| Base_V3_Discs | Phone face down | `base-no-supports.ini`: zero supports |
| Circular, scalloped_coin, rounded_hexagon, wave_rim, turbine_wheel caps | Deck down | No supports |
| Ships_wheel, rounded_triangle, petal_flower, four_leaf_clover, rounded_square caps | Deck down | `cap-early-rim-supports.ini` |
| Thumb_scoop cap | Upright | `supports-everywhere.ini`, then `V3-edge-cap-supports.ini` |

The continuous base wall starts on the floor. Tapered pocket vents eliminate closed roof bridges; keep the annular stops intact when cleaning. The slicer audit requires zero base support extrusion, bridge spans below 1 mm and no warnings. Other cap styles have their own support policies in the generated manifest.

Print pocket coupons and bearing coupons using the same material and process. Check actual magnet seating and bearing fit before full prints. Nominal shaft Ø40.05 and housing Ø51.95 are starting dimensions, not a qualified printer tolerance. Never scale a complete part to adjust a fit.

```sh
bun run build:source
python mechanical/build_enclosure.py
python mechanical/build_fit_coupons.py
python mechanical/audit.py --slicer /path/to/prusa-slicer
```

Results and the print manifest are generated under `dist/mechanical/`. Audit G-code stays in `dist/mechanical/slicer/`; slice again with the correct machine configuration for actual printing. Physical fit, pull-off force, creep, bonds and print yield remain prototype checks.
