"""Define schematic alternatives and draw measured elevation references.

Front x is lot-local from street-left. Rear x is mirrored from building-left
as seen from the garden. All z levels are relative to ground finished floor.
"""
from pathlib import Path
import json, hashlib, copy, subprocess, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'concept-10'
TMP=Path('/private/tmp/las-juntas-style-study-01'); TMP.mkdir(exist_ok=True)
base=json.loads((BASE/'rendering-geometry.json').read_text())
schedule=json.loads((BASE/'area-schedule.json').read_text())
common={
 'coordinate_basis':base['coordinate_basis'],
 'adopted':base['adopted'], 'areas_m2':schedule['areas'],
 'parking':base['parking_m'], 'gate':base['gate_lot_coordinates_m'],
 'ground_plan_lot_xywh':[1,5.5,9,10.5],
 'upper_plan_lot_xywh':[1,5.5,9,9.5],
 'terrace_lot_xywh':[3,16,6,3],
 'rear_openings':base['rear_openings_x_z_w_h'],
 'rear_canopy_columns_lot_xywh':[[3.09,18.81,.12,.12],[8.79,18.81,.12,.12]],
 'status':'Appearance alternatives only. Proposed openings, roof levels, slopes, reveals and canopies are schematic; structure, glazing, drainage, guards and cost are not selected.',
 'baseline_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.iterdir() if p.is_file()},
}
variants={
 'A':{'title':'Warm tropical contemporary','subtitle':'Ivory plaster / bronze / timber / horizontal shade',
 'color':'#E9DEC9','trim':'#665847','accent':'#A76840','recommended':True,
 'front_openings':copy.deepcopy(base['front_openings_x_z_w_h']),
 'roof':{'type':'flat roof with parapet','main_top':6.70,'highest_top':6.70,'footprint_lot':[1,5.5,9,9.5]},
 'front_canopy':{'footprint_lot':[4.85,4.70,1.80,.80],'soffit':2.65,'top':2.80},
 'stair_reveal_projection':.20,
 'rear_canopy':{'type':'flat','footprint_lot':[3,16,6,3],'soffit':2.65,'low_top':2.85,'high_top':2.85},
 'notes':['One high bathroom ribbon replaces two upper openings; split into three glazed modules.',
          'Two independent stair windows retain the floor band between them. Bronze frames sit behind projecting plaster reveals.',
          'Use timber at the protected entry and canopy soffit; keep exposed frame and gate finishes coordinated.'],
 'tradeoff':'The closest fit to the established flat-roof structure. The wider bathroom opening needs a coordinated lintel and high-level operating hardware.',
 'source':{'title':'Casa Los Mangos / Bernal Architecture Studio / Bucerias','url':'https://www.brnlarchitecture.com/es/casa-los-mangos-nuevo-vallarta'}},
 'B':{'title':'Traditional Vallarta','subtitle':'Warm white / clay roofs / muted ochre trim / dark metal',
 'color':'#F3EADB','trim':'#A88152','accent':'#A65535','recommended':False,
 'front_openings':copy.deepcopy(base['front_openings_x_z_w_h']),
 'roof':{'type':'hipped clay-tile roof','main_top':6.60,'highest_top':7.95,'slope_rise_per_run':.30,
         'footprint_lot':[1,5.15,9,10.20],'ridge_lot_xy_start_end':[[5.50,9.65],[5.50,10.85]],
         'side_eave_projection':0,'front_rear_eave_projection':.35},
 'front_canopy':None,'stair_reveal_projection':.12,
 'rear_canopy':{'type':'clay-tile shed roof descending to garden','footprint_lot':[3,16,6,3],
                'soffit':2.50,'low_top':2.70,'high_top':3.60,'slope_rise_per_run':.30},
 'notes':['Narrower vertical stair windows sit in restrained ochre plaster trim; bathroom windows stay separate and obscure-glazed.',
          'The roof hips on all four sides. Eaves project at front/rear only; side edges stay within the lot.',
          'The rear canopy uses a matching sloping clay roof and timber-toned soffit. Its outer soffit is lower than A and C.'],
 'tradeoff':'The strongest traditional character, with an added pitched roof and more roof junctions to price and maintain. Tile fixing, pitch suitability and roof support require selection.',
 'source':{'title':'Puerto Vallarta Tourism Board / Cultural Patrimony of Jalisco','url':'https://visitpuertovallarta.com/blog/puerto-vallarta-cultural-patrimony-of-jalisco'}},
 'C':{'title':'Sculptural contemporary','subtitle':'Sand-gray plaster / deep reveals / curved entry / stepped roofline',
 'color':'#C5B8A4','trim':'#5B4E41','accent':'#8F674B','recommended':False,
 'front_openings':copy.deepcopy(base['front_openings_x_z_w_h']),
 'roof':{'type':'flat roof with raised front stair parapet','main_top':6.65,'highest_top':7.10,
         'footprint_lot':[1,5.5,9,9.5],'raised_parapet_footprint_lot':[7.25,5.5,2.75,4.80]},
 'front_canopy':{'footprint_lot':[4.85,4.95,1.80,.55],'soffit':2.60,'top':2.85,'form':'rounded plaster entry surround'},
 'stair_reveal_projection':.25,
 'rear_canopy':{'type':'flat','footprint_lot':[3,16,6,3],'soffit':2.65,'low_top':2.85,'high_top':2.85},
 'notes':['Taller independent stair windows, with the floor band left solid, create a clear vertical rhythm.',
          'The raised parapet occupies the front stair zone only. From the low garden viewpoint it sits behind the rear roofline, not on the rear wall.',
          'A rounded external plaster surround softens the unchanged entrance. Use textured plaster for the finish; exposed structural concrete is not specified.'],
 'tradeoff':'More custom plaster geometry and coping junctions than A. The deeper reveals and taller windows need coordinated flashing, cleaning reach and stair guarding.',
 'source':{'title':'Casa Tao / HW Studio / Puerto Vallarta','url':'https://www.hw-studio.com/tao-house'}},
}
v=variants['A']; v['front_openings'].pop('upper_bath_1');v['front_openings'].pop('upper_bath_2')
v['front_openings']['upper_bath_ribbon']=[1.40,5.15,3.10,.55]
variants['B']['front_openings']['ground_stair']=[8.075,1.00,1.10,1.60]
variants['B']['front_openings']['upper_stair']=[8.075,4.40,1.10,1.60]
variants['C']['front_openings']['ground_stair']=[8.025,.90,1.20,1.80]
variants['C']['front_openings']['upper_stair']=[8.025,4.30,1.20,1.80]

