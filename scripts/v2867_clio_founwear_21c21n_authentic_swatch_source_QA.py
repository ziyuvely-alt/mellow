#!/usr/bin/env python3
"""v2867: Two independent *real-photo, source-labeled* shade proof references
for CLIO Founwear The Original 21C and 21N. No invention/recoloring of swatches.
Retailer screenshots only for INTERNAL QA, commercial usage rights NOT granted.
Nothing from v2866 or 55 published URLs is modified or re-rendered.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
from hashlib import sha256
import json
R=Path("qa-review")
OUT=R/"v2867-founwear-21C-21N-real-swatch-source-evidence-QA"
assert not OUT.exists()
OUT.mkdir(parents=True)
sources=[
 {"id":"merchant-cheek-five-labeled-shades",
  "url":"https://glowupdiary.com/cdn/shop/files/Snimek_obrazovky_2024-10-20_v_10.53.20.png?v=1729414526&width=4096",
  "source":"Glow Up Diary merchant",
  "subject":"Five actual labeled cheek application stripes, including 21C Lingerie and 21N Linen"},
 {"id":"merchant-forearm-five-labeled-shades",
  "url":"https://i.ebayimg.com/images/g/Ri0AAOSwbDlm0Q8O/s-l1200.png",
  "source":"eBay merchant photograph",
  "subject":"Five real forearm stripe shades, actual labels including 21C and 21N"},
 {"id":"marketplace-color-chart-five-shades",
  "url":"https://down-my.img.susercontent.com/file/vn-11134208-7ra0g-m8d5d2whzqtj44",
  "source":"Shopee merchant reference",
  "subject":"Five labeled brand-shade cosmetics chart, including distinct 21C and 21N"}
]
rows=[]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F=lambda n,b=False:ImageFont.truetype(boldfile if b else fontfile,n)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
previews=[]
for src in sources:
 row=dict(src,status="NOT_FETCHED",source_reuse_rights_verified=False,actual_user_stock_verified=False)
 try:
  request=Request(src["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/png,image/jpeg,image/*,*/*"})
  with urlopen(request,timeout=19) as response:
   raw=response.read(8_000_001)
  assert 5000<len(raw)<=8_000_000,"source file invalid length"
  with Image.open(BytesIO(raw)) as im:
   im.load()
   assert im.format in ("PNG","JPEG","WEBP") and min(im.size)>=350
   rgb=im.convert("RGB")
   real_type=im.format
   native=list(im.size)
  # Stage exact raw bytes for source preservation. Never forge swatch pixels.
  extension={"PNG":".png","JPEG":".jpg","WEBP":".webp"}[real_type]
  rawpath=OUT/(src["id"]+"-source-unaltered"+extension)
  rawpath.write_bytes(raw)
  canvas=Image.new("RGB",(1080,1080),"#FEFCFD")
  d=ImageDraw.Draw(canvas)
  d.text((61,44),"CLIO FOUNWEAR | SOURCE SWATCH QA",font=F(31,True),fill="#433944")
  d.text((61,100),"21C LINGERIE   /   21N LINEN",font=F(24,True),fill="#635268")
  d.line((60,147,1020,147),fill="#D8C9D8",width=3)
  fit=ImageOps.contain(rgb,(958,810),Image.Resampling.LANCZOS)
  canvas.paste(fit,((1080-fit.width)//2,164+(810-fit.height)//2))
  d.text((61,1000),"REAL MERCHANT SOURCE  |  NOT FOR COMMERCIAL PUBLICATION",font=F(18,True),fill="#745E71")
  jpg=OUT/(src["id"]+"-1080-source-swatch-QA.jpg")
  canvas.save(jpg,"JPEG",quality=93,subsampling=0,optimize=True)
  with Image.open(jpg) as im:assert im.size==(1080,1080) and im.format=="JPEG"
  assert jpg.stat().st_size<2_000_000
  row.update(status="SOURCE_ART_BYTES_SAVED_PENDING_VISUAL_SHADENUMBER_QA",
     format=real_type,native_px=native,raw_path=str(rawpath),
     raw_sha256=sha(rawpath),qa_JPG_1080=str(jpg),qa_sha256=sha(jpg),
     qa_bytes=jpg.stat().st_size,swatch_RGB_recolored=False)
  previews.append((src["id"],canvas))
 except Exception as e:
  row.update(status="HOLD_SOURCE_UNAVAILABLE_SKIP_TO_NEXT",error=type(e).__name__+": "+str(e)[:200])
 rows.append(row)
contact=Image.new("RGB",(1570,560),"#F0EDF1")
d=ImageDraw.Draw(contact)
d.text((15,12),"v2867 | 21C/21N REAL SHADE PHOTO SOURCE REFERENCES | QA ONLY",font=F(24,True),fill="#3A3340")
for i,(name,im) in enumerate(previews[:3]):
 panel=im.resize((500,500),Image.Resampling.LANCZOS)
 contact.paste(panel,(15+520*i,52))
cpath=OUT/"v2867-21C-21N-actual-swatch-source-photo-comparison-QA.jpg"
contact.save(cpath,"JPEG",quality=86,optimize=True)
manifest={"version":"v2867","baseline":"v2866","family":"pending-05",
 "work":"Staged 21C/21N original real shade reference photos, not reused ambiguous compact variant images.",
 "sources_attempted":len(sources),"real_source_photos_saved":len(previews),
 "real_source_photos_held":len(sources)-len(previews),
 "sources":rows,"contact":str(cpath),"contact_sha256":sha(cpath),
 "user_stock_shades_in_scope":["19C","19N","21C","21N","23N"],
 "prior_v2866_photos_unchanged":True,"prior_v2861_near_duplicate_hold_for_21C_21N":True,
 "new_source_photo_rights_licensed":False,"exact_stock_giftset_edition_verified":False,
 "official_clio_swatches_independently_authenticated":False,
 "new_public_URLs":0,"new_retail_approved":0,"old_55_public_URLs_unchanged":True,
 "old_11_published_families_unchanged":True,"final_spreadsheet_shared":False,
 "next":"Inspect source photos to confirm 21C/21N text visually; use only actual shade distinctions for internal QA. Never publish third-party reference images or fake product photos. Requires licensed source/owned packaging."}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2867","source_photo_qa_saved":len(previews),
 "held":len(sources)-len(previews),"new_sales_approved":0}))
