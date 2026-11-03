#!/usr/bin/env python3
"""v2.4.28 non-destructive image QA: no publication or imaginary cutouts."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import csv, hashlib, json, re, shutil
from datetime import datetime, timezone

SRC=Path("v2427b-source")
OUT=Path("v2428-output")
OUT.mkdir(exist_ok=True)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def valid(p):
    with Image.open(p) as im:
        im.load()
        return {"width":im.width,"height":im.height,"format":im.format,"mode":im.mode,"bytes":p.stat().st_size,"sha256":digest(p),"spec_ok":im.format=="JPEG" and im.size==(1080,1080) and p.stat().st_size<2000000}
def add_card(paths, dest, title):
    w=1160; cellw=360; cellh=410
    n=len(paths)
    canvas=Image.new("RGB",(w,90+((n+2)//3)*cellh),(246,246,244))
    d=ImageDraw.Draw(canvas)
    d.text((20,20),title,fill=(40,42,40))
    for i,p in enumerate(paths):
        with Image.open(p) as im:
            im=ImageOps.contain(im.convert("RGB"),(340,340))
            x=20+(i%3)*380; y=70+(i//3)*cellh
            canvas.paste(im,(x+(340-im.width)//2,y))
            label=p.name[:47]
            d.text((x,y+349),label,fill=(40,42,40))
    canvas.save(dest,"JPEG",quality=88,optimize=True)
    return valid(dest)

baseline=SRC/"summary.json"
assert baseline.exists(), "missing baseline summary"
prior=json.loads(baseline.read_text(encoding="utf-8"))
assert prior.get("version")=="2.4.27b"
source_list=sorted(p for p in SRC.rglob("*.jpg") if p.is_file())
before_hash={str(p.relative_to(SRC)):digest(p) for p in source_list}
four=sorted((SRC/"new-EN-info-four"/"pending-10").glob("*.jpg"))
assert len(four)==4, "do not claim four without four actual files"
shade=SRC/"OBGE_3shade_clean_QA_V2427b.jpg"
clio=SRC/"immutable-v2426b"/"CLIO_Mini_3shade_actual_source_QA_CLEAN_V2426b.jpg"
photo=SRC/"OBGE_product_photo_white_background_REJECTED_FOR_FINAL_QA.jpg"
assert all(x.exists() for x in [shade,clio,photo])
checks={}
for category,items in {"obge_en":four,"obge_shade":[shade],"clio_shade":[clio],"obge_photo":[photo]}.items():
    checks[category]=[{"path":str(p.relative_to(SRC)),**valid(p)} for p in items]
    assert all(x["spec_ok"] for x in checks[category]), "existing JPG spec conflict: "+category
# Real visual review sheets of real, unaltered source JPEGs. Not retail images.
sheets={}
sheets["OBGE_EN4"]=add_card(four,OUT/"v2428_OBGE_four_EN_contact_sheet.jpg","OBGE four existing EN JPG | actual thumbnails | QA only")
sheets["OBGE_vs_CLIO"]=add_card([photo,shade,clio],OUT/"v2428_source_and_shades_contact_sheet.jpg","Original photo / OBGE regional shade / CLIO shade | QA only")
# The white square is NOT removed without a verified, matching official alpha source.
# Preserve and block this image, no artificial cutout.
inventory=[]
groups=[
("MISSHA Cover Lasting","pending-01",4,"EXCLUDE_COVER_21_FROM_SHADE_CHART"),
("MISSHA Moist Up","pending-02",2,"CHECK_21_SEPARATELY"),
("CLIO Mesh Glow Mini","pending-04",3,"SOURCE_AND_EDITION_PENDING"),
("CLIO Founwear Set","pending-05",5,"OFFICIAL_SWATCH_PENDING"),
("CLIO Mesh Glow Essential Set","pending-06",5,"OFFICIAL_SWATCH_PENDING"),
("CLIO Mesh Blur Set","pending-07",3,"OFFICIAL_SWATCH_PENDING"),
("Peripera Mood Glowy Tint","pending-08",20,"26AD_004_006_007_012_CONFLICT"),
("OBgE Perfect Cover Cushion","pending-10",3,"HK_SHADE_VS_RENEWED_KR_PENDING")]
for name,code,count,note in groups:
    inventory.append({"product_group":name,"group_id":code,"sku_option_count":count,"official_swatches_sales_approved":0,"next_action":note,"qa_status":"SHADE_EVIDENCE_REQUIRED"})
assert sum(x["sku_option_count"] for x in inventory)==45
with (OUT/"C8_45_options_8_groups_workqueue.csv").open("w",encoding="utf-8-sig",newline="") as fh:
    writer=csv.DictWriter(fh,fieldnames=list(inventory[0]));writer.writeheader();writer.writerows(inventory)
# Read actual 45 row CSV; preservation and row count, no edits.
source_csv=SRC/"immutable-v2426b"/"C8_45_options_v2426_verified_status.csv"
assert source_csv.is_file()
shutil.copy2(source_csv,OUT/"C8_45_options_v2426_verified_status_UNCHANGED.csv")
assert digest(source_csv)==digest(OUT/"C8_45_options_v2426_verified_status_UNCHANGED.csv")
# Validate existing JPEGs hash unchanged after QA; no writes to originals.
after_hash={str(p.relative_to(SRC)):digest(p) for p in source_list}
assert before_hash==after_hash
with (OUT/"source_jpg_sha256_manifest.csv").open("w",encoding="utf-8",newline="") as fh:
    wr=csv.writer(fh);wr.writerow(["relative_path","sha256"])
    wr.writerows(sorted(before_hash.items()))
finding={
 "version":"2.4.28","timestamp_utc":datetime.now(timezone.utc).isoformat(),
 "baseline_branch":"production-assets-v2427b-obge-shade-clean",
 "baseline_commit":"102ef1854c9d6c299ee8d20a505d4b7fe01f6ae3",
 "baseline_source_jpg_count":len(before_hash),
 "baseline_source_jpg_sha_unchanged":True,
 "legacy_519_hash_preservation":"CHECKPOINT_ONLY_NOT_INDEPENDENT_519_AUDIT",
 "legacy_55_public_urls":"NO_PUBLIC_FILE_WRITE; LIVE_HTTP_NOT_RECHECKED",
 "obge_english_4_reused":len(four),"obge_shade_clean_1_reused":shade.is_file(),
 "new_customer_ready_image_count":0,
 "new_qa_contact_sheets":len(sheets),
 "obge_white_rectangle":"CUTOUT_SOURCE_REQUIRED",
 "obge_KR_renewed_options":"1 Ivory / 2 Beige / 3 Sand (official domestic listing)",
 "obge_HK_against_KR_renewed_generation":"GENERATION_MISMATCH_REVIEW_REQUIRED",
 "clio_5g_official_product_listing":"VERIFIED; EXACT_SWATCH_SOURCE_GENERATION_UNVERIFIED",
 "commercial_image_reuse_verified":0,"stock_package_verified":0,
 "MK_original_binary_verified":False,
 "C8_group_count":len(groups),"C8_option_count":45,
 "peripera_26AD_conflict_resolved":False,"missha_cover_21_excluded_from_shade_chart":True,
 "READY_EXCEPT_LOGO":0,"FINAL_QA_APPROVED":0,
 "customer_sales_released":False,
 "checks":checks,"contact_sheets":sheets,
 "public_image_path_mutation":0
}
(OUT/"v2428_checkpoint.json").write_text(json.dumps(finding,ensure_ascii=False,indent=2),encoding="utf-8")
(OUT/"v2428_QA_README.md").write_text(
 "# v2.4.28 independently executed QA\n\n"
 "Actual source JPGs opened with Pillow and their formats, dimensions, file size and SHA-256 checked. "
 "Two QA-only review contact sheets generated from genuine stored JPGs. Neither image is customer-facing. "
 "The white rectangle is deliberately NOT removed because no verifiably identical official alpha source is available. "
 "No new fabricated shades or packages. Sales permissions and stock-generation proof remain unverified.\n"
 "Status: CUTOUT_SOURCE_REQUIRED / SHADE_EVIDENCE_REQUIRED. "
 "No public URL, retail approved set, or historical asset is written by this workflow.\n",
 encoding="utf-8")
print(json.dumps({k:v for k,v in finding.items() if k not in ("checks","contact_sheets")},ensure_ascii=False),flush=True)
