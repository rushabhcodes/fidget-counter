"""Check the fitted JST model and its full rotational clearance under every cap."""
from pathlib import Path
import hashlib
import json
import math

import cadquery as cq
import numpy as np
import trimesh

root = Path(__file__).resolve().parents[1]
parameters = json.loads((root / 'mechanical/enclosure-parameters.json').read_text())
circuit_path = root / 'dist/index/circuit.json'
circuit = json.loads(circuit_path.read_text())
source = next(e for e in circuit if e['type'] == 'source_component' and e.get('name') == 'J_DEBUG')
pcb = next(e for e in circuit if e['type'] == 'pcb_component' and e.get('source_component_id') == source['source_component_id'])
cad = next(e for e in circuit if e['type'] == 'cad_component' and e.get('source_component_id') == source['source_component_id'])
assert source['manufacturer_part_number'] == 'SM05B-SRSS-TB(LF)(SN)'
assert pcb['layer'] == 'top' and pcb['rotation'] == 0 and not pcb['do_not_place']
assert cad['rotation'] == {'x': 0, 'y': 0, 'z': 0}
pcb_top = parameters['pcb_bottom'] + parameters['pcb_thickness']
x, y = pcb['center']['x'], pcb['center']['y']
origin = cad['model_origin_position']
step_path = root / cad['model_step_url']
model = cq.importers.importStep(str(step_path)).val().translate(
    (x - origin['x'], y - origin['y'], pcb_top - origin['z']))
box = model.BoundingBox()

# Fill the whole footprint courtyard to a height that also covers the slightly
# taller supplier STEP (2.911 mm) instead of relying on catalog height alone.
width, depth, height = 8.3, 6.1, 2.92
envelope = cq.Workplane('XY').box(width, depth, height).val().translate((x, y, pcb_top + height / 2))
eb = envelope.BoundingBox()
for axis in 'xyz':
    assert getattr(box, axis + 'min') >= getattr(eb, axis + 'min') - 1e-6
    assert getattr(box, axis + 'max') <= getattr(eb, axis + 'max') + 1e-6

base_path = root / 'mechanical/STEP_Parts/Stationary_Base.step'
base = cq.importers.importStep(str(base_path)).val()
base_overlap = envelope.intersect(base).Volume()
assert base_overlap < 1e-6

# The annulus contains the envelope at every rotation angle. Intersecting each
# complete cap with it bounds the minimum height over a continuous 360-degree
# sweep, including all internal reinforcing spokes and the full button stroke.
rmin = abs(y) - depth / 2
rmax = max(math.hypot(a, b) for a in (eb.xmin, eb.xmax) for b in (eb.ymin, eb.ymax))
assert rmin > parameters['pusher_outer_radius']
assert rmax < parameters['bearing']['bore_mm'] / 2
annulus = cq.Workplane('XY').circle(rmax + .001).circle(rmin - .001).extrude(20).val()
reports = []
for style in parameters['cap_styles']:
    cap = cq.importers.importStep(str(root / f'mechanical/STEP_Parts/Cap_{style}.step')).val()
    swept_material = cap.intersect(annulus)
    assert swept_material.Volume() > 0
    floor = swept_material.BoundingBox().zmin - parameters['button_travel']
    gap = floor - eb.zmax
    assert gap > .7, (style, gap)
    reports.append({'style': style, 'pressed_swept_cap_floor_z_mm': floor,
                    'conservative_clearance_mm': gap, 'supplier_step_clearance_mm': floor - box.zmax})
    print(f'{style}: {gap:.3f} mm conservative clearance', flush=True)

# Verify that the actual fitted preview mesh uses the same placement as the STEP.
glb_path = root / 'dist/index/3d.glb'
scene = trimesh.load(glb_path, force='scene')
nodes = [n for n in scene.graph.nodes_geometry if n == 'J_DEBUG' or n.startswith('J_DEBUG_')]
assert nodes, 'Missing fitted JST mesh'
mesh_vertices = []
for node in nodes:
    transform, geometry = scene.graph[node]
    mesh = scene.geometry[geometry].copy()
    mesh.apply_transform(transform)
    mesh_vertices.append(mesh.vertices)
mesh_vertices = np.concatenate(mesh_vertices)
vertices = np.column_stack((-mesh_vertices[:, 0], mesh_vertices[:, 2], mesh_vertices[:, 1] + parameters['pcb_bottom'] + parameters['pcb_thickness'] / 2))
mesh_bounds = np.array([vertices.min(axis=0), vertices.max(axis=0)])
step_bounds = np.array([[box.xmin, box.ymin, box.zmin], [box.xmax, box.ymax, box.zmax]])
assert np.max(np.abs(mesh_bounds - step_bounds)) < .02, (mesh_bounds, step_bounds)

files = [circuit_path, glb_path, step_path, base_path,
         root / 'mechanical/enclosure-parameters.json', root / 'validation/check-jst-fit.py']
files.extend(root / f'mechanical/STEP_Parts/Cap_{style}.step' for style in parameters['cap_styles'])
result = {'passed': True, 'physical_tested': False, 'connector': source['manufacturer_part_number'],
          'placement_mm': [x, y], 'envelope_mm': [width, depth, height],
          'supplier_step_bounds_mm': step_bounds.tolist(), 'preview_mesh_bounds_mm': mesh_bounds.tolist(),
          'base_intersection_mm3': base_overlap, 'continuous_rotation_deg': 360,
          'full_press_travel_mm': parameters['button_travel'], 'cap_checks': reports,
          'minimum_conservative_clearance_mm': min(r['conservative_clearance_mm'] for r in reports),
          'minimum_supplier_step_clearance_mm': min(r['supplier_step_clearance_mm'] for r in reports),
          'service': 'Remove top cap screws, cap, inner nut and bearing; unscrew/lift PCB for side-entry access. Disconnect cable before refitting.',
          'sha256': {str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
(root / 'validation/jst-connector-clearance.json').write_text(json.dumps(result, indent=2) + '\n')
print('Pass: supplier STEP and fitted GLB agree; all eleven caps clear the JST throughout rotation and pressing')
