#!/usr/bin/env python3
"""Reproducible page-by-page transcription of government's October KPI report.
Retains source page boundaries. No automatic inference of comparable rates.
"""
import io,json,urllib.request
from pathlib import Path
from datetime import datetime,timezone
import pdfplumber
URL="https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/suishin_platform/dai8/shiryo04.pdf"
TARGET=Path("data/official-kpi-pages-2026-10.json")
def main():
 req=urllib.request.Request(URL,headers={"User-Agent":"GenerationGapAtlas/1.0 public-data-audit"})
 raw=urllib.request.urlopen(req,timeout=45).read()
 if not raw.startswith(b"%PDF"):raise RuntimeError("Invalid PDF")
 with pdfplumber.open(io.BytesIO(raw)) as pdf:
  if len(pdf.pages)!=8:raise RuntimeError("KPI page count changed; review required")
  pages=[{"page":i+1,"text":p.extract_text() or "","url":URL+"#page="+str(i+1)} for i,p in enumerate(pdf.pages)]
 if not all(len(p['text'])>20 for p in pages):raise RuntimeError("Unextractable page; review required")
 result={"as_of":"2026-10-27","source":URL,"extraction_method":"pdfplumber text extraction, no OCR, no interpretation","warning":"表・グラフのPDFテキストの並び順は原版と異なる可能性があるため、数値の確定には元PDFを確認してください。", "pages":pages}
 TARGET.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("verified 8-page KPI transcription",sum(len(p["text"]) for p in pages),"characters")
if __name__=="__main__":main()
