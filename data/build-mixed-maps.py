from pathlib import Path
import json,re,gzip,csv,io,unicodedata,collections
ROOT=Path(__file__).resolve().parent.parent;R=ROOT/'data/additions-mixed-2026-10-25';OUT=ROOT/'dist/data/deepdives';d=json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>',(ROOT/'dist/index.html').read_text(),re.S)[1]);series={};metadata={}
def add(key,label,unit,group,rows,url,definition,periods=None,**flags):
 rows={str(y):{k:v for k,v in vals.items() if v is not None and (k=='00' or k in d['names'] or k in d['municipalities'])} for y,vals in rows.items()};rows={y:vals for y,vals in rows.items() if vals};assert rows,key;codes={k for vals in rows.values() for k in vals};series[key]=rows;metadata[key]={'label':label,'unit':unit,'group':group,'source':flags.pop('source'),'code':flags.pop('code'),'url':url,'definition':definition,'years':sorted(map(int,rows)),'periods':periods or {y:y for y in rows},'country':'00' in codes,'county':any(k in d['names'] for k in codes),'municipality':any(k in d['municipalities'] for k in codes),'count':sum(map(len,rows.values())),'retrieved':'25 oktober 2026','mixedAddition':True,**flags}
for code,key,label,group,unit in [('U23466','elderOutdoor','Trivsamt utomhus vid särskilt boende','Äldreomsorg & utemiljö','%'),('N07925','housingPermits','Bostäder med beviljat bygglov under två år','Bostäder & byggande','bostäder/1000 inv.')]:
 data=json.loads((R/(code+'.json')).read_text());rows={}
 for r in data['rows']:
  geo=r.get('municipality') or r.get('region');geo='00' if geo=='0000' else geo[-2:] if geo and geo.startswith('00') else geo
  for v in r['values']:
   if not v.get('is_deleted') and v['gender']=='T' and v.get('value') is not None:rows.setdefault(str(r['period']),{})[geo]=v['value']
 add(key,label,unit,group,rows,'https://api.kolada.se/v3/kpi/'+code,data['metadata']['description']+(' Beviljat bygglov är inte färdigställda bostäder. Rullande tvåårsperioder överlappar.' if code=='N07925' else ' Undersökningsbortfall påverkar jämförelser; ingen åsikt ingår inte i nämnaren.'),source='Kolada / '+('SCB' if code=='N07925' else 'Socialstyrelsen'),code=code,license='CC BY 4.0',rateComparison=True,noTrend=True)
rs=list(csv.DictReader(io.StringIO(gzip.decompress((R/'iaf-recipients.raw.gz').read_bytes()).decode('utf-8-sig'))));rows={}
for r in rs:
 try:v=float(r['persons'])
 except ValueError:continue
 rows.setdefault(r['year'],{})[r['municipality_id']]=v
