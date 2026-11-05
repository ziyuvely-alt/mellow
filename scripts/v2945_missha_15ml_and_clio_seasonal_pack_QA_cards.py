#!/usr/bin/env python3
"""v2945 make a corrected 15mL MISSHA internal QA image and two distinct CLIO
pack-edition spec review cards; never impersonate an approved pack product photo.
Uses brand-backed v2941 facts and existing bytes. No old images touched.
"""
from pathlib import Path
from hashlib import sha256
from io import BytesIO
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,time

Q=Path("qa-review")
PRE=Q/"v2944-four-5frame-product-first-internal-only-QA-ZIPs"
FACT=Q/"v2941-five-option-pack-generation-unit-conflict-resolution-QA"
OUT=Q/"v2945-missha-official-15ml-and-clio-edition-distinction-info-QA"
assert not OUT.exists()
state=json.loads((PRE/"stock30-incremental-state-v2944.json").read_text(encoding="utf-8"))
facts=json.loads((FACT/"manifest.json").read_text(encoding="utf-8"))
assert state["version"]=="v2944" and len(state["families"])==30
assert facts["version"]=="v2941" and facts["resolved_official_unit_conflicts"]==1
fx={x["family"]:x for x in facts["reconciliation"]}
assert fx["pending-12"]["confirmed_content_unit"]=="15mL"
editions=fx["pending-06"]["offer_variants"]
assert {x["edition"] for x in editions}=={"25FW","REGULAR"}
def font(sz,bold=False):
 name="DejaVuSans-Bold" if bold else "DejaVuSans"
 try:return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/"+name+".ttf",sz)
 except:return ImageFont.load_default()
def draw_wrap(d,words,x,y,maxw,size,fill):
 lines=[]
 for phrase in words:
  tokens=phrase.split()
  line=""
  for token in tokens:
   candidate=(line+" "+token).strip()
   if line and d.textbbox((0,0),candidate,font=font(size))[2]>maxw:
    lines.append(line);line=token
   else:line=candidate
  if line:lines.append(line)
 for line in lines:
  d.text((x,y),line,font=font(size),fill=fill);y+=size+15
 return y
def save(img,path):
 img.save(path,"JPEG",quality=91,optimize=True,subsampling=0)
 assert path.stat().st_size<2_000_000
 with Image.open(path) as x:
  x.load();assert x.format=="JPEG" and x.size==(1080,1080)
 return sha256(path.read_bytes()).hexdigest()

OUT.mkdir(parents=True)
source=Q/"v2719-four-unprocessed-clio-missha-real-photo-cutouts/pending-12/01-actual-product-cutout-square-1080-QA.jpg"
data=source.read_bytes()
with Image.open(BytesIO(data)) as img:
 img.load();assert img.format=="JPEG" and img.size==(1080,1080)
 # Trim existing QA source labels. The product remains as originally photographed.
 photo=img.convert("RGB").crop((130,225,930,982))
