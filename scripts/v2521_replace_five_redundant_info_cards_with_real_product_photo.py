#!/usr/bin/env python3
"""Replace ONLY five redundant information-card JPEGs with unchanged genuine product photography.
Read v2520 150 QA JPG files, v2494b Goodal Cream Alpha original, v2496 Goodal Mist
2 original scenes and v2475 OBgE Pore Zero 2 source scenes.
Retain the other 145 JPEGs byte-identical. This is QA-only, no commercial/public approval.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import shutil,hashlib,json
BASE=Path("v2521-inputs")
SRC=BASE/"review-JPG-by-family"
OUT=Path("v2521-five-photo-upgrades")
TARGET=OUT/"review-JPG-by-family"
assert SRC.is_dir(), "Missing previously saved 150 QA JPEGs"
shutil.copytree(SRC,TARGET)
F=lambda n,b=False:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
replacements=[]
def replace(fam,slot,source,title,subtitle,style="contain"):
 orig=list((TARGET/fam).glob(f"{slot:02d}_*.jpg"))
 assert len(orig)==1,(fam,slot,len(orig))
 previous=orig[0];old=previous.read_bytes();oldhash=hashlib.sha256(old).hexdigest()
 photo=Image.open(BASE/source).convert("RGB")
 if style=="full":
  im=ImageOps.fit(photo,(1080,1080),Image.Resampling.LANCZOS)
  layer=Image.new("RGBA",(1080,1080),(0,0,0,0));d=ImageDraw.Draw(layer)
  d.rounded_rectangle((24,15,1056,131),radius=17,fill=(255,255,255,225))
  d.text((52,26),title,font=F(34,True),fill="#2e4a47")
  d.text((52,77),subtitle,font=F(23),fill="#4c6966")
  im=Image.alpha_composite(im.convert("RGBA"),layer).convert("RGB")
 else:
  im=Image.new("RGB",(1080,1080),"#f8f8f4")
  photo=ImageOps.contain(photo,(1020,850))
  im.paste(photo,((1080-photo.width)//2,155+(850-photo.height)//2))
  d=ImageDraw.Draw(im)
  d.text((56,50),title,font=F(39,True),fill="#2e4a47")
  d.text((56,103),subtitle,font=F(23),fill="#4c6966")
 new=previous.parent/f"{slot:02d}_v2521-genuine-product-photo.jpg"
 im.save(new,"JPEG",quality=90,optimize=True,subsampling=0)
 b=new.read_bytes()
 assert Image.open(new).size==(1080,1080) and len(b)<2000000
 previous.unlink()
 replacements.append(dict(family=fam,slot=slot,prior_sha256=oldhash,new_sha256=hashlib.sha256(b).hexdigest(),photo_source=source,bytes=len(b)))
replace("pending-19",1,"source_alpha/source-alpha-original.webp","GOODAL  |  VITA-C CREAM ALPHA","Actual product jar photo  |  50 mL")
replace("pending-20",2,"source_mist/25ad-straight-product.jpg","GOODAL  |  VITA-C SERUM MIST","Real 100 mL bottle, front angle")
replace("pending-20",4,"source_mist/25ad-angled-product.jpg","GOODAL  |  VITA-C SERUM MIST","Real 100 mL bottle, angled photo","full")
replace("pending-23",1,"source_pore/soonsu-mint-cube.webp","OBgE  |  PORE ZERO","Oil Control Sun Cream  |  50 mL","full")
replace("pending-23",3,"source_pore/dodoskin-product-texture.webp","OBgE  |  PORE ZERO","Real 50 mL tube and texture scene","full")
old=json.loads((BASE/"manifest.json").read_text())
before={(x["family"],x["sha256"]) for x in old["file_records"]}
removed={(x["family"],x["prior_sha256"]) for x in replacements}
actual={}
for file in sorted(TARGET.glob("pending-*/*.jpg")):
 im=Image.open(file);im.load()
 assert im.format=="JPEG" and im.size==(1080,1080) and file.stat().st_size<2_000_000
 actual.setdefault(file.parent.name,[]).append(dict(file=str(file.relative_to(OUT)),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),bytes=file.stat().st_size))
assert len(actual)==30 and all(len(x)==5 for x in actual.values())
after={(fam,z["sha256"]) for fam,lst in actual.items() for z in lst}
assert before-removed<=after,"An unchanged approved candidate was altered"
assert len(before-removed)==145
assert all(len({x["sha256"] for x in lst})==5 for lst in actual.values())
report={"version":"v2521","date":"2026-11-04","source":"v2520 saved QA corpus","total_valid_JPG":150,
"unchanged_JPG_byte_identical":145,"actual_source_photo_replacements":5,"replacements":replacements,
"all_30_families_five_images":True,"all_JPG_1080x1080_under_2mb":True,
"new_public_URLs":0,"legacy_55_URLs_untouched":True,"excel_shared":False,
"final_sales_QA_approved":False,"original_MK_logo_missing":True,"photo_rights_unverified":True,
"physical_owned_stock_edition_unverified":True,
"note":"A 30x5 technical QA corpus, NOT a full sales-ready 30-family release. External-source photos are preserved for visual proof only."}
OUT.mkdir(exist_ok=True)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"real_JPG":150,"unchanged":145,"exact_photo_replacements":5,"families":30,"sales_approved":False}))
