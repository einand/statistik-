"""Hämta Turistrådets officiella fullständiga JSON-LD-samling."""
from pathlib import Path
import urllib.request,gzip,json
R=Path(__file__).resolve().parent/'additions-mixed-2026-10-25'
u='https://www.vastsverige.com/api/json-ld-collection'
b=urllib.request.urlopen(u,timeout=120).read();json.loads(b)
(R/'tourism-collection.json.gz').write_bytes(gzip.compress(b,mtime=0))
print('Downloaded official JSON-LD collection',len(b),'bytes')
