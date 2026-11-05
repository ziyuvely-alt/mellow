#!/usr/bin/env python3
"""v2846 recursive product-specific QA mapping audit.
Conservative QA evidence mapping, no image writes, no sales approval.
"""
from pathlib import Path
from collections import defaultdict
import json,re

ROOT=Path("qa-review")
OUT=ROOT/"v2846-recursive-nested-family-identity-audit"
assert not OUT.exists()
INV=json.loads(Path("/tmp/v2846-inventory-crosswalk.json").read_text())
BASE=json.loads((ROOT/"v2844-30family-product-identity-batch-QA"/"manifest.json").read_text())
assert len(INV["pending_families"])==30
stocks={row["family_id"]:row for row in INV["pending_families"]}

def scoped_objects(node, path="$", depth=0):
    if depth>12:return
    if isinstance(node,dict):
        yield path,node
        for k,v in node.items():
            if isinstance(v,(dict,list)):
                yield from scoped_objects(v,path+"."+k,depth+1)
    elif isinstance(node,list):
        for i,v in enumerate(node):
            if isinstance(v,(dict,list)):
                yield from scoped_objects(v,f"{path}[{i}]",depth+1)
def fam(obj):
    for k in ("family","pending_family","pending_family_id","product_family","inventory_family_id"):
        val=obj.get(k)
        if isinstance(val,str) and val in stocks: return val
    return None
def desc(obj):
    return " | ".join(str(obj[k]) for k in ("product","product_name","item","product_title",
                  "inventory_product","family_name","source_product_title") if isinstance(obj.get(k),str))
def mismatch(wanted,actual):
    n=wanted.lower().replace(" ","")
    a=actual.lower().replace(" ","")
    out=[]
    gift=any(s in n for s in ("기획세트","giftset","x2","×2"))
    if gift and (("mini" in a or "미니" in a) and
                 not any(s in a for s in ("giftset","기획세트","x2","×2"))):
        out.append("GIFT_SET_VS_SINGLE_MINI")
    p=re.findall(r"(?<!\d)(\d+)\s*ml\b",n)
    q=re.findall(r"(?<!\d)(\d+)\s*ml\b",a)
    if p and q and not set(p).intersection(q):out.append("ML_VOLUME_CONFLICT")
    p=re.findall(r"(?<!\d)(\d+)\s*g\b",n)
    q=re.findall(r"(?<!\d)(\d+)\s*g\b",a)
    if p and q and not set(p).intersection(q):out.append("GRAM_CONFLICT")
    return out

reports={}
newly=[]
flags=[]
for p in sorted(ROOT.rglob("manifest.json")):
    if OUT in p.parents:continue
    try:d=json.loads(p.read_text())
    except:continue
    results=[]
    top=fam(d) if isinstance(d,dict) else None
    for xpath,item in scoped_objects(d):
        family=fam(item)
        if family is None:continue
        name=desc(item)
        if not name and xpath!="$":continue
        err=mismatch(stocks[family]["family_name"],name) if name else []
        candidate={"family_id":family,"nested_json_path":xpath,
                   "candidate_name":name[:240],
                   "issues":err,
                   "status":"HOLD_EXPLICIT_PRODUCT_CONFLICT" if err else "EVIDENCE_ONLY_NOT_SALES_APPROVAL"}
        results.append(candidate)
        if err:
            flags.append({"source_file":str(p),**candidate})
    if results:
        # Duplicate linkage to the same family within one QA manifest is
        # reference evidence, not proof of multiple completed product groups.
        dedup=[]
        seen=set()
        for x in results:
            fingerprint=(x["family_id"],x["candidate_name"],tuple(x["issues"]))
            if fingerprint in seen:continue
            seen.add(fingerprint);dedup.append(x)
        reports[str(p)]={"top_level_family_id":top,"matches":dedup}
        if top is None:
            newly.append({"file":str(p),"nested_families":sorted(set(x["family_id"] for x in dedup)),
                          "blockers":sum(bool(x["issues"]) for x in dedup)})
family_coverage={fid:{"manifest_count":sum(any(x["family_id"]==fid for x in entry["matches"])
                    for entry in reports.values()),
                    "nested_recovered_count":sum(fid in row["nested_families"] for row in newly),
                    "identity_blocker_entries":sum(x["family_id"]==fid for x in flags)}
                 for fid in stocks}
OUT.mkdir()
summary={
 "version":"v2846","baseline":"v2845","audit":"recursive product-level manifests, including nested products arrays",
 "inventory_family_count":30,
 "scanned_manifest_count":len(list(ROOT.rglob("manifest.json")))-1,
 "manifest_files_with_any_explicit_pending_id":len(reports),
 "additional_manifest_files_recovered_from_nested_ids":len(newly),
 "families_with_new_nested_evidence":sorted({fid for r in newly for fid in r["nested_families"]}),
 "explicit_product_identity_flags":len(flags),
 "flagged_records":flags,
 "newly_mapped_nested_manifest_files":newly,
 "by_family":family_coverage,
 "zero_linked_families":[f for f,v in family_coverage.items() if not v["manifest_count"]],
 "photo_rights_verified":False,
 "actual_owned_stock_generation_verified":False,
 "sale_approved_new":0,
 "old_11_approved_families_unchanged":True,
 "old_55_published_urls_unchanged":True,
 "existing_QA_source_manifests_unchanged":True,
 "existing_QA_JPGs_modified":0,
 "final_spreadsheet_shared":False,
 "source_summary":reports,
 "next":"Block exact-product mismatches; use nested evidence solely for triage; do not count unlicensed photos as commercial artwork."
}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
lines=["# v2846 Recursive 30-family product identity audit",
       f"Manifest files with explicit IDs: {len(reports)}; newly recovered via nested products: {len(newly)}",
       f"Identity conflicts: {len(flags)}; zero-link families: {','.join(summary['zero_linked_families'])}",
       "No sales approval or original artwork changes.","","## Explicit conflict records"]
lines.extend(f"- {r['family_id']}: {r['candidate_name'][:125]} | {','.join(r['issues'])} | {r['source_file']}" for r in flags)
lines.extend(["","## Family coverage"])
lines.extend(f"- {fid}: {row}" for fid,row in family_coverage.items())
(OUT/"summary.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"version":"v2846","any_explicit":len(reports),
"nested_recovered":len(newly),"families_recovered":summary["families_with_new_nested_evidence"],
"identity_flags":len(flags),"zero_linked":summary["zero_linked_families"],
"sales_approved":0},ensure_ascii=False))
