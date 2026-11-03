#!/usr/bin/env python3
"""Recover exact official 145ml PIXEL PURE Gentle Gel to Foam cleanser photo sources.
Guard against accidental 150ml external/reused packaging. Product official page only;
stage originals for visual label inspection. No customer image or workbook creation.
"""
import io,hashlib,json,re
from urllib.parse import urljoin,urlparse
from urllib.request import urlopen,Request
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image,ImageOps,ImageDraw,ImageFont
url="https://www.pixelpure.com/product/detail.html?product_no=21"
out=Path("v2533-pixelpure-cleanser-official145-source");out.mkdir(exist_ok=True)
manifest={"date":"2026-11-04","family":"pending-26","target":"PIXEL PURE Gentle Gel to Foam Cleanser 145 ml",
"official_url":url,"official_name_verified":False,"actual_source_images":[],"excluded_150ml_image_candidates":[],
"commercial_rights_checked":False,"real_owned_stock_145ml_physically_verified":False,
"no_reused_150ml_photo":True,"new_public_urls":0,"excel_shared":False}
try:
 with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=24) as r:
  html=r.read(7_000_000).decode("utf-8","replace")
 if not (("젠틀 젤투폼 클렌저 145ml" in html) or ("젠틀 젤투폼 클렌저 145ML" in html)):
  raise ValueError("Exact official 145ml product name absent; do not scrape images")
 manifest["official_name_verified"]=True
 soup=BeautifulSoup(html,"html.parser")
 photos=[]
 # Evidence comes from exact product's own image region, not recommended products.
 for tag in soup.find_all("meta"):
  if tag.get("property") in ("og:image","twitter:image") and tag.get("content"):photos.append((tag.get("content"),"meta-og"))
 for selector in [".prdImg img",".keyImg img",".xans-product-image img",
                  "#prdDetail img",".cont img",".detail img",".xans-product-detail img"]:
  for x in soup.select(selector):
   v=x.get("data-src") or x.get("src") or x.get("data-original")
   if v:photos.append((v,selector))
 # Embedded static product detail images also appear in data-escaped HTML.
 for match in re.findall(r'(?:"|&#34;)(?:src|data-src)(?:"|&#34;)\s*[:=]\s*(?:"|&#34;)([^"<>]+?\.(?:jpg|jpeg|webp|png)(?:\?[^"<>]*)?)(?:"|&#34;)',html,re.I):
  photos.append((match,"embedded-detail"))
 seen_urls=set();seen_sha=set();tiles=[]
 for src,section in photos:
  if len(manifest["actual_source_images"])>=30:break
  src=src.replace("&amp;","&").strip()
  if src.startswith("//"):src="https:"+src
  real=urljoin(url,src)
  if real in seen_urls or not real.startswith("https://"):continue
  seen_urls.add(real)
  try:
   with urlopen(Request(real,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*","Referer":url}),timeout=15) as r:raw=r.read(7_000_001)
   if len(raw)>7_000_000:continue
   im=Image.open(io.BytesIO(raw));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<350:continue
   sha=hashlib.sha256(raw).hexdigest()
   if sha in seen_sha:continue
   seen_sha.add(sha)
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   name=f"official-product-image-{len(manifest['actual_source_images'])+1:02d}.{ext}"
   (out/name).write_bytes(raw)
   manifest["actual_source_images"].append({"name":name,"url":real,"section":section,"dimensions":list(im.size),
      "bytes":len(raw),"sha256":sha,"label_145ml_confirmed_in_photo":False,"status":"VISUAL_LABEL_CHECK_PENDING"})
   thumb=ImageOps.contain(im.convert("RGB"),(310,320))
   card=Image.new("RGB",(335,370),"white")
   card.paste(thumb,((335-thumb.width)//2,5))
   ImageDraw.Draw(card).text((12,344),name,fill="#232323");tiles.append(card)
  except Exception as e:pass
 if tiles:
  sheet=Image.new("RGB",(335*min(5,len(tiles)),370*((len(tiles)+4)//5)),"white")
  for i,t in enumerate(tiles):sheet.paste(t,((i%5)*335,(i//5)*370))
  sheet.save(out/"contact.jpg",quality=86,optimize=True)
except Exception as e:manifest["capture_error"]=str(e)[:260]
(out/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"official_145ml_name_verified":manifest["official_name_verified"],
                 "staged_images":len(manifest["actual_source_images"]),"error":manifest.get("capture_error")}))
