import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {verifyNordicElectrical} from './nordic-electrical-revision.mjs'
const current=()=>JSON.parse(readFileSync('published.circuit.json'))
test('DEC2 is unconnected; DEC3 has the specified100pF; schematic uses package numbers',()=>{
 expect(verifyNordicElectrical(current()).fitted_components).toBe(27)
})
test('rejects a capacitor connection to DEC2 even when marked no-connect',()=>{
 const c=current(),u=c.find(e=>e.type==='source_component'&&e.name==='U1')
 const p=c.find(e=>e.type==='source_port'&&e.source_component_id===u.source_component_id&&e.pin_number===32)
 c.find(e=>e.type==='source_trace'&&e.name==='U1_DEC3').connected_source_port_ids.push(p.source_port_id)
 expect(()=>verifyNordicElectrical(c)).toThrow()
})
test('rejects the former100nF DEC3 value and wrong supplier identity',()=>{
 for(const field of ['capacitance','manufacturer_part_number']){
  const c=current(),p=c.find(e=>e.type==='source_component'&&e.name==='C8')
  p[field]=field==='capacitance'?100e-9:'GRM155R71C104KA88D'
  expect(()=>verifyNordicElectrical(c)).toThrow()
 }
})
test('rejects virtual schematic ordinals in place of physical package pin numbers',()=>{
 const c=current(),u=c.find(e=>e.type==='source_component'&&e.name==='U1')
 const p=c.find(e=>e.type==='source_port'&&e.source_component_id===u.source_component_id&&e.pin_number===33)
 c.find(e=>e.type==='schematic_port'&&e.source_port_id===p.source_port_id).pin_number=8
 expect(()=>verifyNordicElectrical(c)).toThrow()
})
