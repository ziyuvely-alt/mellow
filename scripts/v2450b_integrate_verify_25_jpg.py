#!/usr/bin/env python3
"""v2450b: Validate and consolidate 20 prior exact JPEGs plus 5 new JPGs.
Uses 4 prior visually confirmed placeholder MK logo frames as positive templates.
No image rerender, no spreadsheets, no publication, no false rights approval.
"""
from pathlib import Path
from PIL import Image
import cv2,numpy as np
import hashlib,json,shutil,zipfile
A=Path("prior-v2449b");B=Path("prior-v2450");C=Path("prior-v2445b")
OUT=Path("v2450b-output");OUT.mkdir(exist_ok=True)
a=json.loads((A/"v2449b-resumable-checkpoint.json").read_text())
b=json.loads((B/"v2450_checkpoint.json").read_text())
c=json.loads((C/"v2445b-resumable-checkpoint.json").read_text())
assert len(a["files"])==20 and len(b["items"])==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cvimg(p):
 im=cv2.imread(str(p),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[:2]==(1080,1080)
 return im
positive=[x for x in c["asset_rows"] if x["disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
assert len(positive)==4
templates=[]
for x in positive:
 src=C/x["file"];assert sha(src)==x["sha256"]
 im=cvimg(src)
 for lx,ly,w,h in [(834,736,77,82),(842,748,61,68),(827,733,90,88)]:
  templates.append(cv2.cvtColor(im[ly:ly+h,lx:lx+w],cv2.COLOR_BGR2GRAY))
def corr(p):
 ro=cv2.cvtColor(cvimg(p)[675:895,760:996],cv2.COLOR_BGR2GRAY)
 return max(float(cv2.minMaxLoc(cv2.matchTemplate(ro,t,cv2.TM_CCOEFF_NORMED))[1]) for t in templates)
assert min(corr(C/x["file"]) for x in positive)>0.99
results=[]
for base,rows,pathkey,sha_key,origin in [
 (A,a["files"],"file","sha256","prior_v2449b"),
 (B,b["items"],"new_file","new_sha256","new_v2450")]:
 for x in rows:
  p=base/x[pathkey]
  assert p.is_file() and sha(p)==x[sha_key]
  with Image.open(p) as test:
   test.load();assert test.format=="JPEG" and test.size==(1080,1080) and p.stat().st_size<2_000_000
  score=corr(p)
  gid=x["group_id"]
  status="MK_LOGO_MATCH_QUARANTINE" if score>=0.68 else "PHOTO_AND_PACKAGE_RIGHTS_HOLD"
  if origin=="prior_v2449b" and gid in ("pending-09","pending-16") and "v2449" in p.name:
   status="MODEL_LIKENESS_PERMISSION_HOLD"
  if gid=="pending-27":status="200ML_TONER_EXACT_PHOTO_GENERATION_HOLD"
  target=OUT/"25-actual-customer-JPGs-not-final"/gid/(origin+"__"+p.name)
  target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,target)
  assert sha(target)==x[sha_key]
  results.append({"group_id":gid,"file":str(target.relative_to(OUT)),"SHA256":x[sha_key],
   "source_version":origin,"logo_template_correlation":round(score,5),"hold":status,
   "commercial_photo_rights_verified":False,"real_stock_package_verified":False,
   "final_sku_release":False})
assert len(results)==25 and len(set((x["group_id"],x["SHA256"]) for x in results))==25
report={"version":"2.4.50b","previous_completed_checkpoint":"production-assets-v2449b-20-actual-photo-candidates",
 "new_batch":"production-assets-v2450-five-fresh-customer-JPGs",
 "customer_JPG_byte_verified":25,"prior_20_JPG_unchanged":True,"new_JPGs_added":5,
 "distinct_product_groups":len(set(x["group_id"] for x in results)),
 "MK_template_positive_controls_passed":True,
 "MK_template_matches":sum(x["hold"]=="MK_LOGO_MATCH_QUARANTINE" for x in results),
 "all_25_in_1080x1080_JPG_under2MB":True,
 "previous_64_MK_quarantined_images_overwritten":0,
 "previous_531_historical_JPGs_overwritten":0,"public_55_URL_paths_modified":0,
 "new_approved_full_product_sets":0,
 "photo_rights_approved":0,"stock_edition_verified":0,
 "user_requested_no_spreadsheets_until_all_finished":True,
 "spreadsheet_created_or_shared":False,"new_color_swatches":0,
 "files":results,
 "remaining":["Official same-edition C8 shade charts and exact option match for MISSHA, CLIO, peripera, OBgE",
 "Original MK PNG binary unavailable in checked sources",
 "All 30 families require per-frame human visual QA and rights, even for images with no MK template match",
 "Physical stock package proof and photo-use rights not established",
 "Blurred OBgE 300mL bottle source must not be sharpened or reconstructed",
 "No workbook/XLSX/Google Sheets sharing before all production tasks genuinely complete"],
 "next":"Continue only on as-yet-unedited distinct actual customer photographs and evidence-based product option/stock matching; skip blocked products"
}
(OUT/"v2450b-resumable-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2450b_25_JPG_source-backed_QA-HOLD.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for x in results:z.write(OUT/x["file"],arcname=x["file"])
 z.write(OUT/"v2450b-resumable-checkpoint.json",arcname="v2450b-resumable-checkpoint.json")
with zipfile.ZipFile(OUT/"v2450b_25_JPG_source-backed_QA-HOLD.zip") as z:
 assert len(z.namelist())==26 and z.testzip() is None
print(json.dumps({"version":"v2450b","byte_verified":25,"families":report["distinct_product_groups"],"MK_matches":report["MK_template_matches"],"spreadsheet_shared":False,"approved_groups":0}),flush=True)
