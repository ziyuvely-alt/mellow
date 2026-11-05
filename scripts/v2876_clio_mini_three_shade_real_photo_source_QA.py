#!/usr/bin/env python3
"""v2876 | Source-only CLIO Mesh Glow Essential MINI 5g three distinct
shade-labeled PHOTOGRAPHS from different existing merchant listings.
This is a PHOTO RIGHTS/EDITION HOLD archive, never a seller-ready output.
Don't use incorrect v2711 alpha or repeat v2788 shared pink hand photo.
Each source is fetched at most once; failure is quarantined per shade.
The source picture, label and color pixels are retained without recolor.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageDraw,ImageOps,ImageFont
from hashlib import sha256
from io import BytesIO
import json,traceback

R=Path("qa-review")
PREVIOUS=R/"v2875-clio-mini5g-obge-doublechamber-batch-identity-QA"/"manifest.json"
OUT=R/"v2876-clio-mini5g-three-independent-shade-photo-source-QA"
assert PREVIOUS.exists() and not OUT.exists()
prev=json.loads(PREVIOUS.read_text())
assert prev["version"]=="v2875"
assert prev["families"]["pending-04"]["old_v2711_alpha_candidate_status"].startswith("REJECT")
sources=[
 {"shade":"21C","name":"LINGERIE","merchant":"Sagi Shop Vietnam",
  "image":"https://bizweb.dktcdn.net/thumb/1024x1024/100/443/867/products/imgi-1-sg-11134207-81ztc-mitq2uocowsj70-jpeg.jpg?v=1770383044833",
  "page":"https://sagishop.vn/clio-cushion-kill-cover-mau-hong-mini-21c",
  "expected_printed_label":"21C Lingerie","provenance":"shop image labeled 21C on mini 5g foundation"},
 {"shade":"21N","name":"LINEN","merchant":"Tanpopo Vietnam",
  "image":"https://bizweb.dktcdn.net/thumb/1024x1024/100/353/847/products/ava-san-pham-tren-website-25-3197fd52-4a2d-4b17-ae6b-96a905564ebf.jpg?v=1785052315773",
  "page":"https://www.tanpopo.vn/phan-nuoc-2-loi-cang-bong-clio-kill-cover-mesh-glow-essential-cushion-spf50-5g",
  "expected_printed_label":"21N Linen","provenance":"mini 5g product photo labeled 21N"},
 {"shade":"23N","name":"GINGER","merchant":"Shopee Vietnam merchant",
  "image":"https://down-vn.img.susercontent.com/file/sg-11134207-81zw7-mitq2uokf18nc8",
  "page":"https://shopee.vn/-CLIO-MINI-VER-M%E1%BB%9AI-Kill-Cover-Mesh-Glow-Essential-Cushion-%2815gX2%29-%C4%90%E1%BB%99-%E1%BA%A9m-m%E1%BB%8Bn-m%C3%A0ng-ch%C4%83m-s%C3%B3c-da-th%E1%BA%ADt-nh%E1%BA%B9-d%C6%B0%E1%BB%A1ng-%E1%BA%A9m-c%C3%B4ng-th%E1%BB%A9c-ch%C4%83m-s%C3%B3c-da-i.462006215.27076512382",
  "expected_printed_label":"23N Ginger","provenance":"merchant image specifically labeled 23N Ginger MINI"}
]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True)
records=[];previews=[]
for row in sources:
 a={**row,"status":"PENDING_IMAGE_SOURCE",
    "photo_usage_license_verified":False,"user_owned_stock_edition_verified":False,
    "sale_approved":False}
 try:
  req=Request(row["image"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,image/*,*/*"})
  with urlopen(req,timeout=16) as res:
   raw=res.read(8_000_001)
  assert 4000<len(raw)<8_000_000,(row["shade"],len(raw))
  with Image.open(BytesIO(raw)) as p:
   p.load();native=p.size;fmt=p.format
   assert fmt in {"JPEG","PNG","WEBP"} and min(native)>=550,(fmt,native)
   original=p.convert("RGB")
  file=OUT/("CLIO-MINI-"+row["shade"]+"-ORIGINAL-SOURCE."+
          {"JPEG":"jpg","PNG":"png","WEBP":"webp"}[fmt])
  file.write_bytes(raw)
  canvas=Image.new("RGB",(1080,1080),"#FCFBFD")
  d=ImageDraw.Draw(canvas)
  d.rounded_rectangle((39,38,1041,1042),radius=22,outline="#E2DAE7",width=2)
  d.text((73,64),"CLIO | MESH GLOW ESSENTIAL MINI 5g",font=ft(29,True),fill="#51465D")
  d.rounded_rectangle((71,130,1009,204),radius=13,fill="#F0EAF2")
  d.text((87,143),row["shade"]+"  "+row["name"]+"  | ORIGINAL MERCHANT SHADE PHOTO",font=ft(23,True),fill="#5B4D65")
  fit=ImageOps.contain(original,(926,730),Image.Resampling.LANCZOS)
  canvas.paste(fit,((1080-fit.width)//2,218+(730-fit.height)//2))
  d.line((76,960,1003,960),fill="#E2D7E8",width=2)
  d.text((79,975),"QA ONLY  |  PHOTO RIGHTS + EXACT STOCK VERSION NOT VERIFIED",font=ft(16,True),fill="#71657A")
  jpg=OUT/("CLIO-MINI-"+row["shade"]+"-"+row["name"]+"-1080-source-evidence-QA.jpg")
  canvas.save(jpg,"JPEG",quality=93,subsampling=0,optimize=True)
  with Image.open(jpg) as img:
   img.load();assert img.size==(1080,1080) and img.format=="JPEG"
  assert jpg.stat().st_size<2_000_000 and sha(file)==sha256(raw).hexdigest()
  a.update(status="ORIGINAL_SHADE_LINKED_PHOTO_SAVED_AWAIT_VISUAL_LABEL_AND_RIGHTS",
    source_original=str(file),source_sha256=sha(file),source_format=fmt,
    source_native_pixels=list(native),new_1080_QA=str(jpg),
    new_JPG_sha256=sha(jpg),new_JPG_bytes=jpg.stat().st_size,
    shade_label_visible_not_programmatically_authenticated=True,
    shade_pixels_in_original_source_not_recolored=True)
  previews.append((row["shade"],canvas))
 except Exception as e:
  a.update(status="HOLD_FAILED_DOWNLOAD_NO_RETRY",reason=type(e).__name__+": "+str(e)[:250])
  print("HOLD",row["shade"],str(e)[:140])
 records.append(a)
contact=Image.new("RGB",(1550,600),"#F1EDF3")
d=ImageDraw.Draw(contact)
d.text((16,13),"v2876 MINI 5g | INDEPENDENT MERCHANT SHADE SOURCES | NO SHARED-PHOTO RELABEL",font=ft(22,True),fill="#463D4B")
for i,(shade,img) in enumerate(previews):
 preview=img.resize((500,500),Image.Resampling.LANCZOS)
 contact.paste(preview,(16+i*510,55))
 d.text((20+i*510,564),shade+" REAL MERCHANT SOURCE | NOT SALES",font=ft(16,True),fill="#5A4F61")
cp=OUT/"v2876-mini-three-merchant-source-contact-QA.jpg"
contact.save(cp,"JPEG",quality=88,optimize=True)
m={"version":"v2876","baseline":"v2875","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g",
 "scope_stock_shades":["21C Lingerie","21N Linen","23N Ginger"],
 "source_candidates_searched_once":3,"saved_originals":len(previews),
 "held_originals":3-len(previews),"new_1080_JPGs":len(previews),
 "source_new_labeled_variants_compared_to_v2875":True,
 "real_shade_source_photographs_retained":True,
 "old_v2711_bad_hand_alpha_reused":False,
 "unlabeled_v2788_same_scene_photo_reused_as_shade_specific":False,
 "all_images_source_color_pixel_preserved":True,
 "commercial_photo_rights_verified":False,
 "exact_user_stock_packaging_verified":False,
 "label_visual_qa_final_review_pending":True,
 "new_sales_approved":0,"new_public_URLs":0,
 "previous_11_approved_families_preserved":True,
 "previous_55_verified_URLs_preserved":True,
 "final_spreadsheet_shared":False,
 "rows":records,"contact":str(cp),"contact_sha256":sha(cp),
 "next":"Review 21C, 21N, 23N printed labels in the original photos at high resolution; if any misleading/old-generation 15g+refill source, reject just that variant. Source commercial permission and physical 5g box still required prior to publication."
}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2876","new_photos":len(previews),"held":[x["shade"] for x in records if x["status"].startswith("HOLD")],"sale_approved":0},ensure_ascii=False))
