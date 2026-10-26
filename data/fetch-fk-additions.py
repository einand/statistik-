from pathlib import Path
import urllib.request,json,concurrent.futures
R=Path(__file__).resolve().parent/'additions-fk-2026-10-25';R.mkdir(exist_ok=True)
ids=['32232','32167','32225','31699','32235','32239','32236','32169','32228','31873','32155','32227']
def get(i):
 p=R/(i+'.catalog.json')
 d=json.loads(p.read_text()) if p.exists() else json.load(urllib.request.urlopen(f'https://admin.dataportal.se/store/547/metadata/{i}?format=application/json',timeout=40));p.write_text(json.dumps(d,ensure_ascii=False))
 u=next(k for k in d if k.endswith('/meta.json'));node=d[u];m=json.load(urllib.request.urlopen(u,timeout=45));(R/(i+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False));return {'id':i,'url':u,'title':node['http://purl.org/dc/terms/title'][0]['value'],'meta':m}
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 results=list(pool.map(get,ids))
(R/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
for r in results:print(r['id'],r['title'],str(r['meta'])[:3500],flush=True)
