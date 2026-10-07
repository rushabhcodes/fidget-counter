import objPath from "./LQG15HS6N8G02D.obj"
import stepPath from "./LQG15HS6N8G02D.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"]
} as const

export const LQG15HS6N8G02D = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      symbol={
        <symbol>
          <schematiccircle center={{ x: -0.26, y: 0.02 }} radius={0.02} strokeWidth={0.02} color="#880000" isFilled fillColor="#880000" />
          <schematicpath svgPath="M 0.174 0.00138 A 0.08 0.078 0 1 0 0.3333 0.00128" strokeColor="#880000" />
          <schematicpath svgPath="M 0.00134 0.00142 A 0.08 0.078 0 1 0 0.16064 0.00132" strokeColor="#880000" />
          <schematicpath svgPath="M -0.168 0.00142 A 0.08 0.078 0 1 0 -0.0087 0.00132" strokeColor="#880000" />
          <schematicpath svgPath="M -0.33766 0.00136 A 0.08 0.078 0 1 0 -0.17836 0.00128" strokeColor="#880000" />
          <port name="pin1" pinNumber={1} aliases={["1"]} direction="left" schX={-0.4} schY={0} schStemLength={0.06} />
          <port name="pin2" pinNumber={2} aliases={["2"]} direction="right" schX={0.4} schY={0} schStemLength={0.06} />
          <schematictext schX={0} schY={0.286} text="{NAME}" fontSize={0.2} anchor="bottom_center" />
        </symbol>
      }
      supplierPartNumbers={{
  "jlcpcb": [
    "C521064"
  ]
}}
      manufacturerPartNumber="LQG15HS6N8G02D"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.545084mm" pcbY="0mm" width="0.7900924mm" height="0.540004mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.545084mm" pcbY="0mm" width="0.7900924mm" height="0.540004mm" shape="rect" />
<silkscreenpath route={[{"x":-1.397000000000162,"y":0.5715000000000146},{"x":-1.397000000000162,"y":-0.5715000000000146}]} />
<silkscreenpath route={[{"x":0.22621240000000853,"y":-0.4986020000000053},{"x":1.0163048000000572,"y":-0.4986020000000053},{"x":1.1687048000000004,"y":-0.3462019999999484},{"x":1.1687048000000004,"y":0.34620200000006207},{"x":1.0163048000000572,"y":0.498602000000119},{"x":0.22621240000000853,"y":0.498602000000119}]} />
<silkscreenpath route={[{"x":-0.22621240000012222,"y":-0.4986020000000053},{"x":-1.0163048000000572,"y":-0.4986020000000053},{"x":-1.1687048000001141,"y":-0.3462019999999484},{"x":-1.1687048000001141,"y":0.34620200000006207},{"x":-1.0163048000000572,"y":0.498602000000119},{"x":-0.22621240000012222,"y":0.498602000000119}]} />
<silkscreentext text="{NAME}" pcbX="-0.1143mm" pcbY="1.5588mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-0.7999984000000495,"y":0.24998679999998785},{"x":-0.5499862000000348,"y":0.24998679999998785},{"x":-0.5499862000000348,"y":-0.2500122000000147},{"x":-0.7999984000000495,"y":-0.2500122000000147},{"x":-0.7999984000000495,"y":-0.19999960000006922},{"x":-0.7999984000000495,"y":0.24998679999998785}]} strokeWidth="0.254mm" />
<courtyardoutline outline={[{"x":-1.1901301999999987,"y":0.5200019999999768},{"x":1.1901301999999987,"y":0.5200019999999768},{"x":1.1901301999999987,"y":-0.5200019999999768},{"x":-1.1901301999999987,"y":-0.5200019999999768},{"x":-1.1901301999999987,"y":0.5200019999999768}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0, y: 0, z: -0.26 },
      }}
      {...props}
    />
  )
}