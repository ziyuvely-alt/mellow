#!/usr/bin/env python3
"""v2975: immutable evidence-driven release gate, frame hold, and manufacturer catalog contracts.

Does not create/copy photos, does not publish or modify previous public files.
It updates machine-readable release queues, and aborts if a proposed release lacks
ownership/edition, image rights, authentic MK, and anonymous SHA256 checks.
"""
import json, pathlib, hashlib, datetime
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2975-actual-frame-quarantine-and-unit-contract-20261106"
PREVIOUS=ROOT/"qa-review/v2972-reconciled-30-family-manual-visual-and-181-file-gates-20261106/manifest.json"
SEARCH=ROOT/"qa-review/v2974-goodal-eyecream-same-SHA-original-candidate-search-20261106/manifest.json"
REPORT2970=ROOT/"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106/manifest.json"

def as_json(p):return json.loads(p.read_text(encoding="utf-8"))
def require(cond,msg):
    if not cond:raise ValueError(msg)
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    require(not OUT.exists(),"v2975 exists, refuse to overwrite")
    prev=as_json(PREVIOUS)
    search=as_json(SEARCH)
    report=as_json(REPORT2970)
    groups={row["id"]:row.copy() for row in prev["families"]}
    require(len(groups)==30,"Missing 30-family roster")
    require(search["outcome"]=="BOTH_MATCHING_STANDALONE_FOUND","Do not assume archived photo match")
    archived=report["results"]["pending-21"]["JPG_files"]
    require(len(archived)==5 and archived[2]["SHA256"]==search["archived_sha256"]["3"],"Eyecream third frame mismatch")
    require(archived[3]["SHA256"]==search["archived_sha256"]["4"],"Eyecream fourth frame mismatch")
    frame3="qa-review/v2815-goodal-25ad-five-photo-set-silver-cap-crop-fixed/03-original-2026-yellow-tube-cream-swatch-QA.jpg"
    frame4="qa-review/v2815-goodal-25ad-five-photo-set-silver-cap-crop-fixed/04-real-tube-front-and-silver-cap-full-detail-QA.jpg"
    require(frame3 in search["matching_existing_standalone_paths"]["3"],"Unexpected frame3 photo")
    require(frame4 in search["matching_existing_standalone_paths"]["4"],"Unexpected frame4 photo")
    manufacturer_units={
      "pending-05":{
        "product":"CLIO Kill Cover Founwear Cushion full-size gift set",
        "manufacturer_catalog_net":"15g x 2","dimension":"net mass",
        "manufacturer_url":"https://clubclio.co.kr/shop/goodsView/6670",
        "manufacturer_page_fact":"15g*2; full-size set original compact + refill",
        "manufacturer_page_batch_hint":"Manufactured July 2025 or later in indexed page; current seasonal packaging/gifts can change",
        "physical_unit_status":"UNVERIFIED_OWNED_SKU",
        "do_not_assume_promotional_gifts":True
      },
      "pending-07":{
        "product":"CLIO Kill Cover Mesh Blur cushion 15g x 2",
        "manufacturer_catalog_net":"15g x 2","dimension":"net mass",
        "manufacturer_url":"https://clubclio.co.kr/shop/goodsView/6455",
        "manufacturer_page_fact":"15g x 2; current listing may include extra finish pact/gift unrelated to stocked set",
        "manufacturer_page_batch_hint":"Manufactured April 2025 or later in indexed page",
        "physical_unit_status":"UNVERIFIED_OWNED_SKU",
        "do_not_assume_promotional_gifts":True
      },
      "pending-12":{
        "product":"MISSHA PDRN NAD+ Renew Peel Shot 25",
        "manufacturer_catalog_net":"15mL","dimension":"net volume",
        "manufacturer_url":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236",
        "manufacturer_page_fact":"Brand seller lists 15ml. Treat previously written 15g as UNVERIFIED_MISMATCH, not convert g -> mL.",
        "physical_unit_status":"UNVERIFIED_OWNED_SKU",
        "corrected_source_claim":"15mL BRAND_CATALOG_PROVEN, stock label pending"
      },
      "pending-21":{
        "product":"GOODAL Green Tangerine Vita-C Dark Circle Eye Cream 25AD",
        "manufacturer_catalog_net":"30mL","dimension":"net volume",
        "independent_product_distributor_url":"https://m.shilladfs.com/estore/kr/ko/p/5754369",
        "retailer_reference":"25AD model and 30mL single product in Shilla DFS catalog",
        "manufacturer_page_fact":"Shilla Duty Free 25AD single 30mL; other merchants also sell bundles, not proof of actual owned unit",
        "physical_unit_status":"UNVERIFIED_SINGLE_VS_BUNDLE",
        "do_not_assume_bundle":True
      }
    }
    holds=[
      {
        "family":"pending-21","slot":3,"sha256":archived[2]["SHA256"],"action":"PRESERVE_QA_SOURCE",
        "existing_source":frame3,
        "reason":"Entire yellow 30mL tube photographed against cream smear; photo distinct from standalone single tube hero. Already present, no recreation."
      },
      {
        "family":"pending-21","slot":4,"sha256":archived[3]["SHA256"],"action":"QUARANTINE_FROM_FIVE_DISTINCT_SCENE_COUNT_ONLY",
        "existing_source":frame4,
        "reason":"Direct visual comparison of exact identical archived SHA source shows same yellow 30mL tube and cream smear with different crop; repeats #3 scene.",
        "duplicate_of_slot":3,
        "allowed":"Keep original JPG bytes for archival QA; do not include as separate scene 4 in customer-ready pack",
        "replacement_requirements":["different exact 25AD product photograph OR factual card from proven claim",
            "commercial photo permission if replacing with real photo",
            "authentic MellowKR circular MK before public publication",
            "owned stock single-vs-bundle net quantity check"]
      },
      {"family":"pending-05","slot":"M/B reference","action":"KEEP_ONLY_AS_ONE_COMPOSITION_PER_EDITION",
       "reason":"6670 M/B sources displayed matching model-with-black-compact, do not count as two independent product scenes"},
      {"family":"pending-07","slot":"M/B reference","action":"KEEP_ONLY_AS_ONE_COMPOSITION_PER_EDITION",
       "reason":"6455 M/B source visually same pale compact and puff, separate from 3 color information cards"},
      {"family":"pending-12","slot":"15g wording in any existing informational frame","action":"BLOCK_INCORRECT_NET_CONTENT_PROMISE",
       "reason":"Official brand catalog has 15mL; no mass/volume interchange or physical 15g claim until verified."}
    ]
    approved_release=[]
    gate_conditions=["physical_owned_version_proven","commercial_photo_rights_proven",
        "original_MK_binary_SHA256_verified","all_frames_claims_and_crop_pass",
        "anonymous_Render_JPG_GET_SHA256_verified"]
    for family,row in groups.items():
        row["manufacturer_catalog_confirmation"]=manufacturer_units.get(family)
        row["media_frame_action_status"]=[h for h in holds if h["family"]==family]
        row["release_gate_evidence"]={x:False for x in gate_conditions}
        row["new_verified_URLs"]=0
        row["not_retail_approved"]=True
        if row["media_frame_action_status"]:
            row["stage"]="FRAME_LEVEL_QUARANTINE_OR_CATALOG_MISMATCH_HOLD"
        if all(row["release_gate_evidence"].values()):
            approved_release.append(family)
    require(len(approved_release)==0,"Unexpected proposed publishing of unapproved images")
    out={
      "version":"v2975","source_checkpoint":"v2974","date_kst":"2026-11-06",
      "project":"Shopee Thumbnail Creator PRO | inventory 82 SKU / 41 groups",
      "catalog_units_verified_for_families":list(manufacturer_units.keys()),
      "manual_archived_photograph_duplicate_confirmed":{"family":"pending-21","slot_3_SHA256":archived[2]["SHA256"],
        "slot_4_SHA256":archived[3]["SHA256"],"both_archived_original_SHA_paths_recovered":True,
        "visual_scene_same":True,"different_crop":True,
        "frame3_preserve":True,"frame4_quarantine_for_retail":True},
      "source_photo_hash_different_does_not_mean_independent_scene":True,
      "release_gate_required_evidence":gate_conditions,
      "new_retail_approvals":len(approved_release),
      "new_public_URLs":0,
      "parent_11_published_families_preserved":True,
      "parent_55_verified_public_URLs_preserved":True,
      "old_JPGs_overwritten":0,"new_unlicensed_binary_uploaded":0,
      "public_GitHub_QA_source_control":"JSON only; never write new unlicensed source photo to public QA branch",
      "frame_actions":holds,
      "families":[groups[k] for k in sorted(groups)],
      "next_actions":[
         "pending-21: preserve frame 3; only replace visually repeating frame 4 after true pack identity and licensed distinct source/factual card verified",
         "pending-12: official 15mL catalog, hold obsolete 15g marketing copy; no conversion; verify physically stocked package",
         "pending-05 and pending-07: official full-size 15g x2 is documented; physical packaging edition and gifts still independent blockers",
         "pending-08: 01-20 reference JPG/alpha confirmed; do not allow 21-26 on any public product variations",
         "Leave six preflight-staged five-source-photo groups intact, continue commercial rights and original MK resolution, not repetitive download"
      ],
      "final_excel_not_shared":True
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"release-gate-and-frame-actions.json").write_text(json.dumps(
        {"catalog_units":manufacturer_units,"frame_actions":holds,"release_gate_required_evidence":gate_conditions,
            "published_eligible_families":approved_release,"must_not_publish":sorted(groups)},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2975","frame4_duplicate_quarantined":True,
         "manufacturer_product_catalogs":len(manufacturer_units),
         "product_families":len(groups),"publish_eligible":0,"public_URLs_new":0}))
if __name__=="__main__":main()
