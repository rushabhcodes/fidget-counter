import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {createHash} from 'node:crypto'
import assert from 'node:assert/strict'
import {fittedComponentRecords} from './fitted-component-records.mjs'
const json = path => JSON.parse(readFileSync(path))
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
const p=json('mechanical/enclosure-parameters.json'),m=json('mechanical/Circuit_Models/manifest.json')
const g=json('mechanical/enclosure-validation.json'),stls=json('validation/bearing-stl-audit.json')
const pushfit=p.cap_retention?.mode==='push_fit',freshRouting=json('package.json').dependencies.tscircuit==='0.0.3060'
assert.deepEqual(m.sourceParameters,p,'Stale model parameters')
assert.deepEqual(g.parameters,p,'Stale CAD checks')
assert.equal(p.base_diameter,58);assert(p.overall_height<=17.2);assert(!('button_travel' in p))
assert.equal(g.flexible_printed_latches,0);assert.equal(g.pcb_screws,2);assert.equal(g.return_springs,0)
assert.equal(g.printed_parts.length,pushfit?12:14);assert(g.printed_parts.every(x=>x.valid&&x.solids===1))
assert.equal(g.press_travel_mm,0);assert.equal(g.rotation_checks.length,24)
assert(g.rotation_checks.every(x=>x.rigid_collisions===0));assert.equal(g.physical_tested,false)
assert(g.jst_swept_clearance_mm>=.7)
assert.equal(stls.parts.length,pushfit?12:14);assert(stls.passed&&!stls.physically_tested)
for(const part of stls.parts)assert.equal(hash(readFileSync(`mechanical/Print_STL/${part.file}`)),part.sha256,`Stale STL ${part.file}`)
for(const [file,sha] of Object.entries(m.modelSha256))assert.equal(hash(readFileSync(`mechanical/Circuit_Models/${file}`)),sha,`Stale model ${file}`)
const bytes=readFileSync('dist/index/circuit.json'),c=JSON.parse(bytes)
assert(!c.some(x=>x.type.endsWith('_error')))
const sources=c.filter(x=>x.type==='source_component'&&x.name?.startsWith('BEARING_V5_'))
const ids=new Set(sources.map(x=>x.source_component_id))
assert.equal(sources.length,m.modelsPerSelectedStyle)
assert(!c.some(x=>(x.type==='pcb_component'||x.type==='source_port')&&ids.has(x.source_component_id)))
const style=readFileSync('index.circuit.tsx','utf8').match(/const CAP_STYLE: CapStyle = "([a-z_]+)"/)[1]
assert(sources.some(x=>x.name===`BEARING_V5_Cap_${style}`))
for(const name of ['Stationary_Base',...(pushfit?[]:['Inner_Race_Nut']),'Bearing_6808','PCB_Fasteners','MagSafe_Ring'])assert(sources.some(x=>x.name===`BEARING_V5_${name}`))
assert(!sources.some(x=>['BEARING_V5_Attachment_Magnets','BEARING_V5_Backing_Ring'].includes(x.name)))
assert.equal(m.modelsPerSelectedStyle,pushfit?7:10)
if(pushfit)for(const name of ['Inner_Race_Nut','Outer_Race_Retainer','Cap_Retainer_Screws'])assert(!sources.some(x=>x.name===`BEARING_V5_${name}`))
assert(!sources.some(x=>x.name==='BEARING_V5_Encoder_Spacer'))
assert.equal(g.separate_encoder_spacers,0);assert.equal(g.encoder_stop_z_mm,p.encoder_stop.seated_top_z_mm)
assert.equal(g.manufacturing_qualified,false)
assert.equal(g.finished_cap_retainer_and_screw_clearance_checks,pushfit?0:11)
assert.equal(g.attachment_ring.separate_trays,0);assert.equal(g.attachment_ring.separate_tray_bonds,0)
assert.equal(g.handled_parts_per_unit_excluding_adhesive_and_shims,pushfit?9:14);assert.equal(g.screw_driving_operations,pushfit?2:5)
assert(!sources.some(x=>x.name==='BEARING_V5_Bottom_Tray'))
assert.equal(fittedComponentRecords(c).length,27)
for(const name of ['SW1','R5','C17','BEARING_V5_Return_Springs','BEARING_V5_Actuator_Ring','BEARING_V5_Bearing_Carrier','BEARING_V5_Guide_Fasteners'])assert(!c.some(e=>e.type==='source_component'&&e.name===name))
for(const via of c.filter(x=>x.type==='pcb_via')){assert.equal(via.hole_diameter,.3);assert.equal(via.outer_diameter,.55)}
const holes=c.filter(x=>x.type==='pcb_hole');assert.equal(holes.length,4)
for(const a of p.pcb_mount.angles_deg){const r=p.pcb_mount.radius_mm,theta=a*Math.PI/180;assert(holes.some(h=>Math.hypot(h.x-r*Math.cos(theta),h.y-r*Math.sin(theta))<1e-6&&h.hole_diameter===p.pcb_mount.hole_diameter_mm))}
const glb=readFileSync('dist/index/3d.glb'),gltf=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString())
const reports=[]
for(const source of sources){
 const name=source.name.replace('BEARING_V5_',''),cad=c.find(x=>x.type==='cad_component'&&x.source_component_id===source.source_component_id)
 assert.equal(cad.model_glb_url,`./mechanical/Circuit_Models/${name}.glb`)
 assert.deepEqual(cad.position,{x:0,y:0,z:-m.pcbMidplaneZMm})
 const bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
 const model=readFileSync(`mechanical/Circuit_Models/${name}.glb`),asset=JSON.parse(model.subarray(20,20+model.readUInt32LE(12)).toString())
 assert.equal(asset.asset.extras.cadUpAxis,'Z');assert.equal(asset.asset.extras.cadUnits,'mm')
 for(const node of asset.nodes??[]){assert(!node.translation&&!node.rotation&&!node.scale,'Unexpected source transform');if(node.matrix)assert.deepEqual(node.matrix,[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])}
 for(const mesh of asset.meshes)for(const primitive of mesh.primitives){const a=asset.accessors[primitive.attributes.POSITION];for(let axis=0;axis<3;axis++){bounds[0][axis]=Math.min(bounds[0][axis],a.min[axis]);bounds[1][axis]=Math.max(bounds[1][axis],a.max[axis])}}

 const node=gltf.nodes.find(n=>n.name===source.name&&Number.isInteger(n.mesh));assert(node,`Missing native mesh ${name}`)
 const actual=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
 for(const primitive of gltf.meshes[node.mesh].primitives){const positions=gltf.accessors[primitive.attributes.POSITION];for(let a=0;a<3;a++){actual[0][a]=Math.min(actual[0][a],positions.min[a]+(node.translation?.[a]??0));actual[1][a]=Math.max(actual[1][a],positions.max[a]+(node.translation?.[a]??0))}}
 const [min,max]=bounds,expected=[[-max[0],min[2]-m.pcbMidplaneZMm,min[1]],[-min[0],max[2]-m.pcbMidplaneZMm,max[1]]]
 const error=Math.max(...actual.flatMap((v,i)=>v.map((n,j)=>Math.abs(n-expected[i][j]))));assert(error<.0001,`Misaligned ${name}: ${error}`)
 reports.push({name,maximumBoundsErrorMm:error})
}
for(const file of ['validation/attachment-ring-audit.json','validation/jst-connector-clearance.json','validation/pcb-mount-clearance.json','validation/bearing-hardware-clearance.json']){
 const report=json(file);assert(report.passed&&!report.physical_tested,file)
 for(const [path,sha] of Object.entries(report.sha256))assert.equal(hash(readFileSync(path)),sha,`Stale clearance result ${path}`)
}
const insertion=json('validation/pcb-insertion-audit.json')
assert(insertion.passed&&!insertion.physical_tested)
assert.equal(insertion.electronics.length,27);assert(insertion.nominal_radial_insertion_clearance_mm>=.3)
assert(insertion.previous_obstruction_volume_mm3>1);assert(pushfit?insertion.minimum_fixed_shaft_wall_mm>=1.3:insertion.minimum_male_root_wall_mm>=.8)
for(const [path,sha] of Object.entries(insertion.source_sha256))assert.equal(hash(readFileSync(path)),sha,`Stale PCB insertion proof ${path}`)
const batteryUpgrade=p.battery?.standard==='CR2450'
if(p.cap_compaction)for(const file of ['validation/compact-cap-audit.json','validation/encoder-gap-audit.json']){
 const report=json(file);assert(report.passed&&!report.physical_tested,file)
 for(const [path,sha]of Object.entries(report.source_sha256))assert.equal(hash(readFileSync(path)),sha,`Stale compact/encoder proof ${path}`)
}
const manufacturing=json(pushfit?'validation/pushfit-cad-audit.json':batteryUpgrade?'validation/cr2450-cad-audit.json':'validation/rotation-only-cad-audit.json')
assert(manufacturing.passed&&!manufacturing.physical_tested)
assert.equal(manufacturing.comparison_commit,p.cap_compaction?'b300e196ec7e3ff56dc7dc9638462b9cf52ab772':pushfit?'a7c29c470c439e6f4e35314b9c68bba5c8d8c100':batteryUpgrade?'346fade26c8934f9d0b6411d7e30c1c9b06e9dac':'0397495f30583bb6a4501f5fb0f67bccf0f397aa')
assert.equal(manufacturing.cap_results.length,11)
for(const [path,sha] of Object.entries(manufacturing.source_sha256))assert.equal(hash(readFileSync(path)),sha,`Stale CAD proof ${path}`)
if(batteryUpgrade)for(const file of ['validation/cr2450-circuit-audit.json',...(freshRouting?['validation/fresh-routing-audit.json','validation/native-fabrication-audit.json','validation/gerber-parity-audit.json','validation/source-snapshot-audit.json']:['validation/cr2450-copper-audit.json']),'validation/cr2450-holder-audit.json','validation/cr2450-display-audit.json','validation/passive-substitution-audit.json',...(pushfit?['validation/npth-copper-audit.json','validation/print-readiness.json']:[])]){
 const report=json(file);assert(report.passed,file)
 for(const [path,sha] of Object.entries(report.source_sha256))assert.equal(hash(readFileSync(path)),sha,`Stale battery proof ${path}`)
}
mkdirSync('work',{recursive:true});writeFileSync('work/enclosure-model-audit.json',JSON.stringify({passed:true,physicalTested:false,style,models:reports,baseDiameterMm:58,heightMm:p.overall_height,circuitSha256:hash(bytes)},null,2)+'\n')
console.log(`Pass: ${sources.length} aligned mechanical models; 27 fitted electronics and four PCB holes preserved; 58 x ${p.overall_height} mm enclosure`)
