import {readFileSync,writeFileSync,mkdirSync} from "node:fs"
import {createHash} from "node:crypto"
import assert from "node:assert/strict"

const hash = bytes => createHash("sha256").update(bytes).digest("hex")
const parameters = JSON.parse(readFileSync("mechanical/enclosure-parameters.json"))
const manifest = JSON.parse(readFileSync("mechanical/Circuit_Models/manifest.json"))
const geometry = JSON.parse(readFileSync("mechanical/enclosure-validation.json"))
const stls = JSON.parse(readFileSync("validation/onepiece-stl-audit.json"))
assert.deepEqual(manifest.sourceParameters,parameters,"Mesh parameters are stale")
assert.deepEqual(geometry.parameters,parameters,"Geometry audit is stale")
assert.deepEqual(manifest.styles,parameters.cap_styles)
assert.equal(manifest.styles.length,11)
assert.equal(manifest.totalAssets,18)
assert.equal(manifest.modelsPerSelectedStyle,8)
assert.equal(geometry.printed_parts.length,14)
assert(geometry.printed_parts.every(p => p.valid && p.solids === 1))
assert.equal(geometry.press_rotation_checks.length,396)
assert(geometry.press_rotation_checks.every(p => p.rigid_collisions === 0))
assert(geometry.snap_release_checks.every(p => p.collision_mm3 === 0 && p.tabs_outward_mm === 0.8))
assert.equal(geometry.exact_shared_hub_magnet_poses,72)
assert.equal(geometry.cap_mount_screws,0)
assert.equal(geometry.separate_return_springs,0)
assert.equal(geometry.encoder_magnet_per_top_module,1)
assert.equal(parameters.overall_height,15.2)
assert.equal(parameters.grip_height,8)
assert.equal(parameters.button_travel,0.25)
assert(stls.passed && stls.parts.length === 14 && !stls.physically_tested)
for (const part of stls.parts)
  assert.equal(hash(readFileSync(`mechanical/Print_STL/${part.file}`)),part.sha256,`Stale print mesh: ${part.file}`)
for (const [file,sha] of Object.entries(manifest.modelSha256))
  assert.equal(hash(readFileSync(`mechanical/Circuit_Models/${file}`)),sha,`Stale circuit model: ${file}`)

const circuitBytes = readFileSync("dist/index/circuit.json")
const circuit = JSON.parse(circuitBytes)
const sources = circuit.filter(e => e.type === "source_component" && e.name?.startsWith("ONEPIECE_V4_"))
const ids = new Set(sources.map(e => e.source_component_id))
assert.equal(sources.length,8)
assert.equal(circuit.filter(e => e.type === "pcb_component" && ids.has(e.source_component_id)).length,0)
const style = readFileSync("index.circuit.tsx","utf8").match(/const CAP_STYLE: CapStyle = "([a-z_]+)"/)[1]
assert(manifest.styles.includes(style))
assert(sources.some(e => e.name === `ONEPIECE_V4_Cap_${style}`))
assert.equal(sources.filter(e => e.name.startsWith("ONEPIECE_V4_Cap_")).length,1)
const component = name => circuit.find(e => e.type === "pcb_component" && e.source_component_id ===
  circuit.find(s => s.type === "source_component" && s.name === name)?.source_component_id)
assert.deepEqual(component("SW1").center,{x:0,y:-5})
assert.equal(component("SW1").rotation,0)
assert.deepEqual(component("U2").center,{x:0,y:0})
for (const via of circuit.filter(e => e.type === "pcb_via")) {
  assert.equal(via.hole_diameter,0.3)
  assert.equal(via.outer_diameter,0.55)
}

const glbBytes = readFileSync("dist/index/3d.glb")
const gltf = JSON.parse(glbBytes.subarray(20,20 + glbBytes.readUInt32LE(12)).toString())
const reports = []
for (const source of sources) {
  const name = source.name.replace("ONEPIECE_V4_","")
  const cad = circuit.find(e => e.type === "cad_component" && e.source_component_id === source.source_component_id)
  assert(cad,`Missing CAD: ${name}`)
  assert.equal(cad.model_obj_url,`./mechanical/Circuit_Models/${name}.obj`)
  assert.equal(cad.model_mtl_url,`./mechanical/Circuit_Models/${name}.mtl`)
  assert.deepEqual(cad.position,{x:0,y:0,z:-7.6})
  assert.deepEqual(cad.rotation,{x:0,y:0,z:0})
  assert.deepEqual(cad.model_origin_position,{x:0,y:0,z:0})
  assert.equal(cad.model_unit_to_mm_scale_factor,1)
  const bounds = [[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
  for (const line of readFileSync(`mechanical/Circuit_Models/${name}.obj`,"utf8").split("\n")) {
    if (!line.startsWith("v ")) continue
    line.split(/\s+/).slice(1).map(Number).forEach((value,axis) => {
      bounds[0][axis] = Math.min(bounds[0][axis],value)
      bounds[1][axis] = Math.max(bounds[1][axis],value)
    })
  }
  const node = gltf.nodes.find(n => n.name === source.name && Number.isInteger(n.mesh))
  assert(node,`Missing GLB mesh: ${name}`)
  assert(!node.rotation && !node.matrix && !node.scale)
  const actual = [[Infinity,Infinity,Infinity],[-Infinity,-Infinity,-Infinity]]
  for (const primitive of gltf.meshes[node.mesh].primitives) {
    const positions = gltf.accessors[primitive.attributes.POSITION]
    for (let axis=0;axis<3;axis++) {
      actual[0][axis] = Math.min(actual[0][axis],positions.min[axis] + (node.translation?.[axis] ?? 0))
      actual[1][axis] = Math.max(actual[1][axis],positions.max[axis] + (node.translation?.[axis] ?? 0))
    }
  }
  const [min,max] = bounds
  const expected = [[-max[0],min[2]-7.6,min[1]],[-min[0],max[2]-7.6,max[1]]]
  const error = Math.max(...actual.flatMap((v,i) => v.map((n,j) => Math.abs(n-expected[i][j]))))
  assert(error < 0.0001,`Misaligned ${name}: ${error} mm`)
  reports.push({name,worldBoundsGltfMm:actual,maximumBoundsErrorMm:error})
}
mkdirSync("work",{recursive:true})
writeFileSync("work/enclosure-model-audit.json",JSON.stringify({
  revision:"1.0.7",selectedStyle:style,allCapStyles:manifest.styles,mechanicalModels:reports.length,
  circuitSha256:hash(circuitBytes),glbSha256:hash(glbBytes),models:reports,
  printParts:stls.parts.length,pressRotationConfigurationsCovered:396,physicalTested:false,
},null,2)+"\n")
console.log(`Pass: ${reports.length} aligned enclosure models, 11 interchangeable tops, inward SW1 and 0.30 mm via drills`)
