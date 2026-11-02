# Purchased MagSafe attachment ring

The local ring revision replaces the 24 separate attachment discs and their separate backing ring with one purchased MagSafe ring assembly. The central diametrically magnetized encoder disc remains essential to rotation sensing. Base diameter stays 58 mm, overall height 17.2 mm, and the current revision is rotation-only without axial press travel.

Supplier pages were checked on 1 November 2026. Prices, stock and delivery are supplier listings, not a confirmed quotation or order.

| Supplier | Published dimensions, OD × ID × thickness | Listed supply | Use in this design |
| --- | --- | --- | --- |
| [MagnetPrint Hub N52 ring kit](https://magnetprinthub.com/products/magsafe-magnet-kit) | 54 × 45.8 × 1.9 mm, stated ±0.05 mm | US shop; $9.50/2, $34.99/10, $69/25 | Default CAD reference. Supplier describes a one-sided multipole Halbach array for glue-in printed phone mounts. India is absent from its displayed region list; India delivery is unverified. |
| [Magneticks, Mumbai](https://www.magneticks.in/magsafe-magnetic-ring-13003978.html) | 54 × 46 × 1.0 mm, N52 | Supplier lists MOQ 100 and 3-day delivery; [marketplace listing](https://www.tradeindia.com/products/magsafe-magnetic-ring-c13003978.html) displays ₹75 + GST per piece | Domestic sourcing candidate. Requires its own parameterized seat depth; do not put the thin ring in the 1.9 mm pocket without adapting the seat. Tolerance, accessory-side working face and complete assembly thickness need supplier confirmation. |
| [totalElement R54X46X15MMN52-5PK](https://totalelement.com/products/54-x-46-x-1-5mm-magsafe-neodymium-rare-earth-magnet-phone-attachment-ring-assembly-with-alignment-magnet-5-pack) | Detailed specification says 54.1 × 46 × 1.5 mm; title rounds OD to 54 | US shop; $24.99/5, listed in stock | Alternative assembled N52 ring on a steel carrier. Confirm whether the stated thickness covers the carrier. The supplied separate alignment bar is outside this round housing's scope. |

A passive steel adapter sticker is not an equivalent replacement. Obtain a ready-assembled magnetic ring; do not assemble loose segments into the printed part. The display model's shallow segmentation is representative, not a supplier-certified internal drawing or field simulation.

## Seat and assembly

The current manufacturing candidate has one open annular seat in the integrated stationary base. Published 1.0.24 used a separate bonded tray. For the default kit its pocket is OD54.30 × ID45.50 mm, giving nominal 0.15 mm radial clearance on each edge. The pocket roof is at Z2.40 mm, with a 1.50 mm continuous printed roof above it. A nominal 0.10 mm adhesive layer places the ring face at Z0.40 mm, 0.20 mm behind the base's phone-contact plane. Supplier thickness tolerance changes this setback to approximately 0.15–0.25 mm at the nominal bondline. The ring adds no enclosure height.

Bond the purchased assembly's nonworking face to the seat ceiling, with its working face toward the phone. The tray/base adhesive joint has been removed by consolidating them into one print. Adhesive compatibility, cure procedure and peel/shear retention need sample testing. Do not press-fit a brittle magnet or rely on small printed snap tabs. No additional loose backing ring is specified: the purchased array replaces the old custom attachment system. Removing the old steel ring changes the magnetic environment and requires Hall/RF qualification.

Use `attachment_ring` in `enclosure-parameters.json` to adapt a supplier's complete envelope. The thinner 1 mm Mumbai candidate can retain the same face position by lowering the pocket roof to Z1.50 mm; the printed roof becomes thicker, without a loose shim or taller housing. The earlier nominal-fit study covered the separate-tray revision. Rebuild and recheck a complete candidate if selecting this supplier; it does not qualify polarity or sourcing claims.

Before buying production quantities, request the dimensioned drawing including all carrier/tape layers, tolerance, magnetization/working-face identification, sample quantity, current quote, and delivery to the actual India/US destination. Bench-check fit, attachment peel/shear loads, off-center pressing, Hall angle error and BLE operation with the intended phone/case. No supplier has been contacted and no order has been placed.
