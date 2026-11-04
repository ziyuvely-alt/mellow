#!/usr/bin/env python3
"""v2577: only the FIVE changed product-family review boards, no 30-family redo.
Uses saved product images, latest five delta JPGs, retains actual image pixels;
does not sign off rights, stock edition, logo or public release.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
from collections import defaultdict
import hashlib,json
B=Path("v2577-base/review-JPG-by-family")
D=Path("v2577-delta")
OUT=Path("v2577-five-change-only-visual-review");OUT.mkdir(exist_ok=True)
manifest=json.loads((D/"manifest.json").read_text())
assert manifest["version"]=="v2576" and len(manifest["new_image_deltas"])==5
delta={(r["family"],r["slot"]):r for r in manifest["new_image_deltas"]}
F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
Small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
families=sorted({f for f,s in delta})
assert len(families)==5
records=[]
for family in families:
 photos=sorted((B/family).glob("*.jpg"))
 assert len(photos) in (5,6)
 board=Image.new("RGB",(1680,1260),"#f5f5f3")
 d=ImageDraw.Draw(board)
 d.text((38,20),family+" | REVIEW OF ONE CORRECTED CUSTOMER-IMAGE FRAME",font=F,fill="#2b4034")
 d.text((40,64),"Unchanged scenes shown for context. New footer text is NOT product/rights approval.",font=Small,fill="#555d57")
 changed_count=0
 for i,p in enumerate(photos):
  s=int(p.name[:2]);key=(family,s)
  candidate=D/delta[key]["new_file"] if key in delta else p
  if key in delta:
   changed_count+=1
   assert hashlib.sha256(candidate.read_bytes()).hexdigest()==delta[key]["new_sha256"]
  im=Image.open(candidate);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
  # Intentionally no product image content replaced.
  thumb=ImageOps.contain(im.convert("RGB"),(500,480))
  col=i%3;row=i//3;x=col*550+(550-thumb.width)//2
  y=row*567+101+(480-thumb.height)//2
  board.paste(thumb,(x,y))
  label=f"SLOT {s:02d}   "+("NEW COPY-CORRECTED QA CANDIDATE" if key in delta else "PRESERVED SOURCE")
  d.text((35+col*550,591+row*567),label,font=Small,fill="#3e604d")
 assert changed_count==1
 d.text((40,1220),"HOLD: Commercial photo rights / matching actual stock / authentic MK logo / manual content review",font=Small,fill="#6d665b")
 dst=OUT/(family+"-all-scenes-with-one-latest-copy-fix.jpg")
 board.save(dst,"JPEG",quality=85,optimize=True)
 assert Image.open(dst).size==(1680,1260)
 records.append({"family":family,"review_board":dst.name,"existing_scenes_shown":len(photos),
 "newly_corrected_frame_count":1,"older_source_bytes_modified":0,
 "approval":"HOLD_RIGHTS_STOCK_LOGO_HUMAN_QA"})
assert len(records)==5
summary={"version":"v2577","source_review_run":41753618979,
"source_five_delta_run":41761227478,
"family_review_boards_new":5,"source_scene_images_reused":sum(x["existing_scenes_shown"] for x in records),
"new_customer_scene_images_rendered":0,"review_boards_not_selling_images":True,
"unchanged_25_family_review_boards_not_recreated":True,
"old_55_public_urls_changed":0,"xlsx_created_or_shared":False,
"final_product_rights_release_approved":False,"products":records}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"changed_family_review_boards":len(records),
"existing_image_scenes_reused":summary["source_scene_images_reused"],
"unchanged_family_review_boards_regenerated":0,"public_url_changes":0,"xls":False}))
