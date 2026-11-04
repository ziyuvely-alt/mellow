#!/usr/bin/env python3
"""v2794 CLIO three remaining noncurated product families: official high-resolution
detail photo scouting, not a release. Do NOT re-fetch v2793 502/600px thumbnails.
Stage only new larger official product-detail image candidates (>700px long dimension)
or explicit product detail section images, preserving native bytes and honest provenance.

Sources remain rights/stock/bundle HOLD. No changes to previous 11 retail approvals
or 55 public URLs, no XLSX, no fabricated product photography.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.parse import urljoin,urlparse,unquote
from collections import defaultdict
import requests,json,re,hashlib,base64,html,os
OUT=Path("qa-review/v2794-clio-official-detail-original-photo-discovery")
assert not OUT.exists()
OUT.mkdir(parents=True)
CASES=[
 dict(family="pending-05",name="CLIO Kill Cover Founwear Mini",
      candidates=[5750,7108],expected=["파운웨어","founwear"],
      known_hold="5750/7108 image includes full-size and mini case; owned stock mini edition/5g unclear"),
 dict(family="pending-06",name="CLIO Mesh Glow Essential Cushion",
      candidates=[6182],expected=["메쉬 글로우 에센셜","mesh glow essential"],
      known_hold="6182 is a main+refill set listing; individual 15g product to be confirmed"),
 dict(family="pending-07",name="CLIO Mesh Blur Cushion",
      candidates=[6455],expected=["메쉬 블러","mesh blur"],
      known_hold="6455 is a set listing; single vs refill and shade not proven"),
]
UA={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Accept-Language":"ko-KR,ko;q=0.9","Accept":"text/html,image/webp,image/jpeg,image/png,*/*"}
safe_hosts={"clubclio.co.kr","www.clubclio.co.kr","clubclio.shop","www.clubclio.shop","cdn.shopify.com"}
def sha(b):return hashlib.sha256(b).hexdigest()
def to_url(raw,base):
 if not raw:return None
 x=html.unescape(raw.strip()).replace("\\/","/").replace("&#39;","'")
 if x.startswith(("data:","blob:","javascript:","#","mailto:")):return None
 if x.startswith("//"):x="https:"+x
 u=urljoin(base,x)
 parts=urlparse(u)
 if parts.scheme not in ("https","http"):return None
 if parts.hostname not in safe_hosts:return None
 # eliminate files that are likely brand navigation, reviews, or unrelated items
 lower=u.lower()
 if any(y in lower for y in ("icon","logo","review","banner","event","promotion","ranking","btn_","cart_","sns_")):return None
 if re.search(r'/images/product/00/00/00/\d\d/\d\d/[mblor]\.(?:gif|jpg)$',lower):return None
 return u
results=[]
for c in CASES:
 row={"family":c["family"],"product":c["name"],"pages":[],
      "high_resolution_originals":[],"identity_hold":c["known_hold"],
      "commercial_use_license_verified":False,
      "owned_stock_generation_verified":False,
      "retail_approved":False,"status":"HOLD_DETAIL_PHOTO_NOT_YET_VERIFIED"}
 family_dir=OUT/c["family"];family_dir.mkdir()
 seen_bytes=set()
 for pid in c["candidates"]:
  base=f"https://clubclio.co.kr/shop/goodsView/{pid}"
  page={"id":pid,"url":base,"status":"NO_NEW_IMAGE","candidates":0,"downloaded":0}
  try:
   r=requests.get(base,headers=UA,timeout=15);r.raise_for_status()
   soup=BeautifulSoup(r.text,"html.parser")
   text=" ".join(soup.get_text(" ",strip=True).split())
   page["full_page_target_word_present"]=any(x.lower() in text.lower() for x in c["expected"])
   if not page["full_page_target_word_present"]:
    page["status"]="HOLD_PAGE_IDENTITY_NOT_MATCHED";row["pages"].append(page);continue
   heads=[x.get_text(" ",strip=True) for x in soup.select("h1,h2,h3,.goods_name,.goodsName,.prod_tit") if x.get_text(" ",strip=True)]
   page["product_heading_candidates"]=heads[:12]
   page["bundle_cues_present"]=bool(re.search(r"본품.{0,5}리필|기획세트|증정|GIFT|세트",text,re.I))
   # Product-specific detailed content, not global page recommendation thumbnails.
   regions=[]
   for selector in ("#goodsDetail","#goods_detail","#goodsInfo","#goods_info",
     "#detail","#productDetail",".goodsDetail",".goods_detail",".goods_detail_view",
     ".goods_view_detail",".item-detail",".product-detail",".detail_con",".detailContents",
     ".goods_detail_content",".goods_view_cont",".detailArea",".detail_area"):
    for node in soup.select(selector):
     if not any(node is existing for existing in regions):regions.append(node)
   page["detail_regions_found"]=len(regions)
   image_urls=[]
   for node in regions:
    for im in node.find_all("img"):
     for key in ("src","data-src","data-original","data-lazy","data-image","data-large","data-srcset"):
      raw=im.get(key)
      if raw:
       for part in (raw.split(",") if key.endswith("srcset") else [raw]):
        u=to_url(part.split(" ")[0],base)
        if u:image_urls.append((u,"product_detail_section"))
   # Many Cafe24 / ESM detail HTML image references are escaped JSON strings.
   for raw in re.findall(r"""(?:https?:)?(?://[^"'<> \n]+|/[^"'<> \n]+)\.(?:jpg|jpeg|png|webp)(?:\?[^"'<> \n]+)?""",r.text,re.I):
    u=to_url(raw,base)
    if u and any(seg in u.lower() for seg in ("/goods/detail","/goods/editor","/product/detail","/upload/","/detail/","/editor/","/web/product/","/goods/")):
     image_urls.append((u,"product_page_embedded_asset"))
   # Generic page og:image is not added: v2793 already captured 600px thumbnails.
   unique=[];seen=set()
   for u,role in image_urls:
    if u not in seen:unique.append((u,role));seen.add(u)
   page["discovered_unique_candidate_urls"]=len(unique)
   page["sample_candidate_urls"]=[u for u,_ in unique[:12]]
   for u,role in unique[:18]:
    if len(row["high_resolution_originals"])>=10:break
    try:
     rr=requests.get(u,headers={"User-Agent":UA["User-Agent"],"Referer":base},timeout=12)
     if rr.status_code!=200 or len(rr.content)>12000000:continue
     pic=Image.open(BytesIO(rr.content));pic.load()
     w,h=pic.size
     # high-res photographs only, 600 px already in v2793
     if max(w,h)<800 or min(w,h)<250:continue
     # Avoid long marketing infographics masquerading as single packshots;
     # preserved only as distinct reference, never suitable by default.
     digest=sha(rr.content)
     if digest in seen_bytes:continue
     seen_bytes.add(digest)
     im=ImageOps.exif_transpose(pic).convert("RGB")
     full=family_dir/f"{len(row['high_resolution_originals'])+1:02d}-official-{pid}-native-source-reference.{pic.format.lower() if pic.format and pic.format.lower() in ('jpeg','png','webp') else 'jpg'}"
     if pic.format=="JPEG":full.write_bytes(rr.content)
     else:pic.save(full)
     preview=ImageOps.contain(im,(1040,1040),Image.Resampling.LANCZOS)
     square=Image.new("RGB",(1080,1080),"white")
     square.paste(preview,((1080-preview.width)//2,(1080-preview.height)//2))
     jpg=family_dir/f"{len(row['high_resolution_originals'])+1:02d}-official-{pid}-photo-reference-1080-QA.jpg"
     square.save(jpg,"JPEG",quality=90,optimize=True)
     if jpg.stat().st_size>=2_000_000:
      jpg.unlink();full.unlink();continue
     row["high_resolution_originals"].append({"official_page":base,"source":u,"source_type":role,
       "original_dimensions":[w,h],"original_sha256":digest,
       "native_file":str(full.relative_to(OUT)),"qa_jpg":str(jpg.relative_to(OUT)),
       "qa_jpg_sha256":sha(jpg.read_bytes()),
       "product_identity_verified_in_photo":False,
       "bundle_or_gift_excluded_by_visual_review":False,"retail_approved":False})
     page["downloaded"]+=1
    except (OSError,requests.RequestException,ValueError):continue
   page["status"]="NEW_HIGH_RES_REFERENCES_STAGED_FOR_VISUAL_QA" if page["downloaded"] else "NO_NEW_HIGH_RES_PHOTOS_RETRIEVED"
  except Exception as e:
   page["status"]="PAGE_OR_DOWNLOAD_ERROR";page["error"]=str(e)[:210]
  row["pages"].append(page)
 row["status"]="NEW_NATIVE_PHOTO_CANDIDATES_FOR_VISUAL_QA" if row["high_resolution_originals"] else "HOLD_NO_NEW_HIGH_RES_ITEM_PHOTOS"
 results.append(row)
# Proof sheets per family, also produce a text-based source identity log on empty.
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
for row in results:
 pics=row["high_resolution_originals"]
 canvas=Image.new("RGB",(1715,72+430*max(1,(len(pics)+3)//4)),"#f0f0ef")
 d=ImageDraw.Draw(canvas)
 d.text((17,13),f"v2794 {row['family']} NEW OFFICIAL NATIVE REFERENCES / NEVER RETAIL",font=font,fill="#262626")
 for n,x in enumerate(pics):
  with Image.open(OUT/x["qa_jpg"]) as img:
   tile=img.convert("RGB").resize((315,315),Image.Resampling.LANCZOS)
  px=16+(n%4)*427;py=58+(n//4)*430
  canvas.paste(tile,(px,py))
  d.text((px,py+326),f"{x['original_dimensions'][0]}x{x['original_dimensions'][1]} ID {x['official_page'].split('/')[-1]}",font=font,fill="#252525")
 if not pics:d.text((20,105),"NO NEW EXACT-ITEM HIGH-RES PHOTO; DO NOT INVENT A SOURCE",font=font,fill="#555555")
 proof=OUT/f"v2794-{row['family']}-photo-proof.jpg"
 canvas.save(proof,"JPEG",quality=83,optimize=True)
 (OUT/f"v2794-{row['family']}-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
manifest={"version":"v2794","baseline":"v2793","families_searched":3,"page_count":sum(len(x["pages"]) for x in results),
 "new_original_high_resolution_photo_files":sum(len(x["high_resolution_originals"]) for x in results),
 "never_reuse_v2793_502_600_catalog_thumb":True,
 "no_previous_QA_JPGs_changed":True,"previous_11_approved_families_untouched":True,
 "verified_55_public_urls_untouched":True,"original_MK_logo_not_proven":True,
 "commercial_photo_licensing_unverified":True,"stock_package_edition_unverified":True,
 "new_retail_approvals":0,"final_spreadsheet_not_shared":True,
 "products":results}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2794","new_official_highres_assets":manifest["new_original_high_resolution_photo_files"],
 "states":[{"family":x["family"],"status":x["status"],"new_files":len(x["high_resolution_originals"])} for x in results],
 "new_retail_approvals":0},ensure_ascii=False))
