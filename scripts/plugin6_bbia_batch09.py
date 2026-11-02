from pathlib import Path
from urllib.parse import urljoin
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
import requests,re,hashlib,zipfile,json,concurrent.futures
ROOT=Path("plugin6-bbia-batch09-official");ROOT.mkdir(exist_ok=True)
FAMILIES=[
 ("36_last_blush","1357","Bbia Last Blush"),
 ("34_last_contour_stick","1129","Bbia Last Contour Stick")
]
def one(args):
 slug,gid,prefix=args
 page=f"https://www.bbia.co.th/product_info.php?products_id={gid}"
 sub=ROOT/slug;sub.mkdir(exist_ok=True)
 report={"family":slug,"page":page,"candidate_options":[],"errors":[]}
 try:
  r=requests.get(page,timeout=22,headers={"User-Agent":"Mozilla/5.0"});r.raise_for_status()
  soup=BeautifulSoup(r.text,"html.parser")
  candidates={}
  for tag in soup.find_all("img"):
   alt=(tag.get("alt") or "").strip()
   if prefix.lower() not in alt.lower():continue
   m=re.search(r" - (\\d{2}) (.+)$",alt)
   if not m:continue
   n=int(m.group(1));imgurl=urljoin(r.url,tag.get("src") or tag.get("data-src") or "")
   if not imgurl.startswith("http"):continue
   candidates.setdefault(n,(n,m.group(2).strip(),imgurl,alt))
  def collect(item):
   n,name,url,alt=item;row={"number":n,"official_name":name,"alt":alt,"source_url":url,"status":"FAILED"}
   try:
    res=requests.get(url,timeout=13,headers={"User-Agent":"Mozilla/5.0","Referer":page});res.raise_for_status()
    if not res.content or len(res.content)>8_000_000:raise ValueError("download size")
    image=Image.open(BytesIO(res.content));image.load()
    if min(image.size)<120 or image.format not in ("JPEG","PNG","WEBP"):raise ValueError("invalid image")
    fname=f"{slug}_{n:02d}.jpg"
    image.convert("RGB").save(sub/fname,quality=92,optimize=True)
    row.update(status="OFFICIAL_PRODUCT_PHOTO_PENDING_VISUAL_QA",file=fname,width=image.width,height=image.height,sha256=hashlib.sha256(res.content).hexdigest())
   except Exception as exc:row["error"]=str(exc)[:120]
   return row
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:report["candidate_options"]=list(pool.map(collect,candidates.values()))
 except Exception as exc:report["errors"].append(str(exc)[:200])
 report["downloaded"]=sum(x["status"].startswith("OFFICIAL_") for x in report["candidate_options"])
 print(slug,"downloaded",report["downloaded"],"option_candidates",len(report["candidate_options"]),flush=True)
 (sub/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
 return report
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:report=list(pool.map(one,FAMILIES))
(ROOT/"BATCH09_AUDIT.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
with zipfile.ZipFile(ROOT/"SOURCE_ONLY_QA_PENDING.zip","w",zipfile.ZIP_DEFLATED) as z:
 for p in ROOT.rglob("*"):
  if p.is_file() and p.suffix.lower() in (".jpg",".json"):z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(ROOT/"SOURCE_ONLY_QA_PENDING.zip") as z:assert z.testzip() is None
