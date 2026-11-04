#!/usr/bin/env python3
"""v2589 Goodal Green Tangerine Vita-C Serum Mist 100ml 25AD:
two real product photos, no invented labels, 100ml verified by Korean stock
retail references. These are rights-hold QA sources, not sales-approved JPGs.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageStat
from urllib.request import Request,urlopen
from io import BytesIO
import hashlib,json
B=Path("v2589-base/review-JPG-by-family/pending-20")
OUT=Path("v2589-goodal-serum-mist-two-source-JPG-QA")
OUT.mkdir(exist_ok=True)
old=sorted(B.glob("*.jpg"))
assert len(old)==5
sources=[
("bottle-front","https://medias.watsons.com.sg/publishing/WTCSG-95021-side-zoom.jpg?version=1759861834"),
("spray-in-action","https://medias.watsons.com.sg/publishing/WTCSG-95021-back-zoom.jpg?version=1759861837")]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dhash(im):
 arr=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 v=0
 for y in range(8):
  for x in range(8):v=(v<<1)|(arr[y*9+x]>arr[y*9+x+1])
 return v
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
oldimages=[Image.open(x).convert("RGB") for x in old]
newimages=[];res=[]
for kind,url in sources:
 row={"scene":kind,"source_url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=18) as response:raw=response.read(7_000_001)
  assert 12000<len(raw)<7_000_000
  src=Image.open(BytesIO(raw));src.load()
  assert src.format in ("JPEG","PNG","WEBP") and min(src.size)>=350
  fit=ImageOps.contain(src.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  im=Image.new("RGB",(1080,1080),"#fafafa")
  im.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  file=OUT/(kind+"-actual-product-QA.jpg")
  im.save(file,"JPEG",quality=90,optimize=True,subsampling=0)
  assert file.stat().st_size<2_000_000 and Image.open(file).size==(1080,1080)
  checks=[{"slot":int(p.name[:2]),"dhash":(dhash(im)^dhash(x)).bit_count(),"MAE":mae(im,x)} for p,x in zip(old,oldimages)]
  checks += [{"slot":"new","dhash":(dhash(im)^dhash(x)).bit_count(),"MAE":mae(im,x)} for x in newimages]
  repeats=[v for v in checks if v["dhash"]<=6 or v["MAE"]<8]
  row.update({"status":"HOLD_NEAR_DUPLICATE" if repeats else "DISTINCT_REAL_PRODUCT_SCENE_QA",
    "file":file.name,"file_sha256":sha(file.read_bytes()),"source_sha256":sha(raw),
    "source_dimension":list(src.size),"old_frame_checks":checks,"near":repeats})
  if not repeats:newimages.append(im)
 except Exception as exc:row.update({"status":"SOURCE_ACCESS_HOLD","error_class":type(exc).__name__})
 row["licensed_for_seller_reuse"]=False
 row["exact_25AD_stock_package_compared"]=False
 row["published"]=False
 res.append(row)
assert len(res)==2
report={"version":"v2589","family":"pending-20",
 "product":"Goodal Green Tangerine Vita-C Serum Mist 100ml 25AD",
 "stock_claim_sources":["https://m.shilladfs.com/estore/kr/ko/p/5777042",
 "https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000706462566"],
 "source_product_page":"https://www.watsons.com.sg/goodal-green-tangerine-vita-c-serum-mist-100ml/p/BP_95021",
 "source_photo_attempts":2,"new_saved_jpg":sum("file" in x for x in res),
 "new_distinct_QA_photos":sum(x["status"]=="DISTINCT_REAL_PRODUCT_SCENE_QA" for x in res),
 "unavailable_or_repeated":sum(x["status"]!="DISTINCT_REAL_PRODUCT_SCENE_QA" for x in res),
 "product_25AD_edition_direct_visual_comparison_complete":False,
 "photo_commercial_reuse_rights_verified":False,
 "old_156_source_JPGs_modified":0,"previous_16_delta_checkpoint_unchanged":True,
 "existing_55_public_URLs_changed":0,"new_public_URLs":0,
 "xlsx_created_or_shared":False,"approved":False,"photos":res}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_saved":report["new_saved_jpg"],"distinct":report["new_distinct_QA_photos"],
"holds":report["unavailable_or_repeated"],"published":False,"xlsx":False}))
