#!/usr/bin/env python3
"""v2754. Source-only recovery and actual alpha candidates for the three
PERIPERA PERITAGE 12/13/14 older-collection variants missing real bottle photos.

Only user-facing original product photo facts, NO generated products, no
invented swatches, no source-rights claim. All outputs private QA, not for
commercial upload; immutable prior 55 URLs and completed photo assets.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
from rembg import remove,new_session
import base64,hashlib,json,requests
OUT=Path("qa-review/v2754-peripera-peritage-three-missing-bottle-source-QA")
assert not OUT.exists()
OUT.mkdir(parents=True)
# Three independently identified image sources; retain exact URL in report.
CASES=[
 {"shade":"12","name":"Warm-gorithm","source_page":"https://lacosmetique.com.au/products/ink-mood-glowy-tint",
  "source_url":"https://lacosmetique.com.au/cdn/shop/files/69_8417969c-7984-487c-9262-4d00b8f40b2b.png?v=1754439487&width=1946",
  "region":[0.06,0.05,0.74,0.96],"source_note":"Legacy Peritage shade12 pink product tube plus actual applicator"},
 {"shade":"13","name":"Berry Pretty","source_page":"https://officialnamane.com/products/ink-mood-glowy-tint-peritage-collection",
  "source_url":"https://officialnamane.com/cdn/shop/files/PERIPERA_-_Ink_Mood_Glowy_Tint_Peritage_Collection_13_berry_pretty.jpg?v=1749751711&width=1200",
  "region":[0.01,0.01,0.80,0.98],"source_note":"Legacy Peritage shade13 ribboned tube and applicator"},
 {"shade":"14","name":"Follow Rose","source_page":"https://truekbeautystore.com/products/peripera-ink-mood-glowy-tint-09-nude-to-heart",
  "source_url":"https://truekbeautystore.com/cdn/shop/files/PERIPERA_-_INK_MOOD_GLOWY_TINT_14_-_FOLLOW_ROSE-PIX4.png?v=1743147135&width=1920",
  "region":[0.32,0.02,0.88,0.98],"source_note":"Legacy Peritage shade14 ribboned closed tube, background swatch excluded by crop"}
]
HDR={"User-Agent":"Mozilla/5.0 (compatible; ShopeeCandidateProof/1.0)","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*"}
fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldpath="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,b=False):return ImageFont.truetype(boldpath if b else fontpath,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
try: session=new_session("isnet-general-use")
except Exception:session=None
rows=[]
for spec in CASES:
 sh=spec["shade"]
 itemdir=OUT/f"shade-{sh}";itemdir.mkdir()
 row={"shade":sh,"legacy_product_name":spec["name"],
      "source_page":spec["source_page"],"source_url":spec["source_url"],
      "source_note":spec["source_note"],"source_is_peritage_not_26AD":True,
      "commercial_photo_rights_verified":False,
      "owned_inventory_variant_verified":False,
      "retail_approved":False,
      "status":"HOLD_SOURCE_DOWNLOAD"}
 try:
  resp=requests.get(spec["source_url"],headers=HDR,timeout=17)
  resp.raise_for_status()
  if len(resp.content)>8500000:raise ValueError("Original photo larger than safe source limit")
  original=Image.open(BytesIO(resp.content))
  original.load()
  if min(original.size)<460:raise ValueError("Original image too small for genuine product comparison")
  im=ImageOps.exif_transpose(original).convert("RGB")
  raw=itemdir/f"{sh}-unmodified-original-source-bytes-QA{'.png' if original.format=='PNG' else '.jpg'}"
  raw.write_bytes(resp.content)
  prepared=Image.new("RGB",(1080,1080),"white")
  fitted=ImageOps.contain(im,(1050,1050),Image.Resampling.LANCZOS)
  prepared.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
  preview=itemdir/f"{sh}-old-peritage-exact-source-1080-QA.jpg"
  prepared.save(preview,"JPEG",quality=89,optimize=True)
  assert preview.stat().st_size<2_000_000
  row.update({"status":"SOURCE_PHOTO_CAPTURED_NO_SALE_RIGHTS",
    "raw_photo":str(raw.relative_to(OUT)),"prepared_source_JPG":str(preview.relative_to(OUT)),
    "source_dimensions":list(im.size),"raw_sha256":sha(raw),"preview_sha256":sha(preview)})
  reg=spec["region"]
  region=im.crop((round(reg[0]*im.width),round(reg[1]*im.height),
                  round(reg[2]*im.width),round(reg[3]*im.height)))
  if session is None:raise ValueError("Foreground segmentation dependency unavailable")
  removed=remove(region.convert("RGBA"),session=session,
    alpha_matting=True,alpha_matting_foreground_threshold=230,
    alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
  if removed.mode!="RGBA":raise ValueError("No alpha channel")
  alp=removed.getchannel("A")
  bb=alp.getbbox()
  if bb is None:raise ValueError("No segmented foreground")
  fraction=sum(p>=128 for p in alp.getdata())/(alp.width*alp.height)
  if not(.015<fraction<.84 and bb[2]-bb[0]>95 and bb[3]-bb[1]>180):
    raise ValueError(f"Mask geometry not credible: {fraction:.3f},{bb}")
  isolated=removed.crop(bb)
  png=itemdir/f"{sh}-real-photo-alpha-only-QA.png"
  isolated.save(png,optimize=True)
  card=Image.new("RGB",(1080,1080),"white")
  d=ImageDraw.Draw(card)
  d.rounded_rectangle((55,52,1025,1027),radius=32,outline="#ebe4e9",width=2)
  d.text((94,95),"PERIPERA",font=ft(40,True),fill="#44333c")
  d.text((94,158),f"Old Ink Mood Glowy Tint #{sh} {spec['name']}",font=ft(26),fill="#7b6c76")
  thumb=ImageOps.contain(isolated,(860,760),Image.Resampling.LANCZOS)
  card.paste(thumb,((1080-thumb.width)//2,216+(760-thumb.height)//2),thumb)
  d.text((94,994),"SOURCE PRODUCT CUTOUT  |  QA ONLY",font=ft(18),fill="#a19aa0")
  jpg=itemdir/f"{sh}-old-peritage-true-alpha-1080-QA.jpg"
  card.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
  assert jpg.stat().st_size<2_000_000
  row.update({"status":"REAL_PHOTO_CUTOUT_RENDERED_NEEDS_VISUAL_QA",
    "cutout_png":str(png.relative_to(OUT)),"cutout_jpg":str(jpg.relative_to(OUT)),
    "alpha_coverage":round(fraction,4),"cutout_jpg_sha256":sha(jpg)})
 except Exception as e:
  row.update({"error_type":type(e).__name__,"error":str(e)[:190]})
 rows.append(row)
board=Image.new("RGB",(1600,1520),"#f1f0ef")
d=ImageDraw.Draw(board)
d.text((16,18),"v2754 PERITAGE 12/13/14 | REAL EDITION-SPECIFIC BOTTLE PHOTOS | QA ONLY",font=ft(24,True),fill="#343034")
for i,r in enumerate(rows):
 y=65+i*485
 d.text((18,y+16),f"#{r['shade']}",font=ft(30,True),fill="#44313b")
 d.text((18,y+65),r["status"],font=ft(17),fill="#60545e")
 if r.get("prepared_source_JPG"):
  with Image.open(OUT/r["prepared_source_JPG"]) as im:
   left=im.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
  board.paste(left,(245,y))
 if r.get("cutout_jpg"):
  with Image.open(OUT/r["cutout_jpg"]) as im:
   right=im.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
  board.paste(right,(1130,y))
proof=OUT/"v2754-three-legacy-product-only-source-versus-mask.jpg"
board.save(proof,"JPEG",quality=81,optimize=True)
(OUT/"v2754-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={"version":"v2754","baseline":"v2753","family":"pending-08",
 "missing_old_peritage_shades_attempted":["12","13","14"],
 "actual_photo_sources_captured":sum(bool(x.get("raw_photo")) for x in rows),
 "actual_png_jpg_alpha_pairs_captured":sum(bool(x.get("cutout_png")) for x in rows),
 "same_26AD_new_edition_not_used":True,"unverified_photos_not_published":True,
 "original_55_public_urls_unchanged":True,"approved_previous_11_families_unchanged":True,
 "commercial_photo_rights_proven":False,"physical_stock_package_proven":False,
 "original_MK_brand_logo_verified":False,"retail_approved_new":0,"final_XLSX_not_shared":True,
 "rows":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2754","source_photos":report["actual_photo_sources_captured"],
"alpha_pairs":report["actual_png_jpg_alpha_pairs_captured"],
"statuses":[x["status"] for x in rows],"new_sale_approvals":0}))
