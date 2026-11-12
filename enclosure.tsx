import {assembly} from "@tscircuit/core"
import {Fragment} from "react"
import obj0 from "./mechanical/Circuit_Models/Base_V3_Discs.glb"
import obj1 from "./mechanical/Circuit_Models/Cell.glb"
import obj2 from "./mechanical/Circuit_Models/Attachment_Discs_V3.glb"
import obj3 from "./mechanical/Circuit_Models/PCB_Fasteners.glb"
import obj4 from "./mechanical/Circuit_Models/Bearing_6808.glb"
import obj5 from "./mechanical/Circuit_Models/Magnet.glb"
import obj6 from "./mechanical/Circuit_Models/Cap_circular.glb"
import obj7 from "./mechanical/Circuit_Models/Cap_ships_wheel.glb"
import obj8 from "./mechanical/Circuit_Models/Cap_rounded_triangle.glb"
import obj9 from "./mechanical/Circuit_Models/Cap_scalloped_coin.glb"
import obj10 from "./mechanical/Circuit_Models/Cap_petal_flower.glb"
import obj11 from "./mechanical/Circuit_Models/Cap_four_leaf_clover.glb"
import obj12 from "./mechanical/Circuit_Models/Cap_rounded_hexagon.glb"
import obj13 from "./mechanical/Circuit_Models/Cap_rounded_square.glb"
import obj14 from "./mechanical/Circuit_Models/Cap_wave_rim.glb"
import obj15 from "./mechanical/Circuit_Models/Cap_turbine_wheel.glb"
import obj16 from "./mechanical/Circuit_Models/Cap_thumb_scoop.glb"

export const CAP_STYLE_OPTIONS = ["circular", "ships_wheel", "rounded_triangle", "scalloped_coin", "petal_flower", "four_leaf_clover", "rounded_hexagon", "rounded_square", "wave_rim", "turbine_wheel", "thumb_scoop"] as const
export type CapStyle = typeof CAP_STYLE_OPTIONS[number]
const models = [
  {name:"Base_V3_Discs",obj:obj0,mtl:"./mechanical/Circuit_Models/Base_V3_Discs.mtl",style:null},
  {name:"Cell",obj:obj1,mtl:"./mechanical/Circuit_Models/Cell.mtl",style:null},
  {name:"Attachment_Discs_V3",obj:obj2,mtl:"./mechanical/Circuit_Models/Attachment_Discs_V3.mtl",style:null},
  {name:"PCB_Fasteners",obj:obj3,mtl:"./mechanical/Circuit_Models/PCB_Fasteners.mtl",style:null},
  {name:"Bearing_6808",obj:obj4,mtl:"./mechanical/Circuit_Models/Bearing_6808.mtl",style:null},
  {name:"Magnet",obj:obj5,mtl:"./mechanical/Circuit_Models/Magnet.mtl",style:null},
  {name:"Cap_circular",obj:obj6,mtl:"./mechanical/Circuit_Models/Cap_circular.mtl",style:"circular"},
  {name:"Cap_ships_wheel",obj:obj7,mtl:"./mechanical/Circuit_Models/Cap_ships_wheel.mtl",style:"ships_wheel"},
  {name:"Cap_rounded_triangle",obj:obj8,mtl:"./mechanical/Circuit_Models/Cap_rounded_triangle.mtl",style:"rounded_triangle"},
  {name:"Cap_scalloped_coin",obj:obj9,mtl:"./mechanical/Circuit_Models/Cap_scalloped_coin.mtl",style:"scalloped_coin"},
  {name:"Cap_petal_flower",obj:obj10,mtl:"./mechanical/Circuit_Models/Cap_petal_flower.mtl",style:"petal_flower"},
  {name:"Cap_four_leaf_clover",obj:obj11,mtl:"./mechanical/Circuit_Models/Cap_four_leaf_clover.mtl",style:"four_leaf_clover"},
  {name:"Cap_rounded_hexagon",obj:obj12,mtl:"./mechanical/Circuit_Models/Cap_rounded_hexagon.mtl",style:"rounded_hexagon"},
  {name:"Cap_rounded_square",obj:obj13,mtl:"./mechanical/Circuit_Models/Cap_rounded_square.mtl",style:"rounded_square"},
  {name:"Cap_wave_rim",obj:obj14,mtl:"./mechanical/Circuit_Models/Cap_wave_rim.mtl",style:"wave_rim"},
  {name:"Cap_turbine_wheel",obj:obj15,mtl:"./mechanical/Circuit_Models/Cap_turbine_wheel.mtl",style:"turbine_wheel"},
  {name:"Cap_thumb_scoop",obj:obj16,mtl:"./mechanical/Circuit_Models/Cap_thumb_scoop.mtl",style:"thumb_scoop"},
]

// V3: twenty diameter-6 by 3 mm discs insert from underneath the one-piece base.
// CAD coordinates are mm from the phone plane; all upper interfaces are retained.
export const PCB_MIDPLANE_Z_MM = 11.1
export const EnclosureAssembly = ({capStyle="circular",transparentShell=false}: {capStyle?:CapStyle;transparentShell?:boolean} = {}) => <Fragment>
  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly
    key={m.name} name={`BEARING_V5_${m.name}`} displayName={m.name.replace(/_/g," ")}
    cadModel={{glbUrl:m.obj,modelUnitToMmScale:1,
      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-PCB_MIDPLANE_Z_MM},
      rotationOffset:{x:0,y:0,z:0},
      showAsTranslucentModel:transparentShell && (m.style !== null || m.name === "Base_V3_Discs"),
    }}/>)}
</Fragment>
