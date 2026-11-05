#!/usr/bin/env python3
"""v2842: use proven v2837 21N alpha shape on 23N RGB if photos align.
No photo regeneration/retouching of older QA, no retail rights inferred.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import cv2,numpy as np,json,hashlib,base64
R=Path("qa-review")
A=R/"v2834-clio-meshglow-mini-21N-high-native-resolution-source-probe"/"02-21N-high-native-source-QA.jpg"
B=R/"v2840-clio-meshglow-mini5g-23N-five-photo-no-reviews-QA"/"05-23N-MERCHANT-LACOSMETIQUE-QA.jpg"
MASK=R/"v2837-21N-mini5g-restore-inner-cushion-source-pixels-QA"/"01-21N-compact-inner-cushion-restored-TRUE-ALPHA-QA.png"
OLD=R/"v2836-clio-mini5g-21N-1200px-isolated-compact-alpha-QA"/"manifest.json"
OUT=R/"v2842-clio-mini5g-23N-native-registered-alpha-QA"
assert all(x.is_file() for x in [A,B,MASK,OLD]) and not OUT.exists()
OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in [A,B,MASK,OLD]}
with Image.open(A) as im: im.load(); reference=im.convert("RGB")
with Image.open(B) as im: im.load(); target=im.convert("RGB")
with Image.open(MASK) as im: im.load(); alpha=im.getchannel("A")
assert reference.size==target.size==(1080,1080)
row=json.loads(OLD.read_text())["candidate"]
crop,box=row["extracted_photo_crop"],row["mask_bbox"]
x0,y0=crop[0]+box[0],crop[1]+box[1]
assert alpha.size==(box[2]-box[0],box[3]-box[1])
needle=np.array(reference.crop((x0,y0,x0+alpha.width,y0+alpha.height)).convert("L"))
area=(215,270,735,820)
hay=np.array(target.crop(area).convert("L"))
best={"score":-1}
for factor in [0.92,0.96,1.,1.04,1.08]:
    w,h=round(alpha.width*factor),round(alpha.height*factor)
    template=cv2.resize(needle,(w,h))
    _,score,_,pos=cv2.minMaxLoc(cv2.matchTemplate(hay,template,cv2.TM_CCOEFF_NORMED))
    if score>best["score"]:
        best={"score":round(float(score),5),"scale":factor,
              "bbox":[area[0]+pos[0],area[1]+pos[1],area[0]+pos[0]+w,area[1]+pos[1]+h]}
report={"version":"v2842","baseline":"v2840","family":"pending-04",
 "variant":"23N Ginger","alignment":best,"mask_source":"v2837 21N silhouette alpha only",
 "23N_photographic_RGB_source":str(B),
 "segmentation_model_runs":0,"review_photos_used":0,
 "photo_usage_rights_verified":False,"exact_owned_inventory_verified":False,
 "authentic_MK_logo_verified":False,"retail_approved":False,
 "11_published_families_unchanged":True,"55_public_URLs_unchanged":True,
 "previous_23N_5JPG_galleries_unchanged":True,"final_xlsx_shared":False}
bx=best["bbox"]
if best["score"]>=0.84 and abs(bx[0]-x0)<85 and abs(bx[1]-y0)<85:
    actual=target.crop(tuple(bx)).convert("RGBA")
    actual.putalpha(alpha.resize(actual.size,Image.Resampling.LANCZOS))
    png=OUT/"01-23N-Ginger-real-product-transparent-QA.png"
    actual.save(png,optimize=True)
    fpath="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bpath="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font=lambda n,b=False:ImageFont.truetype(bpath if b else fpath,n)
    hero=Image.new("RGB",(1080,1080),"white")
    d=ImageDraw.Draw(hero)
    d.rounded_rectangle((48,48,1032,1032),radius=33,outline="#eee3e8",width=2)
    d.text((91,96),"CLIO",font=font(43,True),fill="#363037")
    d.text((91,166),"Mesh Glow Essential Cushion Mini 5g",font=font(27),fill="#726770")
    d.text((91,212),"23N Ginger | Exact merchant-variant photograph",font=font(19),fill="#8b7c87")
    fitted=ImageOps.contain(actual,(880,705),Image.Resampling.LANCZOS)
    hero.paste(fitted,((1080-fitted.width)//2,270+(705-fitted.height)//2),fitted)
    d.text((91,996),"23N SOURCE PIXELS ONLY  |  QA, NOT SALES-APPROVED",font=font(18),fill="#948991")
    jpg=OUT/"01-23N-Ginger-real-product-1080-hero-QA.jpg"
    hero.save(jpg,"JPEG",quality=93,optimize=True)
    assert jpg.stat().st_size<2_000_000
    with Image.open(jpg) as check:check.load();assert check.size==(1080,1080)
    contact=Image.new("RGB",(1400,510),"#f1efed")
    for i,pic in enumerate([reference,target,hero]):
        contact.paste(pic.resize((445,445),Image.Resampling.LANCZOS),(15+i*465,15))
    cf=OUT/"v2842-21N-23N-registration-visual-QA.jpg"
    contact.save(cf,"JPEG",quality=85,optimize=True)
    (OUT/"v2842-proof.b64.txt").write_text(base64.b64encode(cf.read_bytes()).decode())
    report.update({"status":"TRUE_23N_RGB_WITH_REGISTERED_MASK_VISUAL_QA_PENDING",
       "new_PNG":png.name,"new_JPG":jpg.name,"sha256":sha(jpg),
       "JPG_bytes":jpg.stat().st_size,"mask_shift_and_scale_QA_REQUIRED":True})
else:
    report.update({"status":"HOLD_SOURCE_GEOMETRY_MISMATCH","new_images_created":0,
                   "next":"Use original 23N five-JPG QA set; do not put mismatched 21N alpha on product."})
for p in [A,B,MASK,OLD]: assert sha(p)==before[str(p)]
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2842","match":best,"status":report["status"],"sales_approved":0}))
