// Repeatable, local fabrication exports and independent native review.
import {readFileSync,writeFileSync,mkdirSync}from'node:fs'
import{resolve}from'node:path'
import{execFileSync}from'node:child_process'
import{gerberCompatibleCircuit}from'../gerber-compat.mjs'
const out=resolve(process.argv[2]??'dist/fabrication');mkdirSync(out,{recursive:true})
const run=(exe,args)=>execFileSync(exe,args,{stdio:'inherit',maxBuffer:16e6})
run(process.execPath,['validation/prepare-supplier-frames.mjs','published.circuit.json',out])
writeFileSync(`${out}/export.circuit.json`,JSON.stringify(gerberCompatibleCircuit(JSON.parse(readFileSync(`${out}/prepared.circuit.json`))),null,2)+'\n')
run(process.execPath,['node_modules/.bin/tsci','export',`${out}/export.circuit.json`,'--format','gerbers','--output',`${out}/gerbers.zip`,'--disable-parts-engine'])
run(process.execPath,['node_modules/.bin/tsci','export',`${out}/prepared.circuit.json`,'--format','kicad_pcb','--output',`${out}/native.kicad_pcb`,'--disable-parts-engine'])
run('/usr/bin/python3',['validation/kicad-review-adapter.py',`${out}/native.kicad_pcb`,`${out}/review.kicad_pcb`])
run('python',['validation/check-native-fabrication.py',out])
