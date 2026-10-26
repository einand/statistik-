"""Normalisera FK:s fulla tabeller utan att konstruera dolda celler eller regionvärden."""
from pathlib import Path
import json,gzip,re,math
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-fk-2026-10-25';OUT=ROOT/'dist/data/deepdives';manifest=json.loads((R/'manifest.json').read_text());catalog=json.loads((OUT/'catalog.json').read_text());catalog=[c for c in catalog if not c['id'].startswith('FK-')]
def put(p,d):p.write_bytes(gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
def unit(k,label):
 if '1000' in label:return 'tkr'
 if 'andel' in k or 'andel' in label.lower():return '%'
 if k=='spt':return 'nettodagar/försäkrad'
 if 'per_barn' in k:return 'dagar/barn'
 if 'dagar' in k or k=='netto':return 'dagar'
 return 'antal'
for source in manifest:
 meta=source['meta'];lookup={};dimlabels={}
 def walk(d):
  key=d['key'];dimlabels[key]=d['label'];values=lookup.setdefault(key,{})
  for v in d['values']:
   values[v['key']]=v['label']
   if v.get('subdimension'):walk(v['subdimension'])
 for d in meta['filter']['dimension']:walk(d)
 measures={m['key']:m['label'] for m in meta['filter']['matt']}
 license_nodes=json.loads((R/(source['id']+'.catalog.json')).read_text());licenses=[v['value'] for n in license_nodes.values() for v in n.get('http://purl.org/dc/terms/license',[])];lic='CC BY 4.0' if any('by/4.0' in v for v in licenses) else 'Öppna data enligt Försäkringskassan; särskild licens saknas i katalogposten'
 for table in meta['filter']['uppdelning']:
  name=table['table'];p=R/(name+'.json.gz')
  if not p.exists():raise RuntimeError('Missing '+name)
  raw=json.loads(gzip.decompress(p.read_bytes()));rows=[];unique={};labels={};protected=0
  for row in raw:
   original=row['dimensions'];d={};d['Tid']=original['ar']+('-'+original['manad'] if 'manad' in original else '')
   for k,v in original.items():
    if k in ['ar','manad','ar_manad','row_nr']:continue
    if k in ['diagnoskapitel_kod','diagnosavsnitt_kod','diagnos_kod']:continue
    if (k=='lan' or k.startswith('lan_kod')) or k=='kommun_kod':continue
    d[k]=v
   if 'diagnos_kod' in original:
    diagnosis_keys=['diagnoskapitel_kod','diagnosavsnitt_kod','diagnos_kod'];diagnosis='|'.join(original[k] for k in diagnosis_keys);d['Diagnosgrupp']=diagnosis;labels.setdefault('Diagnosgrupp',{})[diagnosis]=' / '.join(lookup.get(k,{}).get(original[k],original[k]) for k in diagnosis_keys);dimlabels['Diagnosgrupp']='Diagnoskapitel / avsnitt / diagnos'
   geo=original.get('kommun_kod') or next((v for k,v in original.items() if (k=='lan' or k.startswith('lan_kod'))),None)
   if geo is not None:
    d['Region']='00' if geo in ['ALL','ALL_ALL'] else geo[4:] if geo.startswith('ALL_') else geo
    namegeo=lookup.get('kommun_kod',{}).get(geo) or next((lookup[k].get(geo) for k in lookup if (k=='lan' or k.startswith('lan_kod')) and geo in lookup[k]),geo)
    labels.setdefault('Region',{})[d['Region']]='Riket' if d['Region']=='00' else namegeo
   for k,v in d.items():unique.setdefault(k,set()).add(v)
   rows.append((d,row['observations']))
  keys=list(unique);keys.remove('Tid');keys=['Tid']+keys+['Matt'];unique['Matt']=set(k for _,obs in rows for k in obs)
  dims=[]
  for k in keys:
   codes=sorted(unique[k],key=lambda v:(0 if v=='00' and k=='Region' or v.startswith('ALL') else 1,v))
   dims.append({'id':k,'label':'Mätperiod' if k=='Tid' else 'Geografiskt område' if k=='Region' else 'Mått' if k=='Matt' else dimlabels.get(k,k),'values':[[v,measures.get(v,v) if k=='Matt' else labels.get(k,{}).get(v,lookup.get(k,{}).get(v,v))] for v in codes]})
  indexes={d['id']:{v[0]:i for i,v in enumerate(d['values'])} for d in dims};sizes=[len(d['values']) for d in dims];values={};status={}
  for d,obs in rows:
   for k,o in obs.items():
    selection=d|{'Matt':k};i=0
    for dim,size in zip(dims,sizes):i=i*size+indexes[dim['id']][selection[dim['id']]]
    assert i<9007199254740991
    if o.get('rojd') or not isinstance(o.get('value'),(int,float)):
     status[str(i)]='Sekretesskyddad' if o.get('rojd') else 'Uppgift saknas';protected+=1;continue
    assert str(i) not in values or values[str(i)]==o['value'],(name,i)
    values[str(i)]=o['value']
  notes=['Statistik från Försäkringskassan. Källa och alla uppdelningar bevaras; sekretesskyddade värden visas som saknade.','Månadsstatistik är ett läge eller en redovisning för en månad. Summera inte månatliga mottagare eller pågående sjukfall till antal unika personer under ett år. Pågående år kan vara ofullständigt. Belopp anges i löpande priser.','Diagnoser, kön, åldrar och förmåner kan avse överlappande grupper. Summera inte totaler och undergrupper. Antal förmånsmottagare är inte ett mått på all sjuklighet, all frånvaro eller varje invånares situation.']
  if source['id']=='32239':notes+=['Sjukpenningtalet 2.0: utbetalda nettodagar under rullande 12 månader per uppskattat sjukpenningförsäkrad i åldrarna 15–69 år (sysselsatta och arbetssökande). Det är en separat serie från tidigare sjukpenningtal. December motsvarar helår; senaste månad under pågående år är inte ett separat helårsutfall.']
  if source['id']=='32225':notes+=['Reglerna för dubbeldagar ändrades 1 juli 2024: högst 60 dagar under barnets första 15 månader, tidigare 30 under första året. Detta påverkar jämförelser mellan år.']
  if source['id']=='32235':notes+=['Jämställt uttag avser källans intervall 40/60 av föräldrapenningdagarna och den redovisade barnpopulationen. Det är inte ett mått på allt obetalt omsorgsarbete eller generell jämställdhet.']
  if source['id']=='31699':notes+=['Avser högkostnadsskydd i det statliga tandvårdsstödet, inte läkemedel eller all vård. Regler och åldersgränser för tandvårdsstöd kan ändras över tid.']
  if source['id']=='32227':notes+=['Förstagångsbeviljanden är ett inflöde av beslut, inte beståndet av alla mottagare. Aktivitetsersättning och sjukersättning redovisas separat.']
  cells=math.prod(sizes)
  if cells<=5000000 and cells<=max(len(values)*3,1000000):
   dense=[None]*cells
   for i,v in values.items():dense[int(i)]=v
   values=dense
  id='FK-'+name;file=id+'.json.gz';c={'id':id,'label':source['title']+' · '+table['label'],'source':'Försäkringskassan','license':lic,'url':source['url'].rsplit('/',1)[0]+'/'+name+'.json','dimensions':dims,'size':sizes,'values':values,'status':status,'time':'Tid','region':'Region' if 'Region' in keys else None,'measure':'Matt','units':{k:{'base':unit(k,measures.get(k,k)),'decimals':2} for k in unique['Matt']},'notes':notes,'retrieved':'25 oktober 2026'};put(OUT/file,c)
  periods=next(d['values'] for d in dims if d['id']=='Tid');catalog.append({k:c[k] for k in ['id','label','source','license','url','time','region']}|{'file':file,'periods':[v[1] for v in periods],'years':sorted(set(int(v[0][:4]) for v in periods)),'status':'available'})
  print(name,len(raw),'rows',len(values),'values',protected,'missing',int((OUT/file).stat().st_size/1024),'KiB',flush=True)
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
