# Studio set dressing: realistic industrial details built as editable geometry.
# Called before the world GLB is exported from generate_assets.py.
import math,random
random.seed(9026)
# New paint/material palette. Keep dark separation between equipment and walls.
COLORS.update({
 'mint':'#73a895','grass':'#80a681','grass2':'#658a73','edge':'#536e66','asphalt':'#52606b','roadEdge':'#66757c',
 'line':'#e8e4ca','concrete':'#c4c5be','concrete2':'#959f9c','tile':'#d9d6ca','white':'#e5e4de','cream':'#d9d0bb',
 'light':'#e5d7bc','wall':'#a2aeb1','wall2':'#a4aaa8','teal':'#197971','teal2':'#2f9189','blue':'#2c628b',
 'navy':'#324851','sky':'#618c9e','orange':'#be753a','gold':'#ca9d3e','yellow':'#e8b848',
 'wood':'#856447','wood2':'#b28b60','cardboard':'#ac815a','cardboard2':'#c6a079',
 'boxgreen':'#5f907a','boxblue':'#638ca0','boxorange':'#be8954','ink':'#243841','steel':'#6c787e',
 'darksteel':'#37434a','silver':'#b2bac0','glass':'#8ebbc8','plant':'#456c54','plant2':'#5a8763',
 'tree':'#4a7152','tree2':'#6b8762','red':'#b4493d','darkblue':'#2e536e', 'gray':'#7c898b',
 'rust':'#995b3f','stainless':'#a5b0b3','hazard':'#e7b548','rubber':'#333b41','stencil':'#eae9df',
 'epoxy':'#77837b','concretestain':'#afb5aa','coollight':'#e4f6f8','copper':'#986f4f',
 'greyblue':'#637580','charcoal':'#2b343b','gravel':'#81867b','brass':'#b69a68',
 'aquatic':'#287981','dust':'#c2b9a8','stripe':'#f1d377','screen':'#203c4c'
})

# Repeating detail functions; all stay inside original factory footprints.
def rivet(x,y,z,r=.045,col='steel'):
 S(x,y,z,r,col,1)
def bolted_panel(x,y,z,w,h,front='front'):
 B(x,y,z,w,h,.06,'stainless')
 for dx in [-w*.45,w*.45]:
  for dy in [-h*.4,h*.4]:rivet(x+dx,y+dy,z+.047,.028,'darksteel')
def crate(x,z,depth=.7,height=.75):
 B(x,.69+height/2,z,.82,height,depth,'wood2')
 for side in (-1,1):
  B(x+side*.37,.70+height/2,z,.05,height+.06,depth+.04,'wood')
 for h in [.80,1.10,1.4]:
  if h<=.69+height:B(x,h,z,.83,.055,depth+.03,'wood')
 # bound with metal bands
 B(x,.74+height/2,z+.36,.13,height+.04,.03,'steel')

def pressure_gauge(x,y,z):
 C(x,y,z,.21,.055,'silver',22)
 C(x,y,z+.04,.15,.058,'white',22)
 b.beam((x,y,z+.095),(x+.085,y+.065,z+.095),.012,'red')

def machine_module(cx,zz,i):
 # Side-by-side tool cabinets, machine hoods, gauges, handles and tubing.
 B(cx,1.15,zz,1.10,.95,1.20,'greyblue')
 B(cx,1.69,zz,.95,.15,1.06,'stainless')
 B(cx,1.36,zz+.623,.80,.58,.07,'screen')
 for j in range(4):
  B(cx-.33+j*.22,1.88,zz+.58,.15,.11,.10,'teal' if j%2 else 'gold')
 pressure_gauge(cx+.41,1.53,zz+.67)
 for k in range(3):
  B(cx-.32+k*.3,.76,zz+.72,.035,.24,.04,'darksteel')
  rivet(cx-.32+k*.3,.92,zz+.75,.042,'orange')
 # bolted guard rail
 for xoff in [-.69,.69]:B(cx+xoff,1.24,zz+.78,.07,.84,.07,'yellow')
 B(cx,1.67,zz+.78,1.44,.07,.08,'yellow')

