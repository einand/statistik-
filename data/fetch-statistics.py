"""Hämtar källvärden från Kolada v3 utan att aggregera kommunandelar till län."""
import concurrent.futures,json,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
META=json.loads((ROOT/'kolada-metadata.json').read_text())
SPEC=[
('young','N01994','Invånare 0–19 år','%','Ålder'),('workingAge','N01961','Invånare 20–64 år','%','Ålder'),('older','N01812','Invånare 65–79 år','%','Ålder'),('oldest','N01813','Invånare 80+ år','%','Ålder'),
('education','N01982','Eftergymnasial utbildning, 25–64 år','%','Utbildning'),
('poverty','N66080','Låg ekonomisk standard','%','Ekonomi'),('childPoverty','N66077','Låg ekonomisk standard, 0–19 år','%','Ekonomi'),
('density','N02937','Befolkningstäthet','invånare/km²','Bebyggelse'),('urban','N00954','Tätortsgrad','%','Bebyggelse'),
('crowding','N07907','Trångboddhet, norm 2, flerbostadshus','%','Boende'),('rent','N07956','Hyresrätter i bostadsbeståndet','%','Boende'),('condo','N07957','Bostadsrätter i bostadsbeståndet','%','Boende'),('owned','N07958','Äganderätter i bostadsbeståndet','%','Boende'),
('violent','N07403','Anmälda våldsbrott','per 100 000 inv.','Brottstyper'),('theft','U07417','Anmälda stöld- och tillgreppsbrott','per 100 000 inv.','Brottstyper'),('economicCrime','N07538','Anmälda ekobrott, inkl. bedrägerier','per 100 000 inv.','Brottstyper'),('drugs','N07544','Anmälda narkotikabrott','per 100 000 inv.','Brottstyper'),
('unsafe','N07609','Otrygghet vid sen utomhusvistelse','%','Trygghet'),('victim','N07633','Utsatthet för brott mot enskild person','%','Trygghet'),
('domesticIn','N01965','Inrikes inflyttade','flyttningar','Flyttar inom Sverige'),('domesticOut','N01966','Inrikes utflyttade','flyttningar','Flyttar inom Sverige'),
('residenceShort','U01805','Utrikes födda, 0–5 år efter uppehållstillstånd','% av alla 18–64 år','Tid i Sverige'),('residenceLong','U01806','Utrikes födda, 6–10 år efter uppehållstillstånd','% av alla 18–64 år','Tid i Sverige'),('refugeeEmployment','N02994','Förvärvsarbetande flyktingar, vistelsetid 4–6 år','%','Tid i Sverige'),
('school','N15428','Gymnasiebehörighet åk 9, hemkommun','%','Skolresultat'),
('housing','N07917','Färdigställda bostäder, nybyggnad','per 1 000 inv.','Bostadsbyggande'),
('lifeMale','N00923','Medellivslängd män','år','Hälsa'),('lifeFemale','N00925','Medellivslängd kvinnor','år','Hälsa'),('health','U01405','Bra självskattad hälsa','%','Hälsa'),
('unsafeMargin','N07657','Osäkerhetstal, otrygghet','procentenheter','Osäkerhet'),('victimMargin','N07681','Osäkerhetstal, brottsutsatthet','procentenheter','Osäkerhet'),('healthMargin','U01511','Osäkerhetstal, självskattad hälsa','procentenheter','Osäkerhet')]
REGIONS=json.loads((ROOT/'kolada-regions.json').read_text())['values']
IDS=','.join(r['id'] for r in REGIONS if r['type'] in ['K','L'])
YEARS=','.join(map(str,range(2010,2026)))
def fetch(spec):
 key,code,label,unit,group=spec
 path=ROOT/(code+'.json')
 if path.exists():return key,json.loads(path.read_text())
 rows=[]
 for region_type in ['municipality','region']:
  url=f'https://api.kolada.se/v3/data/kpi/{code}/year/{YEARS}?region_type={region_type}&per_page=5000'
  while url:
   for attempt in range(3):
    try:
     d=json.load(urllib.request.urlopen(url,timeout=35));break
    except Exception:
     if attempt==2:raise
     time.sleep(1)
   rows.extend(d['values']);url=d.get('next_url')
 meta=next(x for x in META if x['id']==code)
 out={'code':code,'label':label,'unit':unit,'group':group,'metadata':meta,'retrieved':'2026-10-22','url':f'https://api.kolada.se/v3/kpi/{code}','rows':rows}
 path.write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
 print(key,len(rows),flush=True);return key,out
if __name__=='__main__':
 errors=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  jobs={pool.submit(fetch,s):s for s in SPEC}
  for f in concurrent.futures.as_completed(jobs):
   try:f.result()
   except Exception as e:errors.append(jobs[f][0]);print('ERROR',jobs[f][0],str(e),flush=True)
 print('Failed:',errors,flush=True)
 (ROOT/'metric-spec.json').write_text(json.dumps(SPEC,ensure_ascii=False))
