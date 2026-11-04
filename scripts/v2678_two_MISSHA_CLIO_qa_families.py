#!/usr/bin/env python3
"""v2678: physical QA JPG drafts for two distinct unreleased SKUs.
No version, shade, 15g/15mL or promotional gift assumptions and no new MK art.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil,base64
ROOT=Path("historical/review-JPG-by-family");OUT=Path("qa-review/v2678-missha-clio-two-five-JPG-sets")
assert not OUT.exists()
OUT.mkdir(parents=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=lambda n,b=False:ImageFont.truetype(B if b else F,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(d,s,x,y,maxwidth,sz,c):
 while sz>=22 and d.textbbox((0,0),s,font=font(sz,True))[2]>maxwidth:sz-=2
 assert sz>=22,s
 d.text((x,y),s,font=font(sz,True),fill=c)
specs=[
 {"family":"pending-12","name":"MISSHA PDRN NAD+ Renew Peel Shot 25",
  "brand":"MISSHA","colors":("#e7d7db","#5d2534"),
  "source":[1,2,3],
  "cards":[("PRODUCT INFORMATION",["PDRN NAD+","RENEW PEEL SHOT 25"]),
           ("PRODUCT GUIDE",["READ PRODUCT","LABEL DIRECTIONS"])],
  "hold":"STOCK_15G_VS_OFFICIAL_15ML_PHOTO_RIGHTS"},
 {"family":"pending-06","name":"CLIO Kill Cover Mesh Glow Essential Cushion",
  "brand":"CLIO","colors":("#e4d5ec","#4a3058"),
  "source":[3,4],
  "cards":[("PRODUCT DETAILS",["KILL COVER","MESH GLOW"]),
           ("PRODUCT NAME",["MESH GLOW","ESSENTIAL CUSHION"]),
           ("SHADE GUIDE",["CHECK ORIGINAL","SHADE LABEL"])],
  "hold":"PACKAGE_GENERATION_PROMOTIONAL_KIT_SHADE_PHOTO_RIGHTS"}
]
proof=Image.new("RGB",(1840,1550),"#eeeded");d=ImageDraw.Draw(proof)
d.text((20,10),"v2678 TWO ADDITIONAL 5-JPG PHOTO-BASED QA FAMILIES",font=font(34,True),fill="#222222")
rows=[]
for ri,s in enumerate(specs):
 fam=s["family"];dst=OUT/fam;dst.mkdir();result=[]
 for i,slot in enumerate(s["source"],1):
  ps=list((ROOT/fam).glob(f"{slot:02d}*.jpg"))
  assert len(ps)==1,(fam,slot,len(ps))
  source=ps[0];target=dst/f"{i:02d}-existing-original-slot{slot:02d}-unchanged-QA.jpg"
  shutil.copy2(source,target)
  assert sha(source)==sha(target)
  result.append({"frame":i,"kind":"ORIGINAL_JPG_BYTE_PRESERVED","source_slot":slot,
                 "sha256":sha(target),"file":target.name})
 for i,(heading,items) in enumerate(s["cards"],len(s["source"])+1):
  bg,textcolor=s["colors"];im=Image.new("RGB",(1080,1080),"#fffefd")
  dr=ImageDraw.Draw(im)
  dr.rounded_rectangle((55,55,1025,1025),radius=32,fill="#ffffff",outline="#ddd8dc",width=3)
  dr.rounded_rectangle((80,80,1000,264),radius=27,fill=bg)
  write(dr,s["brand"],112,139,860,64,textcolor)
  write(dr,heading,112,365,850,42,textcolor)
  y=508
  for word in items:write(dr,word,112,y,850,66,textcolor);y+=125
  dr.line((112,883,965,883),fill="#e2d7dc",width=2)
  dr.text((112,934),"KOREAN BEAUTY",font=font(30),fill="#858085")
  target=dst/f"{i:02d}-safe-original-info-QA.jpg";im.save(target,"JPEG",quality=92,optimize=True,subsampling=0)
  result.append({"frame":i,"kind":"NEW_FACT_ONLY_JPG","sha256":sha(target),"file":target.name})
 assert len(result)==5
 for j,r in enumerate(result):
  p=dst/r["file"]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   mini=im.convert("RGB").resize((340,340),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  x=20+j*363;y=78+ri*710
  proof.paste(mini,(x,y))
  d.text((x,y+349),fam+" / "+str(j+1).zfill(2),font=font(22),fill="#222")
  r["bytes"]=p.stat().st_size
 rows.append({"family":fam,"product":s["name"],"five_QA_jpg_present":True,
              "photographs_original_unchanged":len(s["source"]),
              "new_info_frames":len(s["cards"]),
              "sale_release":"HOLD_"+s["hold"],"files":result})
p=OUT/"v2678-two-family-10-frame-preview.jpg";proof.save(p,"JPEG",quality=82,optimize=True)
(OUT/"v2678-preview.b64.txt").write_text(base64.b64encode(p.read_bytes()).decode())
m={"version":"v2678","baseline":"v2677","source":"historic v2593 original QA corpus",
   "new_five_frame_QA_family_count":2,"JPG_count":10,
   "original_existing_images_unchanged":5,"new_fact_only_images":5,
   "new_sale_approved":0,"owned_stock_generation_unverified":True,
   "commercial_source_photo_rights_unverified":True,"latest_v2647_missing":True,
   "approved_existing_11_untouched":True,"published_55_URLs_untouched":True,
   "final_xlsx_shared":False,"families":rows}
(OUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_QA_family_sets":2,"actual_JPG_count":10,"original_reused":5,
                  "new_factual_frames":5,"retail_approved":0}))
