#!/usr/bin/env python3
"""v2581. Batch-download 4 actual manufacturer/retailer photo candidates from
two exact product listings (BIOHEAL BOH NAD Prizcell Glow Serum 30mL and Boost
Cream 50mL), without claiming these are licensed or exact owned-stock packs.
Compare to already-staged five 1080 JPG scenes per SKU; segregate any duplicates
or suspicious candidate. No existing image modification, publishing, Excel.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageStat,ImageChops
import hashlib,json
BASE=Path("v2581-original/review-JPG-by-family")
OUT=Path("v2581-bioheal-two-products-four-real-source-images")
OUT.mkdir(exist_ok=True)
cases=[
("pending-24","NAD PRIZCELL Glow Power Serum 30ml","https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388235ko.jpg?l=ko","https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000233882"),
("pending-24","NAD PRIZCELL Glow Power Serum 30ml","https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0023/A00000023388202ko.jpg?l=ko","https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000233882"),
("pending-25","NAD PRIZCELL Glow Boost Cream 50ml","https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629910ko.jpg?l=ko","https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246299"),
("pending-25","NAD PRIZCELL Glow Boost Cream 50ml","https://image.oliveyoung.co.kr/cfimages/cf-goods/uploads/images/thumbnails/10/0000/0024/A00000024629911ko.jpg?l=ko","https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo=A000000246299")
]
def sha(data):return hashlib.sha256(data).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 h=0
 for y in range(8):
  for x in range(8):h=(h<<1)|(p[y*9+x]>p[y*9+x+1])
 return h
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
baseline={}
for family in ("pending-24","pending-25"):
 paths=sorted((BASE/family).glob("*.jpg"))
 assert len(paths)==5
 baseline[family]=[(p,Image.open(p).convert("RGB")) for p in paths]
results=[];selected={k:[] for k in baseline}
for idx,(fam,product,url,page) in enumerate(cases,1):
 metadata={"family":fam,"product":product,"retrieval_url":url,"retailer_page":page,
 "commercial_rights_verified":False,"physical_stock_confirmed":False}
 try:
  req=Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"})
  with urlopen(req,timeout=18) as res:raw=res.read(7_000_001)
  assert 15000<len(raw)<7_000_000
  photo=Image.open(BytesIO(raw));photo.load()
  assert photo.format in ("JPEG","PNG","WEBP") and min(photo.size)>=400,(photo.format,photo.size)
  scaled=ImageOps.contain(photo.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  im=Image.new("RGB",(1080,1080),"#fafafa")
  im.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
  dst=OUT/f"{fam}-{idx:02d}-retailer-original-QA.jpg"
  im.save(dst,"JPEG",quality=90,optimize=True,subsampling=0)
  assert Image.open(dst).size==(1080,1080) and dst.stat().st_size<2_000_000
  checks=[]
  for old,img in baseline[fam]:
   checks.append({"against":"previous-"+old.name[:2],"dhash":(dhash(im)^dhash(img)).bit_count(),"mae":mae(im,img)})
  for prev in selected[fam]:
   checks.append({"against":"selected-"+prev["filename"],"dhash":(dhash(im)^dhash(prev["image"])).bit_count(),"mae":mae(im,prev["image"])})
  near=[c for c in checks if c["dhash"]<=6 or c["mae"]<8]
  metadata.update({"status":"HOLD_SCENE_DIVERSITY" if near else "NEW_DISTINCT_CANDIDATE_QA_ONLY",
   "original_image_size":list(photo.size),"original_bytes_sha256":sha(raw),"new_JPG_sha256":sha(dst.read_bytes()),
   "jpg_file":dst.name,"similarity_alerts":near,"similarity_checks":checks,
   "photo_label_or_package_identity_human_confirmed":False})
  if not near:selected[fam].append({"filename":dst.name,"image":im})
 except Exception as exc:
  metadata.update({"status":"SOURCE_ACCESS_OR_IMAGE_QUALITY_HOLD","error_type":type(exc).__name__})
 results.append(metadata)
assert len(results)==4
report={"version":"v2581","families":["pending-24","pending-25"],
"candidate_urls_attempted":len(cases),
"source_images_saved":len([r for r in results if r.get("jpg_file")]),
"distinct_photo_candidates":sum(r["status"]=="NEW_DISTINCT_CANDIDATE_QA_ONLY" for r in results),
"duplicate_photo_candidates":sum(r["status"]=="HOLD_SCENE_DIVERSITY" for r in results),
"download_or_image_quality_holds":sum(r["status"]=="SOURCE_ACCESS_OR_IMAGE_QUALITY_HOLD" for r in results),
"physical_edition_and_merchant_bundle_verified":False,
"external_photo_commercial_usage_license_verified":False,
"original_round_MK_logo_verified":False,
"sale_ready":False,"existing_156_review_images_recreated":0,
"public_original_55_URLs_changed":0,"spreadsheet_created_or_shared":False,
"candidate_results":results}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:report[k] for k in ["source_images_saved","distinct_photo_candidates","duplicate_photo_candidates","download_or_image_quality_holds"]}))
