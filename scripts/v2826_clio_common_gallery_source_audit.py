#!/usr/bin/env python3
"""v2826 discover ADDITIONAL distinct actual CLIO Original Mini 5g product
photo scenes without reusing 21C/21N/23N option images or inventing swatches.
Only shared gallery media are candidates, never shade-labeled or retail-ready.

Actual product photos differ from shade swatches and promotional reference.
This data is QA-only. Existing approved URLs and prior 21C/21N/23N images are
untouched.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from urllib.parse import urljoin,urlsplit,parse_qs
from io import BytesIO
import requests,json,hashlib,re,base64
OUT=Path("qa-review/v2826-clio-mini5g-common-photo-gallery-source-discovery")
assert not OUT.exists()
OUT.mkdir(parents=True)
VENDORS=[
 ("DODOSKIN","https://www.dodoskin.com/products/clio-kill-cover-founwear-cushion-the-original-mini-5g-3-colors.js"),
 ("Lila Beauty","https://lilabeauty.com.au/products/mini-kill-cover-founwear-cushion-the-original-5g.js")
]
HEAD={"User-Agent":"Mozilla/5.0 (compatible; source QA/1.0)","Accept":"application/json,text/html,image/jpeg,image/png,*/*"}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ft=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={"version":"v2826","baseline":"v2825",
 "product":"CLIO Kill Cover Founwear Cushion The Original Mini 5g",
 "variants":["21C Lingerie","21N Linen","23N Ginger"],
 "supplier_gallery_coverage":[],"downloaded_shared_reference_JPGs":[],
 "never_associate_shared_images_with_shade_without_proof":True,
 "original_21C_21N_23N_sources_unchanged":True,
 "old_11_approved_groups_unchanged":True,"old_55_urls_unchanged":True,
 "source_photo_rights_confirmed":False,
 "owned_stock_variant_and_package_confirmed":False,
 "new_sale_approvals":0,"final_XLSX_shared":False}
def normalize(url,base):
 if not isinstance(url,str):return None
 if url.startswith("//"):url="https:"+url
 return urljoin(base,url)
def asset_key(url):
 u=urlsplit(url)
 return u.netloc.lower()+u.path.lower()
for seller,uri in VENDORS:
 vinfo={"merchant":seller,"endpoint":uri,"status":"HOLD_API","gallery_candidates":0,
        "source_title":"","exact_variants":[]}
 try:
  response=requests.get(uri,headers=HEAD,timeout=18);response.raise_for_status()
  data=response.json()
  title=str(data.get("title",""))
  vinfo["source_title"]=title
  if not ("mini" in title.lower() and "founwear" in title.lower() and re.search(r"5\s*g",title.lower())):
   raise ValueError("Not exact 5g Original Mini product")
  variants=data.get("variants") or []
  id_photo={}
  for v in variants:
   name=str(v.get("title") or "")
   if re.search(r"\b(21C|21N|23N)\b",name,re.I):
    vinfo["exact_variants"].append(name)
   p=v.get("featured_image")
   if isinstance(p,dict):p=p.get("src") or p.get("url")
   photo=normalize(p,uri)
   if photo:id_photo[asset_key(photo)]=name
  images=data.get("images") or []
  seen=set();count=0
  for elem in images[:30]:
   p=elem
   if isinstance(p,dict):p=p.get("src") or p.get("url")
   photo=normalize(p,uri)
   if not photo:continue
   key=asset_key(photo)
   if key in seen or key in id_photo:continue
   seen.add(key)
   try:
    res=requests.get(photo,headers=HEAD,timeout=14);res.raise_for_status()
    if len(res.content)>9000000:continue
    with Image.open(BytesIO(res.content)) as im:
     im.load()
     if min(im.size)<650:continue
     native=list(im.size)
     converted=ImageOps.exif_transpose(im).convert("RGB")
    framed=Image.new("RGB",(1080,1080),"white")
    contained=ImageOps.contain(converted,(1060,1060),Image.Resampling.LANCZOS)
    framed.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
    path=OUT/f"{len(report['downloaded_shared_reference_JPGs'])+1:02d}-COMMON-NOT-SHADE-{seller.replace(' ','-')}-QA.jpg"
    framed.save(path,"JPEG",quality=90,optimize=True,subsampling=0)
    assert path.stat().st_size<2_000_000
    report["downloaded_shared_reference_JPGs"].append({"merchant":seller,
      "file":path.name,"source_url":photo,"source_native_dimensions":native,
      "sha256":sha(path),"jpg_bytes":path.stat().st_size,
      "shade_assignment":"NONE_SHARED_PRODUCT_GALLERY",
      "scene_visual_QA":"NOT_INSPECTED",
      "sales_approved":False})
    count+=1
    if count>=12:break
   except (requests.RequestException,OSError,ValueError) as exc:
    vinfo.setdefault("skipped_photos",[]).append(str(exc)[:125])
  vinfo["status"]="SAVED_SHARED_PHOTO_CANDIDATES" if count else "HOLD_NO_DISTINCT_SHARED_GALLERY_PHOTOS"
  vinfo["gallery_candidates"]=count
 except Exception as err:
  vinfo["status"]="HOLD_PRODUCT_API_OR_IDENTITY"
  vinfo["error"]=str(err)[:200]
 report["supplier_gallery_coverage"].append(vinfo)
files=report["downloaded_shared_reference_JPGs"]
per_page=12
for page in range(max(1,(len(files)+per_page-1)//per_page)):
 selected=files[page*per_page:(page+1)*per_page]
 rows=max(1,(len(selected)+3)//4)
 canvas=Image.new("RGB",(1840,80+rows*405),"#f2f0ee")
 draw=ImageDraw.Draw(canvas)
 draw.text((16,12),f"v2826 COMMON PRODUCT GALLERY SOURCE PAGE {page+1} | NO SHADE CLAIM",font=ft(25,True),fill="#2d292b")
 for i,row in enumerate(selected):
  with Image.open(OUT/row["file"]) as im:
   thumb=im.convert("RGB").resize((330,330),Image.Resampling.LANCZOS)
  x=17+(i%4)*456;y=59+(i//4)*405
  canvas.paste(thumb,(x,y))
  draw.text((x,y+339),row["merchant"]+" / NO SHADE",font=ft(20),fill="#343034")
 proof=OUT/f"v2826-gallery-contact-{page+1}.jpg"
 canvas.save(proof,"JPEG",quality=81,optimize=True)
 (OUT/f"v2826-gallery-contact-{page+1}.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["shared_gallery_photos_archived"]=len(files)
report["next_action"]="Visually inspect each image and reject exact shade-specific scenes that cannot be tied to 21C or 21N. Do not turn generic photos into 21C/21N variant slots."
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2826","count":len(files),
 "merchants":[{"name":x["merchant"],"count":x["gallery_candidates"],"status":x["status"]} for x in report["supplier_gallery_coverage"]],
 "new_approved":0}))
