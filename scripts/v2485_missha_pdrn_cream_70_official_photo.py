#!/usr/bin/env python3
"""Acquire authentic MISSHA PDRN NAD+ 30ml serum and 70ml cream photo sources.
Do not assert rights, exact seller stock edition, or permission to publish source images.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin
import hashlib,json,io,re
O=Path("v2485-missha-pdrn-cream-official-evidence");O.mkdir(exist_ok=True)
targets=[
 {"family":"pending-14","name":"MISSHA PDRN NAD FIRMING REPAIR CREAM 70ml","terms":["퍼밍 리페어 크림","firming repair cream"],"pages":["https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114238"]}
]
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="meta" and d.get("property") in ("og:image","twitter:image"):self.urls.append(d.get("content",""))
  if tag=="img":
   for k in ("src","data-src","data-original"):
    if d.get(k):self.urls.append(d[k])
summary={"date":"2026-11-04","license_verified":False,"seller_stock_version_verified":False,"published":False,"families":[]}
for target in targets:
 dest=O/target["family"];dest.mkdir(exist_ok=True)
 found=[];pages=[];visited=set();tiles=[]
 for page in target["pages"]:
  try:
   with urlopen(Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=20) as r:html=r.read(5000000).decode("utf-8","replace")
   if not any(t in html.lower() for t in target["terms"]):raise ValueError("exact product name absent")
   p=Parse();p.feed(html);pages.append({"url":page,"matched":True,"image_candidates":len(p.urls)})
   for u in p.urls:
    if len(found)>=8:break
    u=urljoin(page,u)
    if not u.startswith("https://") or not re.search(r"\.(jpg|jpeg|png|webp)(\?|$)",u,re.I) or u in visited:continue
    visited.add(u)
    try:
     with urlopen(Request(u,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=12) as r:raw=r.read(8000001)
     if len(raw)>8000000:continue
     im=Image.open(io.BytesIO(raw));im.load()
     if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<400:continue
     sha=hashlib.sha256(raw).hexdigest()
     if any(x["sha256"]==sha for x in found):continue
     ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format];name=f"original-{len(found)+1:02d}.{ext}"
     (dest/name).write_bytes(raw)
     found.append({"file":name,"source_page":page,"raw_url":u,"sha256":sha,"size":list(im.size),"bytes":len(raw),"product_visual_edition_match":"PENDING","commercial_rights":"PENDING"})
     tile=Image.new("RGB",(380,420),"white");thumb=ImageOps.contain(im.convert("RGB"),(350,365));tile.paste(thumb,((380-thumb.width)//2,10));ImageDraw.Draw(tile).text((8,385),name,fill="#111");tiles.append(tile)
    except Exception:pass
  except Exception as e:pages.append({"url":page,"matched":False,"error":str(e)[:200]})
 if tiles:
  sheet=Image.new("RGB",(380*min(4,len(tiles)),420*((len(tiles)+3)//4)),"white")
  for i,im in enumerate(tiles):sheet.paste(im,(380*(i%4),420*(i//4)))
  sheet.save(dest/"contact.jpg",quality=90)
 record={"family":target["family"],"name":target["name"],"pages":pages,"photos":found,"count":len(found),"no_substitution_of_other_pdrn_products":True}
 (dest/"manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
 summary["families"].append({"family":target["family"],"downloaded":len(found),"pages":pages})
(O/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(summary["families"],ensure_ascii=False))
