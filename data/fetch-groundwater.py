from pathlib import Path
import urllib.request,json,gzip,concurrent.futures
R=Path(__file__).resolve().parent/'additions-mixed-2026-10-25';base='https://api.sgu.se/oppnadata/grundvattenforekomster/ogc/features/v1/collections/grundvattenforekomster/items?f=application%2Fgeo%2Bjson&limit=1000&startIndex='
def get(start):
 p=R/('groundwater-'+str(start)+'.json.gz')
 if start==0:p0=R/'groundwater-first.json.gz';p.write_bytes(p0.read_bytes())
 if p.exists():return start,len(json.loads(gzip.decompress(p.read_bytes()))['features'])
 b=urllib.request.urlopen(base+str(start),timeout=120).read();json.loads(b);p.write_bytes(gzip.compress(b,mtime=0));return start,len(json.loads(b)['features'])
with concurrent.futures.ThreadPoolExecutor(3) as pool:
 for f in concurrent.futures.as_completed([pool.submit(get,i) for i in range(0,13739,1000)]):print(f.result(),flush=True)
u='https://resource.sgu.se/data/datasets/inspire/AM_SGU_WaterBodyForWFD_epsg3006.zip';p=R/'groundwater-inspire.zip'
if not p.exists():p.write_bytes(urllib.request.urlopen(u,timeout=120).read())
print('INSPIRE',p.stat().st_size,flush=True)
