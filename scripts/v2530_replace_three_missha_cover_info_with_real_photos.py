#!/usr/bin/env python3
"""v2530: Targeted source-photo replacement of three overly repetitive info cards
for MISSHA Magic Cushion Cover Lasting 15g in prior v2528 QA corpus.
Three unmodified genuine 15g physical product scenes; never alter product pixels
or fabricate packaging. Other 152 JPGs must be BYTE IDENTICAL.
Merchant photo rights, seller stock edition, brand-logo original remain QA hold.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import hashlib,json,shutil
B=Path("v2530-base-155/review-JPG-by-family")
S=Path("v2530-real-photo-sources")
O=Path("v2530-155-photo-corrected-QA")
T=O/"review-JPG-by-family"
assert B.is_dir() and S.is_dir()
shutil.copytree(B,T)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
mapping=[
(1,"N21-pink-box-and-compact.jpg","N21 original pastel compact and carton"),
(2,"N23-pink-box-and-compact.webp","N23 original pastel compact and carton"),
(4,"N21-N23-open-puffs-packages.jpg","Actual open cushion showing puff and cases"),
]
replaced=[]
for slot,name,role in mapping:
 source=S/name;assert source.is_file(),source
 source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
 im=Image.open(source).convert("RGB")
 if slot==1:assert im.size==(1000,1000) and source_sha=="ce123eb796d93bcfc441789189a72f7a0b497605bbeab180fbdf9360448319a8"
 if slot==2:assert im.size==(750,750) and source_sha=="e0e63ac515fcb04f5d0a951fb06f4f2f7dd75243dadee420edbff78757d1e3ba"
 if slot==4:assert im.size==(1024,1024) and source_sha=="5eb8097f6bbc936dfa27d67a376ac455ed779b89e6ef871f9f6394edcc6cb512"
 # Only scale authentic original photographic pixels, do not overlay invented product content.
 img=ImageOps.fit(im,(1080,1080),Image.Resampling.LANCZOS)
 old=list((T/"pending-01").glob(f"{slot:02d}_*.jpg"))
 assert len(old)==1,(slot,old)
 old_sha=hashlib.sha256(old[0].read_bytes()).hexdigest()
 old[0].unlink()
 dst=T/"pending-01"/f"{slot:02d}_v2530-real-MISSHA-cover-lasting-photo.jpg"
 img.save(dst,"JPEG",quality=92,optimize=True,subsampling=0)
 assert Image.open(dst).size==(1080,1080) and dst.stat().st_size<2_000_000
 replaced.append({"slot":slot,"new":str(dst.relative_to(O)),"original_source":name,"original_source_sha256":source_sha,
 "new_sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"previous_info_sha256":old_sha,"role":role})
prior=list(B.glob("pending-*/*.jpg"));current=list(T.glob("pending-*/*.jpg"))
assert len(prior)==155 and len(current)==155
changed_slots={x["slot"] for x in replaced}
same_count=0
for f in prior:
 slot=int(f.name.split("_")[0])
 if f.parent.name=="pending-01" and slot in changed_slots:continue
 copied=T/f.relative_to(B)
 assert copied.is_file() and copied.read_bytes()==f.read_bytes(),str(f)
 same_count+=1
assert same_count==152
counts={f.name:len(list(f.glob("*.jpg"))) for f in T.glob("pending-*")}
assert len(counts)==30
assert all(counts[f"pending-{i:02d}"]==(6 if i in (1,2,4,6,7) else 5) for i in range(1,31))
for f in current:
 im=Image.open(f);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and f.stat().st_size<2_000_000
manifest={"version":"v2530","date":"2026-11-04","target_family":"pending-01","original_QA_total":155,
"new_QA_total":155,"unchanged_JPG_byte_identical":152,"genuine_photographic_replacements":replaced,
"real_photo_shots_different":3,"all_30_family_counts_retained":True,"old_55_published_URLs_unchanged":True,
"commercial_photo_reuse_rights_verified":False,"owner_stock_pack_edition_verified":False,
"original_MK_logo_available":False,"final_sale_approval":False,"public_urls_added":0,"excel_created_or_shared":False}
O.mkdir(exist_ok=True)
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"original_files":155,"real_photo_replacements":3,"unchanged_bytes":152,"sales_ready":False}))
