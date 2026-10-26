from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'dist/data/deepdives'
base=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',(ROOT/'dist/index.html').read_text(),re.S)[1])
SPECS=[('teacherRelations','socrBaReg.px','Goda relationer till lärare · barn'),('schoolBullying','mobBaReg.px','Mobbad i skolan · barn'),('schoolDisability','funkBaReg.px','Funktionsnedsättning som påverkar skolan · barn'),('schoolStress','skosBaReg.px','Stressad av skolarbetet · barn'),('preschoolEnrolled','InskForskReg.px','Inskrivna barn i förskola')]
SPECS += [('travel'+str(i),'MHEv1TraXReg.px','Vanligt färdsätt · '+label) for i,label in enumerate(['gång','cykel eller liknande','bil eller motorcykel','kollektivtrafik','annat färdmedel'],1)]
SPECS += [('csnWithdrawal','SUSHSVL30.px','Indragen studiehjälp på grund av ogiltig frånvaro')]
series={};meta={};intervals={}
def endyear(s):return int(re.findall(r'\d{4}',s)[-1])
def get(c,sel):
 index=0
 for d in c['dimensions']:
  codes=[v[0] for v in d['values']];index=index*len(codes)+codes.index(sel[d['id']])
 return c['values'][index]
for key,file,label in SPECS:
 c=json.loads((OUT/(file+'.json')).read_text());sel={};dims={d['id']:d for d in c['dimensions']}
 for d in c['dimensions']:
  selected=next((v for v in d['values'] if re.match('^(Totalt|Andel$)',v[1],re.I)),d['values'][0]);sel[d['id']]=selected[0]
 if key.startswith('travel'):sel['Aktivitet']='3';sel['Färdsätt']=key[-1]
 if key=='csnWithdrawal':sel[c['measure']]=next(v[0] for v in dims[c['measure']]['values'] if v[1].startswith('Andel'));sel['Skolform']='0'
 periods={};rows={};ci={}
 for period in dims[c['time']]['values']:
  y=str(endyear(period[1]));sel[c['time']]=period[0]
  for geo in dims[c['region']]['values']:
   code=geo[0]
   if c.get('regionAliases'):
    codes=[k for k,v in c['regionAliases'].items() if v==geo[0]];code=codes[0] if codes else None
   if code not in ['00',*base['names'],*base['municipalities']]:continue
   sel[c['region']]=geo[0];value=get(c,sel)
   if value is not None:rows.setdefault(y,{})[code]=value;periods[y]=period[1]
   if c.get('measure') and key!='csnWithdrawal':
    for measure in dims[c['measure']]['values']:
     if 'Konfidensintervall' in measure[1]:
      original=sel[c['measure']];sel[c['measure']]=measure[0];v=get(c,sel);sel[c['measure']]=original
      if v is not None:ci.setdefault(y,{}).setdefault(code,{})['lower' if 'nedre' in measure[1] else 'upper']=v
 assert rows,key
 series[key]=rows;intervals[key]=ci
 group='Skola · elevernas villkor' if key in ['teacherRelations','schoolBullying','schoolDisability','schoolStress'] else 'Transportvanor' if key.startswith('travel') else 'Förskola & deltagande' if key=='preschoolEnrolled' else 'Studiehjälp & frånvaro'
 codes={k for v in rows.values() for k in v}
 definition=' '.join(c['notes'])
 if key.startswith('travel'):definition+=' Vanligaste färdsätt till arbete, skola eller andra aktiviteter kombinerat. Vuxna 18–84 år. Ingen trend bedöms.'
 if key=='csnWithdrawal':definition+=' Avser samtliga skolformer och kön, efter folkbokföring i Sverige. Andel enligt CSN, inte frånvarons omfattning eller alla gymnasieelever. Läsåret placeras vid sitt slutår. Historiska värden är inte prognoser. Köns-, skolforms-, läns- och kommunuppdelningar finns i den fullständiga fördjupningstabellen.'
 meta[key]={'label':label,'group':group,'source':c['source'],'code':file,'unit':'%','years':sorted(map(int,rows)),'country':'00' in codes,'county':any(k in base['names'] for k in codes),'municipality':any(k in base['municipalities'] for k in codes),'count':sum(map(len,rows.values())),'url':c['url'],'license':c['license'],'retrieved':'25 oktober 2026','definition':definition,'periods':periods,'noTrend':key!='csnWithdrawal' and key!='preschoolEnrolled'}
