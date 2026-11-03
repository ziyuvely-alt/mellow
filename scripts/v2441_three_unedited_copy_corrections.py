#!/usr/bin/env python3
"""v2441: three targeted actual customer JPG text-only repairs from existing source.
No repeats of v2440e edited frames; no invented photos, shades, permission or approvals.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
B=Path("baseline-v2427b")/"immutable-v2426b/originals-v2425-unchanged/prior-immutable/immutable-prev/preserved-v2422/en-customer-drafts"
O=Path("v2441-output");O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
jobs=[
 {"id":"pending-24","file":"INFO_VOLUME_01_V2414_EN_V2421.jpg","lines":["30 mL","NAD-PRIZCELL Glow Power Serum","BIOHEAL BOH"],"cause":"Source caption omits PRIZCELL element in product line; earlier true packaging text confirmed"},
 {"id":"pending-18","file":"INFO_05_OFFICIAL_V2412_EN_V2421.jpg","lines":["50 mL","Brightening Up Sun Plus","Single sunscreen"],"cause":"Original ornament circle overlaps net-content card"},
 {"id":"pending-22","file":"INFO_03_OFFICIAL_V2412_EN_V2421.jpg","lines":["FACE + BODY","Max Waterful Sun Cream","300 mL"],"cause":"Remove subjective Generous 300mL size; preserve factual existing face/body claim"}
]
rows=[]
for j in jobs:
 p=B/j["id"]/j["file"];assert p.exists(),p
 original_sha=sha(p)
 with Image.open(p) as original:
  original.load();assert original.format=="JPEG" and original.size==(1080,1080)
  im=original.convert("RGB");d=ImageDraw.Draw(im)
  outer=im.getpixel((30,535));inner=im.getpixel((540,324))
  d.rectangle((66,296,1048,774),fill=outer)
  d.rounded_rectangle((72,303,1008,763),radius=39,fill=inner)
  for label,y,size,bold in [(j["lines"][0],378,64,True),(j["lines"][1],568,38,False),(j["lines"][2],650,34,False)]:
   while size>22 and (d.textbbox((0,0),label,font=font(size,bold))[2]>840):size-=1
   assert size>=22
   ff=font(size,bold);w=d.textbbox((0,0),label,font=ff)[2]
   d.text((540-w//2,y),label,font=ff,fill=(45,62,53))
  output=O/"sales-image-drafts"/j["id"]/(j["id"]+"_factual_copy_revision_V2441.jpg")
  output.parent.mkdir(parents=True,exist_ok=True)
  im.save(output,"JPEG",quality=94,optimize=True)
  with Image.open(output) as check:
   check.load();assert check.format=="JPEG" and check.size==(1080,1080) and output.stat().st_size<2_000_000
  assert sha(p)==original_sha and sha(output)!=original_sha
  rows.append({"group_id":j["id"],"source_path":str(p.relative_to(B)),"source_sha256":original_sha,
  "updated_path":str(output.relative_to(O)),"updated_sha256":sha(output),"reason":j["cause"],
  "status":"SALES_IMAGE_DRAFT","external_photo_rights":"UNVERIFIED","physical_stock_generation":"UNVERIFIED","visual_QA":"PENDING"})
report={"version":"2.4.41","baseline":"production-assets-v2440e-12-drafts-consolidated",
 "actually_modified_customer_JPG":len(rows),"new_distinct_group_count":len(rows),"historical_originals_mutated":0,
 "published_55_URL_changes":0,"new_official_swatches":0,"FINAL_QA_APPROVED":0,
 "edits":rows,
 "holds":[{"group":"pending-22","item":"INFO_04_OFFICIAL_V2412_EN_V2421.jpg","reason":"Panthenol/Ectoin/hyaluronic derivatives ingredient claims not verified against exact 300mL INCI; keep on hold"}],
 "next":["Open and visually inspect all three new JPGs","If a draft is defective, reject that draft only and preserve other groups","Continue incomplete 30-family per-frame QA","Rights and actual stock/package remain independent holds"]}
(O/"v2441_checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ("edits","holds","next")},ensure_ascii=False),flush=True)
