import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {createHash} from 'node:crypto'
import assert from 'node:assert/strict'
import {fittedComponentRecords} from './fitted-component-records.mjs'
const json = path => JSON.parse(readFileSync(path))
const hash = bytes => createHash('sha256').update(bytes).digest('hex')
const p=json('mechanical/enclosure-parameters.json'),m=json('mechanical/Circuit_Models/manifest.json')
const g=json('mechanical/enclosure-validation.json'),stls=json('validation/bearing-stl-audit.json')
assert.deepEqual(m.sourceParameters,p,'Stale model parameters')
assert.deepEqual(g.parameters,p,'Stale CAD checks')
assert.equal(p.base_diameter,58);assert(p.overall_height<=17.2);assert.equal(p.button_travel,.8)
assert.equal(g.flexible_printed_latches,0);assert.equal(g.pcb_screws,4);assert.equal(g.return_springs,3)
assert.equal(g.printed_parts.length,16);assert(g.printed_parts.every(x=>x.valid&&x.solids===1))
assert.equal(g.press_checks.length,3);assert.equal(g.rotation_checks.length,72)
assert(g.rotation_checks.every(x=>x.rigid_collisions===0));assert.equal(g.physical_tested,false)
assert.equal(g.actuator_qualified,false,'Do not turn an unmeasured material assumption into a pass')
assert(g.jst_swept_clearance_mm>=.7);assert(g.spring_solid_height_clearance_mm>=.4)
assert.equal(stls.parts.length,16);assert(stls.passed&&!stls.physically_tested)
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
for(const name of ['Bearing_Carrier','Inner_Race_Nut','Bearing_6708','Return_Springs','Guide_Fasteners','PCB_Fasteners'])assert(sources.some(x=>x.name===`BEARING_V5_${name}`))
const baseline=json('validation/fitted-component-baseline.json')
assert.deepEqual(fittedComponentRecords(c).filter(x=>x.source.name!=='J_DEBUG'),baseline.components,'Existing fitted electronics changed')
assert.equal(fittedComponentRecords(c).length,31)
const component=name=>c.find(e=>e.type==='pcb_component'&&e.source_component_id===c.find(s=>s.type==='source_component'&&s.name===name)?.source_component_id)
assert.deepEqual(component('SW1').center,{x:0,y:-5});assert.deepEqual(component('U2').center,{x:0,y:0})
for(const via of c.filter(x=>x.type==='pcb_via')){assert.equal(via.hole_diameter,.3);assert.equal(via.outer_diameter,.55)}
const holes=c.filter(x=>x.type==='pcb_hole');assert.equal(holes.length,4)
for(const a of p.pcb_mount.angles_deg){const r=p.pcb_mount.radius_mm,theta=a*Math.PI/180;assert(holes.some(h=>Math.hypot(h.x-r*Math.cos(theta),h.y-r*Math.sin(theta))<1e-6&&h.hole_diameter===3))}
const glb=readFileSync('dist/index/3d.glb'),gltf=JSON.parse(glb.subarray(20,20+glb.readUInt32LE(12)).toString())
const reports=[]
for(const source of sources){
 const name=source.name.replace('BEARING_V5_',''),cad=c.find(x=>x.type==='cad_component'&&x.source_component_id===source.source_component_id)
 assert.equal(cad.model_obj_url,`./mechanical/Circuit_Models/${name}.obj`)
 assert.deepEqual(cad.position,{x:0,y:0,z:-m.pcbMidplaneZMm})
 const bounds=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
 for(const line of readFileSync(`mechanical/Circuit_Models/${name}.obj`,'utf8').split('\n'))if(line.startsWith('v '))line.split(/\s+/).slice(1,4).map(Number).forEach((v,a)=>{bounds[0][a]=Math.min(bounds[0][a],v);bounds[1][a]=Math.max(bounds[1][a],v)})
 const node=gltf.nodes.find(n=>n.name===source.name&&Number.isInteger(n.mesh));assert(node,`Missing native mesh ${name}`)
 const actual=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
 for(const primitive of gltf.meshes[node.mesh].primitives){const positions=gltf.accessors[primitive.attributes.POSITION];for(let a=0;a<3;a++){actual[0][a]=Math.min(actual[0][a],positions.min[a]+(node.translation?.[a]??0));actual[1][a]=Math.max(actual[1][a],positions.max[a]+(node.translation?.[a]??0))}}
 const [min,max]=bounds,expected=[[-max[0],min[2]-m.pcbMidplaneZMm,min[1]],[-min[0],max[2]-m.pcbMidplaneZMm,max[1]]]
 const error=Math.max(...actual.flatMap((v,i)=>v.map((n,j)=>Math.abs(n-expected[i][j]))));assert(error<.0001,`Misaligned ${name}: ${error}`)
 reports.push({name,maximumBoundsErrorMm:error})
}
for(const file of ['validation/jst-connector-clearance.json','validation/pcb-mount-clearance.json','validation/bearing-hardware-clearance.json']){
 const report=json(file);assert(report.passed&&!report.physical_tested,file)
 for(const [path,sha] of Object.entries(report.sha256))assert.equal(hash(readFileSync(path)),sha,`Stale clearance result ${path}`)
}
mkdirSync('work',{recursive:true});writeFileSync('work/enclosure-model-audit.json',JSON.stringify({passed:true,physicalTested:false,style,models:reports,baseDiameterMm:58,heightMm:p.overall_height,circuitSha256:hash(bytes)},null,2)+'\n')
console.log(`Pass: ${sources.length} aligned V5 models; original 31 fitted electronics and four PCB holes preserved; 58 x ${p.overall_height} mm enclosure`)
