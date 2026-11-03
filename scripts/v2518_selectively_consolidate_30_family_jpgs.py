#!/usr/bin/env python3
"""Consolidate 30-family genuine Shopee image QA candidates, without regenerating.
Read baseline v2444 146 reusable JPEGs, and ONLY targeted verified replacements:
- pending-10 all five replaced: old wrong physical product (beige round vs true dark square 15g)
- pending-03 frame 04: repaired broken Hangul shade card
- pending-04 frame 04: corrected mini shade option names
- pending-18 frame 05: distinct tone-up/sebum facts
- pending-27 append three genuine bottle/gallery frames to old retained one.
Result is 149 physically preserved QA-only JPEG candidates, pending-27 has four, not five.
Never write public/images, merchant spreadsheets or assert sales approval.
"""
from pathlib import Path
import subprocess,shutil,hashlib,io,json
from PIL import Image,ImageOps,ImageDraw,ImageFont
BASE=Path("/tmp/v2518-baseline/reusable-customer-JPG-candidates")
assert BASE.is_dir()
OUT=Path("v2518-30family-selective-consolidation")
FILES=OUT/"review-JPG-by-family";FILES.mkdir(parents=True,exist_ok=True)
def gitshow(branch,path):
 return subprocess.run(["git","show",f"origin/{branch}:{path}"],check=True,stdout=subprocess.PIPE).stdout
def check(raw,source):
 image=Image.open(io.BytesIO(raw));image.load()
 assert image.format=="JPEG" and image.size==(1080,1080) and len(raw)<2000000,(source,image.format,image.size,len(raw))
 return hashlib.sha256(raw).hexdigest()
records=[]
for n in range(1,31):
 family=f"pending-{n:02d}"
 source=BASE/family
 assert source.is_dir(),f"Missing baseline family: {family}"
 dest=FILES/family;dest.mkdir(parents=True,exist_ok=True)
 for jpg in sorted(source.glob("*.jpg")):
  data=jpg.read_bytes();digest=check(data,str(jpg))
  shutil.copy2(jpg,dest/jpg.name)
  records.append({"family":family,"slot":int(jpg.name.split("_")[0]),"file":str((dest/jpg.name).relative_to(OUT)),"sha256":digest,"origin":"v2444-retained", "replaced":False})
def replace(family,slot,branch,srcpath,reason):
 dest=FILES/family;raw=gitshow(branch,srcpath);sha=check(raw,srcpath)
 old=[r for r in records if r["family"]==family and r["slot"]==slot]
 if old:
  assert len(old)==1, (family,slot,len(old))
  (OUT/old[0]["file"]).unlink()
  records.remove(old[0])
 name=f"{slot:02d}_SOURCE_QA_{branch.split('-v')[-1]}_{Path(srcpath).name}"
 new=dest/name;new.write_bytes(raw)
 records.append({"family":family,"slot":slot,"file":str(new.relative_to(OUT)),"sha256":sha,"origin":branch,"original_file":srcpath,"replaced":True,"reason":reason})
for slot,path in enumerate(["01-original-open-compact.jpg","02-original-product-and-texture.jpg","03-original-model-with-cushion.jpg","04-original-3shade-chart.jpg","05-15g-verified-product-facts.jpg"],1):
 replace("pending-10",slot,"production-assets-v2511-obge-homme-15g-corrected",path,"OLD_PRODUCT_REJECTED_wrong_beige_round_cover_cushion")
replace("pending-03",4,"production-assets-v2513-missha-bb-legible","04-stock-shade-names-legible.jpg","Fix broken Hangul glyph on old version")
replace("pending-04",4,"production-assets-v2500b-clio-single-shade-corrected","04-mini-shades-factual-corrected.jpg","Replace unsupported undertone descriptive text")
replace("pending-18",5,"production-assets-v2515-drg-brightening-one","05-tone-up-sebum-finish.jpg","Replace redundant net-content card")
for i,src in enumerate(["03-pouring-liquid-original-photo.jpg","04-bottle-angles-original-photo.jpg","05-package-original-photo.jpg"],2):
 # Source is official Pixelpure toner site; 01 previously passed candidate retained.
 replace("pending-27",i,"production-assets-v2466-pixelpure-toner-three",src,"Restore real product photo in place of previously quarantined wrong-layout info")
