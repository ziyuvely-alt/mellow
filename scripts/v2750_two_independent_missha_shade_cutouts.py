#!/usr/bin/env python3
"""v2750 generate TRUE alpha cutouts from two separately sourced official
MISSHA Magic Cushion Cover Lasting variants No.25 and No.27.
Preserve distinct original variant photos, no recoloring, no fake swatches.
Use 2 independently implemented masks as QA alternatives because pink/white
compact edges are low contrast. No public release or known-logo fabrication.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from rembg import remove,new_session
import numpy as np,cv2,hashlib,base64,json
ROOT=Path("qa-review")
SOURCE=ROOT/"v2749-MISSHA-coverlasting-N25-N27-official-variant-source-proof"
OUT=ROOT/"v2750-missha-N25-N27-distinct-official-photo-cutout-QA"
assert SOURCE.exists() and not OUT.exists()
OUT.mkdir(parents=True)
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cv_mask(rgb):
    arr=np.array(rgb)
    # White-background contour extraction preserves white plastic inside
    # filled item outline rather than erasing white product surfaces.
    minimum=arr.min(axis=2)
    dark=np.uint8(minimum<245)*255
    dark[:33,:]=0;dark[-33:,:]=0;dark[:,:33]=0;dark[:,-33:]=0
    kernel=np.ones((13,13),np.uint8)
    connected=cv2.morphologyEx(dark,cv2.MORPH_CLOSE,kernel,iterations=2)
    contours,_=cv2.findContours(connected,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    ranked=sorted(contours,key=cv2.contourArea,reverse=True)
    selected=[c for c in ranked if cv2.contourArea(c)>=9000][:3]
    if not selected:raise ValueError("No sufficiently large contour")
    mask=np.zeros(dark.shape,dtype=np.uint8)
    cv2.drawContours(mask,selected,-1,255,thickness=cv2.FILLED)
    # Soft antialiasing of factual photo edges only.
    mask=cv2.GaussianBlur(mask,(5,5),0.8)
    coverage=float(np.mean(mask>128))
    if coverage<.04 or coverage>.75:raise ValueError(f"Implausible contour coverage: {coverage:.3f}")
    result=np.dstack((arr,mask))
    return Image.fromarray(result,"RGBA"),coverage,len(selected)
session=new_session("isnet-general-use")
report={"version":"v2750","base":"v2749","family":"pending-01",
  "product":"MISSHA Magic Cushion Cover Lasting No25/27",
  "distinct_official_original_colorways_only":True,
  "no_N21_or_N23_photo_used":True,
  "source_originals_sha_preserved":True,
  "new_retail_approvals":0,
  "photo_commercial_rights_verified":False,
  "exact_owned_Korean_stock_generation_verified":False,
  "original_MK_brand_logo_authenticated":False,
  "published_11_families_unchanged":True,
  "published_55_public_urls_unchanged":True,
  "final_xlsx_shared":False,"variants":[]}
font_small=f(20)
for shade in ("25","27"):
    source=SOURCE/f"shade-{shade}"/f"01-real-variant-linked-{shade}-source-reference-QA.jpg"
    assert source.is_file()
    with Image.open(source) as im:
        im.load();assert im.format=="JPEG" and im.size==(1080,1080)
        rgb=im.convert("RGB")
    # Whole composition: back lid plus original open foundation pan are both
    # scenes of the same physical shade and must not be misdescribed as 2 units.
    v={"shade":shade,"source":str(source),"source_sha256":sha(source),
       "alpha_methods":[],"retail_approved":False,
       "sku_generation_and_rights_hold":True}
    item=OUT/f"shade-{shade}";item.mkdir()
    methods=[
      ("isnet",lambda: (remove(rgb.convert("RGBA"),session=session,alpha_matting=True,
             alpha_matting_foreground_threshold=230,alpha_matting_background_threshold=20,
             alpha_matting_erode_size=4),None,None)),
      ("white_bg_contour",lambda: cv_mask(rgb))
    ]
    for method,producer in methods:
        entry={"method":method,"status":"REJECTED_UNTIL_VISUAL_QA"}
        try:
            cut,coverage,ncount=producer()
            if cut.mode!="RGBA":raise ValueError("Not alpha")
            a=cut.getchannel("A");box=a.getbbox()
            if not box:raise ValueError("No foreground")
            cov=float(np.mean(np.array(a)>=128))
            assert .04<cov<.80 and box[2]-box[0]>230 and box[3]-box[1]>260,(cov,box)
            cropped=cut.crop(box)
            png=item/f"01-original-{shade}-{method}-true-alpha-QA.png"
            cropped.save(png,optimize=True)
            canvas=Image.new("RGB",(1080,1080),"white")
            d=ImageDraw.Draw(canvas)
            d.rounded_rectangle((48,50,1032,1030),radius=39,outline="#eae6e8",width=2)
            d.text((91,92),"MISSHA",font=f(43,True),fill="#3d363a")
            d.text((91,153),"MAGIC CUSHION COVER LASTING",font=f(25),fill="#756c71")
            d.text((91,196),f"NO. {shade}  |  OFFICIAL VARIANT PHOTO",font=f(23,True),fill="#876a75")
            fitted=ImageOps.contain(cropped,(890,720),Image.Resampling.LANCZOS)
            x=(1080-fitted.width)//2;y=256+(720-fitted.height)//2
            canvas.paste(fitted,(x,y),fitted)
            d.text((91,995),"ACTUAL PRODUCT PHOTO  |  QA ONLY",font=font_small,fill="#9d9296")
            jpg=item/f"01-original-{shade}-{method}-product-1080-QA.jpg"
            canvas.save(jpg,"JPEG",quality=93,optimize=True,subsampling=0)
            assert jpg.stat().st_size<2000000
            with Image.open(jpg) as check:
                check.load();assert check.format=="JPEG" and check.size==(1080,1080)
            entry.update({"status":"REAL_ALPHA_RENDERED_VISUAL_QA_REQUIRED",
              "alpha_coverage":round(cov,4),"box_xyxy":list(box),
              "contours":ncount,"png":str(png.relative_to(OUT)),
              "jpg":str(jpg.relative_to(OUT)),
              "jpg_bytes":jpg.stat().st_size,"png_sha256":sha(png),"jpg_sha256":sha(jpg)})
        except Exception as exc:
            entry["failure_type"]=type(exc).__name__
            entry["failure"]=str(exc)[:220]
        v["alpha_methods"].append(entry)
    report["variants"].append(v)
panels=[]
for v in report["variants"]:
    src=SOURCE/f"shade-{v['shade']}"/f"01-real-variant-linked-{v['shade']}-source-reference-QA.jpg"
    with Image.open(src) as im:
        orig=im.convert("RGB").resize((290,290),Image.Resampling.LANCZOS)
    panels.append((v["shade"],"source",orig))
    for method in v["alpha_methods"]:
        if method.get("jpg"):
            with Image.open(OUT/method["jpg"]) as im:thumb=im.convert("RGB").resize((290,290),Image.Resampling.LANCZOS)
            panels.append((v["shade"],method["method"],thumb))
board=Image.new("RGB",(1050,700),"#f0efee")
d=ImageDraw.Draw(board)
d.text((15,13),"v2750 REAL VARIANT 25 / 27 CUTOUTS - NOT RETAIL APPROVED",font=f(24,True),fill="#222222")
for i,(shade,label,im) in enumerate(panels[:6]):
    px=15+(i%3)*345;py=54+(i//3)*319
    board.paste(im,(px,py))
    d.text((px,py+292),f"NO.{shade} {label}",font=f(19),fill="#383438")
proof=OUT/"v2750-real-photo-masks-comparison.jpg"
board.save(proof,"JPEG",quality=86,optimize=True)
(OUT/"v2750-proof.b64.txt").write_text(base64.b64encode(proof.read_bytes()).decode())
report["real_alpha_PNG_and_JPG_pairs"]=sum(1 for v in report["variants"] for m in v["alpha_methods"] if m.get("jpg"))
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2750","shade_photo_sources":2,"real_alpha_pairs":report["real_alpha_PNG_and_JPG_pairs"],
 "status":{v["shade"]:[m["status"] for m in v["alpha_methods"]] for v in report["variants"]},
 "retail_approved":0}))
