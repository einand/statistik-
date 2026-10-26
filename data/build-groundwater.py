from pathlib import Path
import json,gzip,re,sys,collections,shutil
try:from pyproj import Transformer
except ImportError:sys.path.insert(0,'/tmp/site-projection');from pyproj import Transformer
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-mixed-2026-10-25';OUT=ROOT/'dist/data/geodata';project=Transformer.from_crs('EPSG:4326','EPSG:3006',always_xy=True);byyear=collections.defaultdict(list);counts=collections.Counter();total=0
# Screen geometry: retain original full-resolution sources separately.
def thin(ring):
 ps=[]
 for lon,lat,*_ in ring:
  x,y=project.transform(lon,lat);p=[round(x,1),round(y,1)]
  if not ps or (p[0]-ps[-1][0])**2+(p[1]-ps[-1][1])**2>=900:ps.append(p)
 if len(ps)<3:ps=[list(project.transform(*p[:2])) for p in ring[:3]]
 if ps[0]!=ps[-1]:ps.append(ps[0])
 return ps
for page in sorted(R.glob('groundwater-[0-9]*.json.gz')):
 d=json.loads(gzip.decompress(page.read_bytes()));assert d['numberReturned']==len(d['features'])
 for f in d['features']:
  p=f['properties'];y=int(p['begin_lifespanversion'][:4]);g=f['geometry'];polygons=[g['coordinates']] if g['type']=='Polygon' else g['coordinates'];rings=[thin(ring) for poly in polygons for ring in poly];props=p|{'NAMN':p['name'],'Källa':'SGU','Licens':'CC0','Förvaltningscykel':p['versiondescr'],'ar':y};byyear[y].append({'p':props,'r':rings});total+=1
 (ROOT/'dist/data'/('sgu-groundwater-source-'+page.name.split('-')[1])).write_bytes(page.read_bytes())
assert total==13739,total
for y,features in byyear.items():
 file='Grundvatten_'+str(y)+'.json';(OUT/(file+'.gz')).write_bytes(gzip.compress(json.dumps({'source':'SGU','license':'CC0','features':features,'definition':'Vattenförvaltningens grundvattenförekomster. Visningsgeometrin förenklad; originaldata kan laddas ner.'},ensure_ascii=False,separators=(',',':')).encode(),mtime=0));counts[y]=len(features)
shutil.copyfile(R/'groundwater-inspire.zip',ROOT/'dist/data/sgu-groundwater-inspire.zip')
cat=json.loads((OUT/'catalog.json').read_text());cat['Grundvatten']=sorted(byyear);cat['_gzip']=sorted(set(cat.get('_gzip',[])+['Grundvatten_'+str(y)+'.json' for y in byyear]));(OUT/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,separators=(',',':')))
p=ROOT/'dist/assets/geodata-map.html';s=p.read_text()
if 'Grundvatten:[' not in s:s=s.replace('const groups={',"const groups={Grundvatten:['Grundvattenförekomster','SGU · CC0. Vattenförvaltningens avgränsade grundvattenförekomster i separata förvaltningscykler. Aktuellt material kan innehålla preliminära områden. Detta visar varken dagens vattennivå, vattenbrist eller vattenkvalitet. Ändrade gränser behöver inte betyda ändrad vattenmängd.'],",1)
s=s.replace("$('download').innerHTML='<a href=", "$('download').innerHTML=(g==='Grundvatten'?'<a href=\"/data/sgu-groundwater-inspire.zip\" download>INSPIRE-utgåvan · GML i zip · separat format</a> · ':'')+'<a href=",1)
p.write_text(s)
for name in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/name;s=p.read_text()
 if 'GROUNDWATER_V1' not in s:
  s=s.replace('const GEO_LAYERS={','// GROUNDWATER_V1\nconst GEO_LAYERS={"Grundvatten":"Grundvattenförekomster · SGU",',1)
  if name=='dist/focus/index.html':
   marker=" const missingText=missing.length?";block=""" if(year>=2004)additionalContext+='<h3>Grundvatten</h3><p>Grundvattenkartan visar områden som är viktiga för vår vattenförsörjning. Välj ett område för att läsa dess namn och uppgifter. Kartan visar äldre och nyare kartläggningar var för sig. Den visar inte hur mycket vatten som finns just nu eller om vattnet är rent. Ett ändrat område på kartan kan bero på bättre kunskap. Det behöver alltså inte betyda att vattnet har ökat eller minskat. Den särskilda europeiska datautgåvan finns också att ladda ner.</p>';
""";assert marker in s;s=s.replace(marker,block+marker,1)
  else:
   pass
 tmp=p.with_suffix('.next.html');tmp.write_text(s);tmp.replace(p)
print('Groundwater cycles',dict(counts),'full source records',total)
