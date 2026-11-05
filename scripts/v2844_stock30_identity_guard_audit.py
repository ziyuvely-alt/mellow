#!/usr/bin/env python3
"""v2844 immutable, inventory-first audit of pending 30-family QA manifests.
Read-only analysis on existing assets; writes only a new audit folder.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,re,hashlib

ROOT=Path("qa-review")
INVENTORY=Path("/tmp/v2844-inventory-crosswalk.json")
OUT=ROOT/"v2844-30family-product-identity-batch-QA"
assert INVENTORY.exists()
assert ROOT.exists() and not OUT.exists()
crosswalk=json.loads(INVENTORY.read_text())
assert crosswalk["checks"]["unique_pending_family_count"]==30
families={f["family_id"]:f for f in crosswalk["pending_families"]}
assert len(families)==30 and set(families)=={f"pending-{i:02d}" for i in range(1,31)}

def identity_text(obj):
    fields=("product","product_name","product_family_name","item","family_name",
            "product_title","stock_product","inventory_product")
    return " | ".join(str(obj[k]) for k in fields if isinstance(obj.get(k),str))

def feature(name):
    n=name.lower().replace(" ","")
    mini=bool(re.search(r"mini|미니",n))
    gift=bool(re.search(r"기획세트|giftset|setof2|2pack|x2|×2",n))
    single=bool(re.search(r"single|단품",n))
    # actual size/volume only, avoid extracting option shade numbers
    vol={int(a) for a in re.findall(r"(?<!\d)(\d+)\s*ml\b",n)}
    gram={int(a) for a in re.findall(r"(?<!\d)(\d+)\s*g\b",n)}
    return {"mini":mini,"gift_set":gift,"single":single,
            "volume_ml":sorted(vol),"weight_g":sorted(gram)}

def risky(expected, observed):
    a,b=feature(expected),feature(observed)
    reasons=[]
    if a["gift_set"] and b["mini"] and not b["gift_set"]:
        reasons.append("GIFT_SET_MAPPED_TO_SINGLE_MINI")
    if a["mini"] and b["gift_set"] and not b["mini"]:
        reasons.append("MINI_MAPPED_TO_GIFT_SET")
    if a["volume_ml"] and b["volume_ml"] and not set(a["volume_ml"]).intersection(b["volume_ml"]):
        reasons.append("VOLUME_MISMATCH")
    if a["weight_g"] and b["weight_g"] and not set(a["weight_g"]).intersection(b["weight_g"]):
        reasons.append("WEIGHT_MISMATCH")
    return reasons

all_files=sorted(p for p in ROOT.rglob("manifest.json") if OUT not in p.parents)
found=defaultdict(list)
unassigned=[]
errors=[]
for path in all_files:
    try: doc=json.loads(path.read_text())
    except Exception as e:
        errors.append({"path":str(path),"error":str(e)[:120]})
        continue
    fid=next((doc[k] for k in ("family","pending_family","pending_family_id","product_family")
              if isinstance(doc.get(k),str) and re.fullmatch(r"pending-\d{2}",doc[k])),None)
    if not fid:
        # identity-audit gates refer to family by an explicit inventory key
        fid=doc.get("inventory_family_id")
    if fid not in families:
        unassigned.append(str(path));continue
    found[fid].append((path,doc))

rows=[]
flags=[]
for fid,stock in families.items():
    wanted=stock["family_name"]
    option_count=len(stock.get("option_values",[]))
    sources=[]
    for path,doc in found.get(fid,[]):
        actual=identity_text(doc)
        reasons=risky(wanted,actual) if actual else []
        if reasons:
            flags.append({"family_id":fid,"stock_family":wanted,
                          "candidate":actual[:240],"file":str(path),"reasons":reasons,
                          "action":"BLOCK_FOR_STOCK_MATCH_ONLY_NO_IMAGE_DELETE"})
        sources.append({"manifest":str(path),"candidate_name":actual[:220],
                       "flags":reasons,"stage":str(doc.get("status") or doc.get("gallery_status") or "")[:110]})
    rows.append({"family_id":fid,"stock_family":wanted,
                 "stock_option_count":option_count,
                 "matched_manifest_count":len(sources),
                 "requires_option_chart":bool(stock.get("requires_option_chart")),
                 "flags_count":sum(bool(s["flags"]) for s in sources),
                 "linked_manifests":sources})
# Preserve earlier v2841 stop gate. No new approval from an audit.
old_gate=ROOT/"v2841-pending05-giftset-vs-mini-identity-block"/"manifest.json"
assert old_gate.is_file()
gate=json.loads(old_gate.read_text())
assert gate["decision"]=="HOLD_PRODUCT_IDENTITY_INCOMPATIBLE"
# Certain stock-family variants were accidentally linked in earlier QA scripts.
# Zero flags is NOT an endorsement: unlicensed sources and packaging remain held.
OUT.mkdir()
report={
  "version":"v2844","baseline":"v2843",
  "scope":"30 pending inventory families and existing linked QA manifest identities",
  "stock_crosswalk":"evidence/inventory-30-family-crosswalk-20261104.json",
  "source_qa_branch":"qa-assets/v2662-immutable-14-candidates",
  "pending_families":30,
  "manifest_files_scanned":len(all_files),
  "manifest_files_with_identified_family":sum(len(v) for v in found.values()),
  "manifest_files_without_pending_family_id":len(unassigned),
  "parse_errors":errors,
  "family_count_with_explicit_identity_risk":len({a["family_id"] for a in flags}),
  "explicit_identity_flag_count":len(flags),
  "identity_flags":flags,
  "existing_pending05_mini_vs_giftset_block_preserved":True,
  "risk_flags_not_proof_of_sku_match_or_photo_license":True,
  "all_30_family_records":rows,
  "11_sale_approved_families_unchanged":True,
  "55_verified_public_URLs_unchanged":True,
  "source_images_changed":0,
  "final_excel_shared":False,
  "new_sales_approvals":0,
  "next":"Resolve actual stock product/version and licensed photos; never reuse a Mini 5g QA reference as a cushion gift-set sale asset."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
text=["# v2844 | 30-family inventory/QA identity cross-check",
      "All QA sources are preserved. This audit does not grant commercial photo rights.",
      "",
      f"QA manifests scanned: {len(all_files)}",
      f"Manifests with explicit pending IDs: {report['manifest_files_with_identified_family']}",
      f"Families with explicit identity warnings: {report['family_count_with_explicit_identity_risk']}",
      f"Risk rows: {len(flags)}",
      "",
      "## Identity blockers"]
for flag in flags:
    text.append(f"- {flag['family_id']}: {', '.join(flag['reasons'])} | {flag['candidate'][:100]} | {flag['file']}")
text.extend(["","## All pending families"])
for row in rows:
    text.append(f"- {row['family_id']}: {row['stock_family']} | linked manifests {row['matched_manifest_count']} | flagged {row['flags_count']}")
text.extend(["","Caution: missing risks do not imply product or packaging verified. Prior approved 11 families and 55 public URLs left unchanged.",""])
(OUT/"summary.md").write_text("\n".join(text))
print(json.dumps({"v":"v2844","scanned":len(all_files),"linked":report["manifest_files_with_identified_family"],
"flagged":len(flags),"families_flagged":report["family_count_with_explicit_identity_risk"],
"sample":flags[:5],"sales_approved":0},ensure_ascii=False))
