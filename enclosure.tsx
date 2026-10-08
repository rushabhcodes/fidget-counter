import {assembly} from "@tscircuit/core"
import {Fragment} from "react"
import manifest from "./mechanical/Circuit_Models/manifest.json"
import obj0 from "./mechanical/Circuit_Models/Rotating_Cap.obj"
import obj1 from "./mechanical/Circuit_Models/Encoder_Magnet.obj"
import obj2 from "./mechanical/Circuit_Models/Stationary_Housing.obj"
import obj3 from "./mechanical/Circuit_Models/Flexure_Retention_System.obj"
import obj4 from "./mechanical/Circuit_Models/CR2032.obj"
import obj5 from "./mechanical/Circuit_Models/Battery_Hatch.obj"
import obj6 from "./mechanical/Circuit_Models/MagSafe_Magnet_Array.obj"
import obj7 from "./mechanical/Circuit_Models/Magnetic_Shield.obj"
import obj8 from "./mechanical/Circuit_Models/Bottom_Cover.obj"
import obj9 from "./mechanical/Circuit_Models/Flexure_Fasteners.obj"
import obj10 from "./mechanical/Circuit_Models/Battery_Fasteners.obj"
import obj11 from "./mechanical/Circuit_Models/Phone_Pad.obj"
import obj12 from "./mechanical/Circuit_Models/Encoder_Shim.obj"
import obj13 from "./mechanical/Circuit_Models/PCB_Spacers.obj"

// CAD solids use the phone plane as Z=0; the circuit uses the PCB midplane.
// Keep imported electronics and BT1 on the board; never add their CAD dummies.
// Bottom attachment uses the ordered-size discs; magnetic performance is untested.
const models = [
  {name:"ENCLOSURE_Rotating_Cap",obj:obj0,mtl:"./mechanical/Circuit_Models/Rotating_Cap.mtl",translucent:true},
  {name:"ENCLOSURE_Encoder_Magnet",obj:obj1,mtl:"./mechanical/Circuit_Models/Encoder_Magnet.mtl",translucent:false},
  {name:"ENCLOSURE_Stationary_Housing",obj:obj2,mtl:"./mechanical/Circuit_Models/Stationary_Housing.mtl",translucent:true},
  {name:"ENCLOSURE_Flexure_Retention_System",obj:obj3,mtl:"./mechanical/Circuit_Models/Flexure_Retention_System.mtl",translucent:false},
  {name:"ENCLOSURE_CR2032",obj:obj4,mtl:"./mechanical/Circuit_Models/CR2032.mtl",translucent:false},
  {name:"ENCLOSURE_Battery_Hatch",obj:obj5,mtl:"./mechanical/Circuit_Models/Battery_Hatch.mtl",translucent:true},
  {name:"ENCLOSURE_MagSafe_Magnet_Array",obj:obj6,mtl:"./mechanical/Circuit_Models/MagSafe_Magnet_Array.mtl",translucent:false},
  {name:"ENCLOSURE_Magnetic_Shield",obj:obj7,mtl:"./mechanical/Circuit_Models/Magnetic_Shield.mtl",translucent:false},
  {name:"ENCLOSURE_Bottom_Cover",obj:obj8,mtl:"./mechanical/Circuit_Models/Bottom_Cover.mtl",translucent:true},
  {name:"ENCLOSURE_Flexure_Fasteners",obj:obj9,mtl:"./mechanical/Circuit_Models/Flexure_Fasteners.mtl",translucent:false},
  {name:"ENCLOSURE_Battery_Fasteners",obj:obj10,mtl:"./mechanical/Circuit_Models/Battery_Fasteners.mtl",translucent:false},
  {name:"ENCLOSURE_Phone_Pad",obj:obj11,mtl:"./mechanical/Circuit_Models/Phone_Pad.mtl",translucent:false},
  {name:"ENCLOSURE_Encoder_Shim",obj:obj12,mtl:"./mechanical/Circuit_Models/Encoder_Shim.mtl",translucent:false},
  {name:"ENCLOSURE_PCB_Spacers",obj:obj13,mtl:"./mechanical/Circuit_Models/PCB_Spacers.mtl",translucent:false},
]

export const EnclosureAssembly = () => <Fragment>
  {models.map(({name,obj,mtl,translucent}) => <assembly.cadassembly
    key={name} name={name} displayName={name.replace("ENCLOSURE_", "").replace(/_/g, " ")}
    cadModel={{
      objUrl:obj,mtlUrl:mtl,
      modelOriginPosition:{x:0,y:0,z:0},modelUnitToMmScale:1,
      positionOffset:{x:0,y:0,z:-manifest.pcbMidplaneZMm},
      rotationOffset:{x:0,y:0,z:0},showAsTranslucentModel:translucent,
    }}/>)}
</Fragment>
