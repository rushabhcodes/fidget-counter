"""Export a tscircuit component with interchangeable capStyle options."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
out=root;models=out/'Circuit_Models';models.mkdir(parents=True,exist_ok=True)
rows=json.loads((root/'export/Validation/scene_meshes.json').read_text());selected={}
for m in rows:
    if m['name'] not in ['PCB','Holder','Sensor','Button']:selected.setdefault(m['name'],m)
assert len(selected)==18 and 'Button_Actuator_Reference' not in selected
assert 'PCB_Retainers' not in selected and 'Encoder_Spacer' in selected
for name,m in selected.items():
    obj=models/(name+'.obj');mtl=models/(name+'.mtl')
    obj.write_text('mtllib '+name+'.mtl\no '+name+'\n'+''.join('v '+' '.join(f'{x:.7f}' for x in v)+'\n' for v in m['vertices'])+'usemtl '+name+'\ns off\n'+''.join('f '+' '.join(str(i+1) for i in f)+'\n' for f in m['faces']))
    mtl.write_text('newmtl '+name+'\nKd '+' '.join(str(x) for x in m['color'])+'\nKs 0.15 0.15 0.15\nNs 20\nd 1\n')
lines=['import {assembly} from "@tscircuit/core"','import {Fragment} from "react"']
for i,name in enumerate(selected):lines.append(f'import obj{i} from "./Circuit_Models/{name}.obj"')
lines += ['','export type CapStyle = "circular" | "ships_wheel" | "rounded_triangle" | "scalloped_coin" | "petal_flower" | "four_leaf_clover" | "rounded_hexagon" | "rounded_square" | "wave_rim" | "turbine_wheel" | "thumb_scoop"','export const CAP_STYLE_OPTIONS = ["circular", "ships_wheel", "rounded_triangle", "scalloped_coin", "petal_flower", "four_leaf_clover", "rounded_hexagon", "rounded_square", "wave_rim", "turbine_wheel", "thumb_scoop"] as const','const models = [']
for i,name in enumerate(selected):
    style=name.removeprefix('Cap_') if name in ['Cap_circular', 'Cap_ships_wheel', 'Cap_rounded_triangle', 'Cap_scalloped_coin', 'Cap_petal_flower', 'Cap_four_leaf_clover', 'Cap_rounded_hexagon', 'Cap_rounded_square', 'Cap_wave_rim', 'Cap_turbine_wheel', 'Cap_thumb_scoop'] else None
    lines.append('  {name:'+json.dumps(name)+',obj:obj'+str(i)+',mtl:'+json.dumps('./Circuit_Models/'+name+'.mtl')+',style:'+('null' if style is None else json.dumps(style))+'},')
lines += [']','','// Each top is an integral rotor/grip/pusher; all tops share the snap base.','// CAD coordinates are mm from the phone plane; PCB midplane is at Z=7.6 mm.','export const EnclosureAssembly = ({capStyle="circular"}: {capStyle?:CapStyle} = {}) => <Fragment>','  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly','    key={m.name} name={`ONEPIECE_V4_${m.name}`} displayName={m.name.replace(/_/g," ")}', '    cadModel={{objUrl:m.obj,mtlUrl:m.mtl,modelUnitToMmScale:1,','      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-7.6},','      rotationOffset:{x:0,y:0,z:0},','      showAsTranslucentModel:m.style !== null || ["Bottom_Tray","Stationary_Base"].includes(m.name),','    }}/>)}','</Fragment>','']
(root.parent/'enclosure.tsx').write_text('\n'.join(lines).replace('./Circuit_Models/', './mechanical/Circuit_Models/'))
(models/'manifest.json').write_text(json.dumps({'styles':['circular', 'ships_wheel', 'rounded_triangle', 'scalloped_coin', 'petal_flower', 'four_leaf_clover', 'rounded_hexagon', 'rounded_square', 'wave_rim', 'turbine_wheel', 'thumb_scoop'],'modelsPerSelectedStyle':8,'totalAssets':18,'pcbMidplaneZMm':7.6,'sourceParameters':json.loads((root/'enclosure-parameters.json').read_text()),'modelSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in models.iterdir() if p.suffix in ['.obj','.mtl']}},indent=2)+'\n')
print('Created tscircuit selector: 18 mesh assets, 8 per selected style.')
