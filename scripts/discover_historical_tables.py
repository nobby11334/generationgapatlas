import urllib.request,re
urls={
"2012":"https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&month=0&page=1&tclass1=000001059806&tclass2=000001059807&toukei=00200532&tstat=000001058052&year=20120",
"2002":"https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&month=0&page=1&tclass1=000000130002&tclass2=000000130003&toukei=00200532&tstat=000000130001&year=20020"
}
for year,u in urls.items():
 try:
  r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read().decode('utf-8','replace')
  print(year,"html",len(r),"statInfID",sorted(set(re.findall(r'statInfId[=/%3D]+(\d+)',r,re.I)))[:30])
  for pattern in ['第４０表','表番号','所得，男女，教育','04101']:
   i=r.find(pattern)
   if i!=-1:print(year,pattern,r[max(0,i-900):i+1600][:2600].replace('\n',' ') )
 except Exception as e:print(year,"ERROR",e)

for year,u in {"2002":"https://www.e-stat.go.jp/stat-search/files?cycle=0&layout=datalist&page=1&tclass1=000000130002&tclass2=000000130003&toukei=00200532&tstat=000000130001&year=20020"}.items():
 r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read().decode("utf-8","replace")
 for marker in ["年齢，従業上の地位，雇用形態，所得，男女，教育別有業者数","年齢，従業上の地位，雇用形態，所得"]:
  i=r.find(marker)
  if i>=0:print(year,"MATCH",r[i-700:i+1200].replace("\\n"," ")[:1900])
