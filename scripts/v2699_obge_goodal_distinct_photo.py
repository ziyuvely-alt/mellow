#!/usr/bin/env python3
"""v2699 no fabrication. Crop the exact single upright GOODAL 30mL eye tube
from existing 1010x472 single-SKU retailer photo, preserving physical product
pixels. Investigate official OBGE product gallery without using unrelated images.
Neither staged candidate is approved for commercial republication.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,re,hashlib,base64,requests
OUT=Path("qa-review/v2699-OBGE-original-gallery-and-GOODAL-single-tube-QA")
assert not OUT.exists();OUT.mkdir(parents=True)
HEAD={"User-Agent":"Mozilla/5.0","Accept":"text/html,image/avif,image/jpeg,image/png,image/webp,*/*"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={"version":"v2699","baseline":"v2698","retail_approval":False,
"goodal":{"source":"https://product-image.kurly.com/product/image/8880a713-9c74-484c-adfd-846bce7e1d3a.jpg",
"expected":"GOODAL Green Tangerine Vita C Dark Spot Eye Cream 30mL",
"status":"HOLD_NO_VALID_SINGLE_TUBE_CROP"},
"obge":{"page":"https://obge.co.kr/product/오일-컨트롤-피니셔/1206",
"expected":"OBgE Oil Control Finisher 5g","status":"HOLD_NO_EXACT_MAIN_IMAGE"},
"existing_11_approved_families_unchanged":True,"public_55_urls_unchanged":True,
"final_xlsx_shared":False}
# Cropping product geometry uses real photographed pixels; never add product elements.
try:
 req=requests.get(result["goodal"]["source"],headers=HEAD,timeout=17);req.raise_for_status()
 im=Image.open(BytesIO(req.content)).convert("RGB")
 w,h=im.size
 assert w>=900 and h>=400,(w,h)
 # standing tube at approximately x=57-70% of full source photo and centered y.
 # retain enough negative space to show entire packaging (no generative inpainting).
 bounds=(round(.50*w),round(.015*h),round(.80*w),round(.985*h))
 crop=im.crop(bounds)
 output=Image.new("RGB",(1080,1080),"white")
 # upscale only to 850px height, keep real-source aspect ratio, no artificial cutout.
 placed=ImageOps.contain(crop,(850,900),Image.Resampling.LANCZOS)
 output.paste(placed,((1080-placed.width)//2,(1080-placed.height)//2))
 file=OUT/"GOODAL-30mL-single-upright-original-photo-crop-QA.jpg"
 output.save(file,"JPEG",quality=93,optimize=True,subsampling=0)
 assert file.stat().st_size<2000000
 result["goodal"].update({"status":"SINGLE_TUBE_CROP_VISUAL_QA_PENDING","source_pixels":[w,h],
  "crop_original_pixels":list(bounds),"cropped_single_photo":file.name,"photo_sha256":sha(file),
  "product_ref_in_prior_single_product_listing":"https://www.kurly.com/goods/1001465618"})
except Exception as exc:
 result["goodal"].update({"status":"HOLD_SINGLE_TUBE_SOURCE_OR_CROP_FAILED",
  "failure":str(exc)[:250]})
# Official OBGE Cafe24 page image links may be in lazy attributes, JSON or CSS.
try:
 url=result["obge"]["page"]
 response=requests.get(url,headers=HEAD,timeout=16);response.raise_for_status()
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(response.text,"html.parser")
 title=soup.title.get_text(" ",strip=True) if soup.title else ""
 if "오일 컨트롤 피니셔" not in title:raise ValueError("wrong official product page")
 candidates=[]
 def add(u,context):
  if not u or u.startswith(("data:","javascript:")):return
  full=urljoin(url,u.replace("&amp;","&"))
  host=(urlparse(full).hostname or "").lower()
  if not (host.endswith("obge.co.kr") or host.endswith("cafe24img.com") or host.endswith("cafe24.com") or host.endswith("obge.com")):return
  low=full.lower()
  if any(p in low for p in ("product/big","product/extra","product/medium","/prdimg/","/product/202","/goods/1206","/web/product/")):
   candidates.append((full,context))
 for m in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
  add(m.get("content"),"meta")
 for image in soup.find_all("img"):
  attrs=" ".join([str(image.get("src") or ""),str(image.get("class") or ""),str(image.get("alt") or "")])
  for k in ("src","data-src","data-original","data-zoom","data-image","data-large"):
   add(image.get(k),"img:"+attrs[:50])
 # Cafe24 embeds full-sized main /web/product/big path in product data.
 raw=response.text.replace("\\/","/")
 paths=re.findall(r'''(?:https?:)?//[^"'<> ]+?/web/product/(?:big|extra|medium)/[^"'<> ]+?\.(?:jpg|jpeg|png|webp)''',raw,re.I)
 paths+=re.findall(r'''/web/product/(?:big|extra|medium)/[^"'<> ]+?\.(?:jpg|jpeg|png|webp)''',raw,re.I)
 for path in paths:add(path,"raw_catalog")
 seen=set();unique=[]
 for u,role in candidates:
  if u not in seen:unique.append((u,role));seen.add(u)
 result["obge"]["source_url_candidates"]=[{"url":u,"role":role} for u,role in unique[:30]]
 for u,role in unique[:22]:
  try:
   dl=requests.get(u,headers=HEAD,timeout=12);dl.raise_for_status()
   if len(dl.content)>8000000:continue
   im=Image.open(BytesIO(dl.content));im.load()
   if min(im.size)<440:continue
   photo=ImageOps.exif_transpose(im).convert("RGB")
   art=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(photo,(1040,1040),Image.Resampling.LANCZOS)
   art.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   path=OUT/f"OBGE-source-candidate-{len(result['obge'].get('photos',[]))+1:02d}-QA.jpg"
   art.save(path,"JPEG",quality=91,optimize=True)
   assert path.stat().st_size<2000000
   result["obge"].setdefault("photos",[]).append({"file":path.name,"url":u,"source_pixels":list(im.size),"sha256":sha(path)})
   if len(result["obge"]["photos"])>=6:break
  except (OSError,ValueError,requests.RequestException):continue
 if result["obge"].get("photos"):
  result["obge"]["status"]="OFFICIAL_DOMAIN_PHOTO_CANDIDATES_STAGED_VISUAL_QA_PENDING"
 else:result["obge"]["status"]="HOLD_NO_DECODABLE_OFFICIAL_PRODUCT_GALLERY"
except Exception as exc:
 result["obge"]["status"]="HOLD_OFFICIAL_HTML_OR_IMAGES_INACCESSIBLE"
 result["obge"]["failure"]=str(exc)[:260]
files=[p for p in OUT.glob("*.jpg")]
if files:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
 board=Image.new("RGB",(1815,80+420*((len(files)+3)//4)),"#f0f0ef")
 draw=ImageDraw.Draw(board)
 draw.text((18,16),"v2699 SINGLE PRODUCT PHOTO QA / NEVER RETAIL AUTO-APPROVE",font=font,fill="#292929")
 for idx,p in enumerate(files):
  with Image.open(p) as im:
   im.load()
   thumb=im.convert("RGB").resize((338,338),Image.Resampling.LANCZOS)
  x=16+idx%4*450;y=68+idx//4*420
  board.paste(thumb,(x,y))
  draw.text((x,y+344),p.name[:25],font=font,fill="#292929")
 file=OUT/"v2699-crop-and-official-source-proof.jpg"
 board.save(file,"JPEG",quality=83,optimize=True)
 (OUT/"v2699-proof.b64.txt").write_text(base64.b64encode(file.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"goodal":result["goodal"]["status"],"obge":result["obge"]["status"],
 "obge_official_photos":len(result["obge"].get("photos",[])),
 "new_sale_approvals":0},ensure_ascii=False))
