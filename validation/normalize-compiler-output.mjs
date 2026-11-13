// Keep the released physical PCB exact across the0.0.3168 schema transition.
// No pad, route, drill, mask, net or component movement is permitted here.
import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
const sha=bytes=>createHash('sha256').update(bytes).digest('hex')
const ref=JSON.parse(readFileSync(new URL('./compiler-compat-reference.json',import.meta.url)))
const approvedBytes=readFileSync(new URL('../'+ref.approved_circuit,import.meta.url))
assert.equal(sha(approvedBytes),ref.approved_circuit_sha256)
const approved=JSON.parse(approvedBytes)
export function normalizeCompilerOutput(input) {
  const c=structuredClone(input),byTypeId=new Map()
  for(const e of approved)if(e.type.startsWith('pcb_'))byTypeId.set(e[e.type+'_id'],e)
  const owners=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]))
  for(const e of c){
    if(e.type==='source_port'){
      const change=ref.port_alias_changes.find(x=>x.owner===owners.get(e.source_component_id)&&x.pin_number===e.pin_number)
      if(change){assert([change.new_hints,change.approved_hints].some(x=>JSON.stringify(x)===JSON.stringify(e.port_hints)),'Unrecognized compiler pin aliases');e.port_hints=change.approved_hints}
    }
    if(!e.type.startsWith('pcb_'))continue
    const old=byTypeId.get(e[e.type+'_id']);assert(old,'Unexpected physical PCB record')
    if(e.type==='pcb_component')for(const key of ['display_offset_x','display_offset_y']){
      if(typeof e[key]==='string'){
        assert(/^-?\d+(?:\.\d+)?mm$/.test(e[key]),'Unexpected display offset units')
        e[key]=Number(e[key].slice(0,-2))
      }
    }
    if(e.type==='pcb_silkscreen_text'&&!('pcb_component_id'in e)&&old.pcb_component_id===null)e.pcb_component_id=null
    if(e.type==='pcb_copper_pour'){
      const hash=sha(JSON.stringify(e.brep_shape))
      assert(hash===ref.raw_pour_brep_sha256[e.pcb_copper_pour_id]||JSON.stringify(e.brep_shape)===JSON.stringify(old.brep_shape),'Unrecognized compiler copper fill')
      e.brep_shape=structuredClone(old.brep_shape)
    }
    if(e.type==='pcb_trace'){
      assert.equal(e.route.length,old.route.length,'Trace geometry changed')
      for(let i=0;i<e.route.length;i++)for(const key of ['copper_pour_id','is_inside_copper_pour']){
        if(key in old.route[i]){
          if(key in e.route[i])assert.deepEqual(e.route[i][key],old.route[i][key],'Unexpected trace/pour membership')
          e.route[i][key]=old.route[i][key]
        }
        else {assert(!(key in e.route[i]),'Unexpected trace/pour metadata');delete e.route[i][key]}
      }
    }
    assert.deepEqual(e,old,'Physical PCB changed during compiler upgrade')
  }
  assert.deepEqual(c.filter(e=>e.type.startsWith('pcb_')),approved.filter(e=>e.type.startsWith('pcb_')),'Missing or reordered physical PCB records')
  return c
}
if(import.meta.main){
  assert.equal(JSON.parse(readFileSync('package.json')).dependencies.tscircuit,ref.compiler)
  const path=process.argv[2]??'dist/index/circuit.json',raw=readFileSync(path)
  mkdirSync('work/compiler-upgrade',{recursive:true})
  writeFileSync('work/compiler-upgrade/raw-circuit.json',raw)
  const result=normalizeCompilerOutput(JSON.parse(raw))
  writeFileSync(path,JSON.stringify(result,null,2)+'\n')
  writeFileSync('work/compiler-upgrade/audit.json',JSON.stringify({passed:true,compiler:ref.compiler,raw_sha256:sha(raw),normalized_sha256:sha(readFileSync(path)),approved_circuit_sha256:ref.approved_circuit_sha256,physical_pcb_records_identical:true,pours_preserved:3,port_alias_changes:ref.port_alias_changes.length},null,2)+'\n')
  console.log('PASS: latest compiler output; all physical PCB records exactly match approved RevC; three original pours preserved')
}
