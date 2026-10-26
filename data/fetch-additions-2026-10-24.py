import urllib.request,urllib.parse,json,concurrent.futures
from pathlib import Path
root=Path(__file__).resolve().parent/'additions-2026-10-24';root.mkdir(exist_ok=True)
codes=['U50105','N65827','N65811','N05810','N65810','N05814','N05828','N05825','N05827']
def fetch(code):
 path=root/(code+'.json')
 if path.exists():return code,len(json.load(open(path))['rows'])
 meta=json.load(urllib.request.urlopen('https://api.kolada.se/v3/kpi/'+code,timeout=35))['values'][0]
 rows=[]
 for rt in ['municipality','region']:
  for ys in [range(2000,2014),range(2014,2027)]:
   url='https://api.kolada.se/v3/data/kpi/'+code+'/year/'+','.join(map(str,ys))+'?region_type='+rt+'&per_page=5000'
   while url:
    d=json.load(urllib.request.urlopen(url,timeout=50));rows+=d['values'];url=d.get('next_url')
 path.write_text(json.dumps({'metadata':meta,'rows':rows},ensure_ascii=False,separators=(',',':')));return code,len(rows),rows[:1]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
 for f in concurrent.futures.as_completed([p.submit(fetch,c) for c in codes]):
  try:print(f.result(),flush=True)
  except Exception as e:print('ERROR',str(e),flush=True)
