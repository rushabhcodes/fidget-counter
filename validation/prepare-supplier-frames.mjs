import {Circuit} from '@tscircuit/core'
import {createElement} from 'react'
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs'
import {resolve} from 'node:path'
import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {verifyImportedFile} from './import-provenance.mjs'
import {populatePartOrientationMetadata,convertCircuitJsonToPickAndPlaceCsv,convertCircuitJsonToPickAndPlaceRows} from 'circuit-json-to-pnp-csv'
const root=process.cwd(),out=resolve(process.argv[3]??'dist/fabrication'),input=process.argv[2]??'published.circuit.json';mkdirSync(out,{recursive:true})
const c=JSON.parse(readFileSync(input,'utf8')),prov=JSON.parse(readFileSync('validation/jlc-imports.json','utf8'))
const byId=new Map(prov.parts.filter((p)=>p.files.some((f)=>f.path.endsWith('.tsx'))).map((p)=>[p.jlcpcb,p]))
const frames=new Map(),proof=[]
for(const s of c.filter((e)=>e.type==='source_component'&&e.supplier_part_numbers?.jlcpcb)){
 const id=s.supplier_part_numbers.jlcpcb[0];if(frames.has(id))continue
 const entry=byId.get(id);if(!entry)throw Error('No raw supplier TSX for '+id)
 for(const f of entry.files)verifyImportedFile(f,readFileSync(f.path))
 const path=entry.files.find((f)=>f.path.endsWith('.tsx')).path
 const mod=await import(resolve(root,path));const raw=Object.values(mod).find(v=>typeof v==='function');if(!raw)throw Error(path)
 const cc=new Circuit({partsEngineDisabled:true});cc.add(createElement('board',{width:60,height:60},createElement(raw,{name:'SUPPLIER_REF',loadCapacitance:s.load_capacitance,pcbX:0,pcbY:0,pcbRotation:0,layer:'top'})))
 await cc.renderUntilSettled();const json=cc.getCircuitJson();frames.set(id,json);proof.push({id,path,sha256:createHash('sha256').update(readFileSync(path)).digest('hex'),pads:json.filter((e)=>e.type==='pcb_smtpad'||e.type==='pcb_plated_hole')})
 console.log('Supplier frame:',id,path)
}

const recompute=structuredClone(c);for(const e of recompute)if(e.type==='pcb_component')delete e.supplier_pin1_location_map
const prepared=await populatePartOrientationMetadata(recompute,{supplier:'jlcpcb',partsEngine:{fetchPartCircuitJson:async({supplierPartNumber})=>frames.get(supplierPartNumber)}})
const rows=convertCircuitJsonToPickAndPlaceRows(prepared,{supplier:'jlcpcb',requireSupplierRotation:true})
if(rows.length!==27||rows.find(r=>r.designator==='BT1')?.layer!=='bottom')throw Error('Fitted assembly selection changed')
writeFileSync(resolve(out,'prepared.circuit.json'),JSON.stringify(prepared,null,2)+'\n');writeFileSync(resolve(out,'cpl.csv'),convertCircuitJsonToPickAndPlaceCsv(prepared,{supplier:'jlcpcb',requireSupplierRotation:true}));writeFileSync(resolve(out,'supplier-frames.json'),JSON.stringify(proof,null,2)+'\n')
for(const e of c)if(e.type==='pcb_component'&&e.supplier_pin1_location_map)assert.deepEqual(e.supplier_pin1_location_map,prepared.find(p=>p.type==='pcb_component'&&p.pcb_component_id===e.pcb_component_id).supplier_pin1_location_map,'Stored supplier orientation differs from raw import')
const stripped=structuredClone(prepared);for(const e of stripped)if(e.type==='pcb_component')delete e.supplier_pin1_location_map
delete stripped._internal_store // soup-util attaches an array lookup cache, not circuit data
const original=structuredClone(c);for(const e of original)if(e.type==='pcb_component')delete e.supplier_pin1_location_map
assert.deepEqual(stripped,original,'Orientation enrichment changed physical geometry or connectivity')
const sourceNames=new Map(c.filter((e)=>e.type==='source_component').map((e)=>[e.source_component_id,e.name]))
const adjustments=rows.flatMap(row=>{const p=c.find((e)=>e.type==='pcb_component'&&sourceNames.get(e.source_component_id)===row.designator);return p.rotation===row.rotation?[]:[{designator:row.designator,layer:row.layer,authored_rotation:p.rotation,jlcpcb_rotation:row.rotation}]})
writeFileSync(resolve(out,'orientation-audit.json'),JSON.stringify({passed:true,physical_qualified:false,source_circuit_sha256:createHash('sha256').update(readFileSync(input)).digest('hex'),fitted_rows:rows.length,supplier_frame_types:frames.size,adjustments,limits:['Verify BT1 pin1 positive and all polarized parts in JLCPCB assembly preview before approving the order']},null,2)+'\n')
console.log('PASS:27 strict supplier-frame placement rotations; raw import provenance retained; physical assembly-preview approval remains required')
