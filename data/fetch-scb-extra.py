import json,urllib.request,concurrent.futures,sys,time,urllib.parse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from importlib.machinery import SourceFileLoader
helper=SourceFileLoader('townhelper',str(Path(__file__).parent/'fetch-scb-tatorter.py')).load_module()
OUT=Path(__file__).parent.parent/'dist/data/geodata';OUT.mkdir(parents=True,exist_ok=True)
groups={'Smaorter':[1990,1995,2000,2005,2010,2015,2020,2023],'Gronomraden':[2010,2015,2020],'Verksamhetsomraden':[2015,2020],'Arbetsplatsomraden':[2000,2005,2010],'DeSO':[2018,2025],'RegSO':[2020,2025],'befolkning_1km':list(range(2015,2026))}
def fetch(job):
 group,y=job;layer=f'{group}_{y}'+('_tatort' if group=='Gronomraden' else '')
 path=OUT/(layer+'.json')
 if path.exists():return
 params={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':'stat:'+layer,'outputFormat':'application/json','count':200000 if group=='befolkning_1km' else 3000}
 if group=='befolkning_1km':params['propertyName']='rutid_scb,beftotalt,man,kvinna'
 features=[];start=0
 while True:
  params['startIndex']=start
  url='https://geodata.scb.se/geoserver/stat/wfs?'+urllib.parse.urlencode(params)
  for attempt in range(4):
   try:
    with urllib.request.urlopen(url,timeout=120) as r:page=json.load(r)
    if 'features' not in page:raise ValueError(str(page)[:200])
    break
   except Exception as error:
    print('Retry',layer,start,str(error)[:100],flush=True)
    if attempt==3:raise
  rows=page['features'];features.extend(rows);start+=len(rows)
  matched=page.get('numberMatched',page.get('totalFeatures'))
  if not rows or (isinstance(matched,int) and start>=matched) or len(rows)<params['count']:break
  print('Page',layer,start,'/',matched,flush=True)
 x={'features':features}
 out=[]
 for f in x['features']:
  p=f['properties'];g=f.get('geometry');rings=[]
  if g:
   polys=[g['coordinates']] if g['type']=='Polygon' else g['coordinates']
   for poly in polys:
    rings.extend([[[round(a),round(b)] for a,b in helper.simplify(ring,30**2)] for ring in poly])
  elif group=='befolkning_1km':
   rid=str(p['rutid_scb']);a=int(rid[:6]);b=int(rid[6:]);rings=[[[a,b],[a+1000,b],[a+1000,b+1000],[a,b+1000],[a,b]]]
  out.append({'p':p,'r':rings})
 path.write_text(json.dumps({'group':group,'year':y,'features':out},ensure_ascii=False,separators=(',',':')))
 print(layer,len(out),path.stat().st_size,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(fetch,[(g,y) for g,ys in groups.items() for y in ys]))
(OUT/'catalog.json').write_text(json.dumps(groups))
