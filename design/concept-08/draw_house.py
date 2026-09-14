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
OUT = ROOT / 'las-juntas-concept-08.pdf'
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
ACOUSTIC = HexColor('#B9CCCA')
S = 1000 / 100 * 72 / 25.4  # 1:100 on A3, printed at 100 percent
c = canvas.Canvas(str(OUT), pagesize=(W, H))
c.setTitle('Las Juntas | Kitchen and parking revision | Concept 08')
c.setAuthor('Client concept study')
c.setSubject('Furnished schematic plans, area reconciliation, budget allowances and appearance concept')

HEIGHTS = {'ground_clear':3.00,'upper_clear':2.80,'floor_to_floor':3.40}
HEIGHTS['floor_assembly_allowance'] = HEIGHTS['floor_to_floor']-HEIGHTS['ground_clear']
HEIGHTS['upper_ceiling_level'] = HEIGHTS['floor_to_floor']+HEIGHTS['upper_clear']
STAIR = {'risers':20,'risers_per_flight':10,'tread':.28,'flight_width':1.05,
         'front_landing':1.00,'turn_landing':1.05,'zone_width':2.50,'zone_depth':4.60,
         'start_y':1.20,'opening_width':2.25,'opening_depth':3.59}
STAIR['riser'] = HEIGHTS['floor_to_floor']/STAIR['risers']
STAIR['run'] = (STAIR['risers_per_flight']-1)*STAIR['tread']
STAIR['flight_back_y'] = STAIR['start_y']+STAIR['run']
STAIR['turn_back_y'] = STAIR['flight_back_y']+STAIR['turn_landing']
STAIR['midlanding_level'] = STAIR['risers_per_flight']*STAIR['riser']

rooms = [
    ('G1', 'Queen guest bedroom', 'Ground', .2, 2.75, 3.5, 3.9),
    ('G2', 'Front shared full bathroom', 'Ground', .2, .2, 2, 2.3),
    ('G3', 'Recessed stacked laundry bay', 'Ground', 2.35, .2, 1.45, 1.3),
    ('G4', 'Kitchen / transition zone', 'Ground', 3.95, 4.95, 4.85, 1.8),
    ('G5', 'Living / dining zone', 'Ground', .2, 6.9, 8.6, 3.4),
    ('G6', 'Entrance circulation', 'Ground', 3.95, .2, 2.2, 4.6),
    ('G7', 'Stair zone, including landings', 'Ground', 6.3, .2, 2.5, 4.6),
    ('G8', 'Enclosed service passage', 'Ground', 2.35, 1.5, 1.45, 1),
    ('U1', 'Two-double guest bedroom', 'Upper', .2, 2.75, 4.5, 4.0),
    ('U2', 'Open shared bathroom with far-end shower', 'Upper', .2, .2, 3.6, 2.3),
    ('U3', 'Hall linen cupboard', 'Upper', 3.95, 1.95, .6, .55),
    ('U4', 'Primary dressing / storage', 'Upper', .2, 6.9, 4.6, 2.4),
    ('U5', 'Primary bedroom', 'Upper', 4.95, 5.05, 3.85, 4.25),
    ('U6', 'Hall', 'Upper', 4.95, .2, 1.2, 4.6),
    ('U7', 'Upper arrival landing', 'Upper', 6.3, .2, 2.5, 1),
]
void = STAIR['opening_width'] * STAIR['opening_depth']
areas = {'lot': 200, 'ground': 94.5, 'upper_envelope': 85.5,
         'upper_stair_void': void, 'upper_floor': 85.5 - void,
         'combined_floor': 180 - void, 'covered_terrace': 18,
         'front_zone': 55, 'side_passage': 10.5, 'rear_zone': 40}
# Building-local rectangles in meters. The shower occupies the far end from the hall door.
UPPER_BATH_FIXTURES = {
    'shower': [.2,.2,1.1,2.3],
    'double_vanity': [1.65,.2,1.9,.55],
    'toilet': [2.0,1.72,.6,.75],
}
UPPER_BATH_DOOR = {'x':3.875,'y':.85,'width':.9}
UPPER_SHOWER_ENTRY = [.9,1.8]  # Open segment along the glass line at x=1.30.
LINING_RESERVE = .10  # Design allowance, not a selected tested assembly.
LININGS = {
    'Ground': [(.2,2.65,3.6,.1),(3.7,2.75,.1,3.9),(.2,6.65,3.6,.1)],
    'Upper': [(.2,2.65,4.6,.1),(4.7,2.75,.1,4.0),(4.95,4.95,3.85,.1)],
}
DOORS = {
    'D1_stair': {'x':6.225,'y':.25,'width':.90,'into':'left'},
    'D2_service': {'x':3.875,'y':1.55,'width':.90,'into':'right'},
    'D0_front': {'x':4.10,'y':.10,'width':1.00,'wall':'h'},
}
LIVING_FURNITURE = {
    'media_console': (.25,7.70,.35,1.65),
    'tv': (.20,7.90,.08,1.25),
    'sofa': (2.95,7.25,.85,2.60),
    'coffee_table': (1.95,8.10,.55,1.20),
    'chair': (.90,7.15,.75,.75),
    'rear_chair': (.90,9.40,.75,.75),
}
LIVING_ROUTE = (3.95,6.90,1.00,3.40)
REAR_ROUTE = (4.95,9.30,3.15,1.00)
KITCHEN = {
    'counter': (5.20,4.95,3.60,.65),
    'cooktop': (5.70,5.06,.75,.43),
    'sink': (7.10,5.06,.65,.43),
    'fridge_bay': (7.95,5.75,.85,.90),
    'fridge_body': (8.03,5.80,.72,.80),
    'sink_standing': (7.125,5.60,.60,.75),
    'through_route': (3.95,4.95,1.00,5.35),
}
FRIDGE_DOOR = {'hinge':(8.03,6.60),'width':.80,'angle':90,
               'sweep_bounds':(7.23,5.80,.80,.80)}
DINING_TABLE = (5.50,7.55,2.20,.95)
CHAIR_PULL_OUT = .30  # Illustrative movement test, not a selected chair specification.
PARKING = {'court_depth':5.50,'car':(1.80,.55,1.85,4.50),
           'gate_gap':.55,'house_gap':.45,'vehicle_gate_width':3.20}

def dining_chairs(pulled=False):
    x,y,w,h=DINING_TABLE
    move=CHAIR_PULL_OUT if pulled else 0
    result=[]
    for xx in [x+.12,x+w/2-.225,x+w-.57]:
        result.extend([(xx,y-.55-move,.45,.43),(xx,y+h+.12+move,.45,.43)])
    result.extend([(x-.55-move,y+h/2-.225,.43,.45),
                   (x+w+.12+move,y+h/2-.225,.43,.45)])
    return result

SOURCES = {
    'noise': 'https://www.yourhome.gov.au/live-adapt/noise-control',
    'usg': 'https://www.usg.com/en-US/learning-reference/performance/acoustic/principles',
    'insulation': 'https://www.yourhome.gov.au/passive-design/insulation',
    'glazing': 'https://www.pilkington.com/en-gb/united-kingdom/architectural-and-technical-glass/product-categories/noise-control/pilkington-optiphon',
}
METERS_PER_FOOT = .3048  # Exact international foot; convert before rounding.

def feet(meters):
    return meters / METERS_PER_FOOT

def square_feet(square_meters):
    return square_meters / METERS_PER_FOOT**2

def area_row(label, area):
    return label, f'{area:,.1f} m²', f'{square_feet(area):,.1f} ft²'

