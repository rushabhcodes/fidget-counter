"""Render actual B-rep meshes and a dimensioned underside plan."""
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def render(out, disc, housing, plate, inserts, old, p):
    bg, ink, gray, teal = "#f5f4ef", "#18353d", "#53666c", "#138c8c"
    fig = plt.figure(figsize=(14, 9), facecolor=bg)
    fig.text(.045, .94, "Reverse-loading magnetic base", fontsize=23, weight="bold", color=ink)
    fig.text(.045, .90, "24 press-fit pockets from the phone side  /  Four M2 heat-set insert mounts", fontsize=13, color=gray)

    def mesh(ax, shape, rgb):
        vertices, faces = shape.tessellate(.05, .08)
        points = np.array([[v.x, v.y, v.z] for v in vertices])
        triangles = points[np.asarray(faces)]
        n = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        n /= np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-9)
        shade = .58 + .42 * np.abs(n @ np.array([.25, -.45, .85]))
        ax.add_collection3d(Poly3DCollection(triangles, facecolors=shade[:, None] * np.array(rgb), edgecolors="none"))

    ax = fig.add_axes([.015, .37, .49, .44], projection="3d", facecolor=bg)
    # Turn over the physical parts so the new loading faces are visible.
    mesh(ax, housing.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, 22)), (.55, .63, .67))
    mesh(ax, inserts.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, 22)), (.80, .57, .20))
    mesh(ax, disc.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, 8)), (.14, .59, .64))
    mesh(ax, plate, (.12, .58, .53))
    ax.set(xlim=(-32, 32), ylim=(-32, 32), zlim=(-2, 24))
    ax.set_box_aspect((64, 64, 40))
    ax.view_init(elev=30, azim=-55)
    ax.set_axis_off()
    fig.text(.045, .825, "Actual CAD · underside exploded view", fontsize=12, weight="bold", color=ink)
    fig.text(.045, .35, "Gray: revised housing   /   Brass: M2 insert references", fontsize=10, color=gray)
    fig.text(.045, .315, "Blue: reverse-loading disc   /   Green: glue-on retainer", fontsize=10, color=gray)

    plan = fig.add_axes([.54, .405, .41, .39], facecolor=bg)
    plan.add_patch(Circle((0, 0), 29, facecolor="#dfe6e6", edgecolor=ink, lw=1.2))
    plan.add_patch(Circle((0, 0), 21, facecolor=bg, edgecolor="#9aaeb2", lw=.8))
    for c in old["attachment_centers"]:
        plan.add_patch(Circle((c["x"], c["y"]), p["magnet_pocket_diameter"] / 2,
                              facecolor="white", edgecolor=teal, lw=1.2))
    for x, y in old["mounts"]:
        plan.add_patch(Circle((x, y), p["boss_diameter"] / 2, facecolor="#cfab64", edgecolor="#94722f"))
        plan.add_patch(Circle((x, y), p["insert_hole_diameter"] / 2, facecolor="white", edgecolor="#94722f"))
    plan.text(0, 0, "58 mm base\nMount centres unchanged", ha="center", va="center", fontsize=10, color=ink)
    plan.set(xlim=(-33, 33), ylim=(-33, 33), aspect="equal")
    plan.axis("off")
    fig.text(.54, .825, "Phone-side plan · housing and disc overlaid", fontsize=12, weight="bold", color=ink)

    fig.text(.54, .35, "Ø4.95 mm pockets for Ø5 mm magnets", fontsize=14, weight="bold", color=ink)
    fig.text(.54, .31, "0.05 mm nominal interference · Ø5.35 mm lead-in", fontsize=11, color=gray)
    fig.text(.54, .265, "M2 inserts: Ø3.6 × 3.0 mm", fontsize=14, weight="bold", color=ink)
    fig.text(.54, .225, "Ø3.2 × 4.1 mm pockets · Ø6.2 mm lower bosses", fontsize=11, color=gray)
    fig.text(.045, .205, "Load from below, then close with the retainer.", fontsize=15, weight="bold", color=ink)
    fig.text(.045, .155, "Heat-set inserts first → bond disc and backing ring → press magnets → glue retainer → fit pad", fontsize=11, color=gray)
    fig.text(.045, .10, "Use the included fit coupons before assembling. M2 × 10 countersunk screws replace the four M1.6 screws.", fontsize=11, color=gray)
    fig.text(.045, .055, "CAD checks cover released/pressed states and PCB removal. Actual printed fit, heat setting and retention strength remain untested.", fontsize=10, color=gray)
    fig.savefig(out / "base-rev2-preview.png", dpi=160, facecolor=bg)
    plt.close(fig)
