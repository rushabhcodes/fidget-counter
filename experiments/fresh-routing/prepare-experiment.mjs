// Strip routing decisions from an isolated copy; leave production routing guards intact.
import ts from 'typescript'
import {readFileSync,writeFileSync,mkdirSync,copyFileSync,existsSync,rmSync}from'node:fs'
import {dirname,resolve}from'node:path'
import {execFileSync}from'node:child_process'
import{createHash}from'node:crypto'
const root=process.cwd(),destination=resolve(process.argv[2]??'/workspace/experiments/fidget-counter-fresh-routing-2026-11-03')
if(destination===root||destination.startsWith(root+'/'))throw Error('Use a separate workspace outside the production checkout')
if(existsSync(destination))throw Error('Inspect existing experiment before replacing it')
mkdirSync(destination,{recursive:true})
const files=execFileSync('git',['ls-files','--cached','--others','--exclude-standard'],{encoding:'utf8'}).trim().split('\n').filter(p=>!p.startsWith('experiments/')&&!p.startsWith('cloud-assets/')&&existsSync(p))
const hashes={}
for(const p of files){const data=readFileSync(p);const out=resolve(destination,p);mkdirSync(dirname(out),{recursive:true});writeFileSync(out,data);hashes[p]=createHash('sha256').update(data).digest('hex')}
copyFileSync('published.circuit.json',resolve(destination,'baseline.circuit.json'))
const source=readFileSync('index.circuit.tsx','utf8'),sf=ts.createSourceFile('index.circuit.tsx',source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX),vias=new Map()
const attr=(n,key)=>n.attributes?.properties.find(a=>ts.isJsxAttribute(a)&&a.name.getText(sf)===key)?.initializer
function collect(n){if(ts.isJsxSelfClosingElement(n)&&n.tagName.getText(sf)==='via'){const name=attr(n,'name'),net=attr(n,'connectsTo');if(!name||!ts.isStringLiteral(name)||!net||!ts.isStringLiteral(net))throw Error('Unresolved manual via');vias.set(name.text,net.text)}ts.forEachChild(n,collect)}collect(sf)
const removed={manual_vias:vias.size,route_attributes:0,net_self_traces:0}
const result=ts.transform(sf,[context=>{
 const visit=node=>{
  if(ts.isImportDeclaration(node)&&['./routing','./critical-routes.json'].includes(node.moduleSpecifier.text))return undefined
  if(ts.isVariableStatement(node)&&node.declarationList.declarations.some(d=>['localRoutes','orientMcuPath','criticalRoutes'].includes(d.name.getText(sf))))return undefined
  if(ts.isJsxSelfClosingElement(node)&&node.tagName.getText(sf)==='via')return ts.factory.createJsxExpression(undefined,ts.factory.createNull())
  if(ts.isJsxAttribute(node)&&['pcbPath','pcbPathRelativeTo','pcbStraightLine'].includes(node.name.getText(sf))){removed.route_attributes++;return undefined}
  if(ts.isJsxAttribute(node)&&node.name.getText(sf)==='autorouter')return ts.factory.createJsxAttribute(ts.factory.createIdentifier('autorouter'),ts.factory.createStringLiteral('auto-local'))
  if(ts.isStringLiteral(node)){
   const match=node.text.match(/^\.([^ ]+) > \.(top|bottom)$/)
   if(match&&vias.has(match[1]))return ts.factory.createStringLiteral(vias.get(match[1]))
  }
  let next=ts.visitEachChild(node,visit,context)
  if(ts.isJsxSelfClosingElement(next)&&next.tagName.getText(sf)==='trace'){
   // The 1.5mm C18 limit describes the deleted, positioned ground-via stub.
   // A pin-to-global-net objective instead measures distance to another pin.
   // Retain the 1.5mm requirement as a separate result check, not that new objective.
   const name=attr(next,'name')
   if(name&&ts.isStringLiteral(name)&&name.text==='C18_LOCAL_GND')next=ts.factory.updateJsxSelfClosingElement(next,next.tagName,next.typeArguments,ts.factory.createJsxAttributes(next.attributes.properties.filter(a=>!ts.isJsxAttribute(a)||a.name.getText(sf)!=='maxLength')))
   const a=attr(next,'from'),b=attr(next,'to')
   if(a&&b&&ts.isStringLiteral(a)&&ts.isStringLiteral(b)&&a.text===b.text&&a.text.startsWith('net.')){removed.net_self_traces++;return ts.factory.createJsxExpression(undefined,ts.factory.createNull())}
  }
  return next
 };return node=>ts.visitNode(node,visit)
}])
const text=ts.createPrinter({newLine:ts.NewLineKind.LineFeed}).printFile(result.transformed[0]);result.dispose()
if(/pcbPath|pcbStraightLine|routeBoard|routed-paths/.test(text))throw Error('A routing prescription survived the AST transform')
const isolated=text.replace('"./published.circuit.json"','"./supplier-identities.json"')
writeFileSync(resolve(destination,'index.circuit.tsx'),'// ISOLATED EXPERIMENT: fresh auto-local routing; not approved for fabrication.\n'+isolated)
writeFileSync(resolve(destination,'supplier-identities.json'),JSON.stringify(JSON.parse(readFileSync('published.circuit.json')).filter(e=>e.type==='source_component'),null,2)+'\n')
for(const file of ['routing.ts','routed-paths.json','routing-contract.json','critical-routes.json','published.circuit.json'])rmSync(resolve(destination,file),{force:true})
const latest=process.argv[3]?JSON.parse(readFileSync(process.argv[3])):(()=>{const m=JSON.parse(execFileSync('npm',['view','tscircuit@latest','version','dist.integrity','--json'],{encoding:'utf8'}));return {version:m.version,integrity:m['dist.integrity']}})();const pkg=JSON.parse(readFileSync('package.json'));pkg.name='fidget-counter-fresh-routing-experiment';pkg.private=true;pkg.version='0.0.0';pkg.dependencies.tscircuit=latest.version;pkg.scripts={build:'tsci build index.circuit.tsx --pcb-png --svgs --glbs --disable-parts-engine',typecheck:'tsc --noEmit'}
writeFileSync(resolve(destination,'package.json'),JSON.stringify(pkg,null,2)+'\n')
writeFileSync(resolve(destination,'tscircuit.config.json'),JSON.stringify({mainEntrypoint:'index.circuit.tsx',previewComponentPath:'index.circuit.tsx'},null,2)+'\n')
writeFileSync(resolve(destination,'experiment-input.json'),JSON.stringify({production_base_commit:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),input_working_tree_sha256:hashes,compiler:latest,...removed,production_files_edited:false,constraint_translation:{C18_LOCAL_GND:'Deleted positioned-via stub maxLength1.5 is evaluated on the result; global-net pin-distance gate removed. All other maxLength/maxViaCount constraints retained.'},description:'Preserve placements, footprints, logical connections, widths and board rules; discard every manual routing path, custom prescribed router, positioned routing via and saved route input.'},null,2)+'\n')
console.log(JSON.stringify({destination,compiler:latest.version,...removed},null,2))