# Pending-27 ends at four slots. Do NOT claim five frames until verified fifth exists.
family_counts={f"pending-{i:02d}":len([r for r in records if r["family"]==f"pending-{i:02d}"]) for i in range(1,31)}
assert family_counts["pending-27"]==4
assert all(v==5 for k,v in family_counts.items() if k!="pending-27")
assert len(records)==149
for family in family_counts:
 family_records=[r for r in records if r["family"]==family]
 assert len(set(r["slot"] for r in family_records))==len(family_records)
# Audit strict SHA copies after all swaps, no repeated exact photo hashes within families
duplicate_content=[]
for family in family_counts:
 lst=[r for r in records if r["family"]==family]
 for i,a in enumerate(lst):
  for b in lst[i+1:]:
   if a["sha256"]==b["sha256"]:duplicate_content.append({"family":family,"a":a["file"],"b":b["file"]})
# Real preview contact sheets for visual QA, NOT user-facing marketing images.
ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
for k in range(0,30,10):
 sheet=Image.new("RGB",(400*5,385*10),"#eeeeee");d=ImageDraw.Draw(sheet)
 for row_idx,fam_idx in enumerate(range(k+1,min(k+10,30)+1)):
  family=f"pending-{fam_idx:02d}"
  for col,info in enumerate(sorted([x for x in records if x["family"]==family],key=lambda x:x["slot"])):
   im=Image.open(OUT/info["file"]).convert("RGB")
   thumb=ImageOps.contain(im,(365,344))
   x=col*400+(400-thumb.width)//2;y=row_idx*385+8
   sheet.paste(thumb,(x,y))
   d.text((col*400+18,row_idx*385+353),family+" "+str(info["slot"]),font=ft,fill="#222222")
 sheet.save(OUT/f"contact-families-{k+1:02d}-{min(k+10,30):02d}.jpg",quality=80,optimize=True)
report={"version":"v2518","date":"2026-11-04","source_branch":"production-assets-v2444-reviewed-146-and-quarantine-4",
"latest_source_branches":["production-assets-v2511-obge-homme-15g-corrected","production-assets-v2513-missha-bb-legible","production-assets-v2500b-clio-single-shade-corrected","production-assets-v2515-drg-brightening-one","production-assets-v2466-pixelpure-toner-three"],
"physical_jpg_count":len(records),"pending_families":30,"family_counts":family_counts,
"exact_sha_duplicates":duplicate_content,"individual_frames":sorted(records,key=lambda r:(r["family"],r["slot"])),
"quarantined_v2444_pending27_source_frames_kept_excluded":4,"known_wrong_old_pending10_frames_kept_excluded":5,
"repeated_existing_product_jpg_generation":0,
"public_url_modified":0,"existing_55_verified_public_urls_preserved":True,
"excel_or_spreadsheet_created":False,"final_sales_ready":False,
"per_family_hold":{f"pending-{n:02d}":"PENDING_MK_ORIGINAL_LOGO_RIGHTS_PHYSICAL_STOCK_AND_VISUAL_QA" for n in range(1,31)},
"critical_missing":{"pending-27":"One independent verified fifth frame is still missing; only four QA candidates present"},
"notes":["QA-only selected originals and corrected candidates. Source-photo rights NOT validated.","Do not publish or translate before full-frame visual approval and brand logo bytes.","Color swatches must be authentic brand sourced, no image generator color inference."]}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"jpg_count":len(records),"families":30,"not_five":{k:v for k,v in family_counts.items() if v!=5},"duplicate_sha_pairs":len(duplicate_content),"replacement_count":sum(r["replaced"] for r in records)}))
