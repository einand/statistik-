"""Fetch additional regional indicators from official SCB PxWeb tables."""
import json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE='https://api.scb.se/OV0104/v1/doris/sv/ssd/'
SPECS={
 'births':('BE/BE0101/BE0101H/FoddaK','Antal levande födda','födda','Födda och döda','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__BE__BE0101__BE0101H/FoddaK/'),
 'deaths':('BE/BE0101/BE0101I/DodaHandelseK','Antal döda','dödsfall','Födda och döda','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__BE__BE0101__BE0101I/DodaHandelseK/'),
 'householdSize':('BE/BE0101/BE0101S/HushallT09','Antal personer per hushåll','personer/hushåll','Hushåll','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__BE__BE0101__BE0101S/HushallT09/'),
 'turnoutRiksdag':('ME/ME0104/ME0104D/ME0104T4','Valdeltagande i riksdagsval','%','Val och valdeltagande','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__ME__ME0104__ME0104D/ME0104T4/'),
 'turnoutRegion':('ME/ME0104/ME0104D/ME0104T4','Valdeltagande i regionfullmäktigval','%','Val och valdeltagande','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__ME__ME0104__ME0104D/ME0104T4/'),
 'turnoutMunicipal':('ME/ME0104/ME0104D/ME0104T4','Valdeltagande i kommunfullmäktigval','%','Val och valdeltagande','https://www.statistikdatabasen.scb.se/pxweb/sv/ssd/START__ME__ME0104__ME0104D/ME0104T4/')}
site=json.loads((ROOT/'../src/template.html').read_text().split('<script type="application/json" id="data">',1)[1].split('</script>',1)[0])
regions=['00',*site['names'],*site['municipalities']]
def meta(path):return json.load(urllib.request.urlopen(BASE+path,timeout=40))
def request(path,query):
 req=urllib.request.Request(BASE+path,data=json.dumps({'query':query,'response':{'format':'json-stat2'}}).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=90) as r:return json.load(r)
def dim(code,values,fil='item'):return {'code':code,'selection':{'filter':fil,'values':values}}
def run(key,spec):
 path,label,unit,group,url=spec
 m=meta(path);vs={x['code']:x for x in m['variables']};geoRegions=[r for r in regions if r in vs['Region']['values']];q=[dim('Region',geoRegions,'item')]
 if 'AlderModer' in vs:q += [dim('AlderModer',['tot']),dim('Kon',['1','2'])]
 elif 'Alder' in vs:
  q += [dim('Alder',['tot']),dim('Kon',['1','2'])]
  if 'Fodelseregion' in vs:q += [dim('Fodelseregion',['11'])]
 if 'ContentsCode' in vs:
  if key=='householdSize': q += [dim('ContentsCode',['000000M5'])]
  elif key=='foreignBorn': q += [dim('ContentsCode',['000001NS'])]
  elif key.startswith('turnout'):
   code={'turnoutRiksdag':'ME0104B8','turnoutRegion':'ME0104C5','turnoutMunicipal':'ME0104C6'}[key]
   q += [dim('ContentsCode',[code])]
 if 'Tid' in vs:q += [dim('Tid',vs['Tid']['values'])]
 import itertools,urllib.error
 years=vs.get('Tid',{}).get('values',[])
 data={}
 for regionChunk in [geoRegions[i:i+100] for i in range(0,len(geoRegions),100)]:
  subq=[dict(x) for x in q]; next(x for x in subq if x['code']=='Region')['selection']['values']=regionChunk
  try:responses=[request(path,subq)]
  except urllib.error.HTTPError as e:raise RuntimeError(f'{key} SCB query failed for region chunk beginning {regionChunk[0]}: {e.code}')
  for response in responses:
   dims=response['dimension']; ids=response['id']; cats=[list(dims[i]['category']['index']) for i in ids]
   for combo,v in zip(itertools.product(*cats),response['value']):
    if v is None:continue
    item=dict(zip(ids,combo));geo=item['Region'];period=next((item[k] for k in ids if k.lower() in ['tid','valår','valar']),None)
    if period is None:continue
    if key in ('births','deaths'):
     bucket=data.setdefault(period,{});bucket[geo]=bucket.get(geo,0)+float(v)
    else:data.setdefault(period,{})[geo]=float(v)
 out={'key':key,'code':path.rsplit('/',1)[-1],'label':label,'unit':unit,'group':group,'sourceTitle':m['title'],'url':url,'years':sorted(map(int,data)),'data':data}
 print(key,sum(len(v) for v in data.values()),out['years'][:1],out['years'][-1:],flush=True)
 return out
if __name__=='__main__':
 out=[]
 cache=ROOT/'historical-maps.json'
 if cache.exists():out=json.loads(cache.read_text())
 done={x['key'] for x in out}
 for k,v in SPECS.items():
  if k not in done:out.append(run(k,v));cache.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
