"""Export PDF/PNG copies of sheets rendered by tsCircuit's native drawing CLI."""
from pathlib import Path
import hashlib,io,json
import cairosvg
from pypdf import PdfReader,PdfWriter
R=Path(__file__).resolve().parents[1]
version=json.loads((R/'package.json').read_text())['version']
H=R/'mechanical/variants/V3_disc_magnets';D=H/'drawings';D.mkdir(exist_ok=True)
names=['enclosure-assembly','enclosure-magnet-details'];writer=PdfWriter();outputs={}
sha=lambda b:hashlib.sha256(b).hexdigest()
for number,name in enumerate(names,1):
 source=R/'dist/enclosure-drawing/drawings'/(name+'.svg')
 svg=source.read_bytes();assert b'data-drawing-part-view-id'in svg and b'data-drawing-dimension-line-id'in svg
 target=D/f'engineering-drawing-v{version}-sheet-{number}.svg';target.write_bytes(svg)
 png=target.with_suffix('.png');cairosvg.svg2png(bytestring=svg,write_to=str(png),output_width=2646,output_height=1871)
 pdf=cairosvg.svg2pdf(bytestring=svg);writer.append(PdfReader(io.BytesIO(pdf)))
 outputs[str(target.relative_to(R))]=sha(svg);outputs[str(png.relative_to(R))]=sha(png.read_bytes())
writer.add_metadata({'/Title':f'Fidget counter native engineering drawing {version}','/Author':'rushabhcodes','/Subject':'Native tsCircuit assembly.drawing pages; assembled and exploded enclosure; model-derived dimensions'})
path=D/f'engineering-drawing-v{version}.pdf'
with path.open('wb')as stream:writer.write(stream)
outputs[str(path.relative_to(R))]=sha(path.read_bytes())
pdf=PdfReader(path);assert len(pdf.pages)==2
for page in pdf.pages:
 assert abs(float(page.mediabox.width)-420/25.4*72)<.01 and abs(float(page.mediabox.height)-297/25.4*72)<.01
 assert 'FCT-MECH-001'in page.extract_text()
native=json.loads((R/'work/native-drawing/dimension-audit.json').read_text());assert native['passed']
report={**native,'project_release':version,'format':'A3 landscape','native_drawing_support':True,'renderer':'tsCircuit --drawings / @tscircuit/circuit-json-to-drawing','export_only_no_redrawing':True,'outputs':outputs}
(D/'drawing-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'native_pages':native['native_pages'],'native_views':native['native_views'],'native_dimension_lines':native['native_dimension_lines'],'PDF':str(path.relative_to(R))},indent=2))
