#!/usr/bin/env python3
"""Audit newest independently preserved image review branches without changing any files.
Uses GitHub REST API and Pillow; output JSON only, never XLSX.
A green technical check MUST NOT be interpreted as release approval.
"""
import io,json,os,urllib.request,urllib.error,hashlib
from pathlib import Path
from PIL import Image
REPO="ziyuvely-alt/mellow"
BRANCHES=[
 ("pending-03","production-assets-v2513-missha-bb-legible"),
 ("pending-03","production-assets-v2512-missha-bb-stock-info"),
 ("pending-04","production-assets-v2500b-clio-single-shade-corrected"),
 ("pending-04","production-assets-v2500-clio-mini-targeted"),
 ("pending-05","production-assets-v2507-drg-clio-info-QA"),
 ("pending-09","production-assets-v2467-obge-photo-layout-repair"),
 ("pending-10","production-assets-v2511-obge-homme-15g-corrected"),
 ("pending-11","production-assets-v2493-obge-double-essence-three"),
 ("pending-15","production-assets-v2507-drg-clio-info-QA"),
 ("pending-16","production-assets-v2503-drg-old-2022-three"),
 ("pending-17","production-assets-v2489-drg-moisture-three"),
 ("pending-18","production-assets-v2514-drg-brightening-three"),
 ("pending-18","production-assets-v2515-drg-brightening-one"),
 ("pending-19","production-assets-v2494b-goodal-alpha-corrected"),
 ("pending-20","production-assets-v2497-goodal-25ad-mist"),
 ("pending-20","production-assets-v2501-goodal-one-usage-fix"),
 ("pending-21","production-assets-v2505-goodal-eye-three"),
 ("pending-26","production-assets-v2473-pixelpure-two-family-six"),
 ("pending-27","production-assets-v2466-pixelpure-toner-three"),
 ("pending-28","production-assets-v2462-pixelpure-three-info"),
 ("pending-29","production-assets-v2469-pixelpure-cream-three"),
 ("pending-30","production-assets-v2473-pixelpure-two-family-six"),
]
# A list of review branches, NOT 22 approved image packs. Several branches include different families and superseded cards.
TOKEN=os.environ.get("GH_TOKEN","")
def get(url,raw=False):
 req=urllib.request.Request(url,headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"Shopee-source-QA"})
 with urllib.request.urlopen(req,timeout=22) as r:return r.read() if raw else json.load(r)
def status_for(family,branch,path):
 # do not infer file family for mixed branch from filename alone
 if branch=="production-assets-v2507-drg-clio-info-QA":
  return path.startswith(family+"/")
 if branch=="production-assets-v2473-pixelpure-two-family-six":
  return path.startswith(family+"/")
 return True
out=Path("v2516-branch-image-audit");out.mkdir(exist_ok=True)
result={"version":"v2516","date":"2026-11-04","repository":REPO,"branches_checked":0,
"technical_only":True,"release_QA_approved":False,"old_55_verified_urls_immutable":True,
"source_photo_rights_not_verified_by_this_audit":True,"MK_logo_not_fixed_by_this_audit":True,
"stock_edition_not_verified_by_this_audit":True,"excel_shared":False,"records":[]}
seen_sha={}
for family,branch in BRANCHES:
 record={"family":family,"branch":branch,"status":"FETCH_FAILED","images":[],"errors":[]}
 try:
  from urllib.parse import quote
  tree=get(f"https://api.github.com/repos/{REPO}/git/trees/{quote(branch,safe='')}?recursive=1")
  if tree.get("truncated"):raise ValueError("Branch tree was truncated")
  files=[x for x in tree.get("tree",[]) if x.get("type")=="blob" and x["path"].lower().endswith((".jpg",".jpeg")) and status_for(family,branch,x["path"])]
  for item in files:
   path=item["path"]
   try:
    url=f"https://raw.githubusercontent.com/{REPO}/{quote(branch,safe='')}/{quote(path,safe='/')}"
    raw=get(url,raw=True)
    im=Image.open(io.BytesIO(raw));im.load()
    sha=hashlib.sha256(raw).hexdigest()
    key=f"{family}:{sha}"
    entry={"path":path,"sha256":sha,"bytes":len(raw),"dimensions":list(im.size),
           "format":im.format,"is_1080x1080_under_2mb":im.format=="JPEG" and im.size==(1080,1080) and len(raw)<2000000,
           "duplicate_content_in_other_branch":seen_sha.get(key)}
    if key not in seen_sha:seen_sha[key]=branch+":"+path
    record["images"].append(entry)
   except Exception as e:record["errors"].append({"path":path,"exception":str(e)[:190]})
  record["status"]="FILES_CHECKED" if files else "NO_JPG_MATCH"
  record["image_files_found"]=len(files)
  record["passed_technical_count"]=sum(x["is_1080x1080_under_2mb"] for x in record["images"])
 except Exception as e:record["errors"].append({"branch":branch,"exception":str(e)[:190]})
 result["records"].append(record);print(json.dumps({"family":family,"branch":branch,"status":record["status"],"files":record.get("image_files_found",0),"errors":len(record["errors"])}),flush=True)
result["branches_checked"]=len(result["records"])
result["actual_JPG_files_decoded"]=sum(len(x["images"]) for x in result["records"])
result["technical_pass_count"]=sum(x.get("passed_technical_count",0) for x in result["records"])
result["technical_fail_count"]=result["actual_JPG_files_decoded"]-result["technical_pass_count"]
result["branch_fetch_or_decode_error_count"]=sum(len(x["errors"]) for x in result["records"])
result["sha_duplicates_within_same_family_across_branches"]=sum(bool(i["duplicate_content_in_other_branch"]) for x in result["records"] for i in x["images"])
result["critical_limitations"]=["Content quality, source license, exact-edition, logo and official swatch require separate visual/human QA",
"Two branches can contain superseded versions; manifest alone is not final approval",
"Most of 30 families have not received exact source/rights verification; 55 old published URLs untouched"]
(out/"audit.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:result[k] for k in ["branches_checked","actual_JPG_files_decoded","technical_pass_count","technical_fail_count","branch_fetch_or_decode_error_count","sha_duplicates_within_same_family_across_branches"]}))
