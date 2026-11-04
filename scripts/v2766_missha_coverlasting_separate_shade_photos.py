#!/usr/bin/env python3
"""v2766 exact shade separation, not manufacture, of existing MISSHA Magic
Cushion Cover Lasting QA photos. Prevent mixed #21/#23 images in variants.
Only copies previously verified original JPG bytes and v2764 #23 real alpha.
Do NOT create fake #25/#27 shade pictures or edit the 55 public approved URLs.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,shutil,json,base64
R=Path("qa-review")
OLD=R/"v2675-missha-two-five-frame-photo-sets/pending-01"
NEW=R/"v2764-two-new-original-source-real-alpha-QA/pending-01"
OUT=R/"v2766-missha-coverlasting21-23-exact-shade-photo-QA"
assert OLD.is_dir() and NEW.is_dir() and not OUT.exists()
OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
specs={
"21":[{"source":OLD/"01-prior-original-byte-identical-QA.jpg","role":"BOX_PLUS_COMPACT_SHADE_21","shade_reliable":True}],
"23":[
 {"source":NEW/"01-clean-real-object-1080-JPG-QA.jpg","role":"ACTUAL_ALPHA_QA_HERO_SHADE_23","shade_reliable":True},
 {"source":OLD/"02-prior-original-byte-identical-QA.jpg","role":"ORIGINAL_BOX_CLOSED_COMPACT_SHADE_23","shade_reliable":True},
 {"source":OLD/"05-prior-original-byte-identical-QA.jpg","role":"APPLICATION_GUIDE_REFERENCES_SHADE_23","shade_reliable":True}],
"mixed_reference":[{"source":OLD/"04-prior-original-byte-identical-QA.jpg","role":"MIXED_SHADE_21_23_STOCK_REFERENCE_ONLY","shade_reliable":False}],
"common_info":[{"source":OLD/"03-factual-detail-new-QA.jpg","role":"GENERIC_CUSHION_FACT_CARD_NOT_SHADE_PROOF","shade_reliable":False}]
}
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(BOLD if b else FONT,n)
rows=[]
for key,arr in specs.items():
 folder=OUT/("shade-"+key if key.isdigit() else key);folder.mkdir()
 for idx,item in enumerate(arr,1):
  src=item["source"];assert src.is_file(),src
  path=folder/f"{idx:02d}-{item['role'].lower()}-QA.jpg"
  shutil.copy2(src,path)
  assert sha(src)==sha(path)
  with Image.open(path) as pic:
   pic.load();assert pic.format=="JPEG" and pic.size==(1080,1080)
  assert path.stat().st_size<2_000_000
  rows.append({"exact_shade_scope":key,"role":item["role"],
      "image_file":str(path.relative_to(OUT)),
      "source":str(src),"SHA256":sha(path),"source_bytes_unchanged":True,
      "shade_specific":item["shade_reliable"],"retail_approved":False})
board=Image.new("RGB",(1470,980),"#f1f1f0")
d=ImageDraw.Draw(board)
d.text((20,15),"v2766 MISSHA COVER LASTING: SHADE IDENTITY QA ONLY",font=f(27,True),fill="#2d2d2d")
by={
 "21":next(x for x in rows if x["exact_shade_scope"]=="21"),
 "23":next(x for x in rows if x["exact_shade_scope"]=="23"),
 "mixed_reference":next(x for x in rows if x["exact_shade_scope"]=="mixed_reference"),
 "common_info":next(x for x in rows if x["exact_shade_scope"]=="common_info")}
for i,(group,row) in enumerate(by.items()):
 with Image.open(OUT/row["image_file"]) as im:
  tile=im.convert("RGB").resize((380,380),Image.Resampling.LANCZOS)
 x=16+(i%3)*481;y=80+(i//3)*458
 board.paste(tile,(x,y))
 d.text((x,y+390),group+" / "+("SHADE SPECIFIC" if row["shade_specific"] else "REFERENCE ONLY"),font=f(18),fill="#3b3838")
preview=OUT/"v2766-separate-21-23-mixed-reference.jpg"
board.save(preview,"JPEG",quality=85,optimize=True)
(OUT/"v2766-proof.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
manifest={
 "version":"v2766","baseline":"v2765",
 "product":"MISSHA Magic Cushion Cover Lasting",
 "family":"pending-01","option_inventory":[21,23,25,27],
 "shade21_photo_candidates":1,"shade23_photo_candidates":3,
 "shade25_verified_photo_candidates":0,
 "shade27_verified_photo_candidates":0,
 "shade25_27_status":"HOLD_NO_IN_THIS_BATCH_VERIFIED_OPTION_PHOTOS",
 "mixed_21_23_source_QUARANTINED_AS_REFERENCE":True,
 "nonshade_factual_card_QUARANTINED_AS_REFERENCE":True,
 "distinct_real_per_shade_5_photo_sets_complete":False,
 "all_existing_QA_photo_pixels_unchanged":True,
 "new_image_generation":False,
 "prior_11_retail_families_unchanged":True,
 "prior_55_public_urls_unchanged":True,
 "stock_edition_rights_MK_logo_still_held":True,
 "new_retail_approved":0,
 "final_spreadsheet_shared":False,"staged_files":rows}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2766","original_image_refs_staged":len(rows),
 "shade21":1,"shade23":3,"shade25":0,"shade27":0,"new_retail_approved":0}))
