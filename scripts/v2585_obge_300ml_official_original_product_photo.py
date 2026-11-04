#!/usr/bin/env python3
"""v2585 obtain actual exact OBgE MAX Waterful 300mL official product photo.
No fake packaging, no licensed rights inference, never replace prior image.
If URL is inaccessible report HOLD, do not abort the other completed work.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageChops,ImageStat
from io import BytesIO
import hashlib,json
OUT=Path("v2585-obge-waterful-300ml-original-photo-QA")
OUT.mkdir(exist_ok=True)
BASE=Path("v2585-base/review-JPG-by-family/pending-22")
assert BASE.is_dir()
prior=sorted(BASE.glob("*.jpg"))
assert len(prior)==5
url="https://m.obge.co.kr/web/product/medium/202603/e039688781d45789b70ee436c13cf0f6.png"
source_page="https://obge.co.kr/product/detail.html?cate_no=1&display_group=14&product_no=1251"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dhash(im):
  p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata());v=0
  for y in range(8):
    for x in range(8):v=(v<<1)|(p[y*9+x]>p[y*9+x+1])
  return v
def mae(a,b):
 a=a.resize((128,128));b=b.resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
m={"version":"v2585","family":"pending-22","source_page":source_page,
"source_url":url,"official_catalog_300ml_confirmed_from_prior_document":True,
"product_photo_identity_on_package_human_verified":False,"owned_stock_edition_verified":False,
"photo_commercial_reuse_rights_confirmed":False,"published":False,
"previous_156_jpgs_changed":0,"old_55_public_urls_changed":0,"xlsx_created_or_shared":False}
try:
 with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/*"}),timeout=20) as response: raw=response.read(7_000_001)
 assert 12000<len(raw)<7_000_000
 src=Image.open(BytesIO(raw));src.load()
 assert src.format in ("JPEG","PNG","WEBP") and min(src.size)>=320
 real=ImageOps.contain(src.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 frame=Image.new("RGB",(1080,1080),"#fafbf9")
 frame.paste(real,((1080-real.width)//2,(1080-real.height)//2))
 dest=OUT/"pending-22-official-300ml-product-photo-CANDIDATE.jpg"
 frame.save(dest,"JPEG",quality=90,optimize=True,subsampling=0)
 assert Image.open(dest).size==(1080,1080) and dest.stat().st_size<2_000_000
 comparisons=[]
 for p in prior:
  old=Image.open(p).convert("RGB")
  comparisons.append({"slot":int(p.name[:2]),"dhash_distance":(dhash(old)^dhash(frame)).bit_count(),"pixel_mae":mae(old,frame)})
 alerts=[x for x in comparisons if x["dhash_distance"]<=6 or x["pixel_mae"]<8]
 m.update({"status":"HOLD_POSSIBLE_DUPLICATE" if alerts else "DISTINCT_PRODUCT_PHOTO_QA_ONLY",
 "file":dest.name,"candidate_sha256":sha(dest.read_bytes()),"original_sha256":sha(raw),
 "source_size_px":list(src.size),"similarity_against_existing":comparisons,
 "similarity_alerts":alerts})
except Exception as e:
 m.update({"status":"SOURCE_DOWNLOAD_HOLD","error_type":type(e).__name__})
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":m["status"],"photo_saved":int("file" in m),"alerts":len(m.get("similarity_alerts",[])),"released":False,"xlsx":False}))