add('unemploymentBenefit','Mottagare av arbetslöshetsersättning','personer','Arbetslöshetsförsäkring',rows,'https://catalog.iaf.se/store/1/resource/217','Antal personer som fått arbetslöshetsersättning under året enligt IAF:s kommunfördelning. Det är inte arbetslöshetstal och omfattar inte alla arbetslösa. Riks- och länsvärden konstrueras inte genom summering. Regelförändringar och försäkringens villkor påverkar.',source='IAF',code='persons-municipality-year',license='CC0')
for kind in ['rot','tax']:
 c=json.loads(gzip.decompress((OUT/('SKV-'+kind+'-geografi.json.gz')).read_bytes()));dims={x['id']:x for x in c['dimensions']};ix={k:{v[0]:i for i,v in enumerate(x['values'])} for k,x in dims.items()}
 def value(sel):
  i=0
  for x in c['dimensions']:
   if sel[x['id']] not in ix[x['id']]:raise RuntimeError((key,x['id'],sel,list(ix[x['id']])[:4]))
   i=i*len(x['values'])+ix[x['id']][sel[x['id']]]
  return c['values'][i] if isinstance(c['values'],list) else c['values'].get(str(i))
 specs=[('rotBuyers','Preliminärt rotavdrag','antal','Köpare av rotarbete','köpare'),('rutBuyers','Preliminärt rutavdrag','antal','Köpare av rutarbete','köpare'),('rotPerBuyer','Preliminärt rotavdrag','ratio','Preliminärt rotavdrag per köpare','kr/köpare'),('rutPerBuyer','Preliminärt rutavdrag','ratio','Preliminärt rutavdrag per köpare','kr/köpare')] if kind=='rot' else [('laborTaxMedian','Direkta skatter på arbete','median','Fastställd skatt på arbete · median','kr/skattebetalare'),('capitalTaxMedian','Skatt på kapital','median','Fastställd skatt på kapital · median','kr/skattebetalare')]
 for key,term,measure,label,unit in specs:
  rows={};sel={k:x['values'][0][0] for k,x in dims.items()}
  if kind=='rot':sel|={'Roll':'Köpare','Periodtyp':'Betalningsperiod','Statistikterm':term}
  else:sel['Skatteslag']=next(v[0] for v in dims['Skatteslag']['values'] if v[0]=='Typ av skatt / '+term)
  for y,_ in dims['Tid']['values']:
   if not re.fullmatch(r'\d{4}',y):continue
   sel['Tid']=y
   for geo,_ in dims['Region']['values']:
    if geo!='00' and geo not in d['names'] and geo not in d['municipalities']:continue
    sel['Region']=geo
    variants=dims.get('Källradvariant',{}).get('values',[['1','1']]);values=[]
    for variant,_ in variants:
     if 'Källradvariant' in dims:sel['Källradvariant']=variant
     if measure=='ratio':
      sel['Matt']='antal';n=value(sel);sel['Matt']='belopp';b=value(sel);v=b/n if b is not None and n is not None and n>0 else None
     else:sel['Matt']=measure;v=value(sel)
     if v is not None:values.append(v)
    # Do not arbitrarily select a conflicting source row.
    if len(set(values))==1:rows.setdefault(y,{})[geo]=values[0]
  definition=' '.join(c['notes'])
  if kind=='rot':definition+=' Kartan avser köpare, betalningsperiod och redovisade årsantal. Belopp per köpare är belopp dividerat med köparantal, inte per invånare. Uttaget för 2026 är hittills redovisat.'
  else:definition+=' Kartan avser källans median för fastställd skatt inom angivet skatteslag. Det är inte medianinkomst, skattesats, kommunalskatt eller samtliga invånares betalningar. Bedömnings- och registertäckning varierar med inkomstår; sena inkomstår är ofullständiga. Motstridiga rader med identisk synlig indelning utesluts från kartvärdet.'
  add(key,label,unit,'Skatter & avdrag',rows,c['url'],definition,source='Skatteverket',code=c['id'],license=c['license'],rateComparison=unit.startswith('kr/'),noTrend=kind=='tax',partialYears=[2026])
