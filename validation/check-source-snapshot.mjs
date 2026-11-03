// The compiler's filesystem MD5 describes its build context. Every physical,
// electrical, schematic and verified orientation record must match exactly.
import{readFileSync,writeFileSync}from'node:fs'
import{createHash}from'node:crypto'
import assert from'node:assert/strict'
const generated=readFileSync('dist/index/circuit.json'),saved=readFileSync('published.circuit.json')
const content=bytes=>JSON.parse(bytes).filter(e=>e.type!=='source_project_metadata')
assert.deepEqual(content(generated),content(saved),'Source and saved circuit differ beyond filesystem metadata')
const sha=b=>createHash('sha256').update(b).digest('hex')
const report={passed:true,method:'Exact ordered circuit records; exclude only descriptive source_project_metadata filesystem hash',records:content(saved).length,source_circuit_sha256:sha(generated),saved_circuit_sha256:sha(saved),source_sha256:Object.fromEntries(['validation/check-source-snapshot.mjs','index.circuit.tsx','parts.tsx','passives.tsx','enclosure.tsx','critical-routes.json','routing.ts','routing-contract.json','routed-paths.json','published.circuit.json'].map(p=>[p,sha(readFileSync(p))]))}
writeFileSync('validation/source-snapshot-audit.json',JSON.stringify(report,null,2)+'\n')
console.log('PASS: source and saved circuit match exactly outside descriptive filesystem metadata')
