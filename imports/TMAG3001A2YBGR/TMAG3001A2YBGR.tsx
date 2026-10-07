import objPath from "./TMAG3001A2YBGR.obj"
import stepPath from "./TMAG3001A2YBGR.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["VCC","A1"],
  pin2: ["N_INT","B1"],
  pin3: ["SDA","C1"],
  pin4: ["ADDR","A2"],
  pin5: ["GND","B2"],
  pin6: ["SCL","C2"]
} as const

export const TMAG3001A2YBGR = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C31115089"
  ]
}}
      manufacturerPartNumber="TMAG3001A2YBGR"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-0.199898mm" pcbY="0.40005mm" radius="0.0999998mm" shape="circle" />
<smtpad portHints={["pin2"]} pcbX="-0.199898mm" pcbY="-0mm" radius="0.0999998mm" shape="circle" />
<smtpad portHints={["pin3"]} pcbX="-0.199898mm" pcbY="-0.40005mm" radius="0.0999998mm" shape="circle" />
<smtpad portHints={["pin4"]} pcbX="0.199898mm" pcbY="0.40005mm" radius="0.0999998mm" shape="circle" />
<smtpad portHints={["pin5"]} pcbX="0.199898mm" pcbY="-0mm" radius="0.0999998mm" shape="circle" />
<smtpad portHints={["pin6"]} pcbX="0.199898mm" pcbY="-0.40005mm" radius="0.0999998mm" shape="circle" />
<silkscreenpath route={[{"x":-0.6998969999999929,"y":0.40004999999999313},{"x":-0.6998969999999929,"y":1.0000488000000018},{"x":-0.19989799999999036,"y":1.0000488000000018}]} />
<silkscreenpath route={[{"x":-0.47320199999998636,"y":0.7192009999999982},{"x":0.47320200000000057,"y":0.7192009999999982},{"x":0.47320200000000057,"y":-0.7192010000000124},{"x":-0.47320199999998636,"y":-0.7192010000000124},{"x":-0.47320199999998636,"y":0.7192009999999982}]} />
<silkscreentext text="{NAME}" pcbX="-0.127mm" pcbY="1.9906mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-0.6499991999999963,"y":0.9000113999999968},{"x":0.6499991999999963,"y":0.9000113999999968},{"x":0.6499991999999963,"y":-0.8999860000000126},{"x":-0.6499991999999963,"y":-0.8999860000000126},{"x":-0.6499991999999963,"y":0.9000113999999968}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.000012699999984988608, z: -0.478 },
      }}
      {...props}
    />
  )
}