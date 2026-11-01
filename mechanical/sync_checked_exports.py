"""Install only a complete, checked V5 CAD build into the distributed folders."""
from pathlib import Path
import json
import shutil


def sync_checked_exports(root, output):
    root, output = Path(root), Path(output)
    report = json.loads((output / 'Validation/geometry.json').read_text())
    expected = {'Stationary_Base', 'Bottom_Tray', 'Bearing_Carrier', 'Inner_Race_Nut', 'Outer_Race_Retainer'}
    expected.update('Cap_' + style for style in report['parameters']['cap_styles'])
    assert {part['name'] for part in report['printed_parts']} == expected, 'Build all grip styles before distributing CAD'
    expected.add('Actuator_Ring_REFERENCE_ONLY')
    for source, target, suffix in [('STL', 'Print_STL', '.stl'), ('STEP', 'STEP_Parts', '.step')]:
        folder = root / target
        folder.mkdir(exist_ok=True)
        for old in folder.glob('*' + suffix):
            if old.stem not in expected:
                old.unlink()
        for name in expected:
            shutil.copyfile(output / source / (name + suffix), folder / (name + suffix))
    shutil.copyfile(output / 'Validation/geometry.json', root / 'enclosure-validation.json')
    audit = {'passed': True, 'physically_tested': False, 'parts': report['printed_parts'],
             'reference_only': ['Actuator_Ring_REFERENCE_ONLY.stl']}
    (root.parent / 'validation/bearing-stl-audit.json').write_text(json.dumps(audit, indent=2) + '\n')


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    sync_checked_exports(root, root / 'export')
    print('Installed checked V5 STLs, STEP parts and validation report')
