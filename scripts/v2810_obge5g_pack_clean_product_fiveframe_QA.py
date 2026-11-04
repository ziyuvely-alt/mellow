#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64
R=Path("qa-review")
OLD=R/"v2808-obge-oil-finisher-five-official-scenes-true-alpha-QA"
FIX=R/"v2809-obge-finisher-genuine-product-left-swipe-alpha-correction"
OUT=R/"v2810-obge-5g-fiveframe-selected-true-alpha-sales-QA-HOLD"
assert OLD.is_dir() and FIX.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
frames=[]
for n in range(1,6):
 if n==1:
  src=FIX/"01-OBgE-5g-clean-compact-hero-1080-QA.jpg"
  filename="01-selected-clean-OBgE-5g-real-alpha-hero-QA.jpg"
 else:
  sources=list(OLD.glob("%02d-actual-brand-gallery-*-QA.jpg"%n))
  assert len(sources)==1,(n,sources)
  src=sources[0]
  filename="%02d-original-brand-gallery-unchanged-QA.jpg"%n
 target=OUT/filename
 assert src.is_file()
 shutil.copy2(src,target)
 assert sha(src)==sha(target)
 with Image.open(target) as im:
  im.load()
  assert im.format=="JPEG" and im.size==(1080,1080)
 assert target.stat().st_size<2000000
 frames.append({"slot":n,"file":filename,"source":str(src),
     "sha256":sha(target),"bytes":target.stat().st_size,
     "source_bytes_unchanged":True})
png=FIX/"01-OBgE-5g-beige-compact-only-transparent-QA.png"
assert png.is_file()
copied=OUT/"01-selected-genuine-alpha-transparent-product-QA.png"
shutil.copy2(png,copied)
assert sha(copied)==sha(png)
with Image.open(copied) as im:
 im.load()
 assert im.format=="PNG" and im.mode=="RGBA"
assert len(set(x["sha256"] for x in frames))==5
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
canvas=Image.new("RGB",(1850,500),"#f1f0ee")
d=ImageDraw.Draw(canvas)
d.text((16,14),"v2810 OBgE 5g CLEAN PRODUCT CUTOUT + FOUR OFFICIAL GALLERY SCENES / QA HOLD",font=font,fill="#333333")
for x in frames:
 with Image.open(OUT/x["file"]) as im:
  thumb=im.convert("RGB").resize((337,337),Image.Resampling.LANCZOS)
 xx=14+(x["slot"]-1)*370
 canvas.paste(thumb,(xx,59))
 d.text((xx,417),"SLOT %02d "%x["slot"]+("CLEAN CUTOUT" if x["slot"]==1 else "ORIGINAL SAVED"),font=font,fill="#292929")
contact=OUT/"v2810-contact.jpg"
canvas.save(contact,"JPEG",quality=85,optimize=True)
(OUT/"v2810-proof.b64.txt").write_text(base64.b64encode(contact.read_bytes()).decode())
report={"version":"v2810","baseline":"v2809","family":"pending-09",
"product":"OBgE Oil Control Finisher 5g","actual_five_JPGs_saved":5,
"actual_selected_true_alpha_PNG_preserved":True,
"four_official_brand_source_JPGs_exact_SHA_preserved":True,
"no_source_product_rendered_or_invented":True,
"photo_rights_verified":False,"user_owned_5g_edition_verified":False,
"original_MK_logo_verified":False,"new_retail_approval":0,
"old_11_sale_approved_groups_unchanged":True,
"old_55_public_image_URLs_unchanged":True,
"previous_qa_photo_assets_unchanged":True,"final_XLSX_shared":False,
"frames":frames}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2810","JPGs":5,"transparent_PNG":True,"retail_approved":0}))
