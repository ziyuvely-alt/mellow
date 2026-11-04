#!/usr/bin/env python3
"""v2696 inventory: discover *all* media images on exact official MISSHA PDRN serum
page and create an image proof for human visual selection. Never release,
never overwrite earlier QA, and never use recommendations as product photos.
"""
import requests,re,json,hashlib,base64,html
from pathlib import Path
from urllib.parse import urljoin,urlparse
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
OUT=Path("qa-review/v2696-missha-serum-official-gallery-proof")
assert not OUT.exists()
OUT.mkdir(parents=True)
PAGE="https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114237"
AGENT={"User-Agent":"Mozilla/5.0","Accept":"text/html,image/avif,image/png,image/jpeg,*/*"}
resp=requests.get(PAGE,timeout=16,headers=AGENT);resp.raise_for_status()
resp.encoding=resp.apparent_encoding or "utf-8"
soup=BeautifulSoup(resp.text,"html.parser")
name=soup.title.get_text(" ",strip=True) if soup.title else ""
assert "퍼밍 리페어 세럼" in name,(name)
urls=[]
def add(url,role):
 if not url or url.startswith("data:") or url.startswith("blob:"):return
 u=urljoin(PAGE,html.unescape(url).replace("&amp;","&"))
 host=urlparse(u).hostname or ""
 if not(host.endswith("ableshop.kr") or host.endswith("cafe24img.com") or host.endswith("ablecdn.com")):return
 if "/product/" not in u and "BO00114237" not in u and "goods/" not in u and "static.ableshop.kr/ext/images" not in u:return
 urls.append((u,role))
for meta in soup.find_all("meta"):
 if meta.get("property") in ("og:image","twitter:image") or meta.get("name")=="twitter:image":add(meta.get("content"),"metadata")
for i,img in enumerate(soup.find_all("img")):
 for key in ("src","data-src","data-original","data-lazy-src","data-image","data-zoom"):
  add(img.get(key),f"html_img_{i}_{key}_{img.get('alt','')[:20]}")
 for key in ("srcset","data-srcset"):
  for field in (img.get(key) or "").split(","):
   add(field.strip().split(" ")[0],f"html_img_{i}_srcset")
for matched in re.findall(r'(?:"|\\u0022)(https?://[^"\s\\]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"]*)?)',resp.text,re.I):
 add(matched,"embedded_json")
seen=set();candidate=[]
for u,role in urls:
 if u not in seen:seen.add(u);candidate.append((u,role))
result={"version":"v2696","product":"MISSHA PDRN NAD+ Firming Repair Serum 30mL",
        "page":PAGE,"title":name,"candidate_url_count":len(candidate),
        "candidate_urls":[{"url":u,"role":role} for u,role in candidate[:45]],
        "downloaded":[],"retail_approved":False}
for u,role in candidate[:30]:
 try:
  download=requests.get(u,timeout=11,headers=AGENT)
  download.raise_for_status()
  if len(download.content)>8500000:continue
  img=Image.open(BytesIO(download.content));img.load()
  if min(img.size)<320:continue
  src=ImageOps.exif_transpose(img).convert("RGB")
  target=OUT/f"source-{len(result['downloaded'])+1:02d}-REVIEW-ONLY.jpg"
  square=Image.new("RGB",(1080,1080),"white")
  fit=ImageOps.contain(src,(1040,1040),Image.Resampling.LANCZOS)
  square.paste(fit,((1080-fit.width)//2,(1080-fit.height)//2))
  square.save(target,"JPEG",quality=88,optimize=True)
  assert target.stat().st_size<2000000
  result["downloaded"].append({"url":u,"file":target.name,"role":role,
   "source_pixels":list(src.size),"sha256":hashlib.sha256(target.read_bytes()).hexdigest()})
  if len(result["downloaded"])>=12:break
 except (OSError,ValueError,requests.RequestException):continue
if result["downloaded"]:
 images=result["downloaded"]
 f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
 board=Image.new("RGB",(1920,660*((len(images)+3)//4)+60),"#eeefef")
 d=ImageDraw.Draw(board)
 d.text((20,14),"v2696 SAME OFFICIAL SERUM PRODUCT MEDIA / REVIEW ONLY",fill="#222",font=f)
 for idx,row in enumerate(images):
  with Image.open(OUT/row["file"]) as img:
   tile=img.convert("RGB").resize((450,450),Image.Resampling.LANCZOS)
  x=20+(idx%4)*474;y=58+(idx//4)*660
  board.paste(tile,(x,y))
  d.text((x,y+462),f"MEDIA {idx+1:02d} / {row['role'][:27]}",fill="#222",font=f)
 p=OUT/"v2696-all-official-media-proof.jpg";board.save(p,quality=80,optimize=True)
 (OUT/"v2696-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"candidate":len(candidate),"pictures_downloaded":len(result["downloaded"]),
"official_title":name,"sales_approved":False},ensure_ascii=False))