def dimension_row(label, *dimensions, precision=2):
    metric = ' x '.join(f'{d:.{precision}f}' for d in dimensions) + ' m'
    imperial = ' x '.join(f'{feet(d):.2f}' for d in dimensions) + ' ft'
    return label, metric, imperial

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
    txt(W-48, H-40, 'CONCEPT 08  /  3 BED + 2 BATH  /  12 SEPTEMBER 2026', 9, MUTED, align='right')
    txt(48, H-77, title, 26, bold=True)
    txt(48, H-98, subtitle, 10, MUTED)
    line(48, 49, W-48, 49)
    txt(48, 32, 'SCHEMATIC STUDY - NOT FOR CONSTRUCTION OR PERMIT', 8, TERRACOTTA, True)
    txt(W-48, 32, f'{sheet:02d} / 08', 8, MUTED, align='right')

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
    def kitchen(self,detail=False):
        self.rect(*KITCHEN['counter'],WOOD,INK,.5)
        for key in ['cooktop','sink']:
            self.rect(*KITCHEN[key],PAPER,INK,.5)
        hx,hy,hw,hh=KITCHEN['cooktop']
        for xx in [hx+.18,hx+hw-.18]:
            for yy in [hy+.11,hy+hh-.11]: self.circle(xx,yy,.06,PAPER,INK,.4)
        sx,sy,sw,sh=KITCHEN['sink']
        self.rect(sx+.05,sy+.05,sw-.1,sh-.1,WATER,INK,.35)
        self.circle(sx+sw/2,sy+sh/2,.025,PAPER,INK,.3)
        self.rect(*KITCHEN['fridge_bay'],ACOUSTIC,SAGE,.4)
        self.rect(*KITCHEN['fridge_body'],PAPER,INK,.6)
        fx,fy,fw,fh=KITCHEN['fridge_body']
        self.line(fx+.04,fy+.12,fx+.04,fy+fh-.12,INK,.7)
        self.text(fx+fw/2,fy+fh/2-.06,'FR / 80 cm' if detail else 'FR',8 if detail else 6.5,INK,True)
        hinge_x,hinge_y=FRIDGE_DOOR['hinge']; r=FRIDGE_DOOR['width']
        self.line(hinge_x,hinge_y,hinge_x-r,hinge_y,TERRACOTTA,.9)
        points=[(hinge_x+r*cos(radians(a)),hinge_y+r*sin(radians(a))) for a in range(180,271,3)]
        for a,b in zip(points,points[1:]): self.line(*a,*b,TERRACOTTA,.5,[2,2] if detail else None)
        if detail:
            self.text(5.45,5.29,'LOW',6.8,MUTED)
            self.text(5.45,5.15,'COUNTER',6.8,MUTED)
            self.text(6.775,5.22,'PREP',8,INK,True)
            self.text(8.29,5.22,'LANDING',7.1,MUTED)
    def linings(self, floor):
        for rect in LININGS[floor]: self.rect(*rect,ACOUSTIC,SAGE,.35)
    def acoustic_door(self, key, detail=False):
        d=DOORS[key]
        self.door(d['x'],d['y'],d['width'],wall=d.get('wall','v'),into=d.get('into','left'))
        if key=='D1_stair':
            self.text(5.96,.54,'D1',8 if detail else 5.8,TERRACOTTA,True)
        elif key=='D2_service':
            self.text(4.20,2.59,'D2',8 if detail else 5.8,TERRACOTTA,True)
    def living_furniture(self, detail=False):
        self.rect(.75,7.02,3.10,2.98,HexColor('#E5DECC'),None)
        for name,rect in LIVING_FURNITURE.items():
            self.rect(*rect,INK if name=='tv' else PAPER if name=='coffee_table' else WOOD,
                      None if name=='tv' else INK,.5)
        self.line(3.13,7.35,3.13,9.75,INK,.45)
        self.line(3.13,8.10,3.70,8.10,INK,.35)
        self.line(3.13,8.97,3.70,8.97,INK,.35)
        if detail:
            self.text(.425,9.65,'TV',8,INK,True)
            self.text(3.375,8.53,'SOFA',7,INK,True)
            self.rect(*LIVING_ROUTE,None,SAGE,.55)
            for a,b in [((4.45,7.05),(4.45,9.80)),((4.45,9.80),(7.30,9.80)),((7.30,9.80),(7.30,10.45))]:
                self.line(*a,*b,SAGE,1,[4,3])
            self.line(7.30,10.45,7.18,10.28,SAGE,1)
            self.line(7.30,10.45,7.42,10.28,SAGE,1)
    def window(self,x,y,w,h):
        self.rect(x,y,w,h,WATER,None)
        if w>h:
            self.line(x,y+h*.33,x+w,y+h*.33,SAGE,.6); self.line(x,y+h*.67,x+w,y+h*.67,SAGE,.6)
        else:
            self.line(x+w*.33,y,x+w*.33,y+h,SAGE,.6); self.line(x+w*.67,y,x+w*.67,y+h,SAGE,.6)
    def door(self,x,y,w,wall='v',into='left'):
        if wall=='v':
            self.rect(x-.1,y,.2,w,FLOOR,None)
            angle = 90 if into=='left' else 270
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
    def stair(self,upper=False,detail=False):
        self.rect(6.3,.2,STAIR['zone_width'],STAIR['zone_depth'],FLOOR,RULE)
        if upper:
            self.rect(6.4,STAIR['start_y'],STAIR['opening_width'],STAIR['opening_depth'],HexColor('#E4E7E0'),RULE)
        for xx in [6.4,7.6]:
            for i in range(STAIR['risers_per_flight']):
                yy=STAIR['start_y']+i*STAIR['tread']
                self.line(xx,yy,xx+STAIR['flight_width'],yy,INK,.45,[2,2] if (upper and xx==6.4) else None)
        self.line(7.5,STAIR['start_y'],7.5,STAIR['flight_back_y'],INK,.9)
        turn_mid=(STAIR['flight_back_y']+STAIR['turn_back_y'])/2
        pts=[(6.925,1.45),(6.925,turn_mid),(8.125,turn_mid),(8.125,1.45)]
        for a,b in zip(pts,pts[1:]): self.line(*a,*b,TERRACOTTA,.8)
        self.line(8.125,1.45,7.99,1.68,TERRACOTTA,.8)
        self.line(8.125,1.45,8.26,1.68,TERRACOTTA,.8)
        self.text(7.55,.64,'U7  /  ARRIVAL' if upper else 'G7  /  UP',6.4,TERRACOTTA)
        if detail: self.text(7.55,turn_mid+.18,'MID +1.70 m',7,INK,True)
    def shared_family_bath(self, detail=False):
        # One open bathroom; the only internal screen encloses the far-end shower.
        self.rect(.2,.2,3.6,2.3,WATER,None)
        sx,sy,sw,sh=UPPER_BATH_FIXTURES['shower']
        self.rect(sx,sy,sw,sh,HexColor('#C1D9DB'),None)
        self.line(sx,2.15,sx+.33,2.15,SAGE,.7)
        self.circle(sx+.33,2.15,.10,PAPER,SAGE)
        self.line(sx+.15,2.33,sx+sw-.15,2.33,SAGE,1)
        gx=sx+sw
        for ya,yb in [(sy,UPPER_SHOWER_ENTRY[0]),(UPPER_SHOWER_ENTRY[1],sy+sh)]:
            self.line(gx,ya,gx,yb,SAGE,1.2)
            self.line(gx+.025,ya,gx+.025,yb,SAGE,.45)
        self.text(sx+sw/2,1.30,'SHOWER',9 if detail else 5.5,INK,True)
        tx,ty,tw,th=UPPER_BATH_FIXTURES['toilet']
        self.rect(tx,ty+th-.20,tw,.20,PAPER,INK,.4)
        px,py=self.p(tx+.07,ty)
        c.saveState(); c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(.4)
        c.roundRect(px,py,.46*self.s,.57*self.s,.18*self.s,fill=1,stroke=1); c.restoreState()
        vx,vy,vw,vh=UPPER_BATH_FIXTURES['double_vanity']
        self.rect(vx,vy,vw,vh,WOOD,INK,.4)
        for dx in (.12,1.12): self.rect(vx+dx,vy+.09,.60,.37,PAPER,INK,.4)
        self.text(2.25,1.09,'U2  SHARED',9 if detail else 6.8,INK,True)
        if detail:
            self.text(tx+tw/2,ty-.15,'TOILET',8,MUTED)
            self.line(3.52,1.38,1.03,1.38,SAGE,1.1,[4,3])
            self.line(1.03,1.38,1.19,1.48,SAGE,1.1)
            self.line(1.03,1.38,1.19,1.28,SAGE,1.1)
    def front_service(self, detail=False):
        # D2 encloses G3 and G8 as one service vestibule, without cabinet leaves in G8.
        self.rect(.2,.2,2,2.3,WATER,None)
        self.rect(2.35,.2,1.45,1.3,HexColor('#E8E2D3'),None)
        self.rect(2.35,1.5,1.45,1,HexColor('#E5EBD9'),None)
        self.wall(2.2,.2,.15,2.3)
        self.wall(3.8,1.5,.15,1)
        self.acoustic_door('D2_service',detail)
        self.door(2.275,1.6,.85)
        # Bathroom: shower at rear-left; toilet and vanity at the front.
        self.rect(.2,1.6,1,.9,None,SAGE,.6)
        self.line(.2,1.6,1.2,2.5,SAGE,.35)
        self.circle(.7,2.05,.05,PAPER,SAGE)
        self.line(1.2,1.6,1.2,2.5,SAGE,1)
        self.rect(.35,.23,.6,.2,PAPER,INK,.4)
        px,py=self.p(.42,.41)
        c.saveState(); c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(.4)
        c.roundRect(px,py,.46*self.s,.57*self.s,.18*self.s,fill=1,stroke=1); c.restoreState()
        self.rect(1.3,.2,.9,.55,WOOD,INK,.4)
        self.rect(1.47,.28,.55,.36,PAPER,INK,.4)
        # Nominal stack footprint, with service space behind and in front.
        self.rect(2.45,.35,.75,.85,PAPER,INK,.6)
        self.circle(2.825,.79,.23,WATER,INK)
        self.text(2.825,.74,'W/D',8 if detail else 6,INK,True)
        self.rect(3.28,.35,.47,.70,WOOD,INK,.4)
        self.rect(3.35,.48,.33,.40,PAPER,INK,.4)
        self.line(2.35,1.5,3.8,1.5,SAGE,.45,[2,2])
        self.text(1.14,1.20,'G2  BATH',9.5 if detail else 7.2,INK,True)
        self.text(3.2 if detail else 3.04,1.33,'G3  LAUNDRY',8 if detail else 6.1,INK,True)
        self.text(3.04,2.22,'G8  PASSAGE',9 if detail else 6.1,INK,True)
        if detail:
            route=HexColor('#57774B')
            self.line(4.65,2.02,1.85,2.02,route,1.4,[4,3])
            self.line(1.85,2.02,2.02,2.12,route,1.4)
            self.line(1.85,2.02,2.02,1.92,route,1.4)
            self.line(2.825,2.02,2.825,1.28,route,1.4,[4,3])
            self.line(2.825,1.28,2.725,1.45,route,1.4)
            self.line(2.825,1.28,2.925,1.45,route,1.4)
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
        p.rect(*PARKING['car'],HexColor('#C6CDCA'),INK,.6)
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
        p.shared_family_bath()
    for wall in [(0,0,.2,d),(8.8,0,.2,d),(.2,0,8.6,.2),(.2,d-.2,8.6,.2),
                 (6.15,.2,.15,4.6),(6.3,4.8,2.5,.15)]: p.wall(*wall)
    if not upper:
        for wall in [(3.8,.2,.15,6.55),(.2,2.5,3.6,.15),(.2,6.75,3.6,.15)]: p.wall(*wall)
        p.linings('Ground')
        p.front_service()
        p.rect(3.69,3.0,.27,.9,FLOOR,None)
        p.door(3.70,3.0,.9)
        p.acoustic_door('D0_front')
        p.window(.4,0,.85,.2); p.window(3.25,0,.45,.2); p.window(6.8,0,1.65,.2)
        p.window(.65,10.3,2.9,.2); p.sliding(4.9,10.4,3.2)
        p.window(0,4.25,.2,1.3)
        p.bed(1.4,4.42,1.52,2.03,'QUEEN')
        p.rect(.2,2.95,.6,1.25,WOOD,INK,.4)
        p.rect(5.7,2.6,.45,1.2,WOOD,INK,.4)
        p.kitchen()
        p.table(*DINING_TABLE)
        p.living_furniture()
        labels=[(2,3.55,'G1  GUEST'),
                (6.20,6.17,'G4  KITCHEN'),(2.20,10.10,'G5  LIVING'),
                (6.6,9.6,'DINING / 8'),(5.15,2.15,'G6')]
    else:
        for wall in [(3.8,.2,.15,2.3),(.2,2.5,4.6,.15),(4.8,2.65,.15,6.65),
                     (.2,6.75,4.6,.15),(4.95,4.8,3.85,.15)]: p.wall(*wall)
        p.linings('Upper')
        p.door(UPPER_BATH_DOOR['x'],UPPER_BATH_DOOR['y'],UPPER_BATH_DOOR['width'])
        p.rect(4.69,3.4,.27,.9,FLOOR,None)
        p.door(4.70,3.4,.9)
        p.rect(5.05,4.79,.9,.27,FLOOR,None)
        p.door(5.05,5.05,.9,'h')
        p.sliding(4.875,7.15,.9,True)
        p.window(.4,0,.7,.2); p.window(2.6,0,.9,.2); p.window(6.8,0,1.65,.2)
        p.window(0,4.1,.2,1.5)
        p.window(0,7.8,.2,.55); p.window(5.2,9.3,3.05,.2)
        p.bed(.8,4.55,1.35,1.9,'DOUBLE')
        p.bed(2.85,4.55,1.35,1.9,'DOUBLE')
        p.rect(.35,2.75,3.05,.6,WOOD,INK,.4)
        p.rect(3.95,1.95,.6,.55,WOOD,INK,.4)
        p.text(4.25,2.15,'U3',6.5)
        p.bed(6.65,6.15,2,2,'KING',head='right')
        p.rect(8.1,5.57,.55,.48,WOOD,INK,.4)
        p.rect(8.1,8.25,.55,.48,WOOD,INK,.4)
        p.rect(.35,8.7,4.3,.6,WOOD,INK,.4)
        for x in [1.07,1.78,2.50,3.22,3.93]: p.line(x,8.7,x,9.3,INK,.35)
        p.rect(.35,7.15,.6,1.2,WOOD,INK,.4)
        labels=[(2.5,3.92,'U1  GUEST / 4'),(2.8,7.90,'U4  DRESSING'),
                (6.7,5.5,'U5  PRIMARY'),(5.55,3.0,'U6')]
    # Both levels enter the U-stair through the same front landing.
    if upper: p.rect(6.145,.25,.16,.9,FLOOR,None)
    else: p.acoustic_door('D1_stair')
    for x,y,t in labels: p.text(x,y,t,7.2,INK,True)

