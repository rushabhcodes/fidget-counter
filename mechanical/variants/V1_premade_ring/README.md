# V1 — preserved premade-ring base

Frozen from commit `6a3be158ec28513a15d348b5957a9a1a7c072228` (release 1.0.30). `Base_V1_Premade_Ring.stl` is the original bed-oriented print, and the STEP is its assembly-coordinate source. The supplied SHA256 manifest identifies the exact originals, parameters and supplier STEP dependencies. V1 takes the purchased 54 × 45.8 × 1.9 mm ring; it does **not** take the V2 carrier.

The physical height is 16.4 mm and the nominal encoder gap is 1.8 mm. Use the existing cap, 6808-ZZ bearing, two PCB screws and assembly instructions. Physical retention, adhesive, sensing and RF qualification remain open.

For regeneration, use a separate checkout of the source commit, install `mechanical/requirements.txt`, and run `python mechanical/build_enclosure.py --assembly-style circular`. The frozen source here also records the generating implementation; it is not intended to run in-place because its project-relative supplier imports belong to the original checkout. Do not overwrite this archive when building V2.
