"""Concept 12 roof coordination supplement. Geometry is schematic, not a hydraulic design."""
from pathlib import Path
from math import sqrt,atan2,cos,sin,pi,isclose
import json,hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'concept-12'
D=json.loads((BASE/'selected-style-geometry.json').read_text())
for n,f in [('Regular','Arial.ttf'),('Bold','Arial Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/System/Library/Fonts/Supplemental/'+f))
W,H=landscape(A3);M=48
INK='#293A36';MUTED='#63716C';ACCENT='#A35539';PAPER='#FCFAF5';RULE='#D5D9D0';BLUE='#427C8D';PALE='#E5F0F1';CLAY='#DFC6A5';GREEN='#DAE3CE'
OUT=ROOT/'las-juntas-roof-coordination-01.pdf';C=canvas.Canvas(str(OUT),pagesize=(W,H))
C.setTitle('Las Juntas | Roof drainage and junctions | Concept 12 supplement 01');C.setAuthor('Client concept study');C.setSubject('Proposed roof water paths, boundary gutter coordination and design handoff')
def text(x,y,t,size=10,color=INK,bold=False,align='left'):
 C.setFillColor(HexColor(color));C.setFont('Bold' if bold else 'Regular',size)
 getattr(C,{'left':'drawString','center':'drawCentredString','right':'drawRightString'}[align])(x,y,str(t))
def para(x,top,width,t,size=10,color=INK):
 p=Paragraph(t,ParagraphStyle('body',fontName='Regular',fontSize=size,leading=size*1.4,textColor=HexColor(color)))
 _,h=p.wrap(width,1000);p.drawOn(C,x,top-h);return top-h
def line(x,y,x2,y2,color=RULE,lw=.6,dash=None):
 C.saveState();C.setStrokeColor(HexColor(color));C.setLineWidth(lw)
 if dash:C.setDash(dash)
 C.line(x,y,x2,y2);C.restoreState()
def rect(x,y,w,h,fill=None,stroke=RULE,lw=.6):
 C.saveState();C.setFillColor(HexColor(fill or PAPER));C.setStrokeColor(HexColor(stroke or PAPER));C.setLineWidth(lw);C.rect(x,y,w,h,fill=bool(fill),stroke=bool(stroke));C.restoreState()
def poly(points,fill,stroke=RULE):
 path=C.beginPath();path.moveTo(*points[0])
 for pt in points[1:]:path.lineTo(*pt)
 path.close();C.setFillColor(HexColor(fill));C.setStrokeColor(HexColor(stroke));C.setLineWidth(.7);C.drawPath(path,fill=1,stroke=1)
def arrow(x,y,x2,y2,color=BLUE,lw=1.5):
 line(x,y,x2,y2,color,lw);a=atan2(y2-y,x2-x)
 for turn in [-.45,.45]:line(x2,y2,x2-7*cos(a+turn),y2-7*sin(a+turn),color,lw)
def section(x,y,t,width):
 text(x,y,t,12,ACCENT,True);line(x,y-9,x+width,y-9);return y-28
def header(n,title,sub):
 rect(0,0,W,H,PAPER,None);text(M,H-39,'LAS JUNTAS',12,ACCENT,True);text(W-M,H-39,'CONCEPT 12 / ROOF COORDINATION 01 / 12 SEPTEMBER 2026',8.5,MUTED,align='right')
 text(M,H-78,title,26,INK,True);text(M,H-100,sub,10,MUTED)
 line(M,49,W-M,49);text(M,32,'PROPOSED COORDINATION SUPPLEMENT - NOT FOR CONSTRUCTION',8,ACCENT,True);text(W-M,32,f'{n:02d} / 03',8,MUTED,align='right')
def ft(v):return v/.3048
def dim(label,*vals):return (label,' x '.join(f'{v:.2f}' for v in vals)+' m',' x '.join(f'{ft(v):.2f}' for v in vals)+' ft')
def area(label,v):return label,f'{v:.2f} m²',f'{v/.3048**2:.2f} ft²'
def table(x,top,w,rows,headers=('Meters','Feet / reference'),rowh=25,size=9):
 splits=[x,x+w*.46,x+w*.73,x+w];text(x+8,top-10,'ITEM',7.8,MUTED,True)
 for i,t in enumerate(headers,2):text(splits[i]-8,top-10,t,8,MUTED,True,align='right')
 y=top-22
 for n,row in enumerate(rows):
  if n%2==0:rect(x,y-rowh+3,w,rowh,'#F0EADF',None)
  bottom=para(x+8,y-2,w*.46-16,row[0],size);assert bottom>=y-rowh+2,(row[0],bottom,y)
  for i,t in enumerate(row[1:],2):
   assert pdfmetrics.stringWidth(t,'Regular',size)<=w*.27-16,t
   text(splits[i]-8,y-12,t,size,align='right')
  y-=rowh
 return y
