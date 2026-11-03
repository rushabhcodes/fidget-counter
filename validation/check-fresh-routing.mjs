import assert from'node:assert/strict'
import{execFileSync}from'node:child_process'
import{readFileSync,writeFileSync}from'node:fs'
import{createHash}from'node:crypto'
import{fittedComponentRecords}from'./fitted-component-records.mjs'
const canonical=v=>JSON.stringify(v,(_,x)=>typeof x==='number'?Math.round(x*1e9)/1e9:x&&!Array.isArray(x)&&typeof x==='object'?Object.fromEntries(Object.entries(x).sort(([a],[b])=>a.localeCompare(b))):x)
export function freshRoutingSignature(c){
 const ss=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]));
 const sp=new Map(c.filter(e=>e.type==='source_port').map(e=>[e.source_port_id,`${ss.get(e.source_component_id)??'positioned-via'}.${e.pin_number??e.name}`]));
 const pp=new Map(c.filter(e=>e.type==='pcb_port').map(e=>[e.pcb_port_id,sp.get(e.source_port_id)]));
 const nn=new Map(c.filter(e=>e.type==='source_net').map(e=>[e.source_net_id,e.name]));
 const connection=e=>canonical({ports:e.connected_source_port_ids.map(i=>sp.get(i)).sort(),nets:e.connected_source_net_ids.map(i=>nn.get(i)).sort(),max_length:e.max_length,max_via_count:e.max_via_count});
 const tt=new Map(c.filter(e=>e.type==='source_trace').map(e=>[e.source_trace_id,connection(e)]));
 const id=x=>sp.get(x)??pp.get(x)??nn.get(x)??tt.get(x)??x;
 const clean=v=>Array.isArray(v)?v.map(clean):v&&typeof v==='object'?Object.fromEntries(Object.entries(v).filter(([k])=>!k.endsWith('_id')&&!k.endsWith('_ids')&&!['subcircuit_connectivity_map_key','name','title'].includes(k)).map(([k,v])=>[k,k==='connectsTo'?v.map(id).sort():k==='connection_name'?id(v):clean(v)])):v;
 const rows=type=>c.filter(e=>type.includes(e.type)).map(e=>canonical({...clean(e),terminal:e.pcb_port_id?pp.get(e.pcb_port_id):undefined,sourceConnection:e.source_trace_id?tt.get(e.source_trace_id):undefined,net:e.source_net_id?nn.get(e.source_net_id):undefined})).sort();
 return {orientations:c.filter(e=>e.type==='pcb_component'&&e.supplier_pin1_location_map).map(e=>canonical({owner:ss.get(e.source_component_id),map:e.supplier_pin1_location_map})).sort(),connections:[...tt.values()].sort(),pins:c.filter(e=>e.type==='source_port'&&ss.has(e.source_component_id)).map(e=>canonical({...clean(e),terminal:sp.get(e.source_port_id)})).sort(),lands:rows(['pcb_board','pcb_hole','pcb_plated_hole','pcb_smtpad','pcb_port','pcb_keepout']),copper:rows(['pcb_trace','pcb_via','pcb_copper_pour'])}
}
export function logicalNetPartition(c){
 const owners=new Map(c.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e.name]));const parent=new Map();
 const find=x=>{if(!parent.has(x))parent.set(x,x);if(parent.get(x)!==x)parent.set(x,find(parent.get(x)));return parent.get(x)};
 for(const e of c.filter(e=>e.type==='source_trace')){const nodes=[...e.connected_source_port_ids,...e.connected_source_net_ids];for(const x of nodes)parent.set(find(x),find(nodes[0]))}
 const groups=new Map();
 for(const e of c){let id,label;if(e.type==='source_port'&&owners.has(e.source_component_id)&&!owners.get(e.source_component_id).startsWith('BEARING_')){id=e.source_port_id;label=owners.get(e.source_component_id)+'.'+e.pin_number}else if(e.type==='source_net'){id=e.source_net_id;label='net.'+e.name}else continue;const root=find(id);if(!groups.has(root))groups.set(root,[]);groups.get(root).push(label)}
 return [...groups.values()].map(g=>g.sort()).sort((a,b)=>canonical(a).localeCompare(canonical(b)))
}
const old=()=>JSON.parse(execFileSync('git',['show','a7c29c470c439e6f4e35314b9c68bba5c8d8c100:published.circuit.json'],{maxBuffer:16e6}));
export function verifyFreshRouting(c){
 const ref=JSON.parse(readFileSync('validation/fresh-routing-reference.json'));assert.equal(ref.compiler,'0.0.3060');assert.equal(JSON.parse(readFileSync('package.json')).dependencies.tscircuit,ref.compiler);
 const baseline=old();assert.deepEqual(fittedComponentRecords(c),fittedComponentRecords(baseline),'Fitted identity, value, land, layer or CAD pose changed');
 assert.deepEqual(logicalNetPartition(c),logicalNetPartition(baseline),'Actual component-pin net membership changed');
 assert.deepEqual(freshRoutingSignature(c).pins,freshRoutingSignature(baseline).pins,'Real electrical pin attributes changed');
 assert.deepEqual(freshRoutingSignature(c),ref.signature,'Approved new copper, connectivity, constraints, layers or fixed geometry changed');
 assert(!c.some(e=>e.type.endsWith('_error')),'New routing has circuit errors');
 return {passed:true,approved_new_routing:true,compiler:ref.compiler,comparison_commit:'a7c29c470c439e6f4e35314b9c68bba5c8d8c100',all_28_fitted_values_lands_layers_poses_preserved:true,routing_changed_intentionally:true,physical_tested:false,reference_sha256:createHash('sha256').update(readFileSync('validation/fresh-routing-reference.json')).digest('hex')}
}
if(import.meta.main){const report=verifyFreshRouting(JSON.parse(readFileSync(process.argv[2]??'published.circuit.json')));report.source_sha256=Object.fromEntries(['index.circuit.tsx','published.circuit.json','critical-routes.json','routing.ts','routing-contract.json','routed-paths.json','validation/check-fresh-routing.mjs','validation/fresh-routing-reference.json','validation/fitted-component-records.mjs'].map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')]));writeFileSync('validation/fresh-routing-audit.json',JSON.stringify(report,null,2)+'\n');console.log('PASS: approved fresh routing; all28 fitted geometries and actual pin-net partitions preserved; fixed copper/constraints/layers fail closed')}
