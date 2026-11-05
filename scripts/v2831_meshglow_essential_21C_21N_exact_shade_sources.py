#!/usr/bin/env python3
"""v2831: add two previously missing *exact shade-labelled* photo REFERENCES,
CLIO MESH GLOW ESSENTIAL Mini 5g, not Founwear The Original Mini.

No customer-review photos, no generative swatches, no invented packaging, no
reuse of other product line. This is licensed/stock-generation HOLD material;
original 11 approved groups and 55 URLs are immutable.
"""
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
from urllib.parse import urlparse
import hashlib,json,base64,requests

OUT=Path("qa-review/v2831-clio-mesh-glow-essential-mini-21C-21N-exact-shade-reference")
assert not OUT.exists()
OUT.mkdir(parents=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
SOURCES=[
 {"shade":"21C","label":"Lingerie",
  "merchant":"SagiShop Viet Nam",
  "product_page":"https://sagishop.vn/clio-cushion-kill-cover-mau-hong-mini-21c",
  "original_image_url":"https://bizweb.dktcdn.net/thumb/1024x1024/100/443/867/products/imgi-1-sg-11134207-81ztc-mitq2uocowsj70-jpeg.jpg?v=1770383044833"},
 {"shade":"21N","label":"Linen",
  "merchant":"Tanpopo Viet Nam",
  "product_page":"https://www.tanpopo.vn/phan-nuoc-2-loi-cang-bong-clio-kill-cover-mesh-glow-essential-cushion-spf50-5g",
  "original_image_url":"https://bizweb.dktcdn.net/thumb/1024x1024/100/353/847/products/ava-san-pham-tren-website-25-3197fd52-4a2d-4b17-ae6b-96a905564ebf.jpg?v=1785052315773"}
]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for s in SOURCES:
 r={**s,"family":"pending-04","photo_license":"UNVERIFIED","owned_stock_generation":"UNVERIFIED",
    "source_type":"MERCHANT_VARIANT_LABELLED_REFERENCE_NOT_AUTHORIZED_REPUBLICATION",
    "status":"HOLD_SOURCE_ACCESS_OR_SHADE_VERIFICATION"}
 try:
  assert urlparse(s["original_image_url"]).hostname=="bizweb.dktcdn.net"
  resp=requests.get(s["original_image_url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"},timeout=22)
  resp.raise_for_status()
  assert len(resp.content)<7_500_000
  im=Image.open(BytesIO(resp.content));im.load()
  original_dims=list(im.size)
  assert min(im.size)>=450,(s["shade"],im.size)
  img=ImageOps.exif_transpose(im).convert("RGB")
  image=Image.new("RGB",(1080,1080),"white")
  fitted=ImageOps.contain(img,(1080,1080),Image.Resampling.LANCZOS)
  image.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
  photo_file=OUT/f'{s["shade"]}-{s["label"]}-source-variant-labelled-photo-QA.jpg'
  image.save(photo_file,"JPEG",quality=92,optimize=True,subsampling=0)
  assert photo_file.stat().st_size<2_000_000
  with Image.open(photo_file) as check:
   check.load();assert check.format=="JPEG" and check.size==(1080,1080)
  r.update({"status":"VARIANT_LABELLED_REFERENCE_SAVED_VISUAL_QA_PENDING",
            "photo_file":photo_file.name,
            "original_dimensions":original_dims,
            "stored_sha256":digest(photo_file),
            "bytes":photo_file.stat().st_size,
            "original_source_reencoded_for_1080":True,
            "not_background_removed":True,
            "new_retail_approved":False})
 except Exception as e:
  r.update({"status":"HOLD_SOURCE_PHOTO_DOWNLOAD_OR_SIZE_FAILED","error":str(e)[:270]})
 rows.append(r)
assert len(rows)==2
board=Image.new("RGB",(1520,890),"#f3f1ef")
d=ImageDraw.Draw(board)
d.text((22,18),"v2831 | CLIO MESH GLOW ESSENTIAL MINI 5g | 21C / 21N",font=font(25,True),fill="#252525")
d.text((22,57),"Shade-labelled merchant reference only: NO publishing permission / NO stock sign-off",font=font(19),fill="#584d51")
for idx,r in enumerate(rows):
 x=30+idx*760
 if r.get("photo_file"):
  with Image.open(OUT/r["photo_file"]) as im:
   pic=im.convert("RGB").resize((685,685),Image.Resampling.LANCZOS)
  board.paste(pic,(x,118))
 d.text((x,811),f"{r['shade']} {r['label']} / {r['merchant']}",font=font(20,True),fill="#272727")
 d.text((x,839),r["status"][:42],font=font(17),fill="#585858")
proof=OUT/"v2831-21C-21N-shade-reference-contact.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2831-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2831","baseline":"v2830","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion MINI 5g",
 "source_21C_21N_only":True,"different_line_Founwear_Original_Mini_source_used":False,
 "new_shade_labelled_reference_photos_saved":sum(bool(x.get("photo_file")) for x in rows),
 "unique_shade_source_photo_shas":len(set(x["stored_sha256"] for x in rows if x.get("stored_sha256"))),
 "actual_owned_stock_and_shade_labels_verified":False,
 "photo_commercial_reuse_rights_verified":False,
 "customer_review_source_reused":False,
 "original_MK_logo_authenticated":False,
 "existing_v2830_five_JPG_QA_set_untouched":True,
 "prior_11_approved_families_untouched":True,
 "prior_55_published_URLs_untouched":True,
 "new_retail_approvals":0,"final_xlsx_shared":False,
 "status":"SHADE_LABELLED_REFERENCE_PHOTOS_QA_NOT_LICENSED",
 "candidates":rows,
 "next":"Manual visually confirm shade label printed in each JPG and actual item 5g edition; do not use as seller image without photo rights"
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2831","actual_photo_references":manifest["new_shade_labelled_reference_photos_saved"],"statuses":[x["status"] for x in rows],"approved_for_sale":0}))
