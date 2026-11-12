import urllib.request,io,xlrd
urls={"2012":"https://www.e-stat.go.jp/stat-search/file-download?statInfId=000021291516&fileKind=0","2002":"https://www.e-stat.go.jp/stat-search/file-download?statInfId=000000130068&fileKind=0"}
for year,url in urls.items():
 try:
  b=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
  print("YEAR",year,"SIZE",len(b),"MAGIC",b[:8])
  book=xlrd.open_workbook(file_contents=b,on_demand=True)
  print("SHEETS",[(s.name,s.nrows,s.ncols) for s in book.sheets()])
  for sheet in book.sheets()[:2]:
   print("SHEET",sheet.name)
   for i in range(min(sheet.nrows,62)):
    vals=[f"{j}:{str(sheet.cell_value(i,j))[:55]}" for j in range(min(sheet.ncols,18)) if sheet.cell_value(i,j) not in ("",None)]
    if vals:print("ROW",i," ".join(vals[:13])[:430])
 except Exception as e:print("ERROR",year,str(e))
