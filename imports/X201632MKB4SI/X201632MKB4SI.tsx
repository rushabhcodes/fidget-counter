import objPath from "./X201632MKB4SI.obj"
import stepPath from "./X201632MKB4SI.step"
import type { CrystalProps } from "@tscircuit/props"

type ImportedCrystalProps = Omit<CrystalProps, "frequency" | "pinVariant">

export const X201632MKB4SI = (props: ImportedCrystalProps) => {
  const { name = "X1", ...restProps } = props

  return (
    <crystal
      name={name}
      frequency="32MHz"
      pinVariant="four_pin"
      supplierPartNumbers={{
  "jlcpcb": [
    "C718072"
  ]
}}
      manufacturerPartNumber="X201632MKB4SI"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.700024mm" pcbY="-0.549783mm" width="0.8999982mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0.700024mm" pcbY="0.550037mm" width="0.8999982mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-0.700024mm" pcbY="0.550037mm" width="0.8999982mm" height="0.7999984mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.700024mm" pcbY="-0.549783mm" width="0.8999982mm" height="0.7999984mm" shape="rect" />
<silkscreenpath route={[{"x":-1.6499840000000177,"y":-0.1498853999999028},{"x":-1.6499840000000177,"y":-1.4498827999999548},{"x":-0.24998679999987417,"y":-1.4498827999999548}]} />
<silkscreenrect pcbX="0mm" pcbY="0mm" width="2.70002mm" height="2.29997mm" strokeWidth="0.151999696mm" />
<silkscreentext text="{NAME}" pcbX="-0.1524mm" pcbY="2.143127mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-1.4000230999998848,"y":1.2000362000001132},{"x":1.4000230999999985,"y":1.2000362000001132},{"x":1.4000230999999985,"y":-1.1997821999999587},{"x":-1.4000230999998848,"y":-1.1997821999999587},{"x":-1.4000230999998848,"y":1.2000362000001132}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: -0.00011430000006384944, z: -0.01 },
      }}
      {...restProps}
    />
  )
}