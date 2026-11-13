import {assembly} from '@tscircuit/core'
import type {CadModelProp} from '@tscircuit/props'
import base from './mechanical/Circuit_Models/Base_V3_Discs.glb'
import cap from './mechanical/Circuit_Models/Cap_circular.glb'
import bearing from './mechanical/Circuit_Models/Bearing_6808.glb'
import screws from './mechanical/Circuit_Models/PCB_Fasteners.glb'
import cell from './mechanical/Circuit_Models/Cell.glb'
import encoder from './mechanical/Circuit_Models/Magnet.glb'
import pcba from './mechanical/Circuit_Models/Drawings/PCBA_Body.glb'
import hall from './mechanical/Circuit_Models/Drawings/Hall_Sensor.glb'
import attachment from './mechanical/Circuit_Models/Attachment_Discs_V3.glb'
import project from './package.json'

// Two display states of the same audited enclosure, used only by drawing
// viewports. The manufacturing unit/BOM remains index.circuit.tsx + ORDER_LIST.
const model=(glbUrl:string,z=0,x=0,y=0):CadModelProp=>({
  glbUrl,modelUnitToMmScale:1,modelOriginPosition:{x:0,y:0,z:0},
  positionOffset:{x,y,z},rotationOffset:{x:0,y:0,z:0},
})
const State=({name,exploded=false}:{name:string;exploded?:boolean})=>{
  const dz=(value:number)=>exploded?value:0
  return <assembly.subassembly name={name}>
    <assembly.subassembly name="Mount">
      <assembly.printedpart name="Base" material="petg" cadModel={model(base,dz(25))}/>
      <assembly.part name="AttachmentDiscs" displayName="20 × Ø6 × 3 axial discs" cadModel={model(attachment,dz(-20))}/>
    </assembly.subassembly>
    <assembly.printedpart name="Cap" material="petg" cadModel={model(cap,dz(280))}/>
    <assembly.part name="Encoder" displayName="Same Ø6 × 3 axial disc on edge" cadModel={model(encoder,dz(235))}/>
    <assembly.part name="Bearing" displayName="6808-ZZ / 40 × 52 × 7" cadModel={model(bearing,dz(190))}/>
    <assembly.part name="PCB_Screws" displayName="2 × M2 × 4 nylon" cadModel={model(screws,dz(145))}/>
    <assembly.subassembly name="PCBA">
      <assembly.part name="BoardAnd26FittedParts" cadModel={model(pcba,dz(105))}/>
      <assembly.part name="Hall" cadModel={model(hall,dz(105))}/>
    </assembly.subassembly>
    <assembly.part name="Battery" displayName="CR2450" cadModel={model(cell,dz(70))}/>
  </assembly.subassembly>
}

export default ()=> <assembly.device name="EnclosureDrawing">
  <State name="Assembled"/>
  <State name="Exploded" exploded/>


  <assembly.drawing.page name="enclosure-assembly" displayName="Enclosure / assembled and exploded" size="iso_a3">
    <assembly.drawing.titleblock title="Fidget counter / enclosure and exploded assembly" legalOwner="rushabhcodes"
      identificationNumber="FCT-MECH-001" revisionIndex={project.version} dateOfIssue="2026-11-13" creator="rushabhcodes" sheetNumber={1} numberOfSheets={2}/>
    <assembly.drawing.partview name="AssembledIso" displayName="Assembled enclosure" partRef=".Assembled" direction="isometric" centerX={-100} centerY={65} width={180} height={110}/>
    <assembly.drawing.partview name="Front" displayName="Front / nominal mm" partRef=".Assembled" direction="y-" centerX={-100} centerY={-45} width={180} height={85}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="ExplodedIso" displayName="Exploded enclosure / 20 bottom discs + same disc on edge" partRef=".Exploded" direction="isometric" centerX={100} centerY={15} width={180} height={220}/>
  </assembly.drawing.page>

  <assembly.drawing.page name="enclosure-magnet-details" displayName="Magnet pattern and sensor clearance" size="iso_a3">
    <assembly.drawing.titleblock title="Fidget counter / magnet pockets and axial encoder" legalOwner="rushabhcodes"
      identificationNumber="FCT-MECH-001" revisionIndex={project.version} dateOfIssue="2026-11-13" creator="rushabhcodes" sheetNumber={2} numberOfSheets={2}/>
    <assembly.drawing.partview name="BottomPockets" displayName="20 × Ø6.4 blind pockets, 3.2 deep / Ø49.7 PCD" partRef=".Assembled > .Mount" direction="z-" centerX={-105} centerY={45} width={175} height={145}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="AxialDisc" displayName="Encoder Ø6 × 3 / mounted on edge" partRef=".Assembled > .Encoder" direction="y-" centerX={-105} centerY={-90} width={32} height={90}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="CenterSection" displayName="Center section / 3.4 × 6.4 slot, 1.2 roof, 1.8 Hall gap" partRef=".Assembled" direction="y-" centerX={100} centerY={45} width={180} height={145} section={{axis:'y',offset:0,keepSide:'greater',hatchSpacing:.6}}>
    </assembly.drawing.partview>
  </assembly.drawing.page>
</assembly.device>
