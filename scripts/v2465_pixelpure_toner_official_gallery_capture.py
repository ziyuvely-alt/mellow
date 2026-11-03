#!/usr/bin/env python3
"""Discover actual photo bytes from official PIXEL PURE 200ml toner pages; evidence only, no fake artwork."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin,urlparse
from PIL import Image,ImageOps,ImageDraw
import hashlib,io,json,re
OUT=Path("v2465-pixelpure-toner-official-gallery");OUT.mkdir(exist_ok=True)
pages=["https://www.pixelpure.com/product/detail.html?product_no=24","https://eng.pixelpure.com/product/pixelpure-soothing-ampule-toner-200ml/24/"]
class P(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("property") in ("og:image","twitter:image"):self.urls.append(a.get("content",""))
  if tag in ("img","source"):
   for k in ("src","data-src","data-original","srcset"):
    if k in a:
     val=a[k].split(",")[0].strip().split(" ")[0]
     if val:self.urls.append(val)
ledger={"family":"pending-27","date":"2026-11-04","exact_product":"PIXEL PURE Soothing Ampoule Toner 200ml","source_kind":"OFFICIAL_PRODUCT_PAGE_GALLERY_CANDIDATE","status":"QA_ONLY_NOT_APPROVED","pages":[],"downloaded":[],"notes":[]}
seen=set()
for page in pages:
 p=P()
 try:
  with urlopen(Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=25) as r:html=r.read(5_000_000).decode("utf-8","replace")
  if not any(x in html.lower() for x in ("수딩 앰플 토너","soothing ampule toner","soothing ampoule toner")):raise ValueError("product name not found in page HTML")
  p.feed(html);ledger["pages"].append({"url":page,"candidate_urls":len(p.urls),"status":"MATCHED_PRODUCT_HTML"})
 except Exception as e:
  ledger["pages"].append({"url":page,"error":str(e)[:180]});continue
 for u in p.urls:
  if len(ledger["downloaded"])>=10:break
  url=urljoin(page,u)
  if not url.startswith("https://") or not re.search(r"\.(jpg|jpeg|png|webp)(?:[?]|$)",url,re.I):continue
  if url in seen:continue
  seen.add(url)
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=15) as r:raw=r.read(8_000_001)
   if len(raw)>8_000_000:continue
   im=Image.open(io.BytesIO(raw));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<450:continue
   sha=hashlib.sha256(raw).hexdigest()
   if any(x["sha256"]==sha for x in ledger["downloaded"]):continue
   suffix={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   name="original-%02d.%s"%(len(ledger["downloaded"])+1,suffix)
   (OUT/name).write_bytes(raw)
   ledger["downloaded"].append({"filename":name,"url":url,"dimensions":im.size,"sha256":sha,"bytes":len(raw),"photo_identity":"PENDING_VISUAL_REVIEW","reuse_rights":"NOT_CHECKED"})
  except Exception as e:continue
(OUT/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
if ledger["downloaded"]:
 thumbs=[]
 for x in ledger["downloaded"]:
  im=Image.open(OUT/x["filename"]).convert("RGB");t=ImageOps.contain(im,(350,355))
  c=Image.new("RGB",(380,405),"white");c.paste(t,((380-t.width)//2,8));ImageDraw.Draw(c).text((10,370),x["filename"],fill="black");thumbs.append(c)
 sheet=Image.new("RGB",(380*min(5,len(thumbs)),405*((len(thumbs)+4)//5)),"white")
 for i,t in enumerate(thumbs):sheet.paste(t,(380*(i%5),405*(i//5)))
 sheet.save(OUT/"contact.jpg",quality=86)
print(json.dumps({"candidate_original_jpg_png":len(ledger["downloaded"]),"pages":ledger["pages"]},ensure_ascii=False))
