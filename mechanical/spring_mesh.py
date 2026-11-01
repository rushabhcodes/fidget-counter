"""Lightweight closed preview meshes for nominal purchased compression springs.

STEP retains the swept solid. This analytic mesh avoids excessively dense
OpenCascade triangulation of a thin helical wire in browser previews.
"""
import math


def make_spring_mesh(parameters, press=0):
    spec = parameters['return_springs']
    vertices, faces = [], []
    height = spec['assembled_length_mm'] - press
    wire = spec['wire_mm'] / 2
    radius = spec['outside_mm'] / 2 - wire
    segments, sides = 200, 12
    for angle in spec['angles_deg']:
        cx = spec['radius_mm'] * math.cos(math.radians(angle))
        cy = spec['radius_mm'] * math.sin(math.radians(angle))
        start = len(vertices)
        for i in range(segments + 1):
            theta = 10 * math.pi * i / segments
            center_z = spec['seat_z_mm'] + wire + (height - 2 * wire) * i / segments
            for j in range(sides):
                phi = 2 * math.pi * j / sides
                r = radius + wire * math.cos(phi)
                vertices.append([cx + r * math.cos(theta), cy + r * math.sin(theta), center_z + wire * math.sin(phi)])
        for i in range(segments):
            for j in range(sides):
                a = start + i * sides + j
                b = start + (i + 1) * sides + j
                c = start + (i + 1) * sides + (j + 1) % sides
                d = start + i * sides + (j + 1) % sides
                faces.extend([[a, b, c], [a, c, d]])
        for end in [0, segments]:
            points = vertices[start + end * sides:start + (end + 1) * sides]
            center = [sum(v[axis] for v in points) / sides for axis in range(3)]
            ci = len(vertices)
            vertices.append(center)
            for j in range(sides):
                a, b = start + end * sides + j, start + end * sides + (j + 1) % sides
                faces.append([ci, a, b] if end == 0 else [ci, b, a])
    return vertices, faces
