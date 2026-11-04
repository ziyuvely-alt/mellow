#!/usr/bin/env python3
"""v2595 genuine Dr.G BRIGHTENING UP SUN+ 50 mL scenes. Reject 35mL and
Moisture Sun; compare only pending-18 in v2593 latest physical review corpus.
Never publish or assert photo rights or owned-stock package proof.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageChops,ImageStat
import json,hashlib
ROOT=Path("latest/review-JPG-by-family/pending-18")
OUT=Path("v2595-drg-brightening-up-sunplus-50ml-new-real-scenes")
OUT.mkdir(exist_ok=True)
previous=sorted(ROOT.glob("*.jpg"))
assert len(previous)==5
sources=[
 {"id":"fifty-tube-white","url":"https://item.elandrs.com/upload/prd/orgimg/016/2302843016_0000001.jpg?h=&q=100&w=750",
  "page":"https://www.elandmall.co.kr/i/item?chnl_no=GSW&itemNo=2302843016",
  "display":"Dr.G Brightening Up Sun+ 50mL white orange tube, original front hero"},
 {"id":"fifty-tube-box","url":"https://gdimg.gmarket.co.kr/2282603044/still/400?ver=1636965526",
  "page":"https://global.gmarket.co.kr/item?goodsCode=2282603044",
  "display":"Dr.G Brightening Up Sun+ 50mL tube and carton"}
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 out=0
 for r in range(8):
  for c in range(8):out=(out<<1)|(p[r*9+c]>p[r*9+c+1])
 return out
def mae(a,b):
 x=a.convert("RGB").resize((128,128));y=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(x,y)).mean)/3,2)
previmgs=[(x,Image.open(x).convert("RGB")) for x in previous]
accepted=[];rows=[]
for s in sources:
 item=dict(s)
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=16) as r:body=r.read(6_000_001)
  assert 12000<len(body)<6_000_000
  orig=Image.open(BytesIO(body));orig.load()
  assert orig.format in ("JPEG","PNG","WEBP") and min(orig.size)>=380
  fit=ImageOps.contain(orig.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"#fcfcfc")
  canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  out=OUT/(s["id"]+"-QA.jpg")
  canvas.save(out,"JPEG",quality=91,optimize=True,subsampling=0)
  assert out.stat().st_size<2_000_000
  scores=[{"other":x.name,"dhash":(dhash(canvas)^dhash(im)).bit_count(),"mae":mae(canvas,im)} for x,im in previmgs]
  scores.extend({"other":"selected-new","dhash":(dhash(canvas)^dhash(x["im"])).bit_count(),"mae":mae(canvas,x["im"])} for x in accepted)
  similar=[x for x in scores if x["dhash"]<=6 or x["mae"]<8]
  item.update(status="HOLD_NEAR_DUPLICATE" if similar else "DISTINCT_REAL_50ML_PHOTO_QA_ONLY",
   saved_file=out.name, "sha256":sha(out), source_dims=list(orig.size),similarity_alerts=similar)
  if not similar:accepted.append({"im":canvas,"file":out})
 except Exception as e:
  item.update(status="ACCESS_HOLD",error_class=type(e).__name__)
 item.update(sales_approved=False,source_license_verified=False,owned_50ml_stock_verified=False)
 rows.append(item)
manifest={"version":"v2595","family":"pending-18","identity":"Dr.G Brightening Up Sun PLUS 50mL, not Brightening Up MOISTURE Sun and not 35mL",
 "sources_attempted":2,"photos_downloaded":sum("saved_file" in x for x in rows),
 "distinct_candidates":len(accepted),"original_five_JPGs_untouched":True,
 "v2593_full_156_JPGs_untouched":True,"existing_public_55_URLs_changed":0,
 "XLSX_created_or_shared":False,"commercial_use_rights_verified":False,
 "actual_owned_stock_label_verified":False,"approved_for_sales":False,"sources":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"downloads":manifest["photos_downloaded"],"unique":len(accepted),
 "failures":2-manifest["photos_downloaded"],"released":False,"excel":False}))