def within(rect,outer):
 x,y,w,h=rect;a,b,c,d=outer
 return x>=a-1e-8 and y>=b-1e-8 and x+w<=a+c+1e-8 and y+h<=b+d+1e-8
def overlap(a,b):
 return min(a[0]+a[2],b[0]+b[2])>max(a[0],b[0])+1e-8 and min(a[1]+a[3],b[1]+b[3])>max(a[1],b[1])+1e-8
def verify():
 zones={'ground_bath':(1.2,3.2),'ground_laundry':(3.35,4.8),'entry':(4.95,7.15),
        'ground_stair':(7.3,9.8),'upper_bath':(1.2,4.8),'upper_stair':(7.3,9.8)}
 for key,v in variants.items():
  for name,(x,z,w,h) in v['front_openings'].items():
   room='upper_bath' if name.startswith('upper_bath') else name
   left,right=zones[room]
   assert x>=left and x+w<=right,(key,name,'room bounds')
   level=3.4 if name.startswith('upper') else 0
   ceiling=6.2 if level else 3.0
   assert z>=level and z+h<=ceiling,(key,name,'height bounds')
   if 'bath' in name:
    assert z-level>=1.6 # Obscure glazing also required; height alone is not privacy.
   if name.startswith('upper_bath'):
    assert z-level>.90 # Above the assumed vanity worktop; mirrors/sashes to detail.
  gs=v['front_openings']['ground_stair'];us=v['front_openings']['upper_stair']
  assert abs(us[1]-gs[1]-3.4)<1e-8 and gs[1]+gs[3]<us[1]
  assert within(v['roof']['footprint_lot'],[0,0,10,20])
  assert within(v['rear_canopy']['footprint_lot'],[0,0,10,20])
  assert v['rear_canopy']['high_top']<common['rear_openings']['upper_primary_window'][1]
  fc=v['front_canopy']
  if fc:
   assert within(fc['footprint_lot'],[0,0,10,20])
   assert not overlap(fc['footprint_lot'],common['parking']['car'])
   assert fc['soffit']>2.45
 for col in common['rear_canopy_columns_lot_xywh']:
  assert within(col,common['terrace_lot_xywh'])
 assert abs(7.95-6.6-4.5*.3)<1e-8
 assert abs(3.60-2.70-3*.3)<1e-8
 gate=common['gate'];car=common['parking']['car']
 assert not overlap(gate['open_leaf'],car)
 assert within(gate['open_leaf'],gate['runback_reserve'])
 assert gate['closed_leaf'][0]<gate['opening_x'][0] and sum(gate['closed_leaf'][::2])>gate['opening_x'][1]
 assert common['parking']['court_depth']==5.5 and car[3]==4.5
 return ['Opening extents match their existing rooms','Opening heads below adopted ceilings',
 'Separate stair windows resolve the 3.40 m floor separation','Bathroom openings high and specified obscure-glazed',
 'Roof/canopy footprints inside lot','Front entrance details outside car footprint',
 'Roof pitches reconcile with proposed ridge/canopy levels','Rear canopy clears upper primary window',
 'Complete gate fits runback; car footprint retained','Baseline room, floor, stair, kitchen and gate data retained']

