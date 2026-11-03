"""Package preserved V1 and explicitly experimental V2 without mixing print sets."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1];V=R/'mechanical/variants';H=V/'V2_discrete_magnets';G=H/'generated';D=R/'manufacturing';D.mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
geometry=json.loads((G/'geometry-audit.json').read_text());audit=json.loads((G/'print-audit.json').read_text());assert geometry['passed']and audit['passed']and audit['actual_slicer_executed']
assert audit['geometry_audit_sha256']==sha((G/'geometry-audit.json').read_bytes())
assert geometry['parameters_sha256']==sha((H/'parameters.json').read_bytes())
assert geometry['builder_sha256']==sha((H/'build.py').read_bytes())
assert audit['audit_source_sha256']==sha((H/'audit.py').read_bytes())
assert geometry['source_circuit_sha256']==sha((R/'published.circuit.json').read_bytes())
for part in geometry['new_printed_parts']:
    for kind in ['STEP','STL']:assert sha((H/part[kind]).read_bytes())==part[kind+'_sha256']
version=json.loads((R/'package.json').read_text())['version']

def archive(label,files,start):
    entries={str(p.relative_to(R)):p.read_bytes()for p in files};entries['START_HERE.txt']=start.encode()
    path=D/f'fidget-counter-{label}-{version}.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,blob in sorted(entries.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,11,4,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,blob)
    return {'file':str(path.relative_to(R)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'members':{n:sha(b)for n,b in entries.items()}}

v1=archive('V1-preserved-base',[p for p in (V/'V1_premade_ring').rglob('*')if p.is_file()and'__pycache__'not in p.parts],
    'PRESERVED V1 PREMADE-RING BASE. Original 1.0.30 source commit and hashes are in manifest.json. Do not use with the V2 carrier. Follow V1 README and current cap/fit instructions. Physical qualification remains open.\n')
docs=[H/n for n in ['README.md','parameters.json','BOM.csv','polarity.svg','review.png']]+[G/n for n in ['geometry-audit.json','print-audit.json','print-ready-manifest.json','assembly-step-audit.json']]+[R/'ASSEMBLY.md',R/'mechanical/printing/PRINTING.md']+list((R/'mechanical/printing').glob('*.ini'))
printmanifest=json.loads((R/'mechanical/print-ready-manifest.json').read_text())
caps=[x for x in printmanifest['parts']if x['name'].startswith('Cap_')]
assert len(caps)==11
files=list((G/'Print_STL').glob('*.stl'))+list((G/'STEP').glob('*.step'))+docs
for cap in caps:
    for field in ['file','STEP_file']:
        p=R/cap[field];assert sha(p.read_bytes())==cap['sha256'if field=='file'else'STEP_sha256'];files.append(p)
files+=list((R/'mechanical/Print_STL/Coupons').glob('*'))
prints=archive('V2-magnets-print-test',files,
    'EXPERIMENTAL V2 FIT/FORCE TEST. Print Base_V2_Discrete + Magnet_Carrier_V2 + ONE existing Cap (3 product parts). Other ten cap styles are alternatives. Never print magnets or steel backing. Use base supports; carrier needs no supports and uses first-layer0.15mm to preserve its0.3mm floor. PETG0.4mm nozzle provisional: re-slice for your actual printer. Read V2 README and polarity template before bonding. Holding-force equivalence and physical qualification are UNVERIFIED. No machine G-code included.\n')
cad=archive('V2-magnets-CAD',[*docs,*list((G/'Assemblies').glob('*.step')),*list((G/'Reference_STEP').glob('*')),G/'V2_assembled.glb'],
    'V2 FULL ASSEMBLY AND PURCHASED/FABRICATED-PART REFERENCES. These assembled/exploded STEP and GLB files are for review, NOT rigid printing. Steel_Backing_V2_cut_profile.dxf is a 2D laser/waterjet profile; finished low-carbon steel thickness0.762mm and edge/finish requirements are in parameters/README. Holding force and magnetic material properties remain unverified. No order placed.\n')
result={'version':version,'physical_qualified':False,'holding_force_verified':False,'V1':v1,'V2_print':prints,'V2_CAD':cad}
(D/'magnet-variants-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:({n:v[n]for n in ['file','bytes','sha256']}if isinstance(v,dict)else v)for k,v in result.items()},indent=2))
