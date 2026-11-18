import assert from 'node:assert/strict'
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs'
import {verifyNordicElectrical} from './nordic-electrical-revision.mjs'

export function verifyDevice(c){
  assert(!c.some(e=>e.type.endsWith('_error')),'Circuit has errors')
  const sources=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e]))
  const fitted=c.filter(e=>e.type==='pcb_component'&&!e.do_not_place&&sources.has(e.source_component_id))
  assert.equal(fitted.length,27,'Expected 27 fitted electronics')
  const holes=c.filter(e=>e.type==='pcb_hole')
  assert.equal(holes.length,4)
  for(const hole of holes){
    assert.equal(hole.hole_diameter,2.2)
    assert(Math.abs(Math.hypot(hole.x,hole.y)-16.6)<1e-6,'Mounting hole moved')
  }
  const sensor=fitted.find(e=>sources.get(e.source_component_id).name==='U2')
  assert.deepEqual(sensor.center,{x:0,y:0},'Hall sensor must be centered')
  const parts=[...sources.values()].filter(e=>e.name.startsWith('BEARING_V5_'))
  assert.equal(parts.length,7,'Enclosure assembly changed')
  for(const name of ['Base_V3_Discs','Cell','Attachment_Discs_V3','PCB_Fasteners','Bearing_6808','Magnet']){
    const source=parts.find(e=>e.name==='BEARING_V5_'+name);assert(source,name)
    const cad=c.find(e=>e.type==='cad_component'&&e.source_component_id===source.source_component_id)
    assert.equal(cad.model_glb_url,'./mechanical/models/'+name+'.glb')
    assert.deepEqual(cad.position,{x:0,y:0,z:-11.1})
  }
  verifyNordicElectrical(c)
  return {passed:true,fitted_components:27,mounting_holes:4,mechanical_models:7}
}
if(import.meta.main){
  const c=JSON.parse(readFileSync('dist/index/circuit.json'))
  const report=verifyDevice(c)
  mkdirSync('dist/validation',{recursive:true})
  writeFileSync('dist/validation/device.json',JSON.stringify(report,null,2)+'\n')
  console.log('PASS: current RevC electronics, screw mounts, centered Hall sensor and enclosure assembly')
}