def table(x,y,width,rows,col2=360,rowh=25,size=10):
    for i,(a,b) in enumerate(rows):
        if i%2==0:
            c.setFillColor(FLOOR); c.rect(x,y-rowh+6,width,rowh,fill=1,stroke=0)
        txt(x+10,y-10,a,size)
        txt(x+width-10,y-10,b,size,align='right')
        y-=rowh
    return y

def unit_table(x, y, width, rows, label_fraction=.43, rowh=24, size=9,
               headers=('Meters', 'Feet / reference')):
    """Room/item labels followed by two fixed, right-aligned unit columns."""
    label_width = width * label_fraction
    unit_width = (width-label_width)/2
    metric_right = x+label_width+unit_width-10
    imperial_right = x+width-10
    txt(x+10,y-8,'SPACE / ITEM',7.5,MUTED,True)
    txt(metric_right,y-8,headers[0],8,MUTED,True,align='right')
    txt(imperial_right,y-8,headers[1],8,MUTED,True,align='right')
    line(x,y-16,x+width,y-16)
    y-=21
    for i,(label,metric,imperial) in enumerate(rows):
        if i%2==0:
            c.setFillColor(FLOOR); c.rect(x,y-rowh+3,width,rowh,fill=1,stroke=0)
        label_bottom=para(x+10,y-3,label_width-20,label,size,leading=size+2)
        assert label_bottom >= y-rowh+3, f'Label exceeds row: {label}'
        for right,value in [(metric_right,metric),(imperial_right,imperial)]:
            values=value if isinstance(value,tuple) else (value,)
            for j,text in enumerate(values):
                value_size=size if j==0 else size-1
                assert pdfmetrics.stringWidth(text,'HouseRegular',value_size) <= unit_width-20, text
                txt(right,y-11-j*12,text,value_size,MUTED if j else INK,align='right')
        y-=rowh
    return y

def page_plans():
    header(1,'A quieter house, with the same warm character.',
           'Clear ceilings: ground 3.00 m / upper 2.80 m     |     Floor-to-floor 3.40 m, provisional     |     Plans at 1:100 on A3 at 100%')
    for upper,x,title in [(False,80,'01  GROUND FLOOR'),(True,481,'02  UPPER FLOOR')]:
        txt(x, H-119,title,11,INK,True)
        p=Plan(x,125); site(p,upper)
        building(Plan(x,125,bx=1,by=5.5),upper)
    x=837; width=W-x-48; y=H-139
    y=section(x,y,'3 bedrooms / 2 full bathrooms',width)
    y=para(x,y,width,'Queen guest room downstairs; king primary and two-double guest room upstairs. Each floor has one shared, hall-accessed bathroom. Neither bedroom upstairs is an en suite.',10)-18
    y=section(x,y,'The proposed fit',width)
    y=unit_table(x,y,width,[area_row('Ground floor',areas['ground']),area_row('Upper, less stair void',areas['upper_floor']),area_row('Combined floors',areas['combined_floor']),area_row('Covered terrace, extra',areas['covered_terrace'])],label_fraction=.49,rowh=25,size=8,headers=('m²','ft² / ref.'))-12
    y=para(x,y,width,'Gross areas include walls. Bedroom dimensions on page 6 now deduct the reserved acoustic linings. Metric dimensions govern; feet are rounded references.',9,MUTED)-17
    y=section(x,y,'Noise-control changes',width)
    y=para(x,y,width,'TV moved to the left exterior wall. D1 closes the stair; D2 encloses the laundry and service passage. Blue-green bands reserve 0.10 m for bedroom acoustic linings. Details and specifications: pages 4-5.',9.5)-18
    y=section(x,y,'Room arrangement',width)
    for title,body in [
        ('Ground / social + guest','G1 queen room; G2 front shared bath; G3 laundry; G4 kitchen with fridge on right wall (detail: page 7); G5 living/dining; G6 entry; G7 stair; G8 service passage.'),
        ('Upper / shared bath','U1 two-double room; U2 open shared bath with a far-end shower, toilet and double vanity; U3 linen; U4 dressing/storage; U5 primary; U6 hall; U7 stair arrival.')]:
        txt(x,y,title,10,bold=True); y=para(x,y-9,width,body,9.5)-17
    y=section(x,y,'Still schematic',width)
    para(x,y,width,'Setbacks, boundary-wall permission, floor elevation, structure and services need local review. Front/rear orientation is schematic; no surveyed north is asserted.',9)
    # Scale bar is independent of the diagram labels.
    for i in range(5):
        c.setFillColor(INK if i%2==0 else PAPER); c.setStrokeColor(INK)
        c.rect(80+i*S,80,S,5,fill=1,stroke=1)
    txt(80,66,'0',7,MUTED); txt(80+5*S,66,'5 m',7,MUTED,align='right')
    txt(295,76,'Windows',8,MUTED); line(270,79,289,79,SAGE,2)
    txt(400,76,'Door swings',8,MUTED); line(375,79,394,79,TERRACOTTA,1)
    line(521,79,539,79,ACOUSTIC,4)
    txt(545,76,'Reserved acoustic lining',8,MUTED)
    c.showPage()

