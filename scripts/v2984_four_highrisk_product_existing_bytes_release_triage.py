#!/usr/bin/env python3
"""v2984 four high-risk stock families: SHA validate only NEW choice of existing assets,
reconcile wrong-kit photos, make append-only metadata. No redistribution, new images,
fake MK, unproven unit conversions or Render deploy.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,io
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2984-four-highrisk-families-actual-photo-reuse-and-release-holds-20261106"
refs={
 "v2982":"qa-review/v2982-30-family-restart-with-four-fiveframe-corrections-20261106/manifest.json",
 "v2983":"qa-review/v2983-obge-doubleessence-photo-free-dual-formula-replacement-20261106/manifest.json",
 "v2931":"qa-review/v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA/manifest.json",
 "v2971":"qa-review/v2971-four-orphan-product-photo-sets-peripera20-options-20261106/manifest.json",
 "v2677":"qa-review/v2677-three-obge-five-JPG-source-led-QA-sets/manifest.json",
 "v2678":"qa-review/v2678-missha-clio-two-five-JPG-sets/manifest.json",
 "v2945":"qa-review/v2945-missha-official-15ml-and-clio-edition-distinction-info-QA/manifest.json",
 "v2780":"qa-review/v2780-four-unfinished-missha-obge-photo-first-QA/pending-11/manifest.json",
}
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
def asset(path,expected=None,kind="REFERENCE_PHOTO",note=""):
    dat=(ROOT/path).read_bytes()
    if expected is not None and sha(dat)!=expected:raise RuntimeError("Existing source hash changed: "+path)
    with Image.open(io.BytesIO(dat)) as im:
        im.load();dims=list(im.size);fmt=im.format
    if fmt!="JPEG" or dims!=[1080,1080] or len(dat)>=2_000_000:
        raise ValueError("Bad 1080 JPG: "+path)
    return {"source":path,"sha256":sha(dat),"bytes":len(dat),
       "dimensions":dims,"format":fmt,"kind":kind,"review_note":note,
       "technical_pass":True,"redistribution_rights_verified":False if kind=="REFERENCE_PHOTO" else True,
       "authentic_MK_embedded":False}
def main():
    if OUT.exists():raise RuntimeError("Already ran v2984, refuse to regenerate.")
    m={k:load(v) for k,v in refs.items()}
    if m["v2982"]["version"]!="v2982" or len(m["v2982"]["pending_product_families"])!=30 or m["v2983"]["version"]!="v2983":
        raise RuntimeError("Stale/mismatched baseline")
    result={}
    # CLIO fullsize official 6670 (M/B original 502/600 pixel, upsized QA only).
    c05=m["v2931"]["new_fullsize_sources"]
    sources05=[]
    for r in c05:
        q=asset(r["preview_path"],r["preview_sha256"],note="Correct 6670 model source, but native 502/600px and same core scene M/B")
        q["native_px"]=r["native_pixels"];q["physical_stock_edition"]=False
        q["not_retail_ready"]=True;sources05.append(q)
    if len(sources05)!=2:raise RuntimeError("Missing full-size 6670 previews")
    result["pending-05"]={
       "product":"CLIO Founwear cushion fullsize 15g + 15g refill",
       "chosen_reference_JPGs":sources05,"existing_refs_2_not_5_proven":True,
       "known_wrong_prior_sources":["5750 MINI 5g","7108 MINI 5g"],
       "distinct_product_scene_count_proven":1,
       "QA_stage":"ONLY_TWO_CORRECT_PRODUCT_ID_LOW_NATIVE_REFERENCES; DO_NOT_PROMOTE_5PHOTO",
       "official_item":"https://clubclio.co.kr/shop/goodsView/0000006670",
       "official_net":"15g x 2, main compact + refill",
       "current_promo_puff_gift":"NOT_ASSUMED_IN_OWNED_STOCK",
       "current_new_color_options_20261012":"DO_NOT_ADD_NEW_15C_20N_22N_TO_STOCK_UNLESS_CONFIRMED",
       "physical_owned_stock_variant_verified":False,
       "photo_rights_verified":False,"published":False
    }
    # Mesh Blur 6455: 2 photos near identical plus 3 independent label CARDS (not photos).
    c07=m["v2971"]["four_orphan_families"]["pending-07"]["files"]
    s07=[asset(x["path"],x["sha256"],
         "REFERENCE_PHOTO" if i<2 else "EXISTING_INFORMATION_CARD",
         "M/B same composition" if i<2 else "Shade name card; do not claim authentic swatch pixels")
         for i,x in enumerate(c07)]
    result["pending-07"]={
       "product":"CLIO Mesh Blur cushion fullsize 15g + 15g refill",
       "existing_JPGs":s07,
       "technically_available":5,"unique_photo_scene_count_proven":1,
       "three_shade_cards_not_photos":True,
       "QA_stage":"TECH_5FILES_MIXED_2_PHOTOS_3_CARDS_M_B_SIMILAR_HOLD",
       "official_item":"https://clubclio.co.kr/shop/goodsView/0000006455",
       "official_net":"15g x 2; option-specific contents vary",
       "physical_owned_variant_set_confirmed":False,"commercial_rights_confirmed":False,"published":False
    }
    # MISSHA 15ml: true source old shots + original nonphoto safe label/usage. NO 15g conversion.
    existing12=next(x for x in m["v2678"]["families"] if x["family"]=="pending-12")
    shots=existing12["files"][:3]
    base12="qa-review/v2678-missha-clio-two-five-JPG-sets/pending-12/"
    s12=[asset(base12+v["file"],v["sha256"],"REFERENCE_PHOTO") for v in shots]
    v15=next(x for x in m["v2945"]["results"] if x["family"]=="pending-12")
    s12.append(asset(v15["image"],v15["sha256"],"EXISTING_BRAND_15ML_QA_CARD","Brand catalog 15mL, not evidence stock 15G is equivalent"))
    v5=existing12["files"][4]
    s12.append(asset(base12+v5["file"],v5["sha256"],"EXISTING_ORIGINAL_LABEL_GUIDE","Directions card, not independent product photo"))
    result["pending-12"]={
       "product":"MISSHA PDRN NAD+ Renew Peel Shot 25",
       "candidate_source_5frame_set":s12,
       "photo_count":3,"original_info_card_count":2,
       "QA_stage":"FIVE_FRAME_TECH_PASS_PRODUCT_NET_15G_STOCK_VS_15ML_BRAND_HOLD",
       "brand_catalog_volume":"15mL","stock_legacy_record":"15g (unverified, not converted)",
       "brand_listing":"https://m.ableshop.kr/product/goods/view-goods?goodsId=BO00114236",
       "stock_printed_unit_verified":False,"photo_rights_verified":False,"published":False
    }
    # OBgE Double essence exactly one 100mL dual-chamber; preserve white-bottle photos
    # and replace dissimilar old golden/translucent packaging with brand-grounded ORIGINAL card.
    obge=m["v2677"]["families"][2]
    if obge["family"]!="pending-11":raise RuntimeError("Unexpected OBGE existing QA list")
    info=obge["frames"]
    prefix="qa-review/v2677-three-obge-five-JPG-source-led-QA-sets/pending-11/"
    hero=m["v2780"]["frames"][0]["path"]
    choice=[
      asset(hero,kind="REFERENCE_PHOTO",note="White single dual-chamber bottle candidate, actual user-owned edition not proven"),
      asset(prefix+info[1]["file"],info[1]["sha256"],"REFERENCE_PHOTO","Same white bottle with cream texture, user-owned generation unverified"),
      asset(prefix+info[2]["file"],info[2]["sha256"],"EXISTING_ORIGINAL_GENERIC_INFO","Original informational frame, no source photo"),
      asset(m["v2983"]["new_original_JPG"],m["v2983"]["new_original_SHA256"],"NEW_ORIGINAL_FORMULA_CORRECTION","50mL TONER+ESSENCE and 50mL LOTION+CREAM, one bottle, no photo"),
      asset(prefix+info[4]["file"],info[4]["sha256"],"EXISTING_ORIGINAL_USAGE_INFO","Product guide generic, no source photo")
    ]
    if len(set(x["sha256"] for x in choice))!=5:raise RuntimeError("Exact OBGE source duplicated")
    result["pending-11"]={
       "product":"OBgE All In One Double Essence 100mL",
       "candidate_source_5frame_set":choice,
       "photo_count":2,"original_info_card_count":3,
       "QA_stage":"FIVE_FRAME_TECH_PASS_ONE_BOTTLE_TWO_FORMULAS_EXACT_STOCK_AND_RIGHTS_HOLD",
       "one_bottle":"Yes, 2 formulas in one dual-chamber bottle",
       "formula_01":"Toner + Essence 50mL",
       "formula_02":"Lotion + Cream 50mL",
       "rejected_legacy":"v2923 old photo slot2 see-through golden bottle mismatches preferred white candidate; do not reuse until proved same owned edition",
       "official_item":"https://www.obge.co.kr/product/detail.html?cate_no=0&display_group=0&product_no=15",
       "formula_details":"https://www.yesstyle.com/en/obge-all-in-one-double-essence-100ml/info.html/pid.1128931980",
       "actual_physical_packaging_verified":False,
       "licensed_source_photo_redistribution":False,"original_MK_logo_verified":False,
       "published":False
    }
    counts={k:len(v.get("candidate_source_5frame_set",v.get("existing_JPGs",v.get("chosen_reference_JPGs",[])))) for k,v in result.items()}
    if counts!={"pending-05":2,"pending-07":5,"pending-12":5,"pending-11":5}:raise RuntimeError("Family counts mismatch: "+str(counts))
    report={
       "version":"v2984","parent":"v2983","project":"Shopee Thumbnail Creator PRO stock 82 SKU / 41 families",
       "true_new_original_image_this_sequence":"v2983 one formula photo-free JPG",
       "new_image_data_created_now":0,
       "existing_JPG_files_physically_opened_sha_checked_now":sum(counts.values()),
       "never_recreated_existing_image":True,
       "four_product_families_evaluated":list(result),
       "actual_new_retail_approvals":0,"new_public_URLs_verified":0,
       "prior_completed_family_count_immutable":11,"prior_URLs_immutable":55,
       "qa_rosters":result,
       "do_not_repeat":["v2678 MISSHA 3 original photos and 2 existing cards","v2677 OBGE 2 white photos / 2 existing info",
         "v2931 CLIO 6670 M/B low-res original source recovery",
         "v2983 new OBGE info original",
         "v2982 four corrected families preflight"],
       "next_action_queue":[
         "pending-11: do not redownload/generate new formula card; actual owned white bottle edition and rights, authentic MK to pass",
         "pending-12: physical stocked product label 15mL vs original 15g row, avoid numerical volume conversion",
         "pending-05: 6670 correct product original 502/600 native only, require suitable higher native authorized exact giftset pack photo; do not substitute MINI",
         "pending-07: 6455 official 15g x 2, 2 near-identical image scenes plus three info cards are not 5 true product photos",
         "All four retail HOLD until packaging/rights/MK/customer QA and versioned Render GET-SHA"
       ],
       "spreadsheet_shared":False
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"four-high-risk-product-source-frames.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2984","checked_existing_JPG":sum(counts.values()),
        "two_5slot_sets":["pending-11","pending-12"],"two_held_kit_families":["pending-05","pending-07"],
        "new_sale_approved":0,"old_URLs_protected":55}))
if __name__=="__main__":main()
