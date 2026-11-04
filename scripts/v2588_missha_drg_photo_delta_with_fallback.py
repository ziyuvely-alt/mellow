#!/usr/bin/env python3
"""v2588 exact product photo QA incremental addition from v2587.
Reuse three photo JPGs; retry ONLY the failed fourth source via an alternate
same-product page. Place up to two distinct images per family into slots 03/05,
without altering baseline, prior thirteen deltas or any public URL.
"""
from pathlib import Path
from io import BytesIO
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageChops,ImageStat
import json,hashlib
B=Path("v2588-base/review-JPG-by-family")
OLD=Path("v2588-prev")
SOURCE=Path("v2588-source")
OUT=Path("v2588-MISSHA-DrG-photo-deltas")
OUT.mkdir(exist_ok=True)
old=json.loads((OLD/"manifest.json").read_text())
info=json.loads((SOURCE/"manifest.json").read_text())
assert old["version"]=="v2586" and old["delta_count"]==13
assert info["version"]=="v2587" and len(info["items"])==4
assert info["downloaded"]==3
prior={(x["family"],x["slot"]) for x in old["previous_eleven"]}
prior.add((old["twelfth"]["family"],old["twelfth"]["slot"]))
prior.add((old["thirteenth"]["family"],old["thirteenth"]["slot"]))
assert len(prior)==13
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 a=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata());h=0
 for i in range(8):
  for j in range(8):h=(h<<1)|(a[i*9+j]>a[i*9+j+1])
 return h
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
fallbacks={
 "pending-03":("https://korean-skincare.de/cdn/shop/files/missha-m-perfect-cover-bb-cream-spf42-pa-29-caramel-beige-foundations-concealers-38449178476780_webp_cd891315-81d7-44f7-b9cf-f0915a1eb985.jpg?v=1751286946",
               "https://korean-skincare.de/products/missha-m-perfect-covering-bb-cream-spf42-pa"),
 "pending-17":("https://img.hwahae.co.kr/products/2023450/2023450_20230215101949.jpg",
               "https://www.hwahae.com/en/products/Dr-G-BRIGHTENING-UP-MOISTURE-SUN-SPF50PLUS-PAPLUS-PLUS-PLUS-PLUS/2023450")
}
records={x["family"]:[] for x in info["items"]}
for item in info["items"]:
 if item["status"]=="NEW_DISTINCT_PHOTO_QA_ONLY":
  f=SOURCE/item["saved_file"]
  assert f.is_file() and sha(f)==item["jpg_sha256"]
  records[item["family"]].append({"file":f,"url":item["url"],"method":"v2587_preserved"})
 else:
  family=item["family"]
  url,page=fallbacks[family]
  try:
   with urlopen(Request(url,headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=18) as r: raw=r.read(6_000_001)
   assert 12_000<len(raw)<6_000_000
   photo=Image.open(BytesIO(raw));photo.load()
   assert photo.format in ("JPEG","PNG","WEBP") and min(photo.size)>=400
   small=ImageOps.contain(photo.convert("RGB"),(1080,1080))
   frame=Image.new("RGB",(1080,1080),"#fafafa")
   frame.paste(small,((1080-small.width)//2,(1080-small.height)//2))
   f=OUT/(family+"-fallback-real-source-QA.jpg")
   frame.save(f,"JPEG",quality=91,optimize=True)
   assert f.stat().st_size<2_000_000
   records[family].append({"file":f,"url":url,"page":page,"method":"alternate_exact_product_reference"})
  except Exception as err:
   records[family].append({"error":type(err).__name__,"status":"SOURCE_FALLBACK_HOLD","url":url})
chosen=[];quarantine=[]
for family in ("pending-03","pending-17"):
 originals=sorted((B/family).glob("*.jpg"))
 assert len(originals)==5
 baselines=[Image.open(p).convert("RGB") for p in originals]
 used=[]
 for item in records[family]:
  if "file" not in item:
   quarantine.append({"family":family,**item})
   continue
  candidate=Image.open(item["file"]);candidate.load()
  assert candidate.format=="JPEG" and candidate.size==(1080,1080)
  checks=[]
  for p,img in zip(originals,baselines):
   checks.append({"against":p.name[:2],"dhash":(dhash(candidate)^dhash(img)).bit_count(),"mae":mae(candidate,img)})
  for obj in used:
   checks.append({"against":"selected","dhash":(dhash(candidate)^dhash(obj)).bit_count(),"mae":mae(candidate,obj)})
  alerts=[c for c in checks if c["dhash"]<=6 or c["mae"]<8]
  if alerts:
   quarantine.append({"family":family,"source":item["url"],"status":"NEAR_DUPLICATE","alerts":alerts})
   continue
  if len(used)>=2:
   quarantine.append({"family":family,"source":item["url"],"status":"OVER_CAPACITY"})
   continue
  slot=(3,5)[len(used)]
  assert (family,slot) not in prior
  dest=OUT/(family+f"-slot{slot:02d}-source-photo-QA.jpg")
  dest.write_bytes(item["file"].read_bytes())
  chosen.append({"family":family,"slot":slot,"source":item["url"],"method":item["method"],
    "old_sha256":sha(originals[slot-1]),"new_sha256":sha(dest),"file":dest.name,
    "edition_verified":False,"photo_rights_verified":False,"sale_ready":False})
  used.append(candidate.convert("RGB"))
assert 3<=len(chosen)<=4,(len(chosen),quarantine)
assert len({(x["family"],x["slot"]) for x in chosen})==len(chosen)
report={"version":"v2588","previous_v2586_run":41763244120,"source_v2587_run":41763646587,
"existing_thirteen_preserved":True,"additional_real_photo_QA_deltas":len(chosen),
"virtual_total_QA_deltas":13+len(chosen),"unmodified_original_slots":156-13-len(chosen),
"other_28_product_families_untouched":True,"source_photo_rights_confirmed":False,
"exact_stock_edition_human_checked":False,"original_MK_logo_inserted":False,
"full_sales_approval":False,"new_public_URLs":0,"old_55_public_URLs_changed":0,
"XLSX_created_or_shared":False,"new_changes":chosen,"quarantine":quarantine,
"provenance":{"prior_manifest":"v2586","new_source_manifest":"v2587"}}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_QA_photos":len(chosen),"virtual_total_changes":13+len(chosen),
"unresolved_or_similarity_holds":len(quarantine),"public_changes":0,"XLSX":False}))
