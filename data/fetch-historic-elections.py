"""Add 2010, 2014, and 2018 municipal election results from Valmyndigheten."""
from pathlib import Path
from urllib.request import Request, urlopen
import csv, io, json, unicodedata, openpyxl

ROOT=Path(__file__).resolve().parent
FILES={
 2010:{
  "Riksdag":"https://historik.val.se/val/val2010/statistik/slutligt_valresultat_kommuner_R.skv",
  "Region":"https://historik.val.se/val/val2010/statistik/slutligt_valresultat_kommuner_L.skv",
  "Kommun":"https://historik.val.se/val/val2010/statistik/slutligt_valresultat_kommuner_K_procent.skv"},
 2014:{
  "Riksdag":"https://historik.val.se/val/val2014/statistik/2014_riksdagsval_per_kommun.skv",
  "Region":"https://historik.val.se/val/val2014/statistik/2014_landstingsval_per_kommun.skv",
  "Kommun":"https://historik.val.se/val/val2014/statistik/2014_kommunval_per_kommun.skv"},
 2018:{
  "Riksdag":"https://historik.val.se/val/val2018/statistik/2018_R_per_kommun.xlsx",
  "Region":"https://historik.val.se/val/val2018/statistik/2018_L_per_kommun.xlsx",
  "Kommun":"https://historik.val.se/val/val2018/statistik/2018_K_per_kommun.xlsx"}}
NAMES={"M":"Moderaterna","C":"Centerpartiet","L":"Liberalerna","FP":"Liberalerna (tidigare Folkpartiet)","KD":"Kristdemokraterna","S":"Arbetarepartiet-Socialdemokraterna","V":"Vänsterpartiet","MP":"Miljöpartiet de gröna","SD":"Sverigedemokraterna","FI":"Feministiskt initiativ","PP":"Piratpartiet","AfS":"Alternativ för Sverige","OVR":"Övriga anmälda partier"}

def norm(value):
    text=unicodedata.normalize("NFD",str(value or ""))
    return "".join(c for c in text if unicodedata.category(c)!="Mn").strip().upper()

def number(value):
    if value is None or str(value).strip()=="": return 0.0
    return float(str(value).strip().replace(" ","").replace(",","."))

def make_data(url,parties,counts,valid,voters,turnout):
    shares={}
    for geo,values in counts.items():
        denom=valid.get(geo,0)
        if denom: shares[geo]={p:v/denom for p,v in values.items()}
    denom=sum(valid.values())
    shares["00"]={p:sum(v.get(p,0) for v in counts.values())/denom for p in parties} if denom else {}
    votes=sum(v["votes"] for v in voters.values());eligible=sum(v["eligible"] for v in voters.values())
    turnout["00"]=100*votes/eligible if eligible else None
    return {"parties":sorted(parties),"shares":shares,"turnout":turnout,"validVotes":valid,"voterTotals":voters,"sourceUrl":url,"municipalityCount":len(counts)}

def parse_skv(url,body):
    reader=csv.reader(io.StringIO(body.decode("cp1252").lstrip("\ufeff")),delimiter=";")
    header=next(reader); county_i=next(i for i,x in enumerate(header) if norm(x) in ("LAN","LANSKOD")); muni_i=next(i for i,x in enumerate(header) if norm(x) in ("KOM","KOMMUNKOD"))
    valid_i=next(i for i,x in enumerate(header) if norm(x) in ("ROST GILTIGA","ROSTER GILTIGA","GILTIGA ROSTER"))
    turnout_i=next(i for i,x in enumerate(header) if norm(x) in ("VDT","VALDELTAGANDE"))
    votes_i=next((i for i,x in enumerate(header) if norm(x)=="ROSTANDE"),None); eligible_i=next((i for i,x in enumerate(header) if norm(x) in ("ROSTB","ROSTBERATTIGADE")),None)
    pairs=[]
    for i,x in enumerate(header):
        n=norm(x)
        if n.endswith(" TAL"):
            code=n[:-4].strip(); label=NAMES.get(norm(code),code)
            if code not in ("BL","OG","OGEJ"): pairs.append((i,code,label))
    parties={label for _,code,label in pairs if code!="OVR"};counts={};valid={};voters={};turnout={}
    for row in reader:
        if len(row)<=max(county_i,muni_i,valid_i,turnout_i): continue
        geo=str(row[county_i]).strip().zfill(2)+str(row[muni_i]).strip().zfill(2)
        valid[geo]=number(row[valid_i]); cast=number(row[votes_i]) if votes_i is not None else 0;eligible=number(row[eligible_i]) if eligible_i is not None else 0
        voters[geo]={"votes":cast,"eligible":eligible};turnout[geo]=number(row[turnout_i])
        counts[geo]={label:number(row[i]) for i,code,label in pairs if i<len(row) and (code=="OVR" or number(row[i])!=0)}
    return make_data(url,parties,counts,valid,voters,turnout)

