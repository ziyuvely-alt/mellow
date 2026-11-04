#!/usr/bin/env python3
"""v2675: progress two new entire product family 5-JPG QA sets with verified
photo bytes preserved, targeted minimal factual frame replacements.
No fake product rendering, product label changes, logo insertion or public URL mutations.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,shutil,base64
ROOT=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2675-missha-two-five-frame-photo-sets")
assert not OUT.exists()
OUT.mkdir(parents=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(size,b=False):return ImageFont.truetype(BOLD if b else FONT,size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def line(d,s,x,y,maxw,size,color):
 while size>=24 and d.textbbox((0,0),s,font=ft(size,True))[2]>maxw:size-=2
 assert size>=24,(s,size)
 d.text((x,y),s,font=ft(size,True),fill=color)
specs=[
 {"family":"pending-01","brand":"MISSHA","name":["MAGIC CUSHION","COVER LASTING"],"detail":"CUSHION COMPACT",
  "new_slot":3,"accent":"#e8dcd8","copy":"PRODUCT DETAILS",
  "preserve_slots":[1,2,4,5],
  "limits":["No shade count declared without matching owned-stock package"]},
 {"family":"pending-14","brand":"MISSHA","name":["PDRN NAD+","FIRMING REPAIR CREAM"],"detail":"70 mL",
  "new_slot":5,"accent":"#eadadb","copy":"NET CONTENT",
  "preserve_slots":[1,2,3,4],
  "limits":["No active ingredients claimed without independently verified formula"]}
]
proof=Image.new("RGB",(1860,1590),"#f1f1ef")
d=ImageDraw.Draw(proof)
d.text((25,14),"v2675 TWO MISSHA PHOTO-FIRST FIVE-JPG DRAFTS / QA ONLY",font=ft(39,True),fill="#282828")
records=[]
for i,s in enumerate(specs):
 fam=s["family"];dst=OUT/fam;dst.mkdir()
 imgrows=[]
 for slot in s["preserve_slots"]:
  matches=list((ROOT/fam).glob(f"{slot:02d}*.jpg"))
  assert len(matches)==1,(fam,slot)
  src=matches[0];tar=dst/f"{slot:02d}-prior-original-byte-identical-QA.jpg"
  shutil.copy2(src,tar)
  assert sha(tar)==sha(src)
  imgrows.append({"slot":slot,"filename":tar.name,"sha256":sha(tar),"source":src.name,
                  "status":"EXISTING_JPG_PRESERVED_NO_REENCODE"})
 im=Image.new("RGB",(1080,1080),"#fffefa")
 draw=ImageDraw.Draw(im)
 draw.rounded_rectangle((52,48,1028,1032),radius=38,fill="#fffefc",outline="#d9d7d4",width=3)
 draw.rounded_rectangle((78,76,1002,260),radius=27,fill=s["accent"])
 line(draw,s["brand"],115,126,860,54,"#392b31")
 line(draw,s["copy"],115,340,870,42,"#6f555a")
 y=475
 for item in s["name"]:
  line(draw,item,115,y,860,67,"#332830")
  y+=110
 draw.line((115,767,965,767),fill="#d8b6b8",width=3)
 line(draw,s["detail"],115,815,845,56,"#332830")
 draw.text((115,950),"KOREAN BEAUTY",font=ft(29),fill="#8e787a")
 tar=dst/f"{s['new_slot']:02d}-factual-detail-new-QA.jpg"
 im.save(tar,quality=94,optimize=True,subsampling=0)
 imgrows.append({"slot":s["new_slot"],"filename":tar.name,"sha256":sha(tar),
                 "status":"NEW_FACTUAL_FRAME_REPLACES_UNVERIFIED_COPY"})
 imgrows.sort(key=lambda z:z["slot"])
 assert len(imgrows)==5
 for j,row in enumerate(imgrows):
  p=dst/row["filename"]
  with Image.open(p) as image:
   image.load()
   assert image.format=="JPEG" and image.size==(1080,1080)
   thumb=image.convert("RGB").resize((342,342),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  x=22+j*366;y=82+i*735
  proof.paste(thumb,(x,y))
  d.text((x,y+350),fam+" / "+str(row["slot"]).zfill(2),font=ft(25),fill="#303030")
  row["bytes"]=p.stat().st_size
 records.append({"family":fam,"five_frame_draft_exists":True,
                 "four_real_source_JPGs_unmodified":4,
                 "new_factual_frame_slot":s["new_slot"],
                 "unresolved":["Exact owned-stock version and shades","Source-photo redistribution rights","Current v2647 comparison","Final retail design review"],
                 "frames":imgrows,"retail_approval":"HOLD"})
p=OUT/"v2675-two-missha-preview.jpg";proof.save(p,quality=85,optimize=True)
(OUT/"v2675-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
m={"version":"v2675","prior_checkpoint":"v2674","two_distinct_five_frame_sets":2,
   "physical_JPG_frames":10,"byte_identical_reused":8,"new_safe_copy_frames":2,
   "new_retail_approvals":0,
   "source_is_historical_not_latest":True,
   "approved_11_product_families_mutated":False,"public_55_URLs_mutated":False,
   "final_xlsx_shared":False,"families":records}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_QA_product_families":2,"JPGs":10,"preserved_source_JPGs":8,
                  "replaced_unsafe_information_frames":2,"retail_approved":0}))
