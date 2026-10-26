"""Lägger in observerade värden och källmetadata i den fristående kartan."""
from pathlib import Path
import json,math,re,runpy,html
ROOT=Path(__file__).resolve().parent
spec=runpy.run_path(str(ROOT/'fetch-statistics.py'))['SPEC']
p=ROOT.parent/'src/template.html';s=p.read_text()
match=re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)',s,re.S)
if not match:
 match=re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)',s,re.S)
assert match,'Data tag missing'
d=json.loads(match.group(2));metadata={};coverage=[]
for key,code,label,unit,group in spec:
 raw=json.loads((ROOT/(code+'.json')).read_text());series={};retained=0
 for row in raw['rows']:
  geo=row['municipality'];y=str(row['period'])
  if y not in [str(y) for y in range(2010,2026)]:continue
  selected=next((v for v in row['values'] if v['gender']=='T'),None)
  if selected is None and key in ['lifeMale','lifeFemale']:
   selected=next((v for v in row['values'] if v['gender']==('M' if key=='lifeMale' else 'K')),None)
  if selected is None or selected.get('isdeleted') or not isinstance(selected.get('value'),(int,float)) or not math.isfinite(selected['value']):continue
  if geo=='0000':geo='00'
  elif geo.startswith('00') and geo[2:] in d['names']:geo=geo[2:]
  elif geo not in d['municipalities']:continue
  value=selected['value'];series.setdefault(y,{})[geo]=value;retained+=1
  if unit.startswith('%'):assert 0<=value<=100,(key,geo,y,value)
 assert retained>0,(key,'no observed data')
 d['social'][key]=series
 meta=raw['metadata'];yrs=sorted(map(int,series));country=any('00' in v for v in series.values());county=any(any(k in d['names'] for k in v) for v in series.values());muni=any(any(k in d['municipalities'] for k in v) for v in series.values())
 metadata[key]={'code':code,'label':label,'unit':unit,'group':group,'definition':meta['description'],'sourceTitle':meta['title'],'url':raw['url'],'years':yrs,'country':country,'county':county,'municipality':muni,'count':retained}
 coverage.append((key,retained,yrs[0],yrs[-1]))
historical=json.loads((ROOT/'historical-maps.json').read_text())
for row in historical:
 d['social'][row['key']]=row['data']
 metadata[row['key']]={'code':row['code'],'label':row['label'],'unit':row['unit'],'group':row['group'],'definition':row['sourceTitle'],'sourceTitle':row['sourceTitle'],'url':row['url'],'years':row['years'],'country':True,'county':row['key'] not in ['turnoutRiksdag','turnoutRegion','turnoutMunicipal'],'municipality':True,'count':sum(len(v) for v in row['data'].values()),'source':'SCB'}
byKey={row['key']:row for row in historical}
births=byKey['births']['data'];deaths=byKey['deaths']['data'];natural={}
for year in sorted(set(births)&set(deaths)):
 natural[year]={geo:births[year][geo]-deaths[year][geo] for geo in set(births[year])&set(deaths[year])}
