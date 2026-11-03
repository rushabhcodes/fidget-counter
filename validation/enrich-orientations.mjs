// Add verified supplier rotation metadata to the generated circuit, without
// changing a land, electrical connection, component pose or native CAD mesh.
import{execFileSync}from'node:child_process'
import{copyFileSync}from'node:fs'
const input=process.argv[2]??'dist/index/circuit.json',out='.local-validation/orientation'
execFileSync(process.execPath,['validation/prepare-supplier-frames.mjs',input,out],{stdio:'inherit'})
copyFileSync(`${out}/prepared.circuit.json`,input)