def page_service_detail():
    header(2,'Both bathrooms, with clear indoor access.',
           'Enlarged bathroom studies / both at 1:30 on A3 at 100% / meter and feet reference columns below')
    section(48,H-139,'Ground / bathroom and laundry',518)
    section(624,H-139,'Upper / shower at the far end',W-624-48)
    detail_scale=S*100/30
    p=Plan(80,390,scale=detail_scale)
    p.rect(0,0,4.95,2.65,FLOOR,None)
    for wall in [(0,0,.2,2.65),(0,0,3.95,.2),(.2,2.5,3.6,.15),(3.8,.2,.15,2.3)]: p.wall(*wall)
    p.front_service(detail=True)
    p.rect(.2,2.65,3.6,.1,ACOUSTIC,SAGE,.35)
    p.window(.4,0,.85,.2); p.window(3.25,0,.45,.2)
    p.text(1.9,2.95,'G1 BEDROOM BEYOND',9,MUTED,True)
    p.text(4.43,1.02,'G6 ENTRY',9,INK,True)
    p.text(4.43,.80,'HALL',9,INK,True)
    p.text(1.9,-.60,'FRONT COURT / STREET SIDE',8,MUTED)
    p.dimh(.2,2.2,-.29,'2.00 m')
    p.dimh(2.35,3.8,-.29,'1.45 m')
    p.dimv(-.30,.2,2.5,'2.30 m')
    p.line(3.61,1.5,3.61,2.5,MUTED,.5)
    for yy in (1.5,2.5): p.line(3.55,yy,3.67,yy,MUTED,.6)
    p.text(3.29,1.71,'1.00 m',8,MUTED)
    p=Plan(656,390,scale=detail_scale)
    p.rect(0,0,4.95,2.65,FLOOR,None)
    p.shared_family_bath(detail=True)
    for wall in [(0,0,.2,2.65),(0,0,3.95,.2),(.2,2.5,3.6,.15),(3.8,.2,.15,2.3)]: p.wall(*wall)
    p.rect(.2,2.65,3.6,.1,ACOUSTIC,SAGE,.35)
    p.door(UPPER_BATH_DOOR['x'],UPPER_BATH_DOOR['y'],UPPER_BATH_DOOR['width'])
    p.window(.4,0,.7,.2); p.window(2.6,0,.9,.2)
    p.text(1.9,2.95,'U1 BEDROOM BEYOND',9,MUTED,True)
    p.text(4.43,1.02,'U6 HALL',9,INK,True)
    p.text(1.9,-.60,'FRONT COURT / STREET SIDE',8,MUTED)
    p.dimh(.2,3.8,-.29,'3.60 m')
    p.dimv(-.30,.2,2.5,'2.30 m')
    y=section(48,300,'Ground-floor service dimensions',518)
    rows=[]
    for ident in ('G2','G3','G8'):
        room=next(r for r in rooms if r[0]==ident)
        label={'G2':'G2 / Bathroom','G3':'G3 / Recessed laundry bay','G8':'G8 / Passage'}[ident]
        rows.append(dimension_row(label,*room[5:7]))
    y=unit_table(48,y,518,rows,rowh=25,size=9.5)-12
    y=para(48,y,518,'D2 opens into G6 and encloses G3 + G8 together. The 1.00 m-deep passage stays free of door swings; its hall doorway is 0.90 m nominal. G2 opens inward. Loading still uses G8 temporarily. Ventilate the enclosure to suit the chosen washer/dryer; see page 5.',9.5,MUTED)
    assert y>65, 'Ground detail notes reach footer'
    y=section(624,300,'Upper bathroom dimensions',W-624-48)
    rows=[dimension_row('U2 / Open shared bathroom',3.6,2.3),
          dimension_row('Far-end walk-in shower',*UPPER_BATH_FIXTURES['shower'][2:]),
          dimension_row('Double vanity',*UPPER_BATH_FIXTURES['double_vanity'][2:]),
          dimension_row('Shower entry / nominal',UPPER_SHOWER_ENTRY[1]-UPPER_SHOWER_ENTRY[0])]
    y=unit_table(624,y,W-624-48,rows,rowh=25,size=9.5)-12
    y=para(624,y,W-624-48,'The former toilet compartment is removed. The shower is at the far end opposite the hall door, behind a glass screen. The toilet stays in the main bathroom. Final fixture, glazing, drainage and finished clearances need detailed review.',9.5,MUTED)
    assert y>65, 'Upper detail notes reach footer'
    c.showPage()

def page_heights():
    header(3,'Adopted heights and the revised stair.',
           'Height diagram: vertical dimensions at 1:50 / stair plan at 1:50 / provisional structure and site levels')
    section(48,H-139,'Finished floors and clear ceilings',518)
    section(624,H-139,'20 risers connect the two floors',W-624-48)
    s=Plan(105,310,scale=S*2)
    s.rect(0,0,4.8,HEIGHTS['ground_clear'],FLOOR,None)
    s.rect(0,HEIGHTS['floor_to_floor'],4.8,HEIGHTS['upper_clear'],FLOOR,None)
    for z,h in [(0,HEIGHTS['ground_clear']),(HEIGHTS['floor_to_floor'],HEIGHTS['upper_clear'])]:
        s.wall(0,z,.12,h); s.wall(4.68,z,.12,h)
    s.wall(0,-.10,4.8,.10)
    s.rect(0,HEIGHTS['ground_clear'],4.8,HEIGHTS['floor_assembly_allowance'],WOOD,INK,.5)
    s.text(2.4,3.16,'FLOOR + ACOUSTICS / SEE PAGE 5',7.1,INK,True)
    # Roof strip is a graphic placeholder; no roof thickness or final building height is set.
    s.rect(0,HEIGHTS['upper_ceiling_level'],4.8,.25,HexColor('#E5E7DF'),None)
    s.line(0,HEIGHTS['upper_ceiling_level'],4.8,HEIGHTS['upper_ceiling_level'],INK,.8)
    s.line(0,HEIGHTS['upper_ceiling_level']+.25,4.8,HEIGHTS['upper_ceiling_level']+.25,MUTED,.6,[3,3])
    s.text(2.4,6.29,'ROOF BUILD-UP TO DESIGN',7.5,MUTED)
    s.text(2.4,1.48,'GROUND FLOOR',12,INK,True)
    s.text(2.4,4.82,'UPPER FLOOR',12,INK,True)
    s.dimv(-.45,0,HEIGHTS['ground_clear'],'3.00 m / 9.84 ft CLEAR')
    s.dimv(-.45,HEIGHTS['floor_to_floor'],HEIGHTS['upper_ceiling_level'],'2.80 m / 9.19 ft CLEAR')
    s.dimv(5.08,0,HEIGHTS['floor_to_floor'],'3.40 m / 11.15 ft')
    for z,label in [(0,'GROUND FLOOR +0.00 m'),(3.0,'CEILING +3.00 m'),(3.4,'UPPER FLOOR +3.40 m'),(6.2,'CEILING +6.20 m')]:
        s.line(4.8,z,5.38,z,MUTED,.45)
        s.text(5.48,z+.03,label,8,MUTED,align='left')
    y=section(48,270,'Height references',518)
    rows=[dimension_row('Ground / clear ceiling',HEIGHTS['ground_clear']),
          dimension_row('Upper / clear ceiling',HEIGHTS['upper_clear']),
          dimension_row('Ground-to-upper floor',HEIGHTS['floor_to_floor']),
          dimension_row('Floor assembly allowance',HEIGHTS['floor_assembly_allowance']),
          dimension_row('Upper ceiling above datum',HEIGHTS['upper_ceiling_level'])]
    y=unit_table(48,y,518,rows,rowh=22,size=9)-12
    y=para(48,y,518,'The 0.40 m includes structure, tile, acoustic layers, services and any isolated ceiling. Layer thicknesses are unresolved. Coordinate the stack before fixing floor levels and stairs; roof and site levels remain to be set.',9,MUTED)
    assert y>65, 'Height notes reach footer'
    sp=Plan(651,397,scale=S*2,bx=-6.3,by=-.2)
    sp.stair(False,detail=True)
    sp.dimh(6.3,8.8,5.04,'2.50 m BAY')
    sp.dimv(9.15,.2,4.8,'4.60 m BAY')
    x=866; width=W-x-48; y=670
    txt(x,y,'20 x 0.170 m = 3.40 m',12,INK,True)
    y=para(x,y-14,width,'Two flights of 10 risers, with nine 280 mm treads per flight. Each run is 2.52 m. The turning landing is at +1.70 m.',10)-18
    txt(x,y,'D1 closes the stair at ground level',11,TERRACOTTA,True)
    y=para(x,y-12,width,'The new door swings into G6, outside the landing. The front entrance moves 0.20 m left to separate the two nominal door sweeps. See the enlarged entrance study on page 4.',10)-18
    txt(x,y,'Keep the stair opening clear',11,TERRACOTTA,True)
    y=para(x,y-12,width,'The opening covers both flights and the turning landing. Final beam positions, services, handrails, guards and clear headroom need coordinated architectural and structural sections.',9.5,MUTED)
    assert y>350, 'Stair notes reach reference table'
    y=section(624,340,'Stair references',W-624-48)
    rows=[dimension_row('Riser / 20 total',STAIR['riser'],precision=3),
          dimension_row('Tread depth',STAIR['tread'],precision=3),
          dimension_row('Run per flight / 9 treads',STAIR['run']),
          dimension_row('Flight / turning landing',STAIR['flight_width']),
          dimension_row('Front arrival landing',STAIR['front_landing']),
          dimension_row('Reserved stair bay',STAIR['zone_width'],STAIR['zone_depth']),
          dimension_row('Upper stair opening',STAIR['opening_width'],STAIR['opening_depth'])]
    y=unit_table(624,y,W-624-48,rows,rowh=23,size=9)-12
    y=para(624,y,W-624-48,'Nominal dimensions before detailed finishes and rail design. The stair arithmetic and plan fit are checked; local compliance and final headroom are not certified.',9,MUTED)
    assert y>65, 'Stair references reach footer'
    c.showPage()

