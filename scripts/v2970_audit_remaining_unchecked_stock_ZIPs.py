#!/usr/bin/env python3
"""v2970: Actually open/check pending source archives NOT audited by v2968.

Only JSON manifests written on public QA branch. No unlicensed image files copied,
generated or exposed beyond previously present user assets. Never approves retail.
"""
from pathlib import Path
from collections import defaultdict, Counter
import io, json, re, hashlib, zipfile
from PIL import Image, ImageStat

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106"
BASE=ROOT/"qa-review/v2966-30-family-post-production-evidence-and-restart-ledger-20261106/manifest.json"
PREV=ROOT/"qa-review/v2968-30-family-real-zip-integrity-and-no-repeat-gate-20261106/manifest.json"
SECURITY=ROOT/"qa-review/v2969-public-GitHub-QA-visibility-and-product-provenance-gate-20261106/manifest.json"
V2940=ROOT/"qa-review/v2940-four-final-source-gaps-photo-archive-integrity-and-approval-gate/manifest.json"

def sha(data):return hashlib.sha256(data).hexdigest()
def phash64(image):
    pixels=list(image.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join("1" if pixels[y*9+x]>pixels[y*9+x+1] else "0"
                   for y in range(8) for x in range(8))
def distance(a,b):return sum(x!=y for x,y in zip(a,b))
def check_archive(path):
    ret={"archive":path,"exists":False,"zip_CRC_pass":False,
         "JPG_files":[],"PNG_files":[],"other_images":[],
         "other_entries":0,"errors":[]}
    p=ROOT/path
    if not p.is_file():
        ret["errors"].append("ARCHIVE_PATH_MISSING")
        return ret
    ret["exists"]=True
    ret["archive_SHA256"]=sha(p.read_bytes())
    ret["archive_size_bytes"]=p.stat().st_size
    try:
        with zipfile.ZipFile(p) as z:
            bad=z.testzip()
            if bad:ret["errors"].append("CRC_FAILURE:"+bad)
            else:ret["zip_CRC_pass"]=True
            for entry in z.infolist():
                if entry.is_dir():continue
                ext=Path(entry.filename).suffix.lower()
                if ext not in (".jpg",".jpeg",".png",".webp"):
                    ret["other_entries"]+=1
                    continue
                try:
                    data=z.read(entry.filename)
                    with Image.open(io.BytesIO(data)) as image:
                        image.load()
                        size=list(image.size)
                        img_format=image.format
                        hash64=phash64(image)
                        gray=image.convert("L").resize((32,32))
                        stat=ImageStat.Stat(gray)
                        contrast=round(stat.stddev[0],1)
                    rec={
                        "name":entry.filename,"bytes":len(data),
                        "SHA256":sha(data),"dimensions":size,"format":img_format,
                        "dHash64":hash64,"gray_stddev":contrast,
                        "is_small_1080_JPEG":img_format=="JPEG" and size==[1080,1080] and len(data)<2000000
                    }
                    if ext in (".jpg",".jpeg"):ret["JPG_files"].append(rec)
                    elif ext==".png":ret["PNG_files"].append(rec)
                    else:ret["other_images"].append(rec)
                except Exception as e:
                    ret["errors"].append("INVALID_IMAGE:"+entry.filename+" "+type(e).__name__)
    except (zipfile.BadZipFile, OSError, RuntimeError) as e:
        ret["errors"].append("ZIP_UNREADABLE:"+type(e).__name__+": "+str(e)[:150])
    return ret

def audit():
    if OUT.exists():raise SystemExit("v2970 already exists; resume from saved report instead.")
    base=json.loads(BASE.read_text(encoding="utf-8"))
    previous=json.loads(PREV.read_text(encoding="utf-8"))
    security=json.loads(SECURITY.read_text(encoding="utf-8"))
    old2940=json.loads(V2940.read_text(encoding="utf-8"))
    if security["evidence"]["repo_visibility"]!="public":raise RuntimeError("Repo classification mismatch")
    completed=set(previous["tech_pass_five_JPG_families"])
    if len(completed)!=6:raise RuntimeError("Unexpected v2968 coverage; prevent duplicate work.")
    all_rows=base["family_lanes"]
    if len(all_rows)!=30:raise RuntimeError("30-family baseline mismatch")
    already=completed|{"pending-20"}
    # pending-24 had a newer 5-image verified archive than the early 4-image row.
    upgrades={"pending-24":next(q["verified_archive"] for q in old2940["other_verified_families"] if q["family"]=="pending-24")["path"]}
    results={}
    across=defaultdict(list)
    examined_count=0
    for row in all_rows:
        family=row["family_id"]
        if family in already:continue
        p=upgrades.get(family,row.get("existing_archive_locator"))
        if not p:
            results[family]={"product":row["product"],"state":"NO_ARCHIVE_VARIANT_EDITION_HOLD",
                             "previous_stage":row["production_stage"],
                             "next_action":row.get("next_action")}
            continue
        result=check_archive(p)
        photos=result["JPG_files"]
        pngs=result["PNG_files"]
        examined_count+=len(photos)+len(pngs)+len(result["other_images"])
        hashes=Counter(x["SHA256"] for x in photos)
        dupe=[{"same_SHA256":k,"count":v} for k,v in hashes.items() if v>1]
        similar=[]
        for i in range(len(photos)):
            for j in range(i+1,len(photos)):
                if photos[i]["SHA256"]==photos[j]["SHA256"]:continue
                hd=distance(photos[i]["dHash64"],photos[j]["dHash64"])
                if hd<=5:
                    similar.append({"files":[photos[i]["name"],photos[j]["name"]],"hamming":hd,
                                    "classification":"MANUAL_REVIEW_ONLY_NOT_CONFIRMED_COPY"})
        for im in photos:
            across[im["SHA256"]].append({"family":family,"file":im["name"]})
        invalid=[x["name"] for x in photos if not x["is_small_1080_JPEG"]]
        if not result["exists"] or not result["zip_CRC_pass"]:status="ARCHIVE_CORRUPT_OR_MISSING"
        elif family=="pending-08":
            # 20 shade JPG + 20 alpha PNG is an option reference archive, not a retail 5-frame product story.
            status="PERIPERA_01_TO_20_OPTION_REFERENCES_NOT_RETAIL"
        elif invalid:status="JPG_TECH_FORMAT_OR_SIZE_FAILURE"
        elif len(photos)>=5:status="JPG_COUNT_TECH_PASS_SEMANTIC_AND_RIGHTS_PENDING"
        else:status="INSUFFICIENT_ARCHIVED_JPGS_OR_REFERENCE_NOT_FULL_SET"
        result.update({
            "product":row["product"],"status":status,
            "previous_stage":row["production_stage"],
            "JPG_count":len(photos),"PNG_count":len(pngs),
            "invalid_JPGs":invalid,
            "same_byte_duplicates":dupe,
            "visually_similar_hash_candidates":similar,
            "source_photo_5_scene_count_proven":False,
            "safety_release":"NOT_APPROVED_RIGHTS_STOCK_MK",
            "next_action":row.get("next_action")
        })
        # Peripera 01-20 is a hard sales option constraint regardless of unlabeled alpha filenames.
        if family=="pending-08":
            filenames=[x["name"] for x in photos+pngs]
            shade_hits=sorted(set(int(m.group(1)) for name in filenames
                     for m in re.finditer(r"(?i)(?:shade|option|color|no)[-_ .]*(0[1-9]|1[0-9]|20|2[1-6])\b",name)))
            result["observed_explicit_shade_name_numbers"]=shade_hits
            result["unwanted_shades_21_to_26_in_file_names"]=[x for x in shade_hits if x>20]
            result["option_mapping_requires_physical_edition_verification"]=True
        results[family]=result
    cross_family=[{"SHA256":hash_, "references":list_} for hash_,list_ in across.items()
                  if len({x["family"] for x in list_})>1]
    # The follow-on priority is new actionable triage rather than reprocessing v2968 six known-good source groups.
    needs=[
        {"family":family,"state":v["status"] if "status" in v else v.get("state"),
         "immediate":(
             "Resolve missing archive or wrong edition from existing source ledger; avoid image duplication."
             if v.get("status")=="ARCHIVE_CORRUPT_OR_MISSING" or v.get("state")=="NO_ARCHIVE_VARIANT_EDITION_HOLD"
             else "Inspect only specific bad JPG and reuse other verified bytes."
             if v.get("invalid_JPGs")
             else "Compare only listed near-duplicate frames against exact physical edition; keep archive unchanged."
             if v.get("visually_similar_hash_candidates")
             else "Clear product rights and stock/MK, no new source search."
         )}
        for family,v in results.items()
    ]
    summary={
      "version":"v2970","project":"82SKU 41 families, 30 pending stock source QA",
      "based_on":["v2966","v2968","v2969"],
      "prior_archives_skipped_without_rechecking":sorted(already),
      "pending_families_not_previously_reaudited":len(results),
      "source_ZIP_or_option_archives_attempted":sum(bool(row.get("archive")) for row in results.values()),
      "actual_JPG_PNG_files_decoded_in_newly_checked_archives":examined_count,
      "state_counts":dict(Counter(x.get("status",x.get("state")) for x in results.values())),
      "cross_family_exact_duplicate_blob_hashes":cross_family,
      "release_status":"ALL_NEW_RETAIL_APPROVALS_HOLD_NOT_AUTHORITATIVE_STOCK_RIGHTS_MK",
      "no_new_photo_binary_copied":True,
      "no_prior_files_modified":True,"legacy_published_families_preserved":11,
      "legacy_verified_public_URLs_preserved":55,
      "new_render_approved_URLs":0,"new_JPG_created":0,
      "public_qa_branch_visibility":"PUBLIC_DO_NOT_UPLOAD_NEW_UNLICENSED_BINARY",
      "results":results,"next_queue":needs,
      "no_final_spreadsheet_shared":True
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
    (OUT/"new-prioritized-source-gates.json").write_text(json.dumps(needs,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"version":"v2970","ZIP_sources":summary["source_ZIP_or_option_archives_attempted"],
      "decoded":examined_count,"state_counts":summary["state_counts"],
      "cross_family_duplicate_hashes":len(cross_family),"new_retail":0},ensure_ascii=False))
if __name__=="__main__": audit()
