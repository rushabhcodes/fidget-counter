import paths from "./routed-paths.json"
import contract from "./routing-contract.json"

const canonical = (value:any):string => JSON.stringify(value, (_,v) =>
 v && !Array.isArray(v) && typeof v === "object"
  ? Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))) : v)
const pointKey = (point:any) => canonical(Object.fromEntries(Object.entries(point)
 .filter(([key])=>key!=="pointId" && key!=="pcb_port_id")))

// Match physical terminals within their electrical group. IDs are allocated by
// core and can change between versions without changing the actual board.
export const routingGeometry = (input:any) => {
 const anchors=new Map<string,string>()
 for(const c of input.connections)for(const p of c.pointsToConnect)
  for(const key of ["pointId","pcb_port_id"])anchors.set(p[key],c.name+":"+pointKey(p))
 const {connections,obstacles,traces,...settings}=input
 return JSON.parse(canonical({...settings,
  connections:connections.map((c:any)=>({name:c.name,width:c.width,
   nominalTraceWidth:c.nominalTraceWidth,points:c.pointsToConnect.map(pointKey).sort()}))
   .sort((a:any,b:any)=>a.name.localeCompare(b.name)),
  obstacles:obstacles.map((o:any)=>{
   const {circuitJsonMetadata,componentId,obstacleId,connectedTo,offBoardConnectsTo,...geometry}=o
   return {...geometry,connectedTo:(connectedTo??[]).filter((id:string)=>
    id.startsWith("source_net_") || connections.some((c:any)=>c.name===id)).sort()}
  }).sort((a:any,b:any)=>canonical(a).localeCompare(canonical(b))),
  traces:traces.map((t:any)=>({type:t.type,route:t.route,
   connectsTo:t.connectsTo.map((id:string)=>anchors.get(id)??id).sort()}))
   .sort((a:any,b:any)=>canonical(a).localeCompare(canonical(b))),
 }))
}

// Prescribed routing through the supported local router API. The contract covers
// board geometry, copper obstacles, existing routes, layers, widths, design rules
// and electrical membership, in addition to terminal XY.
export const routeBoard = async (input:any) => {
 if(canonical(routingGeometry(input))!==canonical(contract.geometry))
  throw new Error("Routing terminals or copper changed; update the prescribed routes and rerun all checks")
 const expected=JSON.parse(paths.expectedPhaseSignature)
 const portIds=new Map<string,string>()
 for(const connection of expected) {
  const incoming=input.connections.find((c:any)=>c.name===connection.name)
  const points=new Map<string,any>(incoming.pointsToConnect.map((p:any)=>[pointKey(p),p]))
  if(points.size!==incoming.pointsToConnect.length)throw new Error("Ambiguous physical routing terminals")
  for(const point of connection.points) {
   const current=points.get(pointKey(point))
   if(!current)throw new Error("Routing terminals changed")
   for(const field of ["pointId","pcb_port_id"]) {
    const from=point[field],to=current[field]
    if(typeof from!=="string"||typeof to!=="string"||
      (portIds.has(from)&&portIds.get(from)!==to))throw new Error("Invalid routing terminal IDs")
    portIds.set(from,to)
   }
  }
 }
 // These prescribed through vias expose both ports, but the API does not tell
 // which ID belongs to which layer. Require their IDs and physical/net semantics.
 for(const via of contract.auxiliaryVias) {
  const matches=input.obstacles.filter((o:any)=>o.shape==="circle" &&
   canonical(o.center)===canonical(via.center) && canonical(o.layers)===canonical(via.layers) &&
   o.width===via.width && o.height===via.height &&
   via.ports.every(id=>o.connectedTo.includes(id)) && o.connectedTo.includes(via.net))
  if(matches.length!==1)throw new Error("Prescribed through-via terminals changed")
  for(const id of via.ports)portIds.set(id,id)
 }
 const remap=(value:any):any=>{
  if(typeof value==="string"&&value.startsWith("pcb_port_")) {
   if(!portIds.has(value))throw new Error(`Prescribed route references an unknown terminal: ${value}`)
   return portIds.get(value)
  }
  if(Array.isArray(value))return value.map(remap)
  if(value&&typeof value==="object")return Object.fromEntries(Object.entries(value).map(([key,v])=>[key,remap(v)]))
  return value
 }
 const traces=remap(paths.traces)
 const listeners:Record<string,(event:any)=>void>={}
 return {on(event:string,listener:(event:any)=>void){listeners[event]=listener},
  start(){listeners.complete({traces})},stop(){}}
}
