import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {verifyDevice} from './check-device.mjs'

const current=()=>JSON.parse(readFileSync('dist/index/circuit.json'))
test('freshly compiled device satisfies the current design constraints',()=>{
  expect(verifyDevice(current()).fitted_components).toBe(27)
})
test('rejects a moved board mounting hole',()=>{
  const c=current();c.find(e=>e.type==='pcb_hole').x+=.1
  expect(()=>verifyDevice(c)).toThrow()
})
test('rejects a displaced Hall sensor',()=>{
  const c=current(),s=c.find(e=>e.type==='source_component'&&e.name==='U2')
  c.find(e=>e.type==='pcb_component'&&e.source_component_id===s.source_component_id).center.x=.1
  expect(()=>verifyDevice(c)).toThrow()
})
test('rejects an enclosure part positioned in a different coordinate frame',()=>{
  const c=current(),s=c.find(e=>e.type==='source_component'&&e.name==='BEARING_V5_Base_V3_Discs')
  c.find(e=>e.type==='cad_component'&&e.source_component_id===s.source_component_id).position.z+=1
  expect(()=>verifyDevice(c)).toThrow()
})
