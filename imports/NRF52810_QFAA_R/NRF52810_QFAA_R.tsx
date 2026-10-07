import objPath from "./NRF52810_QFAA_R.obj"
import stepPath from "./NRF52810_QFAA_R.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["DEC1"],
  pin2: ["P0_00","XL1"],
  pin3: ["P0_01","XL2"],
  pin4: ["P0_02","AIN0"],
  pin5: ["P0_03","AIN1"],
  pin6: ["P0_04","AIN2"],
  pin7: ["P0_05","AIN3"],
  pin8: ["P0_06"],
  pin9: ["P0_07"],
  pin10: ["P0_08"],
  pin11: ["P0_09"],
  pin12: ["P0_10"],
  pin13: ["VDD1"],
  pin14: ["P0_11"],
  pin15: ["P0_12"],
  pin16: ["P0_13"],
  pin17: ["P0_14"],
  pin18: ["P0_15"],
  pin19: ["P0_16"],
  pin20: ["P0_17"],
  pin21: ["P0_18"],
  pin22: ["P0_19"],
  pin23: ["P0_20"],
  pin24: ["P0_21","nRESET"],
  pin25: ["SWDCLK"],
  pin26: ["SWDIO"],
  pin27: ["P0_22"],
  pin28: ["P0_23"],
  pin29: ["P0_24"],
  pin30: ["ANT"],
  pin31: ["VSS2"],
  pin32: ["DEC2"],
  pin33: ["DEC3"],
  pin34: ["XC1"],
  pin35: ["XC2"],
  pin36: ["VDD3"],
  pin37: ["P0_25"],
  pin38: ["P0_26"],
  pin39: ["P0_27"],
  pin40: ["P0_28","AIN4"],
  pin41: ["P0_29","AIN5"],
  pin42: ["P0_30","AIN6"],
  pin43: ["P0_31","AIN7"],
  pin44: ["NC"],
  pin45: ["VSS1"],
  pin46: ["DEC4"],
  pin47: ["DCC"],
  pin48: ["VDD2"],
  pin49: ["EP"]
} as const

const pinAttributes = {
  pin13: {requiresPower: true},
  pin31: {requiresGround: true},
  pin36: {requiresPower: true},
  pin44: {doNotConnect: true},
  pin45: {requiresGround: true},
  pin48: {requiresPower: true}
} as const

