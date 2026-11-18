import {assembly} from "@tscircuit/core"
import {Fragment} from "react"
import obj0 from "./mechanical/models/Base_V3_Discs.glb"
import obj1 from "./mechanical/models/Cell.glb"
import obj2 from "./mechanical/models/Attachment_Discs_V3.glb"
import obj3 from "./mechanical/models/PCB_Fasteners.glb"
import obj4 from "./mechanical/models/Bearing_6808.glb"
import obj5 from "./mechanical/models/Magnet.glb"
import obj6 from "./mechanical/models/Cap_circular.glb"
import obj7 from "./mechanical/models/Cap_ships_wheel.glb"
import obj8 from "./mechanical/models/Cap_rounded_triangle.glb"
import obj9 from "./mechanical/models/Cap_scalloped_coin.glb"
import obj10 from "./mechanical/models/Cap_petal_flower.glb"
import obj11 from "./mechanical/models/Cap_four_leaf_clover.glb"
import obj12 from "./mechanical/models/Cap_rounded_hexagon.glb"
import obj13 from "./mechanical/models/Cap_rounded_square.glb"
import obj14 from "./mechanical/models/Cap_wave_rim.glb"
import obj15 from "./mechanical/models/Cap_turbine_wheel.glb"
import obj16 from "./mechanical/models/Cap_thumb_scoop.glb"

export const CAP_STYLE_OPTIONS = ["circular", "ships_wheel", "rounded_triangle", "scalloped_coin", "petal_flower", "four_leaf_clover", "rounded_hexagon", "rounded_square", "wave_rim", "turbine_wheel", "thumb_scoop"] as const
export type CapStyle = typeof CAP_STYLE_OPTIONS[number]
const models = [
  {name:"Base_V3_Discs",obj:obj0,style:null},
  {name:"Cell",obj:obj1,style:null},
  {name:"Attachment_Discs_V3",obj:obj2,style:null},
  {name:"PCB_Fasteners",obj:obj3,style:null},
  {name:"Bearing_6808",obj:obj4,style:null},
  {name:"Magnet",obj:obj5,style:null},
  {name:"Cap_circular",obj:obj6,style:"circular"},
  {name:"Cap_ships_wheel",obj:obj7,style:"ships_wheel"},
  {name:"Cap_rounded_triangle",obj:obj8,style:"rounded_triangle"},
  {name:"Cap_scalloped_coin",obj:obj9,style:"scalloped_coin"},
  {name:"Cap_petal_flower",obj:obj10,style:"petal_flower"},
  {name:"Cap_four_leaf_clover",obj:obj11,style:"four_leaf_clover"},
  {name:"Cap_rounded_hexagon",obj:obj12,style:"rounded_hexagon"},
  {name:"Cap_rounded_square",obj:obj13,style:"rounded_square"},
  {name:"Cap_wave_rim",obj:obj14,style:"wave_rim"},
  {name:"Cap_turbine_wheel",obj:obj15,style:"turbine_wheel"},
  {name:"Cap_thumb_scoop",obj:obj16,style:"thumb_scoop"},
]

// V3: twenty diameter-6 by 3 mm discs insert from underneath the one-piece base.
// The encoder is an identical axial disc held on edge, with its axis parallel to PCB.
// CAD coordinates are mm from the phone plane; all upper interfaces are retained.
export const PCB_MIDPLANE_Z_MM = 11.1
export const EnclosureAssembly = ({capStyle="circular",transparentShell=false}: {capStyle?:CapStyle;transparentShell?:boolean} = {}) => <Fragment>
  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly
    key={m.name} name={`BEARING_V5_${m.name}`} displayName={m.name === "Magnet" ? "Encoder disc on edge" : m.name.replace(/_/g," ")}
    cadModel={{glbUrl:m.obj,modelUnitToMmScale:1,
      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-PCB_MIDPLANE_Z_MM},
      rotationOffset:{x:0,y:0,z:0},
      showAsTranslucentModel:transparentShell && (m.style !== null || m.name === "Base_V3_Discs"),
    }}/>)}
</Fragment>