d['social']['naturalIncrease']=natural
metadata['naturalIncrease']={'code':'FoddaK − DodaHandelseK','label':'Födelseöverskott','unit':'personer','group':'Födda och döda','definition':'Beräknat som antal levande födda minus antal döda i samma region och år. Baserat på SCB:s befolkningsstatistik.','sourceTitle':'Härlett från SCB:s födda och döda','url':byKey['births']['url'],'years':sorted(map(int,natural)),'country':True,'county':True,'municipality':True,'count':sum(len(v) for v in natural.values()),'source':'SCB'}
d['electionResults']=json.loads((ROOT/'val-election.json').read_text())
for key,election in d['electionResults'].items():
 share_key='election'+key+'Share';turnout_key='election'+key+'Turnout';all_years=sorted(map(int,election['years']))
 share_count=turnout_count=0
 for election_year,data in election['years'].items():
  county_votes={};county_eligible={};county_cast={};county_party_votes={}
  for code,share in [(geo,values) for geo,values in data['shares'].items() if len(geo)==4]:
   county=d['municipalities'].get(code,{}).get('lan')
   if not county:continue
   weight=data['validVotes'].get(code,0);cast=data['voterTotals'].get(code,{})
   county_votes[county]=county_votes.get(county,0)+weight
   county_cast[county]=county_cast.get(county,0)+cast.get('votes',0)
   county_eligible[county]=county_eligible.get(county,0)+cast.get('eligible',0)
   totals=county_party_votes.setdefault(county,{})
   for party,value in share.items():totals[party]=totals.get(party,0)+value*weight
  for county,total in county_votes.items():
   if total:data['shares'][county]={party:value/total for party,value in county_party_votes[county].items()}
   if county_eligible.get(county):data['turnout'][county]=100*county_cast[county]/county_eligible[county]
  data['partyIndex']={party:i for i,party in enumerate(data['parties'])}
  data['partyShares']={geo:[round(values.get(party,0),6) for party in data['parties']] for geo,values in data['shares'].items()}
  data.pop('shares',None)
  for helper in ('validVotes','voterTotals'):data.pop(helper,None)
  share_count+=len(data['partyShares']);turnout_count+=len(data['turnout'])
  d['social'].setdefault(turnout_key,{})[election_year]=data['turnout']
 year_span=f'Val {min(all_years)}–{max(all_years)}'
 metadata[share_key]={'code':year_span,'label':election['name']+' · partiets röstandel','unit':'% av giltiga röster','group':'Valresultat','definition':'Partiets andel av giltiga röster. Välj valår och parti i kartan. Partierna varierar mellan valår och visas enligt källfilens namn.','sourceTitle':'Valmyndighetens slutliga resultat','url':election['years'][str(max(all_years))]['sourceUrl'],'years':all_years,'country':True,'county':True,'municipality':True,'count':share_count,'source':'Valmyndigheten'}
 metadata[turnout_key]={'code':year_span,'label':election['name']+' · valdeltagande','unit':'%','group':'Valresultat','definition':'Andel röstande bland röstberättigade. Valår väljs i kartan.','sourceTitle':'Valmyndighetens slutliga resultat','url':election['years'][str(max(all_years))]['sourceUrl'],'years':all_years,'country':True,'county':True,'municipality':True,'count':turnout_count,'source':'Valmyndigheten'}
 election['shareMetric']=share_key;election['turnoutMetric']=turnout_key
