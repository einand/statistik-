"""Inför skol-, resurs- och ekonomiuppgifter utan att blanda index, modeller och utfall."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-2026-10-25'
SPECS=[('compulsoryEfficiency','U15900'),('preschoolResource','U11001'),('preschoolQuality','U11404'),('gymnasiumEfficiency','U17900'),('compulsoryResource','U15010'),('preschoolEfficiency','U11901'),('compulsoryQuality','U15401'),('gymnasiumResource','U17001'),('preschoolRevenue','N11002'),('gymnasiumReferenceResident','N17016'),('gymnasiumReferencePupil','N17029'),('gymnasiumProduction','N17042'),('gymnasiumNeed','N17041'),('cultureCost','N09100'),('compulsoryReference','N15018'),('compulsoryOtherCost','N15010'),('schoolForeignBalance','N15217')]
series={};metadata={}
for key,code in SPECS:
 d=json.loads((R/(code+'.json')).read_text());m=d['metadata'];vs={}
 for r in d['rows']:
  value=next((v['value'] for v in r['values'] if v['gender']=='T' and v.get('value') is not None and not v.get('isdeleted')),None)
  if value is None:continue
  id=r.get('municipality') or r.get('region');id='00' if id=='0000' else id
  vs.setdefault(str(r['period']),{})[id]=value
 assert vs,key
 isindex=code.startswith('U');unit='indexpoäng (0–100)' if isindex else 'balanstal' if key=='schoolForeignBalance' else 'kr/elev' if 'kr/elev' in m['title'] else 'kr/inv'
 group='Kultur & kommunal ekonomi' if key=='cultureCost' else 'Skola · kvalitet och resurser'
 caveat=' Relativt normaliserat index, inte procent. Ingen trend eller automatisk kvalitetsbedömning. Högt resursindex betyder lägre relativa kostnader, inte mer resurser eller högre kvalitet. Yttervärden klipps.' if isindex else ' Belopp i löpande priser, inte inflationsjusterat. Modellberäknade referenskostnader, produktionsförutsättningar och behovsnivåer är inte kommunens faktiska kostnad eller skolans kvalitet.'
 if key=='schoolForeignBalance':caveat=' Balanstal, inte procent. Ett motsvarar samma andel utrikes födda bland personal och befolkning. Ingen bedömning av enskilda personer eller skolornas kvalitet.'
 series[key]=vs;metadata[key]={'label':m['title'],'group':group,'source':'Kolada / RKA' if isindex else 'Kolada','code':code,'unit':unit,'years':sorted(map(int,vs)),'country':any('00' in v for v in vs.values()),'county':False,'municipality':True,'count':sum(map(len,vs.values())),'url':'https://api.kolada.se/v3/kpi/'+code,'license':'CC BY 4.0','retrieved':'25 oktober 2026','definition':m['description']+caveat,'relativeIndex':isindex}
base=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',(ROOT/'dist/index.html').read_text(),re.S)[1])
def obs(d,selection):
 index=0
 for k,size in zip(d['id'],d['size']):index=index*size+d['dimension'][k]['category']['index'][selection[k]]
 return d['value'].get(str(index)) if isinstance(d['value'],dict) else d['value'][index]
for key,table,code,label in [('preschoolActualCost','TAB4169','055ny','Kostnad förskola · hemkommun, kr/inv'),('compulsoryActualCost','TAB1487','440ny','Kostnad grundskola · hemkommun, kr/inv'),('gymnasiumActualCost','TAB1488','760','Kostnad gymnasium · hemkommun, kr/inv')]:
 d=json.loads((R/(table+'.json')).read_text());vs={}
 for y in d['dimension']['Tid']['category']['index']:
  for id in d['dimension']['Region']['category']['index']:
   value=obs(d,{'Region':id,'Nyckeltal':code,'ContentsCode':next(iter(d['dimension']['ContentsCode']['category']['index'])),'Tid':y});pop=base['national'].get(y) if id=='00' else base['municipalPopulation'].get(y,{}).get(id)
   if value is not None and pop and pop>0:vs.setdefault(y,{})[id]=value*1000/pop
 series[key]=vs;metadata[key]={'label':label,'group':'Skola · kvalitet och resurser','source':'SCB · egen beräkning','code':table+' / '+code,'unit':'kr/inv','years':sorted(map(int,vs)),'country':True,'county':False,'municipality':True,'count':sum(map(len,vs.values())),'url':'https://statistikdatabasen.scb.se/api/v2/tables/'+table,'license':'CC0','retrieved':'25 oktober 2026','definition':'SCB:s publicerade kostnad för hemkommun i tkr multiplicerad med tusen och dividerad med SCB:s folkmängd samma år. Kr per invånare, INTE kr per elev. Samtliga kostnadskomponenter, skolkommun och hemkommun hålls åtskilda i de lokala fördjupningstabellerna. Belopp i löpande priser. '+ ' '.join(d.get('note',[]))}
d=json.loads((R/'TAB4200.json').read_text());vs={};private={}
for y in d['dimension']['Tid']['category']['index']:
 for id in d['dimension']['Region']['category']['index']:
  select={'Region':id,'Verksomrkom':'950','ContentsCode':'0000005W','Tid':y};total=obs(d,select);select['ContentsCode']='00000068';part=obs(d,select);pop=base['national'].get(y) if id=='00' else base['municipalPopulation'].get(y,{}).get(id)
  if total is not None and pop and pop>0:vs.setdefault(y,{})[id]=total*1000/pop
  if total and part is not None:private.setdefault(y,{})[id]=100*part/total
for key,values,label,unit in [('purchasedServicesResident',vs,'Köp av huvudverksamhet, kr/inv','kr/inv'),('purchasedPrivateShare',private,'Privatägda företags andel av verksamhetsköpen','%')]:
 series[key]=values;metadata[key]={'label':label,'group':'Verksamhetsköp & utförare','source':'SCB · egen beräkning','code':'TAB4200','unit':unit,'years':sorted(map(int,values)),'country':True,'county':False,'municipality':True,'count':sum(map(len,values.values())),'url':'https://statistikdatabasen.scb.se/api/v2/tables/TAB4200','license':'CC0','retrieved':'25 oktober 2026','definition':'Totalsumma köp av huvudverksamhet. Kr/inv är tkr multiplicerat med tusen dividerat med SCB:s folkmängd samma år. Andel är köp från privatägda företag delat med totala köp. Ingen värdering av utförarkvalitet eller effektivitet. Belopp i löpande priser. Äldre andelstabell TAB4066 och nationell verksamhets-/utförartabell TAB6851 hålls separata på grund av skillnader i population, definition och enhet. '+ ' '.join(d.get('note',[]))}
(ROOT/'dist/data/school-expansion.json').write_text(json.dumps({'series':series,'metadata':metadata},ensure_ascii=False,separators=(',',':')))
for name in ['dist/index.html','dist/lan/index.html','dist/focus/index.html']:
 p=ROOT/name;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['social'].update(series);d['extraMetadata'].update(metadata);s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if 'SCHOOL_EXPANSION_V1' not in s:
  s=s.replace('const groupForMetric=key=>{',"const groupForMetric=key=>{ // SCHOOL_EXPANSION_V1\n if(['Skola · kvalitet och resurser','Kultur & kommunal ekonomi','Verksamhetsköp & utförare'].includes(D.extraMetadata[key]?.group))return D.extraMetadata[key].group;",1)
  marker='    sparkline(measure,type,id,obj);'
  block="""    if(['Skola · kvalitet och resurser','Kultur & kommunal ekonomi','Verksamhetsköp & utförare'].includes(D.extraMetadata[measure]?.group)){
      const m=D.extraMetadata[measure],sy=latestAvailableYear(measure,year);
      $('info-'+measure).textContent=m.source+' · '+m.code+' · mätår '+sy+' · '+m.unit+' · kommunnivå'+(m.country?' och riket':'');
      $('secondary-'+measure).textContent=absolute==null?'Ingen uppgift för vald plats eller period. Länsvärden beräknas inte.':m.relativeIndex?'Relativt index, inte procent eller absolut kvalitetsbetyg. Högt resursindex betyder lägre relativa kostnader.':measure==='schoolForeignBalance'?'Balanstal: 1 betyder samma andel utrikes födda bland personal och befolkning.':'Löpande priser där måttet gäller kronor. Modellvärden är inte faktiska kostnader. Se fullständig definition nedan.';
    }
