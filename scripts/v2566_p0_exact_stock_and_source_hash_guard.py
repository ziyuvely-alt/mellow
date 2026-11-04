#!/usr/bin/env python3
"""v2566 targeted gate executable for five P0 Shopee inventory families.
Uses previous verified release-queue + physical imagery hashes, no OCR,
no claims of physical-stock or copyright permission.
Machine-readable DENY/HOLD gate: consumer publication must require explicit human approval.
"""
from pathlib import Path
import json,hashlib,re
P=Path("v2566-reuse/release-gates.json")
I=Path("evidence/inventory-30-family-crosswalk-20261104.json")
C=Path("v2566-base/review-JPG-by-family")
O=Path("v2566-p0-five-family-verifiable-guards");O.mkdir(exist_ok=True)
p=json.loads(P.read_text());stock=json.loads(I.read_text())
families={f["family_id"]:f for f in stock["pending_families"]}
q={f["family"]:f for f in p["products"]}
targets=["pending-01","pending-02","pending-08","pending-10","pending-26"]
assert len(targets)==len(set(targets))==5 and all(t in families and t in q for t in targets)
rules={
 "pending-01":{"allowed_shades":["21","23","25","27"],"edition":"MISSHA Magic Cushion Cover Lasting; not Moist Up, Velvet or Pro",
   "forbidden":["21/23-only chart substituted for four shades","PRO edition substituted for owned original"]},
 "pending-02":{"allowed_shades":["21","23"],"edition":"MISSHA Magic Cushion Moist Up; never Cover Lasting",
   "forbidden":["Sagi retailer-watermarked art used commercially without permission","Cover Lasting product pictures"]},
 "pending-08":{"allowed_shades":[f"{n:03d}" for n in range(1,21)],"edition":"Peripera Mood Glowy Tint 26AD recorded in stock; seller selection 001-020 only",
   "forbidden":["021-026 shades","unverified chart with invented chip colors","unverified 26AD / old-generation swatch mixing"],
   "name_discrepancy":{"014_inventory":"로지워시","014_retailer":"로지위시"}},
 "pending-10":{"allowed_shades":["1","2","3"],"edition":"OBgE Perfect Homme Cushion 15g (dark square; old round Perfect Cover is wrong)",
   "forbidden":["beige rounded Perfect Cover compact","13g package for 15g target",
      "SPF50+ PA++++ invented for verified Homme PA+++"]},
 "pending-26":{"allowed_shades":["145ML"],"edition":"Pixelpure Gentle Gel to Foam 145 mL only",
   "forbidden":["150mL printed product photo","gallery shopping bag as cleanser product","145mL footer over 150mL bottle"],
   "allowed_source_145ml_sha":"6bcb50db894591dd724125629308de7907b427021fef2edcc67f8debecc505cd",
   "blocked_source_sha":[
      "915cf0476cc9952d04af9b8eff0c46169eb4c207a274116c6c72eb1bbfc3ea0d",
      "07c4121b016578b4981085364ec649d049dc0d18d1102c1583f240a9cb17c15b",
      "e308d286ae3f4b49029cfeb18c817c330c37acb8e88c26ac265c5e92df9af190",
      "7e79fb3edbe6a0a42ff7cf19067c59ab4aa0c1360289a56ef2feb23670d789a1"]}
}
checks=[]
for target in targets:
 data=families[target];conf=rules[target];expected=conf["allowed_shades"]
 options=[str(x).strip() for x in data["option_values"]]
 actual=[]
 for o in options:
  if target=="pending-26":actual.append(o.upper())
  elif target=="pending-08":actual.append(o.split(" ",1)[0].zfill(3))
  elif target=="pending-10":actual.append(re.match(r"[123]",o).group())
  else:actual.append(re.match(r"\d+",o).group())
 assert actual==expected,(target,actual,expected)
 photos=list((C/target).glob("*.jpg"))
 assert len(photos)==(5 if target in ("pending-08","pending-10","pending-26") else 6)
 image_sha=[hashlib.sha256(x.read_bytes()).hexdigest() for x in photos]
 assert len(set(image_sha))==len(photos)
 # Direct source SHA collisions are a real rejection; composites are not provably safe.
 forbidden_source=conf.get("blocked_source_sha",[])
 direct_hash_collision=sorted(set(image_sha)&set(forbidden_source))
 assert not direct_hash_collision,(target,direct_hash_collision)
 eligible_cards=[{"file":x.name,"sha256":hashlib.sha256(x.read_bytes()).hexdigest()} for x in photos]
 flags=[]
 if target=="pending-08":flags+=["INVENTORY_26AD_VS_OLDER_THUMBNAIL_RULE_CONFLICT","SHADE_014_NAME_CONFLICT"]
 if target=="pending-10":flags+=["OLD_15G_WRONG_PRODUCT_SOURCE_HISTORIC_QUARANTINE"]
 if target=="pending-26":flags+=["OFFICIAL_145_ML_PAGE_MIXED_150_ML_PHOTOGRAPHS","COMPOSITE_150ML_CONTAMINATION_NOT_EXCLUDED_BY_HASH_ONLY"]
 if target=="pending-01":flags+=["FOUR_SHADE_CHART_OFFICIAL_OWNED_STOCK_EDITION_UNCONFIRMED"]
 if target=="pending-02":flags+=["RETAILER_WATERMARK_IMAGE_LICENSE_UNCONFIRMED"]
 checks.append({"family":target,"product":data["family_name"],"expected_shades":expected,
  "actual_inventory_shades":actual,"all_shades_match_inventory":True,
  "image_count":len(photos),"image_files_and_sha":eligible_cards,
  "blocked_direct_source_SHA_matches":direct_hash_collision,
  "known_wrong_source_blocks":conf["forbidden"],"edition_guard":conf["edition"],
  "specific_qa_flags":flags,
  "commercial_release_gate":"DENY_UNTIL_EDITION_AND_VISUAL_AND_LICENSE_AND_LOGO_EVIDENCE",
  "technical_sha_collision_check":"PASS_NOT_PROOF_OF_PHOTOGRAPHIC_CORRECTNESS"})
assert len(checks)==5 and sum(x["image_count"] for x in checks)==27
manifest={"version":"v2566","source_queue_run":41755214185,
 "existing_156_JPG_corpus_run":41753618979,"P0_families_checked":5,"P0_existing_jpg_checked":27,
 "all_inventory_option_sets_exact":True,
 "direct_forbidden_source_sha_collisions":0,
 "actual_composites_verified_to_match_purchased_stock":False,
 "commercial_photo_reuse_rights_verified":False,
 "original_mk_logo_verified":False,
 "released":0,"source_public_55_URLs_changed":0,"new_urls":0,
 "excel_generated":False,"all_P0_public_release_denied_without_human_evidence":True,
 "guard_results":checks}
(O/"product-guards.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
(O/"publication-denylist.json").write_text(json.dumps({"version":"v2566",
 "deny_public_release_for_family":targets,
 "known_bad_photo_source_sha":rules["pending-26"]["blocked_source_sha"],
 "known_good_145ml_photo_source_sha_still_rights_hold":rules["pending-26"]["allowed_source_145ml_sha"],
 "peripera_approved_scope_only":rules["pending-08"]["allowed_shades"],
 "require_human_signoff":True,"source":"grounded existing source visual QA"},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"P0_families":5,"photos_sha_checked":27,"inventory_option_sets_verified":5,
 "critical_conflicts":sum(len(x["specific_qa_flags"]) for x in checks),
 "commercial_approval":0,"new_uploads":0,"xlsx_shared":False}))
