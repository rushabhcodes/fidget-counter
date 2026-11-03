// Explicit sourcing substitutions only. Every value, pad, layer, pose, pin
// attribute and CAD origin remains subject to the existing strict comparison.
import assert from 'node:assert/strict'
export const substitutions = [
 {refs:['C1','C2','C11','C12'],oldPart:'GRM1555C1H120JA01D',oldId:'C76948',part:'0402CG120J500NT',id:'C1547',model:'A_0402CG120J500NT'},
 {refs:['C10'],oldPart:'CL10B105KA8NNWC',oldId:'C730442',part:'CL10B105KA8NNNC',id:'C29936',model:'CL10B105KA8NNNC'},
 {refs:['L2'],oldPart:'LQG15HS6N8G02D',oldId:'C521064',part:'LQG15HS6N8J02D',id:'C77110',model:'LQG15HS6N8J02D'},
]
export function substituteRecords(prior){
 const expected=structuredClone(prior)
 for(const s of substitutions)for(const ref of s.refs){
  const r=expected.find(r=>r.source.name===ref);assert(r,ref)
  assert.equal(r.source.manufacturer_part_number,s.oldPart)
  assert.deepEqual(r.source.supplier_part_numbers.jlcpcb,[s.oldId])
  r.source.manufacturer_part_number=s.part;r.source.supplier_part_numbers.jlcpcb=[s.id]
  assert.equal(r.cad.length,1)
  for(const [key,ext] of [['model_obj_url','obj'],['model_step_url','step']]){
   assert.equal(r.cad[0][key],`./imports/${s.oldPart}/${s.oldPart}.${ext}`)
   r.cad[0][key]=`./imports/${s.model}/${s.model}.${ext}`
  }
 }
 return expected
}
