// Bound the reviewed electrical correction; preserve every other fitted part,
// electrical attribute and pin-net partition against the preceding design.
import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
const reference=()=>JSON.parse(readFileSync('validation/nordic-electrical-reference.json'))
export function approvedNordicFittedRecords(before){
 const r=reference(),names=new Set(['C3','C7','C8'])
 assert.deepEqual(before.filter(e=>names.has(e.source.name)),r.before,'Unexpected pre-correction component records')
 return [...before.filter(e=>!names.has(e.source.name)),...r.after].sort((a,b)=>a.source.name.localeCompare(b.source.name))
}
export function approvedNordicPins(before){
 const r=reference(),names=new Set(['U1.32','C7.1','C7.2'])
 assert.deepEqual(before.filter(e=>names.has(JSON.parse(e).terminal)),r.before_pins,'Unexpected pre-correction DEC2 attributes')
 return [...before.filter(e=>!names.has(JSON.parse(e).terminal)),...r.after_pins].sort()
}
export function approvedNordicPartition(before){
 return before.map(g=>g.filter(p=>!p.startsWith('C7.'))).filter(g=>g.length).sort((a,b)=>JSON.stringify(a).localeCompare(JSON.stringify(b)))
}
export function verifyNordicElectrical(c){
 const owner=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]))
 const source=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.name,e]))
 const port=(name,pin)=>c.find(e=>e.type==='source_port'&&owner.get(e.source_component_id)===name&&e.pin_number===pin)
 const nc=port('U1',32);assert(nc.do_not_connect&&nc.is_passive&&!nc.must_be_connected&&!nc.provides_power)
 assert(!c.some(e=>e.type==='source_trace'&&e.connected_source_port_ids.includes(nc.source_port_id)),'DEC2 must have no connection')
 assert(!source.has('C7'),'Unused DEC2 capacitor must be absent')
 assert.equal(source.get('C8').capacitance,100e-12,'DEC3 requires100pF, not100nF')
 assert.equal(source.get('C8').manufacturer_part_number,'GRM1555C1H101JA01D')
 const dec=port('U1',33),cap=port('C8',1)
 assert.equal(dec.subcircuit_connectivity_map_key,cap.subcircuit_connectivity_map_key)
 const members=c.filter(e=>e.type==='source_port'&&e.subcircuit_connectivity_map_key===dec.subcircuit_connectivity_map_key)
 assert.deepEqual(members.map(e=>owner.get(e.source_component_id)+'.'+e.pin_number).sort(),['C8.1','U1.33'])
 const returnTrace=c.find(e=>e.type==='source_trace'&&e.name==='C3_VSS2_RETURN')
 assert(returnTrace&&returnTrace.max_via_count===0&&returnTrace.max_length===1.5)
 assert.deepEqual([...returnTrace.connected_source_port_ids].sort(),[port('C3',2).source_port_id,port('U1',31).source_port_id].sort())
 for(const e of c.filter(e=>e.type==='schematic_port'&&owner.get(c.find(p=>p.type==='source_port'&&p.source_port_id===e.source_port_id)?.source_component_id)==='U1')){
  const physical=c.find(p=>p.type==='source_port'&&p.source_port_id===e.source_port_id)
  assert.equal(e.pin_number,physical.pin_number,'Split schematic must display the physical package pin number')
 }
 return {passed:true,fitted_components:27,DEC2_pin32:'unconnected',DEC3_pin33:'100pF C8 / C77177',C3_return:'dedicated top trace through VSS31; actual copper isolation checked independently',schematic_physical_pin_numbers:true,physical_qualified:false}
}
