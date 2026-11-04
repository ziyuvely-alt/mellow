#!/usr/bin/env python3
"""v2725 | Previously unattempted correct MISSHA serum 30mL single-source cutout.

Read saved exact-product v2696 source-04, not v2719 fact card.
Make an actual transparent PNG + Shopee-size JPG by neural foreground removal.
Check cropped geometry; never invent product packaging or a fake MK logo.
All outputs append-only QA; no customer-facing URL / release / spreadsheet.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
from rembg import remove, new_session
import base64,hashlib,json

root=Path("qa-review")
source=root/"v2696-missha-serum-official-gallery-proof/source-04-REVIEW-ONLY.jpg"
out=root/"v2725-missha-serum-30ml-true-single-bottle-cutout-QA"
assert source.is_file(), f"Original reviewed serum media missing: {source}"
assert not out.exists(), f"Never overwrite earlier QA: {out}"
out.mkdir(parents=True)

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reg="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False: ImageFont.truetype(bold if b else reg,n)
report={
 "version":"v2725","baseline":"v2724","family":"pending-13",
 "actual_product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
 "source_jpg":str(source),"source_sha256":sha(source),
 "source_visual_selection":"v2696 official single bottle media04",
 "previous_wrong_info_card_discarded":True,
 "other_cosmetics_or_gift_set_discarded":True,
 "source_photo_changed":False,
 "status":"HOLD_NO_RELEASE_UNTIL_VISUAL_REVIEW",
 "commercial_photo_reuse_permission_verified":False,
 "owned_stock_edition_verified":False,
 "round_MK_logo_verified":False,
 "retail_sale_approved":False,
 "approved_11_families_unchanged":True,
 "public_55_urls_unchanged":True,
 "final_spreadsheet_shared":False
}
try:
 with Image.open(source) as im:
  im.load()
  assert im.size==(1080,1080) and im.format=="JPEG", (im.size,im.format)
  original=im.convert("RGBA")
 # Constrain single-bottle region; exclude right-side decorative bubble and
 # surrounding decorative cosmetics, never crop a product's full body in output.
 roi=(105,90,652,1075)
 source_crop=original.crop(roi)
 isnet=new_session("isnet-general-use")
 isolated=remove(source_crop,session=isnet,alpha_matting=True,
   alpha_matting_foreground_threshold=230,
   alpha_matting_background_threshold=18,
   alpha_matting_erode_size=4)
 assert isolated.mode=="RGBA"
 alpha=isolated.getchannel("A")
 bbox=alpha.getbbox()
 assert bbox is not None,"empty foreground"
 coverage=sum(x>=128 for x in alpha.getdata())/(isolated.width*isolated.height)
 assert .07<coverage<.76, (coverage,bbox)
 width=bbox[2]-bbox[0];height=bbox[3]-bbox[1]
 assert width>115 and height>300,(width,height)
 # Reject if cropped to frame boundary: too risky to present as intact bottle.
 # (Some minimal masked edges are acceptable but not a completely clipped body.)
 w,h=isolated.size
 side_counts={}
 pix=alpha.load()
 for side in ("left","right","top","bottom"):
  if side=="left": n=sum(pix[0,y]>=80 for y in range(h));den=h
  elif side=="right":n=sum(pix[w-1,y]>=80 for y in range(h));den=h
  elif side=="top":n=sum(pix[x,0]>=80 for x in range(w));den=w
  else:n=sum(pix[x,h-1]>=80 for x in range(w));den=w
  side_counts[side]=round(n/den,4)
 assert max(side_counts.values())<.1,side_counts
 only_product=isolated.crop(bbox)
 png=out/"01-real-transparent-serum-30ml-QA.png"
 only_product.save(png,optimize=True)
 with Image.open(png) as v:
  v.load();assert v.mode=="RGBA" and v.format=="PNG"
 sheet=Image.new("RGB",(1080,1080),"white")
 pen=ImageDraw.Draw(sheet)
 pen.rounded_rectangle((49,48,1031,1032),radius=35,fill="white",outline="#e9e4e8",width=2)
 pen.text((102,106),"MISSHA",font=ft(44,True),fill="#36313a")
 pen.text((102,169),"PDRN NAD+ Firming Repair Serum 30mL",font=ft(25),fill="#655c63")
 hero=ImageOps.contain(only_product,(840,760),Image.Resampling.LANCZOS)
 at=((1080-hero.width)//2,216+(776-hero.height)//2)
 sheet.paste(hero,at,hero)
 pen.text((102,984),"AUTHENTIC PHOTO CUTOUT  |  QA ONLY",font=ft(20),fill="#8e888c")
 jpg=out/"01-real-1080-single-serum-hero-QA.jpg"
 sheet.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(jpg) as test:
  test.load();assert test.format=="JPEG" and test.size==(1080,1080)
 assert jpg.stat().st_size<2_000_000
 report.update({
  "status":"TRUE_ALPHA_PNG_AND_JPG_RENDERED_NEEDS_VISUAL_QA",
  "source_crop":list(roi),"mask_coverage":round(coverage,4),
  "mask_bbox":list(bbox),"mask_touching_frame_fraction":side_counts,
  "png_path":str(png.relative_to(out)),
  "jpg_path":str(jpg.relative_to(out)),
  "png_sha256":sha(png),"jpg_sha256":sha(jpg),"jpg_bytes":jpg.stat().st_size
 })
except Exception as e:
 report.update({"status":"HOLD_SINGLE_BOTTLE_MASK_FAILED",
                "exception":type(e).__name__,"error":str(e)[:230]})

if report.get("jpg_path"):
 frame=Image.new("RGB",(1510,580),"#f0f0ed")
 dr=ImageDraw.Draw(frame)
 dr.text((20,14),"v2725 EXACT 30mL ORIGINAL vs TRUE ALPHA CUTOUT / QA ONLY",
         font=ft(24,True),fill="#2b292c")
 with Image.open(source) as old:
  a=old.convert("RGB").resize((480,480),Image.Resampling.LANCZOS)
 with Image.open(out/report["jpg_path"]) as new:
  b=new.convert("RGB").resize((480,480),Image.Resampling.LANCZOS)
 frame.paste(a,(20,60));frame.paste(b,(1010,60))
 dr.text((524,105),"Original source 04",font=ft(30,True),fill="#343034")
 dr.text((524,170),"New source-only alpha hero",font=ft(23),fill="#605660")
 dr.text((524,252),"NO STOCK APPROVAL",font=ft(21),fill="#9b2d3e")
 proof=out/"v2725-photo-vs-real-cutout-proof.jpg"
 frame.save(proof,"JPEG",quality=83,optimize=True)
 (out/"v2725-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())

(out/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":report["version"],"family":report["family"],
                  "status":report["status"],
                  "new_real_photo_JPG":int(bool(report.get("jpg_path"))),
                  "new_retail_approvals":0}))
