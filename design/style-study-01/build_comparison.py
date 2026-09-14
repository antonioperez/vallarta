"""Editable five-page A3 comparison. All geometry comes from study-geometry.json."""
from pathlib import Path
import json, hashlib, zipfile
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT=Path(__file__).resolve().parent
D=json.loads((ROOT/'study-geometry.json').read_text());COMMON=D['common'];V=D['variants']
OUT=ROOT/'las-juntas-style-study-01.pdf'
W,H=landscape(A3);M=48;CW=W-2*M
PAPER='#FCFAF5';INK='#293A36';MUTED='#66716B';ACCENT='#A35539';RULE='#D6D8CF';PALE='#F1EBDD'
pdfmetrics.registerFont(TTFont('HouseRegular','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('HouseBold','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
C=canvas.Canvas(str(OUT),pagesize=(W,H))
C.setTitle('Las Juntas | Three local architectural directions | Style study 01')
C.setAuthor('Client concept study');C.setSubject('Three appearance alternatives based on Concept 10; schematic dimensions and tradeoffs')
def ft(m):return m/.3048
def text(x,y,t,size=10,color=INK,bold=False,align='left'):
 C.setFillColor(HexColor(color));C.setFont('HouseBold' if bold else 'HouseRegular',size)
 getattr(C,{'left':'drawString','right':'drawRightString','center':'drawCentredString'}[align])(x,y,t)
def para(x,top,width,t,size=9,color=INK,leading=None):
 p=Paragraph(t,ParagraphStyle('body',fontName='HouseRegular',fontSize=size,leading=leading or size*1.4,textColor=HexColor(color)))
 _,h=p.wrap(width,1200);p.drawOn(C,x,top-h);return top-h
def line(x,y,x2,y2,color=RULE,lw=.7):
 C.setStrokeColor(HexColor(color));C.setLineWidth(lw);C.line(x,y,x2,y2)
def box(x,y,w,h,fill,stroke=None):
 C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(stroke or fill));C.rect(x,y,w,h,fill=1,stroke=bool(stroke))
def header(n,title,subtitle):
 box(0,0,W,H,PAPER)
 text(M,H-39,'LAS JUNTAS',12,ACCENT,True)
 text(W-M,H-39,'STYLE STUDY 01  /  CONCEPT 10 BASIS  /  12 SEPTEMBER 2026',8.5,MUTED,align='right')
 text(M,H-78,title,28,INK,True);text(M,H-99,subtitle,10,MUTED)
 line(M,49,W-M,49);text(M,32,'SCHEMATIC APPEARANCE STUDY - NOT FOR CONSTRUCTION OR PERMIT',8,ACCENT,True)
 text(W-M,32,f'{n:02d} / 05',8,MUTED,align='right')
def section(x,y,t,w):
 text(x,y,t,10,ACCENT,True);line(x,y-8,x+w,y-8);return y-23
def row(label,*values):
 return [label,' x '.join(f'{v:.2f}' for v in values)+' m',' x '.join(f'{ft(v):.2f}' for v in values)+' ft']
def pair(label,a,b):return [label,f'{a:.2f} / {b:.2f} m',f'{ft(a):.2f} / {ft(b):.2f} ft']
def table(x,top,width,rows,rowh=20,size=8.2,label_fraction=.46):
 xs=[x,x+width*label_fraction,x+width*(label_fraction+(1-label_fraction)/2),x+width]
 text(x+8,top-11,'ITEM',7.6,MUTED,True)
 text(xs[2]-8,top-11,'Meters',7.6,MUTED,True,align='right')
 text(xs[3]-8,top-11,'Feet / reference',7.6,MUTED,True,align='right')
 y=top-21;line(x,y,x+width,y)
 for i,r in enumerate(rows):
  if i%2==0:box(x,y-rowh,width,rowh,PALE)
  text(x+8,y-rowh/2-3,r[0],size)
  text(xs[2]-8,y-rowh/2-3,r[1],size,align='right')
  text(xs[3]-8,y-rowh/2-3,r[2],size,align='right')
  # Report text overflow before an unreadable PDF can be delivered.
  assert pdfmetrics.stringWidth(r[0],'HouseRegular',size)<xs[1]-x-12,r[0]
  for j in [1,2]:assert pdfmetrics.stringWidth(r[j],'HouseRegular',size)<xs[j+1]-xs[j]-12,r[j]
  y-=rowh
 return y
def photo(filename,x,y,size):
 ir=ImageReader(str(ROOT/filename));C.drawImage(ir,x,y,size,size,preserveAspectRatio=True,anchor='c',mask='auto')

def elevation(key,side,x,y,scale=21):
 v=V[key];front=side=='front';x0=1 if front else .5
 def r(a,z,w,h,fill):box(x+a*scale,y+z*scale,w*scale,h*scale,fill)
 def p(pts,fill):
  path=C.beginPath();path.moveTo(x+pts[0][0]*scale,y+pts[0][1]*scale)
  for a,z in pts[1:]:path.lineTo(x+a*scale,y+z*scale)
  path.close();C.setFillColor(HexColor(fill));C.drawPath(path,fill=1,stroke=0)
 r(x0,0,9,v['roof']['main_top'],v['color'])
 if key=='B':p([(x0,6.60),(x0+4.5,7.95),(x0+9,6.60)],'#A65A3D')
 if key=='C' and front:r(7.25,6.65,2.75,.45,v['color'])
 # Dashed floor line is a datum, not an additional facade joint.
 C.saveState();C.setDash(2,2);line(x+x0*scale,y+3.4*scale,x+(x0+9)*scale,y+3.4*scale,'#998F7D',.5);C.restoreState()
 for name,(a,z,w,h) in (v['front_openings'] if front else COMMON['rear_openings']).items():
  if not front:a+=.5
  r(a,z,w,h,'#9DAFAE' if name!='entry' else '#91633E')
 if front:
  fc=v['front_canopy']
  if fc:r(fc['footprint_lot'][0],fc['soffit'],fc['footprint_lot'][2],fc['top']-fc['soffit'],v['trim'])
 else:
  rc=v['rear_canopy'];r(1.5,rc['soffit'],6,rc['high_top']-rc['soffit'],'#A65A3D' if key=='B' else v['trim'])
  for a in [1.59,7.29]:r(a,0,.12,rc['soffit'],v['trim'])
 line(x+x0*scale,y,x+(x0+9)*scale,y,INK,.5)
 text(x+(x0+4.5)*scale,y-14,side.upper()+' / 9.00 m',7.3,MUTED,align='center')

def overview():
 header(1,'Three local directions. One house.',
        'A warm contemporary lead, a traditional Vallarta alternative and a sculptural study / Concept 10 preserved')
 cardw=(CW-36)/3;imagey=332
 summaries={
 'A':'A horizontal bathroom window and shaded entrance organize the front. Ivory plaster, bronze and timber keep the familiar warmth.',
 'B':'A hipped clay roof and narrow stair windows give the strongest traditional character. Roof tiles carry through to the terrace.',
 'C':'A stepped stair parapet and rounded entrance create a stronger silhouette. Sand-gray plaster and deeper reveals keep the palette restrained.'}
 for i,(k,v) in enumerate(V.items()):
  x=M+i*(cardw+18)
  text(x,H-133,k+' / '+v['title'],12,INK,True)
  photo(k.lower()+'-front.png',x,imagey,cardw)
  y=para(x,imagey-12,cardw,summaries[k],9.3)
  for j,color in enumerate([v['color'],v['trim'],v['accent']]):box(x+j*38,y-21,32,8,color)
  text(x+124,y-20,'PALETTE / ILLUSTRATIVE',7.5,MUTED)
 y=section(M,221,'RETAINED BASIS',526)
 table(M,y,526,[row('Lot / width x depth',10,20),pair('Clear ceilings / ground, upper',3,2.8),row('Finished floor to finished floor',3.4),pair('Court depth / car length',5.5,4.5),row('Vehicle gate / clear opening',3.6)],rowh=21,size=8.3)
 x=622;y=section(x,221,'RECOMMENDATION / A',W-x-M)
 y=para(x,y,W-x-M,'<b>Develop A first.</b> It gives the facade a clearer composition while staying closest to the established flat-roof building. B is the traditional alternative; C is the more sculptural option.',10)-12
 y=para(x,y,W-x-M,'The room layout, kitchen, two full bathrooms, stair and complete sliding gate remain the basis. New openings, roof forms and facade details are proposals for coordination.',8.8,MUTED)-10
 para(x,y,W-x-M,'<b>Budget:</b> the MXN 4 million working allocation remains unpriced. None of these alternatives has a verified construction cost.',8.8,MUTED)
 C.showPage()

def dimensions(key):
 v=V[key];op=v['front_openings'];gs=op['ground_stair'];us=op['upper_stair'];roof=v['roof'];rc=v['rear_canopy']
 bath=row('Upper bathroom / opening',3.1,.55) if key=='A' else ['Upper bath / two openings','0.70 x 0.70 / 0.90 x 0.70 m','2.30 x 2.30 / 2.95 x 2.30 ft']
 return [row('Each stair opening / W x H',gs[2],gs[3]),pair('Stair sills / ground, upper',gs[1],us[1]),bath,
 row('Main roof edge / eave level',roof['main_top']),row('Highest roof / ridge level',roof['highest_top']),
 row('Highest roof above upper ceiling',roof['highest_top']-6.2),pair('Terrace roof / low, high top',rc['low_top'],rc['high_top']),
 row('Terrace outer clear soffit',rc['soffit']),row('Entry shade / projection',v['front_canopy']['footprint_lot'][3] if v['front_canopy'] else 0)]

def variant_page(key,n):
 v=V[key];header(n,key+' / '+v['title'],v['subtitle'])
 size=380;gap=28;left=(W-2*size-gap)/2;bottom=H-139-size
 for i,side in enumerate(['front','rear']):
  x=left+i*(size+gap);text(x,bottom+size+10,'STREET / FRONT COURT' if side=='front' else 'GARDEN / COVERED TERRACE',8.5,ACCENT,True)
  photo(key.lower()+'-'+side+'.png',x,bottom,size)
 y=para(M,bottom-11,CW,v['notes'][0]+' '+v['notes'][1],8.5,MUTED,leading=11.5)-15
 y=min(y,286)
 ty=section(M,y,'PROPOSED DIMENSIONS / METRIC VALUES GOVERN',558)
 end=table(M,ty,558,dimensions(key),rowh=19,size=7.55,label_fraction=.43)
 assert end>66,('table footer',key,end)
 x=647;rw=W-x-M;dy=section(x,y,'MEASURED ELEVATIONS / SAME FLOOR LEVELS',rw)
 scale=18.0;ey=dy-155
 elevation(key,'front',x-5,ey,scale);elevation(key,'rear',x+231,ey,scale)
 para(x,ey-27,rw,'Dashed datum: upper finished floor +3.40 m. Roof and window dimensions are schematic; the perspectives communicate character, not exact construction geometry.',7.6,MUTED,leading=10)
 C.showPage()

def references():
 header(5,'What each direction asks of the build.',
        'Relative design judgments, local references and the decisions still needed before pricing or construction')
 widths=[55,352,343,CW-750];xs=[M]
 for w in widths:xs.append(xs[-1]+w)
 top=H-140
 for i,t in enumerate(['','CONSTRUCTION / MAINTENANCE','PRIVACY / SHADING','DESIGN POSITION']):text(xs[i]+9,top,t,8.6,ACCENT,True)
 line(M,top-11,W-M,top-11);y=top-11
 construction={
 'A':'Coordinate the wide bathroom lintel, three glazed modules and simple entry canopy. Provide drainage at the flat roofs and window reveals; protect the timber soffits and plan access for repainting and seal maintenance.',
 'B':'Price the added hip roof and terrace roof support, tile fixings and rainwater details. The study assumes a 30% roof slope; compatibility with the chosen tile system is unverified. Allow inspection of tiles, flashings and roof junctions.',
 'C':'Price the curved entrance, deeper reveals and stepped coping separately. Shape these as exterior details so the rooms retain their areas. Detail drip edges and repairable plaster finishes; structural concrete is not the specified finish.'}
 privacy={
 'A':'High obscure bathroom glass limits direct views. Recessed stair glazing and the entry canopy add localized shade; effective solar control still depends on orientation and sun angles.',
 'B':'Keep obscure bathroom glass and independent narrow stair windows. Front/rear roof eaves provide some shade; flush side edges require rainwater details within the lot. The lower terrace soffit changes its feel.',
 'C':'Taller stair glass needs coordinated sill guarding, inward sash clearance and cleaning reach. Deep reveals shape light, but do not establish a solar or acoustic rating.'}
 position={'A':'1 / LEADING CANDIDATE\nBest continuity with the established building. Develop the entry and window proportions first.',
 'B':'2 / TRADITIONAL ALTERNATIVE\nMost recognizable local roof character. Accept the additional roof work deliberately.',
 'C':'3 / SCULPTURAL ALTERNATIVE\nStrongest silhouette and custom plaster details. Keep the finish warm and restrained.'}
 for i,k in enumerate(V):
  rowh=107
  if i%2==0:box(M,y-rowh,CW,rowh,PALE)
  text(M+12,y-24,k,19,ACCENT,True)
  for j,t in enumerate([construction[k],privacy[k],position[k].replace('\n','<br/><br/>')],1):
   bottom=para(xs[j]+9,y-11,widths[j]-18,t,9,leading=12.3);assert bottom>=y-rowh+7,(k,j,bottom,y-rowh)
  y-=rowh;line(M,y,W-M,y)
 y-=26;yy=section(M,y,'LOCAL REFERENCE POINTS',CW)
 cardw=(CW-38)/3
 sourced={
 'A':'Bernal Architecture Studio describes Casa Los Mangos in Bucerias through simple white plaster volumes, shaded access and timber. This study adapts that material and shade vocabulary to the smaller house.',
 'B':'Puerto Vallarta Tourism Board identifies white walls, colored trim and reddish tiles as characteristic of the historic center. These are visual references here; downtown heritage requirements are not assumed to apply to Las Juntas.',
 'C':'HW Studio describes Casa Tao in Puerto Vallarta through controlled openings, shade and an inward-looking composition. This study borrows that restraint without copying its layout or specifying its concrete structure.'}
 for i,(k,v) in enumerate(V.items()):
  x=M+i*(cardw+19);text(x,yy,k+' / '+v['source']['title'].split(' / ')[0],11,INK,True)
  bottom=para(x,yy-16,cardw,sourced[k],9,leading=12.5)
  para(x,bottom-10,cardw,'<link href="'+v['source']['url']+'" color="'+ACCENT+'">Open the source reference</link>',9)
 y=177;line(M,y,W-M,y)
 para(M,y-15,526,'<b>Retained geometry:</b> ground envelope 9.00 x 10.50 m; upper 9.00 x 9.50 m; upper rear setback 1.00 m; terrace 6.00 x 3.00 m. House floor area remains 171.92 m², plus the separate 18.00 m² terrace. The 3.80 m sliding leaf and 4.05 x 0.45 m sliding reserve remain intact.',9,leading=12.5)
 para(622,y-15,W-622-M,'<b>Before adoption:</b> coordinate structure, selected glazing and operating hardware, stair guards, weatherproofing, roof drainage, ventilation and measured noise. No acoustic, thermal, structural or code performance is certified by these images. Obtain itemized prices before treating any version as within budget.',9,leading=12.5)
 text(M,68,'All z levels reference ground finished floor. 1 ft = 0.3048 m exactly; feet are rounded references. Concept 10 remains the adopted planning basis.',7.8,MUTED)
 C.showPage()

def brief():
 lines=['# Las Juntas / style study 01','',
 'Three appearance alternatives, 12 September 2026. Concept 10 is preserved. This is a separate comparison; no alternative changes the adopted floor plan.','',
 'Recommendation: develop A first, compare B for traditional roof character and C for a stronger sculptural composition.','',
 '## Retained basis','',
 '| Item | Meters | Feet / reference |','|---|---:|---:|']
 for r in [row('Lot',10,20),row('Ground envelope',9,10.5),row('Upper envelope',9,9.5),row('Terrace',6,3),row('Upper rear setback',1),row('Ground clear ceiling',3),row('Upper clear ceiling',2.8),row('Floor to floor',3.4),row('Court depth',5.5),row('Car length',4.5),row('Vehicle gate clear opening',3.6),row('Moving leaf length',3.8),row('Gate sliding reserve',4.05,.45)]:lines.append('| '+' | '.join(r)+' |')
 lines+=['','Room areas, kitchen coordinates, bathrooms and stairs are unchanged. Ground finished floor is a relative datum; actual grade is not established. Roof forms, slopes, openings and details below are proposals only.','']
 for k,v in V.items():
  lines+=['## '+k+' / '+v['title'],'',v['subtitle'],'']+['- '+n for n in v['notes']]+['',v['tradeoff'],'',
  '| Item | Meters | Feet / reference |','|---|---:|---:|']
  lines+=['| '+' | '.join(r)+' |' for r in dimensions(k)]
  lines+=['','### Front opening schedule','',
  'Front x uses lot coordinates from street-left; z is above ground finished floor. All new sill/head levels are schematic.','',
  '| Opening | x / z, meters | Width x height, meters | Width x height, feet |','|---|---:|---:|---:|']
  for name,(x,z,w,h) in v['front_openings'].items():lines.append(f'| {name} | {x:.3f} / {z:.2f} | {w:.2f} x {h:.2f} | {ft(w):.2f} x {ft(h):.2f} |')
  lines+=['','Reference: ['+v['source']['title']+']('+v['source']['url']+').','']
 lines+=['## Coordination and limitations','',
 'All bathroom windows use obscure glazing. High sill levels alone do not guarantee privacy. Window sashes, mirrors, safe glass, stair guards and cleaning access need product-level coordination. No front celosia screen is included. Floor and terrace tiles remain.',
 '', 'All roof footprints stay inside the lot. B has no side eave projection; the main roof extends 0.35 m only at front and rear. Both B roof slopes are 0.30 rise/run, pending tile-system compatibility. C has a raised parapet over the front stair zone only, hidden behind the main rear roofline from the low garden view. Roof assembly depths, supports and drainage remain unengineered.',
 '', 'Canopy columns are reserved at the same outer terrace positions; images are illustrative and do not specify member sections. Front entrance details have no ground columns and stay outside the car footprint. The complete single gate leaf still slides right behind the fixed fence.',
 '', 'The MXN 4 million working allocation remains unpriced. No alternative has verified acoustic, thermal, structural or code performance. Seek itemized quotations after a preferred direction is selected.',
 '', '## Files','',
 'Final images: a-front.png, a-rear.png, b-front.png, b-rear.png, c-front.png, c-rear.png. The six-image archive contains only these final views. The five-page comparison is las-juntas-style-study-01.pdf. Editable geometry, elevation references and saved prompts accompany it.',
 '', '## Verification basis','']+['- '+s for s in D['checks']]
 lines+=['','The final images are inspected for the intended openings, roof form, gate clearance and rear orientation. Elevations and dimension tables govern exact geometry; perspective views do not establish measured dimensions. The PDF is rendered and inspected before delivery.','']
 (ROOT/'brief.md').write_text('\n'.join(lines))

if __name__=='__main__':
 for filename,digest in COMMON['baseline_sha256'].items():
  assert hashlib.sha256((ROOT.parent/'concept-10'/filename).read_bytes()).hexdigest()==digest,filename
 overview()
 for i,k in enumerate(V,2):variant_page(k,i)
 references();C.save();brief()
 with zipfile.ZipFile(ROOT/'six-style-views.zip','w',zipfile.ZIP_DEFLATED) as z:
  for k in V:
   for side in ['front','rear']:
    name=k.lower()+'-'+side+'.png';z.write(ROOT/name,name)
 print(json.dumps({'pdf':str(OUT),'pages':5,'final_images':6,'baseline':'Concept 10 unchanged'}))
