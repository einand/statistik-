"""Inför de tolv beställda källorna. Råfiler finns i additions-2026-10-24."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
R=ROOT/'data/additions-2026-10-24'
SPECS=[
 ('kitchenTraining','U50105','Utbildad måltidspersonal i kommunala särskilda boenden','kategori','Måltider & omsorg'),
 ('regionPoliticianIncome','N65827','Regionpolitikers mediannettonettoinkomst','kr/person','Politisk representation'),
 ('regionPartTime','N65811','Regionpolitiker på deltid','%','Politisk representation'),
 ('municipalFullTime','N05810','Kommunpolitiker på heltid','%','Politisk representation'),
 ('regionFullTime','N65810','Regionpolitiker på heltid','%','Politisk representation'),
 ('municipalWomen','N05814','Kvinnor bland kommunpolitiker','%','Politisk representation'),
 ('municipalChairMen','N05828','Män på kommunala ordförandeposter','%','Politisk representation'),
 ('municipalForeignBorn','N05825','Utrikes födda bland kommunpolitiker','%','Politisk representation'),
 ('municipalPoliticianIncome','N05827','Kommunpolitikers mediannettoinkomst','kr/person','Politisk representation')]
series={};meta={}
for key,code,label,unit,group in SPECS:
 raw=json.loads((R/(code+'.json')).read_text());m=raw['metadata'];reg=m['municipality_type']=='L';allowed=[2018,2021,2024] if code=='U50105' else [2002,2006,2010,2014,2018,2022];rows={}
 for r in raw['rows']:
  if r['period'] not in allowed:continue
  v=next((v['value'] for v in r['values'] if v['gender']=='T' and not v.get('isdeleted') and v['value'] is not None),None)
  if v is None:continue
  region=r.get('municipality') or r.get('region');id='00' if region=='0000' else region[-2:] if reg else region
  rows.setdefault(str(r['period']),{})[id]=v
 assert rows,key
 series[key]=rows
 extra=' Återpublicerade mellanår har tagits bort: endast undersökningsår visas. Senaste föregående utgåva används därefter, inte en ny årlig observation. Uppgifter för saknade områden fylls inte ut. Källa: Kolada, RKA; ursprungskälla '+('Livsmedelsverket.' if code=='U50105' else 'SCB.')
 if code=='U50105':extra+=' Kategorikod, INTE exakt procent: 0=0–10 %, 1=11–20 %, 2=21–30 %, 3=31–40 %, 4=41–50 %, 5=51–60 %, 6=61–70 %, 7=71–80 %, 8=81–90 %, 9=91–99 %, 10=100 %. Ingen aritmetisk riks-/länsberäkning av dessa kategorier.'
 if code=='N65827':extra+=' Källan benämner måttet mediannettonettoinkomst, och beskrivningen avser regionens förtroendevalda heltidspolitiker. Detta är inte regionpolitikernas arvode eller månadslön.'
 if code=='N05827':extra+=' Inkomsten exkluderar kapitalinkomst och avser personer från 20 år. Den är inte ett politikerarvode eller månadslön.'
 meta[key]={'label':label,'group':group,'source':'Kolada / '+('Livsmedelsverket' if code=='U50105' else 'SCB'),'code':code,'unit':unit,'years':sorted(map(int,rows)),'country':any('00' in v for v in rows.values()),'county':reg,'municipality':not reg,'count':sum(map(len,rows.values())),'url':'https://api.kolada.se/v3/kpi/'+code,'retrieved':'24 oktober 2026','license':'CC BY 4.0','definition':m['description']+extra,'periodicSurvey':True}
raw=json.loads((R/'daily-smoking.json').read_text());smoke={};ci={};periods={}
for r in raw['data']:
 region,measure,stat,sex,period=r['key'];y=period[-4:]
 try:v=float(r['values'][0])
 except ValueError:continue
 periods[y]=period;ci.setdefault(y,{}).setdefault(region,{})[stat]=v
 if stat=='01':smoke.setdefault(y,{})[region]=v
series['dailySmoking']=smoke
meta['dailySmoking']={'label':'Daglig tobaksrökning · flerårsmedel','group':'Hälsa & dödsorsaker','source':'Folkhälsomyndigheten','code':'HLV1TobXReg','unit':'%','years':sorted(map(int,smoke)),'country':True,'county':True,'municipality':False,'count':sum(map(len,smoke.values())),'url':'https://fohm-app.folkhalsomyndigheten.se/Folkhalsodata/pxweb/sv/A_Folkhalsodata/A_Folkhalsodata__B_HLV__aLevvanor__aagLevvanortobak/hlv1tobxreg.px/','retrieved':'24 oktober 2026','definition':'Nationella folkhälsoenkäten. Röker tobak dagligen, båda könen. Icke åldersstandardiserat fyraårsmedelvärde, placerat vid periodens slutår. Inte ett enskilt års rökning. Befolkningen 16–84 år till och med 2020, därefter 16 år och äldre. Perioder överlappar; frågor och urval har ändrats. Gotland saknar värde för två perioder. Riket/län, inga kommunvärden. PX-export COPYRIGHT=NO; egna kartor av numeriska data med källangivelse. Urvalsosäkerhet redovisas; ingen säker trendbedömning görs.','periods':periods,'periodicSurvey':True}
assert json.loads((R/'swedac-ai-0.json').read_text())['totalCount']==0
series['aiAccreditations']={'2026':{'00':0}}
meta['aiAccreditations']={'label':'AI-området · registrerade ackrediteringar','group':'Teknik & ackreditering','source':'Swedac','code':'Artificial intelligence (AI)','unit':'registerträffar','years':[2026],'country':True,'county':False,'municipality':False,'count':1,'url':'https://api2.swedac.se/v2/accreditations?area=ff75e5a1-12bd-ef11-85fd-005056ae1051','retrieved':'24 oktober 2026','definition':'Registerögonblicksbild för AI-området, identifierat i Swedacs områdeslista som (EU) 2024/1689, Artificial Intelligence (AI). Verifierad sökning ger inga träffar, även kontroll med områdesnamnet. Tomt resultat är inte saknade API-svar. Inga organisationer eller platser kan därför ritas ut. Måttet säger inte hur mycket AI som används eller hur många AI-företag som finns. Ingen historisk serie. Källa: Swedac. Fristående sammanställning, inte en tjänst från Swedac. API-villkor: fri användning med källhänvisning, https://www.swedac.se/psidata/.','snapshot':True}
public={'series':series,'metadata':meta,'smokingIntervals':ci,'retrieved':'2026-10-24','catalogs':[p.stem for p in R.glob('*_*.json')]}
(ROOT/'dist/data/dataportal-additions.json').write_text(json.dumps(public,ensure_ascii=False,separators=(',',':')))
for file in ['dist/index.html','dist/lan/index.html','dist/focus/index.html']:
 p=ROOT/file;s=p.read_text();match=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(match[2]);d['social'].update(series);d['extraMetadata'].update(meta);d['smokingIntervals']=ci
 s=s[:match.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[match.end(2):]
 # Refresh data without duplicating the already installed interface hooks.
 if "if(D.extraMetadata[measure]?.periodicSurvey||measure==='aiAccreditations')" in s:
  p.write_text(s);continue
 s=s.replace("const groupForMetric=key=>{", "const groupForMetric=key=>{\n if(D.extraMetadata[key]?.group==='Politisk representation')return 'Politisk representation';\n if(key==='kitchenTraining')return 'Måltider & omsorg';\n if(key==='aiAccreditations')return 'Teknik & ackreditering';\n if(key==='dailySmoking')return 'Hälsa & dödsorsaker';",1)
 s=s.replace("value == null || !Number.isFinite(value)?'–':", "value == null || !Number.isFinite(value)?'–':measure==='kitchenTraining'?(['0–10 %','11–20 %','21–30 %','31–40 %','41–50 %','51–60 %','61–70 %','71–80 %','81–90 %','91–99 %','100 %'][Math.round(value)]||'–'):",1)
 anchor='    sparkline(measure,type,id,obj);'
 inject="""    if(D.extraMetadata[measure]?.periodicSurvey||measure==='aiAccreditations'){
      const m=D.extraMetadata[measure],sy=latestAvailableYear(measure,year),period=m.periods?.[sy]||sy;
      $('info-'+measure).textContent=m.source+' · '+m.code+' · '+(m.snapshot?'registeruttag 24 oktober 2026':'mätperiod '+period)+' · '+(m.municipality?'kommun':'riket/län')+(m.periodicSurvey?' · ingen ny årlig mätning':'');
      if(measure==='aiAccreditations'){$('info-'+measure).textContent='Källa: Swedac · nationellt registeruttag 24 oktober 2026 · fristående sammanställning';$('secondary-'+measure).textContent='Inga registerträffar i AI-området. Ingen lokal fördelning eller historik finns. Detta mäter inte användningen av AI.';}
      if(measure==='dailySmoking'){
        const ci=D.smokingIntervals?.[sy]?.[type==='country'?'00':id];
        $('secondary-'+measure).textContent=absolute==null?'Ingen uppgift på vald nivå och period. Kommunvärden saknas.':'Fyraårsmedel '+period+(ci?' · konfidensintervall '+fraction.format(ci['02'])+'–'+fraction.format(ci['03'])+' %':'')+' · inte ett enskilt års värde.';
      }
      if(measure==='kitchenTraining'){$('info-'+measure).textContent+=' · kategoriserad andel, inte exakt procent';$('secondary-'+measure).textContent=absolute==null?'Ingen uppgift på vald nivå/utgåva.':'Andelsintervall för utbildad måltidspersonal. Undersökning vart tredje år; mellanår är återpubliceringar.';}
    }
