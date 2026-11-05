#!/usr/bin/env python3
"""v2839 MISSHA PDRN NAD+ Firming Repair Serum 30mL (pending-13).
Correct old failure: v2719 fed an INFORMATION CARD to the segmentation model.
Use authenticated exact-product photographic source-04 (bottle with pipette)
already archived in v2696, opportunistically test only its unresized CDN URL.
No other product or fact-card is a valid fallback. Existing 11 approved + 55
public URLs and all previous QA archives remain unchanged. QA-only art.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
from io import BytesIO
import requests,hashlib,json,base64
ROOT=Path("qa-review")
SRC=ROOT/"v2696-missha-serum-official-gallery-proof"
OUT=ROOT/"v2839-missha-pdrn-serum30ml-correct-single-product-actual-photo-alpha"
assert SRC.is_dir() and not OUT.exists()
OUT.mkdir()
ORIGINAL=SRC/"source-04-REVIEW-ONLY.jpg"
assert ORIGINAL.is_file()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((SRC/"manifest.json").read_text())
assert "PDRN" in manifest["product"] and "30mL" in manifest["product"]
item=[x for x in manifest["downloaded"] if x["file"]==ORIGINAL.name]
assert len(item)==1 and "0000390487.jpg" in item[0]["url"]
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(boldfile if b else fontfile,n)
source_urls=[
 ("official_original_unresized","https://static.ableshop.kr/ext/images/goods/add/26/06/09/05/0000390487.jpg"),
 ("official_1000px_variant","https://static.ableshop.kr/ext/images/goods/add/26/06/09/05/1000/1000/0000390487.jpg")
]
attempts=[]
sources=[]
with Image.open(ORIGINAL) as im:
 im.load()
 assert im.format=="JPEG" and im.size==(500,500)
 sources.append({"kind":"v2696_archived_single_product_500px","pixels":[500,500],
     "source_path":str(ORIGINAL),"source_hash":sha(ORIGINAL),"image":im.copy().convert("RGB")})
for label,url in source_urls:
 rec={"kind":label,"url":url,"status":"NOT_AVAILABLE"}
 try:
  resp=requests.get(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/png,image/webp,*/*"},timeout=15)
  resp.raise_for_status()
  assert len(resp.content)<8_000_000
  with Image.open(BytesIO(resp.content)) as im:
   im.load();size=list(im.size);frame=ImageOps.exif_transpose(im).convert("RGB")
  rec.update({"status":"AVAILABLE","pixels":size,
    "higher_native_resolution_than_500":min(size)>500})
  if min(size)>500:
   sources.append({"kind":label,"pixels":size,"source_url":url,"image":frame})
 except Exception as exc:
  rec["failure"]=str(exc)[:190]
 attempts.append(rec)
best=max(sources,key=lambda x:(min(x["pixels"]),x["pixels"][0]*x["pixels"][1]))
row={
 "version":"v2839","family":"pending-13",
 "product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
 "reference":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114237",
 "source_photo_role":"SINGLE_RED_30ML_SERUM_BOTTLE_WITH_PIPETTE",
 "source_image_catalog_slot":4,
 "previous_bad_source":"v2719 used 01 information card instead of product photograph",
 "native_resolution_attempts":attempts,
 "selected_native_pixels":best["pixels"],
 "source_kind":best["kind"],
 "original_500px_source_untouched":True,
 "source_image_reuse_rights_confirmed":False,
 "actual_owned_stock_package_verified":False,
 "original_round_MK_logo_proven":False,
 "status":"HOLD_MASK_OR_DIRECT_VISUAL_QA",
 "sales_approved":False
}
source_photo=OUT/"01-verified-single-30mL-source-photo-reference-QA.jpg"
best["image"].save(source_photo,"JPEG",quality=95,optimize=True)
row["candidate_original_JPG"]=source_photo.name
row["candidate_original_sha256"]=sha(source_photo)
try:
 im=best["image"].convert("RGBA")
 w,h=im.size
 # Target only the single actual red serum bottle on the left; the decorative
 # pink bubble at upper-right and gift/product banners are not a product.
 roi=(int(w*.08),int(h*.045),int(w*.75),int(h*.97))
 photo=im.crop(roi)
 segmented=remove(photo,session=new_session("isnet-general-use"),
    alpha_matting=True,alpha_matting_foreground_threshold=230,
    alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
 assert segmented.mode=="RGBA"
 mask=segmented.getchannel("A")
 box=mask.getbbox()
 assert box
 fraction=sum(p>=128 for p in mask.getdata())/(segmented.width*segmented.height)
 assert .028<fraction<.83,(fraction,box)
 assert box[2]-box[0]>=max(85,int(segmented.width*.22))
 assert box[3]-box[1]>=max(140,int(segmented.height*.28))
 item_photo=segmented.crop(box)
 alpha_png=OUT/"01-actual-single-30mL-serum-true-alpha-QA.png"
 item_photo.save(alpha_png,optimize=True)
 board=Image.new("RGB",(1080,1080),"white")
 d=ImageDraw.Draw(board)
 d.rounded_rectangle((53,53,1027,1027),radius=34,outline="#ece3e5",width=2)
 d.text((97,101),"MISSHA",font=ft(42,True),fill="#3b3336")
 d.text((97,169),"PDRN NAD+ Firming Repair Serum 30mL",font=ft(26),fill="#716771")
 display=ImageOps.contain(item_photo,(845,755),Image.Resampling.LANCZOS)
 board.paste(display,((1080-display.width)//2,216+(755-display.height)//2),display)
 d.text((97,995),"ACTUAL 30ML PHOTO SOURCE  |  QA ONLY",font=ft(19),fill="#9b9296")
 jpg=OUT/"01-MISSHA-30mL-serum-photo-cutout-1080-QA.jpg"
 board.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
 assert jpg.stat().st_size<2_000_000
 with Image.open(jpg) as verify:
  verify.load();assert verify.format=="JPEG" and verify.size==(1080,1080)
 row.update({"status":"REAL_ALPHA_PRODUCT_JPG_PNG_SAVED_VISUAL_QA_PENDING",
 "photo_crop_xyxy":list(roi),"mask_bbox":list(box),
 "mask_coverage":round(fraction,5),
 "alpha_png":alpha_png.name,"JPG":jpg.name,"JPG_sha256":sha(jpg),"JPG_bytes":jpg.stat().st_size})
except Exception as exc:
 row.update({"status":"HOLD_MASK_OR_PHOTO_INCOMPLETE",
   "error_type":type(exc).__name__,"error":str(exc)[:240]})
review=Image.new("RGB",(1540,625),"#f2f1ef")
d=ImageDraw.Draw(review)
d.text((16,16),"v2839 MISSHA PDRN NAD+ 30mL | archived original vs selected photo vs first real cutout",font=ft(22,True),fill="#242326")
for idx,(source,title) in enumerate([
 (ORIGINAL,"PREVIOUS ARCHIVED 500PX"),
 (source_photo,f"SELECTED NATIVE {best['pixels']}"),
 (OUT/row["JPG"] if row.get("JPG") else source_photo,"NEW TRUE ALPHA QA" if row.get("JPG") else "MASK FAILED")]):
 with Image.open(source) as im:
  thumb=im.convert("RGB").resize((463,463),Image.Resampling.LANCZOS)
 x=20+idx*505
 review.paste(thumb,(x,60))
 d.text((x,539),title,font=ft(17,True),fill="#3b3034")
d.text((19,586),"No other serum, gifts, or information cards included | PHOTO RIGHTS / STOCK EDITION HOLD",font=ft(18),fill="#665d63")
proof=OUT/"v2839-official-single-serum-actual-alpha-proof.jpg"
review.save(proof,"JPEG",quality=84,optimize=True)
(OUT/"v2839-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest_out={
 "version":"v2839","baseline":"v2838","product_family":"pending-13",
 "single_30mL_product_actual_photo_source_selected":True,
 "previous_fact_card_bug_avoided":True,
 "new_true_alpha_png_jpg_pairs":1 if row.get("alpha_png") else 0,
 "previous_JPG_photo_reencoded_or_modified":0,
 "prior_11_approved_product_families_untouched":True,
 "prior_55_verified_public_urls_untouched":True,
 "commercial_photo_permission_verified":False,
 "exact_owned_stock_package_verified":False,
 "authentic_MK_logo_verified":False,
 "new_retail_approvals":0,
 "final_xlsx_shared":False,
 "candidate":row
}
(OUT/"manifest.json").write_text(json.dumps(manifest_out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2839","native":best["pixels"],"cutouts":manifest_out["new_true_alpha_png_jpg_pairs"],
"status":row["status"],"new_sales_approved":0}))
