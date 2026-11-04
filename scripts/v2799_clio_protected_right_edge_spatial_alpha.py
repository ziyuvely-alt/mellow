#!/usr/bin/env python3
"""v2799: Two spatially limited real-alpha reflection edits from untouched v2797.

Explicitly REJECT v2798: its full-width fade clipped the right lower compact
frame. Here only lower-left floor-reflection alpha is adjustable. Product
upper region and all rightmost 24% of mask are STRICT byte-identical.
Compare before/after, do not auto-release retail.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import numpy as np, hashlib,base64,json
ROOT=Path("qa-review")
SRC=ROOT/"v2797-clio-meshglow-five-distinct-official-photo-scenes-and-alpha-qa"
OUT=ROOT/"v2799-clio-reflection-spatial-right-edge-preserving-alpha-QA"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
path=SRC/"01-alternate-real-transparent-CLIO-object-QA.png"
with Image.open(path) as im:
 im.load();assert im.format=="PNG" and im.mode=="RGBA"
 source=im.copy()
base=np.asarray(source)
h,w=base.shape[:2]
assert w>=400 and h>=400
FONT=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Smooth alpha fade exclusively lower-left reflection, *not* full-width
# bottom fade. The right-hand product hinge and case border are protected.
SPECS=[
 ("A-gentle-reflection-tail",.875,.975,.59,.73),
 ("B-stronger-lower-left-reflection",.850,.955,.64,.76)
]
rows=[]
for name,start,end,x_inner,x_outer in SPECS:
 array=base.copy()
 for iy in range(int(h*start),h):
  py=iy/h
  yfactor=1.0 if py<start else max(0.,min(1.,(end-py)/(end-start)))
  for ix in range(int(w*x_outer)):
   px=ix/w
   xfactor=1.0 if px<=x_inner else max(0.,min(1.,(x_outer-px)/(x_outer-x_inner)))
   # amount = (1 - yfade) * x taper, preserving upper and right.
   multiplier=1.0-(1.0-yfactor)*xfactor
   array[iy,ix,3]=np.uint8(round(int(base[iy,ix,3])*multiplier))
 assert np.array_equal(array[:int(h*start)],base[:int(h*start)])
 assert np.array_equal(array[:,int(w*x_outer):],base[:,int(w*x_outer):])
 n_changed=int(np.count_nonzero(array[:,:,3]!=base[:,:,3]))
 assert n_changed>50
 out=Image.fromarray(array,"RGBA")
 bbox=out.getchannel("A").getbbox()
 assert bbox
 out=out.crop(bbox)
 png=OUT/f"01-{name}-true-alpha-QA.png"
 out.save(png,optimize=True)
 white=Image.new("RGB",(1080,1080),"white")
 fit=ImageOps.contain(out,(930,930),Image.Resampling.LANCZOS)
 white.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2),fit)
 jpg=OUT/f"01-{name}-1080-QA.jpg"
 white.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(jpg) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert jpg.stat().st_size<2000000
 rows.append({"variant":name,"source":"v2797 original transparent cutout, NOT v2798 clipped result",
   "PNG":png.name,"JPG":jpg.name,"changed_alpha_pixels":n_changed,
   "source_sha256":sha(path),"output_png_sha256":sha(png),"output_jpg_sha256":sha(jpg),
   "preserved_top_fraction":start,"protected_product_right_fraction":1-x_outer,
   "retail_approved":False,"visual_QA":"UNREVIEWED"})
board=Image.new("RGB",(1720,650),"#efefef")
d=ImageDraw.Draw(board)
d.text((20,17),"v2799 right product edge protected: source / gentle / stronger, three QA views",font=FONT,fill="#232323")
original=SRC/"01-alternate-real-segmented-object-1080-QA.jpg"
pics=[(original,"v2797 unchanged"),(OUT/rows[0]["JPG"],"A: gentle, lower-left only"),(OUT/rows[1]["JPG"],"B: lower-left only")]
for i,(p,label) in enumerate(pics):
 with Image.open(p) as im:
  tile=im.convert("RGB").resize((522,522),Image.Resampling.LANCZOS)
 x=15+i*568
 board.paste(tile,(x,61))
 d.text((x,597),label,font=FONT,fill="#2b2b2b")
preview=OUT/"v2799-original-vs-two-spatial-alpha-options.jpg"
board.save(preview,"JPEG",quality=86,optimize=True)
(OUT/"v2799-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
report={"version":"v2799","baseline":"v2797","previous_attempt":"v2798",
 "previous_v2798_visual_qa":"REJECT_CLIPPED_BOTTOM_RIGHT_CASE",
 "products_tested":1,"saved_png_jpg_variant_pairs":2,
 "actual_source_1200px_photos_untouched":True,
 "five_original_official_JPGs_unchanged":True,
 "all_pixels_at_product_right_edge_unchanged":True,
 "original_MK_logo_verified":False,
 "photo_reuse_rights_verified":False,
 "owned_stock_edition_verified":False,
 "new_sale_approval":0,
 "original_11_approved_families_unchanged":True,
 "original_55_public_URLs_untouched":True,
 "final_XLSX_shared":False,
 "variants":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2799","variants":2,
"changed_alpha_pixels":[r["changed_alpha_pixels"] for r in rows],
"approved":0}))
