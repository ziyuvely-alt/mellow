#!/usr/bin/env python3
"""v2600 four source-backed, entirely original, photo-free fact frames.
The existing 156 JPEG corpus and v2599 OBgE draft are preserved unchanged.
Do not invent exact product visuals, logo, package graphics, efficacy or swatches.
Variant cards are candidate replacements only after visual and commercial QA.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageStat,ImageChops,ImageOps
import json,hashlib,math
INV=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
ROOT=Path("review/review-JPG-by-family")
OUT=Path("v2600-four-original-product-info-JPG-review-only")
OUT.mkdir(exist_ok=True)
fam={f["family_id"]:f for f in INV["pending_families"]}
cases=[
 ("pending-12","MISSHA","PDRN NAD+","RENEW PEEL SHOT 25","15 mL","WASH-OFF TREATMENT",("15G","15ml"),"#f8eeec","#8d5360","peel"),
 ("pending-13","MISSHA","PDRN NAD+","FIRMING REPAIR SERUM","30 mL","SERUM",("30ML","30ml"),"#f3f1f4","#684e74","serum"),
 ("pending-14","MISSHA","PDRN NAD+","FIRMING REPAIR CREAM","70 mL","CREAM",("70ML","70ml"),"#f5eff5","#7f567b","cream"),
 ("pending-28","PIXEL PURE","GLOW CLEANSING","SERUM PAD","210 mL","70 PADS",("210ML/70PADS","210ml/70매"),"#edf7f6","#377f7a","pads")
]
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata());v=0
 for y in range(8):
  for x in range(8):v=(v<<1)|(p[y*9+x]>p[y*9+x+1])
 return v
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
results=[]
for family,brand,series,name,amount,descriptor,required,bg,accent,kind in cases:
 data=fam[family]
 assert any(required[0].lower()==str(x).lower() for x in data["option_values"]),(family,required,data["option_values"])
 assert required[1].replace(" ","").lower() in data["family_name"].replace(" ","").lower(),(family,data["family_name"])
 old=sorted((ROOT/family).glob("*.jpg"))
 assert len(old)==5,(family,len(old))
 board=Image.new("RGB",(1080,1080),bg);d=ImageDraw.Draw(board)
 # Four deliberately distinct original editorial compositions, not package mockups.
 if kind=="peel":
  d.ellipse((510,-340,1350,500),outline=accent,width=18)
  d.ellipse((690,-170,1190,330),outline="#dec5ca",width=10)
  d.text((68,84),brand,font=F(50,True),fill=accent)
  d.text((68,179),series,font=F(35,True),fill=accent)
  d.text((68,280),"RENEW PEEL",font=F(69,True),fill="#53333c")
  d.text((68,372),"SHOT 25",font=F(96,True),fill="#53333c")
  d.line((69,525,1000,525),fill="#c7a4ac",width=4)
  d.text((69,589),amount,font=F(147,True),fill=accent)
  d.text((75,811),descriptor,font=F(31,True),fill="#664b53")
 elif kind=="serum":
  d.rounded_rectangle((42,38,1038,1042),radius=60,outline="#cfc2d5",width=5)
  for i in range(7):
   x=130+i*120;d.line((x,150,x-120,430),fill="#e7dce9",width=5)
  d.text((92,102),brand,font=F(52,True),fill=accent)
  d.text((92,505),series,font=F(44),fill=accent)
  d.text((92,579),"FIRMING REPAIR",font=F(55,True),fill="#3b3343")
  d.text((92,670),"SERUM",font=F(94,True),fill="#3b3343")
  d.text((92,860),amount,font=F(65,True),fill=accent)
 elif kind=="cream":
  d.ellipse((-430,120,540,1050),outline="#d6b8d5",width=32)
  d.ellipse((-340,210,450,960),outline="#e9d6e8",width=13)
  d.text((530,124),brand,font=F(56,True),fill=accent)
  d.text((528,266),series,font=F(33,True),fill=accent)
  d.text((528,421),"FIRMING",font=F(62,True),fill="#49334b")
  d.text((528,500),"REPAIR",font=F(68,True),fill="#49334b")
  d.text((528,585),"CREAM",font=F(72,True),fill="#49334b")
  d.text((530,814),amount,font=F(67,True),fill=accent)
 elif kind=="pads":
  for radius in (315,250,184):
   d.ellipse((570-radius,505-radius,570+radius,505+radius),outline="#b8dfdc",width=15)
  d.text((72,75),brand,font=F(48,True),fill=accent)
  d.text((72,729),"GLOW CLEANSING",font=F(46,True),fill="#234e4c")
  d.text((72,801),"SERUM PAD",font=F(74,True),fill="#234e4c")
  d.text((72,933),"210 mL  /  70 PADS",font=F(43,True),fill=accent)
 image=OUT/(family+"-original-facts-"+kind+"-CANDIDATE.jpg")
 board.save(image,"JPEG",quality=93,optimize=True,subsampling=0)
 assert Image.open(image).size==(1080,1080) and image.stat().st_size<2_000_000
 oldscore=[]
 for src in old:
  previous=Image.open(src)
  oldscore.append({"slot":int(src.name[:2]),"mae":mae(board,previous),"dhash":(dhash(board)^dhash(previous)).bit_count()})
 near=[x for x in oldscore if x["mae"]<8 or x["dhash"]<=6]
 results.append({"family":family,"product":data["family_name"],
  "candidate_file":image.name,"candidate_sha256":sha(image),
  "bytes":image.stat().st_size,"score_against_5_existing_images":oldscore,
  "duplicate_alerts":near,"release_status":"HOLD_NEAR_SCENE" if near else "STANDALONE_DISTINCT_FACTS_CANDIDATE",
  "verified_product_content":amount,
  "no_packaging_simulated":True,"no_photo_source_used":True,"logo_included":False,
  "physical_stock_signed_off":False,"retail_approval":False})
assert len(results)==4
assert all(x["release_status"]=="STANDALONE_DISTINCT_FACTS_CANDIDATE" for x in results),results
manifest={"version":"v2600","source_corpus_run":41765900358,"existing_obge_pending09_candidate_run":41766677519,
 "original_verified_inventory":"evidence/inventory-30-family-crosswalk-20261104.json",
 "new_original_product_info_image_count":4,
 "affected_families":[x["family"] for x in results],
 "source_156_photo_images_modified":0,
 "existing_55_public_urls_modified":0,"xlsx_generated_or_shared":False,
 "all_four_review_only":True,"original_MK_logo_missing":True,
 "pending12_original_stock_15G_vs_official_15mL_hold":True,
 "photo_licensing_is_not_claimed":True,
 "human_review_before_adding_to_final_156":True,
 "frames":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"original_product_info_JPG":4,
 "distinct_within_each_family":4,"source_156_modified":0,
 "public_url_changes":0,"excel_shared":False}))
