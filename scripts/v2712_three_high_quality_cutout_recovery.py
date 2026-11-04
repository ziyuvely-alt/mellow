#!/usr/bin/env python3
"""v2712 second-model foreground alpha segmentation for three formerly failed
pale/light product backgrounds. Saved originals unmodified, no fabricated products,
no fake brand logos, never automatically retail approve.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageFilter
from rembg import remove,new_session
import hashlib,json,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2712-3-failed-cutouts-high-quality-recovery"
assert not OUT.exists();OUT.mkdir(parents=True)
SRC=[
  {"family":"pending-04","dir":"v2706-six-archival-five-real-source-families",
   "title":"CLIO","subtitle":"Mesh Glow Mini Cushion 5g","crop":(145,205,920,958)},
  {"family":"pending-25","dir":"v2707-seven-remaining-archival-real-photo-family-sets",
   "title":"BIOHEAL BOH","subtitle":"NAD-PRIZCELL Glow Boost Cream 50mL","crop":(190,199,900,963)},
  {"family":"pending-22","dir":"v2707-seven-remaining-archival-real-photo-family-sets",
   "title":"OBgE","subtitle":"Max Waterful Sun Cream 300mL","crop":(230,193,843,968)}
]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,bold=False):return ImageFont.truetype(boldfile if bold else fontfile,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
entries=[]
for spec in SRC:
  fid=spec["family"]
  path=list((ROOT/spec["dir"]/fid).glob("01-*.jpg"))
  assert len(path)==1,(fid,path)
  path=path[0]
  with Image.open(path) as im:
    im.load();assert im.size==(1080,1080) and im.format=="JPEG"
    source=im.convert("RGBA")
  roi=source.crop(spec["crop"])
  record={"family":fid,"source":str(path),"source_sha256":sha(path),
    "source_crop":spec["crop"],"model":"isnet-general-use",
    "prior_v2711_result":"REJECTED_VISUAL_PRODUCT_PART_MISSING",
    "retail_approved":False,"status":"REJECTED_UNTIL_VISUAL_REVIEW"}
  try:
    segmented=remove(roi,session=session,alpha_matting=True,
       alpha_matting_foreground_threshold=230,
       alpha_matting_background_threshold=18,
       alpha_matting_erode_size=4)
    assert segmented.mode=="RGBA"
    mask=segmented.getchannel("A")
    bbox=mask.getbbox()
    assert bbox is not None
    data=list(mask.getdata())
    coverage=sum(a>=128 for a in data)/len(data)
    assert .04<coverage<.75,(coverage,fid)
    assert bbox[2]-bbox[0]>150 and bbox[3]-bbox[1]>280
    trimmed=segmented.crop(bbox)
    # No logo corner region in ROI; source background product graphics may be
    # kept, so this is quality-candidate only.
    sub=OUT/fid;sub.mkdir()
    png=sub/"01-actual-alpha-cutout-high-res-QA.png"
    trimmed.save(png,optimize=True)
    result=Image.new("RGB",(1080,1080),"#ffffff")
    d=ImageDraw.Draw(result)
    d.rounded_rectangle((54,54,1026,1026),radius=32,fill="#ffffff",outline="#e5dee2",width=2)
    d.text((105,105),spec["title"],font=ft(39,True),fill="#333333")
    d.text((105,164),spec["subtitle"],font=ft(25),fill="#777077")
    fitted=ImageOps.contain(trimmed,(865,775),Image.Resampling.LANCZOS)
    pos=((1080-fitted.width)//2,216+(775-fitted.height)//2)
    result.paste(fitted,pos,fitted)
    d.text((105,990),"ACTUAL FOREGROUND CUTOUT  |  QA ONLY",font=ft(19),fill="#9c9497")
    jpg=sub/"01-full-product-high-quality-cutout-1080-QA.jpg"
    result.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    assert jpg.stat().st_size<2_000_000
    with Image.open(jpg) as v:
      v.load();assert v.format=="JPEG" and v.size==(1080,1080)
    record.update({"status":"SECOND_MODEL_REAL_CUTOUT_RENDERED_REVIEW_REQUIRED",
      "mask_coverage":round(coverage,4),"mask_bbox":list(bbox),
      "transparent_png":str(png.relative_to(OUT)),
      "square_jpg":str(jpg.relative_to(OUT)),
      "jpg_sha256":sha(jpg)})
  except Exception as exc:
    record.update({"status":"REJECTED_MASK_FAILED_TECHNICAL_GATE","failure":str(exc)[:200],
      "exception":type(exc).__name__})
  entries.append(record)
canvas=Image.new("RGB",(1480,490*len(entries)+70),"#f0f0f0")
d=ImageDraw.Draw(canvas)
d.text((16,14),"v2712 SECOND-MODEL ACTUAL CUTOUTS / ORIGINAL vs RE-SEGMENTED / QA ONLY",font=ft(24,True),fill="#262626")
for i,item in enumerate(entries):
  with Image.open(ROOT/SRC[i]["dir"]/item["family"]/Path(item["source"]).name) as src:
    orig=src.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
  y=60+i*490;canvas.paste(orig,(15,y))
  d.text((467,y+15),item["family"],font=ft(32,True),fill="#333333")
  d.text((467,y+70),item["status"],font=ft(18),fill="#555555")
  if item.get("square_jpg"):
    with Image.open(OUT/item["square_jpg"]) as im:
      revision=im.convert("RGB").resize((430,430),Image.Resampling.LANCZOS)
    canvas.paste(revision,(1026,y))
proof=OUT/"v2712-original-vs-high-model-review.jpg"
canvas.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2712-review.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2712","baseline":"v2711",
  "attempted_families":3,
  "technically_rendered_cutout_candidates":sum(e["status"].startswith("SECOND_MODEL") for e in entries),
  "retail_approved":0,
  "original_11_approved_product_families_unchanged":True,
  "old_55_public_urls_unchanged":True,
  "prior_all_photos_and_v2711_assets_unchanged":True,
  "source_image_commercial_permissions_unverified":True,
  "real_owned_stock_variant_match_unverified":True,
  "approved_MK_logo_source_unavailable":True,
  "final_spreadsheet_shared":False,
  "products":entries}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"second_model_cutouts_rendered":manifest["technically_rendered_cutout_candidates"],
  "candidate_families":3,"sale_approved":0}))
