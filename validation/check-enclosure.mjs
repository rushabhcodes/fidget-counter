import {readFileSync,writeFileSync,mkdirSync} from "node:fs"
import {createHash} from "node:crypto"
import assert from "node:assert/strict"
import {fittedComponentRecords} from "./fitted-component-records.mjs"

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
assert.equal(geometry.printed_parts.length,13)
assert(geometry.printed_parts.every(p => p.valid && p.solids === 1))
assert.equal(geometry.press_rotation_checks.length,396)
assert(geometry.press_rotation_checks.every(p => p.rigid_collisions === 0))
assert(geometry.snap_release_checks.every(p => p.collision_mm3 === 0 && p.tabs_outward_mm === 0.8))
assert.equal(geometry.exact_shared_hub_magnet_poses,108)
assert.equal(geometry.cap_mount_screws,0)
assert.equal(geometry.separate_return_springs,0)
assert.equal(geometry.encoder_magnet_per_top_module,1)
assert.equal(parameters.overall_height,15.2)
assert.equal(parameters.grip_height,8)
assert.equal(parameters.button_travel,0.25)
assert(stls.passed && stls.parts.length === 13 && !stls.physically_tested)
const locks=geometry.pcb_retention
assert.equal(locks.pcb_screws,0)
assert.equal(locks.separate_pcb_retainers,0)
assert.equal(locks.lock_count,2)
assert(locks.minimum_released_hook_to_hole_clearance_mm>.15)
assert(locks.minimum_locked_feature_to_hole_clearance_mm>.2)
assert(locks.locator_recess_below_board_top_mm>.3)
assert(locks.axial_float_mm>=.15-1e-7)
assert(locks.seated_base_to_pcb_intersection_mm3<.002)
assert(locks.released_base_to_pcb_intersection_mm3<.002)
assert(Math.abs(locks.mount_radius_mm-parameters.pcb_mount.radius_mm)<1e-7)
assert(locks.nominal_pcb_edge_web_mm>1.5)
assert.equal(locks.extraction_checks.length,13)
assert(locks.extraction_checks.every(p=>p.rigid_collisions===0))
assert.equal(geometry.encoder_spacer.thickness_mm,.2)
for (const part of stls.parts)
  assert.equal(hash(readFileSync(`mechanical/Print_STL/${part.file}`)),part.sha256,`Stale print mesh: ${part.file}`)
for (const [file,sha] of Object.entries(manifest.modelSha256))
  assert.equal(hash(readFileSync(`mechanical/Circuit_Models/${file}`)),sha,`Stale circuit model: ${file}`)

const circuitBytes = readFileSync("dist/index/circuit.json")
const circuit = JSON.parse(circuitBytes)
const mountClearance=JSON.parse(readFileSync("validation/pcb-mount-clearance.json"))
assert(mountClearance.passed && !mountClearance.physical_tested)
assert(mountClearance.base_to_actual_pcb_intersection_mm3<.002)
assert.equal(mountClearance.native_glb_holes.length,4)
for(const [file,sha] of Object.entries(mountClearance.sha256))
  assert.equal(hash(readFileSync(file)),sha,`Stale native PCB/base clearance check: ${file}`)
const connectorClearance=JSON.parse(readFileSync("validation/jst-connector-clearance.json"))
assert(connectorClearance.passed && !connectorClearance.physical_tested)
assert.equal(connectorClearance.cap_checks.length,11)
assert.equal(connectorClearance.continuous_rotation_deg,360)
assert.equal(connectorClearance.full_press_travel_mm,parameters.button_travel)
assert(connectorClearance.minimum_conservative_clearance_mm>.7)
for(const [file,sha] of Object.entries(connectorClearance.sha256))
  assert.equal(hash(readFileSync(file)),sha,`Stale JST/enclosure clearance check: ${file}`)
const sources = circuit.filter(e => e.type === "source_component" && e.name?.startsWith("ONEPIECE_V4_"))
const ids = new Set(sources.map(e => e.source_component_id))
assert.equal(sources.length,8)
assert.equal(circuit.filter(e => e.type === "pcb_component" && ids.has(e.source_component_id)).length,0)
const style = readFileSync("index.circuit.tsx","utf8").match(/const CAP_STYLE: CapStyle = "([a-z_]+)"/)[1]
assert(manifest.styles.includes(style))
assert(sources.some(e => e.name === `ONEPIECE_V4_Cap_${style}`))
assert.equal(sources.filter(e => e.name.startsWith("ONEPIECE_V4_Cap_")).length,1)
assert(sources.some(e=>e.name==="ONEPIECE_V4_Encoder_Spacer"))
assert(!sources.some(e=>/Screw|Fastener|PCB_Retainer/.test(e.name)))
assert.equal(circuit.filter(e=>e.type==="source_port"&&ids.has(e.source_component_id)).length,0)
const board=circuit.find(e=>e.type==="pcb_board")
assert.equal(board.thickness,parameters.pcb_thickness)
const holes=circuit.filter(e=>e.type==="pcb_hole"&&e.hole_diameter===locks.pcb_hole_diameter_mm)
assert.equal(holes.length,4)
for(const [x,y] of locks.mount_centers_mm) {
  const hole=holes.find(h=>Math.hypot(h.x-x,h.y-y)<1e-6)
  assert(hole,"PCB mounting hole and snap post are misaligned")
  assert.equal(hole.hole_diameter,locks.pcb_hole_diameter_mm)
}
const fittedBaseline=JSON.parse(readFileSync("validation/fitted-component-baseline.json"))
assert.equal(fittedBaseline.components.length,30)
assert.deepEqual(fittedComponentRecords(circuit).filter(e=>e.source.name!=="J_DEBUG"),fittedBaseline.components,
  "Fitted component identities, copper footprints, placement or CAD changed from the pre-TC2030 draft")
assert.equal(fittedComponentRecords(circuit).length,31)
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
    line.split(/\s+/).slice(1,4).map(Number).forEach((value,axis) => {
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
  revision:"Inward-hole, clearance-fit snap draft based on 1.0.9",selectedStyle:style,allCapStyles:manifest.styles,mechanicalModels:reports.length,
  circuitSha256:hash(circuitBytes),glbSha256:hash(glbBytes),models:reports,
  printParts:stls.parts.length,pressRotationConfigurationsCovered:396,physicalTested:false,
  pcbRetention:locks,fittedComponentsUnchangedFrom:"pre-TC2030 automatic-lock 1.0.9 draft",
  nativePcbAndBaseClearanceVerified:true,
  jstConnectorClearance:connectorClearance.minimum_conservative_clearance_mm,
},null,2)+"\n")
console.log(`Pass: ${reports.length} aligned enclosure models, 11 interchangeable tops, two automatic PCB locks, zero PCB screws; 30 original fitted component records unchanged plus the JST connector`)
