#!/usr/bin/env python3
"""v2822b investigate missing #21C Lingerie ORIGINAL MINI 5g variant-specific
photos without substituting #21N/#23N. Only vendor-side explicitly mapped
variant photos are saved. Korean ClubClio 7108 currently advertises 21N/23N,
so exact owned-stock availability is a separate HOLD gate.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin
from PIL import Image,ImageOps,ImageDraw,ImageFont
import requests,json,re,base64,hashlib
OUT=Path("qa-review/v2822b-clio-original-mini-5g-21C-exact-variant-gallery-proof")
assert not OUT.exists();OUT.mkdir(parents=True)
HEADER={"User-Agent":"Mozilla/5.0","Accept":"application/json,text/html,image/avif,image/jpeg,image/png,*/*"}
SOURCES=[
 ("DODOSKIN","https://www.dodoskin.com/products/clio-kill-cover-founwear-cushion-the-original-mini-5g-3-colors.js"),
 ("Lila Beauty","https://lilabeauty.com.au/products/mini-kill-cover-founwear-cushion-the-original-5g.js")
]
font_regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(font_bold if b else font_regular,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"version":"v2822b","baseline":"v2821",
 "family":"pending-05",
 "product":"CLIO Kill Cover Founwear Cushion The Original Mini 5g",
 "target_variant":"21C Lingerie",
 "Korean_official_site_7108_advertises":["21N","23N"],
 "Korean_firstparty_21C_available_confirmed":False,
 "merchant_exact_variant_source_probes":[],
 "source_image_21C_candidate_files":[],
 "never_use_other_shade_images":True,"21N_23N_prior_files_unchanged":True,
 "sale_approval":False,"original_MK_logo_verified":False,"photo_reuse_permission_verified":False,
 "stock_21C_owner_inventory_match_verified":False,
 "published_11_approved_families_untouched":True,
 "published_55_urls_untouched":True,"prior_QA_images_untouched":True,
 "final_excel_shared":False}
for merchant,url in SOURCES:
 probe={"merchant":merchant,"url":url,"status":"HOLD_API_OR_VARIANT_UNVERIFIED"}
 try:
  res=requests.get(url,headers=HEADER,timeout=17);res.raise_for_status()
  data=res.json()
  title=str(data.get("title",""))
  if not all(k in title.lower() for k in ("mini","founwear","cushion")):
   raise ValueError("Not exact original mini product")
  if not re.search(r"5\s*g",title,re.I):
   raise ValueError("5g size not specified in product title")
  variants=data.get("variants") or []
  exact=[v for v in variants if re.search(r"(?<!\d)21\s*C\b",str(v.get("title") or ""),re.I)]
  probe.update({"title":title,"variant_total":len(variants),
                "exact_21C_variant_count":len(exact),
                "exact_21C_variants":[{"id":str(v.get("id")), "title":v.get("title")} for v in exact]})
  if not exact:
   probe["status"]="HOLD_NO_EXPLICIT_21C_VARIANT";report["merchant_exact_variant_source_probes"].append(probe);continue
  urls=[]
  for v in exact:
   pic=v.get("featured_image")
   if isinstance(pic,str):urls.append((pic,str(v.get("id"))))
   elif isinstance(pic,dict):
    u=pic.get("src") or pic.get("url")
    if u:urls.append((u,str(v.get("id"))))
  unique=[];seen=set()
  for u,vid in urls:
   u=urljoin(url,u)
   if u not in seen:unique.append((u,vid));seen.add(u)
  probe["variant_photo_links"]=[x[0] for x in unique]
  for pic_url,vid in unique[:4]:
   try:
    picres=requests.get(pic_url,headers=HEADER,timeout=15);picres.raise_for_status()
    if len(picres.content)>8000000:continue
    im=Image.open(BytesIO(picres.content));im.load()
    if min(im.size)<450:continue
    native=list(im.size)
    rgb=ImageOps.exif_transpose(im).convert("RGB")
    resized=ImageOps.contain(rgb,(1080,1080),Image.Resampling.LANCZOS)
    img=Image.new("RGB",(1080,1080),"white")
    img.paste(resized,((1080-resized.width)//2,(1080-resized.height)//2))
    file=OUT/f"{len(report['source_image_21C_candidate_files'])+1:02d}-21C-{merchant.replace(' ','-')}-exact-variant-QA.jpg"
    img.save(file,"JPEG",quality=91,optimize=True,subsampling=0)
    assert file.stat().st_size<2_000_000
    report["source_image_21C_candidate_files"].append({
     "file":file.name,"merchant":merchant,"variant_id":vid,
     "exact_shade":"21C Lingerie","source_image_url":pic_url,
     "native_dimensions":native,"sha256":sha(file),"jpg_bytes":file.stat().st_size,
     "visual_single_compact_verification":"PENDING_DIRECT_QA"})
   except (requests.RequestException,OSError,ValueError) as e:
    probe.setdefault("photo_failures",[]).append(str(e)[:160])
  probe["status"]="STAGED_EXPLICIT_21C_VARIANT_LINKED_IMAGE" if report["source_image_21C_candidate_files"] else "HOLD_NO_DECODABLE_VARIANT_PHOTO"
 except Exception as e:
  probe["status"]="HOLD_ERROR";probe["error"]=str(e)[:180]
 report["merchant_exact_variant_source_probes"].append(probe)
n=len(report["source_image_21C_candidate_files"])
if n:
 canvas=Image.new("RGB",(1820,80+425*((n+3)//4)),"#f2f0ed")
 draw=ImageDraw.Draw(canvas)
 draw.text((16,14),"v2822b 21C LINGERIE | EXPLICIT MERCHANT VARIANT PHOTO ONLY | QA HOLD",font=ft(26,True),fill="#282629")
 for i,photo in enumerate(report["source_image_21C_candidate_files"]):
  with Image.open(OUT/photo["file"]) as im:
   thumb=im.convert("RGB").resize((337,337),Image.Resampling.LANCZOS)
  x=18+(i%4)*452;y=62+(i//4)*425
  canvas.paste(thumb,(x,y))
  draw.text((x,y+340),photo["merchant"]+" / 21C",font=ft(21),fill="#333")
else:
 canvas=Image.new("RGB",(1200,230),"#f2f0ed")
 ImageDraw.Draw(canvas).text((18,20),"v2822b NO VERIFIED 21C VARIANT PHOTO | HOLD",font=ft(26,True),fill="#252525")
proof=OUT/"v2822b-21C-merchant-variant-proof.jpg"
canvas.save(proof,"JPEG",quality=83,optimize=True)
(OUT/"v2822b-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["21C_variant_linked_real_photo_count"]=n
report["next_action"]="Visual inspect candidate photos: if only texture swatch, do not use as compact hero; stock 21C availability and right-to-publish remain HOLD."
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2822b","21C_variant_linked_real_photos":n,
 "merchants":[{"name":x["merchant"],"status":x["status"]} for x in report["merchant_exact_variant_source_probes"]],
 "new_sale_approved":False}))
