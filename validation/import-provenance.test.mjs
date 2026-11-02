import {test,expect} from 'bun:test'
import {readFileSync} from 'node:fs'
import {verifyImportedFile} from './import-provenance.mjs'
const provenance=JSON.parse(readFileSync('validation/jlc-imports.json'))
const files=provenance.parts.flatMap(p=>p.files)
const antenna=files.find(f=>f.path==='imports/RFANT3216120A5T/RFANT3216120A5T.tsx')
test('accepts the two exact prior anchor compensations and original supplier files',()=>{
  for(const adaptation of provenance.localCadAdaptations){
    const file=files.find(f=>f.path===adaptation.path)
    expect(verifyImportedFile(file,readFileSync(file.path))).toBe('compiler-anchor-compensation')
  }
  const original=files.find(f=>f.path.endsWith('.step'))
  expect(verifyImportedFile(original,readFileSync(original.path))).toBe('original')
})
test('rejects a changed geometric compensation',()=>{
  const bytes=readFileSync(antenna.path,'utf8').replace('x: 0.026035,','x: 0.026036,')
  expect(()=>verifyImportedFile(antenna,Buffer.from(bytes))).toThrow('Imported file changed')
})
test('rejects additional footprint changes inside an adapted wrapper',()=>{
  const bytes=readFileSync(antenna.path,'utf8').replace('pcbX="1.57607mm"','pcbX="1.67607mm"')
  expect(()=>verifyImportedFile(antenna,Buffer.from(bytes))).toThrow('Imported file changed')
})
test('rejects modified supplier model bytes and unrelated wrappers',()=>{
  for(const file of [files.find(f=>f.path.endsWith('.obj')),files.find(f=>f.path.endsWith('.tsx')&&f.path!==antenna.path)]){
    const bytes=Buffer.concat([readFileSync(file.path),Buffer.from('\nchanged geometry\n')])
    expect(()=>verifyImportedFile(file,bytes)).toThrow('Imported file changed')
  }
})