board=Image.new("RGB",(1080,1080),"#F7F6F8");d=ImageDraw.Draw(board)
d.rounded_rectangle((33,33,1047,1047),radius=35,fill="#FFFFFF",outline="#E9DCE0",width=3)
d.text((70,81),"MISSHA",font=font(49,True),fill="#54262F")
d.text((70,154),"PDRN NAD+ Renew Peel Shot 25",font=font(27),fill="#60343B")
d.rounded_rectangle((68,245,611,904),radius=25,fill="#FBF6F7")
fit=ImageOps.contain(photo,(510,625),Image.Resampling.LANCZOS)
board.paste(fit,(339-fit.width//2,575-fit.height//2))
d.text((642,310),"NET CONTENT",font=font(25,True),fill="#9F626C")
d.text((636,399),"15 mL",font=font(56,True),fill="#632C37")
d.line((640,485,1000,485),fill="#D7BDC4",width=3)
draw_wrap(d,["Verified against","the brand's official","product listing."],640,555,340,23,"#603C45")
d.text((72,939),"OFFICIAL UNIT CHECK  |  QA ONLY",font=font(20,True),fill="#853E4C")
d.text((72,978),"Physical batch, image rights and commercial approval pending",font=font(17),fill="#8F777D")
p=OUT/"pending-12-MISSHA-PDRN-Peel-Shot25-official-15mL-info-INTERNAL.jpg"
missha_sha=save(board,p)
outputs=[{"family":"pending-12","type":"OFFICIAL_VOLUME_CORRECTION_INFO","edition":"SINGLE_15mL",
 "image":str(p),"sha256":missha_sha,"source_sha256":sha256(data).hexdigest(),
 "official_claim_confirmed":"15mL", "marketplace_photo_rights_confirmed":False,"retail_approved":False}]

# CLIO 25FW and REGULAR are distinct packs. Source photos do not establish owned inventory editions.
for e in editions:
 code=e["edition"]
 main=Image.new("RGB",(1080,1080),"#F9F4F7");a=ImageDraw.Draw(main)
 a.rounded_rectangle((34,34,1046,1046),radius=34,fill="white",outline="#E4D1DC",width=3)
 a.text((69,77),"CLIO  |  PACK EDITION REVIEW",font=font(34,True),fill="#542F47")
 a.text((69,135),"Kill Cover Mesh Glow Essential Cushion",font=font(24),fill="#654A57")
 accent="#8B4474" if code=="25FW" else "#567389"
 a.rounded_rectangle((70,228,1010,318),radius=25,fill=accent)
 a.text((100,246),"25FW PACK" if code=="25FW" else "REGULAR PACK",font=font(34,True),fill="white")
 a.text((83,385),"CUSHION MAIN",font=font(23,True),fill="#6F5C68")
 a.text((83,423),"15 g",font=font(50,True),fill="#352E35")
 a.text((575,385),"REFILL",font=font(23,True),fill="#6F5C68")
 a.text((575,423),"15 g",font=font(50,True),fill="#352E35")
 a.line((78,515,1000,515),fill="#D9C6D0",width=3)
 a.text((83,557),"ADDITIONAL ITEM",font=font(24,True),fill=accent)
 addition="Skin Prep Base 15 mL" if code=="25FW" else "Duo Cheek 10 g"
 a.text((83,611),addition,font=font(34,True),fill="#392E36")
 a.line((77,724,1000,724),fill="#E1D6DD",width=2)
 a.text((83,768),"CONFIRM ACTUAL STOCK EDITION",font=font(22,True),fill="#A0394E")
 draw_wrap(a,["This is a reference card, not a", "photograph of the complete set."],83,820,880,23,"#684F5C")
 a.text((76,970),"INTERNAL VARIANT QA  |  NOT FOR RETAIL LISTING",font=font(17,True),fill="#8B4B60")
 dest=OUT/("pending-06-CLIO-"+code+"-distinct-pack-edition-INTERNAL.jpg")
 digest=save(main,dest)
 outputs.append({"family":"pending-06","type":"PACK_EDITION_PROOF_REFERENCE",
   "edition":code,"source_official_goods_id":6182,
   "known_inclusions":{"main":"15g","refill":"15g","added":addition},
   "image":str(dest),"sha256":digest,
   "exact_inventory_photo_verified":False,"commercial_rights_verified":False,
   "retail_approved":False})
state["families"]["pending-12"].update({"last_delta_version":"v2945",
 "v2945_official_15ml_info_QA":str(p),"release_status":"OFFICIAL_VOLUME_15ML_VISUAL_INFO_QA_CREATED_RETAIL_HOLD",
 "latest_photo_QA_checkpoint":"v2945 true brand official 15mL applied to one new information-only image; earlier source hero remains unchanged. Photo rights and stock HOLD.",
 "sale_approved":False})
state["families"]["pending-06"].update({"last_delta_version":"v2945",
 "v2945_verified_edition_specific_QA_cards":[x["image"] for x in outputs if x["family"]=="pending-06"],
 "release_status":"CLIO_25FW_VS_REGULAR_EDITION_INFORMATION_DISTINCT_STOCK_UNVERIFIED",
 "latest_photo_QA_checkpoint":"v2945 generated 25FW and REGULAR edition info cards using official main/refill/add-on pack descriptions. No finished product-set photo or exact stock identity is inferred.",
 "sale_approved":False})
report={"version":"v2945","baseline":"v2944","created_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
 "new_1080_information_review_images":len(outputs),
 "missha_15mL_official_fix_frame":1,
 "clio_distinct_pack_edition_cards":2,
 "new_source_product_photographs":0,
 "original_source_photos_changed":0,
 "preexisting_11_approved_product_families_unchanged":True,
 "preexisting_55_public_URLs_unchanged":True,
 "new_public_URLs":0,"new_retail_approvals":0,
 "final_spreadsheet_shared":False,
 "results":outputs}
assert len(outputs)==3 and all(not r["retail_approved"] for r in outputs)
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
state.update({"version":"v2945","baseline":"v2944","new_sales_approvals":0,"new_public_URLs":0,"final_spreadsheet_shared":False})
(OUT/"stock30-incremental-state-v2945.json").write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"version":"v2945","new_1080_images":3,"missha_unit_corrected":True,"clio_editions":2,"sale_approved":0},ensure_ascii=False))
