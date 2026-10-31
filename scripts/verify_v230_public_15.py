import hashlib,json,urllib.request,os
from PIL import Image
from io import BytesIO
from pathlib import Path
BASE="https://mellow-bbia-images.onrender.com/"
items=json.loads(Path("evidence/v230-public-url-15.json").read_text())
out=[]
for a in items:
 url=BASE+a["file"]
 record={"group":a["group"],"url":url,"expected_sha256":a["sha256"]}
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; PublicURLSourceQA/1.0)","Accept":"image/jpeg,image/*"})
  with urllib.request.urlopen(req,timeout=28) as r:
   record["status_code"]=r.status
   record["content_type"]=r.headers.get("Content-Type","")
   blob=r.read(2000001)
  im=Image.open(BytesIO(blob)); im.load()
  record["image_dimensions"]=list(im.size)
  record["bytes"]=len(blob)
  record["sha256"]=hashlib.sha256(blob).hexdigest()
  record["passed"]=record["status_code"]==200 and record["content_type"].lower().startswith("image/jpeg") and im.format=="JPEG" and im.size==(1080,1080) and len(blob)==a["bytes"] and len(blob)<2000000 and record["sha256"]==a["sha256"]
 except Exception as e:record.update({"passed":False,"error":str(e)[:400]})
 out.append(record)
 print(a["group"],os.path.basename(a["file"]),"PASS" if record["passed"] else "FAIL",record.get("error",""),flush=True)
Path("v230-url-check.json").write_text(json.dumps({"total":len(out),"passed":sum(r["passed"] for r in out),"results":out},ensure_ascii=False,indent=2))
