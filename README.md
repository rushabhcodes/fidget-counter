# MagSafe BLE Fidget Counter — V5 bearing enclosure

A CR2032-powered nRF52810 rotation counter with a centered TMAG3001 magnetic angle sensor, interchangeable grips and a five-pin JST-SH programming connector.

The current mechanical draft replaces the snap-fit cap and tiny PCB latches with a **bearing-supported rotor and a separately guided full-cap press**:

- **Base Ø58 mm**, unchanged; **height 17.2 mm**, 2.0 mm above V4.
- Nominal **40 × 50 × 6 mm** purchased bearing around the Ø36.5 mm PCB.
- **0.8 mm whole-cap press**, three purchased return springs and housing hard stops.
- Three solid guides with screw/washer upward retention; four nylon PCB screws and two short rigid locating collars.
- Three top-accessible screws retain the cap; eleven exterior grip options share the bearing drum.
- Original attachment magnets, backing ring, PCB hole pattern, electronics and programming pinout retained. The PCB sits 1 mm higher in the enclosure.

[Ploopy Knob](https://ploopyco.github.io/knob/assembly-instructions/) informs the rotation architecture; [Microsoft Surface Dial](https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808) informs the independent spring return and press action. The CAD is independently authored for this board.

See [MECHANICAL.md](MECHANICAL.md) for assembly, print orientation, service and prototype qualification; [mechanical BOM](mechanical/MECHANICAL_BOM.csv) for purchased hardware; and [PROGRAMMING.md](PROGRAMMING.md) for SWD and power precautions. Firmware is not included.

## Build and check

Install the pinned Bun dependencies and Python packages in `mechanical/requirements.txt`. Then run:

```sh
python mechanical/build_enclosure.py --style all
python mechanical/export_circuit_models.py
bun run typecheck
bun run check:routing
bun run build:source
bun validation/check-compiler-upgrade.mjs
# After checking a changed source, refresh the saved snapshot and previews:
cp dist/index/circuit.json published.circuit.json
bun run build
python validation/check-model-detail.py
python mechanical/render_bearing_layout.py
python validation/check-pcb-mounts.py
python validation/check-jst-fit.py
python validation/check-bearing-hardware.py
bun run check:programming
bun run check:assembly
python mechanical/build_fit_coupons.py
bun run build:cloud:prepare
```

`mechanical/Print_STL` contains the sixteen rigid print parts; `Coupons` contains small fit tests. Start with the coupons and circular starter set. `Actuator_Ring_REFERENCE_ONLY.stl` is a silicone geometry reference, **not a rigid print**. Source parameters are in `mechanical/enclosure-parameters.json`. Released, pressed and exploded STEP assemblies are generated under `mechanical/export/Assemblies`.

This remains an unqualified mechanical prototype. CAD clearances and mesh checks do not establish physical spring return, switch force/overtravel, fatigue, Hall sensing or BLE performance. Verify those with the selected bearing, springs, elastomer, phone and magnets before assembled-board ordering. Older validation reports retain their original revision labels and do not certify V5.

The local toolchain is pinned to `tscircuit` **0.0.3047** (package release version
is 1.0.23). The routing contract matches terminals by electrical group and
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
