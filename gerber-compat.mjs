// Preserve imported copper geometry. The pinned core omits paste for pill
// pads; add the same 70% linear paste reduction used for its rectangular pads.
// Bare interfaces and DNP sites receive no paste. Stencil review remains open.
export function gerberCompatibleCircuit(circuit) {
  const components = new Map(circuit.filter(e => e.type === "pcb_component").map(e => [e.pcb_component_id, e]))
  const pads = new Map(circuit.filter(e => e.type === "pcb_smtpad").map(e => [e.pcb_smtpad_id, e]))
  const sources = new Map(circuit.filter(e => e.type === "source_component").map(e => [e.source_component_id, e]))
  const isFitted = pad => pad && !components.get(pad.pcb_component_id)?.do_not_place
  const prepared = circuit.filter(element => element.type !== "pcb_solder_paste" || isFitted(pads.get(element.pcb_smtpad_id)))
  const pasted = new Set(prepared.filter(e => e.type === "pcb_solder_paste").map(e => e.pcb_smtpad_id))
  for (const pad of pads.values()) {
    if (!isFitted(pad) || pasted.has(pad.pcb_smtpad_id)) continue
    if (!["pill", "rotated_pill"].includes(pad.shape)) throw new Error(`Missing paste for ${pad.pcb_smtpad_id}`)
    prepared.push({type:"pcb_solder_paste", pcb_solder_paste_id:`paste_for_${pad.pcb_smtpad_id}`,
      pcb_smtpad_id:pad.pcb_smtpad_id, pcb_component_id:pad.pcb_component_id,
      subcircuit_id:pad.subcircuit_id, layer:pad.layer, shape:pad.shape,
      x:pad.x, y:pad.y, width:pad.width * .7, height:pad.height * .7,
      radius:pad.radius * .7, ccw_rotation:pad.ccw_rotation ?? 0})
  }
  return prepared.map(element => {
    // The source board requests both-side tenting, but the pinned core does
    // not carry that default into every prescribed/explicit via record.
    if (element.type === "pcb_via") return {...element, is_tented:true, tented_on_top:true, tented_on_bottom:true}
    if (element.type === "pcb_plated_hole" && sources.get(components.get(element.pcb_component_id)?.source_component_id)?.name.startsWith("GPIO_")) {
      return {...element, is_covered_with_solder_mask:true}
    }
    if (!["pcb_smtpad", "pcb_solder_paste"].includes(element.type) || element.shape !== "rotated_pill") return element
    const rotation = ((element.ccw_rotation % 360) + 360) % 360
    const quarter = Math.round(rotation / 90)
    if (Math.abs(rotation - quarter * 90) > 1e-6) throw new Error("Gerber export requires an orthogonal pill rotation")
    const {ccw_rotation, ...rest} = element
    return {...rest, shape: "pill", width: quarter % 2 ? element.height : element.width,
      height: quarter % 2 ? element.width : element.height}
  })
}