export const NRF52810_QFAA_R = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      pinAttributes={pinAttributes}
      supplierPartNumbers={{
  "jlcpcb": [
    "C141828"
  ]
}}
      manufacturerPartNumber="NRF52810-QFAA-R"
      footprint={<footprint>
        <smtpad portHints={["pin49"]} pcbX="-0.0009398mm" pcbY="0.00127mm" width="4.5999908mm" height="4.5999908mm" shape="rect" />
<smtpad portHints={["pin13"]} pcbX="2.999994mm" pcbY="-2.200148mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin14"]} pcbX="2.999994mm" pcbY="-1.800098mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin15"]} pcbX="2.999994mm" pcbY="-1.400048mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin16"]} pcbX="2.999994mm" pcbY="-0.999998mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin17"]} pcbX="2.999994mm" pcbY="-0.599948mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin18"]} pcbX="2.999994mm" pcbY="-0.200152mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin19"]} pcbX="2.999994mm" pcbY="0.199898mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin20"]} pcbX="2.999994mm" pcbY="0.599948mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin21"]} pcbX="2.999994mm" pcbY="0.999998mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin22"]} pcbX="2.999994mm" pcbY="1.400048mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin23"]} pcbX="2.999994mm" pcbY="1.799844mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin24"]} pcbX="2.999994mm" pcbY="2.199894mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin37"]} pcbX="-2.999994mm" pcbY="2.199894mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin38"]} pcbX="-2.999994mm" pcbY="1.799844mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin39"]} pcbX="-2.999994mm" pcbY="1.400048mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin40"]} pcbX="-2.999994mm" pcbY="0.999998mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin41"]} pcbX="-2.999994mm" pcbY="0.599948mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin42"]} pcbX="-2.999994mm" pcbY="0.199898mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin43"]} pcbX="-2.999994mm" pcbY="-0.200152mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin44"]} pcbX="-2.999994mm" pcbY="-0.599948mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin45"]} pcbX="-2.999994mm" pcbY="-0.999998mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin46"]} pcbX="-2.999994mm" pcbY="-1.400048mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin47"]} pcbX="-2.999994mm" pcbY="-1.800098mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin48"]} pcbX="-2.999994mm" pcbY="-2.200148mm" width="0.9500108mm" height="0.1999996mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin36"]} pcbX="-2.199894mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin35"]} pcbX="-1.799844mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin34"]} pcbX="-1.400048mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin33"]} pcbX="-0.999998mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin32"]} pcbX="-0.599948mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin31"]} pcbX="-0.199898mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin30"]} pcbX="0.200152mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin29"]} pcbX="0.599948mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin28"]} pcbX="0.999998mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin27"]} pcbX="1.400048mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin26"]} pcbX="1.800098mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin25"]} pcbX="2.200148mm" pcbY="2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin12"]} pcbX="2.200148mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin11"]} pcbX="1.800098mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin10"]} pcbX="1.400048mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin9"]} pcbX="0.999998mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin8"]} pcbX="0.599948mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin7"]} pcbX="0.200152mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin6"]} pcbX="-0.199898mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin5"]} pcbX="-0.599948mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin4"]} pcbX="-0.999998mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin3"]} pcbX="-1.400048mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin2"]} pcbX="-1.799844mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<smtpad portHints={["pin1"]} pcbX="-2.199894mm" pcbY="-2.999994mm" width="0.1999996mm" height="0.9500108mm" radius="0.0999998mm" shape="pill" />
<silkscreenpath route={[{"x":-2.9999431999999615,"y":2.5320498000000953},{"x":-2.9999431999999615,"y":2.999943200000075}]} />
<silkscreenpath route={[{"x":-2.5320498000000953,"y":-3.0000447999998414},{"x":-2.9999431999999615,"y":-3.0000447999998414},{"x":-2.9999431999999615,"y":-2.5295097999999143}]} />
<silkscreenpath route={[{"x":3.000044799999955,"y":-2.5295097999999143},{"x":3.000044799999955,"y":-3.0000447999998414},{"x":2.5320498000000953,"y":-3.0000447999998414}]} />
<silkscreenpath route={[{"x":2.5320498000000953,"y":2.999943200000075},{"x":3.000044799999955,"y":2.999943200000075},{"x":3.000044799999955,"y":2.5320498000000953}]} />
<silkscreenpath route={[{"x":-2.9999431999999615,"y":2.999943200000075},{"x":-2.5320498000000953,"y":2.999943200000075}]} />
<silkscreenpath route={[{"x":-2.8012643999999227,"y":-3.400043999999866},{"x":-2.950005455997598,"y":-3.5506860297037974},{"x":-2.799994399999946,"y":-3.700063424014502},{"x":-2.6499833440024076,"y":-3.5506860297037974},{"x":-2.798724400000083,"y":-3.400043999999866}]} />
<silkscreentext text="{NAME}" pcbX="0.00254mm" pcbY="4.4798mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-3.724999399999888,"y":3.7249994000000015},{"x":3.724999399999888,"y":3.7249994000000015},{"x":3.724999399999888,"y":-3.724999399999888},{"x":-3.724999399999888,"y":-3.724999399999888},{"x":-3.724999399999888,"y":3.7249994000000015}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 270,
        modelOriginPosition: { x: -0.00005079999993995443, y: -0.00005079999993995443, z: 0 },
      }}
      {...props}
    />
  )
}