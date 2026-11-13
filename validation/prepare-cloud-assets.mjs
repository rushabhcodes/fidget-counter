import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync,mkdirSync,readdirSync,unlinkSync} from 'node:fs'
import {dirname,resolve,relative,extname} from 'node:path'
import {fileURLToPath} from 'node:url'
import {gzipSync} from 'node:zlib'
import {getPackageInput} from './cloud-package-input.mjs'
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..')
const read=name=>readFileSync(resolve(root,name))
const sha=bytes=>createHash('sha256').update(bytes).digest('hex')
const pkg=JSON.parse(read('package.json')),config=JSON.parse(read('tscircuit.config.json'))
const version=pkg.version,folder='mechanical/variants/V3_disc_magnets'
const cadVersion=JSON.parse(read(`${folder}/parameters.json`)).release
const walk=path=>readdirSync(path,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(resolve(path,e.name)):[resolve(path,e.name)])
const variantFiles={
  'review.html':'index.html','review.png':'review.png',
  [`exploded-v${cadVersion}.png`]:`exploded-v${cadVersion}.png`,
  'encoder-orientation.png':'encoder-orientation.png',
  ...Object.fromEntries(readdirSync(resolve(root,folder,'drawings')).map(name=>['drawings/'+name,'drawings/'+name])),
}
const variantArtifacts=Object.entries(variantFiles).map(([name,target])=>{
  const source=`${folder}/${name}`,bytes=read(source)
  return {source,output:`dist/v3/${target}`,sha256:sha(bytes),bytes:bytes.length}
})
// Manufacturing STEP/STL and historical assemblies stay in GitHub CAD kits.
// The registry needs checked source, runtime models and native drawing outputs.
const inputs=[
  ...readdirSync(root).filter(name=>/\.(tsx?|circuit\.json)$/.test(name)),
  'routed-paths.json','critical-routes.json','routing-contract.json','tsconfig.json',
  'cloud-build.mjs','tscircuit.config.json','validation/prepare-cloud-assets.mjs',
  'validation/cloud-package-input.mjs','validation/restore-cad-inputs.mjs',
  'validation/enrich-orientations.mjs','validation/prepare-supplier-frames.mjs',
  'validation/import-provenance.mjs','validation/jlc-imports.json',
  'validation/check-fresh-routing.mjs','validation/fresh-routing-reference.json',
  'validation/fitted-component-records.mjs','validation/nordic-electrical-revision.mjs',
  'validation/nordic-electrical-reference.json','validation/check-nordic-rf.py',
  'validation/normalize-compiler-output.mjs','validation/compiler-compat-reference.json',
  'validation/resolve-native-drawing-dimensions.mjs','validation/check-native-drawings.mjs',
  'validation/source-snapshot-audit.json','validation/native-drawing-audit.json',
  'validation/check-disc-variant.mjs','validation/check-source-snapshot.mjs',
  'validation/apply-model-materials.mjs','validation/compact-glb.mjs','validation/restore-model-normals.mjs',
  ...variantArtifacts.map(a=>a.source),
  ...walk(resolve(root,'imports')).filter(p=>extname(p)!=='.step').map(p=>relative(root,p)),
  ...walk(resolve(root,'mechanical')).filter(p=>{
    const name=relative(root,p)
    if(name.startsWith('mechanical/export/')||name.includes('/__pycache__/')||/_meshes\.json$/.test(name))return false
    return ['.py','.json'].includes(extname(p))||(name.startsWith('mechanical/Circuit_Models/')&&extname(p)==='.glb')
  }).map(p=>relative(root,p)),
]
const manifest={formatVersion:3,description:'Checked latest-tsCircuit preview and native engineering drawings; manufacturing CAD ships in GitHub kits.',inputs:Object.fromEntries([...new Set(inputs)].sort().map(name=>[name,sha(read(name))])),packageInput:getPackageInput(pkg,read('bun.lock')),artifacts:[],variantArtifacts}
const cacheDir=resolve(root,'cloud-assets');mkdirSync(cacheDir,{recursive:true})
for(const name of readdirSync(cacheDir))if(name.endsWith('.b64'))unlinkSync(resolve(cacheDir,name))
const ignored=name=>config.ignoredFiles.some(pattern=>new Bun.Glob(pattern).match(name)||(pattern.startsWith('**/')&&new Bun.Glob(pattern.slice(3)).match(name)))
const packedNames=Object.keys(manifest.inputs).filter(name=>ignored(name))
const groups=[];let group=[],size=0
for(const name of packedNames){
  const bytes=read(name)
  if(size+bytes.length>5_500_000&&group.length){groups.push(group);group=[];size=0}
  group.push({path:name,contentBase64:bytes.toString('base64')});size+=bytes.length
}
if(group.length)groups.push(group)
function writePacked(prefix,bytes){
  const encoded=Buffer.from(gzipSync(bytes,{level:9}).toString('base64')+'\n'),parts=[]
  for(let offset=0;offset<encoded.length;offset+=3_000_000){
    const name=`cloud-assets/${prefix}.part-${String(parts.length).padStart(3,'0')}.gz.b64`
    writeFileSync(resolve(root,name),encoded.subarray(offset,offset+3_000_000));parts.push(name)
  }
  return {parts,packed:encoded}
}
manifest.cadInputArchives=groups.map((entries,index)=>{
  const {parts,packed}=writePacked(`runtime-inputs-${index}`,Buffer.from(JSON.stringify(entries)))
  return {source:parts[0],sourceParts:parts,sha256:sha(packed),files:entries.map(e=>e.path)}
})
function artifact(prefix,output,bytes){
  const {parts}=writePacked(prefix,bytes)
  manifest.artifacts.push({source:parts[0],sourceParts:parts,output,encoding:'gzip-base64',bytes:bytes.length,sha256:sha(bytes)})
}
for(const name of ['circuit.json','pcb.png','pcb.svg','schematic.png','schematic.svg','3d.glb','3d.png']){
  let bytes=read(`dist/published/${name}`)
  if(name==='circuit.json'){
    const saved=read('published.circuit.json')
    if(!bytes.equals(saved)&&!Buffer.concat([bytes,Buffer.from('\n')]).equals(saved))throw new Error('Main preview differs from checked snapshot')
    bytes=saved;writeFileSync(resolve(root,'dist/published/circuit.json'),bytes)
  }
  artifact('preview-'+name,`dist/published/${name}`,bytes)
}
const drawing=read('dist/enclosure-drawing/circuit.json'),savedDrawing=read('enclosure-drawing.circuit.json')
if(!drawing.equals(savedDrawing)&&!Buffer.concat([drawing,Buffer.from('\n')]).equals(savedDrawing))throw new Error('Native drawing differs from checked document')
artifact('native-drawing-document','dist/enclosure-drawing/circuit.json',savedDrawing)
for(const name of ['enclosure-assembly.svg','enclosure-magnet-details.svg'])artifact('native-'+name,`dist/enclosure-drawing/drawings/${name}`,read(`dist/enclosure-drawing/drawings/${name}`))
artifact('native-drawing-preview','dist/enclosure-drawing/3d.png',read('dist/enclosure-drawing/3d.png'))
let html=read('dist/index.html').toString()
if(html.includes('src="./standalone.min.js"'))throw new Error('Build the site with --use-cdn-javascript before preparing cloud assets')
if(!html.includes('enclosure-drawing.circuit.json'))throw new Error('Native drawing is missing from the site file list')
if(!html.includes('engineering-download'))html=html.replace('</body>',`<a id="engineering-download" href="./v3/drawings/engineering-drawing-v${version}.pdf" style="position:fixed;right:12px;bottom:12px;z-index:10000;background:white;border:1px solid #ccd2d8;border-radius:6px;padding:8px 12px;font:14px system-ui;color:#163b56">Download A3 drawing PDF</a></body>`)
artifact('native-site','dist/index.html',Buffer.from(html))
writeFileSync(resolve(cacheDir,'manifest.json'),JSON.stringify(manifest,null,2)+'\n')
console.log(`Prepared ${manifest.artifacts.length} native preview/site artifacts, ${variantArtifacts.length} engineering review files and ${Object.keys(manifest.inputs).length} checked source/runtime inputs; manufacturing CAD stays in GitHub kits`)
