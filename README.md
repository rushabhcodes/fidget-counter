# MagSafe BLE fidget counter — rotation-only pilot

A CR2450-powered nRF52810 rotation counter with a centered TMAG3001 angle sensor, hollow bearing-supported cap, interchangeable grips and a five-pin JST-SH programming connector. Firmware is not included.

The current RevC design removes the whole-cap push action. The bearing shaft is integral with the stationary base: there are no return springs, sliding carrier, guide screws/washers, silicone actuator or pusher. SW1, its R5 pull-up, C17 filter and CAP_PRESS copper are removed from the PCB. U1 P0.29 is explicitly unused. The programmer's independent nRESET connection and R4 remain.

A unit uses **four rigid prints, five screws and 14 handled parts** including the PCBA, cell, bearing and two magnet assemblies. Adhesive and tooling are excluded from that count. The prior press pilot used five rigid prints, ten screws and 27 handled parts. Assembly time has not been measured.

The base remains Ø58 mm and the cap top remains at Z17.2 mm (17.0 mm above the phone-contact face). The standard 6808-ZZ / 61808-2Z bearing is now 40×52×7 mm. The Ø36.5×1 mm PCB outline, relative encoder/sensor gap, purchased 54×45.8×1.9 mm attachment ring and maximum Ø61.6mm cap envelope are retained. These ring dimensions describe the selected supplier reference; verify the sample and working face before buying a batch.

