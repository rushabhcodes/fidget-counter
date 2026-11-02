# Rotation-only mechanical assembly

The fixed bearing shaft is part of the Ø58 mm PETG base. Three solid Ø5 mm web stems join it to the base floor, with broad Ø8 mm upper heads. The bearing sits at Z6.6–12.6 mm; its inner race is retained by a removable coarse nut. The hollow cap rotates on the outer race, retained by a lower ring and three top-accessible screws. There is no designed axial click or press travel.

The top datum remains Z17.2 mm; actual height above the base contact face Z0.2 is17.0 mm. The selected cap can extend to Ø61.6 mm. The PCB stays at Z8.1–9.1 mm. The Ø5×1.5 mm diametric encoder magnet stays at Z11.4–12.9 mm against its integral cap stop, nominally1.8 mm above the sensor envelope. The selected attachment ring reference remains OD54, ID45.8, thickness1.9 mm; its integrated seat has0.15 mm radial clearance and0.10 mm adhesive bondline. Supplier sample and polarity remain unverified.

## Parts and print process

Print Stationary_Base, Inner_Race_Nut, Outer_Race_Retainer and one selected Cap. There is no separate carrier, actuator or spring reference in the printable set. Use matching files from the [manifest](mechanical/print-ready-manifest.json) and follow [PETG printing instructions](mechanical/printing/PRINTING.md). All eleven cap options share the same bearing interfaces. Purchased bearing, screws, magnets, cell and PCBA are not print parts.

The pilot assumes a calibrated0.4 mm FDM nozzle with PETG,0.15 mm layers and four requested walls. Print fit coupons first. Support removal from the integrated base must leave its bearing shoulder, shaft, thread and ring seat clean. The split assembly nest is separate tooling. No physical print/fit test has been performed.

## Assembly and service

1. Inspect, deburr and clean the four qualified prints. Confirm actual bearing/thread coupon fits without force. Verify the selected ring's dimensions and working face with the intended phone/case. Bond the ring into the integrated base seat and bond the encoder magnet sidewall against the cap's integral stop. Cure before loading either joint; do not add an axial glue layer under the encoder.
2. Program/test the PCBA with **no CR2032 installed**, following [PROGRAMMING.md](PROGRAMMING.md). Disconnect programmer power. Insert the cell into the underside holder before lowering the board into the base; the assembled enclosure does not provide side-entry battery access.
3. Seat the board/holder/cell on four fixed PCB posts, using the two rigid locating collars. Fit four M2×4 nylon screws without conductive washers. Qualify torque and confirm no board deflection.
4. Put the base in the split assembly nest. Lower the outer-race retainer **before the bearing**, with its three bosses up. Its Ø48.8 mm bore cannot pass over the Ø50 mm bearing. The nest holds the loose retainer at Z5.1 mm. Then fit the bearing over the fixed shaft and hand-tighten the inner nut, clamping only the inner race. Keep shields free. Do not use nut torque to compensate for poor fits.
5. Lower the prepared cap over the bearing, align its three sockets to the retainer bosses and start all three M2×12 countersunk screws from the top. Tighten using a physically qualified sequence and torque. Nominal screw engagement is4.4 mm; actual printed pull-out strength is untested.
6. Open each nest half by at least3 mm and lift out the product. Check free rotation, axial retention, wobble, screw-head flushness and magnet retention. Test Hall/count/BLE behavior and attachment on the intended phone/case. There is no press/reset test because that mechanism has been removed.

For service, remove the three cap screws and lift the cap, leaving the outer retainer beneath the bearing. Remove the inner nut and bearing before lifting the retainer. Remove the four PCB screws and lift the PCB/holder to replace the cell or access the programming cable. The fixed shaft remains in the base.

## Reference and validation limits

[Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) uses a bearing and fixed housing for rotation. Its hardware dimensions and fastener approach are not copied blindly: its25×32×4 bearing cannot surround this36.5 mm board, and reversible screws/nut retain our larger printed pilot without new small snap latches. The Surface Dial press reference is no longer applicable.

The generated source CAD is checked for single valid solids, closed/wound meshes, exact fitted-electronics clearance, separate race contact, continuous axisymmetric rotational clearance and24 sampled hub angles. All11 cap solids are checked. A Boolean comparison against6224fc9 confines changes to joining the fixed base/support, filling old press holes/removing spring seats and deleting the annular pusher. Nut/retainer geometry, envelope and encoder position remain guarded.

## CAD detail and rendering

Native models include grooved/chamfered races,25 balls, a stamped cage and metal shields, threaded fasteners, detailed CR2032 can/gasket/lid and all28 retained supplier STEP electronics. Ball count/diameter follow [AST6708](https://www.astbearings.com/catalog/root/6708); the [ISK envelope](https://iskbearing.com/product-details/6708zz) is40×50×6 mm. Internal details are representative, not supplier production drawings. GLB/OBJ triangle and pose checks prevent display substitution or geometry loss. Renders show actual assembled, cutaway and exploded CAD.

CAD and real slicing are evidence for a fit-test print, not production qualification. Measure bearing fit/drag/retention, printed thread and cap-screw torque/pull-out/endurance, support cleanup, adhesive aging, Hall error and RF with bearing/phone/magnets present. Firmware is absent. No complete assembly-time study or physical pilot has been performed. See [pilot review](mechanical/MANUFACTURING_REVIEW.md).
