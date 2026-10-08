"""Render the exported bottom-cover solid and audited disc pocket coordinates."""
from pathlib import Path
import argparse
import json
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('cad_output',type=Path)
ap.add_argument('output',type=Path)
args=ap.parse_args()
audit=json.loads((args.cad_output/'Validation/geometry_checks.json').read_text())
p=audit['parameters_mm']; layout=audit['attachment_disc_array']
solid=cq.importers.importStep(str(args.cad_output/'STEP_Parts/Bottom_Cover.step')).val()
vertices,faces=solid.tessellate(0.04,0.08)
points=np.array([[v.x,v.y,v.z] for v in vertices])
triangles=points[np.asarray(faces)]
normals=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-9)
shade=.55+.45*np.abs(normals@np.array([.25,-.25,.93]))
colors=shade[:,None]*np.array([.36,.48,.56])
fig=plt.figure(figsize=(12,6.2),facecolor='#f7f8fa')
ax=fig.add_axes([.015,.20,.48,.64],projection='3d',facecolor='#f7f8fa')
ax.add_collection3d(Poly3DCollection(triangles,facecolors=colors,edgecolors='none'))
ax.set(xlim=(-31,31),ylim=(-31,31),zlim=(0,8))
ax.set_box_aspect((62,62,10)); ax.view_init(elev=58,azim=-50); ax.set_axis_off()
plan=fig.add_axes([.52,.20,.45,.64],facecolor='#f7f8fa')
plan.add_patch(Circle((0,0),p['attachment_flange_diameter']/2,facecolor='#d8e0e6',edgecolor='#405865',lw=1.5))
plan.add_patch(Circle((0,0),p['body_diameter']/2,facecolor='#edf0f4',edgecolor='#405865',lw=.8))
plan.add_patch(Circle((0,0),12.25,facecolor='#f7f8fa',edgecolor='#405865',lw=1))
for x,y in audit['hatch_mounts_mm']:
    plan.add_patch(Circle((x,y),2.25,facecolor='#f7f8fa',edgecolor='#405865',lw=.7))
plan.add_patch(Circle((0,0),layout['pitch_circle_diameter_mm']/2,fill=False,ls='--',edgecolor='#65818f',lw=.8))
for c in layout['centers_mm']:
    x,y=c['x'],c['y']
    plan.add_patch(Circle((x,y),layout['pocket_diameter_mm']/2,facecolor='white',edgecolor='#147f93',lw=1.3))
    r=layout['pitch_circle_diameter_mm']/2
    plan.text(x/r*19.1,y/r*19.1,str(c['index']),ha='center',va='center',fontsize=6.5,color='#314b59')
plan.text(0,0,'Battery hatch\nopening',ha='center',va='center',fontsize=10,color='#405865')
plan.set(xlim=(-32,32),ylim=(-32,32));plan.set_aspect('equal');plan.axis('off')
fig.text(.035,.91,'Bottom cover with magnet tray',fontsize=18,weight='bold',color='#203746')
fig.text(.535,.91,'24 pockets · Ø5 × 1.5 mm discs',fontsize=18,weight='bold',color='#203746')
fig.text(.035,.86,'Inside face · actual exported STEP geometry',fontsize=10,color='#526a78')
fig.text(.535,.86,f"Ø{layout['pitch_circle_diameter_mm']:.2f} mm pitch circle · 15° spacing",fontsize=10,color='#526a78')
fig.text(.035,.12,'Pockets Ø5.25 × 1.55 mm · adhesive allowance 0.05 mm · floor 0.60 mm',fontsize=11,color='#203746')
fig.text(.035,.075,f"Minimum web {layout['minimum_pocket_web_mm']:.3f} mm · use the revised housing and cover together",fontsize=10,color='#526a78')
fig.text(.035,.035,'Check axial polarity and phone attraction before gluing. Holding force and Hall bias require a prototype test.',fontsize=9,color='#526a78')
args.output.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(args.output,dpi=160)
plt.close(fig)
print(args.output)
