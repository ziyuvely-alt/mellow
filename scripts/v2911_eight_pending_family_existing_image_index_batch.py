#!/usr/bin/env python3
"""v2911: one-pass non-destructive inventory of previously neglected 8 pending families.
Scan source image files already present in QA branch; produce contact sheets from existing
bytes for inspection. Never claim these are sales-approved. Do not change older assets.
"""
from pathlib import Path
from collections import defaultdict, Counter
from io import BytesIO
import json, subprocess, re, hashlib, time
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path("qa-review")
PRE=ROOT/"v2910-drg-2022-red-and-2023-moisture-sun-10-existing-image-qa"/"stock30-incremental-state-v2910.json"
OUT=ROOT/"v2911-eight-unscored-stock-family-existing-photo-index-QA"
state=json.loads(PRE.read_text(encoding="utf-8"))
assert state["version"]=="v2910" and len(state["families"])==30 and not OUT.exists()
TARGETS=["pending-20","pending-23","pending-24","pending-25","pending-27","pending-28","pending-29","pending-30"]
def list_files():
 out=subprocess.check_output(["git","ls-files","-z","qa-review","public"])
 return [Path(x.decode("utf-8")) for x in out.split(b"\0") if x]
def matching_family(p):
 parts={x.lower() for x in p.parts}
 name=p.name.lower()
 for k in TARGETS:
  if k in parts or re.search(r"(?<![a-z0-9])"+re.escape(k)+r"(?![0-9])",name):
   return k
 return None
def font(n):
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",n)
 except:return ImageFont.load_default()
def image_read(p):
 with Image.open(p) as raw:
  raw.load()
  if raw.format not in ("JPEG","PNG","WEBP"):return None
  width,height=raw.size
  if min(width,height)<350 or max(width,height)>20000:return None
  rgb=ImageOps.exif_transpose(raw).convert("RGB")
  return rgb,raw.format,[width,height]
def digest(rgb):
 gray=ImageOps.fit(ImageOps.grayscale(rgb),(9,8)).load()
 return "".join("1" if gray[x,y]>gray[x+1,y] else "0" for y in range(8) for x in range(8))
def dist(a,b):return sum(x!=y for x,y in zip(a,b))
def score(p,sz):
 s=p.as_posix().lower()
 score=sum((num if word in s else 0) for word,num in [
  ("original",18),("real",12),("firstparty",10),("manufacturer",9),
  ("photo",5),("gallery",4),("cutout",5),("1080",3),("source",2),
  ("hero",3),("product",3),("clean",2),("official",5)
 ])
 score-=sum((num if word in s else 0) for word,num in [
  ("contact",35),("comparison",30),("preview",8),("draft",12),("bad-",40),
  ("rejected",60),("quarantine",60),("unverified",20),("wrong",60),
  ("logo",6),("swatch",5),("old-",2),("duplicate",12)
 ])
 if min(sz)>=900:score+=8
 return score
