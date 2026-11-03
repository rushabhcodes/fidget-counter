# CR2450 external height study — not a circuit release

The nominal CAD study fits a CR2450-holder envelope with **0 mm added exterior height**. This assumes a CR2450 cell (24.5 × 5 mm) and MYOUNG BS-24-B4AK014 / C964813 holder. The exact battery and holder selected by the user are still unconfirmed. The active PCB and printable product remain CR2032.

| Measurement | Current CR2032 | CR2450 packaging study | Change |
| --- | ---: | ---: | ---: |
| Phone-contact face to cap top | 17.0 mm | 17.0 mm | **0 mm** |
| CAD cap-top datum | Z17.2 mm | Z17.2 mm | 0 mm |
| Base diameter / maximum cap diameter | 58 / 61.6 mm | 58 / 61.6 mm | 0 mm |
| PCB underside | Z8.1 mm | Z10.6 mm | +2.5 mm internally |
| Encoder magnet underside | Z11.4 mm | Z13.9 mm | +2.5 mm internally |
| Conservative JST-to-cap clearance | 3.88 mm | 1.38 mm | −2.5 mm |

The contact face is at Z0.2 mm; subtract it from the top datum to obtain the physical 17.0 mm height. Raising both the PCB and encoder magnet preserves the supplier-model sensor gap of approximately 1.799 mm (nominally 1.8 mm). The candidate holder clears the floor by approximately 0.49 mm.

The isolated study uses the actual supplier STEP models for all 28 fitted components. The proposed base, threaded nut and common cap hub clear those models. All 11 cap styles retain the same top datum and clear the continuous electronics keepout. The drilled PCB can pass vertically through the proposed base without a collision. These checks prove nominal external packaging, not internal battery seating or printed strength.

This requires a different BT1 footprint, rerouted battery branches, four Ø2.2 mm PCB holes at radius 16.4 mm, revised base posts/bearing webs and a higher encoder pocket in every cap. Those circuit and fabrication changes have **not** been applied to the active product.

The supplier holder's cover solid overlaps the nominal cell volume in its STEP model. Its internal cell/cover seating therefore remains unresolved; the cover has not been removed or edited to manufacture a passing result. Resolve that discrepancy against the supplier drawing and a physical sample before selecting the holder. See the [supplier listing](https://jlcpcb.com/partdetail/MYOUNG-BS_24B4AK014/C964813) and [drawing](https://datasheet.lcsc.com/datasheet/pdf/020fcde92e5545930d8684b3cfed077d.pdf?productCode=C964813).

## Evidence and reproduction

The saved [height report](../validation/cr2450-height-study.json) records all model checks and input SHA256 values. With the pinned Python requirements installed, import C964813 into the ignored `work/assembly-opt/battery-imports/` directory using the existing JLC import workflow. Then run:

```sh
python validation/studies/check-cr2450-height.py
```

The supplier STEP must be at `work/assembly-opt/battery-imports/imports/BS_24_B4AK014/BS_24_B4AK014.step`; compare its SHA256 with the saved report. Outputs are written under `work/larger-battery/holder-placement/`, including the proposed base/cap and an external-packaging STEP assembly. The scripts modify parameters only in memory and generate separate study files.

Before releasing a larger-battery revision: confirm the exact chosen cell/holder, resolve internal seating, implement and validate the revised PCB/routing, validate the finished rigid prints and toolpaths, and test populated physical fit, magnetic sensing, RF, adhesive retention and battery performance. No larger-battery release or runtime improvement is claimed.
