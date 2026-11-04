#!/usr/bin/env python3
"""v2819: inspect Shopify exact 5g CLIO Original Mini variants, save 21N-specific
real photos ONLY when explicitly assigned to a 21N variant ID or featured_image.
No reuse of 23N shade scenes, no fabricated/averaged shade chips.
Only internal reference QA; no commercial image permission inferred.
"""
from pathlib import Path
from PIL import Image,ImageOps
from io import BytesIO
import requests,hashlib,json,re,base64
OUT=Path("qa-review/v2819-clio-original-mini-5g-21N-exact-variant-photo-evidence")
assert not OUT.exists()
OUT.mkdir(parents=True)
PRODUCTS=[
 ("Lila Beauty","https://lilabeauty.com.au/products/mini-kill-cover-founwear-cushion-the-original-5g.js"),
 ("DODOSKIN","https://www.dodoskin.com/products/clio-kill-cover-founwear-cushion-the-original-mini-5g-3-colors.js"),
]
HEAD={"User-Agent":"Mozilla/5.0","Accept":"application/json,image/avif,image/webp,image/jpeg,image/png,*/*"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
evidence=[];photo_candidates=[]
for store,url in PRODUCTS:
 record={"store":store,"shopify_product_json":url,"status":"NOT_VERIFIED","matched_21N_variants":[],"product_title":None}
 try:
  r=requests.get(url,headers=HEAD,timeout=17);r.raise_for_status()
  d=r.json()
  title=str(d.get("title",""))
  if not ("clio" in title.lower() and "mini" in title.lower() and ("original" in title.lower() or "5g" in title.lower())):
    raise ValueError("Product JSON is not exact CLIO Original Mini 5g: "+title[:140])
  record["product_title"]=title
  variants=d.get("variants",[])
  match=[v for v in variants if re.search(r"(?<!\w)21\s*N(?!\w)|linen",str(v.get("title","")),re.I)]
  record["variant_count"]=len(variants)
  imgs=d.get("images",[])
  record["gallery_count"]=len(imgs)
  for v in match:
   vid=v.get("id")
   ent={"variant_id":str(vid),"variant_name":str(v.get("title")),
        "featured_image_present":False,"explicit_photo_urls":[]}
   feature=v.get("featured_image")
   if isinstance(feature,dict):
    u=feature.get("src")
    if u:ent["explicit_photo_urls"].append(u)
   elif isinstance(feature,str):
    ent["explicit_photo_urls"].append(feature)
   for im in imgs:
    if isinstance(im,dict) and (vid in im.get("variant_ids",[]) or str(vid) in [str(x) for x in im.get("variant_ids",[])]):
      url2=im.get("src")
      if url2:ent["explicit_photo_urls"].append(url2)
   ent["explicit_photo_urls"]=list(dict.fromkeys(ent["explicit_photo_urls"]))
   ent["featured_image_present"]=bool(ent["explicit_photo_urls"])
   record["matched_21N_variants"].append(ent)
   for u in ent["explicit_photo_urls"]:
    photo_candidates.append({"merchant":store,"url":u,"variant_id":str(vid),"variant_name":str(v.get("title"))})
  record["status"]="VARIANT_MATCH_FOUND" if match else "HOLD_21N_VARIANT_NOT_FOUND"
 except Exception as e:
  record.update({"status":"HOLD_MERCHANT_JSON_UNAVAILABLE","error":str(e)[:240]})
 evidence.append(record)
# Only images attached to 21N variants qualify; metadata links are not photo-license proof.
seen=set();stored=[]
for ent in photo_candidates[:12]:
 if len(stored)>=5:break
 try:
  r=requests.get(ent["url"],headers={"User-Agent":"Mozilla/5.0"},timeout=15);r.raise_for_status()
  assert 7000<len(r.content)<8_000_000
  with Image.open(BytesIO(r.content)) as img:
   img.load();assert min(img.size)>=350
   rgb=ImageOps.exif_transpose(img).convert("RGB")
   dim=list(img.size)
  visual_hash=hashlib.sha256(rgb.resize((24,24),Image.Resampling.LANCZOS).tobytes()).hexdigest()
  if visual_hash in seen:continue
  seen.add(visual_hash)
  name=f"{len(stored)+1:02d}-source-linked-exact-21N-mini5g-QA.jpg"
  path=OUT/name
  white=Image.new("RGB",(1080,1080),"white")
  contained=ImageOps.contain(rgb,(1050,1050),Image.Resampling.LANCZOS)
  white.paste(contained,((1080-contained.width)//2,(1080-contained.height)//2))
  white.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
  assert path.stat().st_size<2000000
  stored.append({**ent,"file":name,"native_dimensions":dim,"jpg_sha256":sha(path),"qa_only":True})
 except Exception as e:continue
# generate proof for source-specific candidate images; no phony 21N if no variant mapping.
canvas=Image.new("RGB",(1740,505),"#f2f0ee")
from PIL import ImageDraw,ImageFont
d=ImageDraw.Draw(canvas);font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
d.text((14,12),"v2819 CLIO 5g 21N EXACT VARIANT-LINKED IMAGES ONLY  |  NO 23N SUBSTITUTE",font=font,fill="#303030")
for i,x in enumerate(stored[:4]):
 with Image.open(OUT/x["file"]) as img:
  thumb=img.convert("RGB").resize((400,400),Image.Resampling.LANCZOS)
 canvas.paste(thumb,(14+i*431,56))
 d.text((14+i*431,466),str(x["merchant"])[:23],font=font,fill="#454545")
if not stored:d.text((18,175),"NO VERIFIABLE OPTION-LINKED PHOTO, 21N IMAGE REMAINS ON HOLD",font=font,fill="#7a4444")
preview=OUT/"v2819-variant-linked-21N-source-contact.jpg"
canvas.save(preview,"JPEG",quality=83,optimize=True)
(OUT/"v2819-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode("ascii"))
record={"version":"v2819","baseline":"v2818","family":"pending-05","target_shade":"21N Linen","size":"5g",
 "metadata_probes":evidence,"option_linked_candidate_files":stored,
 "genuine_21N_specific_photos_saved":len(stored),
 "never_substitute_23N":True,
 "previous_23N_five_QA_JPGs_untouched":True,
 "new_21N_images_sales_approved":False,
 "actual_owned_21N_stock_edition_verified":False,
 "photo_rights_verified":False,
 "previous_11_approved_groups_untouched":True,"verified_55_urls_untouched":True,
 "final_spreadsheet_shared":False,
 "next":"If images explicitly mapped to 21N, inspect label and product geometry. Otherwise hold, do not re-label 23N assets."
}
(OUT/"manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2819","21N_proven_variant_linked_images":len(stored),"merchant_metadata_sources":len(evidence),"retail_approved":0}))
