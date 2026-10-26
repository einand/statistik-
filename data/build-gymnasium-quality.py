"""Inför U17401 utan att konstruera läns-/riksvärden eller historik."""
from pathlib import Path
import json,re
root=Path(__file__).resolve().parent.parent
raw=json.loads((root/'data/U17401.json').read_text());series={}
for row in raw['rows']:
 v=next((v['value'] for v in row['values'] if v['gender']=='T' and v.get('value') is not None and not v.get('isdeleted')),None)
 if v is not None:series.setdefault(str(row['period']),{})[row['municipality']]=v
assert set(series)=={'2025'} and len(series['2025'])==168 and '0000' not in series['2025']
meta={'label':'Kvalitetsindex kommunal gymnasieskola','group':'Utbildning, arbete & ekonomi','source':'Kolada / RKA','code':'U17401','unit':'indexpoäng (0–100)','years':[2025],'country':False,'county':False,'municipality':True,'count':168,'url':'https://api.kolada.se/v3/kpi/U17401','retrieved':'25 oktober 2026','license':'CC BY 4.0','definition':raw['metadata']['description']+' Relativt index, inte andel elever och inte mått på all gymnasieutbildning för kommunens invånare. Yttervärden klipps; hundra betyder inte perfekt kvalitet. Enbart 2025 har publicerade värden i det hämtade underlaget. Riks- och länstal saknas och beräknas inte. Fokusvyn jämför med ovägt genomsnitt bland kommuner med tillgänglig uppgift; detta är en egen jämförelse, inte ett officiellt riksindex. Ingen trend bedöms. Lokalt hostad data.'}
(root/'dist/data/gymnasium-quality.json').write_text(json.dumps({'series':series,'metadata':meta},ensure_ascii=False,separators=(',',':')))
for name in ['dist/index.html','dist/lan/index.html','dist/focus/index.html']:
 p=root/name;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['social']['gymnasiumQuality']=series;d['extraMetadata']['gymnasiumQuality']=meta;s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if "if(key==='gymnasiumQuality')" not in s:
  s=s.replace("const groupForMetric=key=>{", "const groupForMetric=key=>{\n if(key==='gymnasiumQuality')return 'Utbildning, arbete & ekonomi';",1)
  marker='    sparkline(measure,type,id,obj);'
  block="""    if(measure==='gymnasiumQuality'){
      $('info-'+measure).textContent='Kolada / RKA · U17401 · kommunal gymnasieskola · mätår '+latestAvailableYear(measure,year)+' · indexpoäng, inte procent';
      $('secondary-'+measure).textContent=absolute==null?'Ingen uppgift på vald nivå/period. Endast kommunvärden för 2025 finns; riks- och länsindex saknas.':'Relativt index. Ingen säker trend bedöms. Riks- och länsindex saknas; extrema värden är begränsade till skalans ändpunkter.';
    }
"""
  assert marker in s;s=s.replace(marker,block+marker,1)
  if name=='dist/focus/index.html':
   s=s.replace("'aiAccreditations','kitchenTraining'].includes(key)", "'aiAccreditations','kitchenTraining','gymnasiumQuality'].includes(key)",1)
   s=s.replace("const naturalLabels={", "const naturalLabels={gymnasiumQuality:'kvalitetsindexet för kommunal gymnasieskola',",1)
   marker="  const label=plainLabel(METRIC_LABELS[key]"
   assert marker in s;s=s.replace(marker,"  if(key==='gymnasiumQuality')reference='genomsnittet bland kommuner med uppgift';\n"+marker,1)
   marker="  if(group==='Ekonomi, arbete och utbildning')paragraphs.push"
   assert marker in s;s=s.replace(marker,"  if(items.some(i=>i.key==='gymnasiumQuality'))paragraphs.push('Gymnasieindexet väger samman examen inom ordinarie studietid och elevernas enkätsvar i kommunala gymnasieskolor. Ett högt värde beskriver ett starkare relativt resultat, inte en felfri skola eller att alla elever tar examen. Det omfattar inte alla skolor eller alla ungdomar som bor i kommunen. Vi bedömer ingen trend utifrån detta index.');\n"+marker,1)
 p.write_text(s)
print('Installed U17401: 168 municipalities, 2025; no invented national/county values or history.')
