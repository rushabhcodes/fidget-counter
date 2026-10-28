import {readFileSync,writeFileSync,mkdirSync} from "node:fs"
import {join} from "node:path"
import {convertCircuitJsonToAssemblySvg,convertCircuitJsonToPcbSvg,convertCircuitJsonToSchematicSvg,convertCircuitJsonToStackedSchematicSheetsSvg} from "circuit-to-svg"
import {Resvg} from "@resvg/resvg-js"
import {convertCircuitJsonToPickAndPlaceRows} from "circuit-json-to-pnp-csv"
import type {AnyCircuitElement} from "circuit-json"

const out=process.cwd()
const j=JSON.parse(readFileSync("dist/index/circuit.json","utf8")) as AnyCircuitElement[]
if(j.some(x=>x.type.includes("error"))) throw new Error("Refusing to export a board with errors")
mkdirSync(join(out,"previews"),{recursive:true})
mkdirSync(join(out,"fabrication"),{recursive:true})
const saveSvg=(stem:string,svg:string)=>{
 writeFileSync(join(out,"previews",stem+".svg"),svg)
 writeFileSync(join(out,"previews",stem+".png"),new Resvg(svg).render().asPng())
}
for(const layer of ["top","bottom"] as const){
 const svg=convertCircuitJsonToPcbSvg(j,{layer,width:1600,height:1600,backgroundColor:"#111111",showCourtyards:false})
 if(layer==="bottom"){
  saveSvg("pcb-bottom-top-coordinates",svg)
  // Mirror the complete copper view to show the actual underside orientation.
  saveSvg("pcb-bottom",svg.replace(/(<svg[^>]*>)([\s\S]*)(<\/svg>)/,"$1<g transform=\"translate(1600 0) scale(-1 1)\">$2</g>$3"))
 }else saveSvg("pcb-top",svg)
}
const sheets=j.filter(x=>x.type==="schematic_sheet")
for(const [i,sheet] of sheets.entries()){
 const s=sheet as any
 const stem="schematic-"+(i+1)+"-"+s.name
 const svg=convertCircuitJsonToSchematicSvg(j,{schematicSheetId:s.schematic_sheet_id,width:2000,height:1200})
 writeFileSync(join(out,"previews",stem+"-sheet.svg"),svg)
 // Content-only companion makes labels readable without zooming into an A4 frame.
 const content=j.filter(x=>!x.type.startsWith("schematic_") || (x.type!=="schematic_sheet" && (x as any).schematic_sheet_id===s.schematic_sheet_id))
 saveSvg(stem,convertCircuitJsonToSchematicSvg(content,{width:1800,height:1000}))
}
writeFileSync(join(out,"previews","schematic-all-sheets.svg"),convertCircuitJsonToStackedSchematicSheetsSvg(j,{width:2000,height:1200}))
const sc=new Map(j.filter(x=>x.type==="source_component").map((x:any)=>[x.source_component_id,x]))
const assemblyJson=j.filter((x:any)=>x.type!=="pcb_component" || (sc.has(x.source_component_id) && !sc.get(x.source_component_id)?.name?.startsWith("GPIO_") && !["TP_VDD","TP_GND","TP_SWDIO","TP_SWDCLK","TP_RESET"].includes(sc.get(x.source_component_id)?.name)))
const rows=convertCircuitJsonToPickAndPlaceRows(assemblyJson)
const fittedComponentIds=new Set(assemblyJson.filter((x:any)=>x.type==="pcb_component" && !x.do_not_place)
 .map((x:any)=>x.pcb_component_id))
const assemblyViewJson=j.filter((x:any)=>x.type==="pcb_component"?fittedComponentIds.has(x.pcb_component_id):
 !x.pcb_component_id || fittedComponentIds.has(x.pcb_component_id))
saveSvg("assembly-top",convertCircuitJsonToAssemblySvg(assemblyViewJson,{width:1600,height:1600}))
const csv=["Designator,Mid_X_mm,Mid_Y_mm,Layer,Authored_Rotation_deg",...rows.map(r=>[r.designator,r.mid_x,r.mid_y,r.layer,r.rotation].join(","))].join("\n")+"\n"
writeFileSync(join(out,"fabrication","Assembly_Position_Reference.csv"),csv)
console.log(JSON.stringify({sheets:sheets.length,assemblyRows:rows.length,previews:join(out,"previews")}))
