#!/usr/bin/env python3
"""v2811. Rescue GOODAL pending-21 with photos from a documented SINGLE 30ml
retailer listing, distinct from official 30ml x2 bundle. External photographs
are QA-only reference assets; no Shopee publication or permission implied.
Do not claim 25AD stock edition from the retailer images alone.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from io import BytesIO
import requests,hashlib,json,base64
OUT=Path("qa-review/v2811-goodal-25AD-single-30mL-three-real-source-photos")
assert not OUT.exists()
OUT.mkdir(parents=True)
URLS=[
 "https://media.ktown4u.com/products/resize/thumbnail/2025/12/22/a6wykq.jpeg",
 "https://media.ktown4u.com/products/resize/thumbnail/2025/12/22/tyUqvT.jpeg",
 "https://media.ktown4u.com/products/resize/thumbnail/2025/10/14/oJXK8h.jpg"
]
HEAD={"User-Agent":"Mozilla/5.0 (compatible; ProductImage-QA/1.0)","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"}
def sha(b):return hashlib.sha256(b).hexdigest()
photos=[]
for i,u in enumerate(URLS,1):
 rec={"slot":i,"source_url":u,"status":"HOLD_REVIEW"}
 try:
  resp=requests.get(u,headers=HEAD,timeout=16)
  resp.raise_for_status()
  assert 400<=len(resp.content)<8_000_000
  original=Image.open(BytesIO(resp.content))
  original.load()
  assert min(original.size)>=360
  rgb=ImageOps.exif_transpose(original).convert("RGB")
  sourcebytes=resp.content
  # Save unchanged captured original bytes separately; thumbnails may not be JPEG.
  suffix=".jpg" if original.format=="JPEG" else (".png" if original.format=="PNG" else ".original")
  p=OUT/f"{i:02d}-original-retailer-reference{suffix}"
  p.write_bytes(sourcebytes)
  square=Image.new("RGB",(1080,1080),"#ffffff")
  scaled=ImageOps.contain(rgb,(1050,1050),Image.Resampling.LANCZOS)
  square.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
  jpg=OUT/f"{i:02d}-30mL-single-listing-scene-REVIEW-ONLY.jpg"
  jpgsave={"format":"JPEG","quality":91,"optimize":True,"subsampling":0}
  square.save(jpg,**jpgsave)
  assert jpg.stat().st_size<2_000_000
  rec.update({"status":"SINGLE_ITEM_RETAIL_LISTING_PHOTO_REFERENCE_SAVED",
     "source_dimensions":list(original.size),
     "original_file":p.name,"original_sha256":sha(sourcebytes),
     "qa_1080_jpg":jpg.name,"qa_sha256":sha(jpg.read_bytes())})
 except Exception as exc:
  rec.update({"status":"HOLD_DOWNLOAD_OR_IMAGE_INVALID","reason":str(exc)[:230]})
 photos.append(rec)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
board=Image.new("RGB",(1830,515),"#f0f0ed")
d=ImageDraw.Draw(board)
d.text((17,15),"v2811 GOODAL SINGLE 30mL RETAIL PHOTO CANDIDATES / NOT COMMERCIAL",font=font,fill="#202020")
for i,rec in enumerate(photos):
 x=18+i*602
 if rec.get("qa_1080_jpg"):
  with Image.open(OUT/rec["qa_1080_jpg"]) as im:
   img=im.convert("RGB").resize((460,460),Image.Resampling.LANCZOS)
  board.paste(img,(x,52))
 else:
  d.text((x,100),rec["status"],font=font,fill="#aa4444")
p=OUT/"v2811-source-comparison.jpg"
board.save(p,"JPEG",quality=85,optimize=True)
(OUT/"v2811-contact.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode("ascii"))
report={"version":"v2811","baseline":"v2810","family":"pending-21",
"product":"GOODAL Green Tangerine Vita C Dark Circle Eye Cream 30mL",
"separate_single_30mL_evidence":[
 {"name":"The Shilla Duty Free","page":"https://m.shilladfs.com/estore/kr/ko/p/5754369",
  "sku":"669210000423","edition":"25AD","single_unit":True,"size":"30mL"},
 {"name":"Ktown4u","page":"https://kr.ktown4u.com/iteminfo?goods_no=148768",
  "good_no":148768,"single_unit_listing":True,"size":"30mL",
  "exact_25AD_packaging_in_images_verified":False}
],
"prior_official_brand_bundle":{"page":"https://clubclio.co.kr/shop/goodsView/6606",
 "unit":"30mL + 30mL","not_equivalent_to_single_unit":True},
"newly_saved_photographic_references":sum(bool(r.get("qa_1080_jpg")) for r in photos),
"retail_approval":False,"actual_owned_inventory_edition_confirmed":False,
"photo_republication_rights_verified":False,
"prior_BAD_clipped_tube_image_reused":False,
"unverified_MK_logo_added":False,
"previously_approved_11_families_untouched":True,
"existing_55_published_URLs_untouched":True,
"previous_QA_artifacts_untouched":True,
"final_excel_shared":False,
"photos":photos}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2811","retrieved_reference_jpgs":report["newly_saved_photographic_references"],
 "result":[x["status"] for x in photos],"new_retail_approvals":0}))
