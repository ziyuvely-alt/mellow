#!/usr/bin/env python3
"""v2438b: remove only residual ring pixels OUTSIDE the rounded info card of two prior edits.
The original card, titles, body copy and photo data are not redrawn.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import hashlib,json
B=Path("baseline-v2438")/"sales-image-drafts"
O=Path("v2438b-output");O.mkdir(exist_ok=True)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entries=[]
for gid in ["pending-02","pending-21"]:
 src=B/gid/(gid+"_clean_legible_card_V2438.jpg")
 assert src.exists()
 before=h(src)
 with Image.open(src) as inp:
  im=inp.convert("RGB")
  # The outside arc remains at x1009..1026, y378..489; the area outside card
  # has a uniform plain background, so paint ONLY x1009+, preserving card pixels.
  color=im.getpixel((1042,450))
  d=ImageDraw.Draw(im)
  d.rectangle((1009,345,1050,545),fill=color)
  dest=O/"sales-image-drafts"/gid/(gid+"_clean_card_no_outer_arc_V2438b.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  im.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as ck:
   ck.load()
   assert ck.format=="JPEG" and ck.size==(1080,1080) and dest.stat().st_size<2000000
  assert h(src)==before
  entries.append({"group_id":gid,"original":str(src),"original_sha256":before,"output":str(dest.relative_to(O)),"sha256":h(dest),"change":"remove residual circle pixels outside card only","state":"SALES_IMAGE_DRAFT","rights_hold":True})
cp={"version":"2.4.38b","revision_count":2,"accepted_provisionally_after_visual_QA":0,"source_files_changed":0,"public_image_paths_changed":0,"FINAL_QA_APPROVED":0,"entries":entries}
(O/"v2438b_checkpoint.json").write_text(json.dumps(cp,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="entries"}),flush=True)
