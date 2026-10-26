"""Publicera fullständiga flerdimensionella källtabeller lokalt, med tydlig geografi."""
from pathlib import Path
import json,re,math,shutil
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-2026-10-25';OUT=ROOT/'dist/data/deepdives';OUT.mkdir(exist_ok=True)
def year(p):
 ns=re.findall(r'\d{4}',str(p))
 if not ns:return None
 y=int(ns[-1])
 if '/' in str(p) and len(ns)==1 and re.search(r'/\d{2}$',str(p)):y=y//100*100+int(str(p)[-2:])
 return y
catalog=[]
def save(c):
 name=c['id']+'.json';(OUT/name).write_text(json.dumps(c,ensure_ascii=False,separators=(',',':')))
 times=next(d for d in c['dimensions'] if d['id']==c['time']);catalog.append({k:c[k] for k in ['id','label','source','url','license','region','time'] }|{'file':name,'periods':[v[1] for v in times['values']],'years':sorted(set(year(v[1]) for v in times['values'])),'status':'available'})
for p in sorted(R.glob('TAB*.json')):
 d=json.loads(p.read_text())
 if 'dimension' not in d:continue
 dims=[]
 for k in d['id']:
  q=d['dimension'][k];cat=q['category'];codes=sorted(cat['index'],key=cat['index'].get);dims.append({'id':k,'label':q['label'],'values':[[v,cat['label'].get(v,v)] for v in codes]})
 values=d['value'] if isinstance(d['value'],list) else [d['value'].get(str(i)) for i in range(math.prod(d['size']))]
 id=p.stem;save({'id':id,'label':d['label'],'source':'SCB','license':'CC0','url':'https://statistikdatabasen.scb.se/api/v2/tables/'+id,'dimensions':dims,'size':d['size'],'values':values,'status':d.get('status'),'time':d.get('role',{}).get('time',['Tid'])[0],'region':'Region' if 'Region' in d['id'] else None,'measure':'ContentsCode','units':d['dimension'].get('ContentsCode',{}).get('category',{}).get('unit',{}),'notes':d.get('note',[]),'retrieved':'25 oktober 2026'})
for p in sorted(R.glob('*.px.json')):
 id=p.name[:-5];m=json.loads((R/(id+'.meta.json')).read_text());d=json.loads(p.read_text());dims=[{'id':v['code'],'label':v['text'],'values':list(zip(v['values'],v['valueTexts']))} for v in m['variables']];sizes=[len(v['values']) for v in m['variables']];indexes=[{c:i for i,c in enumerate(v['values'])} for v in m['variables']];values=[None]*math.prod(sizes);statuses={}
 for row in d['data']:
  index=0
  for k,size,lookup in zip(row['key'],sizes,indexes):index=index*size+lookup[k]
  try:values[index]=float(row['values'][0])
  except (ValueError,TypeError):statuses[str(index)]=row['values'][0]
 px=(R/(id+'.px')).read_bytes().decode('cp1252',errors='replace') if (R/(id+'.px')).exists() else ''
 note=re.search(r'NOTE="(.*?)";',px,re.S);notes=[re.sub(r'"\s*\r?\n"','',note[1]).replace('#','\n')] if note else []
 source=json.loads((R/(id+'.source.json')).read_text());tk=next(v['code'] for v in m['variables'] if v.get('time') or 'år' in v['code'].lower());rk=next((v['code'] for v in m['variables'] if v['code']=='Region' or 'RegSO' in v['code'] or 'Folkbokföring' in v['code']),None);mk=next((v['code'] for v in m['variables'] if v['code'] in ['Mått','Andel och konfidensintervall'] or v['code'].startswith('Antal personer med')),None)
 units={}
 if mk:
  v=next(v for v in m['variables'] if v['code']==mk)
  units={c:{'base':'antal' if 'antal' in t.lower() else '%','decimals':1} for c,t in zip(v['values'],v['valueTexts'])}
 save({'id':id,'label':m['title'],'source':source.get('source','Folkhälsomyndigheten'),'license':'CC0','url':source['api'],'dimensions':dims,'size':sizes,'values':values,'status':statuses,'time':tk,'region':rk,'regionAliases':({code:v for v,txt in next(x for x in dims if x['id']==rk)['values'] for code in re.findall(r'^(\d{2}(?:\d{2})?)\s',txt)} if rk and 'Folkbokföring' in rk else {}),'measure':mk,'defaultUnit':'%' if source.get('source')!='CSN' else '', 'units':units,'notes':notes+['Läs källans definition och metod. Redovisade gruppskillnader bevisar inte orsaker. Socioekonomisk områdestyp är en grupp av områden, inte ett unikt RegSO eller ett kommunvärde.'],'retrieved':'25 oktober 2026'})
# A catalogue record is not evidence of available observations.
if not any(c['id']=='mobBaSocek.px' for c in catalog):catalog.append({'id':'mobBaSocek.px','label':'Mobbad i skolan, barn efter socioekonomisk områdestyp, kön och år','source':'Folkhälsomyndigheten','url':'https://www.dataportal.se/datasets/525_13902','license':'CC0','status':'unavailable','reason':'Katalogposten finns men tabellen saknas i källans aktuella API-listning. Inga värden har konstruerats.','years':[],'periods':[],'region':None})
(OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
print('Published',len(catalog),'deep-dive tables;',sum(c['status']=='unavailable' for c in catalog),'unavailable source tables explicitly marked.')
