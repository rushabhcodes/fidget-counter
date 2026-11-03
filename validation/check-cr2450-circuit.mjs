// Bound the intentional CR2450 electrical revision. Retained copper, terminals,
// electrical meaning and routing rules remain fail-closed.
import assert from 'node:assert/strict'
import {execFileSync} from 'node:child_process'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {fittedComponentRecords} from './fitted-component-records.mjs'
export const comparisonCommit='346fade26c8934f9d0b6411d7e30c1c9b06e9dac'
const json=p=>JSON.parse(readFileSync(p))
const baseline=()=>JSON.parse(execFileSync('git',['show',`${comparisonCommit}:published.circuit.json`],{maxBuffer:16e6}))
const canonical=v=>JSON.stringify(v,(_,x)=>typeof x==='number'?Math.round(x*1e9)/1e9:x&&!Array.isArray(x)&&typeof x==='object'?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a.localeCompare(b))):x)
const records=c=>{
 const source=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]))
 const ports=new Map(c.filter(e=>e.type==='source_port').map(e=>[e.source_port_id,`${source.get(e.source_component_id)}.${e.pin_number}`]))
 const pcbPorts=new Map(c.filter(e=>e.type==='pcb_port').map(e=>[e.pcb_port_id,ports.get(e.source_port_id)]))
 const nets=new Map(c.filter(e=>e.type==='source_net').map(e=>[e.subcircuit_connectivity_map_key,e.name]))
 const traces=new Map(c.filter(e=>e.type==='source_trace').map(e=>[e.source_trace_id,e]))
 const clean=v=>Array.isArray(v)?v.map(clean):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).filter(([k])=>!k.endsWith('_id')&&!k.endsWith('_ids')&&!['connectsTo','subcircuit_connectivity_map_key','connection_name','name','title'].includes(k)).map(([k,v])=>[k,clean(v)])):v
 return {source,ports,pcbPorts,nets,traces,clean,
  copper:e=>canonical({...clean(e),net:nets.get(e.subcircuit_connectivity_map_key??traces.get(e.source_trace_id)?.subcircuit_connectivity_map_key)??c.find(n=>n.type==='source_net'&&n.source_net_id===e.connection_name)?.name,privateTerminals:e.connection_name?.startsWith('source_trace_')?traces.get(e.connection_name)?.connected_source_port_ids.map(id=>ports.get(id)).sort():undefined}),
  connections:c.filter(e=>e.type==='source_trace').map(e=>canonical({terminals:e.connected_source_port_ids.map(id=>ports.get(id)).sort(),nets:(e.connected_source_net_ids??[]).map(id=>c.find(n=>n.type==='source_net'&&n.source_net_id===id)?.name).sort(),max_length:e.max_length,max_via_count:e.max_via_count})).sort(),
  portAttributes:c.filter(e=>e.type==='source_port').map(e=>canonical({...clean(e),owner:source.get(e.source_component_id)})).sort()}
}
const sorted=(items,f)=>items.map(f).sort()
export function verifyCr2450Circuit(current,old=baseline()){
 const a=records(old),b=records(current)
 const prior=fittedComponentRecords(old),now=fittedComponentRecords(current)
 assert.equal(now.length,28)
 assert.deepEqual(now.filter(e=>e.source.name!=='BT1'),prior.filter(e=>e.source.name!=='BT1'),'Unrelated fitted identity, footprint, layer or pose changed')
 assert.deepEqual(b.connections,a.connections,'Electrical connections/route constraints changed')
 assert.deepEqual(b.portAttributes,a.portAttributes,'Electrical pin attributes changed')
 const bt=now.find(e=>e.source.name==='BT1')
 assert.equal(bt.source.manufacturer_part_number,'BS-24-B4AA014')
 assert.deepEqual(bt.source.supplier_part_numbers.jlcpcb,['C7525448'])
 assert.equal(bt.source.display_name,'CR2450 3V primary')
 assert.deepEqual(bt.pcb.center,{x:0,y:0});assert.equal(bt.pcb.layer,'bottom');assert.equal(bt.pcb.rotation,0)
 assert.equal(bt.cad.length,1);assert.deepEqual(bt.cad[0].model_origin_position,{x:0,y:0,z:-.9})
 const pcbOwner=c=>new Map(c.filter(e=>e.type==='pcb_component').map(e=>[e.pcb_component_id,records(c).source.get(e.source_component_id)]))
 const oldOwner=pcbOwner(old),newOwner=pcbOwner(current)
 for(const type of ['pcb_board','pcb_plated_hole'])assert.deepEqual(sorted(current.filter(e=>e.type===type),b.copper),sorted(old.filter(e=>e.type===type),a.copper),type+' changed')
 const padFilter=(c,owners)=>c.filter(e=>e.type==='pcb_smtpad'&&owners.get(e.pcb_component_id)!=='BT1')
 assert.deepEqual(sorted(padFilter(current,newOwner),b.copper),sorted(padFilter(old,oldOwner),a.copper),'Unrelated solder lands changed')
 const pads=current.filter(e=>e.type==='pcb_smtpad'&&newOwner.get(e.pcb_component_id)==='BT1')
 assert.equal(pads.length,2)
 for(const [terminal,x] of [['BT1.1',-15.550007],['BT1.2',15.550007]]){
  const pad=pads.find(p=>b.pcbPorts.get(p.pcb_port_id)===terminal);assert(pad)
  assert.equal(pad.layer,'bottom');assert.equal(pad.shape,'rect')
  assert(Math.abs(pad.x-x)<1e-7&&Math.abs(pad.y)<1e-7)
  assert(Math.abs(pad.width-3.3999932)<1e-7&&Math.abs(pad.height-3.5999928)<1e-7)
 }
 const holes=current.filter(e=>e.type==='pcb_hole');assert.equal(holes.length,4)
 for(const angle of [45,135,225,315])assert(holes.some(h=>Math.abs(h.hole_diameter-2.2)<1e-9&&Math.hypot(h.x-16.6*Math.cos(angle*Math.PI/180),h.y-16.6*Math.sin(angle*Math.PI/180))<1e-6),'Wrong new mounting drill')
 const isBattery=(e,r)=>(e.connectsTo??[]).some(id=>r.pcbPorts.get(id)?.startsWith('BT1.'))
 const branches=c=>c.filter(e=>e.type==='pcb_trace')
 const oldBranches=branches(old).filter(e=>isBattery(e,a)),newBranches=branches(current).filter(e=>isBattery(e,b))
 assert.equal(oldBranches.length,2);assert.equal(newBranches.length,2)
 assert.deepEqual(sorted(branches(current).filter(e=>!isBattery(e,b)),b.copper),sorted(branches(old).filter(e=>!isBattery(e,a)),a.copper),'Unrelated copper/net/layer/width changed')
 const branch=(xs,r,pin)=>xs.find(e=>e.connectsTo.some(id=>r.pcbPorts.get(id)===`BT1.${pin}`))
 const positive=branch(newBranches,b,1),priorPositive=branch(oldBranches,a,1)
 const expectedPositive=a.clean(priorPositive.route);expectedPositive[0].x=-15.550007;expectedPositive[0].y=0
 assert.equal(canonical(b.clean(positive.route)),canonical(expectedPositive),'Unexpected positive battery branch change')
 assert.equal(JSON.parse(b.copper(positive)).net,'VBAT')
 const negative=branch(newBranches,b,2),expectedNegative=[
  {route_type:'wire',x:15.550007,y:0,width:.25,layer:'bottom'},
  {route_type:'wire',x:15.550007,y:-3,width:.25,layer:'bottom'},
  {route_type:'via',x:15.550007,y:-3,from_layer:'bottom',to_layer:'top',via_diameter:.55,via_hole_diameter:.3},
  {route_type:'wire',x:15.550007,y:-3,width:.25,layer:'top'},
  {route_type:'wire',x:10,y:-3,width:.25,layer:'top'},
  {route_type:'via',x:10,y:-3,from_layer:'top',to_layer:'bottom',via_diameter:.55,via_hole_diameter:.3},
  {route_type:'wire',x:10,y:-3,width:.25,layer:'bottom'},
  {route_type:'wire',x:9.4999151,y:-2.4999151,width:.25,layer:'bottom'},
  {route_type:'wire',x:9.4999151,y:0,width:.25,layer:'bottom'},
  {route_type:'wire',x:-2,y:-9.4,width:.11,layer:'bottom'},
 ]
 for(const point of expectedNegative)if(point.route_type==='wire')point.is_inside_copper_pour=true
 assert.equal(canonical(b.clean(negative.route)),canonical(expectedNegative),'Unexpected negative battery branch change')
 assert.equal(JSON.parse(b.copper(negative)).net,'GND')
 const extra=current.filter(e=>e.type==='pcb_via'&&[15.550007,10].some(x=>Math.hypot(e.x-x,e.y+3)<1e-7))
 assert.equal(extra.length,2);for(const v of extra){assert.equal(v.hole_diameter,.3);assert.equal(v.outer_diameter,.55);assert.deepEqual(v.layers,['top','bottom']);assert.equal(JSON.parse(b.copper(v)).net,'GND')}
 assert.deepEqual(sorted(current.filter(e=>e.type==='pcb_via'&&!extra.includes(e)),b.copper),sorted(old.filter(e=>e.type==='pcb_via'),a.copper),'Unrelated via geometry/net changed')
 assert(!current.some(e=>e.type.endsWith('_error')),'Build errors remain')
 for(const name of ['SW1','R5','C17'])assert(!current.some(e=>e.type==='source_component'&&e.name===name))
 assert(!current.some(e=>e.type==='source_net'&&e.name==='CAP_PRESS'))
 assert(current.some(e=>e.type==='source_port'&&b.source.get(e.source_component_id)==='U1'&&e.pin_number===41&&e.do_not_connect))
 return {passed:true,comparison_commit:comparisonCommit,retained_unchanged_fitted_components:27,fitted_components:28,changed_holder:'C7525448 BS-24-B4AA014',changed_battery_branch_traces:2,added_through_vias:2,unchanged_other_copper:true,all_electrical_connectivity_and_pin_attributes_preserved:true,mounting_holes:{count:4,diameter_mm:2.2,pitch_radius_mm:16.6},firmware_provided:false}
}
export function runCr2450Check(){
 const report=verifyCr2450Circuit(json(process.argv[2]??'dist/index/circuit.json'))
 const files=['validation/check-cr2450-circuit.mjs','index.circuit.tsx','parts.tsx','passives.tsx','routing.ts','routing-contract.json','routed-paths.json','dist/index/circuit.json','published.circuit.json','mechanical/battery-holder-courtyard.json']
 report.source_sha256=Object.fromEntries(files.map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]))
 writeFileSync('validation/cr2450-circuit-audit.json',JSON.stringify(report,null,2)+'\n')
 console.log('Pass: CR2450 holder, two bounded battery branches and two vias;27 other fitted parts, all other copper, connectivity and pin attributes preserved')
}
if(import.meta.main)runCr2450Check()
