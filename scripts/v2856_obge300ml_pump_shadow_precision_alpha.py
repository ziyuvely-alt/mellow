#!/usr/bin/env python3
"""v2856: OBgE Max Waterful Sun Cream 300mL pump/body matte edge correction.
Keep photographic original RGB and source JPG/PNG immutable. Bound edits
to shadow areas at right pump, shoulder, and bottle edge. Internal QA only.
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from hashlib import sha256
import numpy as np,json

R=Path("qa-review")
P=R/"v2712-3-failed-cutouts-high-quality-recovery"/"pending-22"
OUT=R/"v2856-obge300ml-pump-shadow-alpha-precision-QA"
assert P.is_dir() and not OUT.exists()
OUT.mkdir()
s=P/"01-actual-alpha-cutout-high-res-QA.png"
legacy=P/"01-full-product-high-quality-cutout-1080-QA.jpg"
sha=lambda p:sha256(p.read_bytes()).hexdigest()
source_sha=sha(s);legacy_sha=sha(legacy)
with Image.open(s) as im:
 im.load();src=im.convert("RGBA")
w,h=src.size
assert 220<=w<=1080 and 450<=h<=1080,(w,h)
rgb=np.asarray(src.convert("RGB")).copy()
before=np.asarray(src.getchannel("A"),dtype=np.uint8)
yy,xx=np.mgrid[:h,:w]
# The pump nozzle is wider than the pump collar, so use a geometry
# profile. Keep the original RGB pixels, only reduce alpha of cast shadows
# outside the photographic package silhouette.
ys=np.array([0,.026,.052,.075,.12,.205,.235,.265,.80,.93,.965,1.0])*h
xs=np.array([.95,.96,.925,.74,.72,.72,.79,.94,.94,.93,.91,.88])*w
max_right=np.interp(yy.astype(float),ys,xs)
alpha_gate=np.clip((max_right-xx)/8.,0,1)
alpha_gate=alpha_gate*alpha_gate*(3-2*alpha_gate)
after=np.rint(before.astype(float)*alpha_gate).astype(np.uint8)
affected=int(np.count_nonzero(after!=before))
removed255=int(np.sum(before.astype(int)-after.astype(int))/255)
# Preserve left/center product, labels, and source files.
assert np.array_equal(after[:,:int(w*.62)],before[:,:int(w*.62)])
assert 0<affected<.14*w*h,(w,h,affected)
assert np.count_nonzero(after)>=.76*np.count_nonzero(before)
corrected=Image.fromarray(np.dstack([rgb,after]),"RGBA")
png=OUT/"01-OBgE300mL-original-RGB-shadow-trim-TRUE-ALPHA-QA.png"
corrected.save(png,optimize=True)
bbox=corrected.getchannel("A").getbbox()
assert bbox is not None and bbox[2]-bbox[0]>.55*w
object_only=corrected.crop(bbox)
canvas=Image.new("RGB",(1080,1080),"white")
fitted=ImageOps.contain(object_only,(865,975),Image.Resampling.LANCZOS)
canvas.paste(fitted,((1080-fitted.width)//2,50+(975-fitted.height)//2),fitted.getchannel("A"))
jpg=OUT/"01-OBgE300mL-precise-foreground-1080-QA.jpg"
canvas.save(jpg,"JPEG",quality=94,optimize=True,subsampling=0)
with Image.open(jpg) as verify:
 verify.load();assert verify.size==(1080,1080) and verify.format=="JPEG"
assert jpg.stat().st_size<2_000_000
font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda n,b=False:ImageFont.truetype(bold if b else font,n)
def white(art):
 a=Image.new("RGBA",art.size,"white");a.alpha_composite(art)
 return a.convert("RGB")
board=Image.new("RGB",(1515,860),"#f3f0ee")
d=ImageDraw.Draw(board)
d.text((16,16),"v2856 OBgE Max Waterful 300mL | pump/body shadow trim | QA ONLY",fill="#342f36",font=f(23,True))
for i,art in enumerate([src,corrected]):
 thumb=ImageOps.contain(white(art),(680,745),Image.Resampling.LANCZOS)
 board.paste(thumb,(30+i*750+(680-thumb.width)//2,65+(745-thumb.height)//2))
d.text((25,812),"BEFORE: preserved original v2712",font=f(20),fill="#514b52")
d.text((783,812),"AFTER: source RGB retained; mask-only precision QA",font=f(19),fill="#514b52")
proof=OUT/"v2856-OBgE-pump-before-after-comparison-QA.jpg"
board.save(proof,"JPEG",quality=88,optimize=True)
assert sha(s)==source_sha and sha(legacy)==legacy_sha
report={
 "version":"v2856","family":"pending-22","baseline":"v2855",
 "product":"OBgE Max Waterful Sun Cream 300mL",
 "source_cutout_png":str(s),"source_cutout_sha256":source_sha,
 "source_hero_JPG":str(legacy),"source_hero_sha256":legacy_sha,
 "source_PNG_dimensions":[w,h],
 "fix_scope":"right-side pump, neck, and perimeter cast shadow only",
 "original_product_RGB_preserved":True,
 "left_62pct_alpha_unchanged":True,
 "alpha_pixel_count_changed":affected,"equivalent_fully_opaque_pixels_removed":removed255,
 "new_transparent_PNG":png.name,"new_transparent_PNG_sha256":sha(png),
 "new_JPG":jpg.name,"new_JPG_sha256":sha(jpg),"JPG_bytes":jpg.stat().st_size,
 "new_contact_qa":proof.name,
 "previously_approved_11_families_preserved":True,
 "prior_55_verified_public_URLs_unchanged":True,
 "v2854_five_frame_set_unchanged":True,"resegmentation_or_photo_downloads":0,
 "source_photo_rights_confirmed":False,"exact_owned_stock_packaging_confirmed":False,
 "genuine_round_MK_logo_authenticated":False,
 "human_closeup_mask_qa":"PENDING","new_retaiI_approvals":0,"new_public_URLs":0,
 "final_xlsx_shared":False,"state":"NEW_MASK_QA_ONLY_RETAIL_HOLD",
 "next":"Compare physical 300mL pump and labels, check close edges manually and license before any sale image."
}
(OUT/"manifest.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"v":"v2856","PNG":[w,h],"alpha_changed":affected,
"new_1080_JPG_bytes":jpg.stat().st_size,"retail_approved":False}))
