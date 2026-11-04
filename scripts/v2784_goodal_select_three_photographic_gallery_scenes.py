#!/usr/bin/env python3
"""v2784 curate ONLY 3 actual physical photographic brand images from the
8 v2783 GOODAL Cream Alpha gallery sources, preserving exact JPG bytes.
Do not count copy-rich efficacy, before/after comparison or other bundled
products as independent product photos. Do not make fake images/swatches.
All photos QA/reference only and not cleared for marketplace use.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,hashlib,base64
BASE=Path("qa-review/v2783-goodal-cream-alpha-official-distinct-photo-sources")
OUT=Path("qa-review/v2784-goodal-cream-alpha-three-distinct-real-photo-only-QA")
assert BASE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
SOURCE=json.loads((BASE/"manifest.json").read_text())
assert SOURCE["status"]=="CANDIDATES_STAGED_FOR_REAL_FRAME_VISUAL_QA"
assert len(SOURCE["new_source_photo_candidates"])>=8
SELECT={
  1:("real single Alpha cream jar with product formulation as background","PHOTOGRAPHIC_JAR_HERO"),
  2:("two open and closed views of same Alpha jar, marketing overlay; NOT a two-pack","PHOTOGRAPHIC_OPEN_JAR_AND_CREAM"),
  7:("cream capsule texture being applied on actual hand, marketing claim caption to review","PHOTOGRAPHIC_HAND_TEXTURE")
}
REJECT={
  3:"Diagram and strong marketing claim: not an independent new product photograph",
  4:"Numerical efficacy claims on skin: require approved clinical source and promotion authorization",
  5:"Before/after human photographs: not appropriate as a product detail hero without rights/claims",
  6:"Text ingredient information card: not a new genuine product photo",
  8:"Multi-product daily routine: could misrepresent single 50mL jar as bundled products"
}
out=[]
for slot,(purpose,role) in SELECT.items():
 srcmeta=SOURCE["new_source_photo_candidates"][slot-1]
 source=BASE/srcmeta["candidate"]
 dest=OUT/f"{len(out)+1:02d}-original-{role}-QA.jpg"
 shutil.copy2(source,dest)
 h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert h(dest)==h(source)
 with Image.open(dest) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
 assert dest.stat().st_size<2000000
 out.append({"slot":len(out)+1,"official_gallery_index":slot,"role":role,"visual_qa_description":purpose,
   "file":dest.name,"sha256":h(dest),"original_photo_sha256":h(source),
   "brand_source_url":srcmeta["official_original_url"],
   "actual_product_edition_50ml_confirmed_against_user_inventory":False,
   "commercial_rights_verified":False,"approved_for_retail":False})
assert len(out)==3 and len(REJECT)==5
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f=ImageFont.truetype(font,20)
canvas=Image.new("RGB",(1260,465),"#f0f0ed")
d=ImageDraw.Draw(canvas)
d.text((18,12),"v2784 GOODAL CREAM ALPHA / REAL BRAND PHOTO PROOFS ONLY / NO RETAIL",font=f,fill="#2c2c2c")
for i,x in enumerate(out):
 with Image.open(OUT/x["file"]) as im:tile=im.convert("RGB").resize((380,380),Image.Resampling.LANCZOS)
 xx=16+i*410
 canvas.paste(tile,(xx,50))
 d.text((xx,432),f"IMAGE {x['slot']} / {x['role'][:22]}",font=f,fill="#292929")
photo=OUT/"v2784-three-selected-physical-photo-proof.jpg"
canvas.save(photo,"JPEG",quality=83,optimize=True)
(OUT/"v2784-photo-proof.b64.txt").write_text(base64.b64encode(photo.read_bytes()).decode())
result={
 "version":"v2784","baseline":"v2783","family":"pending-19",
 "product":"GOODAL Green Tangerine Vita C Dark Spot Care Cream Alpha 50mL",
 "brand_verified_product_gallery":"https://clubclio.shop/products/goodal-green-tangerine-vitamin-c-cream-advanced-ver",
 "previous_qa_blocker":"Only a real single cream hero and mostly generic routine/fact cards; no genuine distinct texture/use source",
 "newly_curated_actual_distinct_source_JPGs":len(out),
 "new_photo_pixels_generated":0,"source_bytes_unchanged_sha_identical":True,
 "source_gallery_images_rejected":REJECT,
 "curated_photos":out,
 "total_customer_ready_five_photo_set_complete":False,
 "open_issues":["Brand-owned gallery is not proof of commercial photo redistribution license",
                "Actual user's physical stock 50mL package generation not independently verified",
                "Original approved MK logo unavailable",
                "Marketing overlay claims not approved for reuse",
                "Full premium 5-distinct-scene final commercial QA not completed"],
 "new_retail_approvals":0,"approved_11_product_families_unchanged":True,
 "published_55_public_URLs_unchanged":True,
 "prior_archived_original_JPGs_unchanged":True,
 "final_spreadsheet_shared":False
}
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2784","original_photos_curated":3,"rejected_non_independent_or_high_claim_images":5,
"no_duplicate_source_download":True,"new_retail_approved":0}))
