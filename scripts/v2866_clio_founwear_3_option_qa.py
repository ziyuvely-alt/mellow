#!/usr/bin/env python3
"""v2866: Three labeled CLIO Founwear The Original reference photo cards,
reuse exactly the archived v2864 good white lid/puff U2Net alpha.
Never use v2862 failed masks, 21C/21N suspected relabel collisions,
fabricated swatches, gift set imagery, logos, or previous released URLs.
"""
from pathlib import Path
from hashlib import sha256
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json
R=Path("qa-review")
BASE=R/"v2864-founwear-3-white-lid-u2net-native-RGB-check"
OUT=R/"v2866-founwear-preserved-three-white-puff-option-QA"
assert BASE.is_dir() and not OUT.exists()
m=json.loads((BASE/"manifest.json").read_text())
assert m["version"]=="v2864" and m["retained_white_material_candidates"]==3
records={v["shade"]:v for v in m["results"]}
names={"19C":"LIGHT","19N":"PORCELAIN","23N":"GINGER"}
assert set(records)==set(names)
sha=lambda p:sha256(p.read_bytes()).hexdigest()
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=lambda n,b=False:ImageFont.truetype(B if b else F,n)
OUT.mkdir(parents=True)
new=[]
for shade,label in names.items():
 r=records[shade]
 assert r["status"]=="TECHNICAL_ALPHA_CANDIDATE_HOLD_VISUAL_AND_LICENSE"
 assert r["white_material_pass"] and r["blank_background_pass"] and r["geometry_pass"]
 source=Path(r["png"])
 assert source.exists() and sha(source)==r["png_sha256"]
 with Image.open(source) as o:
  o.load()
  assert o.format=="PNG" and o.mode=="RGBA"
  product=o.copy()
 im=Image.new("RGB",(1080,1080),"#FBFAFC")
 d=ImageDraw.Draw(im)
 d.rounded_rectangle((43,43,1037,1037),radius=24,outline="#DFDBE4",width=2)
 d.text((84,73),"CLIO",font=font(56,True),fill="#39323A")
 d.text((84,153),"KILL COVER FOUNWEAR CUSHION",font=font(28),fill="#605A66")
 d.line((84,205,998,205),fill="#D5CDD9",width=3)
 d.rounded_rectangle((784,81,999,165),radius=15,fill="#EEE9F2")
 d.text((803,106),shade+"  "+label,font=font(18,True),fill="#574C5C")
 placed=ImageOps.contain(product,(910,705),Image.Resampling.LANCZOS)
 im.paste(placed,((1080-placed.width)//2,221+(705-placed.height)//2),placed.getchannel("A"))
 d.line((82,949,1000,949),fill="#D5CDD9",width=2)
 d.text((84,958),"SHADE OPTION REFERENCE  |  QA ONLY",font=font(21,True),fill="#625968")
 d.text((84,995),"GIFT SET / COMMERCIAL RIGHTS / MK LOGO UNVERIFIED",font=font(15),fill="#827986")
 dst=OUT/f"CLIO-Founwear-{shade}-real-alpha-source-option-QA.jpg"
 im.save(dst,"JPEG",quality=94,subsampling=0,optimize=True)
 with Image.open(dst) as check:
  check.load()
  assert check.format=="JPEG" and check.size==(1080,1080)
 assert dst.stat().st_size < 2_000_000
 assert sha(source)==r["png_sha256"]
 new.append({"shade":shade,"name":label,"source_png":str(source),
             "source_sha256":r["png_sha256"],"card_jpg":str(dst),
             "card_sha256":sha(dst),"jpg_bytes":dst.stat().st_size,
             "product_RGB_recolored":False,"source_modified":False,
             "shade_proven_by_merchant_variant":True,
             "gift_set_edition_verified":False,"retail_approved":False})
assert len(set(x["card_sha256"] for x in new))==3
contact=Image.new("RGB",(1560,620),"#F2EFF3")
d=ImageDraw.Draw(contact)
d.text((18,14),"v2866 CLIO FOUNWEAR | three source-pixel QA options | NOT SALES",font=font(23,True),fill="#3E3746")
for i,r in enumerate(new):
 with Image.open(r["card_jpg"]) as im:
  frame=im.convert("RGB").resize((500,500),Image.Resampling.LANCZOS)
 contact.paste(frame,(20+i*515,62))
 d.text((25+i*515,576),r["shade"]+"  "+r["name"]+"  |  SET ON HOLD",font=font(18,True),fill="#51455A")
cp=OUT/"v2866-three-preserved-real-alpha-option-photo-QA.jpg"
contact.save(cp,"JPEG",quality=89,optimize=True)
assert all(sha(Path(x["source_png"]))==x["source_sha256"] for x in new)
manifest={"version":"v2866","baseline":"v2865","source_qa":"v2864","family":"pending-05",
 "new_JPG_1080":3,"new_photo_sources":0,"stock_shades_used":["19C","19N","23N"],
 "pending_shades_due_to_source_collision":["21C","21N"],
 "source_alpha_pngs_changed":0,"earlier_v2862_rejected_mattes_not_reused":True,
 "approved_11_product_groups_unchanged":True,"verified_55_public_URLs_unchanged":True,
 "commercial_rights_verified":False,"physical_gift_set_edition_verified":False,
 "authenticated_original_MK_logo":False,"new_sales_approved":0,"new_public_URLs":0,
 "spreadsheet_shared":False,"cards":new,"contact":str(cp),"contact_sha256":sha(cp),
 "next":"Review original product gift-set contents, rights and true brand identity before sales. Source distinct verified 21C/21N imagery separately; never reuse near-duplicate merchant photos as evidence of different shades."}
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2866","new_cards":3,"source_rewrites":0,"sales_approved":0}))
