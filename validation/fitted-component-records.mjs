// Compare fitted electronics independently of regenerated internal IDs and bare
// programming lands. Ignore the new redundant footprint_origin metadata;
// actual centers, pad coordinates, CAD poses and layers remain checked; only
// sub-nanometre numerical noise is rounded away. Display-only crystal labels
// are omitted while numerical frequency and capacitance remain compared.
// Includes original supplier identity, pads, placement and CAD.
export function fittedComponentRecords(circuit) {
  const portNames=new Map(circuit.filter(e=>e.type==='source_port').map(p=>[p.source_port_id,`${circuit.find(s=>s.type==='source_component'&&s.source_component_id===p.source_component_id)?.name}.${p.pin_number}`]))
  const omit=(record,keys)=>JSON.parse(JSON.stringify(Object.fromEntries(Object.entries(record).filter(([key])=>!keys.includes(key)))),(key,value)=>typeof value==='number'?Math.round(value*1e9)/1e9:typeof value==='string'&&portNames.has(value)?portNames.get(value):value)
  const sources=new Map(circuit.filter(e=>e.type==='source_component').map(e=>[e.source_component_id,e]))
  return circuit.filter(e=>e.type==='pcb_component'&&!e.do_not_place&&sources.has(e.source_component_id)).map(pcb=>({
    source:omit(sources.get(pcb.source_component_id),['source_component_id','source_group_id','display_frequency','display_load_capacitance']),
    pcb:omit(pcb,['pcb_component_id','source_component_id','footprint_origin']),
    cad:circuit.filter(e=>e.type==='cad_component'&&e.source_component_id===pcb.source_component_id)
      .map(e=>omit(e,['cad_component_id','source_component_id','pcb_component_id'])),
    pads:circuit.filter(e=>['pcb_smtpad','pcb_plated_hole'].includes(e.type)&&e.pcb_component_id===pcb.pcb_component_id)
      .map(e=>omit(e,['pcb_smtpad_id','pcb_plated_hole_id','pcb_component_id','pcb_port_id'])),
  })).sort((a,b)=>a.source.name.localeCompare(b.source.name))
}
