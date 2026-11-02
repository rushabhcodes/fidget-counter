# MagSafe BLE fidget counter — rotation-only pilot

A CR2032-powered nRF52810 rotation counter with a centered TMAG3001 angle sensor, hollow bearing-supported cap, interchangeable grips and a five-pin JST-SH programming connector. Firmware is not included.

The current RevB design removes the whole-cap push action. The bearing shaft is integral with the stationary base: there are no return springs, sliding carrier, guide screws/washers, silicone actuator or pusher. SW1, its R5 pull-up, C17 filter and CAP_PRESS copper are removed from the PCB. U1 P0.29 is explicitly unused. The programmer's independent nRESET connection and R4 remain.

A unit uses **four rigid prints, seven screws and 16 handled parts** including the PCBA, cell, bearing and two magnet assemblies. Adhesive and tooling are excluded from that count. The prior press pilot used five rigid prints, ten screws and 27 handled parts. Assembly-time savings are estimates until measured.

The base remains Ø58 mm and the cap top remains at Z17.2 mm (17.0 mm above the phone-contact face). The 40×50×6 mm bearing, Ø36.5×1 mm PCB, encoder magnet position, purchased 54×45.8×1.9 mm attachment ring and eleven grip envelopes are retained. These ring dimensions describe the selected supplier reference; verify the sample and working face before buying a batch.

[Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) is the rotation reference. Its fixed housing, rotating top and purchased bearing support the simpler architecture. Its [6705ZZ bearing](https://ploopyco.github.io/knob/appendices/hardware/) is too small for this PCB; our CAD is independent. The prior Surface Dial press reference is historical and no longer describes this product.

Start with [printing instructions](mechanical/printing/PRINTING.md), the [print manifest](mechanical/print-ready-manifest.json), [assembly guide](MECHANICAL.md), [mechanical BOM](mechanical/MECHANICAL_BOM.csv), [pilot review](mechanical/MANUFACTURING_REVIEW.md) and [programming guide](PROGRAMMING.md). Print one circular fit prototype and its coupons before a 10–50-unit batch. CAD and slicing do not prove printed fit, thread strength, adhesive retention, magnetic sensing or RF performance.

## Rebuild and validate

Use the pinned Bun lockfile and Python requirements. With a working PrusaSlicer CLI:

```sh
bun install --frozen-lockfile
bun run typecheck
bun run check:routing
bun test validation/import-provenance.test.mjs
bun run build:source
bun validation/check-rotation-only.mjs
cp dist/index/circuit.json published.circuit.json
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/tooling/build_assembly_nest.py
python mechanical/build_fit_coupons.py
python mechanical/printing/audit_prints.py --slicer /path/to/prusa-slicer
python mechanical/printing/check_wall_sections.py
python mechanical/printing/render_slices.py
python mechanical/export_circuit_models.py
bun run build:source
bun validation/check-rotation-only.mjs
cp dist/index/circuit.json published.circuit.json
bun run build
python validation/check-rotation-only-cad.py
python validation/check-model-detail.py
python validation/check-attachment-ring.py
python validation/check-display-geometry.py
python validation/check-pcb-mounts.py
python validation/check-jst-fit.py
python validation/check-bearing-hardware.py
bun validation/check-imports.mjs
bun run check:programming
bun run check:assembly
python mechanical/render_bearing_layout.py
bun run build:cloud:prepare
bun validation/check-cloud-build.mjs
```

`mechanical/Print_STL` contains three common product parts and eleven alternative caps. Use exactly one cap per unit. Four fit coupons and two split-nest halves are separate calibration/tooling prints. Purchased/display parts are excluded. Assemblies are generated as assembled and exploded STEP files, with no pressed state.

The compiler remains pinned to tscircuit 0.0.3047. The router retains its failing safeguards for changes to physical terminals, net membership, layers, existing copper, widths, obstacles and board rules. The rotation-only regression compares retained electronics and every surviving copper record against commit `6224fc9`. Two unchanged legacy trace-style advisories are exactly allowlisted; new advisories fail validation.

Release **1.0.25** packages the rotation-only pilot;1.0.24 is the earlier press mechanism. Hosted publication verification is separate from local CAD/print validation. Historical compiler, manufacturing and publication reports retain their original revision labels; they do not certify the rotation-only pilot. The active evidence is `validation/rotation-only-status.json`, `validation/rotation-only-cad-audit.json` and `validation/print-readiness.json`.
