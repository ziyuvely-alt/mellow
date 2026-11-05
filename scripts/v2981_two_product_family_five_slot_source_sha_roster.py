#!/usr/bin/env python3
"""v2981 validate ten existing 1080 JPG files and create append-only two-family 5-slot QA storyboards.
Strictly metadata: no additional copies of unlicensed merchant pictures, no public Render, no invented swatches.
"""
from pathlib import Path
from PIL import Image
import hashlib,io,json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2981-two-product-family-5slot-byteverified-storyboards-20261106"
PATHS={
 "v2903":"qa-review/v2903-missha-BB-21-23-25-best-existing-source-option-QA/manifest.json",
 "v2838":"qa-review/v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA/manifest.json",
 "v2840":"qa-review/v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA/manifest.json",
 "v2979":"qa-review/v2979-missha-clio-two-original-shade-name-only-cards-20261106/manifest.json",
 "v2980":"qa-review/v2980-missha-clio-two-original-howto-not-photo-cards-20261106/manifest.json"
}
def sha(b):return hashlib.sha256(b).hexdigest()
def check(path,digest,slot,role,photo):
    data=(ROOT/path).read_bytes()
    if sha(data)!=digest:raise ValueError("old image SHA256 changed: "+path)
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        if im.size!=(1080,1080) or im.format!="JPEG" or len(data)>=2_000_000:raise ValueError("Bad actual archived JPG: "+path)
    return {"slot":slot,"photo":photo,"role":role,"existing_source_path":path,
            "source_SHA256":digest,"size":[1080,1080],"JPG_bytes":len(data),
            "technical_validated_now":True,
            "commercial_photo_rights":False if photo else True,
            "MK_original_logo_verified":False}
