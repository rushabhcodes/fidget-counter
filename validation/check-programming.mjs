import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
import {gerberCompatibleCircuit} from '../gerber-compat.mjs'
const input=process.argv[2]??'dist/index/circuit.json'
const bytes=readFileSync(input),circuit=JSON.parse(bytes)
const all=type=>circuit.filter(e=>e.type===type)
const source=all('source_component').find(e=>e.name==='J_DEBUG')
assert(source,'Missing five-pin JST programming connector')
assert.equal(source.manufacturer_part_number,'SM05B-SRSS-TB(LF)(SN)')
assert.deepEqual(source.supplier_part_numbers.jlcpcb,['C136657'])
assert.equal(source.standard,'jst_sh');assert.equal(source.pin_count,5)
assert(!all('source_component').some(e=>/^TP_(VDD|GND|SWDIO|SWDCLK|RESET)$/.test(e.name)),'Old custom programming pads remain')
assert(!all('source_component').some(e=>/TC2030/.test(e.manufacturer_part_number??'')),'Old Tag-Connect interface remains')
const pcb=all('pcb_component').find(e=>e.source_component_id===source.source_component_id)
assert.equal(pcb.layer,'top');assert(!pcb.do_not_place);assert.equal(pcb.rotation,0)
assert.deepEqual(pcb.center,{x:0,y:-13.3})
assert(pcb.cable_insertion_center.y<pcb.center.y,'Cable entry must face the lower board edge')
const ports=all('source_port').filter(e=>e.source_component_id===source.source_component_id)
const nets=all('source_net')
const expected=['VBAT','SWDIO','GND','SWDCLK','NRESET']
const padXs=[-1.999615,-.998855,.000635,1.000125,2.000885]
const pads=all('pcb_smtpad').filter(e=>e.pcb_component_id===pcb.pcb_component_id)
const near=(a,b,tolerance=1e-6)=>assert(Math.abs(a-b)<tolerance,`${a} differs from ${b}`)
assert.equal(ports.length,5);assert.equal(pads.length,7)
const reports=[]
const portForPad=pad=>ports.find(p=>all('pcb_port').some(pp=>pp.pcb_port_id===pad.pcb_port_id&&pp.source_port_id===p.source_port_id))
for(let i=1;i<=5;i++) {
 const port=ports.find(e=>e.pin_number===i)
 const pp=all('pcb_port').find(e=>e.source_port_id===port.source_port_id)
 const pad=pads.find(e=>e.pcb_port_id===pp.pcb_port_id)
 assert.equal(pad.shape,'rect');near(pad.width,.5999988);near(pad.height,1.5500096)
 assert.equal(pad.layer,'top');assert(!pad.is_covered_with_solder_mask)
 near(pad.x,padXs[i-1]);near(pad.y,-11.3001183)
 const net=nets.find(n=>n.subcircuit_connectivity_map_key===port.subcircuit_connectivity_map_key)
 assert.equal(net?.name,expected[i-1],`Wrong programmer contact ${i}`)
 assert(all('source_trace').some(t=>t.connected_source_port_ids?.includes(port.source_port_id)),`Unconnected JST pin ${i}`)
 reports.push({pin:i,signal:port.name,net:net.name,x:pad.x,y:pad.y,widthMm:pad.width,heightMm:pad.height})
}
const anchors=pads.filter(p=>!p.pcb_port_id)
assert.equal(anchors.length,2)
for(const x of [-3.300095,3.300095]) {
 const pad=anchors.find(p=>Math.abs(p.x-x)<1e-6)
 assert(pad);near(pad.y,-15.1748883);near(pad.width,1.1999976);near(pad.height,1.7999964)
}
assert.equal(all('pcb_hole').length,4,'Only the four enclosure mounting holes should remain')
assert(!all('pcb_hole').some(e=>e.pcb_component_id===pcb.pcb_component_id),'Tag-Connect alignment holes remain')
assert(!all('pcb_plated_hole').some(e=>e.pcb_component_id===pcb.pcb_component_id))
const padIds=new Set(pads.map(e=>e.pcb_smtpad_id))
const paste=gerberCompatibleCircuit(circuit).filter(e=>e.type==='pcb_solder_paste'&&padIds.has(e.pcb_smtpad_id))
assert.equal(new Set(paste.map(p=>p.pcb_smtpad_id)).size,7,'All five contacts and both mounting tabs need stencil paste')
const idToSource=new Map(all('source_trace').map(e=>[e.source_trace_id,e]))
const mcu=all('source_component').find(e=>e.name==='U1')
for(const [pin,name] of [[24,'NRESET'],[25,'SWDCLK'],[26,'SWDIO']]) {
 const sp=all('source_port').find(e=>e.source_component_id===mcu.source_component_id&&e.pin_number===pin)
 assert.equal(nets.find(n=>n.subcircuit_connectivity_map_key===sp.subcircuit_connectivity_map_key)?.name,name)
}
const pointSegmentDistance=(p,a,b)=>{
 const dx=b.x-a.x,dy=b.y-a.y
 const t=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy||1)))
 return Math.hypot(p.x-a.x-t*dx,p.y-a.y-t*dy)
}
const rectCorners=p=>[
 {x:p.x-p.width/2,y:p.y-p.height/2},{x:p.x+p.width/2,y:p.y-p.height/2},
 {x:p.x+p.width/2,y:p.y+p.height/2},{x:p.x-p.width/2,y:p.y+p.height/2}]
