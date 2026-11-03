#!/usr/bin/env python3
"""v2455: two genuinely new OBgE 300mL factual photo-free sales info JPGs.
All claims copied only as verified factual paraphrase from the exact official OBgE
300mL product no. 1251 page, checked 2026-11-04. Do not generate bottle photos,
color swatches, original logo, mock packaging, claims of licensed art or approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,zipfile
OUT=Path("v2455-output");OUT.mkdir(exist_ok=True)
INK=(43,64,55)
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def center(draw,text,y,sz,bold,max_width=872):
 while sz>=23 and draw.textbbox((0,0),text,font=font(sz,bold))[2]>max_width:sz-=1
 assert sz>=23,text
 f=font(sz,bold);w=draw.textbbox((0,0),text,font=f)[2]
 draw.text(((1080-w)//2,y),text,font=f,fill=INK)
def make(file,kicker,header,lines,footer,bg,panel):
 im=Image.new("RGB",(1080,1080),bg)
 d=ImageDraw.Draw(im)
 d.text((64,52),"OBgE  /  VERIFIED PRODUCT FACTS",font=font(29,True),fill=INK)
 d.line((65,140,1015,140),fill=(158,180,164),width=2)
 d.text((72,203),kicker,font=font(39,True),fill=INK)
 d.rounded_rectangle((65,304,1015,791),radius=38,fill=panel)
 center(d,header,391,61,True)
 d.line((183,519,897,519),fill=(156,177,165),width=2)
 for y,line in zip((575,653),lines):center(d,line,y,38,False)
 d.line((67,857,1013,857),fill=(158,180,164),width=2)
 d.text((69,918),footer,font=font(28),fill=INK)
 p=OUT/"pending-22-new-official-source-fact-JPGs"/file
 p.parent.mkdir(parents=True,exist_ok=True)
 im.save(p,"JPEG",quality=94,optimize=True)
 with Image.open(p) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and p.stat().st_size<2_000_000
 return p
a=make("03_OBGE_300ml_official_ingredients_V2455.jpg","INGREDIENT HIGHLIGHTS",
       "PANTHENOL + ECTOIN",["Sodium Hyaluronate","Hyaluronic Acid Derivatives"],
       "Selected INCI ingredients, not the full ingredients list",
       (234,241,235),(250,227,216))
b=make("04_OBGE_300ml_official_function_V2455.jpg","OFFICIAL FUNCTION",
       "UV PROTECTION",["Sunscreen for daily sun care","Includes wrinkle-care function"],
       "OBgE Max Waterful Sun Cream 300 mL",
       (251,240,230),(222,239,229))
files=[{"file":str(p.relative_to(OUT)),"sha256":h(p),"status":"BRAND_OFFICIAL_TEXT_FACTS_VERIFIED",
       "photo_licensing":"NO_BRAND_PRODUCT_PHOTO_USED","exact_stock_package":"NOT_VERIFIED",
       "final_sale_approved":False} for p in (a,b)]
report={
 "version":"2.4.55",
 "brand_product":"OBgE MAX Waterful Sun Cream 300 mL",
 "official_source":"https://www.obge.co.kr/product/detail.html?cate_no=43&display_group=1&product_no=1251",
 "official_page_product_no":1251,
 "verified_ingredients":["Panthenol","Ectoin","Sodium Hyaluronate","Hyaluronic Acid","Hydrolyzed Hyaluronic Acid","Potassium Hyaluronate"],
 "verified_function_text":["UV protection","Helps improve the appearance of wrinkles"],
 "new_distinct_customer_fact_JPG":2,
 "previous_v2454_2_fact_JPGs_reproduced":0,
 "previous_v2454b_36_success_JPGs_reproduced":0,
 "invented_product_pixels":0,"new_swatches":0,"new_unlicensed_MK_logo":0,
 "old_published_55_URL_changes":0,"old_531_original_photo_changes":0,
 "commercial_photo_rights_verified":False,
 "stock_package_generation_verified":False,"FINAL_SALES_APPROVED":False,
 "no_XLSX_or_Google_Sheets_created_or_shared":True,
 "new_files":files,
 "next":["Visually inspect the two new files and reject layout defects",
 "Reuse exactly earlier successful 36 JPEG bytes and only append these 2 distinct fact-card JPEGs",
 "Continue true-product photo and shade generation review for pending-01, pending-08 and pending-22"]
}
(OUT/"v2455_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2455_two_official_ingredients_function_JPGs.zip","w",zipfile.ZIP_DEFLATED) as z:
 for row in files:z.write(OUT/row["file"],arcname=row["file"])
 z.write(OUT/"v2455_checkpoint.json",arcname="v2455_checkpoint.json")
with zipfile.ZipFile(OUT/"v2455_two_official_ingredients_function_JPGs.zip") as z:
 assert z.testzip() is None and len(z.namelist())==3
print(json.dumps({"version":"2.4.55","new_fact_JPG":2,"actual_product_photos_generated":0,"spreadsheet_shared":False}),flush=True)
