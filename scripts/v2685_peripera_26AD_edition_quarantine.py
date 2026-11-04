#!/usr/bin/env python3
"""v2685 PERIPERA 26AD edition-safe stock source quarantine.
Preserve old physical frames without calling them sale-ready; compare historical
01-20 option numbers against a separately sourced 26AD retailer listing.
Never infer shade name/photo mapping across cosmetic generations.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil
HIST=Path("historical/review-JPG-by-family/pending-08")
OUT=Path("qa-review/v2685-peripera-edition-and-shade-quarantine")
assert HIST.is_dir() and not OUT.exists()
PH=OUT/"HISTORICAL_REFERENCE_NOT_FOR_UPLOAD";PH.mkdir(parents=True)
photo_entries=[]
for source in sorted(HIST.glob("*.jpg")):
    data=source.read_bytes()
    h=hashlib.sha256(data).hexdigest()
    target=PH/source.name
    shutil.copy2(source,target)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==h
    with Image.open(target) as im:
        im.load()
        assert im.format=="JPEG" and im.size==(1080,1080)
    photo_entries.append({"source_name":source.name,"sha256":h,
      "status":"REFERENCE_ONLY_WRONG_GENERATION_POSSIBLE_DO_NOT_UPLOAD"})
assert len(photo_entries)==5
# Retailer 26AD listing is an independent catalog, NOT a proof of user's exact old stock edition.
# GS SHOP product 1106843033, observed 2026-11-04.
retailer_available={1,2,3,5,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,25,26,28,29,30}
per_option=[]
for n in range(1,21):
   if n not in retailer_available:
       state="NOT_LISTED_IN_26AD_RETAILER_OPTIONS"
   else:
       state="NUMBER_ONLY_EXISTS_NOT_SHADE_MATCH_VERIFIED"
   per_option.append({"inventory_option":f"{n:03d}",
        "26AD_retailer_ordinal_listed":n in retailer_available,
        "exact_stock_name_proven":False,
        "exact_product_generation_match_proven":False,
        "image_color_swatch_approved":False,
        "decision":state})
missing=[r["inventory_option"] for r in per_option if not r["26AD_retailer_ordinal_listed"]]
assert missing==["004","006","007"],missing
report={
 "version":"v2685","family":"pending-08","product":"PERIPERA Mood Glowy Tint (4g)",
 "previous_checkpoint":"v2684b",
 "current_source_url":"https://m.gsshop.com/prd/prd.gs?prdid=1106843033",
 "catalog_observed_date":"2026-11-04",
 "retailer_page_product_label":"[NEW COLOR] 페리페라 무드 글로이 틴트 26AD",
 "catalog_26AD_current_option_numbers":sorted(retailer_available),
 "owned_inventory_scope":"historical 001-020, generation crossmatch NOT proven",
 "unlisted_inventory_numbers":missing,
 "number_listed_in_current_retailer_count":17,
 "number_missing_from_current_retailer_count":3,
 "verified_shade_to_name_mappings":0,
 "old_004_conflict":"Historical inventory has old 004 names but GS SHOP current 26AD selector does not list 004. Never merge new catalog by number without exact edition proof.",
 "old_jpgs_preserved_unchanged":len(photo_entries),
 "original_jpgs":photo_entries,
 "per_option":per_option,
 "gallery_status":"HOLD_EDITION_AND_OFFICIAL_SWATCH_MATCH",
 "sales_ready_images":0,
 "current_29_fiveframe_QA_families_unchanged":True,
 "prior_11_approved_product_families_unchanged":True,
 "public_verified_55_urls_unchanged":True,
 "no_final_excel_shared":True,
 "next_action":"Check exact owned 26AD packaging/GTIN/sku and per-shade real physical stock before any color gallery or public release."
}
(OUT/"v2685-option-edition-evidence.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
(OUT/"READ_ME_NOT_FOR_UPLOAD.txt").write_text(
 "PERIPERA original five JPG references preserved byte-for-byte.\n"
 "NOT SALES-READY and NOT eligible for storefront URLs.\n"
 "Current 26AD retailer selector lacks 004, 006 and 007.\n"
 "Do not map old 001-020 shade chart to 26AD without stock evidence.\n"
 "29 other QA sets and 55 approved URLs are unchanged.\n")
print(json.dumps({"historical_jpgs_preserved":len(photo_entries),
"inventory_options_screened":20,"26AD_number_only_present":17,
"26AD_number_not_listed":missing,
"shades_approved":0,"new_customer_release":0},ensure_ascii=False))
