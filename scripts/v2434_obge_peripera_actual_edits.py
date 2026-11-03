#!/usr/bin/env python3
"""v2434: real OBgE photographed cushion white-field draft + precise Peripera text revisions.
No generated swatches, product pixels, new logo, fake permissions, or original overwrites.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
B=Path("baseline-v2427b")/"immutable-v2426b"/"originals-v2425-unchanged"/"prior-immutable"/"immutable-prev"/"preserved-v2422"
O=Path("v2434-output");O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def F(n,b=False):return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def save(im,path):
 path.parent.mkdir(parents=True,exist_ok=True);im.save(path,"JPEG",quality=94,optimize=True)
 with Image.open(path) as ck:
  ck.load();assert ck.format=="JPEG" and ck.size==(1080,1080) and path.stat().st_size<2_000_000
 return {"file":str(path.relative_to(O)),"sha256":sha(path),"bytes":path.stat().st_size}
items=[]
# Product photograph field exactly x290..790 and y210..710. Re-layout with white outer background.
src=B/"en-photo-captions"/"pending-10"/"SOURCE_01_363f13d61_EN_V2421C.jpg";assert src.exists()
old=sha(src)
with Image.open(src) as im:
 im.load();im=im.convert("RGB")
 img=im.crop((290,210,790,710))
 board=Image.new("RGB",(1080,1080),"white");d=ImageDraw.Draw(board)
 d.text((72,66),"OBgE",font=F(48,True),fill=(46,60,52))
 d.text((72,136),"Perfect Cover Cushion",font=F(43,True),fill=(46,60,52))
 d.line((72,206,1008,206),fill=(178,189,180),width=2)
 # Use exact photographed JPEG pixels; do not paint, remove or generate product silhouette.
 board.paste(img,(290,245))
 d.line((72,867,1008,867),fill=(178,189,180),width=2)
 d.text((72,905),"15 g",font=F(66,True),fill=(46,60,52))
 dest=O/"sales-image-drafts"/"pending-10"/"OBGE_real_cushion_white_photo_field_V2434.jpg"
 out=save(board,dest)
 assert sha(src)==old
 items.append({"group_id":"pending-10","source":str(src.relative_to(B)),"source_sha":old,"output":out,
  "change":"Actual photographed cushion preserved, white studio image merged into white canvas, corrected Perfect Cover caption",
  "state":"SALES_IMAGE_DRAFT","restrictions":["RENEWED_PACKAGE_VERSION_UNVERIFIED","PHOTO_RIGHTS_UNVERIFIED","MK_ORIGINAL_MISSING"],"alpha_cutout":False})
# Two existing text-only Peripera frames: edit body panel only, keep title and panels.
for name,fix,lines in [
 ("INFO_FORMULA_01_V2414_EN_V2421.jpg","remove_unverified_20_shades_repetition",[
  ("MOOD GLOWY TINT",390,55,True),
  ("Lip tint  |  4 g",578,39,False),
  ("Select a shade from the listing",655,30,False)]),
 ("INFO_PRODUCT_01_V2414B_EN_V2421.jpg","replace_repeated_01_to20_with_actual_product_info",[
  ("4 g",397,80,True),
  ("Peripera Mood Glowy Tint",571,39,False),
  ("Single lip tint",655,34,False)])
]:
 source=B/"en-customer-drafts"/"pending-08"/name;assert source.exists()
 with Image.open(source) as im:
  im=im.convert("RGB");d=ImageDraw.Draw(im)
  # Panel x72..1008 y303..762; do not write outside or cover top headings.
  color=im.getpixel((500,720))
  # Cover only the text region, preserve rounded panel edges and left accent when present.
  d.rectangle((184,374,902,706),fill=color)
  for line,y,size,bold in lines:
   ff=F(size,bold);w=d.textbbox((0,0),line,font=ff)[2]
   assert w<705,(name,line,w)
   d.text((540-w//2,y),line,font=ff,fill=(48,66,56))
  path=O/"sales-image-drafts"/"pending-08"/(name[:-4]+"_V2434.jpg")
  entry=save(im,path)
  assert sha(source)!=sha(path)
  items.append({"group_id":"pending-08","source":str(source.relative_to(B)),"source_sha":sha(source),"output":entry,
   "change":fix,"state":"SALES_IMAGE_DRAFT","restrictions":["26AD_GENERATION_UNVERIFIED","EXACT_20_SHADE_SWATCHS_UNVERIFIED","PHOTO_RIGHTS_UNVERIFIED"]})
cp={"version":"2.4.34","actual_JPG_modified":len(items),"groups_modified":2,"photographic_cushion_relayout":1,
"peripera_customer_copy_revisions":2,"new_official_swatch_charts":0,"final_qa_approved":0,
"source_photograph_pixels_generated":False,"external_approval_obtained":False,"published_URL_changes":0,
"edits":items,"next":["Open all 3 outputs and QA visible text, product and boundaries","Check official renewed OBgE cushion packaging against this photo","Verify Peripera original 01..20 generation and official swatches","Go next pending item rather than retry failed swatch search"]}
(O/"v2434_checkpoint.json").write_text(json.dumps(cp,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in cp.items() if k!="edits"},ensure_ascii=False),flush=True)
