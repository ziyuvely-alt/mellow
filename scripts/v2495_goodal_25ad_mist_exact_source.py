#!/usr/bin/env python3
"""Goodal 25AD serum mist 100mL: recover exact-product proof images only.
Do not reuse Goodal E TXA mist or 2-pack bundle; no publication until approval.
"""
import io,re,json,hashlib
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from PIL import Image,ImageOps,ImageDraw
out=Path("v2495-goodal-mist-25ad-exact");out.mkdir(exist_ok=True)
page="https://m.shilladfs.com/estore/kr/ko/p/5777042"
class P(HTMLParser):
 def __init__(self):super().__init__();self.img=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("property") in ("og:image","twitter:image") and a.get("content"):self.img.append(a["content"])
  if tag=="img":
   for key in ("src","data-src","data-original","data-lazy-src"):
    if a.get(key):self.img.append(a[key])
data={"date":"2026-11-04","family_id":"pending-20","product":"Goodal Green Tangerine Vita C Serum Mist 100ml (25AD)","retailer_page":page,"seller_stock_edition_2025AD_verified_from_listing":True,"product_page_sku":"669210000427","source_images":[],"page_status":"UNTRIED","commercial_photo_rights_verified":False,"new_public_urls":0,"excel_shared":False}
try:
 with urlopen(Request(page,headers={"User-Agent":"Mozilla/5.0","Accept":"text/html,application/xhtml+xml"}),timeout=24) as r:html=r.read(6000000).decode("utf8","replace")
 if "청귤비타C세럼미스트" not in html and "청귤 비타C 세럼 미스트" not in html:raise ValueError("product title missing in page")
 p=P();p.feed(html);data["page_status"]="EXACT_25AD_PAGE_MATCHED"
 seen=set();thumbs=[]
 for url in p.img:
  if len(data["source_images"])>=12:break
  url=urljoin(page,url)
  if url in seen or not url.startswith("https://"):continue
  seen.add(url)
  if not re.search(r"\.(jpg|jpeg|png|webp)(\?|$)",url,re.I):continue
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=12) as f:raw=f.read(7000001)
   if len(raw)>7000000:continue
   im=Image.open(io.BytesIO(raw));im.load()
   if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<440:continue
   sha=hashlib.sha256(raw).hexdigest()
   if any(x["sha256"]==sha for x in data["source_images"]):continue
   ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
   name="candidate-%02d.%s"%(len(data["source_images"])+1,ext);(out/name).write_bytes(raw)
   data["source_images"].append({"file":name,"source_url":url,"bytes":len(raw),"sha256":sha,"dimensions":im.size,"status":"EXACT_PAGE_IMAGE_CANDIDATE_VISUAL_QA_PENDING"})
   t=ImageOps.contain(im.convert("RGB"),(320,320));tile=Image.new("RGB",(340,360),"white")
   tile.paste(t,((340-t.width)//2,6));ImageDraw.Draw(tile).text((8,332),name,fill="#222")
   thumbs.append(tile)
  except Exception:pass
 if thumbs:
  sheet=Image.new("RGB",(340*min(4,len(thumbs)),360*((len(thumbs)+3)//4)),"white")
  for i,t in enumerate(thumbs):sheet.paste(t,((i%4)*340,(i//4)*360))
  sheet.save(out/"contact.jpg",quality=87)
except Exception as e:data["page_status"]="BLOCKED_OR_NOT_EXACT";data["error"]=str(e)[:250]
(out/"manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"page_status":data["page_status"],"downloaded":len(data["source_images"])}))
