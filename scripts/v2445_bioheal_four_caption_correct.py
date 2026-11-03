#!/usr/bin/env python3
"""v2445 Correct visually confirmed misspelling on four existing BIOHEAL BOH Cream JPEGs.
Only bottom text caption is replaced. Keep untouched genuine product photo,
existing historical 531 originals and every other previously edited JPG intact.
No sales release or image licensing claim.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import hashlib,json,zipfile
BASE=Path("prior-v2444")
OUT=Path("v2445-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((BASE/"v2444_quarantine_and_reuse_manifest.json").read_text())
family=next(x for x in manifest["families"] if x["group_id"]=="pending-25")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(sz):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",sz)
source_records=[]
for row in family["frames"]:
 if row["slot"]==1:continue # existing v2430c corrected; NEVER re-render
 assert row["slot"] in [2,3,4,5]
 p=BASE/row["file"];assert p.exists(),p
 prev=sha(p);assert prev==row["sha256"]
 with Image.open(p) as opened:
  opened.load();assert opened.format=="JPEG" and opened.size==(1080,1080)
  im=opened.convert("RGB")
  d=ImageDraw.Draw(im)
  # The observed text typo is entirely below the original genuine photograph,
  # x approx 70-1010, y 875-910; sample the flat outer background x25,900.
  bg=im.getpixel((25,900))
  d.rectangle((60,862,1020,927),fill=bg)
  line="BIOHEAL BOH NAD-PRIZCELL Glow Boost Cream 50 mL"
  size=34
  while size>=24 and d.textbbox((0,0),line,font=font(size))[2]>940:size-=1
  assert size>=24
  width=d.textbbox((0,0),line,font=font(size))[2]
  d.text(((1080-width)//2,883),line,fill=(45,62,53),font=font(size))
  dst=OUT/"corrected-customer-jpg/pending-25"/(f"slot-{row['slot']:02d}-bioheal-prizcell-name-V2445.jpg")
  dst.parent.mkdir(parents=True,exist_ok=True)
  im.save(dst,"JPEG",quality=94,optimize=True)
  with Image.open(dst) as test:
   test.load();assert test.format=="JPEG" and test.size==(1080,1080) and dst.stat().st_size<2_000_000
  assert sha(p)==prev and sha(dst)!=prev
  source_records.append({"slot":row["slot"],"previous_original_file":row["file"],"previous_sha256":prev,
   "new_corrected_jpg":str(dst.relative_to(OUT)),"new_sha256":sha(dst),
   "corrected_exact_text":line,"visible_qa":"REVIEW_AFTER_OUTPUT",
   "unverified_MK_logo":"REMAINS_PRESENT","commercial_photo_use":"NOT_AUTHORIZED_BY_THIS_EDIT",
   "sale_release_approved":False})
assert len(source_records)==4
report={"version":"2.4.45","source":"production-assets-v2444-reviewed-146-and-quarantine-4",
"product":"BIOHEAL BOH NAD-PRIZCELL Glow Boost Cream 50 mL",
"earlier_corrected_slot1_reused":True,"previous_17_completed_JPGs_rerendered":False,
"new_actual_text_corrections":4,"latest_total_corrected_pending25_frames":5,
"new_product_pixels_generated":False,
"original_historical_JPG_overwritten":0,"prior_55_live_URLs_modified":0,
"sales_release_approved":False,"MK_badge_rights":"UNVERIFIED",
"physical_stock_package":"UNVERIFIED","new_frames":source_records,
"next":"Inspect all 4 JPEGs visually and use corrected exact JPG bytes to replace four older misspelled candidate captions; keep rights hold"}
(OUT/"v2445_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2445_4_corrected_bioheal_jpgs.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
 for row in source_records:z.write(OUT/row["new_corrected_jpg"],arcname=row["new_corrected_jpg"])
 z.write(OUT/"v2445_checkpoint.json",arcname="v2445_checkpoint.json")
with zipfile.ZipFile(OUT/"v2445_4_corrected_bioheal_jpgs.zip") as z:assert len(z.namelist())==5 and z.testzip() is None
print(json.dumps({"version":"2.4.45","new_jpg":len(source_records),"prior_first_frame_reused":True,"final_sale_approved":False},ensure_ascii=False),flush=True)
