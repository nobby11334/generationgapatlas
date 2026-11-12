#!/usr/bin/env python3
"""Read separately listed 207 municipalities partnering in wide-area grant projects."""
import io,json,re,urllib.request
from pathlib import Path
import pdfplumber
URL="https://www.cao.go.jp/shushoku_hyogaki/suishin/pdf/kettei-r08.pdf"
OUT=Path("data/wide-area-partners-2026.json")
def tidy(x):return re.sub(r"\s+","",str(x or "")).strip()
def main():
  request=urllib.request.Request(URL,headers={"User-Agent":"GenerationGapAtlas/1.0 public-data-research"})
  data=urllib.request.urlopen(request,timeout=35).read()
  if not data.startswith(b"%PDF"):raise RuntimeError("download is not PDF")
  result=[]; diag=[]
  with pdfplumber.open(io.BytesIO(data)) as pdf:
    for index in range(5,len(pdf.pages)):
      p=pdf.pages[index]
      for side,rect in (("L",(0,0,p.width/2,p.height)),("R",(p.width/2,0,p.width,p.height))):
        segment=p.crop(rect)
        tables=segment.extract_tables(table_settings={"vertical_strategy":"lines","horizontal_strategy":"lines","snap_tolerance":4,"join_tolerance":4})
        num=0
        if index==6 and side=='L':
          print('PAGE7LEFT DEBUG',repr([(len(t),[len(r) for r in t[:5]],t[:5]) for t in tables])[:5000])
        for table in tables:
          for row in table:
            if len(row)<3:continue
            for j in range(0,len(row)-2,3):
              gov=tidy(row[j]);project=tidy(row[j+1]);expense=tidy(row[j+2])
              if not gov or gov in ("地方公共団体名","地方公共団体名交付対象事業の名称"):continue
              if not gov.endswith(("市","区","町","村")):continue
              if expense not in ("―","－","-","—",""):continue
              result.append({"municipality":gov,"participating_project":project or None,"source_page":index+1,"expense_note":"連携自治体に金額の重複計上なし。交付金執行は実施主体側。"})
              num+=1
        diag.append({"page":index+1,"side":side,"found":num})
  print("diagnostics",json.dumps(diag,ensure_ascii=False),"total",len(result),"unique",len(set(x["municipality"] for x in result)))
  if len(result)!=207:raise RuntimeError("expected 207 partners, parsed "+str(len(result))+"; refusing to publish")
  OUT.parent.mkdir(exist_ok=True,parents=True)
  OUT.write_text(json.dumps({"source":URL,"snapshot":"2026-04-01","listed_partners":207,"notes":"別添の広域連携事業で実施主体と連携する自治体一覧。152事業とは別の参加団体名簿。国の交付金は実施主体に計上される。", "municipalities":result},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
