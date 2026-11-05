#!/usr/bin/env python3
"""v2869 CLIO Founwear source-bridged stock option QA, WITHOUT fake swatch
or reprocessing any image. Two archived merchant option photos look similar,
so no shade correctness is inferred from the compact. Identifiable 21C and
21N real cheek/forearm swatches from TWO archived source photos are shown
beside original merchant product pictures. INTERNAL REFERENCE ONLY.
Never overwrite any previous asset, public URL, or spreadsheet.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from hashlib import sha256
import json
R=Path("qa-review")
SRC_PHOTO=R/"v2852-founwear-original-five-variant-alternative-merchant-QA"
SRC_SWATCH=R/"v2867-founwear-21C-21N-real-swatch-source-evidence-QA"
SRC_CROPS=R/"v2868-founwear-21C21N-two-real-source-crops-and-stock30-resume"
OUT=R/"v2869-founwear-21c21n-option-photo-swatch-crosscheck-QA"
assert not OUT.exists(),"Immutable QA branch: do not overwrite prior output"
def sha(p):return sha256(p.read_bytes()).hexdigest()
photo_m=json.loads((SRC_PHOTO/"manifest.json").read_text())
swatch_m=json.loads((SRC_SWATCH/"manifest.json").read_text())
crop_m=json.loads((SRC_CROPS/"manifest.json").read_text())
assert photo_m["version"]=="v2852"
assert swatch_m["version"]=="v2867" and swatch_m["real_source_photos_saved"]==3
assert crop_m["version"]=="v2868" and crop_m["new_swatches"]==4
photo_rows={r["shade"]:r for r in photo_m["variants"]}
swatch_rows={r["id"]:r for r in swatch_m["sources"]}
cropped={(r["shade"],r["src"]):r for r in crop_m["items"]}
assert set(["21C","21N"]).issubset(photo_rows)
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
names={"21C":"LINGERIE","21N":"LINEN"}
source_ids=["merchant-cheek-five-labeled-shades","merchant-forearm-five-labeled-shades"]
OUT.mkdir(parents=True)
output=[]
for shade,name in names.items():
 row={"shade":shade,"name":name,"status":"HOLD_MISSING_SOURCE",
      "retail_approved":False,"licensed_for_commercial_use":False}
 try:
  source_prod=photo_rows[shade]
  product_path=SRC_PHOTO/source_prod["rendered_file"]
  assert product_path.exists() and sha(product_path)==source_prod["rendered_JPG_sha256"]
  with Image.open(product_path) as im:
   im.load();assert im.format=="JPEG"
   product=im.convert("RGB")
  original_crops=[]
  for sid in source_ids:
   s=swatch_rows[sid]
   c=cropped[(shade,sid)]
   source_path=Path(s["raw_path"])
   assert source_path.exists() and sha(source_path)==s["raw_sha256"]
   assert c["original_source_SHA256"]==s["raw_sha256"]
   with Image.open(source_path) as im:
    im.load()
    assert list(im.size)==c["original_source_native_px"]
    region=im.convert("RGB").crop(c["source_crop_coord_original_px"])
   original_crops.append((sid,region.copy(),s["raw_sha256"],c["source_crop_coord_original_px"]))
  canvas=Image.new("RGB",(1080,1080),"#FAF8FB")
  d=ImageDraw.Draw(canvas)
  d.rounded_rectangle((34,36,1046,1042),radius=25,outline="#DCD4E3",width=2)
  d.text((70,65),"CLIO  |  KILL COVER FOUNWEAR THE ORIGINAL",font=ft(29,True),fill="#3D3446")
  d.rounded_rectangle((68,118,550,175),radius=12,fill="#EDE6F1")
  d.text((88,129),shade+"  "+name+"  /  SHADE REFERENCE",font=ft(22,True),fill="#50435F")
  d.line((60,197,1020,197),fill="#D3C5D9",width=3)
  # Merchant-linked product PHOTO. Its resemblance to the alternate shade
  # remains known; not evidence of distinct compact packagings or real shade.
  pr=ImageOps.contain(product,(500,520),Image.Resampling.LANCZOS)
  canvas.paste(pr,(55+(500-pr.width)//2,237+(520-pr.height)//2))
  d.text((75,764),"MERCHANT-LINKED PRODUCT PHOTO",font=ft(16,True),fill="#74677C")
  d.text((75,790),"Visual shade identity NOT proven",font=ft(17),fill="#6F6277")
  for i,(sid,crop,source_sha,coords) in enumerate(original_crops):
   x,y,w,h=606,238+i*281,393,242
   d.rounded_rectangle((x-10,y-13,x+w+10,y+h+22),radius=10,fill="#FFFFFF",outline="#E4DBE7",width=2)
   fit=ImageOps.contain(crop,(w,h-19),Image.Resampling.LANCZOS)
   canvas.paste(fit,(x+(w-fit.width)//2,y+(h-19-fit.height)//2))
   cap="REAL CHEEK SWATCH" if i==0 else "REAL FOREARM SWATCH"
   d.text((x+7,y+h-14),cap+" / "+shade,font=ft(16,True),fill="#615368")
  d.line((66,854,1020,854),fill="#D7CBDF",width=2)
  d.text((70,872),"INTERNAL QA ONLY  |  NO INVENTED SHADE PIXELS",font=ft(24,True),fill="#504458")
  d.text((70,929),"Exact owned gift-set edition and photo rights NOT verified.",font=ft(19),fill="#675C6B")
  d.text((70,964),"Do not publish; verify stock + licensed images before sales.",font=ft(19),fill="#675C6B")
  path=OUT/f"CLIO-Founwear-{shade}-product-plus-real-2-source-swatches-1080-QA.jpg"
  canvas.save(path,"JPEG",quality=92,subsampling=0,optimize=True)
  with Image.open(path) as im:
   im.load();assert im.size==(1080,1080) and im.format=="JPEG"
  assert path.stat().st_size<2_000_000
  assert sha(product_path)==source_prod["rendered_JPG_sha256"]
  for sid,_,s_sha,_ in original_crops:assert sha(Path(swatch_rows[sid]["raw_path"]))==s_sha
  row.update(status="SOURCE_LINKED_PRODUCT_AND_TWO_REAL_SWATCHS_QA_ONLY",
    output=str(path),bytes=path.stat().st_size,sha256=sha(path),
    source_product=str(product_path),source_product_sha256=sha(product_path),
    source_swatch_photos= [{"id":sid,"sha256":ssha,"crop_original_pixels":cr} for sid,_,ssha,cr in original_crops],
    visual_product_image_near_duplicate_other_shade=True,
    photographed_swatch_labels_present_in_source=True,
    user_stock_set_packaging_verified=False)
 except Exception as e:
  row.update(status="HOLD_MISSING_OR_MISMATCHED_SOURCE",reason=str(e)[:260])
  print("HOLD",shade,str(e))
 output.append(row)
good=[x for x in output if x["status"].startswith("SOURCE_LINKED")]
if good:
 contact=Image.new("RGB",(1100*len(good),1150),"#F3EFF4")
 d=ImageDraw.Draw(contact)
 d.text((22,13),"v2869 | ORIGINAL PRODUCT + 2 REAL SHADENUMBER SWATCH SOURCES | INTERNAL QA",font=ft(22,True),fill="#4C4250")
 for i,row in enumerate(good):
  with Image.open(row["output"]) as im:
   contact.paste(im.convert("RGB"),(i*1100+12,60))
 cp=OUT/"v2869-21C-21N-source-bridge-option-review-QA.jpg"
 contact.save(cp,"JPEG",quality=88,optimize=True)
else:cp=None
report={
 "version":"v2869","baseline":"v2868","family":"pending-05",
 "product":"CLIO Founwear Cushion The Original (gift-set edition not confirmed)",
 "source_edition_reference":[
   {"shade":"21C","listing":"https://www.belieef.com/clio-kill-cover-founwear-cushion-the-original-1pack-15g-refill-15g-403178.html","seller_says":"15g compact + 15g refill; 21C one listed option; user-owned stock match unverified"},
   {"shade":"21N","listing":"https://www.watsons.com.sg/kill-cover-founwear-cushion-the-original-21n-linen-15g-refill-15g/p/BP_85755","seller_says":"21N 15g + refill 15g; owned stock match unverified"}],
 "new_option_composite_JPGs":len(good),
 "created_from_new_photo_downloads":0,
 "archived_original_product_images_changed":0,
 "archived_original_swatches_changed":0,
 "previous_v2866_three_shade_card_bytes_changed":0,
 "two_near_duplicate_merchant_compact_visuals_not_resolved":True,
 "results":output,
 "contact":str(cp) if cp else None,
 "prior_11_public_groups_unchanged":True,
 "prior_55_verified_public_URLs_unchanged":True,
 "retail_photo_rights_verified":False,
 "authenticated_original_MK_logo_present":False,
 "physical_owned_stock_edition_verified":False,
 "new_sales_approved":0,"new_public_URLs":0,
 "final_spreadsheet_shared":False,
 "next":"Use source swatches only as internal cross-validation, do not treat near-identical merchant product photos as exact shade-specific proof. To sell, verify user's actual 15g+refill boxes and legal image rights; move to other unresolved family instead of resegmentation."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2869","new_1080_QA":len(good),"held":len(output)-len(good),"new_sales_approved":0},ensure_ascii=False))
