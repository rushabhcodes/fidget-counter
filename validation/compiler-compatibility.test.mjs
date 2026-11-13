import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {normalizeCompilerOutput} from './normalize-compiler-output.mjs'
const raw=()=>JSON.parse(readFileSync('work/compiler-upgrade/raw-circuit.json'))
const approved=JSON.parse(readFileSync('mechanical/variants/V1_premade_ring/source/published.circuit.json'))
test('latest compiler preserves every approved PCB record after the bounded schema transition',()=>{
  expect(normalizeCompilerOutput(raw()).filter(e=>e.type.startsWith('pcb_'))).toEqual(approved.filter(e=>e.type.startsWith('pcb_')))
})
test('compiler compatibility rejects a moved fitted pad',()=>{
  const c=raw();c.find(e=>e.type==='pcb_smtpad').x+=.01
  expect(()=>normalizeCompilerOutput(c)).toThrow()
})
test('compiler compatibility rejects changed trace geometry',()=>{
  const c=raw(),trace=c.find(e=>e.type==='pcb_trace'&&e.route.some(p=>p.route_type==='wire'))
  trace.route.find(p=>p.route_type==='wire').x+=.01
  expect(()=>normalizeCompilerOutput(c)).toThrow()
})
test('compiler compatibility rejects an unrecognized copper fill',()=>{
  const c=raw();c.find(e=>e.type==='pcb_copper_pour').brep_shape.outer_ring.vertices[0].x+=.01
  expect(()=>normalizeCompilerOutput(c)).toThrow()
})
test('compiler compatibility rejects changed silkscreen offsets and pin aliases',()=>{
  const c=raw();c.find(e=>e.type==='pcb_component').display_offset_x='0.123mm'
  expect(()=>normalizeCompilerOutput(c)).toThrow()
  const p=raw(),owner=p.find(e=>e.type==='source_component'&&e.name==='L1').source_component_id
  p.find(e=>e.type==='source_port'&&e.source_component_id===owner&&e.pin_number===2).port_hints.push('unexpected')
  expect(()=>normalizeCompilerOutput(p)).toThrow()
})
test('compiler compatibility rejects removed physical records',()=>{
  const c=raw(),i=c.findIndex(e=>e.type==='pcb_hole');c.splice(i,1)
  expect(()=>normalizeCompilerOutput(c)).toThrow()
})
