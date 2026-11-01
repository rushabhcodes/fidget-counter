import { createHash } from "node:crypto"
import { readFileSync, writeFileSync, mkdirSync, readdirSync, unlinkSync } from "node:fs"
import { dirname, resolve, relative, extname } from "node:path"
import { fileURLToPath } from "node:url"
import { gzipSync } from "node:zlib"
import { getPackageInput } from "./cloud-package-input.mjs"

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex")
const walk = (path) => readdirSync(path, { withFileTypes: true }).flatMap((item) => {
  const child = resolve(path, item.name)
  return item.isDirectory() ? walk(child) : [child]
})
const inputs = [
  ...readdirSync(root).filter((name) => /\.(tsx?|circuit\.json)$/.test(name)),
  "routed-paths.json",
  "cloud-build.mjs",
  "tscircuit.config.json",
  "tsconfig.json",
  "validation/cloud-package-input.mjs",
  "validation/restore-cad-inputs.mjs",
  ...walk(resolve(root, "imports")).map((path) => relative(root, path)),
  ...walk(resolve(root, "mechanical"))
    .filter((path) => !relative(root, path).startsWith("mechanical/export/") && !path.includes("/__pycache__/"))
    .filter((path) => [".py", ".json", ".stl", ".obj", ".mtl", ".step"].includes(extname(path)))
    .map((path) => relative(root, path)),
]
const manifest = {
  formatVersion: 2,
  description: "Locally built and checked preview; hashes bind it to the published source and CAD assets.",
  inputs: Object.fromEntries([...new Set(inputs)].sort().map((name) => [name, sha256(readFileSync(resolve(root, name)))])),
  packageInput: getPackageInput(JSON.parse(readFileSync(resolve(root, "package.json"))), readFileSync(resolve(root, "bun.lock"))),
  artifacts: [],
}
mkdirSync(resolve(root, "cloud-assets"), { recursive: true })
// Keep the worker's input map small. These manufacturing/CAD exports are
// restored inside the sandbox before the unchanged source hashes are checked.
const cadFiles = Object.keys(manifest.inputs).filter(name =>
  name.startsWith("mechanical/Print_STL/") || name.startsWith("mechanical/STEP_Parts/"))
const cadGroups = []
let cadGroup = []
let cadBytes = 0
for (const path of cadFiles) {
  const bytes = readFileSync(resolve(root, path))
  if (cadBytes + bytes.length > 5_500_000 && cadGroup.length) {
    cadGroups.push(cadGroup)
    cadGroup = []
    cadBytes = 0
  }
  cadGroup.push({ path, contentBase64: bytes.toString("base64") })
  cadBytes += bytes.length
}
if (cadGroup.length) cadGroups.push(cadGroup)
manifest.cadInputArchives = cadGroups.map((entries, index) => {
  const source = `cloud-assets/cad-inputs-${index}.json.gz.b64`
  const packed = Buffer.from(gzipSync(JSON.stringify(entries), { level: 9 }).toString("base64") + "\n")
  writeFileSync(resolve(root, source), packed)
  return { source, sha256: sha256(packed), files: entries.map(entry => entry.path) }
})
const activeCadArchives = new Set(manifest.cadInputArchives.map(archive => archive.source))
for (const name of readdirSync(resolve(root, "cloud-assets"))) {
  const path = `cloud-assets/${name}`
  if (/^cad-inputs-\d+\.json\.gz\.b64$/.test(name) && !activeCadArchives.has(path))
    unlinkSync(resolve(root, path))
}
for (const name of ["circuit.json", "pcb.png", "pcb.svg", "schematic.png", "schematic.svg", "3d.glb"]) {
  const bytes = readFileSync(resolve(root, "dist/published", name))
  const output = `dist/published/${name}`
  let source = "published.circuit.json"
  let encoding = "raw"
  if (name === "circuit.json") {
    if (sha256(bytes) !== sha256(readFileSync(resolve(root, source)))) {
      throw new Error("dist/published/circuit.json differs from published.circuit.json; rebuild the saved snapshot first")
    }
  } else {
    source = `cloud-assets/${name}.gz.b64`
    encoding = "gzip-base64"
    writeFileSync(resolve(root, source), gzipSync(bytes, { level: 9 }).toString("base64") + "\n")
  }
  manifest.artifacts.push({ source, output, encoding, bytes: bytes.length, sha256: sha256(bytes) })
}
writeFileSync(resolve(root, "cloud-assets/manifest.json"), JSON.stringify(manifest, null, 2) + "\n")
console.log(`Prepared ${manifest.artifacts.length} checked artifacts with ${Object.keys(manifest.inputs).length} input hashes`)
