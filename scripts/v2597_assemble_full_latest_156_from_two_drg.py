#!/usr/bin/env python3
"""v2597 final current physical review-only corpus, overlay precisely two newly
staged Dr.G 50ml Sun Plus photos onto v2593 156 originals. Verify hash for 154
untouched JPGs but do not re-encode them. Do not publish, no XLSX, no approval.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
BASE=Path("source/latest/review-JPG-by-family")
NEW=Path("source/new")
OUT=Path("v2597-latest-156-JPG-19QA-deltas")
DST=OUT/"review-JPG-by-family"
DST.mkdir(parents=True,exist_ok=True)
prev=json.loads(Path("source/latest/manifest.json").read_text())
delta=json.loads((NEW/"manifest.json").read_text())
assert prev["version"]=="v2593" and prev["latest_17_JPG_verified_and_assembled"]==17
assert delta["version"]=="v2596" and len(delta["changed"])==2
assert [(x["family"],x["slot"]) for x in delta["changed"]]==[("pending-18",3),("pending-18",5)]
fixes={(x["family"],x["slot"]):x for x in delta["changed"]}
before={(x["family"],x["slot"]):x for x in prev["files"]}
assert len(before)==156 and len(fixes)==2
for key in fixes:
 assert before[key]["source"]=="v2560-immutable",(key,before[key]["source"])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
newrows=[];unchanged=0;changed=0
for family_num in range(1,31):
 fam=f"pending-{family_num:02d}"
 p=sorted((BASE/fam).glob("*.jpg"))
 assert len(p)==(6 if family_num in (1,2,4,5,6,7) else 5)
 (DST/fam).mkdir(exist_ok=True)
 for file in p:
  slot=int(file.name[:2]);key=(fam,slot);info=before[key]
  assert sha(file)==info["sha256"]
  item=fixes.get(key)
  if item:
   src=NEW/item["file"]
   assert src.is_file() and sha(src)==item["new_sha256"]
   assert item["old_sha256"]==sha(file)
   target=DST/fam/f"{slot:02d}_v2597-REAL-50ml-SUNPLUS-QA-ONLY.jpg"
   shutil.copy2(src,target);changed+=1
   source="v2596-external-photo-rights-HOLD"
  else:
   target=DST/fam/file.name
   shutil.copy2(file,target)
   assert sha(target)==sha(file)
   unchanged+=1;source=info["source"]
  img=Image.open(target);img.load()
  assert img.format=="JPEG" and img.size==(1080,1080) and target.stat().st_size<2_000_000
  newrows.append({"family":fam,"slot":slot,"file":str(target.relative_to(OUT)),
   "sha256":sha(target),"source":source})
assert len(newrows)==156 and unchanged==154 and changed==2
assert len({(r["family"],r["slot"]) for r in newrows})==156
manifest={"version":"v2597","base_run":41764831639,"new_photo_run":41765754599,
 "total_JPGs":156,"product_families":30,
 "previous_17_fixes_byte_preserved":True,"new_exact_50ml_DrG_source_photo_slots":[3,5],
 "changed_current_corpus_JPG":2,"unchanged_previous_corpus_JPG":154,
 "changes_since_original_v2560":19,"previous_55_public_urls_modified":0,
 "no_new_public_url":True,"spreadsheets_created_or_shared":False,
 "customer_sales_image_license_verified":False,
 "actual_owned_stock_edition_human_verified":False,
 "original_round_MK_logo_verified":False,
 "human_final_visual_QA_approved":False,"commercial_release_ready":False,
 "known_inventory_hold":"pending-12 15G inventory vs brand official 15mL; remain blocked until physical stock check",
 "files":newrows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total_JPGs":156,"changed":2,"unchanged":154,
 "cumulative_QA_deltas":19,"published":0,"xlsx":False}))
