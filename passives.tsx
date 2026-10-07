import type {CapacitorProps,ResistorProps,InductorProps} from "@tscircuit/props"
import {libraryProps} from "./parts"
import {GRM155R71C104KA88D} from "./imports/GRM155R71C104KA88D/GRM155R71C104KA88D"
import {GRM188R60J475KE19D} from "./imports/GRM188R60J475KE19D/GRM188R60J475KE19D"
import {GRM188R60J226ME15D} from "./imports/GRM188R60J226ME15D/GRM188R60J226ME15D"
import {GRM1555C1H101JA01D} from "./imports/GRM1555C1H101JA01D/GRM1555C1H101JA01D"
import {CL10B105KA8NNWC} from "./imports/CL10B105KA8NNWC/CL10B105KA8NNWC"
import {GRM1555C1H120JA01D} from "./imports/GRM1555C1H120JA01D/GRM1555C1H120JA01D"
import {GRM155R71C103KA01D} from "./imports/GRM155R71C103KA01D/GRM155R71C103KA01D"
import {GJM1555C1HR80WB01D} from "./imports/GJM1555C1HR80WB01D/GJM1555C1HR80WB01D"
import {RC0402FR_0710KL} from "./imports/RC0402FR_0710KL/RC0402FR_0710KL"
import {RC0402FR_07100KL} from "./imports/RC0402FR_07100KL/RC0402FR_07100KL"
import {LQG15HS3N9B02D} from "./imports/LQG15HS3N9B02D/LQG15HS3N9B02D"
import {LQG15HS6N8G02D} from "./imports/LQG15HS6N8G02D/LQG15HS6N8G02D"

const caps={
 "100nF":GRM155R71C104KA88D, "4.7uF":GRM188R60J475KE19D,
 "22uF":GRM188R60J226ME15D, "100pF":GRM1555C1H101JA01D,
 "1uF":CL10B105KA8NNWC, "12pF":GRM1555C1H120JA01D,
 "10nF":GRM155R71C103KA01D, "0.8pF":GJM1555C1HR80WB01D,
}
export const Cap=(props:Omit<CapacitorProps,"footprint">)=>{
 const imported=caps[String(props.capacitance) as keyof typeof caps]
 if(!imported) {
  if(!props.doNotPlace) throw new Error(`No imported capacitor for ${props.capacitance}`)
  return <capacitor footprint="cap0402_nosilkscreen" schOrientation="vertical" {...props}/>
 }
 return <capacitor {...libraryProps(imported({name:props.name}))} schOrientation="vertical" {...props}/>
}
export const Res=(props:Omit<ResistorProps,"footprint">)=>{
 const imported=props.resistance==="10k"?RC0402FR_0710KL:props.resistance==="100k"?RC0402FR_07100KL:undefined
 if(!imported) throw new Error(`No imported resistor for ${props.resistance}`)
 return <resistor {...libraryProps(imported({name:props.name}))} {...props}/>
}
export const Ind=(props:Omit<InductorProps,"footprint">)=>{
 const imported=props.inductance==="3.9nH"?LQG15HS3N9B02D:props.inductance==="6.8nH"?LQG15HS6N8G02D:undefined
 if(!imported) throw new Error(`No imported inductor for ${props.inductance}`)
 return <inductor {...libraryProps(imported({name:props.name}))} {...props}/>
}
