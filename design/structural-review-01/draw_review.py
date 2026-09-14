"""Plot existing architectural wall alignment. No structure or member sizes proposed."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
ROOT=Path(__file__).parent
walls=json.loads((ROOT/'wall-geometry-reviewed.json').read_text())
schedule=json.loads((ROOT.parent/'concept-14/area-schedule.json').read_text())
style=json.loads((ROOT.parent/'concept-14/selected-style-geometry.json').read_text())
fig=plt.figure(figsize=(13.6,9),facecolor='#fcfaf5')
ax=fig.add_axes([.065,.13,.47,.73]); ax.set_facecolor('#fcfaf5')
ground='#79877f';upper='#ad563a';muted='#56655f';ink='#293a36'
ax.add_patch(Rectangle((0,0),9,10.5,facecolor='#f2ece0',edgecolor='none'))
# The full wall footprint includes material above doors/windows. Floor-level openings
# are highlighted in white, so a drawn wall is never mistaken for a solid shear panel.
for floor,color,fill in [('ground',ground,True),('upper',upper,False)]:
 for w in walls['walls'][floor]:
  if w.get('lining'):continue
  x,y,dx,dy=w['rect'];horizontal=dx>dy
  ax.add_patch(Rectangle((x,y),dx,dy,facecolor=color if fill else 'none',edgecolor=color,
                         linewidth=.9 if fill else 1.5,linestyle='-' if fill else (0,(4,2)),alpha=.7 if fill else 1,zorder=2 if fill else 4))
  for o in w.get('openings',[]):
   if o['kind']!='door':continue
   if horizontal:
    xx,yy,ww,hh=o['start'],y,o['width'],dy
   else:xx,yy,ww,hh=x,o['start'],dx,o['width']
   ax.add_patch(Rectangle((xx,yy),ww,hh,facecolor='#fcfaf5',edgecolor=color,linewidth=.45,zorder=3 if fill else 5))
# Retain scale context from the approved kitchen and dining geometry.
k=schedule['kitchen_revision']
for r in [k['rectangles_m'][n] for n in ['counter','return','fridge_body']]+[k['dining_table_m']]:
 ax.add_patch(Rectangle(r[:2],r[2],r[3],facecolor='#ddc8a8',edgecolor='#8f826e',linewidth=.5,zorder=1))
ax.add_patch(Rectangle((2,10.5),6,3,facecolor='#eee2c9',edgecolor=ground,linewidth=.9,zorder=1))
for px,py,w,h in style['rear_canopy_columns_lot_xywh']:
 ax.add_patch(Rectangle((px-1,py-5.8),w,h,facecolor=ground,zorder=3))
ax.text(4.9,12.05,'CLAY TERRACE ROOF',ha='center',fontsize=9,color=ink)
ax.text(2.35,8.2,'OPEN LIVING / DINING',ha='center',fontsize=8,color=muted)
vx,vy,vw,vd=walls['stairVoid']
ax.add_patch(Rectangle((vx,vy),vw,vd,facecolor='#e2e5e0',edgecolor=muted,
                       linewidth=.7,linestyle=':',alpha=.65,zorder=1))
ax.text(7.5,2.5,'STAIR VOID',ha='center',fontsize=8,color=muted)
ax.text(7.5,2.25,'2.25 x 3.59 m',ha='center',fontsize=7,color=muted)
ax.axvline(9,color='#9b3738',linewidth=1.6,zorder=7)
ax.text(9.16,6.7,'RIGHT LOT BOUNDARY / NO GAP DRAWN',rotation=90,fontsize=8,color='#9b3738',va='center')
ax.annotate('',xy=(3.875,5.9),xytext=(4.875,5.9),arrowprops={'arrowstyle':'<->','lw':1,'color':ink})
ax.text(4.375,6.13,'1.00 m',ha='center',fontsize=9,color=ink)
ax.annotate('',xy=(2.5,9.4),xytext=(2.5,10.4),arrowprops={'arrowstyle':'<->','lw':1,'color':ink})
ax.text(2.67,9.84,'1.00 m',fontsize=8,color=ink)
for n,x,y in [(1,8.75,6.15),(2,4.875,4.0),(3,4.5,9.4),(4,7.5,3.6),(5,3.0,.1),(6,5.0,13.3)]:
 ax.text(x,y,str(n),ha='center',va='center',fontsize=10,color='white',fontweight='bold',zorder=10,bbox={'boxstyle':'circle,pad=.26','fc':upper,'ec':'white','lw':1})
ax.set_xlim(-.4,9.65);ax.set_ylim(-.65,13.9);ax.set_aspect('equal')
ax.set_xticks([0,2,4,6,8]);ax.set_yticks([0,2,4,6,8,10,12]);ax.tick_params(labelsize=8,colors=muted)
ax.set_xlabel('Building-local x / meters',fontsize=9,color=muted)
ax.set_ylabel('Depth from front of building / meters',fontsize=9,color=muted)
for sp in ax.spines.values():sp.set_visible(False)
ax.text(4.5,-.55,'FRONT / TOWARD STREET',ha='center',fontsize=8,color=muted)
fig.text(.065,.945,'LAS JUNTAS  /  CONCEPT 14 REVIEW',fontsize=10,color=upper,weight='bold')
fig.text(.065,.90,'The load path is not defined yet.',fontsize=24,color=ink,weight='bold')
fig.legend(handles=[Line2D([0],[0],color=ground,lw=6,label='Ground wall footprint'),Line2D([0],[0],color=upper,lw=1.5,ls='--',label='Upper wall projected down')],loc='upper left',bbox_to_anchor=(.58,.87),frameon=False,fontsize=9)
notes=[
 ('1  Boundary separation', 'Right wall and main roof reach the lot line.\nResolve the required seismic gap before fixing width.'),
 ('2  Offset upper partition', 'Upper x=4.80 m; ground x=3.80 m: a 1.00 m offset.\nNo beam or designed slab support is documented.'),
 ('3  Upper rear wall over open space', 'Upper rear wall is 1.00 m ahead of the ground rear wall.\nIts support must be designed independently of the facade.'),
 ('4  Stair opening', 'The 2.25 x 3.59 m floor opening needs designed\nedge supports, landing connections and lateral-force transfer.'),
 ('5  Wide openings', 'The 3.10 m bathroom ribbon and 3.20 m rear slider\nneed designed headers, supports and seismic detailing.'),
 ('6  Clay roofs and terrace supports', 'Tile loads, uplift anchors, roof members and foundations\nare unselected. Terrace post centers are 5.70 m apart.'),
]
y=.79
for title,body in notes:
 fig.text(.585,y,title,fontsize=11,color=upper,weight='bold')
 fig.text(.585,y-.028,body,fontsize=9.1,color=ink,linespacing=1.55,va='top')
 y-=.106
fig.text(.585,.135,'Kitchen wall: height and alignment do not establish\nbearing capacity. Classify it in the structural design.',fontsize=9.2,color=ink,linespacing=1.5)
fig.text(.065,.035,'ARCHITECTURAL ALIGNMENT REVIEW ONLY  /  No members, reinforcement or foundations sized.  /  13 September 2026',fontsize=8,color=upper)
fig.savefig(ROOT/'wall-alignment-review.png',dpi=160,facecolor=fig.get_facecolor())
fig.savefig(ROOT/'wall-alignment-review.svg',facecolor=fig.get_facecolor())
print('Saved existing-wall alignment review')
