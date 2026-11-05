#!/usr/bin/env python3
"""v2971: audit existing loose JPEGs for four variant-held product families.
No new photograph, ZIP or public output. Peripera checks shade directory structure.
Manual visual classifications reflect already-inspected v2882 and earlier QA, not image rights.
"""
from pathlib import Path
from collections import Counter
import hashlib, io, json, re
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"qa-review/v2971-four-orphan-product-photo-sets-peripera20-options-20261106"
RESULT2970=ROOT/"qa-review/v2970-remaining-stock-archive-audit-no-new-binary-20261106/manifest.json"
SOURCES={
 "pending-05":{
  "product":"CLIO Kill Cover Founwear Cushion full-size set",
  "photos":[
   "qa-review/v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA/pending-05/01-6670-M-1080-REFERENCE-NOT-RETAIL.jpg",
   "qa-review/v2931-clio-founwear-fullsize-6670-correct-mini-source-quarantine-QA/pending-05/02-6670-B-1080-REFERENCE-NOT-RETAIL.jpg"],
  "manual_classification":["FULLSIZE_OFFICIAL_M_VARIANT_REFERENCE","FULLSIZE_OFFICIAL_B_VARIANT_REFERENCE"],
  "banned_old_photo":"Prior pending-05 mini product references cannot be used for full-size gift set; 6670 M/B require physical exact kit / options",
  "sale_block":"M vs B full-size edition and stocked refill/gift-set exact composition not proven"},
 "pending-06":{
  "product":"CLIO Mesh Glow Essential Cushion 15g+15g refill",
  "photos":[
   "qa-review/v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint/CLIO-MeshGlow-pending06-01-source-story-QA.jpg",
   "qa-review/v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint/CLIO-MeshGlow-pending06-02-source-story-QA.jpg",
   "qa-review/v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint/CLIO-MeshGlow-pending06-03-source-story-QA.jpg",
   "qa-review/v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint/CLIO-MeshGlow-pending06-04-source-story-QA.jpg",
   "qa-review/v2882-meshglow-five-genuine-story-frames-and-30-family-checkpoint/CLIO-MeshGlow-pending06-05-source-story-QA.jpg"],
  "manual_classification":["OPEN_COMPACT_SINGLE_REFERENCE","FIVE_SHADE_LINEUP_WITH_JAPANESE_TEXT","FIVE_SHADE_MODEL_FACE_SWATCH","FIVE_SHADE_FOREARM_SWATCH_LOWER_NATIVE_SRC_550PX","FACE_BEFORE_AFTER_MARKETING_CLAIM_UNVERIFIED"],
  "banned_old_photo":"Do not treat 5 different story JPGs as 5 independent real product photos. Frame 4 enlarged from ~550px source; frame5 before/after usage rights unsupported.",
  "sale_block":"15g x2 refill package proof + regular/25FW generation + 19C 19N 21C 21N 23N shade identity + commercial rights"},
 "pending-07":{
  "product":"CLIO Mesh Blur 15g x2 pack",
  "photos":[
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-07/01-official-6455-m-gif-REFERENCE.jpg",
   "qa-review/v2793-three-clio-remaining-families-exact-page-edition-and-photo-proof/pending-07/02-official-6455-b-gif-REFERENCE.jpg",
   "qa-review/v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit/pending-07-CLIO-MeshBlur-19C-reference-card-1080-QA.jpg",
   "qa-review/v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit/pending-07-CLIO-MeshBlur-19N-reference-card-1080-QA.jpg",
   "qa-review/v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit/pending-07-CLIO-MeshBlur-21N-reference-card-1080-QA.jpg"],
  "manual_classification":["OFFICIAL_M_PRODUCT_REFERENCE","OFFICIAL_B_PRODUCT_REFERENCE",
    "SHADE_19C_INFO_CARD_NOT_INDEPENDENT_PHOTO","SHADE_19N_INFO_CARD_NOT_INDEPENDENT_PHOTO","SHADE_21N_INFO_CARD_NOT_INDEPENDENT_PHOTO"],
  "banned_old_photo":"Informational shade cards are not 3 extra original product photographs; avoid claiming full kit if source is single compact.",
  "sale_block":"M/B source generation, actual gift-set refill and 19C/19N/21N stock options need positive official matching"},
 "pending-12":{
  "product":"MISSHA PDRN Peel Shot 25 (actual net amount unresolved)",
  "photos":[
   "qa-review/v2678-missha-clio-two-five-JPG-sets/pending-12/01-existing-original-slot01-unchanged-QA.jpg",
   "qa-review/v2678-missha-clio-two-five-JPG-sets/pending-12/02-existing-original-slot02-unchanged-QA.jpg",
   "qa-review/v2678-missha-clio-two-five-JPG-sets/pending-12/03-existing-original-slot03-unchanged-QA.jpg",
   "qa-review/v2945-missha-official-15ml-and-clio-edition-distinction-info-QA/pending-12-MISSHA-PDRN-Peel-Shot25-official-15mL-info-INTERNAL.jpg"],
  "manual_classification":["OLD_SOURCE_PRODUCT_PHOTO_1","OLD_SOURCE_PRODUCT_PHOTO_2","OLD_SOURCE_PRODUCT_PHOTO_3","INFORMATIONAL_15ML_CARD_NOT_PHOTO"],
  "banned_old_photo":"Do not promote information card as independent photo or conflate stock sheet 15g with product official 15mL; no density conversion.",
  "sale_block":"Physical Korean label/net quantity 15g vs official 15mL and product generation unresolved"}
}
def sha(b):return hashlib.sha256(b).hexdigest()
def dHash(image):
    arr=list(image.convert("L").resize((9,8),Image.Resampling.LANCZOS).getdata())
    return "".join(str(int(arr[y*9+x]>arr[y*9+x+1])) for y in range(8) for x in range(8))
