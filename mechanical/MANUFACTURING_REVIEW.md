# Printed pilot manufacturing review

Scope: user-confirmed **10–50 units, 3D printed pilot**, reviewed 2 November 2026. This local candidate follows published 1.0.24 (`7e34fa6ac4ac2bafb9b2abe5689e58e93ada9c84`); it has not been published. No parts were purchased or suppliers contacted. This is a design-for-assembly recommendation with nominal CAD checks, not manufacturing qualification or a claim of an objectively optimal mechanism.

## Recommendation and actual changes

Use the bearing-supported cap, three guided return coils and four PCB screws for the first engineering samples. Establish repeatable click force, return and attachment before producing the whole pilot. Keep the current PCB, whole-cap reset, Ø58 mm base, 17.2 mm nominal released top datum and 0.8 mm stroke. The phone-contact plane is Z0.2, so the source solid envelope above that plane is 17.0 mm; both datums are unchanged from 1.0.24. Use those explicit datums when measuring parts.

1. **One printed base replaces base plus permanently bonded tray.** They share material, have no relative movement and need not separate for top-side battery service. The former annular interface is filled, keeping the purchased-ring pocket and guide/spring clearances. The continuous roof over the ring is now 1.5 mm rather than two separated roofs. This removes one handled part and one adhesive joint.
2. **An integral cap stop replaces the loose 0.2 mm encoder spacer.** All eleven caps locate the encoder magnet at the same Z11.4–12.9 mm. Bond in the existing 0.1 mm radial clearance; an axial adhesive layer would change the sensing gap and is not allowed without revalidation. This removes another handled part.
3. **Three integral retainer bosses increase nominal screw overlap from 1.4 to 4.4 mm.** Matching blind sockets in each cap provide 0.2 mm radial and roof clearance. Bearing lands, outside envelope and three M2×12 screws stay in place. The final cuts are applied after the grip union: the previous order refilled parts of the screw holes, and the first independent comparison exposed the same problem in the new boss sockets. Every finished cap is now checked against both retainer bosses and screw envelopes. No extra nut or insert is added. Thread engagement is geometric overlap, not a tested pull-out or torque rating; incomplete screw lead threads reduce effective engagement.
4. **A split assembly nest holds the retainer at Z5.1.** The old written sequence put the bearing in before the retainer. A Ø48.8 mm retainer cannot pass over a Ø50 mm bearing or Ø58 mm base. Place it first. The nest supports it while the top screws are started, avoiding a second hand holding the cap down. Open the halves at least 3 mm each to eject. Remove the nest before testing the cap press.
5. **A separate two-PCB-screw trial is provided**, using the opposite locating-post pair (indices 0,2), with all four support posts and board holes retained. Default remains four screws. Ploopy's two-screw board is a useful trial reference, but does not establish retention of our board, bottom battery holder or off-center switch load. Do not mix this candidate into the default BOM before deflection/shock/service tests.

## Parts and operations

Count one chosen cap, one fully populated PCBA as a subassembly, and each separately handled screw, washer and coil. Exclude soldered parts within the PCBA, liquid adhesive and optional calibration shims. Tooling is not a product part. Fifteen rigid STL files cover four common parts plus eleven cap alternatives; a unit uses five rigid prints. The silicone reference STL is not a PETG part.

| Per unit | Published 1.0.24 | Default candidate | Two-screw trial |
| --- | ---: | ---: | ---: |
| Rigid printed parts | 6 | 5 | 5 |
| Screws / screw drives | 10 | 10 | 8 |
| Separate guide washers | 3 | 3 | 3 |
| Return coils | 3 | 3 | 3 |
| Other purchased/handled parts | 7 | 6 | 6 |
| **Total handled parts** | **29** | **27** | **25** |
| Minimum specified adhesive joints | 4 | 3 | 3 |

The default's six other parts are bearing, silicone actuator, encoder magnet, attachment ring, CR2032 and populated PCBA. Published 1.0.24 also had the encoder spacer. Adhesive joints are ring, encoder and actuator, plus the former tray joint; an optional spacer bond or calibration shim could add operations.

[Timing worksheet](ASSEMBLY_TIME_STUDY.csv): the expected benefit is removal of tray preparation/bonding and spacer handling, plus easier retainer screw starting. A planning hypothesis is **45–105 seconds less touch labor per unit** (40–90 seconds for tray handling/adhesive, 5–15 for spacer), not a measured cycle time. Cure, printing, flashing, calibration, inspection and rework are excluded. Any newly required hole drilling/tapping or longer screw driving must be timed too and may reduce the net saving; the estimate is removed touch labor, not a guaranteed net cycle reduction. The optional two-screw trial could remove another 16–30 seconds assuming 8–15 seconds per screw; that estimate also needs measurement. Do not quote a total assembly time or cost yet. Time at least five repetitions per design, record failures/rework and compare median and slow cases before accepting the change.

