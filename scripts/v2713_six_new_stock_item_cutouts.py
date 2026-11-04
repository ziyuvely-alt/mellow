#!/usr/bin/env python3
"""v2713 batch actual alpha segmentation of SIX NEW original product hero JPGs.
Source product photograph pixels only; no invented packaging or MK badge.
Each output stays QA HOLD until direct visual validation and photo-rights check.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,json,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2713-six-new-product-hero-real-alpha-cutouts"
assert not OUT.exists()
OUT.mkdir(parents=True)
SPECS=[
 ("pending-16","v2707-seven-remaining-archival-real-photo-family-sets","Dr.G","R.E.D Blemish Soothing Cream 70mL",(180,183,920,956)),
 ("pending-24","v2707-seven-remaining-archival-real-photo-family-sets","BIOHEAL BOH","NAD Glow Power Serum 30mL",(200,182,890,959)),
 ("pending-27","v2707-seven-remaining-archival-real-photo-family-sets","PIXEL PURE","Soothing Ampoule Toner 200mL",(210,185,883,950)),
 ("pending-28","v2707-seven-remaining-archival-real-photo-family-sets","PIXEL PURE","Glow Cleansing Serum Pads 70ea",(190,182,894,953)),
 ("pending-29","v2706-six-archival-five-real-source-families","PIXEL PURE","Radiance Aqua Soothing Cream 50mL",(190,180,902,951)),
 ("pending-30","v2707-seven-remaining-archival-real-photo-family-sets","PIXEL PURE","Aura Radiance Serum 50mL",(212,180,884,960))
]
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font=lambda n,b=False:ImageFont.truetype(BOLD if b else REG,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
rows=[]
for fid,directory,brand,description,crop_box in SPECS:
 srcs=list((ROOT/directory/fid).glob("01-*.jpg"))
 assert len(srcs)==1,(fid,srcs)
 src=srcs[0]
 with Image.open(src) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
  part=im.convert("RGBA").crop(crop_box)
 rec={"family":fid,"brand":brand,"product":description,"source_JPG":str(src),
  "source_sha256":sha(src),"original_source_crop":list(crop_box),
  "model":"isnet-general-use","status":"HOLD_REJECTED_UNTIL_QA"}
 try:
  cut=remove(part,session=model,alpha_matting=True,
      alpha_matting_foreground_threshold=230,
      alpha_matting_background_threshold=18,
      alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  channel=cut.getchannel("A")
  bbox=channel.getbbox()
  assert bbox is not None
  values=list(channel.getdata())
  coverage=sum(x>=128 for x in values)/len(values)
  bw=bbox[2]-bbox[0];bh=bbox[3]-bbox[1]
  assert .035<=coverage<=.78 and bw>=120 and bh>=230,(fid,coverage,bbox)
  item_dir=OUT/fid;item_dir.mkdir()
  extracted=cut.crop(bbox)
  png=item_dir/"01-truly-transparent-product-QA.png"
  extracted.save(png,optimize=True)
  jpg=item_dir/"01-product-only-1080white-hero-QA.jpg"
  square=Image.new("RGB",(1080,1080),"#ffffff")
  d=ImageDraw.Draw(square)
  d.rounded_rectangle((54,54,1026,1026),radius=35,outline="#e8e3e5",width=2)
  d.text((95,99),brand,font=font(42,True),fill="#373239")
  size=28
  while d.textbbox((0,0),description,font=font(size))[2]>890 and size>18:size-=1
  d.text((95,159),description,font=font(size),fill="#777078")
  fit=ImageOps.contain(extracted,(855,777),Image.Resampling.LANCZOS)
  position=((1080-fit.width)//2,207+(778-fit.height)//2)
  square.paste(fit,position,fit)
  d.text((95,994),"REAL PRODUCT PHOTO CUTOUT  |  QA ONLY",font=font(19),fill="#9b8b93")
  square.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
  with Image.open(jpg) as verify:
   verify.load()
   assert verify.size==(1080,1080) and verify.format=="JPEG"
  assert jpg.stat().st_size<2000000
  rec.update({"status":"ACTUAL_ALPHA_CUTOUT_RENDERED_VISUAL_QA_PENDING",
     "mask_alpha_coverage":round(coverage,4),"mask_bbox":list(bbox),
     "transparent_PNG":str(png.relative_to(OUT)),
     "JPG":str(jpg.relative_to(OUT)),"JPG_sha256":sha(jpg),"bytes":jpg.stat().st_size})
 except Exception as e:
  rec.update({"status":"HOLD_MASK_OR_SOURCE_FAILED","error_type":type(e).__name__,
              "error":str(e)[:240]})
 rows.append(rec)
for page in range(2):
 group=rows[page*3:(page+1)*3]
 canvas=Image.new("RGB",(1500,1530),"#f0f0ee")
 draw=ImageDraw.Draw(canvas)
 draw.text((20,16),f"v2713 ORIGINAL VS REAL CUTOUT / PAGE {page+1} / REVIEW ONLY",font=font(25,True),fill="#333333")
 for ix,rec in enumerate(group):
  with Image.open(ROOT/SPECS[page*3+ix][1]/rec["family"]/Path(rec["source_JPG"]).name) as im:
   original=im.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
  y=57+ix*488
  canvas.paste(original,(20,y))
  draw.text((460,y+15),rec["family"],font=font(29,True),fill="#333333")
  draw.text((460,y+65),rec["status"],font=font(17),fill="#666666")
  if rec.get("JPG"):
   with Image.open(OUT/rec["JPG"]) as im:
    revised=im.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
   canvas.paste(revised,(1060,y))
 p=OUT/f"v2713-proof-page-{page+1}.jpg"
 canvas.save(p,"JPEG",quality=82,optimize=True)
 (OUT/f"v2713-proof-page-{page+1}.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
manifest={"version":"v2713","baseline":"v2712","candidates":rows,
 "attempted_new_families":6,
 "actual_alpha_png_and_jpg_pairs":sum(bool(x.get("JPG")) for x in rows),
 "approved_for_sale":0,"exact_owned_stock_edition_verified":False,
 "photos_reuse_rights_verified":False,"MK_original_logo_verified":False,
 "existing_11_published_families_mutated":False,"existing_55_public_urls_changed":False,
 "existing_80_original_JPGs_reencoded":0,"final_excel_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"families":6,"rendered":manifest["actual_alpha_png_and_jpg_pairs"],
 "statuses":[x["status"] for x in rows],"new_retail_approved":0}))
