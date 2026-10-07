import objPath from "./RFANT3216120A5T.obj"
import stepPath from "./RFANT3216120A5T.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"]
} as const

export const RFANT3216120A5T = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C127629"
  ]
}}
      manufacturerPartNumber="RFANT3216120A5T"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="1.57607mm" pcbY="-0mm" width="0.7999984mm" height="1.6599916mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-1.524mm" pcbY="-0mm" width="0.7999984mm" height="1.6599916mm" shape="rect" />
<silkscreenrect pcbX="-0.418592mm" pcbY="0mm" width="0.127mm" height="2.032mm" strokeWidth="0.254mm" />
<silkscreenrect pcbX="-0.722884mm" pcbY="0.0635mm" width="0.228092mm" height="1.905mm" strokeWidth="0.254mm" />
<silkscreenrect pcbX="0mm" pcbY="0mm" width="4.318mm" height="2.032mm" strokeWidth="0.254mm" />
<silkscreentext text="{NAME}" pcbX="0.00127mm" pcbY="2.016mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.1739992000000257,"y":1.0799957999998924},{"x":2.2260692000000972,"y":1.0799957999998924},{"x":2.2260692000000972,"y":-1.0799958000001197},{"x":-2.1739992000000257,"y":-1.0799958000001197},{"x":-2.1739992000000257,"y":1.0799957999998924}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.026035000000092623, y: 0, z: -0.6 },
      }}
      {...props}
    />
  )
}