# Battery and assembly review

The current fitted battery remains a replaceable **3V primary lithium CR2032,20×3.2mm** in the complete underside MYOUNG BS-08-B2AA020-R holder (C964787). Panasonic specifies225mAh nominal for its CR2032, at0.2mA standard continuous drain. This is a reference capacity, not a measured product runtime. Firmware, BLE duty cycle, Hall-sensor current and pulse voltage drop remain unmeasured. The circuit has no battery charger. Remove the cell before powering the programmer.

A Panasonic **CR2450 is24.5×5mm,620mAh nominal**:2.76times the reference capacity. The existing CR2032 holder does not accept it. Checking only the bare cell would miss the contacts, holder, supports, routing and insertion path.

| Candidate supplier holder | Result of assessment |
| --- | --- |
| MY-2450-01 / C964845 | Positive-pad corners reach18.64mm radius, beyond the18.25mm PCB radius. Has a central PCB pressure contact. |
| MY-2450-05-J / C7525439 |5.7mm clip height is attractive, but its large central negative PCB contact would cover existing bottom copper and vias on several other nets. Requires intentional PCB rerouting and qualified contact loading; it is not a soldered two-terminal replacement. |
| BS-24-B4AA016-R / C964810 | Complete insulated two-terminal holder; pad corners again exceed the current circular PCB outline. |
| BS-24-B4AK014 / C964813 | Two-terminal pads fit the outline, but supplier STEP height is8.61mm. At the current PCB bottomZ8.1 its lowest point would be−0.51mm, below the enclosure floor. |

An isolated trial of the last holder raised the board bottom toZ10.6 and rebuilt four posts at16mm radius, retaining2mm post radius. It cleared the1.5mm floor by0.49mm but intersected two upper posts by13.2074mm³ total. Translating the holderY−0.5mm still left3.0553mm³ overlap; other offsets and post angles tested did not resolve all collisions. This trial was not promoted into the circuit, enclosure or print set. It does not establish that every CR2450 solution is impossible; it establishes that the examined complete holders are not drop-in upgrades. A larger cell needs a dedicated board/support/holder design and physical contact qualification. The current revision keeps the proven layout and battery envelope.

Primary references: [Panasonic CR2032](https://energy.panasonic.com/na/business/products/lithium/coin-cr-standard/models/CR2032), [Panasonic CR2450](https://energy.panasonic.com/na/business/products/lithium/coin-cr-standard/models/CR2450), [C964813 holder drawing](https://datasheet.lcsc.com/datasheet/pdf/020fcde92e5545930d8684b3cfed077d.pdf?productCode=C964813). The drawing was visually inspected. Holder models and footprints were imported separately for evaluation; no speculative holder or cell change is included in the BOM.

# Bearing and assembly choice

The local V7 design uses **6808-ZZ /61808-2Z,40×52×7mm**, replacing6708,40×50×6mm. Metal shields are preferred for low hand-turning drag; seal, lubricant, internal clearance and race shoulder details still require the chosen sample. Do not substitute6808-2RS without evaluating drag. Nominal size equivalence is not brand/quality equivalence.

| Source checked | Evidence and limit |
| --- | --- |
| [AST6808](https://www.astbearings.com/catalog/root/6808) | Manufacturer40×52×7mm,21ballsØ3.5mm reference used for representative internals. |
| [ZKL61808-2Z](https://www.zkl.cz/en/p/61808-2Z) | Manufacturer dimensions;0.3mm corner radius; inner shoulder maximum42mm and housing shoulder maximum50mm. Model shouldersØ41.3 andØ50 match these nominal limits. |
| [SantEnt, India](https://store.santent.in/products/61808-2z-skf-ball-bearings) | SKF61808-2Z listing,40×52×7mm. Listing checked; firm stock, price and batch lead time unconfirmed. |
| [Bearings Direct, US](https://bearingsdirect.com/6808-zz-ball-bearing-40x52x7mm-shielded/) |6808-ZZ40×52×7mm listing with in-stock indication at review. Inventory is variable; no reservation/order. |

The40mm bore remains necessary around theØ36.5mm PCB and fixed support. Common smaller skateboard bearings do not leave that cavity. The new bearing fits without increasingØ58mm base or17.2mm top datum: bearingZ6.1–13.1, nutZ13.1–15.6, cap deck undersideZ15.9, three cap screws onR27.8. ShaftØ39.7 and housingØ52.2 preserve nominal radial assembly clearances0.15/0.10mm. Do not use those nominal numbers as a physical printer tolerance qualification.

For the10–50-unit printed PETG pilot, keep **three cap screws and two opposite PCB screws**, with four board support posts and two short rigid locating collars. This gives **four rigid prints,14 handled parts and five screw drives**, down from16parts/seven drives in1.0.25. The PCBA counts as one handled part; adhesive, tooling and consumables are excluded. Timing savings have not been measured. Bearing loads go through the fixed shaft/webs into the base rather than the PCB, which supports evaluating this reduced board-fastener count. Two-screw board retention, deflection, vibration and service life are physical release gates. Select screw heads within the BOM envelopes; common M2 thread size alone does not guarantee head fit. Use matching driver type where qualified SKUs allow. The steel bearing is0.5mm closer to the attachment ring than before, so magnetic and Hall tests must use the new bearing.

The [Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) supports a fixed bearing housing and uses two PCB screws, although its25×32×4mm bearing is too small for this board. [Formlabs' snap-fit guidance](https://formlabs.com/blog/designing-3d-printed-snap-fit-enclosures/) identifies process/orientation/tolerance dependence. PETG flexure fatigue and layer strength make tiny snaps a poor default for this pilot.

A three-lug rigid bayonet with one positive locking screw was modeled and its insertion/turn/seating path checked in an isolated trial. It reduces screw count further, but introduces internal undercuts, supported tracks, orientation/alignment and additional cleanup. No measured evidence shows it faster or more reliable on the user's printer. It is excluded from the delivered print set. Standard screw access is the more practical pilot recommendation; no claim of an objectively best design or production qualification is made.

The wider bearing requires moving the three cap screws outward by1mm and their supporting pads with them. Small exterior pad regions can grow on individual grip styles, including the turbine rim; every cap stays within the commonØ61.6mm limit. The base diameter and overall height do not increase.

Three shallow3mm-wide recesses in the retainer’s outer underside provide jig contact atZ5.1 while its body starts atZ4.6. They stay outside the bearing race lands and away from screw bosses, leaving1mm roof above the rests. The jig retains1mm-thick fingers with0.2mm clearance above the base roof. Its two halves still open3mm for removal. These are printed reference fits requiring a physical cleanup/handling trial.
