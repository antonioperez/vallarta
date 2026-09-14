"""Perspective control views from the actual plan envelopes, for rendering input."""
from pathlib import Path
from math import sqrt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import json, subprocess, shutil

ROOT=Path(__file__).resolve().parent
TMP=Path('/private/tmp/las-juntas-massing-08'); TMP.mkdir(exist_ok=True)
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a):
 n=sqrt(dot(a,a)); return tuple(x/n for x in a)

class Scene:
 def __init__(self,camera,target,focal=1050):
  self.camera=camera; self.forward=norm(sub(target,camera)); self.right=norm(cross(self.forward,(0,0,1))); self.up=cross(self.right,self.forward); self.faces=[]; self.focal=focal
 def face(self,points,color,stage=0):
  normal=cross(sub(points[1],points[0]),sub(points[2],points[0]))
  if dot(normal,sub(self.camera,points[0]))>0: self.faces.append((points,color,stage))
 def box(self,x,y,z,w,d,h,color,stage=0):
  self.face([(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)],color,stage)
  self.face([(x,y+d,z+h),(x+w,y+d,z+h),(x+w,y+d,z),(x,y+d,z)],color,stage)
  self.face([(x,y,z+h),(x,y+d,z+h),(x,y+d,z),(x,y,z)],color,stage)
  self.face([(x+w,y,z),(x+w,y+d,z),(x+w,y+d,z+h),(x+w,y,z+h)],color,stage)
  self.face([(x,y,z+h),(x+w,y,z+h),(x+w,y+d,z+h),(x,y+d,z+h)],'#E8DEC9' if color=='#E4D4B9' else color,stage)
  self.face([(x,y+d,z),(x+w,y+d,z),(x+w,y,z),(x,y,z)],color,stage)
 def glass(self,x,y,z,w,h):
  if (y>10)!=(self.camera[1]>10): return
  points=[(x,y,z),(x+w,y,z),(x+w,y,z+h),(x,y,z+h)]
  if y>10: points.reverse()
  self.face(points,'#85ADB4',10)
  self.box(x+w/2-.02,y-.015,z,.04,.03,h,'#324640',11)
 def point(self,p):
  v=sub(p,self.camera); depth=dot(v,self.forward)
  return (600+self.focal*dot(v,self.right)/depth,620+self.focal*dot(v,self.up)/depth)
 def draw(self,name,title,notes):
  out=TMP/(name+'.pdf'); c=canvas.Canvas(str(out),pagesize=(1200,1200))
  c.setFillColor(HexColor('#FCFAF5')); c.rect(0,0,1200,1200,fill=1,stroke=0)
  for vertices,color,stage in sorted(self.faces,key=lambda f:(f[2],-sum(dot(sub(p,self.camera),self.forward) for p in f[0])/len(f[0]))):
   points=[self.point(p) for p in vertices]
   c.setFillColor(HexColor(color)); c.setStrokeColor(HexColor('#5D6259')); c.setLineWidth(.7)
   p=c.beginPath(); p.moveTo(*points[0])
   for xy in points[1:]: p.lineTo(*xy)
   p.close(); c.drawPath(p,fill=1,stroke=1)
  c.setFillColor(HexColor('#293A36')); c.setFont('Helvetica-Bold',18); c.drawString(50,1150,title)
  c.setFont('Helvetica',12)
  for i,t in enumerate(notes): c.drawString(50,95-i*19,t)
  c.save()
  subprocess.run(['/Users/antonioperez/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm','-singlefile','-r','100','-png',str(out),str(TMP/name)],check=True)
  shutil.copyfile(TMP/(name+'.png'),ROOT/(name+'.png'))

def building(s):
 s.box(1,5.5,0,9,10.5,3.4,'#E4D4B9')
 s.box(1,5.5,3.4,9,9.5,3.3,'#E4D4B9')
 # All plan-dimensioned front openings, rendering-only sill/head assumptions.
 g=json.loads((ROOT/'rendering-geometry.json').read_text())
 for key,(x,z,w,h) in g['front_openings_x_z_w_h'].items():
  if key=='entry': s.face([(x,5.485,z),(x+w,5.485,z),(x+w,5.485,z+h),(x,5.485,z+h)],'#88623E',10)
  else: s.glass(x,5.48,z,w,h)
 # Rear mirrored coordinates converted back to global x.
 for key,(x,z,w,h) in g['rear_openings_x_z_w_h'].items():
  s.glass(10-x-w,15.02 if key.startswith('upper') else 16.02,z,w,h)
 # Six by three terrace and its slim canopy, all in plan coordinates.
 s.box(3,16,-.06,6,3,.06,'#C9B08D')
 if s.camera[1]>20:
  s.box(3,16,2.65,6,3,.20,'#7C7461',20)
  for x in [3.15,8.85]: s.box(x-.06,18.87,0,.12,.12,2.65,'#3E4943',21)
 # Exterior screen, open grid as placeholder for flower-pattern clay blocks.
 if s.camera[1]<0:
  for i in range(9): s.box(7.5+i*2.15/8-.025,5.10,.55,.05,.12,5.65,'#B25F3D',20)
  for j in range(21): s.box(7.5,5.10,.55+j*5.65/20-.025,2.15,.12,.05,'#B25F3D',20)

front=Scene((-2.8,-8.0,3.1),(4.7,6.0,2.5),focal=1000)
front.face([(0,0,-.07),(10,0,-.07),(10,20,-.07),(0,20,-.07)],'#D4DCC6',-10)
front.face([(0,0,-.065),(10,0,-.065),(10,5.5,-.065),(0,5.5,-.065)],'#D8CBB6',-9)
building(front)
front.box(1.8,.55,.25,1.85,4.5,.55,'#AFB9B6',30)
front.box(1.92,1.55,.8,1.61,2.35,.65,'#AFB9B6',31)
front.box(.0,-.08,-.02,10,.08,.025,'#324640',40)
for x in [.75,4.1,7.95,9.2]: front.box(x,-.12,0,.15,.18,1.85,'#BDAF92',40)
for z in [.12,.34,.56,.78,1.0,1.22,1.44,1.66]:
 front.box(4.25,-.07,z,3.05,.08,.11,'#4B514A',40)
front.draw('front-massing-guide','FRONT / 4.50 m car almost fills the 5.50 m court',[
 'Parking depth: street / gate line | 0.55 m gap | 4.50 m car | 0.45 m gap | house facade.',
 'Gate opening is 3.20 m at left; gate slides sideways. No steps or planting in the car footprint or end gaps.',
 'Car width 1.85 m. Low steps and planting belong at the pedestrian entry to the right. Roof cap is illustrative.'])

rear=Scene((5.7,25.5,2.0),(5.5,15.0,2.65),focal=850)
rear.face([(0,15,-.07),(10,15,-.07),(10,20,-.07),(0,20,-.07)],'#CCD8B8',-10)
building(rear)
rear.draw('rear-massing-guide','REAR / measured upper setback and terrace canopy',[
 'Upper rear wall y=15; lower rear wall y=16: 1.00 m setback. Canopy x=3..9, y=16..19: 6.00 x 3.00 m.',
 'Rear boundary y=20: only 1.00 m remains beyond canopy. Upper window and lower sliding doors on VIEWER LEFT.',
 'Upper wall on VIEWER RIGHT is solid. Drawing is geometry guidance, not a finish or landscape design.'])
print('Perspective massing guides saved.')
