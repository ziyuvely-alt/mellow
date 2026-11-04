#!/usr/bin/env python3
"""v2656 compile previously produced QA-only JPEGs into one immutable review source.
Requires v2655 SHA provenance and zero cross-SKU alerts. No reencode/recreate.
"""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path("source")
OUT=Path("v2656-preserved-14-QA-candidates")
JPG=OUT/"review-JPG";JPG.mkdir(parents=True,exist_ok=True)
audit=json.loads((ROOT/"v2655"/"v2655-cross-sku-evidence.json").read_text())
assert audit["version"]=="v2655" and audit["candidate_files"]==14
assert audit["flagged_candidate_count"]==0
names={"v2651":"a","v2652":"b","v2653":"c"}
entries=[]
for c in audit["candidates"]:
    version=c["version"]
    src=ROOT/names[version]/c["file"]
    assert src.is_file(),src
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    assert digest==c["sha256"],c["file"]
    output=JPG/f"{version}_{c['family']}_{c['file']}"
    assert not output.exists(),output
    shutil.copy2(src,output)
    assert hashlib.sha256(output.read_bytes()).hexdigest()==digest
    with Image.open(output) as im:
        im.load()
        assert im.format=="JPEG" and im.size==(1080,1080)
    assert output.stat().st_size<2_000_000
    entries.append({"file":str(output.relative_to(OUT)),"family":c["family"],
                    "prior_artifact_version":version,"sha256":digest,
                    "bytes":output.stat().st_size,"retail_status":"QA_ONLY_UNAPPROVED"})
assert len(entries)==14
manifest={"version":"v2656","source_versions":["v2651","v2652","v2653","v2655"],
 "image_count":14,"sha256_verified":14,"cross_sku_high_similarity_alerts":0,
 "historical_source":"v2593 historical photos, not current v2647",
 "sales_ready_count":0,"image_licenses_verified":False,
 "current_v2647_frame_comparison_done":False,
 "real_stock_packaging_verified":False,
 "pending_manual_visual_qa":True,
 "published_existing_55_urls_changed":0,
 "prior_11_approved_families_changed":0,
 "final_xlsx_included":False,
 "files":entries}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
shutil.copy2(ROOT/"v2655"/"v2655-cross-sku-evidence.json",OUT/"v2655-cross-sku-evidence.json")
print(json.dumps({"preserved_original_candidate_JPGs":len(entries),
    "sha_match":len(entries),"newly_generated_artwork":0,
    "existing_public_urls_affected":0,"approved_for_sale":0},ensure_ascii=False))
