#!/usr/bin/env python3
"""Perceptual duplicate candidate triage, NEVER sales approval.
Read newest JPEG URLs from v2516 saved evidence. Compare within same product family
only, applying horizontal difference hash and an image-color thumbnail histogram.
Many identical informational templates can legitimately be similar; do not auto-delete.
"""
import io,json,os,urllib.request,itertools,hashlib
from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageStat
from urllib.parse import quote
REPO="ziyuvely-alt/mellow"
BRANCHES={
 "pending-03":["production-assets-v2513-missha-bb-legible","production-assets-v2512-missha-bb-stock-info"],
 "pending-04":["production-assets-v2500b-clio-single-shade-corrected","production-assets-v2500-clio-mini-targeted"],
 "pending-09":["production-assets-v2467-obge-photo-layout-repair"],
 "pending-10":["production-assets-v2511-obge-homme-15g-corrected"],
 "pending-11":["production-assets-v2493-obge-double-essence-three"],
 "pending-15":["production-assets-v2507-drg-clio-info-QA"],
 "pending-16":["production-assets-v2503-drg-old-2022-three"],
 "pending-17":["production-assets-v2489-drg-moisture-three"],
 "pending-18":["production-assets-v2514-drg-brightening-three","production-assets-v2515-drg-brightening-one"],
 "pending-19":["production-assets-v2494b-goodal-alpha-corrected"],
 "pending-20":["production-assets-v2497-goodal-25ad-mist","production-assets-v2501-goodal-one-usage-fix"],
 "pending-21":["production-assets-v2505-goodal-eye-three"],
 "pending-26":["production-assets-v2473-pixelpure-two-family-six"],
 "pending-27":["production-assets-v2466-pixelpure-toner-three"],
 "pending-28":["production-assets-v2462-pixelpure-three-info"],
 "pending-29":["production-assets-v2469-pixelpure-cream-three"],
 "pending-30":["production-assets-v2473-pixelpure-two-family-six"]
}
TOKEN=os.environ["GH_TOKEN"]
headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"Shopee-real-JPG-near-duplicate-QA"}
def fetch(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=22) as r:return r.read()
def dhash(im):
 g=ImageOps.grayscale(im).resize((9,8),Image.Resampling.LANCZOS)
 px=list(g.getdata());result=0
 for y in range(8):
  for x in range(8):result=(result<<1)|(px[y*9+x]>px[y*9+x+1])
 return result
def histogram(im):
 return im.convert("RGB").resize((32,32)).histogram()
out=Path("v2517-perceptual-near-duplicate-QA");out.mkdir(exist_ok=True)
report={"date":"2026-11-04","version":"v2517","families_audited":0,"image_count":0,"candidate_pairs":[],"manifest_issues":[],"auto_deleted_files":0,"public_urls_changed":0,"excel_shared":False,"final_sale_QA":False,"purpose":"Prioritize visual duplicate inspection only; no automatic rejection based solely on aHash/dHash"}
for family,branches in BRANCHES.items():
 pics=[]
 for br in branches:
  try:
   tree=json.loads(fetch(f"https://api.github.com/repos/{REPO}/git/trees/{quote(br)}?recursive=1"))
   for f in tree.get("tree",[]):
    path=f["path"]
    if not path.lower().endswith(".jpg"):continue
    if br=="production-assets-v2473-pixelpure-two-family-six" and not path.startswith(family+"/"):continue
    if br=="production-assets-v2507-drg-clio-info-QA" and not path.startswith(family+"/"):continue
    raw=fetch(f"https://raw.githubusercontent.com/{REPO}/{quote(br)}/{quote(path,safe='/')}")
    im=Image.open(io.BytesIO(raw));im.load()
    pics.append({"path":br+"/"+path,"sha256":hashlib.sha256(raw).hexdigest(),"dhash":dhash(im),"histogram":histogram(im)})
  except Exception as e:report["manifest_issues"].append({"family":family,"branch":br,"error":str(e)[:160]})
 if pics:report["families_audited"]+=1
 report["image_count"]+=len(pics)
 for a,b in itertools.combinations(pics,2):
  distance=(a["dhash"]^b["dhash"]).bit_count()
  # strict 8x8 difference hash <= 6 is only a visual candidate requiring review.
  if distance<=6:
   report["candidate_pairs"].append({"family":family,"left":a["path"],"right":b["path"],"dhash_distance":distance,
       "identical_sha256":a["sha256"]==b["sha256"],"decision":"VISUAL_INSPECTION_REQUIRED_NOT_AUTOMATIC_DUPLICATE"})
 print(json.dumps({"family":family,"image_count":len(pics),"near_pairs":len([p for p in report["candidate_pairs"] if p["family"]==family])}),flush=True)
report["near_pair_count"]=len(report["candidate_pairs"])
(out/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({k:report[k] for k in ["families_audited","image_count","near_pair_count","auto_deleted_files","public_urls_changed"]}))
