import{test,expect}from'bun:test'
import{readFileSync}from'node:fs'
import{verifyFreshRouting}from'./check-fresh-routing.mjs'
const current=()=>JSON.parse(readFileSync('published.circuit.json'))
test('fresh routing rejects an unapproved pour void, retaining interior-ring semantics',()=>{
 const c=current(),p=c.find(e=>e.type==='pcb_copper_pour'&&e.layer==='top')
 p.brep_shape.inner_rings.push({vertices:[{x:-.1,y:-17.1},{x:.1,y:-17.1},{x:.1,y:-16.9},{x:-.1,y:-16.9}]})
 expect(()=>verifyFreshRouting(c)).toThrow()
})
test('fresh routing rejects incorrect supplier placement orientation metadata',()=>{
 const c=current();const map=c.find(e=>e.type==='pcb_component'&&e.supplier_pin1_location_map).supplier_pin1_location_map;map.jlcpcb=map.jlcpcb==='topside_left'?'topside_right':'topside_left'
 expect(()=>verifyFreshRouting(c)).toThrow()
})
test('fresh routing rejects relaxation of the retained crystal constraint',()=>{
 const c=current();c.find(e=>e.type==='source_trace'&&e.max_length===10).max_length=11
 expect(()=>verifyFreshRouting(c)).toThrow()
})
