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
  "critical-routes.json",
  "validation/enrich-orientations.mjs",
  "validation/prepare-supplier-frames.mjs",
  "validation/import-provenance.mjs",
  "validation/jlc-imports.json",
  "validation/check-fresh-routing.mjs",
  "validation/check-source-snapshot.mjs",
  "validation/fresh-routing-reference.json",
  "validation/fitted-component-records.mjs",
  "validation/nordic-electrical-revision.mjs",
  "validation/nordic-electrical-reference.json",
  "validation/check-nordic-rf.py",
  "routing-contract.json",
  "cloud-build.mjs",
  "tscircuit.config.json",
  "tsconfig.json",
  "validation/cloud-package-input.mjs",
  "validation/apply-model-materials.mjs",
  "validation/compact-glb.mjs",
  "validation/restore-model-normals.mjs",
  "validation/restore-cad-inputs.mjs",
  "mechanical/variants/V2_discrete_magnets/review.html",
  "mechanical/variants/V2_discrete_magnets/review.png",
  "mechanical/variants/V2_discrete_magnets/polarity.svg",
  ...walk(resolve(root, "imports")).map((path) => relative(root, path)),
  ...walk(resolve(root, "mechanical"))
    .filter((path) => !relative(root, path).startsWith("mechanical/export/") && !path.includes("/__pycache__/"))
    // Full V2 STEP assemblies ship in a separate manufacturing CAD archive;
    // the transient render mesh is regenerated from source, not a worker input.
    .filter((path) => !relative(root,path).startsWith("mechanical/variants/V2_discrete_magnets/generated/Assemblies/") && relative(root,path)!=="mechanical/variants/V2_discrete_magnets/generated/scene_meshes.json")
    .filter((path) => [".py", ".json", ".stl", ".obj", ".mtl", ".step", ".glb"].includes(extname(path)))
    // OBJ/MTL references stay in Git; indexed GLB assets are the runtime inputs.
    .filter((path) => !(relative(root,path).startsWith("mechanical/Circuit_Models/") && [".obj",".mtl"].includes(extname(path))))
    .map((path) => relative(root, path)),
]
const variantPageFiles = {
  "review.html":"index.html",
  "review.png":"review.png",
  "polarity.svg":"polarity.svg",
  "generated/V2_assembled.glb":"V2_assembled.glb",
}
const manifest = {
  formatVersion: 2,
  description: "Locally built and checked preview; hashes bind it to the published source and CAD assets.",
  inputs: Object.fromEntries([...new Set(inputs)].sort().map((name) => [name, sha256(readFileSync(resolve(root, name)))])),
  packageInput: getPackageInput(JSON.parse(readFileSync(resolve(root, "package.json"))), readFileSync(resolve(root, "bun.lock"))),
  artifacts: [],
  variantArtifacts: Object.entries(variantPageFiles).map(([name,target]) => {
    const source=`mechanical/variants/V2_discrete_magnets/${name}`
    const bytes=readFileSync(resolve(root,source))
    return {source,output:`dist/v2/${target}`,sha256:sha256(bytes),bytes:bytes.length}
  }),
}
mkdirSync(resolve(root, "cloud-assets"), { recursive: true })
// Keep the worker's input map small. These manufacturing/CAD exports are
// restored inside the sandbox before the unchanged source hashes are checked.
const cadFiles = Object.keys(manifest.inputs).filter(name =>
  name.startsWith("mechanical/Print_STL/") || name.startsWith("mechanical/STEP_Parts/") ||
  (name.startsWith("mechanical/variants/") && /\.(stl|step|glb)$/.test(name)))
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
  const sourceParts = []
  if (packed.length > 3_000_000) {
    for (let start=0;start<packed.length;start+=3_000_000) {
      const part = `cloud-assets/cad-inputs-${index}.part-${String(sourceParts.length).padStart(3,"0")}.json.gz.b64`
      writeFileSync(resolve(root,part),packed.subarray(start,start+3_000_000));sourceParts.push(part)
    }
  } else writeFileSync(resolve(root, source), packed)
  return { source, ...(sourceParts.length ? {sourceParts} : {}), sha256: sha256(packed), files: entries.map(entry => entry.path) }
})
const activeCadArchives = new Set(manifest.cadInputArchives.flatMap(archive => archive.sourceParts ?? [archive.source]))
for (const name of readdirSync(resolve(root, "cloud-assets"))) {
  const path = `cloud-assets/${name}`
  if (/^cad-inputs-\d+(\.part-\d+)?\.json\.gz\.b64$/.test(name) && !activeCadArchives.has(path))
    unlinkSync(resolve(root, path))
}
for (const name of ["circuit.json", "pcb.png", "pcb.svg", "schematic.png", "schematic.svg", "3d.glb"]) {
  let bytes = readFileSync(resolve(root, "dist/published", name))
  const output = `dist/published/${name}`
  let source = "published.circuit.json"
  let encoding = "raw"
  let sourceParts
  if (name === "circuit.json") {
    const saved = readFileSync(resolve(root, source))
    // The JSON exporter omits a terminal LF. Restore that one formatting byte
    // only; every circuit record and all other source bytes remain strict.
    if (!bytes.equals(saved) && Buffer.concat([bytes, Buffer.from("\n")]).equals(saved)) {
      bytes = saved
      writeFileSync(resolve(root, output), bytes)
    }
    if (!bytes.equals(saved)) {
      throw new Error("dist/published/circuit.json differs from published.circuit.json; rebuild the saved snapshot first")
    }
  } else {
    source = `cloud-assets/${name}.gz.b64`
    encoding = "gzip-base64"
    const encoded = gzipSync(bytes, { level: 9 }).toString("base64") + "\n"
    // Registry requests have a size limit. Chunk the cached text without
    // changing a single byte of the reconstructed, checked artifact.
    const limit = 3_000_000
    const active = new Set()
    if (Buffer.byteLength(encoded) > limit) {
      sourceParts = []
      for (let start = 0; start < encoded.length; start += limit) {
        const part = `cloud-assets/${name}.part-${String(sourceParts.length).padStart(3, "0")}.gz.b64`
        writeFileSync(resolve(root, part), encoded.slice(start, start + limit))
        sourceParts.push(part); active.add(part)
      }
    } else {
      writeFileSync(resolve(root, source), encoded); active.add(source)
    }
    for (const old of readdirSync(resolve(root, "cloud-assets"))) {
      const path = `cloud-assets/${old}`
      if ((path === source || (old.startsWith(`${name}.part-`) && old.endsWith(".gz.b64"))) && !active.has(path))
        unlinkSync(resolve(root, path))
    }
  }
  manifest.artifacts.push({ source, ...(sourceParts ? {sourceParts} : {}), output, encoding, bytes: bytes.length, sha256: sha256(bytes) })
}
writeFileSync(resolve(root, "cloud-assets/manifest.json"), JSON.stringify(manifest, null, 2) + "\n")
console.log(`Prepared ${manifest.artifacts.length} checked artifacts with ${Object.keys(manifest.inputs).length} input hashes`)
