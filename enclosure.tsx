import {assembly} from "@tscircuit/core"
import {Fragment} from "react"
import obj0 from "./mechanical/Circuit_Models/Stationary_Base.obj"
import obj1 from "./mechanical/Circuit_Models/Bottom_Tray.obj"
import obj2 from "./mechanical/Circuit_Models/Cell.obj"
import obj3 from "./mechanical/Circuit_Models/Backing_Ring.obj"
import obj4 from "./mechanical/Circuit_Models/Attachment_Magnets.obj"
import obj5 from "./mechanical/Circuit_Models/Guide_Fasteners.obj"
import obj6 from "./mechanical/Circuit_Models/PCB_Fasteners.obj"
import obj7 from "./mechanical/Circuit_Models/Bearing_Carrier.obj"
import obj8 from "./mechanical/Circuit_Models/Inner_Race_Nut.obj"
import obj9 from "./mechanical/Circuit_Models/Bearing_6708.obj"
import obj10 from "./mechanical/Circuit_Models/Outer_Race_Retainer.obj"
import obj11 from "./mechanical/Circuit_Models/Cap_Retainer_Screws.obj"
import obj12 from "./mechanical/Circuit_Models/Magnet.obj"
import obj13 from "./mechanical/Circuit_Models/Encoder_Spacer.obj"
import obj14 from "./mechanical/Circuit_Models/Actuator_Ring.obj"
import obj15 from "./mechanical/Circuit_Models/Return_Springs.obj"
import obj16 from "./mechanical/Circuit_Models/Cap_circular.obj"
import obj17 from "./mechanical/Circuit_Models/Cap_ships_wheel.obj"
import obj18 from "./mechanical/Circuit_Models/Cap_rounded_triangle.obj"
import obj19 from "./mechanical/Circuit_Models/Cap_scalloped_coin.obj"
import obj20 from "./mechanical/Circuit_Models/Cap_petal_flower.obj"
import obj21 from "./mechanical/Circuit_Models/Cap_four_leaf_clover.obj"
import obj22 from "./mechanical/Circuit_Models/Cap_rounded_hexagon.obj"
import obj23 from "./mechanical/Circuit_Models/Cap_rounded_square.obj"
import obj24 from "./mechanical/Circuit_Models/Cap_wave_rim.obj"
import obj25 from "./mechanical/Circuit_Models/Cap_turbine_wheel.obj"
import obj26 from "./mechanical/Circuit_Models/Cap_thumb_scoop.obj"

