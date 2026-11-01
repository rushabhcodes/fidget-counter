import {describe,it as test} from "node:test"
import assert from "node:assert/strict"
import paths from "../routed-paths.json"
import contract from "../routing-contract.json"
import {routeBoard} from "../routing"

const input=()=>{
 const value=structuredClone(contract.geometry)
 value.connections=JSON.parse(paths.expectedPhaseSignature).map((c)=>({name:c.name,
  width:.11,nominalTraceWidth:.11,pointsToConnect:c.points}))
 for(const via of contract.auxiliaryVias){
  const o=value.obstacles.find((o)=>o.shape==="circle"&&o.center.x===via.center.x&&o.center.y===via.center.y)
  o.connectedTo.push(...via.ports)
 }
 return value
}
const output=async(value)=>{
 const router=await routeBoard(value)
 let traces=[]
 router.on("complete",event=>{traces=event.traces})
 router.start()
 return traces
}
const portRefs=(value)=>{
 if(typeof value==="string")return value.startsWith("pcb_port_")?[value]:[]
 if(Array.isArray(value))return value.flatMap(portRefs)
 if(value&&typeof value==="object")return Object.values(value).flatMap(portRefs)
 return []
}

describe("prescribed routing across compiler versions",()=>{
 test("retains the existing routes for the validated terminal IDs",async()=>{
  assert.deepEqual(await output(input()),paths.traces)
 })
 test("renumbering and ordering preserve all copper geometry and update every port reference",async()=>{
  const value=input()
  for(const c of value.connections) {
   c.pointsToConnect.reverse()
   for(const p of c.pointsToConnect)for(const key of ["pointId","pcb_port_id"])
    p[key]=`pcb_port_${Number(p[key].replace("pcb_port_",""))+1000}`
  }
  value.connections.reverse()
  const result=await output(value)
  assert.deepEqual(result.map(t=>t.route.map(({start_pcb_port_id,end_pcb_port_id,...geometry})=>geometry)),
   paths.traces.map(t=>t.route.map(({start_pcb_port_id,end_pcb_port_id,...geometry})=>geometry)))
  assert.deepEqual(portRefs(result),portRefs(paths.traces).map(id=>Number(id.replace("pcb_port_",""))>=151?id:`pcb_port_${Number(id.replace("pcb_port_",""))+1000}`))
 })
 test("rejects moved pads",async()=>{
  const value=input();value.connections[0].pointsToConnect[0].x+=.01
  await assert.rejects(output(value),/Routing terminals or copper changed/)
 })
 test("rejects changed net membership even when all physical points still exist",async()=>{
  const value=input(),a=value.connections[0].pointsToConnect,b=value.connections[1].pointsToConnect
  ;[a[0],b[0]]=[b[0],a[0]]
  await assert.rejects(output(value),/Routing terminals or copper changed/)
 })
 test("rejects changed existing copper width",async()=>{
  const value=input();value.traces[0].route[0].width+=.01
  await assert.rejects(output(value),/copper changed/)
 })
 test("rejects changed layers",async()=>{
  const value=input();value.connections[0].pointsToConnect[0].layer="bottom"
  await assert.rejects(output(value),/copper changed/)
 })
 test("rejects moved obstacles",async()=>{
  const value=input();value.obstacles[0].center.x+=.01
  await assert.rejects(output(value),/copper changed/)
 })
 test("rejects unidentifiable through-via port renumbering",async()=>{
  const value=input()
  for(const o of value.obstacles)o.connectedTo=o.connectedTo.map((id)=>id==="pcb_port_151"?"pcb_port_999":id)
  await assert.rejects(output(value),/through-via terminals changed/)
 })
})
