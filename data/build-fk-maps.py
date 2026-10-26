from pathlib import Path
import json,gzip,re
ROOT=Path(__file__).resolve().parent.parent;OUT=ROOT/'dist/data/deepdives';series={};metadata={}
# key, table, measure, label, unit, thematic group, optional fixed dimensions
specs=[
('doubleDaysChild','FPDubbeldagarArLan','dagar_per_barn_dd','Dubbeldagar per barn','dagar/barn','Föräldraförsäkring',{}),
('doubleDaysChildren','FPDubbeldagarArLan','antal_barn_dd','Barn med uttagna dubbeldagar','barn','Föräldraförsäkring',{}),
('parentEqual','fp4060lan','andel','Barn med jämställt uttag av föräldrapenning','%','Föräldraförsäkring',{}),
('dentalSupport','tvshogkostnadsskydd','andel','Högkostnadsskydd för tandvård','%','Tandvård',{}),
('sickness20','SJPT2','spt','Sjukpenningtalet 2.0','nettodagar/försäkrad','Socialförsäkring & sjukfall',{}),
('ongoingSick','SJPPagSjukfallKommun','antal','Pågående sjukfall','sjukfall','Socialförsäkring & sjukfall',{}),
('activityRecipients','SAManBestAnskanlAkters','antal','Mottagare av aktivitetsersättning','personer','Socialförsäkring & sjukfall',{}),
('vabRecipients','tfpVabAntalDagarBeloppLanKommun','antal_bm','Mottagare av vab','personer','Föräldraförsäkring',{}),
('vabDaysRecipient','tfpVabAntalDagarBeloppLanKommun','ratio','Vabdagar per mottagare','nettodagar/mottagare','Föräldraförsäkring',{}),
('vabMenShare','tfpVabAntalDagarBeloppLanKommun','andel_nettodagar','Mäns andel av vabdagarna','%','Föräldraförsäkring',{'kon_kod':'M'}),
('parentRecipients','FPAntalDagarBeloppLanKommun','ant_mottagar','Mottagare av föräldrapenning','personer','Föräldraförsäkring',{}),
('parentDaysRecipient','FPAntalDagarBeloppLanKommun','ratio','Föräldrapenningdagar per mottagare','nettodagar/mottagare','Föräldraförsäkring',{}),
('parentMenShare','FPAntalDagarBeloppLanKommun','andel_nettodagar','Mäns andel av föräldrapenningdagarna','%','Föräldraförsäkring',{'kon':'M'}),
('newActivity','SABeviljadeArDiagnosLan','antal','Förstagångsbeviljad aktivitetsersättning','beslut','Socialförsäkring & sjukfall',{'delforman':'A'}),
('newSickness','SABeviljadeArDiagnosLan','antal','Förstagångsbeviljad sjukersättning','beslut','Socialförsäkring & sjukfall',{'delforman':'S'})]
for key,file,measure,label,unit,group,fixed in specs:
 c=json.loads(gzip.decompress((OUT/('FK-'+file+'.json.gz')).read_bytes()));dims={d['id']:d for d in c['dimensions']};indexes={k:{v[0]:i for i,v in enumerate(d['values'])} for k,d in dims.items()};sel={}
 for k,d in dims.items():sel[k]=next((v[0] for v in d['values'] if v[0].startswith('ALL')),d['values'][0][0])
 sel.update(fixed)
 def get(m):
  selection=sel|{'Matt':m};i=0
  for d in c['dimensions']:i=i*len(d['values'])+indexes[d['id']][selection[d['id']]]
  return c['values'][i] if isinstance(c['values'],list) else c['values'].get(str(i))
 periods={};rows={}
 for period,_ in dims['Tid']['values']:periods[period[:4]]=max(period,periods.get(period[:4],''))
 for y,period in periods.items():
  sel['Tid']=period
  for geo,_ in dims['Region']['values']:
   sel['Region']=geo
   if measure=='ratio':
    days=get('nettodagar');recipients=get('antal_bm' if key.startswith('vab') else 'ant_mottagar');v=days/recipients if days is not None and recipients is not None and recipients>0 else None
   else:v=get(measure)
   if v is not None:rows.setdefault(y,{})[geo]=v
 codes={k for v in rows.values() for k in v};assert rows,key;series[key]=rows
 definition=' '.join(c['notes'])
 if measure=='ratio':definition+=' Härlett: redovisade nettodagar dividerat med antal mottagare, samma kön, period och område. Det är inte antal dagar per barn eller per invånare.'
 if key in ['vabMenShare','parentMenShare']:definition+=' Mäns andel av de ersatta nettodagarna, inte andel män som är föräldralediga eller allt obetalt omsorgsarbete.'
 monthly=any('-' in p for p in periods.values())
 if monthly:definition+=' Årskartan visar senast redovisade månad inom valt år. Månadsantal summeras inte till årspersoner. Ingen automatisk årstrend bedöms.'
 metadata[key]={'label':label,'group':group,'source':'Försäkringskassan','code':file,'url':c['url'],'license':c['license'],'unit':unit,'years':sorted(map(int,rows)),'country':'00' in codes,'county':any(len(k)==2 and k!='00' for k in codes),'municipality':any(len(k)==4 for k in codes),'count':sum(map(len,rows.values())),'definition':definition,'periods':periods,'retrieved':'25 oktober 2026','fkAddition':True,'rateComparison':unit in ['%','dagar/barn','nettodagar/försäkrad','nettodagar/mottagare'],'noTrend':monthly or key.startswith('doubleDays') or key=='dentalSupport'}
