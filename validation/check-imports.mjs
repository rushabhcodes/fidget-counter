import {readFileSync, writeFileSync, mkdirSync} from "node:fs"
import {createHash} from "node:crypto"

const hash = path => createHash("sha256").update(readFileSync(path)).digest("hex")
const provenance = JSON.parse(readFileSync("validation/jlc-imports.json"))
for (const part of provenance.parts) for (const file of part.files) {
  if (hash(file.path) !== file.sha256) throw new Error(`Imported file changed: ${file.path}`)
}
for (const path of ["parts.tsx", "passives.tsx", "index.circuit.tsx"]) {
  if (/<footprint\b/.test(readFileSync(path, "utf8"))) throw new Error(`Hand-authored footprint in ${path}`)
}
const circuit = JSON.parse(readFileSync("dist/index/circuit.json"))
const sources = new Map(circuit.filter(e => e.type === "source_component").map(e => [e.source_component_id, e]))
const fitted = circuit.filter(e => e.type === "pcb_component" && !e.do_not_place && sources.has(e.source_component_id))
const models = new Map(circuit.filter(e => e.type === "cad_component").map(e => [e.source_component_id, e]))
const importedFiles = new Set(provenance.parts.flatMap(p => p.files.map(f => f.path)))
const glb = readFileSync("dist/index/3d.glb")
const gltf = JSON.parse(glb.subarray(20, 20 + glb.readUInt32LE(12)).toString())
const meshNames = new Set(gltf.nodes.filter(n => Number.isInteger(n.mesh)).map(n => n.name))
for (const component of fitted) {
  const source = sources.get(component.source_component_id)
  const model = models.get(component.source_component_id)
  if (!model?.model_obj_url || !importedFiles.has(model.model_obj_url.replace(/^\.\//, ""))) throw new Error(`Missing imported model: ${source.name}`)
  if (!meshNames.has(source.name)) throw new Error(`Model absent from built GLB: ${source.name}`)
  if (source.name !== "SW1" && !source.supplier_part_numbers?.jlcpcb?.length) throw new Error(`Missing exact JLC identifier: ${source.name}`)
  if (source.name === "SW1" && source.supplier_part_numbers?.jlcpcb?.length) throw new Error("Original 2 N switch assigned a substitute's supplier ID")
}
if (fitted.length !== 29) throw new Error(`Expected 29 fitted parts, got ${fitted.length}`)
mkdirSync("work", {recursive:true})
writeFileSync("work/import-model-audit.json", JSON.stringify({importedLibraryTypes:provenance.parts.length,
  originalImportedFiles:provenance.parts.reduce((n,p) => n + p.files.length,0), fittedParts:fitted.length,
  exactJlcpcbParts:28, sharedGeometrySwitch:"KMR223NG ULC LFG uses the KMR232NGULCLFS package model; original 2 N MPN retained",
  builtGlbMeshCount:gltf.meshes.length, circuitSha256:hash("dist/index/circuit.json"), glbSha256:hash("dist/index/3d.glb")}, null, 2) + "\n")
console.log("Pass: original JLC imports, supplier identifiers and all 29 fitted model nodes")
