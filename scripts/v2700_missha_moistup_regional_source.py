#!/usr/bin/env python3
"""v2700 2-shade official regional MISSHA Magic Cushion Moist Up source QA.
Acquire the original four Shopify product media frames, filter exact item,
do not infer user's 21/23 stock edition or authorize commercialization.
Distinct scenes are reviewed before replacing any previously staged QA cards.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,base64,hashlib
OUT=Path("qa-review/v2700-missha-moistup-regional-exact-product-photo-proofs")
assert not OUT.exists()
OUT.mkdir(parents=True)
PAGE="https://www.misshame.com/products/m-magic-cushion-moisture-spf50-pa"
HEAD={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/html,image/jpeg,image/png,image/webp,*/*"}
report={"version":"v2700","baseline":"v2699","family":"pending-02","product":"MISSHA Magic Cushion Moist Up 21/23",
"regional_source_page":PAGE,"photos":[],"candidate_photo_links":[],
"region_edition_vs_korean_stock_verified":False,
"photo_commercial_use_permission_verified":False,
"retail_approved":False,"prior_5_JPG_QA_set_untouched":True,
"11_approved_families_untouched":True,"public_55_URLs_untouched":True,"final_xlsx_shared":False}
try:
 product_json=PAGE+".js"
 res=requests.get(product_json,headers=HEAD,timeout=16);res.raise_for_status()
 pdata=res.json()
 title=pdata.get("title","")
 if not all(x in title.lower() for x in ("magic","cushion","moist")):
  raise ValueError("Store product title mismatch")
 report["regional_product_title"]=title
 report["variants"]=[{"title":v.get("title"),"sku":v.get("sku")} for v in pdata.get("variants",[])[:12]]
 urls=[]
 for item in pdata.get("images",[]):
  if isinstance(item,str):urls.append(item)
  elif isinstance(item,dict):urls.append(item.get("src") or "")
 # Fallback to Shopify product HTML if images absent.
 if not urls:
  html=requests.get(PAGE,headers=HEAD,timeout=15);html.raise_for_status()
  soup=BeautifulSoup(html.text,"html.parser")
  for meta in soup.select('meta[property="og:image"]'):
   urls.append(meta.get("content") or "")
 seen=set()
 urls=[urljoin(PAGE,u) for u in urls if u]
 urls=[u for u in urls if not (u in seen or seen.add(u))]
 report["candidate_photo_links"]=urls[:20]
 for u in urls[:12]:
  try:
   d=requests.get(u,headers=HEAD,timeout=12);d.raise_for_status()
   if len(d.content)>8000000:continue
   im=Image.open(BytesIO(d.content));im.load()
   if min(im.size)<400:continue
   im=ImageOps.exif_transpose(im).convert("RGB")
   target=OUT/f"{len(report['photos'])+1:02d}-Missha-regional-real-photo-reference.jpg"
   square=Image.new("RGB",(1080,1080),"white")
   fit=ImageOps.contain(im,(1040,1040),Image.Resampling.LANCZOS)
   square.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
   square.save(target,"JPEG",quality=92,optimize=True,subsampling=0)
   assert target.stat().st_size<2_000_000
   report["photos"].append({"file":target.name,"source_url":u,
     "source_px":list(im.size),"sha256":hashlib.sha256(target.read_bytes()).hexdigest()})
   if len(report["photos"])>=8:break
  except (OSError,requests.RequestException,ValueError):
   continue
 report["status"]="REGIONAL_SOURCE_PHOTO_CANDIDATES_PENDING_GENERATION_CHECK" if report["photos"] else "HOLD_NO_PRODUCT_MEDIA_AVAILABLE"
except Exception as exc:
 report["status"]="HOLD_REGIONAL_PAGE_ACCESS_OR_IDENTITY"
 report["error_type"]=type(exc).__name__;report["error"]=str(exc)[:240]
if report["photos"]:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
 cols=4;rows=(len(report["photos"])+3)//4
 board=Image.new("RGB",(1810,85+430*rows),"#eff0ee")
 draw=ImageDraw.Draw(board)
 draw.text((20,18),"v2700 MISSHA MAGIC CUSHION MOIST UP | REGIONAL PHOTO QA ONLY",font=font,fill="#252525")
 for idx,x in enumerate(report["photos"]):
  with Image.open(OUT/x["file"]) as im:
   thumb=im.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
  px=18+(idx%4)*450;py=65+(idx//4)*430
  board.paste(thumb,(px,py))
  draw.text((px,py+343),f"REGIONAL SOURCE {idx+1}",font=font,fill="#252525")
 fp=OUT/"v2700-source-proof.jpg";board.save(fp,"JPEG",quality=85,optimize=True)
 (OUT/"v2700-proof.b64.txt").write_text(base64.b64encode(fp.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"family":"pending-02","sources":len(report["photos"]),
"status":report["status"],"retail_approved":0}))
