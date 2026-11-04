#!/usr/bin/env python3
"""v271 mini products: create 3 non-destructive source-backed English packshot QA JPGs and archive originals."""
import hashlib,io,json,concurrent.futures
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageDraw,ImageFont
OUT=Path("/tmp/bbia-v271");OUT.mkdir(parents=True,exist_ok=True)
IDS=["1000000187","1000000120","1000000208"]
TITLES={"1000000187":"L'EAU TINT MINI","1000000120":"EAU GLOW CUSHION MINI","1000000208":"OVER GLAZE MINI"}
M={str(z["product_id"]):z for z in json.loads(Path("evidence/bbia-image-review-input.json").read_text("utf8"))["families"]}
def source(sku):
 url=M[sku]["official_photo_url"]
 item={"goodsNo":sku,"source_url":url}
 try:
  with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=22) as r:b=r.read(8_000_000)
  im=Image.open(io.BytesIO(b));im.load()
  item.update(source_sha256=hashlib.sha256(b).hexdigest(),source_dimensions=[im.width,im.height],source_bytes=len(b),status="DOWNLOADED")
  return item,im.convert("RGB"),b
 except Exception as ex:
  item.update(status="SOURCE_HOLD",error=f"{type(ex).__name__}: {str(ex)[:150]}")
  return item,None,None
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 acquired=list(pool.map(source,IDS))
board=Image.new("RGB",(1800,730),"#f5f4f3")
draw=ImageDraw.Draw(board)
draw.text((18,15),"BBIA v271 | 3 MINI-SPECIFIC PACKSHOTS | NEW QA ONLY",fill="#242424")
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
for col,(meta,photo,blob) in enumerate(acquired):
 if photo is None:continue
 sku=meta["goodsNo"]
 (OUT/(sku+"_SOURCE_ORIGINAL.jpg")).write_bytes(blob)
 frame=Image.new("RGB",(1080,1080),"#fbf9f7")
 d=ImageDraw.Draw(frame)
 d.text((78,63),"BBIA",font=ImageFont.truetype(bold,54),fill="#252224")
 d.text((78,152),TITLES[sku],font=ImageFont.truetype(bold,30),fill="#43393a")
 d.line((78,213,1002,213),fill="#d9c9c7",width=2)
 # Native 500px hero kept at native source size to avoid fabricated upscale/sharpness.
 x=(1080-photo.width)//2;y=270+(650-photo.height)//2
 frame.paste(photo,(x,y))
 d.text((78,985),"MINI FORMAT  |  GENUINE PRODUCT PHOTO",font=ImageFont.truetype(regular,22),fill="#5c5153")
 name=f"BBIA_{sku}_MINI_HERO_v271_QA_PENDING.jpg"
 path=OUT/name
 frame.save(path,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(path) as check:check.verify()
 meta.update(status="NEW_QA_JPG_CREATED",output=name,dimensions=[1080,1080],bytes=path.stat().st_size,
             output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_upscaled=False,
             sales_approved=False,quality_hold="Native packshot 500px, not a transparent cutout and may look small.")
 preview=frame.copy();preview.thumbnail((575,575),Image.Resampling.LANCZOS)
 board.paste(preview,(col*600+12,70))
 draw.text((col*600+12,655),sku,fill="#252525")
board.save(OUT/"BBIA_v271_THREE_MINI_QA_CONTACT.jpg",quality=90)
report={"checkpoint":"v271","parent":"v270","created":sum(x["status"]=="NEW_QA_JPG_CREATED" for x,_,_ in acquired),
        "sources":[x for x,_,_ in acquired],"approved_sales":0,"public_changed":False,
        "verified_55_urls_changed":False,"new_excel":False}
(OUT/"BBIA_v271_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print("V271_CREATED",json.dumps({"jpg":report["created"],"ids":IDS}))
