from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
for name in ['dist/index.html','dist/focus/index.html','dist/lan/index.html']:
 p=ROOT/name;s=p.read_text()
 if 'href="/score/"' not in s[:s.index('<script')]:
  s=re.sub(r'(<nav class="site-menu"[^>]*>)(.*?)(</nav>)',lambda m:m[1]+m[2]+'<a href="/score/">Boendepoäng</a>'+m[3],s,count=1,flags=re.S)
 if name=='dist/focus/index.html' and 'SCORE_FOCUS_V1' not in s:
  s=s.replace('<section id="focusStory"', '<section id="focusScore" class="focus-story" aria-label="Kommunens boendepoäng"></section><section id="focusStory"',1)
  s=s.replace('function renderFocusValues(){', 'function renderFocusValues(){\n renderFocusScore();',1)
  code="""
// SCORE_FOCUS_V1: default model only; custom weights stay on /score.
var scoreSnapshot;
function renderFocusScore(){
 const target=$('focusScore');if(!target)return;
 if(selectedType()!=='municipality'){target.innerHTML='<h3>Boendepoäng</h3><p>Poängen räknas för kommuner. Välj en kommun för att se dess resultat. Du kan jämföra alla kommuner på <a href="/score/">sidan med boendepoäng</a>.</p>';return;}
 if(!scoreSnapshot){target.innerHTML='<h3>Boendepoäng</h3><p>Poängunderlaget laddas. <a href="/score/">Öppna jämförelsen</a>.</p>';return;}
 const data=scoreSnapshot.years[String(year)],row=data?.rows[selectedId()];
 if(!row||row.score==null){target.innerHTML='<h3>Boendepoäng</h3><p>Uppgifterna räcker inte för en rättvis poäng för kommunen och tiden du har valt. Du kan läsa de uppgifter som finns nedanför.</p><p><a href="/score/">Se hur poängen räknas</a></p>';return;}
 const number=new Intl.NumberFormat('sv-SE',{maximumFractionDigits:1});
 target.innerHTML='<h3>Boendepoäng</h3><p>'+esc(row.comment)+'</p><p>Poängen ger en samlad jämförelse med andra kommuner. Här används standardvikterna. På poängsidan kan du välja vad som är viktigt för dig.</p><div class="focus-value-row"><span>Boendepoäng · standardvikter</span><strong>'+number.format(row.score)+' / 100</strong><small>Placering '+row.rank+' av '+data.ranked+' kommuner med tillräckligt underlag · valt år '+year+' · underlag '+Math.round(row.coverage*100)+' % · metod '+esc(scoreSnapshot.methodVersion)+' · datautgåva '+esc(scoreSnapshot.revision)+'</small><a href="/score/?year='+year+'&q='+encodeURIComponent(selectedName())+'">Se jämförelsen, mätår och källor</a></div>';
}
fetch('/data/score-default.json').then(r=>{if(!r.ok)throw Error('score');return r.json()}).then(d=>{scoreSnapshot=d;renderFocusScore()}).catch(()=>{const target=$('focusScore');if(target)target.innerHTML='<h3>Boendepoäng</h3><p>Poängen kunde inte läsas. <a href="/score/">Öppna poängsidan</a>.</p>';});
const scoreLocation=new URLSearchParams(location.search),scoreMunicipality=scoreLocation.get('municipality'),scoreYear=Number(scoreLocation.get('year'));
if(scoreMunicipality&&D.municipalities[scoreMunicipality]){if(YEARS.includes(scoreYear))setYear(scoreYear);navigate('municipality',scoreMunicipality);$('placeSearch').value=D.municipalities[scoreMunicipality].name;}
"""
  i=s.rfind('</script>');s=s[:i]+code+s[i:]
 tmp=p.with_suffix('.next.html');tmp.write_text(s);tmp.replace(p)
# This is the existing mandatory public packaging entrypoint.
p=ROOT/'data/prepare-public.py';s=p.read_text()
if 'build-score.mjs' not in s:
 s=s.replace('import json,shutil,re','import json,shutil,re,subprocess')
 needle="if target.exists():shutil.rmtree(target)";assert needle in s;s=s.replace(needle,"subprocess.run(['node',str(ROOT/'data/build-score.mjs')],cwd=ROOT,check=True)\n"+needle,1);p.write_text(s)
print('Installed score navigation, municipal focus summary/deep links and automatic publishing rebuild.')
