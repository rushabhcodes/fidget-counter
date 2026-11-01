"""Compare complete triangle multisets and poses across display formats."""
from pathlib import Path
import hashlib,json,struct,sys
import numpy as np
root=Path(__file__).resolve().parents[1]
def load(path):
 blob=Path(path).read_bytes();n=struct.unpack_from('<I',blob,12)[0];return json.loads(blob[20:20+n]),blob[28+n:]
def accessor(g,b,i):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];types={5121:'u1',5123:'<u2',5125:'<u4',5126:'<f4'};dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4};size=np.dtype(types[a['componentType']]).itemsize;d=dims[a['type']]
 return np.ndarray((a['count'],d),dtype=types[a['componentType']],buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',size*d),size))
def record(g,b,node):
 triangles=[]
 for p in g['meshes'][node['mesh']]['primitives']:
  assert p.get('mode',4)==4
  v=accessor(g,b,p['attributes']['POSITION']);ii=accessor(g,b,p['indices']).ravel() if 'indices' in p else np.arange(len(v));triangles.append(v[ii].reshape(-1,3,3))
 t=np.concatenate(triangles).astype('<f4');t[t==0]=0
 corners=t.reshape(-1,3,3).view('V12').reshape(-1,3);ordered=np.sort(corners,axis=1).copy().view('V36').ravel();ordered.sort()
 return {'triangles':len(t),'triangle_sha256':hashlib.sha256(ordered.tobytes()).hexdigest(),'translation':node.get('translation',[0,0,0]),'rotation':node.get('rotation',[0,0,0,1]),'scale':node.get('scale',[1,1,1]),'matrix':node.get('matrix')}
def records(path):
 g,b=load(path);return {n['name']:record(g,b,n) for n in g['nodes'] if n.get('name','').startswith('BEARING_V5_')}
baseline=root/'validation/display-geometry-baseline.json'
if '--capture' in sys.argv:
 d=records(root/'work/model-source-before-compact.glb');baseline.write_text(json.dumps({'source_commit':'5fa112ffc8ffc72a630025258cbf3fa2a7f05daf','models':d},indent=2)+'\n');print('Captured',len(d),'validated display meshes')
else:
 expected=json.loads(baseline.read_text())['models'];actual=records(root/'dist/index/3d.glb')
 # The purchased-ring revision intentionally replaces exactly these parts.
 # Keep the original baseline to guard every other triangle and model pose.
 params=json.loads((root/'mechanical/enclosure-parameters.json').read_text())
 changed={'BEARING_V5_Stationary_Base','BEARING_V5_Bottom_Tray'}
 removed={'BEARING_V5_Attachment_Magnets','BEARING_V5_Backing_Ring'}
 added={'BEARING_V5_MagSafe_Ring'}
 assert params['attachment_ring']['outside_mm']==54.0
 assert set(actual)==(set(expected)-removed)|added
 for name in set(expected)-changed-removed:assert actual[name]==expected[name],name
 for name in changed:
  assert {k:v for k,v in actual[name].items() if k not in ['triangles','triangle_sha256']}=={k:v for k,v in expected[name].items() if k not in ['triangles','triangle_sha256']},name+' pose changed'
 source_checks=[]
 for asset_path in sorted((root/'mechanical/Circuit_Models').glob('*.glb')):
  source_g,source_b=load(asset_path);tri=[]
  for mesh in source_g['meshes']:
   for primitive in mesh['primitives']:
    v=accessor(source_g,source_b,primitive['attributes']['POSITION']);ii=accessor(source_g,source_b,primitive['indices']).ravel();tri.append(v[ii].reshape(-1,3,3))
  vv=[];ff=[]
  for line in asset_path.with_suffix('.obj').read_text().splitlines():
   if line.startswith('v '):vv.append(list(map(float,line.split()[1:4])))
   elif line.startswith('f '):ff.append([int(x.split('/')[0])-1 for x in line.split()[1:]])
  def digest(t):
   t=np.asarray(t,dtype='<f4').copy();t[t==0]=0
   records=np.sort(t.view('V12').reshape(-1,3),axis=1).copy().view('V36').ravel();records.sort();return hashlib.sha256(records.tobytes()).hexdigest()
  assert digest(np.concatenate(tri))==digest(np.asarray(vv,dtype='<f4')[np.asarray(ff)]),asset_path.name
  source_checks.append(asset_path.stem)
 assert len(source_checks)==26
 (root/'work/display-geometry-audit.json').write_text(json.dumps({'passed':True,'method':'Exact original triangle and pose equality outside the explicitly revised ring seat; all source GLBs equal companion OBJ triangles','intentional_changes':sorted(changed|removed|added),'models':actual,'source_assets_verified_against_OBJ':source_checks},indent=2)+'\n');print('Pass: original meshes/poses preserved outside the ring seat; all 26 GLB assets retain every OBJ triangle')