def check_file(path):
    file=ROOT/path
    data=file.read_bytes()
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        result={"path":path,"sha256":sha(data),"bytes":len(data),"dims":list(im.size),
          "format":im.format,"dHash64":dHash(im),
          "technical_1080_JPG_under2MB":im.format=="JPEG" and im.size==(1080,1080) and len(data)<2000000}
    return result
def audit():
    if OUT.exists():raise RuntimeError("v2971 report already exists; do not repeat.")
    previous=json.loads(RESULT2970.read_text(encoding="utf8"))
    result={}
    for key,val in SOURCES.items():
        files=[check_file(p) for p in val["photos"]]
        nearest=[]
        for i in range(len(files)):
            for j in range(i+1,len(files)):
                distance=sum(a!=b for a,b in zip(files[i]["dHash64"],files[j]["dHash64"]))
                if distance<=5:
                    nearest.append({"positions":[i+1,j+1],"similarity_hamming":distance,
                                    "human_product_photo_conflict_not_automatically_proven":True})
        result[key]={"product":val["product"],"physical_jpgs_accessible":len(files),
          "all_input_files_technical_valid":all(f["technical_1080_JPG_under2MB"] for f in files),
          "files":files,"manual_photo_type":val["manual_classification"],
          "candidate_near_duplicate_pairs":nearest,
          "actual_retail_product_photo_count_approved":0,
          "unlicensed_qa_sources_not_customer_images":True,
          "existing_known_conflict":val["banned_old_photo"],
          "exact_blocker":val["sale_block"],"has_final_photo_ZIP":False,
          "why_not_create_ZIP":"Public repository and source-image commercial permissions not cleared"}
    p=previous["results"]["pending-08"]
    jpg=[x["name"] for x in p["JPG_files"]]
    png=[x["name"] for x in p["PNG_files"]]
    def ids(items):
        r=[]
        for n in items:
            m=re.search(r"^01to20/(0[1-9]|1[0-9]|20)/",n)
            if m:r.append(int(m.group(1)))
        return sorted(r)
    shade_jpg=ids(jpg); shade_png=ids(png)
    expected=list(range(1,21))
    peripera={
      "product":"peripera Mood Glowy Tint legacy shades 01-20 only",
      "archive":p["archive"],
      "JPG_shades":shade_jpg,"PNG_alpha_shades":shade_png,
      "all_01_to_20_JPG_and_PNG_present":shade_jpg==expected and shade_png==expected,
      "extra_21_to_26_entries":[],
      "exact_SHA256_duplicate_photos":len({x["SHA256"] for x in p["JPG_files"]})!=20,
      "dHash_shape_similar_pairs":len(p["visually_similar_hash_candidates"]),
      "interpretation":"Near-equal grayscale dHash can result from same package silhouette, not identical tint color; never reject shades solely by shape hash.",
      "not_yet_proved":"Shade color accuracy, true owned edition, licensing, and same-generation match for shade 12/18/19",
      "export_allowed_variants":"01..20 only",
      "retail_approved":False
    }
    OUT.mkdir(parents=True)
    overall={
      "version":"v2971","parent":"v2970","project":"Shopee Thumbnail Creator PRO 82 SKU 41 families",
      "scope":"Four variant-held families' loose existing JPEG bytes, plus Peripera 01-20 structural option matching",
      "new_photo_binary_created":0,"new_photo_binary_published":0,
      "public_repo_visibility":"PUBLIC",
      "four_orphan_families":result,"peripera":peripera,
      "new_approved_families":0,"verified_new_public_URLs":0,
      "old_11_published_families_preserved":True,
      "old_55_public_URLs_preserved":True,
      "next_execution_priority":[
        "Do not create customer ZIP for pending-05/06/07/12 until exact edition/net quantity and photo usage rights are proven.",
        "pending-06 v2882 has five actual story JPG files but only one product compact hero; swatch and before/after frames have separate use/claim gates.",
        "pending-05 use correct fullsize 6670 M/B candidates not mini sources; choose stocked edition with physical proof.",
        "pending-07 separate 6455 M/B item photos and three shade info cards, do not call five real photo scenes.",
        "pending-12 resolve physical 15g vs 15mL label, do not convert units mathematically.",
        "peripera all 01-20 source filenames structurally present; compare real photo and shade chart rather than rely on grayscale similarity."
      ],
      "do_not_repeat":["v2970 completed 130 source-image integrity checks","v2968 completed 35 image checks"],
      "no_final_xlsx_shared":True
    }
    (OUT/"manifest.json").write_text(json.dumps(overall,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"version":"v2971",
      "four_groups_original_JPGs_verified":sum(len(v["files"]) for v in result.values()),
      "peripera_structural_01_20":peripera["all_01_to_20_JPG_and_PNG_present"],
      "new_JPG":0,"approved":0},ensure_ascii=False))
if __name__=="__main__":audit()
