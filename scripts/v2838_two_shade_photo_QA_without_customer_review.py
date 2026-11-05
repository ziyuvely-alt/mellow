#!/usr/bin/env python3
"""v2838: make non-customer-photo 21C & 21N five-photo QA gallery.
Use two *variant-assigned* merchant images for slots 4/5 each; reuse and
preserve existing first 3 product JPG bytes. 21N native sources are already
stored from v2834, so DO NOT RE-DOWNLOAD or reprocess them. 21C W/La merchant
variant images are fetched once from v2835 exact variant links, never generic
Founwear or 23N. No copyright authorization or owned stock approval implied.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageChops
from io import BytesIO
import requests,json,hashlib,shutil,base64
R=Path("qa-review")
P32=R/"v2832-meshglow-essential-mini5g-21C-21N-five-image-internal-QA"
P34=R/"v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe"
P35=R/"v2835-clio-mini-21N-merchant-variant-image-assignment-audit"
OUT=R/"v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA"
assert P32.is_dir() and P34.is_dir() and P35.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(font_bold if b else font_path,n)
old=json.loads((P32/"manifest.json").read_text())
catalog=json.loads((P35/"manifest.json").read_text())
assert old["exact_21C_21N_five_photo_internal_QA_sets"]==2
assert all(z["status"]=="SHADE_LINK_AUDIT_COMPLETE" for z in catalog["merchant_results"])
merchant_order=["W Cosmetics Australia","La Cosmetique Australia"]
catalog_map={x["merchant"]:x for x in catalog["merchant_results"]}
variants_out=[]
all_frames=0
for variant in old["variants"]:
 shade=variant["shade"]
 assert shade in ("21C","21N")
 folder=OUT/shade;folder.mkdir()
 old_three=variant["frames"][:3]
 assert len(old_three)==3
 frames=[]
 for frame in old_three:
   slot=frame["slot"]
   assert slot in (1,2,3)
   src=P32/frame["file"]
   dest=folder/f"{slot:02d}-PRESERVED_{frame['photo_role']}-QA.jpg"
   shutil.copy2(src,dest)
   assert sha(src)==sha(dest)
   frames.append({"slot":slot,"source":str(src),"file":str(dest.relative_to(OUT)),
     "sha256":sha(dest),"source_sha256":sha(src),
     "role":frame["photo_role"],"commercial_photo_rights_verified":False,
     "original_image_bytes_unchanged":True,
     "source_shade_assignment":"EXACT" if slot==1 else "COMMON_UNASSIGNED"})
 for index,merchant in enumerate(merchant_order,4):
   cat=catalog_map[merchant]
   wanted=[x for x in cat["all_variant_rows"] if shade.lower() in str(x["shade_title"]).lower()]
   assert len(wanted)==1, (shade,merchant,wanted)
   url=wanted[0]["linked_photo_url"]
   assert url.startswith("https://") and "cdn.shopify.com" in url
   other=[x for x in cat["all_variant_rows"] if shade.lower() not in str(x["shade_title"]).lower()]
   assert all(x["linked_photo_url"]!=url for x in other)
   row={"slot":index,"merchant":merchant,"variant_title":wanted[0]["shade_title"],
        "url":url,"status":"HOLD_NOT_ACQUIRED"}
   try:
     if shade=="21N":
       src=P34/("01-21N-high-native-source-QA.jpg" if index==4 else "02-21N-high-native-source-QA.jpg")
       assert src.is_file()
       dest=folder/f"{index:02d}-MERCHANT_{'W' if index==4 else 'LACOSMETIQUE'}_EXACT_{shade}_QA.jpg"
       shutil.copy2(src,dest)
       assert sha(src)==sha(dest)
       original_dimensions=[800,800] if index==4 else [1200,1200]
       preserved=True
     else:
       r=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/png,image/webp,image/jpeg,*/*"},timeout=18)
       r.raise_for_status()
       assert len(r.content)<8_000_000
       with Image.open(BytesIO(r.content)) as im:
         im.load()
         original_dimensions=list(im.size)
         assert min(im.size)>=700,original_dimensions
         img=ImageOps.exif_transpose(im).convert("RGB")
       dst=Image.new("RGB",(1080,1080),"white")
       display=ImageOps.contain(img,(1080,1080),Image.Resampling.LANCZOS)
       dst.paste(display,((1080-display.width)//2,(1080-display.height)//2))
       dest=folder/f"{index:02d}-MERCHANT_{'W' if index==4 else 'LACOSMETIQUE'}_EXACT_{shade}_QA.jpg"
       dst.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
       preserved=False
     with Image.open(dest) as im:
       im.load()
       assert im.format=="JPEG" and im.size==(1080,1080)
     assert dest.stat().st_size<2_000_000
     row.update({"status":"EXACT_SHADE_MERCHANT_IMAGE_SAVED_QA",
       "source_photo_native_dimensions":original_dimensions,
       "file":str(dest.relative_to(OUT)),
       "sha256":sha(dest),"source_bytes_preserved":preserved,
       "commercial_photo_rights_verified":False})
   except Exception as exc:
     row["status"]="HOLD_IMAGE_UNAVAILABLE_OR_TOO_SMALL"
     row["failure"]=str(exc)[:220]
   frames.append(row)
 num=sum(bool(z.get("file")) for z in frames)
 valid=[z for z in frames if z.get("sha256")]
 distinct=len(set(z["sha256"] for z in valid))
 result={"shade":shade,"label":variant["shade_label"],
         "actual_photo_JPGs_saved":num,"distinct_sha_count":distinct,
         "customer_review_photo_frames":0,
         "missing_or_invalid_frames":5-num,
         "status":"FIVE_REAL_SOURCE_PHOTO_QA_ONLY_NO_CUSTOMER_REVIEW" if num==5 and distinct==5 else "PARTIAL_PHOTO_QA_NO_CUSTOMER_REVIEW",
         "frames":frames,"photo_redistribution_rights_verified":False}
 variants_out.append(result);all_frames+=num
 board=Image.new("RGB",(1830,470),"#f1f0ed")
 d=ImageDraw.Draw(board)
 d.text((12,11),f"v2838 {shade} {variant['shade_label']} | Merchant variant photos, no customer reviews | QA ONLY",font=font(22,True),fill="#302b31")
 for fr in frames:
    pos=int(fr["slot"])-1;x=12+pos*363
    if fr.get("file"):
      with Image.open(OUT/fr["file"]) as im:
       thumb=im.convert("RGB").resize((330,330),Image.Resampling.LANCZOS)
      board.paste(thumb,(x,53))
    d.text((x,391),"SHADE-LABEL" if pos==0 else ("COMMON" if pos<3 else "EXACT VARIANT"),font=font(19,True),fill="#3b333a")
    d.text((x,426),"PHOTO RIGHTS UNVERIFIED",font=font(13),fill="#776970")
 proof=OUT/f"v2838-{shade}-five-photo-no-customer-review-contact.jpg"
 board.save(proof,"JPEG",quality=82,optimize=True)
 (OUT/f"v2838-{shade}-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report={
 "version":"v2838","baseline":"v2837","family":"pending-04",
 "product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g",
 "21C_21N_rebuilt_internal_QA_photo_sets":2,
 "actual_photo_JPGs_saved":all_frames,
 "customer_review_photos_in_new_QA_sets":0,
 "licensed_for_Shopee_commercial_use":False,
 "owned_physical_stock_variants_verified":False,
 "unverified_original_MK_logo_not_added":True,
 "old_v2832_customer_review_reference_sets_preserved":True,
 "old_v2837_corrected_21N_cutout_preserved":True,
 "previous_11_approved_product_groups_unchanged":True,
 "previous_55_public_image_URLs_unchanged":True,
 "new_retail_approved":0,
 "final_spreadsheet_shared":False,
 "variants":variants_out
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2838","actual_photo_JPGs":all_frames,
 "variants":[{"shade":v["shade"],"count":v["actual_photo_JPGs_saved"],"unique":v["distinct_sha_count"],"status":v["status"]} for v in variants_out],
 "new_retail_approved":0}))
