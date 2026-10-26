"""Återskapa SCB- och CSN-underlag för skolutökningen, med fulla tidsserier."""
from pathlib import Path
import urllib.request,urllib.parse,json,concurrent.futures
R=Path(__file__).resolve().parent/'additions-2026-10-25'
IDS=['TAB6859','TAB6861','TAB6851','TAB4200','TAB4066','TAB1487','TAB1488','TAB6798','TAB4169']
def scb(id):
 m=json.load(urllib.request.urlopen(f'https://statistikdatabasen.scb.se/api/v2/tables/{id}/metadata?lang=sv',timeout=40));q={'lang':'sv','outputFormat':'json-stat2'};q.update({'valueCodes['+k+']':'*' for k in m['id']})
 if id=='TAB4200':q['valueCodes[Verksomrkom]']='950'
 d=json.load(urllib.request.urlopen(f'https://statistikdatabasen.scb.se/api/v2/tables/{id}/data?'+urllib.parse.urlencode(q),timeout=60));(R/(id+'.json')).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')));return id
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for id in pool.map(scb,IDS):print(id,flush=True)
 id='SUSHSVL30.px';u='https://statistik.csn.se/PxWeb/api/v1/sv/CSNstat/SU/L/SH/SV/'+id;m=json.load(urllib.request.urlopen(u,timeout=40));(R/(id+'.meta.json')).write_text(json.dumps(m,ensure_ascii=False));q={'query':[{'code':v['code'],'selection':{'filter':'item','values':v['values']}} for v in m['variables']],'response':{'format':'json'}}
 for fmt in ['json','px']:
  q['response']['format']=fmt;b=urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(q).encode(),headers={'Content-Type':'application/json'}),timeout=90).read();(R/(id+'.'+fmt)).write_bytes(b)
 (R/(id+'.source.json')).write_text(json.dumps({'api':u,'license':'CC0','source':'CSN','retrieved':'2026-10-25'}));print(id)