def contact(family,slots):
 im=Image.new("RGB",(1080,1080),"#f6f7f8");d=ImageDraw.Draw(im)
 d.text((24,14),family.upper()+" | 8-FAMILY SOURCE PHOTO INDEX v2911",font=font(28),fill="#222222")
 d.text((24,57),"EXISTING PHOTOS ONLY  |  Internal QA, NOT marketplace assets",font=font(18),fill="#9b3535")
 for i,record in enumerate(slots):
  row,col=divmod(i,3);x=20+col*352;y=102+row*322
  d.rounded_rectangle((x,y,x+337,y+302),radius=9,fill="#ffffff",outline="#cdcdcd",width=2)
  photo=ImageOps.contain(record["image"],(323,236),Image.Resampling.LANCZOS)
  im.paste(photo,(x+169-photo.width//2,y+6+(235-photo.height)//2))
  d.text((x+12,y+250),f"{i+1:02d} {record['size'][0]}x{record['size'][1]}  {record['ext']}",font=font(14),fill="#343434")
  short=record["path"].name[:35]
  d.text((x+12,y+273),short,font=font(12),fill="#585858")
 d.text((24,1058),"Own stock edition / provenance / photo rights / original MK: not confirmed",font=font(16),fill="#a03838")
 return im

allfiles=list_files()
paths=defaultdict(list)
for p in allfiles:
 if p.suffix.lower() not in (".jpg",".jpeg",".png",".webp"):continue
 k=matching_family(p)
 if k:paths[k].append(p)
OUT.mkdir(parents=True)
records=[]
for family in TARGETS:
 candidates=[];failed=[]
 for p in paths[family]:
  try:
   tup=image_read(p)
   if tup is None:continue
   rgb,fmt,dimensions=tup
   raw_sha=hashlib.sha256(p.read_bytes()).hexdigest()
   candidates.append({"path":p,"image":rgb,"format":fmt,"size":dimensions,
    "score":score(p,dimensions),"dhash":digest(rgb),"sha":raw_sha,"bytes":p.stat().st_size})
  except Exception as e:failed.append({"path":str(p),"reason":str(e)[:95]})
 candidates.sort(key=lambda x:(-x["score"],-min(x["size"]),str(x["path"])))
 selected=[];seen_hash=set();selected_phash=[]
 for c in candidates:
  if c["sha"] in seen_hash:continue
  if any(dist(c["dhash"],d)<4 for d in selected_phash):continue
  selected.append(c);seen_hash.add(c["sha"]);selected_phash.append(c["dhash"])
  if len(selected)==9:break
 contact_path=None
 if selected:
  contact_path=OUT/(family+"-existing-real-photo-source-review-1080-INTERNAL-QA.jpg")
  items=[{"image":c["image"],"size":c["size"],"ext":c["format"],"path":c["path"]} for c in selected]
  contact(family,items).save(contact_path,"JPEG",quality=89,optimize=True,subsampling=0)
  with Image.open(contact_path) as check:assert check.size==(1080,1080) and check.format=="JPEG"
  assert contact_path.stat().st_size<2_000_000
 entry={
  "family":family,"product":state["families"][family]["product"],
  "matching_assets_in_worktree":len(paths[family]),"decodable_existing_images":len(candidates),
  "distinct_existing_sources_selected":len(selected),"decoding_errors":failed[:6],
  "contact_sheet":str(contact_path) if contact_path else None,
  "selected_original_paths":[{"path":str(c["path"]),"sha256":c["sha"],"bytes":c["bytes"],
     "native_pixels":c["size"],"format":c["format"],"source_selection_score":c["score"],
     "dhash":c["dhash"],"actual_owned_stock_verified":False,
     "photo_commercial_rights_verified":False,"authentic_original_MK_logo_verified":False,
     "sale_approved":False} for c in selected],
  "visual_label_rights_stock_check":"PENDING","retail_photo_release":"HOLD",
  "next_action":"Review contact sources for exact packaging/edition, visual scene variety and unsafe claims; obtain inventory and rights proof before release."
 }
 records.append(entry)
 st=state["families"][family]
 st.update({"last_delta_version":"v2911","sale_approved":False,
   "release_status":"EXISTING_IMAGE_REFERENCE_INDEXED_NO_SALE_RIGHTS_OR_STOCK_PROOF" if selected else "NO_LOCAL_MATCHING_SOURCE_IMAGES_IN_WORKTREE",
   "v2911_source_assets_scanned":len(paths[family]),
   "v2911_distinct_candidate_images":len(selected),
   "v2911_contact_sheet":entry["contact_sheet"],
   "latest_photo_QA_checkpoint":f"v2911 selected {len(selected)} existing distinct-ish photo candidates from {len(paths[family])} indexed image paths, internal contact review only; cannot approve until photo scene and exact stock/rights check."})
manifest={"version":"v2911","baseline":"v2910","generated_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "families_targeted":len(TARGETS),"family_record_count":len(records),
 "existing_QA_image_assets_indexed":sum(r["matching_assets_in_worktree"] for r in records),
 "existing_source_candidate_selection":sum(r["distinct_existing_sources_selected"] for r in records),
 "new_INTERNAL_QA_contact_JPGs":sum(bool(r["contact_sheet"]) for r in records),
 "new_sales_approved":0,"new_public_image_URLs":0,"old_image_bytes_changed":0,
 "old_published_11_families_untouched":True,"old_55_published_URLs_unchanged":True,
 "final_excel_shared":False,"families":records}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state["version"]="v2911";state["baseline"]="v2910";state["new_sales_approvals"]=0;state["new_public_URLs"]=0;state["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2911.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2911","families":8,"existing_indexed":manifest["existing_QA_image_assets_indexed"],
  "candidate_selected":manifest["existing_source_candidate_selection"],
  "contact_JPGs":manifest["new_INTERNAL_QA_contact_JPGs"],
  "family_counts":{r["family"]:r["distinct_existing_sources_selected"] for r in records},
  "new_sales_approvals":0},ensure_ascii=False))
