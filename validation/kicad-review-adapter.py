"""KiCad9 review adapter: syntax/tolerance metadata only; never refill copper."""
from pathlib import Path
import json,re,sys,subprocess,shutil
import pcbnew
source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.parent.mkdir(parents=True,exist_ok=True)
text=source.read_text();text,n=re.subn(r'\(tenting\s+\(front yes\)\s+\(back yes\)\s*\)','(tenting front back)',text)
out.write_text(text);b=pcbnew.LoadBoard(str(out))
for z in b.Zones():
 if not z.GetIsRuleArea():z.SetLocalClearance(pcbnew.FromMM(.10))
pcbnew.SaveBoard(str(out),b)
profile={'board':{'design_settings':{'defaults':{},'diff_pair_dimensions':[],'drc_exclusions':[],'rules':{'min_clearance':.1,'min_track_width':.11,'min_via_diameter':.55,'min_through_hole_diameter':.3,'min_via_annular_width':.125,'min_copper_edge_clearance':.3,'min_hole_clearance':.2,'min_hole_to_hole':.2},'track_widths':[],'via_dimensions':[]}},'boards':[],'libraries':{'pinned_footprint_libs':[],'pinned_symbol_libs':[]},'meta':{'filename':out.with_suffix('.kicad_pro').name,'version':1},'net_settings':{'classes':[{'name':'Default','description':'JLC 2layer1oz minima; exact source fills retained without refill','clearance':.1,'track_width':.11,'via_diameter':.55,'via_drill':.3}],'meta':{'version':0}},'pcbnew':{'page_layout_descr_file':''},'sheets':[],'text_variables':{}}
out.with_suffix('.kicad_pro').write_text(json.dumps(profile,indent=2)+'\n')
out.with_suffix('.kicad_dru').write_text('''(version 1)
(rule "JLC different-net SMT pad spacing"
 (condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Pad_Type == 'SMD' && B.Pad_Type == 'SMD'")
 (constraint clearance (min 0.15mm)))
''')
def fills(board):
 result=[]
 for z in board.Zones():
  if z.GetIsRuleArea():continue
  layer='top'if z.GetLayer()==pcbnew.F_Cu else'bottom';polys=z.GetFilledPolysList(z.GetLayer())
  def points(c):return [[c.CPoint(i).x/1e6-100,100-c.CPoint(i).y/1e6]for i in range(c.PointCount())]
  for i in range(polys.OutlineCount()):result.append({'net':z.GetNetname(),'layer':layer,'outer':points(polys.COutline(i)),'holes':[points(polys.CHole(i,j))for j in range(polys.HoleCount(i))]})
 return result
out.with_suffix('.fills.json').write_text(json.dumps(fills(b)))
def drc(path):
 result=subprocess.run(['kicad-cli','pcb','drc',str(path),'--format','json','--output',str(path.with_suffix('.drc.json'))],capture_output=True,text=True)
 path.with_suffix('.drc.log').write_text(result.stdout+result.stderr)
 assert path.with_suffix('.drc.json').exists(),result.stderr
drc(out)
# A real wrong-net short must survive this adapter and be rejected by the review.
bad=out.with_name(out.stem+'-negative.kicad_pcb');target=next(p for f in b.GetFootprints()if f.GetReference()=='U2'for p in f.Pads()if p.GetNumber()=='4')
t=pcbnew.PCB_TRACK(b);t.SetLayer(pcbnew.F_Cu);t.SetWidth(pcbnew.FromMM(.25));t.SetNetCode(b.GetNetcodeFromNetname('VBAT'));t.SetStart(target.GetPosition());t.SetEnd(pcbnew.VECTOR2I(target.GetPosition().x+1000000,target.GetPosition().y));b.Add(t)
pcbnew.SaveBoard(str(bad),b)
for suffix in ['.kicad_pro','.kicad_dru']:shutil.copyfile(out.with_suffix(suffix),bad.with_suffix(suffix))
drc(bad)
print(json.dumps({'review_board':str(out),'tenting_syntax_replacements':n,'copper_refilled':False,'injected_wrong_net_short':str(bad)}))
