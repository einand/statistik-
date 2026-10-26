from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parent.parent
catalog=json.loads((ROOT/'dist/data/deepdives/catalog.json').read_text())
for name in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/name;s=p.read_text();m=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S);d=json.loads(m[2]);d['deepDiveCatalog']=[{k:c.get(k) for k in ['id','label','source','years','periods','region','status']} for c in catalog];s=s[:m.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(2):]
 if 'DEEP_DIVES_V1' in s:
  temp=p.with_suffix('.next.html');temp.write_text(s);temp.replace(p);continue
 s=s.replace('function syncGeoFrames(){','function syncGeoFrames(){syncStatisticsFrames();',1)
 code="""
// DEEP_DIVES_V1: local full-source tables, kept separate from geographic estimates.
function syncStatisticsFrames(){document.querySelectorAll('iframe[data-statistics]').forEach(frame=>{if(!frame.dataset.ready)return;frame.contentWindow.postMessage({kind:'statistics-context',year,place:{type:typeof selectedType==='function'?selectedType():'country',id:typeof selectedId==='function'?selectedId():'00',name:typeof selectedName==='function'?selectedName():'Sverige'}},location.origin)})}
window.addEventListener('message',event=>{if(event.origin!==location.origin||event.data?.kind!=='statistics-ready')return;const frame=[...document.querySelectorAll('iframe[data-statistics]')].find(f=>f.contentWindow===event.source);if(frame){frame.dataset.ready='yes';syncStatisticsFrames()}});
"""
 if name!='dist/lan/index.html':
  code+="""const deepCard=document.createElement('section');deepCard.id='statisticalDetails';deepCard.className='geospatial-card';deepCard.style.gridColumn='1 / -1';deepCard.innerHTML='<h2>Fördjupning: skola, livsvillkor och kommunal ekonomi</h2><p style="padding:0 15px">Alla hämtade uppdelningar och mätperioder. Nationella grupper hålls isär från lokala värden.</p><iframe title="Fördjupning med fullständiga lokalt hostade statistikunderlag" loading="lazy" data-statistics="yes" src="/assets/statistics-explorer.html" style="height:760px"></iframe>';
"""
  if name=='dist/index.html':
   code+="""document.querySelector('.metric-maps').appendChild(deepCard);const deepLine=document.createElement('label');deepLine.className='metric-filter-item';const deepToggle=document.createElement('input');deepToggle.type='checkbox';try{deepToggle.checked=localStorage.getItem('statistics-deepdives-visible')!=='false'}catch{deepToggle.checked=true}deepCard.hidden=!deepToggle.checked;deepToggle.onchange=()=>{deepCard.hidden=!deepToggle.checked;try{localStorage.setItem('statistics-deepdives-visible',String(deepToggle.checked))}catch{}};deepLine.append(deepToggle,document.createTextNode('Fördjupningstabeller · skola och livsvillkor'));geoFilters.appendChild(deepLine);
"""
  else:code+="focusPanel.appendChild(deepCard);\n"
 if name=='dist/lan/index.html':
  marker="  }).join('')+'<tr><td>Fysiska elflöden"
  s=s.replace(marker,"  }).join('')+'<tr><td>Fördjupade källtabeller</td><td data-label=\"Värde\">Olika geografiska nivåer</td><td data-label=\"År\">Alla hämtade årgångar</td><td data-label=\"Enhet\"><a href=\"/#statisticalDetails\">Öppna fullständiga tabeller</a></td></tr><tr><td>Fysiska elflöden",1)
 if name=='dist/focus/index.html':
  marker=" const missingText=missing.length?"
  block=""" const deepAvailable=(D.deepDiveCatalog||[]).filter(c=>c.status==='available'&&(c.years||[]).some(y=>y<=year));
 const hasDeep=prefix=>deepAvailable.some(c=>c.id.startsWith(prefix));
 const schoolTopics=[];if(hasDeep('socr'))schoolTopics.push('relationer till lärare');if(hasDeep('funk'))schoolTopics.push('funktionsnedsättning som påverkar skolan');if(hasDeep('skos'))schoolTopics.push('stress av skolarbetet');if(hasDeep('mob'))schoolTopics.push('mobbning');if(hasDeep('InskForsk'))schoolTopics.push('förskoleinskrivning');
 if(schoolTopics.length)additionalContext+='<h3>Fördjupning om uppväxt och skola</h3><p>För '+esc(joinWords(schoolTopics))+' finns fler uppdelningar i de nationella underlagen. Där går det att välja bland de redovisade grupperna efter exempelvis ålder, kön, ekonomisk situation, föräldrarnas utbildning, födelseland och socioekonomisk områdestyp. Uppdelningarna varierar mellan måtten. De nationella grupperna får inte användas som uppskattningar för den valda kommunen eller enskilda invånare. Fullständiga värden och mätperioder finns i fördjupningen nedanför.</p>';
 if(hasDeep('MHEv1Tra'))additionalContext+='<h3>Transporter och livsvillkor</h3><p>Transportvanor kan också studeras efter områdestyp, ålder, utbildning, födelseland och funktionsnedsättning. Detta är gruppresultat från en enkät, inte en lokal trafikmätning eller ett bevis på varför människor väljer ett visst färdsätt.</p>';
 if(hasDeep('TAB6859')||hasDeep('TAB6861'))additionalContext+='<h3>Arbetslivets sammansättning</h3><p>De nationella sysselsättningstabellerna visar hur utbildningsnivå och ålder fördelas mellan näringsgrenar och sektorer. De beskriver arbetslivets sammansättning, inte kommunens arbetslöshet. Sekretesskydd kan göra att delarna inte summerar exakt till redovisade totaler.</p>';
 if(hasDeep('TAB6798'))additionalContext+='<h3>Gymnasiebehörighet och bakgrund</h3><p>Det finns nationella uppdelningar av gymnasiebehörigheten efter tid i Sverige, svensk och utländsk bakgrund samt andra bakgrundsvariabler. De redovisade grupperna kan överlappa. Uppgifterna beskriver grupper och ska inte tolkas som att bakgrunden ensam förklarar elevernas resultat.</p>';
 if((D.deepDiveCatalog||[]).some(c=>c.status==='unavailable'))additionalContext+='<p>Den beställda uppdelningen av mobbning efter socioekonomisk områdestyp saknar ännu åtkomliga källvärden. Den ersätts inte med siffror från andra grupper.</p>';
"""
  assert marker in s;s=s.replace(marker,block+marker,1)
 last=s.rfind('</script>');s=s[:last]+code+s[last:];temp=p.with_suffix('.next.html');temp.write_text(s);temp.replace(p)
print('Installed local full-table explorer on root/focus; linked from table-only county page.')
