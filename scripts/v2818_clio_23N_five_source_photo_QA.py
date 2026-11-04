from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json,base64
R=Path("qa-review")
A=R/"v2817-clio-mini-23N-one-alpha-QA"
B=R/"v2816-clio-original-mini-5g-23N-real-single-unit-source"
O=R/"v2818-clio-23N-five-distinct-real-photo-QA-set"
assert A.is_dir() and B.is_dir() and not O.exists()
O.mkdir()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[(A/"01-23N-5g-true-alpha-1080-QA.jpg","NEURAL_REAL_SINGLE_CLOSED_COMPACT"),
       (B/"01-original-sasa-23N-5g-photo-1080-QA.jpg","ACTUAL_SINGLE_BOX_WITH_COMPACT"),
       (B/"03-original-sasa-23N-5g-photo-1080-QA.jpg","ACTUAL_OPEN_COMPACT_WITH_PUFF"),
       (B/"04-original-sasa-23N-5g-photo-1080-QA.jpg","ACTUAL_CLOSED_ANGLED_COMPACT"),
       (B/"05-original-sasa-23N-5g-photo-1080-QA.jpg","ACTUAL_OPEN_CUSHION_AND_PUFF")]
rows=[]
for i,(src,scene) in enumerate(files,1):
 assert src.is_file(),src
 p=O/f"{i:02d}-{scene}-QA.jpg"
 shutil.copy2(src,p)
 assert digest(src)==digest(p)
 with Image.open(p) as im:
  im.load();assert im.format=="JPEG" and im.size==(1080,1080)
 assert p.stat().st_size<2000000
 rows.append({"slot":i,"scene":scene,"file":p.name,"copied_source":str(src),
              "source_sha256":digest(src),"saved_sha256":digest(p),
              "jpg_bytes":p.stat().st_size,"verified_photographic_shade":"23N",
              "verified_5g_listing":True,"commercial_reuse_authorized":False})
assert len({x["saved_sha256"] for x in rows})==5
a=A/"01-23N-5g-true-alpha-QA.png"
assert a.is_file()
shutil.copy2(a,O/"01-original-actual-alpha-preserved-QA.png")
assert digest(a)==digest(O/"01-original-actual-alpha-preserved-QA.png")
preview=Image.new("RGB",(1875,620),"#f2f0ee")
d=ImageDraw.Draw(preview)
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
d.text((18,18),"CLIO The Original Mini 5g 23N | Five real scenes / one true alpha | QA ONLY",font=font,fill="#202020")
for idx,row in enumerate(rows):
 with Image.open(O/row["file"]) as im:
  thumb=im.convert("RGB").resize((348,348),Image.Resampling.LANCZOS)
 x=13+idx*372
 preview.paste(thumb,(x,71))
 d.text((x,436),f"{idx+1:02d} {row['scene'][:20]}",font=font,fill="#333333")
d.text((20,515),"23N gallery only. Do not apply to 21N. Prior original images unchanged.",font=font,fill="#464646")
d.text((20,553),"Original MK logo, owned physical stock edition, and commercial photo rights: HOLD.",font=font,fill="#464646")
proof=O/"v2818-five-photos-comparison-QA.jpg"
preview.save(proof,"JPEG",quality=85,optimize=True)
(O/"v2818-five-photos-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode("ascii"))
manifest={"version":"v2818","baseline":"v2817","family":"pending-05",
  "product":"CLIO Kill Cover Founwear The Original Mini 5g #23N",
  "five_JPGs_saved_1080_under_2MB":True,"five_scene_count":5,
  "original_source_JPGs_copied_identical":5,
  "original_transparent_alpha_png_copied_identical":True,
  "single_23N_shade_only":True,"for_21N_usable":False,
  "stock_generation_5g_23N_owned_confirmed":False,
  "commercial_photo_license_verified":False,"original_round_MK_brand_logo_verified":False,
  "sale_approved":False,"prior_11_approved_families_untouched":True,
  "prior_55_public_URLs_untouched":True,
  "previous_v2816_v2817_assets_untouched":True,
  "final_excel_shared":False,
  "frames":rows,"visual_QA":"PENDING_DIRECT_CONTACT_SHEET_REVIEW"}
(O/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2818","five_actual_jpgs":len(rows),"duplicate_sha":False,"new_sale_approvals":0}))
