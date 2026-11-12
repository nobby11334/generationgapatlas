#!/usr/bin/env python3
"""Harmonize 2002/2012/2022 employment survey income brackets to 15 consistent nominal bins.
Comparability scope: all workers and regular employees; sex and age groups.
Always retain unsummed income-undisclosed population, never impute.
"""
import io,json,re,urllib.request
from pathlib import Path
import xlrd
HERE=Path("data")
LINKS={
 2002:["https://www.e-stat.go.jp/stat-search/file-download?statInfId=000000130068&fileKind=0",
       "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000000130069&fileKind=0"],
 2012:["https://www.e-stat.go.jp/stat-search/file-download?statInfId=000021291516&fileKind=0"]
}
AGES=["20～24歳","25～29歳","30～34歳","35～39歳","40～44歳","45～49歳","50～54歳","55～59歳","60～64歳","65～69歳"]
BINS=[{"label":s,"lower":low,"upper":hi} for s,low,hi in [
 ("50万円未満",0,50),("50～99万円",50,100),("100～149万円",100,150),("150～199万円",150,200),
 ("200～249万円",200,250),("250～299万円",250,300),("300～399万円",300,400),
 ("400～499万円",400,500),("500～599万円",500,600),("600～699万円",600,700),
 ("700～799万円",700,800),("800～899万円",800,900),("900～999万円",900,1000),
 ("1000～1499万円",1000,1500),("1500万円以上",1500,None)]]
def get(url):
 raw=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 research"}),timeout=70).read()
 if not raw.startswith(b"\xd0\xcf\x11\xe0"):raise ValueError("unexpected excel data at "+url)
 return xlrd.open_workbook(file_contents=raw,on_demand=True)
def num(value):
 if value in ("",None,"-","－","*"):return 0
 if isinstance(value,(int,float)):return int(round(value))
 raise ValueError("Unexpected cell value "+repr(value))
def normalize_age(s):
 return str(s).strip().replace("〜","～").replace(" ","")
def blocks(sheet,year,col):
 # Row positions are carefully verified against official XLS tables.
 if year==2002:
  spec=[("all",16,17,31),("regular",64,65,79)]
 else:
  spec=[("all",13,14,29),("regular",64,65,80)]
 out=[]
 for employment,total_row,first,last in spec:
  total=num(sheet.cell_value(total_row,col))
  values=[num(sheet.cell_value(r,col)) for r in range(first,last+1)]
  if year==2012:values=values[:13]+[values[13]+values[14],values[15]]
  if len(values)!=15:raise ValueError(f"{year} {sheet.name} {employment} bins={len(values)}")
  known=sum(values)
  # Survey figures rounded to nearest 100; allow 100 persons per income bin.
  if known>total+1600:raise ValueError(f"{year} {sheet.name} {employment} over-count {known}>{total}")
  unknown=max(0,total-known)
  out.append((employment,total,known,unknown,values))
 return out
def main():
 records=[]
 for year,urls in LINKS.items():
  processed=set()
  for url in urls:
   book=get(url)
   print("BOOK",year,len(book.sheet_names()),book.sheet_names())
   for sheet in book.sheets():
    age=normalize_age(sheet.cell_value(6,7))
    if age not in AGES or age in processed:continue
    processed.add(age)
    for sex,col in ([("all",9),("male",16),("female",23)] if year==2002 else [("all",9),("male",19),("female",28)]):
     for employment,total,known,unknown,values in blocks(sheet,year,col):
      if total<=0:continue
      records.append({"year":year,"age":age,"sex":sex,"employment":employment,
                      "total_people":total,"known_income_people":known,"unknown_income_people":unknown,
                      "people_by_bracket":values,"source":url})
  print("YEAR",year,"matched ages",sorted(processed))
  if len(processed)<10:raise RuntimeError(f"{year}: not enough age bands, only {len(processed)}")
 previous=json.loads((HERE/"income-distribution-2022.json").read_text(encoding="utf-8"))
 for item in previous["records"]:
  if item["employment"] not in ("all","regular"):continue
  vals=item["people_by_bracket"]
  fifteen=vals[:13]+[vals[13]+vals[14],vals[15]]
  records.append({**item,"year":2022,"people_by_bracket":fifteen,"source":previous["source"]})
 for year in (2002,2012,2022):
  for sex in ("all","male","female"):
   for job in ("all","regular"):
    for age in AGES:
     if not any(r["year"]==year and r["age"]==age and r["sex"]==sex and r["employment"]==job for r in records):
      raise RuntimeError(f"Missing {year} {age} {sex} {job}")
 if len(records)!=180:raise RuntimeError(f"Expected 180 disaggregated records, found {len(records)}")
 for year in (2002,2012,2022):
  for age in AGES:
   for employment in ("all","regular"):
    ar=next(r for r in records if r["year"]==year and r["age"]==age and r["sex"]=="all" and r["employment"]==employment)
    mr=next(r for r in records if r["year"]==year and r["age"]==age and r["sex"]=="male" and r["employment"]==employment)
    fr=next(r for r in records if r["year"]==year and r["age"]==age and r["sex"]=="female" and r["employment"]==employment)
    if abs(ar["total_people"]-mr["total_people"]-fr["total_people"])>2000:raise RuntimeError(f"Sex sum mismatch {year} {age} {employment}")

 doc={"dataset":"2002, 2012, 2022 Japan Employment Status Survey, national 15-bin distributions",
      "years":[2002,2012,2022],"brackets":BINS,"records":records,
      "scope":"有業者と正規の職員・従業員。年齢10区分×性3区分×雇用2区分×調査3時点。",
      "warnings":["所得階級は各年の名目円。物価調整なしで実質購買力の高低を断定できない。",
                  "2002年の1000〜1499万円に合わせ、2012/2022年の1000〜1249/1250〜1499万円を合算。",
                  "2002年の非正規区分が一致しないため三時点の正規以外は対象に含めない。",
                  "各年の同一年齢帯の比較は異なる出生世代を比較する。出生年代固定の分析は年齢帯を10年ずらして見る近似に限る。",
                  "所得不詳者は常に記録し、分布割合は所得判明者を分母として計算。",
                  "所得階級内の細かな分布は不明。二極化の進行は中間層の変化など複数指標と照合する。"],
      "sources":{"2002":LINKS[2002],"2012":LINKS[2012],"2022":[previous["source_excel"]]}}
 HERE.mkdir(exist_ok=True)
 (HERE/"income-distribution-history.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("VERIFIED",len(records),"historical income series")
if __name__=="__main__":main()
