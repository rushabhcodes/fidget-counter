import {Children,cloneElement,isValidElement} from "react"
import type {ReactElement} from "react"
import {NRF52810_QFAA_R} from "./imports/NRF52810_QFAA_R/NRF52810_QFAA_R"
import {TMAG3001A2YBGR} from "./imports/TMAG3001A2YBGR/TMAG3001A2YBGR"
import {X201632MKB4SI} from "./imports/X201632MKB4SI/X201632MKB4SI"
import {ABS07_32_768KHZ_9_T} from "./imports/ABS07_32_768KHZ_9_T/ABS07_32_768KHZ_9_T"
import {KMR232NGULCLFS} from "./imports/KMR232NGULCLFS/KMR232NGULCLFS"
import {RFANT3216120A5T} from "./imports/RFANT3216120A5T/RFANT3216120A5T"
import {BS_08_B2AA020_R} from "./imports/BS_08_B2AA020_R/BS_08_B2AA020_R"
import type { BatteryProps, ChipProps, CrystalProps, PinAttributeMap } from "@tscircuit/props"

// Nordic QFAA signal labels; copper and models come from the JLCPCB import.
export const nrfPins = Object.fromEntries([
 "DEC1",["P0_00","XL1"],["P0_01","XL2"],"P0_02","P0_03","P0_04","P0_05",
 "P0_06","P0_07","P0_08","P0_09","P0_10","VDD1","P0_11","P0_12","P0_13",
 "P0_14","P0_15","P0_16","P0_17","P0_18","P0_19","P0_20",["P0_21","nRESET"],
 "SWDCLK","SWDIO","P0_22","P0_23","P0_24","ANT","VSS2","DEC2","DEC3",
 "XC1","XC2","VDD3","P0_25","P0_26","P0_27","P0_28","P0_29","P0_30",
 "P0_31","NC","VSS1","DEC4","DCC","VDD2","EP",
].map((p,i)=>[`pin${i+1}`,Array.isArray(p)?p:[p]]))
// Nordic QFAA pin functions, configured for LDO, two crystals and open-drain I2C.
const nrfPinAttributes: Record<string,PinAttributeMap> = Object.fromEntries(
 Object.entries(nrfPins).map(([pin,labels])=>[pin,
  labels.some(label=>label.startsWith("P0_"))?{isBidirectional:true,isGpio:true}:{}]))
