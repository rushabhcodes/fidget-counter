import {readFileSync,writeFileSync,mkdirSync} from "node:fs"
import {createHash} from "node:crypto"
import assert from "node:assert/strict"

const hash = bytes => createHash("sha256").update(bytes).digest("hex")
const manifest = JSON.parse(readFileSync("mechanical/Circuit_Models/manifest.json"))
assert.deepEqual(manifest.sourceParameters,JSON.parse(readFileSync("mechanical/enclosure-parameters.json")),
  "Enclosure mesh assets are stale; regenerate from the current CAD parameters")
const geometry = JSON.parse(readFileSync("mechanical/enclosure-validation.json"))
assert.deepEqual(geometry.parameters_mm,manifest.sourceParameters,"Stale enclosure geometry audit")
assert.equal(geometry.collision_audit.length,0,"Unintended mechanical collision remains")
assert(geometry.manifest.every(part => part.cad_valid),"Invalid enclosure solid remains")
if (manifest.sourceParameters.attachment_mode === "disc_array") {
  const layout = geometry.attachment_disc_array
  assert.equal(layout.count,manifest.sourceParameters.attachment_disc_count)
  assert.equal(layout.centers_mm.length,layout.count)
  assert.equal(layout.diameter_mm,manifest.sourceParameters.attachment_disc_diameter)
  assert.equal(layout.thickness_mm,manifest.sourceParameters.attachment_magnet_thickness)
  assert(layout.minimum_pocket_web_mm >= 1 && layout.inner_wall_mm >= 1)
  assert(layout.outer_wall_mm >= 0.8-1e-6 && layout.housing_outer_rim_mm >= 0.8-1e-6)
  assert(layout.floor_thickness_mm >= 0.6)
  assert(Math.abs(layout.pocket_depth_mm-layout.thickness_mm-layout.adhesive_allowance_mm)<1e-6)
}
const circuitBytes = readFileSync("dist/index/circuit.json")
const circuit = JSON.parse(circuitBytes)
const sources = circuit.filter(e => e.type === "source_component" && e.name?.startsWith("ENCLOSURE_"))
const assemblyIds = new Set(sources.map(e => e.source_component_id))
assert.equal(sources.length,14)
assert.equal(circuit.filter(e => e.type === "pcb_component" && assemblyIds.has(e.source_component_id)).length,0)
// Baseline: the checked v1.0.3 board at Git commit 8d744cd. Metadata hashes and
// the newly added mechanical-only records are the sole excluded records.
const electronics = circuit.filter(e => e.type !== "source_project_metadata" &&
  !(["source_component","cad_component"].includes(e.type) && assemblyIds.has(e.source_component_id)))
const electricalHash = hash(JSON.stringify(electronics))
assert.equal(electricalHash,"2f61bd60f92435a4ff0948e47598774b3395add7e045356aa0880ad5f3d10843",
  "Electrical geometry or connectivity changed from the checked holder revision")
const glbBytes = readFileSync("dist/index/3d.glb")
const gltf = JSON.parse(glbBytes.subarray(20,20 + glbBytes.readUInt32LE(12)).toString())
const reports = []
for (const part of manifest.parts) {
  for (const [file,sha] of Object.entries(part.sha256))
    assert.equal(hash(readFileSync(`mechanical/Circuit_Models/${file}`)),sha,`Changed asset: ${file}`)
  const name = `ENCLOSURE_${part.name}`
  const source = sources.find(e => e.name === name)
  assert(source,`Missing assembly source: ${name}`)
  const cad = circuit.find(e => e.type === "cad_component" && e.source_component_id === source.source_component_id)
  assert(cad,`Missing assembly CAD: ${name}`)
  assert.equal(cad.model_obj_url,`./mechanical/Circuit_Models/${part.name}.obj`)
  assert.equal(cad.model_mtl_url,`./mechanical/Circuit_Models/${part.name}.mtl`)
  assert.deepEqual(cad.position,{x:0,y:0,z:-manifest.pcbMidplaneZMm})
  assert.deepEqual(cad.rotation,{x:0,y:0,z:0})
  assert.deepEqual(cad.model_origin_position,{x:0,y:0,z:0})
  assert.equal(cad.model_unit_to_mm_scale_factor,1)
  assert.equal(cad.show_as_translucent_model,part.translucent)
  const node = gltf.nodes.find(n => n.name === name && Number.isInteger(n.mesh))
  assert(node,`Missing exported mesh: ${name}`)
  assert(!node.rotation && !node.matrix && !node.scale,`Unexpected model transform: ${name}`)
  const actual = [[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
  for (const primitive of gltf.meshes[node.mesh].primitives) {
    const positions = gltf.accessors[primitive.attributes.POSITION]
    for (let axis=0;axis<3;axis++) {
      actual[0][axis] = Math.min(actual[0][axis],positions.min[axis] + (node.translation?.[axis] ?? 0))
      actual[1][axis] = Math.max(actual[1][axis],positions.max[axis] + (node.translation?.[axis] ?? 0))
    }
  }
  // The exporter consistently maps circuit (x,y,z) to GLTF (-x,z,y).
  const [min,max] = part.boundsMm
  const expected = [[-max[0],min[2]-manifest.pcbMidplaneZMm,min[1]],
                    [-min[0],max[2]-manifest.pcbMidplaneZMm,max[1]]]
  const error = Math.max(...actual.flatMap((v,i) => v.map((n,j) => Math.abs(n-expected[i][j]))))
  assert(error < 0.0001,`Misaligned model: ${name}, error ${error} mm`)
  reports.push({name,worldBoundsGltfMm:actual,maximumBoundsErrorMm:error,translucent:part.translucent})
}
mkdirSync("work",{recursive:true})
writeFileSync("work/enclosure-model-audit.json",JSON.stringify({
  electricalBaselineVersion:"1.0.3",electricalRecordsUnchanged:true,electricalRecordsSha256:electricalHash,
  circuitSha256:hash(circuitBytes),glbSha256:hash(glbBytes),mechanicalModels:reports.length,
  pcbMidplaneOffsetMm:-manifest.pcbMidplaneZMm,models:reports,
  sourceSha256:Object.fromEntries(["enclosure.tsx","mechanical/export_circuit_models.py",
    "mechanical/build_enclosure.py","mechanical/Circuit_Models/manifest.json"].map(p=>[p,hash(readFileSync(p))])),
},null,2)+"\n")
console.log("Pass: 14 aligned enclosure models; electrical records unchanged; portable model URLs")
