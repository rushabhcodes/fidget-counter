// Intentional RevB removal, against the last verified press-cap commit.
// Retained electronics and every surviving copper segment must be identical.
import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {execFileSync} from 'node:child_process'
import {readFileSync,writeFileSync} from 'node:fs'
import {fittedComponentRecords} from './fitted-component-records.mjs'
if(JSON.parse(readFileSync('mechanical/enclosure-parameters.json')).battery?.standard==='CR2450'){
 const {runCr2450Check}=await import('./check-cr2450-circuit.mjs');runCr2450Check();process.exit(0)
}
const commit='6224fc92863964ff770789ec086876e289d29bee'
const old=JSON.parse(execFileSync('git',['show',`${commit}:published.circuit.json`],{maxBuffer:8e6}))
const current=JSON.parse(readFileSync(process.argv[2]??'dist/index/circuit.json'))
const removed=new Set(['SW1','R5','C17'])
const canonical=v=>JSON.stringify(v,(_,x)=>typeof x==='number'?Math.round(x*1e9)/1e9:x&&!Array.isArray(x)&&typeof x==='object'?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a.localeCompare(b))):x)
const fitted=fittedComponentRecords(current),expected=fittedComponentRecords(old).filter(r=>!removed.has(r.source.name))
assert.deepEqual(fitted,expected,'Retained fitted identity, pads, layer, pose or placement changed')
assert.equal(fitted.length,28)
const records=c=>{
 const sources=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]))
 const ports=new Map(c.filter(e=>e.type==='source_port').map(e=>[e.source_port_id,`${sources.get(e.source_component_id)}.${e.pin_number}`]))
 const nets=new Map(c.filter(e=>e.type==='source_net').map(e=>[e.subcircuit_connectivity_map_key,e.name]))
 const traces=new Map(c.filter(e=>e.type==='source_trace').map(e=>[e.source_trace_id,e]))
 const pcbPorts=new Map(c.filter(e=>e.type==='pcb_port').map(e=>[e.pcb_port_id,ports.get(e.source_port_id)]))
 const clean=v=>Array.isArray(v)?v.map(clean):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).filter(([k])=>!k.endsWith('_id')&&!k.endsWith('_ids')&&!['connectsTo','subcircuit_connectivity_map_key','connection_name','name','title'].includes(k)).map(([k,x])=>[k,clean(x)])):v
 return {sources,ports,nets,traces,pcbPorts,clean,
  copper:e=>canonical({...clean(e),net:nets.get(e.subcircuit_connectivity_map_key??traces.get(e.source_trace_id)?.subcircuit_connectivity_map_key)??c.find(n=>n.type==='source_net'&&n.source_net_id===e.connection_name)?.name,privateTerminals:e.connection_name?.startsWith('source_trace_')?traces.get(e.connection_name)?.connected_source_port_ids.map(id=>ports.get(id)).sort():undefined}),
  connections:c.filter(e=>e.type==='source_trace').map(e=>({terminals:e.connected_source_port_ids.map(id=>ports.get(id)).sort(),nets:(e.connected_source_net_ids??[]).map(id=>c.find(n=>n.type==='source_net'&&n.source_net_id===id)?.name).sort(),max_length:e.max_length,max_via_count:e.max_via_count}))}
}
const a=records(old),b=records(current)
const before=a.connections.filter(r=>!r.terminals.some(p=>removed.has(p.split('.')[0]))&&!r.nets.includes('CAP_PRESS'))
assert.deepEqual(b.connections.map(canonical).sort(),before.map(canonical).sort(),'Remaining electrical connectivity or route constraints changed')
assert(!current.some(e=>e.type==='source_net'&&e.name==='CAP_PRESS'))
const gpio=current.find(e=>e.type==='source_port'&&b.sources.get(e.source_component_id)==='U1'&&e.pin_number===41)
assert(gpio?.do_not_connect,'Former cap GPIO must be explicitly unused')
const diff=(xs,ys)=>{const count=new Map();for(const y of ys)count.set(y,(count.get(y)??0)+1);return xs.filter(x=>{const n=count.get(x)??0;if(n){count.set(x,n-1);return false}return true})}
const summaries={}
let deletedRoutes=[]
for(const type of ['pcb_trace','pcb_via','pcb_hole','pcb_smtpad','pcb_plated_hole','pcb_board']){
 const x=old.filter(e=>e.type===type),y=current.filter(e=>e.type===type),removedRecords=diff(x.map(a.copper),y.map(b.copper)),added=diff(y.map(b.copper),x.map(a.copper))
 assert.equal(added.length,0,`${type}: new or changed copper, layer, net or board geometry`)
 if(type==='pcb_trace'){
  deletedRoutes=x.filter(e=>removedRecords.includes(a.copper(e)))
  assert.equal(deletedRoutes.length,7,'Expected only3 manual and4 prescribed branch routes removed')
  for(const t of deletedRoutes){const src=a.traces.get(t.source_trace_id),terminals=(src?.connected_source_port_ids??[]).map(p=>a.ports.get(p)),ends=(t.connectsTo??[]).map(p=>a.pcbPorts.get(p));
   assert(a.nets.get(src?.subcircuit_connectivity_map_key)==='CAP_PRESS'||[...terminals,...ends].some(p=>p&&removed.has(p.split('.')[0])),`Unrelated route removed ${t.pcb_trace_id}`)
  }
 }else if(type==='pcb_via'){
  for(const v of x.filter(e=>removedRecords.includes(a.copper(e))))assert((v.x===10.4&&v.y===2.1)||deletedRoutes.some(t=>t.route.some(p=>p.route_type==='via'&&p.x===v.x&&p.y===v.y)),'Unrelated via removed')
 }else if(type==='pcb_smtpad'){
  const oldComp=new Map(old.filter(e=>e.type==='pcb_component').map(e=>[e.pcb_component_id,a.sources.get(e.source_component_id)]))
  assert.equal(removedRecords.length,8)
  assert(x.filter(e=>removedRecords.includes(a.copper(e))).every(e=>removed.has(oldComp.get(e.pcb_component_id))))
 }else assert.equal(removedRecords.length,0,`${type}: unrelated geometry removed`)
 summaries[type]={before:x.length,after:y.length,removed:removedRecords.length}
}
assert(!current.some(e=>e.type.endsWith('_error')),'Build errors remain')
const report={passed:true,comparison_commit:commit,removed_components:[...removed],retained_fitted:28,copper:summaries,remaining_connectivity_preserved:true,hardware_programmer_reset_retained:true,firmware_provided:false,source_sha256:Object.fromEntries(['index.circuit.tsx','parts.tsx','passives.tsx','routing.ts','routing-contract.json','routed-paths.json','dist/index/circuit.json', 'published.circuit.json'].map(path=>[path,createHash('sha256').update(readFileSync(path)).digest('hex')]))}
for(const path of ['work/rotation-only-circuit-audit.json','validation/rotation-only-circuit-audit.json'])writeFileSync(path,JSON.stringify(report,null,2)+'\n')
console.log('Pass: exactly SW1/R5/C17 and their branch copper removed;28 fitted parts, all surviving copper/net semantics and SWD reset preserved')
