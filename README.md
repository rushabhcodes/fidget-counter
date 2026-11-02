# MagSafe BLE Fidget Counter — V5 bearing enclosure

A CR2032-powered nRF52810 rotation counter with a centered TMAG3001 magnetic angle sensor, interchangeable grips and a five-pin JST-SH programming connector.

The current mechanical draft replaces the snap-fit cap and tiny PCB latches with a **bearing-supported rotor and a separately guided full-cap press**:

- **Base Ø58 mm**, unchanged; **height 17.2 mm**, 2.0 mm above V4.
- Nominal **40 × 50 × 6 mm** purchased bearing around the Ø36.5 mm PCB.
- **0.8 mm whole-cap press**, three purchased return springs and housing hard stops.
- Three solid guides with screw/washer upward retention; four nylon PCB screws and two short rigid locating collars.
- Three top-accessible screws retain the cap; eleven exterior grip options share the bearing drum.
- One purchased **54 × 45.8 × 1.9 mm N52 MagSafe ring** replaces the 24 attachment discs and separate backing ring. The central encoder magnet remains.
- PCB hole pattern, electronics and programming pinout retained. The PCB sits 1 mm higher in the enclosure.

[Ploopy Knob](https://ploopyco.github.io/knob/assembly-instructions/) informs the rotation architecture; [Microsoft Surface Dial](https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808) informs the independent spring return and press action. The CAD is independently authored for this board.

See [ring sourcing and assembly](mechanical/MAGSAFE_RING_SOURCING.md) for the exact US ring and a Mumbai sourcing candidate. The local manufacturing candidate combines the base and tray and replaces the encoder spacer with an integral cap stop. It adds retainer bosses without increasing height. See [the manufacturing review](mechanical/MANUFACTURING_REVIEW.md) for the 10–50-unit printed pilot.

See [MECHANICAL.md](MECHANICAL.md) for assembly, print orientation, service and prototype qualification; [mechanical BOM](mechanical/MECHANICAL_BOM.csv) for purchased hardware; and [PROGRAMMING.md](PROGRAMMING.md) for SWD and power precautions. Firmware is not included.

## Build and check

Install the pinned Bun dependencies and Python packages in `mechanical/requirements.txt`. Then run:

```sh
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/export_circuit_models.py
bun run typecheck
bun run check:routing
bun test validation/import-provenance.test.mjs
bun run build:source
bun validation/check-compiler-upgrade.mjs
bun validation/check-imports.mjs
# After checking a changed source, refresh the saved snapshot and previews:
cp dist/index/circuit.json published.circuit.json
bun run build
python validation/check-manufacturing-stop.py
python mechanical/tooling/build_assembly_nest.py
python validation/check-model-detail.py
python validation/check-attachment-ring.py
python validation/check-display-geometry.py
python mechanical/render_bearing_layout.py
python validation/check-pcb-mounts.py
python validation/check-jst-fit.py
python validation/check-bearing-hardware.py
bun run check:programming
bun run check:assembly
python mechanical/build_fit_coupons.py
bun run build:cloud:prepare
```

`mechanical/Print_STL` contains fifteen rigid print files: four common parts and eleven cap options; a unit uses five; `Coupons` contains small fit tests. Start with the coupons and circular starter set. `Actuator_Ring_REFERENCE_ONLY.stl` is a silicone geometry reference, **not a rigid print**. Source parameters are in `mechanical/enclosure-parameters.json`. Released, pressed and exploded STEP assemblies are generated under `mechanical/export/Assemblies`.

The local review evidence is [manufacturing-review-status.json](validation/manufacturing-review-status.json); [assembly timing worksheet](mechanical/ASSEMBLY_TIME_STUDY.csv) deliberately has no measured times.

This remains an unqualified mechanical prototype. CAD clearances and mesh checks do not establish physical spring return, switch force/overtravel, fatigue, Hall sensing or BLE performance. Verify those with the selected bearing, springs, elastomer, phone and magnets before assembled-board ordering. Older validation reports retain their original revision labels and do not certify V5.

The local toolchain is pinned to `tscircuit` **0.0.3047** (package metadata remains at published 1.0.24; the manufacturing candidate is local and unpublished). The routing contract matches terminals by electrical group and
physical coordinates rather than generated IDs, and rejects changes to copper,
layers, board geometry, design rules and connectivity. `check:routing` includes
negative regression cases for those safeguards. The compiler adds three style
advisories on unchanged legacy segments; an exact geometry-based allowlist records
them and rejects additional or changed warnings. Two tiny supplier-CAD offsets
preserve the previously validated poses under the new footprint-origin anchor.

Hardware previews and STEP assemblies now include detailed bearing internals,
threaded/recessed fasteners, close-wound spring ends and a CR2032 can/gasket/lid.
All 31 fitted supplier STEP parts appear in the mechanical assemblies. See
[CAD detail and rendering](MECHANICAL.md#cad-detail-and-rendering) for reference
sources and the distinction between nominal detail and selected purchased SKUs.

The cloud restore uses `published.circuit.json` and checked artifacts tied to source hashes. Refresh them after a verified source build; see `validation/prepare-cloud-assets.mjs`. Original release history remains in Git and the excluded `.archive-v1.0.6.zip`.

Registry publication uses the checked snapshot and six verified artifacts. Large
cached artifacts are split into request-sized source files and reconstructed
without changing their SHA-256 hashes. Physical qualification remains open.

Mechanical display assets use indexed GLB files with embedded materials.
The companion OBJ/MTL references remain in Git. Display packing retains every
triangle and pose; `python validation/check-display-geometry.py` checks the
complete meshes against the validated pre-publication display, allowing only the bounded manufacturing changes to base, cap and retainer and removal of tray/spacer. The manufacturing Boolean audit checks each changed solid against published 1.0.24; the ring audit verifies the seat and all fitted electronics. The GLB packing
pass also compares every rendered corner attribute before and after encoding.

[Registry release 1.0.23](https://rushabhcodes--fidget-counter-v1-0-23.tscircuit.app) completed successfully with 163 source files and six exact preview hashes verified against commit `157a36b62ba084e0a812fcc93dbe21a016904da8`. See [publication receipt](validation/published-1.0.23.json). Version 1.0.24 contains the subsequent purchased-ring revision. Its publication result is verified separately from the 1.0.23 milestone.
