#!/usr/bin/env python3
"""v2861: extend v2860 alpha recovery with readable CLIO MeshBlur stock-option QA
cards and audit possible duplicated/cross-shade images in the two other CLIO
gift-set family archives. No original pixels or published assets altered.
All output remains internal QA; a merchant variant association is NOT proof
that the user's physical gift set includes that exact packaging/skin tone.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from hashlib import sha256
import numpy as np
import json, itertools

R=Path("qa-review")
OUT=R/"v2861-clio-three-shade-option-QA-and-ten-variant-collision-audit"
assert not OUT.exists()
SRC=R/"v2860-clio-meshblur-three-truealpha-source-variants-QA"
META=json.loads((SRC/"manifest.json").read_text())
assert META["version"]=="v2860" and META["output_usable_alpha_candidate_count"]==3
OUT.mkdir(parents=True)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
font_root="/usr/share/fonts/truetype/dejavu"
def font(n,b=False):return ImageFont.truetype(font_root+("/DejaVuSans-Bold.ttf" if b else "/DejaVuSans.ttf"),n)
inventory_shades={"19C":"LIGHT","19N":"PORCELAIN","21N":"LINEN"}
newcards=[]
for row in META["per_shade"]:
 shade=row["shade"]
 assert shade in inventory_shades and row["status"]=="TRUE_ALPHA_TECHNICAL_CANDIDATE_HOLD_VISUAL"
 fp=Path(row["original_PNG"])
 assert fp.is_file() and sha(fp)==row["png_sha256"]
 with Image.open(fp) as src:
  src.load()
  assert src.mode=="RGBA"
  product=src.copy()
 canvas=Image.new("RGB",(1080,1080),"#FAF9FD")
 d=ImageDraw.Draw(canvas)
 d.rounded_rectangle((43,42,1037,1038),radius=29,outline="#E7E1EB",width=2)
 d.text((76,72),"CLIO",font=font(53,True),fill="#4D435F")
 d.text((76,141),"KILL COVER MESH BLUR CUSHION",font=font(25),fill="#6F6580")
 d.line((74,193,1002,193),fill="#D7CCD9",width=3)
 d.rounded_rectangle((805,83,999,158),radius=19,fill="#EFEAF3")
 d.text((830,102),shade+" "+inventory_shades[shade],font=font(17,True),fill="#5B486B")
 # Preserve unedited product RGB from original v2860 true-alpha PNG.
 fitted=ImageOps.contain(product,(905,715),Image.Resampling.LANCZOS)
 canvas.paste(fitted,((1080-fitted.width)//2,210+(715-fitted.height)//2),fitted.getchannel("A"))
 d.line((75,944,1002,944),fill="#DAD1DE",width=2)
 d.text((77,960),"OPTION PHOTO REFERENCE  |  QA ONLY",font=font(22,True),fill="#76697B")
 d.text((77,997),"GIFT SET PACKAGING / PHOTO RIGHTS / MK UNVERIFIED",font=font(15),fill="#887F8D")
 out=OUT/f"pending-07-CLIO-MeshBlur-{shade}-reference-card-1080-QA.jpg"
 canvas.save(out,"JPEG",quality=92,optimize=True,subsampling=0)
 with Image.open(out) as ck: assert ck.size==(1080,1080) and ck.format=="JPEG"
 assert out.stat().st_size<2_000_000
 assert sha(fp)==row["png_sha256"]
 newcards.append({"shade":shade,"source_PNG":str(fp),"source_SHA256":row["png_sha256"],
                  "new_JPG":str(out),"new_SHA256":sha(out),"JPG_bytes":out.stat().st_size,
                  "SHADE_PRESENT_IN_USER_INVENTORY":True,"SET_IMAGE_IDENTITY_APPROVED":False,
                  "COMMERCIAL_IMAGE_APPROVED":False})
assert len(newcards)==3 and len(set(x["new_SHA256"] for x in newcards))==3

# Also use archived source-only QA JPGs from other CLIO bundle families to
# detect potentially identical photos being relabeled as five shade-specific pictures.
SOURCE_GROUPS={
 "pending-05":{
  "directory":"v2852-founwear-original-five-variant-alternative-merchant-QA",
  "manifest":"manifest.json",
  "rows":{r["shade"]:r for r in json.loads((R/"v2852-founwear-original-five-variant-alternative-merchant-QA/manifest.json").read_text())["variants"]},
  "file_key":"rendered_file","sha_key":"rendered_JPG_sha256"
 },
 "pending-06":{
  "directory":"v2851-clio-giftset-five-option-variant-photo-QA",
  "manifest":"manifest.json",
  "rows":{r["shade"]:r for r in json.loads((R/"v2851-clio-giftset-five-option-variant-photo-QA/manifest.json").read_text())["families"][1]["variants"]},
  "file_key":"filename","sha_key":"rendered_sha256"
 }
}
stock_shades=["19C","19N","21C","21N","23N"]
similarity=[]
previews={}
for family,group in SOURCE_GROUPS.items():
 assert set(group["rows"])==set(stock_shades)
 folder=R/group["directory"]
 assets=[]
 for shade in stock_shades:
  r=group["rows"][shade]
  p=folder/r[group["file_key"]]
  assert p.is_file() and sha(p)==r[group["sha_key"]],(family,shade)
  with Image.open(p) as obj:
   obj.load()
   assert obj.format=="JPEG" and obj.size==(1080,1080)
   base=obj.convert("RGB")
  # Entire original image, resized only for numerical analysis. Overlay
  # texts in contact reports do not alter real source imagery.
  analysis=np.asarray(base.resize((256,256),Image.Resampling.BILINEAR),dtype=np.int16)
  assets.append((shade,p,analysis))
  previews[(family,shade)]=base.copy()
 pairs=[]
 for (s1,p1,a),(s2,p2,b) in itertools.combinations(assets,2):
  diff=np.abs(a-b)
  mad=round(float(diff.mean()),4)
  pix_near=round(float((diff.max(axis=2)<=5).mean()),5)
  px_mean=round(float((diff.max(axis=2)<=12).mean()),5)
  pairs.append({"shade_pair":[s1,s2],"whole_image_MAD_RGB":mad,
                "all_channels_within_5_ratio":pix_near,
                "all_channels_within_12_ratio":px_mean,
                "potential_relabel_collision":bool(mad<3.0 or pix_near>0.91)})
 pairs.sort(key=lambda x:x["whole_image_MAD_RGB"])
 similarity.append({"family":family,"source_gallery":group["directory"],
                    "pair_count":len(pairs),"most_similar_pairs":pairs[:5],
                    "possible_collisions":sum(x["potential_relabel_collision"] for x in pairs),
                    "method_note":"Same product photo may be reused across shades; similarity cannot prove variant identity or counterfeit swatch."})
 # Reuse existing five JPGs, create a single comparison board only.
 board=Image.new("RGB",(1660,980),"#F1F0F1")
 d=ImageDraw.Draw(board)
 d.text((22,12),f"v2861 {family} | five distinct merchant-linked JPG source QA, NOT SALES",font=font(24,True),fill="#383239")
 for i,shade in enumerate(stock_shades):
  image=ImageOps.contain(previews[(family,shade)],(500,420),Image.Resampling.LANCZOS)
  x=28+(i%3)*550;y=65+(i//3)*453
  board.paste(image,(x,y))
  d.text((x,y+422),f"{shade}  /  merchant variant photo",font=font(18,True),fill="#5D4E60")
 fn=OUT/f"{family}-five-original-variant-photo-collision-check-QA.jpg"
 board.save(fn,"JPEG",quality=90,optimize=True)
 similarity[-1]["contact"]=str(fn)
 similarity[-1]["contact_sha256"]=sha(fn)
 report_path=OUT/f"{family}-collision-metrics.json"
 report_path.write_text(json.dumps(similarity[-1],ensure_ascii=False,indent=2)+"\n")
 if similarity[-1]["possible_collisions"]>0:
  similarity[-1]["image_uniqueness_release_gate"]="HOLD_REVIEW_NEAR_DUPLICATE_SOURCES"
 else:similarity[-1]["image_uniqueness_release_gate"]="UNRESOLVED_EDITION_AND_RIGHTS_HOLD"

# For v2860 per-shade product reference cards, make one contact.
board=Image.new("RGB",(1550,630),"#EFE9F0")
d=ImageDraw.Draw(board)
d.text((20,12),"v2861 CLIO Mesh Blur 19C / 19N / 21N | ORIGINAL-ALPHA OPTION PHOTO QA",font=font(23,True),fill="#35303C")
for i,item in enumerate(newcards):
 with Image.open(item["new_JPG"]) as im:
  frame=im.convert("RGB").resize((500,500),Image.Resampling.LANCZOS)
 board.paste(frame,(20+i*510,65))
 d.text((25+i*510,575),item["shade"]+" | GIFT SET NOT VERIFIED",font=font(17,True),fill="#5B5062")
contact=OUT/"v2861-three-meshblur-real-alpha-option-cards-QA.jpg"
board.save(contact,"JPEG",quality=88,optimize=True)
report={
 "version":"v2861","baseline":"v2860",
 "work_summary":"3 previously recovered native-alpha option cards + source-only 10 shade photo collision audit",
 "new_individual_option_JPGs":3,"new_comparison_contacts":3,
 "target_families":["pending-07","pending-05","pending-06"],
 "new_cards":newcards,"comparison_metrics":similarity,
 "three_option_contact":str(contact),"three_option_contact_sha256":sha(contact),
 "archived_v2860_v2851_v2852_sources_modified":0,
 "previous_11_published_families_unchanged":True,
 "previous_55_public_URLs_unchanged":True,
 "final_spreadsheet_shared":False,
 "verified_stock_edition":False,
 "commercial_image_rights_verified":False,
 "original_MK_logo_authenticated":False,
 "new_sales_approvals":0,"new_public_urls":0,
 "next":"Review visually whether merchant variant-linked source images are actually distinct, not only different filenames; pursue exact 15g+refill stock package evidence for pending-05/06/07 before public release."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2861","new_option_cards":3,
                  "new_contact_images":3,
                  "collision_flags":{x["family"]:x["possible_collisions"] for x in similarity},
                  "sales_approved":0,"source_rewrites":0},ensure_ascii=False))
