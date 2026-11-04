#!/usr/bin/env python3
"""v2596 append two genuine Dr.G 50ml SUN PLUS candidate JPGs to definitive
v2593 156-image QA corpus without touching source bytes or public images.
No physical stock/photo rights signoff; no final Excel.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
SOURCE=Path("v2596-source")
BASE=Path("v2596-base/review-JPG-by-family/pending-18")
OUT=Path("v2596-drg-50ml-two-JPG-delta-QA");OUT.mkdir(exist_ok=True)
m=json.loads((SOURCE/"manifest.json").read_text())
assert m["version"]=="v2595" and m["distinct_candidates"]==2
assert m["photos_downloaded"]==2
new=[r for r in m["sources"] if r["status"]=="DISTINCT_REAL_50ML_PHOTO_QA_ONLY"]
assert len(new)==2
old=sorted(BASE.glob("*.jpg"))
assert len(old)==5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for slot,s in zip((3,5),new):
 src=SOURCE/s["saved_file"]
 originals=[p for p in old if int(p.name[:2])==slot]
 assert len(originals)==1
 assert src.is_file() and sha(src)==s["sha256"]
 photo=Image.open(src);photo.load()
 assert photo.format=="JPEG" and photo.size==(1080,1080) and src.stat().st_size<2_000_000
 assert sha(src)!=sha(originals[0])
 saved=OUT/f"pending-18-slot{slot:02d}-SunPLUS-50ml-real-photo-QA.jpg"
 shutil.copy2(src,saved)
 assert sha(saved)==sha(src)
 rows.append({"family":"pending-18","slot":slot,"source_page":s["page"],
  "old_sha256":sha(originals[0]),"new_sha256":sha(saved),"file":saved.name,
  "commercial_photo_rights_verified":False,"physical_stock_identical_edition_verified":False,
  "status":"QA_CANDIDATE_HOLD"})
assert len(rows)==2 and len(set(r["new_sha256"] for r in rows))==2
report={"version":"v2596","base_corpus_run":41764831639,"new_source_run":41765634102,
 "previous_17_QA_overlays_preserved":True,
 "new_drg_sunplus_50ml_JPGs":2,"virtual_overlay_delta_count":19,
 "previous_154_image_slots_not_rewritten":True,
 "source_156_JPG_recreated":0,
 "prior_11_published_product_groups_untouched":True,
 "old_public_55_verified_urls_changed":0,
 "new_public_urls":0,"no_XLSX_generated_or_shared":True,
 "sales_approval":False,"rights_and_own_stock_and_original_MK_logo_pending":True,
 "changed":rows}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_jpg_candidates":2,"prior_17_kept":True,
 "total_virtual_changes":19,"published":0,"xlsx":False}))
