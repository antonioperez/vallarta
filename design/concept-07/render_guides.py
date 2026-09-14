"""Measured facade guides for concept imagery, not construction elevations."""
from pathlib import Path
import json, subprocess, shutil
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parent
CREAM='#E5DAC5'; INK='#293A36'; GLASS='#AFCACC'; CLAY='#AB593B'
FRONT={
 'ground_bath': [1.4,1.60,.85,.70], 'ground_laundry': [4.25,1.40,.45,.90],
 'entry': [5.10,0,1.00,2.45], 'ground_stair': [7.8,1.10,1.65,1.50],
 'upper_bath_1': [1.4,5.00,.70,.70], 'upper_bath_2': [3.6,5.00,.90,.70],
 'upper_stair': [7.8,4.50,1.65,1.50],
}
REAR={'ground_sliding_door': [.90,0,3.20,2.50], 'ground_living_window': [5.45,.60,2.90,1.90], 'upper_primary_window': [.75,4.25,3.05,1.70]}
S=85; OX=115; OY=170; W=1150; H=845
TEMP=Path('/private/tmp/las-juntas-render-guides'); TEMP.mkdir(exist_ok=True)
PDF=TEMP/'facades.pdf'; c=canvas.Canvas(str(PDF),pagesize=(W,H))
def xy(x,z): return OX+x*S, OY+z*S
def box(rect,color,edge=INK,lw=1):
 x,z,w,h=rect; c.setFillColor(HexColor(color)); c.setStrokeColor(HexColor(edge)); c.setLineWidth(lw)
 c.rect(*xy(x,z),w*S,h*S,fill=1,stroke=1)
def line(x1,z1,x2,z2,color=INK,lw=1,dash=None):
 c.saveState(); c.setStrokeColor(HexColor(color)); c.setLineWidth(lw)
 if dash: c.setDash(dash)
 c.line(*xy(x1,z1),*xy(x2,z2)); c.restoreState()
def text(x,z,label,size=10,color=INK,rotate=0):
 c.saveState(); c.translate(*xy(x,z)); c.rotate(rotate); c.setFillColor(HexColor(color)); c.setFont('Helvetica',size); c.drawCentredString(0,0,label); c.restoreState()
def setup(title):
 c.setFillColor(HexColor('#FCFAF5')); c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor(INK)); c.setFont('Helvetica-Bold',19); c.drawString(50,H-50,title)
def dims():
 for z,label in [(0,'Ground datum 0.00 m'),(3,'Ground ceiling 3.00 m'),(3.4,'Upper floor 3.40 m'),(6.2,'Upper ceiling 6.20 m')]:
  line(-.3,z,10.6,z,'#78857E',.65,[4,4]); text(10.95,z,label,8,rotate=90)
 line(0,-.45,10,-.45)
 for x in [0,10]: line(x,-.52,x,-.38)
 text(5,-.73,'10.00 m lot width',12)

setup('FRONT / looking from street / geometry controls the render')
box([1,0,9,6.7],CREAM)
text(.48,3,'1 m side passage',12,rotate=90)
for key,r in FRONT.items():
 box(r,'#8B6040' if key=='entry' else GLASS)
 if 'stair' in key: line(r[0]+r[2]/2,r[1],r[0]+r[2]/2,r[1]+r[3])
 else: text(r[0]+r[2]/2,r[1]+r[3]+.13,key.replace('_',' '),8)
for i in range(9): line(7.5+i*2.15/8,.55,7.5+i*2.15/8,6.2,CLAY,2)
for j in range(21): line(7.5,.55+j*5.65/20,9.65,.55+j*5.65/20,CLAY,2)
text(8.575,6.92,'Open clay screen; glass behind',10,CLAY)
dims()
text(5,-1.15,'Front court depth 5.50 m. One car left; pedestrian entry right.',11)
text(5,-1.42,'Window sill/head heights and roof cap are illustrative; horizontal openings follow the plan.',10)
c.showPage()
setup('REAR / looking from garden / left-right reverses relative to plan')
box([0,0,9,3.4],CREAM); box([0,3.4,9,3.3],CREAM)
text(9.5,3,'1 m side passage',12,rotate=90)
for key,r in REAR.items():
 box(r,GLASS); line(r[0]+r[2]/2,r[1],r[0]+r[2]/2,r[1]+r[3])
 text(r[0]+r[2]/2,r[1]+r[3]+.13,key.replace('_',' '),8)
text(6.15,5.05,'DRESSING / SOLID REAR WALL',12)
text(4.5,3.82,'Upper rear wall is set back 1.00 m behind the lower rear wall',11)
box([1,2.65,6,.20],'#6F6658')
for x in [1.15,6.85]: box([x-.06,0,.12,2.65],'#444945')
text(4,2.25,'6.00 m x 3.00 m covered terrace',12)
dims()
text(5,-1.15,'Rear yard depth 4.00 m total: canopy 3.00 m + remaining 1.00 m planting strip.',11)
text(5,-1.42,'No roof balcony. Window/roof/canopy heights are illustrative, not adopted dimensions.',10)
c.showPage(); c.save()
subprocess.run(['/Users/antonioperez/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm','-r','120','-png',str(PDF),str(TEMP/'guide')],check=True)
for num,view in [(1,'front'),(2,'rear')]: shutil.copyfile(TEMP/f'guide-{num}.png',ROOT/f'{view}-elevation-guide.png')
(ROOT/'rendering-geometry.json').write_text(json.dumps({
 'coordinate_basis':'Front x uses lot coordinates from street-left; rear x uses distance from building-left as seen from garden. z is relative to ground finished floor.',
 'adopted':{'lot':[10,20],'ground_envelope':[9,10.5],'upper_envelope':[9,9.5],'ground_clear':3,'upper_clear':2.8,'floor_to_floor':3.4,'upper_ceiling_level':6.2,'front_court_depth':5.5,'rear_zone_depth':4,'rear_upper_setback':1,'terrace':[6,3]},
 'front_openings_x_z_w_h':FRONT,'rear_openings_x_z_w_h':REAR,
 'visual_assumptions_only':{'roof_cap_level':6.7,'screen_front_x_z_w_h':[7.5,.55,2.15,5.65],'canopy_soffit':2.65,'canopy_top':2.85,'opening_sill_head_heights':'all provisional, as shown in coordinate records','ground_above_grade':'not established'},
 'screen_direction':'Open terracotta screen spanning both stories, with two separate inward-opening stair-window groups behind. Support, drainage, insect screens and cleaning clearances still to detail.'
},indent=2)+'\n')
print('Wrote front/rear facade guides and rendering geometry record.')
