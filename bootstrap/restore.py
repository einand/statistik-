"""One-time, checksum-verified import of the existing public website."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time,urllib.request,urllib.parse,re,gzip
ROOT=Path(__file__).resolve().parent.parent
config=json.loads((ROOT/'bootstrap/manifest.json').read_text())
templates=json.loads(gzip.decompress((ROOT/'bootstrap/html-templates.json.gz').read_bytes()))
def restore(item):
 rel=Path(item['path']);assert rel.parts[0]=='dist' and '..' not in rel.parts
 target=ROOT/rel
 if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:return
 url=config['base_url']+urllib.parse.quote(str(rel.relative_to('dist')),safe='/')
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Statistik-project-import/1.0','Accept-Encoding':'identity'}),timeout=120) as r:data=r.read()
   if str(rel) in templates:
    if data[:2]==b'\x1f\x8b':data=gzip.decompress(data)
    template=templates[str(rel)]
    match=re.search(rb'<script[^>]*\bid="data"[^>]*>(.*?)</script>',data,re.S)
    if not match:raise ValueError(str(rel)+' missing data block; received '+str(len(data))+' bytes: '+repr(data[:160]))
    embedded=match[1]
    assert hashlib.sha256(embedded).hexdigest()==template['data_sha256'],str(rel)+' data block mismatch'
    data=template['prefix'].encode()+embedded+template['suffix'].encode()
   assert len(data)==item['size'],str(rel)+' size mismatch: '+str(len(data))+' expected '+str(item['size'])
   assert hashlib.sha256(data).hexdigest()==item['sha256'],str(rel)+' checksum mismatch'
   target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.import-tmp');tmp.write_bytes(data);tmp.replace(target);return
  except Exception:
   if attempt==3:raise
   time.sleep(2*(attempt+1))
with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(restore,config['files']))
print('Verified',len(config['files']),'published files.')