Object.assign(nrfPinAttributes, {
 pin1:{isOutput:true,providesPower:true,mustBeConnected:true},
 pin2:{isInput:true,mustBeConnected:true}, pin3:{isInput:true,mustBeConnected:true},
 pin13:{requiresPower:true,mustBeConnected:true,shouldHaveDecouplingCapacitor:true,recommendedDecouplingCapacitorCapacitance:"100nF"},
 pin24:{isInput:true,needsExternalPullup:true,mustBeConnected:true},
 pin25:{isInput:true,mustBeConnected:true}, pin26:{isBidirectional:true,mustBeConnected:true},
 pin30:{isBidirectional:true,mustBeConnected:true},
 pin31:{requiresGround:true,mustBeConnected:true},
 pin32:{isOutput:true,providesPower:true,mustBeConnected:true},
 pin33:{isOutput:true,providesPower:true,mustBeConnected:true},
 pin34:{isInput:true,mustBeConnected:true}, pin35:{isInput:true,mustBeConnected:true},
 pin36:{requiresPower:true,mustBeConnected:true,shouldHaveDecouplingCapacitor:true,recommendedDecouplingCapacitorCapacitance:"100nF"},
 pin38:{isBidirectional:true,isGpio:true,activeCapability:"i2c_scl",canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
 pin39:{isBidirectional:true,isGpio:true,activeCapability:"i2c_sda",canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
 pin40:{isInput:true,isGpio:true,needsExternalPullup:true,mustBeConnected:true},
 pin41:{isInput:true,isGpio:true,needsExternalPullup:true,mustBeConnected:true},
 pin44:{doNotConnect:true,isPassive:true},
 pin45:{requiresGround:true,mustBeConnected:true},
 pin46:{isOutput:true,providesPower:true,mustBeConnected:true},
 pin47:{doNotConnect:true,isOutput:true},
 pin48:{requiresPower:true,mustBeConnected:true,shouldHaveDecouplingCapacitor:true,recommendedDecouplingCapacitorCapacitance:"100nF"},
 pin49:{requiresGround:true,mustBeConnected:true},
})
// Preserve imported copper/pad numbers/courtyards and models. The dense board
// uses its own validated legend rather than supplier outline graphics.
export const libraryProps = (element: ReactElement): ChipProps => {
 const props=element.props as ChipProps
 const footprint=props.footprint
 if(!isValidElement<{children?:React.ReactNode}>(footprint)) return props
 return {...props, footprint:cloneElement(footprint,{children:Children.toArray(footprint.props.children)
  .filter(child=>!isValidElement(child) || typeof child.type!=="string" || !child.type.startsWith("silkscreen"))})}
}
export const NRF52810 = (props:ChipProps)=><chip
 {...libraryProps(NRF52810_QFAA_R({name:props.name}))}
 pcbRotation={270} pinAttributes={nrfPinAttributes} {...props}/>

// EasyEDA numbers the WCSP down columns; retain its A1/B1/C1/A2/B2/C2 mapping.
export const TMAG3001 = (props:ChipProps)=><chip
 {...libraryProps(TMAG3001A2YBGR({name:props.name}))}
 pinLabels={{pin1:["VCC","A1"],pin2:["INT","N_INT","B1"],pin3:["SDA","C1"],pin4:["ADDR","A2"],pin5:["GND","B2"],pin6:["SCL","C2"]}}
 pinAttributes={{
  pin1:{requiresPower:true,mustBeConnected:true,shouldHaveDecouplingCapacitor:true,recommendedDecouplingCapacitorCapacitance:"100nF"},
  pin2:{isOutput:true,canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
  pin3:{isBidirectional:true,activeCapability:"i2c_sda",canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
  pin4:{isInput:true,mustBeConnected:true},
  pin5:{requiresGround:true,mustBeConnected:true},
  pin6:{isInput:true,activeCapability:"i2c_scl",needsExternalPullup:true,mustBeConnected:true},
 }} {...props}/>
export const HF_XTAL=(p:Omit<CrystalProps,"frequency"|"loadCapacitance">)=><crystal
 {...libraryProps(X201632MKB4SI({name:p.name,loadCapacitance:"8pF"}))} frequency="32MHz" pinVariant="four_pin"
 loadCapacitance="8pF" maxTraceLength={10}
 pinAttributes={{pin1:{isPassive:true},pin2:{isPassive:true,requiresGround:true},pin3:{isPassive:true},pin4:{isPassive:true,requiresGround:true}}} {...p}/>
export const LF_XTAL=(p:Omit<CrystalProps,"frequency"|"loadCapacitance">)=><crystal
 {...libraryProps(ABS07_32_768KHZ_9_T({name:p.name,loadCapacitance:"9pF"}))} frequency="32.768kHz"
 loadCapacitance="9pF" maxTraceLength={10}
 pinAttributes={{pin1:{isPassive:true},pin2:{isPassive:true}}} {...p}/>
export const RF_ANT=(p:ChipProps)=><chip
 {...libraryProps(RFANT3216120A5T({name:p.name}))}
 pinLabels={{pin1:["feed"],pin2:["NC"]}} noConnect={["pin2"]}
 pinAttributes={{pin1:{isPassive:true,mustBeConnected:true},pin2:{isPassive:true}}} {...p}/>
// Shared KMR2 package geometry from C221681. Keep the existing 2 N ULC part;
// C221681 is the 3 N variant, so it must not be assigned to this BOM row.
export const CapButton=(p:ChipProps)=><pushbutton
 {...libraryProps(KMR232NGULCLFS({name:p.name}))}
 manufacturerPartNumber="KMR223NG ULC LFG / Y78B22324FP" supplierPartNumbers={{}}
 pinLabels={{pin1:["A1"],pin2:["B2"],pin3:["B"],pin4:["A"]}}
 internallyConnectedPins={[["pin1","pin4"],["pin2","pin3"]]}
 {...p}/>
// Complete two-terminal holder: unmodified JLCPCB copper and model, fitted below
// the PCB. Pin 1 is the positive contact, matching the imported polarity marker.
export const BatteryHolder=(p:BatteryProps)=><battery
 {...{...libraryProps(BS_08_B2AA020_R({name:p.name})),symbol:undefined}} standard="CR2032" voltage="3V"
 pinAttributes={{pin1:{providesPower:true,providesVoltage:"3V",mustBeConnected:true},pin2:{providesGround:true,mustBeConnected:true}}}
 {...p}/>
