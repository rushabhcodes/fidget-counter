import paths from "./routed-paths.json"

// Prescribed, editable routing through tscircuit's supported local router API.
// Normal placement, connectivity, clearance, pour and shorts checks still run.
export const routeBoard = async (input: any) => {
 // Generated port IDs change when parts are removed. Bind preserved routes
 // by their terminal geometry and net membership, never by an old numeric ID.
 const points=input.connections.flatMap((c:any)=>c.pointsToConnect.map((p:any)=>({...p,connection:c.name})))
 const remap=new Map<string,any>()
 for(const [id,old] of Object.entries(paths.terminals)) {
  const matches=points.filter((p:any)=>Math.hypot(p.x-old.x,p.y-old.y)<.001 && old.layers.includes(p.layer))
  if(matches.length===1) remap.set(id,matches[0])
  // Already connected junction vias can be omitted from pointsToConnect.
  // Their obstacle owns the first two port IDs (top, bottom), before the
  // remaining connected-group IDs. Retain these deliberate junction routes.
  if(!matches.length) {
   const via=input.obstacles.find((o:any)=>o.circuitJsonMetadata?.pcb_via_id &&
    Math.hypot(o.center.x-old.x,o.center.y-old.y)<.001)
   if(via) {
    const connection=input.connections.find((c:any)=>via.connectedTo.includes(c.name))?.name
    const ownPorts=via.connectedTo.filter((s:string)=>s.startsWith("pcb_port_")).slice(0,2)
    if(connection && ownPorts.length===2) remap.set(id,{pcb_port_id:ownPorts[old.layers[0]==="bottom"?1:0],connection})
   }
  }
 }
 const traces=paths.traces.flatMap((saved:any)=>{
  const endpoints=saved.connectsTo.map((id:string)=>remap.get(id))
  // Changed/deleted terminals are routed explicitly in index.circuit.tsx.
  if(endpoints.some((p:any)=>!p) || endpoints[0].connection!==endpoints[1].connection) return []
  const trace=structuredClone(saved)
  trace.connection_name=endpoints[0].connection
  trace.connectsTo=endpoints.map((p:any)=>p.pcb_port_id)
  for(const p of trace.route) for(const key of ["start_pcb_port_id","end_pcb_port_id"])
   if(p[key]) p[key]=remap.get(p[key])?.pcb_port_id
  return [trace]
 })
 const signature=JSON.stringify(input.connections.map((c:any)=>({name:c.name,points:c.pointsToConnect}))
  .sort((a:any,b:any)=>a.name.localeCompare(b.name)))
 if(signature!==paths.expectedPhaseSignature)
  throw new Error("Routing terminals changed; update the prescribed routes and rerun all checks")
 const listeners:Record<string,(event:any)=>void>={}
 return {
  on(event:string,listener:(event:any)=>void){listeners[event]=listener},
  start(){listeners.complete({traces})},
  stop(){},
 }
}
