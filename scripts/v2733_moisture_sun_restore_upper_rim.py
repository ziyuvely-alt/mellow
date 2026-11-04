#!/usr/bin/env python3
"""v2733: Recover one 50mL Dr.G suncream top rim after v2732 alpha edge warning.

pending-17 uses archived photo scene 04, extending source crop upward to retain sealed rim. v2732 pending-15 is already done and is not regenerated. Original bytes, 11 approved families and all
55 URLs are immutable. Outputs are QA only, not commercial release.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import hashlib,base64,json,numpy as np
R=Path("qa-review")
D=R/"v2733-moisture-sun-top-edge-extended-source-photo-QA"
assert not D.exists()
D.mkdir(parents=True)
CASES=[
 {"family":"pending-17","brand":"Dr.G",
  "product":"Brightening Up Moisture Sun 50mL",
  "source":"v2672-two-five-JPG-real-scene-sets/pending-17/04-original-QA.jpg",
  "crop":[180,55,867,1060],"reason":"Extend top crop from y180 to y55 to retain full sealed upper rim in archived frame04, no new source"}
]
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(FB if b else FR,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
session=new_session("isnet-general-use")
rows=[]
for item in CASES:
  source=R/item["source"]
  assert source.is_file(),source
  with Image.open(source) as img:
    img.load()
    assert img.format=="JPEG" and img.size==(1080,1080)
    roi=img.convert("RGBA").crop(tuple(item["crop"]))
  result={"family":item["family"],"product":item["product"],
    "source_JPG":str(source),"source_sha256":sha(source),
    "source_crop_xyxy":item["crop"],"why_new_approach":item["reason"],
    "retail_approved":False,"status":"HOLD_INCOMPLETE"}
  try:
    cut=remove(roi,session=session,alpha_matting=True,
        alpha_matting_foreground_threshold=230,
        alpha_matting_background_threshold=18,
        alpha_matting_erode_size=4)
    assert cut.mode=="RGBA"
    alpha=np.asarray(cut.getchannel("A"))
    mask=(alpha>=128)
    ratio=float(np.mean(mask))
    from PIL import Image as PILImage
    bbox=cut.getchannel("A").getbbox()
    assert bbox
    bw,bh=bbox[2]-bbox[0],bbox[3]-bbox[1]
    assert .03<ratio<.80 and bw>=125 and bh>=240,(ratio,bbox)
    # Before trimming, check if the product runs beyond input crop boundaries.
    limits={"top":round(float(np.mean(mask[0,:])),4),
      "bottom":round(float(np.mean(mask[-1,:])),4),
      "left":round(float(np.mean(mask[:,0])),4),
      "right":round(float(np.mean(mask[:,-1])),4)}
    isolated=cut.crop(bbox)
    folder=D/item["family"];folder.mkdir()
    png=folder/"01-real-photographed-product-transparent-QA.png"
    isolated.save(png,optimize=True)
    canvas=Image.new("RGB",(1080,1080),"#ffffff")
    draw=ImageDraw.Draw(canvas)
    draw.rounded_rectangle((55,53,1025,1027),radius=33,outline="#e8e3e5",width=2)
    draw.text((99,99),"Dr.G",font=ft(44,True),fill="#383337")
    draw.text((99,164),item["product"],font=ft(27),fill="#746d73")
    obj=ImageOps.contain(isolated,(865,775),Image.Resampling.LANCZOS)
    canvas.paste(obj,((1080-obj.width)//2,219+(775-obj.height)//2),obj)
    draw.text((99,990),"REAL PHOTOGRAPH ALPHA  |  REVISED QA ONLY",font=ft(19),fill="#979095")
    jpg=folder/"01-real-photographed-product-1080-JPG-QA.jpg"
    canvas.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    assert jpg.stat().st_size<2_000_000
    with Image.open(jpg) as verify:
      verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
    result.update({"status":"REAL_ALPHA_PNG_JPG_STAGED_VISUAL_REVIEW",
        "mask_alpha_coverage":round(ratio,4),"original_roi_boundary_alpha_coverage":limits,
        "input_crop_bbox":list(bbox),
        "png":str(png.relative_to(D)),"jpg":str(jpg.relative_to(D)),
        "png_sha256":sha(png),"jpg_sha256":sha(jpg),"jpg_bytes":jpg.stat().st_size,
        "warning":"INPUT_EDGE_TOUCH_REVIEW" if max(limits.values())>.15 else None})
  except Exception as e:
    result.update({"status":"HOLD_SOURCE_OR_ALPHA_FAILED",
      "error_type":type(e).__name__,"reason":str(e)[:260]})
  rows.append(result)
# side-by-side image proof
board=Image.new("RGB",(1550,1040),"#f1f0ef")
d=ImageDraw.Draw(board)
d.text((15,14),"v2733 ORIGINAL VS NEW TRUE ALPHA CUTOUT / QA ONLY",font=ft(27,True),fill="#292929")
for n,row in enumerate(rows):
  y=64+n*484
  with Image.open(row["source_JPG"]) as img:ori=img.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
  board.paste(ori,(17,y))
  d.text((466,y+12),row["family"],font=ft(30,True),fill="#292929")
  d.text((466,y+64),row["status"],font=ft(18),fill="#656060")
  if row.get("jpg"):
    with Image.open(D/row["jpg"]) as img:new=img.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
    board.paste(new,(1112,y))
p=D/"v2733-one-DrG-original-vs-revised-hero.jpg"
board.save(p,"JPEG",quality=83,optimize=True)
(D/"v2733-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
report={"version":"v2733","baseline":"v2732","product_families":1,
  "genuine_new_alpha_png_jpg_pairs":sum(bool(x.get("jpg")) for x in rows),
  "actual_original_photo_bytes_changed":0,"regenerated_existing_successful_cutouts":0,
  "new_sales_approved":0,
  "old_11_approved_product_families_preserved":True,"old_55_image_URLs_preserved":True,
  "source_photos_commercial_reuse_rights_not_confirmed":True,
  "exact_owned_stock_edition_not_proven":True,
  "original_MK_logo_not_available":True,
  "no_final_XLSX_shared":True,"rows":rows}
(D/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2733","sources_processed":2,
 "saved_pairs":report["genuine_new_alpha_png_jpg_pairs"],
 "outcomes":[x["status"] for x in rows],"new_sale_approvals":0}))
