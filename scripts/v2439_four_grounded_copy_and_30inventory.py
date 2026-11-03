#!/usr/bin/env python3
"""v2439 fact-grounded four real customer JPG edits plus all 30 families source inventory.
No false full visual QA, publication, original overwrite, artificial color chart or invented logo.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import defaultdict
import csv, hashlib, json, datetime
ROOT=Path("baseline-v2427b")
SRC=ROOT/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422"
OUT=Path("v2439-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
jobs=[
 {"id":"pending-05","filename":"INFO_05_V2413_EN_V2421.jpg",
  "header":"SET INFORMATION","lines":["MAIN + REFILL","Kill Cover Founwear Cushion","Cushion compact + refill"],
  "reason":"Original image says generic CLIO Kill Cover cushion twice instead of exact Founwear product","url":"https://clubclio.co.kr/shop/goodsList/120701000000000"},
 {"id":"pending-07","filename":"INFO_05_V2413_EN_V2421.jpg",
  "header":"PRODUCT INFORMATION","lines":["15 g CUSHION","Kill Cover Mesh Blur","Mesh Blur Cushion compact"],
  "reason":"Original 15 g cushion heading overlaps decorative ring; remove ring and preserve original product info","url":"https://clubclio.co.kr/shop/goodsList/120701000000000"},
 {"id":"pending-17","filename":"INFO_05_V2413_EN_V2421.jpg",
  "header":"NET CONTENT","lines":["50 mL","Brightening Up Moisture Sun","Single product"],
  "reason":"Original contains twice the same product name, wasting customer information space","url":None},
 {"id":"pending-19","filename":"INFO_VOLUME_03_V2414_EN_V2421.jpg",
  "header":"NET CONTENT","lines":["50 mL","Goodal Vita C Cream Alpha","Single product"],
  "reason":"Unverified 25AD generation claim in original, removed without asserting a different edition","url":None}
]
reviews=[]
for job in jobs:
 p=SRC/"en-customer-drafts"/job["id"]/job["filename"]
 assert p.is_file(),p
 before=sha(p)
 with Image.open(p) as original:
  original.load();assert original.size==(1080,1080) and original.format=="JPEG"
  im=original.convert("RGB")
  # Keep original MellowKR title and upper/lower lines untouched; redo precisely the
  # text-only center card. Sample card fill and surrounding background from existing actual JPG.
  background=im.getpixel((30,540))
  panel=im.getpixel((530,325))
  d=ImageDraw.Draw(im)
  d.rectangle((67,296,1045,774),fill=background)
  d.rounded_rectangle((72,303,1008,763),radius=39,fill=panel)
  lines=job["lines"]
  for s,y,initial,bold in [(lines[0],378,65,True),(lines[1],565,39,False),(lines[2],651,35,False)]:
   size=initial
   while size>=22 and (d.textbbox((0,0),s,font=font(size,bold))[2])>840: size-=1
   assert size>=22,(job["id"],s)
   ft=font(size,bold); bb=d.textbbox((0,0),s,font=ft)
   width=bb[2]-bb[0]
   d.text((540-width//2,y),s,font=ft,fill=(42,62,53))
  dst=OUT/"sales-image-drafts"/job["id"]/(job["id"]+"_fact_copy_and_card_revised_V2439.jpg")
  dst.parent.mkdir(parents=True,exist_ok=True)
  im.save(dst,"JPEG",quality=94,optimize=True)
  with Image.open(dst) as ck:
   ck.load()
   assert ck.format=="JPEG" and ck.size==(1080,1080) and dst.stat().st_size<2_000_000
  assert sha(p)==before and sha(dst)!=before
  reviews.append({"group_id":job["id"],"previous":str(p.relative_to(ROOT)),"previous_sha256":before,
                  "edited_jpg":str(dst.relative_to(OUT)),"edited_sha256":sha(dst),
                  "cause":job["reason"],"reference":job["url"],"status":"SALES_IMAGE_DRAFT",
                  "after_render_visual_review":"PENDING","photo_reuse_authorization":"UNVERIFIED",
                  "physical_stock":"UNVERIFIED"})
allsource=sorted(ROOT.rglob("*.jpg"))
# Hash each source, and preserve strict count and all 30 group IDs. No copied existing photo counted as new.
before_hash={str(p.relative_to(ROOT)):sha(p) for p in allsource}
ids=[f"pending-{n:02d}" for n in range(1,31)]
inventory=[]
for gid in ids:
 paths=sorted([p for p in allsource if f"/{gid}/" in str(p)])
 with_frame=[]
 for p in paths:
  with Image.open(p) as im:
   im.load()
   with_frame.append({"source":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,
                      "sha256":before_hash[str(p.relative_to(ROOT))],
                      "actual_jpg":im.format=="JPEG","dimensions":[im.width,im.height],
                      "meets_1080_under_2mb":im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000})
 inventory.append({"group_id":gid,"source_frame_count":len(with_frame),"source_frames":with_frame,
                   "independent_manual_visual_QA_complete":False,
                   "official_stock_and_rights_approved":False,
                   "new_edit_file":next((x["edited_jpg"] for x in reviews if x["group_id"]==gid),None)})
# previously reported 531 JPGs were across entire archive, not just this narrowly selected preserved-v2422 folder.
total_jpg_archive=list(ROOT.rglob("*.jpg"))
assert len(total_jpg_archive)>=531,len(total_jpg_archive)
assert before_hash=={str(p.relative_to(ROOT)):sha(p) for p in allsource}
(O:=OUT/"source_inventory_30groups.json").write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
with (OUT/"source_SHA256_index.csv").open("w",encoding="utf-8",newline="") as fh:
 wr=csv.writer(fh);wr.writerow(["relative_path","SHA256"])
 for path,digest in sorted(before_hash.items()):wr.writerow([path,digest])
check={"version":"2.4.39","baseline":"production-assets-v2438c-consolidated-checkpoint",
 "groups_in_source_inventory":30,"historical_source_JPG_checked":len(allsource),
 "groups_with_no_source_JPG":[x["group_id"] for x in inventory if x["source_frame_count"]==0],
 "new_real_customer_JPG_drafts":len(reviews),"groups_with_new_edits":len(reviews),
 "photos_fabricated":0,"official_color_charts_new":0,"rights_confirmed":0,
 "complete_sets_approved":0,"FINAL_QA_APPROVED":0,"published_55_URLs_changed":0,
 "historical_JPG_sha256_unchanged":True,"manual_full_visual_QA_completed":False,
 "edits":reviews,"next":["Open each of four actual edits and reject geometry/text defects",
 "Verify exact pending-19 25AD generation externally, keep removed until proven",
 "Verify exact pending-05 Founwear kit generation and original shade photos",
 "Continue remaining 30-group individual source-frame QA without repeat contact sheets",
 "Recover MK PNG binary and photo reuse rights, never publish drafts before permission"]}
(OUT/"v2439_checkpoint.json").write_text(json.dumps(check,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in check.items() if k not in ["edits","next"]},ensure_ascii=False),flush=True)
