#!/usr/bin/env python3
"""v2590: create ONE content-safe Goodal Green Tangerine Vita-C Serum Mist
100mL fact-only photo-free image from already documented inventory and product
source. No fabricated 25AD packaging, exact-product hero, claims or shade chips.
Keep prior 16 QA deltas, 156 original JPG, all published images unchanged.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
import json,hashlib
OUT=Path("v2590-goodal-mist-100ml-factual-image-QA");OUT.mkdir(exist_ok=True)
B=Path("v2590-base/review-JPG-by-family/pending-20")
I=Path("evidence/inventory-30-family-crosswalk-20261104.json")
assert B.is_dir()
item=next(f for f in json.loads(I.read_text())["pending_families"] if f["family_id"]=="pending-20")
assert "100ml" in item["family_name"].lower()
assert len(list(B.glob("*.jpg")))==5
im=Image.new("RGB",(1080,1080),"#f7f9f5")
d=ImageDraw.Draw(im)
font=lambda sz,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
d.rounded_rectangle((42,44,1038,1038),radius=38,fill="#fffefd")
d.rectangle((42,44,1038,64),fill="#a1b68a")
d.text((70,92),"goodal",fill="#355d38",font=font(75,True))
d.text((71,206),"GREEN TANGERINE VITA-C",fill="#32533c",font=font(41,True))
d.text((71,274),"SERUM MIST",fill="#426344",font=font(66,True))
d.line((72,376,1004,376),fill="#b9c8b7",width=3)
d.rounded_rectangle((72,438,1004,770),radius=34,fill="#e9f0e3")
d.text((113,501),"PRODUCT INFORMATION",fill="#31503b",font=font(35,True))
d.text((113,585),"NET CONTENT",fill="#58725c",font=font(26))
d.text((113,630),"100 mL",fill="#274c35",font=font(72,True))
d.line((72,832,1004,832),fill="#b9c8b7",width=2)
d.text((75,866),"Refer to the product label for directions.",font=font(26),fill="#536954")
d.text((75,932),"Packaging version: confirm with stock.",font=font(21),fill="#637663")
path=OUT/"pending-20-slot05-goodal-serum-mist-100ml-facts-QA.jpg"
im.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
assert path.stat().st_size<2_000_000 and Image.open(path).size==(1080,1080)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scores={}
for f in B.glob("*.jpg"):
 a=Image.open(f).convert("RGB").resize((128,128))
 b=im.resize((128,128))
 scores[f.name[:2]]=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
assert len(scores)==5
# Always record low scene variety rather than falsely declaring approval.
close=[slot for slot,s in scores.items() if s<8]
status="HOLD_NEAR_DUPLICATE" if close else "NEW_DISTINCT_FACTS_CARD_QA_ONLY"
manifest={"version":"v2590","family":"pending-20","product":"Goodal Green Tangerine Vita-C Serum Mist 100mL 25AD",
"previous_photo_source_run":41763993953,
"earlier_two_external_sources_status":"SOURCE_ACCESS_HOLD",
"prior_16_QA_deltas_unchanged":True,"existing_156_JPG_unchanged":True,
"actual_photo_in_this_card":False,"new_JPG_count":1,"slot_candidate":5,
"file":path.name,"candidate_sha256":sha(path),
"previous_slot05_sha256":sha(next(B.glob("05*.jpg"))),
"compare_MAE_to_previous_same_family":scores,"similarity_holds":close,
"status":status,"100mL_source":"stored inventory crosswalk: pending-20",
"external_product_source":"https://www.watsons.com.sg/goodal-green-tangerine-vita-c-serum-mist-100ml/p/BP_95021",
"product_stock_25AD_packaging_verified":False,"use_directions_verified":False,
"original_MK_logo_available":False,"commercial_photo_rights_needed_for_this_text_only_card":False,
"seller_public_release_approved":False,"public_55_URLs_changed":0,
"xlsx_created_or_shared":False}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"created_jpg":1,"bytes":path.stat().st_size,"status":status,"min_MAE":min(scores.values()),"public_changes":0,"xls":False}))
