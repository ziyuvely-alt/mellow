#!/usr/bin/env python3
"""v2886: FIX one v2885 schema mismatch without repeating 95 completed audits.
Four v2775 family manifests store five assets under 'photos'/'destination',
not 'frames'/'path'. Read ONLY those 20 previously skipped JPEGs; use saved
95 dHash metrics to compare, touching old JPEG bytes only when a dHash hit
requires a small color reference. Annotate prior 6 broad layout-similarity
candidates as visually different products based on v2885 proof montage.
No sales approval, no image mutation, no refund/workbook changes.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageDraw,ImageFont,ImageOps
import itertools,copy,json,numpy as np

R=Path("qa-review")
PRE=R/"v2885-23-pending-family-115-existing-JPG-perceptual-dedupe-QA"
STATE=PRE/"stock30-incremental-state-v2885.json"
OUT=R/"v2886-twenty-skipped-v2775-photos-only-append-perceptual-QA"
assert not OUT.exists() and STATE.is_file()
p=json.loads((PRE/"manifest.json").read_text())
old=json.loads((PRE/"per-frame-perceptual-hashes.json").read_text())
state=json.loads(STATE.read_text())
assert p["version"]=="v2885" and state["version"]=="v2885"
assert len(old)==p["JPGs_analyzed"]==95
assert all(x["status"]=="ANALYZED" for x in old)
assert p["JPGs_on_hold_or_unreadable"]==20
FAMILIES=["pending-16","pending-22","pending-27","pending-28"]
BATCH=R/"v2775-four-photo-first-fiveframe-product-QA"
def sha(f):return sha256(f.read_bytes()).hexdigest()
def d_hash(im):
 a=np.asarray(im.convert("L").resize((9,8),Image.Resampling.LANCZOS),dtype=np.int16)
 return sum(int(x)<<i for i,x in enumerate((a[:,1:]>a[:,:-1]).ravel()))
def rgbsize(im):
 return np.asarray(im.convert("RGB").resize((64,64),Image.Resampling.BILINEAR),dtype=np.int16)
def mad(a,b):return round(float(np.mean(np.abs(a-b))),3)
new=[]
for family in FAMILIES:
 mpath=BATCH/family/"manifest.json"
 assert mpath.is_file()
 m=json.loads(mpath.read_text())
 assert m["family"]==family and m["physical_jpgs_staged"]==5
 assert "frames" not in m and isinstance(m["photos"],list) and len(m["photos"])==5
 for row in m["photos"]:
  source=Path(row["destination"])
  assert source.is_file() and source.stat().st_size<2_000_000
  with Image.open(source) as im:
   im.load();assert im.format=="JPEG" and min(im.size)>=640
   h=d_hash(im)
   sample=rgbsize(im)
   size=list(im.size)
  rec={"family":family,"batch":"v2775","slot":row["slot"],
       "file":str(source),"width":size[0],"height":size[1],
       "perceptual_hash_64":f"{h:016x}","byte_sha256":sha(source),
       "status":"ANALYZED_ADDITIONAL_SCHEMA_PHOTOS","photo_source_original_unmodified":True}
  new.append((rec,sample))
assert len(new)==20 and len(set(x[0]["file"] for x in new))==20
# Compare new 20 with old 95 without reprocessing old-old pairs.
# dHash alone overflags similar centered product layout. Re-read color
# only for shortlisted sources (dHash<=8), then require greater color
# agreement; classify as QA review, not a wrong product verdict.
color_cache={}
def oldrgb(path):
 if path not in color_cache:
  with Image.open(path) as im:
   im.load()
   color_cache[path]=rgbsize(im)
 return color_cache[path]
candidate=[]
for index,(n,newrgb) in enumerate(new):
 nh=int(n["perceptual_hash_64"],16)
 for o in old:
  h=(nh^int(o["perceptual_hash_64"],16)).bit_count()
  if h>8:continue
  difference=mad(newrgb,oldrgb(o["file"]))
  if difference>25:continue
  area_new=newrgb[12:52,12:52]
  area_old=oldrgb(o["file"])[12:52,12:52]
  roi=mad(area_new,area_old)
  candidate.append({"family_a":o["family"],"frame_a":o["slot"],
   "file_a":o["file"],"family_b":n["family"],"frame_b":n["slot"],
   "file_b":n["file"],"same_family":o["family"]==n["family"],
   "dhash_hamming":h,"full_RGB_MAD":difference,"central_product_RGB_MAD":roi,
   "possible_near_repeat":bool(h<=6 and difference<=15),
   "likely_same_visual_framing_only":bool(roi>18),
   "retail_status":"HUMAN_QA_ONLY_NO_APPROVAL"})
 for n2,rgb2 in new[index+1:]:
  hd=(nh^int(n2["perceptual_hash_64"],16)).bit_count()
  if hd>8:continue
  diff=mad(newrgb,rgb2)
  if diff>25:continue
  roi=mad(newrgb[12:52,12:52],rgb2[12:52,12:52])
  candidate.append({"family_a":n["family"],"frame_a":n["slot"],"file_a":n["file"],
    "family_b":n2["family"],"frame_b":n2["slot"],"file_b":n2["file"],
    "same_family":n["family"]==n2["family"],
    "dhash_hamming":hd,"full_RGB_MAD":diff,"central_product_RGB_MAD":roi,
    "possible_near_repeat":bool(hd<=6 and diff<=15),
    "likely_same_visual_framing_only":bool(roi>18),
    "retail_status":"HUMAN_QA_ONLY_NO_APPROVAL"})
candidate.sort(key=lambda o:(not o["possible_near_repeat"],o["dhash_hamming"],o["full_RGB_MAD"]))
flagged=[x for x in candidate if x["possible_near_repeat"]]
# Six visually reviewed v2885 matches share graphic-white backgrounds but
# show unmistakably different labeled products. Do NOT call these product
# mix-ups or re-run 95-image dHash analysis.
reviewed=[]
for t in p["human_review_top_pairs"]:
 if not t["possible_near_repeat_for_human_QA"]:continue
 reviewed.append({"a":t["family_a"],"a_slot":t["frame_a"],
  "b":t["family_b"],"b_slot":t["frame_b"],
  "v2885_visual_source":"v2885-23family-115scene-perceptual-QA-triage.jpg",
  "result":"VISUALLY_DISTINCT_LABELED_PRODUCT_SIMILAR_STUDIO_LAYOUT",
  "not_product_identity_mismatch":True,
  "note":"Inspect product label and packaging rather than treating small perceptual hash Hamming as evidence of wrong source."})
assert len(reviewed)==p["visual_candidate_pairs"]==6
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ft=lambda n,b=False:ImageFont.truetype(B if b else F,n)
proof=Image.new("RGB",(1580,1150),"#F1EFF2")
d=ImageDraw.Draw(proof)
d.text((18,14),"v2886  |  FOUR v2775 FAMILIES / 20 PHOTOS  |  INCREMENTAL QA",font=ft(23,True),fill="#493E4C")
if flagged:
 for i,pair in enumerate(flagged[:6]):
  col=i%2;row=i//2
  left=20+col*775;top=75+row*344
  for j,sp in enumerate((pair["file_a"],pair["file_b"])):
   with Image.open(sp) as im:
    pic=ImageOps.contain(im.convert("RGB"),(355,265),Image.Resampling.LANCZOS)
   proof.paste(pic,(left+j*369+(355-pic.width)//2,top+(265-pic.height)//2))
  d.text((left+8,top+271),f"{pair['family_a']}/{pair['frame_a']} : {pair['family_b']}/{pair['frame_b']}",font=ft(15,True),fill="#5B4F60")
  d.text((left+8,top+298),f"h={pair['dhash_hamming']}, fullMAD={pair['full_RGB_MAD']}, centerMAD={pair['central_product_RGB_MAD']}",font=ft(13),fill="#695E6D")
else:
 d.text((40,200),"No near-repeat image candidates among the remaining 20 photos.",font=ft(24),fill="#53465A")
d.text((22,1114),"DIFFERENT PACKAGING AND LABELS MATTER MORE THAN SIMILAR WHITE GRAPHIC BACKGROUNDS.",font=ft(17,True),fill="#67586A")
contact=OUT/"v2886-extra20-original-photo-perceptual-QA-contact.jpg"
proof.save(contact,"JPEG",quality=88,optimize=True)
new_results=[x[0] for x in new]
assert len(old)+len(new_results)==115
report={"version":"v2886","baseline":"v2885",
 "algorithm_revision":"Support v2775 photos/destination schema. Scan only missing 20; reuse previous 95 hashes, color sample read on low-Hamming candidates only.",
 "new_families":[*FAMILIES],"new_JPGs_analyzed":20,
 "previously_analyzed_JPGs_not_rescanned":95,
 "complete_23_families":23,"all_baseline_115_JPGs_covered":True,
 "v2885_previous_candidate_pairs":6,
 "v2885_manual_visual_distinct_products":reviewed,
 "additional_possible_visual_repeat_pairs":len(flagged),
 "additional_pair_details":candidate[:40],
 "full_new_jpg_hash_rows":new_results,
 "new_JPG_files_generated":0,
 "diagnostic_contact":str(contact),"diagnostic_sha256":sha(contact),
 "prior_115_source_JPG_files_modified":0,
 "previous_11_approved_groups_unchanged":True,
 "previous_55_public_URLs_unchanged":True,
 "no_commercial_license_assumed":True,
 "no_owner_stock_edition_assumed":True,
 "new_retail_approval":0,"new_public_URLs":0,"final_spreadsheet_shared":False,
 "next":"Only inspect any new candidate pair at original resolution. Do not change already completed product photos based on dHash alone; actual retail release still requires physical stock / license / original MK."}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"all-115-source-file-perceptual-index.json").write_text(json.dumps(old+new_results,ensure_ascii=False,indent=2)+"\n")
state=copy.deepcopy(state)
assert len(state["families"])==30
state.update(version="v2886",baseline="v2885",
  last_operation="v2886 20 v2775 unscanned actual images added without repeated 95 processing",
  full_baseline_perceptual_QA={"families":23,"images":115,
   "layout_false_positive_visual_reviews":6,
   "new_potential_visual_similarity_pairs":len(flagged),
   "report":str(OUT/"manifest.json")},
  new_retail_approvals=0,new_public_URLs=0,final_spreadsheet_shared=False)
(OUT/"stock30-incremental-state-v2886.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2886","new_JPGs_analyzed":20,
 "previous_JPGs_preserved":95,"total":115,
 "additional_pairs":len(flagged),"retail_approved":0}))