# Corrugated roof striping & roof fans, overhead service pipes and cable trays.
for cx,basecolor in [(-19,'teal'),(0,'blue'),(19,'orange')]:
 # industrial standing-seam ridges, with visible metallic trim.
 for i in range(32):
  x=cx-7.5+i*.48
  B(x,4.045,-17.75,.030,.08,2.52,'steel' if i%7 else 'stainless')
 # factory exhaust stacks and their guards, painted piping.
 for off in [-5.5,-.2,4.8]:
  x=cx+off
  C(x,4.40,-18.2,.41,.9,'stainless',16)
  C(x,4.91,-18.2,.47,.12,'darksteel',16)
  for k in range(8):
   a=k*math.pi/4
   b.beam((x+math.sin(a)*.16,5.0,-18.2+math.cos(a)*.16),(x+math.sin(a)*.34,5.0,-18.2+math.cos(a)*.34),.025,'steel')
 # arched overhead ducting behind machine lines
 for dx in [-6.0,-2.9,.2,3.2,6.3]:
  x=cx+dx
  B(x,2.88,-16.5,.18,1.05,.17,'stainless')
  B(x,3.38,-16.25,.18,.20,5.4,'stainless')
  B(x,3.03,-13.6,.18,.54,.18,'stainless')
 # suspended light rails & electrical cable bundles, independent of workers.
 for xoff in [-4.2,0,4.2]:
  x=cx+xoff
  for z in [-16.2,-12.1]:
   B(x,3.34,z,2.25,.12,.48,'stainless')
   B(x,3.266,z,1.94,.045,.29,'coollight')
   for bpos in [-.96,.96]:B(x+bpos,3.63,z,.05,.52,.05,'darksteel')
 # realistic green gantry production indicator above each line
 for dx in [-3.65,3.65]:
  x=cx+dx
  B(x,2.83,-12.5,.055,1.5,7.6,'gold')
  for z in [-16.1,-12.5,-9.0]:
   B(x,2.8,z,.85,.63,.68,'darksteel')
   B(x,2.79,z+.35,.78,.50,.04,'screen')
   for n in range(3):rivet(x-.22+n*.20,2.62,z+.4,.042,['red','yellow','teal'][n])
 # production supplies at back of assembly hall
 for xo in [-6.8,-5.2,5.15,6.4]:
  x=cx+xo; crate(x,-17.1,.75,.80)
  B(x,.19,-17.1,.96,.06,.96,'darksteel')
 # colored waste-segregation bins near entrance
 for j,color in enumerate(['teal','yellow','red']):
  x=cx-5.75+j*.70
  B(x,.78,-8.6,.50,.86,.48,color)
  B(x,1.24,-8.6,.57,.11,.54,'darksteel')
 # cable tray racks with supports mounted on back wall
 B(cx,3.14,-18.66,12.7,.12,.16,'darksteel')
 for i in range(19):
  x=cx-6.2+i*.69
  B(x,3.16,-18.64,.065,.16,.20,'steel')
 # floor wear and yellow work area stripes
 for dx in [-5.2,-.6,4.2]:
  x=cx+dx
  B(x,.489,-10.0,1.35,.010,.075,'hazard')
  B(x,.489,-8.62,1.35,.010,.075,'hazard')
  for dz in [-9.9,-9.6,-9.3,-9.0,-8.8]:
   B(x-.7,.492,dz,.11,.010,.12,'hazard')
   B(x+.7,.492,dz,.11,.010,.12,'hazard')
 for j in range(10):
  x=cx+random.uniform(-6.7,6.7);z=random.uniform(-18,-9.0)
  B(x,.494,z,.21,.008,.12,'concretestain')
 # fire safety extinguisher at each manufacturing entry
 B(cx+6.62,.91,-8.20,.28,.84,.29,'red')
 C(cx+6.62,1.36,-8.20,.17,.10,'black',12)
 B(cx+6.64,1.23,-7.99,.26,.17,.025,'white')

# Warehouse details: rack beam braces, carton labels, pallets on standby, steel pillars.
for x in [14.4,19.2,24.0]:
 for z in [18.6,22.25]:
  for level in [.7,1.9,3.1]:
   for side in [-1,1]:
    rivet(x+side*1.81,level,z+.68,.063,'gold')
    B(x+side*1.81,level+.40,z+.72,.09,.66,.10,'yellow')
   for dx in [-1.0,0,1.0]:
    # carton barcode labels on outward visible faces
    xx=x+dx
    B(xx,level+.56,z+.665,.30,.18,.012,'white')
    for k in range(6): B(xx-.105+k*.043,level+.56,z+.677,.015,.112,.006,'charcoal')
# Rack numbering, metal staircase and safety rails near dispatch.
for row,z in enumerate([18.6,22.25]):
 for n,x in enumerate([14.4,19.2,24.0]):
  B(x,3.63,z+.71,.7,.28,.06,'navy')
  for i in range(3):B(x-.18+i*.18,3.64,z+.745,.08,.12,.03,'white')
# Industrial stretchwrap station, roller rollers and scales.
for i in range(18):
 xx=12.22+i*.40
 C(xx,1.19,16.45,.09,.7,'steel',10)
for x,z in [(14.7,12.7),(23.1,12.5),(27.2,15.6)]:
 crate(x,z,.62,.70)
for x in [12.5,21.4,26.7]:
 B(x,.51,11.85,1.65,.1,1.20,'epoxy')
 for side in [-1,1]:B(x+side*.77,.53,11.85,.08,.028,1.25,'hazard')
# overhead warehouse bridge / industrial roof beams
for z in [17.9,20.7,23.0]:
 B(19,4.27,z,17.5,.23,.23,'darksteel')
 for x in [11.5,15.9,20.4,24.9,28.0]:
  b.beam([x,3.43,z-.5],[x,4.23,z],.062,'steel')
