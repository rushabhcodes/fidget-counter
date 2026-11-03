# MagSafe BLE fidget counter — rotation-only pilot

A CR2450-powered nRF52810 rotation counter with a centered TMAG3001 angle sensor, hollow bearing-supported cap, interchangeable grips and a five-pin JST-SH programming connector. Firmware is not included.

The current RevC design removes the whole-cap push action. The bearing shaft is integral with the stationary base: there are no return springs, sliding carrier, guide screws/washers, silicone actuator or pusher. SW1, its R5 pull-up, C17 filter and CAP_PRESS copper are removed from the PCB. U1 P0.29 is explicitly unused. The programmer's independent nRESET connection and R4 remain.

A unit uses **two rigid prints, two PCB screws and nine handled parts** including the PCBA, cell, bearing and two magnet assemblies. Adhesive and tooling are excluded from that count. The prior press pilot used five rigid prints, ten screws and 27 handled parts. Assembly time has not been measured.

The base remains Ø58 mm and the cap top remains at Z17.2 mm (17.0 mm above the phone-contact face). The standard 6808-ZZ / 61808-2Z bearing is now 40×52×7 mm. The Ø36.5×1 mm PCB outline, relative encoder/sensor gap, purchased 54×45.8×1.9 mm attachment ring and maximum Ø61.6mm cap envelope are retained. These ring dimensions describe the selected supplier reference; verify the sample and working face before buying a batch.

