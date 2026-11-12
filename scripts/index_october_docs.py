#!/usr/bin/env python3
"""Index the official October 2026 national platform documents.
Do not fabricate outcome statistics; collect source URLs and text samples
for human review, leaving KPI result interpretation to audited datasets.
"""
import json,re,urllib.request,urllib.parse
from html.parser import HTMLParser
from datetime import datetime,timezone
from pathlib import Path
import io,pdfplumber

ROOT="https://www.cas.go.jp/jp/seisaku/shushoku_hyogaki_shien/suishin_platform/dai8/gijishidai.html"
OUT=Path("data/october-2026-official-documents.json")
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.active=None
 def handle_starttag(self,tag,attrs):
  if tag=="a":self.active=dict(attrs).get("href");self.buf=[]
 def handle_data(self,data):
  if self.active is not None:self.buf.append(data)
 def handle_endtag(self,tag):
  if tag=="a" and self.active:
   self.links.append((self.active,"".join(self.buf).strip()))
   self.active=None
def req(url):
 r=urllib.request.Request(url,headers={"User-Agent":"GenerationGapAtlas/1.0 (public data research)"})
 with urllib.request.urlopen(r,timeout=55) as response:return response.read()
def main():
 html=req(ROOT).decode("utf-8","replace");p=Links();p.feed(html)
 links=[]
 for href,label in p.links:
  if not href:continue
  url=urllib.parse.urljoin(ROOT,href)
  if "/suishin_platform/dai8/" not in url or not url.lower().endswith(".pdf"):continue
  if not re.search(r"(資料|siryou|pdf)",label,re.I):continue
  if url in {x["url"] for x in links}:continue
  links.append(dict(url=url,title=re.sub(r"\s+"," ",label),text_extracted=False))
 print("found",len(links),"PDF documents",[(x["title"],x["url"]) for x in links])
 if len(links)<14:raise ValueError("Expected October meeting PDFs; found fewer than 14. Rejecting partial publication.")
 for x in links:
  raw=req(x["url"])
  if not raw.startswith(b"%PDF"):raise ValueError("Invalid PDF at "+x["url"])
  with pdfplumber.open(io.BytesIO(raw)) as doc:
   x["pages"]=len(doc.pages)
   if not x["pages"]:raise ValueError("No pages: "+x["url"])
   x["sample_text"]=[]
   for pn,page in enumerate(doc.pages):
    t=page.extract_text() or ""
    if not t.strip():continue
    # Truncated text is for search/discovery, not a complete transcription.
    x["sample_text"].append(dict(page=pn+1,excerpt=t[:900]))
   x["text_extracted"]=bool(x["sample_text"])
 # Source manifest only: no unreviewed assertions about program outcome changes.
 doc={"meeting_date":"2026-10-27","source_page":ROOT,"generated_utc":datetime.now(timezone.utc).isoformat(),"scope":"第8回全国プラットフォームの公表PDF一覧。抜粋テキストは検索補助であり全文・KPI構造化ではない。","documents":links}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("indexed",len(links),"documents, pages",sum(x["pages"] for x in links))
if __name__=="__main__":main()
