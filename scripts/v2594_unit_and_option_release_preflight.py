#!/usr/bin/env python3
"""v2594 stock-to-customer-image unit and option crosswalk.
Uses the exact original inventory 30-family mapping, official MISSHA 15 mL
primary evidence, and existing Peripera 014 corrected reference.
Does not alter source inventory, customer JPG, public URLs or XLSX.
"""
from pathlib import Path
import re,json
I=json.loads(Path("evidence/inventory-30-family-crosswalk-20261104.json").read_text())
E=json.loads(Path("evidence/v2594-missha-pdrn-renew-peel-shot25-official-15ml-versus-stock-15G-20261104.json").read_text())
C=json.loads(Path("evidence/v2569-peripera-004-006-007-014-naming-verified-20261104.json").read_text())
OUT=Path("v2594-30family-unit-identity-and-options-qa")
OUT.mkdir(exist_ok=True)
allrows=I["pending_families"]
assert len(allrows)==30
def measures(s):
 t=str(s).lower().replace(" ","")
 found=[]
 i=0
 while i<len(t):
  if not t[i].isdigit():
   i+=1
   continue
  j=i
  while j<len(t) and (t[j].isdigit() or t[j]=="+"):
   j+=1
  number=t[i:j]
  if t[j:j+2]=="ml":
   found.append((number,"ml"));i=j+2
  elif t[j:j+1]=="g":
   found.append((number,"g"));i=j+1
  else:
   i=j
 return found
hold=[];confirmed=[];ignored=[];scanned=0
for item in allrows:
 family=item["family_id"]; name=item["family_name"]
 options=[str(x).strip() for x in item["option_values"] if str(x).strip()]
 found=measures(name)
 if not found:
  ignored.append({"family":family,"reason":"NO_COMPARABLE_VOLUME_IN_FAMILY_NAME"})
  continue
 volume,unit=found[0]
 exact_options=[]
 for option in options:
  found_option=measures(option)
  if found_option and option[0].isdigit():
   n,u=found_option[0]
   exact_options.append((n,u,option))
 if not exact_options:
  ignored.append({"family":family,"expected":volume+unit,"reason":"OPTIONS_ARE_SHADES_EMPTY_OR_NON_SIZE_METADATA"})
  continue
 scanned+=1
 discrepancies=[{"option":raw,"expected":volume+unit,"actual":n+u} for n,u,raw in exact_options if (n,u)!=(volume,unit)]
 if discrepancies:
  hold.append({"family":family,"product":name,"discrepancies":discrepancies,"status":"HOLD_INVENTORY_UNIT_CONFLICT_NO_AUTO_CORRECTION"})
 else:
  confirmed.append({"family":family,"expected":volume+unit,"option_values":options,"status":"INVENTORY_INTERNAL_UNITS_AGREE_NOT_PHYSICAL_PACKAGING_PROOF"})
assert len(hold)==1 and hold[0]["family"]=="pending-12",hold
assert E["canonical_public_product_volume"]=="15 mL"
assert E["original_inventory_option"]=="15G"
assert C["canonical_014_for_future_draft"]=="014 로지위시"
warnings=[{"family":"pending-08","conflict":"Shade 014 Korean inventory says 로지워시 while validated retailer label reads 로지위시; source rows preserved","disposition":"USE_CANONICAL_REFERENCE_ONLY; HOLD_LICENSED_SHADE_CHART"},
 {"family":"pending-22","conflict":"Stored option text SPF50+ PA++++ is a sunscreen rating, not a color/quantity SKU","disposition":"DO_NOT_MAKE_SPF_A_VARIANT"},
 {"family":"pending-12","conflict":"Inventory 15G contradicts official 15mL product label","disposition":"HOLD_PHYSICAL_STOCK_QA; USE_15mL_IN_COPY_ONLY_AFTER_STOCK_CROSSCHECK"}]
report={"version":"v2594","families_in_inventory":30,"families_with_comparable_quantity_options":scanned,
"internally_matching_quantity_families":len(confirmed),"unit_conflicts":len(hold),
"non_quantity_option_groups_excluded_from_unit_check":len(ignored),
"critical_unit_conflicts":hold,"other_copy_and_option_warnings":warnings,
"official_15mL_brand_evidence_urls":[x["url"] for x in E["sources"][:2]],
"source_inventory_edited":False,"review_corpus_v2593_left_unchanged":True,
"public_55_URLs_changed":0,"xlsx_created_or_shared":False,
"sales_approval_granted":False,"known_consistent_product_quantity_groups":confirmed,
"noncomparable_families":ignored}
(OUT/"unit-and-identity-release-holds.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"safe-copy-rules.md").write_text(
    "# Unit and identity release gates\n\n"
    "MISSHA PDRN NAD+ Renew Peel Shot 25: brand verified 15 mL; inventory 15G is a conflict pending physical stock check.\n\n"
    "PERIPERA Mood Glowy Tint: shade 014 Rosy Wish / 로지위시 is a corrected candidate label. Do not invent swatches.\n\n"
    "OBgE Max Waterful: SPF50+ PA++++ option is specification, not a selectable shade.\n\n"
    "No pending product has photo-rights, stock-edition, MK-logo and final visual approval.\n"
)
print(json.dumps({"inventory_families":30,"comparable_quantities":scanned,
"unit_mismatches":len(hold),"mismatch_family":"pending-12",
"source_files_mutated":0,"spreadsheet_shared":False}))
