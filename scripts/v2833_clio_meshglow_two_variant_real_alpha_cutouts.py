#!/usr/bin/env python3
"""v2833 actual neural-alpha product cutout from exact-labelled 21C / 21N
CLIO Mesh Glow Essential Cushion MINI 5g QA reference photos.

Only source photo pixels used, no generated product/color swatches/logo.
The extracted image is a QA candidate, never a proof of seller photo rights.
Product parts/peach swatch require visual review. Existing 55 URLs immutable.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
from io import BytesIO
import json,hashlib,base64
R=Path("qa-review")
SOURCE=R/"v2831-clio-mesh-glow-essential-mini-21C-21N-exact-shade-reference"
OUT=R/"v2833-clio-meshglow-essential-mini-21C-21N-real-alpha-photo-heroes"
assert SOURCE.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
model=new_session("isnet-general-use")
results=[]
for shade,name in [("21C","Lingerie"),("21N","Linen")]:
    path=SOURCE/f"{shade}-{name}-source-variant-labelled-photo-QA.jpg"
    assert path.is_file()
    row={
        "family":"pending-04","shade":shade,"shade_label":name,
        "source":str(path),"source_sha256":sha(path),
        "mask_model":"isnet-general-use","original_photo_rights_verified":False,
        "owned_stock_variant_confirmed":False,
        "status":"HOLD_VISUAL_REVIEW","commercial_release":False
    }
    try:
      with Image.open(path) as im:
        im.load();assert im.format=="JPEG" and im.size==(1080,1080)
        original=im.convert("RGBA")
      # Only original above-caption product photograph, including full compact.
      crop_xyxy=(58,55,1034,737)
      roi=original.crop(crop_xyxy)
      foreground=remove(roi,session=model,alpha_matting=True,
        alpha_matting_foreground_threshold=230,
        alpha_matting_background_threshold=18,
        alpha_matting_erode_size=4)
      assert foreground.mode=="RGBA"
      alpha=foreground.getchannel("A")
      bbox=alpha.getbbox()
      assert bbox is not None
      maskcount=sum(x>=128 for x in alpha.getdata())
      coverage=maskcount/(foreground.width*foreground.height)
      assert 0.015<coverage<0.83,(shade,coverage)
      assert bbox[2]-bbox[0]>100 and bbox[3]-bbox[1]>110,(shade,bbox)
      product=foreground.crop(bbox)
      outdir=OUT/shade;outdir.mkdir()
      png=outdir/f"01-{shade}-mini5g-real-alpha-cutout-QA.png"
      product.save(png,optimize=True)
      jpg=outdir/f"01-{shade}-mini5g-real-product-source-1080-QA.jpg"
      board=Image.new("RGB",(1080,1080),"white")
      d=ImageDraw.Draw(board)
      d.rounded_rectangle((48,48,1032,1032),radius=35,fill="#ffffff",outline="#eadfe7",width=2)
      d.text((96,100),"CLIO",font=ft(42,True),fill="#333038")
      d.text((96,164),"Mesh Glow Essential Mini 5g",font=ft(29),fill="#6c6269")
      d.text((96,211),f"{shade} {name} / merchant-labelled reference",font=ft(21),fill="#8b7980")
      fitted=ImageOps.contain(product,(875,710),Image.Resampling.LANCZOS)
      point=((1080-fitted.width)//2,254+(710-fitted.height)//2)
      board.paste(fitted,point,fitted)
      d.text((96,996),"REAL PHOTO FOREGROUND  |  QA ONLY  |  NOT LICENSED",font=ft(18),fill="#a3989d")
      board.save(jpg,"JPEG",quality=92,optimize=True,subsampling=0)
      assert jpg.stat().st_size<2_000_000
      with Image.open(jpg) as check:
        check.load();assert check.format=="JPEG" and check.size==(1080,1080)
      row.update({
        "status":"TRUE_ALPHA_PNG_AND_1080_JPG_SAVED_VISUAL_QA_PENDING",
        "crop_xyxy":list(crop_xyxy),
        "mask_bbox":list(bbox),
        "alpha_pixel_coverage":round(coverage,5),
        "transparent_png":str(png.relative_to(OUT)),
        "white_background_jpg":str(jpg.relative_to(OUT)),
        "jpg_sha256":sha(jpg),
        "jpg_bytes":jpg.stat().st_size,
        "actual_fabricated_product_pixels":0
      })
    except Exception as e:
      row.update({"status":"HOLD_MASK_OR_PHOTO_REJECTED","reason":str(e)[:220],
                  "exception":type(e).__name__})
    results.append(row)
board=Image.new("RGB",(1570,1080),"#f2f0ee")
d=ImageDraw.Draw(board)
d.text((16,15),"v2833 ORIGINAL MERCHANT REFERENCE vs GENUINE ALPHA CUTOUT | QA ONLY",font=ft(24,True),fill="#2a2929")
for idx,r in enumerate(results):
    y=60+idx*498
    with Image.open(r["source"]) as im:
      original=im.convert("RGB").resize((445,445),Image.Resampling.LANCZOS)
    board.paste(original,(14,y))
    d.text((474,y+20),f"{r['shade']} {r['shade_label']}",font=ft(32,True),fill="#292929")
    d.text((474,y+79),r["status"],font=ft(17),fill="#6a6064")
    if r.get("white_background_jpg"):
       with Image.open(OUT/r["white_background_jpg"]) as im:
          after=im.convert("RGB").resize((445,445),Image.Resampling.LANCZOS)
       board.paste(after,(1110,y))
p=OUT/"v2833-two-shades-photo-vs-cutout-review.jpg"
board.save(p,"JPEG",quality=83,optimize=True)
(OUT/"v2833-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
manifest={
 "version":"v2833","baseline":"v2832","family":"pending-04",
 "product":"CLIO Mesh Glow Essential Cushion Mini 5g",
 "attempted_variant_cutouts":2,
 "physically_saved_alpha_png_plus_1080_jpg_pairs":sum(bool(x.get("white_background_jpg")) for x in results),
 "previous_10_photo_QA_files_unchanged":True,
 "previous_11_approved_product_families_untouched":True,
 "previous_55_public_image_URLs_unchanged":True,
 "verified_photo_redistribution_rights":False,
 "owned_stock_edition_and_shade_verified":False,
 "authentic_MK_logo_verified":False,
 "photo_source_has_shade_label_not_physical_stock_proof":True,
 "retail_approved":False,
 "new_sales_approval_count":0,
 "final_xlsx_shared":False,
 "products":results
}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2833","pairs":manifest["physically_saved_alpha_png_plus_1080_jpg_pairs"],
 "outcomes":[x["status"] for x in results],"sales_approved":0}))
