"""Dimensioned YZ sections from the actual old STEP and current CAD meshes."""
from pathlib import Path
import json,subprocess
import numpy as np
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1];BASE='b300e196ec7e3ff56dc7dc9638462b9cf52ab772'
P=json.loads((R/'mechanical/enclosure-parameters.json').read_text())
rows={row['name']:row for row in json.loads((R/'mechanical/export/Validation/scene_meshes.json').read_text())}
oldfile=R/'work/compact-baseline/Cap_circular.step'
oldfile.parent.mkdir(parents=True,exist_ok=True)
oldfile.write_bytes(subprocess.check_output(['git','show',BASE+':mechanical/STEP_Parts/Cap_circular.step'],cwd=R))
v,f=cq.importers.importStep(str(oldfile)).val().tessellate(.02,.07)
old=trimesh.Trimesh(vertices=[q.toTuple()for q in v],faces=f,process=True)
def mesh(name):
 row=rows[name];return trimesh.Trimesh(vertices=row['vertices'],faces=row['faces'],process=True)
def section(ax,m,color,label=None,style='-',width=1.):
 path=m.section(plane_origin=[0,0,0],plane_normal=[1,0,0])
 if path is None:return
 for i,line in enumerate(path.discrete):
  ax.plot(line[:,1],line[:,2]-.2,style,color=color,lw=width,label=label if i==0 else None)
def dimension(ax,x,z1,z2,label,color='#243342',offset=.6):
 ax.annotate('',xy=(x,z1-.2),xytext=(x,z2-.2),arrowprops={'arrowstyle':'<->','color':color,'lw':1.0})
 ax.text(x+offset,(z1+z2)/2-.2,label,color=color,va='center',fontsize=9)
fig,(a,b)=plt.subplots(1,2,figsize=(13,4.6),gridspec_kw={'width_ratios':[2.3,1]})
for ax in [a,b]:
 for name,color in [('Stationary_Base','#6e7d85'),('Cell','#8d9297'),('Bearing_6808','#a9aeb3'),('MagSafe_Ring','#bf8c49'),('PCB','#398466'),('Electronic_J_DEBUG','#b78743'),('Electronic_U2','#403c38'),('Magnet','#91619c')]:
  section(ax,mesh(name),color)
 section(ax,old,'#87919b','Previous cap','--',1.1)
 section(ax,mesh('Cap_circular'),'#087f95','Compact cap','-',1.7)
 ax.axhline(0,color='#b6c0c9',lw=.7);ax.set_xlabel('CAD Y (mm)');ax.set_ylabel('Height above phone-contact face (mm)')
 ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.12)
a.set(xlim=(-35,35),ylim=(-.8,20),title='Actual CAD section: 0.6 mm lower shell')
a.set_aspect('equal',adjustable='box');a.legend(loc='upper right',frameon=False,fontsize=9)
dimension(a,-32,.2,17.2,'17.0 mm',color='#87919b',offset=.8)
dimension(a,30,.2,P['overall_height'],'16.4 mm',offset=-7.2)
sensor_top=max(p[2]for p in rows['Electronic_U2']['vertices'])
assert abs(P['magnet_bottom']-sensor_top-1.799)<1e-6
dimension(a,5.5,sensor_top,P['magnet_bottom'],'1.8 mm gap\nunchanged')
a.annotate('Encoder magnet',xy=(0,14.65-.2),xytext=(-8,18.2),fontsize=9,ha='center',arrowprops={'arrowstyle':'-','color':'#91619c'},color='#70497a')
b.set(xlim=(-18,-8.5),ylim=(10.5,18),title='Programming connector clearance')
b.set_aspect('equal',adjustable='box')
dimension(b,-10.2,14.52,15.3,'0.78 mm',offset=-4.8)
b.text(-17.7,17.4,'Magnet and sensor keep\ntheir original world positions.',fontsize=9,color='#243342')
fig.suptitle('RevC compact cap | unchanged base, bearing, PCB and magnetic interfaces',fontsize=13,color='#243342')
fig.tight_layout()
out=R/'previews/compact-cap-section.png';fig.savefig(out,dpi=180,bbox_inches='tight',facecolor='white')
print('Rendered actual old/new CAD sections:',out)