(ROOT/'dist/data/fk-additions.json').write_text(json.dumps({'series':series,'metadata':metadata},ensure_ascii=False,separators=(',',':')))
for path in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/path;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['social'].update(series);d['extraMetadata'].update(metadata);s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if 'FK_ADDITIONS_V1' not in s:
  s=s.replace('const groupForMetric=key=>{',"const groupForMetric=key=>{ // FK_ADDITIONS_V1\n if(D.extraMetadata[key]?.fkAddition)return D.extraMetadata[key].group;",1)
  marker='    sparkline(measure,type,id,obj);'
  block="""    if(D.extraMetadata[measure]?.fkAddition){const m=D.extraMetadata[measure],sy=latestAvailableYear(measure,year);$('info-'+measure).textContent=m.source+' · '+m.code+' · period '+(m.periods?.[sy]||'saknas')+' · '+[m.country?'riket':null,m.county?'län':null,m.municipality?'kommun':null].filter(Boolean).join('/');$('secondary-'+measure).textContent=m.definition;}
"""
  assert marker in s;s=s.replace(marker,block+marker,1)
  s=s.replace('Fördjupning: skola, livsvillkor och kommunal ekonomi','Fördjupning: livsvillkor, socialförsäkring och ekonomi').replace('Fördjupningstabeller · skola och livsvillkor','Fördjupningstabeller · livsvillkor och socialförsäkring')
  if path=='dist/focus/index.html':
   s=s.replace("isRate=unit.includes('%')", "isRate=D.extraMetadata[key]?.rateComparison||unit.includes('%')",1)
   s=s.replace("'Hälsa och sjukfrånvaro','Befolkning och hushåll'", "'Hälsa och sjukfrånvaro','Socialförsäkring & sjukfall','Tandvård','Föräldraförsäkring','Befolkning och hushåll'",1)
   marker="  if(group==='Skola · elevernas villkor')"
   block="""  if(group==='Socialförsäkring & sjukfall')paragraphs.push('Sjukpenningtalet med den nya definitionen relaterar ersatta dagar till uppskattat antal sjukpenningförsäkrade. Det hålls isär från det äldre måttet. Pågående sjukfall är ett bestånd, medan förstagångsbeviljad ersättning är ett inflöde av beslut. Antalen påverkas av befolkningens storlek och beskriver inte all ohälsa. Månadsserierna visar den senast redovisade månaden, inte summan av årets mottagare.');
  if(group==='Tandvård')paragraphs.push('Tandvårdsuppgiften gäller mottagare av det statliga högkostnadsskyddet. Den visar varken all tandvård eller hela befolkningens tandhälsa. Ändrade regler och åldersgränser påverkar jämförbarheten.');
  if(group==='Föräldraförsäkring')paragraphs.push('Uttaget av föräldrapenning och vab beskriver ersatta dagar och mottagare. Nettodagar räknar om deldagar till hela dagar. Männens andel av dagarna och föräldrarnas jämna fördelning är olika mått; inget av dem omfattar allt obetalt omsorgsarbete. Dubbeldagar avser samtidig föräldraledighet, och ändrade regler begränsar jämförelser bakåt.');
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
   marker=" const missingText=missing.length?"
   block=""" if(deepAvailable.some(c=>c.id==='FK-SJPAntalmottagarediagnos'))additionalContext+='<h3>Diagnoser, ersättningar och livsvillkor</h3><p>De nationella diagnosuppgifterna visar sjuk- och rehabiliteringspenning, ersatta dagar och mottagare. För arbetsskadelivränta finns egna uppdelningar efter ålder, kön och födelsekohort. De beskriver ersättningar enligt försäkringens regler, inte hur många som totalt har en sjukdom eller arbetsskada i kommunen. Olika diagnosgrupper och totaler kan överlappa och ska inte summeras okritiskt.</p>';
 if(deepAvailable.some(c=>c.id.startsWith('FK-')))additionalContext+='<p>I fördjupningen finns samtliga hämtade uppdelningar av Försäkringskassans uppgifter efter bland annat kön, ålder, diagnos, sjukfallslängd, ersättningens omfattning och föräldrapenningens dagtyp. Varje tabell visar sin egen geografiska nivå och mätperiod. Nationella grupper är inte lokala uppskattningar.</p>';
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
 tmp=p.with_suffix('.next.html');tmp.write_text(s);tmp.replace(p)
print('Added',len(series),'FK map measures')