[Ploopy Knob](https://ploopy.co/knob/) and its [assembly guide](https://ploopyco.github.io/knob/assembly-instructions/) are the rotation references. Its fixed housing, rotating top and purchased bearing support the simpler architecture. Its [6705ZZ bearing](https://ploopyco.github.io/knob/appendices/hardware/) is too small for this PCB; our CAD is independent. The prior Surface Dial press reference is historical and no longer describes this product.

Start with [printing instructions](mechanical/printing/PRINTING.md), the [print manifest](mechanical/print-ready-manifest.json), [assembly guide](MECHANICAL.md), [mechanical BOM](mechanical/MECHANICAL_BOM.csv), [pilot review](mechanical/MANUFACTURING_REVIEW.md) and [programming guide](PROGRAMMING.md). Print one circular fit prototype and its coupons before a 10–50-unit batch. CAD and slicing do not prove push-fit retention, adhesive strength, magnetic sensing or RF performance.

## What to buy

Quantities below are **per device with one cap**, except shared consumables and tools. Supplier links are examples checked on **3 November 2026**; stock, shipping to your country and pack quantities still need confirmation. Use the specified dimensions when comparing alternatives.

**Battery status:** the active **RevC** circuit, BOM and CAD use **CR2450** with the complete [MYOUNG BS-24-B4AA014 / C7525448 holder](https://jlcpcb.com/partdetail/MYOUNG-BS_24B4AA014/C7525448). The PCB and encoder rise 2.5 mm internally, retaining **17.0 mm exterior height**. See the [implemented battery revision](mechanical/CR2450_UPGRADE.md), including holder/contact and physical qualification limits. Use matching RevC PCB/base/cap files.

| Item | Quantity | Required specification | Supplier links and fit notes |
| --- | ---: | --- | --- |
| Custom assembled PCB | 1 | RevC Ø36.5 × 1.0 mm PCB with the 28 fitted components in [BOM.csv](BOM.csv) | [JLCPCB assembly service](https://jlcpcb.com/pcb-assembly). This is a custom fabrication/assembly quote, not a stock product. If all **FIT** rows are assembled, BT1's battery holder, J_DEBUG and the other electronics are already included; do not buy those again as loose mechanical parts. |
| Thin-section bearing | 1 | **6808-ZZ / 61808-2Z, 40 × 52 × 7 mm**, chrome steel, two metal shields | [India: HMS](https://www.hmsbearings.co.in/68-series-deep-groove-ball-bearing.html) · [India: BM3/Moglix](https://www.moglix.com/bm3-6808-zz-chrome-steel-deep-groove-ball-bearing-40x52x7-mm/mp/msn8klp8p8yr5v) · [India: NTN/Bearing House](https://bearinghouse.in/shop/ntn-6808zz-deep-groove-ball-bearings/) · [US: JSB](https://jsbgreatbearings.com/product/6808-zz-two-side-metal-shields-bearing-6808-rs-ball-bearings-6808-rs/). See the price/stock comparison below. Supplier drawing and samples must establish race contact, fit, drag and play; 2RS variants require their own drag evaluation. |
| MagSafe magnetic ring assembly | 1 | Current seat: **N52, OD54 × ID45.8 × 1.9 mm**, complete magnetic array with working face toward the phone | [Default reference: MagnetPrint Hub kit](https://magnetprinthub.com/products/magsafe-magnet-kit). [India alternative: Magneticks](https://www.magneticks.in/magsafe-magnetic-ring-13003978.html) lists a **1.0 mm** ring and requires a changed seat depth; it is not the current 1.9 mm part. See [ring sourcing](mechanical/MAGSAFE_RING_SOURCING.md). |
| Encoder magnet | 1 per cap | **Ø5 × 1.5 mm, diametrically magnetized neodymium disc** | [BUYNEOMAGNETS exact-size diametric N38 example, 50-pack](https://www.buyneomagnets.com/p/5mm-x-1-5mm-diametrically-magnetized-neodymium-disc-magnet-n38-rare-earth-diametric-magnets-50-pack/). Size/pole-direction match the reference; magnetic grade and Hall performance still need sample testing. India delivery is unverified. Ordinary axially magnetized discs are not equivalent. |
| PCB screws | 2 | **M2 × 4 mm nylon**, head Ø3.8 mm maximum and height 1.3 mm maximum | [Vital Parts DIN 85, SPH85-M2-4-NY-N](https://www.vital-parts.co.uk/slotted-pan-head-nylon-screws-din-85/42809-sph85-m2-4-ny-n). This example is slotted; use a matching driver. UK supplier example; local equivalents must fit the same head envelope. No metal washer is specified. |
| Battery for current RevC PCB | 1 | **CR2450, 3 V primary lithium, 24.5 × 5 mm**, loose cell without solder tabs | [Panasonic India](https://www.panasonic.com/in/consumer/battery/specialty-batteries/lithium-coin/cr-2450-5be.html) · [India retailer example](https://rajivelectronics.com/product/panasonic-cr2450-3v-lithium-coin-cell-battery/). Insert after PCB reflow. The loose cell is separate from BT1; rechargeable LIR2450 is not a substitute. |
| Magnet adhesive | Small amount; shared pack | Compatible two-part adhesive for PETG and the magnet coating; ring bondline nominal 0.10 mm, encoder sidewall bond only | [RS India: LOCTITE EA 3430 clear epoxy example](https://in.rsdelivers.com/product/loctite/loctite-ea-3430-dc24ml/loctite-loctite-ea-3430-adhesive/2442021). **Coupon-test candidate**, not a qualified PETG bond specification. Check cure, adhesion and retention before choosing a batch adhesive. |
| PETG filament or printing service | As needed | PETG; the provisional print profile assumes a 0.4 mm nozzle and 1.75 mm filament | [Prusament PETG example](https://www.prusa3d.com/product/prusament-petg-jet-black-1kg/). Quantity depends on cap style, supports and batch size. Print the two product parts from the [manifest](mechanical/print-ready-manifest.json); filament is unnecessary if a print service supplies the material. |

The two printed product parts are **Stationary_Base and one Cap**. There is no separate nut, outer-race retainer or top screw. Ten bearing-fit coupons are separate calibration prints, not unit parts. The rotation-only design has no springs or push-button assembly. This Ploopy-style hand push-fit is a **fit-test pilot**: nominal 0.05 mm diametral interference is not a measured printer fit, and there is no positive axial lock. Qualify pull-off force, drag, PETG creep, service life and attachment loads before a batch.

The CR2450 holder is included in the custom PCBA quote as BT1; it is not an extra loose assembly part.

### Bearing sourcing for the 10–50-unit pilot

The design uses the standard **6808-ZZ / 61808-2Z, 40 × 52 × 7 mm** family; it does not require the SKF brand in the earlier reference link. Start with economical chrome-steel, double-shielded samples and qualify a primary and backup supplier.

| Region and supplier | Advertised price per bearing | Availability shown when checked |
| --- | --- | --- |
| [India: HMS Bearings](https://www.hmsbearings.co.in/68-series-deep-groove-ball-bearing.html) | Approx. **₹75**, minimum **10 pieces** | Indicative quote; stock, GST and shipping unconfirmed |
| [India: BM3 through Moglix](https://www.moglix.com/bm3-6808-zz-chrome-steel-deep-groove-ball-bearing-40x52x7-mm/mp/msn8klp8p8yr5v) | Approx. **₹124 including GST** | **Available on request**; not confirmed ready stock |
| [India: NTN through Bearing House](https://bearinghouse.in/shop/ntn-6808zz-deep-groove-ball-bearings/) | **₹566.40 including GST** | Listed **in stock**; quantity and delivery-pincode stock unconfirmed |
| [US: JSB Great Bearing, JSB-6808-ZZ](https://jsbgreatbearings.com/product/6808-zz-two-side-metal-shields-bearing-6808-rs-ball-bearings-6808-rs/) | **US$1.60 each for 10–49**, **US$1.50 for 50–99**; single-piece price **US$5.90** | Listed in stock; seller advertises free US shipping; tax/checkout unconfirmed |

Prices and page stock indications were checked on **3 November 2026**. These are sourcing candidates, not accepted quotes, reserved inventory or qualified interchangeable SKUs. Confirm dimensions, actual race/shield contact lands, corner radii, normal internal clearance, lubricant/turning drag, axial play and magnetic/Hall behavior on the chosen samples. The representative bearing internals in the CAD are not supplier production CAD.

A 608 bearing's 8 mm bore does not support the present annular layout around the Ø36.5 mm PCB; a 6008's Ø68 mm outside diameter exceeds the Ø58 mm base. Changing to either would require a different layout. The 6808 family preserves the current nominal cavity and outer envelope. The pre-fabrication revision changes the base shoulder contact land from Ø41.3 to **Ø42.0 mm**, matching the [NSK 6808ZZ abutment recommendation](https://www.nsk.com/engineering/products/bearings/ball-bearings/deep-groove-ball-bearings/single-row-deep-groove-ball-bearings/6808zz-dgbb-sr.html) and the [ZKL 61808-2Z maximum](https://www.zkl.cz/en/p/61808-2Z). Use the matching current base/cap files. This nominal correction does not qualify an arbitrary supplier’s shield/race geometry or a printed interference fit.

### Shared programming equipment

| Item | Quantity for the bench | Link and requirement |
| --- | ---: | --- |
| Five-way JST-SH programming cable | 1 | [JST A05SR05SR30K152B, DigiKey India](https://www.digikey.in/en/products/detail/jst-sales-america-inc/A05SR05SR30K152B/6708507). Use the **B** candidate and verify continuity **1→1 through 5→5** before powering; the A variant is listed as reversed. |
| Compatible SWD programmer and adapter | 1 setup | [Standard JST programmer v0.8.0 design](https://tscircuit--standard-jst-programmer-v0-8-0.tscircuit.app/#file=circuits%2Fprogrammer.circuit.tsx), which must itself be assembled/flashed, or a commercial [SEGGER J-Link BASE](https://www.segger.com/products/debug-probes/j-link/models/j-link-base/) with the adapter and target-power arrangement in [PROGRAMMING.md](PROGRAMMING.md). These are alternative setups, not two required purchases. |

Program before enclosure assembly. Use the documented 3.3 V programming arrangement and remove the coin cell when the programmer supplies power. The project does not yet include application firmware. Precision screwdrivers and ordinary PCB-handling tools can be reused across the batch.

## Current downloads

[Print pilot ZIP](https://github.com/rushabhcodes/fidget-counter/blob/codex/bearing-supported-enclosure/manufacturing/fidget-counter-print-pilot-1.0.28.zip) · [Fabrication ZIP](https://github.com/rushabhcodes/fidget-counter/blob/codex/bearing-supported-enclosure/manufacturing/fidget-counter-fabrication-1.0.28.zip) · [Contents and limits](manufacturing/README.md)

Use the linked checked fabrication ZIP for the PCBA quote; it includes the verified supplier rotations and paste/mask preparation.

## Rebuild and validate

Clone the Git repository with history for the regression baselines. Use **tscircuit0.0.3060**, the pinned Bun lockfile, mechanical Python requirements, validation/requirements-gerber.txt, KiCad9 and PrusaSlicer2.8.1. The hosted build uses the pinned compiler.

```sh
bun install --frozen-lockfile
bun run typecheck
bun test
python mechanical/build_battery_courtyard.py
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/build_fit_coupons.py
python mechanical/printing/audit_prints.py --slicer /path/to/prusa-slicer
python mechanical/printing/check_wall_sections.py
python mechanical/printing/render_slices.py
python mechanical/export_circuit_models.py
bun run build:source
cp dist/index/circuit.json published.circuit.json
bun validation/check-fresh-routing.mjs
bun validation/check-source-snapshot.mjs
bun validation/run-fabrication-review.mjs
python validation/check-gerber-parity.py
python validation/check-pushfit-cad.py
python validation/check-cr2450-copper.py
bun validation/check-cr2450-circuit.mjs
python validation/check-model-detail.py
python validation/check-attachment-ring.py
python validation/check-cr2450-display.py
python validation/check-pcb-mounts.py
python validation/check-pcb-insertion.py
python validation/check-cr2450-holder.py
python validation/check-jst-fit.py
python validation/check-bearing-hardware.py
bun validation/check-imports.mjs
bun validation/check-passive-substitutions.mjs
bun run check:programming
bun run check:assembly
bun run build
python mechanical/render_bearing_layout.py
bun run build:cloud:prepare
bun validation/check-cloud-build.mjs
```

`mechanical/Print_STL` contains **one common base and eleven alternative caps**. A unit uses the base and exactly one cap. Ten bearing-fit coupons are separate calibration prints; there is no split fixture, nut or retainer to print. Purchased/display parts are excluded. Re-slice for the actual printer; no machine G-code is supplied.

The active1.0.28 revision has two printed parts, two PCB screws and no top screws. It replaces the old copper with refined fresh routing on0.0.3060: new critical paths, latest-pipeline routing and local clearance repairs. All28 fitted geometries, real electrical pin attributes and pin-net membership remain unchanged; routing vias fall from48 to40. Strict input/output routing contracts and negative checks reject unapproved copper, connectivity, layers, locations and constraints. The new circuit has no trace-style advisories.

See the [fabrication review](validation/FABRICATION_REVIEW.md), [pilot assembly review](mechanical/MANUFACTURING_REVIEW.md) and [compact experiment record](experiments/fresh-routing/README.md). Current evidence is the named current audit JSON files in validation/; obsolete release logs, snapshots, fixtures and reports have been removed from the working tree. Previous revisions remain in Git history. The [tsCircuit package](https://tscircuit.com/rushabhcodes/fidget-counter) carries versioned releases. Digital checks support a controlled prototype, with physical fit, retention, holder/contact, magnet/Hall, RF and firmware qualification still required.

### Passive sourcing update (1.0.27)

| References | Replacement to select in PCBA quote | Specification |
| --- | --- | --- |
| C1, C2, C11, C12 | [FH 0402CG120J500NT / C1547](https://jlcpcb.com/partdetail/0402CG120J500NT/C1547) | 12pF, 50V, C0G, ±5%, 0402; Basic catalog part |
| C10 | [Samsung CL10B105KA8NNNC / C29936](https://jlcpcb.com/partdetail/CL10B105KA8NNNC/C29936) | 1µF, 25V, X7R, ±10%, 0603 |
| L2 | [Murata LQG15HS6N8J02D / C77110](https://jlcpcb.com/partdetail/MurataElectronics-LQG15HS6N8J02D/C77110) | 6.8nH, **±5%**, 0402; replaces the ±2% G variant |

The native source, saved circuit and BOM use these exact new supplier identifiers. Their imported solder lands match the preceding parts exactly; supplier OBJ and STEP model bytes also match. The1.0.27 sourcing change retained placement, copper and enclosure. The active1.0.28 revision retains the fitted electrical geometry and height while applying the new routing and simpler cap assembly described above. Original imports remain as provenance and comparison data, not alternative fitted BOM selections. L2 retains the validated two-terminal schematic symbol and pin aliases while using its new supplier import for the lands, identity and CAD.

**L2 is a conditional RF substitution:** the wider ±5% tolerance is not identical to the previous ±2% specification. Verify antenna matching, radiated performance and oscillator operation on populated samples in the final enclosure before production. Existing battery/contact, printed-fit, magnetic and firmware qualification gates remain open. Public catalog stock is not reserved stock; confirm exact SKUs, quantity and attrition in the assembly quote. For 20 boards the four 12pF references consume 80 pieces before attrition from the same shared SKU stock.

Run `bun validation/check-passive-substitutions.mjs` and `bun test`. The sourcing guard verifies the six identities and original supplier model bytes; the fresh-routing guard separately checks the explicitly approved new copper, all fitted geometry, electrical pin attributes and net membership. See validation/passive-substitution-audit.json and validation/fresh-routing-audit.json.