SOURCES=[
 {'name':'[1] Tejas Borja / TB-12','url':'https://tejasborja.com/teja/tb-12/','note':'The listed 30% minimum is conditional on roof length and exposure. Product example only; no tile or local supply selected.'},
 {'name':'[2] Copper Development Association / built-in gutters','url':'https://archive.copper.org/applications/architecture/arch_dhb/arch-details/gutters_downspouts/gutter_linings.php','note':'Principles for lining, support, movement and positive drainage. This supplement does not specify copper or copy its material dimensions.'},
 {'name':'[3] Copper Development Association / overflow scuppers','url':'https://archive.copper.org/applications/architecture/arch_dhb/arch-details/gutters_downspouts/scuppers.php','note':'A secondary outlet sits above normal drainage and limits water accumulation if the primary route blocks.'},
 {'name':'[4] Marley / roof maintenance','url':'https://www.marley.co.uk/support/problems-and-maintenance','note':'Marley advises against walking directly on tiles. Provide a professional access strategy appropriate to the chosen roof.'}]

def page_plan():
 header(1,'Keep roof water inside the property.', 'Recommended next detail: an inset right-side gutter, separate terrace drainage and visible emergency outlets')
 x0=84;y0=120;s=27
 def p(x,y):return x0+x*s,y0+y*s
 def r(x,y,w,h,fill=None,stroke=RULE):rect(*p(x,y),w*s,h*s,fill,stroke)
 def l(x,y,x2,y2,col=BLUE,lw=1.5,dash=None):line(*p(x,y),*p(x2,y2),col,lw,dash)
 def a(x,y,x2,y2):arrow(*p(x,y),*p(x2,y2))
 r(0,0,10,20,None,INK);r(0,16.3,10,3.7,GREEN);r(1,5.8,9,10.5,'#EDEAE1')
 r(*D['roof']['footprint_lot'],CLAY,ACCENT)
 for v in [(1,5.45,5.5,9.95),(10,5.45,5.5,9.95),(1,15.65,5.5,11.15),(10,15.65,5.5,11.15),(5.5,9.95,5.5,11.15)]:l(*v,ACCENT,.7)
 r(*D['rear_canopy']['footprint_lot'],CLAY,ACCENT);r(*D['front_canopy']['footprint_lot'],CLAY,ACCENT)
 r(1.8,.55,1.85,4.8,'#CFD8D5',INK)
 text(*p(2.73,2.8),'CAR',8,MUTED,align='center');text(*p(6.7,2.6),'FRONT COURT',9,MUTED,align='center')
 # Colored lines indicate collection paths only. They are not gutter section widths.
 for v in [(1.1,5.55,9.85,5.55),(1.1,15.55,9.85,15.55),(1.1,5.55,1.1,15.55)]:l(*v)
 l(9.85,5.55,9.85,15.55,ACCENT,4)
 for v in [(5.5,8.4,5.5,5.8),(5.5,12.6,5.5,15.3),(3.2,10.55,1.35,10.55),(7.7,10.55,9.6,10.55),(9.85,10.3,9.85,6.8),(9.85,10.8,9.85,14.4),(1.1,10.3,1.1,6.8),(1.1,10.8,1.1,14.4)]:a(*v)
 for i,(x,y,dx,dy) in enumerate([(1.1,5.55,-.65,-.55),(9.85,5.55,.7,-.55),(1.1,15.55,-.65,.3),(9.85,15.55,.7,.3)],1):
  px,py=p(x,y);C.setFillColor(HexColor(BLUE));C.circle(px,py,4,fill=1,stroke=0);text(*p(x+dx,y+dy),'R'+str(i),8,BLUE,True,align='center')
 # Separate emergency discharge face symbols; elevations and receivers need design.
 for xx,yy,end_y,label,label_y in [(9.5,5.45,4.8,'O1',4.5),(9.5,15.65,16.15,'O2',16.45)]:
  arrow(*p(xx,yy),*p(xx,end_y),ACCENT,1.2);text(*p(10.55,label_y),label,8,ACCENT,True,align='center')
 # Rear upper outlets need a transfer over the setback to lower rear wall piers.
 for x in [1.1,9.85]:l(x,15.55,x,16.3,BLUE,1,[3,3])
 l(3.05,19.18,8.9,19.18);a(6,17.1,6,18.95);a(6,19.18,8.6,19.18)
 text(*p(8.9,19.5),'T1',8,BLUE,True,align='center');text(*p(5.8,17.4),'TERRACE',8,INK,True,align='center')
 l(4.9,5.05,6.55,5.05);text(*p(6.9,4.7),'E1',8,BLUE,True)
 text(*p(5,20.5),'10.00 m LOT / 32.81 ft',9,MUTED,align='center');text(*p(5,-.7),'STREET / OUTFALL NOT YET VERIFIED',8,MUTED,align='center')
 text(54,704,'PROPOSED COLLECTION PATHS',10,ACCENT,True)
 text(54,91,'Blue: primary collection / dots: outlet zones',8,BLUE)
 text(54,77,'Orange: boundary detail + O1/O2 overflow faces / symbols not to scale',8,ACCENT)
 x=457;w=W-x-M;y=section(x,704,'The boundary edge is the first constraint',w)
 y=para(x,y,w,'The current roof reaches lot x=10.00 m. An added outside gutter would cross the boundary. Develop a lined collection channel inside that edge, with the tile termination pulled back as needed. Its width, depth and roof support still have to be designed.',11)-16
 y=para(x,y,w,'<b>Geometry consequence:</b> a real gutter occupies space. Its reserve changes the tiled edge and may affect the hip/ridge geometry. Reconcile that detail before issuing a new roof layout; do not assume every Concept 12 roof dimension survives unchanged.',10,ACCENT)-22
 y=section(x,y,'Main roof: four collection zones',w)
 y=para(x,y,w,'R1-R4 are candidate outlet zones near the four corners. Split each long side gutter toward front and rear; the front and rear eaves feed their adjacent corners. Pipe count and capacity remain a hydraulic-design decision. O1/O2 mark candidate emergency discharge faces; exact outlet heights and receiving details are unresolved. Keep downpipes on opaque wall piers, clear of glazing, gate travel and entrances.',10)-13
 y=para(x,y,w,'R3/R4 need a supported transfer across the upper rear setback before descending at the lower rear wall. Keep this route outside the rooms and separate from the terrace roof. Locate inspection access at every concealed change of direction.',10)-22
 y=section(x,y,'Terrace, setback and entry each need collection',w)
 y=para(x,y,w,'T1 collects the terrace at its low garden edge; keep the gutter within the 6.00 x 3.00 m overall envelope. The 1.00 m upper rear setback needs its own continuous waterproofing and outlet. E1 drains the small entry shade away from the doorway. Do not dump upper-roof water onto the terrace tiles or entry path.',10)-22
 y=section(x,y,'Connect to a verified site drainage system',w)
 y=para(x,y,w,'Take the downpipes to accessible site collection points. Survey the street and floor levels, establish the permitted receiving system and check gravity fall before routing buried pipes. A connection to the street or sanitary drain is not assumed. Keep ordinary and emergency discharge inside the property until a permitted outfall is confirmed.',10)-12
 y=para(x,y,w,'Concept 12 and the original style study remain intact. This supplement proposes drainage relationships; it does not resize the roof, alter room areas or establish a final drainage installation.',9,MUTED)
 assert y>68,y
 C.showPage()

