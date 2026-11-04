#!/usr/bin/env python3
"""v2711 four original-product cutout QA trials using an actual foreground
segmentation model. No drawn products, no fake original MK badge, no invented
shade chips. Never alter old approved URLs, prior photos, or public files.

New real cutouts are staged only if mask geometry passes basic tests.
Visual check of the contact sheet determines usefulness; no retail approval.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
from rembg import remove,new_session
import hashlib,json,base64,math
ROOT=Path("qa-review")
OUT=ROOT/"v2711-real-segmentation-four-source-product-heroes"
assert not OUT.exists()
OUT.mkdir(parents=True)
# Crops deliberately exclude the unverified MK mark lower-right and legacy text.
SPECS=[
  {"family":"pending-04","dir":"v2706-six-archival-five-real-source-families",
   "name":"CLIO MESH GLOW MINI","desc":"Mini Cushion 5g","crop":[190,225,890,866]},
  {"family":"pending-26","dir":"v2706-six-archival-five-real-source-families",
   "name":"PIXEL PURE","desc":"Gentle Gel-to-Foam Cleanser 145mL","crop":[270,225,800,890]},
  {"family":"pending-25","dir":"v2707-seven-remaining-archival-real-photo-family-sets",
   "name":"BIOHEAL BOH","desc":"NAD-PRIZCELL Glow Boost Cream 50mL","crop":[240,225,845,877]},
  {"family":"pending-22","dir":"v2707-seven-remaining-archival-real-photo-family-sets",
   "name":"OBgE","desc":"Max Waterful Sun Cream 300mL","crop":[270,220,802,882]}
]
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("u2netp")
rows=[]
for spec in SPECS:
  fid=spec["family"]
  srcs=sorted((ROOT/spec["dir"]/fid).glob("01-*.jpg"))
  assert len(srcs)==1,(fid,srcs)
  source=srcs[0]
  with Image.open(source) as img:
    img.load();assert img.size==(1080,1080)
    crop=img.convert("RGBA").crop(tuple(spec["crop"]))
  entry={"family":fid,"source":str(source),"source_sha256":hashfile(source),
   "crop_xyxy":spec["crop"],"segmentation_model":"u2netp",
   "cutout_pixels_real_source_only":True,"original_MK_badge_region_excluded":True,
   "status":"HOLD_FAILED_MASK_GEOMETRY","retail_approved":False}
  try:
    # Real neural foreground segmentation, not a rectangular crop presented as cutout.
    cut=remove(crop,session=session,alpha_matting=False)
    assert cut.mode=="RGBA"
    a=cut.getchannel("A")
    # Remove near-transparent fringe without removing hairline product edges.
    a=a.point(lambda x:0 if x<20 else x)
    bbox=a.getbbox()
    assert bbox is not None
    pix=list(a.getdata())
    alpha_count=sum(1 for x in pix if x>=128)
    ratio=alpha_count/len(pix)
    bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
    assert 0.035<=ratio<=0.75,(fid,ratio)
    assert bw>=100 and bh>=150,(fid,bbox)
    isolated=Image.new("RGBA",cut.size,(0,0,0,0))
    cut.putalpha(a)
    isolated.alpha_composite(cut)
    isolated=isolated.crop(bbox)
    # A transparent PNG proves a real cutout; matching JPG is the Shopee-sized test.
    target=OUT/fid;target.mkdir()
    alpha_file=target/"01-real-alpha-segmented-product-QA.png"
    isolated.save(alpha_file,optimize=True)
    cover=Image.new("RGB",(1080,1080),"#ffffff")
    draw=ImageDraw.Draw(cover)
    draw.rounded_rectangle((50,48,1030,1030),radius=38,fill="#ffffff",outline="#ede7e8",width=2)
    draw.text((88,86),spec["name"],font=ft(38,True),fill="#383238")
    draw.text((88,148),spec["desc"],font=ft(27),fill="#746a70")
    contain=ImageOps.contain(isolated,(865,750),Image.Resampling.LANCZOS)
    pos=((1080-contain.width)//2,217+(750-contain.height)//2)
    cover.paste(contain,pos,contain)
    draw.text((88,994),"SEGMENTED SOURCE-PHOTO PREVIEW  |  QA ONLY",font=ft(19),fill="#988d91")
    jpg=target/"01-background-removed-hero-1080-QA.jpg"
    cover.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    with Image.open(jpg) as verify:
      verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
    assert jpg.stat().st_size<2000000
    entry.update({"status":"REAL_ALPHA_SEGMENTATION_RENDERED_VISUAL_QA_PENDING",
      "mask_alpha_coverage":round(ratio,4),"mask_bbox":list(bbox),
      "cutout_PNG":str(alpha_file.relative_to(OUT)),
      "white_hero_JPG":str(jpg.relative_to(OUT)),
      "JPG_sha256":hashfile(jpg),"JPG_bytes":jpg.stat().st_size})
  except Exception as e:
    entry["failure_type"]=type(e).__name__
    entry["failure"]=str(e)[:200]
  rows.append(entry)
# Side-by-side contact for honest inspect of product and segmentation clipping.
board=Image.new("RGB",(1740,500*len(rows)+58),"#f0f0f0")
draw=ImageDraw.Draw(board)
draw.text((18,17),"v2711 ORIGINAL (LEFT) vs ACTUAL ALPHA CUTOUT (RIGHT) | QA ONLY",font=ft(26,True),fill="#292929")
for i,r in enumerate(rows):
  with Image.open(ROOT/SPECS[i]["dir"]/r["family"]/sorted((ROOT/SPECS[i]["dir"]/r["family"]).glob("01-*.jpg"))[0].name) as im:
    original=im.convert("RGB").resize((440,440),Image.Resampling.LANCZOS)
  x0=16;y=62+i*500
  board.paste(original,(x0,y))
  draw.text((470,y+22),r["family"],font=ft(29,True),fill="#2d2d2d")
  draw.text((470,y+76),r["status"],font=ft(19),fill="#666666")
  if r.get("white_hero_JPG"):
    with Image.open(OUT/r["white_hero_JPG"]) as img:
      revised=img.convert("RGB").resize((440,440),Image.Resampling.LANCZOS)
    board.paste(revised,(1220,y))
proof=OUT/"v2711-real-cutout-side-by-side.jpg"
board.save(proof,"JPEG",quality=82,optimize=True)
(OUT/"v2711-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2711","baseline":"v2710",
  "candidate_families":len(SPECS),
  "true_segmentation_successes":sum(r["status"].startswith("REAL_ALPHA") for r in rows),
  "actual_new_1080_JPG_crops":sum(bool(r.get("white_hero_JPG")) for r in rows),
  "retail_approved_count":0,
  "photo_commercial_rights_verified":False,
  "exact_owned_stock_package_verified":False,
  "original_MK_logo_authenticated":False,
  "prior_80_photo_originals_modified":False,
  "previous_11_retail_approved_families_modified":False,
  "prior_55_public_urls_changed":False,
  "final_XLSX_shared":False,
  "candidates":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"candidates":len(rows),"actually_cut_out":report["true_segmentation_successes"],
  "statuses":[r["status"] for r in rows],"new_retail_approvals":0}))
