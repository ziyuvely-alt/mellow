#!/usr/bin/env python3
"""v2456 full 38-existing-JPG non-destructive visual risk scan.
Checks SHA256, dimensions, known fake MK logo similarity, perceptual near duplicate,
central image sharpness. Every numerical flag needs direct visual confirmation
before rejection. All JPEGs stay unchanged; no spreadsheet created.
"""
from pathlib import Path
from collections import defaultdict
import hashlib,json
import numpy as np,cv2
SRC=Path("prior-v2455b");CTRL=Path("prior-v2445b")
OUT=Path("v2456-output");OUT.mkdir(exist_ok=True)
manifest=json.loads((SRC/"v2455b-current-38jpg-checkpoint.json").read_text())
controls=json.loads((CTRL/"v2445b-resumable-checkpoint.json").read_text())
assert len(manifest["files"])==38
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 im=cv2.imread(str(p),cv2.IMREAD_COLOR)
 assert im is not None and im.shape[:2]==(1080,1080),p
 assert p.stat().st_size<2_000_000
 return im
positive=[x for x in controls["asset_rows"] if x["disposition"]=="KNOWN_MK_BADGE_QUARANTINE"]
assert len(positive)==4
templates=[]
for x in positive:
 p=CTRL/x["file"];assert sha(p)==x["sha256"]
 im=read(p)
 for xx,yy,w,h in [(834,736,77,82),(842,748,61,68),(827,733,90,88)]:
  templates.append(cv2.cvtColor(im[yy:yy+h,xx:xx+w],cv2.COLOR_BGR2GRAY))
def logo_score(im):
 roi=cv2.cvtColor(im[675:895,760:996],cv2.COLOR_BGR2GRAY)
 return max(float(cv2.minMaxLoc(cv2.matchTemplate(roi,t,cv2.TM_CCOEFF_NORMED))[1]) for t in templates)
positive_scores=[logo_score(read(CTRL/x["file"])) for x in positive]
assert min(positive_scores)>0.99,positive_scores
def phash(image):
 gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
 small=cv2.resize(gray,(32,32),interpolation=cv2.INTER_AREA).astype(np.float32)
 freq=cv2.dct(small)[:8,:8]
 median=np.median(freq[1:].reshape(-1))
 return int(''.join('1' if v>median else '0' for v in freq.reshape(-1)),2)
def dist(a,b):return (a^b).bit_count()
rows=[];hash_cache={}
for x in manifest["files"]:
 p=SRC/x["file"];assert p.is_file() and sha(p)==x["sha256"]
 im=read(p);g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
 sharpen_metric=float(cv2.Laplacian(g[240:850,210:870],cv2.CV_64F).var())
 logo=logo_score(im)
 hashed=phash(im)
 rows.append({
   "group_id":x["group_id"],"source_file":x["file"],"sha256":x["sha256"],
   "size_bytes":p.stat().st_size,
   "central_laplacian_variance":round(sharpen_metric,2),
   "low_central_edge_metric_FLAG_ONLY":bool(sharpen_metric<48),
   "MK_logo_match_correlation":round(logo,5),
   "possible_MK_logo_flag":bool(logo>=0.68),
   "perceptual_hash64":f"{hashed:016x}",
   "direct_manual_visual_QA":"NOT_YET_COMPLETE_FOR_ALL_FRAMES",
   "commercial_photo_use_rights_verified":False,
   "original_product_physical_stock_verified":False,
   "final_sales_approved":False
 })
 hash_cache[x["file"]]=hashed
assert len(rows)==38
groups=defaultdict(list)
for x in rows:groups[x["group_id"]].append(x)
pairs=[]
for gid,group in groups.items():
 for i,a in enumerate(group):
  for b in group[i+1:]:
   ham=dist(hash_cache[a["source_file"]],hash_cache[b["source_file"]])
   if ham<=8:pairs.append({"group":gid,"fileA":a["source_file"],"fileB":b["source_file"],
                           "hamming_distance":ham,"meaning":"CHECK_VARIETY_MANUALLY_NOT_AUTO_REJECT"})
scanned={"version":"2.4.56","source":"production-assets-v2455b-38-JPGs-official-shade-evidence",
"all_38_source_jpg_hashes_reverified":True,
"known_MK_positive_control_scores":positive_scores,
"total_JPGs":38,"product_families":len(groups),
"new_JPG_created":0,
"prior_JPGs_modified":0,
"published_55_URLs_modified":0,
"logo_match_flagged_count":sum(x["possible_MK_logo_flag"] for x in rows),
"low_sharpness_metric_flagged_count":sum(x["low_central_edge_metric_FLAG_ONLY"] for x in rows),
"within_family_near_duplicate_pairs":len(pairs),
"no_spreadsheets_created_or_shared":True,"FINAL_SALE_APPROVED":0,
"limits":["Laplacian variance also varies with large blank backgrounds; not a validated blur classifier",
        "pHash on templated cards may flag similar layouts; not proof of identical product photos",
        "Known-logo template non-match does not prove absence of other unlicensed logos",
        "Original MK PNG and commercial product photo rights remain unresolved",
        "Product edition and color swatch verification remain independent holds"],
"files":rows,"suspected_near_duplicate_pairs":pairs,
"next":["Visually inspect top low sharpness and any MK flagged JPGs, not only statistics",
        "Do not reject or auto approve source images solely on quantitative QA",
        "For current 38, keep 5/6-frame sale approval pending until source license, same-generation stock and official swatch proof"]}
(OUT/"v2456_full_38_JPG_visual_quality_audit.json").write_text(json.dumps(scanned,indent=2,ensure_ascii=False))
print(json.dumps({k:scanned[k] for k in ["total_JPGs","product_families","logo_match_flagged_count","low_sharpness_metric_flagged_count","within_family_near_duplicate_pairs","new_JPG_created"]}),flush=True)
