import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import assert from 'node:assert/strict'
const read=p=>JSON.parse(readFileSync(p)),sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex')
const c=read('enclosure-drawing.circuit.json'),dims=read('work/native-drawing/dimension-audit.json')
const pages=c.filter(e=>e.type==='drawing_page'),views=c.filter(e=>e.type==='drawing_part_view'),lines=c.filter(e=>e.type==='drawing_dimension_line')
assert.equal(pages.length,2);assert.equal(views.length,6);assert.equal(lines.length,7)
assert(pages.every(p=>p.width===420&&p.height===297))
assert(!c.some(e=>e.type.startsWith('pcb_')),'Drawing references must not introduce a PCB')
assert(!c.some(e=>['drawing_artifact','drawing_view','drawing'].includes(e.type)),'Use native drawing-page records')
const sources=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e]))
const cad=new Map(c.filter(e=>e.type==='cad_component').map(e=>[e.source_component_id,e]))
const viewParts=name=>{
  const view=views.find(v=>v.name===name);assert(view?.source_component_ids?.length)
  return new Map(view.source_component_ids.filter(id=>cad.has(id)).map(id=>[sources.get(id).name,cad.get(id)]))
}
const assembled=viewParts('AssembledIso'),exploded=viewParts('ExplodedIso')
const offsets={Base:25,AttachmentDiscs:-20,Cap:280,Encoder:235,Bearing:190,PCB_Screws:145,BoardAnd26FittedParts:105,Hall:105,Battery:70}
assert.equal(assembled.size,9);assert.equal(exploded.size,9)
for(const[name,offset]of Object.entries(offsets)){
  const a=assembled.get(name),b=exploded.get(name);assert(a&&b)
  assert.equal(a.model_glb_url,b.model_glb_url);assert.deepEqual(a.rotation,b.rotation)
  assert.deepEqual(a.model_origin_position,b.model_origin_position)
  assert.equal(a.position.x,b.position.x);assert.equal(a.position.y,b.position.y)
  assert(Math.abs(b.position.z-a.position.z-offset)<1e-6,`Wrong exploded pose: ${name}`)
}
assert(assembled.get('Base').model_glb_url.endsWith('/Base_V3_Discs.glb'))
assert(assembled.get('Encoder').model_glb_url.endsWith('/Magnet.glb'))
assert(views.some(v=>v.section?.axis==='y'))
for(const line of lines)assert(views.some(v=>v.drawing_part_view_id===line.drawing_part_view_id))
assert.equal(dims.source_sha256,sha('enclosure-drawing.assembly.tsx'))
assert.equal(dims.resolver_sha256,sha('validation/resolve-native-drawing-dimensions.mjs'))
assert.equal(dims.circuit_sha256,sha('enclosure-drawing.circuit.json'))
for(const model of read('mechanical/Circuit_Models/Drawings/manifest.json').models)assert.equal(model.sha256,sha(model.file))
const report={...dims,passed:true,exploded_parts_match_assembled:true,native_model_states:2,models_per_state:9,no_PCB_records_in_drawing:true,compiler:read('package.json').dependencies.tscircuit,physical_geometry_release:'1.0.33'}
writeFileSync('validation/native-drawing-audit.json',JSON.stringify(report,null,2)+'\n')
console.log('PASS: native A3 drawing pages, six views, seven model-derived dimensions; exploded geometry equals assembled parts; PCB unchanged')
