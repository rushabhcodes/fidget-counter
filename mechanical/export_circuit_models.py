"""Export V5 mechanical models beside the actual native routed PCB."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parent
models=root/'Circuit_Models';models.mkdir(exist_ok=True)
p=json.loads((root/'enclosure-parameters.json').read_text())
rows=json.loads((root/'export/Validation/scene_meshes.json').read_text());selected={}
# Electronics already have their own native tscircuit models.
for m in rows:
 if m['name'] not in ['PCB','Holder','Sensor','Button','J_DEBUG']:selected.setdefault(m['name'],m)
mid=p['pcb_bottom']+p['pcb_thickness']/2
expected={suffix for name in selected for suffix in [name+'.obj',name+'.mtl']}
for old in models.iterdir():
 if old.suffix in ['.obj','.mtl'] and old.name not in expected:old.unlink()
for name,m in selected.items():
 (models/(name+'.obj')).write_text('mtllib '+name+'.mtl\no '+name+'\n'+''.join('v '+' '.join(f'{x:.7f}' for x in v)+'\n' for v in m['vertices'])+'usemtl '+name+'\ns off\n'+''.join('f '+' '.join(str(i+1) for i in f)+'\n' for f in m['faces']))
 (models/(name+'.mtl')).write_text('newmtl '+name+'\nKd '+' '.join(str(x) for x in m['color'])+'\nKs 0.15 0.15 0.15\nNs 20\nd 1\n')
lines=['import {assembly} from "@tscircuit/core"','import {Fragment} from "react"']
for i,name in enumerate(selected):lines.append(f'import obj{i} from "./mechanical/Circuit_Models/{name}.obj"')
lines+=['','export const CAP_STYLE_OPTIONS = '+json.dumps(p['cap_styles'])+' as const','export type CapStyle = typeof CAP_STYLE_OPTIONS[number]','const models = [']
for i,name in enumerate(selected):
 style=name.removeprefix('Cap_') if name.startswith('Cap_') and name.removeprefix('Cap_') in p['cap_styles'] else None
 lines.append('  {name:'+json.dumps(name)+',obj:obj'+str(i)+',mtl:'+json.dumps('./mechanical/Circuit_Models/'+name+'.mtl')+',style:'+json.dumps(style)+'},')
lines += [']','','// V5 bearing carrier and spring return; CAD coordinates are mm from the phone plane.',f'export const PCB_MIDPLANE_Z_MM = {mid}','export const EnclosureAssembly = ({capStyle="circular"}: {capStyle?:CapStyle} = {}) => <Fragment>',
 '  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly',
 '    key={m.name} name={`BEARING_V5_${m.name}`} displayName={m.name.replace(/_/g," ")}',
 '    cadModel={{objUrl:m.obj,mtlUrl:m.mtl,modelUnitToMmScale:1,',
 '      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-PCB_MIDPLANE_Z_MM},',
 '      rotationOffset:{x:0,y:0,z:0},',
 '      showAsTranslucentModel:m.style !== null || ["Bottom_Tray","Stationary_Base"].includes(m.name),',
 '    }}/>)}','</Fragment>','']
(root.parent/'enclosure.tsx').write_text('\n'.join(lines))
count=len(selected)-len(p['cap_styles'])+1
(models/'manifest.json').write_text(json.dumps({'styles':p['cap_styles'],'modelsPerSelectedStyle':count,'totalAssets':len(selected),'pcbMidplaneZMm':mid,'sourceParameters':p,'modelSha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in models.iterdir() if f.suffix in ['.obj','.mtl']}},indent=2)+'\n')
print(f'Created V5 selector: {len(selected)} assets, {count} per selected style, PCB midplane Z{mid} mm.')
