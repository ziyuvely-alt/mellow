import json,hashlib,requests,io
from PIL import Image
from pathlib import Path
data=[["01","49272fd632b8505254d16be4b6e1c0c5964a7022da05925714f852bc9b664b1e",155529],["02","60530c62d0d61ea1ecab20c4eb189b5f723367fdab34f165ed800fa5bd3d967e",121694],["03","c638e8357a6b72c56473283640f4bc78a7258973d830833b75866f618ae068b9",159934],["04","c5ed8c26e75019d5c950559f6f41bb1b01802450ab0784a234aa176674012da5",139489],["05","6e581843252b4e13b5e7091589df96a1e5d3c8cdf88dc036ec7356603243a6bb",136334]]
prefix="images/bioheal-boh-collagen-remodeling-eye-patch-60p-v240-20261031/"
bases={"github_raw":"https://raw.githubusercontent.com/ziyuvely-alt/mellow/main/public/","render":"https://mellow-bbia-images.onrender.com/"}
out=[]
for host,base in bases.items():
 for stem,sha,n in data:
  url=base+prefix+stem+".jpg"; item={"host":host,"url":url,"sha256_expected":sha}
  try:
   r=requests.get(url,timeout=30,headers={"User-Agent":"Shopee-ImageQA/2.4.0","Accept":"image/jpeg"})
   raw=r.content;im=Image.open(io.BytesIO(raw));im.load()
   item.update(http=r.status_code,mime=r.headers.get("Content-Type",""),bytes=len(raw),dimensions=list(im.size),sha256=hashlib.sha256(raw).hexdigest())
   item["pass"]=r.status_code==200 and item["mime"].lower().startswith("image/jpeg") and im.format=="JPEG" and im.size==(1080,1080) and len(raw)==n and item["sha256"]==sha
  except Exception as e:item.update(pass_=False,error=str(e)[:300]);item["pass"]=False
  print(host,stem,"PASS" if item["pass"] else "FAIL",item.get("http"),flush=True)
  out.append(item)
Path("v240_boh_public_url_qa.json").write_text(json.dumps({"results":out,"verified":[x for x in out if x["pass"]]},indent=2))
