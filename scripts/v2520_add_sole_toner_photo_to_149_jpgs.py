#!/usr/bin/env python3
"""v2520 strictly incremental one-file addition to successfully consolidated v2518 149 JPEGs.
Never rewrite the 149 source files. Add fifth real Pixelpure Toner 200ml photo.
Recheck actual all 150 JPGs, per family slot counts, SHA duplicates, file sizes; output JSON QA.
Do not publish public URLs or Excel. No brand-logo, rights, physical-stock approval.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFont
import hashlib, json, shutil,io
BASE=Path("/tmp/v2520-baseline")
SOURCE=Path("/tmp/v2520-new-real-photo/05-real-bottle-held-over-water-200ml.jpg")
OUT=Path("v2520-30family-150-physical-JPG-QA")
assert (BASE/"review-JPG-by-family").is_dir()
assert SOURCE.is_file()
shutil.copytree(BASE/"review-JPG-by-family",OUT/"review-JPG-by-family",copy_function=shutil.copy2)
toner=OUT/"review-JPG-by-family/pending-27"
dst=toner/"05_v2519_original-real-bottle-held-over-water-200ml.jpg"
dst.write_bytes(SOURCE.read_bytes())
original=json.loads((BASE/"manifest.json").read_text())
files=list((OUT/"review-JPG-by-family").glob("pending-*/*.jpg"))
by={};fileinfo=[];dup=[]
for f in sorted(files):
 family=f.parent.name
 img=Image.open(f);img.load()
 size=f.stat().st_size
 assert img.format=="JPEG" and img.size==(1080,1080) and size<2000000,(str(f),img.size,size)
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 slot=int(f.name.split("_")[0])
 item={"family":family,"slot":slot,"path":str(f.relative_to(OUT)),"sha256":sha,"bytes":size}
 fileinfo.append(item)
 by.setdefault(family,[]).append(item)
for n in range(1,31):
 fam=f"pending-{n:02d}"
 assert len(by[fam])==5,(fam,len(by[fam]))
 slots=[x["slot"] for x in by[fam]]
 assert sorted(slots)==[1,2,3,4,5],(fam,slots)
 hashes=[x["sha256"] for x in by[fam]]
 assert len(set(hashes))==5,(fam,"identical JPG hash duplicate")
assert len(fileinfo)==150,len(fileinfo)
# Critical preservation check: 149 source files identical, same hashes
baseline_files={x["file"]:x["sha256"] for x in original["individual_frames"]}
for source_name,sha in baseline_files.items():
 f=OUT/source_name
 assert f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==sha,(source_name,"immutable source violation")
assert hashlib.sha256(dst.read_bytes()).hexdigest()=="87716e1d8f81c54610c9c05ffabf552dc0f1b79ec2aac71e21fecdcf0298c091"
# Copy existing 3 contact sheets byte-for-byte, build ONLY final pending-27 row contact
for f in BASE.glob("contact-families-*.jpg"):
 shutil.copy2(f,OUT/f.name)
ft=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
sheet=Image.new("RGB",(400*5,400),"#eeeeee");d=ImageDraw.Draw(sheet)
for col,item in enumerate(sorted(by["pending-27"],key=lambda x:x["slot"])):
 image=Image.open(OUT/item["path"]).convert("RGB")
 thumbnail=ImageOps.contain(image,(370,350))
 sheet.paste(thumbnail,(col*400+(400-thumbnail.width)//2,12))
 d.text((col*400+14,368),f"pending-27 / {item['slot']}",font=ft,fill="#252525")
sheet.save(OUT/"contact-pending-27-final-five.jpg",quality=88)
manifest={"version":"v2520","date":"2026-11-04","source_integrated_149_run_id":41700820012,
"source_integrated_149_branch":"production-assets-v2518-149-recovered-30family-qa",
"fifth_real_photo_run_id":41701283592,
"fifth_real_photo_branch":"production-assets-v2519-pixelpure-toner-fifth-photo",
"new_addition":{"family":"pending-27","slot":5,"file":str(dst.relative_to(OUT)),"sha256":hashlib.sha256(dst.read_bytes()).hexdigest()},
"total_review_jpg":len(fileinfo),"families":30,
"all_families_exactly_five":all(len(x)==5 for x in by.values()),
"all_families_sequential_1_to_5":True,
"retained_149_byte_identical":True,
"technical_JPEG_1080_2mb_pass":len(fileinfo),"technical_fail":0,
"sha_duplicates_within_family":dup,"file_records":fileinfo,
"original_55_published_urls_unchanged":True,"new_public_URLs_verified":0,
"legacy_11_completed_families_unchanged":True,
"actual_MK_logo_applied":False,
"photo_commercial_rights_verified":False,"actual_stock_package_edition_qa":False,
"perceptual_seller_safety_QA":False,"approved_seller_ready_families":0,
"all_150_images_final_sales_approved":False,
"excel_created_or_shared":False,
"notes":["All 30 families have 5 technical 1080px JPEG candidates, NOT 5 final brand-approved retail images.",
"Any wrongly sourced photo, incompatible product edition, missing verified official swatch or logo requires targeted repair before approval.",
"No public/images modifications. Retain all previously verified URLs."]}
(OUT/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({k:manifest[k] for k in ["total_review_jpg","families","all_families_exactly_five","retained_149_byte_identical","technical_fail","approved_seller_ready_families"]}))
