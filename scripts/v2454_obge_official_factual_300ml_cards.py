#!/usr/bin/env python3
"""v2454: two source-backed OBgE MAX Waterful sunscreen 300mL English factual info cards.
The source product itself has no commercial-photo license, so these are text-only
sales information drafts NOT a substitute for genuine product photography.
No invented bottle, packaging, sunscreen SPF, color swatch, logo, or unverified formula claim.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,zipfile
OUT=Path("v2454-output");OUT.mkdir(exist_ok=True)
def ff(size,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,kicker,head,first,second,foot,colors):
 im=Image.new("RGB",(1080,1080),colors[0])
 d=ImageDraw.Draw(im)
 ink=(42,63,54)
 d.text((65,52),"OBgE  /  PRODUCT FACTS",font=ff(30,True),fill=ink)
 d.line((65,140,1015,140),fill=(167,184,172),width=2)
 d.text((70,210),kicker,font=ff(39,True),fill=ink)
 d.rounded_rectangle((65,309,1015,780),radius=34,fill=colors[1])
 sz=65
 while sz>=31 and d.textbbox((0,0),head,font=ff(sz,True))[2]>864:sz-=1
 assert sz>=31
 w=d.textbbox((0,0),head,font=ff(sz,True))[2]
 d.text(((1080-w)//2,390),head,font=ff(sz,True),fill=ink)
 d.line((183,523,897,523),fill=(168,183,171),width=2)
 for y,line in [(578,first),(660,second)]:
  size=39
  while size>=23 and d.textbbox((0,0),line,font=ff(size))[2]>860:size-=1
  assert size>=23
  width=d.textbbox((0,0),line,font=ff(size))[2]
  d.text(((1080-width)//2,y),line,font=ff(size),fill=ink)
 d.line((68,856,1012,856),fill=(168,183,171),width=2)
 sz=30
 while sz>=22 and d.textbbox((0,0),foot,font=ff(sz))[2]>935:sz-=1
 d.text((69,911),foot,font=ff(sz),fill=ink)
 p=OUT/"pending-22-official-facts-source-only"/(name+".jpg")
 p.parent.mkdir(parents=True,exist_ok=True)
 im.save(p,"JPEG",quality=94,optimize=True)
 with Image.open(p) as c:
  c.load();assert c.format=="JPEG" and c.size==(1080,1080) and p.stat().st_size<2_000_000
 return p
one=write("01_FACE_AND_BODY_300ML_V2454","SIZE & USE","300 mL  |  Face + Body",
"Designed for face and exposed body","Water-drop sunscreen texture",
"OBgE Max Waterful Sun Cream 300 mL",((233,241,237),(250,229,218)))
two=write("02_DAILY_REAPPLICATION_V2454","DAILY SUN CARE","REAPPLY AS NEEDED",
"Use on exposed skin as directed","Reapply during the day as needed",
"Refer to the actual packaging for SPF and directions",((248,240,234),(221,237,227)))
pointers=[
 "https://www.obge.co.kr/product/detail.html?cate_no=43&display_group=1&product_no=1251",
 "https://obge.co.kr/product/detail.html?cate_no=1&display_group=14&product_no=1251"
]
items=[{"file":str(f.relative_to(OUT)),"sha256":sha(f),"status":"FACTS_SOURCE_CHECKED_DRAFT","commercial_photo_assets_used":False,
 "licensable_generated_brand_artwork":False,"real_product_photo_included":False,"final_sales_approval":False} for f in [one,two]]
report={"version":"2.4.54","source":"OBgE brand-owned official Korean 300mL product page, public FAQ",
"official_urls":pointers,"sku":"OBgE Max Waterful Sun Cream 300mL",
"verified_facts":["300mL","face and body use","water-drop texture","reapply during the day"],
"new_customer_info_JPG":2,
"new_or_fabricated_product_photos":0,"new_official_swatches":0,
"commercial_image_rights_verified":0,"correct_original_300ml_pump_photo_available_for_publication":False,
"wrong_category_beige_cushion_source_still_quarantined":True,
"old_34_source_photo_review_JPGs_regenerated":0,
"original_531_JPGs_unchanged":True,"published_55_URL_paths_changed":0,
"no_spreadsheets_created_or_shared":True,
"FINAL_SALES_APPROVED":False,
"files":items,
"next":"Open two JPGs and verify text and source; actual pump package photo still requires authorized source, current exact model and stock QA"
}
(OUT/"v2454_fact_cards_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2454_two_verified_OBGE_300ml_info_cards.zip","w",zipfile.ZIP_DEFLATED) as z:
 for r in items:z.write(OUT/r["file"],arcname=r["file"])
 z.write(OUT/"v2454_fact_cards_checkpoint.json",arcname="v2454_fact_cards_checkpoint.json")
with zipfile.ZipFile(OUT/"v2454_two_verified_OBGE_300ml_info_cards.zip") as z:
 assert len(z.namelist())==3 and z.testzip() is None
print(json.dumps({"new_exact_source_fact_cards":2,"fabricated_product_photos":0,"previous_completed_recreated":0,"spreadsheet":False}),flush=True)
