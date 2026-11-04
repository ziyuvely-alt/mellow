#!/usr/bin/env python3
"""v2687 finalize missing family QA six-JPG set, not sales publication.
Never regenerate pictures or color swatches; source five historical JPGs plus
previously verified shade-name index image are byte-preserved in one folder.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil,base64
SRC=Path("qa-review/v2685-peripera-edition-and-shade-quarantine/HISTORICAL_REFERENCE_NOT_FOR_UPLOAD")
SHADE=Path("qa-review/v2686-peripera-20-verified-name-index/v2686-20-shade-names-no-swatches-QA.jpg")
OUT=Path("qa-review/v2687-peripera-six-frame-reference-QA-NOT-FOR-UPLOAD")
assert SRC.is_dir() and SHADE.is_file() and not OUT.exists()
OUT.mkdir(parents=True)
originals=sorted(SRC.glob("*.jpg"))
assert len(originals)==5,len(originals)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
frames=[]
for num,p in enumerate(originals,1):
    q=OUT/f"{num:02d}-HISTORICAL-edition-unverified-NOT-FOR-UPLOAD.jpg"
    shutil.copy2(p,q)
    assert sha(q)==sha(p)
    frames.append({"slot":num,"source":str(p),"file":q.name,"sha256":sha(q),
    "kind":"historical unverified edition JPG","sale_ready":False})
q=OUT/"06-20-shade-name-reference-only-no-swatches.jpg"
shutil.copy2(SHADE,q);assert sha(q)==sha(SHADE)
frames.append({"slot":6,"source":str(SHADE),"file":q.name,"sha256":sha(q),
"kind":"previously verified 20-shade NAME reference with no fake chips","sale_ready":False})
board=Image.new("RGB",(1920,1510),"#eeefec")
d=ImageDraw.Draw(board)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",32)
d.text((24,16),"PERIPERA / 6-FRAME REFERENCE ONLY / DO NOT UPLOAD",font=font,fill="#242424")
for idx,row in enumerate(frames):
 p=OUT/row["file"]
 with Image.open(p) as im:
  im.load();assert im.size==(1080,1080) and im.format=="JPEG"
  thumb=im.convert("RGB").resize((560,560),Image.Resampling.LANCZOS)
 assert p.stat().st_size<2_000_000
 x=35+(idx%3)*630;y=80+(idx//3)*715
 board.paste(thumb,(x,y))
 d.text((x,y+565),f"FRAME {idx+1:02d} / "+("NAMES" if idx==5 else "HISTORICAL"),fill="#222",font=font)
preview=OUT/"six-frame-contact-QA.jpg"
board.save(preview,"JPEG",quality=82,optimize=True)
(OUT/"six-frame-contact.b64.txt").write_text(base64.b64encode(preview.read_bytes()).decode())
manifest={
"version":"v2687","family":"pending-08","product":"PERIPERA Mood Glowy Tint 4g, shade numbers 01-20",
"real_JPGs_in_one_reference_set":6,
"prior_historical_JPGs_unchanged":5,"prior_v2686_name_index_JPG_unchanged":1,
"generated_product_images":0,"generated_color_chips":0,
"commercial_release_approved":False,
"photo_exact_26AD_edition_verified":False,
"historical_5_images_still_reference_only":True,
"visual_reference_6_for_names_only":True,
"known_exclusive_04_06_07_not_excluded":True,
"known_literal_shade_17_question_mark_not_typo":True,
"awaiting":["owned physical edition proof","official actual full shade swatches","commercial photo-use rights","final commercial visual QA"],
"prior_29_QA_product_families_unchanged":True,
"prior_11_published_families_untouched":True,
"prior_55_public_image_URLs_untouched":True,
"no_final_spreadsheet_shared":True,
"frames":frames}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"pending08_reference_JPG_set":6,"existing_original_JPGs_reused":6,
"new_product_artwork":0,"sale_approved":0,"last_unstaged_family_has_QA_reference_set":True}))
