#!/usr/bin/env python3
"""v2599 isolate exact stock OBgE Oil Control Finisher 5 g info-card
candidate without replacing an unknown existing 05 JPG. Never call an old
picture v2467 unless its exact bytes match. Use only inventory-proven claims,
no real product photo or derivative. QA output only, no public release.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat,ImageOps
import json,hashlib
B=Path("source/review-JPG-by-family/pending-09")
O=Path("v2599-obge-5g-single-item-info-QA");O.mkdir(exist_ok=True)
stock=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
item=next(i for i in stock["pending_families"] if i["family_id"]=="pending-09")
assert item["option_values"]==["단품"] and "5g" in item["family_name"].lower()
prior=sorted(B.glob("*.jpg"));assert len(prior)==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
canvas=Image.new("RGB",(1080,1080),"#f7f7f3")
d=ImageDraw.Draw(canvas)
ff=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
d.rounded_rectangle((37,38,1043,1040),radius=42,fill="#fffefb")
d.rectangle((37,38,1043,58),fill="#5e7468")
d.text((78,116),"OBgE",font=ff(89,True),fill="#2b493c")
d.text((80,252),"OIL CONTROL",font=ff(54,True),fill="#3e5447")
d.text((80,322),"FINISHER",font=ff(75,True),fill="#3e5447")
d.line((80,433,1000,433),fill="#bccbc0",width=3)
d.rounded_rectangle((78,505,1002,795),radius=28,fill="#e6ece4")
d.text((119,554),"NET CONTENT",font=ff(35),fill="#4d6652")
d.text((117,610),"5 g",font=ff(112,True),fill="#2b543c")
d.line((80,849,1000,849),fill="#becac0",width=3)
d.text((80,885),"PACKAGE",font=ff(26),fill="#6e7c70")
d.text((80,924),"Single item",font=ff(43,True),fill="#395a46")
path=O/"pending-09-slot05-OBgE-5g-single-item-info-REVIEW-ONLY.jpg"
canvas.save(path,"JPEG",quality=91,subsampling=0,optimize=True)
assert path.stat().st_size<2_000_000 and Image.open(path).size==(1080,1080)
comparison=[]
for p in prior:
 im=Image.open(p).convert("RGB").resize((128,128))
 new=canvas.resize((128,128))
 score=round(sum(ImageStat.Stat(ImageChops.difference(im,new)).mean)/3,2)
 comparison.append({"slot":int(p.name[:2]),"mae":score,"sha256":sha(p)})
near=[x for x in comparison if x["mae"]<8]
report={"version":"v2599","family":"pending-09","official_product_photo_used":False,
 "inventory_5g_single_item_proven":True,
 "new_candidate":path.name,"new_sha256":sha(path),"base_run":41765900358,
 "old_five_existing_slots_and_hashes":comparison,
 "potential_duplicate":near,"new_customer_facing_internal_QA_text":False,
 "source_sale_photo_rewritten":False,"public_image_overwritten":False,
 "source_156_JPG_bytes_modified":0,"prior_11_finished_product_families_untouched":True,
 "old_55_public_urls_changed":0,"xlsx_generated_or_shared":False,
 "original_MK_logo_present":False,
 "actual_inventory_packaging_and_human_QA_verified":False,
 "sale_release":False,"status":"INDEPENDENT_PRODUCT_INFO_CARD_ONLY"}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_jpg":1,"bytes":path.stat().st_size,"near_duplicates":len(near),
 "source_changed":0,"public_urls_changed":0,"excel":False}))
