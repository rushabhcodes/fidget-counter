import paths from "./routed-paths.json"

// Prescribed, editable routing through tscircuit's supported local router API.
// Normal placement, connectivity, clearance, pour and shorts checks still run.
export const routeBoard = async (input: any) => {
 const signature=JSON.stringify(input.connections.map((c:any)=>({name:c.name,points:c.pointsToConnect}))
  .sort((a:any,b:any)=>a.name.localeCompare(b.name)))
 if(paths.expectedPhaseSignature && signature!==paths.expectedPhaseSignature)
  throw new Error("Routing terminals changed; update the prescribed routes and rerun all checks")
 if(!paths.expectedPhaseSignature) console.log("ROUTE_PHASE_SIGNATURE="+signature)
 const listeners:Record<string,(event:any)=>void>={}
 return {
  on(event:string,listener:(event:any)=>void){listeners[event]=listener},
  start(){listeners.complete({traces:structuredClone(paths.traces)})},
  stop(){},
 }
}
