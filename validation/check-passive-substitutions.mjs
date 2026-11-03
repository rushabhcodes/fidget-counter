import assert from 'node:assert/strict'
import {execFileSync} from 'node:child_process'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {fittedComponentRecords} from './fitted-component-records.mjs'
import {records} from './check-cr2450-circuit.mjs'
import {substituteRecords,substitutions} from './passive-substitutions.mjs'
export const comparisonCommit='31c224875298f3c41c1698029c5d0f01bee24db3'
const baseline=()=>JSON.parse(execFileSync('git',['show',`${comparisonCommit}:published.circuit.json`],{maxBuffer:16e6}))
export function verifyPassiveSubstitutions(current,old=baseline()){
 assert.deepEqual(fittedComponentRecords(current),substituteRecords(fittedComponentRecords(old)),
  'Only six specified supplier identities and CAD paths may change; all lands, values and poses must remain identical')
 const a=records(old),b=records(current)
 assert.deepEqual(b.connections,a.connections,'Connectivity or routing constraints changed')
 assert.deepEqual(b.portAttributes,a.portAttributes,'Electrical pin attributes changed')
 for(const type of ['pcb_board','pcb_trace','pcb_via','pcb_hole','pcb_plated_hole','pcb_smtpad','pcb_port','pcb_copper_pour']){
  const items=(c,r)=>c.filter(e=>e.type===type).map(e=>{
   const v=JSON.parse(r.copper(e))
   if(e.type==='pcb_copper_pour')v.net=c.find(n=>n.type==='source_net'&&n.source_net_id===e.source_net_id)?.name
   return JSON.stringify(v)
  }).sort()
  assert.deepEqual(items(current,b),items(old,a),type+': physical geometry, net, layer or mask changed')
 }
 assert(!current.some(e=>e.type.endsWith('_error')),'Build errors remain')
 // Supplier models really are identical, rather than merely sharing a package label.
 for(const s of substitutions)for(const ext of ['obj','step'])assert.deepEqual(
  readFileSync(`imports/${s.model}/${s.model}.${ext}`),readFileSync(`imports/${s.oldPart}/${s.oldPart}.${ext}`),
  `Supplier ${ext} geometry changed: ${s.id}`)
 return {passed:true,comparison_commit:comparisonCommit,substitutions,changed_fitted_identities:6,
  all_28_values_lands_poses_preserved:true,all_copper_connectivity_layers_masks_preserved:true,
  supplier_obj_step_bytes_identical:true,printed_geometry_changed:false,
  L2_tolerance:{before_percent:2,after_percent:5,RF_qualification_required:true},
  stock_reserved:false,physical_tested:false}
}
if(import.meta.main){
 const report=verifyPassiveSubstitutions(JSON.parse(readFileSync('published.circuit.json')))
 const sha=bytes=>createHash('sha256').update(bytes).digest('hex')
 const prior=path=>execFileSync('git',['show',`${comparisonCommit}:${path}`],{maxBuffer:32e6})
 const tracked=execFileSync('git',['ls-tree','-r','--name-only',comparisonCommit],{encoding:'utf8'}).trim().split('\n')
 const retained=tracked.filter(p=>/^mechanical\/(Print_STL|STEP_Parts)\//.test(p)&&/\.(stl|step)$/.test(p))
 retained.push('mechanical/build_enclosure.py','mechanical/enclosure-parameters.json','validation/print-readiness.json','previews/bearing-layout.png')
 report.retained_geometry_sha256=Object.fromEntries(retained.map(p=>{
  const bytes=readFileSync(p);assert.deepEqual(bytes,prior(p),'Unexpected printed geometry or retained evidence change: '+p)
  return [p,sha(bytes)]
 }))
 const slicing=JSON.parse(readFileSync('validation/print-readiness.json'))
 assert(slicing.passed&&slicing.actual_slicer_executed&&!slicing.physical_tested)
 for(const [p,h] of Object.entries(slicing.source_sha256))assert.equal(sha(readFileSync(p)),h,'Stale retained slicer input: '+p)
 for(const part of slicing.parts){assert.equal(part.slicer_exit_code,0);assert.equal(part.slicer_warnings.length,0)}
 assert.equal(sha(readFileSync('dist/index/3d.glb')),JSON.parse(prior('cloud-assets/manifest.json')).artifacts.find(a=>a.output==='dist/published/3d.glb').sha256,'Rendered assembly geometry changed')
 report.retained_print_evidence={slicer:slicing.slicer,parts:slicing.parts_checked,new_slicer_execution:false,reason:'All manufacturing exports and slicer inputs byte-identical to 1.0.26; prior toolpaths retained'}
 const paths=['published.circuit.json','passives.tsx','validation/passive-substitutions.mjs','validation/check-passive-substitutions.mjs','validation/jlc-imports.json',...substitutions.flatMap(s=>['tsx','obj','step'].map(ext=>`imports/${s.model}/${s.model}.${ext}`))]
 paths.push(...retained,'dist/index/3d.glb')
 report.source_sha256=Object.fromEntries(paths.map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]))
 writeFileSync('validation/passive-substitution-audit.json',JSON.stringify(report,null,2)+'\n')
 console.log('PASS: six exact sourcing substitutions; every land, value, pose, net, copper region and layer preserved; supplier CAD bytes identical')
}
