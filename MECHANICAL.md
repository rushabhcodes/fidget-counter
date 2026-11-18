# Enclosure

The current magnet base has a continuous annular wall supporting the bearing shaft. It is one connected solid, printed phone face down without supports. Twenty Ø6.4 mm bottom-entry pockets hold Ø6 × 3 mm axial discs on a Ø49.7 mm pitch circle. A flat annular stop at Z3.4 and a 45° taper to a Ø3.6 mm vent replace closed pocket roofs. Nominal magnet faces sit 0.2 mm behind the phone face.

One selected cap forms the second print. Its keyed 3.4 × 6.4 mm internal slot holds another Ø6 × 3 mm axial disc on edge, with the magnetic axis parallel to the PCB. Nominal Hall clearance is 1.8 mm. Overall height is 20.9 mm; base diameter is 58 mm and circular cap diameter is 61.6 mm.

The 6808-ZZ bearing is 40 × 52 × 7 mm. Nominal printed shaft and housing diameters are 40.05 and 51.95 mm. Calibrate with actual bearings and the generated fit coupons. Require hand-only seating and free rotation. The push fit has no positive axial lock; measure seating, pull-off and creep before using it in a batch.

[enclosure-parameters.json](mechanical/enclosure-parameters.json) defines the base and encoder. [assembly-parameters.json](mechanical/assembly-parameters.json) defines the common bearing, PCB, cell and grip dimensions. [build_enclosure.py](mechanical/build_enclosure.py) builds all eleven cap alternatives and the base from these inputs and current compiled electronic placements. [audit.py](mechanical/audit.py) independently checks stops, vents, solid/mesh integrity, assembly poses and slicer output. All outputs are generated under `dist/mechanical/`.

Print one base and one cap using the [printing guide](mechanical/printing/PRINTING.md). Purchase 21 identical axial N52 magnets, one bearing, one CR2450, two M2 × 4 nylon screws and one populated PCB. See the [order list](mechanical/ORDER_LIST.csv) and [mechanical BOM](mechanical/MECHANICAL_BOM.csv).

## Service

Pull the cap off evenly, supporting the appropriate bearing race if it stays on the base. Avoid transferring force through balls or shields. Remove the two nylon screws and lift the PCB for battery and programming access. Remove the cell before connecting the 3.3 V programmer. Recheck fits and magnet bonds after service; replace damaged or loose parts.
