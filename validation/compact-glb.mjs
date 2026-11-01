// Lossless indexed display packing. Every rendered corner attribute is checked
// byte-for-byte before/after; nodes, triangle order and materials are preserved.
import assert from 'node:assert/strict'
import {readFileSync,writeFileSync} from 'node:fs'
import {createHash} from 'node:crypto'
const file=process.argv[2];assert(file,'Pass the generated GLB')
const original=readFileSync(file),jlen=original.readUInt32LE(12)
const g=JSON.parse(original.subarray(20,20+jlen));const start=20+jlen
const bin=original.subarray(start+8,start+8+original.readUInt32LE(start))
const sha=b=>createHash('sha256').update(b).digest('hex')
if(g.extras?.fidgetLosslessCompact){
 assert.equal(sha(bin),g.extras.fidgetLosslessCompact.compactedBinarySha256)
 console.log('Verified lossless compact GLB');process.exit(0)
}
assert(!g.animations?.length&&!g.skins?.length,'Unsupported animated display asset')
const dimensions={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16}
const widths={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}
const read=(json,data,id)=>{
 const a=json.accessors[id],v=json.bufferViews[a.bufferView];assert(!a.sparse);assert.equal(v.buffer??0,0)
 const width=widths[a.componentType]*dimensions[a.type];assert(width)
 const offset=(v.byteOffset??0)+(a.byteOffset??0),stride=v.byteStride??width
 return {accessor:a,width,row:i=>data.subarray(offset+i*stride,offset+i*stride+width)}
}
const indices=(json,data,p)=>{
 if(p.indices===undefined)return Array.from({length:json.accessors[p.attributes.POSITION].count},(_,i)=>i)
 const a=read(json,data,p.indices);assert.equal(a.accessor.type,'SCALAR')
 return Array.from({length:a.accessor.count},(_,i)=>a.accessor.componentType===5125?a.row(i).readUInt32LE():a.accessor.componentType===5123?a.row(i).readUInt16LE():a.row(i).readUInt8())
}
const streamDigest=(json,data)=>{
 const h=createHash('sha256')
 for(let mi=0;mi<json.meshes.length;mi++)for(let pi=0;pi<json.meshes[mi].primitives.length;pi++){
  const p=json.meshes[mi].primitives[pi],names=Object.keys(p.attributes).sort(),attrs=names.map(n=>read(json,data,p.attributes[n]))
  h.update(JSON.stringify([mi,pi,p.mode??4,names,attrs.map(a=>[a.accessor.type,a.accessor.componentType,!!a.accessor.normalized])]))
  for(const id of indices(json,data,p))for(const a of attrs)h.update(a.row(id))
 }
 return h.digest('hex')
}
const before=streamDigest(g,bin),oldViews=g.bufferViews,oldAccessors=g.accessors
const chunks=[],views=[],accessors=[];let total=0,oldVertices=0,newVertices=0
const addView=(data,target)=>{
 if(total%4){const pad=Buffer.alloc(4-total%4);chunks.push(pad);total+=pad.length}
 const index=views.length;views.push({buffer:0,byteOffset:total,byteLength:data.length,...(target?{target}:{})});chunks.push(data);total+=data.length;return index
}
const old={...g,bufferViews:oldViews,accessors:oldAccessors}
for(const mesh of g.meshes)for(const p of mesh.primitives){
 assert(!p.targets?.length);const names=Object.keys(p.attributes).sort(),attrs=names.map(n=>read(old,bin,p.attributes[n]))
 const ids=indices(old,bin,p),lookup=new Map(),rows=names.map(()=>[]),mapped=Buffer.alloc(ids.length*4)
 for(let i=0;i<ids.length;i++){
  const values=attrs.map(a=>a.row(ids[i])),key=Buffer.concat(values).toString('latin1');let id=lookup.get(key)
  if(id===undefined){id=lookup.size;lookup.set(key,id);values.forEach((v,k)=>rows[k].push(v))}
  mapped.writeUInt32LE(id,i*4)
 }
 oldVertices+=attrs[0].accessor.count;newVertices+=lookup.size
 const next={}
 names.forEach((name,k)=>{
  const a=attrs[k].accessor,{bufferView,byteOffset,count,min,max,sparse,...meta}=a,data=Buffer.concat(rows[k])
  const id=accessors.length;const extra={}
  if(name==='POSITION'){
   assert.equal(a.componentType,5126);assert.equal(a.type,'VEC3')
   extra.min=[Infinity,Infinity,Infinity];extra.max=[-Infinity,-Infinity,-Infinity]
   for(let i=0;i<lookup.size;i++)for(let axis=0;axis<3;axis++){const v=data.readFloatLE(i*12+axis*4);extra.min[axis]=Math.min(extra.min[axis],v);extra.max[axis]=Math.max(extra.max[axis],v)}
  }
  accessors.push({...meta,bufferView:addView(data,34962),count:lookup.size,...extra});next[name]=id
 })
 p.attributes=next;p.indices=accessors.length
 accessors.push({bufferView:addView(mapped,34963),componentType:5125,count:ids.length,type:'SCALAR'})
}
for(const image of g.images??[])if(image.bufferView!==undefined){const v=oldViews[image.bufferView];image.bufferView=addView(bin.subarray(v.byteOffset??0,(v.byteOffset??0)+v.byteLength))}
if(total%4){const pad=Buffer.alloc(4-total%4);chunks.push(pad);total+=pad.length}
const packed=Buffer.concat(chunks);g.bufferViews=views;g.accessors=accessors;g.buffers=[{byteLength:packed.length}]
const after=streamDigest(g,packed);assert.equal(after,before,'Display geometry/corner attributes changed during packing')
g.extras={...g.extras,fidgetLosslessCompact:{originalBinarySha256:sha(bin),compactedBinarySha256:sha(packed),inputRenderStreamSha256:before,outputRenderStreamSha256:after,verticesBefore:oldVertices,verticesAfter:newVertices}}
let json=Buffer.from(JSON.stringify(g));json=Buffer.concat([json,Buffer.alloc((-json.length%4+4)%4,0x20)])
const header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67);header.writeUInt32LE(2,4);header.writeUInt32LE(20+json.length+8+packed.length,8);header.writeUInt32LE(json.length,12);header.writeUInt32LE(0x4e4f534a,16)
const bh=Buffer.alloc(8);bh.writeUInt32LE(packed.length);bh.writeUInt32LE(0x004e4942,4)
const result=Buffer.concat([header,json,bh,packed]);writeFileSync(file,result)
console.log(`Lossless GLB packing: ${original.length} -> ${result.length} bytes; rendered attribute stream unchanged: ${after}`)