"""
 assert anchor in s;s=s.replace(anchor,inject+anchor,1)
 # Add electricity to the existing map and filter registry.
 s=s.replace('const GEO_LAYERS={','const GEO_LAYERS={"Electricity":"Fysiska elflöden mellan elområden",',1)
 if file=='dist/index.html':
  s=s.replace("card.innerHTML='<h2>'+esc(label)+' · geografiska objekt</h2><iframe", "card.innerHTML='<h2>'+esc(label)+(key==='Electricity'?' · flödeskarta':' · geografiska objekt')+'</h2><iframe",1)
  s=s.replace("src=\"/assets/geodata-map.html?embed=1&type='+key+'\"", "src=\"'+(key==='Electricity'?'/assets/electricity-map.html':'/assets/geodata-map.html?embed=1&type='+key)+'\"",1)
 if file=='dist/lan/index.html':
  # Keep the county page table-only; electricity is not county statistics.
  a=s.index('function renderCountyProfileTable()');b=s.index('function comparisonTable()',a);piece=s[a:b];piece=piece.replace("}).join('');", "}).join('')+'<tr><td>Fysiska elflöden</td><td data-label=\"Värde\">Elområden, inte län</td><td data-label=\"År\">2022–2026</td><td data-label=\"Enhet\"><a href=\"/#geo-Electricity\">Öppna flödeskartan</a></td></tr>';",1);s=s[:a]+piece+s[b:]
 if file=='dist/focus/index.html':
  # All money metrics compare to their own national figure, not peer medians.
  s=s.replace("const unit=UNITS[key]||'',isRate=unit.includes('%')||", "const unit=UNITS[key]||'',isRate=unit.includes('%')||unit.includes('kr/person')||key==='kitchenTraining'||key==='aiAccreditations'||",1)
  s=s.replace("if(type==='town'||['greenArea','tobaccoOutdoor'].includes(key))return '';", "if(type==='town'||['greenArea','tobaccoOutdoor','dailySmoking','aiAccreditations','kitchenTraining'].includes(key))return '';",1)
  s=s.replace("'Digital infrastruktur','Handelsområden'", "'Digital infrastruktur','Politisk representation','Måltider & omsorg','Teknik & ackreditering','Handelsområden'",1)
  s=s.replace("if(group==='Val & valdeltagande')paragraphs.push", "if(group==='Politisk representation')paragraphs.push('Uppgifterna gäller förtroendevalda politiker, inte befolkningen i stort. Mätningarna görs med flera års mellanrum; återpublicerade mellanår räknas inte som nya undersökningar. Inkomstmåtten beskriver inkomst, inte politiska arvoden eller månadslöner.');\n  if(group==='Måltider & omsorg')paragraphs.push('Utbildningen hos måltidspersonalen redovisas i breda andelsintervall. Det går därför inte att läsa ut en exakt andel eller säkert bedöma en liten förändring.');\n  if(group==='Teknik & ackreditering')paragraphs.push('AI-registret har inga träffar vid vårt uttag. Det säger inget om hur utbredd användningen av artificiell intelligens är, och innebär inte att området saknar AI-verksamhet.');\n  if(items.some(i=>i.key==='dailySmoking'))paragraphs.push('Daglig rökning redovisas som ett medelvärde över flera år. Perioder överlappar och undersökningen har ändrats, så vi beskriver ingen säker trend.');\n  if(group==='Val & valdeltagande')paragraphs.push",1)
  # A separate, explicitly labelled county context never replaces a municipality value.
  marker=" const missingText=missing.length?"
  extra=""" let additionalContext='';
 if(type==='municipality'){
   const county=String(id).slice(0,2),sy=latestAvailableYear('dailySmoking',year),value=rawValue('dailySmoking','county',county,sy),national=rawValue('dailySmoking','country','00',sy);
   if(Number.isFinite(value)){
     const word=relativeWord(value,national),comparison=word==='ungefär lika'?'ungefär lika vanlig':word+' '+(value>national?'vanligare':'mindre vanlig');
     additionalContext+='<h3>Rökning i länet</h3><p>För kommunen saknas ett eget rökningstal i denna källa. I länet som kommunen tillhör är daglig tobaksrökning '+comparison+'. Det är en länsuppgift och ett medel över flera år, ingen uppskattning för kommunen. Skillnader måste tolkas med hänsyn till undersökningens osäkerhet.</p>';
   }
 }
 if(year>=2026&&type!=='country')additionalContext+='<h3>Artificiell intelligens och ackreditering</h3><p>Det nationella registret för AI-området har inga träffar i vårt uttag. Därför finns inga organisationer att fördela geografiskt. Det säger inget om hur mycket AI som används på platsen.</p>';
 if(year>=2022)additionalContext+='<h3>Elflöden och energisystem</h3><p>Elflödeskartan visar hur el överförs mellan elområden och över landsgränser. Dessa områden följer inte läns- eller kommungränser. Flödena kan därför inte användas som ett mått på platsens egen förbrukning, produktion eller självförsörjning. Välj flödeskartan för att se riktning och detaljer.</p>';
