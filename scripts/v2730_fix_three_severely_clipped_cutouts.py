#!/usr/bin/env python3
"""v2730 remediate only genuinely clipped or high-risk alpha-source product
scenes from v2729. Do not repeat the v2711/2715/2720 same narrow photo crop.
Use a wider original photo ROI (18/23) and a different already archived
single-product frame (26). Source bytes, 11 approved assets and 55 URLs frozen.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,base64,json
ROOT=Path("qa-review")
OUT=ROOT/"v2730-three-source-crop-and-alternate-photo-real-alpha-corrections"
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
  {
    "id":"pending-18","brand":"Dr.G","title":"Brightening Up Sun Plus 50mL",
    "source":"v2706-six-archival-five-real-source-families/pending-18/01-historical-real-art-photo-unchanged-QA.jpg",
    "crop":(120,84,916,1060),"prior_problem":"v2715 alpha bottom clipped, old narrow crop y<=965",
    "approach":"BROADER_SAME_AUTHENTIC_SOURCE_ROI"
  },
  {
    "id":"pending-23","brand":"OBgE","title":"Pore Zero Oil Control Sun Cream 50mL",
    "source":"v2680-six-brand-five-JPG-photo-led-batch/pending-23/01-actual-source-slot01-UNMODIFIED-QA.jpg",
    "crop":(100,75,910,1060),"prior_problem":"v2720 mask top/bottom clipping on y<=960",
    "approach":"BROADER_SAME_AUTHENTIC_SOURCE_ROI"
  },
  {
    "id":"pending-26","brand":"PIXEL PURE","title":"Gentle Gel-to-Foam Cleanser 145mL",
    "source":"v2706-six-archival-five-real-source-families/pending-26/04-historical-real-art-photo-unchanged-QA.jpg",
    "crop":(200,155,894,1065),"prior_problem":"v2711 old frame01 cropped bottle lower base; use real distinct frame04",
    "approach":"DIFFERENT_ARCHIVED_REAL_SOURCE_PHOTO"
  },
]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(boldfile if b else fontfile,n)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
records=[]
for c in CASES:
   src=ROOT/c["source"]
   assert src.is_file(),src
   entry={"family":c["id"],"product":c["title"],"source":str(src),
          "source_sha256":digest(src),"crop_xyxy":list(c["crop"]),
          "remediation":c["approach"],"previous_issue":c["prior_problem"],
          "status":"HOLD_SOURCE_OR_ALPHA_FAILURE","sale_approved":False}
   try:
      with Image.open(src) as orig:
         orig.load(); assert orig.format=="JPEG" and orig.size==(1080,1080),src
         region=orig.convert("RGBA").crop(c["crop"])
      alpha=remove(region,session=session,alpha_matting=True,
           alpha_matting_foreground_threshold=230,alpha_matting_background_threshold=18,
           alpha_matting_erode_size=4)
      if alpha.mode!="RGBA":raise ValueError("Missing real alpha channel")
      band=alpha.getchannel("A")
      bbox=band.getbbox()
      if not bbox:raise ValueError("No foreground found")
      coverage=sum(v>=128 for v in band.getdata())/(band.width*band.height)
      width=bbox[2]-bbox[0];height=bbox[3]-bbox[1]
      if not(.025<=coverage<=.86 and width>85 and height>240):
          raise ValueError(f"Mask did not isolate a plausible object: {coverage:.3f}, {bbox}")
      contact={
        "top":round(sum(band.getpixel((x,0))>=128 for x in range(band.width))/band.width,4),
        "bottom":round(sum(band.getpixel((x,band.height-1))>=128 for x in range(band.width))/band.width,4),
        "left":round(sum(band.getpixel((0,y))>=128 for y in range(band.height))/band.height,4),
        "right":round(sum(band.getpixel((band.width-1,y))>=128 for y in range(band.height))/band.height,4)}
      cropped=alpha.crop(bbox)
      folder=OUT/c["id"];folder.mkdir()
      png=folder/"01-recovered-product-foreground-alpha-QA.png"
      cropped.save(png,optimize=True)
      jpg=folder/"01-recovered-source-product-1080-hero-QA.jpg"
      canvas=Image.new("RGB",(1080,1080),"#ffffff")
      d=ImageDraw.Draw(canvas)
      d.rounded_rectangle((52,52,1028,1028),radius=36,outline="#eae5e5",width=2)
      d.text((98,99),c["brand"],font=font(43,True),fill="#343035")
      n=29
      while d.textbbox((0,0),c["title"],font=font(n))[2]>878 and n>19:n-=1
      d.text((98,161),c["title"],font=font(n),fill="#706970")
      fitted=ImageOps.contain(cropped,(860,785),Image.Resampling.LANCZOS)
      pos=((1080-fitted.width)//2,210+(785-fitted.height)//2)
      canvas.paste(fitted,pos,fitted)
      d.text((98,989),"ORIGINAL SOURCE PRODUCT CUTOUT   |   QA ONLY",font=font(18),fill="#988f94")
      canvas.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
      with Image.open(jpg) as verify:
         verify.load()
         assert verify.format=="JPEG" and verify.size==(1080,1080)
      if jpg.stat().st_size>=2_000_000:raise ValueError("JPG > 2MB")
      mask_reaches_product_boundary=max(contact.values())>.28
      entry.update({"status":"REAL_ALPHA_JPG_PNG_RENDERED_VISUAL_QA_PENDING",
        "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
        "png_sha256":digest(png),"jpg_sha256":digest(jpg),
        "mask_coverage":round(coverage,4),"mask_bbox":list(bbox),
        "edge_contact_original_ROI":contact,
        "warning":"CROP_EDGE_CONTACT_CHECK" if mask_reaches_product_boundary else None,
        "original_source_image_mutated":False})
   except Exception as ex:
      entry.update({"status":"HOLD_SEGMENTATION_FAILED_OR_SOURCE_NOT_VALID",
         "error_type":type(ex).__name__,"error":str(ex)[:240]})
   records.append(entry)
# Original vs new actual source proof.
sheet=Image.new("RGB",(1510,60+485*len(CASES)),"#f1f0ef")
d=ImageDraw.Draw(sheet)
d.text((16,12),"v2730 ONLY 3 SELECTED CUTOUT FIXES / NO ORIGINAL JPG REDRAW",font=font(25,True),fill="#2d2b2d")
for i,x in enumerate(records):
  y=56+485*i
  with Image.open(x["source"]) as src:
      old=src.convert("RGB").resize((428,428),Image.Resampling.LANCZOS)
  sheet.paste(old,(16,y))
  d.text((467,y+20),x["family"],font=font(31,True),fill="#333")
  d.text((467,y+73),x["status"],font=font(17),fill="#666")
  if x.get("jpg"):
    with Image.open(OUT/x["jpg"]) as im:
        curr=im.convert("RGB").resize((428,428),Image.Resampling.LANCZOS)
    sheet.paste(curr,(1060,y))
proof=OUT/"v2730-original-and-improved-three-source-QA.jpg"
sheet.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2730-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={
 "version":"v2730","baseline":"v2729",
 "attempted_genuinely_selected_families":len(records),
 "new_actual_png_JPG_pairs":sum(bool(x.get("jpg")) for x in records),
 "original_product_JPG_bytes_changed":0,
 "same_failed_segmentations_repeated":False,
 "new_retail_approved_families":0,
 "new_logo_generated":False,"licensing_proven":False,
 "stock_package_match_proven":False,
 "prior_11_approved_families_unchanged":True,
 "prior_55_public_urls_unchanged":True,"final_excel_shared":False,
 "results":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2730","attempted":len(records),"saved_pairs":manifest["new_actual_png_JPG_pairs"],
 "statuses":[x["status"] for x in records],"new_retail_approved":0}))
