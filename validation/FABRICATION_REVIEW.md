# 1.0.30 fabrication review

This revision corrects confirmed electrical errors in 1.0.29. **Use the 1.0.30 fabrication ZIP; do not order the older PCB files.** It supports a controlled first article and quote. RF performance and physical assembly qualification remain open.

## Corrected circuit and layout

- DEC2 / U1 pin 32 is unconnected and marked accordingly in the physical pin model. C7 and its lands/trace are removed.
- DEC3 / U1 pin 33 uses C8 = **100 pF**, Murata GRM1555C1H101JA01D / JLC C77177. The former 100 nF value was wrong.
- C3 returns through VSS / physical pin 31 on a dedicated **1.348 mm, 0.18 mm top trace**, without vias. Both ground pours are excluded locally. An independent geometric check requires every contact with other ground copper to occur inside the actual VSS31 land, including its rounded end. It rejects a pour, branch or via bypass.
- All functional U1 schematic boxes display physical QFAA pin numbers while retaining physical port identity.
- C3 and C8 move locally; two crystal paths and one C8 ground endpoint change to maintain assembly/copper clearance. Two ground stitches give explicit local returns outside the isolated C3 region. There are **27 fitted components, 69 traces and 37 vias**. The other 25 fitted parts retain their supplier identities, lands, layers and poses. The board remains Ø36.5 × 1.0 mm with four Ø2.2 mm mounting holes.

Nordic's nRF52810 Product Specification v1.3, sections 7.3.1 and 7.3.9, supports these corrections. The [review resolution](AI_REVIEW_RESOLUTION.md) and [reference evidence](nordic-reference-evidence.json) identify the manufacturer PDF, inspected pages and download limitations. This does not establish Nordic qualification of the modified RF artwork.

## Digital verification

The compiler remains pinned to **tscircuit 0.0.3060** with a reproducible frozen lockfile. Source/saved-circuit comparison covers every record except descriptive filesystem metadata. The bounded revision guard permits only the specified component/pin changes against the earlier design; its complete routing reference continues to reject unapproved copper, nets, layers, widths, locations, masks, constraints and supplier orientations. Targeted tests reject the previous DEC3 value, a DEC2 connection and misleading schematic pin numbers.

**KiCad 9.0.2** independently checks 0.10 mm copper clearance, 0.11 mm tracks, 0.15 mm different-net SMT pad spacing, 0.20 mm drill clearance and 0.30 mm board-edge clearance. The final native check requires zero unresolved electrical/clearance errors and zero unconnected items. An actual injected wrong-net short must be rejected.

The native exporter triangulates ground fills into thousands of fragments. The review adapter fixes KiCad 9 tenting syntax and reconstructs connected contours from those existing fragments, preserving every hole as a bridged native contour. It **does not run a zone filler**. Native copper is independently compared with source at the **1 nm native coordinate precision**, including a real-copper-removal negative test. Source-exclusion diagnostics for mounting reserves, the antenna/feed, C3's isolated region and a DNP GPIO courtyard remain narrowly classified with reasons in the audit; actual fills and keepouts are checked separately. No electrical open, short or spacing error is waived.

**Gerbonara 1.6.3** independently parses delivered copper, mask and paste with ordered dark/clear polarity. Artwork must match source within 2 µm, including all **40 plated holes (37 vias + 3 GPIO interfaces)**, four NPTH holes, the closed 128-segment outline, tented vias and fitted-only stencil apertures. Actual added/removed copper mutations must fail. Separate checks retain programming connector margins, mounting-hole ground clearance and RF-return isolation.

The actual CAD assembly includes all 27 supplier models in their new poses. Printed geometry, 16.4 mm height, encoder gap, battery/holder, bearing and two-screw assembly interfaces remain unchanged. CAD/mesh, insertion, swept-clearance and slicer evidence are refreshed as their inputs require. Firmware host tests run C rotation/sensor logic with address/undefined-behavior sanitizers and 14 Python tool tests; actual flashing remains a separate gate.

## Assembly outputs and remaining gates

Strict placement frames come from 18 provenance-checked JLC imports. All 27 fitted BOM/CPL rows use verified supplier rotations. **Bottom BT1 uses JLC rotation 180°**, rather than authored 0°. It is the complete MYOUNG BS-24-B4AA014 / C7525448 holder, included in SMT assembly. Buy and insert the CR2450 separately. Verify positive pin 1 and polarized parts in the fabricator's placement preview.

Upload the bundle's **inner gerbers.zip** for the PCB and its accompanying BOM/CPL for assembly. Specify a 1.0 mm, two-layer, 1 oz board, Standard PCBA and ENIG for the WCSP sensor; confirm stencil/fixture requirements in the quote. Stock and attrition are not reserved.

The 17.924 mm RF feed retains a 0.5 mm width and no vias. **Its impedance is not verified.** Obtain the actual dielectric/copper stackup and solve the grounded coplanar structure before RF sign-off; measure matching, harmonics and BLE range on the populated assembly with bearing, ring, cell, phone and case. Component values and L2 ±5% remain initial matching choices.

The bearing has no positive axial lock. Coupon fit, seating/pull-off force, drag, repeated servicing, PETG creep, drop/handling, screw retention and magnet adhesive strength require physical measurements against defined acceptance loads. Holder/reflow/contact/polarity, magnetic counting, oscillator, current/runtime and firmware acceptance also remain open. See ASSEMBLY.md and the review resolution. Digital checks do not qualify a manufacturing batch.

## Reproduce

Install Bun dependencies with `bun install --frozen-lockfile`; install mechanical Python requirements plus validation/requirements-gerber.txt, KiCad 9 CLI/pcbnew and PrusaSlicer 2.8.1. Run the source build, refresh the saved snapshot, then bounded routing/RF checks, Bun tests, TypeScript, source parity, native fabrication and Gerber parity. Follow README.md for commands and the print manifest for slicer instructions. Audit hashes bind results to the final source and exports.