"""
  assert marker in s;s=s.replace(marker,extra+marker,1).replace('+tobaccoContext+missingText+', '+tobaccoContext+additionalContext+missingText+',1)
  # County context in the numerical area too.
  marker=" $('focusValueList').querySelectorAll('button').forEach"
  extra=""" if(selectedType()==='municipality'){
   const county=String(selectedId()).slice(0,2),sy=latestAvailableYear('dailySmoking',year),value=rawValue('dailySmoking','county',county,sy),national=rawValue('dailySmoking','country','00',sy),ci=D.smokingIntervals?.[sy]?.[county];
   if(Number.isFinite(value))$('focusValueList').insertAdjacentHTML('beforeend','<article class="focus-value-row"><span>Daglig tobaksrökning · länskontext: '+esc(D.names[county])+'</span><strong>'+fraction.format(value)+' %</strong><small>Inget kommunvärde · period '+esc(D.extraMetadata.dailySmoking.periods[sy])+' · Riket: '+fraction.format(national)+' %'+(ci?' · konfidensintervall '+fraction.format(ci['02'])+'–'+fraction.format(ci['03'])+' %':'')+' · Källa: Folkhälsomyndigheten.</small></article>');
 }
 if(year>=2026&&selectedType()!=='country')$('focusValueList').insertAdjacentHTML('beforeend','<article class="focus-value-row"><span>AI-ackreditering · nationell registerkontext</span><strong>0 registerträffar</strong><small>Uttag 24 oktober 2026 · ingen lokal fördelning · Källa: Swedac. Fristående sammanställning.</small></article>');
 if(year>=2022)$('focusValueList').insertAdjacentHTML('beforeend','<article class="focus-value-row"><span>Fysiska elflöden</span><strong>Elområden och gränsförbindelser</strong><small>Lokalt hostade observationer 2022–2026 · MW per mättillfälle, inte kommunal förbrukning · Källa: Svenska kraftnät. Välj flödeskartan ovan.</small></article>');
"""
  assert marker in s;s=s.replace(marker,extra+marker,1)
  s=s.replace("$('focusGeoFrame').dataset.geolayer=key.slice(4);syncGeoFrames()", "const frame=$('focusGeoFrame'),kind=key.slice(4),url=kind==='Electricity'?'/assets/electricity-map.html':'/assets/geodata-map.html?embed=1&type='+kind;frame.dataset.geolayer=kind;if(frame.getAttribute('src')!==url){frame.dataset.ready='';frame.src=url;}syncGeoFrames()",1)
 p.write_text(s)
print('Added',len(series),'new regional/national metrics; preserved all 12 catalog links.')