[Ploopy Knob assembly](https://ploopyco.github.io/knob/assembly-instructions/) is the rotation reference. Its fixed housing, rotating top and purchased bearing support the simpler architecture. Its [6705ZZ bearing](https://ploopyco.github.io/knob/appendices/hardware/) is too small for this PCB; our CAD is independent. The prior Surface Dial press reference is historical and no longer describes this product.

Start with [printing instructions](mechanical/printing/PRINTING.md), the [print manifest](mechanical/print-ready-manifest.json), [assembly guide](MECHANICAL.md), [mechanical BOM](mechanical/MECHANICAL_BOM.csv), [pilot review](mechanical/MANUFACTURING_REVIEW.md) and [programming guide](PROGRAMMING.md). Print one circular fit prototype and its coupons before a 10–50-unit batch. CAD and slicing do not prove printed fit, thread strength, adhesive retention, magnetic sensing or RF performance.

## What to buy

Quantities below are **per device with one cap**, except shared consumables and tools. Supplier links are examples checked on **3 November 2026**; stock, shipping to your country and pack quantities still need confirmation. Use the specified dimensions when comparing alternatives.

**Battery status:** the active local **RevC** circuit, BOM and CAD use **CR2450** with the complete [MYOUNG BS-24-B4AA014 / C7525448 holder](https://jlcpcb.com/partdetail/MYOUNG-BS_24B4AA014/C7525448). The PCB and encoder rise 2.5 mm internally, retaining **17.0 mm exterior height**. See the [implemented battery revision](mechanical/CR2450_UPGRADE.md), including holder/contact and physical qualification limits. Use matching RevC PCB/base/cap files.

| Item | Quantity | Required specification | Supplier links and fit notes |
| --- | ---: | --- | --- |
| Custom assembled PCB | 1 | RevC Ø36.5 × 1.0 mm PCB with the 28 fitted components in [BOM.csv](BOM.csv) | [JLCPCB assembly service](https://jlcpcb.com/pcb-assembly). This is a custom fabrication/assembly quote, not a stock product. If all **FIT** rows are assembled, BT1's battery holder, J_DEBUG and the other electronics are already included; do not buy those again as loose mechanical parts. |
| Thin-section bearing | 1 | **6808-ZZ / 61808-2Z, 40 × 52 × 7 mm**, metal shields | [India: SantEnt SKF 61808-2Z](https://store.santent.in/products/61808-2z-skf-ball-bearings) · [US: Bearings Direct 6808-ZZ](https://bearingsdirect.com/6808-zz-ball-bearing-40x52x7mm-shielded/). Confirm sample fit and drag; rubber-sealed 2RS variants need their own drag evaluation. |
| MagSafe magnetic ring assembly | 1 | Current seat: **N52, OD54 × ID45.8 × 1.9 mm**, complete magnetic array with working face toward the phone | [Default reference: MagnetPrint Hub kit](https://magnetprinthub.com/products/magsafe-magnet-kit). [India alternative: Magneticks](https://www.magneticks.in/magsafe-magnetic-ring-13003978.html) lists a **1.0 mm** ring and requires a changed seat depth; it is not the current 1.9 mm part. See [ring sourcing](mechanical/MAGSAFE_RING_SOURCING.md). |
| Encoder magnet | 1 per cap | **Ø5 × 1.5 mm, diametrically magnetized neodymium disc** | [BUYNEOMAGNETS exact-size diametric N38 example, 50-pack](https://www.buyneomagnets.com/p/5mm-x-1-5mm-diametrically-magnetized-neodymium-disc-magnet-n38-rare-earth-diametric-magnets-50-pack/). Size/pole-direction match the reference; magnetic grade and Hall performance still need sample testing. India delivery is unverified. Ordinary axially magnetized discs are not equivalent. |
| Cap-retainer screws | 3 | **M2 × 12 mm countersunk**, head Ø3.8 mm maximum; countersunk length includes the head | [India: 3fparts DIN 965 example](https://3fparts.com/shop/m2-12mm-csk-phillips-countersunk-machine-screws-din-965-stainless-steel-304-a2-70). Check the purchased head profile and tip/lead against a printed sample; torque and pull-out strength remain unqualified. |
| PCB screws | 2 | **M2 × 4 mm nylon**, head Ø3.8 mm maximum and height 1.3 mm maximum | [Vital Parts DIN 85, SPH85-M2-4-NY-N](https://www.vital-parts.co.uk/slotted-pan-head-nylon-screws-din-85/42809-sph85-m2-4-ny-n). This example is slotted; use a matching driver. UK supplier example; local equivalents must fit the same head envelope. No metal washer is specified. |
| Battery for current RevC PCB | 1 | **CR2450, 3 V primary lithium, 24.5 × 5 mm**, loose cell without solder tabs | [Panasonic India](https://www.panasonic.com/in/consumer/battery/specialty-batteries/lithium-coin/cr-2450-5be.html) · [India retailer example](https://rajivelectronics.com/product/panasonic-cr2450-3v-lithium-coin-cell-battery/). Insert after PCB reflow. The loose cell is separate from BT1; rechargeable LIR2450 is not a substitute. |
| Magnet adhesive | Small amount; shared pack | Compatible two-part adhesive for PETG and the magnet coating; ring bondline nominal 0.10 mm, encoder sidewall bond only | [RS India: LOCTITE EA 3430 clear epoxy example](https://in.rsdelivers.com/product/loctite/loctite-ea-3430-dc24ml/loctite-loctite-ea-3430-adhesive/2442021). **Coupon-test candidate**, not a qualified PETG bond specification. Check cure, adhesion and retention before choosing a batch adhesive. |
| PETG filament or printing service | As needed | PETG; the provisional print profile assumes a 0.4 mm nozzle and 1.75 mm filament | [Prusament PETG example](https://www.prusa3d.com/product/prusament-petg-jet-black-1kg/). Quantity depends on cap style, supports and batch size. Print the four product parts from the [manifest](mechanical/print-ready-manifest.json); filament is unnecessary if a print service supplies the material. |

The four printed product parts are **Stationary_Base, Inner_Race_Nut, Outer_Race_Retainer and one Cap**. The inner-race nut is printed, so no separate metal nut or heat-set insert is on this list. The reusable two-piece assembly nest and four fit coupons are separate prints. The rotation-only design has no return springs or push-button assembly to purchase.

The CR2450 holder is included in the custom PCBA quote as BT1; it is not an extra loose assembly part. The [earlier C964813 packaging study](mechanical/CR2450_HEIGHT_STUDY.md) is historical and is not the selected holder.

### Shared programming equipment

| Item | Quantity for the bench | Link and requirement |
| --- | ---: | --- |
| Five-way JST-SH programming cable | 1 | [JST A05SR05SR30K152B, DigiKey India](https://www.digikey.in/en/products/detail/jst-sales-america-inc/A05SR05SR30K152B/6708507). Use the **B** candidate and verify continuity **1→1 through 5→5** before powering; the A variant is listed as reversed. |
| Compatible SWD programmer and adapter | 1 setup | [Standard JST programmer v0.8.0 design](https://tscircuit--standard-jst-programmer-v0-8-0.tscircuit.app/#file=circuits%2Fprogrammer.circuit.tsx), which must itself be assembled/flashed, or a commercial [SEGGER J-Link BASE](https://www.segger.com/products/debug-probes/j-link/models/j-link-base/) with the adapter and target-power arrangement in [PROGRAMMING.md](PROGRAMMING.md). These are alternative setups, not two required purchases. |

Program before enclosure assembly. Use the documented 3.3 V programming arrangement and remove the coin cell when the programmer supplies power. The project does not yet include application firmware. Precision screwdrivers and ordinary PCB-handling tools can be reused across the batch.

## Rebuild and validate

Use the pinned Bun lockfile and Python requirements. With a working PrusaSlicer CLI:

```sh
bun install --frozen-lockfile
bun run typecheck
bun run check:routing
bun test validation/import-provenance.test.mjs validation/cr2450-regression.test.mjs
python mechanical/build_battery_courtyard.py
bun run build:source
cp dist/index/circuit.json published.circuit.json
bun validation/check-rotation-only.mjs
python mechanical/build_enclosure.py --style all --assembly-style circular
python mechanical/tooling/build_assembly_nest.py
python mechanical/build_fit_coupons.py
python mechanical/printing/audit_prints.py --slicer /path/to/prusa-slicer
python mechanical/printing/check_wall_sections.py
python mechanical/printing/render_slices.py
python mechanical/export_circuit_models.py
bun run build:source
cp dist/index/circuit.json published.circuit.json
bun validation/check-rotation-only.mjs
bun run build
python validation/check-rotation-only-cad.py
python validation/check-cr2450-copper.py
python validation/check-model-detail.py
python validation/check-attachment-ring.py
python validation/check-display-geometry.py
python validation/check-pcb-mounts.py
python validation/check-pcb-insertion.py
python validation/check-cr2450-holder.py
python validation/check-jst-fit.py
python validation/check-bearing-hardware.py
bun validation/check-imports.mjs
bun run check:programming
bun run check:assembly
python mechanical/render_bearing_layout.py
bun run build:cloud:prepare
bun validation/check-cloud-build.mjs
```

`mechanical/Print_STL` contains three common product parts and eleven alternative caps. Use exactly one cap per unit. Four fit coupons and two split-nest halves are separate calibration/tooling prints. Purchased/display parts are excluded. Assemblies are generated as assembled and exploded STEP files, with no pressed state.

The compiler remains pinned to tscircuit 0.0.3047. The router retains its failing safeguards for changes to physical terminals, net membership, layers, existing copper, widths, obstacles and board rules. The active CR2450 regression compares 27 retained components, all electrical pin attributes/connectivity and all trace/via/pad geometry outside the battery branches, and regenerated ground copper outside specified battery/mounting regions against commit `346fade`. The earlier press-removal proof remains in history. Two unchanged legacy trace-style advisories are exactly allowlisted; new advisories fail validation.

Hosted **1.0.25** contains the preceding6708/seven-screw rotation-only pilot;1.0.24 is the earlier press mechanism. The local RevC revision uses6808/five screws and CR2450 and is unpublished. Hosted publication verification is separate from local CAD/print validation. Historical compiler, manufacturing and publication reports retain their original revision labels; they do not certify the rotation-only pilot. The active evidence is `validation/cr2450-upgrade-status.json`, the `validation/cr2450-*-audit.json` files and `validation/print-readiness.json`. Earlier assembly-optimization reports describe the preceding CR2032 revision.

See the [implemented CR2450 revision](mechanical/CR2450_UPGRADE.md) and [earlier sourcing/screw-joint review](mechanical/BATTERY_AND_ASSEMBLY_REVIEW.md) for battery details, India/US bearing listings and the reasons for retaining five screws. The new local CAD has not been published as a tsCircuit release.
