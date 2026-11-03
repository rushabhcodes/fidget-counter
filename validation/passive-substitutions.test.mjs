import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {verifyPassiveSubstitutions} from './check-passive-substitutions.mjs'
const current=()=>JSON.parse(readFileSync('published.circuit.json'))
test('accepts only the six approved sourcing substitutions',()=>expect(verifyPassiveSubstitutions(current()).changed_fitted_identities).toBe(6))
test('rejects wrong replacement SKU or electrical value',()=>{
 for(const key of ['supplier_part_numbers','capacitance']){
  const c=current(),s=c.find(e=>e.type==='source_component'&&e.name==='C1')
  s[key]=key==='capacitance'?999:{jlcpcb:['C76948']}
  expect(()=>verifyPassiveSubstitutions(c)).toThrow()
 }
})
test('rejects moved or resized replacement lands and changed layers',()=>{
 for(const key of ['x','width','layer']){
  const c=current(),s=c.find(e=>e.type==='source_component'&&e.name==='L2'),p=c.find(e=>e.type==='pcb_component'&&e.source_component_id===s.source_component_id),pad=c.find(e=>e.type==='pcb_smtpad'&&e.pcb_component_id===p.pcb_component_id)
  pad[key]=key==='layer'?'bottom':pad[key]+.01
  expect(()=>verifyPassiveSubstitutions(c)).toThrow()
 }
})
test('rejects replacement CAD offset changes',()=>{
 const c=current(),s=c.find(e=>e.type==='source_component'&&e.name==='C10')
 c.find(e=>e.type==='cad_component'&&e.source_component_id===s.source_component_id).model_origin_position.z+=.01
 expect(()=>verifyPassiveSubstitutions(c)).toThrow()
})
test('rejects real copper, layer, net and mask changes',()=>{
 for(const kind of ['width','layer','net','mask']){
  const c=current()
  if(kind==='mask')c.find(e=>e.type==='pcb_copper_pour').covered_with_solder_mask=false
  else if(kind==='net')c.find(e=>e.type==='source_trace').connected_source_port_ids=[]
  else {const p=c.find(e=>e.type==='pcb_trace').route.find(e=>e.route_type==='wire');p[kind]=kind==='width'?p.width+.01:'changed-layer'}
  expect(()=>verifyPassiveSubstitutions(c)).toThrow()
 }
})
