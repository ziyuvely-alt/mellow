#!/usr/bin/env python3
"""Stage exact OBgE Perfect Homme Cushion 15g three-shade original photos.
Reconcile old 13g conflict from earlier checkpoint, but do not assert identical packaging
until seller-owned stock SKU, label, and official photo match. Not customer approved.
"""
import io,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageOps
O=Path("v2510-obge-perfect-homme-15g-originals");O.mkdir(exist_ok=True)
products=[
 {"label":"Soonsu exact 15g","uri":"https://soonsubeauty.com/products/obge-perfect-homme-cushion-15g.js"},
 {"label":"JOSEPH Beauty exact 15g","uri":"https://josephbeauty.com/products/obge-perfect-homme-cushion-spf50-pa-15g-3colors.js"}
]
report={"date":"2026-11-04","family_id":"pending-10","product":"OBgE Perfect Homme Cushion 15g","historical_13g_qa_hold_not_overridden_without_physical_stock":True,
"confirmed_15g_external_evidence":["https://cn.hd-dfs.com/shop/gd/dtl/goos.do?onlnGoosCd=56716260000401","https://josephbeauty.com/products/obge-perfect-homme-cushion-spf50-pa-15g-3colors"],
"shopify":[],"photos":[],"photograph_commercial_rights_verified":False,"physical_stock_version_verified":False,"new_urls_published":0,"workbook_unchanged":True}
seen=set();cards=[]
for p in products:
 entry={"shop":p["label"],"url":p["uri"],"state":"FETCH_FAILED"}
 try:
  with urlopen(Request(p["uri"],headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}),timeout=20) as resp:data=json.loads(resp.read(3_000_000))
  entry["product_title"]=data.get("title","")
  if "Homme Cushion" not in entry["product_title"]:raise ValueError("not exact Homme Cushion item")
  entry["variant_names"]=[x.get("title") for x in data.get("variants",[])]
  imgs=data.get("images",[])
  entry["image_count"]=len(imgs)
  for url in imgs[:16]:
   if len(report["photos"])>=12:break
   if isinstance(url,dict):url=url.get("src","")
   if url.startswith("//"):url="https:"+url
   if not url.startswith("https://"):continue
   try:
    with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=15) as res:b=res.read(7_000_001)
    if len(b)>7_000_000:continue
    im=Image.open(io.BytesIO(b));im.load()
    if im.format not in ("JPEG","PNG","WEBP") or min(im.size)<500:continue
    h=hashlib.sha256(b).hexdigest()
    if h in seen:continue
    seen.add(h)
    ext={"JPEG":"jpg","PNG":"png","WEBP":"webp"}[im.format]
    fn=f"15g-source-{len(report['photos'])+1:02d}.{ext}";(O/fn).write_bytes(b)
    report["photos"].append({"filename":fn,"origin":p["label"],"url":url,"sha256":h,"dimensions":list(im.size),"bytes":len(b),"final_product_match":"VISUAL_QA_PENDING"})
    thumb=ImageOps.contain(im.convert("RGB"),(290,300))
    c=Image.new("RGB",(320,350),"white");c.paste(thumb,((320-thumb.width)//2,7))
    ImageDraw.Draw(c).text((9,315),fn,fill="#222");cards.append(c)
   except Exception:pass
  entry["state"]="PRODUCT_JSON_PARSED"
 except Exception as e:entry["error"]=str(e)[:150]
 report["shopify"].append(entry)
if cards:
 contact=Image.new("RGB",(320*min(4,len(cards)),350*((len(cards)+3)//4)),"white")
 for i,c in enumerate(cards):contact.paste(c,((i%4)*320,(i//4)*350))
 contact.save(O/"contact.jpg",quality=85)
report["actual_source_photo_count"]=len(report["photos"])
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"photos":len(report["photos"]),"sources":[x["state"] for x in report["shopify"]]}))
