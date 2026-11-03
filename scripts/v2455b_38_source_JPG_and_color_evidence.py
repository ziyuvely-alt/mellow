#!/usr/bin/env python3
"""v2455b: preserve 36 previous exact JPGs and two newly brand-sourced OBgE facts,
plus factual source conflict evidence for MISSHA/Peripera. No images are re-rendered.
No spreadsheet file is created, exposed or uploaded.
"""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,zipfile
A=Path("prior-v2454b");B=Path("prior-v2455")
OUT=Path("v2455b-output");OUT.mkdir(exist_ok=True)
prev=json.loads((A/"v2454b-resumable-checkpoint.json").read_text())
new=json.loads((B/"v2455_checkpoint.json").read_text())
assert len(prev["manifest"])==36 and len(new["new_files"])==2
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for root,entries,key,hkey,origin in [
  (A,prev["manifest"],"file","SHA256","byte-identical-v2454b"),
  (B,new["new_files"],"file","sha256","byte-identical-v2455")]:
 for i in entries:
  gid=i.get("group_id","pending-22");source=root/i[key]
  assert source.is_file() and sha(source)==i[hkey],source
  with Image.open(source) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080) and source.stat().st_size<2000000
  dest=OUT/"all-38-verified-JPG-drafts"/gid/(origin+"__"+source.name)
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(source,dest)
  assert sha(dest)==i[hkey]
  rows.append({"group_id":gid,"file":str(dest.relative_to(OUT)),"sha256":i[hkey],
    "origin":origin,"commercial_photo_rights_verified":False,
    "actual_physical_stock_generation_verified":False,"full_sales_QA_approved":False})
assert len(rows)==38 and len(set(x["group_id"] for x in rows))==28
# Evidence from public authoritative sources verified separately. These references
# are strictly for review; no published retailer swatch content is copied into JPGs.
color_evidence={
 "peripera":{"product":"Mood Glowy Tint 4 g",
 "scope_requested":"01 through 20 only; 21+ and 26AD new edition excluded from current list",
 "current_brand_operated_retailer_reference":"https://m.gsshop.com/prd/prd.gs?ispre=Y&mseq=444059&prdid=1106843033&rank=10",
 "retailer_operator":"CLIO-operated official shop per retailer page",
 "listing_mentions_01_20_but_04_06_07_option_sources_not_confirmed":True,
 "current_listing_includes_21_plus":True,
 "no_04_06_07_official_same_generation_swatch_verification":True,
 "commercial_content_reuse_warning_on_source":True,
 "visual_swatch_chart_license_granted":False,
 "action":"Do not fabricate 04/06/07 or relabel 26AD; keep all uncertain options on hold"},
 "missha_cover_lasting":{
 "product":"MISSHA Magic Cushion Cover Lasting",
 "user_excluded_shade_21_in_current_shade_chart":True,
 "archived_hero_contains_shade_21":True,
 "archived_hero_permanently_excluded_from_sale_draft":True,
 "source":"https://m.cos-up.com/product/missha-%EB%AF%B8%EC%83%A4-%EB%A7%A4%EC%A7%81-%EC%BF%A0%EC%85%98-%EC%BB%A4%EB%B2%84-%EB%9E%98%EC%8A%A4%ED%8C%85-spf50-pa/1263/",
 "seller_source_shades_21_23_only":"Not evidence for 25/27 in same package generation",
 "shade_23_25_27_same_generation_officially_verified":False,
 "action":"Hold until exact official stock edition and 23/25/27 proven; do not reinsert 21"},
 "obge_300ml":{
 "official_source":"https://www.obge.co.kr/product/detail.html?cate_no=43&display_group=1&product_no=1251",
 "exact_ingredient_verification":"Panthenol Ectoin Sodium Hyaluronate Hyaluronic Acid and derivatives",
 "legitimate_jpg_frames":"4 fact-only cards saved; no real 300mL source bottle approved",
 "wrong_photo":"Historical PRODUCT_PHOTO_02 is a cosmetic cushion, rejected",
 "photo_rights":False,"real_bottle_generation_validated":False
 }
}
report={"version":"2.4.55b",
 "sources":["production-assets-v2454b-36-photo-and-fact-JPG-drafts","production-assets-v2455-two-obge-official-source-facts"],
 "prior_36_JPGs_byte_preserved":True,
 "new_2_verified_facts_byte_preserved":True,
 "all_JPG_source_SHA256_validated":38,
 "product_groups_with_any_photo_or_fact":28,
 "without_suitable_actual_product_photo":["pending-01","pending-08","pending-22"],
 "prior_531_source_JPGs_modified":0,
 "existing_published_55_URLs_modified":0,
 "official_shade_charts_approved":0,
 "commercial_photo_rights_verified":0,
 "fully_approved_five_or_six_frame_sale_sets":0,
 "all_previous_hard_holds_retain":True,
 "XLSX_files_created_or_shared":False,
 "new_source_conflict_evidence":color_evidence,
 "files":rows,
 "next":["Use genuine licensed same-edition official product photography for pending-01, pending-08, pending-22",
 "Verify exact 04/06/07 peripera source before any customer chart; no retailer art reuse without license",
 "Complete each 5 or 6 image family's commercial rights, stock/edition and manual visual QA"]
}
(OUT/"v2455b-current-38jpg-checkpoint.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
with zipfile.ZipFile(OUT/"v2455b_38_actual_JPG_QA_HOLD.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for r in rows:z.write(OUT/r["file"],arcname=r["file"])
 z.write(OUT/"v2455b-current-38jpg-checkpoint.json",arcname="v2455b-current-38jpg-checkpoint.json")
with zipfile.ZipFile(OUT/"v2455b_38_actual_JPG_QA_HOLD.zip") as z:
 assert len(z.namelist())==39 and z.testzip() is None
print(json.dumps({"version":report["version"],"checked_jpg":38,"families":28,"newly_generated":0,"sheets_shared":False,"approved":0}),flush=True)