def page_junctions():
 header(2,'Resolve the edges before the tile order.', 'Schematic coordination sections / gutter widths, upstands, falls and pipe diameters are intentionally not specified')
 lw=518;rx=624
 section(M,704,'Right boundary / inset channel',lw);section(rx,704,'Rear setback / canopy junction',lw)
 # A concept section drawn as a diagram, not a construction detail.
 rect(75,402,462,232,'#F3EFE6',None)
 line(504,410,504,619,ACCENT,1,[4,3]);text(499,647,'LOT BOUNDARY',9,ACCENT,True,align='right')
 poly([(98,585),(375,469),(375,452),(98,568)],CLAY,ACCENT)
 line(98,559,376,443,BLUE,2)
 poly([(361,447),(386,447),(386,423),(477,423),(477,493),(493,493),(493,411),(372,411),(372,436),(361,436)],PALE,BLUE)
 rect(445,365,48,43,'#D6DAD2',INK)
 arrow(302,504,369,477);text(105,615,'CLAY TILE + UNDERLAY',9,INK,True)
 text(403,448,'CHANNEL',8,BLUE,True,align='center');text(493,351,'WALL / SUPPORT TO ENGINEER',8,MUTED,align='right')
 text(80,383,'PRIMARY FLOW ALONG CHANNEL TO FRONT / REAR OUTLETS',7.8,BLUE)
 y=section(M,323,'What this detail must demonstrate',lw)
 y=para(M,y,lw,'1. A continuous compatible lining, roof-underlay discharge into it, supported edges and provision for movement. Keep joints inspectable; test the lined channel before covering adjacent work. [2]',10)-12
 y=para(M,y,lw,'2. Primary outlets plus a separate overflow path positioned above normal drainage but below the level that would allow water into the building. Discharge overflow visibly on an in-lot front/rear face, away from the doorway and neighbor. Final elevations require design. [3]',10)-12
 y=para(M,y,lw,'3. Safe access to clean the full channel, outlets and roof junctions. A narrow void behind the roof is not a maintenance strategy. Detail access from the property with the roof contractor; do not assume walking directly on tiles. [4]',10)-12
 y=para(M,y,lw,'The sketch reserves a relationship, not a channel size. Structure, lining material, edge heights and water capacity remain open.',9,ACCENT)
 assert y>64,y
 # Rear longitudinal relationship using selected z levels.
 bx=675;by=378;sc=91
 def p(x,z):return bx+x*sc,by+(z-2.3)*sc
 rect(*p(0,2.3),10,2.6*sc,'#D6DAD2',INK)
 rect(*p(-.015,4.25),12,.5*sc,PALE,BLUE)
 line(*p(-.1,4.25),*p(1.3,4.25),BLUE,.8,[3,3]);text(*p(1.35,4.25),'WINDOW SILL +4.25 m',8,BLUE)
 line(*p(0,3.4),*p(1,3.4),BLUE,2);text(*p(.1,3.18),'SETBACK',8,MUTED)
 poly([p(1,3.6),p(4,2.7),p(4,2.5),p(1,3.4)],CLAY,ACCENT)
 rect(*p(3.85,2.3),.12*sc,.2*sc,'#D6DAD2',INK)
 arrow(*p(1.5,3.52),*p(3.3,2.98));text(*p(1.1,3.82),'HIGH TILE +3.60 m',8,ACCENT)
 text(*p(1.6,2.38),'OUTER SOFFIT +2.50 m',7.8,MUTED)
 text(684,639,'WINDOW / WALL FLASHING TO COORDINATE',8,MUTED)
 line(*p(0,2.15),*p(1,2.15),MUTED,.6);text(*p(.5,1.98),'1.00 m / 3.28 ft',8,MUTED,align='center')
 line(*p(1,2.15),*p(4,2.15),MUTED,.6);text(*p(2.5,1.98),'3.00 m / 9.84 ft CANOPY',8,MUTED,align='center')
 y=section(rx,323,'Keep the water paths independent',lw)
 y=para(rx,y,lw,'The upper roof ends above the 1.00 m rear setback. Waterproof the entire setback, including the portion below the upper eave, and carry the membrane into a flashed junction at the terrace attachment. The canopy high edge is 0.20 m above the +3.40 m floor datum; its actual support and wall termination need a section.',10)-12
 y=para(rx,y,lw,'The selected canopy top at +3.60 m leaves 0.65 m below the upper window sill. That is a geometric difference, not a verified flashing or access clearance. Keep upper-roof downpipe discharge in a pipe through the transfer, rather than spilling across this junction.',10)-12
 y=para(rx,y,lw,'Provide a low-edge terrace gutter with an inspectable outlet at an outer post zone. Coordinate its depth, beam/soffit and tile edge while retaining the 2.50 m outer clear soffit and the 0.70 m strip beyond the canopy.',10)-12
 y=para(rx,y,lw,'Tile slope check: 30% is about 16.7 degrees, not 30 degrees. The chosen tile assembly must suit the local exposure and roof lengths. [1]',9,ACCENT)
 assert y>64,y
 C.showPage()

