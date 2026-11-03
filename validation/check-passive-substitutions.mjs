import assert from 'node:assert/strict'
import {execFileSync} from 'node:child_process'
import {readFileSync,writeFileSync,existsSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {fittedComponentRecords} from './fitted-component-records.mjs'
import {records} from './check-cr2450-circuit.mjs'
import {verifyFreshRouting} from './check-fresh-routing.mjs'
import {substituteRecords,substitutions} from './passive-substitutions.mjs'
export const comparisonCommit='31c224875298f3c41c1698029c5d0f01bee24db3'
const baseline=()=>JSON.parse(execFileSync('git',['show',`${comparisonCommit}:published.circuit.json`],{maxBuffer:16e6}))
export function verifyPassiveSubstitutions(current,old=baseline()){
 assert.deepEqual(fittedComponentRecords(current),substituteRecords(fittedComponentRecords(old)),
  'Only six specified supplier identities and CAD paths may change; all lands, values and poses must remain identical')
 if(existsSync('validation/fresh-routing-reference.json')){
  const fresh=verifyFreshRouting(current)
  for(const s of substitutions)for(const ext of ['obj','step'])assert.deepEqual(readFileSync(`imports/${s.model}/${s.model}.${ext}`),readFileSync(`imports/${s.oldPart}/${s.oldPart}.${ext}`))
  return {...fresh,substitutions,changed_fitted_identities:6,all_28_values_lands_poses_preserved:true,all_routed_traces_pads_vias_connectivity_layers_masks_preserved:false,approved_fresh_routing:true,supplier_obj_step_bytes_identical:true,L2_tolerance:{before_percent:2,after_percent:5,RF_qualification_required:true},stock_reserved:false}
 }
 const a=records(old),b=records(current)
 assert.deepEqual(b.connections,a.connections,'Connectivity or routing constraints changed')
 assert.deepEqual(b.portAttributes,a.portAttributes,'Electrical pin attributes changed')
 for(const type of ['pcb_board','pcb_trace','pcb_via','pcb_hole','pcb_plated_hole','pcb_smtpad','pcb_port']){
  const items=(c,r)=>c.filter(e=>e.type===type).map(e=>{
   const v=JSON.parse(r.copper(e))
   if(e.type==='pcb_copper_pour')v.net=c.find(n=>n.type==='source_net'&&n.source_net_id===e.source_net_id)?.name
   return JSON.stringify(v)
  }).sort()
  assert.deepEqual(items(current,b),items(old,a),type+': physical geometry, net, layer or mask changed')
 }
 // A separate fail-closed check approves only the later NPTH ground-pour trim.
 const holeAudit=JSON.parse(execFileSync('python',['validation/check-npth-copper.py','--stdin'],{input:JSON.stringify({before:old,current}),maxBuffer:16e6}))
 assert(holeAudit.passed)
 assert(!current.some(e=>e.type.endsWith('_error')),'Build errors remain')
 // Supplier models really are identical, rather than merely sharing a package label.
 for(const s of substitutions)for(const ext of ['obj','step'])assert.deepEqual(
  readFileSync(`imports/${s.model}/${s.model}.${ext}`),readFileSync(`imports/${s.oldPart}/${s.oldPart}.${ext}`),
  `Supplier ${ext} geometry changed: ${s.id}`)
 return {passed:true,comparison_commit:comparisonCommit,substitutions,changed_fitted_identities:6,
  all_28_values_lands_poses_preserved:true,all_routed_traces_pads_vias_connectivity_layers_masks_preserved:true,
  approved_npth_ground_pour_trim:holeAudit,
  supplier_obj_step_bytes_identical:true,
  L2_tolerance:{before_percent:2,after_percent:5,RF_qualification_required:true},
  stock_reserved:false,physical_tested:false}
}
if(import.meta.main){
 const report=verifyPassiveSubstitutions(JSON.parse(readFileSync('published.circuit.json')))
 const sha=bytes=>createHash('sha256').update(bytes).digest('hex')
 let retained=[]
 const pushfit=JSON.parse(readFileSync('mechanical/enclosure-parameters.json')).cap_retention?.mode==='push_fit'
 if(pushfit){
  const cad=JSON.parse(readFileSync('validation/pushfit-cad-audit.json'));assert(cad.passed&&!cad.physical_tested&&cad.product_rigid_parts===2&&cad.nominal_diametral_interference_mm===.05)
  for(const [p,h]of Object.entries(cad.source_sha256))assert.equal(sha(readFileSync(p)),h,'Stale bounded push-fit CAD proof: '+p)
  report.approved_mechanical_revision=`Two-part push fit; exact CAD audit vs ${cad.comparison_commit}`
  report.retained_print_evidence={new_slicer_execution:true,report:'validation/print-readiness.json'}
 }else{
  const prior=path=>execFileSync('git',['show',`${comparisonCommit}:${path}`],{maxBuffer:32e6})
  const tracked=execFileSync('git',['ls-tree','-r','--name-only',comparisonCommit],{encoding:'utf8'}).trim().split('\n')
  retained=tracked.filter(p=>/^mechanical\/(Print_STL|STEP_Parts)\//.test(p)&&/\.(stl|step)$/.test(p))
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
 }
 const paths=['published.circuit.json','passives.tsx','validation/passive-substitutions.mjs','validation/check-passive-substitutions.mjs','validation/jlc-imports.json',...substitutions.flatMap(s=>['tsx','obj','step'].map(ext=>`imports/${s.model}/${s.model}.${ext}`))]
 if(report.approved_fresh_routing)paths.push('validation/check-fresh-routing.mjs','validation/fresh-routing-reference.json')
 paths.push(...retained,'dist/index/3d.glb',...(pushfit?['validation/pushfit-cad-audit.json','mechanical/enclosure-parameters.json']:[]))
 report.source_sha256=Object.fromEntries(paths.map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]))
 writeFileSync('validation/passive-substitution-audit.json',JSON.stringify(report,null,2)+'\n')
 console.log(report.approved_fresh_routing?'PASS: six sourcing substitutions and all28 fitted geometries retained; explicit approved fresh routing verified':'PASS: six substitutions; previous copper and fitted geometry retained')
}
