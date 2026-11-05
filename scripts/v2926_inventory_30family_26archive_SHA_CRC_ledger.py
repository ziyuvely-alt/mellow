#!/usr/bin/env python3
"""v2926 reconcile all 30 pending inventory-image groups using existing immutable QA artifacts.
Single pass ZIP SHA256/CRC validation; no old files changed, no sales approval, no spreadsheet.
"""
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
import json,time,collections
Q=Path("qa-review")
SOURCES={
 "v2918":Q/"v2918-two-family-byte-identical-five-photo-internal-zip-QA/manifest.json",
 "v2920":Q/"v2920-six-incomplete-stock-groups-real-original-photo-bytes-internal-ZIP/manifest.json",
 "v2922":Q/"v2922-five-legacy-stock-family-original-25photo-internal-only-archive-ZIP/manifest.json",
 "v2923":Q/"v2923-nine-other-pending-family-45archived-source-photo-zip-and-contact-QA/manifest.json",
 "v2924":Q/"v2924-eight-unpacked-stock-family-3five-photo-20option-4clio-source-QA/manifest.json",
 "v2925":Q/"v2925-peripera-01to20-40immutable-JPG-PNG-and-alpha-native-QA/manifest.json"
}
OUT=Q/"v2926-30family-26sourcezip-qa-state-and-next-action-ledger"
assert not OUT.exists()
M={key:json.loads(path.read_text(encoding="utf-8")) for key,path in SOURCES.items()}
BASE=Q/"v2925-peripera-01to20-40immutable-JPG-PNG-and-alpha-native-QA/stock30-incremental-state-v2925.json"
S=json.loads(BASE.read_text(encoding="utf-8"))
assert S["version"]=="v2925" and len(S["families"])==30
for key,manifest in M.items(): assert manifest["version"]==key,key
assert all([M["v2918"]["previous_55_published_URLs_preserved"],M["v2920"]["existing_55_public_URLs_unchanged"],M["v2922"]["existing_55_public_URLs_unchanged"],M["v2923"]["prior_55_published_URLs_unchanged"],M["v2924"]["existing_55_verified_URLs_unchanged"],M["v2925"]["preexisting_55_public_URLs_preserved"]])
rows={}; verified=[]
def checkzip(path,hash_value,members):
 p=Path(path)
 assert p.is_file(),("missing existing archive",str(p))
 digest=sha256(p.read_bytes()).hexdigest()
 assert digest==hash_value,("archive SHA mismatch",str(p))
 with ZipFile(p,"r") as z:
  assert len(z.infolist())==members,(p,len(z.infolist()),members)
  assert z.testzip() is None,("ZIP CRC failure",str(p))
 return {"path":str(p),"sha256":digest,"member_count":members,"bytes":p.stat().st_size}
def record(fam,kind,count,path=None,h=None,members=0,blockers=None):
 assert fam not in rows and fam in S["families"],fam
 val=checkzip(path,h,members) if path else None
 rows[fam]={
   "family":fam,"product":S["families"][fam]["product"],"category":kind,
   "valid_existing_product_source_JPGs":count,
   "internal_QA_archive":val,"remaining_photo_source_slots":max(0,5-count) if kind=="PARTIAL_PHOTO_ARCHIVE" else None,
   "right_to_use_in_marketplace":"NOT_VERIFIED","actual_held_inventory_edition":"NOT_VERIFIED",
   "true_MK_logo_and_claims":"NOT_VERIFIED","sale_approved":False,
   "blockers":blockers or ["Exact stock edition, image commercial rights and original MK need verification"]}
 if val:verified.append(val)
for x in M["v2918"]["results"]:
 record(x["family"],"FIVE_PHOTO_ARCHIVE",5,x["internal_QA_zip"],x["internal_QA_zip_sha256"],5)
for x in M["v2920"]["results"]:
 n=x["actual_original_source_jpgs_in_zip"]
 assert 5-n==x["five_source_target_shortfall"] and n in (3,4)
 record(x["family"],"PARTIAL_PHOTO_ARCHIVE",n,x["zip_path"],x["zip_sha256"],n,["Need "+str(5-n)+" distinct original photos","Rights, physical stock and MK unverified"])
for x in M["v2922"]["results"]:
 record(x["family"],"FIVE_PHOTO_ARCHIVE",5,x["zip_path"],x["zip_sha256"],5)
for x in M["v2923"]["results"]:
 record(x["family"],"FIVE_PHOTO_ARCHIVE",5,x["zip_path"],x["zip_sha256"],5)
