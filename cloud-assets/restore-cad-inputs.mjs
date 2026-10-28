import { createHash } from "node:crypto"
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { gunzipSync } from "node:zlib"

const hash = bytes => createHash("sha256").update(bytes).digest("hex")

const restoreArchive = (root, manifest, archive) => {
  const packed = readFileSync(resolve(root, archive.source))
  if (hash(packed) !== archive.sha256) throw new Error("Invalid checked CAD input archive")
  const entries = JSON.parse(gunzipSync(Buffer.from(packed.toString("utf8").trim(), "base64")))
  if (entries.length !== archive.files.length) throw new Error("Incomplete checked CAD input archive")
  const seen = new Set()
  for (const entry of entries) {
    if (!archive.files.includes(entry.path) || seen.has(entry.path)) throw new Error("Unexpected CAD archive entry")
    seen.add(entry.path)
    const path = resolve(root, entry.path)
    if (!path.startsWith(root + "/")) throw new Error("Invalid CAD archive path")
    const bytes = Buffer.from(entry.contentBase64, "base64")
    if (hash(bytes) !== manifest.inputs[entry.path]) throw new Error(`Invalid checked CAD input: ${entry.path}`)
    if (existsSync(path)) {
      if (hash(readFileSync(path)) !== manifest.inputs[entry.path]) throw new Error(`Stale preview: ${entry.path} changed`)
    } else {
      mkdirSync(dirname(path), { recursive: true })
      writeFileSync(path, bytes)
    }
  }
}

export const restoreCadInputs = (root, manifest) => {
  if (!manifest.cadInputArchives?.length) throw new Error("Missing checked CAD input archives")
  for (const archive of manifest.cadInputArchives) restoreArchive(root, manifest, archive)
}
