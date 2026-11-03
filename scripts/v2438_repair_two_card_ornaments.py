#!/usr/bin/env python3
"""v2.4.38: two narrowly scoped actual JPG copy-panel visual fixes.
Only repair overlapping circular ornament on a known flat-colored product-guide panel.
Original visual content, product photos, and all public image URLs are immutable.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
ROOT=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-customer-drafts"
OUT=Path("v2438-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
# These images were directly visually opened: original ornamental circle crosses heading.
jobs=[
("pending-02","INFO_HOWTO_02_V2414B_EN_V2421.jpg",
 ("PRESS + PAT","Pick up product with the puff","Pat gently onto skin")),
("pending-21","INFO_03_V2413_EN_V2421.jpg",
 ("GENTLE EYE CARE","Apply gently around the eye area","Pat until absorbed"))]
results=[]
for gid,name,lines in jobs:
 src=ROOT/gid/name
 assert src.exists(),src
 before=sha(src)
 with Image.open(src) as a:
  a.load();assert a.size==(1080,1080)
  im=a.convert("RGB")
  d=ImageDraw.Draw(im)
  # Original large card is x72..1008 y303..763. Capture original flat fill,
  # replace only this card. Do not touch outside MellowKR layout, titles or dividers.
  inner=im.getpixel((550,325))
  d.rounded_rectangle((72,303,1008,763),radius=40,fill=inner)
  # Recreate headline and supporting instructions with no circle or overrun.
  for text,y,size,bold in [(lines[0],374,65,True),(lines[1],563,38,False),(lines[2],650,36,False)]:
   ft=font(size,bold)
   bb=d.textbbox((0,0),text,font=ft)
   width=bb[2]-bb[0]
   assert width<865,(gid,text,width)
   d.text((540-width//2,y),text,font=ft,fill=(44,65,55))
  dest=OUT/"sales-image-drafts"/gid/(gid+"_clean_legible_card_V2438.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  im.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load()
   assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2000000
  assert sha(src)==before and sha(dest)!=before
  results.append({"group_id":gid,"source":str(src.relative_to(ROOT)),"source_sha256":before,
                  "new_file":str(dest.relative_to(OUT)),"new_sha256":sha(dest),
                  "corrected":"ornament overlapped heading; rebuilt same flat card with readable text",
                  "status":"SALES_IMAGE_DRAFT","rights_verified":False,
                  "actual_stock_verified":False,"visual_QA_after_output":"PENDING"})
cp={"version":"2.4.38","actual_modified_JPG_count":len(results),"groups_modified":len(results),
 "new_original_photograph":0,"commercial_rights_verified":0,"FINAL_QA_APPROVED":0,
 "original_source_files_changed":0,"published_URLs_modified":0,
 "results":results,
 "next":["Visually open both edited customer JPGs; reject if any color/shape mismatch",
         "Check pending-21 exact eye-cream pairing; no final approval before source identity",
         "Continue uninspected customer frames and C8 official swatches without repetition"]}
(OUT/"v2438_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="results"},ensure_ascii=False),flush=True)
