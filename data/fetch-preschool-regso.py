"""Hämta hela FHM-tabellen i årsbitar under API:ets cellgräns."""
from pathlib import Path
import json,urllib.request
R=Path(__file__).resolve().parent/'additions-2026-10-25';id='InskForskRegso.px'
u='https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/api/v1/sv/A_Folkhalsodata/A_Mo8/1_Tidigalivet/02Forskola/01.07InskForsk/'+id
m=json.load(urllib.request.urlopen(u,timeout=45));(R/(id+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False))
rows=[];result=None
for start in (0,6):
 q={'query':[{'code':v['code'],'selection':{'filter':'item','values':v['values'][start:start+6] if v.get('time') or v['code']=='År' else v['values']}} for v in m['variables']],'response':{'format':'json'}}
 result=json.load(urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(q).encode(),headers={'Content-Type':'application/json'}),timeout=90));rows.extend(result['data']);print('Hämtat',len(rows),'celler',flush=True)
result['data']=rows;(R/(id+'.json')).write_text(json.dumps(result,ensure_ascii=False));(R/(id+'.source.json')).write_text(json.dumps({'api':u,'license':'CC0','retrieved':'2026-10-25'}))
