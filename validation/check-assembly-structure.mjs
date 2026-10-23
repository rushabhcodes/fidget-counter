import {Circuit,assembly} from "@tscircuit/core"
import assert from "node:assert/strict"
import {mkdirSync,writeFileSync} from "node:fs"
import {createElement} from "react"
import {CAP_STYLE_OPTIONS,EnclosureAssembly} from "../enclosure.tsx"

const reports=[]
for(const style of CAP_STYLE_OPTIONS) {
  const circuit=new Circuit()
  circuit.add(createElement(assembly.device,{name:"STYLE_CHECK"},createElement(EnclosureAssembly,{capStyle:style})))
  await circuit.renderUntilSettled()
  const elements=circuit.getCircuitJson()
  const sources=elements.filter(e=>e.type==="source_component")
  const models=elements.filter(e=>e.type==="cad_component")
  const names=sources.map(e=>e.name)
  assert.equal(sources.length,8)
  assert.equal(models.length,8)
  assert.equal(new Set(names).size,8)
  assert(names.includes(`ONEPIECE_V4_Cap_${style}`))
  assert(names.includes("ONEPIECE_V4_Encoder_Spacer"))
  assert(!names.some(name=>/Screw|Fastener|PCB_Retainer/.test(name)))
  assert.equal(names.filter(name=>name.startsWith("ONEPIECE_V4_Cap_")).length,1)
  assert(!elements.some(e=>e.type.startsWith("pcb_")||e.type.startsWith("schematic_")||
    e.type==="source_port"||e.type==="source_trace"||e.type.endsWith("_error")))
  reports.push({style,mechanicalModels:models.length,pcbFootprints:0,electricalPorts:0,pcbScrews:0})
}
mkdirSync("work",{recursive:true})
writeFileSync("work/assembly-structure.json",JSON.stringify({passed:true,styles:reports},null,2)+"\n")
console.log("Pass: all eleven cap selectors render eight mechanical-only models, including the spacer; no screw parts")
