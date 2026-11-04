#!/usr/bin/env python3
"""v2717 actual photo-to-alpha segmentation for four not-yet-attempted QA families.
Original JPGs remain untouched. Source photo is NOT a legal license to publish.
Photo may depict multiple products/kit, so explicit human visual QA is required.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,base64,json
ROOT=Path("qa-review")
OUT=ROOT/"v2717-four-fresh-cushion-cream-real-alpha-candidates"
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 {"id":"pending-01","folder":"v2675-missha-two-five-frame-photo-sets","slot":1,
 "brand":"MISSHA","title":"Magic Cushion Cover Lasting","crop":(160,145,931,941),
 "hold":"Shade 21/23/25/27 and owned item generation not verified"},
 {"id":"pending-10","folder":"v2677-three-obge-five-JPG-source-led-QA-sets","slot":1,
 "brand":"OBgE","title":"Perfect Homme Cushion","crop":(160,170,932,945),
 "hold":"Source package may be 15g while inventory may be 13g; exact edition not proven"},
 {"id":"pending-14","folder":"v2675-missha-two-five-frame-photo-sets","slot":1,
 "brand":"MISSHA","title":"PDRN Firming Repair Cream 70mL","crop":(175,152,921,947),
 "hold":"Must match owned 70mL stock, not separate 70g foreign edition"},
 {"id":"pending-06","folder":"v2678-missha-clio-two-five-JPG-sets","slot":1,
 "brand":"CLIO","title":"Mesh Glow Essential Cushion","crop":(175,158,920,942),
 "hold":"A pictured Essential Cushion Set must not be represented as standalone unless verified"},
]
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
rows=[]
for case in CASES:
 srcs=list((ROOT/case["folder"]/case["id"]).glob(f"{case['slot']:02d}-*.jpg"))
 assert len(srcs)==1,(case["id"],[str(x) for x in srcs])
 src=srcs[0]
 with Image.open(src) as photo:
  photo.load()
  assert photo.size==(1080,1080) and photo.format=="JPEG"
  region=photo.convert("RGBA").crop(case["crop"])
 entry={"family":case["id"],"original_JPG":str(src),"original_sha256":sha(src),
        "crop":list(case["crop"]),"stock_hold":case["hold"],
        "status":"HOLD_VISUAL_QA_OR_MASK","retail_approved":False}
 try:
  cut=remove(region,session=model,alpha_matting=True,
             alpha_matting_foreground_threshold=230,
             alpha_matting_background_threshold=18,
             alpha_matting_erode_size=4)
  assert cut.mode=="RGBA"
  alpha=cut.getchannel("A");bbox=alpha.getbbox()
  if bbox is None:raise ValueError("No segmented foreground")
  fraction=sum(p>=128 for p in alpha.getdata())/(cut.width*cut.height)
  if not(.025<fraction<.80 and bbox[2]-bbox[0]>110 and bbox[3]-bbox[1]>160):
   raise ValueError(f"Mask geometry invalid: {fraction:.3f}, {bbox}")
  isolated=cut.crop(bbox)
  outdir=OUT/case["id"];outdir.mkdir()
  png=outdir/"01-actual-product-alpha-cutout-QA.png"
  isolated.save(png,optimize=True)
  jpg=outdir/"01-product-real-cutout-1080-JPG-QA.jpg"
  surface=Image.new("RGB",(1080,1080),"#ffffff")
  d=ImageDraw.Draw(surface)
  d.rounded_rectangle((50,50,1030,1030),radius=32,outline="#e9e5e5",width=2)
  d.text((92,91),case["brand"],font=ft(44,True),fill="#363238")
  size=31
  while d.textbbox((0,0),case["title"],font=ft(size))[2]>890:size-=1
  d.text((92,153),case["title"],font=ft(size),fill="#756b73")
  fitted=ImageOps.contain(isolated,(860,778),Image.Resampling.LANCZOS)
  xy=((1080-fitted.width)//2,209+(785-fitted.height)//2)
  surface.paste(fitted,xy,fitted)
  d.text((92,997),"REAL SOURCE CUTOUT  |  QA ONLY",font=ft(20),fill="#9f989c")
  surface.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  with Image.open(jpg) as test:
   test.load();assert test.format=="JPEG" and test.size==(1080,1080)
  entry.update({"status":"ALPHA_CANDIDATE_RENDERED_REQUIRES_VISUAL_QA",
                "source_mask_area_fraction":round(fraction,4),"bbox":list(bbox),
                "png":str(png.relative_to(OUT)),"jpg":str(jpg.relative_to(OUT)),
                "jpg_sha256":sha(jpg)})
 except Exception as exc:
  entry.update({"status":"HOLD_SEGMENTATION_FAILED","exception":type(exc).__name__,
               "error":str(exc)[:250]})
 rows.append(entry)
for page in range(2):
 sub=rows[page*2:(page+1)*2]
 canvas=Image.new("RGB",(1530,1050),"#f0f0f0")
 draw=ImageDraw.Draw(canvas)
 draw.text((16,18),f"v2717 FOUR NOT-YET-ATTEMPTED PRODUCTS / PAGE {page+1}",font=ft(24,True),fill="#2a282a")
 for ix,row in enumerate(sub):
  y=65+ix*480
  with Image.open(row["original_JPG"]) as im:
   left=im.convert("RGB").resize((422,422),Image.Resampling.LANCZOS)
  canvas.paste(left,(15,y))
  draw.text((455,y+15),row["family"],font=ft(31,True),fill="#2a282a")
  draw.text((455,y+72),row["status"],font=ft(18),fill="#595959")
  if row.get("jpg"):
   with Image.open(OUT/row["jpg"]) as im:
    right=im.convert("RGB").resize((422,422),Image.Resampling.LANCZOS)
   canvas.paste(right,(1090,y))
 proof=OUT/f"v2717-comparison-{page+1}.jpg"
 canvas.save(proof,"JPEG",quality=83,optimize=True)
 (OUT/f"v2717-comparison-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2717","baseline":"v2716","product_families_attempted":len(rows),
          "physically_saved_real_alpha_png_jpg_pairs":sum(bool(x.get("jpg")) for x in rows),
          "new_sale_approved":0,"source_photo_commercial_rights_verified":False,
          "exact_user_owned_stock_edition_verified":False,"original_MK_logo_available":False,
          "prior_11_approved_groups_modified":False,"prior_55_approved_public_URLs_modified":False,
          "original_archived_JPGs_modified":0,"prior_QA_artifacts_modified":0,
          "final_spreadsheet_shared":False,"products":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2717","families":4,
 "saved_png_jpg_pairs":manifest["physically_saved_real_alpha_png_jpg_pairs"],
 "statuses":[x["status"] for x in rows],"sales_approved":0}))
