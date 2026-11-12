#!/usr/bin/env python3
"""Extract every published grant project from Cabinet Office's official PDF.
Fails closed on unexpected publication formats or mismatched total counts.
"""
import io, json, re, urllib.request
from datetime import date
from pathlib import Path
import pdfplumber

URL="https://www.cao.go.jp/shushoku_hyogaki/suishin/pdf/kettei-r08.pdf"
TARGET=Path("data/local-grants-2026.json")
EXPECTED=152
def clean(value):
    return re.sub(r"\s+","", str(value or "")).strip()
def number(value):
    s=clean(value).replace(",","").replace("，","")
    return int(s) if re.fullmatch(r"[0-9]+",s) else None
def collect():
    req=urllib.request.Request(URL,headers={"User-Agent":"GenerationGapAtlas/1.0 public-data-research"})
    raw=urllib.request.urlopen(req,timeout=35).read()
    if not raw.startswith(b"%PDF"):raise ValueError("Not a PDF")
    rows=[]; diagnostic=[]
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for pn,page in enumerate(pdf.pages):
            if pn==0:continue
            bounds=[(0,0,page.width/2,page.height),(page.width/2,0,page.width,page.height)]
            for side,rect in enumerate(bounds):
                crop=page.crop(rect)
                tables=crop.extract_tables(table_settings={"vertical_strategy":"lines","horizontal_strategy":"lines","snap_tolerance":4,"join_tolerance":4})
                last_name=None; added=0
                for tab in tables:
                    for cells in tab:
                        if not cells or len(cells)<3:continue
                        # Extract left/right three column groups from tables.
                        for j in range(0,len(cells)-2,3):
                            government=clean(cells[j]); title=clean(cells[j+1]); amount=number(cells[j+2])
                            if government and government not in ("地方公共団体名","団体名"):
                                last_name=government
                            if not title or title in ("交付対象事業の名称","事業名") or amount is None:continue
                            if not last_name:continue
                            if "【広域】" in title: title=title.replace("【広域】","").strip(); wide=True
                            else:wide=False
                            rows.append(dict(municipality=last_name,project=title,budget_thousand_yen=amount,wide_area=wide,category="prefecture" if last_name.endswith(("都","道","府","県")) else "municipality",source_page=pn+1))
                            added+=1
                diagnostic.append({"page":pn+1,"side":"L" if side==0 else "R","extracted":added,"tables":len(tables)})
    return rows,diagnostic

def main():
    rows,diagnostic=collect()
    print("diagnostics",json.dumps(diagnostic,ensure_ascii=False))
    print("records",len(rows),"budget_thousand_yen_sum",sum(r["budget_thousand_yen"] for r in rows))
    if len(rows)!=EXPECTED: raise ValueError(f"Expected {EXPECTED} official projects, extracted {len(rows)}. Refusing publication.")
    if any(not r["municipality"] or not r["project"] or r["budget_thousand_yen"]<1 for r in rows):
        raise ValueError("Bad record; refusing publication.")
    if len(set((r["municipality"],r["project"],r["budget_thousand_yen"]) for r in rows))!=EXPECTED:
        raise ValueError("Duplicate projects; refusing publication.")
    # 28.1oku is rounded publicly. Per-project budget values should be close.
    amt=sum(r["budget_thousand_yen"] for r in rows)
    if not 2_700_000 <= amt <= 2_920_000:
        raise ValueError(f"Project totals do not reconcile with published 28.1oku yen: {amt}")
    data=dict(source=URL,official_snapshot="2026-04-01",published="2026-03-31",data_kind="project_expense_planned",currency_unit="thousand_JPY",records=len(rows),municipality_notes="300 recipient municipalities includes cooperating municipalities in wide-area projects; the project list only names lead implementing bodies.",total_expense_thousand_yen=amt,notes="事業費。国の交付金額21.4億円とは異なり、執行実績・支払額でもない。",projects=rows)
    TARGET.parent.mkdir(exist_ok=True,parents=True)
    TARGET.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("wrote",TARGET)

if __name__=="__main__":main()
