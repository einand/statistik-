"""Bygg ett stabilt publiceringspaket med en kopia av varje kartfil."""
from pathlib import Path
import json,shutil,re,subprocess
ROOT=Path(__file__).resolve().parent.parent;source=ROOT/'dist';target=ROOT/'build';catalog=json.loads((source/'data/geodata/catalog.json').read_text());skip={'data/geodata/'+p for p in catalog.get('_gzip',[])}
subprocess.run(['node',str(ROOT/'data/build-score.mjs')],cwd=ROOT,check=True)
subprocess.run(['python',str(ROOT/'data/build-boring.py')],cwd=ROOT,check=True)
if target.exists():shutil.rmtree(target)
target.mkdir();total=0;count=0
for p in source.rglob('*'):
 if not p.is_file():continue
 relative=p.relative_to(source)
 if str(relative) in skip or any(v.startswith('.') for v in relative.parts) or p.name.endswith('.next.html'):continue
 if relative in map(Path,['index.html','focus/index.html','lan/index.html']):
  s=p.read_text();assert s.rstrip().endswith('</html>'),str(relative);json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',s,re.S)[1])
 dest=target/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);total+=dest.stat().st_size;count+=1
assert total<256*1048576,('Archive limit',total)
print('Public package',count,'files',round(total/1048576,2),'MiB')
