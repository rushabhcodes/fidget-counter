// Resolve imported-GLB dimensions into native Circuit JSON drawing records.
// Imported CAD dimensions use the same glTF
// scenes and PoppyGL camera as the native drawing exporter for imported CAD.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs'
import {resolve,dirname} from 'node:path'
import {pathToFileURL} from 'node:url'
import {createHash} from 'node:crypto'
import assert from 'node:assert/strict'
import {convertCircuitJsonToGltf} from 'circuit-json-to-gltf'
import {buildSubtree} from '@tscircuit/circuit-json-util'
import {buildCamera,computeWorldAABB,createSceneFromGLTF,loadGLTFWithResourcesFromURL,DEFAULT_RENDER_OPTIONS} from 'poppygl'
import {mat4,vec4} from 'gl-matrix'
import {drawing_dimension_line} from 'circuit-json'
const input=process.argv[2]??'dist/index/circuit.json'
const output='dist/index.circuit.json'
const c=JSON.parse(readFileSync(input)).filter(e=>e.type!=='drawing_dimension_line')
const p=JSON.parse(readFileSync('mechanical/enclosure-parameters.json'))
const cache=new Map(),measurements=[]
const hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex')
const geometry=c.filter(e=>!e.type.startsWith('drawing_'))
for(const e of geometry)if(e.type==='cad_component')for(const key of ['model_obj_url','model_mtl_url','model_glb_url','model_gltf_url','model_stl_url']){
  if(e[key]?.startsWith('./'))e[key]=pathToFileURL(resolve(e[key])).href
}
function membership(view){
  return view.drawing_assembly_stage_id?c.find(e=>e.type==='drawing_assembly_stage'&&e.drawing_assembly_stage_id===view.drawing_assembly_stage_id):view
}
async function sceneFor(view){
  view=membership(view)
  const key=JSON.stringify([view.source_group_id,view.source_component_ids,view.pcb_board_ids])
  if(cache.has(key))return cache.get(key)
  const ids=new Set(view.source_component_ids)
  const boards=new Set(view.pcb_board_ids??[])
  const selected=view.source_group_id?buildSubtree(geometry,{source_group_id:view.source_group_id}):geometry.filter(e=>(['cad_component','source_component'].includes(e.type)&&ids.has(e.source_component_id))||boards.has(e.pcb_board_id))
  const blob=await convertCircuitJsonToGltf(selected,{format:'glb',includeModels:true,showBoundingBoxes:false})
  const {gltf,resources}=await loadGLTFWithResourcesFromURL('data:model/gltf-binary;base64,'+Buffer.from(blob).toString('base64'))
  const scene=createSceneFromGLTF(gltf,resources);assert(scene.drawCalls.length)
  cache.set(key,scene);return scene
}
const directions={x_positive:[1,0,0],x_negative:[-1,0,0],y_positive:[0,0,-1],y_negative:[0,0,1],z_positive:[0,1,0],z_negative:[0,-1,0],isometric:[1,1,-1]}
async function viewInfo(name){
  const view=c.find(e=>e.type==='drawing_part_view'&&e.name===name);assert(view,name)
  const scene=await sceneFor(view),bounds=computeWorldAABB(scene.drawCalls)
  const center=bounds.min.map((v,i)=>(v+bounds.max[i])/2),distance=Math.max(1,Math.hypot(...bounds.min.map((v,i)=>bounds.max[i]-v))*3)
  const vector=directions[view.direction],length=Math.hypot(...vector)
  const eye=center.map((v,i)=>v+vector[i]/length*distance)
  const camera=buildCamera(scene.drawCalls,Math.round(view.width*4),Math.round(view.height*4),DEFAULT_RENDER_OPTIONS.fov,eye,center,view.direction.startsWith('z_')?'z-':'y+',null,'orthographic',view.scale==null?null:view.height/view.scale)
  const matrix=mat4.multiply(new Float64Array(16),camera.proj,camera.view)
  const project=point=>{
    const q=vec4.transformMat4(new Float64Array(4),[...point,1],matrix)
    return {x:view.center.x+q[0]/q[3]*view.width/2,y:view.center.y+q[1]/q[3]*view.height/2}
  }
  const corners=[0,1,2,3,4,5,6,7].map(mask=>project(bounds.min.map((v,i)=>mask&(1<<i)?bounds.max[i]:v)))
  const box={minX:Math.min(...corners.map(v=>v.x)),maxX:Math.max(...corners.map(v=>v.x)),minY:Math.min(...corners.map(v=>v.y)),maxY:Math.max(...corners.map(v=>v.y))}
  return {view,bounds,center,project,box}
}
function add(info,name,a,b,offset,text,value,expected){
  assert(Math.abs(value-expected)<.002,`${name}: CAD changed (${value} versus ${expected})`)
  const record=drawing_dimension_line.parse({type:'drawing_dimension_line',drawing_dimension_line_id:'drawing_dimension_line_'+measurements.length,drawing_part_view_id:info.view.drawing_part_view_id,name,start:{x:a.x+offset.x,y:a.y+offset.y},end:{x:b.x+offset.x,y:b.y+offset.y},edge_ref_start:a,edge_ref_end:b,text})
  c.push(record);measurements.push({name,value_mm:value,nominal_mm:expected})
}
function extent(info,axis,name,text,expected){
  const b=info.box
  const a=axis==='x'?{x:b.minX,y:b.minY}:{x:b.maxX,y:b.minY}
  const z=axis==='x'?{x:b.maxX,y:b.minY}:{x:b.maxX,y:b.maxY}
  add(info,name,a,z,axis==='x'?{x:0,y:-7}:{x:7,y:0},text,info.bounds.max[axis==='x'?0:1]-info.bounds.min[axis==='x'?0:1],expected)
}
const front=await viewInfo('Front')
extent(front,'x','OverallDiameter','Ø61.60 mm',61.6);extent(front,'y','OverallHeight','20.90 mm',p.physical_height_mm)
const bottom=await viewInfo('BottomPockets');extent(bottom,'x','BaseDiameter','Ø58.00 mm',p.base_diameter_mm)
const radius=p.magnet.pitch_radius_mm
const a=bottom.project([-radius,bottom.center[1],0]),b=bottom.project([radius,bottom.center[1],0])
add(bottom,'AttachmentPitchDiameter',a,b,{x:0,y:bottom.box.maxY+7-a.y},'Ø49.70 PCD',radius*2,49.7)
const disc=await viewInfo('AxialDisc');extent(disc,'x','DiscThickness','3.00 mm',3);extent(disc,'y','DiscDiameter','Ø6.00 mm',6)
const section=await viewInfo('CenterSection')
const sectionMembers=membership(section.view)
const selected=sectionMembers.source_component_ids?new Set(sectionMembers.source_component_ids):new Set(buildSubtree(c,{source_group_id:sectionMembers.source_group_id}).filter(e=>e.type==='source_component').map(e=>e.source_component_id))
async function partBounds(name){
  const source=c.find(e=>e.type==='source_component'&&e.name===name&&selected.has(e.source_component_id));assert(source,name)
  const scene=await sceneFor({source_component_ids:[source.source_component_id]})
  return computeWorldAABB(scene.drawCalls)
}
const magnet=await partBounds('BEARING_V5_Magnet'),sensor=await partBounds('U2')
const m=section.project([magnet.max[0],magnet.min[1],(magnet.min[2]+magnet.max[2])/2])
const h=section.project([magnet.max[0],sensor.max[1],(sensor.min[2]+sensor.max[2])/2])
add(section,'EncoderHallGap',h,m,{x:9,y:0},'1.80 mm NOM',magnet.min[1]-sensor.max[1],p.nominal_encoder_gap_mm)
// Keep authored model URLs portable in the saved native drawing document.
for(const e of c)if(e.type==='cad_component')for(const key of ['model_obj_url','model_mtl_url','model_glb_url','model_gltf_url','model_stl_url']){
  if(e[key]?.startsWith(pathToFileURL(process.cwd()+'/').href))e[key]='./'+e[key].slice(pathToFileURL(process.cwd()+'/').href.length)
}
writeFileSync(output,JSON.stringify(c,null,2)+'\n')
mkdirSync('dist/validation/native-drawing',{recursive:true})
writeFileSync('dist/validation/native-drawing/dimension-audit.json',JSON.stringify({passed:true,renderer:'Native tsCircuit / PoppyGL',source:input,output,native_pages:c.filter(e=>e.type==='drawing_page').length,native_views:c.filter(e=>['drawing_part_view','drawing_explosion_view'].includes(e.type)).length,native_dimension_lines:measurements.length,measurements,source_sha256:hash('engineering-drawing.tsx'),resolver_sha256:hash(import.meta.filename),circuit_sha256:hash(output)},null,2)+'\n')
console.log('PASS: native drawing pages, model-derived dimensions and portable CAD URLs',measurements)
