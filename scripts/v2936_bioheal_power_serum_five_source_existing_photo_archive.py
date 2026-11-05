#!/usr/bin/env python3
"""v2936 BIOHEAL 30mL serum: join FOUR immutable old 1080 JPG sources and
ONE independently visually reviewed Shopify 1254px native product-only source.
The preview reference is 1080 JPG; native original PNG is preserved in v2935.
QA ONLY. Commercial photo rights / exact physical stock / MK remain unverified.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_STORED
from io import BytesIO
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json,time

Q=Path("qa-review")
D20=Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP"
D35=Q/"v2935-two-new-retailer-exact-SKU-image-native-source-check-QA"
OUT=Q/"v2936-bioheal-serum-five-source-original-byte-QA-not-retail"
assert not OUT.exists(), "v2936 already completed: do not repeat"
s=json.loads((D35/"stock30-incremental-state-v2935.json").read_text(encoding="utf8"))
m35=json.loads((D35/"manifest.json").read_text(encoding="utf8"))
m20=json.loads((D20/"manifest.json").read_text(encoding="utf8"))
assert s["version"]==m35["version"]=="v2935" and len(s["families"])==30
assert m35["new_unlicensed_native_product_refs"]==1 and m35["old_55_verified_public_urls_changed"]==0
fam="pending-24"
old=next(r for r in m20["results"] if r["family"]==fam)
new=next(r for r in m35["results"] if r["family"]==fam)
assert old["actual_original_source_jpgs_in_zip"]==4
assert new["verified_product_name"] and new["new_source_photos"]==1
v=new["photos"][0]
assert v["native"]==[1254,1254] and v["nearest_existing_hamming"]>=6
assert not v["photo_rights_to_reuse"] and not v["retail_approved"]
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def verify_jpeg(b):
 with Image.open(BytesIO(b)) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080) and len(b)<2_000_000
  return ImageOps.exif_transpose(im).convert("RGB")
def check(b,digest):
 assert sha256(b).hexdigest()==digest
 return b
srczip=Path(old["zip_path"])
check(srczip.read_bytes(),old["zip_sha256"])
photos=[]
with ZipFile(srczip,"r") as z:
 assert z.testzip() is None and len(z.namelist())==4
 for i,name in enumerate(z.namelist(),1):
  b=z.read(name)
  photos.append({"i":i,"data":b,"img":verify_jpeg(b),"sha":sha256(b).hexdigest(),
   "origin":str(srczip)+":"+name,"native":[1080,1080]})
native=Path(v["raw_path"]).read_bytes()
check(native,v["sha256"])
with Image.open(BytesIO(native)) as im:
 im.load()
 assert im.format=="PNG" and im.size==(1254,1254)
reference=check(Path(v["preview_path"]).read_bytes(),v["preview_sha256"])
photos.append({"i":5,"data":reference,"img":verify_jpeg(reference),
 "sha":v["preview_sha256"],"origin":v["preview_path"],"native":[1254,1254]})
assert len({x["sha"] for x in photos})==5

OUT.mkdir(parents=True)
zpath=OUT/"BIOHEAL_NAD-PRIZCELL_GlowPowerSerum30mL_5SOURCE_INTERNAL_QA.zip"
with ZipFile(zpath,"w",compression=ZIP_STORED) as z:
 for p in photos:z.writestr(f"{p['i']:02d}-{fam}-SHA-VERIFIED-NOT-RETAIL.jpg",p["data"])
with ZipFile(zpath,"r") as z:
 assert z.testzip() is None and len(z.namelist())==5
 for p in photos:assert z.read(f"{p['i']:02d}-{fam}-SHA-VERIFIED-NOT-RETAIL.jpg")==p["data"]

board=Image.new("RGB",(1080,1080),"#f5f6f7")
draw=ImageDraw.Draw(board)
draw.text((22,13),"BIOHEAL GLOW POWER SERUM 30mL | v2936",font=font(26),fill="#292929")
draw.text((22,51),"5 photo candidates from existing source bytes; commercial reuse HOLD",font=font(16),fill="#9c3030")
for idx,p in enumerate(photos):
 row,col=divmod(idx,3);x=19+col*352;y=99+row*434
 draw.rounded_rectangle((x,y,x+339,y+408),radius=10,fill="white",outline="#ccc",width=2)
 fit=ImageOps.contain(p["img"],(324,334),Image.Resampling.LANCZOS)
 board.paste(fit,(x+169-fit.width//2,y+8+(334-fit.height)//2))
 draw.text((x+12,y+356),f"SOURCE {idx+1} / 5",font=font(18),fill="#252525")
 draw.text((x+12,y+382),"QA ONLY / NOT APPROVED",font=font(12),fill="#a03232")
draw.text((22,1033),"5 source slots filled. Physical edition, rights, MK and sale QA still open.",font=font(15),fill="#555555")
contact=OUT/"BIOHEAL_GlowPower_5source-comparison-INTERNAL.jpg"
board.save(contact,"JPEG",quality=88,optimize=True,subsampling=0)
with Image.open(contact) as im:
 assert im.format=="JPEG" and im.size==(1080,1080)
assert contact.stat().st_size<2_000_000

s["families"][fam].update({
 "last_delta_version":"v2936",
 "release_status":"FIVE_SOURCE_SCENES_SHA_VERIFIED_BUT_RETAIL_RIGHTS_AND_STOCK_HOLD",
 "v2936_five_source_archive":str(zpath),
 "v2936_photo_contact":str(contact),
 "v2936_source_slot_shortfall":0,
 "latest_photo_QA_checkpoint":"v2936 five reference scenes: 4 byte-identical v2920 QA JPG + one new v2935 1254px native Shopify retailer photo, distinct layout, no added model or claims; source bytes verified. Still no commercial photo permission, physical stock generation or genuine MK approval.",
 "sale_approved":False})
report={"version":"v2936","baseline":"v2935","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "family":fam,"archived_photo_source_count":5,"original_JPGs_reused":4,
 "previously_archived_native_1254_PNG_reused":1,
 "new_original_photography_generated":0,"source_slot_shortfall":0,
 "retailer_original_png":v["raw_path"],"retailer_png_sha256":v["sha256"],
 "source_ZIP":str(zpath),"source_ZIP_sha256":sha256(zpath.read_bytes()).hexdigest(),
 "five_reference_contact":str(contact),
 "commercial_photo_permission_verified":False,"physical_KR_stock_generation_verified":False,
 "MK_logo_verified":False,"new_retail_approved_images":0,"new_public_URLs":0,
 "existing_11_published_groups_modified":0,"existing_55_verified_public_URLs_changed":0,
 "previous_QA_asset_files_modified":0,"final_spreadsheet_shared":False,
 "source_references":[{"slot":p["i"],"source":p["origin"],"sha256":p["sha"],
   "native_pixel_dimensions":p["native"],"image_rights_approved":False,"sale_approved":False} for p in photos]}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
s["version"]="v2936";s["baseline"]="v2935";s["new_sales_approvals"]=0;s["new_public_URLs"]=0;s["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2936.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps({"version":"v2936","source_photo_count":5,"new_sales_approvals":0,"remaining_missing_source_photos_across_six_partial_families":6},ensure_ascii=False))
