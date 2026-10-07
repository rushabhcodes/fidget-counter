import objPath from "./KMR232NGULCLFS.obj"
import stepPath from "./KMR232NGULCLFS.step"
import type { PushButtonProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"]
} as const

export const KMR232NGULCLFS = (props: PushButtonProps<typeof pinLabels>) => {
  const { name = "SW1", ...restProps } = props

  return (
    <pushbutton
      name={name}
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C221681"
  ]
}}
      manufacturerPartNumber="KMR232NGULCLFS"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="2.050034mm" pcbY="0.799973mm" width="0.8999982mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="2.050034mm" pcbY="-0.799973mm" width="0.8999982mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="-2.050034mm" pcbY="-0.799973mm" width="0.8999982mm" height="0.999998mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="-2.050034mm" pcbY="0.799973mm" width="0.8999982mm" height="0.999998mm" shape="rect" />
<silkscreenpath route={[{"x":-0.817727600000012,"y":-0.8380222000000686},{"x":-0.817727600000012,"y":-0.5380228000000216},{"x":-0.8177530000000388,"y":-0.5380228000000216},{"x":-0.9677399999999352,"y":-0.38803580000012516},{"x":-0.9677399999999352,"y":0.21562059999996563},{"x":-0.9677399999999352,"y":0.21562059999996563},{"x":-0.7677404000000934,"y":0.41196259999992435},{"x":-0.7677404000000934,"y":0.7619745999999168},{"x":0.7822691999998597,"y":0.7619745999999168},{"x":0.7822691999998597,"y":0.5119623999999021},{"x":0.7822691999998597,"y":0.4137405999999828},{"x":0.9570211999999856,"y":0.2368804000000182},{"x":0.9570211999999856,"y":-0.3631184000000758},{"x":0.9570211999999856,"y":-0.3631184000000758},{"x":0.8070341999998618,"y":-0.5631180000000313},{"x":0.7822691999998597,"y":-0.8765794000000824},{"x":-0.817727600000012,"y":-0.8765794000000824}]} />
<silkscreenpath route={[{"x":-1.3918438000000606,"y":-1.4000226000000566},{"x":1.3919453999998268,"y":-1.4000226000000566}]} />
<silkscreenpath route={[{"x":-1.3918692000000874,"y":1.399971800000003},{"x":1.3919199999999137,"y":1.399971800000003}]} />
<silkscreenpath route={[{"x":2.1000212000000147,"y":0.06883399999992434},{"x":2.1000212000000147,"y":-0.06888480000020536}]} />
<silkscreenpath route={[{"x":-2.0999704000000747,"y":0.06883399999992434},{"x":-2.0999704000000747,"y":-0.06888480000020536}]} />
<silkscreentext text="{NAME}" pcbX="0.005334mm" pcbY="2.434973mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-2.750033099999996,"y":1.6549755999998297},{"x":2.750033099999996,"y":1.6549755999998297},{"x":2.750033099999996,"y":-1.655026399999997},{"x":-2.750033099999996,"y":-1.655026399999997},{"x":-2.750033099999996,"y":1.6549755999998297}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: -0.00002539999979944696, y: -0.004974599999973184, z: -1.42 },
      }}
      {...restProps}
    />
  )
}