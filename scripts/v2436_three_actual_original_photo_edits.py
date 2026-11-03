#!/usr/bin/env python3
"""v2436: three authentic-photo customer JPG revisions from existing source photographs.
Crop away unverified MK badge but retain actual product photos, no synthetic swatches or packaging.
Candidate drafts only, no rights/stock assertions.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, hashlib
BASE=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-photo-captions"
OUT=Path("v2436-output");OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ft(size,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",size)
items=[
 # source rectangles selected from viewed real JPG, entirely exclude MK logo x827+
 ("pending-16","INV_01_0a62a56a4b_EN_V2421C.jpg",(345,283,744,671),"Dr.G","R.E.D Blemish Clear Soothing Cream","70 mL","Open-jar original product photograph"),
 ("pending-28","INV_01_5a12115d60_EN_V2421C.jpg",(290,265,820,725),"PIXEL PURE","Glow Cleansing Serum Pad","210 mL / 70 Pads","Serum-soaked pads, original photographed texture"),
 ("pending-29","INV_01_023f07baae_EN_V2421C.jpg",(225,285,598,610),"PIXEL PURE","Radiance Aqua Soothing Cream","50 mL","Whole jar original photograph")
]
out=[]
for gid,filename,crop,brand,title,size,desc in items:
 source=BASE/gid/filename
 assert source.exists(),source
 source_sha=sha(source)
 with Image.open(source) as original:
  original.load(); assert original.size==(1080,1080)
  photo=original.convert("RGB").crop(crop)
  photo=ImageOps.contain(photo,(780,645),Image.Resampling.LANCZOS)
  canvas=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(canvas)
  d.text((70,47),brand,font=ft(36,True),fill=(41,61,52))
  font_size=42
  while font_size>24 and d.textbbox((0,0),title,font=ft(font_size,True))[2]>935:font_size-=1
  assert d.textbbox((0,0),title,font=ft(font_size,True))[2]<=935
  d.text((70,107),title,font=ft(font_size,True),fill=(41,61,52))
  d.line((70,179,1010,179),fill=(183,193,186),width=2)
  canvas.paste(photo,((1080-photo.width)//2,217))
  d.line((70,913,1010,913),fill=(183,193,186),width=2)
  fs=54 if len(size)<15 else 41
  d.text((70,943),size,font=ft(fs,True),fill=(41,61,52))
  dest=OUT/"sales-image-drafts"/gid/(gid+"_genuine-photo_no-MK_V2436.jpg")
  dest.parent.mkdir(parents=True,exist_ok=True)
  canvas.save(dest,"JPEG",quality=94,optimize=True)
  with Image.open(dest) as check:
   check.load(); assert check.format=="JPEG" and check.size==(1080,1080) and dest.stat().st_size<2_000_000
  assert sha(source)==source_sha
  out.append({"group_id":gid,"original":str(source.relative_to(BASE)),"original_sha256":source_sha,
              "output":str(dest.relative_to(OUT)),"output_sha256":sha(dest),"size":dest.stat().st_size,
              "photo_content":desc,"original_photo_preserved":True,"MK_logo_badge_excluded":True,
              "state":"SALES_IMAGE_DRAFT","visual_qa":"REQUIRES_AFTER_EXPORT","rights":"UNVERIFIED","stock_packaging":"UNVERIFIED"})
checkpoint={"version":"2.4.36","processed_groups":3,"actual_customer_JPG_drafts":len(out),
            "original_source_changed":0,"published_urls_overwritten":0,
            "official_swatch_charts":0,"FINAL_QA_APPROVED":0,
            "outputs":out,
            "next":["Visually inspect all 3 newest JPGs and reject any crop clipping",
                    "Verify product generation/current stock packaging and photo reuse rights",
                    "Resume unrelated remaining family frames and official C8 swatch verification"]}
(OUT/"v2436_checkpoint.json").write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in checkpoint.items() if k!="outputs"},ensure_ascii=False),flush=True)
