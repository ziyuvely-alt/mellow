#!/usr/bin/env python3
"""v2714 repair exactly two previously unusable REAL product cutouts:
1) BIOHEAL BOH serum: remove small detached background/extra red blob with
connected component segmentation of the previously saved genuine PNG alpha.
2) PIXEL PURE cleansing pad: switch to archived source frame 02 (NOT previously
failed frame 01) and use actual ISNet alpha segmentation.

Never alter original source, v2713, retail URLs, or add a fake logo/product.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
import cv2,numpy as np
import hashlib,json,base64
ROOT=Path("qa-review")
OUT=ROOT/"v2714-serum-alpha-component-and-pad-alternate-photo"
assert not OUT.exists();OUT.mkdir(parents=True)
REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def f(n,b=False):return ImageFont.truetype(BOLD if b else REG,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def render_cutout(rgba,title,desc,path):
    img=Image.new("RGB",(1080,1080),"white")
    d=ImageDraw.Draw(img)
    d.rounded_rectangle((54,54,1026,1026),radius=34,outline="#ebe5e8",width=2)
    d.text((95,102),title,font=f(40,True),fill="#383239")
    d.text((95,165),desc,font=f(27),fill="#746b72")
    size=ImageOps.contain(rgba,(855,775),Image.Resampling.LANCZOS)
    xy=((1080-size.width)//2,214+(780-size.height)//2)
    img.paste(size,xy,size)
    d.text((95,994),"REAL PRODUCT PHOTO  |  ALPHA QA ONLY",font=f(18),fill="#918b8d")
    img.save(path,"JPEG",quality=93,optimize=True,subsampling=0)
    assert path.stat().st_size<2_000_000
    with Image.open(path) as test:
      test.load();assert test.format=="JPEG" and test.size==(1080,1080)

# 1. Preserve main component only, but never silently delete large pieces.
p24=ROOT/"v2713-six-new-product-hero-real-alpha-cutouts"/"pending-24"/"01-truly-transparent-product-QA.png"
assert p24.exists()
item24={"family":"pending-24","operation":"remove-detached-auxiliary-alpha-component",
"source":str(p24),"source_sha256":sha(p24),"status":"HOLD"}
try:
    with Image.open(p24) as im:rgba=im.convert("RGBA")
    arr=np.array(rgba)
    a=arr[:,:,3]
    binary=np.uint8(a>=90)
    n,component,stats,centroids=cv2.connectedComponentsWithStats(binary,connectivity=8)
    parts=sorted([{"label":i,"area":int(stats[i,cv2.CC_STAT_AREA])}
       for i in range(1,n) if int(stats[i,cv2.CC_STAT_AREA])>=25],
       key=lambda x:x["area"],reverse=True)
    assert parts and parts[0]["area"]>22000,parts[:5]
    largest=parts[0]["label"]
    # Other islands must be much smaller than the real bottle or this strategy is unsafe.
    leftover=sum(x["area"] for x in parts[1:])
    ratio=leftover/parts[0]["area"]
    assert ratio<.16,(ratio,parts[:5])
    arr[:,:,3][component!=largest]=0
    revised=Image.fromarray(arr,"RGBA")
    bbox=revised.getchannel("A").getbbox();assert bbox
    revised=revised.crop(bbox)
    dst=OUT/"pending-24";dst.mkdir()
    png=dst/"01-cleaned-real-alpha-isolated-serum-QA.png"
    revised.save(png,optimize=True)
    jpg=dst/"01-real-serum-without-detached-red-blob-1080-QA.jpg"
    render_cutout(revised,"BIOHEAL BOH","NAD Glow Power Serum 30mL",jpg)
    item24.update({"status":"REAL_ALPHA_CLEANUP_RENDERED_VISUAL_QA_PENDING",
       "main_area":parts[0]["area"],"removed_small_islands_area":leftover,
       "removed_ratio":round(ratio,4),"png":str(png.relative_to(OUT)),
       "jpg":str(jpg.relative_to(OUT)),"jpg_sha256":sha(jpg)})
except Exception as exc:
    item24.update({"status":"HOLD_ALPHA_MAIN_BODY_AMBIGUOUS","error":str(exc)[:220]})
# 2. Distinct product photo slot02, no repeat of failed frame01.
fid="pending-28"
srcs=list((ROOT/"v2707-seven-remaining-archival-real-photo-family-sets"/fid).glob("02-*.jpg"))
assert len(srcs)==1
src=srcs[0]
item28={"family":fid,"operation":"alternate-source-isnet-real-product-pad-photo",
  "source":str(src),"source_sha256":sha(src),"status":"HOLD"}
try:
    with Image.open(src) as im:
      im.load();original=im.convert("RGBA")
    # 02 jar sits centrally; preserve top/lid and bottom, omit bottom-right MK badge
    roi_box=(170,200,928,963)
    roi=original.crop(roi_box)
    cut=remove(roi,session=new_session("isnet-general-use"),
      alpha_matting=True,alpha_matting_foreground_threshold=230,
      alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
    assert cut.mode=="RGBA"
    a=np.asarray(cut.getchannel("A"))
    cover=float(np.mean(a>=128))
    bbox=cut.getchannel("A").getbbox()
    assert bbox is not None and .06<=cover<=.80,(cover,bbox)
    assert bbox[2]-bbox[0]>=240 and bbox[3]-bbox[1]>=260,(cover,bbox)
    cut=cut.crop(bbox)
    folder=OUT/fid;folder.mkdir()
    png=folder/"02-alternate-real-source-transparent-product-QA.png"
    cut.save(png,optimize=True)
    jpg=folder/"02-alternate-real-pad-product-hero-1080-QA.jpg"
    render_cutout(cut,"PIXEL PURE","Glow Cleansing Serum Pads 70ea / 210mL",jpg)
    item28.update({"status":"ALTERNATE_PRODUCT_PHOTO_SEGMENTED_VISUAL_QA_PENDING",
        "crop":list(roi_box),"mask_alpha_coverage":round(cover,4),
        "bbox":list(bbox),"png":str(png.relative_to(OUT)),
        "jpg":str(jpg.relative_to(OUT)),"jpg_sha256":sha(jpg)})
except Exception as exc:
    item28.update({"status":"HOLD_ALTERNATE_IMAGE_SEGMENTATION_FAILED",
                   "error":str(exc)[:220]})
rows=[item24,item28]
canvas=Image.new("RGB",(1560,1050),"#f2f1f0")
d=ImageDraw.Draw(canvas)
d.text((18,15),"v2714 REPAIR TWO PREVIOUSLY FAILED PRODUCT CUTOUTS / QA ONLY",font=f(25,True),fill="#292929")
for idx,row in enumerate(rows):
 with Image.open(row["source"]) as image:
   source=image.convert("RGBA")
 thumb=Image.new("RGB",source.size,"white")
 thumb.paste(source,(0,0),source)
 thumb=thumb.resize((420,420),Image.Resampling.LANCZOS)
 y=60+idx*488
 canvas.paste(thumb,(15,y))
 d.text((462,y+15),row["family"],font=f(31,True),fill="#333")
 d.text((462,y+68),row["status"],font=f(17),fill="#666")
 if row.get("jpg"):
   with Image.open(OUT/row["jpg"]) as im:
    new=im.convert("RGB").resize((420,420),Image.Resampling.LANCZOS)
   canvas.paste(new,(1120,y))
proof=OUT/"v2714-repair-original-versus-new.jpg"
canvas.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2714-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2714","baseline":"v2713",
 "recovery_attempts":2,"real_alpha_cutouts_rendered":sum(bool(x.get("jpg")) for x in rows),
 "sales_approved":0,"external_photo_rights_unverified":True,
 "owned_stock_exact_edition_unverified":True,"original_MK_logo_unavailable":True,
 "original_files_unchanged":True,"retail_11_product_families_unchanged":True,
 "public_55_urls_unchanged":True,"no_final_spreadsheet_shared":True,
 "products":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2714","cutouts":manifest["real_alpha_cutouts_rendered"],
"results":[x["status"] for x in rows],"retail_approved":0}))
