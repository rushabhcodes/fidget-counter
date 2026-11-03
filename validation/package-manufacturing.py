"""Package only the current verified print and fabrication deliverables."""
from pathlib import Path
import json,hashlib,zipfile,io
R=Path(__file__).resolve().parents[1];version=json.loads((R/'package.json').read_text())['version'];out=R/'manufacturing';out.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=json.loads((R/'mechanical/print-ready-manifest.json').read_text())
assert manifest['default_rigid_part_count']==2 and len(manifest['parts'])==12 and not manifest['tooling_files']
files={}
for part in manifest['parts']:
 for path,h in [(part['file'],part['sha256']),(part['STEP_file'],part['STEP_sha256'])]:
  b=(R/path).read_bytes();assert sha(b)==h,path;files[path]=b
for p in (R/'mechanical/Print_STL/Coupons').iterdir():
 if p.is_file():files[str(p.relative_to(R))]=p.read_bytes()
for path in ['mechanical/print-ready-manifest.json','mechanical/printing/PRINTING.md','MECHANICAL.md','ASSEMBLY.md','mechanical/COMPACT_CAP_REVIEW.md','mechanical/MANUFACTURING_REVIEW.md','mechanical/MECHANICAL_BOM.csv','mechanical/enclosure-parameters.json','validation/print-readiness.json','validation/print-wall-sections.json','validation/bearing-fit-coupons.json','validation/pushfit-cad-audit.json','validation/compact-cap-audit.json','validation/encoder-gap-audit.json','previews/compact-cap-section.png','previews/bearing-layout.png']:
 files[path]=(R/path).read_bytes()
for p in (R/'mechanical/printing').glob('*.ini'):files[str(p.relative_to(R))]=p.read_bytes()
files['START_HERE.txt']=b'FIT-TEST PRINT PILOT: print Stationary_Base plus ONE Cap only. Calibrate the bearing coupons first. Read mechanical/printing/PRINTING.md. PETG/0.4mm is provisional; re-slice for your machine. Purchased bearings, screws, PCBA, cells and magnets are not print parts. No machine G-code included. Hand-only seating and physical retention qualification remain required.\n'
def archive(name,entries):
 path=out/name
 assert len({n.casefold()for n in entries})==len(entries),'Archive paths collide on case-insensitive filesystems'
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n,b in sorted(entries.items()):
   info=zipfile.ZipInfo(n,date_time=(2026,11,3,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,b)
 return {'file':str(path.relative_to(R)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'files':{n:sha(b)for n,b in sorted(entries.items())}}
prints=archive(f'fidget-counter-print-pilot-{version}.zip',files)
D=R/'dist/fabrication';native=json.loads((R/'validation/native-fabrication-audit.json').read_text());gerber=json.loads((R/'validation/gerber-parity-audit.json').read_text())
assert native['passed']and gerber['passed']and native['unresolved_electrical_errors']==0 and native['unconnected_items']==0
blob=(D/'gerbers.zip').read_bytes();assert sha(blob)==native['fabrication_archive']['sha256']==gerber['archive_sha256']
z=zipfile.ZipFile(io.BytesIO(blob));fabs={'gerbers.zip':blob,'bom.csv':z.read('bom.csv'),'pick_and_place.csv':z.read('pick_and_place.csv'),'schematic.pdf':(D/'schematic.pdf').read_bytes()}
for path in ['validation/FABRICATION_REVIEW.md','validation/AI_REVIEW_RESOLUTION.md','validation/nordic-rf-audit.json','validation/nordic-reference-evidence.json','validation/native-fabrication-audit.json','validation/gerber-parity-audit.json','validation/programming-interface.json','validation/fresh-routing-audit.json','PROGRAMMING.md','BOM.csv']:
 fabs['reference/project-BOM.csv'if path=='BOM.csv'else path]=(R/path).read_bytes()
fabs['orientation-audit.json']=(D/'orientation-audit.json').read_bytes()
fabs['START_HERE.txt']=b'CONTROLLED PROTOTYPE/QUOTE PACKAGE. Upload the inner gerbers.zip for the PCB and the accompanying bom.csv/pick_and_place.csv for assembly. Board:36.5mm round,1.0mm thick,2layers/1oz,ENIG,Standard PCBA.27 fitted items include C7525448 CR2450 holder; loose cell is separate. Verify BT1 positive pin1 and bottom rotation180 in the assembly preview. Do not use failed experimental circuits. Read validation/FABRICATION_REVIEW.md. Pilot firmware/builds are linked in PROGRAMMING.md; physical production qualification remains open. No order is placed by these files.\n'
fabrication=archive(f'fidget-counter-fabrication-{version}.zip',fabs)
result={'version':version,'source_circuit_sha256':sha((R/'published.circuit.json').read_bytes()),'physical_qualified':False,'print':prints,'fabrication':fabrication}
(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'version':version,'archives':[{k:a[k]for k in ['file','bytes','sha256']}for a in [prints,fabrication]]},indent=2))
