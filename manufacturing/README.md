# 1.0.29 prototype files

- fidget-counter-print-pilot-1.0.29.zip: current base, all11 cap alternatives,10 bearing coupons, matching STEP files, print/assembly instructions and exact print evidence. A unit uses **base+one cap** only. Calibrate coupons first and re-slice for the actual printer. No machine G-code or purchased/display hardware is included.
- fidget-counter-fabrication-1.0.29.zip: exact checked gerbers.zip,28-item BOM, strict supplier CPL, programming instructions and native/Gerber audit evidence. Upload its **inner gerbers.zip** for the board. The SMT assembly includes the C7525448 holder; buy/insert the CR2450 separately. Verify bottom BT1 rotation180°/positive pin1 in the manufacturer's preview.

The manifest gives archive and member SHA256 values. Recreate with `python validation/package-manufacturing.py` after all checks pass. These files support a controlled prototype and fabrication quote. Printed seating/pull-off/creep/adhesion, holder contacts, magnetic/Hall/RF/oscillator behavior and firmware remain physical release gates. No purchase or manufacturing order is implied.

Earlier versioned ZIPs remain available for links in published releases. Use the version and files named in the current manifest for this16.4mm cap.
