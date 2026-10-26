"""Punktlager från Turistrådets JSON-LD; ingen kommun- eller historiktilldelning."""
from pathlib import Path
import json,gzip,sys,math
try:from pyproj import Transformer
except ImportError:
 sys.path.insert(0,'/tmp/site-projection');from pyproj import Transformer
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-mixed-2026-10-25';OUT=ROOT/'dist/data/geodata';nodes=json.loads(gzip.decompress((R/'tourism-collection.json.gz').read_bytes()));index={n['@id']:n for n in nodes};NS='http://schema.org/';project=Transformer.from_crs('EPSG:4326','EPSG:3006',always_xy=True)
def text(n,key):
 vs=n.get(NS+key,[]);return next((v.get('@value') or v.get('@id') for v in vs if v.get('@language')=='sv'),next((v.get('@value') or v.get('@id') for v in vs),None))
def link(n,key):return index.get(next((v.get('@id') for v in n.get(NS+key,[])),None),{})
features=[];seen=set();missing=0
for n in nodes:
 if not n.get(NS+'geo'):continue
 geo=link(n,'geo');name=text(n,'name');url=text(n,'url');lat=text(geo,'latitude');lon=text(geo,'longitude');address=link(n,'address')
 try:lat=float(lat);lon=float(lon)
 except (ValueError,TypeError):missing+=1;continue
 if not name or not (54<=lat<=70 and 9<=lon<=25):missing+=1;continue
 identity=(url,name,lat,lon)
 if identity in seen:continue
 seen.add(identity);x,y=project.transform(lon,lat);assert math.isfinite(x+y)
 p={'NAMN':name,'Typ':', '.join(v.rsplit('/',1)[-1] for v in n.get('@type',[])),'Ort':text(address,'addressLocality') or 'Saknas','Adress':text(address,'streetAddress') or 'Saknas','Källänk':url or 'https://www.vastsverige.com/','Källa':'Turistrådet Västsverige','Licens':'CC BY-SA 4.0','ar':2026,'Uttag':'2026-10-25','Latitud':lat,'Longitud':lon}
 for key,label in [('startDate','Startdatum'),('endDate','Slutdatum')]:
  if text(n,key):p[label]=text(n,key)
 features.append({'p':p,'r':[[[x-12,y-12],[x+12,y-12],[x+12,y+12],[x-12,y+12],[x-12,y-12]]]})
payload={'source':'Turistrådet Västsverige','license':'CC BY-SA 4.0','retrieved':'2026-10-25','definition':'Aktuell redaktionell samling av besöksmål, verksamheter och evenemang. Koordinaterna visas som punkter. Inte ett heltäckande företagsregister; inget etableringsår eller historiskt årsantal härleds.','features':features}
file='Turism_2026.json';(OUT/(file+'.gz')).write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));cat=json.loads((OUT/'catalog.json').read_text());cat['Turism']=[2026];cat['_gzip']=sorted(set(cat.get('_gzip',[])+[file]));(OUT/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,separators=(',',':')))
(ROOT/'dist/data/tourism-source.json.gz').write_bytes((R/'tourism-collection.json.gz').read_bytes())
p=ROOT/'dist/assets/geodata-map.html';s=p.read_text();s=s.replace("const groups={", "const groups={Turism:['Besöksmål i Västsverige','Turistrådet Västsverige · CC BY-SA 4.0 · uttag 25 oktober 2026. Aktuell redaktionell samling, inte alla företag eller en historisk årsserie. Symbolerna visar källans koordinater, inte områdesytor. Inga kommunantal eller etableringsår härleds.'],",1) if 'Turism:[' not in s else s
p.write_text(s)
for name in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/name;s=p.read_text()
 if 'TOURISM_V1' not in s:
  s=s.replace('const GEO_LAYERS={', 'const GEO_LAYERS={"Turism":"Besöksmål i Västsverige",',1)
  if name!='dist/lan/index.html':
   s=s.replace("if(layer==='Electricity')", "if(layer==='Electricity')",1)
  if name=='dist/focus/index.html':
   marker=" const missingText=missing.length?";block=""" // TOURISM_V1
 if(year>=2026)additionalContext+='<h3>Besöksmål och evenemang i Västsverige</h3><p>Turistrådets kartlager visar redaktionellt registrerade besöksmål, verksamheter och evenemang med källans koordinater. Det täcker inte alla företag och säger inget säkert om när en verksamhet startade. Kartans utsnitt innebär inte att alla punkter tillhör den valda kommunen. Välj besöksmålskartan och tryck på en punkt för namn, ort och källuppgifter. Äldre årsutgåvor saknas i detta uttag.</p>';
""";assert marker in s;s=s.replace(marker,block+marker,1)
  else:s=s.replace('const GEO_LAYERS={','// TOURISM_V1\nconst GEO_LAYERS={',1)
 tmp=p.with_suffix('.next.html');tmp.write_text(s);tmp.replace(p)
print('Tourism points',len(features),'without usable coordinates',missing,'from',len(nodes),'JSON-LD nodes')
