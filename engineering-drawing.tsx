import {assembly} from '@tscircuit/core'
import {Fragment} from 'react'
import project from './package.json'

// Native views reference the same board and enclosure used by PCB/3D/BOM.
// Each view uses the physical assembly without adding BOM components.
export const EngineeringDrawing=()=> <Fragment>
  <assembly.drawing.page name="enclosure-assembly" displayName="Enclosure / orthographic views" size="iso_a3">
    <assembly.drawing.titleblock title="Fidget counter / enclosure assembly dimensions" legalOwner="rushabhcodes"
      identificationNumber="FCT-MECH-001" revisionIndex={project.version} dateOfIssue="2026-11-19" creator="rushabhcodes" sheetNumber={1} numberOfSheets={2}/>
    <assembly.drawing.partview name="AssembledIso" displayName="Assembled enclosure" partRef=".FIDGET_COUNTER" direction="isometric" centerX={-100} centerY={65} width={180} height={110}/>
    <assembly.drawing.partview name="Front" displayName="Front / nominal mm" partRef=".FIDGET_COUNTER" direction="y-" centerX={-100} centerY={-45} width={180} height={85}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="Top" displayName="Top view" partRef=".FIDGET_COUNTER" direction="z+" centerX={100} centerY={65} width={180} height={110}/>
    <assembly.drawing.partview name="Right" displayName="Right view" partRef=".FIDGET_COUNTER" direction="x+" centerX={100} centerY={-45} width={180} height={85}/>

  </assembly.drawing.page>

  <assembly.drawing.page name="enclosure-magnet-details" displayName="Magnet pattern and sensor clearance" size="iso_a3">
    <assembly.drawing.titleblock title="Fidget counter / magnet pockets and axial encoder" legalOwner="rushabhcodes"
      identificationNumber="FCT-MECH-001" revisionIndex={project.version} dateOfIssue="2026-11-19" creator="rushabhcodes" sheetNumber={2} numberOfSheets={2}/>
    <assembly.drawing.partview name="BottomPockets" displayName="20 × Ø6.4 vented pockets / 3.2 stop depth / Ø49.7 PCD" partRef=".BEARING_V5_Base_V3_Discs" direction="z-" centerX={-105} centerY={45} width={175} height={145}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="AxialDisc" displayName="Encoder Ø6 × 3 / mounted on edge" partRef=".BEARING_V5_Magnet" direction="y-" centerX={-105} centerY={-90} width={32} height={90}>
    </assembly.drawing.partview>
    <assembly.drawing.partview name="CenterSection" displayName="Center section / 3.4 × 6.4 slot, 1.2 roof, 1.8 Hall gap" partRef=".FIDGET_COUNTER" direction="y-" centerX={100} centerY={45} width={180} height={145} section={{axis:'y',offset:0,keepSide:'greater',hatchSpacing:.6}}>
    </assembly.drawing.partview>
  </assembly.drawing.page>
</Fragment>
