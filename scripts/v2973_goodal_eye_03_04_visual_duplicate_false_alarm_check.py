#!/usr/bin/env python3
"""v2973 false-positive investigation for GOODAL Eye Cream 25AD frames #3 and #4.
No files other than JSON created; prior approved media not touched.
"""
import hashlib, io, json, zipfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2973-goodal-eyecream-duplicate-false-alarm-resolution-20261106"
AUDIT=ROOT/"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106/manifest.json"
SOURCES={
 3:"qa-review/v2772-goodal-obge-five-frame-photo-QA/pending-21/03-legacy-eye-area-application-REFERENCE.jpg",
 4:"qa-review/v2772-goodal-obge-five-frame-photo-QA/pending-21/04-legacy-nozzle-cream-REFERENCE.jpg"}
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    if OUT.exists():raise RuntimeError("Refuse duplicate v2973")
    v2970=json.loads(AUDIT.read_text(encoding="utf8"))
    recorded=v2970["results"]["pending-21"]
    zippath=ROOT/recorded["archive"]
    if sha(zippath.read_bytes())!=recorded["archive_SHA256"]:
        raise RuntimeError("Prior archived ZIP checksum changed")
    with zipfile.ZipFile(zippath) as z:
        originals=[x for x in z.infolist() if x.filename.lower().endswith(".jpg")]
        if len(originals)!=5:raise RuntimeError("Expected five prior JPG frames")
        payloads={i+1:z.read(originals[i]) for i in range(5)}
    matches={}
    for slot,path in SOURCES.items():
        refdata=(ROOT/path).read_bytes()
        with Image.open(io.BytesIO(refdata)) as im:
            im.load()
            if im.format!="JPEG" or im.size!=(1080,1080):raise RuntimeError("Unexpected legacy ref frame "+path)
        rec=recorded["JPG_files"][slot-1]
        if rec["SHA256"]!=sha(payloads[slot]):
            raise RuntimeError("v2970 recorded archived frame digest mismatch")
        matches[str(slot)]={
          "archived_photo":originals[slot-1].filename,
          "archived_sha256":sha(payloads[slot]),
          "existing_reference":path,
          "reference_sha256":sha(refdata),
          "exact_same_bytes":sha(refdata)==sha(payloads[slot]),
          "visual_independence_in_viewed_reference":("EYE_AREA_APPLICATION" if slot==3 else "TUBE_NOZZLE_CREAM"),
          "visual_review_source":"The actual v2772 existing QA standalone JPG was opened and visually checked; not regenerated."}
    if all(v["exact_same_bytes"] for v in matches.values()):
        status="FALSE_POSITIVE_BY_GRAYSCALE_DHASH_FRAMES_VISUALLY_DIFFERENT"
    else:
        status="SOURCE_HASH_MAPPING_NOT_IDENTICAL_NEEDS_EXACT_ZIP_3_4_VIEW"
    result={
      "version":"v2973","parent":"v2972","project":"Shopee Thumbnail Creator PRO stock",
      "family":"pending-21","product":"GOODAL Vita-C Dark Circle Eye Cream 25AD 30mL",
      "new_images_downloaded":0,"new_photo_binary_created":0,
      "old_zip_crc_verified":True,"old_zip_unchanged":True,
      "v2970_dHash_similarity_warning":"Archived frame 03 vs frame 04 grayscale Hamming distance 5",
      "source_mapping":matches,"resolution":status,
      "rights_not_proven":True,"single_vs_two_pack_not_resolved":True,
      "actual_stock_generation_not_verified":True,
      "original_MK_logo_sha256_not_verified":True,
      "new_render_urls":0,"new_retail_approvals":0,
      "previously_published_families_preserved":11,"previous_verified_urls_preserved":55,
      "next_action":"When exact source mapping passes, do not replace frame 3/4 for shape similarity; handle stock 30mL single vs twin-pack and image rights, then customer-clean MK QA.",
      "no_final_excel_shared":True
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2973","result":status,
        "exact_matches":{k:v["exact_same_bytes"] for k,v in matches.items()},
        "retail_new":0}))
if __name__=="__main__":main()
