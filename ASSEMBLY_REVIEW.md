# V5 bearing enclosure — verification scope

The current enclosure uses Ploopy's bearing-supported architecture and the Microsoft Surface Dial's separate rotation/press principle. Geometry is authored for the existing fidget PCB; it is not copied from either product. The base stays Ø58 mm, height increases from 15.2 to 17.2 mm, and the whole cap retains a 0.8 mm press stroke.

The native routed PCB and all thirty-one fitted electronics remain in `assembly.device`. Mechanical models are CAD-only siblings, translated from the phone datum using the actual PCB midplane Z8.6 mm. The PCB's four Ø3 mm holes and electrical routing are unchanged. Its new solid supports use four nylon screws and two short rigid locating collars; no flexible printed retaining hooks remain.

The CAD builder checks actual holder and JST STEP clearance, printed single solids and closed meshes, guide retention, full-stroke housing stops, race/seal separation, continuous structural rotational envelopes and sampled rotations. The independent hardware check compares exact structural solids and fixed fastener envelopes with all fitted native component model bounds. The PCB check verifies actual Circuit JSON material and both exported GLB drill faces. Hashes tie STL, mesh and native preview checks to their inputs.

Purchased bearing race models and springs are nominal reference geometry. Bearing fits/shoulders, actual spring sourcing and force, off-center pressing, guide friction, elastomer compression, switch end load and service endurance remain physical qualification. The steel bearing and screws also require Hall-angle and BLE checks in the assembled phone-mounted device. No application firmware or populated prototype is included.

Use `mechanical/enclosure-validation.json` and `validation/bearing-*.json` for this draft. Earlier `onepiece`, `jst-check-summary` and `pcb-mount-check-summary` reports describe their historical revisions. See [the V4 source](https://github.com/rushabhcodes/fidget-counter/tree/06a8e9d0d8a581d524d03d360637f72e829d8be2) for the replaced snap-fit design.
