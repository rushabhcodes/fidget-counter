// Compare electrical/physical semantics, never generated port/component IDs.
import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {fittedComponentRecords} from './fitted-component-records.mjs'
const canonical=value=>JSON.stringify(value,(_,v)=>v&&!Array.isArray(v)&&typeof v==='object'
 ?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):typeof v==='number'?Math.round(v*1e9)/1e9:v)
const hash=value=>createHash('sha256').update(canonical(value)).digest('hex')
export function circuitSemantics(circuit){
 const sources=new Map(circuit.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]))
 const ports=new Map(circuit.filter(e=>e.type==='source_port').map(e=>[e.source_port_id,`${sources.get(e.source_component_id)}.${e.pin_number}`]))
 const nets=new Map(circuit.filter(e=>e.type==='source_net').map(e=>[e.source_net_id,e.name]))
 const traceSemantics=e=>({terminals:(e.connected_source_port_ids??[]).map(id=>ports.get(id)).sort(),
  nets:(e.connected_source_net_ids??[]).map(id=>nets.get(id)).sort(),maxLength:e.max_length,maxViaCount:e.max_via_count})
 const traces=new Map(circuit.filter(e=>e.type==='source_trace').map(e=>[e.source_trace_id,traceSemantics(e)]))
 const pcbPorts=new Map(circuit.filter(e=>e.type==='pcb_port').map(e=>[e.pcb_port_id,
  {terminal:ports.get(e.source_port_id),x:e.x,y:e.y,layers:e.layers}]))
 const clean=value=>Array.isArray(value)?value.map(clean):value&&typeof value==='object'
  ?Object.fromEntries(Object.entries(value).filter(([k])=>!k.endsWith('_id')&&!k.endsWith('_ids')&&
   !['connectsTo','subcircuit_connectivity_map_key'].includes(k)).map(([k,v])=>[k,clean(v)])):value
 const sorted=records=>records.map(canonical).sort()
 const groups={}
 for(const type of ['pcb_trace','pcb_via','pcb_hole','pcb_smtpad','pcb_plated_hole','pcb_board']){
  const records=sorted(circuit.filter(e=>e.type===type).map(e=>({...clean(e),
   ...(e.source_net_id?{electricalNet:nets.get(e.source_net_id)}:{}),
   ...(e.source_trace_id?{electricalTrace:traces.get(e.source_trace_id)}:{}),
   ...(e.route?{routeTerminals:e.route.map(p=>({start:pcbPorts.get(p.start_pcb_port_id),end:pcbPorts.get(p.end_pcb_port_id)}))}:{}),
   ...(e.connectsTo?{connectedTerminals:e.connectsTo.map(id=>pcbPorts.get(id)).sort((a,b)=>canonical(a).localeCompare(canonical(b)))}:{})})))
  groups[type]={count:records.length,sha256:hash(records)}
 }
 const connectivity=sorted([...traces.values()])
 return {copper:groups,connectivity:{count:connectivity.length,sha256:hash(connectivity)},
  fitted:{count:fittedComponentRecords(circuit).length,sha256:hash(fittedComponentRecords(circuit))}}
}
if(import.meta.main){
 const expected=JSON.parse(readFileSync('validation/compiler-upgrade-baseline.json'))
 const actual=circuitSemantics(JSON.parse(readFileSync(process.argv[2]??'dist/index/circuit.json')))
 assert.deepEqual(actual,expected.semantics,'Electrical or physical semantics changed during the compiler upgrade')
 writeFileSync('work/compiler-upgrade-audit.json',JSON.stringify({passed:true,from:expected.compiler_version,
  to:JSON.parse(readFileSync('package.json')).dependencies.tscircuit,semantics:actual},null,2)+'\n')
 console.log('Pass: copper, net membership, all 31 fitted parts, pads, layers, holes and CAD poses preserved')
}
