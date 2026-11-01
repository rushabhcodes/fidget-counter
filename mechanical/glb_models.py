"""Lossless indexed GLB display assets, using the checked OBJ corner data.

The BRep/print geometry is untouched. Coordinates and normals are read from
our OBJ references so the display conversion preserves their float32 values.
"""
from pathlib import Path
import json,struct
import numpy as np
import trimesh

FINISH={'steel':(.9,.3),'polished':(1,.16),'plastic':(0,.4),'nylon':(0,.52),'rubber':(0,.72)}

def write_glb(path,groups):
 path=Path(path);vertices=[];normals=[];faces=[]
 for line in path.with_suffix('.obj').read_text().splitlines():
  if line.startswith('v '):vertices.append(list(map(float,line.split()[1:4])))
  elif line.startswith('vn '):normals.append(list(map(float,line.split()[1:4])))
  elif line.startswith('f '):
   values=[item.split('/') for item in line.split()[1:]]
   assert len(values)==3 and all(int(v[0])==int(v[2]) for v in values)
   faces.append([int(v[0])-1 for v in values])
 vertices=np.asarray(vertices,dtype=np.float32);normals=np.asarray(normals,dtype=np.float32);faces=np.asarray(faces)
 assert len(vertices)==len(normals)
 scene=trimesh.Scene();materials={}
 for i,group in enumerate(groups):
  ff=faces[group['first_face']:group['first_face']+group['face_count']];used=np.unique(ff);local=np.searchsorted(used,ff)
  mesh=trimesh.Trimesh(vertices=vertices[used],faces=local,vertex_normals=normals[used],process=False)
  metallic,roughness=FINISH[group['finish']];name=f'{path.stem}_{i}'
  mesh.visual=trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(name=name,baseColorFactor=[*group['color'],1],metallicFactor=metallic,roughnessFactor=roughness))
  scene.add_geometry(mesh,node_name=name)
  materials[name]={'baseColorFactor':[*group['color'],1],'metallicFactor':metallic,'roughnessFactor':roughness}
 blob=scene.export(file_type='glb',include_normals=True)
 length=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+length]);tail=blob[20+length:]
 # trimesh stores colours as 8-bit values; retain the original scalar colours.
 for material in g['materials']:
  material['pbrMetallicRoughness']=materials[material['name']]
 g.setdefault('asset',{}).setdefault('extras',{}).update({'cadUnits':'mm','cadUpAxis':'Z','source':'Lossless indexed display of the companion OBJ'})
 encoded=json.dumps(g,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4)
 header=struct.pack('<5I',0x46546c67,2,20+len(encoded)+len(tail),len(encoded),0x4e4f534a)
 path.write_bytes(header+encoded+tail)
 return len(faces)