def parse_percent_skv(url,body):
    reader=csv.reader(io.StringIO(body.decode("cp1252").lstrip("\ufeff")),delimiter=";")
    header=next(reader);county_i=next(i for i,x in enumerate(header) if norm(x)=="LAN");muni_i=next(i for i,x in enumerate(header) if norm(x)=="KOM")
    valid_i=next(i for i,x in enumerate(header) if norm(x)=="ROST GILTIGA");turnout_i=next(i for i,x in enumerate(header) if norm(x)=="VDT")
    votes_i=next(i for i,x in enumerate(header) if norm(x)=="ROSTANDE");eligible_i=next(i for i,x in enumerate(header) if norm(x)=="ROSTB")
    excluded={"LAN","KOM","ROST GILTIGA","ROSTANDE","ROSTB","VDT","BLANK","OG"};cols=[]
    for i,code in enumerate(header):
        code=code.strip()
        if i>=4 and norm(code) not in excluded:
            cols.append((i,NAMES.get(norm(code),code)))
    parties={name for _,name in cols if name!="Övriga anmälda partier"};shares={};valid={};voters={};turnout={}
    for row in reader:
        if len(row)<=eligible_i: continue
        geo=str(row[county_i]).strip().zfill(2)+str(row[muni_i]).strip().zfill(2)
        shares[geo]={name:number(row[i])/100 for i,name in cols if i<len(row) and (name=="Övriga anmälda partier" or number(row[i])!=0)}
        valid[geo]=number(row[valid_i]);cast=number(row[votes_i]);eligible=number(row[eligible_i]);voters[geo]={"votes":cast,"eligible":eligible};turnout[geo]=number(row[turnout_i])
    shares["00"]={name:sum(valid.get(geo,0)*values.get(name,0) for geo,values in shares.items())/sum(valid.values()) for name in parties} if sum(valid.values()) else {}
    turnout["00"]=100*sum(x["votes"] for x in voters.values())/sum(x["eligible"] for x in voters.values())
    return {"parties":sorted(parties),"shares":shares,"turnout":turnout,"validVotes":valid,"voterTotals":voters,"sourceUrl":url,"municipalityCount":len(valid)}

def parse_xlsx(url,body):
    wb=openpyxl.load_workbook(io.BytesIO(body),read_only=True,data_only=True);ws=wb[next(n for n in wb.sheetnames if "antal" in n.lower())]
    it=ws.iter_rows(values_only=True);header=next(it);county_i=next(i for i,v in enumerate(header) if norm(v) in ("LANSKOD","LAN"));muni_i=next(i for i,v in enumerate(header) if norm(v) in ("KOMMUNKOD","KOM"))
    valid_i=next(i for i,v in enumerate(header) if norm(v)=="ROSTER GILTIGA");votes_i=next(i for i,v in enumerate(header) if norm(v)=="ROSTANDE");eligible_i=next(i for i,v in enumerate(header) if norm(v)=="ROSTBERATTIGADE")
    excluded={"OGEJ","BLANK","OG","ROSTER GILTIGA","ROSTANDE","ROSTBERATTIGADE","VALDELTAGANDE"}
    cols=[]
    for i,v in enumerate(header):
        code=str(v or "").strip()
        if i>=4 and norm(code) not in excluded: cols.append((i,NAMES.get(norm(code),code)))
    parties={label for _,label in cols if label!="Övriga anmälda partier"};counts={};valid={};voters={};turnout={}
    for row in it:
        geo=str(row[county_i]).strip().zfill(2)+str(row[muni_i]).strip().zfill(2);denom=number(row[valid_i]);valid[geo]=denom
        cast=number(row[votes_i]);eligible=number(row[eligible_i]);voters[geo]={"votes":cast,"eligible":eligible};turnout[geo]=100*cast/eligible if eligible else 0
        counts[geo]={label:number(row[i]) for i,label in cols if label=="Övriga anmälda partier" or number(row[i])!=0}
    wb.close();return make_data(url,parties,counts,valid,voters,turnout)

stored=json.loads((ROOT/"val-election.json").read_text())
for year,files in FILES.items():
    for kind,url in files.items():
        body=urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
        data=parse_xlsx(url,body) if year==2018 else (parse_percent_skv(url,body) if year==2010 and kind=="Kommun" else parse_skv(url,body))
        stored[kind]["years"][str(year)]=data
        print(year,kind,data["municipalityCount"],len(data["parties"]))
(ROOT/"val-election.json").write_text(json.dumps(stored,ensure_ascii=False,separators=(",",":")))
