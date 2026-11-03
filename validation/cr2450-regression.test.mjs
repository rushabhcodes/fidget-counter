import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {verifyCr2450Circuit} from './check-cr2450-circuit.mjs'
const current=()=>JSON.parse(readFileSync('dist/index/circuit.json'))
test('accepts only the specified CR2450 circuit revision',()=>{
 expect(verifyCr2450Circuit(current()).unchanged_other_copper).toBe(true)
})
test('rejects moved unrelated components',()=>{
 const c=current();c.find(e=>e.type==='pcb_component'&&e.layer==='top'&&!e.do_not_place).center.x+=.01
 expect(()=>verifyCr2450Circuit(c)).toThrow()
})
test('rejects unrelated copper width and layer changes',()=>{
 for(const field of ['width','layer']){
  const c=current(),t=c.find(e=>e.type==='pcb_trace'&&!e.pcb_trace_id.includes('holder'))
  if(field==='width')t.route.find(e=>e.route_type==='wire').width+=.01
  else t.route.find(e=>e.route_type==='wire').layer='changed-layer'
  expect(()=>verifyCr2450Circuit(c)).toThrow()
 }
})
test('rejects changed battery branch geometry',()=>{
 const c=current();c.find(e=>e.type==='pcb_trace'&&e.pcb_trace_id==='source_net_0_holder_0').route[1].x+=.01
 expect(()=>verifyCr2450Circuit(c)).toThrow()
})
test('rejects changed mounting drills',()=>{
 const c=current();c.find(e=>e.type==='pcb_hole').hole_diameter+=.1
 expect(()=>verifyCr2450Circuit(c)).toThrow()
})
test('rejects changed source connectivity',()=>{
 const c=current(),a=c.find(e=>e.type==='source_trace'&&e.connected_source_port_ids.length)
 a.connected_source_port_ids=[]
 expect(()=>verifyCr2450Circuit(c)).toThrow()
})
test('rejects changed added-via layers',()=>{
 const c=current();c.find(e=>e.type==='pcb_via'&&e.x===10&&e.y===-3).layers=['top']
 expect(()=>verifyCr2450Circuit(c)).toThrow()
})
