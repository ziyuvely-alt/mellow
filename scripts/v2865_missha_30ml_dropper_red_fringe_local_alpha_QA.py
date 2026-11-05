#!/usr/bin/env python3
"""v2865: deliberately narrow, final non-destructive cap red-fringe trim on
the LAST SUCCESSFUL v2855 serum source alpha. Do not re-run v2801 or v2855;
retain all original RGB, product bottle, old five-photo set and 55 public URLs.
False cap trimming requires visual QA and keeps this candidate on HOLD.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from hashlib import sha256
import numpy as np,json

R=Path("qa-review")
OLD=R/"v2855-missha30ml-dropper-residue-precision-alpha-QA"
OUT=R/"v2865-missha30-dropper-right-red-fringe-isolated-local-QA"
assert not OUT.exists()
M=json.loads((OLD/"manifest.json").read_text())
assert M["version"]=="v2855"
src=OLD/M["new_alpha_png"]
sha=lambda p:sha256(p.read_bytes()).hexdigest()
assert src.is_file() and sha(src)==M["new_alpha_png_sha256"]
with Image.open(src) as im:
 im.load()
 assert im.mode=="RGBA" and im.size==(311,794)
 original=im.copy()
raw=np.asarray(original).copy()
old=raw[:,:,3].astype(np.float32)
rgb=raw[:,:,:3].copy()
H,W=old.shape
yy,xx=np.mgrid[:H,:W]
# The upper-right red curl belongs to the cutout artefact, outside the white
# glass dropper silhouette. Tight, feathered edit only: x>=195, rows 62..143.
# White/near-neutral cap pixels are protected. No editing of bottle or collar.
xblend=np.clip((xx-195.)/7.,0,1)
xblend=xblend*xblend*(3.-2*xblend)
ystart=np.clip((yy-62.)/10.,0,1)
ystart=ystart*ystart*(3-2*ystart)
yend=np.clip((145.-yy)/12.,0,1)
yend=yend*yend*(3-2*yend)
region=xblend*ystart*yend
r,g,b=(rgb[:,:,i].astype(np.float32) for i in range(3))
# Preserve pale cap edge x<205 when pixels match almost-white cap material.
near_neutral=(np.max(rgb,axis=2)-np.min(rgb,axis=2)<12)
bright=(np.min(rgb,axis=2)>210)
cap_preserve=near_neutral & bright & (xx<205)
region[cap_preserve]=0.
# Preserve entirety of original pixels outside the explicitly bounded edit.
region[(xx<195)|(yy<62)|(yy>145)]=0.
new_alpha=np.rint(old*(1-region)).astype(np.uint8)
affected=int(np.count_nonzero(new_alpha!=raw[:,:,3]))
removed=float(np.sum(old-new_alpha)/255.)
assert 4<=affected<3300,(affected,removed)
assert np.array_equal(new_alpha[:60],raw[:60,:,3])
assert np.array_equal(new_alpha[146:],raw[146:,:,3])
assert np.array_equal(new_alpha[:,:195],raw[:,:195,3])
assert np.array_equal(rgb,raw[:,:,:3])
OUT.mkdir(parents=True)
rgba=Image.fromarray(np.dstack((rgb,new_alpha)),"RGBA")
cut=OUT/"01-MISSHA30-dropper-edge-red-fringe-local-original-RGB-alpha-QA.png"
rgba.save(cut,optimize=True)
assert src.read_bytes()==(OLD/M["new_alpha_png"]).read_bytes()
bbox=rgba.getchannel("A").getbbox()
assert bbox and bbox[3]>=790 and bbox[0]<45 and bbox[2]>280
crop=rgba.crop(bbox)
fit=ImageOps.contain(crop,(910,930),Image.Resampling.LANCZOS)
hero=Image.new("RGB",(1080,1080),"white")
hero.paste(fit,((1080-fit.width)//2,68+(930-fit.height)//2),fit.getchannel("A"))
jpg=OUT/"01-MISSHA30-dropper-local-clean-1080-QA.jpg"
hero.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
with Image.open(jpg) as im:assert im.format=="JPEG" and im.size==(1080,1080)
assert jpg.stat().st_size<2000000
# 1:1 numeric alpha/RGB audit and close-crop contrast: no false claim of
# visual approval just because localized alpha differences were saved.
def checker(img):
 result=Image.new("RGBA",img.size,"#f0f1f2")
 d=ImageDraw.Draw(result)
 for y in range(0,img.height,12):
  for x in range(0,img.width,12):
   if (x//12+y//12)%2:d.rectangle((x,y,x+11,y+11),fill="#c7c9cc")
 result.alpha_composite(img)
 return result.convert("RGB")
bg=Image.new("RGB",(1600,870),"#F0EDF0")
d=ImageDraw.Draw(bg)
fontfile="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font=ImageFont.truetype(fontfile,21)
d.text((18,12),"v2865  SERUM CAP FRINGE | ORIGINAL v2855 vs LOCAL ALPHA vs 1080 QA  | NOT SALES",font=font,fill="#372F36")
def fit_panel(img,pos,size):
 base=Image.new("RGB",size,"white")
 fitted=ImageOps.contain(img,size,Image.Resampling.NEAREST)
 base.paste(fitted,((size[0]-fitted.width)//2,(size[1]-fitted.height)//2))
 bg.paste(base,pos)
fit_panel(checker(original),(20,65),(475,680))
fit_panel(checker(rgba),(550,65),(475,680))
fit_panel(hero,(1080,65),(475,680))
d.text((20,757),"BEFORE v2855",font=font,fill="#473C4A")
d.text((550,757),"AFTER local-alpha",font=font,fill="#473C4A")
d.text((1080,757),"1080 white-background QA",font=font,fill="#473C4A")
d.text((20,796),f"Original RGB preserved | alpha pixels changed: {affected} | removed alpha eq: {round(removed)}",font=font,fill="#5B4B5E")
contact=OUT/"v2865-source-vs-local-alpha-hero-QA.jpg"
bg.save(contact,"JPEG",quality=90,optimize=True)
# Native crop includes cap white-right edge and artifact to allow pixel-level
# review; no resizing or model re-synthesis of the actual source pixels.
close=Image.new("RGB",(1140,700),"#F2EFF0")
d2=ImageDraw.Draw(close)
d2.text((20,14),"NATIVE CAP RIGHT EDGE / QA ONLY / PIXELS NEAREST 4X",font=font,fill="#413843")
region_box=(135,50,270,190)
for i,pic in enumerate((checker(original),checker(rgba))):
 px=pic.crop(region_box).resize((540,560),Image.Resampling.NEAREST)
 close.paste(px,(15+i*565,70))
 d2.text((16+i*565,641),"v2855" if i==0 else "v2865",font=font,fill="#413843")
detail=OUT/"v2865-original-cap-vs-local-trim-native-4x-QA.jpg"
close.save(detail,"JPEG",quality=93,optimize=True)
assert sha(src)==M["new_alpha_png_sha256"]
result={"version":"v2865","baseline":"v2864","family":"pending-13",
 "source_version":"v2855","input_png":str(src),"input_sha256":M["new_alpha_png_sha256"],
 "method":"Local upper-right dropper alpha red-fringe trim x>=195 y=62..145, neutral white cap RGB protection",
 "source_RGB_unchanged":True,"source_original_v2855_bytes_unchanged":True,
 "changed_alpha_pixel_count":affected,"removed_alpha_255_equivalent":round(removed,2),
 "new_transparent_png":str(cut),"new_png_SHA256":sha(cut),
 "new_JPG_1080":str(jpg),"new_JPG_sha256":sha(jpg),"new_JPG_bytes":jpg.stat().st_size,
 "compare_contact":str(contact),"native_cap_zoom":str(detail),
 "pending_visual_approval":True,"status":"LOCAL_CAP_TRIM_CANDIDATE_HOLD_FINAL_VISUAL",
 "not_retail":True,"source_photo_rights_verified":False,
 "owned_stock_edition_verified":False,"authentic_original_MK_logo_verified":False,
 "previous_11_sale_approved_families_preserved":True,
 "previous_55_public_URLs_preserved":True,"new_public_urls":0,
 "new_sale_approved_images":0,"final_spreadsheet_shared":False,
 "next":"Review cap edge at high zoom. If red residue remains or actual white cap is clipped, reject v2865 without reattempting same deterministic line; source a clean owned image instead."
}
(OUT/"manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"version":"v2865","new_png":str(cut),"new_JPG":str(jpg),
 "edited_alpha_px":affected,"protected_RGB":True,"retail_approved":0}))
