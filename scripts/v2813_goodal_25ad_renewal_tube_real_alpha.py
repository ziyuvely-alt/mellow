#!/usr/bin/env python3
"""v2813: rescue GOODAL 25AD 30mL by using a REAL 2026 renewal TUBE photo,
not the old 30mL pump source staged v2811/v2812. No commercial use rights
inferred from third-party web photos. Existing 55 image URLs are immutable.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from rembg import remove,new_session
from io import BytesIO
import requests,hashlib,json,base64,numpy as np,cv2
OUT=Path("qa-review/v2813-goodal-renewal-25AD-tube-genuine-source-alpha")
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 {"id":"2026-renewal-single-tube","url":"https://www.shegoestoseoul.com/image/cache/catalog/PRODUCT/2026/goodal/green-tangerine-vitac-dark-spot-care-eyecream/goodal-green-tangerine-vitac-dark-spot-care-eyecream-renewal-m1-480x480fill.jpg",
 "type":"PHOTO_SOURCE_2026_RENEWAL_SINGLE_TUBE","render_alpha":True},
 {"id":"2026-hikoco-tube-photo","url":"https://hikoco.co.nz/cdn/shop/files/hikoco_Goodal_GreenTangerineVitaCDarkCircleEyeCream26_01.jpg?v=1772406150",
 "type":"PHOTO_SOURCE_2026_RENEWAL_TUBE_AND_CREAM_TEXTURE","render_alpha":False},
 {"id":"official-GS-store-25AD-tube-with-gift-ad","url":"https://asset.m-gs.kr/prod/64899358/1/550",
 "type":"BRAND_OFFICIAL_STORE_PHOTO_HAS_EXTRA_GIFT_NOT_SINGLE_PHOTO","render_alpha":False}
]
HEAD={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/jpeg,image/png,*/*"}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
alpha_result={"status":"HOLD_NO_REAL_SINGLE_TUBE_SOURCE","from_source":None}
for i,item in enumerate(CASES,1):
 result={"position":i,"id":item["id"],"source":item["url"],
  "source_role":item["type"],"source_product_generation":"2026_RENEWAL_TUBE_CANDIDATE",
  "status":"NOT_AVAILABLE"}
 try:
  r=requests.get(item["url"],headers=HEAD,timeout=18)
  r.raise_for_status()
  assert len(r.content)<7_000_000
  original=Image.open(BytesIO(r.content));original.load()
  assert min(original.size)>=350
  rgb=ImageOps.exif_transpose(original).convert("RGB")
  dest=OUT/f"{i:02d}-{item['id']}-1080-QA.jpg"
  white=Image.new("RGB",(1080,1080),"#ffffff")
  scaled=ImageOps.contain(rgb,(1045,1045),Image.Resampling.LANCZOS)
  white.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
  white.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
  assert dest.stat().st_size<2_000_000
  result.update({"status":"SOURCE_SAVED_VISUAL_QA_PENDING",
    "source_format":original.format,"source_size":list(original.size),
    "qa_jpg":dest.name,"jpg_sha256":sha(dest)})
  if item["render_alpha"]:
   # Use ORIGINAL real tube photograph, not rendered product geometry.
   try:
    cut=remove(white.convert("RGBA"),session=new_session("isnet-general-use"),
     alpha_matting=True,alpha_matting_foreground_threshold=230,
     alpha_matting_background_threshold=18,alpha_matting_erode_size=4)
    assert cut.mode=="RGBA"
    alpha=np.array(cut.getchannel("A"))
    bbox=cut.getchannel("A").getbbox()
    assert bbox
    cover=float(np.mean(alpha>=128))
    cnt,label,stats,centroid=cv2.connectedComponentsWithStats(np.uint8(alpha>=128),connectivity=8)
    areas=sorted([int(stats[k,cv2.CC_STAT_AREA]) for k in range(1,cnt) if stats[k,cv2.CC_STAT_AREA]>=30],reverse=True)
    main_ratio=areas[0]/sum(areas) if areas else 0
    safe=bool(.025<cover<.78 and bbox[2]-bbox[0]>120 and bbox[3]-bbox[1]>420 and main_ratio>.93)
    alpha_result.update({"from_source":dest.name,"mask_coverage":round(cover,4),
      "bbox":list(bbox),"single_component_ratio":round(main_ratio,4),
      "mask_geometry_pass":safe,"status":"HOLD_MASK_QA_FAIL"})
    if safe:
     isolated=cut.crop(bbox)
     png=OUT/"01-real-2026-renewal-yellow-tube-transparent-QA.png"
     isolated.save(png,optimize=True)
     hero=Image.new("RGB",(1080,1080),"white")
     d=ImageDraw.Draw(hero)
     d.rounded_rectangle((50,50,1030,1030),radius=36,outline="#e4e4dc",width=2)
     d.text((91,94),"GOODAL",font=ft(43,True),fill="#414637")
     d.text((91,161),"Green Tangerine Vita C Eye Cream 30mL",font=ft(25),fill="#797d69")
     fit=ImageOps.contain(isolated,(870,780),Image.Resampling.LANCZOS)
     hero.paste(fit,((1080-fit.width)//2,208+(790-fit.height)//2),fit)
     d.text((91,993),"2026 RENEWAL TUBE PHOTO  |  QA ONLY",font=ft(19),fill="#888d79")
     jpg=OUT/"01-real-2026-renewal-yellow-tube-alpha-hero-1080-QA.jpg"
     hero.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
     assert jpg.stat().st_size<2_000_000
     alpha_result.update({"status":"TRUE_TUBE_ALPHA_RENDERED_NEEDS_VISUAL_QA",
      "png":png.name,"jpg":jpg.name,"png_sha256":sha(png),
      "jpg_sha256":sha(jpg),"jpg_bytes":jpg.stat().st_size})
   except Exception as exc:
    alpha_result.update({"status":"HOLD_SEGMENTATION_FAILURE",
      "error_type":type(exc).__name__,"error":str(exc)[:230]})
 except Exception as exc:
  result.update({"status":"HOLD_IMAGE_UNAVAILABLE","reason":str(exc)[:230]})
 sources.append(result)
# Contact proof does not require all remote sources to be available.
contact=Image.new("RGB",(1840,550),"#f1f1ef")
d=ImageDraw.Draw(contact)
d.text((16,16),"v2813 GOODAL NEW 25AD YELLOW TUBE REFERENCES / NOT OLD PUMP",font=ft(25,True),fill="#292929")
for i,row in enumerate(sources):
 if row.get("qa_jpg"):
  with Image.open(OUT/row["qa_jpg"]) as im:
   thumb=im.convert("RGB").resize((425,425),Image.Resampling.LANCZOS)
  contact.paste(thumb,(10+610*i,62))
d.text((15,505),"1 SINGLE 2026 RENEWAL    2 ALTERNATE RENEWAL PHOTO    3 OFFICIAL 25AD + GIFT (REFERENCE ONLY)",font=ft(17),fill="#333333")
p=OUT/"v2813-new-tube-source-and-alpha-photo-review.jpg"
contact.save(p,"JPEG",quality=82,optimize=True)
(OUT/"v2813-new-tube-source-contact.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode("ascii"))
if alpha_result.get("jpg"):
 with Image.open(OUT/alpha_result["jpg"]) as im:
  left=Image.open(OUT/sources[0]["qa_jpg"]).convert("RGB").resize((530,530),Image.Resampling.LANCZOS)
  right=im.convert("RGB").resize((530,530),Image.Resampling.LANCZOS)
 compared=Image.new("RGB",(1120,610),"#eeeeec")
 compared.paste(left,(12,60));compared.paste(right,(572,60))
 ImageDraw.Draw(compared).text((17,15),"ORIGINAL 2026 TUBE vs TRUE TRANSPARENT ALPHA JPG | QA ONLY",font=ft(22,True),fill="#292929")
 comp=OUT/"v2813-renewal-tube-alpha-before-after.jpg"
 compared.save(comp,"JPEG",quality=84,optimize=True)
 (OUT/"v2813-alpha-contact.b64.txt").write_text(base64.b64encode(comp.read_bytes()).decode("ascii"))
record={"version":"v2813","baseline":"v2812","family":"pending-21",
 "product":"GOODAL Green Tangerine Vita C Eye Cream 30mL",
 "actual_new_source_photos_saved":sum(bool(s.get("qa_jpg")) for s in sources),
 "alpha_result":alpha_result,"photo_sources":sources,
 "source_validation":[
  {"name":"Shilla Duty Free","url":"https://m.shilladfs.com/estore/kr/ko/p/5754369","sku":"669210000423","net_content":"30mL","edition":"25AD","selling_unit":"single"},
  {"name":"GS SHOP official CLIO store","url":"https://m.gsshop.com/prd/prd.gs?mseq=402535-4_17-175072&prdid=64899358","edition":"25AD","packaging":"yellow tube silver cap","promotional_gift_in_picture":True},
  {"name":"2026 tube renewal image","url":CASES[0]["url"],"packaging":"yellow tube silver cap","retailer_unlicensed_reference_only":True}],
 "old_PUMP_references_v2811_v2812_not_reused":True,
 "same_exact_owned_stock_edition_verified":False,
 "commercial_image_redistribution_rights_verified":False,
 "original_MK_logo_authenticated":False,
 "retail_approved":False,
 "prior_11_approved_families_unchanged":True,
 "previous_55_verified_public_URLs_unchanged":True,
 "previous_QA_artifacts_untouched":True,
 "final_excel_or_spreadsheet_shared":False}
(OUT/"manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2813","saved_photo_refs":record["actual_new_source_photos_saved"],
 "alpha_status":alpha_result["status"],"approved_for_sale":False}))
