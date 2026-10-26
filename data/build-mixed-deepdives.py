"""Fullständiga lokala källtabeller: IAF, Skatteverket och Kolada."""
from pathlib import Path
import json,gzip,csv,io,re,math,unicodedata,collections
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-mixed-2026-10-25';OUT=ROOT/'dist/data/deepdives';D=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',(ROOT/'dist/index.html').read_text(),re.S)[1]);catalog=json.loads((OUT/'catalog.json').read_text());catalog=[c for c in catalog if not c['id'].startswith(('SKV-','IAF-','KOLADA-','SLV-'))]
def read(name):
 b=gzip.decompress((R/(name+'.raw.gz')).read_bytes())
 try:s=b.decode('utf-8-sig')
 except UnicodeDecodeError:s=b.decode('cp1252')
 return [{k.lower():v for k,v in r.items()} for r in csv.DictReader(io.StringIO(s))]
def norm(s):return re.sub(r'[\s\-–]','',unicodedata.normalize('NFKC',s).casefold().replace(' län',''))
mun={norm(v['name']):k for k,v in D['municipalities'].items()};county={norm(v):k for k,v in D['names'].items()};county.update({norm(v+'s'):k for k,v in D['names'].items()})
def number(s):
 try:return float(str(s).replace(' ','').replace(',','.'))
 except (ValueError,TypeError):return None