def page_acoustic_details():
    header(4,'Three layout changes for everyday quiet.',
           'Living detail at 1:50 / entrance detail at 1:40 on A3 at 100% / nominal dimensions before final hardware and finishes')
    section(48,H-139,'Living / exterior-wall TV and a clear route',518)
    section(624,H-139,'Entrance / doors close outside the landings',W-672)
    p=Plan(61,430,scale=S*2,bx=-.2,by=-6.9)
    p.rect(.2,6.9,8.6,3.4,FLOOR,None)
    for wall in [(0,6.75,.2,3.75),(8.8,6.75,.2,3.75),(.2,10.3,8.6,.2),(.2,6.75,3.6,.15)]:
        p.wall(*wall)
    p.rect(.2,6.65,3.6,.1,ACOUSTIC,SAGE,.35)
    p.window(.65,10.3,2.9,.2); p.sliding(4.9,10.4,3.2)
    p.living_furniture(detail=True); p.table(5.5,7.55)
    p.text(6.5,9.62,'DINING / 8',8,INK,True)
    p.text(6.5,10.83,'REAR TERRACE',8,MUTED,True)
    p.text(2.0,6.40,'G1 BEDROOM / TV REMOVED FROM THIS WALL',7.1,MUTED)
    p.text(6.3,6.40,'KITCHEN BEYOND',7.5,MUTED)
    p.dimh(3.95,4.95,6.95,'1.00 m')
    # The entrance detail shows only the relevant service bay, hall and first flight.
    p=Plan(650,420,scale=S*2.5,bx=-2.2)
    p.rect(2.2,0,5.35,3.10,FLOOR,None)
    p.rect(2.35,.2,1.45,1.3,HexColor('#E8E2D3'),None)
    p.rect(2.35,1.5,1.45,1,HexColor('#E5EBD9'),None)
    for wall in [(2.2,.2,.15,2.3),(2.35,0,5.20,.2),(3.8,.2,.15,2.8),
                 (2.35,2.5,1.45,.15),(6.15,.2,.15,2.9)]: p.wall(*wall)
    p.rect(2.19,1.6,.17,.85,FLOOR,None)
    p.line(2.23,1.6,2.23,2.45,TERRACOTTA,.8)
    p.text(2.75,2.27,'TO G2',7,INK,True)
    p.rect(2.45,.35,.75,.85,PAPER,INK,.5)
    p.circle(2.825,.79,.23,WATER,INK)
    p.text(2.825,.74,'W/D',7,INK,True)
    p.text(3.07,1.35,'G3',7,MUTED,True)
    p.line(2.35,1.5,3.8,1.5,SAGE,.5,[2,2])
    p.text(3.04,1.77,'G8',8,INK,True)
    p.acoustic_door('D2_service',detail=True)
    p.acoustic_door('D0_front')
    p.acoustic_door('D1_stair',detail=True)
    for i in range(7): p.line(6.4,1.20+i*.28,7.45,1.20+i*.28,INK,.45)
    p.text(6.94,.63,'LANDING',7,INK,True)
    p.text(5.31,2.79,'G6 ENTRY HALL',8,INK,True)
    p.text(4.6,-.30,'D0 / FRONT DOOR',7.5,MUTED)
    p.dimh(3.95,6.15,3.42,'2.20 m HALL')
    y=section(48,360,'Living / nominal reference dimensions',518)
    y=unit_table(48,y,518,[dimension_row('Three-seat sofa',.85,2.60),
                         dimension_row('Media console',.35,1.65),
                         dimension_row('Route beside seating',1.00),
                         dimension_row('Acoustic lining reserve',LINING_RESERVE)],rowh=24,size=9)-14
    y=para(48,y,518,'The sofa faces the left exterior wall; two chairs complete the seating group. A nominal 1.00 m route runs between the sofa and dining furniture, then turns toward the rear doors. Check final chair pull-out and door hardware during furnishing selection.',9.5)-15
    y=para(48,y,518,'AW1 linings sit inside the bedrooms. Ground G1 loses 0.10 m along each front/rear wall and its hall wall; U1 loses 0.10 m at its bathroom and hall walls; U5 loses 0.10 m at its stair/hall wall. Revised room sizes appear on page 6.',9.5,MUTED)
    assert y>70, 'Living detail notes reach footer'
    y=section(624,360,'Doors / nominal leaf and passage sizes',W-672)
    y=unit_table(624,y,W-672,[dimension_row('D0 / front entrance',1.00),
                            dimension_row('D1 / stair door',.90),
                            dimension_row('D2 / service door',.90),
                            dimension_row('G8 / passage depth',1.00),
                            dimension_row('D0 / move left',.20)],rowh=24,size=9)-14
    y=para(624,y,W-672,'D1 swings into G6, outside the stair landing. D2 also swings into G6, leaving G8 free of door sweeps. The nominal D0/D1 sweep envelopes are separated by 0.225 m. Hardware and finished clear openings remain to be detailed.',9.5)-15
    y=para(624,y,W-672,'G3 and G8 form one enclosed laundry/service vestibule. A separate cabinet front would obstruct bathroom access. D2 provides the acoustic closure; G2 retains its own privacy door. Appliance loading temporarily occupies G8.',9.5,MUTED)
    assert y>70, 'Entrance detail notes reach footer'
    c.showPage()

def page_construction():
    header(5,'Construction and acoustic design brief.',
           'Proposed materials and requirements to detail and price / street traffic plus general household noise / no acoustic performance claim yet')
    left=48; right=624; cw=518; y=H-139
    y=section(left,y,'Structure, walls and roof',cw)
    y=para(left,y,cw,'Starting system: an engineered reinforced-concrete structure and foundations, concrete-masonry infill, and concrete upper floor and roof. The engineer must establish wall roles, beam/slab sizes and reinforcement from the site and structural design. Existing wall cores remain schematic.',10)-10
    y=para(left,y,cw,'Finish with warm plaster/stucco, porcelain or ceramic tile and terracotta accents. Design roof insulation, waterproofing, falls and drainage as one coordinated assembly; roof thickness and site levels are still open. <link href="'+SOURCES['insulation']+'" color="#A35539">[3]</link>',9.5)-22
    y=section(left,y,'AW1 / bedroom wall assemblies',cw)
    y=para(left,y,cw,'Reserve 0.10 m on the marked dry bedroom faces for an independent lining: separated framing, mineral-wool cavity absorption and two gypsum layers, subject to a tested assembly fitting the reserve. Carry the separating wall to structure and seal junctions and penetrations. Keep outlets staggered and avoid rigid bridges through the lining. Wet-side backing and waterproofing are separate requirements. <link href="'+SOURCES['noise']+'" color="#A35539">[1]</link>',10)-12
    y=para(left,y,cw,'Request complete wall and floor test reports. STC describes airborne separation; IIC describes impact transmission through floor/ceiling assemblies. Do not assign either rating from a material name alone. <link href="'+SOURCES['usg']+'" color="#A35539">[2]</link>',9.5,MUTED)-22
    y=section(left,y,'AD1 / stair, service and bedroom doors',cw)
    y=para(left,y,cw,'Use solid-core hinged leaves, robust frames, perimeter seals and compatible drop seals. D1 requires a continuous stair enclosure; D2 closes G3 + G8. Coordinate ventilation paths with the seals. Final leaf/frame ratings and installed clear widths are to be selected. <link href="'+SOURCES['noise']+'" color="#A35539">[1]</link>',10)-22
    y=section(left,y,'AV1 / bedroom windows and quiet ventilation',cw)
    y=para(left,y,cw,'Obtain traffic-noise test data for complete window assemblies, including frames and compression seals. Acoustic laminated glazing is a candidate; its makeup must follow the measured source and solar/thermal requirements. <link href="'+SOURCES['glazing']+'" color="#A35539">[4]</link> Provide quiet ventilation and cooling with windows closed; detail attenuated air paths rather than relying on door gaps. <link href="'+SOURCES['noise']+'" color="#A35539">[1]</link>',10)
    assert y>132, 'Construction left column reaches sources'
    y=section(right,H-139,'AF1 / upper floor, top to bottom',cw)
    # Layer order only: equal graphic bands deliberately avoid invented thicknesses.
    for i,(label,fill) in enumerate([
        ('Tile + compatible bedding / wet-area waterproofing where needed',WOOD),
        ('Impact-isolation system + isolated perimeter joints',ACOUSTIC),
        ('Engineered concrete floor structure / beams to coordinate',HexColor('#D6D9D3')),
        ('Services + isolated ceiling where required / finished ceiling',FLOOR),
    ]):
        yy=y-i*29
        c.setFillColor(fill); c.rect(right,yy-25,cw,25,fill=1,stroke=0)
        txt(right+10,yy-16,label,9,INK)
    y-=129
    y=unit_table(right,y,cw,[dimension_row('Complete floor allowance',HEIGHTS['floor_assembly_allowance'])],rowh=25,size=9)-10
    y=para(right,y,cw,'Layer order only, not a thickness detail. Select a tile-compatible impact system with full floor/ceiling test evidence. Keep rigid edge connections from bypassing it. The 0.40 m total must fit all layers and services; if it cannot, revise the floor level and stair before construction documents. <link href="'+SOURCES['usg']+'" color="#A35539">[2]</link> <link href="'+SOURCES['noise']+'" color="#A35539">[1]</link>',9.5)-20
    y=section(right,y,'AP1 / laundry, plumbing and equipment',cw)
    y=para(right,y,cw,'Select the washer/dryer before service design. G3 + G8 needs appliance-specific heat removal, air supply, clearances and exhaust if applicable; do not seal the machines into an unventilated space. Isolate equipment vibration and pipe supports; locate pumps and condensers away from bedroom walls and neighboring windows. Service and vent routes are not yet drawn. <link href="'+SOURCES['noise']+'" color="#A35539">[1]</link>',9.5)-20
    y=section(right,y,'Finishes and street boundary',cw)
    y=para(right,y,cw,'Rugs, upholstery and selected absorptive surfaces address echo from hard finishes. <link href="'+SOURCES['usg']+'" color="#A35539">[2]</link> Front wall/gate treatment is a later pricing item, after site listening or measurement establishes the traffic exposure. No barrier height or noise reduction is assumed here.',9.5)-20
    y=section(right,y,'Before selecting products',cw)
    y=para(right,y,cw,'Record traffic during busy and quiet periods, including night. Set room-specific noise goals with the local designer, select matching tested assemblies, and obtain itemized quotations. This brief reserves space and defines scope; it is not an engineered acoustic design.',9.5)
    assert y>132, 'Construction right column reaches sources'
    line(48,118,W-48,118)
    for xx,yy,label,url in [(48,99,'[1] YourHome / Noise control',SOURCES['noise']),
                            (624,99,'[2] USG / Acoustics 101',SOURCES['usg']),
                            (48,80,'[3] YourHome / Insulation',SOURCES['insulation']),
                            (624,80,'[4] Pilkington / Acoustic laminated glazing',SOURCES['glazing'])]:
        txt(xx,yy,label,8.5,TERRACOTTA)
        c.linkURL(url,(xx,yy-2,xx+pdfmetrics.stringWidth(label,'HouseRegular',8.5),yy+10),relative=0)
    c.showPage()

