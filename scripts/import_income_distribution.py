#!/usr/bin/env python3
"""Import official 2022 Japan Employment Status Survey Table 40 income brackets.
Source XLSX uses XML; parse read-only with Python standard library.
Do not impute any missing or undisclosed cell.
"""
import io,json,re,urllib.request,zipfile,xml.etree.ElementTree as ET
from pathlib import Path

URL="https://www.e-stat.go.jp/stat-search/file-download?fileKind=0&statInfId=000040077301"
PAGE="https://www.e-stat.go.jp/dbview?sid=0004008157"
OUT=Path("data/income-distribution-2022.json")
N={"x":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
BRACKETS=[
["50万円未満",0,50],["50～99万円",50,100],["100～149万円",100,150],
["150～199万円",150,200],["200～249万円",200,250],["250～299万円",250,300],
["300～399万円",300,400],["400～499万円",400,500],["500～599万円",500,600],
["600～699万円",600,700],["700～799万円",700,800],["800～899万円",800,900],
["900～999万円",900,1000],["1000～1249万円",1000,1250],
["1250～1499万円",1250,1500],["1500万円以上",1500,None]
]
AGES=["20～24歳","25～29歳","30～34歳","35～39歳","40～44歳","45～49歳","50～54歳","55～59歳","60～64歳","65～69歳"]
SEX={"総数":"all","男":"male","女":"female"}
EMP={"総数":"all","うち正規の職員・従業員":"regular","うち非正規の職員・従業員":"nonregular"}
def parse_label(s):
 return s.split("_",1)[-1] if s else ""
def xlsx_rows(raw):
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  shared=[]
  if "xl/sharedStrings.xml" in z.namelist():
   root=ET.fromstring(z.read("xl/sharedStrings.xml"))
   shared=["".join(t.text or "" for t in x.findall(".//x:t",N)) for x in root.findall("x:si",N)]
  with z.open("xl/worksheets/sheet1.xml") as stream:
   for event,elem in ET.iterparse(stream,events=("end",)):
    if elem.tag!="{"+N["x"]+"}row":continue
    rec={}
    for c in elem.findall("x:c",N):
     col=re.match(r"[A-Z]+",c.attrib["r"]).group()
     v=c.find("x:v",N)
     value=v.text if v is not None else None
     if c.attrib.get("t")=="s" and value is not None:value=shared[int(value)]
     if c.attrib.get("t")=="inlineStr":
      x=c.find("x:is",N);value="".join(t.text or "" for t in x.findall(".//x:t",N)) if x is not None else None
     rec[col]=value
    yield rec
    elem.clear()
def main():
 req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (GenerationGapAtlas statistical research)"})
 raw=urllib.request.urlopen(req,timeout=60).read()
 if not raw.startswith(b"PK"):raise RuntimeError("Official source is not XLSX")
 results={}
 for row in xlsx_rows(raw):
  if not all(col in row for col in ("D","F","H","J","L","M")):continue
  sex=SEX.get(parse_label(row["D"]))
  age=parse_label(row["H"])
  emp=EMP.get(parse_label(row["J"]))
  marital=parse_label(row["F"])
  income=parse_label(row["L"])
  if sex is None or age not in AGES or emp is None or marital!="総数":continue
  key=(age,sex,emp)
  x=results.setdefault(key,{"total":None,"counts":{},"suppressed":[]})
  value=row["M"]
  number=int(float(value)) if value and re.fullmatch(r"\d+(?:\.\d+)?",value) else (0 if value=="-" else None)
  if income=="総数": x["total"]=number
  elif income in [v[0] for v in BRACKETS]:
   if number is None:x["suppressed"].append(income)
   else:x["counts"][income]=number
 assert len(results)>=60, f"Insufficient age/sex/employment breakdowns: {len(results)}"
 out=[]
 for (age,sex,emp),item in sorted(results.items(),key=lambda x:(AGES.index(x[0][0]),x[0][1],x[0][2])):
  total=item["total"]
  if not total:continue
  values=[item["counts"].get(b[0]) for b in BRACKETS]
  if any(v is None for v in values):continue
  known=sum(values)
  if known>total+len(values)*100:raise RuntimeError(f"Income buckets exceed total: {age} {sex} {emp}: {known}>{total}")
  unknown=max(0,total-known)
  out.append({"age":age,"sex":sex,"employment":emp,"total_people":total,
              "known_income_people":known,"unknown_income_people":unknown,
              "people_by_bracket":values})
 assert len(out)>=60, f"Insufficient complete series: {len(out)}"
 assert any(x["age"]=="45～49歳" and x["sex"]=="all" and x["employment"]=="all" for x in out)
 data={"year":2022,"survey":"令和4年就業構造基本調査","table":"全国表40 / 04000",
       "source":PAGE,"source_excel":URL,"population":"2022年の有業者、主な仕事からの年間収入・収益。無業者は含まない。",
       "brackets":[{"label":x[0],"lower_man_yen":x[1],"upper_man_yen":x[2]} for x in BRACKETS],
       "ages":AGES,"definition":"所得階級内の件数は2022年の調査による推計人口。所得不詳はunknown_income_peopleとして保持。百分率は所得判明者を分母。",
       "notes":["年齢帯別の横断比較であり1980年生まれ等の出生コーホートに厳密に対応するわけではない。",
                "2022年時点の就職氷河期中心層（1974〜1983生まれ）は39〜48歳。35〜49歳帯と一部重なる。",
                "この調査の所得は給与に加え自営業の収益を含み得るため、国税庁給与調査との直接比較はできない。",
                "所得を申告しなかった対象を分母から除く際は欠損率を併記。高所得の最上位階級は上限なし。",
                "階級から中央値のある範囲はわかるが、中央値・ジニ係数・P90/P10の厳密な点推定はできない。"],
       "records":out}
 OUT.parent.mkdir(exist_ok=True,parents=True)
 OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("SUCCESS income distribution",len(out),"complete age/sex/employment series; total",next(x["total_people"] for x in out if x["age"]=="45～49歳" and x["sex"]=="all" and x["employment"]=="all"))
if __name__=="__main__":main()
