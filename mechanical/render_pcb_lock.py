"""Render the real latch section and the revised PCB-hole pattern."""
from pathlib import Path
import json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
import trimesh
from pcb_snap_mounts import make_pcb_mounts

root=Path(__file__).resolve().parent
p=json.loads((root/'enclosure-parameters.json').read_text());spec=p['pcb_mount']
mounts=[(spec['radius_mm']*math.cos(math.radians(t)),spec['radius_mm']*math.sin(math.radians(t))) for t in spec['angles_deg']]
posts,pairs,audit=make_pcb_mounts(p,mounts);x,y=mounts[0]
def section(shape):
    local=shape.translate((-x,-y,0)).rotate((0,0,0),(0,0,1),-45)
    vertices,faces=local.tessellate(.012,.04)
    mesh=trimesh.Trimesh(vertices=[v.toTuple() for v in vertices],faces=faces,process=True)
    return mesh.section(plane_origin=[0,0,0],plane_normal=[0,1,0]).discrete

fig,(ax,plan)=plt.subplots(1,2,figsize=(13.5,8),gridspec_kw={'width_ratios':[1.15,1]})
fig.subplots_adjust(bottom=.18,top=.86,left=.06,right=.97,wspace=.28)
for line in section(posts[0]):ax.fill(line[:,0],line[:,2],color='#dbe2e8',edgecolor='#344557',linewidth=1.6,zorder=2)
for line in section(pairs[0][1]):ax.plot(line[:,0],line[:,2],color='#00889a',linestyle='--',linewidth=1.4,zorder=4)
hole=spec['hole_diameter_mm']/2
for left,right in [(-3.2,-hole),(hole,3.2)]:
    ax.add_patch(Rectangle((left,p['pcb_bottom']),right-left,p['pcb_thickness'],facecolor='#78b894',edgecolor='#245d3b',linewidth=1.4,zorder=3))
ax.annotate('Retaining lip is 0.15 mm\nabove the PCB',xy=(-1.7,8.25),xytext=(-3.1,10.1),arrowprops={'arrowstyle':'->','lw':1.1},fontsize=10)
ax.annotate('Push outward 0.6 mm\nto release',xy=(.05,8.7),xytext=(.25,9.65),arrowprops={'arrowstyle':'->','color':'#00889a','lw':1.2},color='#007a8a',fontsize=10)
ax.annotate('Stem occupies the drilled hole;\nno plastic crosses the FR4',xy=(-.85,7.5),xytext=(-3.2,5.75),arrowprops={'arrowstyle':'->','lw':1.1},fontsize=10,bbox={'facecolor':'white','edgecolor':'none','alpha':.9})
ax.text(.5,4.8,'Support\nshoulder',fontsize=10)
ax.set(xlim=(-3.4,3.4),ylim=(1.2,10.8),xlabel='Local radial position (mm) — outward →',ylabel='Case Z (mm)')
ax.set_aspect('equal');ax.grid(alpha=.15);ax.spines[['top','right']].set_visible(False)
ax.set_title('Latch section — no bolts',loc='left',fontsize=14,pad=14)
plan.add_patch(Circle((0,0),p['pcb_diameter']/2,facecolor='#e8f4ed',edgecolor='#276445',linewidth=1.6))
for (xx,yy),angle in zip(mounts,spec['angles_deg']):
    t=math.radians(angle)
    plan.add_patch(Circle((16.2*math.cos(t),16.2*math.sin(t)),1.8,fill=False,edgecolor='#af7d78',linestyle='--',linewidth=1.1))
    plan.add_patch(Circle((xx,yy),hole,facecolor='white',edgecolor='#245d3b',linewidth=1.5))
plan.plot([0,mounts[0][0]],[0,mounts[0][1]],color='#00889a',linewidth=1)
plan.text(4,4,'R15.2 mm',rotation=45,color='#007a8a',fontsize=10)
plan.text(0,-1,'4 × Ø3.0 mm holes\n1.0 mm inward radially',ha='center',va='center',fontsize=12,linespacing=1.8)
plan.text(0,-21,'Edge web: 0.25 → 1.55 mm nominal\nDashed: previous holes',ha='center',fontsize=10,linespacing=1.8)
plan.set(xlim=(-21,21),ylim=(-24,21));plan.set_aspect('equal');plan.axis('off')
plan.set_title('Actual PCB hole pattern',loc='left',fontsize=14,pad=14)
fig.text(.5,.075,'Solid: retained position     Dashed blue: release pose\nTwo recessed locating posts support the other two holes; no fitted hardware.',ha='center',fontsize=10,linespacing=1.6)
fig.text(.5,.025,'Nominal CAD. Printed fit, insertion force and latch fatigue still require a prototype.',ha='center',fontsize=9,color='#526171')
out=root.parent/'previews/pcb-automatic-lock.png';out.parent.mkdir(exist_ok=True)
fig.savefig(out,dpi=180,bbox_inches='tight');print(out)