def page_schedule():
    header(6,'Area, circulation and budget checks',
           'Metric dimensions govern. Feet are decimal and rounded for reference. Areas are shown in square meters and square feet.')
    left=48; width=518; right=624; rw=W-right-48; y=H-139
    y=section(left,y,'Where the 200 m² lot goes',width)
    y=unit_table(left,y,width,[area_row('Main ground-floor footprint',areas['ground']),area_row('Front parking / entrance',areas['front_zone']),area_row('Nominal side passage',areas['side_passage']),area_row('Rear outdoor zone',areas['rear_zone']),area_row('Total lot allocation',areas['lot'])],rowh=22,headers=('Square meters / m²','Square feet / ft²'))-20
    y=section(left,y,'Approximate internal room sizes',width)
    schedule=[]
    labels=[('G1','Ground queen room'),('G2','Ground shared bath / front'),('G3','Recessed laundry bay'),('G5','Living + dining'),('G4','Kitchen / transition'),('U1','Upper two-double room'),('U2','Open upper shared bathroom'),('U5','Primary bedroom'),('U4','Primary dressing / storage')]
    for ident,label in labels:
        room=next(r for r in rooms if r[0]==ident)
        a,b=room[5:7]
        _,metric,imperial=dimension_row(label,a,b)
        _,metric_area,imperial_area=area_row(label,a*b)
        schedule.append((f'{ident} / {label}',(metric,metric_area),(imperial,imperial_area)))
    y=unit_table(left,y,width,schedule,rowh=33,size=9)-12
    y=para(left,y,width,'Bedroom sizes deduct the 0.10 m lining reserves. These are nominal planning dimensions; final assemblies and finish tolerances may change them. Gross floor area includes partitions. Conversions use unrounded metric values.',9,MUTED)-15
    y=section(left,y,'Privacy and everyday use',width)
    y=para(left,y,width,'Both shared bathrooms include showers. D2 encloses G3 and G8; loading temporarily uses the passage. Bedroom doors receive acoustic seals. Eight guests assumes sharing both double beds; living seating shown is a three-seat sofa and two chairs.',9)
    assert y>65, 'Left schedule column reaches footer'
    y=H-139
    y=section(right,y,'MXN 4 million working target',rw)
    y=table(right,y,rw,[('Construction + site works, residual allowance','2,600,000'),('Design, studies and permits, provisional','300,000'),('Furniture, appliances and linens, provisional','500,000'),('Contingency / 15%','600,000'),('Total, excluding land','4,000,000')],rowh=25)-14
    y=para(right,y,rw,'Unpriced working allocation. Obtain separate quotations for acoustic linings, sealed doors/windows, floor isolation and ventilation. These upgrades are not proven to fit the target. Reprice structure, heights and bathrooms alongside them.',9)-17
    y=section(right,y,'Furniture and stair references',rw)
    references=[dimension_row('Lot / frontage x depth',10,20),
                dimension_row('Queen mattress',1.52,2.03),
                dimension_row('King mattress',2,2),
                dimension_row('Each double mattress',1.35,1.90),
                dimension_row('Dining table / eight seats',2.20,.95),
                dimension_row('Reserved stair zone',STAIR['zone_width'],STAIR['zone_depth']),
                dimension_row('Provisional floor-to-floor',HEIGHTS['floor_to_floor']),
                dimension_row('Riser / 20 total, 10 per flight',STAIR['riser'],precision=3),
                dimension_row('Tread depth',STAIR['tread'],precision=3),
                dimension_row('Run per flight / 9 treads',STAIR['run']),
                dimension_row('Flight / turning landing',STAIR['flight_width']),
                dimension_row('Front arrival landing',STAIR['front_landing'])]
    y=unit_table(right,y,rw,references,rowh=23,size=9)-14
    y=para(right,y,rw,'Stair arithmetic fits the reserved zone. Headroom, guards, finished clear widths, structure and local compliance need professional review. Furniture and cabinetry remain subject to selection and clearance checks.',9,MUTED)
    assert y>65, 'Right schedule column reaches footer'
    c.showPage()

