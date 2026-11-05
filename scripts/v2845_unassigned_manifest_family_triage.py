#!/usr/bin/env python3
"""v2845: triage QA manifests missing explicit pending-family mapping.
This does NOT change products, images, final spreadsheets or approvals.
"""
from pathlib import Path
from collections import defaultdict
import json,re

R=Path("qa-review")
INV=json.loads(Path("/tmp/v2845-inventory-crosswalk.json").read_text())
OLD=json.loads((R/"v2844-30family-product-identity-batch-QA"/"manifest.json").read_text())
OUT=R/"v2845-unassigned-QA-family-linkage-triage"
assert not OUT.exists()
assert len(INV["pending_families"])==30 and OLD["pending_families"]==30
OUT.mkdir()
ids={f["family_id"] for f in INV["pending_families"]}
def explicit(o):
    for k in ["family","pending_family","pending_family_id","product_family","inventory_family_id"]:
        v=o.get(k)
        if isinstance(v,str) and re.fullmatch("pending-[0-9]{2}",v):return v
    return None
def label(o):
    fields=["product","product_name","product_family_name","item","family_name",
            "product_title","product_family","inventory_product","shade"]
    return " | ".join(str(o[k]) for k in fields if isinstance(o.get(k),str))
def tokens(text):
    return re.sub("[ _-]+"," ",text.lower())
def inference(s):
    s=tokens(s)
    checks=[
      ("pending-07",r"mesh\s*blur|메쉬\s*블러"),
      ("pending-12",r"peel\s*shot|필\s*샷|필샷"),
      ("pending-13",r"(missha|미샤).*(pdrn|피디알엔).*(serum|세럼)|pdrn.*(missha|미샤).*(serum|세럼)"),
      ("pending-14",r"(missha|미샤).*(pdrn|피디알엔).*(cream|크림)"),
      ("pending-22",r"max\s*waterful|맥스\s*워터풀"),
      ("pending-23",r"pore\s*zero|포어\s*제로"),
      ("pending-24",r"(bioheal|바이오힐보).*nad.*serum|프리즈셀.*세럼"),
      ("pending-25",r"(bioheal|바이오힐보).*nad.*cream|프리즈셀.*크림"),
      ("pending-26",r"gentle\s*gel\s*to\s*foam|젤\s*투\s*폼"),
      ("pending-27",r"soothing\s*ampule\s*toner|수딩\s*앰플\s*토너"),
      ("pending-28",r"glow\s*cleansing\s*serum\s*pad|글로우\s*클렌징\s*세럼\s*패드"),
      ("pending-29",r"radiance\s*aqua\s*soothing\s*cream|래디언스\s*아쿠아\s*수딩\s*크림"),
      ("pending-30",r"aura\s*radiance\s*serum|아우라\s*래디언스\s*세럼"),
    ]
    return [fid for fid,pattern in checks if re.search(pattern,s)]
results=[]
for path in sorted(R.rglob("manifest.json")):
    if OUT in path.parents: continue
    try: data=json.loads(path.read_text())
    except:continue
    if not isinstance(data,dict) or explicit(data) in ids:continue
    title=label(data)
    # Filename is provenance for a candidate association, never final proof.
    combined=str(path)+" | "+title
    matches=inference(combined)
    status=("PROPOSED_UNVERIFIED" if len(matches)==1 else
            "AMBIGUOUS_MULTIPLE" if len(matches)>1 else
            "UNMAPPED_NO_SAFE_EXACT_EVIDENCE")
    results.append({"file":str(path),"identity_text":title[:300],
                    "potential_families":matches,"status":status,
                    "not_sales_ready":True,"not_auto_linked":True})
summary={
  "version":"v2845","baseline":"v2844",
  "scope":"Unassigned QA manifests and conservative family linkage discovery",
  "unassigned_manifest_count":len(results),
  "single_family_inference_count":sum(r["status"]=="PROPOSED_UNVERIFIED" for r in results),
  "ambiguous_count":sum(r["status"]=="AMBIGUOUS_MULTIPLE" for r in results),
  "unmapped_count":sum(r["status"]=="UNMAPPED_NO_SAFE_EXACT_EVIDENCE" for r in results),
  "coverage_repair_candidates":sorted({fid for r in results for fid in r["potential_families"]}),
  "zero_explicit_id_families_in_v2844":[r["family_id"] for r in OLD["all_30_family_records"] if r["matched_manifest_count"]==0],
  "identity_links_auto_applied":0,
  "prior_v2844_identity_flags_preserved":OLD["explicit_identity_flag_count"],
  "old_11_approved_families_unchanged":True,
  "old_55_public_URLs_unchanged":True,
  "photo_files_modified":0,"new_sale_approvals":0,"final_xlsx_shared":False,
  "rows":results,
  "next":"Review proposed family/edition pairings before linking. Continue image production for other clearly matched groups without using ambiguous assets."
}
(OUT/"manifest.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
lines=["# v2845 Unassigned QA family linkage triage",
       f"Total unassigned: {len(results)}, single-family suggestions: {summary['single_family_inference_count']}, ambiguous: {summary['ambiguous_count']}, no safe match: {summary['unmapped_count']}",
       "No auto-link, photo modification, commercial rights verification, or sales approval.",
       ""]
for r in results:
    lines.append(f"- {r['status']} | {r['file']} | candidates {','.join(r['potential_families']) or 'none'}")
(OUT/"summary.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"v":"v2845","unassigned":len(results),"proposed":summary["single_family_inference_count"],
 "ambiguous":summary["ambiguous_count"],"unmapped":summary["unmapped_count"],
 "no_id_families":summary["zero_explicit_id_families_in_v2844"],
 "sales_approved":0},ensure_ascii=False))