"""
  assert marker in s;s=s.replace(marker,block+marker,1)
  if name=='dist/focus/index.html':
   s=s.replace("if(type==='town'||['greenArea'", "if(D.extraMetadata[key]?.relativeIndex)return '';\n if(type==='town'||['greenArea'",1)
   s=s.replace("unit.includes('kr/person')", "unit.includes('kr/')||key==='schoolForeignBalance'",1)
   s=s.replace("  const label=plainLabel(METRIC_LABELS[key]", "  if(D.extraMetadata[key]?.relativeIndex&&!Number.isFinite(national)){const values=Object.keys(D.municipalities).map(p=>rawValue(key,'municipality',p,y)).filter(Number.isFinite);national=values.length?values.reduce((a,b)=>a+b,0)/values.length:null;reference='genomsnittet bland kommuner med uppgift';}\n  if(key==='schoolForeignBalance'){national=1;reference='balans mellan personalens och befolkningens andel utrikes födda';}\n  const label=plainLabel(METRIC_LABELS[key]",1)
   s=s.replace("'Digital infrastruktur','Politisk representation'", "'Digital infrastruktur','Skola · kvalitet och resurser','Kultur & kommunal ekonomi','Verksamhetsköp & utförare','Politisk representation'",1)
   marker="  if(group==='Politisk representation')"
   block="""  if(group==='Skola · kvalitet och resurser')paragraphs.push('Skolans kvalitets-, resurs- och effektivitetsindex är relativa jämförelser. Högt resursindex betyder lägre relativa kostnader, inte mer personal eller bättre undervisning. Referenskostnad, behovsnivå och produktionsförutsättningar är modellberäkningar; de ska hållas isär från faktiska kostnader och intäkter. Kr per invånare och kr per elev beskriver olika saker. Beloppen tar inte hänsyn till inflation.');
  if(group==='Verksamhetsköp & utförare')paragraphs.push('Verksamhetsköpen beskriver hur mycket kommunen köper in och från vilka utförare. En större privat andel säger inget i sig om kvalitet eller effektivitet. Äldre serier med andra definitioner visas separat i fördjupningen.');
  if(group==='Kultur & kommunal ekonomi')paragraphs.push('Kulturkostnaden omfattar bland annat bibliotek, föreningsstöd och musik- och kulturskola. Högre utgifter betyder inte automatiskt bättre verksamhet, och beloppen är inte inflationsjusterade.');
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
 temp=p.with_suffix('.next.html');temp.write_text(s);temp.replace(p)
print('Installed',len(series),'new regional metrics.')
