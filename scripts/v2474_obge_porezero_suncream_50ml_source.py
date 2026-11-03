#!/usr/bin/env python3
"""Acquire exact official image sources for Pixelpure Aqua Soothing Cream 50ml (pending-23).
Separate original photo candidates from nonphoto banners and never publish before rights QA.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from PIL import Image,ImageOps,ImageDraw
import hashlib,io,json,re
OUT=Path("v2474-obge-porezero-suncream-50ml-gallery");OUT.mkdir(exist_ok=True)
PAGES=["https://obge.co.kr/product/포어-제로-오일-컨트롤-선크림/888/","https://www.obge.co.kr/product/detail.html?product_no=888"]
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("property") in ("og:image","twitter:image"):self.urls.append(a.get("content",""))
  if tag in ("img","source"):
   for key in ("src","data-src","data-original"):
    if a.get(key):self.urls.append(a[key])
report={"date":"2026-11-04","family":"pending-23","product":"OBgE Pore Zero Oil Control Sun Cream 50ml","brand_edition_verified":False,"commercial_photo_rights_verified":False,"published":False,"source_pages":[],"images":[]}
seen=set()
for page in PAGES:
 try:
  with urlopen(Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=25) as r:html=r.read(5000000).decode("utf-8","replace")
  if not any(x in html.lower() for x in ["포어 제로 오일 컨트롤 선크림","pore zero oil control sun cream"]):raise ValueError("identity mismatch")
  p=Parser();p.feed(html)
  report["source_pages"].append({"url":page,"status":"IDENTITY_TEXT_CONFIRMED","potential_urls":len(p.urls)})
  for u in p.urls:
   if len(report["images"])>=12:break
   url=urljoin(page,u)
   if not url.startswith("https://") or not re.search(r"\.(jpg|jpeg|webp|png)(\?|$)",url,re.I):continue
   if url in seen:continue
   seen.add(url)
   try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=15) as r:raw=r.read(8500001)
    if len(raw)>8500000:continue
    im=Image.open(io.BytesIO(raw));im.load()
    if im.format not in ("JPEG","WEBP","PNG") or min(im.size)<450:continue
    h=hashlib.sha256(raw).hexdigest()
    if any(x["sha256"]==h for x in report["images"]):continue
    ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[im.format]
    name=f"original-{len(report['images'])+1:02d}.{ext}"
    (OUT/name).write_bytes(raw)
    report["images"].append({"filename":name,"url":url,"sha256":h,"dimensions":im.size,"bytes":len(raw),"visual_product_match":"PENDING","reuse_rights":"PENDING"})
   except Exception:pass
 except Exception as e:report["source_pages"].append({"url":page,"status":"ERROR","detail":str(e)[:180]})
if report["images"]:
 thumbs=[]
 for item in report["images"]:
  im=Image.open(OUT/item["filename"]).convert("RGB")
  im=ImageOps.contain(im,(340,330))
  card=Image.new("RGB",(360,372),"white");card.paste(im,((360-im.width)//2,8))
  ImageDraw.Draw(card).text((10,343),item["filename"],fill="#333333");thumbs.append(card)
 sheet=Image.new("RGB",(360*min(6,len(thumbs)),372*((len(thumbs)+5)//6)),"white")
 for i,t in enumerate(thumbs):sheet.paste(t,(360*(i%6),372*(i//6)))
 sheet.save(OUT/"contact.jpg",quality=88)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"valid_source_bytes":len(report["images"]),"pages":report["source_pages"]},ensure_ascii=False))
