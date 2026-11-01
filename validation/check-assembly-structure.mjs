import {Circuit,assembly} from '@tscircuit/core'
import assert from 'node:assert/strict'
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {createElement} from 'react'
import {CAP_STYLE_OPTIONS,EnclosureAssembly} from '../enclosure.tsx'
const m=JSON.parse(readFileSync('mechanical/Circuit_Models/manifest.json')),reports=[]
for(const style of CAP_STYLE_OPTIONS){
 const circuit=new Circuit();circuit.add(createElement(assembly.device,{name:'STYLE_CHECK'},createElement(EnclosureAssembly,{capStyle:style})))
 await circuit.renderUntilSettled();const c=circuit.getCircuitJson(),sources=c.filter(x=>x.type==='source_component'),models=c.filter(x=>x.type==='cad_component'),names=sources.map(x=>x.name)
 assert.equal(sources.length,m.modelsPerSelectedStyle);assert.equal(models.length,m.modelsPerSelectedStyle);assert.equal(new Set(names).size,names.length)
 assert(names.includes(`BEARING_V5_Cap_${style}`));assert(names.includes('BEARING_V5_Bearing_6708'));assert(names.includes('BEARING_V5_Return_Springs'))
 assert(!c.some(x=>x.type.startsWith('pcb_')||x.type.startsWith('schematic_')||x.type==='source_port'||x.type==='source_trace'||x.type.endsWith('_error')))
 reports.push({style,mechanicalModels:models.length,pcbFootprints:0,electricalPorts:0})
}
mkdirSync('work',{recursive:true});writeFileSync('work/assembly-structure.json',JSON.stringify({passed:true,styles:reports},null,2)+'\n')
console.log(`Pass: all ${reports.length} grip selectors contain the bearing, springs and mechanical-only hardware`)