d['extraMetadata']=metadata
s=s[:match.start(2)]+json.dumps(d,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+s[match.end(2):]
s=s.replace("const METRICS =", "const EXTRA_METRICS=Object.keys(D.extraMetadata).filter(k=>D.extraMetadata[k].group!=='Osäkerhet');\nconst METRICS =",1).replace('...DERIVED_METRICS];','...DERIVED_METRICS,...EXTRA_METRICS];',1)
s=s.replace('const EVENTS = {', '''for(const key of EXTRA_METRICS) {
  METRIC_LABELS[key]=D.extraMetadata[key].label;UNITS[key]=D.extraMetadata[key].unit;
  COLORS[key]=COLORS.employment;
}
const EVENTS = {''',1)
s=s.replace("['unemployment','sickness','hours','employment','growth1','growth10','immigration1000'].includes(measure)","([...EXTRA_METRICS.filter(k=>!['domesticIn','domesticOut'].includes(k)),'unemployment','sickness','hours','employment','growth1','growth10','immigration1000'].includes(measure))",1)
s=s.replace('for (const key of DERIVED_METRICS) {','for (const key of [...DERIVED_METRICS,...EXTRA_METRICS]) {',1)
s=s.replace("METRIC_LABELS[key]+' · beräknad ur SCB/Brå'","METRIC_LABELS[key]+(D.extraMetadata[key]?' · '+(D.extraMetadata[key].source||'Kolada'):' · beräknad ur SCB/Brå')",1)
s=s.replace("    section.dataset.metric=key;","    section.dataset.metric=key;section.id='indicator-'+key;",1)
s=s.replace("    const nationalMunicipality = national && metric === 'sickness';", "    const nationalMunicipality = national && (metric === 'sickness' || (EXTRA_METRICS.includes(metric) && !D.extraMetadata[metric].county));",1)
# All national municipality layers share the existing cached municipality nodes.
s=s.replace("const measureNodes = measure === 'sickness' && level === 'country' ? sicknessOverviewNodes : currentNodes;", "const measureNodes = level === 'country' && (measure === 'sickness' || (EXTRA_METRICS.includes(measure) && !D.extraMetadata[measure].county)) ? sicknessOverviewNodes : currentNodes;")
s=s.replace("const measureNodes=level==='country' && measure==='sickness'?sicknessOverviewNodes:currentNodes;", "const municipalOverview=measure==='sickness'||(EXTRA_METRICS.includes(measure)&&!D.extraMetadata[measure].county);\n    const measureNodes=level==='country'&&municipalOverview?sicknessOverviewNodes:currentNodes;",1)
s=s.replace("if (level === 'country' && measure !== 'sickness') {", "if (level === 'country' && !municipalOverview) {",1)
s=s.replace("(measure !== 'population' && perCapita?", "(['immigration','crime'].includes(measure) && perCapita?",1)
s=s.replace("const stops = COLORS[measure];", "const stops = COLORS[measure] || COLORS.employment;",1)
s=s.replace("function correlationText(measure,type,id,obj=null) {",'''for(const key of EXTRA_METRICS) CORRELATION_PARTNERS[key]=['income','unemployment'];
Object.assign(CORRELATION_PARTNERS,{
 young:['school','crime100k'],workingAge:['employment','income'],older:['health','income'],oldest:['health','income'],
 education:['income','employment'],poverty:['unemployment','school'],childPoverty:['school','unemployment'],
 density:['crime100k','income'],urban:['density','crime100k'],crowding:['poverty','income'],
 rent:['poverty','income'],condo:['income','density'],owned:['density','income'],
 violent:['unsafe','poverty'],theft:['density','unsafe'],economicCrime:['density','income'],drugs:['density','unsafe'],
 unsafe:['violent','poverty'],victim:['violent','density'],domesticIn:['housing','growth1'],domesticOut:['housing','growth1'],
 residenceShort:['employment','income'],residenceLong:['employment','income'],refugeeEmployment:['education','unemployment'],
 school:['education','childPoverty'],housing:['growth1','domesticIn'],lifeMale:['income','education'],lifeFemale:['income','education'],health:['income','older']
});
function correlationValue(measure,type,id) {
 if(measure==='immigration'||measure==='crime')return rate(measure,type,id);
 if(measure==='domesticIn'||measure==='domesticOut'){
  const value=rawValue(measure,type,id),population=rawValue('population',type,id);
  return value!=null&&population>0?1000*value/population:null;
 }
 return rawValue(measure,type,id);
}
function correlationText(measure,type,id,obj=null) {''',1)
s=s.replace("const geoType=(type==='municipality')?'municipality':'county';", "const geoType=(type==='municipality'||(EXTRA_METRICS.includes(measure)&&!D.extraMetadata[measure].county)||measure==='sickness')?'municipality':'county';",1)
s=s.replace("rawValue(measure,geoType,p,year),rawValue(other,geoType,p,year)","correlationValue(measure,geoType,p),correlationValue(other,geoType,p)",1)
s=s.replace("const own=rawValue(measure,type,id,year,obj);", "const own=correlationValue(measure,type,id);",1)
s=s.replace("' Tvärsnitt, bara observerade värden. Korrelation innebär inte orsakssamband.'", "' Tvärsnitt, bara observerade värden. Flyttantal jämförs per invånare. Korrelation innebär inte orsakssamband.'",1)
s=s.replace("  for (const measure of METRICS) {\n    const absolute=valueForDisplay", "  for(const key of EXTRA_METRICS) {const m=D.extraMetadata[key];description[key]=(m.source||'Kolada')+' · '+m.code+' · '+m.years[0]+'–'+m.years.at(-1)+(m.county?' · län/kommun':' · kommunnivå');}\n  for (const measure of METRICS) {\n    const absolute=valueForDisplay",1)
s=s.replace("    sparkline(measure,type,id,obj);",'''    if(D.extraMetadata[measure]) {
      const m=D.extraMetadata[measure];
      if(absolute==null) $('secondary-'+measure).textContent='Ingen publicerad uppgift för '+year+' på vald nivå. Tillgänglig serie: '+m.years[0]+'–'+m.years.at(-1)+'.';
      const marginKey={unsafe:'unsafeMargin',victim:'victimMargin',health:'healthMargin'}[measure];
      const margin=marginKey?rawValue(marginKey,type,id):null;
      if(absolute!=null && margin!=null) $('secondary-'+measure).textContent+=' · osäkerhetstal ±'+fraction.format(margin)+' procentenheter (Kolada).';
      $('info-'+measure).textContent=description[measure]+(m.county?'':' · rikskartan visar kommuner');
    }
    sparkline(measure,type,id,obj);''',1)
# Methodology and all-source table.
s=s.replace('Valmyndighetens slutresultat visas separat för valåret 2026, med kartor för län och kommun.', 'Valmyndighetens kommunresultat från 2010, 2014, 2018, 2022 och 2026 visas i separata kartor för partiets röstandel och valdeltagande. Länsvärden för partier räknas från kommunernas röster och giltiga röster; valdeltagandet viktas med antalet röstberättigade. Valmyndighetens filer använder olika partinamn och redovisningsformat mellan år. Valårsväljaren visar därför partierna som finns i det valda årets resultatfil.',1)
s=s.replace('  <footer class="sources">', '''  <section class="methodology" aria-label="Definitioner och datatäckning"><h2>Definitioner och datatäckning för de nya måtten</h2>
  <p>Medellivslängd redovisas som flerårsmedel. Självskattad hälsa bygger på urvalsundersökningar med olika åldersintervall och flerårsperioder. NTU innehåller sammanslagna undersökningsår, och utsatthet kan avse föregående kalenderår. Årtalet följer Koladas periodmärkning. Se definitionen för varje mått. Ekobrott omfattar bedrägerier och flera andra brottstyper, och är inte en separat bedrägeriserie. Vistelsetid gäller tiden efter uppehållstillstånd; sysselsättning efter 4–6 år gäller enbart skyddsbehövande och anhöriga. Saknad statistik på RegSO-/tätortsnivå ersätts inte med kommunens värde. <a href="https://www.scb.se/hitta-statistik/sverige-i-siffror/manniskorna-i-sverige/utrikes-fodda-i-sverige/?menu=open" target="_blank" rel="noopener">SCB:s karta och tabeller över utrikes födda per kommun och län</a> visar den aktuella sammansättningen. <a href="https://sdb.socialstyrelsen.se/if_dor/val.aspx" target="_blank" rel="noopener">Socialstyrelsens dödsorsaksdatabas</a> låter dig välja dödsorsak, år och län; den omfattar uppgifter från 1997.</p>
  <div id="extraDefinitions" class="definition-grid"></div></section>
  <footer class="sources">''',1)
css=''' .definition-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:12px;margin-top:15px}.source-definition{min-width:0;padding:13px;border:1px solid var(--border);border-radius:10px}.source-definition h3{font-size:.87rem;margin:0 0 7px}.source-definition p{font-size:.76rem;margin-top:6px}.source-definition details{font-size:.75rem;margin-top:8px;overflow-wrap:anywhere}.source-definition a{color:var(--accent)}.metric-map{scroll-margin-top:85px}.metric-map[hidden]{display:none!important}.metric-jumps{display:flex;flex-wrap:wrap;gap:6px;margin:15px 0}.metric-jumps a{color:var(--accent);font-size:.75rem;border:1px solid var(--border);padding:6px 9px;border-radius:7px;text-decoration:none}.metric-heading{overflow-wrap:anywhere}.metric-customizer{margin:14px 0 18px;border:1px solid var(--border);border-radius:12px;background:#102533}.metric-customizer summary{cursor:pointer;padding:14px 16px;font-weight:700}.customizer-count{margin-left:8px;color:var(--muted);font-size:.8rem;font-weight:500}.customizer-body{padding:0 15px 15px}.customizer-body>p{margin:0 0 10px;color:var(--muted);font-size:.82rem}.customizer-actions{display:flex;gap:8px;margin:8px 0 12px}.customizer-actions button{background:#193a48;border:1px solid var(--border);color:var(--text);border-radius:7px;padding:7px 10px;cursor:pointer}.metric-filter-groups{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:9px}.metric-filter-group{min-width:0;border:1px solid var(--border);border-radius:9px;padding:9px 10px}.metric-filter-group legend{padding:0 4px;font-weight:700;font-size:.82rem}.metric-filter-group legend input,.metric-filter-item input{accent-color:#7ee0c3}.metric-filter-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));gap:5px 8px}.metric-filter-item{display:flex;align-items:flex-start;gap:7px;font-size:.77rem;color:var(--text);line-height:1.3;cursor:pointer}.metric-filter-item input{margin:1px 0 0;flex:none}.metric-jumps{border-top:1px solid var(--border);padding-top:10px}
'''
s=s.replace('</style>',css+'</style>',1)
s=s.replace("const stickySlider=$('stickyYearRange');",'''document.querySelectorAll('.metric-jumps').forEach(node=>node.remove());
const jumpNav=document.createElement('nav');jumpNav.className='metric-jumps';jumpNav.setAttribute('aria-label','Hoppa till statistikmått');
for(const key of METRICS){const section=document.querySelector('[data-metric="'+key+'"]');section.id='indicator-'+key;const link=document.createElement('a');link.href='#indicator-'+key;link.textContent=METRIC_LABELS[key];jumpNav.appendChild(link);}
const customizer=document.createElement('details');customizer.className='metric-customizer';
customizer.innerHTML='<summary>Anpassa kartorna <span class="customizer-count" id="visibleMetricCountText"></span></summary><div class="customizer-body"><p>Välj ämnen eller enskilda kartor. Urvalet sparas i den här webbläsaren.</p><div class="customizer-actions"><button type="button" id="showAllMetrics">Visa alla</button><button type="button" id="hideAllMetrics">Dölj alla</button></div><div class="metric-filter-groups" id="metricFilterGroups"></div></div>';
document.querySelector('.metric-maps').before(customizer);
const groupForMetric=key=>{
 if(['births','deaths','naturalIncrease'].includes(key))return 'Födda & döda';
 if(['householdSize','young','workingAge','older','oldest'].includes(key))return 'Ålder & hushåll';
 if(['turnoutRiksdag','turnoutRegion','turnoutMunicipal','electionRiksdagShare','electionRiksdagTurnout','electionRegionShare','electionRegionTurnout','electionKommunShare','electionKommunTurnout'].includes(key))return 'Val & valdeltagande';
 if(['population','growth1','growth10','density','urban'].includes(key))return 'Befolkning & demografi';
 if(['immigration','immigration1000','domesticIn','domesticOut','residenceShort','residenceLong','refugeeEmployment'].includes(key))return 'Utrikes födda & migration';
 if(['crime','crime100k','violent','theft','economicCrime','drugs','unsafe','victim'].includes(key))return 'Brott & trygghet';
 if(['education','school','unemployment','employment','income','wage','hours','sickness','poverty','childPoverty'].includes(key))return 'Utbildning, arbete & ekonomi';
 if(['housing','crowding','rent','condo','owned'].includes(key))return 'Bostäder & byggande';
 if(['lifeMale','lifeFemale','health'].includes(key))return 'Hälsa & dödsorsaker';
 return 'Övrigt';
};
const filterGroups=new Map();
for(const key of METRICS){const group=groupForMetric(key);if(!filterGroups.has(group))filterGroups.set(group,[]);filterGroups.get(group).push(key);}
let savedMetrics=null;try{savedMetrics=JSON.parse(localStorage.getItem('sverige-statistik-kartor-v1')||'null')}catch{}
const filters=$('metricFilterGroups');
for(const [group,keys] of filterGroups){
 const field=document.createElement('fieldset');field.className='metric-filter-group';
 const legend=document.createElement('legend');const groupToggle=document.createElement('input');groupToggle.type='checkbox';groupToggle.checked=keys.every(k=>savedMetrics?.[k]!==false);groupToggle.setAttribute('aria-label','Visa alla kartor i '+group);legend.append(groupToggle,document.createTextNode(' '+group));field.appendChild(legend);
 const list=document.createElement('div');list.className='metric-filter-list';
 for(const key of keys){const label=document.createElement('label');label.className='metric-filter-item';const box=document.createElement('input');box.type='checkbox';box.checked=savedMetrics?.[key]!==false;box.dataset.metric=key;const text=document.createElement('span');text.textContent=METRIC_LABELS[key];label.append(box,text);list.appendChild(label);}
 field.appendChild(list);filters.appendChild(field);
 groupToggle.addEventListener('change',()=>{list.querySelectorAll('input[data-metric]').forEach(box=>box.checked=groupToggle.checked);applyMetricFilters();});
}
function applyMetricFilters(){
 const state={};filters.querySelectorAll('input[data-metric]').forEach(box=>{state[box.dataset.metric]=box.checked;const card=document.querySelector('.metric-maps [data-metric="'+box.dataset.metric+'"]');if(card)card.hidden=!box.checked;const link=jumpNav.querySelector('a[href="#indicator-'+box.dataset.metric+'"]');if(link)link.hidden=!box.checked;});
 for(const field of filters.querySelectorAll('.metric-filter-group')){const boxes=[...field.querySelectorAll('input[data-metric]')],toggle=field.querySelector('legend input');toggle.checked=boxes.every(box=>box.checked);toggle.indeterminate=boxes.some(box=>box.checked)&&!toggle.checked;}
 try{localStorage.setItem('sverige-statistik-kartor-v1',JSON.stringify(state))}catch{}
 $('visibleMetricCountText').textContent=Object.values(state).filter(Boolean).length+' av '+METRICS.length+' kartor visas';
}
filters.addEventListener('change',event=>{if(event.target.matches('input[data-metric]'))applyMetricFilters();});
customizer.querySelector('#showAllMetrics').addEventListener('click',()=>{filters.querySelectorAll('input[data-metric]').forEach(box=>box.checked=true);applyMetricFilters();});
customizer.querySelector('#hideAllMetrics').addEventListener('click',()=>{filters.querySelectorAll('input[data-metric]').forEach(box=>box.checked=false);applyMetricFilters();});
applyMetricFilters();customizer.appendChild(jumpNav);
$('extraDefinitions').innerHTML=EXTRA_METRICS.map(key=>{
 const m=D.extraMetadata[key];return '<article class="source-definition"><h3>'+esc(m.label)+'</h3><p>'+esc(m.group)+' · '+m.years[0]+'–'+m.years.at(-1)+' · '+m.count+' observationer</p><p>Nivåer: '+[m.country?'riket':null,m.county?'län/region':null,m.municipality?'kommun':null].filter(Boolean).join(', ')+'. Enhet: '+esc(m.unit)+'.</p><p><a target="_blank" rel="noopener" href="'+esc(m.url)+'">Källa: '+(m.source||'Kolada')+', '+m.code+'</a> · hämtad 22 oktober 2026</p><details><summary>Fullständig definition och ursprungskälla</summary><p>'+esc(m.definition)+'</p></details></article>';
}).join('');
const stickySlider=$('stickyYearRange');''',1)
# Replace hard-coded card counts without touching raw JSON data.
count=13+len([x for x in metadata.values() if x['group']!='Osäkerhet'])
s=s.replace('13 parallella',str(count)+' parallella').replace('13 statistikmått',str(count)+' statistikmått').replace('13 kartor',str(count)+' kartor')
s=s.replace('Medianinkomst, löner','Medianinkomst, löner')
s=s.replace('Jämför '+str(count)+' kartor med folkmängd, tillväxt, invandring, brott, arbetsmarknad, sjukpenning, inkomster, löner och arbetstid.', 'Jämför '+str(count)+' synkroniserade kartor med befolkning, migration, brott, arbete, ekonomi, ålder, utbildning, boende, trygghet, skolresultat, bostadsbyggande och hälsa.')
# Valmyndighetens partival styr varje röstandelskarta; årtalet är fast 2026.
s=s.replace("  if (Object.hasOwn(D.social,measure)) {", "  const electionEntry=Object.entries(D.electionResults||{}).find(([kind,e])=>e.shareMetric===measure||e.turnoutMetric===measure);\n  if(electionEntry){const data=electionEntry[1].years[selectedElectionYear[measure]];if(electionEntry[1].shareMetric===measure){const i=data?.partyIndex?.[selectedElectionParty[measure]];return i==null?null:(data?.partyShares?.[id]?.[i]??null);}return data?.turnout?.[id]??null; }\n  if (Object.hasOwn(D.social,measure)) {",1)
s=s.replace("    section.querySelector('.metric-heading').textContent=METRIC_LABELS[key]+(D.extraMetadata[key]?' · '+(D.extraMetadata[key].source||'Kolada'):' · beräknad ur SCB/Brå');", '''    section.querySelector('.metric-heading').textContent=METRIC_LABELS[key]+(D.extraMetadata[key]?' · '+(D.extraMetadata[key].source||'Kolada'):' · beräknad ur SCB/Brå');
    const electionEntry=Object.entries(D.electionResults||{}).find(([kind,e])=>e.shareMetric===key||e.turnoutMetric===key);
    if(electionEntry){const [kind,election]=electionEntry;let fillParties=()=>{};const yearSelect=document.createElement('select');yearSelect.className='election-year';yearSelect.setAttribute('aria-label','Välj valår för '+election.name);const years=Object.keys(election.years).sort((a,b)=>Number(b)-Number(a));selectedElectionYear[key]=years[0];for(const y of years){const o=document.createElement('option');o.value=y;o.textContent='Valår '+y;yearSelect.appendChild(o);}yearSelect.value=years[0];section.querySelector('.metric-map-head').appendChild(yearSelect);yearSelect.addEventListener('change',()=>{selectedElectionYear[key]=yearSelect.value;if(election.shareMetric===key)fillParties();redraw();});if(election.shareMetric===key){const select=document.createElement('select');select.className='election-party';select.setAttribute('aria-label','Välj parti för '+election.name);section.querySelector('.metric-map-head').appendChild(select);fillParties=()=>{const previous=selectedElectionParty[key],data=election.years[selectedElectionYear[key]],national=data.partyShares['00']||[],winnerIndex=national.reduce((best,value,i)=>value>national[best]?i:best,0),winner=data.parties[winnerIndex];select.replaceChildren();for(const party of data.parties){const option=document.createElement('option');option.value=party;option.textContent=party;select.appendChild(option);}selectedElectionParty[key]=data.parties.includes(previous)?previous:(winner||data.parties[0]);select.value=selectedElectionParty[key];};fillParties();select.addEventListener('change',()=>{selectedElectionParty[key]=select.value;redraw();});}}
    ''',1)
s=s.replace("function correlationText(measure,type,id,obj=null) {", "function correlationText(measure,type,id,obj=null) {\n if(D.extraMetadata[measure]?.source==='Valmyndigheten')return 'Valmyndigheten · slutligt valresultat för valt valår.';",1)
s=s.replace("if(['turnoutRiksdag','turnoutRegion','turnoutMunicipal'].includes(key))return 'Val & valdeltagande';", "if(['turnoutRiksdag','turnoutRegion','turnoutMunicipal','electionRiksdagShare','electionRegionShare','electionKommunShare','electionRiksdagTurnout','electionRegionTurnout','electionKommunTurnout'].includes(key))return 'Val & valdeltagande';",1)
s=s.replace('.definition-grid{', '.election-year,.election-party{display:block;max-width:100%;margin-top:6px;padding:6px 8px;border:1px solid var(--border);border-radius:7px;background:#102533;color:var(--text);font:inherit;font-size:.76rem}.definition-grid{',1)
s=s.replace("'Källa: '+(m.source||'Kolada')+', '+m.code", "'Källa: '+(m.source||'Kolada')+', '+m.code",1)
s=s.replace("  2026-modelluppskattningar", "  2026-modelluppskattningar",1)
s=s.replace("function redraw() {", "function redraw() {",1)
# Keep every new card labelled with its observation year, independently of the historical slider.
s=s.replace("  const description={\n    population:", "  const description={\n    population:",1)
s=s.replace("  if (points.length < 2) {", "  if(D.extraMetadata[measure]?.source==='Valmyndigheten'){svg.innerHTML='<text x=\"170\" y=\"37\" text-anchor=\"middle\" fill=\"#9db3c0\" font-size=\"10\">Valår väljs ovan</text>';return;}\n  if (points.length < 2) {",1)
s=s.replace("    $('context-'+measure).textContent=name+(type==='town' && measure==='population'?' · 2023':fixedElectionYear?' · val '+(selectedElectionYear[measure]||'2026'):' · '+year)+(estimation?' · MODELLUPPSKATTNING':'');", "    const discreteTurnout=['turnoutRiksdag','turnoutRegion','turnoutMunicipal'].includes(measure);\n    $('context-'+measure).textContent=name+(type==='town' && measure==='population'?' · 2023':fixedElectionYear?' · val '+(selectedElectionYear[measure]||'2026'):discreteTurnout?' · valår '+latestAvailableYear(measure,year):' · '+year)+(estimation?' · MODELLUPPSKATTNING':'');",1)
s=s.replace("  $('rankingTitle').textContent='Jämför '+areaName.toLowerCase()+' · '+(subType==='towns'&&level!=='country'&&level!=='county'?'2023 / '+year:year);", "  const turnoutYear=Math.max(...['turnoutRiksdag','turnoutRegion','turnoutMunicipal'].map(m=>latestAvailableYear(m,year)));\n  $('rankingTitle').textContent='Jämför '+areaName.toLowerCase()+' · '+(subType==='towns'&&level!=='country'&&level!=='county'?'2023 / '+year:year)+' · valdeltagande: valår '+turnoutYear;",1)
s=s.replace("$('yearDescription').textContent='13 statistikmått · samma årtal · olika tillgängliga tidsserier';", "$('yearDescription').textContent='Kartornas historiska statistik följer valt år. Valresultaten har egna valårsväljare.';",1)
# Persist compact data + source audit, ready for static deployment.
(ROOT.parent/'dist/index.html').write_text(s)
(ROOT/'coverage.json').write_text(json.dumps({'metrics':count,'retrieved':'2026-10-22','series':metadata},ensure_ascii=False,indent=2))
print('Kartor:',count,'Nya observationer:',sum(x[1] for x in coverage));print(coverage)
