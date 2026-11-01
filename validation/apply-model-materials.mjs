// Restore per-part PBR finishes lost by tscircuit's OBJ-to-GLB converter.
// Split index ranges only: no vertices, normals, indices, transforms or copper
// buffers are edited. Cross-check source OBJ triangles before assigning finishes.
import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
const file=process.argv[2];assert(file,'Pass the generated GLB path')
const hash=b=>createHash('sha256').update(b).digest('hex')
const manifestBytes=readFileSync('mechanical/Circuit_Models/manifest.json')
const manifest=JSON.parse(manifestBytes),bytes=readFileSync(file)
assert.equal(bytes.readUInt32LE(0),0x46546c67);assert.equal(bytes.readUInt32LE(4),2)
const jsonLength=bytes.readUInt32LE(12),g=JSON.parse(bytes.subarray(20,20+jsonLength))
const binStart=20+jsonLength,bin=bytes.subarray(binStart+8,binStart+8+bytes.readUInt32LE(binStart))
assert.equal(bytes.readUInt32LE(binStart+4),0x004e4942)
const geometrySha256=hash(bin),manifestSha256=hash(manifestBytes)
if(g.extras?.fidgetModelMaterials?.manifestSha256===manifestSha256){
 assert.equal(g.extras.fidgetModelMaterials.geometrySha256,g.extras.fidgetSourceNormals?.originalBinarySha256??g.extras.fidgetLosslessCompact?.originalBinarySha256??geometrySha256)
 if(g.extras.fidgetSourceNormals&&g.extras.fidgetLosslessCompact)assert.equal(g.extras.fidgetSourceNormals.restoredBinarySha256,g.extras.fidgetLosslessCompact.originalBinarySha256)
 assert.equal(g.extras.fidgetLosslessCompact?.compactedBinarySha256??g.extras.fidgetSourceNormals?.restoredBinarySha256??geometrySha256,geometrySha256)
 console.log('Verified existing PBR material pass; geometry buffer unchanged');process.exit(0)
}
const finish={steel:[.9,.3],polished:[1,.16],plastic:[0,.4],nylon:[0,.52],rubber:[0,.72]}
let models=0,materials=0
for(const node of g.nodes.filter(n=>n.name?.startsWith('BEARING_V5_'))){
 const name=node.name.slice('BEARING_V5_'.length),groups=manifest.materialGroups[name]
 assert(groups?.length,`Missing source material groups: ${name}`)
 const mesh=g.meshes[node.mesh]
 if(manifest.assetFormat==='glb'){
  const expected=new Map(),actual=new Map()
  const key=part=>JSON.stringify([part.color,part.finish])
  for(const part of groups)expected.set(key(part),(expected.get(key(part))??0)+part.face_count*3)
  for(const primitive of mesh.primitives){
   const previous=g.materials[primitive.material].pbrMetallicRoughness?.baseColorFactor??[1,1,1,1]
   const matching=groups.filter(part=>part.color.every((v,i)=>Math.abs(v-previous[i])<.005))
   assert(matching.length,`Unmatched GLB material: ${name}`)
   assert.equal(new Set(matching.map(key)).size,1,`Ambiguous GLB material: ${name}`)
   const part=matching[0],count=primitive.indices===undefined?g.accessors[primitive.attributes.POSITION].count:g.accessors[primitive.indices].count
   actual.set(key(part),(actual.get(key(part))??0)+count)
   const [metallicFactor,roughnessFactor]=finish[part.finish]
   primitive.material=g.materials.length
   g.materials.push({name:`V5_${name}_${matching.map(p=>p.label).join('_')}`,pbrMetallicRoughness:{baseColorFactor:[...part.color,1],metallicFactor,roughnessFactor},alphaMode:'OPAQUE'})
   materials++
  }
  assert.deepEqual([...actual.entries()].sort(),[...expected.entries()].sort(),`GLB material triangle counts changed: ${name}`)
  models++;continue
 }
 assert.equal(mesh.primitives.length,1,`Unexpected GLB hierarchy: ${name}`)
 const primitive=mesh.primitives[0],indices=g.accessors[primitive.indices],view=g.bufferViews[indices.bufferView]
 assert.equal(indices.type,'SCALAR');assert([5123,5125].includes(indices.componentType))
 assert.equal(primitive.mode??4,4);assert(!view.byteStride)
 const size=indices.componentType===5125?4:2
 const indexStart=(view.byteOffset??0)+(indices.byteOffset??0)
 const indexAt=i=>size===4?bin.readUInt32LE(indexStart+i*size):bin.readUInt16LE(indexStart+i*size)
 const pos=g.accessors[primitive.attributes.POSITION],pv=g.bufferViews[pos.bufferView]
 assert.equal(pos.componentType,5126);assert.equal(pos.type,'VEC3')
 const positionAt=i=>[0,1,2].map(axis=>bin.readFloatLE((pv.byteOffset??0)+(pos.byteOffset??0)+i*(pv.byteStride??12)+axis*4))
 const vertices=[],faces=[]
 for(const line of readFileSync(`mechanical/Circuit_Models/${name}.obj`,'utf8').split('\n')){
  if(line.startsWith('v '))vertices.push(line.split(/\s+/).slice(1,4).map(Number))
  else if(line.startsWith('f '))faces.push(line.split(/\s+/).slice(1).map(s=>Number(s.split('/')[0])-1))
 }
 assert.equal(indices.count,faces.length*3,`Changed triangle count: ${name}`)
 assert.equal(groups.reduce((n,part)=>n+part.face_count,0)*3,indices.count)
 let nextFace=0
 for(const part of groups){
  assert.equal(part.first_face,nextFace,`Non-contiguous material ranges: ${name}`)
  assert(part.face_count>0);nextFace+=part.face_count
 }
 assert.equal(nextFace*3,indices.count)
 mesh.primitives=groups.map(part=>{
  // Three source triangles per part prove that ranges refer to the intended
  // component. Compare unordered corners to allow the required handedness flip.
  for(const faceIndex of new Set([part.first_face,part.first_face+Math.floor(part.face_count/2),part.first_face+part.face_count-1])){
   const expected=faces[faceIndex].map(i=>{const [x,y,z]=vertices[i];return [-x,z,y]})
   const actual=[0,1,2].map(i=>positionAt(indexAt(faceIndex*3+i)))
   for(const point of expected)assert(actual.some(p=>p.every((v,a)=>Math.abs(v-point[a])<.00002)),`Triangle ordering changed: ${name}/${part.label}`)
  }
  const [metallicFactor,roughnessFactor]=finish[part.finish]??[];assert(Number.isFinite(metallicFactor),part.finish)
  const material=g.materials.length;g.materials.push({name:`V5_${name}_${part.label}`,pbrMetallicRoughness:{baseColorFactor:[...part.color,1],metallicFactor,roughnessFactor},alphaMode:'OPAQUE'})
  const accessor=g.accessors.length
  const {min,max,...base}=indices
  g.accessors.push({...base,byteOffset:(indices.byteOffset??0)+part.first_face*3*size,count:part.face_count*3})
  assert((indices.byteOffset??0)+(part.first_face+part.face_count)*3*size<=view.byteLength)
  materials++;return {...primitive,indices:accessor,material}
 })
 models++
}
assert.equal(models,manifest.modelsPerSelectedStyle)
g.extras={...g.extras,fidgetModelMaterials:{manifestSha256,geometrySha256,models,materials,logicalMaterialGroups:g.nodes.filter(n=>n.name?.startsWith("BEARING_V5_")).reduce((sum,n)=>sum+manifest.materialGroups[n.name.slice("BEARING_V5_".length)].length,0)}}
let json=Buffer.from(JSON.stringify(g));if(json.length%4)json=Buffer.concat([json,Buffer.alloc(4-json.length%4,0x20)])
const header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(20+json.length+8+bin.length,8);header.writeUInt32LE(json.length,12);header.writeUInt32LE(0x4e4f534a,16)
const bh=Buffer.alloc(8);bh.writeUInt32LE(bin.length);bh.writeUInt32LE(0x004e4942,4)
const output=Buffer.concat([header,json,bh,bin]);assert.equal(hash(output.subarray(20+json.length+8)),geometrySha256)
writeFileSync(file,output)
console.log(`Applied ${materials} PBR finishes to ${models} models; geometry buffer SHA256 unchanged: ${geometrySha256}`)
