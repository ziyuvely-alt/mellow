#!/usr/bin/env python3
"""v2698 source-image evidence acquisition for two previously under-photographed
families. Visual confirmation is mandatory before replacing any QA image.
OBGE images must belong to official product 1206. GOODAL evidence is a
standalone 30mL eye-cream, not 1+1 gift pack; do not treat a retailer page as
photo redistribution permission. Never touch approved 11 families/55 URLs.
"""
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
from bs4 import BeautifulSoup
import requests,json,hashlib,base64,re
OUT=Path("qa-review/v2698-OBGE-GOODAL-two-source-photo-proof")
assert not OUT.exists()
OUT.mkdir(parents=True)
HEAD={"User-Agent":"Mozilla/5.0 (compatible; QualityAssurance/1.0)","Accept":"text/html,image/avif,image/webp,image/jpeg,image/png,*/*"}
PRODUCTS=[
 dict(family="pending-09",brand="OBGE",page="https://obge.co.kr/product/오일-컨트롤-피니셔/1206",
      expected="오일 컨트롤 피니셔",candidate_domains=["obge.co.kr","cafe24img.com","cafe24.com"],
      code_hint="1206",unit="5g",photo_policy="official single finisher product, not bundle"),
 dict(family="pending-21",brand="GOODAL",page="https://www.kurly.com/goods/1001465618",
      expected="아이크림",candidate_domains=["kurly.com","kurlycdn.com","kurlystatic.com","kurlyweb.com"],
      code_hint="1001465618",unit="30ml",photo_policy="single NEW 30mL eye cream, NOT 2EA/eye patch gift set")
]
def check_host(u,domains):
 host=(urlparse(u).hostname or "").lower()
 return any(host==d or host.endswith("."+d) for d in domains)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for item in PRODUCTS:
 record={"family":item["family"],"page":item["page"],"title":None,
 "status":"HOLD_NO_SOURCE_PHOTO_VERIFIED","source_candidate_urls":[],
 "pictures":[],"retail_approved":False,"photo_policy":item["photo_policy"]}
 try:
  resp=requests.get(item["page"],headers=HEAD,timeout=18);resp.raise_for_status()
  soup=BeautifulSoup(resp.text,"html.parser")
  title=soup.title.get_text(" ",strip=True) if soup.title else ""
  text=soup.get_text(" ",strip=True)
  record["title"]=title
  if item["expected"] not in (title+" "+text[:2200]):
   raise ValueError("Product title does not contain expected exact source name")
  if item["brand"]=="GOODAL":
   if not ("30ml" in (title+" "+text[:1600]).lower() or "30 ml" in (title+" "+text[:1600]).lower()):
    raise ValueError("Single Goodal 30mL size not confirmed")
   if any(x in title for x in ("2EA","1+1","패치","세트")):
    raise ValueError("Bundle or gift listing excluded")
  urls=[]
  for m in soup.select('meta[property="og:image"],meta[name="twitter:image"]'):
   if m.get("content"):urls.append((urljoin(item["page"],m["content"]),"meta"))
  for im in soup.find_all("img"):
   role=" ".join([im.get("alt") or ""," ".join(im.get("class") or []),im.get("id") or ""]).lower()
   srcs=[im.get(k) for k in ("src","data-src","data-original","data-zoom")]
   source=(im.get("src") or "")
   product_url=item["code_hint"] in source or "/web/product/big/" in source or "/web/product/extra/" in source
   role_good=any(k in role for k in ["main","product","goods","keyimg","detail","item","thumb","오일 컨트롤","아이크림"])
   if not product_url and not role_good:continue
   for raw in srcs:
    if raw and not raw.startswith(("data:","blob:")):urls.append((urljoin(item["page"],raw),"gallery"))
  unique=[];seen=set()
  for u,role in urls:
   if u.startswith("http") and check_host(u,item["candidate_domains"]) and u not in seen:
    seen.add(u);unique.append((u,role))
  record["source_candidate_urls"]=[x[0] for x in unique[:22]]
  for u,role in unique[:20]:
   try:
    r=requests.get(u,headers=HEAD,timeout=12)
    r.raise_for_status()
    if len(r.content)>8000000:continue
    decoded=Image.open(BytesIO(r.content));decoded.load()
    if min(decoded.size)<450:continue
    img=ImageOps.exif_transpose(decoded).convert("RGB")
    dest_dir=OUT/item["family"];dest_dir.mkdir(exist_ok=True)
    path=dest_dir/f"{len(record['pictures'])+1:02d}-source-candidate-NOT-FOR-RETAIL.jpg"
    preview=Image.new("RGB",(1080,1080),"white")
    contained=ImageOps.contain(img,(1040,1040),Image.Resampling.LANCZOS)
    preview.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
    preview.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
    assert path.stat().st_size<2000000
    record["pictures"].append({"file":path.name,"image_url":u,"source_kind":role,
    "source_dimensions":list(decoded.size),"sha256":sha(path)})
    if len(record["pictures"])>=7:break
   except (requests.RequestException,OSError,ValueError):
    continue
  record["status"]="CANDIDATES_STAGED_MUST_VISUALLY_VERIFY_PRODUCT" if record["pictures"] else "HOLD_NO_DECODABLE_SAME_PRODUCT_PHOTO"
 except Exception as e:
  record["status"]="HOLD_PAGE_UNAVAILABLE_OR_PRODUCT_IDENTITY_NOT_PROVEN"
  record["error_type"]=type(e).__name__
  record["error"]=str(e)[:260]
 results.append(record)
total=sum(len(x["pictures"]) for x in results)
if total:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",25)
 width=1850;rows=sum((len(z["pictures"])+3)//4 for z in results)
 board=Image.new("RGB",(width,60+rows*430),"#eef0ee")
 d=ImageDraw.Draw(board)
 d.text((15,15),"v2698 2 STOCK PRODUCT SOURCE PROOFS / NO SALES PUBLICATION",font=font,fill="#252525")
 row_index=0
 for product in results:
  for i,p in enumerate(product["pictures"]):
   with Image.open(OUT/product["family"]/p["file"]) as img:
    thumb=img.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
   row=row_index+i//4;col=i%4
   x=15+col*457;y=60+row*430
   board.paste(thumb,(x,y))
   d.text((x,y+344),product["family"]+" / "+str(i+1),font=font,fill="#252525")
  row_index+=(len(product["pictures"])+3)//4
 dest=OUT/"v2698-proof-contact.jpg"
 board.save(dest,quality=82,optimize=True)
 (OUT/"v2698-proof-contact.b64.txt").write_text(base64.b64encode(dest.read_bytes()).decode())
manifest={"version":"v2698","baseline":"v2697","families":results,
 "source_candidate_physical_JPG_count":total,
 "changed_existing_QA_JPGs":0,"new_retail_approved":0,
 "approved_11_families_unchanged":True,
 "published_55_verified_URLs_unchanged":True,
 "source_license_and_edition_verified":False,
 "no_final_spreadsheet_shared":True}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"source_candidate_JPGs":total,"results":[{"family":x["family"],"status":x["status"],"images":len(x["pictures"])} for x in results]},ensure_ascii=False))
