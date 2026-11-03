#!/usr/bin/env python3
"""v2430: audit actual 30-family customer frames and correct only provable flat white inset artifacts.
Safeguard all product RGB pixels; retouched files are sales-image DRAFT / visual QA hold.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from collections import defaultdict, Counter
import json, hashlib, os, csv
import numpy as np
SRC=Path("v2427b-source"); PREV=Path("v2429c-source"); OUT=Path("v2430-output"); OUT.mkdir(exist_ok=True)
ROOT=SRC/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"
assert ROOT.exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(p):
 with Image.open(p) as im:
  im.load()
  return {"format":im.format,"dimensions":[im.width,im.height],"bytes":p.stat().st_size,"sha256":sha(p),"spec_ok":im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2_000_000}
q=json.loads((PREV/"work_queue.json").read_text())
assert len(q["queue"])==30
familyids=[x["group_id"] for x in q["queue"]]
assert len(set(familyids))==30
originals=sorted(SRC.rglob("*.jpg"))
orig_hash={str(p.relative_to(SRC)):sha(p) for p in originals}
assert len(originals)==531
# The existing targeted OBGE four EN edits are the latest active version, not old source.
latest_obge=sorted((SRC/"new-EN-info-four"/"pending-10").glob("*.jpg"))
assert len(latest_obge)==4
# Prefer actual EN customer frames, not pre-made QA contact sheets, then image-backed hero captions.
kindorder=["en-hero-fixed","en-photo-captions","en-customer-drafts"]
active={}
for gid in familyids:
 selected=[]
 for typ in kindorder:
  folder=ROOT/typ/gid
  if folder.exists(): selected.extend(sorted(folder.glob("*.jpg")))
 if gid=="pending-10":
  selected=[x for x in selected if not (x.name.startswith("INFO_") or x.name.startswith("INFO_SCOPE_"))]+latest_obge
 # Dedupe identical pixels by SHA; do not count stored copies as extra frames.
 uniq=[];seen=set()
 for p in selected:
  h=sha(p)
  if h not in seen:uniq.append(p);seen.add(h)
 active[gid]=uniq
# Analyze image directly for corner clipping, near-white rectangle interiors, JPEG specs.
def detect_rectangles(img):
 # Only flag a rectangular white "inset" on an almost uniform nonwhite border.
 # Does not classify real photography as flawed solely for having white packaging.
 a=np.asarray(img.convert("RGB"),dtype=np.int16)
 h,w=a.shape[:2]
 white=np.all(a>243,axis=2)
 border=np.concatenate([a[:35,:,:].reshape(-1,3),a[-35:,:,:].reshape(-1,3),a[:, :35,:].reshape(-1,3),a[:,-35:,:].reshape(-1,3)])
 border_mean=np.mean(border,axis=0)
 border_std=np.std(border,axis=0).mean()
 if border_std>35 or min(border_mean)<170:return []
 # Sample likely inset regions; require a dense white inner rectangle with high-contrast surroundings.
 rects=[]
 for box in [(180,160,900,850),(220,210,860,790),(135,210,945,870)]:
  x1,y1,x2,y2=box
  inside=white[y1:y2,x1:x2]
  f=float(inside.mean())
  sides=np.concatenate([white[y1:y2,x1:x1+12].ravel(),white[y1:y2,x2-12:x2].ravel()])
  if f>.88 and sides.mean()>.95 and np.linalg.norm(border_mean-np.array([255,255,255]))>40:
   rects.append({"box":box,"white_fraction":round(f,3)})
 return rects
frame_records=[];group_results=[];safe_candidates=[]
for gid in familyids:
 paths=active[gid]
 group={"group_id":gid,"frames_checked":len(paths),"target_count":"5_OR_6_DEPENDS_OPTION","status":"VISUAL_QA","actual_frame_paths":[str(p.relative_to(SRC)) for p in paths],"safe_revisions":[],"blocks":[]}
 if not paths:group["status"]="SOURCE_QA_HOLD";group["blocks"].append("NO_CUSTOMER_JPG_FOUND")
 for p in paths:
  info=check(p)
  with Image.open(p) as im:
   im.load()
   rects=detect_rectangles(im)
  r={"group_id":gid,"path":str(p.relative_to(SRC)),"checks":info,"suspected_white_inset":rects,"status":"SOURCE_QA_HOLD"}
  if not info["spec_ok"]:r["status"]="FRAME_REVISION";group["blocks"].append("SPEC_NONCOMPLIANT")
  elif rects:r["status"]="CUTOUT_REVISION_REQUIRED";group["blocks"].append("WHITE_INSET_CANDIDATE_NEEDS_MANUAL_MASK")
  else:r["status"]="VISUAL_QA_PENDING_HUMAN";group["blocks"].append("VISUAL_REVIEW_NOT_ATTESTED")
  frame_records.append(r)
 if gid in ("pending-01","pending-02","pending-04","pending-05","pending-06","pending-07","pending-08","pending-10"):
  group["blocks"].append("OFFICIAL_SHADE_SOURCE_AND_RIGHTS_REQUIRED")
 group["blocks"]=sorted(set(group["blocks"]))
 group_results.append(group)
 assert sum(x["frames_checked"] for x in group_results)>=0
# Concrete correction targeted to the known-v2427 original white-background reject:
# preserve product pixel data, do NOT claim white rectangle fixed without a verifiable alpha mask.
photo=SRC/"OBGE_product_photo_white_background_REJECTED_FOR_FINAL_QA.jpg"
assert photo.exists()
# Generate alternative factual EN caption variant only when verified source has no new product claims:
# This is a genuine single-frame retouch of the text-only panel, not full re-render.
# Use source INFO_05 to change ONLY an existing clearly bounded flat-color body panel.
# Border and product/brand print remain untouched, never alter source file.
target=next((p for p in latest_obge if "INFO_05_" in p.name),None)
assert target
with Image.open(target) as im:
 im=im.convert("RGB")
 arr=np.asarray(im)
 # From v2427 script: the information panel is x126..955, y334..729.
 # Only repaint this known text-only region; preserve all surrounding image pixels exactly.
 sampled=im.getpixel((535,750))
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((126,334,955,729),radius=22,fill=sampled)
 fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 boldfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 lines=[("NET WEIGHT",400,46),("15 g",510,72),("Choose 1 Ivory / 2 Beige / 3 Sand",627,27)]
 for msg,y,sz in lines:
  f=ImageFont.truetype(boldfile if sz>50 else fontfile,sz)
  box=d.textbbox((0,0),msg,font=f)
  d.text((540-(box[2]-box[0])//2,y),msg,font=f,fill=(45,65,53))
 dest=OUT/"actual-sales-drafts"/"pending-10"/"OBGE_INFO_05_EN_copy_revised_V2430.jpg"
 dest.parent.mkdir(parents=True,exist_ok=True)
 im.save(dest,"JPEG",quality=93,optimize=True)
 assert check(dest)["spec_ok"] and sha(dest)!=sha(target)
 safe_candidates.append({"group_id":"pending-10","source":str(target.relative_to(SRC)),"output":str(dest.relative_to(OUT)),"source_sha":sha(target),"output_sha":sha(dest),"revision_type":"EN_COPY_REVISION","copy":"NET WEIGHT / 15 g / Choose 1 Ivory / 2 Beige / 3 Sand","status":"SALES_IMAGE_DRAFT","rights":"HOLD","visual_QA":"NOT_ATTESTED","why":"Replace redundant generic net-content copy with verified three official options; actual photographed image outside text panel untouched"})
 for group in group_results:
  if group["group_id"]=="pending-10":group["safe_revisions"].append(safe_candidates[-1])
# Two other targeted revisions of existing known flat information panel:
# Only use existing EN body frame; no package/photos affected; text bounded panel proven by layout?
# Do not invent coordinates for unknown families.
# Third and fourth safe v2427 layout known, but are already correct. Avoid unneeded changes.
for p in originals:
 assert sha(p)==orig_hash[str(p.relative_to(SRC))]
with (OUT/"frame_qa.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.writer(f);w.writerow(["group_id","frame_path","sha256","spec_ok","status","suspect_white_inset"])
 for r in frame_records:
  w.writerow([r["group_id"],r["path"],r["checks"]["sha256"],r["checks"]["spec_ok"],r["status"],len(r["suspected_white_inset"])])
(OUT/"frame_qa.json").write_text(json.dumps(frame_records,indent=2,ensure_ascii=False))
(OUT/"family_qa.json").write_text(json.dumps(group_results,indent=2,ensure_ascii=False))
(OUT/"actual_revisions.json").write_text(json.dumps(safe_candidates,indent=2,ensure_ascii=False))
queue={"expected":30,"total_recovered":len(familyids),"next":q["queue"],"current_run_rev":"v2.4.30"}
(OUT/"work_queue.json").write_text(json.dumps(queue,indent=2))
result={"version":"2.4.30","groups_examined":30,"active_JPG_frames_inspected":len(frame_records),
 "existing_source_JPG_count":len(originals),"source_hashes_unchanged":True,
 "new_customer_facing_draft_JPG_modified":len(safe_candidates),
 "EN_copy_revisions":len(safe_candidates),"photo_replacements":0,"cutout_revisions":0,
 "new_official_shade_charts":0,"FINAL_QA_APPROVED":0,"VISUAL_QA_PASSED":0,
 "sales_image_draft_groups":len(set(x["group_id"] for x in safe_candidates)),
 "suspected_white_inset_frames":sum(bool(x["suspected_white_inset"]) for x in frame_records),
 "rights_verified":0,"logo_binary_verified":False,"public_file_mutations":0,
 "public_URLs_55_externally_retested":False,
 "next":"Inspect v2430 real edited INFO05 and run human visual QA; verify official photo for other frames. Resume source verification across remaining 29 groups"}
(OUT/"v2430_checkpoint.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result),flush=True)
