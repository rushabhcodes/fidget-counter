import {readFileSync, writeFileSync, mkdirSync} from "node:fs"
import {resolve} from "node:path"
import {execFileSync} from "node:child_process"
import {createHash} from "node:crypto"
import JSZip from "jszip"
import {gerberCompatibleCircuit} from "./gerber-compat.mjs"

const input = process.argv[2] ?? "dist/index/circuit.json"
const circuit = JSON.parse(readFileSync(input))
if (circuit.some(e => /error|warning/.test(e.type))) throw new Error("Refusing to export a circuit with diagnostics")
mkdirSync("work", {recursive:true})
mkdirSync("fabrication", {recursive:true})
const compatible = gerberCompatibleCircuit(circuit)
const intermediate = "work/gerber-compatible.circuit.json"
writeFileSync(intermediate, JSON.stringify(compatible, null, 2) + "\n")
execFileSync("bun", ["run", "tsci", "export", intermediate, "-f", "gerbers", "-o", resolve("work/complete-gerbers.zip")], {stdio:"inherit"})
const raw = await JSZip.loadAsync(readFileSync("work/complete-gerbers.zip"))
const archive = new JSZip()
for (const name of Object.keys(raw.files)) {
  if (/\.(gbr|drl|gbrjob)$/.test(name)) archive.file(name, await raw.file(name).async("uint8array"))
}
const output = "fabrication/Fidget_Counter_RevA_Prototype_Gerbers.zip"
writeFileSync(output, await archive.generateAsync({type:"nodebuffer", compression:"DEFLATE"}))
const hash = path => createHash("sha256").update(readFileSync(path)).digest("hex")
writeFileSync("work/gerber-normalization.json", JSON.stringify({source:input, sourceSha256:hash(input),
  exportCircuitSha256:hash(intermediate), gerberZipSha256:hash(output),
  normalizedPadCount:circuit.filter(e => e.type === "pcb_smtpad" && e.shape === "rotated_pill").length,
  fittedPasteCount:compatible.filter(e => e.type === "pcb_solder_paste").length,
  addedPillPasteCount:compatible.filter(e => e.type === "pcb_solder_paste" && e.pcb_solder_paste_id.startsWith("paste_for_")).length,
  tentedViaCount:compatible.filter(e => e.type === "pcb_via" && e.is_tented).length,
  note:"Copper geometry unchanged. Added missing fitted QFN lead paste at 70% linear size; excluded bare/DNP paste; applied source board's both-side via tenting; quarter-turn pills represented as axis-aligned equivalents."}, null, 2) + "\n")
console.log(`Exported ${output}`)
