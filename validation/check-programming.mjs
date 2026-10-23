import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {gerberCompatibleCircuit} from '../gerber-compat.mjs'
const input=process.argv[2]??'dist/index/circuit.json'
const bytes=readFileSync(input),circuit=JSON.parse(bytes)
const all=type=>circuit.filter(e=>e.type===type)
const source=all('source_component').find(e=>e.name==='J_DEBUG')
assert(source,'Missing TC2030 interface')
assert(!all('source_component').some(e=>/^TP_(VDD|GND|SWDIO|SWDCLK|RESET)$/.test(e.name)),'Old custom row remains')
const pcb=all('pcb_component').find(e=>e.source_component_id===source.source_component_id)
assert.equal(pcb.layer,'top');assert(pcb.do_not_place)
assert.deepEqual(pcb.center,{x:0,y:-13.3})
const ports=all('source_port').filter(e=>e.source_component_id===source.source_component_id)
const nets=all('source_net')
const expected=['VBAT','SWDIO','NRESET','SWDCLK','GND',undefined]
const coords=[[-1.27,-13.935],[-1.27,-12.665],[0,-13.935],[0,-12.665],[1.27,-13.935],[1.27,-12.665]]
const pads=all('pcb_smtpad').filter(e=>e.pcb_component_id===pcb.pcb_component_id)
assert.equal(pads.length,6)
const near=(a,b)=>assert(Math.abs(a-b)<1e-6,`${a} differs from ${b}`)
const reports=[]
for(let i=1;i<=6;i++) {
 const port=ports.find(e=>e.pin_number===i)
 const pp=all('pcb_port').find(e=>e.source_port_id===port.source_port_id)
 const pad=pads.find(e=>e.pcb_port_id===pp.pcb_port_id)
 assert.equal(pad.shape,'circle');near(pad.radius,.3937);assert.equal(pad.layer,'top')
 near(pad.x,coords[i-1][0]);near(pad.y,coords[i-1][1])
 const net=nets.find(n=>n.subcircuit_connectivity_map_key===port.subcircuit_connectivity_map_key)
 assert.equal(net?.name,expected[i-1],`Wrong programmer contact ${i}`)
 if(i===6) {
  assert(port.do_not_connect)
  assert(!all('source_trace').some(t=>t.connected_source_port_ids?.includes(port.source_port_id)),'5 V contact has a trace')
 }
 reports.push({pin:i,signal:port.name,net:net?.name??'NC',x:pad.x,y:pad.y,diameterMm:pad.radius*2})
}
const holes=all('pcb_hole').filter(e=>e.pcb_component_id===pcb.pcb_component_id)
assert.equal(holes.length,3)
for(const [x,y] of [[-2.54,-13.3],[2.54,-12.284],[2.54,-14.316]]) {
 const hole=holes.find(h=>Math.hypot(h.x-x,h.y-y)<1e-6)
 assert(hole);near(hole.hole_diameter,.9906)
}
assert(!all('pcb_plated_hole').some(e=>e.pcb_component_id===pcb.pcb_component_id))
const padIds=new Set(pads.map(e=>e.pcb_smtpad_id))
assert(!gerberCompatibleCircuit(circuit).some(e=>e.type==='pcb_solder_paste'&&padIds.has(e.pcb_smtpad_id)),'Contact pad receives stencil paste')
const idToSource=new Map(all('source_trace').map(e=>[e.source_trace_id,e]))
const mcu=all('source_component').find(e=>e.name==='U1')
for(const [pin,name] of [[24,'NRESET'],[25,'SWDCLK'],[26,'SWDIO']]) {
 const sp=all('source_port').find(e=>e.source_component_id===mcu.source_component_id&&e.pin_number===pin)
 assert.equal(nets.find(n=>n.subcircuit_connectivity_map_key===sp.subcircuit_connectivity_map_key)?.name,name)
}
const distance=(p,a,b)=>{
 const dx=b.x-a.x,dy=b.y-a.y
 const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy||1)))
 return Math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy)
}
let minimumUnrelatedTopTrackClearanceMm=Infinity
for(const t of all('pcb_trace')) {
 const key=idToSource.get(t.source_trace_id)?.subcircuit_connectivity_map_key
 assert(key,`Trace ${t.pcb_trace_id} lacks connectivity identity`)
 for(const pad of pads) {
  const pp=all('pcb_port').find(e=>e.pcb_port_id===pad.pcb_port_id)
  const sp=ports.find(e=>e.source_port_id===pp.source_port_id)
  if(sp.subcircuit_connectivity_map_key===key)continue
  for(let i=1;i<t.route.length;i++) {
   const a=t.route[i-1],b=t.route[i]
   if(a.route_type!=='wire'||b.route_type!=='wire'||a.layer!=='top'||b.layer!=='top')continue
   const gap=distance(pad,a,b)-pad.radius-Math.max(a.width,b.width)/2
   minimumUnrelatedTopTrackClearanceMm=Math.min(minimumUnrelatedTopTrackClearanceMm,gap)
   assert(gap>=.508-1e-6,`Contact ${sp.pin_number} is only ${gap} mm from unrelated trace ${t.pcb_trace_id}`)
  }
 }
}
let minimumUnrelatedViaClearanceMm=Infinity
for(const via of all('pcb_via').filter(e=>e.layers.includes('top')))for(const pad of pads) {
 const pp=all('pcb_port').find(e=>e.pcb_port_id===pad.pcb_port_id)
 const sp=ports.find(e=>e.source_port_id===pp.source_port_id)
 if(sp.subcircuit_connectivity_map_key===via.subcircuit_connectivity_map_key)continue
 const gap=Math.hypot(via.x-pad.x,via.y-pad.y)-via.outer_diameter/2-pad.radius
 minimumUnrelatedViaClearanceMm=Math.min(minimumUnrelatedViaClearanceMm,gap)
 assert(gap>=.508-1e-6,`Contact ${sp.pin_number} is only ${gap} mm from an unrelated via`)
}
const courtyard=all('pcb_courtyard_rect').find(e=>e.pcb_component_id===pcb.pcb_component_id)
assert(courtyard,'Missing probe-access courtyard');near(courtyard.width,10.4);near(courtyard.height,7.8)
const other=all('pcb_component').filter(e=>e.layer==='top'&&e.pcb_component_id!==pcb.pcb_component_id&&!e.do_not_place&&all('source_component').some(s=>s.source_component_id===e.source_component_id))
const corners=[[-5.2,-17.2],[5.2,-17.2],[-5.2,-9.4],[5.2,-9.4]]
for(const [x,y] of corners)assert(Math.hypot(x,y)<18.25-.25,'Probe courtyard extends beyond board clearance')
for(const e of other)assert(Math.abs(e.center.x)>(5.2+e.width/2)||Math.abs(e.center.y+13.3)>(3.9+e.height/2),`Probe courtyard overlaps ${e.pcb_component_id}`)
const pkg=JSON.parse(readFileSync('package.json'))
assert.equal(pkg.dependencies['@tsci/tscircuit.standard-jst-programmer'],'0.8.0')
assert(!all('cad_component').some(e=>e.source_component_id===source.source_component_id),'Bare interface has a fitted 3D part')
const crystalBranches=all('source_trace').filter(e=>e.max_length===10&&e.max_via_count===0).map(source=>{
 const routes=all('pcb_trace').filter(e=>e.source_trace_id===source.source_trace_id)
 assert(routes.length,`Missing crystal route ${source.name}`)
 let lengthMm=0
 for(const t of routes)for(let i=1;i<t.route.length;i++) {
  const a=t.route[i-1],b=t.route[i]
  assert(a.route_type==='wire'&&b.route_type==='wire',`Via in crystal route ${source.name}`)
  lengthMm+=Math.hypot(b.x-a.x,b.y-a.y)
 }
 assert(lengthMm<=10,`Crystal route ${source.name} exceeds 10 mm`)
 return {name:source.name,lengthMm,vias:0}
})
assert.equal(crystalBranches.length,8)
const issues=circuit.filter(e=>/error|warning/.test(e.type))
assert.equal(issues.length,0,JSON.stringify(issues))
const result={checkedAt:new Date().toISOString(),passed:true,sourcePackage:'@tsci/tscircuit.standard-jst-programmer@0.8.0',
 reference:'https://tscircuit--standard-jst-programmer-v0-8-0.tscircuit.app/#file=circuits%2Fupward.circuit.tsx',
 footprint:'TC2030-NL-FP Rev B',cable:'TC2030-IDC-NL-050',side:'top',pads:reports,alignmentHoles:holes,
 stencilApertures:0,pin6Isolated:true,power:'Pin 1 supplies fixed 3.3 V to VBAT; CR2032 must be removed',
 minimumUnrelatedTopTrackClearanceMm,minimumUnrelatedViaClearanceMm,crystalBranches,probeCourtyardMm:[10.4,7.8],probeCourtyardClear:true,
 circuitSha256:createHash('sha256').update(bytes).digest('hex'),physicalProbeFitTested:false,physicalProgrammingTested:false}
writeFileSync('validation/programming-interface.json',JSON.stringify(result,null,2)+'\n')
console.log('Pass: exact six-contact/three-hole TC2030 geometry, programmer pinout, isolated 5 V contact, zero stencil paste and clear probe courtyard')