for x in [12.4,17.2,22.0,26.6]:
 B(x,3.85,20.0,2.4,.10,.38,'stainless')
 B(x,3.80,20.0,2.0,.035,.26,'coollight')
# rolling steel panel in west loading dock / loading warning stripes
for z in [10.80,12.05,19.65]:
 B(10.24,1.94,z,.20,2.75,.12,'steel')
 for h in range(8):B(10.23,.8+h*.27,z,.026,.045,.36,'lightgrey')
for i in range(14):
 B(9.92,.54,11.10+i*.53,.12,.025,.25,'hazard' if i%2 else 'charcoal')
# Studio office: lived-in desks, phones, keyboards, file racks, print paper, lamps.
for x,z in [(-23.5,17.3),(-20.3,17.3),(-23.0,12.8)]:
 B(x,1.37,z+.25,.65,.043,.20,'charcoal')
 for k in range(5):B(x-.26+k*.13,1.395,z+.25,.04,.011,.10,'stainless')
 S(x+.77,1.4,z+.33,.10,'black',1)
 B(x-.84,1.47,z-.35,.22,.15,.15,'orange')
 B(x+.89,1.49,z+.32,.14,.29,.14,'white')
 C(x+.89,1.66,z+.32,.08,.055,'white')
 # desk document stacks
 for k in range(4):B(x-.74,1.42+k*.018,z+.3,.25,.015,.21,'white')
# Filing cabinets and partition glass
for x,z in [(-26.2,19),(-12.65,19.1),(-22.0,21.2)]:
 B(x,1.17,z,1.14,1.42,.74,'greyblue')
 for i in range(3):
  B(x,.77+i*.4,z+.38,.95,.36,.025,'stainless')
  B(x,1.0+i*.4,z+.406,.30,.035,.017,'darksteel')
for x in [-19.3,-16.7,-14.5]:
 B(x,1.03,21.75,1.42,1.24,.13,'wood2')
 for z in [21.55,21.78]:B(x,1.62,z,1.4,.08,.07,'cream')
# printer realism: ventilation grids, toner access, display & paper-feeder rails
for i in range(11): B(-15.56+i*.13,1.13,16.48,.06,.026,.022,'charcoal')
for i in range(6):B(-15.43+i*.20,1.47,17.72,.045,.018,.08,'stainless')
B(-14.3,1.50,17.15,.07,.28,.40,'charcoal')
# Admin-office desk equipment
for xx in [-3.2,0,3.2]:
 B(xx,1.26,17.15,.80,.04,.30,'charcoal')
 B(xx,1.29,17.07,.44,.018,.10,'stainless')
 B(xx+.86,1.37,17.76,.28,.28,.24,'stainless')
 B(xx-1.0,1.44,17.86,.08,.37,.08,'black')
 # separate binder stack and clamp-on desk lamp
 for k in range(3):B(xx-.79,1.38+k*.035,17.01,.38,.03,.29,'white')
 C(xx+.93,1.79,17.95,.10,.14,'lamp')
# Site safety: lane markings, road signs, sidewalk bollards, oil stains.
for i in range(20):
 x=random.uniform(-28,28);z=random.choice([1.2,4.0,5.1])+random.uniform(-.2,.2)
 B(x,.25,z,random.uniform(.25,.63),.010,.07,'gravel')
for x,z in [(-30,1.4),(-14,1.4),(1.5,1.4),(9.8,2.9),(31,1.4)]:
 B(x,.40,z,.08,.39,.08,'stainless')
 C(x,.72,z,.34,.05,'red',16)
for x,z in [(-8.5,6.2),(7.85,-5.55),(28.8,5.7)]:
 C(x,1.21,z,.065,2.1,'steel',10)
 B(x,2.33,z,.72,.57,.10,'yellow')
 B(x,2.29,z+.065,.58,.36,.035,'charcoal')
# forklift safe zone, parallel painted bays
for i in range(8):
 z=11.2+i*.9
 B(8.8,.23,z,.12,.025,.57,'hazard' if i%2 else 'charcoal')
# additional woody crates and shopping carts around packing dock
for x,z in [(15.8,11.8),(20.3,11.75),(25,11.9),(28,16.5)]:
 crate(x,z,.68,.84)
# Loading retractable awnings and large safety lamps.
for z in [11.5,16.1,20.6]:
 B(10.02,3.98,z,1.06,.15,1.46,'charcoal')
 B(9.56,3.88,z,.33,.055,1.3,'hazard')
 S(9.48,3.82,z,.11,'coollight')
# Landscaping variations (garden stones, flower pots); away from corridors.
for x,z in [(-31,-19.2),(-30.6,20.2),(29,-20.2),(30,22.2),(-1,24)]:
 for j in range(6):
  dx=random.uniform(-.7,.7);dz=random.uniform(-.7,.7)
  S(x+dx,.24,z+dz,.15+random.random()*.11,'gravel',1)
