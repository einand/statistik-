import urllib.request,csv,io,json,gzip,time
from pathlib import Path
root=Path(__file__).resolve().parent.parent;out=root/'data/additions-2026-10-24';u='https://data.svk.se/datastore/dump/4aa94b88-9f42-4f0a-a6a8-8e47aadc782a?format=csv'
try:
 r=urllib.request.urlopen(u,timeout=60);reader=csv.DictReader(io.TextIOWrapper(r,encoding='utf-8-sig'));print('fields',reader.fieldnames,flush=True)
 groups={};n=0
 for row in reader:
  t=row['start_time_utc'];y=t[:4];key=row['from_bidding_zone']+'>'+row['to_bidding_zone'];power=float(row['power']);groups.setdefault(y,{}).setdefault(key,[]).append([t,power]);n+=1
  if n%200000==0:print('rows',n,flush=True)
 for y,borders in groups.items():
  for rows in borders.values():rows.sort()
  p=root/('dist/data/electricity-flows-'+y+'.json.gz');
  with gzip.open(p,'wt',encoding='utf-8',compresslevel=9) as f:json.dump({'year':int(y),'borders':borders},f,separators=(',',':'))
 summary={y:{b:{'count':len(rs),'first':rs[0][0],'last':rs[-1][0],'latestMW':rs[-1][1],'minMW':min(r[1] for r in rs),'maxMW':max(r[1] for r in rs),'meanMW':round(sum(r[1] for r in rs)/len(rs),2)} for b,rs in borders.items()} for y,borders in groups.items()}
 (root/'dist/data/electricity-summary.json').write_text(json.dumps({'source':'Svenska kraftnät','license':'CC BY 4.0','retrieved':'2026-10-24','records':n,'years':summary},separators=(',',':')));print('COMPLETE',n,[(y,len(b)) for y,b in groups.items()],flush=True)
except Exception as e:print('ERROR',str(e),flush=True);raise