export const CAP_STYLE_OPTIONS = ["circular", "ships_wheel", "rounded_triangle", "scalloped_coin", "petal_flower", "four_leaf_clover", "rounded_hexagon", "rounded_square", "wave_rim", "turbine_wheel", "thumb_scoop"] as const
export type CapStyle = typeof CAP_STYLE_OPTIONS[number]
const models = [
  {name:"Stationary_Base",obj:obj0,mtl:"./mechanical/Circuit_Models/Stationary_Base.mtl",style:null},
  {name:"Bottom_Tray",obj:obj1,mtl:"./mechanical/Circuit_Models/Bottom_Tray.mtl",style:null},
  {name:"Cell",obj:obj2,mtl:"./mechanical/Circuit_Models/Cell.mtl",style:null},
  {name:"Backing_Ring",obj:obj3,mtl:"./mechanical/Circuit_Models/Backing_Ring.mtl",style:null},
  {name:"Attachment_Magnets",obj:obj4,mtl:"./mechanical/Circuit_Models/Attachment_Magnets.mtl",style:null},
  {name:"Guide_Fasteners",obj:obj5,mtl:"./mechanical/Circuit_Models/Guide_Fasteners.mtl",style:null},
  {name:"PCB_Fasteners",obj:obj6,mtl:"./mechanical/Circuit_Models/PCB_Fasteners.mtl",style:null},
  {name:"Bearing_Carrier",obj:obj7,mtl:"./mechanical/Circuit_Models/Bearing_Carrier.mtl",style:null},
  {name:"Inner_Race_Nut",obj:obj8,mtl:"./mechanical/Circuit_Models/Inner_Race_Nut.mtl",style:null},
  {name:"Bearing_6708",obj:obj9,mtl:"./mechanical/Circuit_Models/Bearing_6708.mtl",style:null},
  {name:"Outer_Race_Retainer",obj:obj10,mtl:"./mechanical/Circuit_Models/Outer_Race_Retainer.mtl",style:null},
  {name:"Cap_Retainer_Screws",obj:obj11,mtl:"./mechanical/Circuit_Models/Cap_Retainer_Screws.mtl",style:null},
  {name:"Magnet",obj:obj12,mtl:"./mechanical/Circuit_Models/Magnet.mtl",style:null},
  {name:"Encoder_Spacer",obj:obj13,mtl:"./mechanical/Circuit_Models/Encoder_Spacer.mtl",style:null},
  {name:"Actuator_Ring",obj:obj14,mtl:"./mechanical/Circuit_Models/Actuator_Ring.mtl",style:null},
  {name:"Return_Springs",obj:obj15,mtl:"./mechanical/Circuit_Models/Return_Springs.mtl",style:null},
  {name:"Cap_circular",obj:obj16,mtl:"./mechanical/Circuit_Models/Cap_circular.mtl",style:"circular"},
  {name:"Cap_ships_wheel",obj:obj17,mtl:"./mechanical/Circuit_Models/Cap_ships_wheel.mtl",style:"ships_wheel"},
  {name:"Cap_rounded_triangle",obj:obj18,mtl:"./mechanical/Circuit_Models/Cap_rounded_triangle.mtl",style:"rounded_triangle"},
  {name:"Cap_scalloped_coin",obj:obj19,mtl:"./mechanical/Circuit_Models/Cap_scalloped_coin.mtl",style:"scalloped_coin"},
  {name:"Cap_petal_flower",obj:obj20,mtl:"./mechanical/Circuit_Models/Cap_petal_flower.mtl",style:"petal_flower"},
  {name:"Cap_four_leaf_clover",obj:obj21,mtl:"./mechanical/Circuit_Models/Cap_four_leaf_clover.mtl",style:"four_leaf_clover"},
  {name:"Cap_rounded_hexagon",obj:obj22,mtl:"./mechanical/Circuit_Models/Cap_rounded_hexagon.mtl",style:"rounded_hexagon"},
  {name:"Cap_rounded_square",obj:obj23,mtl:"./mechanical/Circuit_Models/Cap_rounded_square.mtl",style:"rounded_square"},
  {name:"Cap_wave_rim",obj:obj24,mtl:"./mechanical/Circuit_Models/Cap_wave_rim.mtl",style:"wave_rim"},
  {name:"Cap_turbine_wheel",obj:obj25,mtl:"./mechanical/Circuit_Models/Cap_turbine_wheel.mtl",style:"turbine_wheel"},
  {name:"Cap_thumb_scoop",obj:obj26,mtl:"./mechanical/Circuit_Models/Cap_thumb_scoop.mtl",style:"thumb_scoop"},
]

// V5 bearing carrier and spring return; CAD coordinates are mm from the phone plane.
export const PCB_MIDPLANE_Z_MM = 8.6
export const EnclosureAssembly = ({capStyle="circular",transparentShell=false}: {capStyle?:CapStyle;transparentShell?:boolean} = {}) => <Fragment>
  {models.filter(m => m.style === null || m.style === capStyle).map(m => <assembly.cadassembly
    key={m.name} name={`BEARING_V5_${m.name}`} displayName={m.name.replace(/_/g," ")}
    cadModel={{objUrl:m.obj,mtlUrl:m.mtl,modelUnitToMmScale:1,
      modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:0,z:-PCB_MIDPLANE_Z_MM},
      rotationOffset:{x:0,y:0,z:0},
      showAsTranslucentModel:transparentShell && (m.style !== null || ["Bottom_Tray","Stationary_Base"].includes(m.name)),
    }}/>)}
</Fragment>
