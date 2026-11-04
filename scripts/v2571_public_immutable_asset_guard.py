#!/usr/bin/env python3
"""v2571 non-mutating guard for existing public assets. Freeze every image that
existed before new pending family production. New image URLs require manual
release approval and are not created by this script. Protect source assets from
future accidental deletion/overwrite without rechecking 156 pending QA JPGs.
"""
import subprocess,json,hashlib
from pathlib import Path
BASE="a3f64edc571ca5bbe29b4ae75dcc5fe4410bab25"
OUT=Path("v2571-live-asset-lock");OUT.mkdir(exist_ok=True)
def tracked(ref):
 raw=subprocess.check_output(["git","ls-tree","-r","-z",ref,"public/images"])
 assets={}
 for item in raw.split(b"\0"):
  if not item:continue
  meta,name=item.split(b"\t",1)
  mode,kind,sha=meta.decode().split(" ")
  path=name.decode()
  if kind=="blob":assets[path]=sha
 return assets
before=tracked(BASE)
current=tracked("HEAD")
assert len(before)>=55,(len(before),"Baseline missing existing public images")
changed=[p for p,sha in before.items() if current.get(p)!=sha]
added=[p for p in current if p not in before]
report={"version":"v2571","source_immutable_baseline_commit":BASE,
 "original_public_files":len(before),"same_existing_blob_sha":len(before)-len(changed),
 "previous_public_file_modifications_or_deletions":changed,
 "new_public_files":added,
 "protected_scope":"all pre-existing public/images, includes verified 55 URLs",
 "main_history_mutated":False,"pending_156_QA_images_rechecked":False,
 "original_customer_jpgs_recreated":0,"existing_public_55_verified_URLs_changed":len(changed),
 "excel_created_or_shared":False,
 "status":"PASS_NO_EXISTING_PUBLIC_ASSET_MUTATIONS" if not changed and not added else "DENY_NEW_OR_CHANGED_PUBLIC_FILES_UNLESS_RELEASE_APPROVED",
 "note":"A workflow failure is a CI warning, not an atomic block on pushes; GitHub branch protection must be configured separately to enforce merges."}
(OUT/"public-image-immutable-baseline-check.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"baseline_existing_public_assets":len(before),"existing_changed_or_missing":len(changed),"new_unapproved_paths":len(added),"status":report["status"]}))
assert not changed,changed
assert not added,added
