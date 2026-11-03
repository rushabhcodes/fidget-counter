"""Check complete native/source triangle parity and retained world geometry.

PCB midplane moved2.5mm, so native coordinates move while world-space bearing,
ring and retainer geometry stays fixed. Never waive that transform comparison.
"""
from pathlib import Path
import hashlib,json,struct,subprocess
import numpy as np
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1];BASE='346fade26c8934f9d0b6411d7e30c1c9b06e9dac'
def load(data):
 if isinstance(data,Path):data=data.read_bytes()
 n=struct.unpack_from('<I',data,12)[0];return json.loads(data[20:20+n]),data[28+n:]
def accessor(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];types={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'};dims={'SCALAR':1,'VEC3':3,'VEC4':4};size=np.dtype(types[a['componentType']]).itemsize;d=dims[a['type']]
 return np.ndarray((a['count'],d),dtype=types[a['componentType']],buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*d),size))
def triangles(g,b,mesh):
 out=[]
 for p in mesh['primitives']:
  v=accessor(g,b,p['attributes']['POSITION']);ii=accessor(g,b,p['indices']).ravel();out.append(v[ii].reshape(-1,3,3))
 return np.concatenate(out).astype(float)
def ordered(t):
 keys=np.round(t,4);order=np.lexsort((keys[:,:,2],keys[:,:,1],keys[:,:,0]),axis=1)
 return np.take_along_axis(t,order[:,:,None],axis=1).reshape(-1,9)
def match(expected,actual,tolerance=1e-4):
 assert expected.shape==actual.shape,(expected.shape,actual.shape)
 a,b=ordered(expected),ordered(actual);tree=cKDTree(b);dist,indices=tree.query(a)
 assert (dist<tolerance).all(),('Native triangles differ from actual source model',float(dist.max()))
 # Preserve duplicate multiplicity as well as geometry, not just nearest points.
 used=set()
 for i,index in enumerate(indices):
  if int(index) in used:
   candidates=tree.query_ball_point(a[i],tolerance);index=next((j for j in candidates if j not in used),None);assert index is not None,'Triangle multiplicity changed'
  used.add(int(index))
 assert len(used)==len(b)
 return float(dist.max())
def digest(t):
 t=np.asarray(t,dtype='<f4').copy();t[t==0]=0;corners=np.sort(t.view('V12').reshape(-1,3),axis=1).copy().view('V36').ravel();corners.sort();return hashlib.sha256(corners.tobytes()).hexdigest()
manifest=json.loads((R/'mechanical/Circuit_Models/manifest.json').read_text());mid=manifest['pcbMidplaneZMm'];native,buffer=load(R/'dist/index/3d.glb')
pushfit=manifest['sourceParameters'].get('cap_retention',{}).get('mode')=='push_fit'
if pushfit:BASE='a7c29c470c439e6f4e35314b9c68bba5c8d8c100'
retained=['Bearing_6808','PCB_Fasteners','MagSafe_Ring','Cell','Magnet'] if pushfit else ['Bearing_6808','Inner_Race_Nut','Outer_Race_Retainer','Cap_Retainer_Screws','MagSafe_Ring'];retained_checks=[]
for name in retained:
 path='mechanical/Circuit_Models/'+name+'.glb';g,b=load(R/path);oldg,oldb=load(subprocess.check_output(['git','show',BASE+':'+path],cwd=R))
 assert digest(np.concatenate([triangles(g,b,m)for m in g['meshes']]))==digest(np.concatenate([triangles(oldg,oldb,m)for m in oldg['meshes']])),name+' world geometry changed'
 retained_checks.append(name)
checks=[]
for node in native['nodes']:
 if not node.get('name','').startswith('BEARING_V5_')or'mesh'not in node:continue
 name=node['name'].removeprefix('BEARING_V5_');g,b=load(R/'mechanical/Circuit_Models'/(name+'.glb'));source=np.concatenate([triangles(g,b,m)for m in g['meshes']]);expected=np.stack((-source[:,:,0],source[:,:,2]-mid,source[:,:,1]),axis=2)
 actual=triangles(native,buffer,native['meshes'][node['mesh']]);assert not node.get('matrix')and not node.get('rotation')and not node.get('scale')
 actual+=np.asarray(node.get('translation',[0,0,0]));error=match(expected,actual);checks.append({'name':name,'triangles':len(actual),'maximum_triangle_match_error_mm':error})
assert len(checks)==(7 if pushfit else 10)
assets=[]
for path in sorted((R/'mechanical/Circuit_Models').glob('*.glb')):
 g,b=load(path);v=[];faces=[]
 for line in path.with_suffix('.obj').read_text().splitlines():
  if line.startswith('v '):v.append(list(map(float,line.split()[1:4])))
  elif line.startswith('f '):faces.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
 assert digest(np.concatenate([triangles(g,b,m)for m in g['meshes']]))==digest(np.asarray(v)[np.asarray(faces)]),path.name+' OBJ/GLB mismatch';assets.append(path.stem)
assert len(assets)==(17 if pushfit else 20)
files=[Path(__file__),R/'mechanical/Circuit_Models/manifest.json',R/'dist/index/3d.glb']
report={'passed':True,'comparison_commit':BASE,'native_triangle_tolerance_mm':1e-4,'native_models':checks,'unchanged_world_geometry':retained_checks,'source_assets_equal_OBJ':assets,'source_sha256':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}}
(R/'validation/cr2450-display-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: all{len(checks)} native meshes match complete source triangles/poses;{len(retained_checks)} retained world geometries and all{len(assets)} OBJ/GLB triangle multisets preserved')
