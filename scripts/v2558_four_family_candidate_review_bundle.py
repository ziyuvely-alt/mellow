#!/usr/bin/env python3
"""v2558 cross-family staged candidate pack QA.
Verify four source-backed new JPG proposals against unchanged v2548 156 images.
No source overwrite, no public URL publishing, no spreadsheet.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont,ImageStat,ImageChops
import hashlib,json,shutil
O=Path("v2558-four-family-draft-review");O.mkdir(exist_ok=True)
B=Path("v2558-base/review-JPG-by-family")
C=Path("v2558-candidates")
TARGETS=[
 {"family":"pending-21","slot":5,"path":"goodal/pending-21-slot05-package-photo-CANDIDATE.jpg","run":41751173910,"detail":"Goodal 30ml 25AD eye cream candidate"},
 {"family":"pending-16","slot":4,"path":"drg-old/pending16-04-original-70ml-jar-carton-CANDIDATE.jpg","run":41752270122,"detail":"DrG old 2022 70ml jar/carton"},
 {"family":"pending-15","slot":5,"path":"drg-mild/pending15-05-photo-plus-how-to-apply-CANDIDATE.jpg","run":41752451326,"detail":"DrG Green Mild Up 50ml application photo"},
 {"family":"pending-26","slot":5,"path":"pixelpure/pending26-05-verified-original-145ml-CANDIDATE.jpg","run":41752643604,"detail":"Pixelpure cleanser exact 145ml source only"}
]
rows=[]; F=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
for t in TARGETS:
 old=list((B/t["family"]).glob(f'{t["slot"]:02d}_*.jpg'))
 source=C/t["path"];assert len(old)==1 and source.is_file(),(t,old)
 raw=source.read_bytes()
 im=Image.open(source);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and len(raw)<2000000
 md=C/t["path"].split("/")[0]/"manifest.json"
 assert md.is_file(),md
 manifest=json.loads(md.read_text())
 assert not manifest.get("sales_approval",False) and not manifest.get("commercial_release_approved",False)
 s0=Image.open(old[0]).convert("RGB");s1=im.convert("RGB")
 a=s0.resize((128,128));b=s1.resize((128,128))
 difference=round(sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3,3)
 panel=Image.new("RGB",(1140,690),"#f8f8f8")
 for col,img in enumerate((s0,s1)):
  thumb=ImageOps.contain(img,(535,535),Image.Resampling.LANCZOS)
  x=col*570+(570-thumb.width)//2;y=20+(535-thumb.height)//2
  panel.paste(thumb,(x,y))
 draw=ImageDraw.Draw(panel)
 draw.text((32,566),f"{t['family']} / slot {t['slot']:02d} | original vs candidate",fill="#222",font=F)
 draw.text((32,606),f"MAE = {difference}/255 | Q/A only, rights & exact stock on hold",fill="#333",font=F)
 png=O/(t["family"]+f"-slot{t['slot']:02d}-before-after.jpg")
 panel.save(png,"JPEG",quality=88,optimize=True)
 shutil.copy2(source,O/(t["family"]+f"-slot{t['slot']:02d}-CANDIDATE.jpg"))
 rows.append({**t,"original_sha":hashlib.sha256(old[0].read_bytes()).hexdigest(),
  "candidate_sha":hashlib.sha256(raw).hexdigest(),"candidate_bytes":len(raw),
  "mean_absolute_pixel_difference":difference,"not_exact_duplicate":old[0].read_bytes()!=raw,
  "status":"QA_CANDIDATE_RELEASE_HOLD"})
assert len(rows)==4 and all(r["not_exact_duplicate"] for r in rows)
assert len(list(B.glob("pending-*/*.jpg")))==156
report={"version":"v2558","count":4,"source_original_JPG_count":156,
"baseline_original_bytes_untouched":True,"old_public_url_changes":0,
"source_image_rights_verified":False,"owned_stock_exact_editions_verified":False,
"MK_original_logo_verified":False,"xlsx_created":False,"new_public_urls":0,
"commercial_release_approved":False,"candidate_rows":rows,
"review_gate":"Do not replace base; do not publish before manual visual, exact edition, rights, original logo and claim QA."}
(O/"manifest.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"staged_images":4,"proof_panels":4,"not_exact_duplicate":4,"minimum_MAE":min(x["mean_absolute_pixel_difference"] for x in rows),"originals_unchanged":156}))