## Why a return spring exists

The cap, bearing, carrier, nut, retainer and encoder magnet move together during a press. The three coils act in parallel between the **stationary base and nonrotating carrier**. They lift this moving mass, seat it against the upper guide stops and share off-center load. They are not rotation detents and do not count turns. Gravity cannot return a phone accessory reliably in every orientation. The tactile switch's internal dome returns its own actuator; the present 0.15 mm released gap leaves it disconnected from the cap at rest. Deleting all coils would remove the defined return and released-height preload.

Using the specified target rate 0.45 N/mm each, 4 mm free length and 3.5 mm installed length gives **0.675 N total preload**, **1.755 N at full press**, and 1.35 N/mm combined rate. These are calculations from a purchasing target, not measurements or a selected spring SKU. Even without friction, 0.675 N supports only about 69 g against gravity. We must weigh the full moving assembly and measure guide friction, tilt margin and axial magnetic attraction between the fixed ring/phone and the steel bearing. That magnetic force can consume the return preload or hold the cap down; test with the ring and intended phone installed. Nominal spring solid-height clearance is 0.5 mm at full stroke.

The drawn five-active-turn Ø0.25 mm-wire, OD3 mm coil does not by itself prove that target rate. The standard compression-spring formula gives about 0.329–0.376 N/mm for shear moduli of 70–80 GPa. Qualify an actual matched SKU by load at **3.5 and 2.7 mm working lengths**, solid height, end seating and life. The rendered spring is representative; do not order from its mesh.

| Return option | Assembly effect | Decision for this pilot |
| --- | --- | --- |
| Three purchased metal coils | Three placements; known base pockets; independent of rotating friction | Keep pending actual SKU/force qualification |
| One silicone diaphragm connecting three return pads | Could become one handled part; still uses elastic spring action | Best no-separate-metal-coil development candidate; not a drop-in qualified part |
| One annular wave spring | Could reduce three placements to one; still a spring | Possible later; requires a real SKU, seats and guide/holder clearance study |
| Existing tactile dome alone | Fewer parts | Does not support the released cap with the current gap/load path |
| Printed flexures or magnetic repulsion | Potentially fewer parts | Not selected: printed fatigue/creep and Hall-field sensitivity need substantial new qualification |

A silicone return diaphragm must act **between base and carrier**, with no rotating rubbing face. The current rotating actuator ring only presses the switch; it is not that diaphragm. Select return preload from mass, friction and tilt tests; measure temperature-dependent force, compression set and cycle life. Do not assume a foam datasheet's single compression point proves reliable dynamic return. A one-piece elastomer could simplify a later design, but exchanging three available coils for an unqualified custom material is not a production improvement established by this review.

## Reference check

Sources inspected online on 2 November 2026; observations and design inferences are separated here.

