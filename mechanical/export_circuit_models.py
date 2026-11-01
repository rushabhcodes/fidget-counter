"""Export V5 mechanical models beside the actual native routed PCB."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
from mesh_export import clean_scene_file
from glb_models import write_glb
root=Path(__file__).resolve().parent
models=root/'Circuit_Models';models.mkdir(exist_ok=True)
p=json.loads((root/'enclosure-parameters.json').read_text())
rows=clean_scene_file(root/'export/Validation/scene_meshes.json');selected={}
# Electronics already have their own native tscircuit models.
for m in rows:
 if not m.get('nativeElectronic') and m['name'] not in ['PCB','Holder','Sensor','Button','J_DEBUG']:selected.setdefault(m['name'],m)
assert all('Cap_'+style in selected for style in p['cap_styles']),'Build all grip styles before exporting the selector'
mid=p['pcb_bottom']+p['pcb_thickness']/2
expected={suffix for name in selected for suffix in [name+'.obj',name+'.mtl',name+'.glb']}
for old in models.iterdir():
 if old.suffix in ['.obj','.mtl','.glb'] and old.name not in expected:old.unlink()
for name,m in selected.items():
 obj=['mtllib '+name+'.mtl','o '+name];mtl=[];offset=0
 for i,group in enumerate(m.get('groups',[{'first_face':0,'face_count':len(m['faces']),'color':m['color'],'finish':'plastic'}])):
  material=f'{name}_{i}';finish=group['finish'];specular,shininess={'polished':(.9,180),'steel':(.65,90),'nylon':(.12,18),'rubber':(.05,8),'plastic':(.22,35)}[finish]
  mesh=trimesh.Trimesh(vertices=m['vertices'],faces=m['faces'][group['first_face']:group['first_face']+group['face_count']],process=True)
  smooth=trimesh.graph.smooth_shade(mesh,angle=np.radians(38),facet_minarea=None)
  obj+=['v '+' '.join(f'{x:.7f}' for x in v) for v in smooth.vertices]
  obj+=['vn '+' '.join(f'{x:.7f}' for x in v) for v in smooth.vertex_normals]
  obj+=['usemtl '+material,'s 1']
  obj+=['f '+' '.join(f'{j+offset+1}//{j+offset+1}' for j in f) for f in smooth.faces]
  offset+=len(smooth.vertices)
  mtl+=['newmtl '+material,'Kd '+' '.join(str(x) for x in group['color']),f'Ks {specular} {specular} {specular}',f'Ns {shininess}','d 1','illum 2','endmtl','']
 # Native tscircuit's OBJ loader reads embedded material blocks. Keep the
 # separate MTL too, for conventional CAD/mesh tools.
 (models/(name+'.obj')).write_text('\n'.join(obj+mtl)+'\n')
 (models/(name+'.mtl')).write_text('\n'.join(mtl))
 write_glb(models/(name+'.glb'),m['groups'])
lines=['import {assembly} from "@tscircuit/core"','import {Fragment} from "react"']
for i,name in enumerate(selected):lines.append(f'import obj{i} from "./mechanical/Circuit_Models/{name}.glb"')
lines+=['','export const CAP_STYLE_OPTIONS = '+json.dumps(p['cap_styles'])+' as const','export type CapStyle = typeof CAP_STYLE_OPTIONS[number]','const models = [']
for i,name in enumerate(selected):
 style=name.removeprefix('Cap_') if name.startswith('Cap_') and name.removeprefix('Cap_') in p['cap_styles'] else None
 lines.append('  {name:'+json.dumps(name)+',obj:obj'+str(i)+',mtl:'+json.dumps('./mechanical/Circuit_Models/'+name+'.mtl')+',style:'+json.dumps(style)+'},')
lines += [']','','// V5 bearing carrier and spring return; CAD coordinates are mm from the phone plane.',f'export const PCB_MIDPLANE_Z_MM = {mid}','export const EnclosureAssembly = ({capStyle="circular",transparentShell=false}: {capStyle?:CapStyle;transparentShell?:boolean} = {}) => <Fragment>',
 '  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly',
 '    key={m.name} name={`BEARING_V5_${m.name}`} displayName={m.name.replace(/_/g," ")}',
 '    cadModel={{glbUrl:m.obj,modelUnitToMmScale:1,',
 '      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-PCB_MIDPLANE_Z_MM},',
 '      rotationOffset:{x:0,y:0,z:0},',
 '      showAsTranslucentModel:transparentShell && (m.style !== null || ["Bottom_Tray","Stationary_Base"].includes(m.name)),',
 '    }}/>)}','</Fragment>','']
(root.parent/'enclosure.tsx').write_text('\n'.join(lines))
count=len(selected)-len(p['cap_styles'])+1
(models/'manifest.json').write_text(json.dumps({'assetFormat':'glb','styles':p['cap_styles'],'modelsPerSelectedStyle':count,'totalAssets':len(selected),'pcbMidplaneZMm':mid,'sourceParameters':p,'materialGroups':{name:m['groups'] for name,m in selected.items()},'modelSha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in models.iterdir() if f.suffix=='.glb'},'referenceModelSha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in models.iterdir() if f.suffix in ['.obj','.mtl']}},indent=2)+'\n')
print(f'Created V5 selector: {len(selected)} assets, {count} per selected style, PCB midplane Z{mid} mm.')
