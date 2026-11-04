#!/usr/bin/env python3
"""v2598: change only OBgE Oil Control Finisher 5g information frame slot05
from vague "SHOP / Korean stock product" to stock-grounded PACKAGE / Single item.
No source photo rendered or transformed. Other 155 JPGs copied byte-identical.
If the historical v2467 info layout is absent, HOLD rather than corrupt.
Also verify MISSHA Peel Shot 25 uses official 15mL product copy in v2538 recipe.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
import json,hashlib,shutil,ast
B=Path("input/review-JPG-by-family")
OUT=Path("v2598-obge-one-frame-copy-repair")
D=OUT/"review-JPG-by-family"
stock=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
ob=next(f for f in stock["pending_families"] if f["family_id"]=="pending-09")
assert ob["family_name"].endswith("5g") and ob["option_values"]==["단품"]
missha=next(f for f in stock["pending_families"] if f["family_id"]=="pending-12")
assert missha["option_values"]==["15G"]
recipe=Path("scripts/v2538_missha_peelshot_replace_one_netcontent_with_washoff.py").read_text()
assert '"15 mL  /  WASH-OFF TREATMENT"' in recipe and '"15G' not in recipe
files=sorted(B.glob("pending-*/*.jpg"));assert len(files)==156
p=list((B/"pending-09").glob("05*.jpg"));assert len(p)==1
source=p[0]
assert source.name.startswith("05-product-facts-clean-repair") or "v2467" in source.name,source.name
original=Image.open(source).convert("RGB")
assert original.size==(1080,1080)
# The source v2467 info image has a third card between y=699 and y=821.
# Copy only the card panel background from that source style; redraw two labels.
new=original.copy();draw=ImageDraw.Draw(new)
font=lambda size,b=False:ImageFont.truetype(
 "/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",size)
draw.rounded_rectangle((70,699,1010,821),radius=30,fill="#e4e9de")
draw.text((109,714),"PACKAGE",font=font(25),fill="#637568")
draw.text((109,752),"Single item",font=font(34,True),fill="#304739")
D.mkdir(parents=True,exist_ok=True)
shutil.copytree(B,D,dirs_exist_ok=True)
q=D/"pending-09"/source.name
q.unlink()
dest=D/"pending-09"/"05_v2598-clean-single-item-facts-QA-ONLY.jpg"
new.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
assert Image.open(dest).size==(1080,1080) and dest.stat().st_size<2_000_000
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
updated=sorted(D.glob("pending-*/*.jpg"))
assert len(updated)==156
unchanged=0
for f in files:
 if f==source:continue
 assert sha(f)==sha(D/f.relative_to(B))
 unchanged+=1
assert unchanged==155
# Difference away from intended replacement panel is solely JPEG recompression.
a=original.crop((0,0,1080,685)).resize((270,171))
b=Image.open(dest).convert("RGB").crop((0,0,1080,685)).resize((270,171))
mae=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
assert mae<3,mae
assert sha(source)!=sha(dest)
for i in range(1,31):
 family=D/f"pending-{i:02d}"
 expected=6 if i in (1,2,4,5,6,7) else 5
 assert len(list(family.glob("*.jpg")))==expected
results={"version":"v2598","source_run":41765900358,
 "family":"pending-09","slot":5,"old_photo_sha256":sha(source),
 "new_photo_sha256":sha(dest),
 "old_customer_copy":"SHOP | Korean stock product",
 "new_customer_copy":"PACKAGE | Single item",
 "evidence":"exact pending-09 inventory option is 단품",
 "Missha_pending12_15ml_authored_recipe_confirmed":True,
 "missha_inventory_15G_remains_blocked":True,
 "original_155_JPG_sha_identical":True,"upper_crop_mean_pixel_error":round(mae,3),
 "total_review_JPG":156,"cumulative_changes_since_v2560":20,
 "old_55_public_URLs_changed":0,"new_public_URLs":0,
 "commercial_photo_rights_approved":False,
 "actual_owned_stock_package_confirmed":False,
 "original_MK_logo_applied":False,
 "final_sale_approval":False,"xlsx_created_or_shared":False}
(OUT/"manifest.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"updated":1,"unchanged":155,"total":156,
 "pending12_missha_15ml_copy":True,"sales_ready":False,"public_url_changes":0}))