def main():
    if OUT.exists():raise RuntimeError("v2981 already exists; do not recreate")
    data={k:json.loads((ROOT/p).read_text(encoding="utf-8")) for k,p in PATHS.items()}
    if any(data[k].get("version")!=k for k in PATHS):
        raise RuntimeError("Mismatched baseline manifest; fail closed")
    m=data["v2903"];c=data["v2838"];c23=data["v2840"]
    sh={x["shade"]:x for x in m["source_images"]}
    if set(sh)!={"21","23","25"}:raise RuntimeError("Unexpected MISSHA photo shade identity")
    newshade={x["family"]:x for x in data["v2979"]["results"]}
    newhow={x["family"]:x for x in data["v2980"]["results"]}
    if set(newshade)!={"pending-03","pending-04"} or set(newhow)!={"pending-03","pending-04"}:
        raise RuntimeError("Missing one of the new original SHA checks")
    missha=[]
    for slot,shade in enumerate(("21","23","25"),1):
        photo=sh[shade]
        missha.append(check(photo["selected_copy"],photo["sha256"],slot,
            "EXISTING_SHADE_SPECIFIC_LEGACY_GOLD_PUMP_"+shade,True))
    missha.append(check(newhow["pending-03"]["JPG_path"],newhow["pending-03"]["SHA256"],4,
                         "ORIGINAL_ENGLISH_BRAND_USAGE_INSTRUCTIONS_NOT_PHOTO",False))
    missha.append(check(newshade["pending-03"]["JPG_path"],newshade["pending-03"]["JPG_SHA256"],5,
                        "ORIGINAL_NO21_NO23_NO25_SHADE_NAME_GUIDE_NO_SWATCH",False))
    clio=[]
    for slot,shade in enumerate(("21C","21N"),1):
        v=next(x for x in c["variants"] if x["shade"]==shade)
        frame=next(x for x in v["frames"] if x["slot"]==1)
        clio.append(check("qa-review/v2838-clio-mini5g-21C-21N-five-photo-no-customer-review-QA/"+frame["file"],
                      frame["sha256"],slot,"EXISTING_MINI_SHADE_LABELLED_REFERENCE_"+shade,True))
    v=next(x for x in c23["frames"] if x["slot"]==1)
    clio.append(check("qa-review/v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA/"+v["file"],
                   v["sha256"],3,"EXISTING_MINI_SHADE_LABELLED_REFERENCE_23N",True))
    clio.append(check(newhow["pending-04"]["JPG_path"],newhow["pending-04"]["SHA256"],4,
                       "ORIGINAL_ENGLISH_MINI_CUSHION_USAGE_GUIDE",False))
    clio.append(check(newshade["pending-04"]["JPG_path"],newshade["pending-04"]["JPG_SHA256"],5,
                       "ORIGINAL_21C_21N_23N_SHADE_NAMES_NO_SWATCH",False))
    byfam={"pending-03":missha,"pending-04":clio}
    for family,frames in byfam.items():
        if [x["slot"] for x in frames]!=[1,2,3,4,5] or len({x["source_SHA256"] for x in frames})!=5:
            raise ValueError("Duplicate or incorrect 5-slot composition: "+family)
    report={
      "version":"v2981","parent":"v2980","project":"Shopee Thumbnail Creator PRO 82 SKUs / 41 families",
      "previous_finished_product_families":11,"previous_verified_render_urls":55,
      "source_images_opened_and_sha_verified":10,
      "actual_sale_approved_frames":0,
      "new_binary_JPGs_created_now":0,
      "new_unlicensed_picture_files_uploaded_now":0,
      "new_Render_urls_verified_now":0,
      "two_source_preserving_5slot_internal_QA_storyboards":{
        "pending-03":{
          "product":"MISSHA M Perfect Cover BB Cream 50mL, legacy gold-pump packaging",
          "frame_count":5,"existing_shade_labelled_reference_photos":3,
          "new_original_non_photo_info_frames":2,
          "photo_origins_independently_licensed":False,
          "real_swatch_colors_verified":False,
          "source_identity_warning":"Existing 21/23/25 merchant sources show legacy bottles; actual owned edition not proven, official current product shade naming only.",
          "old_rejected_model_or_before_after_frames_included":False,
          "old_two_shade_23_25_only_chart_included":False,
          "frames":missha
        },
        "pending-04":{
          "product":"CLIO Kill Cover Mesh Glow Essential Cushion Mini 5g",
          "frame_count":5,"existing_shade_labelled_reference_photos":3,
          "new_original_non_photo_info_frames":2,
          "photo_origins_independently_licensed":False,
          "real_swatch_colors_verified":False,
          "source_identity_warning":"Mini 21C/21N/23N source files selected by merchant labels; shared compact imagery can remain visually similar and must not be relabeled as physical color swatches.",
          "old_duplicate_legacy_5frame_compact_views_included":False,
          "frames":clio
        }
      },
      "all_5slot_JPGs_technically_pass":True,
      "all_families_still_retail_HOLD":True,
      "reasons":["actual owned SKU packaging and edition not proven",
                 "retail rights to reuse the 3 older merchant photos in each storyboard not documented",
                 "authentic MellowKR original circular MK logo PNG not accessible",
                 "final independent customer-facing crop/copy proof and Render anonymous JPEG SHA not completed"],
      "next_actions":[
        "Do NOT recreate v2979 or v2980, do not redownload six historic option photos; both 5-slot QA source sets are technically complete.",
        "Resolve user-owned exact stock edition and commercial reuse permission for 3 merchant photos per family; original two text-only frames need not be relicensed.",
        "Obtain authentic original MellowKR MK binary from authorised user project source, never fabricate lookalike.",
        "Only once release gates pass, create versioned retail JPG and verify actual anonymous Render GET SHA256. Leave past 55 unchanged."
      ],
      "final_xlsx_shared":False
    }
    OUT.mkdir(parents=True)
    (OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    (OUT/"two-family-five-frame-source-of-truth.json").write_text(json.dumps(report["two_source_preserving_5slot_internal_QA_storyboards"],ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2981","total_SHA_validated_JPGs":10,
       "set_frames":{k:len(v) for k,v in byfam.items()},
       "original_11_and_55_protected":True,"new_published":0},ensure_ascii=False))
if __name__=="__main__":main()
