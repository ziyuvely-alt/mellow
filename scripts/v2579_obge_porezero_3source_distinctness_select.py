#!/usr/bin/env python3
"""v2579: keep only genuinely distinct OBgE Pore Zero 50ml actual product scenes
from v2578 plus one independent Taiwan retailer trio-tube candidate. This is QA
PHOTO EVIDENCE ONLY. Nothing is published, original images never altered.
"""
import json,hashlib
from pathlib import Path
from urllib.request import urlopen,Request
from io import BytesIO
from PIL import Image,ImageOps,ImageChops,ImageStat
O=Path("v2579-selected-distinct-obge-porezero-50ml");O.mkdir(exist_ok=True)
B=Path("v2579-base/review-JPG-by-family/pending-23")
N=Path("v2579-v2578")
base=json.loads((N/"manifest.json").read_text())
assert base["version"]=="v2578" and base["independent_real_photographs_downloaded"]==2
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dhash(im):
 p=list(ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS).getdata())
 x=0
 for row in range(8):
  for c in range(8):x=(x<<1)|(p[row*9+c]>p[row*9+c+1])
 return x
def mae(a,b):
 a=a.convert("RGB").resize((128,128));b=b.convert("RGB").resize((128,128))
 return sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
old=[(p,Image.open(p).convert("RGB")) for p in sorted(B.glob("*.jpg"))]
assert len(old)==5
incoming=[]
for record in base["source_photographs"]:
 if record["status"]=="SOURCE_FETCH_HOLD":continue
 p=N/record["candidate_jpg"];assert p.is_file() and sha(p)==record["QA_jpg_sha256"]
 incoming.append({"image":Image.open(p).convert("RGB"),"p":p,"record":record,"original_source":"v2578"})
extra={"url":"https://i6.momoshop.com.tw/1770299201/goodsimg/TP000/8904/0000/016/TP00089040000016_R4_m.jpg",
 "page":"https://www.momoshop.com.tw/TP/TP0008904/goodsDetail/TP00089040000016",
 "tag":"actual-three-tubes-with-texture"}
extra_status="NOT_ATTEMPTED"
try:
 with urlopen(Request(extra["url"],headers={"User-Agent":"Mozilla/5.0","Accept":"image/*"}),timeout=20) as r:raw=r.read(5_000_001)
 assert 12000<len(raw)<5_000_000
 im=Image.open(BytesIO(raw));im.load()
 assert im.format in ("JPEG","PNG","WEBP") and min(im.size)>=400
 fitted=ImageOps.contain(im.convert("RGB"),(1080,1080),Image.Resampling.LANCZOS)
 scene=Image.new("RGB",(1080,1080),"#f7f9f8")
 scene.paste(fitted,((1080-fitted.width)//2,(1080-fitted.height)//2))
 saved=O/(extra["tag"]+"-UNRELEASED-ORIGINAL-SOURCE.jpg")
 scene.save(saved,"JPEG",quality=91,optimize=True)
 incoming.append({"image":scene,"p":saved,"record":{"source_page":extra["page"],"tag":extra["tag"]},"original_source":"additional"})
 extra_status="DOWNLOADED_FOR_REVIEW_ONLY"
except Exception as e:
 extra_status="HOLD_"+type(e).__name__
# Distinctness is assessed against existing slots AND the selected new candidates.
selected=[];quarantine=[]
for c in incoming:
 img=c["image"]
 comparisons=[{"against":f"existing-{int(p.name[:2]):02d}",
   "dhash":(dhash(img)^dhash(baseim)).bit_count(),
   "MAE":round(mae(img,baseim),2)} for p,baseim in old]
 comparisons += [{"against":f"selected-{i+1}",
   "dhash":(dhash(img)^dhash(other["image"])).bit_count(),
   "MAE":round(mae(img,other["image"]),2)} for i,other in enumerate(selected)]
 alerts=[x for x in comparisons if x["dhash"]<=6 or x["MAE"]<8]
 info={"tag":c["record"]["tag"],"source":c["record"]["source_page"],
  "candidate_sha256":sha(c["p"]),"compared_to":comparisons,
  "similarity_alerts":alerts,"copyright_clearance":False,"stock_edition_confirmed":False}
 if alerts:
  info["status"]="QUARANTINE_NEAR_EXISTING_OR_SELECTED"
  quarantine.append(info)
  # Do not copy source candidate to eligible folder. Source archive remains untouched.
 else:
  dst=O/(f"select-{len(selected)+1:02d}-"+c["record"]["tag"]+"-QA.jpg")
  dst.write_bytes(c["p"].read_bytes())
  assert sha(dst)==sha(c["p"])
  info["candidate_selected_file"]=dst.name
  info["status"]="DISTINCT_SCENE_QA_ONLY"
  selected.append({"image":img,"info":info})
assert len(selected)+len(quarantine)==len(incoming)
assert len(old)==5
report={"version":"v2579","family":"pending-23","previous_run":41761951264,
 "source_scenes_considered":len(incoming),"additional_retailer_status":extra_status,
 "source_candidates_distinct":len(selected),"source_candidates_quarantined":len(quarantine),
 "source_images_approving_sales":0,"source_originals_changed":0,"previous_156_files_unchanged":True,
 "previous_public_55_URLs_changed":0,"new_public_URLs":0,"xlsx_created_or_shared":False,
 "sale_approval":False,"stock_edition_and_license_verified":False,
 "selected":[x["info"] for x in selected],"quarantined":quarantine,
 "next":"Use distinct scenes as QA references only. Require licensed real originals, exact 50ml owned packaging, original MK mark, final visual QA before replacing any selling image."}
(O/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"scenes":len(incoming),"selected_distinct":len(selected),"quarantine":len(quarantine),
 "additional_source":extra_status,"new_public_urls":0,"xls_shared":False}))