def save(id,label,source,url,license,rows,labels,units,notes,region=None,**extra):
 unique={}
 for d,obs in rows:
  for k,v in d.items():unique.setdefault(k,set()).add(v)
  unique.setdefault('Matt',set()).update(obs)
 keys=list(unique);dims=[]
 for k in keys:
  codes=sorted(unique[k],key=lambda x:(0 if x in ['00','ALL','Totalt','Samtliga','Riket'] else 1,x));dims.append({'id':k,'label':labels.get(k,k),'values':[[v,labels.get((k,v),v)] for v in codes]})
 indexes={d['id']:{v[0]:i for i,v in enumerate(d['values'])} for d in dims};sizes=[len(d['values']) for d in dims];values={};count=0
 for d,obs in rows:
  for k,v in obs.items():
   i=0;sel=d|{'Matt':k}
   for dim,size in zip(dims,sizes):i=i*size+indexes[dim['id']][sel[dim['id']]]
   assert i<9007199254740991
   assert str(i) not in values or values[str(i)]==v,(id,i)
   values[str(i)]=v;count+=1
 cells=math.prod(sizes)
 if cells<=5000000 and cells<=max(len(values)*3,100000):
  dense=[None]*cells
  for i,v in values.items():dense[int(i)]=v
  values=dense
 c={'id':id,'label':label,'source':source,'url':url,'license':license,'dimensions':dims,'size':sizes,'values':values,'time':'Tid','measure':'Matt','region':region,'units':{k:{'base':v,'decimals':2} for k,v in units.items()},'notes':notes,'retrieved':'25 oktober 2026',**extra};p=OUT/(id+'.json.gz');p.write_bytes(gzip.compress(json.dumps(c,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));periods=next(d for d in dims if d['id']=='Tid')['values'];catalog.append({k:c[k] for k in ['id','label','source','url','license','time','region']}|{'file':p.name,'periods':[v[1] for v in periods],'years':sorted(set(int(v[0][:4]) for v in periods)),'status':'available'});print(id,count,'cells',p.stat().st_size//1024,'KiB',flush=True)
# IAF: municipality names and official codes, never convert these counts to unemployment rates.
for name,label,url,measures in [('iaf-recipients','Personer med arbetslöshetsersättning per kommun och år','https://catalog.iaf.se/store/1/resource/217',{'persons':('Mottagare','personer')}),('iaf-processing','Handläggningstid vid varning och avstängning','https://catalog.iaf.se/store/1/resource/547',{'quartile1':('Nedre kvartil','dagar'),'median':('Median','dagar'),'quartile3':('Övre kvartil','dagar'),'notifications':('Underrättelser','antal')}),('iaf-wait','Väntetid för nya ersättningstagare','https://catalog.iaf.se/store/1/resource/392',{'quartile1':('Nedre kvartil','veckor'),'median':('Median','veckor'),'quartile3':('Övre kvartil','veckor'),'benefit_cases':('Ärenden','antal')})]:
 rows=[];labels={'Tid':'År','Matt':'Mått','Region':'Kommun'}
 for r in read(name):
  d={'Tid':r['year']}
  if 'municipality_id' in r:d['Region']=r['municipality_id'];labels['Region',d['Region']]=r['municipality']
  rows.append((d,{k:number(r[k]) for k in measures}))
 labels.update({('Matt',k):v[0] for k,v in measures.items()})
 save('IAF-'+name,label,'IAF',url,'CC0',rows,labels,{k:v[1] for k,v in measures.items()},['Antalet mottagare av arbetslöshetsersättning är inte antalet arbetslösa eller arbetslöshetsnivån. Villkor, försäkringsanslutning och regler påverkar.','Nationella handläggnings- och väntetider gäller respektive ärendetyp, inte kommunala väntetider. Kvartilerna är fördelningsmått, inte konfidensintervall.'],region='Region' if name=='iaf-recipients' else None)
# Preserve every row and grouping of both complete Skatteverket extracts.
for kind,name in [('rot','rot-rut-full'),('tax','total-tax-full')]:
 raw=read(name);groups=collections.defaultdict(list)
 for r in raw:groups['Geografi' if r['gruppering'] in ['Kommun','Län','Total'] else r['gruppering']].append(r)
 for group,sourceRows in groups.items():
  rows=[];labels={'Tid':'Inkomstår / mätperiod','Region':'Geografiskt område','Matt':'Mått','Grupp':group,'Statistikterm':'Statistikterm','Periodtyp':'Periodtyp','Roll':'Köpare eller utförare','Skatteslag':'Skatteslag och detaljnivå'};unmatched=set();updated=set()
  for r in sourceRows:
   updated.add(r['uppdateringsdatum']);period=r.get('period','');d={'Tid':r['inkomstar'] if not period else period[:4]+'-'+period[4:]}
   if group=='Geografi':
    value=r['grupperingsvärde'];code='00' if r['gruppering']=='Total' else (mun if r['gruppering']=='Kommun' else county).get(norm(value))
    if code is None:code='source:'+r['gruppering']+':'+value;unmatched.add(value)
    d['Region']=code;labels['Region',code]='Riket' if code=='00' else value
   else:d['Grupp']=r['grupperingsvärde']
   if kind=='rot':
    d|={'Periodtyp':r['typ_av_period'],'Roll':r['utforare_kopare'],'Statistikterm':r['statistikterm']};obs={k:number(r[k]) for k in ['antal','belopp']}
   else:
    d['Skatteslag']=' / '.join([r['detaljeringsgrad_skatt']]+[r[k] for k in ['typ_av_skatt','huvudgrupp_skatt','undergrupp_skatt','detaljerad_skatt'] if r[k]]);obs={k:number(r[k]) for k in ['antal','belopp','medel','median']}
   rows.append((d,obs))
  labels.update({('Matt',k):v for k,v in {'antal':'Antal','belopp':'Belopp','medel':'Medelvärde','median':'Median'}.items()})
  notes=['Samtliga publicerade rader och mått i den här uppdelningen. Tomma/undertryckta värden är saknade, inte noll. Skatteverkets belopp i kronor och löpande priser.','Pågående inkomstår är ofullständigt. Årsrader under pågående år är hittills redovisat, inte ett färdigt helårsutfall. Skatteändringar och ändrade avdragsregler kan bryta jämförbarheten.','Samma personer och belopp kan förekomma i flera uppdelningar. Summera inte totaler, delgrupper eller skatteslag på olika detaljnivåer. Skatteintäkter är inte kommunens budget eller medianinkomst.','Källans uppdateringsdatum i uttaget: '+', '.join(sorted(updated))+'.']
  if kind=='rot':notes+=['Köpare och utförare är skilda populationer. Godkänd period och betalningsperiod hålls isär. Årsantal är inte summan av månaders unika köpare. Preliminärt avdrag är inte samma sak som slutlig skattereduktion.']
  if unmatched:notes+=['Källområden utan säker kodkoppling behålls med källans namn: '+', '.join(sorted(unmatched))]
  variants=collections.Counter();hasVariants=False
  for d,obs in rows:
   key=tuple(d.items());variants[key]+=1;d['Källradvariant']=str(variants[key]);hasVariants|=variants[key]>1
  if not hasVariants:
   for d,obs in rows:d.pop('Källradvariant')
  else:
   labels['Källradvariant']='Källans separata rader med samma synliga indelning';notes+=['Källan innehåller flera rader med samma synliga gruppbenämningar. Dessa behålls som separata källradvarianter och summeras inte. Det gäller bland annat grupper där klassning saknas. Ingen ytterligare förklaring till dessa skillnader har konstruerats.']
  slug=re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',group).encode('ascii','ignore').decode().lower()).strip('-');save('SKV-'+kind+'-'+slug,('Rot och rut' if kind=='rot' else 'Totala skatter')+' · '+group,'Skatteverket','https://skatteverket.entryscape.net/store/26/resource/'+('317' if kind=='rot' else '382'),'Fritt användbar statistik enligt Skatteverket; särskild licens saknas i katalogposten',rows,labels,{'antal':'antal','belopp':'kr','medel':'kr','median':'kr'},notes,region='Region' if group=='Geografi' else None)
# Rent editions are valuation guidance, not observed annual residential rents.
for id,title,n in json.loads((R/'rent-datasets.json').read_text()):
 p=R/(id+'.csv.gz');b=gzip.decompress(p.read_bytes());
 try:text=b.decode('utf-8-sig')
 except UnicodeDecodeError:text=b.decode('cp1252')
 lines=text.splitlines();delimiter=';' if ';' in lines[0] else ',';header=next(csv.reader([lines[0]],delimiter=delimiter));
 if len(header)==1:header=next(csv.reader([header[0]],delimiter=delimiter))
 period=re.search(r'(\d{4})-(\d{4})',title);start,end=period.groups();rows=[]
 for row in csv.reader(lines[1:],delimiter=delimiter):
  if not row:continue
  assert len(row)==len(header),(id,len(row),len(header))
  for i,v in enumerate(row[1:],1):rows.append(({'Tid':start,'Värdeområde':row[0],'Värdeår':header[i]}, {'hyra':number(v)}))
 save('SKV-rent-'+id,title.replace('\xad',''),'Skatteverket','https://www.dataportal.se/datasets/'+id,'CC0',rows,{'Tid':'Giltig från','Värdeområde':'Värdeområdesnummer','Värdeår':'Byggnadens värdeår / åldersklass','Matt':'Mått',('Matt','hyra'):'Vägledande genomsnittshyra'}, {'hyra':'kr/m² och år'},['Taxeringsutgåva '+start+'–'+end+'. Redovisas från giltighetsårets början, inte som observerad årlig marknadshyra.','Vägledande hyra när faktisk hyra saknas. Värdeår avser byggnadens värdeår/åldersklass, inte observationsår. Värdeområdesnummer är inte kommun- eller RegSO-koder. Ingen egen kommun- eller riksgenomsnittshyra konstrueras.'],timeMode='validFrom')
# Kolada: retain all reported genders and metadata alongside maps.
for code in ['U23466','N07925']:
 d=json.loads((R/(code+'.json')).read_text());rows=[];labels={'Tid':'År','Region':'Geografiskt område','Kön':'Kön','Matt':'Mått',('Matt','value'):d['metadata']['title'],('Kön','T'):'Totalt',('Kön','K'):'Kvinnor',('Kön','M'):'Män'}
 for r in d['rows']:
  geo=r.get('municipality') or r.get('region');geo='00' if geo=='0000' else geo[-2:] if geo and geo.startswith('00') else geo
  if not geo:continue
  labels['Region',geo]='Riket' if geo=='00' else D['names'].get(geo) or D['municipalities'].get(geo,{}).get('name') or geo
  for v in r['values']:
   if v.get('is_deleted'):continue
   rows.append(({'Tid':str(r['period']),'Region':geo,'Kön':v['gender']},{'value':v.get('value')}))
 save('KOLADA-'+code,d['metadata']['title'],'Kolada / '+('Socialstyrelsen' if code=='U23466' else 'SCB'),'https://api.kolada.se/v3/kpi/'+code,'CC BY 4.0',rows,labels,{'value':'%' if code=='U23466' else 'bostäder/1000 inv.'},[d['metadata']['description'],'Ett beviljat bygglov är inte en färdigställd bostad. Tvåårsperioder överlappar.' if code=='N07925' else 'Svar från boende som besvarat undersökningen, inte alla äldre. Ingen åsikt exkluderas ur nämnaren. Undersökningsbortfall och avgränsning påverkar jämförbarheten.'],region='Region')
catalog.append({'id':'SLV-Riksmaten','label':'Livsmedelsverkets matvaneundersökningar · Riksmaten','source':'Livsmedelsverket','url':'https://www.dataportal.se/datasets/236_11235','license':'CC BY 4.0','status':'unavailable','reason':'Katalogposten beskriver Riksmaten barn och vuxna, men instruktionerna för dataåtkomst gav åtkomstfel vid uttaget. Inga observationsvärden har kunnat verifieras eller konstruerats.','years':[],'periods':[],'region':None})
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
