#!/usr/bin/env python3
"""v2450: four new photo-based customer details and one separate 25AD label removal.
No previously generated 20 image copies edited or remade. All sources SHA matched.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import hashlib,json,zipfile
OLD=Path("prior-v2445b")
OUT=Path("v2450-output");OUT.mkdir(exist_ok=True)
m=json.loads((OLD/"v2445b-resumable-checkpoint.json").read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ff(sz,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",sz)
photo_jobs=[
 ("pending-12","MISSHA","PDRN NAD+ Renew Peel Shot 25","Original Product Detail","15 mL",(129,21,945,833)),
 ("pending-13","MISSHA","PDRN NAD+ Firming Repair Serum","Serum Dropper Detail","30 mL",(289,176,790,681)),
 ("pending-14","MISSHA","PDRN NAD+ Firming Repair Cream","Cream Texture Detail","70 mL",(290,178,790,681)),
 ("pending-17","Dr.G","Brightening Up Moisture Sun","Sun Cream & Texture","50 mL",(132,24,946,838))
]
entries=[]
def output(gid,brand,title,subtitle,size,photo,source_sha,source_name,issue):
 canvas=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(canvas);color=(46,63,54)
 d.text((70,51),brand,font=ff(38,True),fill=color)
 font_size=42
 while font_size>=25 and d.textbbox((0,0),title,font=ff(font_size,True))[2]>930:font_size-=1
 assert font_size>=25
 d.text((70,119),title,font=ff(font_size,True),fill=color)
 d.line((70,189,1010,189),fill=(179,190,182),width=2)
 p=ImageOps.contain(photo,(790,645),Image.Resampling.LANCZOS)
 canvas.paste(p,((1080-p.width)//2,225+(645-p.height)//2))
 d.line((70,913,1010,913),fill=(179,190,182),width=2)
 d.text((70,937),subtitle,font=ff(34,True),fill=color)
 d.text((70,992),size,font=ff(29),fill=color)
 path=OUT/"v2450-five-new-JPGs"/gid/f"{gid}_customer_photo_or_info_V2450.jpg"
 path.parent.mkdir(parents=True,exist_ok=True)
 canvas.save(path,"JPEG",quality=94,optimize=True)
 with Image.open(path) as check:
  check.load();assert check.format=="JPEG" and check.size==(1080,1080) and path.stat().st_size<2_000_000
 entries.append({"group_id":gid,"new_file":str(path.relative_to(OUT)),"new_sha256":sha(path),
 "source_sha256":source_sha,"source_path":source_name,"issue":issue,
 "new_product_pixels_fabricated":False,"status":"SALES_IMAGE_DRAFT",
 "commercial_photo_rights":"NOT_VERIFIED","stock_package_generation":"NOT_VERIFIED","final_sale_approved":False})
for gid,brand,title,sub,volume,crop in photo_jobs:
 row=next(x for x in m["asset_rows"] if x["family"]==gid and x["slot"]==2)
 src=OLD/row["file"];assert src.is_file() and sha(src)==row["sha256"]
 with Image.open(src) as im:
  im.load()
  assert im.size==(1080,1080)
  crop_photo=im.convert("RGB").crop(crop)
  output(gid,brand,title,sub,volume,crop_photo,row["sha256"],row["file"],"Directly inspected real product photography, photo rights and exact edition pending")
 assert sha(src)==row["sha256"]
# No unverified 25AD claim in pending20 info JPEG; replace only flat information card region.
row=next(x for x in m["asset_rows"] if x["family"]=="pending-20" and x["slot"]==2)
p=OLD/row["file"];assert sha(p)==row["sha256"]
with Image.open(p) as im:
 a=im.convert("RGB");d=ImageDraw.Draw(a)
 bg=a.getpixel((40,540));card=a.getpixel((550,310))
 d.rectangle((67,295,1048,780),fill=bg)
 d.rounded_rectangle((72,303,1008,763),radius=39,fill=card)
 txt=[("100 mL",390,70,True),("Green Tangerine Vita C",570,39,False),("Serum Mist",649,36,False)]
 for val,y,sz,bold in txt:
  while sz>=23 and d.textbbox((0,0),val,font=ff(sz,bold))[2]>850:sz-=1
  f=ff(sz,bold);w=d.textbbox((0,0),val,font=f)[2]
  d.text((540-w//2,y),val,font=f,fill=(43,63,54))
 dest=OUT/"v2450-five-new-JPGs/pending-20/pending-20_unverified_generation_removed_V2450.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 a.save(dest,"JPEG",quality=94,optimize=True)
 with Image.open(dest) as ck:
  ck.load();assert ck.size==(1080,1080) and ck.format=="JPEG" and dest.stat().st_size<2_000_000
 entries.append({"group_id":"pending-20","new_file":str(dest.relative_to(OUT)),"new_sha256":sha(dest),
 "source_sha256":row["sha256"],"source_path":row["file"],
 "issue":"Removed unsourced 25AD generation assertion from older existing customer information image",
 "new_product_pixels_fabricated":False,"status":"SALES_IMAGE_DRAFT",
 "commercial_photo_rights":"NOT_VERIFIED","stock_package_generation":"NOT_VERIFIED","final_sale_approved":False})
assert sha(p)==row["sha256"] and len(entries)==5
checkpoint={"version":"2.4.50","prior_success":"production-assets-v2449b-20-actual-photo-candidates",
 "new_product_photo_detail_JPGs":4,"new_generation_copy_correction_JPGs":1,
 "new_distinct_group_count":5,"previous_20_JPGs_regenerated":0,
 "old_531_original_photo_overwrites":0,"published_55_URLs_modified":0,
 "no_spreadsheets_created_or_shared":True,"new_final_sales_approvals":0,
 "items":entries,"next":["Open and manually inspect all five new real JPGs","Confirm exact product editions and licensed photo reuse; no Shopee publishing","Continue independent 30-family per-frame QA"]}
(OUT/"v2450_checkpoint.json").write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2450_five_additional_actual_customer_JPGs.zip","w",zipfile.ZIP_DEFLATED) as z:
 for x in entries:z.write(OUT/x["new_file"],arcname=x["new_file"])
 z.write(OUT/"v2450_checkpoint.json",arcname="v2450_checkpoint.json")
with zipfile.ZipFile(OUT/"v2450_five_additional_actual_customer_JPGs.zip") as z:assert z.testzip() is None and len(z.namelist())==6
print(json.dumps({"version":"2.4.50","new_real_jpg":5,"previous_20_untouched":True,"sheets_shared":0}),flush=True)
