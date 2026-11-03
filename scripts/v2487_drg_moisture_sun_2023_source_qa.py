#!/usr/bin/env python3
"""Pending-17 Dr.G Brightening Up Moisture Sun 50mL (2023 stock) exact source QA.
Brand item/5387 is 1 x 50mL; excludes 1+1, Brightening Up Sun Plus and other sunscreen.
"""
import re,io,json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
from html.parser import HTMLParser
from PIL import Image,ImageOps,ImageDraw
O=Path("v2480-dr-g-moisture-sun-50ml-source");O.mkdir(exist_ok=True)
PAGES=["https://www.dr-g.co.kr/item/5387"]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("property") in ("og:image","twitter:image") and a.get("content"):self.images.append(a["content"])
  if tag=="img":
   for k in ("src","data-src","data-original","data-lazy-src"):
    if a.get(k):self.images.append(a[k])
ledger={"date":"2026-11-04","family_id":"pending-17","product":"Dr.G Brightening Up Moisture Sun 50mL","edition":"2023 stock reference","source_pages":[],"photos":[],"photo_rights":False,"package_edition_approved":False,"published":False,"existing_public_URLs_changed":0}
seen=set()
for page in PAGES:
 try:
  with urlopen(Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=20) as f:html=f.read(4500000).decode("utf-8","replace")
  if "브라이트닝 업 모이스처 선" not in html:raise ValueError("exact product title missing")
  p=Parser();p.feed(html)
  # Also select direct product hosted images in HTML but never general product recommendation sections as approved evidence.
  sources=p.images[:80]
  ledger["source_pages"].append({"url":page,"status":"MATCHED_TITLE","candidate_image_nodes":len(sources)})
  for u in sources:
   if len(ledger["photos"])>=12:break
   url=urljoin(page,u.strip())
   if url in seen or not url.startswith("https://"):continue
   if not re.search(r"\.(jpg|jpeg|png|webp)(?:\?|$)",url,re.I):continue
   seen.add(url)
   try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=12) as f:raw=f.read(6500001)
    if len(raw)>6500000:continue
    im=Image.open(io.BytesIO(raw));im.load()
    if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<420:continue
    sha=hashlib.sha256(raw).hexdigest()
    if any(x["sha256"]==sha for x in ledger["photos"]):continue
    ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
    name=f"candidate-{len(ledger['photos'])+1:02d}.{ext}";(O/name).write_bytes(raw)
    ledger["photos"].append({"file":name,"sha256":sha,"dimensions":list(im.size),"bytes":len(raw),"url":url,"status":"SOURCE_BYTES_VISUAL_PRODUCT_MATCH_PENDING"})
   except Exception:pass
 except Exception as e:ledger["source_pages"].append({"url":page,"error":str(e)[:200]})
if ledger["photos"]:
 cards=[]
 for x in ledger["photos"]:
  im=ImageOps.contain(Image.open(O/x["file"]).convert("RGB"),(330,325))
  tile=Image.new("RGB",(360,370),"white");tile.paste(im,((360-im.width)//2,8))
  ImageDraw.Draw(tile).text((12,342),x["file"],fill="#292929");cards.append(tile)
 sheet=Image.new("RGB",(360*min(len(cards),4),370*((len(cards)+3)//4)),"white")
 for i,c in enumerate(cards):sheet.paste(c,((i%4)*360,(i//4)*370))
 sheet.save(O/"contact.jpg",quality=87)
(O/"source-manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"candidate_photos_saved":len(ledger["photos"]),"pages":ledger["source_pages"]},ensure_ascii=False))
