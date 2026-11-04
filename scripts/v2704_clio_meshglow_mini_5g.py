#!/usr/bin/env python3
"""v2704 inspect official CLIO mesh glow essential mini 5g gallery, no kit photos.
Source page 0000006954 is official single mini, not 6182 15g+refill promo.
Use exact source title and 5g spec; archive candidates only for visual QA.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from io import BytesIO
import requests,json,hashlib,re,base64,html
OUT=Path("qa-review/v2704-clio-meshglow-mini-5g-genuine-source")
assert not OUT.exists()
OUT.mkdir(parents=True)
URL="https://clubclio.co.kr/shop/goodsView/0000006954"
HEAD={"User-Agent":"Mozilla/5.0","Accept":"text/html,image/avif,image/jpeg,image/png,image/webp,*/*"}
rpt={"version":"v2704","family":"pending-04","product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g",
"official_item_url":URL,"retail_approved":False,"old_approved_11_families_unchanged":True,
"existing_55_public_urls_unchanged":True,"existing_pending04_QA_untouched":True,
"photo_rights_verified":False,"exact_stock_edition_verified":False,"final_xlsx_shared":False,
"images":[]}
try:
 resp=requests.get(URL,headers=HEAD,timeout=16);resp.raise_for_status()
 resp.encoding=resp.apparent_encoding or "utf-8"
 soup=BeautifulSoup(resp.text,"html.parser")
 title=soup.title.get_text(" ",strip=True) if soup.title else ""
 body=soup.get_text(" ",strip=True)
 rpt["official_html_title"]=title
 if "킬커버 메쉬 글로우 에센셜 쿠션 미니" not in body:
  raise ValueError("Official mini product name does not appear in product page text")
 if "5g" not in body.lower() and "5 g" not in body.lower():
  raise ValueError("Standalone mini 5g capacity not verified")
 urls=[]
 for m in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
  if m.get("content"):urls.append((urljoin(URL,m["content"]),"metadata"))
 for i,img in enumerate(soup.find_all("img")):
  alt=(img.get("alt") or "").lower()
  props=" ".join([str(img.get("src") or ""),str(img.get("class") or ""),str(img.get("id") or "")]).lower()
  if not (any(x in props for x in ["detail","goods","product","goodsview","goodsimg","mainimg","swiper","thumb"]) or "쿠션 미니" in alt):
   continue
  for k in ("src","data-src","data-original","data-lazy","data-image","data-zoom"):
   if img.get(k):urls.append((urljoin(URL,img[k]),"product_candidate"))
 for u in re.findall(r'''(?:https?:)?//[^"'<>\s]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"'<> ]*)?''',resp.text,re.I)[:150]:
  if any(w in u.lower() for w in ["goods","item","product","detail"]):
   urls.append((urljoin(URL,u),"embedded"))
 seen=set();unique=[]
 for u,role in urls:
  host=(urlparse(u).hostname or "").lower()
  if u in seen or not(host.endswith("clubclio.co.kr") or host.endswith("clio.co.kr") or host.endswith("clio.com") or host.endswith("amazonaws.com") or host.endswith("cloudfront.net")):
   continue
  seen.add(u);unique.append((u,role))
 rpt["candidate_urls"]=list(x[0] for x in unique[:35])
 for u,role in unique[:32]:
  if any(b in u.lower() for b in ("/event","/banner","thumbnail_review","best_review")):continue
  try:
   dl=requests.get(u,headers=HEAD,timeout=10);dl.raise_for_status()
   if len(dl.content)>7500000:continue
   original=Image.open(BytesIO(dl.content));original.load()
   if min(original.size)<410:continue
   rgb=ImageOps.exif_transpose(original).convert("RGB")
   output=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(rgb,(1040,1040),Image.Resampling.LANCZOS)
   output.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   dest=OUT/f"{len(rpt['images'])+1:02d}-CLIO-mini-official-media-QA.jpg"
   output.save(dest,"JPEG",quality=91,optimize=True,subsampling=0)
   assert dest.stat().st_size<2_000_000
   rpt["images"].append({"file":dest.name,"url":u,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"original_px":list(original.size)})
   if len(rpt["images"])>=12:break
  except (requests.RequestException,OSError,ValueError):continue
 rpt["status"]="CANDIDATES_NEED_VISUAL_PRODUCT_ONLY_QA" if rpt["images"] else "HOLD_NO_DECODABLE_PRODUCT_ONLY_PHOTO"
except Exception as exc:
 rpt["status"]="HOLD_SOURCE_ACCESS_OR_ITEM_IDENTITY"
 rpt["error_type"]=type(exc).__name__
 rpt["error"]=str(exc)[:240]
if rpt["images"]:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",23)
 rows=(len(rpt["images"])+3)//4
 board=Image.new("RGB",(1810,75+rows*425),"#f0f0ee")
 d=ImageDraw.Draw(board)
 d.text((14,15),"v2704 CLIO OFFICIAL MESH GLOW MINI 5G ONLY / UNAPPROVED PHOTOS",fill="#262626",font=font)
 for i,x in enumerate(rpt["images"]):
  with Image.open(OUT/x["file"]) as im:tile=im.convert("RGB").resize((334,334),Image.Resampling.LANCZOS)
  px=15+(i%4)*451;py=60+(i//4)*425
  board.paste(tile,(px,py))
  d.text((px,py+339),f"SOURCE {i+1:02d}",font=font,fill="#222222")
 proof=OUT/"v2704-clio-mini-contact.jpg"
 board.save(proof,"JPEG",quality=83,optimize=True)
 (OUT/"v2704-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(rpt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":rpt["status"],"official_photo_candidates":len(rpt["images"]),"retail_approved":0}))
