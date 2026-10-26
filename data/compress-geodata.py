"""Förlustfri komprimering av lokala kartfiler; katalogen anger verkliga filnamn."""
from pathlib import Path
import json,gzip
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'dist/data/geodata';p=R/'catalog.json';catalog=json.loads(p.read_text());files=set(catalog.get('_gzip',[]));saved=0
for p in R.glob('*.json'):
 if p.name=='catalog.json' or p.stat().st_size<50000:continue
 b=p.read_bytes();d=json.loads(b)
 if d.get('parts'):continue
 c=gzip.compress(b,mtime=0);assert gzip.decompress(c)==b
 p.with_suffix('.json.gz').write_bytes(c);saved+=len(b)-len(c);files.add(p.name);p.unlink()
catalog['_gzip']=sorted(files);(R/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':')))
p=ROOT/'dist/assets/geodata-map.html';s=p.read_text()
if 'async function readGeoFile' not in s:
 s=s.replace('async function load(){',"async function readGeoFile(file){const compressed=catalog._gzip?.includes(file),response=await fetch('/data/geodata/'+file+(compressed?'.gz':''));if(!response.ok)throw Error(response.status);return compressed?await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json():await response.json()}\nasync function load(){",1)
 s=s.replace("url='/data/geodata/'+name+'.json'", "url='/data/geodata/'+name+'.json'+(catalog._gzip?.includes(name+'.json')?'.gz':'')")
 s=s.replace("data=await fetch(url).then(r=>{if(!r.ok)throw Error(r.status);return r.json()})", "data=await readGeoFile(name+'.json')")
 s=s.replace("const a=await fetch('/data/geodata/'+part).then(r=>r.json())", "const a=await readGeoFile(part)")
 s=s.replace("'/data/geodata/'+p+'\"", "'/data/geodata/'+p+(catalog._gzip?.includes(p)?'.gz':'')+'\"")
 p.write_text(s)
print('Saved',round(saved/1048576,2),'MiB in',len(files),'geodata files; exact byte roundtrip verified.')
