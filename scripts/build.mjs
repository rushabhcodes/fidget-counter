import {spawnSync} from 'node:child_process'
import {cpSync,existsSync,mkdirSync,statSync,rmSync,readFileSync,writeFileSync} from 'node:fs'
import {resolve} from 'node:path'

const cli=existsSync('node_modules/.bin/tsci')?resolve('node_modules/.bin/tsci'):'tscircuit'
const run=(command,args)=>{
  const result=spawnSync(command,args,{stdio:'inherit',env:process.env})
  if(result.error)throw result.error
  if(result.status!==0)process.exit(result.status??1)
}

// Every view is compiled from the same TypeScript circuit. Circuit JSON, images and the site
// are build products under dist/, never a second source of truth in Git.
mkdirSync('dist/validation',{recursive:true})
run(cli,['build','--site','--use-cdn-javascript','--glbs','--3d-png',
  '--pcb-png','--schematic-png','--svgs','--disable-parts-engine','--concurrency','1'])
run(process.execPath,['scripts/drawing-dimensions.mjs'])
cpSync('dist/index.circuit.json','dist/index/circuit.json')
// A single-circuit site embeds its initial JSON. Refresh that native payload
// after dimension resolution so the website and downloadable circuit agree.
const site=readFileSync('dist/index.html','utf8')
const json=readFileSync('dist/index/circuit.json','utf8').trim().replaceAll('<','\\u003c')
const embedded=/window\.TSCIRCUIT_RUNFRAME_STATIC_FILE_LIST\[0\]\.fileStaticAssetUrl = URL\.createObjectURL\(new Blob\(\[JSON\.stringify\([\s\S]*?\)\], \{ type: "application\/json" \}\)\);/
if(!embedded.test(site))throw new Error('Expected the native single-circuit site payload')
writeFileSync('dist/index.html',site.replace(embedded,()=>`window.TSCIRCUIT_RUNFRAME_STATIC_FILE_LIST[0].fileStaticAssetUrl = URL.createObjectURL(new Blob([JSON.stringify(${json})], { type: "application/json" }));`))

run(cli,['build','dist/index.circuit.json','--ignore-config',
  '--drawings','--disable-parts-engine'])
cpSync('dist/dist/index/drawings','dist/index/drawings',{recursive:true})
rmSync('dist/dist',{recursive:true,force:true})
rmSync('dist/index.circuit.json')

// The static viewer resolves imported model paths beside each generated view.
for(const directory of ['imports','mechanical/models']){
  for(const prefix of ['dist','dist/index']){
    mkdirSync(resolve(prefix,directory),{recursive:true})
    cpSync(directory,resolve(prefix,directory),{
      recursive:true,
      filter:path=>statSync(path).isDirectory()||/\.(obj|mtl|glb)$/.test(path),
    })
  }
}
console.log('Built current TypeScript circuit, native drawings and static preview in dist/.')
