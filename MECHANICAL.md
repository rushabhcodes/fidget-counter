# V5 bearing-supported rotating and pressing enclosure

V5 replaces the flexible cap-release clips, 0.7 mm retention flange and tiny PCB latches with a purchased thin-section bearing, a rigid guided carrier, separate return springs and screw retention. The base remains **58 mm diameter**. Released height is **17.2 mm**, 2.0 mm above V4; the 8 mm grip depth and maximum 61.6 mm grip envelope remain. The complete cap still rotates freely and presses to reset. The PCB is seated 1 mm higher, at Z8.1–9.1 mm; its electrical layout and four mounting holes are unchanged.

## Architecture and references

[Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) is the architectural reference for a purchased bearing between a printed base and hollow rotating shell. Ploopy's 25 × 32 × 4 mm bearing would have to sit above this board. This design instead places a nominal **6708 / 61708, 40 × 50 × 6 mm** bearing around the 36.5 mm PCB. See the [SKF nominal bearing family](https://www.skf.com/group/products/rolling-bearings/ball-bearings/deep-groove-ball-bearings/productid-61708). Confirm actual race lands, corner radii, tolerances and sourcing before ordering parts.

[Microsoft Surface Dial teardown, steps 6–8](https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808) is the reference for separating rotation, axial return and switch operation. V5 uses three purchased compression springs and three solid guides, rather than relying on the switch dome to lift the whole cap. The housing carries the bottom stop load. This is independently authored geometry; no Ploopy or Microsoft CAD has been copied.

The bearing inner race is held by the nonrotating orange carrier and its coarse threaded nut. The outer race is captured in the rotating cap by a screwed retaining ring. Retainers contact their respective race lands, with nominal seal clearance. The carrier slides on three Ø5 mm solid posts; screw heads and washers retain it upwards. The carrier, bearing, cap and encoder magnet move together during the **0.8 mm** press stroke. The guide arrangement avoids the battery holder and PCB posts. Four purchased nylon M2 screws retain the PCB, replacing printed hooks. Two short rigid locating collars center the PCB; they do not flex or retain it.

## Print parts and purchased hardware

Use the matching V5 files together. Start with the circular cap. `mechanical/Print_STL` contains four shared rigid parts—integrated base, carrier, inner-race nut and outer-race retainer—and eleven cap options. All grips now share a continuous, round bearing drum beneath their exterior grip profile. Old V4 meshes should not be mixed with V5.

Print rigid parts in PETG at 100% scale, in millimetres. The supplied cap STL is inverted onto its top face, except thumb_scoop, which prints upright with internal supports. The nut prints with its wide notched face down. The base roof, carrier shoulder, thumb-scoop interior and split fixture require the supports specified in [PRINTING.md](mechanical/printing/PRINTING.md); keep support out of the guide bores, threads and bearing fits. Start at 0.15 mm layer height and at least four walls, then inspect the slicer paths. Use the explicit [printable manifest](mechanical/print-ready-manifest.json), which excludes purchased and silicone reference parts. Print the fit coupons first and adjust the explicit bearing/guide clearance parameters for the actual printer. Do not force a bearing into an undersized print.

The assembly requires one bearing, three matched compression springs, three M2 × 12 mm countersunk cap screws, three M2.5 guide-retaining screws and washers, and four M2 nylon PCB screws. See `mechanical/MECHANICAL_BOM.csv` for dimensions and sourcing requirements. One purchased N52 **54 × 45.8 × 1.9 mm MagSafe ring assembly** replaces the 24 attachment discs and their separate backing ring. It bonds into one broad open seat in the integrated phone-side base, with its working face toward the phone. The integrated seat has a continuous 1.5 mm roof and 0.9 mm minimum outer wall. The former tray/base bond is eliminated; base diameter and height remain unchanged. The CR2032 holder remains. See [supplier options and seat dimensions](mechanical/MAGSAFE_RING_SOURCING.md). Each cap retains its own Ø5 × 1.5 mm diametrically magnetized encoder disc seated against an integral cap stop at Z12.9; no loose spacer remains.

`Actuator_Ring_REFERENCE_ONLY.stl` is a **silicone shape reference**, not a rigid PETG/PLA part. A rotating annular actuator operates SW1 at every cap angle. Select shim thickness and elastomer from measurements: adjust approximately 0.15 mm free gap at all angles, confirm no closure at rest, then measure electrical closure, overtravel load and return at full stroke. CAD does not establish the elastomer force curve or the switch's permissible end load. Do not substitute a rigid pusher.

## Assembly and service