for x in M["v2924"]["full_reused_5photo_archives"]:
 record(x["family"],"FIVE_PHOTO_ARCHIVE",5,x["internal_zip"],x["zip_sha256"],5,x["blockers"])
for x in M["v2924"]["mixed_option_sources"]:
 record(x["family"],"OPTIONS_PRODUCT_IDENTITY_HOLD",0,blockers=x["blockers"])
 rows[x["family"]]["mixed_photo_reference_count"]=x["reference_count"]
v=M["v2925"]
record("pending-08","PERIPERA_LEGACY_SHADE_EDITION_HOLD",0,v["ZIP_path"],v["ZIP_sha256"],40,
 ["20 legacy shade JPG and alpha PNG pairs; 26AD equivalence unverified",
  "Low-resolution alpha: 12/14/20; additional shade issues 12/13/14/18/19",
  "No 21-26 shade image creation"])
assert len(rows)==30 and set(rows)=={f"pending-{i:02d}" for i in range(1,31)}
c=collections.Counter(x["category"] for x in rows.values())
assert c=={"FIVE_PHOTO_ARCHIVE":19,"PARTIAL_PHOTO_ARCHIVE":6,"OPTIONS_PRODUCT_IDENTITY_HOLD":4,"PERIPERA_LEGACY_SHADE_EDITION_HOLD":1},c
assert len(verified)==26,len(verified)
assert sum(x["remaining_photo_source_slots"] or 0 for x in rows.values())==11
assert sum(x["valid_existing_product_source_JPGs"] for x in rows.values())==114
assert all(not x["sale_approved"] for x in rows.values())
for fam,row in rows.items():
 st=S["families"][fam]
 st["v2926_inventory_ledger_category"]=row["category"]
 st["v2926_verified_internal_archive"]=row["internal_QA_archive"]["path"] if row["internal_QA_archive"] else None
 st["v2926_unresolved_photo_source_slots"]=row["remaining_photo_source_slots"]
 st["v2926_rights_edition_release_state"]="HOLD"
 # prior detailed QA status remains authoritative and untouched
ledger={
 "version":"v2926","baseline":"v2925","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "total_pending_families_checked":30,"existing_published_families_preserved":11,
 "existing_verified_public_urls_preserved":55,
 "sha256_and_ZIP_CRC_verified_archives":26,
 "five_source_archived_family_count":19,
 "three_or_four_source_archived_family_count":6,
 "mixed_option_holds":4,"peripera_legacy_shade_holds":1,
 "reused_original_JPGs_in_25_product_photo_archives":114,
 "peripera_legacy_original_JPG_PNG_files":40,
 "remaining_photo_slots_in_six_partial_families":11,
 "new_original_photos_generated":0,"new_retail_approvals":0,
 "new_public_URLs":0,"prior_source_archives_changed":0,
 "final_spreadsheet_shared":False,
 "next_unblocked_work_batches":[
  {"priority":1,"work":"Fill 11 missing original photo scenes where reliable official rights-cleared matches are available",
   "families":[x for x in sorted(rows) if rows[x]["category"]=="PARTIAL_PHOTO_ARCHIVE"]},
  {"priority":2,"work":"Separate authentic shades/product-set editions for four mixed-source cushion and treatment families",
   "families":[x for x in sorted(rows) if rows[x]["category"]=="OPTIONS_PRODUCT_IDENTITY_HOLD"]},
  {"priority":3,"work":"Audit 26AD physical-stock differences and low-native 12/14/20 Peripera shades, no invented color data","families":["pending-08"]},
  {"priority":4,"work":"Rights, exact physical stock, genuine MK logo and advertising-claim clearance before any commercial release","families":"all 30"}
 ],
 "family_records":[rows[k] for k in sorted(rows)],
 "original_ZIP_integrity":[x for x in verified]
}
OUT.mkdir(parents=True)
(OUT/"manifest.json").write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
S["version"]="v2926";S["baseline"]="v2925";S["new_sales_approvals"]=0;S["new_public_URLs"]=0;S["final_spreadsheet_shared"]=False
(OUT/"stock30-incremental-state-v2926.json").write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:ledger[k] for k in ["version","total_pending_families_checked","sha256_and_ZIP_CRC_verified_archives","five_source_archived_family_count","three_or_four_source_archived_family_count","mixed_option_holds","peripera_legacy_shade_holds","remaining_photo_slots_in_six_partial_families","new_retail_approvals"]},ensure_ascii=False))
