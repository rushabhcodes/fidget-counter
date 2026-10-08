"""Remove optional normals/unused UVs from untextured enclosure meshes.

Position arrays, triangle order, node transforms, electronic meshes and embedded
board textures are preserved. Duplicate buffers share storage; identity index
arrays are implicit. GLTF viewers derive flat face normals.
"""
from pathlib import Path
import argparse,base64,gzip,hashlib,json,struct
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--report',type=Path);a=p.parse_args()
b=a.source.read_bytes();jl=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+jl]);binary=b[28+jl:]
assert len(g['buffers'])==1 and not g.get('animations')and not g.get('skins')
old=json.loads(json.dumps(g));removed=[];implicit_indices=[]
mechanical={n['mesh']for n in g['nodes']if n.get('name','').startswith('ENCLOSURE_')and'mesh'in n}
for i in mechanical:
 for primitive in g['meshes'][i]['primitives']:
  mat=g['materials'][primitive['material']]
  assert 'Texture'not in json.dumps(mat)
  assert not primitive.get('targets')
  for attribute in ['NORMAL','TEXCOORD_0']:
   aid=primitive['attributes'].pop(attribute,None)
   if aid is not None:removed.append(aid)
  if 'indices' in primitive:
   aid=primitive['indices'];acc=g['accessors'][aid];view=g['bufferViews'][acc['bufferView']]
   assert acc['type']=='SCALAR' and not acc.get('sparse') and not view.get('byteStride')
   code={5121:'B',5123:'H',5125:'I'}[acc['componentType']]
   start=view.get('byteOffset',0)+acc.get('byteOffset',0)
   values=struct.unpack_from('<'+str(acc['count'])+code,binary,start)
   if acc['count']==g['accessors'][primitive['attributes']['POSITION']]['count'] and values==tuple(range(acc['count'])):
    assert primitive.get('mode',4)==4 and acc['count']%3==0
    del primitive['indices'];implicit_indices.append(aid)
used=set()
for m in g['meshes']:
 for primitive in m['primitives']:
  used.update(primitive['attributes'].values())
  if 'indices'in primitive:used.add(primitive['indices'])
accessor_ids=sorted(used);amap={v:i for i,v in enumerate(accessor_ids)}
view_ids=sorted({g['accessors'][i]['bufferView']for i in used}|{i['bufferView']for i in g.get('images',[])if'bufferView'in i})
vmap={};data=bytearray();views=[];unique_views={};merged_views=0
for i in view_ids:
 view=g['bufferViews'][i].copy();start=view.get('byteOffset',0);raw=binary[start:start+view['byteLength']]
 metadata={k:v for k,v in view.items() if k not in ['byteOffset','buffer']}
 key=(raw,json.dumps(metadata,sort_keys=True))
 if key in unique_views:
  vmap[i]=unique_views[key];merged_views+=1;continue
 vmap[i]=len(views);unique_views[key]=len(views)
 data.extend(b'\0'*((-len(data))%4));view['byteOffset']=len(data);data.extend(raw);views.append(view)
 assert bytes(data[view['byteOffset']:view['byteOffset']+view['byteLength']])==raw
accessors=[]
for i in accessor_ids:
 acc=g['accessors'][i].copy();acc['bufferView']=vmap[acc['bufferView']];accessors.append(acc)
for m in g['meshes']:
 for primitive in m['primitives']:
  primitive['attributes']={k:amap[v]for k,v in primitive['attributes'].items()}
  if 'indices'in primitive:primitive['indices']=amap[primitive['indices']]
for image in g.get('images',[]):
 if 'bufferView'in image:image['bufferView']=vmap[image['bufferView']]
g['accessors']=accessors;g['bufferViews']=views;g['buffers']=[{'byteLength':len(data)}]
data.extend(b'\0'*((-len(data))%4));js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
result=struct.pack('<III',0x46546c67,2,28+len(js)+len(data))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(data),0x004e4942)+data
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
assert g['nodes']==old['nodes'] and g['materials']==old['materials']
report={'source':str(a.source),'output':str(a.output),'sourceBytes':len(b),'outputBytes':len(result),'sourceSha256':hashlib.sha256(b).hexdigest(),'outputSha256':hashlib.sha256(result).hexdigest(),'meshCount':len(g['meshes']),'removedOptionalAttributeArrays':len(removed),'implicitIdentityIndexArrays':len(implicit_indices),'mergedDuplicateBufferViews':merged_views,'retainedBufferViewsByteIdentical':True,'positionsIndicesAndNodeTransformsUnchanged':True,'normals':'Face normals are derived by the viewer for untextured mechanical models. Electronic model normals and board textures are retained.'}
if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n')
archive=gzip.compress(json.dumps({'files':[{'file_path':str(a.output),'content_base64':base64.b64encode(result).decode()}]}).encode(),compresslevel=9)
print(json.dumps(report));print('Upload archive request bytes',len(archive)*4//3)
