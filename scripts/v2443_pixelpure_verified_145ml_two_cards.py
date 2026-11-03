#!/usr/bin/env python3
"""v2443: complete PIXELPURE pending-26 five-frame candidate using verified 145ml real source.
No duplicated old info, no generated product imagery, and not a legal rights claim.
Two new factual information cards: usage from Korean duty-free product instructions;
listed ingredients from the exact 145mL retailer full-ingredients disclosure.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,zipfile
ROOT=Path("prior-v2442b")
OUT=Path("v2443-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((ROOT/"v2442b_30group_candidate_manifest.json").read_text())
group=next(g for g in manifest["families"] if g["group_id"]=="pending-26")
assert group["candidate_frame_count"]==3 and len(group["frames"])==3
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(size,bold=False):
 return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if bold else "")+".ttf",size)
def create_card(index,kicker,heading,body1,body2,bg,panel):
 im=Image.new("RGB",(1080,1080),bg)
 d=ImageDraw.Draw(im)
 dark=(43,64,55);border=(150,170,157)
 d.text((72,72),"MELLOWKR  /  PRODUCT GUIDE",fill=dark,font=font(30,True))
 d.line((72,138,1008,138),fill=border,width=2)
 label=font(39,True)
 ww=d.textbbox((0,0),kicker,font=label)[2]
 d.text((540-ww//2,204),kicker,fill=dark,font=label)
 d.rounded_rectangle((72,304,1008,763),radius=38,fill=panel)
 d.line((188,511,893,511),fill=border,width=2)
 for line,y,initial,bold in [(heading,394,56,True),(body1,561,39,False),(body2,647,36,False)]:
  sz=initial
  while sz>=24 and d.textbbox((0,0),line,font=font(sz,bold))[2]>855:sz-=1
  assert sz>=24,line
  width=d.textbbox((0,0),line,font=font(sz,bold))[2]
  d.text((540-width//2,y),line,fill=dark,font=font(sz,bold))
 d.line((73,853,1008,853),fill=border,width=2)
 filename=f"{index:02d}_PIXELPURE_Gentle_Gel_145ml_{kicker.replace(' ','_')}_V2443.jpg"
 p=OUT/"verified-fact-new-customer-cards/pending-26"/filename
 p.parent.mkdir(parents=True,exist_ok=True)
 im.save(p,"JPEG",quality=94,optimize=True)
 with Image.open(p) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and p.stat().st_size<2_000_000
 return p
usage=create_card(4,"HOW TO USE","GENTLE CLEANSING","Massage onto a wet face","Rinse with lukewarm water",(246,241,235),(220,234,225))
ing=create_card(5,"KEY INGREDIENTS","PANTHENOL + ALLANTOIN","Included in the 145 mL INCI list","See full packaging ingredient list",(229,239,233),(247,227,215))
actual=[]
for row in group["frames"]:
 src=ROOT/row["file"]
 assert src.exists() and sha(src)==row["sha256"]
 out=OUT/"pending-26-review-five-JPGs"/Path(row["file"]).name
 out.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,out)
 assert sha(out)==row["sha256"]
 actual.append({"role":row["input_role"],"path":str(out.relative_to(OUT)),"sha256":sha(out),"rights":"PENDING"})
for p,role in [(usage,"verified_instructions_copy"),(ing,"verified_ingredients_copy")]:
 assert p.is_file()
 out=OUT/"pending-26-review-five-JPGs"/p.name
 shutil.copyfile(p,out)
 actual.append({"role":role,"path":str(out.relative_to(OUT)),"sha256":sha(out),"rights":"PENDING"})
assert len(actual)==5 and len(set(x["sha256"] for x in actual))==5
report={
 "version":"2.4.43",
 "source":"production-assets-v2442b-thirty-safety-filtered-sets",
 "product":"PIXELPURE Gentle Gel to Foam Cleanser 145mL",
 "source_info":{
  "brand_official":"https://pixelpure.com/product/detail.html?product_no=21",
  "korean_duty_free_full_inci_and_usage":"https://m.shilladfs.com/estore/kr/ko/p/5885757",
  "usage_verified":"Apply onto wet face, massage gently, rinse with lukewarm water",
  "ingredient_names_verified":["Panthenol","Allantoin"]
 },
 "existing_3_original_jpg_unchanged":True,
 "new_copy_only_jpg":2,"five_candidate_set_assembled":True,
 "new_photographic_pixels_generated":False,
 "exact_packaging_reuse_permission":"UNVERIFIED",
 "verified_Korean_145mL_product_identity":True,
 "physical_stock_generation_verified":False,
 "complete_5frame_manual_sales_QA":False,
 "final_QA_approved":False,
 "new_source_photo_or_package_generated":False,
 "public_55_urls_overwritten":0,
 "frames":actual,
 "next":["Manually visually inspect both newly generated copy JPGs","Confirm brand photo usage rights and physical stock package before Shopee publication","If approved, insert this exact new pending-26 5-frame candidate into v2442b 30-family pack without re-rendering 29 other families"]
}
(OUT/"v2443_pending26_checkpoint.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
with zipfile.ZipFile(OUT/"v2443_pending26_five_real_candidate_JPGs.zip","w",compression=zipfile.ZIP_DEFLATED) as z:
 for x in actual:z.write(OUT/x["path"],arcname=x["path"])
 z.write(OUT/"v2443_pending26_checkpoint.json",arcname="v2443_pending26_checkpoint.json")
with zipfile.ZipFile(OUT/"v2443_pending26_five_real_candidate_JPGs.zip") as z:
 assert z.testzip() is None and len(z.namelist())==6
print(json.dumps({"version":report["version"],"existing_reused":3,"new_verified_text_JPG":2,"total_real_candidate_JPG":5,"finished_set_approved":False},ensure_ascii=False),flush=True)
