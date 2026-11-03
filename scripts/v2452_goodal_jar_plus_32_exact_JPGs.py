#!/usr/bin/env python3
"""v2452 actual substantive production: ONE brand-photo crop for previously uncovered
goodal group pending-19; reuse exact previous PIXELPURE 145mL photo and all past 30 good
JPEGs byte-identically. Two visually rejected CLIO layouts remain quarantined.
No modified original, no regenerated prior JPEG, no spreadsheet creation/sharing.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,shutil,zipfile
A=Path("prior-v2450b")
B=Path("prior-v2451b")
C=Path("prior-v2443")
D=Path("prior-v2427b")
OUT=Path("v2452-output");OUT.mkdir(exist_ok=True)
old=json.loads((A/"v2450b-resumable-checkpoint.json").read_text())
seven=json.loads((B/"v2451b_checkpoint.json").read_text())
pixel=json.loads((C/"v2443_pending26_checkpoint.json").read_text())
assert len(old["files"])==25 and len(seven["files"])==7 and len(pixel["frames"])==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def ensureJPG(p):
 with Image.open(p) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000
rows=[];used=set();hold=[]
def add(g,p,expected,origin,status="PHOTO_RIGHTS_AND_STOCK_QA_HOLD",out_group="reviewable-source-JPGs"):
 assert p.is_file() and sha(p)==expected
 ensureJPG(p)
 unique=(g,expected)
 assert unique not in used,unique
 used.add(unique)
 dst=OUT/out_group/g/(origin+"__"+p.name)
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
 assert sha(dst)==expected
 row={"group_id":g,"file":str(dst.relative_to(OUT)),"SHA256":expected,
      "source":origin,"status":status,"original_photos_license_verified":False,
      "exact_stock_package_verified":False,"all_5_or_6_photos_QA_complete":False,
      "approved_for_sales":False}
 (hold if out_group.startswith("quarantine") else rows).append(row)
# Previously success-checksummed 25 JPGs: no photo re-render.
for x in old["files"]:
 add(x["group_id"],A/x["file"],x["SHA256"],"v2450b-byte-identical",x["hold"])
# Five direct-visual-QA acceptable source-photo frames; two crop failures isolated.
rejected={"pending-06":"Crop leaves unnatural isolated narrow image, requires other verified source",
          "pending-07":"Source promo/packaging border remains visible on right"}
for x in seven["files"]:
 gid=x["group_id"]
 if gid in rejected:
  add(gid,B/x["file"],x["SHA256"],"v2451b-rejected-for-design-QA",rejected[gid],"quarantine-two-layout-holds")
 else:
  add(gid,B/x["file"],x["SHA256"],"v2451b-byte-identical", "EXACT_EDITION_AND_PHOTO_RIGHTS_HOLD")
# PIXELPURE exact earlier 145mL package photo (third photographic frame), byte identical.
pix=next(x for x in pixel["frames"] if "PHOTO_OFFICIAL_145ML" in x["path"])
add("pending-26",C/pix["path"],pix["sha256"],"v2443-reused-original-photo",
    "145ML_PRODUCT_IMAGE_RIGHTS_AND_STOCK_GENERATION_HOLD")
# Goodal group 19: one actual new photographic card based on previously verified real jar
# visible in earlier hero, not inventing a package, not reproducing prior text card.
source=(D/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-hero-fixed/pending-19/01_HERO_EN_V2422.jpg")
assert source.is_file()
originalSHA=sha(source)
with Image.open(source) as oldimage:
 oldimage.load();assert oldimage.size==(1080,1080)
 cropped=oldimage.convert("RGB").crop((192,175,889,849))
 p=ImageOps.contain(cropped,(820,635),Image.Resampling.LANCZOS)
 im=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(im);ink=(42,64,56)
 d.text((68,52),"goodal",font=font(38,True),fill=ink)
 t="Green Tangerine Vita C Cream Alpha"
 sz=43
 while sz>=25 and d.textbbox((0,0),t,font=font(sz,True))[2]>945:sz-=1
 assert sz>=25
 d.text((68,116),t,font=font(sz,True),fill=ink)
 d.line((68,190,1012,190),fill=(179,189,183),width=2)
 im.paste(p,((1080-p.width)//2,226+(635-p.height)//2))
 d.line((68,908,1012,908),fill=(179,189,183),width=2)
 d.text((68,935),"Original Jar Detail",font=font(34,True),fill=ink)
 d.text((68,990),"50 mL",font=font(29),fill=ink)
 dest=OUT/"new-actual-photo-JPGs/pending-19/pending-19_goodal_actual_jar_detail_V2452.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 im.save(dest,"JPEG",quality=94,optimize=True)
ensureJPG(dest)
assert sha(source)==originalSHA
add("pending-19",dest,sha(dest),"v2452-genuine-photo-crop-only",
    "GOODAL_50ML_GENERATION_AND_COMMERCIAL_PHOTO_RIGHTS_HOLD")
assert len(rows)==32,(len(rows),[x["group_id"] for x in rows])
assert len(hold)==2 and len(set(x["group_id"] for x in rows))==25
remaining=sorted(set(f"pending-{i:02d}" for i in range(1,31))-set(x["group_id"] for x in rows))
assert remaining==["pending-01","pending-06","pending-07","pending-08","pending-22"],remaining
report={"version":"2.4.52",
"previous_sha_verified":"production-assets-v2450b-25-image-candidate-checkpoint",
"previous_new_seven":"production-assets-v2451b-seven-photo-QA-revised",
"new_photo_pixels_rendered_only_for_group":"pending-19",
"actually_new_photographic_layout_JPGs":1,
"already_completed_JPGs_copied_byte_identical":31,
"reviewable_JPGs":32,"reviewable_product_families":25,
"two_unacceptable_CLIO_detail_layouts_isolated":2,
"groups_missing_a_non-rejected_photographic_candidate":remaining,
"all_JPG_source_bytes_SHA_verified":True,
"real_531_original_JPGs_unchanged":True,"published_55_URLs_unchanged":True,
"MK_logo_original_binary_recovered":False,"commercial_photo_permissions_verified":0,
"physical_stock_exact_generation_verified":0,"official_shade_charts_final_approved":0,
"FINAL_SALES_APPROVED":0,
"NO_XLSX_OR_SPREADSHEET_SHARED":True,
"product_swatch_and_photo_holds":{
"pending-01":"Old hero explicitly includes excluded shade 21; hold for authorized actual stock photo",
"pending-06":"CLIO Mesh Glow special set source includes retailer promo stickers; best accurate full product generation unverified",
"pending-07":"CLIO Mesh Blur same-generation clean product photo unavailable from safe source",
"pending-08":"Peripera 01..20 exact-generation 04/06/07 swatches and photo rights unresolved",
"pending-22":"OBgE MAX Waterful 300mL pump product source badly blurred and shows unverified logo"
},
"new_photo_source":{"path":str(source),"sha256":originalSHA,"crop_xyxy":[192,175,889,849]},
"reviewable_files":rows,"rejected_images":hold,
"next":["Open newly rendered pending-19 jar photo, reject if original photograph distorted",
"Check exact shade/edition for 5 remaining product groups, never fake color chart",
"30 groups still require full sets, commercial photo rights, original MK logo, and stock generation evidence before selling",
"Do not share any spreadsheet until project truly complete"]
}
(OUT/"v2452-resumable-checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
for filename,items in [("v2452_32_actual_JPG_review_candidates.zip",rows),("v2452_two_CLIO_layout_holds.zip",hold)]:
 with zipfile.ZipFile(OUT/filename,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for r in items:z.write(OUT/r["file"],arcname=r["file"])
  z.write(OUT/"v2452-resumable-checkpoint.json",arcname="v2452-resumable-checkpoint.json")
 with zipfile.ZipFile(OUT/filename) as z:assert z.testzip() is None and len(z.namelist())==len(items)+1
print(json.dumps({"version":"2.4.52","original_new_JPGs":1,"copied_prior_JPGs":31,
"reviewable_JPGs":32,"families":25,"layout_holds":2,"missing_families":remaining,
"spreadsheet_shared":False}),flush=True)