| Reference | Verified observation | Application and limit |
| --- | --- | --- |
| [Ploopy official assembly](https://ploopyco.github.io/knob/assembly-instructions/) and [hardware](https://ploopyco.github.io/knob/appendices/hardware/) | Two PCB screws, bearing retained between printed housing parts; specified bearing 6705ZZ, 25×32×4 mm | Supports fewer board fasteners as a test candidate and bearing-supported rotation. Its instructions do not establish full-cap press/return. Its smaller bearing cannot surround our Ø36.5 mm board. |
| [Surface Dial physical teardown, steps 7–8](https://www.ifixit.com/Teardown/Microsoft+Surface+Dial+Teardown/74808) | Two springy posts balance pressure opposite its microswitch; bearing retained separately | Supports separating rotation from guided press/return. Does not prove our three-coil force or dimensions. [Microsoft's fact sheet](https://news.microsoft.com/wp-content/uploads/prod/2016/11/Surface-Dial-Fact-Sheet-Final.pdf) gives 59×30 mm; ours is much shorter, so copying its complete stack is inappropriate. |
| [C&K/Littelfuse KMR2 datasheet](https://www.ckswitches.com/media/1479/kmr2.pdf), revised 28 Jan 2026 | Specified SW1 is KMR223NG ULC LFG / Y78B22324FP: operating force 2±0.5 N, electrical travel 0.25±0.1 mm; 200,000 specified switch operations. The differently named KMR232 model supplies shared package geometry only | The circuit/BOM part number, not the mesh filename, determines the force/life specification. Electrical travel is not a permissible overload rating, and switch life is not assembled-product life. Measure this exact part with the compliant ring and housing stop. |
| [Smalley wave springs](https://www.smalley.com/wave-springs) | Flat-wire compression springs can supply axial load in reduced height; selection depends on working-height loads | Useful one-spring reference, not a selected or verified drop-in part. |
| [Screwerk plastic screw design](https://us.screwerk.com/en/products/stp.html) | Engagement/bore recommendations depend on polymer and screw type; molded PET guidance is about 1.7 diameters | Explains concern with the former 0.7-diameter overlap. Our 2.2-diameter nominal overlap is an improvement, not certification of FDM PETG or generic machine screws. |
| [Boothroyd Dewhurst DFA method](https://www.dfma.com/design-for-assembly.asp) | Reduce unnecessary separate parts and handling while preserving required movement/material/service functions | Basis for consolidating the fixed base/tray and spacer stop while retaining the moving carrier and service fasteners. |

## Process, access and tolerance plan

Use PETG, one qualified printer/profile/material lot initially. Start with 0.15 mm layers and at least four walls, then verify actual slicer paths; these settings are a trial starting point, not a strength specification. Caps print top-face down; the base prints phone-face down. The annular seat roof bridges the ring pocket: inspect this underside for sag, not only its outside dimensions. Keep support scars out of guide bores, bearing seats and threads. Print and measure coupons before parts. Do not scale the whole model to fix a bearing fit.

| Interface | Nominal allowance | Required pilot check |
| --- | --- | --- |
| Bearing shaft ID40 / seat Ø39.7 | 0.15 mm radial | Actual bearing/chamfer/shoulder fit; no seal rubbing or forced insertion |
| Bearing OD50 / cap bore Ø50.2 | 0.10 mm radial | Smooth seated fit and rotation after screws tighten |
| Guides Ø5 / bores Ø5.3 | 0.15 mm radial | Free stroke and off-center return at printer variation; three guides can bind if not parallel |
| Ring OD54 ID45.8 / pocket OD54.3 ID45.5 | 0.15 mm radial; 0.10 mm bondline | Complete supplier envelope/tolerance, face polarity, seating and adhesive thickness |
| Retainer bosses Ø3.2 / sockets Ø3.6 | 0.20 mm radial and roof gap | Free seating; screw clamps the bearing land, not a bottomed boss |
| Actuator / switch | 0.15 mm nominal released gap | Calibrated go/no-go gap, no closure at rest, reliable closure at every angle |

The cap moves 0.8 mm. After the nominal 0.15 mm gap, the approach is 0.65 mm; the specified electrical travel range is 0.15–0.35 mm. The silicone therefore has to accommodate a further **0.30–0.50 mm nominal deformation** in this simplified stack calculation. That is 20–33% of its 1.5 mm thickness. It is not evidence that an arbitrary silicone ring will provide the right force or protect the switch. Measure the assembled force/displacement/electrical-closure curve, tolerance extremes and hard-stop load. Do not compensate with a rigid printed actuator or arbitrary shims. Establish a fixed qualified shim/material recipe to avoid per-unit trial-and-error in production.

Top access permits cap, bearing, PCBA and battery service without removing the bonded attachment ring. Ten screw drives remain in the default. Inspect the printed pilot holes and qualify direct thread-forming versus controlled drilling/tapping with the chosen screw. Record any such preparation as assembly labor. Qualify torque with the chosen screw and printed orientation; no torque is specified without stripping/pull-out tests. Kitting screws by size and using a controlled driver is preferable to mixing hardware. Do not bond service joints to save assembly time.

## Release gates still requiring hardware

1. Build a few engineering samples before committing all 10–50 units. Record actual dimensions, moving mass, spring SKU/working loads, guide friction and tilt in all intended orientations.
2. Qualify printed retainer/guide/PCB threads with tightening, pull-out and repeated service tests. If they fail, assess a same-envelope metal retainer or properly designed inserts as a new revision; do not silently add hardware or use adhesive as retention.
3. Qualify compliant actuator force/travel, switch load limit, off-center clicking, no false reset at rest and repeated press/rotation life. Agree the product-life/load/environment targets before claiming durability; switch catalog life is insufficient.
4. Qualify purchased magnetic ring complete dimensions, working face and phone/case attachment peel/shear/drop performance. Check ring and encoder adhesive retention and printing/adhesive temperature compatibility.
5. Measure Hall angle/count accuracy, BLE range and magnetic axial bias/return with bearing, screws, ring and representative phones/cases present. If steel prevents reliable return or sensing, qualify a nonmagnetic bearing of the same verified envelope or revisit spring/field design; do not infer suitability from CAD. Firmware is absent from this repository: a qualified image, debounce/count/reset behavior, power measurement and end-of-line programmer/test procedure are required.
6. Measure assembly time and first-pass yield using the worksheet. Include calibration, cure and rework in the eventual production estimate; inspect jig fit and screw access with actual tools.

The checked bundle exports the circular released/pressed/exploded STEP assemblies and all eleven cap STEP/STL parts. `--assembly-style all` generates the other assembled variants if needed; their cap solids and motion are still checked in the representative-export build.

Nominal CAD, mesh and circuit validation can be completed locally. All physical tests above remain unrun; this candidate must not be labelled ready for production on the basis of renders.
