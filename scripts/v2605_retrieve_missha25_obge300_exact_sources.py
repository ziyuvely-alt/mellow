#!/usr/bin/env python3
"""v2605 real exact product reference recovery, no image generation.
Candidate photos only: MISSHA old red-tube No.25 Warm Beige and brand-verified
OBgE Max Waterful 300mL original light-background pump image.
Third-party image rights, exact owned-stock generation NOT VERIFIED.
Previously approved 55 URLs and latest 156 review JPEGs untouched.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image,ImageOps,ImageEnhance
import json,hashlib
OUT=Path("v2605-two-exact-photo-candidates-QA")
OUT.mkdir(exist_ok=True)
SOURCES=[
 {"family":"pending-03","slot":"OPTION25_REFERENCE_ONLY",
  "name":"MISSHA M Perfect Cover BB Cream No.25 Warm Beige",
  "shop":"Kindlife India",
  "source_page":"https://www.kindlife.in/m-perfect-cover-bb-cream-spf42-pa-no.25-warm-beige-50ml/",
  "url":"https://cdn.kindlife.in/images/detailed/116/12013188-2094647897654345_1024x1024.webp?t=1692435542",
  "fallback_url":"https://cdn.yesbee.com/45_8809530064955_20260121154346190.png",
  "requirements":"old burgundy-red tube, NO.25 mark, no PRO or 2026 reformulation"},
 {"family":"pending-22","slot":4,"name":"OBgE Max Waterful Sun Cream 300ml",
  "shop":"OBgE official site",
  "source_page":"https://m.obge.co.kr/product/대용량가성비-맥스-워터풀-선크림-300ml/1251/",
  "url":"https://m.obge.co.kr/web/product/small/202603/95c2bcbeb8bf7bfa5b3d3b055e3a87d9.png",
  "fallback_url":"https://m.obge.co.kr/web/product/medium/202603/e039688781d45789b70ee436c13cf0f6.png",
  "requirements":"single genuine white pump bottle labeled MAX WATERFUL 300mL; no dark halo"}
]
rows=[]
for s in SOURCES:
 row={k:s[k] for k in ("family","slot","name","shop","source_page","requirements")}
 for trial,url in enumerate((s["url"],s["fallback_url"]),1):
  try:
   req=Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,image/*"})
   with urlopen(req,timeout=16) as rr:raw=rr.read(7_000_001)
   assert 12000<len(raw)<7_000_000
   src=Image.open(BytesIO(raw));src.load()
   assert src.format in ("PNG","JPEG","WEBP") and min(src.size)>=300,(src.format,src.size)
   fit=ImageOps.contain(src.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
   # Preserve genuine photographed pixels, no fake graphics or product redraw.
   canvas=Image.new("RGB",(1080,1080),"#f8f8f8")
   canvas.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   out=OUT/(s["family"]+"-exact-source-photo-review.jpg")
   canvas.save(out,"JPEG",quality=93,subsampling=0,optimize=True)
   assert out.stat().st_size<2_000_000
   row.update(status="REAL_PHOTO_DOWNLOADED_REVIEW_ONLY",
    candidate_file=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
    downloaded_url=url,source_dimensions=list(src.size),source_format=src.format,
    jpg_bytes=out.stat().st_size,
    package_label_human_verified=False,
    rights_cleared=False,stock_physical_version_match=False,
    commercial_sale_approved=False)
   break
  except Exception as e:
   row["attempt_"+str(trial)+"_hold"]=type(e).__name__
 else:
  row["status"]="SOURCE_ACCESS_HOLD_NO_NEW_IMAGE"
 rows.append(row)
report={"version":"v2605","source_images_attempted":2,
 "reference_JPGs_captured":sum(x["status"]=="REAL_PHOTO_DOWNLOADED_REVIEW_ONLY" for x in rows),
 "old_156_jpgs_modified":0,"old_11_published_families_modified":0,
 "verified_public_55_urls_modified":0,"xlsx_created_or_shared":False,
 "new_images_are_review_only":True,
 "real_stock_version_and_photo_license_unverified":True,
 "source_items":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"retrieved":report["reference_JPGs_captured"],
 "attempted":2,"product_photos_recreated_from_AI":0,"published":0,"excel":False}))
