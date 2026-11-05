#!/usr/bin/env python3
"""v2881. CLIO Kill Cover Mesh Glow Essential Cushion 15g+Refill 15g:
5 real shade swatches on genuine labeled source photographs, no
false independently-colored packshots.

This addresses v2861 all TEN near-duplicate merchant shade product pairs.
Reuse a pre-existing source compact ONLY as a common product scene.
Download at most once from 3 documented real 5-shade charts. Always save
original bytes, don't recolor. Provide five QA source-linked reference cards
only after 5-shade chart is available. No rights claim, no set physical
inventory verification, no public release, original 55 URLs immutable.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json
from hashlib import sha256
R=Path("qa-review")
SRC=R/"v2851-clio-giftset-five-option-variant-photo-QA"
PREV=R/"v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit"
OUT=R/"v2881-clio-meshglow-five-real-labeled-swatch-chart-QA"
assert not OUT.exists()
p=json.loads((SRC/"manifest.json").read_text())
audit=json.loads((PREV/"pending-06-collision-metrics.json").read_text())
assert p["version"]=="v2851" and audit["possible_collisions"]==10
x=next(f for f in p["families"] if f["id"]=="pending-06")
ref=next(v for v in x["variants"] if v["shade"]=="21N")
ref_path=SRC/ref["filename"]
sha=lambda file:sha256(file.read_bytes()).hexdigest()
assert ref_path.is_file() and sha(ref_path)==ref["rendered_sha256"]
with Image.open(ref_path) as im:
 im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 common_photo=im.convert("RGB")
SOURCES=[
 {"id":"brand-Clio-official-LIPS-five-shades","url":"https://cloudflare.lipscosme.com/image/2025-12-18-70d24741cce68ed52ca1da7c.png?auto=avif%2Cwebp&fio=1&orient=1&width=1424",
  "page":"https://lipscosme.com/posts/8237300","source":"Official CLIO account on LIPS","rank":1},
 {"id":"ballagrio-five-real-swatch-arm","url":"https://www.ballagrio.com/cdn/shop/files/12_8892f631-07c7-469c-900d-bee9719219e1.png?v=1749669982",
  "page":"https://www.ballagrio.com/products/clio-kill-cover-mesh-glow-essential-cushion-with-refill-5-colors-15g-2ea","source":"Ballagrio merchant shade chart","rank":2},
 {"id":"konvy-five-cheek-actual-shades","url":"https://s3.konvy.com/static/team/2025/0509/2025050911030426948.jpg",
  "page":"https://www.konvy.com/m/clio/clio-kill-cover-mesh-glow-essential-cushion-spf50%2B-pa%2B%2B%2B%2B-15g-%2B-refill-15g-21c-lingerie-114129.html","source":"Konvy five-shade model swatches","rank":3}
]
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
sources=[]
for entry in SOURCES:
 rec={**entry,"status":"HOLD_UNAVAILABLE","licensed_for_sales":False}
 try:
  req=Request(entry["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/jpeg,image/png,image/*,*/*"})
  with urlopen(req,timeout=14) as resp:raw=resp.read(9_000_001)
  assert 5000<len(raw)<=9_000_000
  with Image.open(BytesIO(raw)) as im:
   im.load()
   assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=500
   imtype=im.format;native=list(im.size);picture=im.convert("RGB")
  ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[imtype]
  path=OUT/(entry["id"]+"-source-original."+ext)
  path.write_bytes(raw)
  rec.update(status="REAL_FIVE_LABEL_CHART_SOURCE_QA_SAVED",
    raw_file=str(path),raw_sha256=sha(path),original_native_px=native,original_format=imtype,
    no_recoloring=True)
 except Exception as err:
  rec.update(status="HOLD_UNAVAILABLE_SKIP",reason=type(err).__name__+": "+str(err)[:210])
 sources.append(rec)
# Official photo first when available; Ballagrio has known clear five
# numbered arms and is the only source used for exact 5 band crops.
ball=next(x for x in sources if x["id"]=="ballagrio-five-real-swatch-arm")
cards=[]
if ball["status"]=="REAL_FIVE_LABEL_CHART_SOURCE_QA_SAVED":
 bpath=Path(ball["raw_file"])
 assert sha(bpath)==ball["raw_sha256"]
 with Image.open(bpath) as im:
  im.load();swatch=im.convert("RGB")
 # Reference photo has left-right five equally spaced labeled arm regions;
 # crops preserve printed swatch labels and original colors, do not
 # pretend photo of 5 different compact shells.
 SHADES=[("19C","LIGHT"),("19N","PORCELAIN"),("21C","LINGERIE"),
         ("21N","LINEN"),("23N","GINGER")]
 N=swatch.width; H=swatch.height
 for i,(shade,name) in enumerate(SHADES):
  left=max(0,round((i*.2-.013)*N))
  right=min(N,round(((i+1)*.2+.018)*N))
  yy0=round(.16*H);yy1=round(.72*H)
  sample=swatch.crop((left,yy0,right,yy1))
  canvas=Image.new("RGB",(1080,1080),"#FBF9FC")
  d=ImageDraw.Draw(canvas)
  d.rounded_rectangle((38,39,1042,1042),radius=24,outline="#E2D9E5",width=2)
  d.text((68,66),"CLIO | MESH GLOW ESSENTIAL 15g+15g REFILL",font=ft(25,True),fill="#443848")
  d.rounded_rectangle((70,128,1007,202),radius=14,fill="#F0EAF2")
  d.text((90,144),shade+"  "+name+"  |  REAL SHADE SWATCH QA",font=ft(24,True),fill="#574960")
  d.line((73,219,1010,219),fill="#D8CFDC",width=3)
  generic=ImageOps.contain(common_photo,(445,455),Image.Resampling.LANCZOS)
  canvas.paste(generic,(65+(445-generic.width)//2,256+(455-generic.height)//2))
  photo_swatch=ImageOps.contain(swatch,(452,360),Image.Resampling.LANCZOS)
  canvas.paste(photo_swatch,(542+(452-photo_swatch.width)//2,255+(360-photo_swatch.height)//2))
  z=ImageOps.contain(sample,(430,310),Image.Resampling.LANCZOS)
  canvas.paste(z,(553+(430-z.width)//2,595+(310-z.height)//2))
  d.text((75,748),"COMMON COMPACT PHOTO",font=ft(16,True),fill="#6B5D70")
  d.text((562,911),"ACTUAL LABELED SWATCH CROP",font=ft(16,True),fill="#6B5D70")
  d.line((78,953,1005,953),fill="#D6CEDA",width=2)
  d.text((75,976),"INTERNAL QA | REAL SOURCE PIXELS | SALE RIGHTS & OWNED SET HOLD",font=ft(16,True),fill="#76687E")
  filename=OUT/f"CLIO-MeshGlow-15gRefill-{shade}-real-swatch-1080-QA.jpg"
  canvas.save(filename,"JPEG",quality=93,optimize=True,subsampling=0)
  with Image.open(filename) as ck:ck.load();assert ck.size==(1080,1080) and ck.format=="JPEG"
  assert filename.stat().st_size<2_000_000
  assert sha(bpath)==ball["raw_sha256"] and sha(ref_path)==ref["rendered_sha256"]
  cards.append({"shade":shade,"name":name,"swatch_source":str(bpath),
   "original_swatch_sha256":ball["raw_sha256"],"swatch_crop_original_px":[left,yy0,right,yy1],
   "shared_compact_source":str(ref_path),"shared_photo_sha256":ref["rendered_sha256"],
   "new_QA_jpg":str(filename),"new_qa_sha256":sha(filename),"jpg_bytes":filename.stat().st_size,
   "shade_specific_compact_photo":False,"swatch_photo_unmodified_RGB":True,
   "commercial_usage_rights":False,"actual_owned_giftset_confirmed":False,
   "release_approved":False})
 # Real five photos cannot be published until pack contents and rights.
 assert len(cards)==5 and len({x["new_qa_sha256"] for x in cards})==5
else:
 print("HOLD: no Ballagrio true 5-shade swatch; do not invent palette")
contact=None
if cards:
 bd=Image.new("RGB",(1600,1200),"#F0EDF1")
 dr=ImageDraw.Draw(bd)
 dr.text((15,12),"v2881 | FIVE REAL ORIGINAL SHADE SWATCHS | NOT FIVE DISTINCT COMPACT PHOTOS | QA",font=ft(21,True),fill="#473A4C")
 for i,x in enumerate(cards):
  with Image.open(x["new_QA_jpg"]) as im:pic=im.resize((500,500),Image.Resampling.LANCZOS)
  bd.paste(pic,(18+i%3*525,55+i//3*555))
 contact=OUT/"v2881-clio-5-real-shades-vs-common-compact-reference-QA.jpg"
 bd.save(contact,"JPEG",quality=88,optimize=True)
report={
 "version":"v2881","baseline":"v2880","family":"pending-06",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion 15g+Refill 15g",
 "distinct_stock_options":["19C","19N","21C","21N","23N"],
 "merchants_confirm_15g_plus_refill_15g":True,
 "exact_user_owned_set_verified":False,"photo_commercial_reuse_licensed":False,
 "reused_previously_saved_common_21N_photo_as_common_not_distinct":True,
 "v2861_near_duplicate_ten_variant_photo_pairs_still_blocked":True,
 "new_authentic_five_shade_swatch_QA_JPGs":len(cards),
 "original_five_swatch_charts_downloaded":sum(x["status"].startswith("REAL_") for x in sources),
 "original_raw_source_images_untouched":True,"new_fake_color_chips":0,
 "sources":sources,"cards":cards,"QA_contact":str(contact) if contact else None,
 "stock_15g+refill_user_owned_variant_verified":False,
 "new_sales_approved":0,"new_public_urls":0,
 "old_11_published_groups_preserved":True,
 "old_55_verified_public_urls_preserved":True,
 "final_spreadsheet_shared":False,
 "next":"Visual verify crop alignment with 19C/19N/21C/21N/23N printed labels. Confirm seller-owned exact 15g+refill pack, source rights, original MK logo. Do not promote common compact photo to unique variant photo."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2881","new_QA_JPGs":len(cards),"chart_sources_saved":report["original_five_swatch_charts_downloaded"],"retail_approved":0}))
