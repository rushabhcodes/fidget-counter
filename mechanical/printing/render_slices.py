"""Inspect actual audited G-code paths; no inferred or illustrated toolpaths."""
from pathlib import Path
import json,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'work/print-readiness'
report=json.loads((ROOT/'validation/print-readiness.json').read_text())
parts={p['name']:p for p in report['parts']}

# Carrier supports must not be generated inside the three finished guide bores.
name='Bearing_Carrier';rows=json.loads((OUT/(name+'-paths.json')).read_text());p=parts[name]
bounds=np.asarray(p['bounds_mm']);shift=np.array([110,110])-(bounds[0,:2]+bounds[1,:2])/2
supports=np.asarray([[*r[:4],r[4]] for r in rows if r[5].startswith('Support material')])
assert len(supports)>0
clearances=[]
for angle in [0,105,255]:
 t=math.radians(angle);center=np.array([16.5*math.cos(t),16.5*math.sin(t)])+shift
 aa=supports[:,:2];bb=supports[:,2:4];ab=bb-aa
 fraction=np.clip(np.sum((center-aa)*ab,axis=1)/np.maximum(np.sum(ab*ab,axis=1),1e-12),0,1)
 distance=np.linalg.norm(aa+ab*fraction[:,None]-center,axis=1)
 # Positive clearance includes the 0.2 mm half width of a support bead.
 clearance=float(distance.min()-2.65-.2)
 assert clearance>0,(angle,'Support touches guide bore',clearance)
 clearances.append({'guide_angle_deg':angle,'support_bead_to_bore_clearance_mm':clearance})
assert p['maximum_support_z_mm']<4,'Support entered upper bearing shaft/thread region'
(ROOT/'validation/print-support-clearance.json').write_text(json.dumps({'passed':True,'physical_tested':False,'method':'Actual G-code line-segment distances including0.2mm support bead radius vs guide bores; source STL bounding-box centering matches CLI--center','carrier_guide_support_clearances':clearances,'maximum_carrier_support_z_mm':p['maximum_support_z_mm'],'limits':['Cleanup and actual printer extrusion width remain physical checks']},indent=2)+'\n')

fig,axes=plt.subplots(3,3,figsize=(18,15),layout='constrained')
cases=[('Stationary_Base',.2,'Base first layer'),('Stationary_Base',2.3,'Base supported roof'),('Bearing_Carrier',2.15,'Carrier shoulder'),('Inner_Race_Nut',1.7,'Nut notch roof'),('Outer_Race_Retainer',1.7,'Retainer bosses'),('Cap_circular',4.7,'Default cap bearing housing'),('Cap_four_leaf_clover',1.85,'Noncircular cap supported rim'),('Cap_thumb_scoop',9.05,'Thumb cap supported interior'),('Nest_Left',12.2,'Fixture support finger')]
colors={'model':'#167d96','support':'#e99425','bridge':'#c94745'}
for ax,(name,target,title) in zip(axes.flat,cases):
 rows=json.loads((OUT/(name+'-paths.json')).read_text())
 model=[r for r in rows if r[5] not in ['Skirt/Brim','Custom'] and not r[5].startswith('Support material')]
 layer=min({r[4] for r in model},key=lambda z:abs(z-target))
 support=[r for r in rows if r[5].startswith('Support material') and r[4]<=layer]
 support_z=max([r[4] for r in support if r[4]<=layer-.1],default=-1)
 for category in ['support','model','bridge']:
  selected=[r for r in rows if (abs(r[4]-support_z)<.001 and r[5].startswith('Support material'))] if category=='support' else [r for r in model if abs(r[4]-layer)<.001 and ((r[5]=='Bridge infill')==(category=='bridge'))]
  segments=[[[r[0],r[1]],[r[2],r[3]]] for r in selected]
  if segments:ax.add_collection(LineCollection(segments,colors=colors[category],linewidths=.65 if category=='support' else .8,alpha=.7 if category=='support' else 1))
 ax.autoscale();ax.set_aspect('equal');ax.set_title(f'{title}\nmodel Z{layer:.2f} mm; support projected from Z{support_z:.2f}' if support_z>=0 else f'{title}\nmodel Z{layer:.2f} mm; no lower support')
 if name=='Nest_Left':ax.set_xlim(110,120);ax.set_ylim(132,143)
 ax.set_xlabel('X / mm');ax.set_ylabel('Y / mm');ax.grid(alpha=.12)
fig.suptitle('Actual PrusaSlicer 2.8.1 paths | teal: model, orange: lower support, red: bridge-labelled infill\nGeneric 0.4 mm PETG audit; re-slice for actual printer. Supported bridge labels do not mean a free unsupported span.',fontsize=13)
dest=ROOT/'previews/print-slice-inspection.png';fig.savefig(dest,dpi=160);print(dest)
