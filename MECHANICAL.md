# V5 bearing-supported rotating and pressing enclosure

V5 replaces the flexible cap-release clips, 0.7 mm retention flange and tiny PCB latches with a purchased thin-section bearing, a rigid guided carrier, separate return springs and screw retention. The base remains **58 mm diameter**. Released height is **17.2 mm**, 2.0 mm above V4; the 8 mm grip depth and maximum 61.6 mm grip envelope remain. The complete cap still rotates freely and presses to reset. The PCB is seated 1 mm higher, at Z8.1–9.1 mm; its electrical layout and four mounting holes are unchanged.

## Architecture and references

[Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) is the architectural reference for a purchased bearing between a printed base and hollow rotating shell. Ploopy's 25 × 32 × 4 mm bearing would have to sit above this board. This design instead places a nominal **6708 / 61708, 40 × 50 × 6 mm** bearing around the 36.5 mm PCB. See the [SKF nominal bearing family](https://www.skf.com/group/products/rolling-bearings/ball-bearings/deep-groove-ball-bearings/productid-61708). Confirm actual race lands, corner radii, tolerances and sourcing before ordering parts.

[Microsoft Surface Dial teardown, steps 6–8](https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808) is the reference for separating rotation, axial return and switch operation. V5 uses three purchased compression springs and three solid guides, rather than relying on the switch dome to lift the whole cap. The housing carries the bottom stop load. This is independently authored geometry; no Ploopy or Microsoft CAD has been copied.

The bearing inner race is held by the nonrotating orange carrier and its coarse threaded nut. The outer race is captured in the rotating cap by a screwed retaining ring. Retainers contact their respective race lands, with nominal seal clearance. The carrier slides on three Ø5 mm solid posts; screw heads and washers retain it upwards. The carrier, bearing, cap and encoder magnet move together during the **0.8 mm** press stroke. The guide arrangement avoids the battery holder and PCB posts. Four purchased nylon M2 screws retain the PCB, replacing printed hooks. Two short rigid locating collars center the PCB; they do not flex or retain it.

## Print parts and purchased hardware

Use the matching V5 files together. Start with the circular cap. `mechanical/Print_STL` contains five shared rigid parts—base, tray, carrier, inner-race nut and outer-race retainer—and eleven cap options. All grips now share a continuous, round bearing drum beneath their exterior grip profile. Old V4 meshes should not be mixed with V5.

Print rigid parts in PETG at 100% scale, in millimetres. The supplied cap STL is inverted onto its top face. The base and carrier have internal shoulders that may require localized support; keep support out of the guide bores, threads and bearing fits. Start at 0.15 mm layer height and at least four walls, then inspect the slicer paths. Print the fit coupons first and adjust the explicit bearing/guide clearance parameters for the actual printer. Do not force a bearing into an undersized print.

The assembly requires one bearing, three matched compression springs, three M2 × 12 mm countersunk cap screws, three M2.5 guide-retaining screws and washers, and four M2 nylon PCB screws. See `mechanical/MECHANICAL_BOM.csv` for dimensions and sourcing requirements. One purchased N52 **54 × 45.8 × 1.9 mm MagSafe ring assembly** replaces the 24 attachment discs and their separate backing ring. It bonds into one broad open seat in the phone-side tray, with its working face toward the phone. The tray has a continuous 0.6 mm roof and 0.9 mm minimum outer wall. Its two changed print parts preserve the 58 mm base and 17.2 mm height. The CR2032 holder remains. See [supplier options and seat dimensions](mechanical/MAGSAFE_RING_SOURCING.md). Each cap retains its own Ø5 × 1.5 mm diametrically magnetized encoder disc and 0.2 mm nonmagnetic spacer.

`Actuator_Ring_REFERENCE_ONLY.stl` is a **silicone shape reference**, not a rigid PETG/PLA part. A rotating annular actuator operates SW1 at every cap angle. Select shim thickness and elastomer from measurements: adjust approximately 0.15 mm free gap at all angles, confirm no closure at rest, then measure electrical closure, overtravel load and return at full stroke. CAD does not establish the elastomer force curve or the switch's permissible end load. Do not substitute a rigid pusher.

## Assembly and service

1. Confirm the purchased ring’s working face against the intended phone/case. Bond the complete ring into the single annular tray seat, working face outward, then bond the tray to the stationary base. Use the nominal 0.10 mm ring bondline and inspect all spring-seat reliefs. Qualify adhesive peel/shear retention before use; no separate backing ring or small magnet pockets remain.
2. Install the three springs in the base pockets. Lower the carrier onto the guides. Install the guide washers and low-profile M2.5 screws. Their shoulders/washer seats define released height; they must not clamp the moving carrier. Confirm free 0.8 mm travel and return before installing the PCB.
3. Seat the PCB on its four posts, with holder beneath. Use M2 **nylon** screws, Ø3.8 mm head envelope, to avoid conductive hardware near the mounting-hole copper. Confirm screw length and underside clearance.
4. Place the bearing over the carrier seat. Tighten the coarse inner-race nut by hand using its broad tool notches. Clamp only the inner race; confirm the seal and outer race remain free.
5. Fit the encoder magnet/spacer and qualified annular actuator to the cap. Seat the outer race in its cap recess. Fit the retaining ring and three flush M2 × 12 mm countersunk screws from the TOP of the cap. The ring clamps only the outer race. Check screw length before tightening.
6. Measure switch free gap/force, all-angle closure and release, cap tilt, bearing freedom, and sensor response. Remove the CR2032 before powering from the programmer, as described in `PROGRAMMING.md`.

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

Run `python mechanical/build_enclosure.py --style all`, then `python mechanical/export_circuit_models.py`. The CAD builder checks single-solid print parts, closed/wound meshes, the actual holder and JST STEP, PCB seating, guide retention, housing stops, race separation, and three press positions with 24 rotation samples. An axisymmetric structural rotor and exterior-grip keepout establish continuous rotational clearance; sampled angles supplement that envelope. Generated STEP assemblies include released, pressed and exploded states.

The report is `mechanical/enclosure-validation.json`. `validation/check-bearing-hardware.py` additionally checks the new hardware against the native electronics. Meshes and fit calculations are a prototype, not measured strength or endurance. Physical qualification remains necessary for print fits, spring return, off-center pressing, switch force/overtravel and repeated service. The steel bearing and screws also change the magnetic/RF environment: measure Hall angle error and BLE performance with the phone and purchased MagSafe ring present. A full-ceramic bearing of the same verified dimensions is an option if steel causes unacceptable disturbance.

Mechanical display assets retain the source triangles and CAD coordinates, original smooth normals and embedded PBR materials. Indexed GLB packing reduces renderer/publication memory without decimating the meshes. The purchased-ring revision deliberately changes only the base and tray print parts and fixed attachment hardware; bearing, cap, carrier and movement interfaces retain their original geometry.
