#!/usr/bin/env python3
"""MISSHA M Perfect Cover BB Cream product photo source acquisition.
The mid-2026 PRO renewal must NOT be conflated with older stock product.
No new published JPGs or overwritten historical source assets.
"""
import json,hashlib,io,re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urljoin
from html.parser import HTMLParser
from PIL import Image,ImageDraw,ImageOps
OUT=Path("v2498-missha-mperfect-source-qa");OUT.mkdir(exist_ok=True)
pages=[
 {"url":"https://missha.com/en/m/makeup/product_detail?prdmCd=1086","edition":"BRAND_CURRENT_2026_PRO_OR_RENEWED_UNVERIFIED"},
 {"url":"https://www.missha.co.kr/product/detail.html?product_no=2129","edition":"KOREAN_BRAND_UNKNOWN_REQUIRE_TITLE_MATCH"}
]
class P(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="meta" and d.get("property") in ("og:image","twitter:image") and d.get("content"):self.links.append(d["content"])
  if tag in ("img","source"):
   for k in ("src","data-src","data-original"):
    if d.get(k):self.links.append(d[k])
ledger={"date":"2026-11-04","family":"pending-03","target":"MISSHA M Perfect Cover BB Cream old Korean stock (NOT automatically 2026 PRO)","brand_2026_renewal_announcement":"https://m.missha.co.kr/bbs/board.php?bo_table=news&wr_id=390","pages":[],"source_images":[],"photo_edition_stock_match_verified":False,"rights_verified":False,"images_published":0,"workbook_unchanged":True}
sha_set=set();thumbs=[]
for page in pages:
 record={"url":page["url"],"edition_assumption":page["edition"],"status":"BLOCKED"}
 try:
  with urlopen(Request(page["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"}),timeout=23) as r:html=r.read(5_000_000).decode("utf-8","replace")
  if not (("Perfect Cover BB" in html) or ("퍼펙트 커버 비비" in html) or ("퍼펙트 커버 BB" in html)):raise ValueError("exact product title absent")
  p=P();p.feed(html)
  record.update(status="EXACT_NAME_HTML_FOUND",img_candidates=len(p.links))
  for src in p.links[:120]:
   if len(ledger["source_images"])>=12:break
   url=urljoin(page["url"],src)
   if not url.startswith("https://") or not re.search(r"\.(jpg|jpeg|webp|png)(?:\?|$)",url,re.I):continue
   try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=12) as r:raw=r.read(7000001)
    if len(raw)>7000000:continue
    im=Image.open(io.BytesIO(raw));im.load()
    if im.format not in ("JPEG","WEBP","PNG") or min(im.size)<420:continue
    sha=hashlib.sha256(raw).hexdigest()
    if sha in sha_set:continue
    sha_set.add(sha)
    ext={"JPEG":"jpg","WEBP":"webp","PNG":"png"}[im.format]
    fn=f"brand-source-{len(ledger['source_images'])+1:02d}.{ext}";(OUT/fn).write_bytes(raw)
    ledger["source_images"].append({"filename":fn,"sha256":sha,"bytes":len(raw),"width":im.width,"height":im.height,"url":url,"edition":page["edition"],"product_identity_VISUAL_QA":"PENDING"})
    tile=Image.new("RGB",(340,370),"white");sample=ImageOps.contain(im.convert("RGB"),(320,325))
    tile.paste(sample,((340-sample.width)//2,6))
    ImageDraw.Draw(tile).text((10,340),fn,fill="#202020");thumbs.append(tile)
   except Exception:pass
 except Exception as e:record["error"]=str(e)[:170]
 ledger["pages"].append(record)
if thumbs:
 sheet=Image.new("RGB",(340*min(4,len(thumbs)),370*((len(thumbs)+3)//4)),"white")
 for i,t in enumerate(thumbs):sheet.paste(t,((i%4)*340,(i//4)*370))
 sheet.save(OUT/"contact.jpg",quality=89)
(OUT/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"candidate_source_images":len(ledger["source_images"]),"pages":ledger["pages"]},ensure_ascii=False))
