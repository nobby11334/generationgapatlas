#!/usr/bin/env python3
import urllib.request,zipfile,io,re,xml.etree.ElementTree as ET
URL="https://www.e-stat.go.jp/stat-search/file-download?fileKind=0&statInfId=000040077301"
h={"User-Agent":"Mozilla/5.0 GenerationGapAtlas/1.0"}
raw=urllib.request.urlopen(urllib.request.Request(URL,headers=h),timeout=50).read()
print("DOWNLOAD",len(raw),raw[:9])
z=zipfile.ZipFile(io.BytesIO(raw))
ss=[]
ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
if 'xl/sharedStrings.xml' in z.namelist():
 root=ET.fromstring(z.read('xl/sharedStrings.xml'))
 for si in root.findall('s:si',ns):
  ss.append(''.join(t.text or '' for t in si.findall('.//s:t',ns)))
print("STRINGS",len(ss),"SHEETS", [x for x in z.namelist() if re.search(r'xl/worksheets/sheet\d+\.xml$',x)])
for sheet in [x for x in z.namelist() if re.search(r'xl/worksheets/sheet\d+\.xml$',x)][:3]:
 print("SHEET",sheet)
 root=ET.fromstring(z.read(sheet))
 for row in root.findall('.//s:sheetData/s:row',ns)[:55]:
  vals=[]
  for c in row.findall('s:c',ns):
   v=c.find('s:v',ns)
   inline=c.find('s:is',ns)
   val=v.text if v is not None else ''
   if c.attrib.get('t')=='s' and val: val=ss[int(val)]
   if inline is not None:val=''.join(t.text or '' for t in inline.findall('.//s:t',ns))
   if val not in (None,''):vals.append(c.attrib.get('r','')+'='+str(val)[:50])
  print(row.attrib.get('r'), ' '.join(vals[:22])[:500])
