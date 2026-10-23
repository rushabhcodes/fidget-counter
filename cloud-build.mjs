import { createHash } from "node:crypto"
import { readFileSync, writeFileSync, mkdirSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { gunzipSync } from "node:zlib"
import { verifyPackageInput } from "./validation/cloud-package-input.mjs"
import { restoreCadInputs } from "./validation/restore-cad-inputs.mjs"

// The registry worker has a time limit. Publish the locally checked artifacts
// without loading the circuit compiler, downloading CAD models, or rebuilding
// their meshes. The registry CLI starts this script after its CI bootstrap.
const root = dirname(fileURLToPath(import.meta.url))
const manifest = JSON.parse(readFileSync(resolve(root, "cloud-assets/manifest.json"), "utf8"))
const sha256 = (bytes) => createHash("sha256").update(bytes).digest("hex")
const projectPath = (name) => {
  const path = resolve(root, name)
  if (!path.startsWith(root + "/")) throw new Error(`Invalid project path: ${name}`)
  return path
}

console.log("[cloud-build] Verifying source and checked preview artifacts")
if (manifest.formatVersion !== 2) throw new Error("Unsupported checked preview manifest; run build:cloud:prepare")
verifyPackageInput({
  packageJson: JSON.parse(readFileSync(projectPath("package.json"))),
  lockfile: readFileSync(projectPath("bun.lock")),
  expected: manifest.packageInput,
  cloudBootstrap: process.env.TSCIRCUIT_INSIDE_BUILD_COMMAND === "1",
})
restoreCadInputs(root, manifest)
for (const [name, expectedHash] of Object.entries(manifest.inputs)) {
  if (sha256(readFileSync(projectPath(name))) !== expectedHash) {
    throw new Error(`Stale preview: ${name} changed. Run the local checks, build, and build:cloud:prepare before pushing.`)
  }
}
console.log(`[cloud-build] Verified ${Object.keys(manifest.inputs).length} input files`)

// Validate every artifact before writing any output, so a failed check cannot
// leave a partially refreshed preview for the registry to collect.
const artifacts = manifest.artifacts.map((item) => {
  const stored = readFileSync(projectPath(item.source))
  const bytes = item.encoding === "gzip-base64"
    ? gunzipSync(Buffer.from(stored.toString("utf8").trim(), "base64"))
    : stored
  if (bytes.length !== item.bytes || sha256(bytes) !== item.sha256) {
    throw new Error(`Invalid checked artifact: ${item.source}`)
  }
  return { ...item, bytes }
})
const circuit = JSON.parse(artifacts.find((item) => item.output.endsWith("/circuit.json")).bytes)
const errors = circuit.filter((item) => item.type?.endsWith("_error"))
if (errors.length) throw new Error(`Saved circuit contains ${errors.length} error records`)

for (const item of artifacts) {
  const output = projectPath(item.output)
  mkdirSync(dirname(output), { recursive: true })
  writeFileSync(output, item.bytes)
  console.log(`[cloud-build] Wrote ${item.output} (${item.bytes.length} bytes)`)
}
console.log("[cloud-build] Complete: checked circuit, PCB, schematic and 3D assembly")
