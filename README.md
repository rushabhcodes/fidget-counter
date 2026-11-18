# Fidget counter

A CR2450-powered nRF52810 BLE rotation counter with a centered TMAG3001 Hall sensor. The enclosure uses two PETG prints: a one-piece magnet base and one of eleven caps. The base prints phone face down with **zero supports**. Twenty Ø6 × 3 mm axial magnets fit vented underside pockets; an identical magnet sits on edge inside the cap.

## Develop and build

Requires Bun. The project pins tsCircuit **0.0.3236** and its dependency graph in `bun.lock`.

```sh
bun install --frozen-lockfile
bun run dev
bun run build
bun run typecheck
bun test
bun run check:assembly
bun run check:programming
bun run check:imports
```

Open `dist/index.html` through a static web server to use the generated website. Use **More views (⋯) → Drawing**. The native view contains two A3 engineering sheets: assembled and orthographic views, a dimensioned front view, the underside magnet pattern, an encoder detail and a section through the sensor clearance. PCB, schematic and 3D views use the same circuit.

[index.circuit.tsx](index.circuit.tsx) is the circuit source; [engineering-drawing.tsx](engineering-drawing.tsx) defines native tsCircuit drawing pages and views. The build resolves imported-model measurements into native dimension records. [enclosure.tsx](enclosure.tsx) selects the cap. Change `CAP_STYLE` in the circuit to select another style.

All generated Circuit JSON, previews, drawings, website files, STEP/STL and validation reports go under ignored `dist/`. There are no checked-in compiled circuit snapshots, release archives or historical design variants. `imports/` contains supplier component definitions and CAD inputs; `mechanical/models/` contains the GLB assets imported by the circuit. These are required inputs for the TypeScript viewer and are refreshed explicitly from the CAD source.

## Mechanical source and printing

```sh
python -m pip install -r mechanical/requirements.txt
bun run build:source
python mechanical/build_enclosure.py
python mechanical/build_fit_coupons.py
python mechanical/audit.py --slicer /path/to/prusa-slicer
# After editing CAD, refresh the imported viewer models and rebuild:
python mechanical/export_models.py
bun run build
```

Generated print parts are in `dist/mechanical/Print_STL`, pocket coupons in `Fit_Coupons`, bearing coupons in `Bearing_Coupons`, and exact assemblies in `Assemblies`. Use the generated `print-ready-manifest.json` for per-part orientation and slicer profiles. The circular cap is the default support-free cap; some other styles require supports.

The base is Ø58 mm, the circular cap Ø61.6 mm and total physical height 20.9 mm. The bearing is 6808-ZZ (40 × 52 × 7 mm). [Mechanical details](MECHANICAL.md), [printing settings](mechanical/printing/PRINTING.md), [assembly](ASSEMBLY.md), [parts to order](mechanical/ORDER_LIST.csv), [electronic BOM](BOM.csv), [programming](PROGRAMMING.md) and [firmware](firmware/README.md) describe the current device.

This is a fit-test prototype. Physical bearing retention, adhesive retention, phone/case holding force, Hall counting and BLE/current performance need qualification on actual hardware.