const pointRectDistance=(p,rect)=>Math.hypot(Math.max(0,Math.abs(p.x-rect.x)-rect.width/2),Math.max(0,Math.abs(p.y-rect.y)-rect.height/2))
const segmentRectDistance=(a,b,rect)=>{
 let lo=0,hi=1
 for(const axis of ['x','y']) {
  const half=rect[axis==='x'?'width':'height']/2,d=b[axis]-a[axis]
  if(Math.abs(d)<1e-12) {if(Math.abs(a[axis]-rect[axis])>half){hi=-1;break}}
  else {const ends=[(rect[axis]-half-a[axis])/d,(rect[axis]+half-a[axis])/d].sort((x,y)=>x-y);lo=Math.max(lo,ends[0]);hi=Math.min(hi,ends[1])}
 }
 if(lo<=hi)return 0
 return Math.min(pointRectDistance(a,rect),pointRectDistance(b,rect),...rectCorners(rect).map(p=>pointSegmentDistance(p,a,b)))
}
let minimumUnrelatedTopTrackClearanceMm=Infinity
for(const t of all('pcb_trace')) {
 const key=idToSource.get(t.source_trace_id)?.subcircuit_connectivity_map_key
 assert(key,`Trace ${t.pcb_trace_id} lacks connectivity identity`)
 for(const pad of pads) {
  if(portForPad(pad)?.subcircuit_connectivity_map_key===key)continue
  for(let i=1;i<t.route.length;i++) {
   const a=t.route[i-1],b=t.route[i]
   if(a.route_type!=='wire'||b.route_type!=='wire'||a.layer!=='top'||b.layer!=='top')continue
   const gap=segmentRectDistance(a,b,pad)-Math.max(a.width,b.width)/2
   minimumUnrelatedTopTrackClearanceMm=Math.min(minimumUnrelatedTopTrackClearanceMm,gap)
   assert(gap>=.13-1e-6,`JST land is only ${gap} mm from unrelated trace ${t.pcb_trace_id}`)
  }
 }
}
let minimumUnrelatedViaClearanceMm=Infinity
for(const via of all('pcb_via').filter(e=>e.layers.includes('top')))for(const pad of pads) {
 assert(pointRectDistance(via,pad)-via.hole_diameter/2>0,'A via drill overlaps a JST contact or anchor')
 if(portForPad(pad)?.subcircuit_connectivity_map_key===via.subcircuit_connectivity_map_key)continue
 const gap=pointRectDistance(via,pad)-via.outer_diameter/2
 minimumUnrelatedViaClearanceMm=Math.min(minimumUnrelatedViaClearanceMm,gap)
 assert(gap>=.13-1e-6,`JST land is only ${gap} mm from an unrelated via`)
}
const courtyard=all('pcb_courtyard_outline').find(e=>e.pcb_component_id===pcb.pcb_component_id)
assert(courtyard,'Missing library courtyard')
const xs=courtyard.outline.map(p=>p.x),ys=courtyard.outline.map(p=>p.y)
const bounds={minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys)}
near(bounds.maxX-bounds.minX,8.2978);near(bounds.maxY-bounds.minY,6.0372)
for(const p of courtyard.outline)assert(Math.hypot(p.x,p.y)<18.25-.25,'JST courtyard extends beyond board clearance')
for(const e of all('pcb_component').filter(e=>e.layer==='top'&&e.pcb_component_id!==pcb.pcb_component_id&&!e.do_not_place&&all('source_component').some(s=>s.source_component_id===e.source_component_id)))
 assert(e.center.x+e.width/2<bounds.minX||e.center.x-e.width/2>bounds.maxX||e.center.y+e.height/2<bounds.minY||e.center.y-e.height/2>bounds.maxY,`JST courtyard overlaps ${e.pcb_component_id}`)
