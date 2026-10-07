import {Fragment} from "react"
import type { AntennaProps, BatteryProps, ChipProps, CrystalProps, PinAttributeMap } from "@tscircuit/props"

// Pin map and exact QFAA land pattern: seveibar/nrf52810 v0.1.3.
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
export const NRF52810 = (props:ChipProps)=><chip manufacturerPartNumber="nRF52810-QFAA-R"
 pinLabels={nrfPins} pinAttributes={nrfPinAttributes} supplierPartNumbers={{jlcpcb:["C141828"]}}
 footprint={<footprint>
  {Array.from({length:48},(_,i)=>{const s=Math.floor(i/12),n=i%12
   const xy=[[-3,2.2-n*.4],[-2.2+n*.4,-3],[3,-2.2+n*.4],[2.2-n*.4,3]][s]
   return <Fragment key={i}><smtpad portHints={[`pin${i+1}`]} shape="rect" pcbX={xy[0]} pcbY={xy[1]}
    width={s%2?.2:.95} height={s%2?.95:.2}/></Fragment>})}
  <smtpad portHints={["pin49","thermalpad"]} shape="rect" width={4.6} height={4.6} pcbX={0} pcbY={0}/>
  <courtyardrect width={7.2} height={7.2}/><silkscreencircle pcbX={-3.65} pcbY={3.65} radius={.15}/>
 </footprint>} {...props}/>

// TI SLYS053C YBG0006 package top view: A1/A2, B1/B2, C1/C2.
export const TMAG3001 = (props:ChipProps)=><chip manufacturerPartNumber="TMAG3001A2YBGR"
 pinLabels={{pin1:["A1","VCC"],pin2:["A2","ADDR"],pin3:["B1","INT"],pin4:["B2","GND"],pin5:["C1","SDA"],pin6:["C2","SCL"]}}
 pinAttributes={{
  pin1:{requiresPower:true,mustBeConnected:true,shouldHaveDecouplingCapacitor:true,recommendedDecouplingCapacitorCapacitance:"100nF"},
  pin2:{isInput:true,mustBeConnected:true},
  pin3:{isOutput:true,canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
  pin4:{requiresGround:true,mustBeConnected:true},
  pin5:{isBidirectional:true,activeCapability:"i2c_sda",canUseOpenDrain:true,isUsingOpenDrain:true,needsExternalPullup:true,mustBeConnected:true},
  pin6:{isInput:true,activeCapability:"i2c_scl",needsExternalPullup:true,mustBeConnected:true},
 }}
 footprint={<footprint>{Array.from({length:6},(_,i)=><Fragment key={i}><smtpad portHints={[`pin${i+1}`]}
  shape="circle" radius={.115} pcbX={i%2?.2:-.2} pcbY={.4-Math.floor(i/2)*.4}
  solderMaskMargin={.025} solderPasteMargin={.01}/></Fragment>)}
  <courtyardrect width={1.324} height={1.816}/><silkscreencircle pcbX={-.7} pcbY={.7} radius={.08}/>
 </footprint>} {...props}/>
// Builtin crystal pins 1/2/3/4 map to manufacturer pads 4/1/2/3 respectively.
// This retains the exact reference land coordinates and oscillator polarity.
export const HF_XTAL=(p:Omit<CrystalProps,"frequency"|"loadCapacitance">)=><crystal
 frequency="32MHz" loadCapacitance="8pF" pinVariant="four_pin" maxTraceLength={10}
 manufacturerPartNumber="X201632MKB4SI" supplierPartNumbers={{jlcpcb:["C718072"]}}
 pinAttributes={{pin1:{isPassive:true},pin2:{isPassive:true,requiresGround:true},pin3:{isPassive:true},pin4:{isPassive:true,requiresGround:true}}}
 footprint={<footprint>{[[.7,.5499],[.7,-.5499],[-.7,-.5499],[-.7,.5499]].map(([x,y],i)=><Fragment key={i}>
  <smtpad portHints={[`pin${i+1}`]} shape="rect" pcbX={x} pcbY={y} width={.9} height={.8}/>
 </Fragment>)}<courtyardrect width={2.55} height={2.4}/></footprint>} {...p}/>
export const LF_XTAL=(p:Omit<CrystalProps,"frequency"|"loadCapacitance">)=><crystal
 frequency="32.768kHz" loadCapacitance="9pF" maxTraceLength={10}
 manufacturerPartNumber="ABS07-32.768KHZ-9-T" supplierPartNumbers={{jlcpcb:["C179635"]}}
 pinAttributes={{pin1:{isPassive:true},pin2:{isPassive:true}}}
 footprint={<footprint>
  <smtpad portHints={["pin1"]} shape="rect" pcbX={-1.27495} pcbY={0} width={1.05} height={1.7}/>
  <smtpad portHints={["pin2"]} shape="rect" pcbX={1.27495} pcbY={0} width={1.05} height={1.7}/>
  <courtyardrect width={4} height={2.1}/>
 </footprint>} {...p}/>
export const RF_ANT=(p:AntennaProps)=><antenna manufacturerPartNumber="RFANT3216120A5T" supplierPartNumbers={{jlcpcb:["C127629"]}}
 pinAttributes={{pin1:{isPassive:true,mustBeConnected:true}}}
 footprint={<footprint>
  <smtpad portHints={["pin1"]} shape="rect" pcbX={-1.55005} pcbY={0} width={.8} height={1.66}/>
  <smtpad portHints={[]} shape="rect" pcbX={1.55005} pcbY={0} width={.8} height={1.66}/>
  <courtyardrect width={4.15} height={2.16}/>
 </footprint>} {...p}/>
// Official KiCad KMR2 lands; repeated pad numbers denote internally common contacts.
export const CapButton=(p:ChipProps)=><pushbutton manufacturerPartNumber="KMR223NG ULC LFG / Y78B22324FP"
 pinLabels={{pin1:["A"],pin2:["B"]}} footprint={<footprint>
  {[-2.05,2.05].flatMap(x=>[.8,-.8].map((y,i)=><Fragment key={`${x}/${y}`}><smtpad portHints={[`pin${i+1}`]}
   shape="rect" pcbX={x} pcbY={y} width={.9} height={1}/></Fragment>))}
  <courtyardrect width={5.5} height={3.3}/><silkscreenrect width={3.6} height={2.3}/>
 </footprint>} {...p}/>
export const BatteryContacts=(p:BatteryProps)=><battery standard="CR2032" voltage="3V"
 manufacturerPartNumber="CR2032 hatch spring-contact interface"
 pinAttributes={{pin1:{providesPower:true,providesVoltage:"3V",mustBeConnected:true},pin2:{providesGround:true,mustBeConnected:true}}}
 footprint={<footprint>
 <platedhole portHints={["pin1"]} shape="circle" pcbX={-2} pcbY={0} holeDiameter={.6} outerDiameter={1.8}/>
 <platedhole portHints={["pin2"]} shape="circle" pcbX={2} pcbY={0} holeDiameter={.6} outerDiameter={1.8}/>
 <courtyardcircle pcbX={-2} pcbY={0} radius={1.1}/><courtyardcircle pcbX={2} pcbY={0} radius={1.1}/>
 </footprint>} {...p}/>
