"""Hämtar begärda FHM-tabeller och närliggande nationella/regionala uppdelningar."""
from pathlib import Path
import urllib.request,json,concurrent.futures,math
ROOT=Path(__file__).resolve().parent/'additions-2026-10-25';BASE='https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/A_Folkhalsodata/'
paths=['I_miljohalsa/BomiljoTrans/Tranvan','A_Mo8/2_Kompetens/01Larmiljo/02.03socrelelev','A_Mo8/2_Kompetens/01Larmiljo/02.05mobbelev','A_Mo8/2_Kompetens/01Larmiljo/02.06stresselev','A_Mo8/2_Kompetens/02Lutbsyss/02.16funknedZelev','A_Mo8/1_Tidigalivet/02Forskola/01.07InskForsk']
items=[]
for p in paths:
 for t in json.load(urllib.request.urlopen(BASE+p,timeout=30)):
  if t['type']=='t' and 'regso' not in t['id'].lower():items.append((t['id'],p))
(ROOT/'related-fhm-index.json').write_text(json.dumps(items,ensure_ascii=False))
def fetch(pair):
 id,path=pair
 if (ROOT/(id+'.json')).exists():return id,'cached'
 u=BASE+path+'/'+id;m=json.load(urllib.request.urlopen(u,timeout=30));(ROOT/(id+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False));q={'query':[{'code':v['code'],'selection':{'filter':'item','values':v['values']}} for v in m['variables']],'response':{'format':'json'}}
 assert math.prod(len(v['values']) for v in m['variables'])<=100000,id
 for fmt in ['json','px']:
  q['response']['format']=fmt;s=urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(q).encode(),headers={'Content-Type':'application/json'}),timeout=45).read();(ROOT/(id+'.'+fmt)).write_bytes(s)
 (ROOT/(id+'.source.json')).write_text(json.dumps({'api':u,'license':'CC0','retrieved':'2026-10-25'}));return id,'downloaded'
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for f in concurrent.futures.as_completed([pool.submit(fetch,p) for p in items]):
  try:print(f.result(),flush=True)
  except Exception as e:print('ERROR',str(e),flush=True)
