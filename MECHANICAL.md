# PCB / enclosure interface

All PCB coordinates are millimetres in a top view, relative to the rotation axis. The board is Ø36.5 × 1.0 mm and uses four Ø3.6 mm **nonplated** holes on a 16.2 mm radius at 45°, 135°, 225° and 315°. Hole centers are (±11.45513, ±11.45513). The 2.2 mm radius keepouts reserve the existing printed spacers around each hole.

The existing spacer positions leave only **0.25 mm nominal FR4 between each mounting hole and the circular edge**. This thin web needs explicit fabricator acceptance and handling review for the prototype. Support the board with the printed bushings and avoid forcing the holes or clamping against unsupported FR4. Increasing the board diameter would interfere with the current cap's inner retention skirt; a production revision should coordinate the hole pattern and enclosure before widening this web.

U2 package center is (0,0). U1 is a 6 × 6 mm QFN at (-7.5,5), replacing the earlier 5 × 5 mm CAD placeholder. SW1 actuator center is (12.65,0); its long body axis follows Y. All populated electronic parts are on top. Battery solder lands and SWD pads are on the underside outside the cell's Ø20 mm footprint.

The PCB bottom/top planes in the enclosure remain Z=5.3/6.3. The selected U2 package is at most 0.5 mm tall, so the existing encoder magnet bottom at Z=8.6 gives approximately 1.8 mm package-top clearance released and 1.3 mm pressed. The internal Hall plane is below the package surface; use measured magnetic field and calibrated angle to set the final magnet shim. Keep the Ø6 × 2 mm magnet **diametrically magnetized**.

## Required cap pusher adjustment

The actual KMR223NG ULC switch has a nominal actuator height of 1.9 mm and electrical travel of 0.25 ± 0.1 mm. The earlier CAD placeholder was 1.6 mm tall.

**Shorten the cap's annular pusher by 0.30 mm:** raise its lower face from Z=8.15 to **Z=8.45** in the released assembly, while retaining its radial extent 11.6–13.7 mm. With the PCB top at Z=6.3 and switch top at nominal Z=8.2, this gives nominal 0.25 mm free clearance. The cap's 0.5 mm travel then supplies nominal 0.25 mm switch displacement. In the existing CAD builder this is the `pcb_top+1.85` pusher expression: replace both occurrences with `pcb_top+2.15`.

The hardware switch and printed stack have tolerances. Fit the printed cap against the actual switch, tune the lower face/shims so electrical closure occurs before the cap stop, and provide local compliance so the tactile mechanism is not the structural hard stop. The outer grip sleeve and captured rotating cap geometry are retained. The previously exported Rev B cap STL is not automatically updated by this PCB project; use `Rotating_Cap_for_PCB_RevA.stl` supplied with the PCB handoff, or regenerate the cap before assembling this switch. The supplied cap preserves the Ø61.6 mm full-height grip sleeve and changes only the pusher.

## Replaceable battery contacts

BT1 is **a two-pole solder interface, not a commercial battery holder or two direct-contact pads on the same cell face**. Its wire lands have 1.8 mm copper diameter with a 0.6 mm plated drill, accessible from the underside:

| Land | Position | Connection |
|---|---|---|
| PLUS | (2,-11) | Spring touching the CR2032 upper positive face / positive rim |
| MINUS | (-2,-11) | Spring touching the smaller negative face on the underside |

Install the CR2032 **positive side toward the PCB**. The printed hatch's shallow cup locates it. Provide two compliant metal contacts and insulated leads to BT1. The existing 0.3 mm space above the cell can accept a thin formed positive leaf; a prototype starting material is 0.15 mm phosphor-bronze strip, approximately 2 mm wide, with an exposed contact tip and insulated tail. Form the tip to provide preload in that gap rather than stacking a commercial holder there.

A separate approximately 3 mm-wide, 0.15 mm-thick negative strip occupies the existing 4 × 11 × 0.2 mm floor relief under the cell. Its exposed contact tip bears on the negative disk; its tail exits through the cup's Y=-10.8 contact notch. Insulate the tail where it passes the positive can/rim. Join insulated flexible leads outside the cell footprint, where there is vertical room, and provide strain relief. The supplied dimensions are prototype contact blanks; spring force and final bends require a fit test. Bare PCB lands are not substitutes for these contacts.

The hatch is removed by undoing its two M2 screws. Lower it carefully; if its negative contact is hatch-mounted, leave enough flexible lead length for it to swing down without pulling on BT1. Lift the cell from the cup, insert a new CR2032 in the marked orientation and reinstall the hatch. The cap and PCB stay assembled. Cover the board underside over the cell with an insulating film; tent vias on both sides as specified. Soldermask alone should not be used as a moving cell-contact wear surface.

The five SWD pads are at Y=-14, X=-4,-2,0,2,4 (top-view coordinates), ordered VDD, GND, SWDIO, SWDCLK, nRESET. Their orientation appears mirrored when viewing the actual underside. Use these pads only with the underside accessible and avoid applying programming voltage against an installed primary cell. VDD is a target-voltage reference unless the cell is removed and an external supply is deliberately used.

Viewed directly from underneath, their left-to-right order is **R, C, D, G, V**, matching the underside silkscreen: reset, clock, data, ground, battery voltage.

TP_GND has a 0.4 mm plated drill in its 1.2 mm land; the other SWD pads are undrilled surface lands. Trim contact-wire ends and solder joints flush enough to preserve the top-side clearance.

Antenna keepout spans X=-3.5…3.5, Y=13.6…18.0 on both layers. Keep metal, wires and attachment parts out of that volume above/below the PCB where practical. The attachment magnet/shield annulus is outside the PCB, but the phone and cell still influence RF and the Hall sensor.

Three small signal diagnostic lands at the MCU escape points are 0.55 mm plated lands with 0.30 mm drills. They require no fitted components. Keep the specified underside insulating film over the cell footprint, including these lands.
