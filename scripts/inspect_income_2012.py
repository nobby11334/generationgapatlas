import urllib.request,zipfile,io,re,xml.etree.ElementTree as ET
url="https://www.e-stat.go.jp/stat-search/file-download?statInfId=000021291516&fileKind=0"
b=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
print("SIZE",len(b),b[:12])
if not b.startswith(b"PK"):quit()
z=zipfile.ZipFile(io.BytesIO(b));print("SHEETS",[(x,z.getinfo(x).file_size) for x in z.namelist() if "worksheets/sheet" in x and x.endswith(".xml")]);ns={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[]
if "xl/sharedStrings.xml" in z.namelist():
 root=ET.fromstring(z.read("xl/sharedStrings.xml"))
 strings=["".join(t.text or "" for t in x.findall(".//x:t",ns)) for x in root.findall("x:si",ns)]
for fn in [x for x in z.namelist() if re.search("xl/worksheets/sheet[0-9]+.xml",x)][:2]:
 print("SHEET",fn)
 with z.open(fn) as stream:
  row_count=0
  for ev,elem in ET.iterparse(stream,events=('end',)):
   if not elem.tag.endswith('}row'):continue
   row_count+=1
   vals=[]
   for cell in elem.findall("x:c",ns):
    v=cell.find("x:v",ns);value=v.text if v is not None else ''
    if cell.attrib.get('t')=='s' and value:value=strings[int(value)]
    if cell.attrib.get('t')=='inlineStr':value=''.join(t.text or '' for t in cell.findall(".//x:t",ns))
    if value not in ('',None):vals.append(cell.attrib.get('r')+'='+str(value)[:38])
   if row_count<=38 or (row_count<500 and row_count%80==0):print('ROW',row_count,' '.join(vals[:17])[:400])
   elem.clear()
 print("TOTAL",row_count)