(ROOT/'dist/data/school-regional.json').write_text(json.dumps({'series':series,'metadata':meta,'confidence':intervals},ensure_ascii=False,separators=(',',':')))
for name in ['dist/index.html','dist/lan/index.html','dist/focus/index.html']:
 p=ROOT/name;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['social'].update(series);d['extraMetadata'].update(meta);d['schoolConfidence']=intervals;s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if 'SCHOOL_REGIONAL_V1' not in s:
  s=s.replace('const groupForMetric=key=>{',"const groupForMetric=key=>{ // SCHOOL_REGIONAL_V1\n if(['Skola · elevernas villkor','Transportvanor','Förskola & deltagande','Studiehjälp & frånvaro'].includes(D.extraMetadata[key]?.group))return D.extraMetadata[key].group;",1)
  marker='    sparkline(measure,type,id,obj);'
  block="""    if(Object.hasOwn(D.schoolConfidence||{},measure)){
      const m=D.extraMetadata[measure],sy=latestAvailableYear(measure,year),ci=D.schoolConfidence[measure]?.[sy]?.[type==='country'?'00':id];
      $('info-'+measure).textContent=m.source+' · '+m.code+' · mätperiod '+(m.periods?.[sy]||sy)+' · '+[m.country?'riket':null,m.county?'län':null,m.municipality?'kommun':null].filter(Boolean).join('/');
      $('secondary-'+measure).textContent=absolute==null?'Ingen uppgift på vald nivå och period. Se nationella eller regionala fördjupningar.':(ci?'Konfidensintervall '+fraction.format(ci.lower)+'–'+fraction.format(ci.upper)+' % · ':'')+(m.noTrend?'Ingen säker trend bedöms.':'Period och definition framgår nedan.');
    }
"""
  assert marker in s;s=s.replace(marker,block+marker,1)
  if name=='dist/focus/index.html':
   s=s.replace("if(D.extraMetadata[key]?.relativeIndex)return '';", "if(D.extraMetadata[key]?.relativeIndex||D.extraMetadata[key]?.noTrend)return '';",1)
   s=s.replace("'Digital infrastruktur','Skola · kvalitet och resurser'", "'Digital infrastruktur','Skola · elevernas villkor','Förskola & deltagande','Studiehjälp & frånvaro','Transportvanor','Skola · kvalitet och resurser'",1)
   marker="  if(group==='Skola · kvalitet och resurser')"
   block="""  if(group==='Skola · elevernas villkor')paragraphs.push('Barnens svar om lärarrelationer, skolstress, mobbning och funktionsnedsättning gäller ett urval av skolelever. De beskriver inte varje skola eller kommuninvånare. Skillnader ska tolkas med hänsyn till urval och osäkerhet. Länsuttaget och de nationella grupptabellerna kan ha olika urval och vikter.');
  if(group==='Förskola & deltagande')paragraphs.push('Förskoleinskrivning beskriver deltagande, inte förskolans kvalitet. Nationella uppdelningar efter föräldrarnas utbildning, hushållets inkomst, födelseland och områdestyp finns i fördjupningen. De grupperna är inte lokala kommunvärden.');
  if(group==='Studiehjälp & frånvaro')paragraphs.push('Indragen studiehjälp är CSN:s uppgift om stöd som dragits in på grund av ogiltig frånvaro. Den mäter inte all frånvaro eller alla elevers situation. Uppgifterna avser läsår och folkbokföring, inte enbart skolor som ligger på platsen.');
  if(group==='Transportvanor')paragraphs.push('Färdsätten bygger på vuxnas enkätsvar om resor till arbete, skola och andra aktiviteter. De är inte uppmätta trafikflöden och kan inte beskriva varje kommuns resvanor.');
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
 temp=p.with_suffix('.next.html');temp.write_text(s);temp.replace(p)
print('Added regional companion tables and CSN:',[(k,len(v),sum(map(len,v.values()))) for k,v in series.items()])
