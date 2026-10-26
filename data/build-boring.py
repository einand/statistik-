"""Derive a compact easy-reading view from the site's existing municipal data."""
from pathlib import Path
import json,re,gzip,datetime
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'dist/index.html').read_text()
d=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',source,re.S)[1])
score=json.loads((ROOT/'dist/data/score-input.json').read_text())
base={
'hours':('Avtalad arbetstid','timmar/vecka','Arbete','Avtalad arbetstid. Det är inte samma sak som faktiskt arbetade timmar.'),
'unemployment':('Arbetslöshet','%','Arbete','Andelen arbetslösa enligt källans definition. Alla som saknar arbete ingår inte.'),
'employment':('Andel som arbetar','%','Arbete','Andelen som arbetar i den åldersgrupp som källan mäter.'),
'income':('Medianinkomst','kr/år','Pengar','Inkomsten för den som ligger i mitten när inkomsterna sorteras. Det är inte medelinkomsten. Beloppet är före justering för ändrade priser.'),
'sickness':('Sjukpenningdagar','dagar per försäkrad','Hälsa','Dagar med sjukpenning per försäkrad. Det mäter inte antalet sjuka eller all sjukfrånvaro.'),
'wage':('Lön för kommunanställda','kr/mån','Arbete','Månadslön för kommunanställda. Det är inte lönen för alla som bor i kommunen.')}
series=dict(d['social']); metadata=dict(d['extraMetadata'])
for key,(label,unit,group,definition) in base.items():
 metadata[key]={**score.get('metadata',{}).get(key,{}),'label':label,'unit':unit,'group':group,'definition':definition}
for key,local,country,label,unit,definition in [
 ('population','municipalPopulation','national','Invånare','personer','Antalet folkbokförda invånare i kommunen.'),
 ('immigration','immigrationMunicipal','immigration','Flyttar från andra länder','invandringar','Registrerade invandringar. Det är flytthändelser, inte alla utrikes födda som bor här.'),
 ('crime','crimeMunicipal','crime','Anmälda brott','anmälda brott','Brott som har anmälts. Det visar inte alla brott som har begåtts. Anmälningar och polisens arbete påverkar värdet.')]:
 series[key]={}
 for year,rows in d[local].items():
  national=d[country].get(year); national=national.get('00') if isinstance(national,dict) else national
  series[key][year]={**rows,'00':national}
 metadata[key]={'label':label,'unit':unit,'group':'Människor' if key!='crime' else 'Trygghet','definition':definition,'source':'Brå' if key=='crime' else 'SCB','url':'https://bra.se/statistik' if key=='crime' else 'https://www.scb.se/'}
# The four derived measures already used by the maps; use exact matching years.
for key,parent,scale,label,unit,definition in [
 ('crime100k','crime',100000,'Anmälda brott i förhållande till folkmängden','per 100 000 inv.','Antalet anmälda brott delat med folkmängden samma år. Anmälda brott är inte alla begångna brott.'),
 ('immigration1000','immigration',1000,'Inflyttning från andra länder i förhållande till folkmängden','per 1 000 inv.','Registrerade invandringar delade med folkmängden samma år. Flytthändelser, inte alla utrikes födda.')]:
 series[key]={}
 for year,rows in series[parent].items():
  pop=series['population'].get(year,{})
  series[key][year]={code:value/pop[code]*scale for code,value in rows.items() if isinstance(value,(int,float)) and isinstance(pop.get(code),(int,float)) and pop[code]>0}
 metadata[key]={'label':label,'unit':unit,'group':'Trygghet' if key=='crime100k' else 'Människor','definition':definition,'source':'Brå och SCB' if key=='crime100k' else 'SCB','url':'https://bra.se/statistik' if key=='crime100k' else 'https://www.scb.se/','rateComparison':True}
for lag in [1,10]:
 key='growth'+str(lag);series[key]={}
 for year,rows in series['population'].items():
  before=series['population'].get(str(int(year)-lag),{})
  series[key][year]={code:(value/before[code]-1)*100 for code,value in rows.items() if isinstance(value,(int,float)) and isinstance(before.get(code),(int,float)) and before[code]>0}
 metadata[key]={'label':'Befolkningsförändring på '+str(lag)+' år','unit':'%','group':'Människor','definition':'Folkmängdens förändring mellan två observerade år, med '+str(lag)+' års mellanrum. Samma källserie som befolkningskartan.','source':'SCB','url':'https://www.scb.se/','rateComparison':False}

now=datetime.datetime.now().year
out={'municipalities':{k:v['name'] for k,v in d['municipalities'].items()},'metrics':{}}
for key,table in series.items():
 years=sorted((int(y) for y in table if int(y)<=now),reverse=True)
 if not years:continue
 year=years[0];values=table[str(year)];meta=metadata.get(key,{'label':key,'unit':'','group':'Övrigt'})
 # Keep exact source observation and same-year country value; never substitute a parent area.
 local={k:v for k,v in values.items() if k in out['municipalities'] and isinstance(v,(int,float))}
 prev={}
 if key in ('population','income','employment','unemployment','school','health','broadband100') and not meta.get('noTrend'):
  for y in years[1:]:
   for code,val in table[str(y)].items():
    if code in local and code not in prev and isinstance(val,(int,float)):prev[code]=[y,val]
 country=values.get('00')
 out['metrics'][key]={'meta':meta,'year':year,'period':str(meta.get('periods',{}).get(str(year),year)),'values':local,'country':country if isinstance(country,(int,float)) else None,'previous':prev}
raw=json.dumps(out,ensure_ascii=False,separators=(',',':')).encode()
target=ROOT/'dist/data/boring.json.gz';target.write_bytes(gzip.compress(raw,mtime=0))
print('Easy view:',len(out['metrics']),'measures,',len(out['municipalities']),'municipalities,',target.stat().st_size,'bytes')
