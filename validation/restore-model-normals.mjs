// Restore the smooth corner normals carried by our source GLB assets. The
// compiler's display conversion replaces these with per-face normals. Position
// streams and triangle order are hashed before/after and must remain identical.
import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
const file=process.argv[2],manifest=JSON.parse(readFileSync('mechanical/Circuit_Models/manifest.json'))
const hash=b=>createHash('sha256').update(b).digest('hex')
const load=b=>{const len=b.readUInt32LE(12);return {g:JSON.parse(b.subarray(20,20+len)),bin:b.subarray(28+len,28+len+b.readUInt32LE(20+len))}}
const blob=readFileSync(file),{g,bin}=load(blob)
if(g.extras?.fidgetSourceNormals){console.log('Verified source-normal stage already present');process.exit(0)}
const read=(g,b,id)=>{
 const a=g.accessors[id],v=g.bufferViews[a.bufferView];assert(!a.sparse)
 const dim={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],size={5121:1,5123:2,5125:4,5126:4}[a.componentType]
 const stride=v.byteStride??dim*size,start=(v.byteOffset??0)+(a.byteOffset??0)
 return {a,offset:i=>start+i*stride,vec:i=>[0,1,2].map(k=>b.readFloatLE(start+i*stride+k*4)),index:i=>a.componentType===5125?b.readUInt32LE(start+i*stride):a.componentType===5123?b.readUInt16LE(start+i*stride):b.readUInt8(start+i*stride)}
}
const ids=(g,b,p)=>p.indices===undefined?Array.from({length:g.accessors[p.attributes.POSITION].count},(_,i)=>i):Array.from({length:g.accessors[p.indices].count},(_,i)=>read(g,b,p.indices).index(i))
const positionDigest=()=>{
 const h=createHash('sha256')
 for(const mesh of g.meshes)for(const p of mesh.primitives){const a=read(g,bin,p.attributes.POSITION);for(const i of ids(g,bin,p))h.update(bin.subarray(a.offset(i),a.offset(i)+12))}
 return h.digest('hex')
}
const before=positionDigest(),originalBinarySha256=hash(bin),flags=new Map();let corners=0,models=0
const positionKey=v=>{const b=Buffer.alloc(12);v.forEach((x,i)=>b.writeFloatLE(x===0?0:x,i*4));return b.toString('hex')}
const canonical=keys=>{const variants=[keys,[keys[1],keys[2],keys[0]],[keys[2],keys[0],keys[1]]].map(k=>k.join(':'));const key=[...variants].sort()[0];return {key,shift:variants.indexOf(key)}}
const colour=(g,p)=>JSON.stringify(g.materials[p.material].pbrMetallicRoughness.baseColorFactor.map(v=>Math.round(v*1e6)/1e6))
for(const node of g.nodes.filter(n=>n.name?.startsWith('BEARING_V5_'))){
 const name=node.name.slice('BEARING_V5_'.length),source=load(readFileSync(`mechanical/Circuit_Models/${name}.glb`)),lookup=new Map()
 for(const mesh of source.g.meshes)for(const p of mesh.primitives){
  const pv=read(source.g,source.bin,p.attributes.POSITION),nv=read(source.g,source.bin,p.attributes.NORMAL),ii=ids(source.g,source.bin,p)
  for(let i=0;i<ii.length;i+=3){
   const keys=ii.slice(i,i+3).map(id=>{const [x,y,z]=pv.vec(id);return positionKey([-x,z,y])}),c=canonical(keys)
   const normals=ii.slice(i,i+3).map(id=>{const [x,y,z]=nv.vec(id);return [-x,z,y]})
   const ordered=[0,1,2].map(k=>normals[(k+c.shift)%3]);const key=colour(source.g,p)+c.key
   if(!lookup.has(key))lookup.set(key,[]);lookup.get(key).push(ordered)
  }
 }
 for(const p of g.meshes[node.mesh].primitives){
  const pv=read(g,bin,p.attributes.POSITION),nv=read(g,bin,p.attributes.NORMAL),ii=ids(g,bin,p)
  assert.equal(nv.a.componentType,5126)
  let marked=flags.get(p.attributes.NORMAL);if(!marked){marked=new Uint8Array(nv.a.count);flags.set(p.attributes.NORMAL,marked)}
  for(let i=0;i<ii.length;i+=3){
   const keys=ii.slice(i,i+3).map(id=>positionKey(pv.vec(id))),c=canonical(keys),key=colour(g,p)+c.key,entries=lookup.get(key)
   assert(entries?.length,`Source normal triangle not found: ${name}`)
   const sourceNormals=entries.pop()
   for(let k=0;k<3;k++){
    const id=ii[i+(k+c.shift)%3],values=sourceNormals[k],pos=nv.offset(id)
    if(marked[id])assert(values.every((v,a)=>Math.abs(bin.readFloatLE(pos+a*4)-v)<1e-6),`Conflicting source corner normals: ${name}`)
    values.forEach((v,a)=>bin.writeFloatLE(v,pos+a*4));marked[id]=1;corners++
   }
  }
 }
 assert([...lookup.values()].every(a=>a.length===0),`Unused source triangles: ${name}`);models++
}
assert.equal(models,manifest.modelsPerSelectedStyle);const after=positionDigest();assert.equal(after,before,'Position/triangle stream changed while restoring normals')
g.extras={...g.extras,fidgetSourceNormals:{models,corners,originalBinarySha256,restoredBinarySha256:hash(bin),inputPositionStreamSha256:before,outputPositionStreamSha256:after}}
let text=Buffer.from(JSON.stringify(g));text=Buffer.concat([text,Buffer.alloc((-text.length%4+4)%4,0x20)])
const header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67);header.writeUInt32LE(2,4);header.writeUInt32LE(20+text.length+8+bin.length,8);header.writeUInt32LE(text.length,12);header.writeUInt32LE(0x4e4f534a,16)
const bh=Buffer.alloc(8);bh.writeUInt32LE(bin.length);bh.writeUInt32LE(0x004e4942,4);writeFileSync(file,Buffer.concat([header,text,bh,bin]))
console.log(`Restored original smooth normals for ${models} models / ${corners} corners; position stream unchanged: ${after}`)
