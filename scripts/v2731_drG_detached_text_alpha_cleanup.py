#!/usr/bin/env python3
"""v2731: SAFELY attempt to remove detached leftover text near a real Dr.G
Brightening Up Sun Plus 50mL photo cutout from v2730.

Never call the segmentation model again, invent any product pixels, remove
connected product parts, fabricate the MK mark or edit the original image.
All changes are in a newly versioned QA directory, NOT public assets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import cv2, hashlib, json, base64

ROOT=Path("qa-review")
SRC=ROOT/"v2730-three-source-crop-and-alternate-photo-real-alpha-corrections"/"pending-18"/"01-recovered-product-foreground-alpha-QA.png"
OUT=ROOT/"v2731-drG-brightening-sun-plus-detached-text-alpha-repair"
assert SRC.is_file() and not OUT.exists(), "Source not found or output folder already exists"
OUT.mkdir(parents=True)
hash_of=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(BOLD if b else REG,n)
report={
 "version":"v2731",
 "baseline":"v2730",
 "family":"pending-18",
 "product":"Dr.G Brightening Up Sun Plus 50mL",
 "source_png":str(SRC),"source_png_sha256":hash_of(SRC),
 "prior_original_PNG_unchanged":True,
 "prior_original_JPG_unchanged":True,
 "prior_11_approved_groups_unchanged":True,
 "prior_55_public_URLs_unchanged":True,
 "commercial_photo_rights_verified":False,
 "owned_stock_generation_verified":False,
 "authentic_MK_logo_verified":False,
 "retail_approved":False,
 "final_XLSX_shared":False,
 "method":"Existing transparency mask connected-component filtering only; original RGB pixels unchanged",
}
with Image.open(SRC) as pic:
    pic.load()
    assert pic.mode=="RGBA"
    source=np.array(pic).copy()
alpha=source[:,:,3]
binary=np.uint8(alpha>=128)
n,components,stats,_=cv2.connectedComponentsWithStats(binary,connectivity=8)
islands=sorted([
 {"id":i,"area":int(stats[i,cv2.CC_STAT_AREA]),
  "bbox_xywh":[int(stats[i,j]) for j in range(4)]}
 for i in range(1,n) if int(stats[i,cv2.CC_STAT_AREA])>=15
],key=lambda z:z["area"],reverse=True)
report["components_15_pixels_or_more"]=islands[:20]
report["source_size"]=[int(source.shape[1]),int(source.shape[0])]
repaired=None
try:
    if len(islands)<2:
        raise ValueError("No detached alpha components. Do not strip connected product pixels.")
    leading=islands[0]
    x,y,w,h=leading["bbox_xywh"]
    if not(w>=130 and h>=230):
        raise ValueError("Largest component does not look like a complete bottle.")
    small_area=sum(z["area"] for z in islands[1:])
    ratio=small_area/max(leading["area"],1)
    report["other_island_to_main_ratio"]=round(ratio,5)
    if ratio>.18:
        raise ValueError("Too much secondary alpha; may contain a genuine disconnected product component.")
    product_labels=np.uint8(components==leading["id"])
    # Keep pixels in a small dilated edge band to preserve semitransparent
    # anti-aliased product contours without bringing back distant letter blobs.
    neighborhood=cv2.dilate(product_labels,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    new_alpha=np.where(neighborhood>0,alpha,0).astype(np.uint8)
    removed=int(np.count_nonzero((alpha>=32)&(new_alpha<32)))
    original_visible=int(np.count_nonzero(alpha>=32))
    report["alpha_pixels_removed"]=removed
    report["alpha_visible_removed_ratio"]=round(removed/max(1,original_visible),5)
    if removed<35:
        raise ValueError("No meaningful detached lettering was removed; don't mark as repaired.")
    out=source.copy()
    out[:,:,3]=new_alpha
    assert np.array_equal(out[:,:,:3],source[:,:,:3]),"RGB product pixels must remain unchanged"
    img=Image.fromarray(out,"RGBA")
    bbox=img.getchannel("A").getbbox()
    if not bbox:raise ValueError("Masked image empty")
    img=img.crop(bbox)
    png=OUT/"01-real-DrG-source-alpha-detached-letters-only-fixed-QA.png"
    img.save(png,optimize=True)
    canvas=Image.new("RGB",(1080,1080),"white")
    d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((54,52,1026,1028),radius=36,outline="#e9e5e6",width=2)
    d.text((98,97),"Dr.G",font=font(43,True),fill="#393439")
    d.text((98,160),"Brightening Up Sun Plus 50mL",font=font(26),fill="#746a72")
    fitted=ImageOps.contain(img,(860,784),Image.Resampling.LANCZOS)
    canvas.paste(fitted,((1080-fitted.width)//2,212+(784-fitted.height)//2),fitted)
    d.text((98,991),"PRODUCT PHOTO ALPHA REPAIR  |  QA ONLY",font=font(18),fill="#958f93")
    jpg=OUT/"01-real-DrG-no-floating-letters-1080-QA.jpg"
    canvas.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    with Image.open(jpg) as check:
        check.load()
        assert check.size==(1080,1080) and check.format=="JPEG"
    assert jpg.stat().st_size<2_000_000
    report.update({
       "status":"DETACHED_ALPHA_REMOVED_PHYSICAL_OUTPUT_VISUAL_QA_PENDING",
       "new_png_file":str(png.relative_to(OUT)),"new_png_sha256":hash_of(png),
       "new_jpg_file":str(jpg.relative_to(OUT)),"new_jpg_sha256":hash_of(jpg)
    })
    repaired=img
except Exception as exc:
    report.update({"status":"HOLD_UNSAFE_TO_EDIT_WITH_CONNECTED_COMPONENT_FILTER",
       "exception_type":type(exc).__name__,"reason":str(exc)[:260]})

# Reliable visual proof even if no repair occurred.
board=Image.new("RGB",(1690,635),"#f1f0ef")
d=ImageDraw.Draw(board)
d.text((18,14),"v2731 ORIGINAL ALPHA vs DETACHED-ISLAND CLEANUP  |  QA ONLY",font=font(24,True),fill="#343035")
for idx,label in enumerate(("BEFORE","AFTER (IF SAFE)")):
    x=21+idx*835
    tile=Image.new("RGBA",(685,530),(255,255,255,255))
    grid=ImageDraw.Draw(tile)
    for yy in range(0,530,30):
        for xx in range(0,685,30):
            if (xx//30+yy//30)%2:grid.rectangle((xx,yy,xx+29,yy+29),fill="#e9e7e9")
    with Image.open(SRC) as original:
        obj=original.convert("RGBA") if idx==0 or repaired is None else repaired
    fitted=ImageOps.contain(obj,(610,490),Image.Resampling.LANCZOS)
    tile.alpha_composite(fitted,((685-fitted.width)//2,(530-fitted.height)//2))
    board.paste(tile.convert("RGB"),(x,65))
    d.text((x+9,596),label,font=font(21,True),fill="#373138")
proof=OUT/"v2731-transparent-product-before-after.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2731-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2731","family":"pending-18",
 "status":report["status"],"removed_visible_alpha":report.get("alpha_pixels_removed",0),
 "new_real_png_jpg_pairs":1 if repaired is not None else 0,"retail_approved":0}))
