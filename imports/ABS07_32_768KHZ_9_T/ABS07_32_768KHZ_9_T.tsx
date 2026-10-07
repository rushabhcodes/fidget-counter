import objPath from "./ABS07_32_768KHZ_9_T.obj"
import stepPath from "./ABS07_32_768KHZ_9_T.step"
import type { CrystalProps } from "@tscircuit/props"

type ImportedCrystalProps = Omit<CrystalProps, "frequency" | "pinVariant">

export const ABS07_32_768KHZ_9_T = (props: ImportedCrystalProps) => {
  const { name = "X1", ...restProps } = props

  return (
    <crystal
      name={name}
      frequency="32.768kHz"
      pinVariant="two_pin"
      supplierPartNumbers={{
  "jlcpcb": [
    "C179635"
  ]
}}
      manufacturerPartNumber="ABS07-32.768KHZ-9-T"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="1.274953mm" pcbY="0mm" width="1.0500106mm" height="1.6999966mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-1.274953mm" pcbY="0mm" width="1.0500106mm" height="1.6999966mm" shape="rect" />
<silkscreenpath route={[{"x":-2.0285710000000563,"y":-1.078484000000003},{"x":-2.0285710000000563,"y":1.0787379999999303},{"x":2.0286217999999963,"y":1.0787379999999303},{"x":2.0286217999999963,"y":-1.078484000000003},{"x":-2.0285710000000563,"y":-1.078484000000003}]} />
<silkscreentext text="{NAME}" pcbX="0.003429mm" pcbY="2.080516mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.0499582999999575,"y":1.0999983000000384},{"x":2.0499582999999575,"y":1.0999983000000384},{"x":2.0499582999999575,"y":-1.0999983000000384},{"x":-2.0499582999999575,"y":-1.0999983000000384},{"x":-2.0499582999999575,"y":1.0999983000000384}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.000025400000026820635, y: -0.00013969999997698324, z: -0.01 },
      }}
      {...restProps}
    />
  )
}