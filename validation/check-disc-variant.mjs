// Native preview parity and strict electrical preservation for the V3 base.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {createHash} from 'node:crypto'
import assert from 'node:assert/strict'
import {fittedComponentRecords} from './fitted-component-records.mjs'
const read=p=>JSON.parse(readFileSync(p)),sha=b=>createHash('sha256').update(b).digest('hex')
const folder='mechanical/variants/V3_disc_magnets',p=read(`${folder}/parameters.json`),audit=read(`${folder}/generated/geometry-audit.json`)
const m=read('mechanical/Circuit_Models/manifest.json'),c=read('dist/index/circuit.json'),old=read('mechanical/variants/V1_premade_ring/source/published.circuit.json')
assert.equal(m.activeVariant,'V3_disc_magnets');assert.deepEqual(m.activeVariantParameters,p)
assert(audit.passed&&!audit.physical_tested&&!audit.holding_force_verified)
assert.equal(audit.parameters_sha256,sha(readFileSync(`${folder}/parameters.json`)))
assert.equal(audit.builder_sha256,sha(readFileSync(`${folder}/build.py`)))
assert.equal(audit.frozen_circuit_sha256,sha(readFileSync('mechanical/variants/V1_premade_ring/source/published.circuit.json')))
assert.equal(p.magnet.quantity,20);assert.equal(p.magnet.diameter_mm,6);assert.equal(p.magnet.thickness_mm,3)
assert.equal(p.physical_height_mm,20.9);assert.equal(p.nominal_encoder_gap_mm,1.8)
assert.equal(p.encoder.diameter_mm,6);assert.equal(p.encoder.thickness_mm,3)
assert.deepEqual(p.encoder.axis_in_rotor,[1,0,0]);assert(p.encoder.same_part_as_attachment_discs)
assert.deepEqual(audit.encoder,p.encoder)
assert(audit.flat_wrong_orientation_rejected&&audit.all_bearing_interfaces_unchanged)
assert.equal(audit.supplier_bodies_checked,27);assert.equal(audit.cap_styles_checked.length,11)
assert(audit.minimum_pocket_web_mm>1.3&&audit.pocket_inner_wall_mm>=.9&&audit.pocket_outer_wall_mm>=.9)
assert.equal(audit.steel_backing_count,0);assert.equal(audit.separate_carrier_count,0)
assert.equal(audit.printed_product_parts,2);assert.equal(audit.handled_parts,28)
assert.equal(audit.bottom_insertion_poses_per_disc,7);assert.equal(audit.bottom_insertion_collision_mm3,0)
assert(!c.some(e=>e.type.endsWith('_error')))
// This comparison includes routed copper, holes, silkscreen, soldermask, all
// fitted component poses and all supplier identities. No rerouting is accepted.
const board=items=>items.filter(e=>e.type.startsWith('pcb_'))
assert.deepEqual(board(c),board(old),'V3 changed native PCB records')
assert.deepEqual(fittedComponentRecords(c),fittedComponentRecords(old),'V3 changed fitted electronic components')
assert.equal(fittedComponentRecords(c).length,27)
for(const [name,digest] of Object.entries(m.modelSha256))assert.equal(sha(readFileSync(`mechanical/Circuit_Models/${name}`)),digest)
const sources=c.filter(e=>e.type==='source_component'&&e.name?.startsWith('BEARING_V5_'))
assert.equal(sources.length,7)
for(const name of ['Base_V3_Discs','Attachment_Discs_V3','Bearing_6808','PCB_Fasteners','Cell','Magnet'])assert(sources.some(e=>e.name===`BEARING_V5_${name}`))
assert(!sources.some(e=>/Steel_Backing|Magnet_Carrier/.test(e.name)))
assert(!sources.some(e=>e.name.includes('MagSafe_Ring')||e.name.includes('Encoder_Spacer')))
const ids=new Set(sources.map(e=>e.source_component_id))
assert(!c.some(e=>(e.type==='pcb_component'||e.type==='source_port')&&ids.has(e.source_component_id)))
const bytes=readFileSync('dist/index/3d.glb'),gltf=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)))
const bounds=[]
for(const source of sources){
 const name=source.name.slice('BEARING_V5_'.length),cad=c.find(e=>e.type==='cad_component'&&e.source_component_id===source.source_component_id)
 assert.equal(cad.model_glb_url,`./mechanical/Circuit_Models/${name}.glb`)
 assert.deepEqual(cad.position,{x:0,y:0,z:-m.pcbMidplaneZMm})
 const blob=readFileSync(cad.model_glb_url),asset=JSON.parse(blob.subarray(20,20+blob.readUInt32LE(12)))
 assert.equal(asset.asset.extras.cadUpAxis,'Z');assert.equal(asset.asset.extras.cadUnits,'mm')
 const actualNode=gltf.nodes.find(n=>n.name===source.name&&Number.isInteger(n.mesh));assert(actualNode,`Missing native ${name}`)
 const collect=(model,meshes,translation=[0,0,0])=>{
  const b=[[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
  for(const mesh of meshes)for(const primitive of mesh.primitives){const a=model.accessors[primitive.attributes.POSITION];for(let axis=0;axis<3;axis++){b[0][axis]=Math.min(b[0][axis],a.min[axis]+translation[axis]);b[1][axis]=Math.max(b[1][axis],a.max[axis]+translation[axis])}}
  return b
 }
 const [min,max]=collect(asset,asset.meshes),expected=[[-max[0],min[2]-m.pcbMidplaneZMm,min[1]],[-min[0],max[2]-m.pcbMidplaneZMm,max[1]]]
 const actual=collect(gltf,[gltf.meshes[actualNode.mesh]],actualNode.translation??[0,0,0])
 const error=Math.max(...actual.flatMap((row,i)=>row.map((v,j)=>Math.abs(v-expected[i][j]))));assert(error<.0001,`Misaligned ${name}`)
 bounds.push({name,maximum_bounds_error_mm:error})
}
mkdirSync('work',{recursive:true})
writeFileSync('work/disc-native-preview-audit.json',JSON.stringify({passed:true,physical_tested:false,variant:p.variant,pcb_records_identical:true,fitted_components_identical:27,mechanical_models:bounds,circuit_sha256:sha(readFileSync('dist/index/circuit.json'))},null,2)+'\n')
console.log('PASS: bottom-load V3 native preview, 20 discs, no steel/carrier; all routed PCB records and 27 fitted components identical to corrected 1.0.31')
