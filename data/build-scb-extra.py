import json,re
from pathlib import Path
root=Path(__file__).parent.parent
base=root/'dist/data/geodata'
specs=[('smallCount','Antal småorter','områden','Smaorter',None),('smallPopulation','Invånare i småorter','personer','Smaorter','bef'),('smallArea','Småorternas landareal','hektar','Smaorter','area_ha'),('businessCount','Antal verksamhetsområden','områden','Verksamhetsomraden',None),('businessArea','Verksamhetsområden · landareal','hektar','Verksamhetsomraden','area_ha'),('workplaceCount','Äldre arbetsplatsområden utanför tätort','områden','Arbetsplatsomraden',None),('workplaceArea','Äldre arbetsplatsområden · landareal','hektar','Arbetsplatsomraden','area_ha'),('desoCount','Antal DeSO-områden','områden','DeSO',None),('regsoCount','Antal RegSO-områden','områden','RegSO',None),('greenArea','Grönområdesyta i tätorter · efter tätortskod','hektar','Gronomraden','areakvm')]
source=(root/'dist/index.html').read_text();source=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',source,re.S)[1])
expected=json.loads((base/'catalog.json').read_text())
for group,years in expected.items():
 for y in years:
  assert (base/(group+'_'+str(y)+('_tatort' if group=='Gronomraden' else '')+'.json')).exists(),(group,y,'not downloaded')
series={};metadata={}
for key,label,unit,group,field in specs:
 records={}
 for path in sorted(base.glob(group+'_*.json')):
  
  if '-part' in path.stem:continue
  x=json.loads(path.read_text())
  if 'parts' in x:x['features']=[f for part in x['parts'] for f in json.loads((base/part).read_text())['features']]
  y=str(x['year']);vals={code:0 for code in ['00',*source['names'],*source['municipalities']]}
  for f in x['features']:
   p=f['p'];county=p.get('lan') or p.get('lankod') or p.get('lanskod');municipality=p.get('kommun') or p.get('kommunkod')
   county=county or str(p.get('tatortskod') or '')[:2];municipality=municipality or str(p.get('tatortskod') or '')[:4]
   county=county or str(p.get('desokod') or p.get('regsokod') or '')[:2];municipality=municipality or str(p.get('desokod') or p.get('regsokod') or '')[:4]
   value=p.get(field) if field else 1
   if value is None:continue
   if group=='Gronomraden':value=value/10000
   for code in ['00',county,municipality]:
    if code:vals[code]=vals.get(code,0)+value
  records[y]=vals
 years=sorted(map(int,records));assert years,(key,'missing data')
 series[key]=records
 metadata[key]={'label':label,'group':'Bebyggelse & områdesindelning','source':'SCB','code':group,'unit':unit,'years':years,'country':True,'county':True,'municipality':True,'count':sum(map(len,records.values())),'url':'https://www.scb.se/vara-tjanster/oppna-data/oppna-geodata/','retrieved':'24 oktober 2026','definition':'Summerat ur SCB:s WFS-utgåvor: '+', '.join(map(str,years))+'. Mellanår använder senast föregående utgåva. Arbetsplatsområden 2000–2010 och verksamhetsområden 2015–2020 har olika definitioner och är separata serier. Antal områden betyder inte antal nybildade orter eller byggnaders ålder. Lokalt hostad data. Historiska kommunkoder behålls. Grönområdesyta tilldelas kommunen via tätortskodens prefix, inte genom klippning mot kommungräns. Tätorter kan korsa kommungränser. Täckning och metod varierar mellan grönområdesutgåvor; måttet avser inte all grönska i länet.'}
for name in ['dist/index.html','dist/lan/index.html']:
 path=root/name;s=path.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['social'].update(series);d['extraMetadata'].update(metadata);s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 s=s.replace("const groupForMetric=key=>{","const groupForMetric=key=>{\n if("+json.dumps(list(series))+".includes(key))return 'Bebyggelse & områdesindelning';",1)
 s=s.replace("value == null || !Number.isFinite(value)?'–':","value == null || !Number.isFinite(value)?'–': ['smallCount','smallPopulation','businessCount','workplaceCount','desoCount','regsoCount'].includes(measure)?fmt(value):",1)
 path.write_text(s)
print('Added',len(series),'regional metrics')
# Store grid coordinates once as the SCB grid identifier, rather than five repeated corners.
for path in base.glob('befolkning_1km_*.json'):
 x=json.loads(path.read_text())
 if 'features' not in x:continue
 fields=['rutid_scb','beftotalt','man','kvinna'];cells=[[f['p'].get(k) for k in fields] for f in x.pop('features')]
 x['fields']=fields;x['cells']=cells;path.write_text(json.dumps(x,separators=(',',':')))
# Keep all downloaded data in static files smaller than 15 MB.
for path in list(base.glob('*.json')):
 if path.stat().st_size<15_000_000:continue
 x=json.loads(path.read_text());fs=x.pop('features',[]);parts=[]
 for start in range(0,len(fs),10000):
  name=path.stem+'-part'+str(start//10000)+'.json';(base/name).write_text(json.dumps({'features':fs[start:start+10000]},ensure_ascii=False,separators=(',',':')));parts.append(name)
 x['parts']=parts;path.write_text(json.dumps(x))
