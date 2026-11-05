#!/usr/bin/env python3
"""v2862: select ONLY 3 distinguishable merchant-linked original Founwear
The Original shade photos from v2852 for careful non-destructive alpha QA.
Do not process the 21C-vs-21N near-collision or the five near-duplicate
Mesh Glow (pending06) photo pairs; their sources are on hold for identity QA.
Never claim a verified gift-set photo/contents or publish merchant art.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json
import numpy as np
import cv2

R=Path("qa-review")
SRC=R/"v2852-founwear-original-five-variant-alternative-merchant-QA"
PREV=R/"v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit"/"manifest.json"
OUT=R/"v2862-clio-founwear-three-distinct-source-truealpha-QA"
assert not OUT.exists() and PREV.is_file()
source=json.loads((SRC/"manifest.json").read_text())
prev=json.loads(PREV.read_text())
assert prev["version"]=="v2861"
p05=next(x for x in prev["comparison_metrics"] if x["family"]=="pending-05")
p06=next(x for x in prev["comparison_metrics"] if x["family"]=="pending-06")
assert p05["possible_collisions"]>=1 and p06["possible_collisions"]>=5
rows={r["shade"]:r for r in source["variants"]}
selected=["19C","19N","23N"]
blocked=["21C","21N"]
assert set(selected+blocked)==set(rows)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
OUT.mkdir(parents=True)
outputs=[];proven=[]
for shade in selected:
 item=rows[shade]
 p=SRC/item["rendered_file"]
 status={"shade":shade,"source":str(p),"source_sha":item["rendered_JPG_sha256"],
         "merchant_variant_id":item["merchant_variant_id"],"role":"SHADE_PHOTO_QA_NOT_GIFT_SET",
         "technical_status":"PENDING","physical_stock_edition_verified":False,
         "merchant_photo_reuse_permission_verified":False,"retail_approved":False}
 try:
  assert p.is_file() and sha(p)==item["rendered_JPG_sha256"]
  with Image.open(p) as s:
   s.load();assert s.format=="JPEG" and s.size==(1080,1080)
   source_im=s.convert("RGB")
  a=np.asarray(source_im).copy()
  H,W=a.shape[:2]
  mask=np.zeros((H,W),np.uint8)
  mask[80:995,35:1050]=cv2.GC_PR_BGD
  # Color-rich product pixels form probable foreground; truly white blank
  # areas stay true background. Pale plastic gets hard original-pixel seeds.
  region=a[80:995,35:1050]
  nearwhite=np.min(region,axis=2)>=252
  colored=np.min(region,axis=2)<246
  m=mask[80:995,35:1050]
  m[colored]=cv2.GC_PR_FGD
  m[nearwhite]=cv2.GC_BGD
  sure=[
    (375,425,330,650),  # true silver compact lid
    (555,605,350,620),  # true cushion pan product
    (710,770,420,610),  # true cushion bottom
    (745,775,800,860),  # true white puff and lettering
    (270,305,125,185),  # cream smear in real merchant source
    (207,248,630,720),  # second cream-smear genuine region
  ]
  for y0,y1,x0,x1 in sure:mask[y0:y1,x0:x1]=cv2.GC_FGD
  bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
  cv2.grabCut(cv2.cvtColor(a,cv2.COLOR_RGB2BGR),mask,None,bg,fg,7,cv2.GC_INIT_WITH_MASK)
  fgmask=np.where((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD),255,0).astype(np.uint8)
  n,lab,stats,cent=cv2.connectedComponentsWithStats(fgmask,8)
  main=[j for j in range(1,n) if stats[j,cv2.CC_STAT_AREA]>600]
  assert main,"no safe product foreground components"
  binary=np.isin(lab,main).astype(np.uint8)*255
  x,y,w,h=cv2.boundingRect((binary>127).astype(np.uint8))
  area=int((binary>127).sum())
  # Reject if true cream smear, compact, or puff lost.
  assert (35<=x<=270 and 80<=y<=330),(shade,"bbox origin invalid",x,y)
  assert (520<=w<=1000 and 550<=h<=930),(shade,"bbox size invalid",w,h)
  assert (130000<=area<=580000),(shade,"foreground area invalid",area)
  for cy,cx in [(392,480),(575,460),(746,495),(759,830)]:
   assert binary[cy,cx]>=127,(shade,"original central product disappeared",cy,cx)
  alpha=cv2.GaussianBlur(binary,(3,3),0.65)
  rgba=Image.fromarray(np.dstack((a,alpha)),"RGBA")
  crop=(max(0,x-16),max(0,y-16),min(1080,x+w+16),min(1080,y+h+16))
  product=rgba.crop(crop)
  png=OUT/f"Founwear-Original-{shade}-truealpha-QA.png"
  product.save(png,optimize=True)
  display=ImageOps.contain(product,(920,920),Image.Resampling.LANCZOS)
  hero=Image.new("RGB",(1080,1080),"white")
  hero.paste(display,((1080-display.width)//2,(1080-display.height)//2),display.getchannel("A"))
  jpg=OUT/f"Founwear-Original-{shade}-1080-hero-QA.jpg"
  hero.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
  with Image.open(jpg) as im:assert im.size==(1080,1080) and im.format=="JPEG"
  assert jpg.stat().st_size<2_000_000
  checker=Image.new("RGBA",(1080,1080),"#F2EBF0")
  dr=ImageDraw.Draw(checker)
  for yy in range(0,1080,32):
   for xx in range(0,1080,32):
    if (xx//32+yy//32)%2:dr.rectangle((xx,yy,xx+31,yy+31),fill="#D5D2DE")
  overlay=Image.new("RGBA",(1080,1080),(0,0,0,0))
  overlay.paste(display,((1080-display.width)//2,(1080-display.height)//2),display)
  checker.alpha_composite(overlay)
  check=OUT/f"Founwear-Original-{shade}-edge-check-QA.jpg"
  checker.convert("RGB").save(check,"JPEG",quality=89,optimize=True)
  assert sha(p)==item["rendered_JPG_sha256"]
  status.update(technical_status="CUTOUT_CANDIDATE_HOLD_CLOSEUP_AND_PRODUCT_IDENTITY",
                mask_bbox=[x,y,w,h],mask_area_px=area,
                PNG=str(png),PNG_SHA256=sha(png),JPG=str(jpg),
                JPG_SHA256=sha(jpg),JPG_BYTES=jpg.stat().st_size,
                checker=str(check),source_original_rgb_unaltered=True)
  proven.append((shade,source_im.copy(),checker.convert("RGB").copy(),hero.copy()))
 except Exception as e:
  status.update(technical_status="HOLD_NO_RETRY_UNSAFE_ALPHA",reason=str(e)[:250])
  print("HOLD",shade,str(e)[:200])
 outputs.append(status)
if proven:
 FT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 b=Image.new("RGB",(1660,550*len(proven)+70),"#F1F0F2");d=ImageDraw.Draw(b)
 d.text((20,12),"v2862 FOUNWEAR | VERIFIED SOURCE IMAGE -> TRUE ALPHA -> WHITE HERO (QA ONLY)",
        font=ImageFont.truetype(FT,24),fill="#4B3F4B")
 for i,(shade,photo,checker,hero) in enumerate(proven):
  y=56+550*i
  for j,im in enumerate((photo,checker,hero)):
   b.paste(im.resize((510,510),Image.Resampling.LANCZOS),(18+545*j,y))
  for j,s in enumerate(("ORIGINAL","TRUE ALPHA","QA HERO")):
   d.text((27+545*j,y+484),shade+" "+s,font=ImageFont.truetype(FT,18),fill="#38303E")
 board=OUT/"v2862-three-founwear-photo-cutouts-comparison-QA.jpg"
 b.save(board,"JPEG",quality=86,optimize=True)
m={"version":"v2862","baseline":"v2861","family":"pending-05",
 "product":"CLIO Kill Cover Founwear Cushion The Original / gift-set identity unconfirmed",
 "attempted_shades":selected,"intentionally_skipped_near_duplicate_shades":blocked,
 "pending06_status":"HOLD_NEAR_DUPLICATE_SOURCE_PHOTOS_10_OF_10_PAIRS",
 "source_variant_photo_count":5,"candidate_alpha_count":len(proven),
 "held_alpha_count":3-len(proven),"new_sale_approvals":0,
 "source_images_modified":0,"new_public_URLs":0,
 "previous_11_published_families_unchanged":True,
 "previous_55_verified_public_URLs_unchanged":True,
 "merchant_photo_rights_verified":False,"owned_exact_gift_set_packaging_verified":False,
 "original_MK_logo_verified":False,"spreadsheet_shared":False,
 "results":outputs,
 "contact":str(OUT/"v2862-three-founwear-photo-cutouts-comparison-QA.jpg") if proven else None,
 "next":"Inspect premium silver compact/puff edges at 1:1; if reliable, reuse for shade-only internal QA, not gift-set proof. Source-new 21C/21N and all pending-06 shade photos before release; do not repeat near-identical images."
}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2862","new_alpha_pngs":len(proven),
                  "new_hero_jpgs":len(proven),
                  "held_shades":[x["shade"] for x in outputs if x["technical_status"].startswith("HOLD")],
                  "near_dup_skipped":blocked,"new_sale_approvals":0}))
