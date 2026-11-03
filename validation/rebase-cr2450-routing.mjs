// One-time, bounded routing migration; normal builds still use routing.ts's
// exact geometry contract and terminal-ID safeguards.
import assert from 'node:assert/strict'
import {execFileSync} from 'node:child_process'
import {readFileSync,writeFileSync} from 'node:fs'
import {routingGeometry} from '../routing'
const baseline='346fade26c8934f9d0b6411d7e30c1c9b06e9dac'
const previous=p=>JSON.parse(execFileSync('git',['show',`${baseline}:${p}`],{maxBuffer:16e6}))
const raw=JSON.parse(readFileSync('work/cr2450-upgrade/routing-input.json'))
const candidate=JSON.parse(readFileSync('work/cr2450-upgrade/before-routing.circuit.json'))
const paths=previous('routed-paths.json'),contract=previous('routing-contract.json')
const canonical=v=>JSON.stringify(v,(_,v)=>v&&!Array.isArray(v)&&typeof v==='object'?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v)
const pk=p=>canonical(Object.fromEntries(Object.entries(p).filter(([k])=>!['pointId','pcb_port_id'].includes(k))))
const oldCircuit=previous('published.circuit.json')
const batteryPorts=c=>{
 const source=c.find(e=>e.type==='source_component'&&e.name==='BT1')
 const sourcePorts=new Map(c.filter(e=>e.type==='source_port'&&e.source_component_id===source.source_component_id).map(p=>[p.source_port_id,p.pin_number]))
 return new Map(c.filter(e=>e.type==='pcb_port'&&sourcePorts.has(e.source_port_id)).map(p=>[p.pcb_port_id,{...p,pin:sourcePorts.get(p.source_port_id)}]))
}
const before=batteryPorts(oldCircuit),after=batteryPorts(candidate),ids=new Map()
assert.equal(before.size,2);assert.equal(after.size,2)
for(const c of JSON.parse(paths.expectedPhaseSignature)){
 const next=raw.connections.find(n=>n.name===c.name);assert(next)
 assert.equal(next.pointsToConnect.length,c.points.length)
 const points=new Map(next.pointsToConnect.map(p=>[pk(p),p]))
 for(const p of c.points){
  let q=points.get(pk(p))
  if(before.has(p.pcb_port_id)){
   const terminal=[...after.values()].find(x=>x.pin===before.get(p.pcb_port_id).pin)
   q=next.pointsToConnect.find(x=>x.pcb_port_id===terminal.pcb_port_id)
   assert(q&&q.layer==='bottom');assert(Math.abs(q.y)<1e-6)
   assert(Math.abs(q.x-(terminal.pin===1?-15.550007:15.550007))<1e-6)
  }
  assert(q,'Unexpected physical-terminal change '+p.pcb_port_id)
  for(const key of ['pointId','pcb_port_id'])ids.set(p[key],q[key])
 }
}
const auxiliaryVias=structuredClone(contract.auxiliaryVias)
for(const via of auxiliaryVias)via.ports=via.ports.map((id,i)=>{
 const matches=candidate.filter(e=>e.type==='pcb_port'&&e.x===via.center.x&&e.y===via.center.y&&e.layers[0]===via.layers[i]);assert.equal(matches.length,1);ids.set(id,matches[0].pcb_port_id);return matches[0].pcb_port_id
})
const remap=v=>typeof v==='string'&&v.startsWith('pcb_port_')?(assert(ids.has(v),'Unmapped '+v),ids.get(v)):Array.isArray(v)?v.map(remap):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).map(([k,x])=>[k,remap(x)])):v
const traces=remap(paths.traces)
const changed=[]
for(let i=0;i<paths.traces.length;i++){
 const prior=paths.traces[i],oldPort=prior.connectsTo.find(id=>before.has(id));if(!oldPort)continue
 const terminal=after.get(ids.get(oldPort)),trace=traces[i];changed.push(trace.pcb_trace_id)
 if(before.get(oldPort).pin===1){trace.route[0].x=terminal.x;trace.route[0].y=terminal.y}
 else{
  const target=auxiliaryVias.find(v=>v.center.x===-2&&v.center.y===-9.4);assert(target)
  const end=target.ports[target.layers.indexOf('bottom')];assert(end)
  trace.connectsTo=[terminal.pcb_port_id,end]
  trace.route=[
   {route_type:'wire',x:terminal.x,y:terminal.y,width:.25,layer:'bottom',start_pcb_port_id:terminal.pcb_port_id},
   {route_type:'wire',x:15.550007,y:-3,width:.25,layer:'bottom'},
   {route_type:'via',x:15.550007,y:-3,from_layer:'bottom',to_layer:'top',via_diameter:.55,via_hole_diameter:.3},
   {route_type:'wire',x:15.550007,y:-3,width:.25,layer:'top'},
   {route_type:'wire',x:10,y:-3,width:.25,layer:'top'},
   {route_type:'via',x:10,y:-3,from_layer:'top',to_layer:'bottom',via_diameter:.55,via_hole_diameter:.3},
   {route_type:'wire',x:10,y:-3,width:.25,layer:'bottom'},
   {route_type:'wire',x:9.4999151,y:-2.4999151,width:.25,layer:'bottom'},
   {route_type:'wire',x:9.4999151,y:0,width:.25,layer:'bottom'},
   {route_type:'wire',x:-2,y:-9.4,width:.11,layer:'bottom',end_pcb_port_id:end},
  ]
 }
}
assert.deepEqual(changed.sort(),['source_net_0_holder_0','source_net_1_holder_0'])
const geometry=routingGeometry(raw),settings=({connections,obstacles,traces,...s})=>s
assert.deepEqual(settings(geometry),settings(contract.geometry),'Board/router design rules changed')
assert.deepEqual(geometry.traces,contract.geometry.traces,'Manual RF/clock/power copper changed')
const diff=(a,b)=>{const rest=b.map(canonical);return a.filter(x=>{const i=rest.indexOf(canonical(x));if(i<0)return true;rest.splice(i,1);return false})}
const removed=diff(contract.geometry.obstacles,geometry.obstacles),added=diff(geometry.obstacles,contract.geometry.obstacles)
// Four drills, two holder pads; replace two two-sided keepouts with two top
// screw-head keepouts and four bottom post keepouts. No other obstacle changes.
assert.equal(removed.length,8);assert.equal(added.length,12)
writeFileSync('work/cr2450-upgrade/routing-migration.json',JSON.stringify({baseline,changed_routes:changed,added_vias:[{x:15.550007,y:-3},{x:10,y:-3}],removed_obstacles:removed,added_obstacles:added},null,2)+'\n')
writeFileSync('routed-paths.json',JSON.stringify({expectedPhaseSignature:JSON.stringify(raw.connections.map(c=>({name:c.name,points:c.pointsToConnect}))),traces},null,2)+'\n')
writeFileSync('routing-contract.json',JSON.stringify({geometry,auxiliaryVias},null,2)+'\n')
console.log('Migrated only two battery branches, two added through vias, two holder lands and revised mounting obstacles; strict runtime contract retained')
