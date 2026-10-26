from pathlib import Path
import urllib.request,json,concurrent.futures,gzip
R=Path(__file__).resolve().parent/'additions-fk-2026-10-25';manifest=json.loads((R/'manifest.json').read_text());jobs=[(r,t['table']) for r in manifest for t in r['meta']['filter']['uppdelning']]
def fetch(job):
 r,t=job;path=R/(t+'.json.gz');u=r['url'].rsplit('/',1)[0]+'/'+t+'.json'
 if path.exists():return t,'cached'
 try:
  b=urllib.request.urlopen(u,timeout=120).read();json.loads(b);path.write_bytes(gzip.compress(b));return t,len(b),b[:400].decode()
 except Exception as e:return t,str(e)
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 for f in concurrent.futures.as_completed([pool.submit(fetch,j) for j in jobs]):print(f.result(),flush=True)
