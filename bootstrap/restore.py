"""One-time, checksum-verified import of the existing public website."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,time,urllib.request,urllib.parse
ROOT=Path(__file__).resolve().parent.parent
config=json.loads((ROOT/'bootstrap/manifest.json').read_text())
def restore(item):
 rel=Path(item['path']);assert rel.parts[0]=='dist' and '..' not in rel.parts
 target=ROOT/rel
 if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:return
 url=config['base_url']+urllib.parse.quote(str(rel.relative_to('dist')),safe='/')
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Statistik-project-import/1.0'}),timeout=120) as r:data=r.read()
   assert len(data)==item['size'],str(rel)+' size mismatch'
   assert hashlib.sha256(data).hexdigest()==item['sha256'],str(rel)+' checksum mismatch'
   target.parent.mkdir(parents=True,exist_ok=True);tmp=target.with_name(target.name+'.import-tmp');tmp.write_bytes(data);tmp.replace(target);return
  except Exception:
   if attempt==3:raise
   time.sleep(2*(attempt+1))
with ThreadPoolExecutor(max_workers=4)as pool:list(pool.map(restore,config['files']))
print('Verified',len(config['files']),'published files.')
