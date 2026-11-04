#!/usr/bin/env python3
"""v2562 QA-only replacements for two remaining near-duplicate frame05 cards.
Use only existing same-SKU saved source pixels in fresh editorial compositions.
No generated shade chips, no altered packaging, no original public image edits.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
import hashlib,json
B=Path("v2562-baseline/review-JPG-by-family")
O=Path("v2562-two-sku-specific-slot05-alternatives");O.mkdir(exist_ok=True)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
specs=[
 {"family":"pending-01","title":"MISSHA","subtitle":"MAGIC CUSHION COVER LASTING",
  "body":"CUSHION APPLICATION","slots":[1,4],
  "steps":["01  PRESS THE PUFF","02  PAT GENTLY","03  FOLLOW PRODUCT LABEL"],
  "line":"COVER LASTING | STOCK SHADES 21 / 23 / 25 / 27",
  "panel":"#f9f3f6","accent":"#a56b84",
  "source_edition":"MAGIC CUSHION COVER LASTING, NOT MOIST UP OR PRO"},
 {"family":"pending-06","title":"CLIO","subtitle":"KILL COVER MESH GLOW ESSENTIAL",
  "body":"CUSHION SET GUIDE","slots":[2,4],
  "steps":["01  CHECK YOUR SET","02  APPLY WITH A PUFF","03  FOLLOW PACKAGE LABEL"],
  "line":"MESH GLOW | 19C 19N 21C 21N 23N",
  "panel":"#f6f7f6","accent":"#697f6f",
  "source_edition":"MESH GLOW ESSENTIAL, NOT MESH BLUR OR FOUNWEAR"}
]
out=[]
for x in specs:
 fam=B/x["family"];files={int(p.name[:2]):p for p in fam.glob("*.jpg")}
 assert set(files)==set(range(1,7)),list(files)
 old=files[5];oldsha=hashlib.sha256(old.read_bytes()).hexdigest()
 photos=[]
 for slot in x["slots"]:
  im=Image.open(files[slot]);im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
  photos.append(im.convert("RGB"))
 assert hashlib.sha256(files[x["slots"][0]].read_bytes()).hexdigest()!=hashlib.sha256(files[x["slots"][1]].read_bytes()).hexdigest()
 canvas=Image.new("RGB",(1080,1080),x["panel"]);d=ImageDraw.Draw(canvas)
 d.rectangle((0,0,1080,20),fill=x["accent"])
 d.text((50,39),x["title"],fill="#283b33",font=F(54,True))
 d.text((50,115),x["subtitle"],fill="#283b33",font=F(28,True))
 d.text((50,185),x["body"],fill="#4a6657",font=F(37,True))
 # show two distinct genuine same-product inputs rather than repeating one hero.
 for i,im in enumerate(photos):
  thumb=ImageOps.contain(im,(440,455),Image.Resampling.LANCZOS)
  xx=45+i*535+(440-thumb.width)//2
  yy=264+(455-thumb.height)//2
  canvas.paste(thumb,(xx,yy))
  d.text((70+i*535,733),f"ACTUAL PHOTO {i+1}",font=F(19),fill="#536b5e")
 for i,step in enumerate(x["steps"]):
  xx=48+i*344
  d.rounded_rectangle((xx,787,xx+316,904),radius=19,fill="#e5eae4")
  d.text((xx+14,838),step,font=F(19,True),fill="#405a4b")
 d.line((45,949,1035,949),fill=x["accent"],width=3)
 d.text((47,961),x["line"],font=F(21),fill="#435b4e")
 target=O/(x["family"]+"-slot05-two-genuine-views-CANDIDATE.jpg")
 canvas.save(target,"JPEG",quality=88,optimize=True)
 raw=target.read_bytes()
 assert Image.open(target).size==(1080,1080) and len(raw)<2_000_000
 scores={}
 for slot,p in files.items():
  im=Image.open(p).convert("RGB").resize((128,128))
  other=canvas.resize((128,128))
  scores[str(slot)]=round(sum(ImageStat.Stat(ImageChops.difference(im,other)).mean)/3,2)
 assert min(scores.values())>8,(x["family"],scores)
 out.append({"family":x["family"],"slot":5,"candidate_file":target.name,
  "source_image_slots":x["slots"],"source_image_hashes":[hashlib.sha256(files[s].read_bytes()).hexdigest() for s in x["slots"]],
  "target_old_sha":oldsha,"candidate_sha":hashlib.sha256(raw).hexdigest(),
  "pixel_MAE_by_slot":scores,"candidate_bytes":len(raw),"edition_guard":x["source_edition"],
  "status":"QA_ONLY_EDITION_RIGHTS_LOGO_VISUAL_HOLD"})
assert len(out)==2 and len(list(B.glob("pending-*/*.jpg")))==156
report={"version":"v2562","source_qa_run":41753618979,"source_remaining_pairs_run":41753774564,
 "candidates_created":2,"old_156_jpg_changed":0,"new_public_urls":0,
 "old_55_public_urls_changed":0,"xlsx_created":False,
 "no_new_synthetic_product_or_shade_pixels":True,"commercial_reuse_rights_verified":False,
 "exact_stock_edition_matched":False,"original_mk_logo_applied":False,
 "sales_release_approved":False,"candidates":out,
 "warning":"Images are re-layouts from saved existing photos, not independent licensed photography. Requires human quality review."}
(O/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"actual_candidate_jpgs":2,"family_targets":[x["family"] for x in out],
 "minimum_pixel_MAE":{x["family"]:min(x["pixel_MAE_by_slot"].values()) for x in out},
 "source_originals_modified":0,"sales_approved":False}))
