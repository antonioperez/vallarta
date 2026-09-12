"""Deterministic, editable schematic study. Units in plan geometry are meters."""
from pathlib import Path
from math import cos, sin, radians, isclose
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
pdfmetrics.registerFont(TTFont('HouseRegular', '/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('HouseBold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
OUT = ROOT / 'las-juntas-concept-01.pdf'
W, H = landscape(A3)
INK = HexColor('#293A36')
MUTED = HexColor('#626C66')
PAPER = HexColor('#FCFAF5')
FLOOR = HexColor('#F4EEE3')
TERRACOTTA = HexColor('#A35539')
GREEN = HexColor('#CDD8BF')
SAGE = HexColor('#6F8466')
WOOD = HexColor('#D7BE9A')
WATER = HexColor('#D8E6E7')
RULE = HexColor('#D4D7CE')
S = 1000 / 100 * 72 / 25.4  # 1:100 on A3, printed at 100 percent
c = canvas.Canvas(str(OUT), pagesize=(W, H))
c.setTitle('Las Juntas | Vacation house | Concept 01')
c.setAuthor('Prepared with Codex - client concept study')
c.setSubject('Furnished schematic plans, area reconciliation, budget allowances and appearance concept')

rooms = [
    ('G1', 'Queen guest bedroom', 'Ground', .2, .2, 3.6, 4.1),
    ('G2', 'Shared full bathroom', 'Ground', 1.95, 4.45, 1.85, 2.3),
    ('G3', 'Laundry / utility', 'Ground', .2, 4.45, 1.6, 2.3),
    ('G4', 'Kitchen / transition zone', 'Ground', 3.95, 4.65, 4.85, 2.1),
    ('G5', 'Living / dining zone', 'Ground', .2, 6.9, 8.6, 3.4),
    ('G6', 'Entrance circulation', 'Ground', 3.95, .2, 2.2, 4.3),
    ('G7', 'Stair zone, including landings', 'Ground', 6.3, .2, 2.5, 4.3),
    ('U1', 'Two-double guest bedroom', 'Upper', .2, .2, 4.6, 4.6),
    ('U2', 'Guest private bathroom', 'Upper', .2, 4.95, 2, 2.3),
    ('U3', 'Primary private bathroom', 'Upper', 2.35, 4.95, 2, 2.3),
    ('U4', 'Primary dressing / storage', 'Upper', .2, 7.4, 4.15, 1.9),
    ('U5', 'Primary bedroom, main rectangle', 'Upper', 4.5, 4.95, 4.3, 4.35),
    ('U6', 'Hall', 'Upper', 4.95, .2, 1.2, 4.3),
    ('U7', 'Upper arrival landing', 'Upper', 6.3, .2, 2.5, 1),
]
void = 2.25 * 3.29
areas = {'lot': 200, 'ground': 94.5, 'upper_envelope': 85.5,
         'upper_stair_void': void, 'upper_floor': 85.5 - void,
         'combined_floor': 180 - void, 'covered_terrace': 18,
         'front_zone': 55, 'side_passage': 10.5, 'rear_zone': 40}

def txt(x, y, text, size=10, color=INK, bold=False, align='left'):
    c.setFillColor(color)
    c.setFont('HouseBold' if bold else 'HouseRegular', size)
    getattr(c, {'left': 'drawString', 'center': 'drawCentredString', 'right': 'drawRightString'}[align])(x, y, str(text))

def para(x, top, width, text, size=10, color=INK, leading=None):
    p = Paragraph(text, ParagraphStyle('p', fontName='HouseRegular', fontSize=size,
                  leading=leading or size*1.45, textColor=color, spaceAfter=0))
    _, h = p.wrap(width, 1000)
    p.drawOn(c, x, top-h)
    return top-h

def line(x1, y1, x2, y2, color=RULE, width=.7, dash=None):
    c.saveState(); c.setStrokeColor(color); c.setLineWidth(width)
    if dash: c.setDash(dash)
    c.line(x1, y1, x2, y2); c.restoreState()

def header(sheet, title, subtitle):
    c.setFillColor(PAPER); c.rect(0, 0, W, H, fill=1, stroke=0)
    txt(48, H-40, 'LAS JUNTAS', 12, TERRACOTTA, True)
    txt(W-48, H-40, 'CONCEPT 01  /  12 SEPTEMBER 2026', 9, MUTED, align='right')
    txt(48, H-77, title, 26, bold=True)
    txt(48, H-98, subtitle, 10, MUTED)
    line(48, 49, W-48, 49)
    txt(48, 32, 'SCHEMATIC STUDY - NOT FOR CONSTRUCTION OR PERMIT', 8, TERRACOTTA, True)
    txt(W-48, 32, f'{sheet:02d} / 03', 8, MUTED, align='right')

def section(x, y, title, width):
    txt(x, y, title, 12, TERRACOTTA, True)
    line(x, y-9, x+width, y-9)
    return y-27

class Plan:
    def __init__(self, x, y, scale=S, bx=0, by=0):
        self.x, self.y, self.s, self.bx, self.by = x, y, scale, bx, by
    def p(self, x, y): return (self.x+(x+self.bx)*self.s, self.y+(y+self.by)*self.s)
    def rect(self, x, y, w, h, fill=FLOOR, stroke=RULE, lw=.5):
        px,py=self.p(x,y); c.saveState(); c.setFillColor(fill or PAPER)
        c.setStrokeColor(stroke or PAPER); c.setLineWidth(lw)
        c.rect(px,py,w*self.s,h*self.s,fill=int(fill is not None),stroke=int(stroke is not None)); c.restoreState()
    def line(self,x1,y1,x2,y2,color=INK,lw=.6,dash=None):
        line(*self.p(x1,y1),*self.p(x2,y2),color,lw,dash)
    def text(self,x,y,t,size=8,color=INK,bold=False,align='center'):
        txt(*self.p(x,y),t,size,color,bold,align)
    def circle(self,x,y,r,fill=GREEN,stroke=SAGE,lw=.5):
        c.saveState(); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(lw)
        c.circle(*self.p(x,y),r*self.s,fill=1,stroke=1); c.restoreState()
    def wall(self,x,y,w,h): self.rect(x,y,w,h,INK,None)
    def window(self,x,y,w,h):
        self.rect(x,y,w,h,WATER,None)
        if w>h:
            self.line(x,y+h*.33,x+w,y+h*.33,SAGE,.6); self.line(x,y+h*.67,x+w,y+h*.67,SAGE,.6)
        else:
            self.line(x+w*.33,y,x+w*.33,y+h,SAGE,.6); self.line(x+w*.67,y,x+w*.67,y+h,SAGE,.6)
    def door(self,x,y,w,wall='v',into='left'):
        if wall=='v':
            self.rect(x-.1,y,.2,w,FLOOR,None)
            angle = 90 if into=='left' else 0
            end = (x-w,y) if into=='left' else (x+w,y+w)
            hinge=(x,y) if into=='left' else (x,y+w)
        else:
            self.rect(x,y-.1,w,.2,FLOOR,None)
            hinge=(x,y); end=(x,y+w); angle=0
        self.line(*hinge,*end,TERRACOTTA,.6)
        hx,hy=self.p(*hinge)
        c.saveState(); c.setStrokeColor(TERRACOTTA); c.setLineWidth(.4)
        c.arc(hx-w*self.s,hy-w*self.s,hx+w*self.s,hy+w*self.s,startAng=angle,extent=90); c.restoreState()
    def sliding(self,x,y,w,vertical=False):
        if vertical:
            self.rect(x-.1,y,.2,w,FLOOR,None)
            self.line(x-.04,y,x-.04,y+w,TERRACOTTA,1)
            self.line(x+.1,y+w,x+.1,y+2*w,TERRACOTTA,.45,[2,2])
        else:
            self.window(x,y-.1,w,.2)
            self.line(x,y,x+w*.55,y,TERRACOTTA,1)
    def bed(self,x,y,w,h,label,head='top'):
        self.rect(x,y,w,h,WOOD,INK,.55)
        if head=='top':
            self.rect(x+.09,y+h-.47,(w-.27)/2,.35,PAPER,INK,.35)
            self.rect(x+.18+(w-.27)/2,y+h-.47,(w-.27)/2,.35,PAPER,INK,.35)
            self.line(x,y+h-.6,x+w,y+h-.6,INK,.4)
        elif head=='left':
            self.rect(x+.1,y+.12,.38,(h-.36)/2,PAPER,INK,.35)
            self.rect(x+.1,y+.24+(h-.36)/2,.38,(h-.36)/2,PAPER,INK,.35)
            self.line(x+.62,y,x+.62,y+h,INK,.4)
        else:
            self.rect(x+w-.48,y+.12,.38,(h-.36)/2,PAPER,INK,.35)
            self.rect(x+w-.48,y+.24+(h-.36)/2,.38,(h-.36)/2,PAPER,INK,.35)
            self.line(x+w-.62,y,x+w-.62,y+h,INK,.4)
        self.text(x+w*.55,y+h*.43,label,6.5)
    def table(self,x,y,w=2.2,h=.95):
        self.rect(x,y,w,h,WOOD,INK,.5)
        for xx in [x+.12,x+w/2-.225,x+w-.57]:
            self.rect(xx,y-.55,.45,.43,PAPER,INK,.45)
            self.rect(xx,y+h+.12,.45,.43,PAPER,INK,.45)
        self.rect(x-.55,y+h/2-.225,.43,.45,PAPER,INK,.45)
        self.rect(x+w+.12,y+h/2-.225,.43,.45,PAPER,INK,.45)
    def bath(self,x,y,w=2,h=2.3,vanity='left'):
        self.rect(x,y,w,h,WATER,None)
        self.rect(x,y+h-1.05,.9,1.05,None,SAGE,.6)
        self.line(x,y+h-1.05,x+.9,y+h,SAGE,.35)
        self.circle(x+.45,y+h-.5,.05,PAPER,SAGE)
        self.rect(x+w-.76,y+h-.23,.6,.2,PAPER,INK,.4)
        px,py=self.p(x+w-.69,y+h-.78)
        c.saveState(); c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(.4)
        c.roundRect(px,py,.46*self.s,.57*self.s,.18*self.s,fill=1,stroke=1); c.restoreState()
        vx=x if vanity=='left' else x+w-.5
        self.rect(vx,y+.1,.5,.78,WOOD,INK,.4)
        self.rect(vx+.07,y+.22,.34,.42,PAPER,INK,.4)
    def stair(self,upper=False):
        self.rect(6.3,.2,2.5,4.3,FLOOR,RULE)
        if upper:
            self.rect(6.4,1.2,2.25,3.29,HexColor('#E4E7E0'),RULE)
        for xx in [6.4,7.6]:
            for i in range(9):
                self.line(xx,1.2+i*.28,xx+1.05,1.2+i*.28,INK,.45,[2,2] if (upper and xx==6.4) else None)
        self.line(7.5,1.2,7.5,3.44,INK,.9)
        pts=[(6.925,1.45),(6.925,3.94),(8.125,3.94),(8.125,1.45)]
        for a,b in zip(pts,pts[1:]): self.line(*a,*b,TERRACOTTA,.8)
        self.line(8.125,1.45,7.99,1.68,TERRACOTTA,.8)
        self.line(8.125,1.45,8.26,1.68,TERRACOTTA,.8)
        self.text(7.55,.64,'U7  /  ARRIVAL' if upper else 'G7  /  UP',6.4,TERRACOTTA)
    def dimh(self,x1,x2,y,label):
        self.line(x1,y,x2,y,MUTED,.45)
        for x in [x1,x2]: self.line(x-.08,y-.12,x+.08,y+.12,MUTED,.55)
        self.text((x1+x2)/2,y+.17,label,8,MUTED)
    def dimv(self,x,y1,y2,label):
        self.line(x,y1,x,y2,MUTED,.45)
        for y in [y1,y2]: self.line(x-.10,y-.1,x+.10,y+.1,MUTED,.5)
        c.saveState(); px,py=self.p(x-.13,(y1+y2)/2); c.translate(px,py); c.rotate(90)
        txt(0,0,label,8,MUTED,align='center'); c.restoreState()

def site(p, upper=False):
    p.rect(0,0,10,20,PAPER,INK,.8)
    p.rect(0,0,10,5.5,HexColor('#E9E3D7'),None)
    p.rect(0,5.5,1,10.5,HexColor('#E9E3D7'),None)
    p.rect(0,16,10,4,GREEN,None)
    p.rect(3,16,6,3,HexColor('#E3D0B5'),None)
    p.rect(1,5.5,9,10.5,HexColor('#EEECE5'),RULE)
    if not upper:
        p.table(5,17.02)
        for x in [3.15,8.85]: p.rect(x-.06,18.87,.12,.12,INK,None)
        p.text(6,19.38,'REAR GARDEN',7,SAGE,True)
        p.text(6,16.17,'18 m² COVERED TERRACE',7.1,TERRACOTTA,True)
        for x,y,r in [(1.25,18.6,.45),(1.9,19.5,.35),(.55,17,.25),(9.5,19.3,.28),(9.45,17.1,.25)]:
            p.circle(x,y,r)
        p.rect(1.1,.25,3.2,5.1,None,MUTED,.45)
        p.rect(1.8,.55,1.85,4.5,HexColor('#C6CDCA'),INK,.6)
        p.rect(1.91,3.38,1.63,.75,WATER,INK,.35)
        p.rect(1.91,1.15,1.63,.58,WATER,INK,.35)
        p.text(2.75,2.45,'1 CAR',8,INK,True)
        p.line(8.65,.2,8.65,4.0,HexColor('#C5BCA9'),.9*p.s)
        p.line(8.65,4.0,5.8,4.0,HexColor('#C5BCA9'),.9*p.s)
        p.line(5.8,4.0,5.8,5.5,HexColor('#C5BCA9'),.9*p.s)
        for x,y,r in [(5.1,1.4,.3),(6.8,2.5,.3),(9.65,4.4,.25)]: p.circle(x,y,r)
        p.line(.9,0,4.1,0,PAPER,3)
        p.line(.9,.04,4.1,.04,TERRACOTTA,1)
        p.line(4.1,.04,7.3,.04,TERRACOTTA,.55,[2,2])
        p.line(8.1,0,9.2,0,PAPER,3)
        p.text(8.65,.65,'ENTRY',6.5)
    else:
        p.text(5,2.5,'FRONT COURT BELOW',8,MUTED)
        p.text(6,17.45,'TERRACE BELOW',8,MUTED)
        p.text(5.5,15.42,'LOWER ROOF - NO TERRACE',6.7,MUTED)
    p.dimh(0,10,20.55,'10.00 m LOT')
    p.dimv(-.62,0,20,'20.00 m LOT')
    if not upper:
        p.dimv(10.65,0,5.5,'5.50 m')
        p.dimv(10.65,5.5,16,'10.50 m')
        p.dimv(10.65,16,20,'4.00 m')
    else: p.dimv(10.65,5.5,15,'9.50 m UPPER')
    p.text(5,-.52,'ALVARO OBREGON / STREET',8.5,INK,True)
    px,py=p.p(.55,10.8); c.saveState(); c.translate(px,py); c.rotate(90)
    txt(0,0,'1.0 m NOMINAL SIDE PASSAGE',6.5,MUTED,align='center'); c.restoreState()

def building(p, upper=False):
    d=9.5 if upper else 10.5
    p.rect(0,0,9,d,FLOOR,None)
    p.stair(upper)
    if upper:
        p.bath(.2,4.95,vanity='right')
        p.bath(2.35,4.95)
    else:
        p.bath(1.95,4.45,1.85)
        p.rect(.2,4.45,1.6,2.3,WATER,None)
    for wall in [(0,0,.2,d),(8.8,0,.2,d),(.2,0,8.6,.2),(.2,d-.2,8.6,.2),
                 (6.15,.2,.15,4.3),(6.3,4.5,2.5,.15)]: p.wall(*wall)
    if not upper:
        for wall in [(3.8,.2,.15,6.55),(.2,4.3,3.6,.15),(1.8,4.45,.15,2.3),(.2,6.75,3.6,.15)]: p.wall(*wall)
        p.door(3.875,.8,.9)
        p.door(3.875,4.65,.9)
        p.door(4.3,.1,1,'h')
        p.sliding(.1,4.7,.9,True)
        p.window(1.15,0,2,.2); p.window(6.8,0,1.65,.2)
        p.window(.65,10.3,2.9,.2); p.sliding(4.9,10.4,3.2)
        p.window(0,2.5,.2,1)
        p.bed(1.4,2.02,1.52,2.03,'QUEEN')
        p.rect(.2,.45,.6,1.8,WOOD,INK,.4)
        p.rect(4.1,2.6,.45,1.2,WOOD,INK,.4)
        p.rect(.35,5.95,.7,.7,PAPER,INK,.5)
        p.circle(.7,6.3,.20,WATER,INK)
        p.rect(.35,4.7,.7,.65,WOOD,INK,.4)
        p.rect(.43,4.8,.54,.43,PAPER,INK,.4)
        p.rect(5.2,4.65,.8,.72,PAPER,INK,.5)
        p.text(5.6,4.94,'FR',6.5)
        p.rect(6,4.65,2.8,.65,WOOD,INK,.5)
        p.rect(8.15,5.3,.65,1.35,WOOD,INK,.5)
        p.rect(6.35,4.76,.75,.43,PAPER,INK,.4)
        for xx in [6.53,6.89]:
            for yy in [4.87,5.08]: p.circle(xx,yy,.06,PAPER,INK)
        p.rect(8.25,5.6,.43,.65,PAPER,INK,.4)
        p.table(5.5,7.55)
        p.rect(.35,9.25,3.3,.85,WOOD,INK,.5)
        p.rect(.35,8.05,.85,1.2,WOOD,INK,.5)
        for xx in [2,3]: p.rect(xx,7.1,.75,.75,WOOD,INK,.5)
        p.rect(1.6,8.15,1.25,.55,PAPER,INK,.4)
        p.rect(1.95,6.9,1.25,.12,INK,None)
        labels=[(2,1.25,'G1  GUEST'),(2.83,5.62,'G2'),(1.35,5.63,'G3'),
                (6.75,5.92,'G4  KITCHEN'),(2.15,8.93,'G5  LIVING'),
                (6.6,9.6,'DINING / 8'),(5.15,2.15,'G6')]
    else:
        for wall in [(4.8,.2,.15,4.6),(.2,4.8,4.6,.15),(2.2,4.95,.15,2.3),
                     (4.35,4.95,.15,4.35),(.2,7.25,4.15,.15),(4.8,4.5,4,.15)]: p.wall(*wall)
        p.door(4.875,1.3,.9)
        p.door(.55,4.875,.9,'h')
        p.door(4.425,5,.9)
        p.door(5.05,4.575,.9,'h')
        p.sliding(4.425,7.5,.9,True)
        p.window(2.6,0,1.6,.2); p.window(6.8,0,1.65,.2)
        p.window(0,2.2,.2,.5); p.window(0,5.5,.2,.55)
        p.window(0,7.8,.2,.55); p.window(5.2,9.3,3.05,.2)
        p.bed(.35,.8,1.9,1.35,'DOUBLE',head='left')
        p.bed(.35,2.85,1.9,1.35,'DOUBLE',head='left')
        p.rect(4.15,2.65,.65,1.9,WOOD,INK,.4)
        p.bed(6.65,6.15,2,2,'KING',head='right')
        p.rect(8.1,5.57,.55,.48,WOOD,INK,.4)
        p.rect(8.1,8.25,.55,.48,WOOD,INK,.4)
        p.rect(.35,8.7,3.85,.6,WOOD,INK,.4)
        for x in [.99,1.63,2.27,2.91,3.55]: p.line(x,8.7,x,9.3,INK,.35)
        labels=[(3.2,3.3,'U1  GUEST'),(3.2,2.93,'4 PEOPLE'),(1.2,5.95,'U2'),
                (3.35,6.08,'U3'),(2.3,8.04,'U4  DRESSING'),(6.7,5.5,'U5  PRIMARY'),(5.55,3.2,'U6')]
    # Both levels enter the U-stair through the same front landing.
    p.rect(6.145,.25,.16,.9,FLOOR,None)
    for x,y,t in labels: p.text(x,y,t,7.2,INK,True)

def table(x,y,width,rows,col2=360,rowh=25,size=10):
    for i,(a,b) in enumerate(rows):
        if i%2==0:
            c.setFillColor(FLOOR); c.rect(x,y-rowh+6,width,rowh,fill=1,stroke=0)
        txt(x+10,y-10,a,size)
        txt(x+width-10,y-10,b,size,align='right')
        y-=rowh
    return y

def page_plans():
    header(1,'A house organized around its rear patio',
           '3 bedrooms / 3 bathrooms / 8 guests / 1 car     |     Furnished schematic, meters     |     A3 at 1:100 when printed at 100%')
    for upper,x,title in [(False,80,'01  GROUND FLOOR'),(True,481,'02  UPPER FLOOR')]:
        txt(x, H-119,title,11,INK,True)
        p=Plan(x,125); site(p,upper)
        building(Plan(x,125,bx=1,by=5.5),upper)
    x=837; width=W-x-48; y=H-139
    y=section(x,y,'The agreed brief',width)
    y=para(x,y,width,'Two floors, a downstairs queen guest room, an upstairs king primary suite, and an upstairs room with two double beds. Three full bathrooms. Warm Mexican contemporary finishes.',10)-22
    y=section(x,y,'The proposed fit',width)
    y=table(x,y,width,[('Ground floor','94.5 m²'),('Upper, stair void deducted','78.1 m²'),('Combined floor area','172.6 m²'),('Covered rear terrace, extra','18.0 m²')],rowh=26)-15
    y=para(x,y,width,'Floor areas use exterior wall faces. They include walls and circulation. The 7.4 m² upper stair opening is deducted; this is not the municipal area calculation.',9,MUTED)-20
    y=section(x,y,'Room arrangement',width)
    for title,body in [
        ('Ground / social + guest','G1 queen room; G2 shared bath; G3 laundry from the side passage; G4 L-shaped kitchen; G5 lounge and eight-place dining; G6 entry; G7 stair.'),
        ('Upper / private','U1 two-double guest room; U2 its private bath; U3 primary bath; U4 dressing/storage; U5 primary bedroom; U6 hall; U7 stair arrival.')]:
        txt(x,y,title,10,bold=True); y=para(x,y-9,width,body,9.5)-17
    y=section(x,y,'What this drawing does not fix',width)
    para(x,y,width,'Setbacks, boundary-wall permission, floor elevation, structural design and utility arrangements remain open. Front/rear orientation is schematic; no surveyed north direction is asserted.',9.5)
    # Scale bar is independent of the diagram labels.
    for i in range(5):
        c.setFillColor(INK if i%2==0 else PAPER); c.setStrokeColor(INK)
        c.rect(80+i*S,80,S,5,fill=1,stroke=1)
    txt(80,66,'0',7,MUTED); txt(80+5*S,66,'5 m',7,MUTED,align='right')
    txt(295,76,'Windows',8,MUTED); line(270,79,289,79,SAGE,2)
    txt(400,76,'Door swings',8,MUTED); line(375,79,394,79,TERRACOTTA,1)
    txt(545,76,'Furniture shown to scale',8,MUTED)
    c.showPage()

def page_schedule():
    header(2,'Area, circulation and budget checks',
           'Planning allowances and geometry checks - no local construction quotation or code-compliance determination')
    left=48; width=518; right=624; rw=W-right-48; y=H-139
    y=section(left,y,'Where the 200 m² lot goes',width)
    y=table(left,y,width,[('Main ground-floor footprint','94.5 m²'),('Front parking / entrance zone','55.0 m²'),('Nominal side passage','10.5 m²'),('Rear outdoor zone (18 covered + 22 uncovered)','40.0 m²'),('Total lot allocation','200.0 m²')],rowh=25)-24
    y=section(left,y,'Approximate internal room sizes',width)
    schedule=[('Ground queen room','3.60 x 4.10 m / 14.8 m²'),('Ground shared bath','1.85 x 2.30 m / 4.3 m²'),('Laundry','1.60 x 2.30 m / 3.7 m²'),
              ('Living + dining rectangle','8.60 x 3.40 m / 29.2 m²'),('Kitchen / transition zone','4.85 x 2.10 m / 10.2 m²'),
              ('Upper two-double guest room','4.60 x 4.60 m / 21.2 m²'),('Each upstairs bathroom','2.00 x 2.30 m / 4.6 m²'),
              ('Primary bedroom, excluding entry nook','4.30 x 4.35 m / 18.7 m²'),('Primary dressing / storage','4.15 x 1.90 m / 7.9 m²')]
    y=table(left,y,width,schedule,rowh=24,size=9.5)-10
    y=para(left,y,width,'Room rectangles are internal planning zones, not a second gross-area total. Kitchen and lounge connect through open circulation. Actual cabinetry, services, wall finishes and purchased furniture must be checked during design development.',9,MUTED)-24
    y=section(left,y,'Furniture and use checks',width)
    y=para(left,y,width,'Queen: 1.52 x 2.03 m. King: 2.00 x 2.00 m. Doubles: 1.35 x 1.90 m each. Eight guests means two people share each double bed. Indoor table: 2.20 x 0.95 m, eight chairs. The lounge uses an L-sofa and two armchairs; dining chairs can supplement it.',10)-13
    para(left,y,width,'Laundry access is outdoors through the side passage. The dressing room is the first space to compress in a smaller alternative. The right boundary wall has no windows or doors.',10)
    y=H-139
    y=section(right,y,'MXN 4 million working target',rw)
    y=table(right,y,rw,[('Construction + site works, residual allowance','2,600,000'),('Design, studies and permits, provisional','300,000'),('Furniture, appliances and linens, provisional','500,000'),('Contingency / 15%','600,000'),('Total, excluding land','4,000,000')],rowh=25)-14
    y=para(right,y,rw,'These are budget allocations, not current market prices. The construction allowance must cover the house, terrace, installed kitchen/joinery, drainage, services, boundaries and gate. The 173 m² scheme has not yet been shown to fit this allowance.',10)-18
    y=section(right,y,'Stair fit study',rw)
    # Enlarged isolated stair plan, 1:50, with the circulation approach visible.
    sp=Plan(right+44,y-194,scale=S*1.5,bx=-6.15,by=-.2)
    sp.stair(False); sp.dimh(6.3,8.8,4.9,'2.50 m ZONE')
    sp.dimv(9.2,.2,4.5,'4.30 m ZONE')
    para(right+225,y-10,rw-225,'18 risers / 9 per flight<br/>175 mm riser at a provisional 3.15 m floor-to-floor height<br/>280 mm treads / 2.24 m run per flight<br/>1.05 m nominal flights and turning landing<br/>1.00 m front arrival landing',9.5)
    y-=221
    y=para(right,y,rw,'The area and tread arithmetic fit the reserved zone. Headroom, handrails/guards, clear widths after finishes, structural support and local compliance still require architectural and engineering review.',9,MUTED)-23
    y=section(right,y,'Decision before design development',rw)
    para(right,y,rw,'Obtain local pricing against this exact scope before accepting the floor area. If the total exceeds the target, simplify discretionary finishes and joinery, then test a smaller furnished plan. Preserve the patio, bathroom usefulness, drainage and waterproofing.',10)
    c.showPage()

def page_appearance():
    header(3,'Warm, private and easy to return to',
           'Appearance study / warm cream plaster, terracotta screen, restrained tilework and shaded outdoor living')
    imagepath=ROOT/'appearance-concept.png'
    ir=ImageReader(str(imagepath)); iw,ih=ir.getSize()
    dh=430; dw=dh*iw/ih; top=H-125; imageleft=(W-dw)/2
    c.drawImage(ir,imageleft,top-dh,width=dw,height=dh,mask='auto')
    txt(imageleft+10,top-20,'STREET / FRONT COURT',9,PAPER,True)
    txt(W/2+15,top-20,'REAR / COVERED PATIO',9,PAPER,True)
    y=top-dh-18
    y=para(48,y,W-96,'AI-generated appearance reference using the built-in image tool. It conveys materials, shade and massing; window positions, roof supports, planting and apparent distances are illustrative. The measured schematic governs the proposed geometry.',8.5,MUTED)-20
    colw=(W-144)/3
    for i,(title,body) in enumerate([
        ('01 / Confirm the envelope','Commission a boundary/topographic survey and obtain the parcel-specific municipal conditions. This concept depends on a side-boundary wall, a one-meter side passage and a covered terrace.'),
        ('02 / Establish the site levels','Use a parcel-level drainage/flood assessment and geotechnical advice to set floor elevation and foundations. Confirm water, sewer and electrical connections before fixing equipment or service space.'),
        ('03 / Price the same scope','Ask local professionals to price the same room schedule, finishes and inclusions. Separate tax, fees, furnishings, site works and contingency; resolve exclusions before approving design development.')]):
        xx=48+i*(colw+24); yy=section(xx,y,title,colw); para(xx,yy,colw,body,9)
    txt(48,65,'Basis: client brief; Google Maps street context; municipal land-use requirements; 2014 municipal risk atlas.',7.5,MUTED)
    c.linkURL('https://www.google.com/maps?q=20.699864,-105.245731',(48,61,228,73),relative=0)
    c.linkURL('https://www.puertovallarta.gob.mx/storage/tramites/dictaminacion-dictamen-de-trazos-usos-y-destinos-especificos/dictaminacion-dictamen-de-trazos-usos-y-destinos-especificos-requisitos-1730386925.pdf',(230,61,500,73),relative=0)
    c.showPage()

def verify_geometry():
    assert isclose(94.5+55+10.5+40,200)
    assert isclose(18*.175,3.15)
    assert isclose(8*.28,2.24)
    assert isclose(2600000+300000+500000+600000,4000000)
    for ident,name,floor,x,y,w,h in rooms:
        assert x>=.2-1e-8 and y>=.2-1e-8
        assert x+w<=8.8+1e-8 and y+h<=(10.3 if floor=='Ground' else 9.3)+1e-8, ident
    # Zone rectangles should be disjoint on each level.
    for i,a in enumerate(rooms):
        for b in rooms[i+1:]:
            if a[2]!=b[2]: continue
            dx=min(a[3]+a[5],b[3]+b[5])-max(a[3],b[3])
            dy=min(a[4]+a[6],b[4]+b[6])-max(a[4],b[4])
            assert dx<=1e-8 or dy<=1e-8,(a[0],b[0])
    payload={'units':'meters; areas in square meters','areas':areas,
             'rooms':[{'id':i,'name':n,'floor':f,'rect':[x,y,w,h],'area':w*h} for i,n,f,x,y,w,h in rooms],
             'checks':['lot allocation reconciles','room rectangles inside floor envelopes','room rectangles do not overlap','stair rise/run arithmetic','budget allocation reconciles'],
             'not_verified':['parcel buildability','structural adequacy','code compliance','stair headroom','actual local construction cost','finished floor level','flood exposure','utility capacity']}
    (ROOT/'area-schedule.json').write_text(json.dumps(payload,indent=2)+'\n')

if __name__=='__main__':
    verify_geometry()
    page_plans(); page_schedule(); page_appearance(); c.save()
    print(json.dumps({'pdf':str(OUT),'pages':3,'combined_floor_area_m2':round(areas['combined_floor'],1),'terrace_m2':18}))
