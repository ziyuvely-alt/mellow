import hashlib,json,urllib.request,time
from io import BytesIO
from PIL import Image
from pathlib import Path
items=json.loads(Path("evidence/v242-new8-image-manifest.json").read_text())
records=[]
for item in items:
 url="https://mellow-bbia-images.onrender.com/"+item["path"]
 r={"url":url,"expected_sha256":item["sha256"],"expected_bytes":item["bytes"],"attempts":0}
 for _ in range(3):
  r["attempts"]+=1
  try:
   q=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (MellowKR v2.4.2 public image verifier)","Accept":"image/jpeg,image/*"})
   with urllib.request.urlopen(q,timeout=25) as resp:
    r["http_status"]=resp.status
    r["content_type"]=resp.headers.get("Content-Type","")
    blob=resp.read(2_000_001)
   im=Image.open(BytesIO(blob));im.load()
   r["image_format"]=im.format
   r["size"]=list(im.size)
   r["bytes"]=len(blob)
   r["sha256"]=hashlib.sha256(blob).hexdigest()
   r["pass"]=r["http_status"]==200 and r["content_type"].lower().startswith("image/jpeg") and im.format=="JPEG" and im.size==(1080,1080) and len(blob)<2_000_000 and len(blob)==item["bytes"] and r["sha256"]==item["sha256"]
   if r["pass"]:break
  except Exception as ex:
   r["pass"]=False;r["error"]=str(ex)[:300]
  time.sleep(5)
 print(r["url"],"PASS" if r["pass"] else "FAIL",r.get("error",""),flush=True)
 records.append(r)
Path("v242-public-new8-report.json").write_text(json.dumps({"total":len(records),"verified":sum(a["pass"] for a in records),"results":records},ensure_ascii=False,indent=2))
