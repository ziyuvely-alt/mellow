#!/usr/bin/env python3
"""v2536 selective ONE-PHOTO substitution into existing v2532 156-JPG QA corpus.
Pending-13 frame 04 repeated 30ml net content from frame 01.
Use captured authentic PDRN NAD+ 30ml serum laboratory still-life photography.
Keep 155 untouched photos byte-for-byte; no product generation or fake packages.
Never publish retailer images until commercial permissions and owned stock match.
"""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib,shutil,json
B=Path("v2536-existing-156/review-JPG-by-family")
S=Path("v2536-source-originals/actual-product-laboratory.png")
assert B.is_dir() and S.is_file()
assert hashlib.sha256(S.read_bytes()).hexdigest()=="ce983ceb01360f82b31bf112a430eed170e787a6e762b32537b4f34f5b715969"
original=Image.open(S);original.load();assert original.format=="PNG" and original.size==(1500,1500)
O=Path("v2536-156-missha-30ml-serum-one-photo-repair")
D=O/"review-JPG-by-family"
shutil.copytree(B,D)
old=list((D/"pending-13").glob("04_*.jpg"))
assert len(old)==1,old
old_hash=hashlib.sha256(old[0].read_bytes()).hexdigest()
old[0].unlink()
p=D/"pending-13/04-v2536-true-missha-pdrn-serum-laboratory-photo.jpg"
photo=original.convert("RGB").resize((1080,1080),Image.Resampling.LANCZOS)
photo.save(p,"JPEG",quality=92,optimize=True,subsampling=0)
image=Image.open(p);image.load();assert image.format=="JPEG" and image.size==(1080,1080) and p.stat().st_size<2000000
before=list(B.glob("pending-*/*.jpg"));after=list(D.glob("pending-*/*.jpg"))
assert len(before)==156 and len(after)==156,(len(before),len(after))
unchanged=0
for f in before:
 if f.parent.name=="pending-13" and f.name.startswith("04_"):continue
 assert f.read_bytes()==(D/f.relative_to(B)).read_bytes(),str(f)
 unchanged+=1
assert unchanged==155
counts={d.name:len(list(d.glob("*.jpg"))) for d in D.glob("pending-*")}
assert len(counts)==30
assert counts["pending-13"]==5
assert all(counts[f"pending-{n:02d}"]==(6 if n in (1,2,4,5,6,7) else 5) for n in range(1,31))
for file in after:
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2000000
for family in counts:
 shas=[hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/family).glob("*.jpg")]
 assert len(shas)==len(set(shas))
manifest={"date":"2026-11-04","version":"v2536","family":"pending-13","product":"MISSHA Camellia PDRN NAD+ Firming Repair Serum 30mL",
"replaced_slot":4,"previous_duplicate":old_hash,"new_photo":str(p.relative_to(O)),
"new_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
"original_photo_url":"https://lacosmetique.com.au/cdn/shop/files/AdelineProductListing_35.png?v=1779428609&width=1500",
"original_photo_sha256":"ce983ceb01360f82b31bf112a430eed170e787a6e762b32537b4f34f5b715969",
"prior_156_total_retained":156,"old_files_byte_identical":155,"replacements":1,"total_qa_JPGs":156,
"commercial_photo_rights":False,"stock_packaging_edition_match":False,"mk_original_logo_applied":False,
"sale_final_QA":False,"existing_55_public_urls_unchanged":True,"new_public_url_count":0,
"excel_created_or_shared":False}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"total":156,"old_unchanged":155,"actual_photo_replacements":1,"published":False}))
