import objPath from "./SM05B_SRSS_TB_LF__SN_.obj"
import stepPath from "./SM05B_SRSS_TB_LF__SN_.step"
import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"],
  pin3: ["pin3"],
  pin4: ["pin4"],
  pin5: ["pin5"],
  pin6: ["pin6"],
  pin7: ["pin7"]
} as const

export const SM05B_SRSS_TB_LF__SN_ = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C136657"
  ]
}}
      manufacturerPartNumber="SM05B-SRSS-TB(LF)(SN)"
      footprint={<footprint>
        <smtpad portHints={["pin1"]} pcbX="-1.999615mm" pcbY="1.9998817mm" width="0.5999988mm" height="1.5500096mm" shape="rect" />
<smtpad portHints={["pin2"]} pcbX="-0.998855mm" pcbY="1.9998817mm" width="0.5999988mm" height="1.5500096mm" shape="rect" />
<smtpad portHints={["pin3"]} pcbX="0.000635mm" pcbY="1.9998817mm" width="0.5999988mm" height="1.5500096mm" shape="rect" />
<smtpad portHints={["pin4"]} pcbX="1.000125mm" pcbY="1.9998817mm" width="0.5999988mm" height="1.5500096mm" shape="rect" />
<smtpad portHints={["pin5"]} pcbX="2.000885mm" pcbY="1.9998817mm" width="0.5999988mm" height="1.5500096mm" shape="rect" />
<smtpad portHints={["pin6"]} pcbX="-3.300095mm" pcbY="-1.8748883mm" width="1.1999976mm" height="1.7999964mm" shape="rect" />
<smtpad portHints={["pin7"]} pcbX="3.300095mm" pcbY="-1.8748883mm" width="1.1999976mm" height="1.7999964mm" shape="rect" />
<silkscreenpath route={[{"x":2.9635449999999963,"y":0.4098417000000012},{"x":3.4639250000000033,"y":0.4098417000000012},{"x":2.9635449999999963,"y":0.4098417000000012}]} />
<silkscreenpath route={[{"x":2.9635449999999963,"y":1.108341700000011},{"x":3.4639250000000033,"y":1.108341700000011},{"x":2.9635449999999963,"y":1.108341700000011}]} />
<silkscreenpath route={[{"x":2.9635449999999963,"y":1.6087216999999896},{"x":2.9635449999999963,"y":0.4098417000000012},{"x":2.9635449999999963,"y":1.6087216999999896}]} />
<silkscreenpath route={[{"x":3.4639250000000033,"y":-0.7407783000000023},{"x":3.4639250000000033,"y":1.6087216999999896},{"x":2.564764999999994,"y":1.6087216999999896}]} />
<silkscreenpath route={[{"x":-2.3983949999999936,"y":-2.5746582999999816},{"x":2.399664999999999,"y":-2.5746582999999816}]} />
<silkscreenpath route={[{"x":-3.500754999999998,"y":-0.6747382999999871},{"x":-3.500754999999998,"y":1.6747617000000048},{"x":-2.599054999999993,"y":1.6747617000000048}]} />
<silkscreenpath route={[{"x":-3.000374999999991,"y":1.6747617000000048},{"x":-3.000374999999991,"y":0.4758817000000022},{"x":-3.000374999999991,"y":1.6747617000000048}]} />
<silkscreenpath route={[{"x":-3.000374999999991,"y":1.1743816999999979},{"x":-3.500754999999998,"y":1.1743816999999979},{"x":-3.000374999999991,"y":1.1743816999999979}]} />
<silkscreenpath route={[{"x":-3.000374999999991,"y":0.4758817000000022},{"x":-3.500754999999998,"y":0.4758817000000022},{"x":-3.000374999999991,"y":0.4758817000000022}]} />
<silkscreenpath route={[{"x":-2.7496008000000103,"y":2.249868499999991},{"x":-2.8423477253630693,"y":2.444417330345189},{"x":-3.0519658589417986,"y":2.494531975190256},{"x":-3.222678050756798,"y":2.362969871533082},{"x":-3.2276199964004775,"y":2.1475010414758344},{"x":-3.063119102311475,"y":2.0082505642884882},{"x":-2.851423763763421,"y":2.048702056102826},{"x":-2.7498548000000227,"y":2.238794100000007}]} />
<silkscreentext text="{NAME}" pcbX="-0.005715mm" pcbY="3.7618817mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-4.150093799999993,"y":3.024886500000008},{"x":4.150093799999993,"y":3.024886500000008},{"x":4.150093799999993,"y":-3.024886500000008},{"x":-4.150093799999993,"y":-3.024886500000008},{"x":-4.150093799999993,"y":3.024886500000008}]} />
      </footprint>}
      cadModel={{
        objUrl: objPath,
        stepUrl: stepPath,
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 2, y: 0.5124965000000032, z: -0.01 },
      }}
      {...props}
    />
  )
}