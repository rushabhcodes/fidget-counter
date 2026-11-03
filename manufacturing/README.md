# 1.0.31 prototype files

The new individual-magnet base is a separate **V2 fit/force-test alternative**, with the previous premade-ring base preserved as **V1**. These layouts share the existing cap, bearing and27-component PCB. Neither is physically production-qualified, and V2 holding-force equivalence is unverified.

- [V1 preserved base](fidget-counter-V1-preserved-base-1.0.31.zip): original base STEP/STL, frozen source/parameters, preview and source-commit/SHA manifest.
- [V2 print test](fidget-counter-V2-magnets-print-test-1.0.31.zip): new base and pocketed carrier, all11 unchanged cap alternatives, fit coupons, assembly/polarity instructions and actual geometry/slicer evidence. Print **base+carrier+one cap** only. The standalone carrier uses a0.15 mm first layer to make its0.3 mm floor two layers.
- [V2 exact CAD](fidget-counter-V2-magnets-CAD-1.0.31.zip): complete assembled/exploded STEP, standalone assembled GLB and custom steel backing STEP/DXF. Reference assemblies and purchased/fabricated parts are **not** rigid print jobs. Use the V2 BOM;36 small magnets and low-carbon steel backing replace the premade magnetic ring.
- `magnet-variants-manifest.json` binds all three archives and their members to hashes. Recreate with `python validation/package-magnet-variants.py` after the V2 builder and slicer audit pass. Full STEP assemblies are generated locally and delivered compressed in the CAD ZIP to avoid storing two57 MB copies as loose Git/registry files.

- fidget-counter-print-pilot-1.0.31.zip: **V1** base, all11 cap alternatives,10 bearing coupons, matching STEP files, print/assembly instructions and exact print evidence. A V1 unit uses **base+one cap** only. Calibrate coupons first and re-slice for the actual printer. No machine G-code or purchased/display hardware is included.
- fidget-counter-fabrication-1.0.31.zip: unchanged, corrected1.0.30 PCB/Gerbers,27-item BOM, strict supplier CPL, programming instructions and native/Gerber audit evidence. Upload its **inner gerbers.zip** for the board. The SMT assembly includes the C7525448 holder; buy/insert the CR2450 separately. Verify bottom BT1 rotation180°/positive pin1 in the manufacturer's preview.

The manifest gives archive and member SHA256 values. Recreate with `python validation/package-manufacturing.py` after all checks pass. These files support a controlled prototype and fabrication quote. Printed seating/pull-off/creep/adhesion, holder contacts, magnetic/Hall/RF/oscillator behavior and firmware remain physical release gates. No purchase or manufacturing order is implied.

Earlier versioned ZIPs remain available for links in published releases. Use the version and files named in the current manifest for this16.4mm cap.

The corrected 1.0.30 PCB files supersede the DEC2/DEC3 and RF-return wiring in earlier bundles. Do not order the older PCB files. See validation/AI_REVIEW_RESOLUTION.md in this branch and the fabrication bundle. RF and printed-retention qualification remain open.