def rect(c,x,z,w,h,fill):
 c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor('#796F61'));c.setLineWidth(.6)
 c.rect(80+x*95,150+z*95,w*95,h*95,fill=1,stroke=1)
def poly(c,pts,fill):
 p=c.beginPath();p.moveTo(80+pts[0][0]*95,150+pts[0][1]*95)
 for x,z in pts[1:]:p.lineTo(80+x*95,150+z*95)
 p.close();c.setFillColor(HexColor(fill));c.drawPath(p,stroke=1,fill=1)
def guide(key,side):
 v=variants[key];pdf=TMP/f'{key.lower()}-{side}-elevation.pdf'
 c=canvas.Canvas(str(pdf),pagesize=(1110,1110));c.setTitle(f'{key} {side} schematic elevation')
 c.setAuthor('Client concept study');c.setFillColor(HexColor('#FBF8F1'));c.rect(0,0,1110,1110,fill=1,stroke=0)
 front=side=='front';x0=1 if front else .5
 rect(c,x0,0,9,v['roof']['main_top'],v['color'])
 if key=='B':poly(c,[(x0,6.6),(x0+4.5,7.95),(x0+9,6.6)],'#AD6242')
 elif key=='C' and front:rect(c,7.25,6.65,2.75,.45,v['color'])
 openings=v['front_openings'] if front else common['rear_openings']
 for name,(x,z,w,h) in openings.items():
  if not front:x+=.5
  if front and 'stair' in name:
   border=v['stair_reveal_projection'];rect(c,x-border,z-border,w+2*border,h+2*border,v['color'])
  rect(c,x,z,w,h,'#B5C1BF' if 'bath' in name else '#7A9396' if name!='entry' else '#946840')
  count=3 if name=='upper_bath_ribbon' else 2
  for i in range(1,count):rect(c,x+w*i/count-.015,z,.03,h,v['trim'])
 if front:
  fc=v['front_canopy']
  if fc:rect(c,fc['footprint_lot'][0],fc['soffit'],fc['footprint_lot'][2],fc['top']-fc['soffit'],v['trim'])
  for x,y,w,d in common['gate']['posts']:rect(c,x,0,w,1.85,v['color'])
  for x,y,w,d in [common['gate']['fixed_fence'],common['gate']['open_leaf']]:
   rect(c,x,.03,w,1.75,v['trim'])
  rect(c,8.55,.03,1.10,1.75,v['trim'])
  rect(c,1.80,.12,1.85,1.40,'#A3ABA7')
  rect(c,1.92,.85,1.61,.44,'#728A8C')
 else:
  rc=v['rear_canopy'];rect(c,1.5,rc['soffit'],6,rc['low_top']-rc['soffit'],v['trim'])
  if key=='B':rect(c,1.5,rc['low_top'],6,rc['high_top']-rc['low_top'],'#AD6242')
  for x in [1.59,7.29]:rect(c,x,0,.12,rc['soffit'],v['trim'])
 c.setFillColor(HexColor('#293A36'));c.setFont('Helvetica-Bold',20)
 c.drawString(60,1050,f'{key} / {v["title"].upper()} / {side.upper()}')
 c.setFont('Helvetica',13)
 c.drawString(60,1018,'Measured schematic elevation. Opening and roof geometry govern over perspective images.')
 notes=['9.00 m house width; 3.40 m floor-to-floor; 3.00 / 2.80 m clear ceilings.',
        'Front: open 3.60 m car gate; full leaf retracted right. Car shown schematically.' if front else 'Rear: 1.00 m upper setback; 6.00 x 3.00 m canopy; only 1.00 m garden beyond.',
        'All new window/roof details are visual study assumptions, not construction specifications.']
 for i,n in enumerate(notes):c.drawString(60,95-20*i,n)
 c.save()
 env=os.environ.copy();env['FONTCONFIG_FILE']='/private/tmp/las-juntas-fonts.conf'
 subprocess.run(['/Users/antonioperez/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm','-singlefile','-r','90','-png',str(pdf),str(ROOT/f'{key.lower()}-{side}-elevation')],check=True,env=env)

if __name__=='__main__':
 checks=verify();(ROOT/'study-geometry.json').write_text(json.dumps({'common':common,'variants':variants,'checks':checks},indent=2)+'\n')
 for k in variants:
  for side in ['front','rear']:guide(k,side)
 print(json.dumps({'variants':list(variants),'elevation_guides':6,'geometry_checks':len(checks)}))
