#!/usr/bin/env python3
"""v2587: new exact-family product photo scenes for MISSHA original M Perfect
Cover BB and Dr.G Brightening Up MOISTURE Sun. Distinguish from PRO / Sun PLUS.
Retain every previous source. Photos are QA-only with edition & reuse-rights HOLD.
Batch 4 image URLs, continue on individual source failures.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageOps,ImageStat,ImageChops
from io import BytesIO
import hashlib,json
B=Path("v2587-original/review-JPG-by-family")
O=Path("v2587-missha-drg-four-real-scene-QA");O.mkdir(exist_ok=True)
requests=[
{"family":"pending-03","product":"MISSHA M Perfect Cover BB Cream original, not PRO","tag":"21-23-old-packaging-pumps","url":"https://img.joomcdn.net/b7a09e59dccdbcbab58bf5e8966c7d7c6d2072b3_original.jpeg","page":"https://www.joom.com/en/products/1518668823506100951-89-5-39131-3555168630"},
{"family":"pending-03","product":"MISSHA M Perfect Cover BB Cream original, not PRO","tag":"21-23-25-old-pumps","url":"https://www.masksheets.com/cdn/shop/files/SaveClip.App_472530123_18477522061054131_3334106103140401695_n_grande.jpg?v=1753115640","page":"https://www.masksheets.com/fr-ca/products/m-perfect-cover-bb-cream-23-natural-beige"},
{"family":"pending-17","product":"Dr.G Brightening Up Moisture Sun 50mL, not Brightening Up SUN PLUS","tag":"real-moisture-sun-lifestyle","url":"https://www.dodoskin.com/cdn/shop/files/Dr.GBrighteningUpMoistureSunSPF50_PA_50ml-2.jpg?v=1746425335&width=3000","page":"https://www.dodoskin.com/en-il/products/dr-g-brightening-up-moisture-sun-spf50-pa-50ml"},
{"family":"pending-17","product":"Dr.G Brightening Up Moisture Sun 50mL, not Brightening Up SUN PLUS","tag":"real-moisture-sun-texture","url":"https://soonsubeauty.com/cdn/shop/files/81840415670479662_1933787592.jpg?v=1761670232","page":"https://soonsubeauty.com/products/dr-g-brightening-up-moisture-sun-50ml"}]
def sha(x):return hashlib.sha256(x).hexdigest()
def dhash(im):
 q=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata());n=0
 for y in range(8):
  for x in range(8):n=(n<<1)|(q[y*9+x]>q[y*9+x+1])
 return n
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,2)
baseline={}
for f in ("pending-03","pending-17"):
 paths=sorted((B/f).glob("*.jpg"));assert len(paths)==5
 baseline[f]=[(int(p.name[:2]),Image.open(p).convert("RGB")) for p in paths]
byfamily={f:[] for f in baseline};results=[]
for s in requests:
 entry={k:s[k] for k in ("family","tag","product","url","page")}
 try:
  with urlopen(Request(s["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/jpeg,image/*"}),timeout=17) as resp:raw=resp.read(6_000_001)
  assert 12_000<len(raw)<6_000_000
  im=Image.open(BytesIO(raw));im.load()
  assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=420
  scaled=ImageOps.contain(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
  image=Image.new("RGB",(1080,1080),"#fafafa")
  image.paste(scaled,((1080-scaled.width)//2,(1080-scaled.height)//2))
  path=O/(s["family"]+"-"+s["tag"]+"-CANDIDATE.jpg")
  image.save(path,"JPEG",quality=90,optimize=True,subsampling=0)
  assert Image.open(path).size==(1080,1080) and path.stat().st_size<2_000_000
  comparisons=[{"comparison":"existing-"+str(slot),"dhash_distance":(dhash(image)^dhash(old)).bit_count(),"MAE":mae(image,old)} for slot,old in baseline[s["family"]]]
  comparisons += [{"comparison":"prior-new-"+v["tag"],"dhash_distance":(dhash(image)^dhash(v["image"])).bit_count(),"MAE":mae(image,v["image"])} for v in byfamily[s["family"]]]
  near=[r for r in comparisons if r["dhash_distance"]<=6 or r["MAE"]<8]
  status="QUARANTINE_NEAR_OTHER_SCENE" if near else "NEW_DISTINCT_PHOTO_QA_ONLY"
  entry.update({"status":status,"saved_file":path.name,"jpg_sha256":sha(path.read_bytes()),"original_sha256":sha(raw),"source_px":list(im.size),"near":near,"comparisons":comparisons})
  if not near:byfamily[s["family"]].append({"tag":s["tag"],"image":image})
 except Exception as e:entry.update({"status":"SOURCE_UNAVAILABLE_HOLD","error_class":type(e).__name__})
 entry["source_rights_verified"]=False
 entry["owned_exact_stock_package_verified"]=False
 entry["new_selling_photo_approved"]=False
 results.append(entry)
summary={"version":"v2587","families":["pending-03","pending-17"],"attempted":len(requests),
"downloaded":sum(bool(x.get("saved_file")) for x in results),
"selected_distinct":sum(x["status"]=="NEW_DISTINCT_PHOTO_QA_ONLY" for x in results),
"quarantined":sum(x["status"]=="QUARANTINE_NEAR_OTHER_SCENE" for x in results),
"unavailable":sum(x["status"]=="SOURCE_UNAVAILABLE_HOLD" for x in results),
"known_product_edition_caution":["MISSHA original red pump not new PRO, actual owned stock volume unknown","Dr.G MOISTURE SUN is not SUN PLUS; actual 2023 stock packaging unverified"],
"previous_156_source_JPG_preserved":True,"previous_v2586_13_QA_delta_preserved":True,"public_55_URLs_changed":0,"new_URLs":0,"xlsx_created_or_shared":False,
"photo_rights_and_stock_edition_approved":False,"items":results}
(O/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:summary[k] for k in ("downloaded","selected_distinct","quarantined","unavailable")}))