def page_handoff():
 header(3,'Give the designer quantities and decisions.', 'Baseline Concept 12 quantities before any gutter inset / no product order, pipe sizing or construction budget established')
 lw=518;rx=624;y=section(M,704,'Retained dimensional basis',lw)
 y=table(M,y,lw,[dim('Main roof / width x depth',9,10.2),('Main roof / eave, ridge','6.60 / 7.95 m','21.65 / 26.08 ft'),dim('Rear setback / depth',1),dim('Terrace roof / width x depth',6,3),dim('Strip beyond canopy',.7),dim('Entry shade / width x depth',1.8,.8)],rowh=24,size=8.8)-17
 y=section(M,y,'Horizontal roof areas for catchment review',lw)
 y=table(M,y,lw,[area('Main / front hip',20.25),area('Main / rear hip',20.25),area('Main / each side plane',25.65),area('Main roof / total',91.8),area('Terrace roof',18)],headers=('Square meters','Square feet / ref.'),rowh=24,size=8.8)-12
 y=para(M,y,lw,'Main total: 20.25 + 20.25 + 2 x 25.65 = 91.80 m². Recalculate areas when the inset gutter and roof edges are resolved. The setback and entry shade also need drainage; the designer must account for overlapping coverage and any upstream pipe contributions.',9,MUTED)-18
 y=section(M,y,'Tile-surface reference, excluding laps / waste',lw)
 y=table(M,y,lw,[area('Main at 30% slope',91.8*sqrt(1.09)),area('Terrace at 30% slope',18*sqrt(1.09))],headers=('Square meters','Square feet / ref.'),rowh=24,size=8.8)-10
 y=para(M,y,lw,'Geometric area only, using horizontal area x sqrt(1 + 0.30²). Not order quantities; hips, ridges, cuts, laps, wastage and the revised gutter geometry remain to be measured.',8.8,MUTED)
 assert y>68,y
 y=section(rx,704,'Issue this scope for coordinated design and pricing',lw)
 tasks=[('Roof contractor + architect','Confirm the actual clay tile, minimum pitch for local exposure, fixing, underlay, ventilation, roof access and warranties. Price the complete roof assembly, not tiles alone.'),('Structural engineer','Resolve roof and gutter supports, wet and maintenance loads, wind attachment, corrosion protection and the terrace junction. Keep the clear room and terrace heights coordinated.'),('Drainage designer','Use an accepted local rainfall basis and actual contributing areas. Size gutters, primary and overflow outlets, downpipes and site drains; check slopes, blockage cases and the final receiving system.'),('Architect + site survey','Locate pipes and cleanouts on opaque piers, review the rear setback transfer, and confirm clear routes at the gate, entry and side passage. Establish property and street levels.'),('Pricing return','Separate main roof, terrace roof, inset gutter, external gutters, primary/overflow outlets, pipes/cleanouts, waterproofed setback, safe access, site connection and testing. The MXN 4 million target remains unpriced.')]
 for title,body in tasks:
  text(rx,y,title,10,INK,True);y=para(rx,y-13,lw,body,9.4)-13
 y=section(rx,y,'Reference principles / not local product specifications',lw)
 for source in SOURCES:
  text(rx,y,source['name'],8.8,ACCENT,True);C.linkURL(source['url'],(rx,y-2,rx+lw,y+10),relative=0)
  y=para(rx,y-12,lw,source['note'],8.3,MUTED)-10
 assert y>68,y
 C.showPage()

if __name__=='__main__':
 assert isclose(20.25*2+25.65*2,9*10.2)
 assert D['roof']['footprint_lot']==[1,5.45,9,10.2]
 assert isclose(D['rear_openings']['upper_primary_window'][1]-D['rear_canopy']['high_top'],.65)
 page_plan();page_junctions();page_handoff();C.save()
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.iterdir() if p.is_file()}
 record={'basis':'Concept 12, unchanged','status':'Proposed coordination only; roof dimension changes not adopted','sources':SOURCES,'baseline_concept12_sha256':before,'catchment_baseline_m2':{'main_front':20.25,'main_rear':20.25,'each_main_side':25.65,'main_total':91.8,'terrace':18},'sloped_tile_surface_m2':{'main':91.8*sqrt(1.09),'terrace':18*sqrt(1.09)},'not_sized':['inset gutter width/depth','gutter slopes','outlet and overflow dimensions','downpipe sizes and exact paths','underground system and final discharge connection']}
 (ROOT/'coordination-record.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps({'pdf':str(OUT),'pages':3,'main_tile_surface_m2':record['sloped_tile_surface_m2']['main']}))