def page_kitchen():
    header(7,'The fridge belongs in the kitchen.',
           'Approved 80 cm appliance allowance / enlarged plan at approximately 1:28 / meter and feet reference columns')
    p=Plan(72,225,scale=100,bx=-3.75,by=-4.55)
    p.rect(3.75,4.55,5.25,4.95,FLOOR,None)
    p.rect(3.95,4.95,1,4.35,HexColor('#E1E9D9'),None)
    p.wall(3.8,4.55,.15,2.2)
    p.wall(6.3,4.8,2.5,.15)
    p.wall(8.8,4.55,.2,4.75)
    p.rect(*KITCHEN['sink_standing'],HexColor('#DFEBEC'),SAGE,.35)
    for x,y,w,h in dining_chairs(pulled=True):
        for a,b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),
                    ((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:
            p.line(*a,*b,TERRACOTTA,.55,[3,2])
    p.table(*DINING_TABLE)
    p.kitchen(detail=True)
    p.text(6.60,8.26,'DINING / 8 SEATS',10,INK,True)
    p.text(6.60,8.04,'2.20 x 0.95 m TABLE',8.4,INK,True)
    p.text(6.0,6.34,'G4 / KITCHEN',10,INK,True)
    p.text(7.42,5.98,'SINK',7.1,MUTED)
    p.text(7.42,5.85,'SPACE',7.1,MUTED)
    p.text(7.23,6.51,'90° OPEN',7.4,TERRACOTTA,True,align='right')
    p.text(6.075,4.68,'COOKTOP',8,INK,True)
    p.text(7.425,4.68,'SINK',8,INK,True)
    p.text(4.45,4.76,'FROM HALL',7.5,SAGE,True)
    p.line(4.45,5.18,4.45,8.75,SAGE,.8)
    p.line(4.45,8.75,4.31,8.51,SAGE,.8)
    p.line(4.45,8.75,4.59,8.51,SAGE,.8)
    p.dimh(3.95,4.95,8.95,'1.00 m NOMINAL')
    p.dimh(5.2,8.8,4.36,'3.60 m COUNTER')
    p.dimh(6.45,7.10,5.74,'0.65 m PREP')
    p.dimv(9.40,5.75,6.65,'0.90 m BAY')
    txt(72,180,'Solid chairs: drawn positions. Dashed chairs: 0.30 m pull-out test.',9,MUTED)
    txt(72,163,'Blue: sink standing test. Terracotta arc: nominal fridge door movement.',9,MUTED)
    para(72,142,530,'The fridge faces left from the right exterior wall. Its dining-side hinge keeps the illustrated 90-degree leaf clear of the long counter. The former hallway-facing fridge position becomes low counter; the short sink return is removed.',9,MUTED)
    x=660; width=W-x-48; y=H-139
    y=section(x,y,'Kitchen dimensions',width)
    y=unit_table(x,y,width,[
        dimension_row('Fridge / selected width allowance',.80),
        dimension_row('Fridge bay / width x projection',.90,.85),
        dimension_row('Long counter / length x depth',3.60,.65),
        dimension_row('Cooktop / footprint',.75,.43),
        dimension_row('Sink / footprint',.65,.43),
        dimension_row('Clear prep / cooktop to sink',.65),
        dimension_row('Through route / drawn chairs',1.00),
        dimension_row('Chair pull-out / test movement',.30),
        dimension_row('Pulled hall chair / remaining route',.70),
        dimension_row('Open leaf to pulled kitchen chair',.10),
    ],rowh=26,size=8.5,label_fraction=.44)-20
    y=section(x,y,'Clearance check / what the plan proves',width)
    y=para(x,y,width,'<b>Fixed fit:</b> the counter, fridge bay and appliance footprints fit G4 and leave the nominal hall-to-living route. The sink standing test clears the fridge body. The 90-degree door clears the cabinets and both drawn and tested pulled-out chairs.',9.2)-14
    y=para(x,y,width,'<b>Everyday use:</b> pulling the hall-side dining chair out 0.30 m temporarily reduces the nominal route to 0.70 m (2.30 ft). A kitchen-side chair in its tested position is only 0.10 m (0.33 ft) from the open fridge leaf. The door sweep shares part of the sink work area; these are not independent workstations during opening.',9.2)-14
    y=para(x,y,width,'<b>Before cabinetry:</b> select the actual refrigerator and verify depth including handles, ventilation, hinge clearance and the opening angle needed for drawers. The 0.90 x 0.85 m bay and 90-degree swing are planning assumptions. Recheck wider opening and actual chair use before fabrication.',9.2)-14
    y=para(x,y,width,'Sink supply, waste and cooktop services move with the appliances; coordinate their routes with the stair wall, structure and acoustic details.',8.6,MUTED)
    assert y>65, 'Kitchen notes collide with footer'
    c.showPage()

def page_appearance():
    header(8,'The same warm architectural character',
           'Updated front and rear views / current opening layout, adopted floor heights and compact outdoor spaces')
    image_size=425; gutter=20; top=H-136
    imageleft=(W-2*image_size-gutter)/2
    for i,(filename,label) in enumerate([
        ('front-updated.png','STREET / FRONT COURT'),
        ('rear-updated.png','REAR / COVERED TERRACE')]):
        xx=imageleft+i*(image_size+gutter)
        ir=ImageReader(str(ROOT/filename))
        txt(xx,top+9,label,8.5,TERRACOTTA,True)
        c.drawImage(ir,xx,top-image_size,width=image_size,height=image_size,
                    preserveAspectRatio=True,anchor='c',mask='auto')
    y=top-image_size-12
    y=para(48,y,W-96,'Front parking fit and rear kitchen interior updated from the current plans. Dimensioned plans govern; perspective, furnishings and planting are illustrative. Parking gaps are nominal before gate hardware. Roof/parapet, window heights and site levels remain to be detailed.',8.5,MUTED,leading=11.5)-15
    colw=(W-120)/2
    for xx,title,rows in [
        (48,'FRONT COURT / PARKING CLEARANCES',[
            dimension_row('Gate line to house',PARKING['court_depth']),
            dimension_row('Car length / planning allowance',PARKING['car'][3]),
            dimension_row('Rear bumper to gate line',PARKING['gate_gap']),
            dimension_row('Front bumper to house',PARKING['house_gap'])]),
        (72+colw,'FOOTPRINTS / REAR TERRACE',[
            dimension_row('Ground floor envelope',9,10.5),
            dimension_row('Upper floor envelope',9,9.5),
            dimension_row('Upper rear setback',1),
            dimension_row('Covered terrace',6,3)])]:
        yy=section(xx,y,title,colw)
        bottom=unit_table(xx,yy,colw,rows,label_fraction=.43,rowh=21,size=8.6)
        assert bottom>75, 'Appearance table collides with footer notes'
    para(48,77,W-96,'Open terracotta screen spans both stories, with separate stair windows behind it. Supports, drainage and inward-opening cleaning access need detailing. Screen and slatted gate do not establish acoustic performance.',7.4,MUTED,leading=9)
    c.showPage()

def verify_geometry():
    assert isclose(94.5+55+10.5+40,200)
    assert isclose(STAIR['risers']*STAIR['riser'],HEIGHTS['floor_to_floor'])
    assert STAIR['risers']==2*STAIR['risers_per_flight']==20
    assert isclose(STAIR['riser'],.17) and isclose(STAIR['run'],2.52)
    assert isclose(HEIGHTS['ground_clear']+HEIGHTS['floor_assembly_allowance'],HEIGHTS['floor_to_floor'])
    assert isclose(HEIGHTS['upper_ceiling_level'],6.2)
    assert STAIR['front_landing']+STAIR['run']+STAIR['turn_landing']<=STAIR['zone_depth']
    assert STAIR['run']+STAIR['turn_landing']<=STAIR['opening_depth']
    assert STAIR['start_y']+STAIR['opening_depth']<=.2+STAIR['zone_depth']
    assert isclose(2*STAIR['flight_width']+.15,STAIR['opening_width'])
    assert isclose(void,8.0775)
    assert isclose(2600000+300000+500000+600000,4000000)
    baths=[r for r in rooms if 'bathroom' in r[1]]
    assert len(baths)==2 and {r[2] for r in baths}=={'Ground','Upper'}
    assert len([r for r in rooms if 'bedroom' in r[1]])==3
    downstairs_bath=next(r for r in rooms if r[0]=='G2')
    kitchen=next(r for r in rooms if r[0]=='G4')
    bathroom_to_kitchen_gap=kitchen[4]-(downstairs_bath[4]+downstairs_bath[6]+.15)
    assert isclose(bathroom_to_kitchen_gap,2.3)
    laundry=next(r for r in rooms if r[0]=='G3')
    passage=next(r for r in rooms if r[0]=='G8')
    hall=next(r for r in rooms if r[0]=='G6')
    assert isclose(passage[6],1.0)
    assert isclose(laundry[4]+laundry[6],passage[4])
    assert isclose(laundry[3],passage[3]) and isclose(laundry[5],passage[5])
    assert isclose(downstairs_bath[3]+downstairs_bath[5]+.15,passage[3])
    assert isclose(passage[3]+passage[5]+.15,hall[3])
    assert passage[4]<=1.6 and 1.6+.85<=passage[4]+passage[6]
    assert .35+.85 < passage[4]  # Recessed stack does not occupy the passage.
    assert isclose(2*2.3+1.45*1.3+1.45*1+.15*2.3,3.6*2.3)
    upper_bath=next(r for r in rooms if r[0]=='U2')
    fixture_items=list(UPPER_BATH_FIXTURES.items())
    door_sweep=(UPPER_BATH_DOOR['x']-UPPER_BATH_DOOR['width'],
                UPPER_BATH_DOOR['y'],UPPER_BATH_DOOR['width'],UPPER_BATH_DOOR['width'])
    def overlap(a,b):
        return min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])>1e-8 and min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])>1e-8
    for i,(name,rect) in enumerate(fixture_items):
        x,y,w,h=rect
        assert x>=upper_bath[3] and y>=upper_bath[4]
        assert x+w<=upper_bath[3]+upper_bath[5]+1e-8
        assert y+h<=upper_bath[4]+upper_bath[6]+1e-8
        assert not overlap(rect,door_sweep),f'Upper door swing intersects {name}'
        for other_name,other_rect in fixture_items[i+1:]:
            assert not overlap(rect,other_rect),(name,other_name)
    assert isclose(UPPER_SHOWER_ENTRY[1]-UPPER_SHOWER_ENTRY[0],.9)
    assert UPPER_BATH_FIXTURES['shower'][0] < UPPER_BATH_FIXTURES['toilet'][0] < UPPER_BATH_DOOR['x']
    upper_dry_gap=UPPER_BATH_FIXTURES['toilet'][1]-(UPPER_BATH_FIXTURES['double_vanity'][1]+UPPER_BATH_FIXTURES['double_vanity'][3])
    assert isclose(upper_dry_gap,.97)
    for ident,name,floor,x,y,w,h in rooms:
        assert x>=.2-1e-8 and y>=.2-1e-8
        assert x+w<=8.8+1e-8 and y+h<=(10.3 if floor=='Ground' else 9.3)+1e-8, ident
    primary=next(r for r in rooms if r[0]=='U5')
    assert primary[3]<=6.65 and primary[4]<=6.15
    assert 6.65+2<=primary[3]+primary[5] and 6.15+2<=primary[4]+primary[6]
    for x,y,w,h in [KITCHEN['counter'],KITCHEN['fridge_bay']]:
        assert x>=kitchen[3] and y>=kitchen[4]
        assert x+w<=kitchen[3]+kitchen[5]+1e-8 and y+h<=kitchen[4]+kitchen[6]+1e-8
    def contains(outer,inner):
        x,y,w,h=outer; a,b,cw,ch=inner
        return x-1e-8<=a and y-1e-8<=b and a+cw<=x+w+1e-8 and b+ch<=y+h+1e-8
    assert contains(KITCHEN['counter'],KITCHEN['cooktop'])
    assert contains(KITCHEN['counter'],KITCHEN['sink'])
    assert contains(KITCHEN['fridge_bay'],KITCHEN['fridge_body'])
    assert isclose(KITCHEN['sink'][0]-sum((KITCHEN['cooktop'][0],KITCHEN['cooktop'][2])),.65)
    assert not overlap(KITCHEN['counter'],KITCHEN['fridge_bay'])
    assert not overlap(KITCHEN['sink_standing'],KITCHEN['fridge_bay'])
    # Conservative bounding box contains the complete quarter-circle door sweep.
    for rect in [KITCHEN['counter'],DINING_TABLE]+dining_chairs()+dining_chairs(pulled=True):
        assert not overlap(FRIDGE_DOOR['sweep_bounds'],rect), 'Fridge door intersects fixed / tested furniture'
    for fixture in [KITCHEN['counter'],KITCHEN['fridge_bay']]:
        assert not overlap(fixture,KITCHEN['through_route'])
        for chair in dining_chairs()+dining_chairs(pulled=True):
            assert not overlap(fixture,chair), 'Fridge / counter intersects tested chair'
    assert isclose(dining_chairs(pulled=True)[-2][0]-KITCHEN['through_route'][0],.70)
    assert isclose(dining_chairs(pulled=True)[0][1]-FRIDGE_DOOR['hinge'][1],.10)
    # An actual point lies inside both the sink standing area and the door sector.
    assert contains(KITCHEN['sink_standing'],(7.6,6.2,0,0))
    assert (7.6-8.03)**2+(6.2-6.6)**2 < FRIDGE_DOOR['width']**2
    assert isclose(PARKING['gate_gap']+PARKING['car'][3]+PARKING['house_gap'],PARKING['court_depth'])
    # Zone rectangles should be disjoint on each level.
    for i,a in enumerate(rooms):
        for b in rooms[i+1:]:
            if a[2]!=b[2]: continue
            dx=min(a[3]+a[5],b[3]+b[5])-max(a[3],b[3])
            dy=min(a[4]+a[6],b[4]+b[6])-max(a[4],b[4])
            assert dx<=1e-8 or dy<=1e-8,(a[0],b[0])
    # Check the changed physical relationships, not just drawing labels.
    door_sweeps = {
        'D0_front': (4.10,.10,1.00,1.00),
        'D1_stair': (6.225-.90,.25,.90,.90),
        'D2_service': (3.875,1.55,.90,.90),
    }
    for i,(name,rect) in enumerate(door_sweeps.items()):
        for other,other_rect in list(door_sweeps.items())[i+1:]:
            assert not overlap(rect,other_rect), (name,other)
    assert isclose(door_sweeps['D1_stair'][0]-(4.10+1.00),.225)
    assert door_sweeps['D1_stair'][0]+.9 < 6.3  # No leaf sweep in stair landing.
    assert door_sweeps['D2_service'][0]>=passage[3]+passage[5]
    assert 1.5<=DOORS['D2_service']['y'] and DOORS['D2_service']['y']+.9<=2.5
    for name,rect in LIVING_FURNITURE.items():
        assert .2<=rect[0] and 6.9<=rect[1]
        assert rect[0]+rect[2]<=8.8 and rect[1]+rect[3]<=10.3
        assert not overlap(rect,LIVING_ROUTE), name
    furniture_items=[(n,r) for n,r in LIVING_FURNITURE.items() if n!='tv']
    for i,(name,rect) in enumerate(furniture_items):
        for other,other_rect in furniture_items[i+1:]:
            assert not overlap(rect,other_rect),(name,other)
    assert isclose(5.5-.55-(LIVING_ROUTE[0]+LIVING_ROUTE[2]),0)
    assert 7.55+.95+.12+.43 <= REAR_ROUTE[1]  # Rear dining chairs stop short of the turn.
    assert LIVING_FURNITURE['tv'][0] < .3 and LIVING_FURNITURE['tv'][1]>7.5
    bedroom_furniture={
        'G1': [(1.4,4.42,1.52,2.03),(.2,2.95,.6,1.25)],
        'U1': [(.8,4.55,1.35,1.9),(2.85,4.55,1.35,1.9),(.35,2.75,3.05,.6)],
        'U5': [(6.65,6.15,2,2),(8.1,5.57,.55,.48),(8.1,8.25,.55,.48)],
    }
    bedroom_sweeps={'G1':(2.8,3,.9,.9),'U1':(3.8,3.4,.9,.9),'U5':(5.05,5.05,.9,.9)}
    for ident,fixtures in bedroom_furniture.items():
        r=next(r for r in rooms if r[0]==ident)
        for x,y,w,h in fixtures:
            assert x>=r[3]-1e-8 and y>=r[4]-1e-8, ident
            assert x+w<=r[3]+r[5]+1e-8 and y+h<=r[4]+r[6]+1e-8, ident
            assert not overlap((x,y,w,h),bedroom_sweeps[ident]), ident
    payload={'units':'meters; areas in square meters','areas':areas,
             'heights_m':HEIGHTS,'heights_feet_reference':{key:feet(value) for key,value in HEIGHTS.items()},
             'stair_design':STAIR,
             'vertical_design_notes':['Ground finished floor is a relative datum, not a surveyed site elevation','0.40 m floor assembly allowance is not a slab thickness specification','Roof build-up and parapet height remain unassigned','Final headroom, structure, guards and local compliance require professional review'],
             'reference_conversion':{'meters_per_foot':METERS_PER_FOOT,'feet_format':'decimal','rounding':'display only; metric dimensions govern'},
             'areas_square_feet_reference':{key:square_feet(value) for key,value in areas.items()},
             'rooms':[{'id':i,'name':n,'floor':f,'rect':[x,y,w,h],'area':w*h,'dimensions_feet_reference':[feet(w),feet(h)],'area_square_feet_reference':square_feet(w*h)} for i,n,f,x,y,w,h in rooms],
             'bathroom_count':2,'bedroom_count':3,'downstairs_bath_wall_to_kitchen_zone_gap_m':bathroom_to_kitchen_gap,
             'service_access':{'route':['G6 entry hall','D2 service door','G8 enclosed service passage','G2 bathroom'],'laundry_access':'G3 alcove opens to G8 inside the D2 acoustic enclosure','passage_width_m':passage[6],'passage_width_ft':feet(passage[6]),'hall_door_nominal_m':.90,'bathroom_door_opening_m':.85,'laundry_type':'stacked washer/dryer in G3 + G8 enclosed service vestibule','ventilation':'appliance-specific ventilation and heat/exhaust routes to design','exterior_laundry_door':False},
             'acoustic_design':{'status':'space reservations and design requirements; no tested performance selected',
                                'main_external_source':'potential street traffic; general noise control',
                                'lining_reserve_m':LINING_RESERVE,'linings_m':LININGS,
                                'doors':DOORS,'door_sweep_rectangles_m':door_sweeps,
                                'living_furniture_m':LIVING_FURNITURE,'living_route_m':LIVING_ROUTE,'rear_route_m':REAR_ROUTE,
                                'floor_layers':['tile and bedding / wet-area waterproofing','compatible impact-isolation system and isolated perimeter','engineered concrete structure','services and isolated ceiling where required'],
                                'floor_layer_thicknesses':'not determined; total allowance 0.40 m',
                                'sources':SOURCES},
             'upper_bathroom':{'private_toilet_compartment':False,'toilet_count':1,'bathing_fixture':'walk-in shower','shower_position':'far end opposite the hall door; left in plan','fixtures_m':UPPER_BATH_FIXTURES,'fixture_dimensions_ft':{name:[feet(r[2]),feet(r[3])] for name,r in fixture_items},'door':UPPER_BATH_DOOR,'shower_entry_m':.9,'nominal_toilet_front_to_vanity_gap_m':upper_dry_gap},
             'checks':['three bedrooms and two full bathrooms, one bathroom per floor','downstairs bathroom has no shared kitchen wall; 2.3 m plan-depth separation','lot allocation reconciles','room rectangles inside floor envelopes','room rectangles do not overlap','service-area rectangles and partition reconcile','passage connects hall, bath opening and laundry bay','stacked appliance footprint stays outside passage','upper bathroom fixture rectangles fit and do not overlap','upper bathroom door swing is clear of fixture rectangles','20 stair risers resolve the 3.40 m height','stair flights and landings fit the enlarged bay and opening','king bed remains inside the revised primary room','shifted kitchen cabinets remain in the revised kitchen zone','floor and ceiling levels reconcile','budget allocation reconciles'],
             'not_verified':['parcel buildability','structural adequacy','code compliance','stair headroom','actual local construction cost','finished floor level','flood exposure','utility capacity','measured street noise','installed acoustic performance','selected wall/floor/window assemblies','appliance ventilation and exhaust routes','finished door clear openings and hardware']}
    payload['checks'] += ['new entrance door sweep envelopes do not overlap','D1 sweep stays outside stair landing','D2 sweep stays outside G8','living furniture fits and leaves nominal 1 m route beside dining furniture','bedroom furniture fits after lining reserves','bedroom door sweeps clear shown furniture']
    payload['kitchen_revision']={
        'rectangles_m':KITCHEN,'fridge_door':FRIDGE_DOOR,'dining_table_m':DINING_TABLE,
        'dining_chairs_drawn_m':dining_chairs(),'dining_chairs_pulled_m':dining_chairs(pulled=True),
        'chair_pull_out_test_m':CHAIR_PULL_OUT,'route_with_hall_chair_pulled_m':.70,
        'open_leaf_to_kitchen_chair_pulled_m':.10,'sink_work_area_overlaps_door_sweep':True,
        'appliance_width_selected_m':.80,'appliance_model_selected':False,
        'services':'relocate sink and cooktop connections; coordinate routes before cabinetry',
        'not_verified':['actual appliance installation clearances','full opening angle for drawer removal','simultaneous sink and fridge use','actual chair pull-out and occupied body clearances']}
    payload['parking_revision']=PARKING
    payload['checks'] += ['approved kitchen coordinates retained','fridge and counter do not overlap','appliances contained in counter and reserved bay','0.65 m cooktop-to-sink preparation surface','fridge 90 degree sweep clears fixed cabinets and chairs with 0.30 m pull-out','chair pull-out route reduction and shared sink work area documented','front court reconciles 0.55 + 4.50 + 0.45 = 5.50 m']
    (ROOT/'area-schedule.json').write_text(json.dumps(payload,indent=2)+'\n')

if __name__=='__main__':
    verify_geometry()
    page_plans(); page_service_detail(); page_heights(); page_acoustic_details(); page_construction(); page_schedule(); page_kitchen(); page_appearance(); c.save()
    print(json.dumps({'pdf':str(OUT),'pages':8,'combined_floor_area_m2':round(areas['combined_floor'],1),'terrace_m2':18}))