1. Inspect and kit the qualified prints, purchased parts and screws. Confirm ring working face against the intended phone/case. Bond the purchased ring to the integrated base seat with the qualified 0.10 mm bondline; no tray/base bond remains. Separately seat the encoder magnet against its integral cap stop and bond its sidewall; fit the qualified compliant actuator to the cap. Complete the specified adhesive cure before loading these joints.
2. Program/test the PCBA **without a CR2032 installed** using `PROGRAMMING.md`. Disconnect programmer power, then insert the CR2032 into the underside holder **before lowering the PCB into the base**. Firmware is not supplied by this repository; an approved image and test procedure remain a pilot gate.
3. Place the base in the split assembly nest, align JST direction to the visual mark, and clamp gently. Install the three matched springs and lower the carrier onto the guides. Fit three guide washers and M2.5 screws. The washers seat on fixed posts, not on the moving carrier. Confirm free 0.8 mm travel/return before covering the guide screws with the PCB.
4. Seat the PCB/holder/cell assembly on its four posts; fit four M2×4 nylon screws. Do not add conductive washers. Verify holder clearance and qualified tightening torque. The separately labelled two-screw trial retains all four support posts but is not the default build.
5. Lower the **outer-race retainer BEFORE the bearing**, with its three bosses pointing upwards. Its Ø48.8 mm opening cannot pass over the Ø50 mm bearing. Rest it on the nest's three supports at Z5.1. Place the bearing over the carrier seat and hand-tighten the coarse inner-race nut using its broad notches. Clamp only the inner race and keep shields clear.
6. Align the three cap sockets with the retainer bosses, lower the prepared cap over the outer race and start all three M2×12 countersunk screws from the top. Tighten with the qualified sequence/torque; do not hold the cap pressed to make the screws catch. The nest supports the loose retainer. Nominal thread overlap is 4.4 mm, but printed thread strength remains unqualified.
7. Open each nest half by at least 3 mm and lift the assembly. **Do not perform a press test while the retainer supports are engaged.** Confirm bearing freedom, full return, all-angle closure/release and the qualified gap/force recipe. Inspect head flushness, rocking and magnet retention. Test Hall/count/reset/BLE behavior and attachment with the intended phone/case.

Service from the top: remove the three cap-retainer screws, lift off the cap, unscrew the inner-race nut and lift off the bearing. Remove the PCB screws and lift the PCB/holder for battery service. The guide screws become accessible after removing the PCB. No tiny printed release hooks are used.

## CAD detail and rendering

Purchased hardware now has modeled construction details in both STEP and native
GLB previews: bearing raceways and 0.3 mm edge chamfers, 25 balls, a pocketed
stamped cage with rivets, and two non-contact metal shields; helical screw
threads and cross recesses; chamfered washers and magnets; and a CR2032 positive
can, insulating gasket and engraved negative lid. Springs have five active turns
and one close-wound end turn at each end in both STEP and lightweight preview
meshes. These details stay inside the existing nominal hardware envelopes.

The bearing ball complement comes from [AST's 6708 catalog](https://www.astbearings.com/catalog/root/6708)
(25 balls, each Ø2.381 mm); the [ISK 6708ZZ reference](https://iskbearing.com/product-details/6708zz)
confirms the shielded 40 × 50 × 6 mm envelope. The cage, shield lips and fastener
drives are representative construction, not supplier production drawings. Spring
end treatment follows [Lee Spring's reference](https://www.leespring.com/learn-about-compression-springs);
the exact spring SKU and measured force remain open. The cell preserves the
[CR2032 20 × 3.2 mm envelope](https://www.duracell.com/wp-content/uploads/2016/04/LI2032US10141.pdf).

All 31 fitted electronic parts use their existing supplier STEP geometry in the
mechanical assemblies, positioned from the native circuit model origin and XYZ
rotation. They are excluded from the mechanical-only tscircuit models because
the native PCB already renders them. Indexed GLB material groups distinguish polished balls,
brushed shields, nylon screws, elastomer and printed parts. The render script
uses these actual meshes for assembled, closed-section and exploded views;
`previews/bearing-detail.png` shows the bearing section separately. The metal
shields correctly conceal the balls in the complete assembled view. Native models
default to opaque materials; pass `transparentShell` to `EnclosureAssembly` for
an optional inspection view. The circuit build applies those PBR finishes to
the exported GLB by splitting contiguous index ranges; it checks source OBJ
triangles and verifies the binary geometry buffer remains byte-for-byte identical.
This avoids the compiler converter assigning the first material to every part.

## Validation and limits

Run `python mechanical/build_enclosure.py --style all --assembly-style circular`, then `python mechanical/export_circuit_models.py`. The CAD builder checks single-solid print parts, closed/wound meshes, the actual holder and JST STEP, PCB seating, guide retention, housing stops, race separation, and three press positions with 24 rotation samples. An axisymmetric structural rotor and exterior-grip keepout establish continuous rotational clearance; sampled angles supplement that envelope. Generated circular STEP assemblies include released, pressed and exploded states. Omit `--assembly-style circular` to export all eleven assembled variants; all requested grip solids and motion are checked in either mode.

The report is `mechanical/enclosure-validation.json`. `validation/check-bearing-hardware.py` additionally checks the new hardware against the native electronics. Meshes and fit calculations are a prototype, not measured strength or endurance. Physical qualification remains necessary for print fits, spring return, off-center pressing, switch force/overtravel and repeated service. The steel bearing and screws also change the magnetic/RF environment: measure Hall angle error and BLE performance with the phone and purchased MagSafe ring present. A full-ceramic bearing of the same verified dimensions is an option if steel causes unacceptable disturbance.

Mechanical display assets retain the source triangles and CAD coordinates, original smooth normals and embedded PBR materials. Indexed GLB packing reduces renderer/publication memory without decimating the meshes. The local manufacturing candidate consolidates the base/tray, replaces the encoder spacer with an integral stop and adds retainer bosses/matching cap sockets. Bearing lands, carrier guides, PCB poses, magnet position and external envelope are retained. Boolean comparisons against published 1.0.24 bound these changes; physical qualification remains open.

See [the manufacturing review](mechanical/MANUFACTURING_REVIEW.md) for the 27-part/10-screw default, the optional 25-part/eight-screw trial, spring calculations, assembly-time assumptions and pilot release gates. `python mechanical/tooling/build_assembly_nest.py` creates the split-nest STEP/STL and checks its support and ejection clearances. The fixture is tooling and has not been physically tested.
