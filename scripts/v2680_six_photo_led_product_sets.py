#!/usr/bin/env python3
"""v2680: Six photo-first five-JPG QA families from historical, genuine source JPEGs.
No generated packaging, no fake color swatches, no MK logo, no unverified gift,
benefit or stock edition statements. Source JPG bytes kept SHA-identical.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import shutil,hashlib,json,base64
SRC=Path("historical/review-JPG-by-family")
OUT=Path("qa-review/v2680-six-brand-five-JPG-photo-led-batch")
assert not OUT.exists()
OUT.mkdir(parents=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ft(size,b=False): return ImageFont.truetype(BOLD if b else FONT,size)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(d,t,x,y,maxw,sz,col):
 while sz>25 and d.textbbox((0,0),t,font=ft(sz,True))[2]>maxw:sz-=2
 assert d.textbbox((0,0),t,font=ft(sz,True))[2]<=maxw,t
 d.text((x,y),t,font=ft(sz,True),fill=col)
specs=[
 dict(id=23,brand="OBgE",lines=["PORE ZERO","OIL CONTROL","SUN CREAM"],volume="50 mL",sources=[1,3,4],color="#c9e7e2"),
 dict(id=24,brand="BIOHEAL BOH",lines=["NAD-PRIZCELL","GLOW POWER SERUM"],volume="30 mL",sources=[2,4,5],color="#e7c4cb"),
 dict(id=25,brand="BIOHEAL BOH",lines=["NAD-PRIZCELL","GLOW BOOST CREAM"],volume="50 mL",sources=[2,4],color="#edcdd0"),
 dict(id=27,brand="PIXEL PURE",lines=["SOOTHING","AMPOULE TONER"],volume="200 mL",sources=[2,3,5],color="#e9cfdc"),
 dict(id=29,brand="PIXEL PURE",lines=["RADIANCE AQUA","SOOTHING CREAM"],volume="50 mL",sources=[2,4],color="#ecd7dc"),
 dict(id=30,brand="PIXEL PURE",lines=["AURA RADIANCE","SERUM"],volume="50 mL",sources=[2,4],color="#edd4df")
]
# Four card layouts with distinct subjects. No need to add spec-unverified methods.
styles=[
 ("PRODUCT INFORMATION",lambda s:s["lines"]),
 ("NET CONTENT",lambda s:[s["volume"],"SINGLE PRODUCT"]),
 ("PRODUCT DETAILS",lambda s:s["lines"][-2:]),
 ("PRODUCT GUIDE",lambda s:["REFER TO THE","ORIGINAL LABEL"]),
]
def factual(s,index):
 heading,make=styles[(index-1)%len(styles)]
 im=Image.new("RGB",(1080,1080),"#fffdfa");d=ImageDraw.Draw(im)
 d.rounded_rectangle((50,52,1030,1027),radius=35,fill="#ffffff",outline="#e1dcda",width=3)
 d.rounded_rectangle((80,80,1000,262),radius=28,fill=s["color"])
 fit(d,s["brand"],116,135,855,60,"#343135")
 fit(d,heading,116,355,855,42,"#65595d")
 y=498
 lines=make(s)
 for text in lines:
  fit(d,text,116,y,850,62,"#393139")
  y+=117
 d.line((116,883,962,883),fill="#ded4d9",width=3)
 d.text((116,930),"KOREAN BEAUTY",font=ft(30),fill="#807579")
 return im,heading
proof=Image.new("RGB",(1832,2250),"#eef0ed");pd=ImageDraw.Draw(proof)
pd.text((17,13),"v2680 SIX PHOTO-FIRST QA FAMILIES / 30 ACTUAL JPG FILES",font=ft(35,True),fill="#262626")
report=[]
for ix,s in enumerate(specs):
 fam=f"pending-{s['id']:02d}";folder=OUT/fam;folder.mkdir()
 frames=[]
 for k,slot in enumerate(s["sources"],1):
  matching=list((SRC/fam).glob(f"{slot:02d}*.jpg"))
  assert len(matching)==1,(fam,slot,matching)
  source=matching[0]
  dest=folder/f"{k:02d}-actual-source-slot{slot:02d}-UNMODIFIED-QA.jpg"
  shutil.copy2(source,dest)
  assert sha(source)==sha(dest)
  frames.append(dict(frame=k,file=dest.name,type="ORIGINAL_REAL_JPG_EXACT_BYTES",
                     sha256=sha(dest),source_slot=slot,bytes=dest.stat().st_size))
 for k in range(len(s["sources"])+1,6):
  artwork,heading=factual(s,k-len(s["sources"]))
  dest=folder/f"{k:02d}-fact-only-{heading.lower().replace(' ','-')}-QA.jpg"
  artwork.save(dest,format="JPEG",quality=92,optimize=True,subsampling=0)
  frames.append(dict(frame=k,file=dest.name,type="NEW_FACTS_ONLY_INFO_FRAME",
                     sha256=sha(dest),bytes=dest.stat().st_size))
 assert len(frames)==5
 for entry in frames:
  p=folder/entry["file"]
  with Image.open(p) as im:
   im.load();assert im.format=="JPEG" and im.size==(1080,1080)
   tile=im.convert("RGB").resize((334,334),Image.Resampling.LANCZOS)
  assert p.stat().st_size<2_000_000
  x=13+(entry["frame"]-1)*363;y=58+ix*360
  proof.paste(tile,(x,y))
  pd.text((x,y+335),fam+" / "+str(entry["frame"]).zfill(2),font=ft(22),fill="#272727")
 report.append(dict(family=fam,brand=s["brand"],product=" ".join(s["lines"]),
                    volume=s["volume"],real_source_unmodified=len(s["sources"]),
                    new_factual_JPG=5-len(s["sources"]),frame_count=5,
                    image_status="QA_ONLY_NEEDS_REAL_STOCK_LICENSE_V2647_FINAL_REVIEW",
                    frames=frames))
proof_file=OUT/"v2680-six-family-contact-sheet.jpg"
proof.save(proof_file,quality=80,optimize=True)
(OUT/"v2680-preview.b64.txt").write_text(base64.b64encode(proof_file.read_bytes()).decode())
manifest=dict(version="v2680",baseline="v2678",
     new_five_JPG_QA_draft_families=len(report),total_JPG_count=30,
     original_real_JPGs_preserved=sum(q["real_source_unmodified"] for q in report),
     new_fact_only_JPGs=sum(q["new_factual_JPG"] for q in report),
     new_retailable_approvals=0,source_historical_not_v2647=True,
     commercial_photo_rights_verified=False,actual_stock_edition_verified=False,
     previously_approved_11_unchanged=True,verified_public_55_urls_unchanged=True,
     final_spreadsheet_not_shared=True,families=report)
(OUT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"new_QA_families":len(report),"physical_JPG_files":30,
 "real_original_JPG_preserved":manifest["original_real_JPGs_preserved"],
 "new_information_JPG":manifest["new_fact_only_JPGs"],"sale_approved":0}))
