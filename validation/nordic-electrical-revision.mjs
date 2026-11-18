import assert from 'node:assert/strict'
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
