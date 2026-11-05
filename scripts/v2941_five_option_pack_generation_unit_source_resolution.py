#!/usr/bin/env python3
"""v2941 resolve MISSHA 15mL labeling and CLIO 25FW-vs-regular bonus pack mapping.
Peripera current 26AD chart does not prove legacy 01-20 photos are identical.
5 previously blocked stock groups; source images, stock SKUs, approved 11 sets and 55 URLs stay immutable.
"""
from pathlib import Path
from hashlib import sha256
import json,time
Q=Path("qa-review")
BASE=Q/"v2940-four-final-source-gaps-photo-archive-integrity-and-approval-gate"
V24=Q/"v2924-eight-unpacked-stock-family-3five-photo-20option-4clio-source-QA"
V25=Q/"v2925-peripera-01to20-40immutable-JPG-PNG-and-alpha-native-QA"
V31=Q/"v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA"
OUT=Q/"v2941-five-option-pack-generation-unit-conflict-resolution-QA"
assert not OUT.exists()
s=json.loads((BASE/"stock30-incremental-state-v2940.json").read_text(encoding="utf-8"))
m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
m24=json.loads((V24/"manifest.json").read_text(encoding="utf-8"))
m25=json.loads((V25/"manifest.json").read_text(encoding="utf-8"))
m31=json.loads((V31/"manifest.json").read_text(encoding="utf-8"))
assert s["version"]==m["version"]=="v2940" and len(s["families"])==30
assert m["mixed_options_and_edition_hold_families"]==5 and m["remaining_distinct_source_photo_slots"]==4
assert m25["peripera_legacy_shades_archived"]==20 and m31["quarantined_prior_mini_photo_references"]==4
blocked={x["family"] for x in m24["mixed_option_sources"]}|{"pending-08"}
assert blocked=={"pending-05","pending-06","pending-07","pending-08","pending-12"}
source_refs={
 "MISSHA_OFFICIAL_VOLUME":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236",
 "CLIO_OFFICIAL_MESH_GLOW_SETS":"https://clubclio.co.kr/shop/goodsView/6182",
 "CLIO_CURRENT_FOUNWEAR_SET":"https://clubclio.co.kr/shop/goodsView/0000006670",
 "CLIO_MESH_BLUR_WEIGHT":"https://shinsegaemall.ssg.com/item/itemView.ssg?itemId=1000696139089&salestrNo=6005&siteNo=6004",
 "CLIO_GLOW_FIVE_SHADE_LABELS":"https://m.shinsegaetvshopping.com/display/detail/1000656537",
 "PERIPERA_26AD_COLOR_AND_RENEWAL_CHART":"https://www.gsshop.com/prd/prd.gs?prdid=1106843033"
}
shade_map={"19C":"LIGHT","19N":"PORCELAIN","21C":"LINGERIE","21N":"LINEN","23N":"GINGER"}
rows={
 "pending-05":{"verified":"Regular CLIO Founwear Cushion SET, brand goods 6670, not 5g mini goods 5750 or 7108",
  "newly_resolved":"v2931 removed four misassigned mini 5g sources from internal full-size mapping",
  "still_blocked":["Product-generation and physical inventory photos","image commercial rights","shade-specific official photographs"],
  "release_gate":"HOLD_FULLSIZE_EDITION_AND_SHADE"},
 "pending-06":{"verified":"CLIO Kill Cover Mesh Glow Essential Cushion, full-size 15g+refill 15g; shade map from retailer product specifications",
  "newly_resolved":"Current official clubclio goods 6182 lists different added gifts by seasonal pack: 25FW skin-prep base 15mL; regular duo-cheek 10g",
  "shade_codes":shade_map,
  "offer_variants":[{"edition":"25FW","main_cushion_g":15,"refill_g":15,"added":"skin prep base 15mL"},{"edition":"REGULAR","main_cushion_g":15,"refill_g":15,"added":"duo cheek 10g"}],
  "still_blocked":["Prior 5 shade-linked images are near-identical across all 10 pairs","stock actual edition undetermined","retailer source rights"],
  "release_gate":"HOLD_SEASONAL_GIFT_GENERATION_AND_OPTION_IMAGES"},
 "pending-07":{"verified":"Mesh Blur Cushion set capacity 15g * 2 per product information, not a mini 5g cushion",
  "newly_resolved":"15g x2 package specification externally corroborated",
  "existing_shade_source_cards":["19C","19N","21N"],
  "still_blocked":["Other shade variants missing or unconfirmed","cushion + refill stock proof","photo usage rights"],
  "release_gate":"HOLD_OTHER_SHADES_AND_SET_STOCK"},
 "pending-08":{"verified":"PERIPERA Mood Glowy Tint 26AD marketed as 4g; new-generation dual container + refreshed formula, legacy JPG/PNG cannot be relabeled 26AD",
  "newly_resolved":"Published 26AD color chart can be cross-checked by option number. Retained user's strict 01-20 input only.",
  "external_color_chart_01to20_covered":["01","02","03","05","08","09","10","11","12","13","14","15","16","17","18","19","20"],
  "not_shown_in_cited_26AD_chart":["04","06","07"],
  "not_added_by_user_instruction":["21","22","23","24","25","26","27","28","29","30"],
  "prior_originals":40,"prior_low_native_alpha_shades":["12","14","20"],
  "still_blocked":["04/06/07 current edition existence not confirmed from cited chart (NOT proof of discontinuation)","legacy photo vs 26AD bottle and shade mismatch","5 previously held shade visuals and commercial rights"],
  "release_gate":"HOLD_LEGACY_VS_26AD_COLOR_GENERATION"},
 "pending-12":{"verified":"MISSHA PDRN NAD+ Renew Peel Shot 25 official Korean shop lists volume 15mL, matching stock name",
  "newly_resolved":"Old 15g vs 15mL ambiguity resolved from current brand-owner official product disclosure",
  "confirmed_content_unit":"15mL","volume_conflict_status":"CLEARED_BY_BRAND_OFFICIAL",
  "still_blocked":["Previously mixed information frames not independently approved product photos","product/claim photo rights","physical inventory lot and packaging"],
  "release_gate":"HOLD_PHOTO_CLAIMS_AND_STOCK_AFTER_VOLUME_CLEARED"}
}
old_names={x["family"]:x["product"] for x in m24["mixed_option_sources"]}
for family,item in rows.items():
 st=s["families"][family]
 st["last_delta_version"]="v2941"
 st["v2941_fact_resolution"]=item["newly_resolved"]
 st["v2941_release_gate"]=item["release_gate"]
 st["v2941_nonphoto_evidence_verified_only"]=True
 st["release_status"]=item["release_gate"]
 st["latest_photo_QA_checkpoint"]="v2941 "+item["newly_resolved"]+"; sale, stock, photo rights and unresolved option image issues still HOLD"
 st["sale_approved"]=False
 if family=="pending-12":
  st["v2941_official_content_value"]=15
  st["v2941_official_content_unit"]="mL"
  st["v2941_15g_vs_15ml_conflict"]="CLEARED_OFFICIAL_15ML"
 if family=="pending-06":
  st["v2941_official_pack_versions"]=item["offer_variants"]
results=[{"family":k,"product":s["families"][k]["product"],**v,"sale_approved":False} for k,v in rows.items()]
r={
 "version":"v2941","baseline":"v2940","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "previous_mixed_option_holds_inspected":5,
 "resolved_official_unit_conflicts":1,
 "identified_seasonal_pack_options":2,
 "verified_five_shade_labels_for_clio_glow":5,
 "peripera_colors_not_in_one_current_chart_but_not_removed":["04","06","07"],
 "photos_newly_generated":0,"source_original_bytes_changed":0,
 "previous_21_fivephoto_archives_untouched":True,
 "previous_4_partial_archives_untouched":True,
 "previous_11_approved_families_untouched":True,"previous_55_public_urls_untouched":True,
 "new_retail_approvals":0,"new_public_urls":0,"final_spreadsheet_shared":False,
 "source_evidence_urls":source_refs,
 "reconciliation":results}
OUT.mkdir(parents=True)
(OUT/"manifest.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
s.update({"version":"v2941","baseline":"v2940","new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False})
(OUT/"stock30-incremental-state-v2941.json").write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2941","family_holds_updated":5,"official_unit_conflicts_cleared":1,"CLIO_seasonal_pack_variants":2,"no_new_retail_approvals":True},ensure_ascii=False))
