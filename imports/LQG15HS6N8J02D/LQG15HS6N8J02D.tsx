import objPath from "./LQG15HS6N8J02D.obj"
import stepPath from "./LQG15HS6N8J02D.step"
import type { InductorProps } from "@tscircuit/props"

export const LQG15HS6N8J02D = (props: Omit<InductorProps, "inductance">) => {
  return (
    <inductor
      inductance="6.8nH"
      supplierPartNumbers={{
  "jlcpcb": [
    "C77110"
  ]
}}
      manufacturerPartNumber="LQG15HS6N8J02D"
      footprint={<footprint>
        <smtpad portHints={["pin2"]} pcbX="0.545084mm" pcbY="0mm" width="0.7900924mm" height="0.540004mm" shape="rect" />
<smtpad portHints={["pin1"]} pcbX="-0.545084mm" pcbY="0mm" width="0.7900924mm" height="0.540004mm" shape="rect" />
<silkscreenpath route={[{"x":-1.397000000000162,"y":0.5715000000000146},{"x":-1.397000000000162,"y":-0.5715000000000146}]} />
<silkscreenpath route={[{"x":0.22621240000000853,"y":-0.4986020000000053},{"x":1.0163048000000572,"y":-0.4986020000000053},{"x":1.1687048000000004,"y":-0.3462019999999484},{"x":1.1687048000000004,"y":0.34620200000006207},{"x":1.0163048000000572,"y":0.498602000000119},{"x":0.22621240000000853,"y":0.498602000000119}]} />
<silkscreenpath route={[{"x":-0.22621240000012222,"y":-0.4986020000000053},{"x":-1.0163048000000572,"y":-0.4986020000000053},{"x":-1.1687048000001141,"y":-0.3462019999999484},{"x":-1.1687048000001141,"y":0.34620200000006207},{"x":-1.0163048000000572,"y":0.498602000000119},{"x":-0.22621240000012222,"y":0.498602000000119}]} />
<silkscreentext text="{NAME}" pcbX="-0.1143mm" pcbY="1.5588mm" anchorAlignment="center" fontSize="1mm" />
<fabricationnotepath route={[{"x":-0.7999984000000495,"y":0.24998679999998785},{"x":-0.5499862000000348,"y":0.24998679999998785},{"x":-0.5499862000000348,"y":-0.2500122000000147},{"x":-0.7999984000000495,"y":-0.2500122000000147},{"x":-0.7999984000000495,"y":-0.19999960000006922},{"x":-0.7999984000000495,"y":0.24998679999998785}]} strokeWidth="0mm" isFilled hasStroke={false} />
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