from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from io import BytesIO
from urllib.parse import urlparse
import requests,json,re,hashlib,base64
OUT=Path("qa-review/v2820-clio-mini-5g-Lila-21N-variant-photo-evidence")
assert not OUT.exists()
OUT.mkdir(parents=True)
URL="https://lilabeauty.com.au/products/mini-kill-cover-founwear-cushion-the-original-5g.js"
R=requests.get(URL,headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"},timeout=22)
R.raise_for_status()
d=R.json()
title=str(d.get("title",""))
vendor=str(d.get("vendor",""))
assert "mini" in title.lower() and "original" in title.lower() and "5g" in title.lower()
assert "clio" in vendor.lower() or "clio" in URL.lower()
variants=d.get("variants",[])
matches=[v for v in variants if re.search(r"(?<!\w)21\s*N(?!\w)|linen",str(v.get("title","")),re.I)]
imgs=d.get("images",[])
def getimage(u):
 if not u:return None
 if isinstance(u,dict):return u.get("src")
 if isinstance(u,str):return u
 return None
mapped=[]
for v in matches:
 vid=str(v.get("id"))
 img_urls=[]
 feature=getimage(v.get("featured_image"))
 if feature:img_urls.append(feature)
 for im in imgs:
  if isinstance(im,dict) and vid in [str(i) for i in im.get("variant_ids",[])]:
   src=getimage(im)
   if src:img_urls.append(src)
 mapped.append({"variant_id":vid,"label":str(v.get("title")),"photo_urls":list(dict.fromkeys(img_urls))})
stored=[]
for item in mapped:
 for url in item["photo_urls"]:
  if len(stored)>=5:break
  try:
   if url.startswith("//"):url="https:"+url
   resp=requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=18)
   resp.raise_for_status()
   assert 9000<len(resp.content)<8_000_000
   image=Image.open(BytesIO(resp.content));image.load()
   assert min(image.size)>=350
   rgb=ImageOps.exif_transpose(image).convert("RGB")
   dest=OUT/f"{len(stored)+1:02d}-21N-variant-linked-Lila-5g-QA.jpg"
   square=Image.new("RGB",(1080,1080),"white")
   thumb=ImageOps.contain(rgb,(1050,1050),Image.Resampling.LANCZOS)
   square.paste(thumb,((1080-thumb.width)//2,(1080-thumb.height)//2))
   square.save(dest,"JPEG",quality=92,optimize=True,subsampling=0)
   assert dest.stat().st_size<2000000
   stored.append({"file":dest.name,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
    "variant_id":item["variant_id"],"label":item["label"],"original_url":url,
    "native_dimensions":list(image.size),
    "still_needs_visual_product_vs_swatch_check":True})
  except Exception:continue
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
can=Image.new("RGB",(1750,550),"#f0f0ee")
dr=ImageDraw.Draw(can)
dr.text((15,15),"v2820 LILA BEAUTY CLIO THE ORIGINAL MINI 5g | EXACT 21N VARIANT ONLY",font=font,fill="#292929")
for i,a in enumerate(stored[:4]):
 with Image.open(OUT/a["file"]) as im:
  prev=im.convert("RGB").resize((400,400),Image.Resampling.LANCZOS)
 can.paste(prev,(12+i*435,62))
 dr.text((12+i*435,476),"21N Linen mapped variant",font=font,fill="#454545")
if not stored:dr.text((18,230),"No 21N variant-associated photograph; no substitution permitted.",font=font,fill="#8d4949")
p=OUT/"v2820-Lila-21N-photos-review.jpg"
can.save(p,"JPEG",quality=84,optimize=True)
(OUT/"v2820-proof.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode("ascii"))
manifest={"version":"v2820","baseline":"v2819","family":"pending-05",
"product":"CLIO The Original Mini 5g","source":URL,"merchant":"Lila Beauty",
"vendor":vendor,"product_title":title,
"21N_variants":mapped,"images_explicitly_linked_to_21N_saved":len(stored),
"new_actual_21N_photo_candidates":stored,
"prior_v2819_DODOSKIN_21N_swatch_preserved":True,
"prior_v2818_23N_JPGs_preserved":True,
"new_photo_for_21N_product_hero_proven":False,
"photo_license_verified":False,"actual_owned_stock_edition_verified":False,
"new_retail_approval":False,"approved_11_families_untouched":True,
"approved_55_URLs_untouched":True,"no_final_XLSX":True}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2820","mapped_variants":len(mapped),"21N_linked_photos":len(stored),"approved":0}))
