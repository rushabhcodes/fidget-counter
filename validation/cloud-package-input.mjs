import { createHash } from "node:crypto"

const dependencyFields = ["dependencies", "devDependencies", "optionalDependencies", "peerDependencies"]
const cloudCompiler = "file:/root/.bun/install/global/node_modules/tscircuit"
const sha256 = bytes => createHash("sha256").update(bytes).digest("hex")
const canonical = value => Array.isArray(value) ? value.map(canonical)
  : value && typeof value === "object"
    ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]))
    : value

// The registry sets the release version and replaces only the compiler entry.
// Keep every other package setting, including the component package versions.
const normalizedPackage = packageJson => {
  const normalized = structuredClone(packageJson)
  delete normalized.version
  for (const field of dependencyFields) {
    if (normalized[field]) delete normalized[field].tscircuit
  }
  return JSON.stringify(canonical(normalized))
}

export const getPackageInput = (packageJson, lockfile) => ({
  sha256: sha256(normalizedPackage(packageJson)),
  compilerVersion: packageJson.dependencies?.tscircuit ?? packageJson.devDependencies?.tscircuit,
  localLockfileSha256: sha256(lockfile),
})

export const verifyPackageInput = ({ packageJson, lockfile, expected, cloudBootstrap }) => {
  if (sha256(normalizedPackage(packageJson)) !== expected.sha256) {
    throw new Error("Stale preview: package.json settings or component dependencies changed")
  }
  const compilerVersions = dependencyFields.flatMap(field =>
    packageJson[field]?.tscircuit ? [packageJson[field].tscircuit] : [])
  if ((!cloudBootstrap && !compilerVersions.length) || compilerVersions.some(version =>
    version !== expected.compilerVersion && !(cloudBootstrap && version === cloudCompiler))) {
    throw new Error("Stale preview: unexpected tscircuit compiler dependency")
  }
  if (!cloudBootstrap && sha256(lockfile) !== expected.localLockfileSha256) {
    throw new Error("Stale preview: local bun.lock changed")
  }
}
