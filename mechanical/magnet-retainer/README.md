# Glue-on magnet retainer — 58 mm base

**Using the reverse-loading disc and M2 mounts? Follow [base revision 2](../base-rev2/README.md) instead.** Its open magnet holes require this closing plate, and its assembly exports/checks include the revised housing. The reference assembly and floor checks on this page apply to the original closed-floor base.

This separate, continuous **Ø58 × 0.60 mm plate** glues beneath the fixed base to cover the attachment-magnet ring. It has a flat bonding face, no holes, and a 0.15 mm bevel on the phone-facing edge. It has no raised locating rim that could enter the rotating cap's clearance.

The saved `Bottom_Cover` already has a 0.60 mm solid floor beneath all 24 Ø5 × 1.5 mm magnets. This part is an **additional protective retainer**, useful when reinforcing that floor or covering exposed pockets on a matching print. It cannot compensate for a detached housing-to-cover joint; check that joint too. CAD checks apply to the saved enclosure, not an unidentified older print.

Files in `export/`:

- `Magnet_Retainer_58mm.stl`: print one; flat phone face on the bed, glue face upward, already at Z=0.
- `Magnet_Retainer_58mm.step`: editable solid in the same print coordinates.
- `Retainer_Installed_Reference.step`: existing fixed housing, cover, magnets and backing ring with the new plate, a nominal glue layer and relocated protective film. Only the retainer STL is a new printable part.
- `retainer-preview.png`: exploded view and section diagram.
- `geometry-checks.json`: solid, mesh, magnet coverage and interference checks.

Print flat in the same rigid material as the base, at **0.20 mm layer height, 100% solid, with no supports or brim touching the bonding surface**. The 0.60 mm plate is three layers thick. Keep the glue face flat and free of first-layer flare or raised lettering. The small underside bevel does not reduce thickness beneath the magnet footprints.

## Fitting

1. Remove the device from the phone. Confirm the base diameter is 58 mm and that the existing cover is securely attached to the stationary housing. Seat any loose magnets completely in their pockets and verify phone attraction before closing them in.
2. Remove the existing protective film or pad from the underside. The plate must bond directly to the rigid stationary base, not to a flexible pad. Dry-fit and center the plate by matching the 58 mm edges. Check free rotation and full cap press travel.
3. Prepare clean, dry, flat bonding faces according to the adhesive manufacturer's directions. Apply a thin film of plastic-compatible cyanoacrylate super glue to the fixed plastic mating surface. If the printed version has exposed pockets, bond the plastic lands between and around the pockets too; the cover must be attached to the base, not just to the magnets. Keep glue away from the moving cap. The CAD allowance is 0.05 mm, not a controlled bond thickness.
4. Hold the plate flat and centered while the bond sets, and allow the adhesive's full specified cure before phone attachment. Refit a protective film or pad on the new phone-facing side. Ensure the plate and pad cannot rub the rotating cap.
5. Test over a soft surface with gradual pull-off and edge-peel loads, then repeated attachment/removal. Check for lifting edges or loose magnets, and confirm phone holding, sliding and rotation resistance before relying on it.

With the original 0.20 mm protective pad relocated, the nominal added separation is **0.65 mm** (0.60 mm plate + 0.05 mm glue). Overall height becomes **14.65 mm** for the saved 14.0 mm enclosure. The extra magnet-to-phone gap can reduce holding force; the amount has not been measured. A thicker pad or glue layer adds further separation. This is a prototype; retention strength and physical print fit are untested.

## Regeneration

Use Python with CadQuery ≥2.6, trimesh, numpy and matplotlib:

```sh
python mechanical/magnet-retainer/generate.py
```

Edit `parameters.json` to change plate thickness or edge bevel, then regenerate and recheck the exported artifacts. The original enclosure STEP files and parameters are read without modification.
