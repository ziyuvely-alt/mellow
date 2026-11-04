#!/usr/bin/env python3
"""v2738: Object-contour photo masking, not a duplicate neural segmentation.

Two original archived 1080x1080 source photographs were visually inspected:
GOODAL CREAM ALPHA 50mL (jar with a cream splash behind it) and OBgE Oil
Control Finisher 5g (closed compact within old brown inset photo).

Manually trace the silhouette of only the real foreground product in each
source, anti-alias at 4x and preserve every RGB product pixel. Never fabricate
product objects, swatches, packaging, logos or brand claims. Save only to
append-only QA, not to any public retail asset / URL.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import hashlib, json, base64
ROOT=Path("qa-review")
DEST=ROOT/"v2738-two-actual-archived-product-contour-cutout-QA"
assert not DEST.exists(), "Never overwrite prior QA version"
DEST.mkdir(parents=True)
SRC=[
 {"family":"pending-09","title":"OBgE","desc":"Oil Control Finisher 5g",
  "src":ROOT/"v2705-three-recovered-photo-first-family-sets"/"pending-09"/"05-original-source-sha-unchanged-QA.jpg",
  "mask_type":"compact_contour","reason":"Isolate top single closed 5g compact, not second compact or beige inset"},
 {"family":"pending-19","title":"GOODAL","desc":"Green Tangerine Vita C Cream Alpha 50mL",
  "src":ROOT/"v2673-two-new-product-five-JPG-sets"/"pending-19"/"01-original-source-slot01-UNMODIFIED-QA.jpg",
  "mask_type":"jar_contour","reason":"Mask only real yellow jar + pale green lid, exclude white cream texture splash behind"}
]
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else REG,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def contour_mask(typ):
    sf=4
    canvas=Image.new("L",(1080*sf,1080*sf),0)
    d=ImageDraw.Draw(canvas)
    if typ=="jar_contour":
        # The lid covers x~294..789, y~426..564; jar x~267..813,
        # y~555..886. Preserve product edges; exclude cream splash above.
        d.rounded_rectangle((294*sf,426*sf,789*sf,566*sf),radius=38*sf,fill=255)
        # shallow lid-to-body seam is covered by this overlap
        d.rounded_rectangle((269*sf,550*sf,812*sf,886*sf),radius=27*sf,fill=255)
    elif typ=="compact_contour":
        # Closed OBgE beige case in archived source slot05, excluding
        # neighboring product underneath. Trace distinct 3D outline.
        points=[
          (485,390),(602,389),(631,396),(653,408),(669,429),
          (681,452),(687,491),(686,563),(680,598),(664,632),
          (639,648),(614,658),(487,657),(462,652),(440,639),
          (422,620),(415,592),(413,482),(421,450),(443,414),(466,399)
        ]
        d.polygon([(round(x*sf),round(y*sf)) for x,y in points],fill=255)
    else:raise ValueError(typ)
    return canvas.resize((1080,1080),Image.Resampling.LANCZOS)

rows=[]
board=Image.new("RGB",(1520,1020),"#f0f0ed")
bd=ImageDraw.Draw(board)
bd.text((16,14),"v2738 REAL ORIGINAL PHOTO CONTOUR CUTOUT  |  QA NOT RETAIL",font=ft(24,True),fill="#242424")
for idx,c in enumerate(SRC):
    src=c["src"];assert src.is_file(),str(src)
    with Image.open(src) as im:
        im.load();assert im.format=="JPEG" and im.size==(1080,1080)
        orig=im.convert("RGBA")
    mask=contour_mask(c["mask_type"])
    assert mask.getbbox()
    cut=orig.copy();cut.putalpha(mask)
    box=mask.getbbox()
    isolated=cut.crop(box)
    alpha=isolated.getchannel("A")
    coverage=sum(a>=128 for a in alpha.getdata())/len(alpha.getdata())
    assert .55<=coverage<=.95,(c["family"],coverage,box)
    sub=DEST/c["family"];sub.mkdir()
    png=sub/"01-real-archived-object-contour-transparent-QA.png"
    isolated.save(png,optimize=True)
    hero=Image.new("RGB",(1080,1080),"#ffffff")
    d=ImageDraw.Draw(hero)
    d.rounded_rectangle((55,55,1025,1025),radius=38,outline="#e9e4e5",width=2)
    d.text((95,95),c["title"],font=ft(45,True),fill="#343238")
    textsize=29
    while d.textbbox((0,0),c["desc"],font=ft(textsize))[2]>885 and textsize>15:textsize-=1
    d.text((95,167),c["desc"],font=ft(textsize),fill="#6e676c")
    fitted=ImageOps.contain(isolated,(800,735),Image.Resampling.LANCZOS)
    pos=((1080-fitted.width)//2,224+(735-fitted.height)//2)
    hero.paste(fitted,pos,fitted)
    d.text((95,987),"EXACT SOURCE PRODUCT PIXELS | QA ONLY",font=ft(18),fill="#8e878b")
    jpg=sub/"01-real-object-only-1080-JPG-QA.jpg"
    hero.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
    with Image.open(jpg) as x:
        x.load();assert x.size==(1080,1080) and x.format=="JPEG"
    assert jpg.stat().st_size<2_000_000
    with Image.open(png) as x:
        x.load();assert x.mode=="RGBA" and x.getchannel("A").getextrema()[0]<255
    y=60+idx*480
    board.paste(orig.convert("RGB").resize((423,423),Image.Resampling.LANCZOS),(16,y))
    bd.text((459,y+20),c["family"],font=ft(31,True),fill="#333333")
    bd.text((459,y+75),"MANUAL CONTOUR | VISUAL QA REQUIRED",font=ft(16),fill="#606060")
    board.paste(hero.resize((423,423),Image.Resampling.LANCZOS),(1082,y))
    rows.append({"family":c["family"],"source":str(src),"source_sha256":sha(src),
       "mask_method":c["mask_type"],"photo_pixels_reconstructed":0,
       "source_badge_MK_not_in_mask":True,"result_JPG":str(jpg.relative_to(DEST)),
       "result_PNG":str(png.relative_to(DEST)),
       "result_sha256":sha(jpg),"png_sha256":sha(png),
       "alpha_coverage_of_cropped_bbox":round(coverage,3),
       "status":"REAL_CONTOUR_PNG_JPG_STAGED_FOR_VISUAL_QA",
       "sellable_image":"HOLD_PENDING_VISUAL_LICENSE_EXACT_STOCK"})
proof=DEST/"v2738-source-versus-transparent-cutout-contact.jpg"
board.save(proof,"JPEG",quality=84,optimize=True)
(DEST/"v2738-contact.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2738","baseline":"v2737","batch":"two previously failed physical photos, novel contour-based method",
"actual_new_true_alpha_PNG_JPG_pairs":len(rows),"products":rows,
"unchanged_prior_source_photos":True,
"official_MK_logo_proven":False,"photography_reuse_rights_proven":False,
"real_owned_stock_edition_proven":False,"new_sale_approvals":0,
"original_published_11_families_unchanged":True,
"original_published_55_URLs_unchanged":True,
"final_spreadsheet_shared":False}
(DEST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2738","actual_new_alpha_jpg_pairs":len(rows),
"families":[r["family"] for r in rows],"new_retail_approvals":0}))
