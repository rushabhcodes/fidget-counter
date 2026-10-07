import { spawn } from "node:child_process"
import { mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { createHash } from "node:crypto"
import { runAllChecks } from "@tscircuit/checks"
import { gerberCompatibleCircuit } from "./gerber-compat.mjs"

mkdirSync("work", { recursive: true })
const run = (args) => new Promise((resolve, reject) => {
  const child = spawn("bun", args, { stdio: ["ignore", "pipe", "pipe"] })
  let output = ""
  child.stdout.on("data", data => { output += data })
  child.stderr.on("data", data => { output += data })
  child.on("error", reject)
  child.on("close", code => resolve({ code, output }))
})
const check = async (name, args) => {
  const result = await run(args)
  writeFileSync(`work/${name}.log`, result.output)
  if (result.code !== 0 || /Errors:\s*[1-9]|Async effect error/.test(result.output)) {
    throw new Error(`${name} failed; see work/${name}.log`)
  }
  if (name === "schematic-placement" && result.output.includes("<SchematicPlacementIssues>")) {
    throw new Error("Schematic placement issues remain")
  }
  if (name === "placement" && !result.output.includes("placement summary: no placement issues")) {
    throw new Error("PCB placement issues remain")
  }
  console.log(`Pass: ${name}`)
  return result.output
}

await Promise.all([
  check("typecheck", ["run", "typecheck"]),
  check("netlist", ["run", "tsci", "check", "netlist", "index.circuit.tsx"]),
  check("pin_specification", ["run", "tsci", "check", "pin_specification", "index.circuit.tsx"]),
  check("source", ["run", "tsci", "check", "source", "index.circuit.tsx"]),
])
// Congestion estimates are advisory. The routed build below determines success.
await Promise.all([
  check("schematic-placement", ["run", "tsci", "check", "schematic-placement", "index.circuit.tsx"]),
  check("placement", ["run", "tsci", "check", "placement", "index.circuit.tsx"]),
  check("routing-difficulty", ["run", "tsci", "check", "routing-difficulty", "index.circuit.tsx"]),
])
await check("build", ["run", "tsci", "build", "index.circuit.tsx", "--pcb-png", "--schematic-png", "--svgs", "--glbs", "--3d-png", "--disable-parts-engine"])

const circuitBytes = readFileSync("dist/index/circuit.json")
const circuit = JSON.parse(circuitBytes)
const buildIssues = circuit.filter(element => /error|warning/.test(element.type))
const findings = await runAllChecks(circuit)
writeFileSync("work/all-checks.json", JSON.stringify(findings, null, 2) + "\n")
if (buildIssues.length || findings.length) {
  throw new Error(`${buildIssues.length} build issues and ${findings.length} validator findings remain`)
}
writeFileSync("work/gerber-compatible.circuit.json", JSON.stringify(gerberCompatibleCircuit(circuit), null, 2) + "\n")
await check("shorts", ["run", "tsci", "check", "shorts", "work/gerber-compatible.circuit.json"])

const components = new Map(circuit.filter(element => element.type === "source_component")
  .map(element => [element.source_component_id, element.name]))
const targets = new Map()
for (const net of circuit.filter(element => element.type === "source_net")) {
  targets.set(net.subcircuit_connectivity_map_key, `net.${net.name}`)
}
for (const port of circuit.filter(element => element.type === "source_port")) {
  const key = port.subcircuit_connectivity_map_key
  const name = components.get(port.source_component_id)
  if (key && name && !targets.has(key)) targets.set(key, `${name}.${port.name}`)
}
const reports = []
const traceSummaries = []
const targetNames = [...targets.values()]
for (let offset = 0; offset < targetNames.length; offset += 3) {
 const results = await Promise.all(targetNames.slice(offset, offset + 3).map(async target => {
  const result = await run(["run", "tsci", "check", "trace-length", target, "dist/index/circuit.json"])
  if (result.code !== 0 || !result.output.includes("<TraceLengthAnalysis")) {
    throw new Error(`Trace length analysis failed for ${target}: ${result.output}`)
  }
  return { output: result.output.trim(), summary: { target,
    routedLengthMm: Number(result.output.match(/totalLengthMm="([\d.]+)"/)?.[1]),
    traceCount: Number(result.output.match(/traceCount="(\d+)"/)?.[1]) } }
 }))
 for (const result of results) {
  reports.push(result.output)
  traceSummaries.push(result.summary)
 }
}
writeFileSync("work/trace-length.log", reports.join("\n\n") + "\n")
writeFileSync("work/trace-length-summary.json", JSON.stringify(traceSummaries, null, 2) + "\n")

const crystalTraces = circuit.filter(element => element.type === "source_trace" &&
  element.max_length === 10 && element.max_via_count === 0)
const clocks = crystalTraces.map(source => {
  const routes = circuit.filter(element => element.type === "pcb_trace" && element.source_trace_id === source.source_trace_id)
  let length = 0
  let vias = 0
  for (const trace of routes) {
    let previous
    for (const point of trace.route) {
      if (point.route_type === "via") { vias++; previous = undefined; continue }
      if (previous && previous.layer === point.layer) length += Math.hypot(point.x - previous.x, point.y - previous.y)
      previous = point
    }
  }
  if (!routes.length || vias || length > 10) throw new Error(`Crystal constraint failed: ${source.name}`)
  return { name: source.name, lengthMm: length, vias }
})
if (clocks.length !== 8) throw new Error(`Expected all eight crystal signal branches, found ${clocks.length}`)
const sha256 = file => createHash("sha256").update(readFileSync(file)).digest("hex")
const summary = {
  checkedAt: new Date().toISOString(),
  checks: ["netlist", "pin_specification", "source", "schematic-placement", "placement", "routing-difficulty", "shorts", "trace-length"],
  errors: 0, warnings: 0,
  routedTraces: circuit.filter(element => element.type === "pcb_trace").length,
  vias: circuit.filter(element => element.type === "pcb_via").length,
  analyzedNetCount: targets.size, crystalBranches: clocks,
  sha256: Object.fromEntries(["index.circuit.tsx", "parts.tsx", "passives.tsx", "model-assets.d.ts", "routing.ts", "routed-paths.json", "published.circuit.json", "package.json", "verify.mjs", "gerber-compat.mjs", "export-gerbers.mjs", "dist/index/circuit.json"].map(file => [file, sha256(file)])),
}
writeFileSync("work/check-all-summary.json", JSON.stringify(summary, null, 2) + "\n")
console.log(`Pass: all library checks; trace lengths for ${targets.size} nets; eight crystal branches have no vias`)
console.log(`Complete: ${summary.routedTraces} routed traces, ${summary.vias} vias, zero errors and warnings`)