const pkg=JSON.parse(readFileSync('package.json'))
assert.equal(pkg.dependencies['@tsci/tscircuit.standard-jst-programmer'],'0.8.0')
const cad=all('cad_component').find(e=>e.source_component_id===source.source_component_id)
assert.equal(cad.model_obj_url,'./imports/SM05B_SRSS_TB/SM05B_SRSS_TB.obj')
assert.equal(cad.model_step_url,'./imports/SM05B_SRSS_TB/SM05B_SRSS_TB.step')
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
const styleWarnings=issues.filter(e=>e.type==='pcb_trace_style_warning')
assert.equal(issues.length-styleWarnings.length,0,JSON.stringify(issues))
// Core 0.0.2245 adds style advisories to three unchanged legacy segments.
// Match every non-ID field exactly (to 1 nm); do not hide other warnings/errors.
const warningRecord=e=>JSON.parse(JSON.stringify(Object.fromEntries(Object.entries(e)
 .filter(([key])=>!key.endsWith('_id')&&key!=='message'))),(k,v)=>typeof v==='number'?Math.round(v*1e9)/1e9:v)
const warningKey=e=>JSON.stringify(e,(_,v)=>v&&!Array.isArray(v)&&typeof v==='object'?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v)
const known=JSON.parse(readFileSync('validation/known-trace-style-warnings.json')).warnings
assert.deepEqual(styleWarnings.map(warningRecord).sort((a,b)=>warningKey(a).localeCompare(warningKey(b))),
 known.sort((a,b)=>warningKey(a).localeCompare(warningKey(b))),'Trace style advisories changed; review the routing')
const result={checkedAt:new Date().toISOString(),passed:true,sourcePackage:'@tsci/tscircuit.standard-jst-programmer@0.8.0',
 reference:'https://github.com/tscircuit/standard-jst-programmer',
 acceptedTraceStyleWarnings:styleWarnings.length,
 footprint:source.manufacturer_part_number,supplier:'JLCPCB C136657',matingHousing:'SHR-05V-S-B',cable:'Straight-through five-way JST-SH, 1.0 mm pitch',side:'top',entryDirection:'-Y',pads:reports,mountingTabs:anchors.length,alignmentHoles:0,
 stencilApertures:paste.length,power:'Pin 1 follows programmer voltage selector; select 3V3 and remove CR2032',
 minimumUnrelatedTopTrackClearanceMm,minimumUnrelatedViaClearanceMm,crystalBranches,courtyardBoundsMm:bounds,courtyardClear:true,
 circuitSha256:createHash('sha256').update(bytes).digest('hex'),physicalConnectorFitTested:false,physicalProgrammingTested:false}
writeFileSync('validation/programming-interface.json',JSON.stringify(result,null,2)+'\n')
console.log('Pass: fitted five-pin JST-SH, correct programmer pinout, seven stencil apertures, no legacy programming pads/holes and clear connector courtyard')
