#!/usr/bin/env python3
"""v2673 batch produce two distinct 5-frame factual QA photo-led families.
Reuse actual product-source JPGs byte-exact. Only add conservative, separately
composed typography. No fake product photo, MK logo, effects or retail approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,shutil,base64
SRC=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2673-two-new-product-five-JPG-sets")
assert not OUT.exists(),"Already staged"
OUT.mkdir(parents=True)
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def f(size,b=False):return ImageFont.truetype(bold if b else regular,size)
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
products=[
 {"family":"pending-16","brand":"Dr.G","name":["R.E.D BLEMISH","CLEAR SOOTHING CREAM"],"volume":"70 mL",
  "reuse_slots":[4,5],"accent":"#d9e9df","dark":"#214739","info":["SOOTHING CREAM","70 mL"]},
 {"family":"pending-19","brand":"goodal","name":["GREEN TANGERINE","VITA C CREAM ALPHA"],"volume":"50 mL",
  "reuse_slots":[1,5],"accent":"#f0edd0","dark":"#4d552b","info":["VITA C CREAM ALPHA","50 mL"]}
]
def safe_text(d,t,x,y,maxw,size,color):
 while size>22 and d.textbbox((0,0),t,font=f(size,True))[2]>maxw:size-=2
 assert d.textbbox((0,0),t,font=f(size,True))[2]<=maxw,t
 d.text((x,y),t,fill=color,font=f(size,True))
def make_card(p,info,kind):
 accent=info["accent"];dark=info["dark"]
 im=Image.new("RGB",(1080,1080),"#fafaf8")
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((60,55,1020,1025),radius=35,fill="#ffffff",outline="#d8dfd7",width=3)
 d.rounded_rectangle((80,80,1000,270),radius=27,fill=accent)
 safe_text(d,info["brand"],120,137,830,59,dark)
 d.line((120,337,960,337),fill="#d2ddd4",width=3)
 if kind=="identity":
  safe_text(d,"PRODUCT DETAILS",120,375,830,40,dark)
  y=490
  for line in info["name"]:
   safe_text(d,line,120,y,835,59,dark);y+=100
  safe_text(d,info["volume"],120,787,830,68,dark)
 elif kind=="capacity":
  safe_text(d,"NET CONTENT",120,415,830,44,dark)
  safe_text(d,info["volume"],120,555,830,116,dark)
  safe_text(d,"ONE PRODUCT",120,780,830,42,dark)
 elif kind=="care":
  safe_text(d,"PRODUCT GUIDE",120,375,830,44,dark)
  for i,txt in enumerate(["Follow directions","on the original","product packaging"]):
   safe_text(d,txt,120,515+i*96,840,54,dark)
 d.line((120,910,960,910),fill="#d9dfd8",width=2)
 d.text((120,943),"KOREAN BEAUTY",font=f(30),fill="#6c7a72")
 im.save(p,format="JPEG",quality=91,optimize=True,subsampling=0)
rows=[]
proof=Image.new("RGB",(1800,1900),"#ecefeb")
d=ImageDraw.Draw(proof)
d.text((22,12),"v2673 TWO NEW PHOTO-LED 5-JPG QA FAMILIES",font=f(37,True),fill="#222222")
for ri,p in enumerate(products):
 fam=p["family"];dest=OUT/fam;dest.mkdir()
 selected=[]
 for slot,src_slot in enumerate(p["reuse_slots"],1):
  matches=list((SRC/fam).glob(f"{src_slot:02d}*.jpg"))
  assert len(matches)==1,(fam,src_slot)
  original=matches[0]
  target=dest/f"{slot:02d}-original-source-slot{src_slot:02d}-UNMODIFIED-QA.jpg"
  shutil.copy2(original,target)
  assert h(target)==h(original)
  selected.append({"frame":slot,"kind":"REAL_EXISTING_PHOTO_OR_GUIDE_NO_REENCODE","file":target.name,
    "source_slot":src_slot,"source_sha256":h(original),"sha256":h(target)})
 for frame,kind in [(3,"identity"),(4,"capacity"),(5,"care")]:
  target=dest/f"{frame:02d}-new-{kind}-QA-only.jpg"
  make_card(target,p,kind)
  selected.append({"frame":frame,"kind":"FACTUAL_INFORMATION_CARD_NEW","file":target.name,
    "sha256":h(target)})
 for entry in selected:
  with Image.open(dest/entry["file"]) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   thumb=im.convert("RGB").resize((326,326),Image.Resampling.LANCZOS)
  assert (dest/entry["file"]).stat().st_size<2_000_000
  entry["bytes"]=(dest/entry["file"]).stat().st_size
  x=22+(entry["frame"]-1)*353;y=65+ri*900
  proof.paste(thumb,(x,y))
  d.text((x,y+337),fam+" / "+str(entry["frame"]).zfill(2),font=f(21),fill="#272b29")
 rows.append({"family":fam,"product":" ".join(p["name"]),"volume":p["volume"],
 "source_photos_unchanged":2,"new_text_info_cards":3,
 "qa_frame_count":5,"sale_release":"HOLD_SOURCE_RIGHTS_STOCK_EDITIONS_LATEST_V2647_HUMAN_QA",
 "frames":selected})
pic=OUT/"v2673-two-products-10-frame-contact.jpg";proof.save(pic,quality=82,optimize=True)
(OUT/"v2673-preview.b64.txt").write_text(base64.b64encode(pic.read_bytes()).decode())
manifest={"version":"v2673","two_new_product_family_five_frame_QA_drafts":2,
"previously_approved_product_families_mutated":0,"published_55_urls_mutated":0,
"original_source_JPGs_regenerated":0,"new_conservative_info_card_JPGs":6,
"source_JPGs_byte_preserved":4,
"review_only":True,"final_xlsx_shared":False,
"latest_v2647_binary_not_available":True,"commercial_photo_rights_unverified":True,
"rows":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"five_JPG_new_family_drafts":2,"JPG_files":10,"source_bytes_untouched":4,
"new_info_frames":6,"new_sales_approved":0}))