(ROOT/'dist/data/mixed-additions.json').write_text(json.dumps({'series':series,'metadata':metadata},ensure_ascii=False,separators=(',',':')))
for name in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/name;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);D=json.loads(m[2]);D['social'].update(series);D['extraMetadata'].update(metadata);s=s[:m.start(2)]+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if 'MIXED_ADDITIONS_V1' not in s:
  s=s.replace('const groupForMetric=key=>{',"const groupForMetric=key=>{ // MIXED_ADDITIONS_V1\n if(D.extraMetadata[key]?.mixedAddition)return D.extraMetadata[key].group;",1)
  s=s.replace('    sparkline(measure,type,id,obj);',"    if(D.extraMetadata[measure]?.mixedAddition){const m=D.extraMetadata[measure],sy=latestAvailableYear(measure,year);$('info-'+measure).textContent=m.source+' · '+m.code+' · period '+(m.periods?.[sy]||'saknas')+' · '+[m.country?'riket':null,m.county?'län':null,m.municipality?'kommun':null].filter(Boolean).join('/');$('secondary-'+measure).textContent=m.definition;}\n    sparkline(measure,type,id,obj);",1)
  if name=='dist/focus/index.html':
   s=s.replace("function focusQualTrend(key,type,id,obj){", "function focusQualTrend(key,type,id,obj){\n if(D.extraMetadata[key]?.partialYears?.includes(latestAvailableYear(key,year)))return '';",1)
   s=s.replace("'Tandvård','Föräldraförsäkring'", "'Tandvård','Föräldraförsäkring','Äldreomsorg & utemiljö','Arbetslöshetsförsäkring','Skatter & avdrag'",1)
   marker="  if(group==='Socialförsäkring & sjukfall')"
   block="""  if(group==='Äldreomsorg & utemiljö')paragraphs.push('Utemiljön vid särskilt boende bedöms av de boende som svarat på undersökningen. Det är en upplevelse av trivsel, inte ett mått på grönyta, träd eller alla äldres boendemiljö. Bortfall påverkar hur säkert svaren kan jämföras.');
  if(group==='Arbetslöshetsförsäkring')paragraphs.push('Arbetslöshetsersättningen omfattar dem som fått ersättning enligt försäkringens regler. Den ska inte förväxlas med antalet arbetslösa. I den nationella fördjupningen finns även handläggningstider för varning och avstängning samt väntetider för nya ersättningstagare. Dessa tider är inte lokala kommunvärden.');
  if(group==='Skatter & avdrag')paragraphs.push('Rot och rut redovisas här för köpare och betalningsperiod. Avdrag per köpare är inte avdrag per invånare eller ett direkt mått på hushållens välstånd. Skatteverkets medianer avser fastställd skatt inom respektive skatteslag, inte inkomster eller kommunens budget. Sena inkomstår och det pågående året kan vara ofullständiga.');
  if(items.some(i=>i.key==='housingPermits'))paragraphs.push('Bygglovsmåttet omfattar bostäder som fått lov under en överlappande tvåårsperiod. Det visar tillstånd, inte hur många bostäder som faktiskt byggts färdigt.');
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
   marker=" const missingText=missing.length?"
   block=""" if(deepAvailable.some(c=>c.id.startsWith('SKV-rent-')))additionalContext+='<h3>Vägledande hyror för fastighetstaxering</h3><p>För bostäder, lokaler och butiker finns Skatteverkets taxeringshyror i separata utgåvor. De gäller värdeområden och byggnadernas åldersklasser, inte hela kommuner eller faktisk nytecknad hyra. Byggnadens värdeår är ingen historisk mätning av hyran. Samtliga hämtade utgåvor finns i fördjupningen.</p>';
 if(deepAvailable.some(c=>c.id.startsWith('SKV-')))additionalContext+='<p>Skattetabellerna innehåller även nationella uppdelningar efter bland annat kön, ålder, inkomstnivå, bransch och företagsstorlek. Årsantal, månadsantal, köpare, utförare och olika detaljnivåer hålls isär. Grupperna kan överlappa och får inte läggas ihop som om de vore olika invånare.</p>';
 if(deepAvailable.some(c=>c.id==='FK-ARBSKYflDecember'))additionalContext+='<p>Yrkesskadelivränta har en egen nationell historik efter kön, ålder och livräntetyp. Den skiljs från arbetsskadelivränta och används inte som en uppskattning av antalet arbetsskador i kommunen. Detaljerna visar den faktiskt redovisade månaden.</p>';
 if((D.deepDiveCatalog||[]).some(c=>c.id==='SLV-Riksmaten'))additionalContext+='<h3>Matvanor</h3><p>Riksmatens matvaneundersökningar är en identifierad källa, men observationsvärden kunde inte verifieras i detta uttag. Därför beskriver vi inte kommunens kostvanor eller en utveckling från dessa undersökningar.</p>';
"""
   assert marker in s;s=s.replace(marker,block+marker,1)
 tmp=p.with_suffix('.next.html');tmp.write_text(s);tmp.replace(p)
print('Added',len(series),'mixed map measures')
